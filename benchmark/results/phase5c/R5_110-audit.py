"""Post-transfer content, chronology, whitespace and authorized change-scope audit."""
import datetime
import importlib.util
import json
from pathlib import Path
import subprocess

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
s = importlib.util.spec_from_file_location("generic110audit", OUT / "R5_110-generic.py")
g = importlib.util.module_from_spec(s); s.loader.exec_module(g)


def main():
    lock = json.loads((OUT / "R5_110-GENERIC-LOCK.json").read_text(encoding="utf-8"))
    corpus = json.loads((OUT / "R5_110-CORPUS-LOCK.json").read_text(encoding="utf-8"))
    verification = json.loads((OUT / "R5_110-GENERIC-VERIFICATION.json").read_text(encoding="utf-8"))
    kernel = json.loads((OUT / "R5_110-KERNEL-ACCOUNTING.json").read_text(encoding="utf-8"))
    transfer = json.loads((OUT / "R5_110-COMPARISON.json").read_text(encoding="utf-8"))
    prior = json.loads((OUT / "R5_109-KERNEL-ACCOUNTING.json").read_text(encoding="utf-8"))
    checks = dict(implementation_unchanged=g.implementation_pins() == lock["implementation"], history_unchanged=g.history_pins() == lock["history"], verification_intact=g.digest(OUT / "R5_110-GENERIC-VERIFICATION.json") == lock["verification_sha256"] and verification["all_pass"], synthetic_intact=g.digest(OUT / "R5_110-SYNTHETIC-EVIDENCE.json") == lock["synthetic_evidence_sha256"], accounting_intact=g.digest(OUT / "R5_110-KERNEL-ACCOUNTING.json") == lock["kernel_accounting_sha256"], exact_kernel=kernel["baseline_kernel"] == prior["baseline_kernel"] + [x["concept"] for x in prior["additions"]] and kernel["baseline_count"] == kernel["final_count"] == 23 and kernel["additions"] == [], corpus_intact=all(g.digest(OUT / ("R5_110-" + c + "-CANDIDATE.json")) == h for c, h in corpus["cases"].items()), generic_before_corpus=lock["utc"] < corpus["utc"], complete_twenty_cases=len(corpus["cases"]) == len(transfer["cases"]) == 20, preserved_16_successes=transfer["distribution"]["SUCCESS"] == 16)
    sources = {}
    for case in corpus["cases"]:
        r = json.loads((OUT / ("R5_110-" + case + "-CANDIDATE.json")).read_text(encoding="utf-8"))["producer_capture"]
        sources[case] = all(g.digest(ROOT / path) == digest for path, digest in r["source_files"].items())
    checks["fresh_source_pins_intact"] = all(sources.values())
    changed = subprocess.check_output(["git", "diff", "--name-only"], cwd=ROOT, text=True).splitlines()
    untracked = subprocess.check_output(["git", "ls-files", "--others", "--exclude-standard"], cwd=ROOT, text=True).splitlines()
    allowed = {"AGENTS.md", "README.md", "benchmark/README.md", "docs/agent-workflow.md", "docs/decisions.md", "docs/research-log.md", "docs/project-overview.md", "docs/atomic-durable-history-v1.md", "src/air_compiler/atomic_state.py", "src/air_compiler/atomic_state_runtime.py", "src/air_compiler/collection_query.py", "src/air_compiler/predicate_integration.py", "src/air_compiler/profiles.py", "src/lykoi_pipeline/mutable_profile.py", "src/lykoi_workspace/mutable_schema.py", "src/lykoi_workspace/atomic_state_schema.py", "src/lykoi_workspace/atomic_state_corpus.py", "tests/test_atomic_state.py"}
    out_of_scope = [p for p in changed + untracked if p not in allowed and not p.startswith("benchmark/results/phase5c/R5_110-")]
    checks["scope_clean"] = not out_of_scope
    p = subprocess.run(["git", "diff", "--check"], cwd=ROOT, capture_output=True, text=True)
    checks["introduced_tracked_whitespace_clean"] = p.returncode == 0
    new_whitespace = []
    for name in untracked:
        file = ROOT / name
        for n, line in enumerate(file.read_text(encoding="utf-8").splitlines(), 1):
            if line.rstrip() != line: new_whitespace.append(dict(path=name, line=n))
    checks["new_file_whitespace_clean"] = not new_whitespace
    inherited_whitespace = []
    for name in changed:
        for n, line in enumerate((ROOT / name).read_text(encoding="utf-8").splitlines(), 1):
            if line.rstrip() != line: inherited_whitespace.append(dict(path=name, line=n))
    result = dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), checks=checks, all_pass=all(checks.values()), tests=verification["tests"], proposed_kernel=kernel["final_count"], external_transfer_invocations=transfer["external_invocations"], out_of_scope=out_of_scope, tracked_changes=changed, new_files=untracked, new_file_whitespace=new_whitespace, inherited_full_file_whitespace=inherited_whitespace, whitespace_stderr=p.stderr, scope="R5.110 semantics, tests, source-authorized exposed transfer and reporting; no arithmetic/B19 or infrastructure changes")
    g.publish("R5_110-FINAL-AUDIT.json", result)
    print(json.dumps(dict(all_pass=result["all_pass"], checks=checks, inherited_whitespace=inherited_whitespace), indent=2))
    assert result["all_pass"]


if __name__ == "__main__": main()
