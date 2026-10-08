"""R5.113 source-bound receipts using existing regression entrypoints."""
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
s = importlib.util.spec_from_file_location("checks113prior", OUT / "R5_112-verify.py")
prior = importlib.util.module_from_spec(s); s.loader.exec_module(prior)
COMMANDS = [["-m", "unittest", "discover", "-s", "tests", "-p", "test_authorization_composition.py", "-v"], *prior.COMMANDS]
TREE = hashlib.sha256(b"".join(p.read_bytes() for parent in (ROOT / "src", ROOT / "tests") for p in sorted(parent.rglob("*.py")))).hexdigest()


def run(pair):
    index, argv = pair
    path = OUT / ("R5_113-CHECK-%02d-%s.json" % (index, TREE[:12]))
    if path.exists(): return json.loads(path.read_text(encoding="utf-8"))
    p = subprocess.run([sys.executable, *argv], cwd=ROOT, env=dict(os.environ, PYTHONPATH=os.pathsep.join((str(ROOT / "src"), str(ROOT)))), capture_output=True, text=True, encoding="utf-8", timeout=4800)
    count = re.search(r"Ran (\d+) tests?", p.stderr)
    row = dict(implementation_test_tree_sha256=TREE, argv=[sys.executable, *argv], exit=p.returncode, tests=int(count.group(1)) if count else 0, stdout=p.stdout, stderr=p.stderr)
    with path.open("x", encoding="utf-8", newline="\n") as f: json.dump(row, f, indent=2); f.write("\n")
    print(argv, "exit", p.returncode, "tests", row["tests"], flush=True)
    return row


def main():
    with ThreadPoolExecutor(max_workers=2) as pool: rows = list(pool.map(run, enumerate(COMMANDS)))
    result = dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), implementation_test_tree_sha256=TREE, commands=rows, tests=sum(r["tests"] for r in rows), all_pass=all(r["exit"] == 0 for r in rows), scope="Prewrite permissions/trusted host/conditional primary and secondary effects/dependencies/duration/refinement, all inherited normal FRC/reconciliation/structural/BDI/adequacy/V1/compiler/persistence/atomic/external regressions")
    if result["all_pass"]:
        with (OUT / "R5_113-GENERIC-VERIFICATION.json").open("x", encoding="utf-8", newline="\n") as f: json.dump(result, f, indent=2); f.write("\n")
    print(result["tests"], result["all_pass"], flush=True)
    return int(not result["all_pass"])


if __name__ == "__main__": sys.exit(main())
