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


class TestFlightAuthorizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entry = next(entry for entry in load_yaml(ROOT / "manifest.yaml")["specs"]
                         if entry["id"] == "apple.testflight-build-inspection")
        cls.spec, cls.suite = check_entry(ROOT, cls.entry)
        cls.happy = next(case for case in cls.suite["cases"]
                         if case["name"] == "happy-path")
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
        args = ["arazzo-cli", "--json", "run", str(target), "testflight-build-inspection",
                "--strict-inputs", "--max-redirects", "0", "--http-timeout", "2s",
                "--execution-timeout", "10s", "--export-run", str(self.export),
                "--input", "authorization=${APP_STORE_CONNECT_AUTHORIZATION}",
                "--input", "bundle_id=com.example.corpus",
                "--input-json", 'marketing_version="1.0"',
                "--input-json", 'build_number="126"']
        self.assertFalse(any(self.auth.removeprefix("Bearer ") in arg for arg in args),
                         "expanded credential must not appear in argv")
        if case.get("numeric_control"):
            index = args.index('marketing_version="1.0"') if case["numeric_control"] == "marketing_version" else args.index('build_number="126"')
            args[index - 1] = "--input"
            args[index] = "marketing_version=1.0" if case["numeric_control"] == "marketing_version" else "build_number=126"
        result = subprocess.run(args, cwd=self.temp, env=env, capture_output=True,
                                text=True, timeout=15)
        surfaces = [result.stdout, result.stderr]
        if self.export.exists():
            surfaces.append(self.export.read_text())
        self.assertFalse(any(self.auth.removeprefix("Bearer ") in surface for surface in surfaces),
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
        self.assertEqual(data["outputs"]["selected_prerelease_version"]["id"], "pre-201")
        self.assertEqual(data["outputs"]["build"]["id"], "build-301")
        self.assertEqual(data["outputs"]["build"]["attributes"]["version"], "126")
        self.assertEqual(data["outputs"], self.happy["expect"]["outputs"])
        self.assertTrue(self.export.is_file(), "successful run should produce the requested export")
        self.assertTrue(json.loads(self.export.read_text()))

    def test_auth_failure_and_rate_limit_failure_remain_secret_free(self):
        for name in ("http-401-step-0", "http-429-step-2"):
            with self.subTest(name=name):
                self.export.unlink(missing_ok=True)
                case = next(item for item in self.suite["cases"] if item["name"] == name)
                result, data = self.run_ordered(case)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(data["kind"], "error")
                self.assertEqual(data["code"], "RUNTIME_SUCCESS_CRITERIA_FAILED")

    def test_unquoted_numeric_controls_make_no_requests(self):
        for key in ("marketing_version", "build_number"):
            with self.subTest(key=key):
                case = copy.deepcopy(self.happy)
                case["numeric_control"] = key
                case["requests"] = []
                result, data = self.run_ordered(case)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(data["code"], "RUNTIME_INPUT_VALIDATION")
                self.assertNotIn("outputs", data)

    def test_summary_rejects_error_envelope(self):
        result = subprocess.run(["jq", "-er", "-f", str(ROOT / "views/apple.testflight-build-inspection.summary.jq")], input='{"kind":"error"}', text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)

    def test_summary_preserves_false_and_labels_unknown_and_empty(self):
        outputs = copy.deepcopy(self.happy["expect"]["outputs"])
        outputs["build"]["attributes"].pop("buildAudienceType")
        outputs["review_submissions"] = []
        outputs["beta_groups"] = []
        result = subprocess.run(
            ["jq", "-er", "-f", str(ROOT / "views/apple.testflight-build-inspection.summary.jq")],
            input=json.dumps({"kind": "success", "outputs": outputs}),
            text=True, capture_output=True)
        self.assertEqual(result.returncode, 0)
        for text in ("audience type: unknown", "Expired: false",
                     "no visible submission returned", "no associated groups returned",
                     "six non-atomic observations", "not fully audited"):
            self.assertIn(text, result.stdout)

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
        for redirect_at, expected_origin_count in ((0, 1), (3, 4), (5, 6)):
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
