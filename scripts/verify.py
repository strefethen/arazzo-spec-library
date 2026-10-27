#!/usr/bin/env python3
"""Manifest-driven offline validation and fixture execution, using arazzo-cli."""

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from urllib.parse import urlsplit

import yaml

from fixture_server import assert_consumed, fixture_server

ROOT = Path(__file__).resolve().parents[1]


def local_path(root, value):
    path = (root / value).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        raise ValueError(f"missing or nonlocal file: {value}")
    return path


def load_yaml(path):
    with path.open() as stream:
        return yaml.safe_load(stream)


def command(args, cwd=ROOT, env=None, forbidden_output=()):
    result = subprocess.run(args, cwd=cwd, env=env, text=True, capture_output=True,
                            timeout=45, check=False)
    # Check before parsing or assertions that could reproduce captured output.
    if any(value in stream for value in forbidden_output
           for stream in (result.stdout, result.stderr)):
        raise AssertionError("forbidden output detected in CLI capture")
    try:
        data = json.loads(result.stdout)
    except ValueError as error:
        raise AssertionError(f"non-JSON output from {args[0]}: {result.stderr}") from error
    return result, data


def assert_subset(expected, actual, location="outputs"):
    if isinstance(expected, dict):
        if not isinstance(actual, dict):
            raise AssertionError(f"{location}: expected object, got {actual!r}")
        for key, value in expected.items():
            if key not in actual:
                raise AssertionError(f"{location}.{key}: missing")
            assert_subset(value, actual[key], f"{location}.{key}")
    elif type(expected) is not type(actual) or expected != actual:
        raise AssertionError(f"{location}: {actual!r} != {expected!r}")


def check_entry(root, entry):
    root = root.resolve()
    for field in ("id", "path", "description", "arazzo", "tier", "openapi", "workflows", "env", "tests"):
        if field not in entry:
            raise ValueError(f"entry missing {field}")
    if entry["tier"] not in ("hermetic", "dry-run", "live"):
        raise ValueError(f"unknown tier for {entry['id']}")
    spec = load_yaml(local_path(root, entry["path"]))
    if entry["workflows"] != [workflow["workflowId"] for workflow in spec["workflows"]]:
        raise ValueError(f"workflow registration mismatch: {entry['id']}")
    sources = set()
    for source in spec["sourceDescriptions"]:
        if source.get("type") != "openapi" or urlsplit(source["url"]).scheme:
            raise ValueError("offline verification requires local OpenAPI sources")
        path = local_path(root, str(Path(entry["path"]).parent / source["url"]))
        sources.add(path.relative_to(root).as_posix())
    if sources != set(entry["openapi"]):
        raise ValueError(f"OpenAPI registration mismatch: {entry['id']}")
    for path in entry["openapi"]:
        description = load_yaml(local_path(root, path))
        if not description.get("servers"):
            raise ValueError(f"OpenAPI servers missing: {path}")
        # Rebase one owning server surface, never silently miss an override.
        for item in description.get("paths", {}).values():
            if "servers" in item or any(isinstance(op, dict) and "servers" in op for op in item.values()):
                raise ValueError("path/operation server overrides require explicit harness support")
    for workflow in spec["workflows"]:
        for step in workflow["steps"]:
            if set(step) & {"operationPath", "workflowId"} or not step.get("operationId", "").startswith("$sourceDescriptions."):
                raise ValueError("offline verification requires qualified local operationId targets")
    suite = load_yaml(local_path(root, entry["tests"]))
    if not isinstance(suite, dict) or not suite.get("cases"):
        raise ValueError(f"no fixture cases: {entry['id']}")
    covered = set()
    names = set()
    for case in suite["cases"]:
        if case["name"] in names:
            raise ValueError("duplicate case name")
        names.add(case["name"])
        if case["workflow"] not in entry["workflows"]:
            raise ValueError("unknown scenario workflow")
        expected = case["expect"]
        if "forbidden_output" in expected:
            check_strings(expected["forbidden_output"], "forbidden_output")
        if expected["kind"] == "success":
            if not expected.get("outputs"):
                raise ValueError("success case requires output assertions")
            covered.add(case["workflow"])
        elif expected["kind"] != "error" or not expected.get("code"):
            raise ValueError("error case requires specific CLI code")
        for request in case["requests"]:
            if "absent_headers" in request:
                check_strings(request["absent_headers"], "absent_headers")
            response = request["response"]
            if ("fixture" in response) == ("body" in response):
                raise ValueError("response requires exactly one of fixture/body")
            if "fixture" in response:
                json.loads(local_path(root, response["fixture"]).read_text())
            if "location" in {key.lower() for key in response.get("headers", {})}:
                raise ValueError("fixture redirects are not allowed")
    if covered != set(entry["workflows"]):
        raise ValueError(f"missing happy-path fixture coverage: {entry['id']}")
    view = entry.get("examples", {}).get("quickstart", {}).get("jq")
    if view:
        local_path(root, view)
    return spec, suite


def check_strings(value, field):
    if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value):
        raise ValueError(f"{field} requires a list of nonempty strings")


def run_case(root, cli, entry, spec, case):
    requests = case["requests"]
    read_fixture = lambda value: json.loads(local_path(root, value).read_text())
    with fixture_server(requests, read_fixture) as (base, state), tempfile.TemporaryDirectory() as directory:
        temp = Path(directory)
        target = temp / entry["path"]
        target.parent.mkdir(parents=True)
        target.write_text(yaml.safe_dump(spec, sort_keys=False))
        for value in entry["openapi"]:
            source = load_yaml(local_path(root, value))
            original = source["servers"][0]["url"]
            source["servers"] = [{"url": base + urlsplit(original).path.rstrip("/")}]
            dest = temp / value
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(yaml.safe_dump(source, sort_keys=False))
        args = [cli, "--json", "run", str(target), case["workflow"], "--strict-inputs",
                "--http-timeout", "5s", "--execution-timeout", "15s", "--max-redirects", "0"]
        for key, value in case.get("inputs", {}).items():
            args += ["--input-json", f"{key}={json.dumps(value)}"]
        env = {key: value for key, value in os.environ.items() if "proxy" not in key.lower()}
        env["NO_PROXY"] = "*"
        result, data = command(args, temp, env, case["expect"].get("forbidden_output", []))
        assert_consumed(requests, state)
        expected = case["expect"]
        assert_subset({"kind": expected["kind"]}, data, "result")
        if expected["kind"] == "success":
            if result.returncode:
                raise AssertionError(result.stderr)
            assert_subset(expected["outputs"], data.get("outputs"))
        else:
            if not result.returncode:
                raise AssertionError("expected nonzero CLI exit")
            assert_subset({"code": expected["code"]}, data, "result")
        if "assert" in expected:
            assertion = subprocess.run(["jq", "-e", expected["assert"]], input=json.dumps(data),
                                       text=True, capture_output=True, timeout=10)
            if assertion.returncode or assertion.stdout.strip() != "true":
                raise AssertionError(f"jq assertion failed: {assertion.stderr}")
        view = entry.get("examples", {}).get("quickstart", {}).get("jq")
        if view:
            summary = subprocess.run(["jq", "-er", "-f", str(local_path(root, view))],
                                     input=json.dumps(data), text=True, capture_output=True, timeout=10)
            if expected["kind"] == "success" and (summary.returncode or not summary.stdout.strip()):
                raise AssertionError(f"summary failed: {summary.stderr}")
            for text in expected.get("view_contains", []):
                if text not in summary.stdout:
                    raise AssertionError(f"summary missing {text!r}")


def verify(root, cli, selected):
    root = root.resolve()
    manifest = load_yaml(root / "manifest.yaml")
    if manifest.get("version") != 1 or not manifest.get("specs"):
        raise ValueError("expected nonempty manifest version 1")
    ids = [entry["id"] for entry in manifest["specs"]]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate manifest IDs")
    paths = [entry["path"] for entry in manifest["specs"]]
    discovered = {path.relative_to(root).as_posix() for path in (root / "specs").rglob("*.arazzo.y*ml")}
    if len(paths) != len(set(paths)) or set(paths) != discovered:
        raise ValueError("manifest paths must register every spec exactly once")
    if set(selected) - set(ids):
        raise ValueError("unknown spec selection")
    count = 0
    for entry in manifest["specs"]:
        if selected and entry["id"] not in selected:
            continue
        spec, suite = check_entry(root, entry)
        for verb in ("validate", "list"):
            result, data = command([cli, "--json", "--strict", verb, str(root / entry["path"])])
            if result.returncode or (verb == "validate" and not data.get("valid")):
                raise AssertionError(f"{entry['id']}: {verb}: {data}")
            if verb == "list" and [item["id"] for item in data] != entry["workflows"]:
                raise AssertionError("CLI workflow discovery mismatch")
        for workflow in spec["workflows"]:
            result, data = command([cli, "--json", "show", workflow["workflowId"], "--dir",
                                    str((root / entry["path"]).parent)])
            if result.returncode or data.get("id") != workflow["workflowId"]:
                raise AssertionError("CLI show mismatch")
            happy = next(case for case in suite["cases"] if case["workflow"] == workflow["workflowId"]
                         and case["expect"]["kind"] == "success")
            args = [cli, "--json", "run", str(root / entry["path"]), workflow["workflowId"],
                    "--dry-run", "--strict-inputs", "--step", workflow["steps"][0]["stepId"]]
            for key, value in happy.get("inputs", {}).items():
                args += ["--input-json", f"{key}={json.dumps(value)}"]
            result, data = command(args)
            if result.returncode or data.get("kind") != "dryRun":
                raise AssertionError(f"dry-run failed: {data}")
        for case in suite["cases"]:
            run_case(root, cli, entry, spec, case)
            count += 1
            print(f"PASS {entry['id']} / {case['name']}", flush=True)
    return count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ids", nargs="*", help="optional manifest IDs")
    parser.add_argument("--cli", default=os.environ.get("ARAZZO_CLI", "arazzo-cli"))
    args = parser.parse_args()
    cli = shutil.which(args.cli)
    if not cli or not shutil.which("jq"):
        parser.error("arazzo-cli and jq are required; use --cli for a specific binary")
    try:
        count = verify(ROOT, cli, args.ids)
        print(f"Verified {count} fixture scenarios; zero live provider requests.")
    except (AssertionError, ValueError, KeyError, TypeError, OSError, yaml.YAMLError, subprocess.SubprocessError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
