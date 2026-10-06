"""Current normal-path checks/captures and pretransfer implementation freeze.

Explicit public test selection only. No held-out requirements or historical
oracle discovery. Evidence is exclusive-create and is never overwritten.
"""
import datetime
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent


def write(name, value):
    with (OUT / name).open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False)
        stream.write("\n")


def file_hash(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def main():
    env = dict(os.environ, PYTHONPATH=str(ROOT / "src"), PYTHONUTF8="1")
    commands = [[sys.executable, "-m", "air_compiler.cli", op, "air/task_manager.json"] for op in ("validate", "safety")]
    for directory, pattern in [
        ("tests", "test_query_normal_path.py"), ("tests", "test_collection_query*.py"),
        ("tests", "test_compiler.py"), ("tests", "test_application.py"),
        ("tests", "test_authority_controller.py"), ("tests", "test_requirements_workspace.py"),
        ("tests", "test_sealed_pipeline.py"), ("tests", "test_public_rehearsal.py"),
        ("benchmark/evaluation", "test_behavioral_discovery_r5_82.py"),
        ("benchmark/evaluation", "test_implementation_adequacy_r5_81.py"),
        ("benchmark/evaluation", "test_formal_requirements_r5_80.py"),
        ("benchmark/evaluation", "test_benchmark_documents_v1.py"),
        ("benchmark/harness", "test_baseline.py"),
    ]:
        commands.append([sys.executable, "-m", "unittest", "discover", "-s", directory, "-p", pattern, "-v"])
    commands.append(["git", "diff", "--check"])
    logs = []
    for command in commands:
        result = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8", timeout=360)
        count = re.search(r"Ran (\d+) tests?", result.stderr)
        logs.append({"argv": command, "exit": result.returncode, "tests": int(count.group(1)) if count else None,
                     "stdout": result.stdout, "stderr": result.stderr})
        print(command[1:], "exit", result.returncode)
    write("R5_99-VERIFICATION-2.json", {"utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
          "model": "openai/gpt-6.1-sol", "provider": "OpenAI", "python": platform.python_version(),
          "commands": logs, "tests": sum(r["tests"] or 0 for r in logs),
          "all_pass": all(r["exit"] == 0 for r in logs),
          "development_correction": "Initial new suite 12/13 passed; missing schema anyOf handling corrected. First full run 279/280 passed: preserved R5.98 test asserts historical normal-V1 gap. Added explicit normal capability_profile selection to preserve historical routing while integrating the versioned extension. No benchmark semantics used for either correction.",
          "firewall_deviation": "A grep requested against this run's exact verification JSON searched its parent directory and returned B04 and later historical implementation logs. Requirement files were not opened, but behavior was indirectly exposed. B03 transfer omitted; no pristine benchmark-nonexposure claim."})
    if any(r["exit"] for r in logs):
        raise SystemExit("Checks failed; no generic freeze or transfer permitted")
    sys.path.insert(0, str(ROOT / "tests"))
    from test_query_normal_path import normal_run, task_capture
    from lykoi_workspace.query_corpus import captures
    records = []
    for capture in captures() + [task_capture()]:
        result = normal_run(capture)
        records.append({"input": capture["source"], "capture_id": capture["id"], "evidence": result})
        print(capture["id"], result["outcome"])
        expected = "COMPILATION_FAILURE" if capture["id"] == "mutating" else "NEEDS_CLARIFICATION" if capture["id"] == "ambiguous-case" else "BEHAVIORALLY_VERIFIED"
        if result["outcome"] != expected:
            raise SystemExit("Unexpected synthetic outcome; freeze refused")
    write("R5_99-SYNTHETIC-EVIDENCE.json", {"scope": "Source-bound active-agent formalization captures replayed through normal ModelAdapter/Workspace/Pipeline; real external processes; same-agent source/model/oracle", "cases": records})
    from lykoi_pipeline.controller import component_paths
    paths = component_paths() + ["src/air_compiler/cli.py", "src/lykoi_workspace/query_corpus.py",
             "src/lykoi_rehearsal/adapters.py", "tests/test_query_normal_path.py", "tests/test_collection_query.py",
             "tests/test_collection_query_behavior.py", "docs/collection-query-normal-path-v1.md",
             "schema/lykoi-contract-v1.schema.json", "benchmark/results/phase5c/R5_99-verify.py",
             "benchmark/results/phase5c/R5_99-SYNTHETIC-EVIDENCE.json", "benchmark/results/phase5c/R5_99-VERIFICATION-2.json"]
    write("R5_99-GENERIC-FREEZE.json", {"utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
          "head": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip(),
          "status": subprocess.run(["git", "status", "--short"], cwd=ROOT, capture_output=True, text=True, check=True).stdout,
          "files": {p: file_hash(p) for p in sorted(set(paths))},
          "rule": "Generic implementation/tests/corpus frozen before already-public transfer; no remediation after transfer. Optional B03 transfer cancelled after indirect later-benchmark disclosure.",
          "b04_requirement_file_read": False, "b04_and_later_log_disclosure": True,
          "benchmark_nonexposure_eligibility": False})


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT / "src"))
    sys.path.insert(0, str(ROOT))
    main()
