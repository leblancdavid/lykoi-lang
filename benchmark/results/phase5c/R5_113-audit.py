"""Final content/history/kernel/chronology/whitespace/change-scope checks."""
import datetime
import importlib.util
import json
from pathlib import Path
import subprocess

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
s = importlib.util.spec_from_file_location("generic113audit", OUT / "R5_113-generic.py")
generic = importlib.util.module_from_spec(s); s.loader.exec_module(generic)


def main():
    lock = json.loads((OUT / "R5_113-GENERIC-LOCK.json").read_text(encoding="utf-8"))
    checks = dict(implementation_unchanged=generic.implementation_pins() == lock["implementation"], history_unchanged=generic.history_pins() == lock["history"])
    for name, field in (("R5_113-GENERIC-VERIFICATION.json", "verification_sha256"), ("R5_113-SYNTHETIC-EVIDENCE.json", "synthetic_evidence_sha256"), ("R5_113-KERNEL-ACCOUNTING.json", "kernel_accounting_sha256")):
        checks[field] = generic.digest(OUT / name) == lock[field]
    corpus = json.loads((OUT / "R5_113-CORPUS-LOCK.json").read_text(encoding="utf-8"))
    checks["corpus_unchanged"] = all(generic.digest(OUT / ("R5_113-" + case + "-CANDIDATE.json")) == digest for case, digest in corpus["cases"].items())
    checks["transfer_script_unchanged"] = generic.digest(OUT / "R5_113-transfer.py") == corpus["transfer_script_sha256"]
    checks["generic_lock_identity"] = generic.digest(OUT / "R5_113-GENERIC-LOCK.json") == corpus["implementation_lock_sha256"]
    kernel = json.loads((OUT / "R5_113-KERNEL-ACCOUNTING.json").read_text(encoding="utf-8"))
    checks["kernel_25_to_26"] = kernel["baseline_count"] == 25 and kernel["final_count"] == 26 and len(kernel["baseline_kernel"]) + len(kernel["preserved_additions"]) + len(kernel["additions"]) == 26 and [a["id"] for a in kernel["additions"]] == ["K26"]
    comparison = json.loads((OUT / "R5_113-COMPARISON.json").read_text(encoding="utf-8"))
    checks["success_16"] = comparison["distribution"]["SUCCESS"] == 16 and comparison["external_invocations"] == 447
    checks["no_new_downstream_stages"] = all(not x["newly_reached"] for x in comparison["cases"])
    disputed = {x["case"] for x in comparison["cases"] if x["r5_113_blocker"] == "FORMALIZATION" and x["native"] == "DISPUTED"}
    checks["actual_authority_disputes_preserved"] = disputed == {"B17", "B18", "B19", "B20"}
    verification = json.loads((OUT / "R5_113-GENERIC-VERIFICATION.json").read_text(encoding="utf-8"))
    synthetic = json.loads((OUT / "R5_113-SYNTHETIC-EVIDENCE.json").read_text(encoding="utf-8"))
    transfer = json.loads((OUT / "R5_113-TRANSFER-EVIDENCE.json").read_text(encoding="utf-8"))
    checks["generic_verification"] = verification["all_pass"] and verification["tests"] == 393 and len(verification["commands"]) == 29
    checks["synthetic_external_evidence"] = synthetic["external_invocations"] == 144 and len(synthetic["cases"]) == 5 and all(x["first_blocker"] == "SUCCESS" for x in synthetic["cases"])
    checks["generic_before_transfer"] = verification["utc"] < synthetic["utc"] < lock["utc"] < corpus["utc"] < transfer["utc"]
    diff = subprocess.run(["git", "diff", "--check"], cwd=ROOT, capture_output=True, text=True)
    checks["tracked_whitespace"] = diff.returncode == 0
    changed = subprocess.check_output(["git", "diff", "--name-only"], cwd=ROOT, text=True).splitlines()
    untracked = subprocess.check_output(["git", "ls-files", "--others", "--exclude-standard"], cwd=ROOT, text=True).splitlines()
    allowed_docs = {"AGENTS.md", "README.md", "benchmark/README.md", "docs/project-overview.md", "docs/agent-workflow.md", "docs/research-log.md", "docs/decisions.md", "docs/prewrite-conditional-composition-v1.md"}
    checks["change_scope"] = all(p in allowed_docs or p.startswith("src/") or p == "tests/test_authorization_composition.py" or p.startswith("benchmark/results/phase5c/R5_113-") for p in changed + untracked)
    protected = ("generated/", "schema/", "air/", "benchmark/requirements/", "benchmark/harness/", "benchmark/conventional/")
    checks["canonical_generated_harness_requirements_preserved"] = not any(p.startswith(protected) for p in changed + untracked)
    whitespace = []
    for name in untracked:
        path = ROOT / name
        if path.suffix in (".py", ".md", ".json"):
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if line.rstrip(" \t") != line: whitespace.append(dict(path=name, line=number))
    checks["new_file_whitespace"] = not whitespace
    checks["current_documentation_targets_exist"] = all(p.exists() for p in (ROOT / "docs/prewrite-conditional-composition-v1.md", OUT / "R5_113-REPORT.md", OUT / "R5_113-CAPABILITY-MATRIX.md"))
    documentation = generic.pins([ROOT / p for p in allowed_docs] + [OUT / "R5_113-REPORT.md", OUT / "R5_113-CAPABILITY-MATRIX.md", Path(__file__)])
    result = dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), checks=checks, all_pass=all(checks.values()), changed=changed, added=untracked, new_file_whitespace=whitespace, diff_check_stdout=diff.stdout, diff_check_stderr=diff.stderr, documentation=documentation, boundary="Stop after R5.113. No product/spec/test/candidate repair after lock/transfer; R5.114 is only recommended.")
    assert result["all_pass"], result
    generic.publish("R5_113-FINAL-AUDIT.json", result)
    print(json.dumps(checks, sort_keys=True))


if __name__ == "__main__": main()
