"""Publish synthetic evidence and unchanged kernel, then lock before transfer."""
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess

from lykoi_workspace.historical_corpus import captures, plan

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]


def load(name, file):
    s = importlib.util.spec_from_file_location(name, OUT / file)
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
    return m


def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def pins(paths): return {str(p.relative_to(ROOT)).replace("\\", "/"): digest(p) for p in sorted(set(paths)) if p.is_file()}
def implementation_pins():
    return pins(list((ROOT / "src").rglob("*.py")) + list((ROOT / "tests").glob("*.py")) + [ROOT / "air/task_manager.json", ROOT / "docs/historical-state-trusted-verification-v1.md", OUT / "R5_114-generic.py", OUT / "R5_114-verify.py", OUT / "R5_114-transfer.py"])
def history_pins():
    return pins([p for p in OUT.iterdir() if p.is_file() and not p.name.startswith("R5_114-")] + list((ROOT / "benchmark/requirements").glob("*.md")) + list((ROOT / "generated").glob("*")) + [ROOT / "docs/prewrite-conditional-composition-v1.md", ROOT / "docs/primary-value-interfaces-v1.md", ROOT / "docs/typed-computation-v1.md", ROOT / "docs/atomic-durable-history-v1.md", ROOT / "docs/persistent-references-v1.md", ROOT / "docs/semantic-kernel-audit-r5.108.md"])
def publish(name, value):
    with (OUT / name).open("x", encoding="utf-8", newline="\n") as f: json.dump(value, f, indent=2); f.write("\n")


def main():
    verification = OUT / "R5_114-GENERIC-VERIFICATION.json"
    verified = json.loads(verification.read_text(encoding="utf-8"))
    tree = hashlib.sha256(b"".join(p.read_bytes() for parent in (ROOT / "src", ROOT / "tests") for p in sorted(parent.rglob("*.py")))).hexdigest()
    assert verified["all_pass"] and verified["implementation_test_tree_sha256"] == tree
    before, history = implementation_pins(), history_pins()
    ev = load("evaluate114generic", "R5_103-evaluate.py")
    rows = []
    for r in captures():
        x = ev.evaluate(r["candidate"], plan(r)); rows.append(x)
        print(x["case"], x["first_blocker"], x.get("external_invocations", 0), flush=True)
    assert [x["first_blocker"] for x in rows] == ["SUCCESS"] * 5 + ["FORMALIZATION"]
    assert rows[-1]["native"] == "DISPUTED" and all(rows[-1]["stages"][s] == "NOT_REACHED" for s in ev.STAGES[1:])
    publish("R5_114-SYNTHETIC-EVIDENCE.json", dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), cases=rows, external_invocations=sum(x.get("external_invocations", 0) for x in rows), limitations=["Same-agent normative typed captures/inventories/oracles and synthetic approvals, not held-out evidence", "Five varied related schemas within one shared primary/permission foundation", "Native overflow and injected replacement failures are in source-bound test receipts, not counted as published pipeline invocations"]))
    prior_path = OUT / "R5_113-KERNEL-ACCOUNTING.json"
    prior = json.loads(prior_path.read_text(encoding="utf-8")); assert prior["final_count"] == 26
    accounting = dict(baseline_round="R5.113", baseline_source_sha256=digest(prior_path), baseline_kernel=prior["baseline_kernel"], preserved_additions=prior["preserved_additions"] + prior["additions"], baseline_count=26, additions=[], final_count=26,
        constructs={"historical_literal_copy_role_reference_nullable_values": "existing-core composition: type/value/presence/guard/operation/durable-state/atomic K01-K22", "computed_migration_values": "existing-core composition K24-K26; no new operators", "related_only_version_chain_and_frc_v1": "profile/interface integration; source authority explicit", "sealed_controlled_host_requests_and_verification_binding": "profile/interface integration of existing K17/K20 authority and R5.113 actor adapter", "private_store_candidate_validation_and_atomic_replace": "backend implementation of existing durable/atomic semantics", "verifier_owned_subprocess_host_loading_and_parent_observations": "backend implementation; no authentication or OS containment"}, claim="Exact proposed 26-concept architectural kernel preserved; no new core candidate or benchmark primitive; no minimality proof")
    publish("R5_114-KERNEL-ACCOUNTING.json", accounting)
    assert before == implementation_pins() and history == history_pins()
    publish("R5_114-GENERIC-LOCK.json", dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), implementation=before, history=history, git_head=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(), verification_sha256=digest(verification), synthetic_evidence_sha256=digest(OUT / "R5_114-SYNTHETIC-EVIDENCE.json"), kernel_accounting_sha256=digest(OUT / "R5_114-KERNEL-ACCOUNTING.json"), rule="Generic implementation/spec/tests/evidence/accounting fixed before fresh exposed transfer; no post-outcome product repair"))


if __name__ == "__main__": main()
