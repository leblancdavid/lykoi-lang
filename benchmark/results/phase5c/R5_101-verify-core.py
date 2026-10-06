"""Supplement initial snapshot with existing FRC/BDI/adequacy core suites."""
import datetime
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
logs = []
for pattern in ("test_formal_requirements_r5_80.py", "test_behavioral_discovery_r5_82.py", "test_implementation_adequacy_r5_81.py"):
    command = [sys.executable, "-m", "unittest", "discover", "-s", "benchmark/evaluation", "-p", pattern, "-v"]
    p = subprocess.run(command, cwd=ROOT, env=dict(os.environ, PYTHONPATH=str(ROOT / "src"), PYTHONUTF8="1"),
                       capture_output=True, text=True, encoding="utf-8", timeout=120)
    count = re.search(r"Ran (\d+) tests?", p.stderr)
    logs.append({"argv": command, "exit": p.returncode, "tests": int(count.group(1)) if count else 0,
                 "stdout": p.stdout, "stderr": p.stderr})
    print(pattern, "exit", p.returncode, "tests", logs[-1]["tests"])
with (OUT / "R5_101-CORE-VERIFICATION.json").open("x", encoding="utf-8", newline="\n") as stream:
    json.dump({"utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "commands": logs,
               "all_pass": all(c["exit"] == 0 for c in logs), "tests": sum(c["tests"] for c in logs)}, stream, indent=2)
    stream.write("\n")
sys.exit(int(any(c["exit"] for c in logs)))
