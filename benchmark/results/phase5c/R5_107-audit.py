"""Read-only final integrity, scope and whitespace audit of evaluated content."""
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
s = importlib.util.spec_from_file_location("audit107pins", OUT / "R5_107-generic.py")
g = importlib.util.module_from_spec(s); s.loader.exec_module(g)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    lock = json.loads((OUT / "R5_107-GENERIC-LOCK-3.json").read_text(encoding="utf-8"))
    corpus = json.loads((OUT / "R5_107-CORPUS-LOCK.json").read_text(encoding="utf-8"))
    verification = json.loads((OUT / "R5_107-GENERIC-FINAL-VERIFICATION-2.json").read_text(encoding="utf-8"))
    comparison = json.loads((OUT / "R5_107-COMPARISON.json").read_text(encoding="utf-8"))
    synthetic = json.loads((OUT / "R5_107-SYNTHETIC-FINAL-EVIDENCE-2.json").read_text(encoding="utf-8"))
    historical = json.loads((OUT / "R5_106-GENERIC-LOCK.json").read_text(encoding="utf-8"))["implementation"]
    implementation = g.implementation_pins()
    changed = sorted(p for p in implementation if historical.get(p) != implementation[p])
    check = subprocess.run(["git", "diff", "--check"], cwd=ROOT, text=True, capture_output=True)
    whitespace = []
    for p in changed:
        for i, line in enumerate((ROOT / p).read_text(encoding="utf-8").splitlines(), 1):
            if line.rstrip(" \t") != line:
                whitespace.append(dict(path=p, line=i, disposition="Retained in final evaluated lock; no post-outcome implementation edit"))
    product_paths = [p for p in changed if p.startswith("src/") and not p.endswith(("input_corpus.py", "interface_corpus.py"))]
    domain_dispatch = {p: re.findall(r"\bB(?:0[1-9]|1[0-9]|20)\b|[\"'](?:archive|list-urgent|list-due|append-note|list-archived)[\"']", (ROOT / p).read_text(encoding="utf-8")) for p in product_paths}
    checks = dict(implementation_unchanged=implementation == lock["implementation"], history_unchanged=g.history_pins() == lock["history"],
        corpus_unchanged=all(sha(OUT / ("R5_107-" + case + "-CANDIDATE.json")) == pin for case, pin in corpus["cases"].items()),
        final_verification_unchanged=sha(OUT / "R5_107-GENERIC-FINAL-VERIFICATION-2.json") == lock["verification_sha256"],
        final_lock_bound_to_corpus=sha(OUT / "R5_107-GENERIC-LOCK-3.json") == corpus["implementation_lock_sha256"],
        transfer_script_unchanged=sha(OUT / "R5_107-transfer.py") == corpus["transfer_script_sha256"],
        final_lock_precedes_corpus=lock["utc"] < corpus["utc"],
        all_twenty_terminal_results=len(comparison["cases"]) == 20 and all((OUT / ("R5_107-" + x["case"] + "-RESULT.json")).exists() for x in comparison["cases"]),
        generic_verification_pass=verification["all_pass"] and verification["tests"] == 361,
        synthetic_all_pass=all(x["first_blocker"] == "SUCCESS" for x in synthetic["cases"]) and synthetic["external_invocations"] == 84,
        no_benchmark_specific_product_dispatch=not any(domain_dispatch.values()))
    assert all(checks.values()), checks
    assert whitespace == [dict(path="src/lykoi_pipeline/mutable_profile.py", line=259, disposition="Retained in final evaluated lock; no post-outcome implementation edit")]
    assert check.returncode == 2 or check.returncode == 1
    evidence_pins = {p.name: sha(p) for p in OUT.glob("R5_107-*") if p.is_file()}
    result = dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), classification="R5_107_PREDICATE_VALUE_INTERFACE_CLOSED", checks=checks,
        semantic_and_integrity_checks_pass=True, whitespace_check_pass=False, whitespace=whitespace, git_diff_check=dict(exit=check.returncode, stdout=check.stdout, stderr=check.stderr),
        changed_implementation_paths_since_r5_106=changed, scope="Existing normal compiler/pipeline/schema/capture/test interface composition only; no canonical model/generated/frozen requirement/oracle/infrastructure edits", product_domain_dispatch_scan=domain_dispatch,
        preserved_pretransfer_locks=["R5_107-GENERIC-LOCK.json", "R5_107-GENERIC-LOCK-2.json", "R5_107-GENERIC-LOCK-3.json"], tests=verification["tests"], synthetic_external_invocations=84, transfer_external_invocations=comparison["external_invocations"], distribution=comparison["distribution"], evidence_sha256=evidence_pins,
        limitations=["One locked guidance trailing space remains a failed formatting check", "Same-agent captures/inventory/oracles and synthetic approvals", "Exposed requirement-local development evidence, not held-out/cumulative"])
    g.publish("R5_107-FINAL-AUDIT.json", result)
    print(json.dumps(dict(checks=checks, whitespace_check_pass=False, tests=361, synthetic_invocations=84, transfer_invocations=comparison["external_invocations"], distribution=comparison["distribution"]), indent=2))


if __name__ == "__main__": main()
