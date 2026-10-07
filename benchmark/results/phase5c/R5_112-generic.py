"""R5.112 synthetic evidence/accounting and content lock before exposed transfer."""
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess

from lykoi_workspace.primary_corpus import captures, plan

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]


def load(name, file):
    s = importlib.util.spec_from_file_location(name, OUT / file)
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
    return m


def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def pins(paths): return {str(p.relative_to(ROOT)).replace("\\", "/"): digest(p) for p in sorted(set(paths)) if p.is_file()}
def implementation_pins():
    return pins(list((ROOT / "src").rglob("*.py")) + list((ROOT / "tests").glob("*.py")) + [ROOT / "air/task_manager.json", ROOT / "docs/primary-value-interfaces-v1.md", OUT / "R5_112-generic.py", OUT / "R5_112-verify.py", OUT / "R5_112-transfer.py"])
def history_pins():
    return pins([p for p in OUT.iterdir() if p.is_file() and not p.name.startswith("R5_112-")] + list((ROOT / "benchmark/requirements").glob("*.md")) + list((ROOT / "generated").glob("*")) + [ROOT / "docs/typed-computation-v1.md", ROOT / "docs/atomic-durable-history-v1.md", ROOT / "docs/persistent-references-v1.md", ROOT / "docs/semantic-kernel-audit-r5.108.md"])
def publish(name, value):
    with (OUT / name).open("x", encoding="utf-8", newline="\n") as f: json.dump(value, f, indent=2); f.write("\n")


def main():
    verification = OUT / "R5_112-GENERIC-VERIFICATION.json"
    verified = json.loads(verification.read_text(encoding="utf-8"))
    tree = hashlib.sha256(b"".join(p.read_bytes() for parent in (ROOT / "src", ROOT / "tests") for p in sorted(parent.rglob("*.py")))).hexdigest()
    assert verified["all_pass"] and verified["implementation_test_tree_sha256"] == tree
    before, history = implementation_pins(), history_pins()
    ev = load("evaluate112generic", "R5_103-evaluate.py")
    rows = []
    for r in captures():
        x = ev.evaluate(r["candidate"], plan(r)); rows.append(x)
        print(x["case"], x["first_blocker"], x.get("external_invocations", 0), flush=True)
    publish("R5_112-SYNTHETIC-EVIDENCE.json", dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), cases=rows, external_invocations=sum(x.get("external_invocations", 0) for x in rows), limitations=["Same-agent captures/inventories/oracles; synthetic approval; not held-out generalization"]))
    assert all(x["first_blocker"] == "SUCCESS" for x in rows)
    prior_path = OUT / "R5_111-KERNEL-ACCOUNTING.json"
    prior = json.loads(prior_path.read_text(encoding="utf-8"))
    assert prior["final_count"] == 25 and len(prior["baseline_kernel"]) == 23 and len(prior["additions"]) == 2
    accounting = dict(baseline_round="R5.111", baseline_source_sha256=digest(prior_path), baseline_kernel=prior["baseline_kernel"], preserved_additions=prior["additions"], baseline_count=25, additions=[], final_count=25, constructs={"primary_integer_nullable_creation_migration_query": "profile/interface integration K01/K02/K04/K05/K17/K19/K21", "explicit_primary_actor_context": "profile/interface integration K04/K17/K20; not authentication", "absolute_UTC_day_at_explicit_midnight": "profile/representation integration of existing K15 instant, not displacement", "numeric_primary_history": "existing-core composition K10/K18/K24/K21/K22", "same_primary_successor": "existing-core composition ordinary complete typed creation K14/K17/K21/K22", "private_candidate_context_validation": "backend-only implementation", "runtime_N_days_to_seconds": "unsupported; dimensional/scaling pressure documented before any kernel proposal", "conditional_secondary_membership_and_created_image": "unsupported interface composition"}, claim="25 concepts retained, not minimum proof; targeted interfaces partially closed")
    publish("R5_112-KERNEL-ACCOUNTING.json", accounting)
    assert before == implementation_pins() and history == history_pins()
    publish("R5_112-GENERIC-LOCK.json", dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), implementation=before, history=history, git_head=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(), verification_sha256=digest(verification), synthetic_evidence_sha256=digest(OUT / "R5_112-SYNTHETIC-EVIDENCE.json"), kernel_accounting_sha256=digest(OUT / "R5_112-KERNEL-ACCOUNTING.json"), rule="All generic semantics/spec/tests/accounting fixed before fresh transfer; no post-transfer semantic repairs"))


if __name__ == "__main__": main()
