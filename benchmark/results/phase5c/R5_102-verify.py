"""R5.102 prospective verification; exclusive records preserve historical evidence."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
COMMANDS = [
    ["-m", "unittest", "discover", "-s", "tests", "-p", pattern, "-v"] for pattern in (
        "test_scalar_normal_path.py", "test_query_normal_path.py", "test_collection_query.py", "test_collection_query_behavior.py",
        "test_compiler.py", "test_application.py", "test_requirements_workspace.py", "test_sealed_pipeline.py", "test_authority_controller.py", "test_public_rehearsal.py")]
COMMANDS += [["-m", "unittest", "discover", "-s", "benchmark/evaluation", "-p", pattern, "-v"] for pattern in (
    "test_formal_requirements_r5_80.py", "test_behavioral_discovery_r5_82.py", "test_implementation_adequacy_r5_81.py", "test_benchmark_documents_v1.py", "test_source_coverage_r5_84.py")]
COMMANDS += [["-m", "unittest", "discover", "-s", "benchmark/harness", "-p", "test_baseline.py", "-v"],
             ["-m", "air_compiler.cli", "validate", "air/task_manager.json"], ["-m", "air_compiler.cli", "safety", "air/task_manager.json"]]


def main():
    logs = []
    start = datetime.datetime.now(datetime.timezone.utc).isoformat()
    for argv in COMMANDS:
        p = subprocess.run([sys.executable, *argv], cwd=ROOT, env=dict(os.environ, PYTHONPATH=str(ROOT / "src"), PYTHONUTF8="1"),
                           capture_output=True, text=True, encoding="utf-8", timeout=240)
        count = re.search(r"Ran (\d+) tests?", p.stderr)
        row = {"argv": [sys.executable, *argv], "exit": p.returncode, "tests": int(count.group(1)) if count else 0, "stdout": p.stdout, "stderr": p.stderr}
        logs.append(row)
        print(argv, "exit", p.returncode, "tests", row["tests"], flush=True)
    baseline = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.glob("R5_101-*") if p.is_file()}
    result = {"utc_started": start, "utc_finished": datetime.datetime.now(datetime.timezone.utc).isoformat(), "commands": logs,
              "tests": sum(r["tests"] for r in logs), "all_pass": all(r["exit"] == 0 for r in logs), "r5_101_baseline_files": baseline,
              "limitations": ["Historical FRC/V1 physical-byte pin assertions may differ in this CRLF checkout; failures retained verbatim, never rewritten", "No infrastructure qualification or repair"]}
    with (OUT / "R5_102-VERIFICATION.json").open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(result, stream, indent=2); stream.write("\n")
    return int(any(r["exit"] for r in logs))


if __name__ == "__main__":
    sys.exit(main())
