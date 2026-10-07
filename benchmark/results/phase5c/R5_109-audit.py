"""Read-only evaluated-content audit; publish final history/scope evidence."""
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
s = importlib.util.spec_from_file_location("generic109audit", OUT / "R5_109-generic.py")
generic = importlib.util.module_from_spec(s); s.loader.exec_module(generic)


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")


def main():
    lock = json.loads((OUT / "R5_109-GENERIC-LOCK.json").read_text(encoding="utf-8"))
    corpus = json.loads((OUT / "R5_109-CORPUS-LOCK.json").read_text(encoding="utf-8"))
    comparison = json.loads((OUT / "R5_109-COMPARISON.json").read_text(encoding="utf-8"))
    verification = json.loads((OUT / "R5_109-GENERIC-VERIFICATION.json").read_text(encoding="utf-8"))
    implementation_intact = generic.implementation_pins() == lock["implementation"]
    history_intact = generic.history_pins() == lock["history"]
    corpus_intact = all(generic.digest(OUT / ("R5_109-" + case + "-CANDIDATE.json")) == h for case, h in corpus["cases"].items())
    driver_intact = generic.digest(OUT / "R5_109-transfer.py") == corpus["transfer_script_sha256"]
    evidence_intact = all(generic.digest(OUT / filename) == lock[key] for filename, key in (("R5_109-GENERIC-VERIFICATION.json", "verification_sha256"), ("R5_109-SYNTHETIC-EVIDENCE.json", "synthetic_evidence_sha256"), ("R5_109-KERNEL-ACCOUNTING.json", "kernel_accounting_sha256")))
    accounting = json.loads((OUT / "R5_109-KERNEL-ACCOUNTING.json").read_text(encoding="utf-8"))
    assert accounting["baseline_count"] == len(accounting["baseline_kernel"]) == 22
    assert accounting["final_count"] == 23 and len(accounting["additions"]) == 1
    assert accounting["baseline_source_sha256"] == generic.digest(ROOT / "docs/semantic-kernel-audit-r5.108.md")
    status = git("status", "--porcelain", "--untracked-files=all")
    paths = [line[3:] for line in status.stdout.splitlines()]
    allowed = {"AGENTS.md", "README.md", "benchmark/README.md", "docs/project-overview.md", "docs/decisions.md", "docs/research-log.md", "docs/agent-workflow.md", "docs/persistent-references-v1.md", "src/air_compiler/profiles.py", "src/air_compiler/references.py", "src/air_compiler/reference_runtime.py", "src/lykoi_pipeline/mutable_profile.py", "src/lykoi_workspace/mutable_schema.py", "src/lykoi_workspace/reference_schema.py", "src/lykoi_workspace/reference_corpus.py", "tests/test_references.py"}
    outside = [p for p in paths if p not in allowed and not p.startswith("benchmark/results/phase5c/R5_109-")]
    whitespace = git("diff", "--check")
    trailing = []
    new_file_trailing = []
    for line in status.stdout.splitlines():
        p = ROOT / line[3:]
        if not p.is_file() or p.suffix not in (".py", ".md", ".json"): continue
        for number, text in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            if text != text.rstrip(" \t"):
                row = dict(path=line[3:], line=number)
                trailing.append(row)
                if line.startswith("??"): new_file_trailing.append(row)
    historical_guidance = git("show", "HEAD:src/lykoi_pipeline/mutable_profile.py").stdout.splitlines()
    current_guidance = (ROOT / "src/lykoi_pipeline/mutable_profile.py").read_text(encoding="utf-8").splitlines()
    inherited = [x for x in historical_guidance if x != x.rstrip(" \t")]
    inherited_preserved = len(inherited) == 1 and inherited[0] in current_guidance
    reference_sources = [ROOT / n for n in allowed if n.startswith("src/") or n.startswith("tests/")]
    benchmark_dispatch = [{"path": str(p.relative_to(ROOT)).replace("\\", "/"), "match": m.group(0)} for p in reference_sources for m in re.finditer(r"\bB(?:0[1-9]|1[0-9]|20)\b", p.read_text(encoding="utf-8"))]
    docs = [ROOT / p for p in allowed if p.endswith(".md")] + [OUT / "R5_109-REPORT.md", OUT / "R5_109-CAPABILITY-MATRIX.md"]
    broken_links = []
    for p in docs:
        for target in re.findall(r"\]\(([^)]+)\)", p.read_text(encoding="utf-8")):
            if "://" in target or target.startswith("#"): continue
            if not (p.parent / target.split("#")[0]).exists(): broken_links.append(dict(path=str(p.relative_to(ROOT)), target=target))
    # Lock publication precedes the corpus lock; all terminal results are fixed
    # captures from that exact lock. Per-result observation timestamps remain in
    # their authority journals rather than inferred from mutable filesystem times.
    ordering = lock["utc"] < corpus["utc"]
    assert all((implementation_intact, history_intact, corpus_intact, driver_intact, evidence_intact, ordering))
    assert verification["all_pass"] and verification["tests"] == 372
    assert comparison["distribution"] == dict(FORMALIZATION=2, STRUCTURAL=1, BDI=1, ADEQUACY=0, REPRESENTATION=0, AUTHORING=0, COMPILATION=0, RUNTIME=0, BEHAVIORAL_VERIFICATION=0, SUCCESS=16)
    assert len(comparison["cases"]) == 20 and comparison["external_invocations"] == 447
    assert not outside and not benchmark_dispatch and not broken_links
    assert whitespace.returncode == 0 and not new_file_trailing and inherited_preserved
    assert trailing == [dict(path="src/lykoi_pipeline/mutable_profile.py", line=278)]
    result = dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), implementation_intact=implementation_intact, historical_evidence_requirements_generated_intact=history_intact, corpus_and_transfer_driver_intact=corpus_intact and driver_intact, verification_generic_behavior_accounting_intact=evidence_intact, generic_lock_precedes_transfer=ordering, proposed_kernel=accounting["final_count"], baseline_kernel=accounting["baseline_count"], tests=verification["tests"], exposed_behavioral_successes=16, transfer_invocations=447, scope=dict(changed_paths=paths, outside_scope=outside, infrastructure_changed=False, benchmark_specific_product_dispatch=benchmark_dispatch), whitespace=dict(git_diff_check_exit=whitespace.returncode, stdout=whitespace.stdout, stderr=whitespace.stderr, new_file_trailing=new_file_trailing, full_changed_file_trailing=trailing, inherited_guidance_preserved=inherited_preserved, full_changed_file_scan_clean=False), broken_document_links=broken_links, evidence_pins=generic.pins(OUT.glob("R5_109-*")))
    generic.publish("R5_109-FINAL-AUDIT.json", result)
    print(json.dumps(dict(implementation_intact=implementation_intact, history_intact=history_intact, scope_clean=not outside, introduced_whitespace_clean=True, inherited_trailing_spaces=len(trailing), kernel=23, tests=372, successes=16)))


if __name__ == "__main__": main()
