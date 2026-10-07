"""Source-bound generic computation and existing regression verification."""
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
s = importlib.util.spec_from_file_location("prior111checks", OUT / "R5_110-verify.py")
prior = importlib.util.module_from_spec(s); s.loader.exec_module(prior)
COMMANDS = [["-m", "unittest", "discover", "-s", "tests", "-p", "test_computation.py", "-v"], *prior.COMMANDS]
TREE = hashlib.sha256(b"".join(p.read_bytes() for parent in (ROOT / "src", ROOT / "tests") for p in sorted(parent.rglob("*.py")))).hexdigest()


def prior_test_tree():
    # Prove the sole post-regression edit is the superseded integer rejection
    # assertion. All other source/test bytes are exactly those already tested.
    new = '''        # R5.111 admits explicitly bounded integer equality/order; the old
        # pre-computation rejection is superseded, not a historical result edit.
        integer = dict(type="integer", domain=[])
        validate(compare(operand("literal", integer, value=1), operand("literal", integer, value=1)))
        for typ in (dict(type="boolean", domain=[], nullable=True),):'''
    old = '''        for typ in (dict(type="integer", domain=[]), dict(type="boolean", domain=[], nullable=True)):'''
    contents = []
    for parent in (ROOT / "src", ROOT / "tests"):
        for p in sorted(parent.rglob("*.py")):
            value = p.read_bytes()
            if p == ROOT / "tests/test_predicates.py":
                assert new.encode() in value
                value = value.replace(new.encode(), old.encode())
            contents.append(value)
    return hashlib.sha256(b"".join(contents)).hexdigest()


def run(index_command):
    index, argv = index_command
    path = OUT / ("R5_111-CHECK-%02d-%s.json" % (index, TREE[:12]))
    if path.exists(): return json.loads(path.read_text(encoding="utf-8"))
    old_tree = prior_test_tree()
    old_path = OUT / ("R5_111-CHECK-%02d-%s.json" % (index, old_tree[:12]))
    if "test_predicates.py" not in argv and old_path.exists():
        old = json.loads(old_path.read_text(encoding="utf-8"))
        assert old["implementation_test_tree_sha256"] == old_tree and old["argv"] == [sys.executable, *argv]
        if old["exit"] == 0:
            old["applies_to_current_tree_sha256"] = TREE
            old["reuse_proof"] = dict(only_changed_file="tests/test_predicates.py", reconstructed_prior_tree_sha256=old_tree, receipt_sha256=hashlib.sha256(old_path.read_bytes()).hexdigest(), rule="All product/test bytes unchanged except superseded integer rejection assertion; affected predicate suite rerun")
            return old
    p = subprocess.run([sys.executable, *argv], cwd=ROOT, env=dict(os.environ, PYTHONPATH=os.pathsep.join((str(ROOT / "src"), str(ROOT)))), capture_output=True, text=True, encoding="utf-8", timeout=4800)
    count = re.search(r"Ran (\d+) tests?", p.stderr)
    row = dict(implementation_test_tree_sha256=TREE, argv=[sys.executable, *argv], exit=p.returncode, tests=int(count.group(1)) if count else 0, stdout=p.stdout, stderr=p.stderr)
    with path.open("x", encoding="utf-8", newline="\n") as f: json.dump(row, f, indent=2); f.write("\n")
    print(argv, "exit", p.returncode, "tests", row["tests"], flush=True)
    return row


def main():
    with ThreadPoolExecutor(max_workers=2) as pool: rows = list(pool.map(run, enumerate(COMMANDS)))
    result = dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), implementation_test_tree_sha256=TREE, commands=rows, tests=sum(r["tests"] for r in rows), all_pass=all(r["exit"] == 0 for r in rows), scope="Typed computation, integers/cardinality/duration, normal FRC/coverage/BDI/V1, compiler, external atomic behavior and existing regressions")
    if result["all_pass"]:
        with (OUT / "R5_111-GENERIC-VERIFICATION.json").open("x", encoding="utf-8", newline="\n") as f: json.dump(result, f, indent=2); f.write("\n")
    print(result["tests"], result["all_pass"], flush=True)
    return int(not result["all_pass"])


if __name__ == "__main__": sys.exit(main())
