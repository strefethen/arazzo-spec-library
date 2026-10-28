"""Real CLI auth-pickup and redirect probes with synthetic loopback credentials."""

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
from fixture_server import assert_consumed, fixture_server, match_request
from verify import check_entry, load_yaml


class AppleAuthorizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entry = next(entry for entry in load_yaml(ROOT / "manifest.yaml")["specs"]
                         if entry["id"] == "apple.release-candidate-inspection")
        cls.spec, cls.suite = check_entry(ROOT, cls.entry)
        cls.happy = next(case for case in cls.suite["cases"]
                         if case["name"] == "happy-path-linked-build-is-not-marketing-version")
        cls.auth = cls.happy["inputs"]["authorization"]

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.temp = Path(self.directory.name)
        self.export = self.temp / "run.json"

    def _write_sources(self, origin):
        target = self.temp / self.entry["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(yaml.safe_dump(self.spec, sort_keys=False))
        for relative in self.entry["openapi"]:
            api = load_yaml(ROOT / relative)
            api["servers"] = [{"url": origin}]
            destination = self.temp / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(yaml.safe_dump(api, sort_keys=False))
        return target

    def run_cli(self, origin, case):
        target = self._write_sources(origin)
        env = {key: value for key, value in os.environ.items() if "proxy" not in key.lower()}
        env.update(NO_PROXY="*", APP_STORE_CONNECT_AUTHORIZATION=self.auth)
        args = ["arazzo-cli", "--json", "run", str(target), "release-candidate-inspection",
                "--strict-inputs", "--max-redirects", "0", "--http-timeout", "2s",
                "--execution-timeout", "10s", "--export-run", str(self.export),
                "--input", "authorization=${APP_STORE_CONNECT_AUTHORIZATION}",
                "--input", "bundle_id=com.example.corpus",
                "--input", "marketing_version=1.2.3"]
        self.assertFalse(any(self.auth in arg for arg in args),
                         "expanded credential must not appear in argv")
        result = subprocess.run(args, cwd=self.temp, env=env, capture_output=True,
                                text=True, timeout=15)
        surfaces = [result.stdout, result.stderr]
        if self.export.exists():
            surfaces.append(self.export.read_text())
        self.assertFalse(any(self.auth in surface for surface in surfaces),
                         "synthetic credential found on an output surface")
        return result, json.loads(result.stdout)

    def run_ordered(self, case):
        requests = copy.deepcopy(case["requests"])
        read_fixture = lambda path: json.loads((ROOT / path).read_text())
        with fixture_server(requests, read_fixture) as (origin, state):
            result, data = self.run_cli(origin, case)
            assert_consumed(requests, state)
        return result, data

    def test_literal_env_reference_keeps_full_bearer_only_in_authorization(self):
        result, data = self.run_ordered(self.happy)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(data["kind"], "success")
        self.assertEqual(data["outputs"]["selected_app"]["id"], "app-101")
        self.assertEqual(data["outputs"]["selected_version"]["id"], "version-201")
        self.assertEqual(data["outputs"]["attached_build_id"], "build-301")
        self.assertEqual(data["outputs"]["build"]["attributes"]["version"], "42")
        self.assertTrue(self.export.is_file(), "successful run should produce the requested export")
        self.assertTrue(json.loads(self.export.read_text()))

    def test_auth_failure_and_rate_limit_failure_remain_secret_free(self):
        for name in ("http-401-app-resolution", "http-429-build-no-retry-or-later-work"):
            with self.subTest(name=name):
                self.export.unlink(missing_ok=True)
                case = next(item for item in self.suite["cases"] if item["name"] == name)
                result, data = self.run_ordered(case)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(data["kind"], "error")
                self.assertEqual(data["code"], "RUNTIME_SUCCESS_CRITERIA_FAILED")

    @contextmanager
    def redirect_servers(self, redirect_at):
        seen = {"origin": [], "target": [], "mismatch": False}
        target_requests = []

        class Target(BaseHTTPRequestHandler):
            def log_message(self, *_args):
                pass

            def do_GET(self):
                seen["target"].append(self.path)
                target_requests.append(self.headers.get("Authorization"))
                self.send_response(500)
                self.end_headers()

        target = ThreadingHTTPServer(("127.0.0.1", 0), Target)
        location = f"http://localhost:{target.server_port}/must-not-contact"
        case_requests = self.happy["requests"]

        class Origin(BaseHTTPRequestHandler):
            def log_message(self, *_args):
                pass

            def do_GET(inner_self):
                index = len(seen["origin"])
                seen["origin"].append((inner_self.command, inner_self.path))
                try:
                    match_request(case_requests[index], inner_self.command, inner_self.path,
                                  inner_self.headers, b"")
                    if index == redirect_at:
                        inner_self.send_response(302)
                        inner_self.send_header("Location", location)
                        inner_self.end_headers()
                        return
                    expectation = case_requests[index]["response"]
                    payload = (ROOT / expectation["fixture"]).read_bytes()
                    inner_self.send_response(200)
                    inner_self.send_header("Content-Type", "application/json")
                    inner_self.send_header("Content-Length", str(len(payload)))
                    inner_self.end_headers()
                    inner_self.wfile.write(payload)
                except (AssertionError, IndexError):
                    seen["mismatch"] = True
                    inner_self.send_error(500)

        origin = ThreadingHTTPServer(("127.0.0.1", 0), Origin)
        servers = [target, origin]
        threads = [threading.Thread(target=server.serve_forever, daemon=True)
                   for server in servers]
        for thread in threads:
            thread.start()
        try:
            yield f"http://127.0.0.1:{origin.server_port}", seen, target_requests
        finally:
            for server in servers:
                server.shutdown()
                server.server_close()
            for thread in threads:
                thread.join(timeout=2)

    def test_redirects_at_first_and_downstream_steps_never_reach_target(self):
        for redirect_at, expected_origin_count in ((0, 1), (1, 2)):
            with self.subTest(redirect_at=redirect_at):
                self.export.unlink(missing_ok=True)
                with self.redirect_servers(redirect_at) as (origin, seen, target_auth):
                    result, data = self.run_cli(origin, self.happy)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(data["kind"], "error")
                self.assertEqual(len(seen["origin"]), expected_origin_count)
                self.assertFalse(seen["mismatch"], "origin request differed from exact scenario")
                self.assertEqual(seen["target"], [], "redirect target must never be contacted")
                self.assertEqual(target_auth, [], "redirect target must never receive credentials")


if __name__ == "__main__":
    unittest.main()
