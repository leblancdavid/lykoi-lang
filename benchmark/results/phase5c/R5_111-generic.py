"""Publish generic computation evidence/accounting, then lock before transfer."""
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess

from lykoi_workspace.computation_corpus import captures, plan

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
    return pins(paths + [ROOT / "air/task_manager.json", ROOT / "docs/typed-computation-v1.md", OUT / "R5_111-generic.py", OUT / "R5_111-verify.py", OUT / "R5_111-transfer.py"])


def history_pins():
    paths = [p for p in OUT.iterdir() if p.is_file() and not p.name.startswith("R5_111-")]
    paths += list((ROOT / "benchmark/requirements").glob("*.md")) + list((ROOT / "generated").glob("*"))
    return pins(paths + [ROOT / "docs/semantic-kernel-audit-r5.108.md", ROOT / "docs/persistent-references-v1.md", ROOT / "docs/atomic-durable-history-v1.md", ROOT / "benchmark/baseline.md"])


def publish(name, value):
    with (OUT / name).open("x", encoding="utf-8", newline="\n") as f: json.dump(value, f, indent=2); f.write("\n")


def main():
    verification = OUT / "R5_111-GENERIC-VERIFICATION.json"
    verified = json.loads(verification.read_text(encoding="utf-8"))
    tree = hashlib.sha256(b"".join(p.read_bytes() for parent in (ROOT / "src", ROOT / "tests") for p in sorted(parent.rglob("*.py")))).hexdigest()
    assert verified["all_pass"] and verified["implementation_test_tree_sha256"] == tree
    before, history = implementation_pins(), history_pins()
    ev = load("compute111evaluator", "R5_103-evaluate.py")
    rows = []
    for r in captures():
        x = ev.evaluate(r["candidate"], plan(r)); rows.append(x)
        print(x["case"], x["first_blocker"], x.get("external_invocations", 0), flush=True)
    publish("R5_111-SYNTHETIC-EVIDENCE.json", dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), cases=rows, external_invocations=sum(x.get("external_invocations", 0) for x in rows), limitations=["Same-agent captures/inventories/oracles; synthetic approval; exposed synthetic development, not generalization"]))
    assert all(x["first_blocker"] == "SUCCESS" for x in rows)
    prior_path = OUT / "R5_110-KERNEL-ACCOUNTING.json"
    prior = json.loads(prior_path.read_text(encoding="utf-8"))
    baseline = prior["baseline_kernel"]
    assert len(baseline) == len(set(baseline)) == prior["final_count"] == 23 and prior["additions"] == []
    additions = [dict(id="K24", concept="checked_integer_addition", reason="Finite map does not supply the deterministic mathematical sum; replacing stored values cannot construct x+adjustment without this meaning", evidence=["inventory signed adjustment", "retry successor", "cardinality-derived ordinal"]), dict(id="K25", concept="fixed_duration_instant_displacement", original_candidate="offset", reason="Instant observation/ordering and integer addition do not define dimensioned UTC instant translation; fixed elapsed-second displacement adds independently observable meaning", evidence=["session/subscription expiry", "ordinary synthetic successor", "Gregorian/negative/fraction/range vectors"])]
    accounting = dict(baseline_round="R5.110", baseline_source_sha256=digest(prior_path), baseline_kernel=baseline, baseline_count=23, additions=additions, final_count=25, constructs={"integer_duration_types": "typed domains/policies", "value_binding_DAG": "K04/K17 composition", "cardinality_value": "K18/K10 composition", "computed_mutation_creation": "K04/K14/K17/K21/K22 composition", "increment": "K24 plus K05 literal one", "successor": "ordinary entity creation + computed fields + atomic coupled effects", "for_each": "existing finite pointwise map; unchanged", "finite_cardinality_domain": "K03/K10/K18 profile", "Event_Expression_Counter_Sequence": "not admitted", "subtraction": "not independently justified; signed adjustments suffice for tested authority", "calendar_month_year": "unresolved/not admitted", "offset": "K25 fixed-duration displacement admitted; broad calendar offsets unresolved"}, pressure="Do not count map as a license for arbitrary transformations; two exact new operator meanings, not a general expression language")
    publish("R5_111-KERNEL-ACCOUNTING.json", accounting)
    assert before == implementation_pins() and history == history_pins()
    publish("R5_111-GENERIC-LOCK.json", dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), implementation=before, history=history, git_head=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(), verification_sha256=digest(verification), synthetic_evidence_sha256=digest(OUT / "R5_111-SYNTHETIC-EVIDENCE.json"), kernel_accounting_sha256=digest(OUT / "R5_111-KERNEL-ACCOUNTING.json"), rule="All generic semantics/spec/tests/accounting fixed before fresh transfer; no post-transfer semantic repairs"))


if __name__ == "__main__": main()
