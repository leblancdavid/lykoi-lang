"""Publish generic multi-domain evidence, exact kernel accounting and content lock."""
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess

from lykoi_workspace.reference_corpus import captures, plan

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
BASELINE = ["record schema", "field", "finite sequence", "var", "literal", "equals", "and", "not", "contains", "selection", "trim", "map(trim)", "stable_unique", "transition", "instant", "before", "operation contract", "cardinality", "input presence", "typed resource/capability authority", "durable state", "atomic commit"]


def load(name, filename):
    s = importlib.util.spec_from_file_location(name, OUT / filename)
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
    return m


def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def pins(paths):
    return {str(p.relative_to(ROOT)).replace("\\", "/"): digest(p) for p in sorted(set(paths)) if p.is_file()}


def implementation_pins():
    paths = list((ROOT / "src").rglob("*.py")) + list((ROOT / "tests").glob("*.py"))
    paths += [ROOT / "air/task_manager.json", ROOT / "docs/persistent-references-v1.md", OUT / "R5_109-verify.py", OUT / "R5_109-generic.py"]
    return pins(paths)


def history_pins():
    paths = [p for p in OUT.iterdir() if p.is_file() and not p.name.startswith("R5_109-")]
    paths += list((ROOT / "benchmark/requirements").glob("*.md")) + list((ROOT / "generated").glob("*"))
    paths += [ROOT / "docs/semantic-kernel-audit-r5.108.md", ROOT / "benchmark/baseline.md"]
    return pins(paths)


def publish(name, value):
    with (OUT / name).open("x", encoding="utf-8", newline="\n") as f:
        json.dump(value, f, indent=2); f.write("\n")


def main():
    verification = OUT / "R5_109-GENERIC-VERIFICATION.json"
    assert json.loads(verification.read_text(encoding="utf-8"))["all_pass"]
    before, history = implementation_pins(), history_pins()
    ev = load("reference109evaluator", "R5_103-evaluate.py")
    rows = []
    for r in captures():
        row = ev.evaluate(r["candidate"], plan(r)); rows.append(row)
        print(row["case"], row["first_blocker"], row.get("external_invocations", 0), flush=True)
    publish("R5_109-SYNTHETIC-EVIDENCE.json", dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), cases=rows, external_invocations=sum(r.get("external_invocations", 0) for r in rows), limitations=["Same-agent source captures/inventories/oracles and synthetic approval; no held-out generalization"]))
    assert all(r["first_blocker"] == "SUCCESS" for r in rows)
    accounting = dict(baseline_round="R5.108", baseline_kernel=BASELINE, baseline_count=22, baseline_source_sha256=digest(ROOT / "docs/semantic-kernel-audit-r5.108.md"), additions=[dict(id="K23", concept="finite nonempty-path reachability", classification="new core candidate", evidence="Project prerequisites and Category parents; 81-record path and cyclic termination probes", decomposition_failure="No recursive/fixpoint/transitive-path relation in the inherited kernel; fixed-depth selection unrolling is incomplete")], final_count=23, constructs={"typed_reference": "existing-core composition", "reference_collection": "existing-core composition", "existence_check": "existing-core composition", "reverse_restrict": "existing-core composition", "EXISTS_NONE_ALL": "existing-core composition", "extent": "existing-core composition", "finite_domain": "composition/profile", "typed_bindings": "composition/profile", "stable_remove": "existing-core composition", "one_store_commit": "existing-core composition/scope refinement", "reference_FRC_V1_BDI": "composition/profile", "reachable": "new core candidate", "JSON_envelope_lock_visited_worklist": "backend-only implementation concept"})
    assert len(accounting["baseline_kernel"]) == len(set(accounting["baseline_kernel"])) == 22
    assert accounting["final_count"] == accounting["baseline_count"] + len(accounting["additions"])
    publish("R5_109-KERNEL-ACCOUNTING.json", accounting)
    assert before == implementation_pins() and history == history_pins()
    publish("R5_109-GENERIC-LOCK.json", dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), implementation=before, history=history, git_head=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(), verification_sha256=digest(verification), synthetic_evidence_sha256=digest(OUT / "R5_109-SYNTHETIC-EVIDENCE.json"), kernel_accounting_sha256=digest(OUT / "R5_109-KERNEL-ACCOUNTING.json"), rule="Generic implementation/spec/tests stay byte-identical throughout R5.109 exposed transfer; no implementation repairs after outcomes"))


if __name__ == "__main__": main()
