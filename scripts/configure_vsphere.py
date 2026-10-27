#!/usr/bin/env python3
"""Create an ignored, credential-free vSphere endpoint bundle; never execute it."""

import argparse
import ipaddress
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
from urllib.parse import urlsplit

import yaml

from verify import ROOT, check_entry, load_yaml


def server_origin(value):
    """Accept only a literal HTTPS origin, never credentials or URL templates."""
    try:
        if not value or any(char.isspace() or ord(char) < 32 for char in value):
            raise ValueError
        parsed = urlsplit(value)
        if (parsed.scheme != "https" or not value.startswith("https://")
                or parsed.username is not None or parsed.password is not None
                or parsed.path not in ("", "/") or "?" in value or "#" in value
                or any(char in value for char in "{}%\\") or not parsed.hostname):
            raise ValueError
        host = parsed.hostname
        if ":" in host:
            ipaddress.IPv6Address(host)
        elif not all(re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?", label)
                     for label in host.rstrip(".").split(".")) or len(host) > 253:
            raise ValueError
        if parsed.netloc.endswith(":") or (parsed.port is not None and not 1 <= parsed.port <= 65535):
            raise ValueError
    except ValueError:
        # Do not echo a rejected URL: it might contain a credential.
        raise ValueError("server must be a literal HTTPS origin with an optional port") from None
    return value.rstrip("/")


def source_path(root, value):
    """Repository-relative, non-symlink file with a stable copied identity."""
    path = Path(value)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise ValueError("bundle source must be repository-relative")
    target = root / path
    if any(part.is_symlink() for part in (target, *target.parents)) or not target.is_file():
        raise ValueError("bundle source must be a regular non-symlink file")
    return target


def check_refs(value):
    if isinstance(value, dict):
        for key, item in value.items():
            if key == "$ref" and (not isinstance(item, str) or not item.startswith("#")):
                raise ValueError("bundle requires document-local references")
            check_refs(item)
    elif isinstance(value, list):
        for item in value:
            check_refs(item)


def bundle_sources(root):
    manifest = load_yaml(source_path(root, "manifest.yaml"))
    if manifest.get("version") != 1 or not isinstance(manifest.get("specs"), list):
        raise ValueError("expected manifest version 1")
    entries = [entry for entry in manifest["specs"] if entry.get("provider") == "vsphere"]
    if not entries:
        raise ValueError("no registered vSphere workflows; no bundle created")
    if (len({entry["id"] for entry in entries}) != len(entries)
            or len({entry["path"] for entry in entries}) != len(entries)):
        raise ValueError("duplicate vSphere registration")
    files = {}
    for entry in entries:
        path = source_path(root, entry["path"])
        if not path.relative_to(root).is_relative_to("specs/vsphere"):
            raise ValueError("vSphere spec must be under specs/vsphere")
        spec = load_yaml(path)
        for source in spec["sourceDescriptions"]:
            url = urlsplit(source["url"])
            if url.scheme or url.netloc or url.query or url.fragment or Path(source["url"]).is_absolute():
                raise ValueError("bundle requires local registered sources")
            raw = path.parent / source["url"]
            if any(part.is_symlink() for part in (raw, *raw.parents)):
                raise ValueError("bundle source must not traverse symlinks")
            relative = Path(os.path.abspath(raw)).relative_to(root).as_posix()
            if relative not in entry["openapi"]:
                raise ValueError("bundle source is not registered")
        for companion in entry["openapi"]:
            target = source_path(root, companion)
            if not target.relative_to(root).is_relative_to("fixtures/openapi/vsphere"):
                raise ValueError("vSphere companion must be under fixtures/openapi/vsphere")
        # Share the harness's registration, target and server-override safeguards.
        check_entry(root, entry)
        names = {source["name"]: load_yaml((path.parent / source["url"]).resolve())
                 for source in spec["sourceDescriptions"]}
        for workflow in spec["workflows"]:
            for step in workflow["steps"]:
                match = re.fullmatch(r"\$sourceDescriptions\.([^.]+)\.([^.]+)", step["operationId"])
                if not match or match[1] not in names:
                    raise ValueError("invalid qualified operationId")
                operations = [op.get("operationId") for item in names[match[1]].get("paths", {}).values()
                              for op in item.values() if isinstance(op, dict)]
                if operations.count(match[2]) != 1:
                    raise ValueError("operationId must resolve to one registered local operation")
        check_refs(spec)
        files[entry["path"]] = path.read_bytes()
        for companion in entry["openapi"]:
            description = load_yaml(root / companion)
            check_refs(description)
            files[companion] = description
    return entries, files


def output_path(root, value):
    path = Path(value)
    if ".." in path.parts:
        raise ValueError("output path must not contain parent traversal")
    path = path if path.is_absolute() else root / path
    if not path.is_relative_to(root / ".artifacts") or path == root / ".artifacts":
        raise ValueError("output must be a new directory beneath repository .artifacts/")
    if any(part.is_symlink() for part in (path, *path.parents)):
        raise ValueError("output path must not traverse symlinks")
    if path.exists():
        raise ValueError("output already exists; refusing to overwrite")
    return path


def configure(root, server, output_dir):
    root = root.resolve()
    origin = server_origin(server)
    output = output_path(root, output_dir)
    entries, files = bundle_sources(root)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".vsphere-", dir=output.parent) as directory:
        temp = Path(directory)
        for relative, data in files.items():
            dest = temp / relative
            dest.parent.mkdir(parents=True, exist_ok=True)
            if isinstance(data, bytes):
                dest.write_bytes(data)
            else:
                for server in data["servers"]:
                    if server.get("variables"):
                        raise ValueError("bundle requires literal server URLs")
                    server["url"] = origin
                dest.write_text(yaml.safe_dump(data, sort_keys=False))
        # Exclusive creation refuses even an empty pre-existing output directory.
        # Generate everything first and remove only our own output on failure.
        output_path(root, output)
        output.mkdir()
        try:
            for child in temp.iterdir():
                shutil.move(str(child), output / child.name)
        except OSError:
            shutil.rmtree(output)
            raise
    return {"specs": [{"id": entry["id"], "path": str(output / entry["path"])} for entry in entries]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server", required=True, help="HTTPS origin without credentials")
    parser.add_argument("--output-dir", required=True, help="new directory beneath .artifacts/")
    args = parser.parse_args()
    try:
        report = configure(ROOT, args.server, args.output_dir)
    except (ValueError, KeyError, TypeError, OSError, yaml.YAMLError):
        print("configuration rejected: check origin, new .artifacts output and registered local bundle", file=sys.stderr)
        return 1
    print(json.dumps(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
