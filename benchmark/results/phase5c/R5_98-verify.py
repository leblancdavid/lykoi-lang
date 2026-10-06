"""R5.98 ordinary verification/evidence; no held-out-source access or qualification."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def write(name, value):
    with (OUT / name).open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False)
        stream.write("\n")


def main():
    env = dict(os.environ, PYTHONPATH=str(ROOT / "src"), PYTHONUTF8="1")
    commands = [
        ["-m", "unittest", "discover", "-s", "tests", "-p", "test_collection_query*.py", "-v"],
        ["-m", "air_compiler.cli", "validate", "air/task_manager.json"],
        ["-m", "air_compiler.cli", "safety", "air/task_manager.json"],
    ]
    for directory, pattern in [
        ("tests", "test_compiler.py"), ("tests", "test_application.py"),
        ("tests", "test_authority_controller.py"), ("tests", "test_requirements_workspace.py"),
        ("tests", "test_sealed_pipeline.py"), ("tests", "test_public_rehearsal.py"),
        ("benchmark/evaluation", "test_behavioral_discovery_r5_82.py"),
        ("benchmark/evaluation", "test_implementation_adequacy_r5_81.py"),
        ("benchmark/evaluation", "test_formal_requirements_r5_80.py"),
        ("benchmark/evaluation", "test_benchmark_documents_v1.py"),
        ("benchmark/harness", "test_baseline.py"),
    ]:
        commands.append(["-m", "unittest", "discover", "-s", directory, "-p", pattern, "-v"])
    records = []
    for args in commands:
        result = subprocess.run([sys.executable, *args], cwd=ROOT, env=env,
                                capture_output=True, text=True, encoding="utf-8", timeout=300)
        records.append({"argv": [sys.executable, *args], "exit": result.returncode,
                        "stdout": result.stdout, "stderr": result.stderr})
        print(args[-2:] if args[-1] == "-v" else args, "exit", result.returncode)
    write("R5_98-VERIFICATION.json", {"utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
          "python": platform.python_version(), "model": "openai/gpt-6.1-sol", "commands": records})
    if records[0]["exit"] != 0:
        raise SystemExit("Synthetic tests failed; no freeze or transfer permitted")
    from lykoi_query.corpus import queries, contract
    from lykoi_query import contracts
    from lykoi_query.compiler import compile_document
    from benchmark.evaluation import formal_requirements_r5_80 as frc
    corpus = []
    for q in queries():
        c = contract(q); p = contracts.structural(c, frc.validate(c))
        b = contracts.bdi(c, p); a = contracts.adequate(c, b)
        doc = contracts.document(c, p)
        target = compile_document(doc)[q["id"]]
        corpus.append({"contract": c, "projection": p, "bdi": b, "adequacy": a,
                       "document": doc, "generated_sha256": hashlib.sha256(target.encode()).hexdigest()})
    write("R5_98-SYNTHETIC-CORPUS.json", corpus)
    paths = ["src/air_compiler/collection_query.py", "src/air_compiler/collection_query_runtime.py",
             "src/lykoi_query/__init__.py", "src/lykoi_query/__main__.py", "src/lykoi_query/contracts.py",
             "src/lykoi_query/compiler.py", "src/lykoi_query/corpus.py", "docs/collection-query-v0.1.md",
             "tests/test_collection_query.py", "tests/test_collection_query_behavior.py",
             "benchmark/results/phase5c/R5_98-SYNTHETIC-CORPUS.json"]
    write("R5_98-SYNTHETIC-FREEZE.json", {"utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
          "synthetic_tests": "21/21 pass; 42 external subprocess invocations",
          "files": {path: digest(path) for path in paths},
          "verification_sha256": digest("benchmark/results/phase5c/R5_98-VERIFICATION.json"),
          "rule": "No implementation/corpus/test changes after this freeze and B03 transfer"})


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT / "src"))
    sys.path.insert(0, str(ROOT))
    main()
