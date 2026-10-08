"""Execute synthetic qualification and negative controls; persist honest evidence."""
import argparse
import io
import json
import os
from pathlib import Path
import platform
import socket
import subprocess
import sys
import tempfile
import unittest

from . import boundary as b


class EvidenceResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cases = []

    def addSuccess(self, test):
        super().addSuccess(test)
        self.cases.append({"test": test.id(), "status": "PASS"})

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.cases.append({"test": test.id(), "status": "SKIP", "reason": reason})

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.cases.append({"test": test.id(), "status": "FAIL"})

    def addError(self, test, err):
        super().addError(test, err)
        self.cases.append({"test": test.id(), "status": "ERROR"})


def qualify(destination):
    destination = Path(destination).absolute()
    destination.mkdir(parents=True, exist_ok=False)
    stream = io.StringIO()
    suite = unittest.defaultTestLoader.discover(str(Path(__file__).parent / "tests"))
    result = unittest.TextTestRunner(stream=stream, verbosity=2, resultclass=EvidenceResult).run(suite)
    (destination / "test-output.txt").write_text(stream.getvalue(), encoding="utf-8")
    with tempfile.TemporaryDirectory(prefix="r69-negative-") as temp:
        root = Path(temp)
        (root / "work").mkdir()
        (root / "forbidden.txt").write_text("synthetic forbidden sentinel", encoding="utf-8")
        (root / "AGENTS.md").write_text("synthetic inherited guidance sentinel", encoding="utf-8")
        # Deliberately unconfined negative control demonstrates that cwd/env/-I
        # do not restrict files or loopback networking. No repository findings read.
        with socket.socket() as listener:
            listener.bind(("127.0.0.1", 0)); listener.listen()
            port = listener.getsockname()[1]
            code = "import pathlib,socket,json; print(json.dumps({'forbidden_file_accessible':pathlib.Path('../forbidden.txt').read_text()=='synthetic forbidden sentinel','guidance_accessible':pathlib.Path('../AGENTS.md').read_text()=='synthetic inherited guidance sentinel','network_accessible':socket.create_connection(('127.0.0.1'," + str(port) + "),timeout=2) is not None}))"
            # Windows Winsock needs the OS installation directory. This is an
            # explicit negative-control-only allowlist, not a runner exception.
            env = {"SystemRoot": os.environ["SystemRoot"]} if sys.platform == "win32" else {}
            proc = subprocess.run([sys.executable, "-I", "-c", code], cwd=root / "work",
                                  env=env, capture_output=True, text=True, timeout=10, check=False)
            probes = {"returncode": proc.returncode, "environment_names": sorted(env),
                      "stdout": proc.stdout, "stderr": proc.stderr}
            if proc.returncode == 0:
                probes.update(json.loads(proc.stdout))
        package = root / "input"
        identity = b.create_package(package, {"task.md": b"Return SYNTHETIC_OK.\n"}, "synthetic")
        adapter = root / "fixture"
        adapter.write_bytes(b"nonexecutable synthetic fixture")
        config = {"provider": "synthetic-local", "model": "literal-fixture-1",
                  "adapter_sha256": b.digest(adapter.read_bytes()), "environment": {}, "tools": [],
                  "network": "none", "session": "new", "retrieval": "disabled",
                  "system_message": "Use only the supplied synthetic input."}
        record, anchor = b.invoke(package, identity, config, adapter, destination / "host-attempt")
    evidence = {"round": "R6.9", "classification": "R6_9_ISOLATION_CONTROL_GAP",
                "python": platform.python_version(), "platform": sys.platform,
                "tests_run": result.testsRun, "failures": len(result.failures),
                "errors": len(result.errors), "skips": len(result.skipped), "cases": result.cases,
                "negative_control": probes, "negative_control_is_isolation": False,
                "host_attempt_status": record["status"], "host_attempt_seal_sha256": anchor,
                "bubblewrap_available": b.sandbox_available(),
                "substantive_review_invocations": 0, "provider_model_invocations": 0,
                "linux_backend_qualification": "NOT_RUN",
                "scope": "Broker tests enforce data access; configuration/mock tests do not enforce OS isolation; fresh-process tests do not verify provider memory."}
    (destination / "qualification.json").write_bytes(b.canonical(evidence))
    print(json.dumps({k: evidence[k] for k in ("classification", "tests_run", "failures", "errors", "skips", "host_attempt_status")}))
    return 0 if result.wasSuccessful() and probes["returncode"] == 0 else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("destination")
    raise SystemExit(qualify(parser.parse_args().destination))
