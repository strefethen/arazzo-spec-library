import copy
from pathlib import Path
import socket
import sys
import tempfile
import unittest
from urllib.request import urlopen
from urllib.error import HTTPError
from unittest.mock import patch

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from fixture_server import assert_consumed, fixture_server, match_request
from verify import assert_subset, check_entry, command, local_path, run_case, verify


class RequestMatchingTests(unittest.TestCase):
    def setUp(self):
        self.expected = {"method": "POST", "path": "/packages/pkg:npm/a@1", "query": {"limit": "1"},
                         "headers": {"Authorization": "Bearer fixture"}, "body": {"name": "a"}}

    def check(self, expected=None, target="/packages/pkg%3Anpm%2Fa%401?limit=1",
              headers=None, body=b'{"name":"a"}', method="POST"):
        match_request(expected or self.expected, method, target,
                      headers or {"authorization": "Bearer fixture"}, body)

    def test_exact_semantic_request(self):
        self.check()

    def test_wrong_query(self):
        with self.assertRaisesRegex(AssertionError, "query"):
            self.check(target="/packages/pkg:npm/a@1?limit=2")

    def test_extra_query(self):
        with self.assertRaisesRegex(AssertionError, "query"):
            self.check(target="/packages/pkg:npm/a@1?limit=1&token=bad")

    def test_wrong_method(self):
        with self.assertRaisesRegex(AssertionError, "target"):
            self.check(method="GET")

    def test_wrong_path(self):
        with self.assertRaisesRegex(AssertionError, "target"):
            self.check(target="/packages/b?limit=1")

    def test_wrong_header(self):
        with self.assertRaisesRegex(AssertionError, "header"):
            self.check(headers={"Authorization": "Bearer wrong"})

    def test_basic_authorization_absent_downstream_case_insensitive(self):
        expected = {"method": "GET", "path": "/inventory", "absent_headers": ["AUTHORIZATION"],
                    "headers": {"vmware-api-session-id": "synthetic-session"}}
        match_request(expected, "GET", "/inventory", {"VMWARE-API-SESSION-ID": "synthetic-session"}, b"")
        with self.assertRaisesRegex(AssertionError, "forbidden request header") as raised:
            match_request(expected, "GET", "/inventory",
                          {"Authorization": "Basic secret", "vmware-api-session-id": "synthetic-session"}, b"")
        self.assertNotIn("Basic secret", str(raised.exception))

    def test_204_has_no_wire_body_or_framing(self):
        requests = [{"method": "DELETE", "path": "/api/session", "response": {
            "status": 204, "body": "must never reach the wire",
            "headers": {"Content-Length": "999", "Transfer-Encoding": "chunked"}}}]
        with fixture_server(requests, lambda _: None) as (url, state):
            from urllib.parse import urlsplit
            parsed = urlsplit(url)
            with socket.create_connection((parsed.hostname, parsed.port), timeout=2) as client:
                client.sendall(b"DELETE /api/session HTTP/1.0\r\nHost: localhost\r\n\r\n")
                chunks = []
                while chunk := client.recv(4096):
                    chunks.append(chunk)
            headers, body = b"".join(chunks).split(b"\r\n\r\n", 1)
            self.assertIn(b"204", headers)
            self.assertNotIn(b"content-length", headers.lower())
            self.assertNotIn(b"transfer-encoding", headers.lower())
            self.assertEqual(body, b"")
            assert_consumed(requests, state)

    def test_wrong_body(self):
        with self.assertRaisesRegex(AssertionError, "body"):
            self.check(body=b'{"name":"b"}')

    def test_extra_body(self):
        expected = copy.deepcopy(self.expected)
        del expected["body"]
        with self.assertRaisesRegex(AssertionError, "unexpected request body"):
            self.check(expected=expected)

    def test_unconsumed_request(self):
        with self.assertRaisesRegex(AssertionError, "consumed 0 of 1"):
            assert_consumed([self.expected], {"index": 0, "errors": []})

    def test_server_rejects_extra_request(self):
        with fixture_server([], lambda _: None) as (url, state):
            try:
                urlopen(url + "/extra", timeout=2)
                self.fail("extra request unexpectedly succeeded")
            except HTTPError as error:
                self.assertEqual(error.code, 500)
                error.close()
            with self.assertRaisesRegex(AssertionError, "unexpected extra"):
                assert_consumed([], state)


class AssertionTests(unittest.TestCase):
    def test_forbidden_output_checked_before_json_parsing_and_diagnostics(self):
        sentinel = "synthetic-private-value"
        for program in (f"print('{sentinel}')", f"import sys; print('{sentinel}', file=sys.stderr)"):
            with self.subTest(program=program), self.assertRaisesRegex(AssertionError, "forbidden output") as raised:
                command([sys.executable, "-c", program], forbidden_output=[sentinel])
            self.assertNotIn(sentinel, str(raised.exception))

    def test_clean_output_passes(self):
        result, data = command([sys.executable, "-c", 'print(\'{"kind":"success"}\')'],
                               forbidden_output=["synthetic-private-value"])
        self.assertEqual(result.returncode, 0)
        self.assertEqual(data, {"kind": "success"})

    def test_nested_subset(self):
        assert_subset({"a": {"b": 3}}, {"a": {"b": 3, "c": 4}})

    def test_missing_output(self):
        with self.assertRaisesRegex(AssertionError, "missing"):
            assert_subset({"version": "1"}, {})

    def test_wrong_type(self):
        with self.assertRaises(AssertionError):
            assert_subset({"number": 1}, {"number": "1"})

    def test_bool_is_not_number(self):
        with self.assertRaises(AssertionError):
            assert_subset({"number": 1}, {"number": True})

    def test_arrays_are_exact(self):
        with self.assertRaises(AssertionError):
            assert_subset([], ["not empty"])


class PreflightTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.entry = {"id": "example.lookup", "path": "specs/example/lookup.arazzo.yaml",
                      "description": "test", "arazzo": "1.0.x", "tier": "live",
                      "openapi": ["fixtures/openapi/example.yaml"], "workflows": ["lookup"],
                      "env": [], "tests": "tests/example.yaml"}
        self.spec = {"sourceDescriptions": [{"name": "api", "type": "openapi",
                      "url": "../../fixtures/openapi/example.yaml"}],
                     "workflows": [{"workflowId": "lookup", "steps": [{"stepId": "get",
                     "operationId": "$sourceDescriptions.api.getThing"}]}]}
        self.openapi = {"servers": [{"url": "https://example.invalid"}],
                        "paths": {"/thing": {"get": {"operationId": "getThing"}}}}
        self.suite = {"cases": [{"name": "happy", "workflow": "lookup", "requests": [],
                                 "expect": {"kind": "success", "outputs": {"id": "1"}}}]}

    def write(self):
        for name, data in ((self.entry["path"], self.spec), (self.entry["openapi"][0], self.openapi),
                           (self.entry["tests"], self.suite)):
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(yaml.safe_dump(data))

    def test_local_sources(self):
        self.write()
        check_entry(self.root, self.entry)

    def test_remote_source_rejected_before_execution(self):
        self.spec["sourceDescriptions"][0]["url"] = "https://example.invalid/openapi.yaml"
        self.write()
        with self.assertRaisesRegex(ValueError, "local OpenAPI"):
            check_entry(self.root, self.entry)

    def test_override_server_rejected_before_execution(self):
        self.openapi["paths"]["/thing"]["get"]["servers"] = [{"url": "https://example.invalid"}]
        self.write()
        with self.assertRaisesRegex(ValueError, "server overrides"):
            check_entry(self.root, self.entry)

    def test_url_target_rejected_before_execution(self):
        self.spec["workflows"][0]["steps"][0] = {"operationPath": "https://example.invalid#/paths/~1x/get"}
        self.write()
        with self.assertRaisesRegex(ValueError, "operationId"):
            check_entry(self.root, self.entry)

    def test_missing_manifest_field(self):
        del self.entry["tests"]
        with self.assertRaisesRegex(ValueError, "missing tests"):
            check_entry(self.root, self.entry)

    def test_unregistered_companion(self):
        self.write()
        self.entry["openapi"] = []
        with self.assertRaisesRegex(ValueError, "registration mismatch"):
            check_entry(self.root, self.entry)

    def test_empty_output_assertions_rejected(self):
        self.suite["cases"][0]["expect"]["outputs"] = {}
        self.write()
        with self.assertRaisesRegex(ValueError, "output assertions"):
            check_entry(self.root, self.entry)

    def test_redirect_rejected_before_execution(self):
        self.suite["cases"][0]["requests"] = [{"response": {"status": 302, "body": {},
            "headers": {"Location": "https://example.invalid"}}}]
        self.write()
        with self.assertRaisesRegex(ValueError, "redirects"):
            check_entry(self.root, self.entry)

    def test_new_assertion_types_preflight(self):
        for value in (None, "Authorization", {}, [1], [""]):
            for field in ("absent_headers", "forbidden_output"):
                with self.subTest(field=field, value=value):
                    self.suite["cases"][0]["expect"].pop("forbidden_output", None)
                    self.suite["cases"][0]["requests"] = []
                    if field == "forbidden_output":
                        self.suite["cases"][0]["expect"][field] = value
                    else:
                        self.suite["cases"][0]["requests"] = [{field: value, "response": {"body": {}}}]
                    self.write()
                    with self.assertRaisesRegex(ValueError, field):
                        check_entry(self.root, self.entry)

    def test_run_case_checks_forbidden_capture_before_other_assertions(self):
        self.write()
        case = self.suite["cases"][0]
        case["expect"]["forbidden_output"] = ["synthetic-private-value"]
        import subprocess
        captured = subprocess.CompletedProcess([], 1, "synthetic-private-value", "")
        with patch("verify.subprocess.run", return_value=captured):
            with self.assertRaisesRegex(AssertionError, "forbidden output") as raised:
                run_case(self.root, "synthetic-cli", self.entry, self.spec, case)
        self.assertNotIn("synthetic-private-value", str(raised.exception))

    def test_path_escape_rejected(self):
        with self.assertRaisesRegex(ValueError, "nonlocal"):
            local_path(self.root, "../not-local")

    def test_empty_manifest(self):
        (self.root / "manifest.yaml").write_text("version: 1\nspecs: []\n")
        with self.assertRaisesRegex(ValueError, "nonempty"):
            verify(self.root, "unused-cli", [])

    def test_duplicate_manifest_ids(self):
        (self.root / "manifest.yaml").write_text(yaml.safe_dump({"version": 1, "specs": [self.entry, self.entry]}))
        with self.assertRaisesRegex(ValueError, "duplicate manifest IDs"):
            verify(self.root, "unused-cli", [])

    def test_unregistered_spec(self):
        self.write()
        extra = self.root / "specs/example/unregistered.arazzo.yaml"
        extra.write_text(yaml.safe_dump(self.spec))
        (self.root / "manifest.yaml").write_text(yaml.safe_dump({"version": 1, "specs": [self.entry]}))
        with self.assertRaisesRegex(ValueError, "register every spec"):
            verify(self.root, "unused-cli", [])


if __name__ == "__main__":
    unittest.main()
