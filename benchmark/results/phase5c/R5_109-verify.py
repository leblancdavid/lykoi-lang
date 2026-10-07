"""R5.109 generic and existing regressions; evidence before exposed transfer."""
import datetime
import importlib.util
import json
from pathlib import Path
import sys
import os
import re
import subprocess
import hashlib
from concurrent.futures import ThreadPoolExecutor

OUT = Path(__file__).resolve().parent
s = importlib.util.spec_from_file_location("checks109", OUT / "R5_107-verify.py")
prior = importlib.util.module_from_spec(s); s.loader.exec_module(prior)
checks = prior.checks
checks.COMMANDS.insert(0, ["-m", "unittest", "discover", "-s", "tests", "-p", "test_references.py", "-v"])
TREE = hashlib.sha256(b"".join(p.read_bytes() for parent in (checks.ROOT / "src", checks.ROOT / "tests") for p in sorted(parent.rglob("*.py")))).hexdigest()


def run(index_command):
    index, argv = index_command
    path = OUT / ("R5_109-CHECK-%02d-%s.json" % (index, TREE[:12]))
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    p = subprocess.run([sys.executable, *argv], cwd=checks.ROOT, env=dict(os.environ, PYTHONPATH=os.pathsep.join((str(checks.ROOT / "src"), str(checks.ROOT)))), capture_output=True, text=True, encoding="utf-8", timeout=1800)
    count = re.search(r"Ran (\d+) tests?", p.stderr)
    row = dict(implementation_test_tree_sha256=TREE, argv=[sys.executable, *argv], exit=p.returncode, tests=int(count.group(1)) if count else 0, stdout=p.stdout, stderr=p.stderr)
    with path.open("x", encoding="utf-8", newline="\n") as f:
        json.dump(row, f, indent=2); f.write("\n")
    print(argv, "exit", p.returncode, "tests", row["tests"], flush=True)
    return row


def main():
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with ThreadPoolExecutor(max_workers=2) as pool:
        rows = list(pool.map(run, enumerate(checks.COMMANDS)))
    result = dict(utc_started=started, utc_finished=datetime.datetime.now(datetime.timezone.utc).isoformat(), commands=rows, tests=sum(r["tests"] for r in rows), all_pass=all(r["exit"] == 0 for r in rows), scope="R5.109 typed references, integrity, quantification/reachability, compiler/backend, FRC/coverage/BDI/adequacy/V1, external and existing regressions")
    with (OUT / "R5_109-GENERIC-VERIFICATION.json").open("x", encoding="utf-8", newline="\n") as f:
        json.dump(result, f, indent=2); f.write("\n")
    print(result["tests"], result["all_pass"], flush=True)
    return int(not result["all_pass"])


if __name__ == "__main__": sys.exit(main())
