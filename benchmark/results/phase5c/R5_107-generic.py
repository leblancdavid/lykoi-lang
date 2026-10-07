"""Publish synthetic behavior and lock generic implementation before transfer."""
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess

from lykoi_workspace.interface_corpus import captures, plan

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]


def load(name, filename):
    s = importlib.util.spec_from_file_location(name, OUT / filename)
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
    return m


prior = load("pins106for107", "R5_106-generic.py")
publish = prior.publish


def implementation_pins():
    pins = prior.implementation_pins()
    paths = [ROOT / "docs/predicate-value-interfaces-v1.md", OUT / "R5_107-generic.py", OUT / "R5_107-verify.py"]
    pins.update({str(p.relative_to(ROOT)).replace("\\", "/"): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})
    return pins


def history_pins():
    pins = prior.history_pins()
    pins.update({str(p.relative_to(ROOT)).replace("\\", "/"): hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.glob("R5_106-*") if p.is_file()})
    return pins


def main():
    v = OUT / "R5_107-GENERIC-FINAL-VERIFICATION-2.json"
    assert json.loads(v.read_text(encoding="utf-8"))["all_pass"]
    pins, history = implementation_pins(), history_pins()
    ev = load("synthetic107evaluator", "R5_103-evaluate.py")
    rows = []
    for r in captures():
        row = ev.evaluate(r["candidate"], plan(r)); rows.append(row)
        print(row["case"], row["first_blocker"], row.get("external_invocations", 0), flush=True)
    publish("R5_107-SYNTHETIC-FINAL-EVIDENCE-2.json", dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), cases=rows, external_invocations=sum(r.get("external_invocations", 0) for r in rows), limitations=["Same-agent captures/inventory/oracle; synthetic approval; controlled-clock subprocess in generic tests"]))
    assert all(r["first_blocker"] == "SUCCESS" for r in rows)
    assert pins == implementation_pins() and history == history_pins()
    publish("R5_107-GENERIC-LOCK-3.json", dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), implementation=pins, history=history, git_head=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(), verification_sha256=hashlib.sha256(v.read_bytes()).hexdigest(), supersedes="R5_107-GENERIC-LOCK-2.json before any transfer outcome: reuse required-CLI rejection with declared query type errors", rule="Generic implementation/spec/tests immutable through R5.107 exposed transfer; no outcome-driven repairs"))


if __name__ == "__main__": main()
