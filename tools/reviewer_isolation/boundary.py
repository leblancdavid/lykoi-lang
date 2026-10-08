"""Fail-closed packaging and provider-neutral synthetic invocation utilities.

No credentials, model SDK, agent harness, or Lykoi implementation is imported.
R6.9 cannot dispatch substantive packages. Hash seals require an external anchor.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import uuid


VERSION = "review-boundary-1"
FORBIDDEN = re.compile(r"R6[._ -]?[78]|AGENTS\.md|opencode\.json|\.opencode", re.I)


class Halt(ValueError):
    pass


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii") + b"\n"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise Halt("DUPLICATE_JSON_KEY")
            result[key] = value
        return result
    return json.loads(Path(path).read_bytes(), object_pairs_hook=pairs)


def safe_name(name):
    if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9_.\-/]+", name):
        raise Halt("UNSAFE_PATH")
    p = PurePosixPath(name)
    if p.is_absolute() or any(x in ("", ".", "..") for x in name.split("/")):
        raise Halt("UNSAFE_PATH")
    if any(x.endswith(".") for x in p.parts):
        raise Halt("UNSAFE_PATH")
    if any(x.upper().split(".")[0] in {"CON", "PRN", "AUX", "NUL"}
           or re.fullmatch(r"(?:COM|LPT)[1-9]", x.upper().split(".")[0])
           for x in p.parts):
        raise Halt("UNSAFE_PATH")
    return name


def no_links(path):
    for p in (Path(path).absolute(), *Path(path).absolute().parents):
        info = p.lstat()
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise Halt("LINK_OR_REPARSE_POINT")


def regular_tree(root):
    """Reject links/reparse points and hardlinks, including root ancestors."""
    root = Path(root).absolute()
    no_links(root)
    if not root.is_dir():
        raise Halt("NOT_DIRECTORY")
    files = {}
    for parent, dirs, names in os.walk(root, followlinks=False):
        for name in dirs + names:
            p = Path(parent) / name
            info = p.lstat()
            if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
                raise Halt("LINK_OR_REPARSE_POINT")
            rel = safe_name(p.relative_to(root).as_posix())
            if p.is_dir():
                continue
            if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
                raise Halt("NONREGULAR_OR_HARDLINK")
            files[rel] = p.read_bytes()
    # Empty undeclared directories are unexpected resources too.
    expected_dirs = {str(p) for name in files for p in PurePosixPath(name).parents
                     if str(p) != "."}
    actual_dirs = {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_dir()}
    if actual_dirs != expected_dirs:
        raise Halt("UNEXPECTED_DIRECTORY")
    if len({name.casefold() for name in files}) != len(files):
        raise Halt("CASE_COLLISION")
    return files


def package_manifest(files, purpose):
    if purpose not in {"synthetic", "candidate-preparation"}:
        raise Halt("UNKNOWN_PURPOSE")
    for name, data in files.items():
        safe_name(name)
        if name == "manifest.json" or FORBIDDEN.search(name + data.decode("utf-8")):
            raise Halt("FORBIDDEN_CONTEXT")
        # Markdown dependencies must resolve inside the explicitly supplied files.
        for target in re.findall(r"\]\(([^)]+)\)", data.decode("utf-8")):
            target = target.split("#")[0]
            if target and target not in files:
                raise Halt("UNDECLARED_DEPENDENCY")
    return {"version": VERSION, "purpose": purpose,
            "files": {k: {"sha256": digest(v), "size": len(v)}
                      for k, v in sorted(files.items())}}


def create_package(destination, files, purpose):
    manifest = package_manifest(files, purpose)
    destination = Path(destination)
    no_links(destination.parent)
    destination.mkdir(parents=True, exist_ok=False)
    for name, data in files.items():
        p = destination / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
    (destination / "manifest.json").write_bytes(canonical(manifest))
    return digest(canonical(manifest))


def verify_package(root, expected):
    files = regular_tree(root)
    if "manifest.json" not in files:
        raise Halt("MISSING_MANIFEST")
    manifest = load(Path(root) / "manifest.json")
    if files.pop("manifest.json") != canonical(manifest) or digest(canonical(manifest)) != expected:
        raise Halt("PACKAGE_IDENTITY_MISMATCH")
    if manifest != package_manifest(files, manifest.get("purpose")):
        raise Halt("PACKAGE_CONTENT_MISMATCH")
    return manifest, files


class Broker:
    """Data-only allowlist broker. Not OS containment of an adapter."""
    def __init__(self, files, permissions):
        if set(permissions) - {"read_package"}:
            raise Halt("EXCESS_TOOL_PERMISSION")
        self.files = dict(files)
        self.permissions = tuple(permissions)

    def call(self, tool, name):
        if tool not in self.permissions or tool != "read_package":
            raise Halt("UNAUTHORIZED_TOOL")
        safe_name(name)
        if name not in self.files:
            raise Halt("FORBIDDEN_FILE")
        return self.files[name]


def validate_config(config):
    keys = {"provider", "model", "adapter_sha256", "environment", "tools", "network",
            "session", "retrieval", "system_message"}
    if set(config) != keys:
        raise Halt("CONFIGURATION_SCHEMA")
    if not all(isinstance(config[k], str) and config[k] for k in ("provider", "model")):
        raise Halt("MISSING_MODEL_CONFIGURATION")
    if not re.fullmatch(r"[0-9a-f]{64}", config["adapter_sha256"]):
        raise Halt("ADAPTER_IDENTITY")
    # This implemented adapter profile is offline and tool-free. Future online
    # adapters must supply a separately tested destination-restricted transport.
    if config["environment"] != {} or config["tools"] != []:
        raise Halt("EXCESS_ENVIRONMENT_OR_TOOLS")
    if config["network"] != "none" or config["retrieval"] != "disabled":
        raise Halt("UNCONTROLLED_NETWORK_OR_RETRIEVAL")
    if config["session"] != "new" or config["system_message"] != "Use only the supplied synthetic input.":
        raise Halt("INHERITED_GUIDANCE_OR_SESSION")


def request_for(manifest, files, config):
    validate_config(config)
    if manifest["purpose"] != "synthetic":
        raise Halt("SUBSTANTIVE_DISPATCH_NOT_AUTHORIZED")
    return {"version": VERSION, "invocation": str(uuid.uuid4()),
            "package_sha256": digest(canonical(manifest)),
            "provider": config["provider"], "model": config["model"],
            "messages": [{"role": "system", "content": config["system_message"]},
                         {"role": "user", "content": {k: v.decode("utf-8")
                                                       for k, v in sorted(files.items())}}],
            "tools": [], "retrieval": "disabled", "session": "new"}


def seal(destination, record, output=b"", stderr=b""):
    destination = Path(destination)
    no_links(destination.parent)
    destination.mkdir(parents=True, exist_ok=False)
    blobs = {"record.json": canonical(record), "output.bin": output, "stderr.bin": stderr}
    for name, data in blobs.items():
        (destination / name).write_bytes(data)
    identity = {"version": VERSION, "files": {k: digest(v) for k, v in blobs.items()}}
    seal_bytes = canonical(identity)
    (destination / "seal.json").write_bytes(seal_bytes)
    return digest(seal_bytes)


def verify_seal(root, trusted_anchor):
    files = regular_tree(root)
    if set(files) != {"record.json", "output.bin", "stderr.bin", "seal.json"}:
        raise Halt("EVIDENCE_FILE_SET")
    identity = load(Path(root) / "seal.json")
    if files["seal.json"] != canonical(identity) or digest(files["seal.json"]) != trusted_anchor:
        raise Halt("SEAL_ANCHOR_MISMATCH")
    if identity != {"version": VERSION, "files": {k: digest(files[k]) for k in
                                                   ("record.json", "output.bin", "stderr.bin")}}:
        raise Halt("OUTPUT_MODIFIED")
    record = load(Path(root) / "record.json")
    required = {"version", "status", "package_sha256", "config_sha256", "runner_sha256",
                "request", "execution", "limitations"}
    if set(record) != required or record["version"] != VERSION:
        raise Halt("MISSING_PROVENANCE")
    for key in ("package_sha256", "config_sha256", "runner_sha256"):
        if not re.fullmatch(r"[0-9a-f]{64}", record[key]):
            raise Halt("MISSING_PROVENANCE")
    if record["status"] == "SEALED_SYNTHETIC_UNQUALIFIED":
        if not record["request"] or not record["execution"]:
            raise Halt("MISSING_PROVENANCE")
        request, execution = record["request"], record["execution"]
        if (request.get("package_sha256") != record["package_sha256"]
                or request.get("version") != VERSION or request.get("tools") != []
                or request.get("retrieval") != "disabled" or request.get("session") != "new"
                or not request.get("provider") or not request.get("model")
                or execution.get("returncode") != 0
                or execution.get("environment_names") != [] or execution.get("tools") != []
                or execution.get("network") != "unshared-none"
                or execution.get("cwd") != "/work" or not execution.get("file_allowlist")
                or not files["output.bin"]):
            raise Halt("INVALID_PROVENANCE")
    return record


def sandbox_available():
    # No substitution with cwd-only subprocesses, WSL launch, or another agent.
    return sys.platform == "linux" and shutil.which("bwrap") is not None


def invoke(package, expected, config, adapter, evidence):
    """Offline process adapter, one JSON stdin request / raw stdout response.

    Only executable on Linux with bubblewrap. Its runtime is an explicitly
    approved standalone executable (no host runtime/library mounts). A Python
    script is not a standalone adapter. Linux path is not qualified on Windows.
    """
    record = {"version": VERSION, "status": "PROTOCOL_HALT", "package_sha256": expected,
              "config_sha256": digest(canonical(config)),
              "runner_sha256": digest(Path(__file__).read_bytes()), "request": None,
              "execution": None, "limitations": ["Provider hidden context is unverified.",
              "Host administrator and publisher are trusted; external seal anchor required.",
              "No independent semantic review is authorized in R6.9."]}
    output = stderr = b""
    try:
        manifest, files = verify_package(package, expected)
        request = request_for(manifest, files, config)
        record["request"] = request
        adapter = Path(adapter).absolute()
        no_links(adapter)
        if adapter.is_symlink() or not adapter.is_file() or adapter.stat().st_nlink != 1:
            raise Halt("ADAPTER_NOT_REGULAR")
        adapter_bytes = adapter.read_bytes()
        if digest(adapter_bytes) != config["adapter_sha256"]:
            raise Halt("ADAPTER_IDENTITY_MISMATCH")
        if not sandbox_available():
            raise Halt("ISOLATION_CONTROL_GAP")
        # Copy already verified bytes, never mount the repository or a mutable
        # adapter source. Private parent is not visible within the sandbox.
        with tempfile.TemporaryDirectory(prefix="review-boundary-") as temp:
            root = Path(temp)
            create_package(root / "input", files, "synthetic")
            (root / "adapter").write_bytes(adapter_bytes)
            (root / "adapter").chmod(0o500)
            command = [shutil.which("bwrap"), "--unshare-all", "--die-with-parent",
                       "--new-session", "--clearenv", "--cap-drop", "ALL",
                       "--ro-bind", str(root / "input"), "/input",
                       "--ro-bind", str(root / "adapter"), "/adapter",
                       "--tmpfs", "/work", "--chdir", "/work", "--", "/adapter"]
            record["execution"] = {"backend": "bubblewrap-offline-static-1",
                "cwd": "/work", "file_allowlist": sorted(files) + ["manifest.json"],
                "runtime_allowlist": ["/adapter"], "environment_names": [],
                "network": "unshared-none", "tools": [], "timeout_seconds": 30}
            try:
                result = subprocess.run(command, input=canonical(request), capture_output=True,
                                        env={}, cwd=temp, timeout=30, check=False)
                output, stderr = result.stdout, result.stderr
                record["execution"]["returncode"] = result.returncode
                if result.returncode:
                    raise Halt("PROVIDER_ADAPTER_FAILURE")
                if not output:
                    raise Halt("EMPTY_OUTPUT")
                # Running here alone is not host qualification or independence.
                record["status"] = "SEALED_SYNTHETIC_UNQUALIFIED"
            except subprocess.TimeoutExpired as exc:
                output, stderr = exc.stdout or b"", exc.stderr or b""
                raise Halt("PROVIDER_ADAPTER_TIMEOUT") from exc
    except (Halt, OSError, ValueError) as exc:
        record["status"] = str(exc) if isinstance(exc, Halt) else "INFRASTRUCTURE_FAILURE"
        # Never publish exception strings that might contain credentials/paths.
    anchor = seal(evidence, record, output, stderr)
    verify_seal(evidence, anchor)
    return record, anchor


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("verify-package")
    p.add_argument("package"); p.add_argument("identity")
    p = sub.add_parser("verify-seal")
    p.add_argument("evidence"); p.add_argument("anchor")
    p = sub.add_parser("run-synthetic")
    for name in ("package", "identity", "config", "adapter", "evidence"):
        p.add_argument(name)
    args = parser.parse_args()
    if args.command == "verify-package":
        verify_package(args.package, args.identity)
        print("PACKAGE_VERIFIED")
    elif args.command == "verify-seal":
        print(verify_seal(args.evidence, args.anchor)["status"])
    else:
        record, anchor = invoke(args.package, args.identity, load(args.config),
                                args.adapter, args.evidence)
        print(json.dumps({"status": record["status"], "seal_sha256": anchor}))
        return 0 if record["status"] == "SEALED_SYNTHETIC_UNQUALIFIED" else 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
