"""Bounded synthetic-only runtime qualification. No benchmark discovery."""
import argparse
from contextlib import closing
import hashlib
import importlib
import io
import json
import os
from pathlib import Path
import platform
import struct
import subprocess
import sys
import tempfile
import unittest

from lykoi_controller import canonical
from lykoi_pipeline.controller import ROOT, digest

CONTRACT_PATH = "rehearsal/python-runtime-contract-v1.json"
TESTS = (
    "test_authority_controller.IdentityTests",
    "test_authority_controller.ControllerTests.test_persistence_actual_process_restart",
    "test_authority_controller.ControllerTests.test_same_artifacts_events_reproduce_identity_and_decisions",
    "test_authority_controller.ControllerTests.test_restart_detects_corrupt_artifact_and_journal",
    "test_requirements_workspace.WorkspaceTests.test_producer_exact_unicode_roundtrip",
    "test_requirements_workspace.WorkspaceTests.test_sealed_workspace_actual_process_restart",
    "test_public_rehearsal.VerificationFreezeTests.test_containment_filesystem_and_network",
    "test_compiler",
    "test_application",
)


def contract_pin():
    return {"version": "PYTHON_RUNTIME_CONTRACT_V1", "contract_sha256": sha(ROOT / CONTRACT_PATH),
            "procedure_sha256": sha(Path(__file__)), "tests": list(TESTS)}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def provenance():
    executable = Path(sys.executable).resolve()
    libraries = {}
    for base in {executable.parent, Path(sys.base_prefix), Path(__import__("sqlite3").__file__).parent}:
        for name in (f"python{sys.version_info.major}{sys.version_info.minor}.dll",
                     f"python{sys.version_info.major}{sys.version_info.minor}.zip", "python3.dll"):
            path = base / name
            if path.is_file():
                libraries[str(path)] = sha(path)
    import sqlite3
    return {"implementation": platform.python_implementation(), "version": sys.version,
            "architecture": platform.machine(), "pointer_bits": struct.calcsize("P") * 8,
            "platform": sys.platform, "executable_path": str(executable),
            "executable_sha256": sha(executable) if executable.is_file() else None,
            "runtime_libraries": libraries, "sqlite_version": sqlite3.sqlite_version}


def qualify():
    contract = json.loads((ROOT / CONTRACT_PATH).read_text(encoding="utf-8"))
    checks, failures = {}, []
    def check(name, operation):
        try:
            value = operation()
            if value is False:
                raise ValueError("requirement not satisfied")
            checks[name] = "PASS"
        except Exception as exc:
            checks[name] = "FAIL"
            failures.append({"requirement": name, "error": type(exc).__name__, "detail": str(exc)})
    check("implementation", lambda: platform.python_implementation() == contract["implementation"])
    check("version", lambda: list(sys.version_info[:2]) >= contract["minimum_version"])
    check("platform_architecture", lambda: sys.platform in contract["platforms"] and struct.calcsize("P") * 8 in contract["pointer_bits"])
    for module in contract["requirements"]["stdlib"]:
        check("stdlib:" + module, lambda m=module: importlib.import_module(m))
    if os.name == "posix":
        check("stdlib:resource", lambda: importlib.import_module("resource"))
    vector = {"z": "é", "a": [True, None, -1]}
    expected = b'{"a":[true,null,-1],"z":"\xc3\xa9"}'
    check("canonical", lambda: canonical(vector) == expected and json.loads(expected) == vector)
    check("sha256", lambda: hashlib.sha256(b"abc").hexdigest() == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")
    def filesystem_process_sqlite():
        import sqlite3
        with tempfile.TemporaryDirectory(prefix="lykoi runtime é ") as directory:
            base = Path(directory).resolve()
            original, destination = base / "a é.txt", base / "b é.txt"
            with original.open("x", encoding="utf-8") as stream:
                stream.write("é")
            try:
                original.open("x").close()
                raise AssertionError("exclusive create did not reject")
            except FileExistsError:
                pass
            original.replace(destination)
            assert destination.resolve().is_relative_to(base)
            assert destination.read_text(encoding="utf-8") == "é"
            database = base / "persistent sqlite.db"
            with closing(sqlite3.connect(database)) as db:
                db.execute("CREATE TABLE t (value TEXT PRIMARY KEY)")
                db.execute("BEGIN IMMEDIATE")
                db.execute("INSERT INTO t VALUES ('discard')")
                db.rollback()
                db.execute("INSERT INTO t VALUES ('é')")
                db.commit()
            child = subprocess.run([sys.executable, "-X", "utf8", "-c",
                "import sqlite3,sys; print(sqlite3.connect(sys.argv[1]).execute('SELECT value FROM t').fetchall()[0][0]); sys.exit(7)",
                str(database)], capture_output=True, text=True, encoding="utf-8", timeout=15)
            assert child.returncode == 7 and child.stdout.strip() == "é", child
            try:
                subprocess.run([sys.executable, "-c", "import time; time.sleep(10)"], timeout=0.1, capture_output=True)
                raise AssertionError("timeout not enforced")
            except subprocess.TimeoutExpired:
                pass
    check("filesystem_subprocess_sqlite_restart", filesystem_process_sqlite)
    def audit_process_native_denial():
        with tempfile.TemporaryDirectory(prefix="lykoi audit ") as directory:
            for source in ("import subprocess; subprocess.run(['unused-runtime-contract-command'])",
                           "import ctypes; ctypes.CDLL('unused-runtime-contract-library')",
                           "import os; os.system('unused-runtime-contract-command')"):
                child = subprocess.run([sys.executable, "-X", "utf8", str(ROOT / "src/lykoi_rehearsal/containment_worker.py")],
                                       input=source, cwd=directory, text=True, encoding="utf-8", capture_output=True, timeout=15)
                # Native import itself may be denied (ctypes loads kernel32 on
                # Windows). Require the actual guard's denial, not exception type
                # alone or a missing executable/library error.
                assert child.returncode != 0 and "PermissionError: CONTAINMENT_FAILURE: forbidden process/network/native API" in child.stderr, child.stderr
    check("audit_process_native_denial", audit_process_native_denial)
    def focused_tests():
        sys.path.insert(0, str(ROOT / "tests"))
        suite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromName(name) for name in TESTS)
        stream = io.StringIO()
        result = unittest.TextTestRunner(stream=stream, verbosity=1).run(suite)
        checks["focused_test_count"] = result.testsRun
        if not result.wasSuccessful() or result.skipped:
            raise AssertionError(stream.getvalue())
    check("focused_existing_tests", focused_tests)
    return {"status": "RUNTIME_INCOMPATIBLE" if failures else "RUNTIME_COMPATIBLE",
            "contract": contract_pin(), "checks": checks, "failures": failures,
            "stable_outputs": {"canonical_utf8_hex": expected.hex(), "canonical_sha256": digest(vector)},
            "provenance": provenance()}


def selected(interpreter=None):
    """Explicit path, environment path, then this interpreter; no PATH lookup."""
    return interpreter or os.environ.get("LYKOI_PYTHON") or sys.executable


def verify_selected(interpreter=None):
    executable = selected(interpreter)
    try:
        process = subprocess.run([executable, "-X", "utf8", "-m", "lykoi_runtime.verify", "verify", "--current"],
                                 cwd=ROOT, capture_output=True, text=True, encoding="utf-8", timeout=180)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"status": "RUNTIME_INCOMPATIBLE", "contract": contract_pin(), "checks": {},
                "failures": [{"requirement": "qualification_process", "error": type(exc).__name__, "detail": str(exc)}],
                "provenance": {"selected_interpreter": str(executable), "executed": False}}
    try:
        result = json.loads(process.stdout)
    except ValueError:
        return {"status": "RUNTIME_INCOMPATIBLE", "contract": contract_pin(), "checks": {},
                "failures": [{"requirement": "qualification_process", "error": "INVALID_QUALIFICATION_RESULT",
                              "exit_status": process.returncode, "detail": process.stderr}],
                "provenance": {"selected_interpreter": str(executable), "qualification_received": False}}
    if result["contract"] != contract_pin():
        raise RuntimeError("Runtime contract/procedure substitution")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["verify"])
    parser.add_argument("--interpreter")
    parser.add_argument("--current", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = qualify() if args.current else verify_selected(args.interpreter)
    text = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.output:
        with args.output.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(text)
    print(text, end="")
    return 0 if result["status"] == "RUNTIME_COMPATIBLE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
