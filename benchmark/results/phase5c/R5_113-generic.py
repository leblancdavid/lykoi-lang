"""Publish generic evidence and accounting before the exposed transfer content lock."""
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess

from lykoi_workspace.authorization_corpus import captures, plan

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]


def load(name, file):
    s = importlib.util.spec_from_file_location(name, OUT / file)
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
    return m


def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def pins(paths): return {str(p.relative_to(ROOT)).replace("\\", "/"): digest(p) for p in sorted(set(paths)) if p.is_file()}
def implementation_pins():
    return pins(list((ROOT / "src").rglob("*.py")) + list((ROOT / "tests").glob("*.py")) + [ROOT / "air/task_manager.json", ROOT / "docs/prewrite-conditional-composition-v1.md", OUT / "R5_113-generic.py", OUT / "R5_113-verify.py", OUT / "R5_113-transfer.py"])
def history_pins():
    return pins([p for p in OUT.iterdir() if p.is_file() and not p.name.startswith("R5_113-")] + list((ROOT / "benchmark/requirements").glob("*.md")) + list((ROOT / "generated").glob("*")) + [ROOT / "docs/primary-value-interfaces-v1.md", ROOT / "docs/typed-computation-v1.md", ROOT / "docs/atomic-durable-history-v1.md", ROOT / "docs/persistent-references-v1.md", ROOT / "docs/semantic-kernel-audit-r5.108.md"])
def publish(name, value):
    with (OUT / name).open("x", encoding="utf-8", newline="\n") as f: json.dump(value, f, indent=2); f.write("\n")


def main():
    verification = OUT / "R5_113-GENERIC-VERIFICATION.json"
    verified = json.loads(verification.read_text(encoding="utf-8"))
    tree = hashlib.sha256(b"".join(p.read_bytes() for parent in (ROOT / "src", ROOT / "tests") for p in sorted(parent.rglob("*.py")))).hexdigest()
    assert verified["all_pass"] and verified["implementation_test_tree_sha256"] == tree
    before, history = implementation_pins(), history_pins()
    ev = load("evaluate113generic", "R5_103-evaluate.py")
    rows = []
    for r in captures():
        x = ev.evaluate(r["candidate"], plan(r)); rows.append(x)
        print(x["case"], x["first_blocker"], x.get("external_invocations", 0), flush=True)
    publish("R5_113-SYNTHETIC-EVIDENCE.json", dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), cases=rows, external_invocations=sum(x.get("external_invocations", 0) for x in rows), limitations=["Same-agent captures/inventories/oracles; synthetic approval; shared schema shape; not held-out generalization", "Trusted controlled-host probes and native signed-64 bounds are in source-bound test receipts, not counted as published pipeline invocations"]))
    assert all(x["first_blocker"] == "SUCCESS" for x in rows)
    prior_path = OUT / "R5_112-KERNEL-ACCOUNTING.json"
    prior = json.loads(prior_path.read_text(encoding="utf-8"))
    assert prior["final_count"] == 25
    accounting = dict(baseline_round="R5.112", baseline_source_sha256=digest(prior_path), baseline_kernel=prior["baseline_kernel"], preserved_additions=prior["preserved_additions"], baseline_count=25, additions=[dict(id="K26", concept="checked_elapsed_day_duration_conversion", relation="seconds=N*86400", input="signed_64_integer_elapsed_days", output="signed_64_duration_seconds", negative="preserve", overflow="reject", reason="16 additions can produce a coefficient of N at most 2^16=65536 < 86400. Constants do not increase that coefficient. K25 accepts duration, not an integer. Exact dimensioned conversion is new meaning; no loop or host coercion is licensed.", evidence=["Five-domain normal pipeline successor displacement", "Native signed-64 positive/negative boundaries", "Selected null and conversion overflow preserve durable bytes", "UTC leap-day and upper-year rejection"] )], final_count=26, constructs={"prewrite_role_owner_permitted_set": "existing predicate/selection/cardinality/type/guard composition K01-K10/K17-K22", "trusted_actor_host_source": "K04/K17/K20 interface authority, no authentication infrastructure", "conditional_update_and_creation": "selection/predicate/operation/atomic composition K10/K17/K21/K22", "created_record_dependency_images": "typed value and operation bindings K01/K02/K04/K17/K20/K22; backend topological assembly", "nullable_integer_and_instant_refinement": "K04/K05/K17/K19/K20 type/presence/guard/literal composition; no coercion", "related_parameter_omission_defaults": "existing K05/K19/K17 authority; not historical migration", "runtime_elapsed_day_conversion": "new explicit K26; not calendar recurrence or unrestricted multiplication"}, claim="Proposed architectural kernel 25 to 26; not minimum proof. No benchmark-specific primitive.")
    publish("R5_113-KERNEL-ACCOUNTING.json", accounting)
    assert before == implementation_pins() and history == history_pins()
    publish("R5_113-GENERIC-LOCK.json", dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), implementation=before, history=history, git_head=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(), verification_sha256=digest(verification), synthetic_evidence_sha256=digest(OUT / "R5_113-SYNTHETIC-EVIDENCE.json"), kernel_accounting_sha256=digest(OUT / "R5_113-KERNEL-ACCOUNTING.json"), rule="Generic implementation/spec/tests/evidence/accounting fixed before fresh exposed transfer. No post-outcome product repairs."))


if __name__ == "__main__": main()
