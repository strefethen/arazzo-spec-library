"""Real CLI pickup/security probes using only synthetic loopback credentials."""

import copy
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from fixture_server import assert_consumed, fixture_server
from verify import check_entry, load_yaml


class AuthPickupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entry = next(entry for entry in load_yaml(ROOT / "manifest.yaml")["specs"]
                         if entry["id"] == "vsphere.vm-guest-diagnosis")
        cls.spec, cls.suite = check_entry(ROOT, cls.entry)

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.temp = Path(self.directory.name)
        self.export = self.temp / "run.json"
        self.case = copy.deepcopy(self.suite["cases"][0])
        self.auth = self.case["inputs"]["authorization"]
        self.token = self.case["requests"][0]["response"]["body"]

    def run_cli(self, origin):
        target = self.temp / self.entry["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(yaml.safe_dump(self.spec, sort_keys=False))
        for relative in self.entry["openapi"]:
            api = load_yaml(ROOT / relative)
            api["servers"] = [{"url": origin}]
            destination = self.temp / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(yaml.safe_dump(api, sort_keys=False))
        env = {key: value for key, value in os.environ.items() if "proxy" not in key.lower()}
        env.update(NO_PROXY="*", VSPHERE_AUTHORIZATION=self.auth)
        # Literal whole env reference: shell single quotes in the documented command
        # produce this exact argv value, never the expanded credential.
        args = ["arazzo-cli", "--json", "run", str(target), "vm-guest-diagnosis",
                "--strict-inputs", "--max-redirects", "0", "--http-timeout", "2s",
                "--execution-timeout", "10s", "--export-run", str(self.export),
                "--input", "authorization=${VSPHERE_AUTHORIZATION}",
                "--input", "datacenter_name=Lab DC", "--input", "vm_name=app-01"]
        self.assertFalse(any(self.auth in arg or self.token in arg for arg in args))
        result = subprocess.run(args, cwd=self.temp, env=env, capture_output=True,
                                text=True, timeout=15)
        # Fail without printing any captured secret. Also inspect failed-run exports
        # whenever the CLI writes one; success must produce an export.
        surfaces = [result.stdout, result.stderr]
        if self.export.exists():
            surfaces.append(self.export.read_text())
        self.assertFalse(any(secret in surface for secret in (self.auth, self.token)
                             for surface in surfaces), "credential found on approved output surface")
        return result, json.loads(result.stdout)

    def run_ordered(self, case):
        requests = case["requests"]
        read = lambda path: json.loads((ROOT / path).read_text())
        with fixture_server(requests, read) as (origin, state):
            result, data = self.run_cli(origin)
            assert_consumed(requests, state)
        return result, data

    def test_env_reference_full_run_headers_stdout_stderr_and_export(self):
        result, data = self.run_ordered(self.case)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(data["kind"], "success")
        self.assertEqual(data["outputs"]["selected_vm"]["vm"], "vm-42")
        self.assertTrue(self.export.is_file(), "successful run must export")
        artifact = json.loads(self.export.read_text())
        self.assertTrue(artifact, "export must be a nonempty JSON document")

    def test_unexpected_login_status_scalar_token_has_no_preview_or_inventory(self):
        case = next(case for case in self.suite["cases"]
                    if case["name"] == "unexpected-login-status-no-token-preview")
        result, data = self.run_ordered(case)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(data["code"], "RUNTIME_SUCCESS_CRITERIA_FAILED")

    def test_work_failure_and_cleanup_failure_exports_remain_secret_free(self):
        for name in ("tools-no-data503", "failure-cleanup-failure", "normal-logout-failure"):
            with self.subTest(name=name):
                if self.export.exists():
                    self.export.unlink()
                case = next(case for case in self.suite["cases"] if case["name"] == name)
                result, data = self.run_ordered(case)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(data["kind"], "error")

    @contextmanager
    def redirect_servers(self, redirect_login):
        """Separate origin and target sockets; no scenario preflight bypass."""
        seen = {"origin": [], "target": []}
        login, logout = self.case["requests"][0], self.case["requests"][-1]

        class Target(BaseHTTPRequestHandler):
            def log_message(self, *_args):
                pass

            def do_GET(self):
                seen["target"].append(self.path)
                self.send_response(500)
                self.end_headers()

            do_POST = do_GET
            do_DELETE = do_GET

        target = ThreadingHTTPServer(("127.0.0.1", 0), Target)
        # Different hostname as well as socket, reproducing the cross-host risk.
        location = f"http://localhost:{target.server_port}/must-not-contact"

        class Origin(BaseHTTPRequestHandler):
            def log_message(self, *_args):
                pass

            def respond(self):
                from fixture_server import match_request
                seen["origin"].append((self.command, self.path))
                try:
                    if self.command == "POST":
                        match_request(login, self.command, self.path, self.headers, b"")
                        status, body = (302, None) if redirect_login else (201, login["response"]["body"])
                    elif self.command == "DELETE":
                        match_request(logout, self.command, self.path, self.headers, b"")
                        status, body = 204, None
                    else:
                        match_request(self_case["requests"][1], self.command, self.path, self.headers, b"")
                        status, body = 302, None
                    self.send_response(status)
                    if status == 302:
                        self.send_header("Location", location)
                    if status != 204:
                        self.send_header("Content-Type", "application/json")
                        payload = json.dumps(body).encode()
                        self.send_header("Content-Length", str(len(payload)))
                    self.end_headers()
                    if status != 204:
                        self.wfile.write(payload)
                except AssertionError:
                    seen["mismatch"] = True
                    self.send_error(500)

            do_POST = respond
            do_GET = respond
            do_DELETE = respond

        self_case = self.case
        origin = ThreadingHTTPServer(("127.0.0.1", 0), Origin)
        servers = [target, origin]
        threads = [threading.Thread(target=server.serve_forever, daemon=True) for server in servers]
        for thread in threads:
            thread.start()
        try:
            yield f"http://127.0.0.1:{origin.server_port}", seen
        finally:
            for server in servers:
                server.shutdown()
                server.server_close()
            for thread in threads:
                thread.join(timeout=2)

    def test_redirect_refused_target_never_contacted_and_work_failure_logs_out(self):
        for redirect_login in (True, False):
            with self.subTest(redirect_login=redirect_login):
                if self.export.exists():
                    self.export.unlink()
                with self.redirect_servers(redirect_login) as (origin, seen):
                    result, data = self.run_cli(origin)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(data["kind"], "error")
                self.assertFalse(seen.get("mismatch"), "origin headers or ordering differed")
                self.assertEqual(seen["target"], [], "redirect target must never be contacted")
                expected = [("POST", "/api/session")]
                if not redirect_login:
                    expected += [("GET", "/api/vcenter/datacenter?names=Lab+DC"),
                                 ("DELETE", "/api/session")]
                self.assertEqual(seen["origin"], expected)


if __name__ == "__main__":
    unittest.main()
