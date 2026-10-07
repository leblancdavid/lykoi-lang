"""Generic external evidence, exact inherited kernel and pre-transfer content lock."""
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess

from lykoi_workspace.atomic_state_corpus import captures, plan

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]


def load(name, file):
    s = importlib.util.spec_from_file_location(name, OUT / file)
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
    return m


def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def pins(paths):
    return {str(p.relative_to(ROOT)).replace("\\", "/"): digest(p) for p in sorted(set(paths)) if p.is_file()}


def implementation_pins():
    paths = list((ROOT / "src").rglob("*.py")) + list((ROOT / "tests").glob("*.py"))
    return pins(paths + [ROOT / "air/task_manager.json", ROOT / "docs/atomic-durable-history-v1.md", OUT / "R5_110-generic.py", OUT / "R5_110-verify.py"])


def history_pins():
    paths = [p for p in OUT.iterdir() if p.is_file() and not p.name.startswith("R5_110-")]
    paths += list((ROOT / "benchmark/requirements").glob("*.md")) + list((ROOT / "generated").glob("*"))
    return pins(paths + [ROOT / "docs/semantic-kernel-audit-r5.108.md", ROOT / "docs/persistent-references-v1.md", ROOT / "benchmark/baseline.md"])


def publish(name, value):
    with (OUT / name).open("x", encoding="utf-8", newline="\n") as f: json.dump(value, f, indent=2); f.write("\n")


def main():
    verification = OUT / "R5_110-GENERIC-VERIFICATION.json"
    assert json.loads(verification.read_text(encoding="utf-8"))["all_pass"]
    before, history = implementation_pins(), history_pins()
    ev = load("atomic110evaluator", "R5_103-evaluate.py")
    rows = []
    for r in captures():
        row = ev.evaluate(r["candidate"], plan(r)); rows.append(row)
        print(row["case"], row["first_blocker"], row.get("external_invocations", 0), flush=True)
    publish("R5_110-SYNTHETIC-EVIDENCE.json", dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), cases=rows, external_invocations=sum(r.get("external_invocations", 0) for r in rows), limitations=["Same-agent source captures/inventories/oracles and synthetic approval; not held-out generalization"]))
    assert all(r["first_blocker"] == "SUCCESS" for r in rows)
    prior_path = OUT / "R5_109-KERNEL-ACCOUNTING.json"
    prior = json.loads(prior_path.read_text(encoding="utf-8"))
    baseline = prior["baseline_kernel"] + [x["concept"] for x in prior["additions"]]
    assert len(baseline) == len(set(baseline)) == prior["final_count"] == 23
    accounting = dict(baseline_round="R5.109", baseline_source_sha256=digest(prior_path), baseline_kernel=baseline, baseline_count=23, additions=[], final_count=23, constructs={"typed_history_entity": "existing-core composition", "bounded_coupled_creations": "existing-core composition/profile", "occurrence_order": "existing-core composition", "timestamp_id_order": "existing-core composition", "shared_clock_identity_resources": "existing-core composition", "history_CollectionQuery": "existing-core composition/profile", "append_only_operation_restriction": "existing-core composition", "FRC_BDI_V1": "composition/profile", "candidate_ContextVar_JSON": "backend-only concept"}, pressure={"Event_Audit_Log": "No extra observable meaning beyond ordinary typed durable state", "coupled_effect_transaction": "Existing atomic commit frame over a bounded candidate", "ordered_effect": "Internal evaluation unobservable; secondary occurrence order is finite sequence authority", "numeric_sequence": "Not admitted; cardinality-derived ordinal needs missing normal integer/value binding and source authority; arbitrary counter/max successor requires arithmetic outside scope"})
    publish("R5_110-KERNEL-ACCOUNTING.json", accounting)
    assert before == implementation_pins() and history == history_pins()
    publish("R5_110-GENERIC-LOCK.json", dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), implementation=before, history=history, git_head=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(), verification_sha256=digest(verification), synthetic_evidence_sha256=digest(OUT / "R5_110-SYNTHETIC-EVIDENCE.json"), kernel_accounting_sha256=digest(OUT / "R5_110-KERNEL-ACCOUNTING.json"), rule="Generic semantics/spec/tests remain byte-identical through all R5.110 exposed transfer outcomes"))


if __name__ == "__main__": main()
