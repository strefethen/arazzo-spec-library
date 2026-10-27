import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from configure_vsphere import configure, server_origin


class ConfigurationTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name).resolve()
        self.entry = {"id": "vsphere.lookup", "provider": "vsphere",
                      "path": "specs/vsphere/lookup.arazzo.yaml", "description": "synthetic test",
                      "arazzo": "1.0.x", "tier": "live", "env": [], "workflows": ["lookup"],
                      "openapi": ["fixtures/openapi/vsphere/session.yaml"], "tests": "tests/lookup.yaml"}
        self.spec = {"sourceDescriptions": [{"name": "session", "type": "openapi",
                      "url": "../../fixtures/openapi/vsphere/session.yaml"}],
                     "workflows": [{"workflowId": "lookup", "steps": [{"stepId": "login",
                                    "operationId": "$sourceDescriptions.session.createSession"}]}]}
        self.openapi = {"openapi": "3.0.3", "servers": [
            {"url": "https://vcenter.invalid", "description": "safe default"}],
            "paths": {"/api/session": {"post": {"operationId": "createSession"}}}}
        self.suite = {"cases": [{"name": "synthetic", "workflow": "lookup", "requests": [],
                                 "expect": {"kind": "success", "outputs": {"ok": True}}}]}
        self.output = self.root / ".artifacts/configured"
        self.write()

    def write(self):
        for relative, value in (("manifest.yaml", {"version": 1, "specs": [self.entry]}),
                                (self.entry["path"], self.spec),
                                (self.entry["openapi"][0], self.openapi),
                                (self.entry["tests"], self.suite)):
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(yaml.safe_dump(value, sort_keys=False))

    def run_configure(self, output=None, server="https://vc.example.invalid:8443/"):
        return configure(self.root, server, output if output is not None else self.output)

    def rejected(self):
        with self.assertRaises((ValueError, KeyError)):
            self.run_configure()
        self.assertFalse(self.output.exists())

    def test_bundle_preserves_layout_source_bytes_and_only_rebases_servers(self):
        before = {path: path.read_bytes() for path in self.root.rglob("*.yaml")}
        with patch("socket.socket", side_effect=AssertionError("network forbidden")):
            report = self.run_configure()
        self.assertEqual(json.loads(json.dumps(report)), {"specs": [
            {"id": self.entry["id"], "path": str(self.output / self.entry["path"])}]})
        self.assertEqual((self.output / self.entry["path"]).read_bytes(), before[self.root / self.entry["path"]])
        expected = copy.deepcopy(self.openapi)
        expected["servers"][0]["url"] = "https://vc.example.invalid:8443"
        self.assertEqual(yaml.safe_load((self.output / self.entry["openapi"][0]).read_text()), expected)
        self.assertEqual({path: path.read_bytes() for path in before}, before)
        self.assertEqual(len(list(self.output.rglob("*.yaml"))), 2)

    def test_valid_origins(self):
        for value in ("https://vc.example.invalid", "https://localhost:443/",
                      "https://127.0.0.1", "https://[2001:db8::1]:8443"):
            with self.subTest(value=value):
                self.assertEqual(server_origin(value), value.rstrip("/"))

    def test_multiple_registered_specs_share_companion_and_ignore_other_providers(self):
        second = dict(self.entry, id="vsphere.second", path="specs/vsphere/second.arazzo.yaml")
        (self.root / second["path"]).write_bytes((self.root / self.entry["path"]).read_bytes())
        manifest = {"version": 1, "specs": [self.entry, second,
                    {"provider": "unrelated", "path": "not-read.yaml"}]}
        (self.root / "manifest.yaml").write_text(yaml.safe_dump(manifest))
        report = self.run_configure()
        self.assertEqual([item["id"] for item in report["specs"]], [self.entry["id"], second["id"]])
        self.assertEqual(len(list(self.output.rglob("*.yaml"))), 3)
        self.assertEqual((self.output / second["path"]).read_bytes(), (self.root / second["path"]).read_bytes())

    def test_invalid_origins_do_not_publish_or_echo_input(self):
        for value in ("http://vc.invalid", "https://user:secret@vc.invalid", "https://vc.invalid/api",
                      "https://vc.invalid?", "https://vc.invalid#", "https://{host}",
                      "https://vc.invalid/{path}", "https://vc.invalid:0", "https://vc.invalid:65536",
                      "https://vc.invalid:", "https://vc.invalid:x", "https://vc.invalid\n",
                      "https://vc.invalid\\evil", "https://vc%2einvalid", "https://-bad.invalid",
                      "https://", "https://bad..invalid", "https://[not-ipv6]"):
            with self.subTest(value=value), self.assertRaises(ValueError) as raised:
                self.run_configure(server=value)
            self.assertNotIn(value, str(raised.exception))
            self.assertFalse(self.output.exists())

    def test_unsafe_outputs(self):
        for output in (Path("/"), self.root, self.root / "specs/new", self.root / "fixtures/new",
                       self.root.parent / "escape", self.root / ".artifacts",
                       self.root / ".artifacts/../escaped"):
            with self.subTest(output=output), self.assertRaises(ValueError):
                self.run_configure(output=output)

    def test_existing_directory_or_file_never_overwritten(self):
        self.output.parent.mkdir()
        self.output.mkdir()
        with self.assertRaisesRegex(ValueError, "exists"):
            self.run_configure()
        self.output.rmdir()
        self.output.write_bytes(b"preserve")
        with self.assertRaises(ValueError):
            self.run_configure()
        self.assertEqual(self.output.read_bytes(), b"preserve")

    def test_output_symlinks_including_dangling_and_parent_are_rejected(self):
        self.output.parent.mkdir()
        self.output.symlink_to(self.root / "absent")
        with self.assertRaisesRegex(ValueError, "symlink"):
            self.run_configure()
        self.output.unlink()
        self.output.parent.rmdir()
        (self.root / ".artifacts").symlink_to(self.root / "specs", target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlink"):
            self.run_configure()

    def test_remote_and_unregistered_sources(self):
        for url in ("https://vc.invalid/api.yaml", "//vc.invalid/api.yaml",
                    "../../fixtures/openapi/vsphere/session.yaml?x=1",
                    "../../fixtures/openapi/vsphere/session.yaml#x",
                    "../../fixtures/openapi/vsphere/missing.yaml", "../../../escape.yaml"):
            with self.subTest(url=url):
                self.spec["sourceDescriptions"][0]["url"] = url
                self.write()
                self.rejected()

    def test_unregistered_companion(self):
        self.entry["openapi"].append("fixtures/openapi/vsphere/extra.yaml")
        (self.root / self.entry["openapi"][1]).write_text(yaml.safe_dump(self.openapi))
        self.write()
        self.rejected()

    def test_source_symlink(self):
        companion = self.root / self.entry["openapi"][0]
        actual = companion.with_name("actual.yaml")
        companion.rename(actual)
        companion.symlink_to(actual)
        self.rejected()

    def test_manifest_source_escape(self):
        for field in ("path", "openapi"):
            with self.subTest(field=field):
                manifest = {"version": 1, "specs": [copy.deepcopy(self.entry)]}
                manifest["specs"][0][field] = "../outside.yaml" if field == "path" else ["../outside.yaml"]
                (self.root / "manifest.yaml").write_text(yaml.safe_dump(manifest))
                self.rejected()

    def test_symlink_alias_cannot_leave_dangling_bundle_reference(self):
        alias = self.root / "fixtures/openapi/vsphere/alias.yaml"
        alias.symlink_to("session.yaml")
        self.spec["sourceDescriptions"][0]["url"] = "../../fixtures/openapi/vsphere/alias.yaml"
        self.write()
        self.rejected()

    def test_server_overrides(self):
        for location in (self.openapi["paths"]["/api/session"],
                         self.openapi["paths"]["/api/session"]["post"]):
            location["servers"] = [{"url": "https://elsewhere.invalid"}]
            self.write()
            self.rejected()
            del location["servers"]

    def test_unqualified_missing_or_remote_targets(self):
        step = self.spec["workflows"][0]["steps"][0]
        for target in ("createSession", "$sourceDescriptions.missing.createSession",
                       "$sourceDescriptions.session.missing", "$sourceDescriptions.session.createSession.extra"):
            step["operationId"] = target
            self.write()
            self.rejected()
        step["operationPath"] = "https://remote.invalid#/paths/session/post"
        self.write()
        self.rejected()

    def test_external_refs_rejected(self):
        for ref in ("https://remote.invalid/schema", "other.yaml#/schema", "../../../outside.yaml"):
            self.openapi["components"] = {"schemas": {"token": {"$ref": ref}}}
            self.write()
            self.rejected()

    def test_empty_registration_is_explicit_error(self):
        self.entry["provider"] = "other"
        self.write()
        with self.assertRaisesRegex(ValueError, "no registered vSphere"):
            self.run_configure()
        self.assertFalse(self.output.exists())

    def test_generation_failure_does_not_publish(self):
        with patch("configure_vsphere.yaml.safe_dump", side_effect=OSError("write failed")):
            with self.assertRaises(OSError):
                self.run_configure()
        self.assertFalse(self.output.exists())
        self.assertEqual(list(self.output.parent.iterdir()), [])

    def test_publication_failure_cleans_only_own_output(self):
        with patch("configure_vsphere.shutil.move", side_effect=OSError("move failed")):
            with self.assertRaises(OSError):
                self.run_configure()
        self.assertFalse(self.output.exists())
        self.assertTrue((self.root / self.entry["path"]).exists())

    def test_session_companion_contract(self):
        path = Path(__file__).resolve().parents[1] / "fixtures/openapi/vsphere/session.yaml"
        contract = yaml.safe_load(path.read_text())
        self.assertEqual(contract["info"]["version"], "8.0.3")
        self.assertEqual(contract["servers"], [{"url": "https://vcenter.invalid"}])
        post = contract["paths"]["/api/session"]["post"]
        delete = contract["paths"]["/api/session"]["delete"]
        self.assertEqual(post["responses"]["201"]["content"]["application/json"]["schema"], {"type": "string"})
        self.assertNotIn("content", delete["responses"]["204"])
        self.assertEqual(post["parameters"][0]["name"], "Authorization")
        self.assertEqual(delete["parameters"][0]["name"], "vmware-api-session-id")
        for operation, suffix in ((post, "post/"), (delete, "delete/")):
            self.assertTrue(operation["externalDocs"]["url"].endswith("/8.0.3/cis/api/session/" + suffix))


if __name__ == "__main__":
    unittest.main()
