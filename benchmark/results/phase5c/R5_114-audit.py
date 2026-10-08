"""Final content/history/authority/chronology/whitespace/change-scope audit."""
import datetime
import importlib.util
import json
from pathlib import Path
import subprocess

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
s = importlib.util.spec_from_file_location("generic114audit", OUT / "R5_114-generic.py")
generic = importlib.util.module_from_spec(s); s.loader.exec_module(generic)


def read(name): return json.loads((OUT / name).read_text(encoding="utf-8"))


def main():
    lock = read("R5_114-GENERIC-LOCK.json")
    checks = dict(implementation_unchanged=generic.implementation_pins() == lock["implementation"], history_unchanged=generic.history_pins() == lock["history"])
    for name, field in (("R5_114-GENERIC-VERIFICATION.json", "verification_sha256"), ("R5_114-SYNTHETIC-EVIDENCE.json", "synthetic_evidence_sha256"), ("R5_114-KERNEL-ACCOUNTING.json", "kernel_accounting_sha256")):
        checks[field] = generic.digest(OUT / name) == lock[field]
    corpus = read("R5_114-CORPUS-LOCK.json")
    checks["corpus_unchanged"] = all(generic.digest(OUT / ("R5_114-" + case + "-CANDIDATE.json")) == digest for case, digest in corpus["cases"].items())
    checks["transfer_script_unchanged"] = generic.digest(OUT / "R5_114-transfer.py") == corpus["transfer_script_sha256"]
    checks["generic_lock_identity"] = generic.digest(OUT / "R5_114-GENERIC-LOCK.json") == corpus["implementation_lock_sha256"]
    kernel = read("R5_114-KERNEL-ACCOUNTING.json")
    checks["kernel_26_preserved"] = kernel["baseline_count"] == kernel["final_count"] == 26 and not kernel["additions"] and len(kernel["baseline_kernel"]) + len(kernel["preserved_additions"]) == 26
    checks["r5_113_accounting_identity"] = kernel["baseline_source_sha256"] == generic.digest(OUT / "R5_113-KERNEL-ACCOUNTING.json")
    comparison = read("R5_114-COMPARISON.json")
    checks["success_16"] = comparison["distribution"]["SUCCESS"] == 16 and comparison["external_invocations"] == 447
    checks["no_new_downstream_stages"] = all(not x["newly_reached"] for x in comparison["cases"])
    disputed = {x["case"] for x in comparison["cases"] if x["r5_114_blocker"] == "FORMALIZATION" and x["native"] == "DISPUTED"}
    checks["actual_authority_disputes_preserved"] = disputed == {"B17", "B18", "B19", "B20"}
    checks["b18_b19_downstream_not_reached"] = all(all(v == "NOT_REACHED" for s, v in x["stages"].items() if s != "FORMALIZATION") for x in comparison["cases"] if x["case"] in ("B18", "B19"))
    verification = read("R5_114-GENERIC-VERIFICATION.json")
    synthetic = read("R5_114-SYNTHETIC-EVIDENCE.json")
    transfer = read("R5_114-TRANSFER-EVIDENCE.json")
    checks["generic_verification"] = verification["all_pass"] and verification["tests"] == 397 and len(verification["commands"]) == 30
    checks["synthetic_external_evidence"] = synthetic["external_invocations"] == 133 and [x["first_blocker"] for x in synthetic["cases"]] == ["SUCCESS"] * 5 + ["FORMALIZATION"]
    checks["sealed_host_normal_verification"] = all(any(a["type"] == "verification" and a["content"]["outcome"] == "BEHAVIORALLY_VERIFIED" and a["content"]["bundle"].get("trusted_context", {}).get("adapter_sha256") == generic.digest(ROOT / "src/lykoi_pipeline/host_verifier.py") for a in x["audit"]["artifacts"].values()) for x in synthetic["cases"][:5])
    checks["generic_before_transfer"] = verification["utc"] < synthetic["utc"] < lock["utc"] < corpus["utc"] < transfer["utc"]
    diff = subprocess.run(["git", "diff", "--check"], cwd=ROOT, capture_output=True, text=True)
    checks["tracked_whitespace"] = diff.returncode == 0
    changed = subprocess.check_output(["git", "diff", "--name-only"], cwd=ROOT, text=True).splitlines()
    untracked = subprocess.check_output(["git", "ls-files", "--others", "--exclude-standard"], cwd=ROOT, text=True).splitlines()
    allowed_docs = {"AGENTS.md", "README.md", "benchmark/README.md", "docs/project-overview.md", "docs/agent-workflow.md", "docs/research-log.md", "docs/decisions.md", "docs/historical-state-trusted-verification-v1.md"}
    checks["change_scope"] = all(p in allowed_docs or p.startswith("src/") or p == "tests/test_historical_state.py" or p.startswith("benchmark/results/phase5c/R5_114-") for p in changed + untracked)
    protected = ("generated/", "schema/", "air/", "benchmark/requirements/", "benchmark/harness/", "benchmark/conventional/")
    checks["canonical_generated_harness_requirements_preserved"] = not any(p.startswith(protected) for p in changed + untracked)
    whitespace = []
    for name in untracked:
        path = ROOT / name
        if path.suffix in (".py", ".md", ".json"):
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if line.rstrip(" \t") != line: whitespace.append(dict(path=name, line=number))
    checks["new_file_whitespace"] = not whitespace
    checks["current_documentation_targets_exist"] = all(p.exists() for p in (ROOT / "docs/historical-state-trusted-verification-v1.md", OUT / "R5_114-REPORT.md", OUT / "R5_114-CAPABILITY-MATRIX.md"))
    documentation = generic.pins([ROOT / p for p in allowed_docs] + [OUT / "R5_114-REPORT.md", OUT / "R5_114-CAPABILITY-MATRIX.md", Path(__file__)])
    result = dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), checks=checks, all_pass=all(checks.values()), changed=changed, added=untracked, new_file_whitespace=whitespace, diff_check_stdout=diff.stdout, diff_check_stderr=diff.stderr, documentation=documentation, boundary="Stop after R5.114; no product/spec/test/candidate repair after lock/transfer; no new evaluation or infrastructure")
    assert result["all_pass"], result
    generic.publish("R5_114-FINAL-AUDIT.json", result)
    print(json.dumps(checks, sort_keys=True))


if __name__ == "__main__": main()
