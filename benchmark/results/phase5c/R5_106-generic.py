"""Publish synthetic normal-path evidence and lock before any transfer outcome."""
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess

from lykoi_workspace.predicate_corpus import captures, plan

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]


def load(name, filename):
    s = importlib.util.spec_from_file_location(name, OUT / filename)
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
    return m


prior = load("pins105for106", "R5_105-generic.py")


def implementation_pins():
    pins = prior.implementation_pins()
    paths = [ROOT / "docs/typed-predicates-v1.md", OUT / "R5_106-generic.py", OUT / "R5_106-verify.py"]
    pins.update({str(p.relative_to(ROOT)).replace("\\", "/"): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})
    return pins


def history_pins():
    pins = prior.history_pins()
    pins.update({str(p.relative_to(ROOT)).replace("\\", "/"): hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.glob("R5_105-*") if p.is_file()})
    return pins


publish = prior.publish


def main():
    v = OUT / "R5_106-GENERIC-FINAL-VERIFICATION-2.json"
    assert json.loads(v.read_text(encoding="utf-8"))["all_pass"]
    pins, history = implementation_pins(), history_pins()
    ev = load("synthetic106evaluator", "R5_103-evaluate.py")
    rows = []
    for r in captures():
        row = ev.evaluate(r["candidate"], plan(r)); rows.append(row)
        print(row["case"], row["first_blocker"], row.get("external_invocations", 0), flush=True)
    publish("R5_106-SYNTHETIC-FINAL-EVIDENCE.json", dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), cases=rows,
        external_invocations=sum(r.get("external_invocations", 0) for r in rows), limitations=["Same-agent captures/inventory/oracle; synthetic approval; development evidence only"]))
    assert all(r["first_blocker"] == "SUCCESS" for r in rows)
    assert pins == implementation_pins() and history == history_pins()
    publish("R5_106-GENERIC-LOCK.json", dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), implementation=pins, history=history,
        git_head=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(), verification_sha256=hashlib.sha256(v.read_bytes()).hexdigest(),
        rule="Implementation/spec/tests immutable through R5.106 exposed transfer; no outcome-driven repairs"))


if __name__ == "__main__": main()
