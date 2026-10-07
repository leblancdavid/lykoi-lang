"""Final immutable-content, kernel, corpus, whitespace and change-scope audit."""
import datetime
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
s = importlib.util.spec_from_file_location("final111generic", OUT / "R5_111-generic.py")
generic = importlib.util.module_from_spec(s); s.loader.exec_module(generic)


def main():
    lock = json.loads((OUT / "R5_111-GENERIC-LOCK.json").read_text(encoding="utf-8"))
    assert generic.implementation_pins() == lock["implementation"]
    assert generic.history_pins() == lock["history"]
    for key, name in (("verification_sha256", "R5_111-GENERIC-VERIFICATION.json"), ("synthetic_evidence_sha256", "R5_111-SYNTHETIC-EVIDENCE.json"), ("kernel_accounting_sha256", "R5_111-KERNEL-ACCOUNTING.json")):
        assert generic.digest(OUT / name) == lock[key]
    corpus = json.loads((OUT / "R5_111-CORPUS-LOCK.json").read_text(encoding="utf-8"))
    assert generic.digest(OUT / "R5_111-GENERIC-LOCK.json") == corpus["implementation_lock_sha256"]
    assert generic.digest(OUT / "R5_111-transfer.py") == corpus["transfer_script_sha256"]
    assert len(corpus["cases"]) == 20
    for case, sha in corpus["cases"].items(): assert generic.digest(OUT / ("R5_111-" + case + "-CANDIDATE.json")) == sha
    kernel = json.loads((OUT / "R5_111-KERNEL-ACCOUNTING.json").read_text(encoding="utf-8"))
    prior = json.loads((OUT / "R5_110-KERNEL-ACCOUNTING.json").read_text(encoding="utf-8"))
    assert kernel["baseline_kernel"] == prior["baseline_kernel"] and kernel["baseline_count"] == 23
    assert kernel["final_count"] == 25 and [x["id"] for x in kernel["additions"]] == ["K24", "K25"]
    verification = json.loads((OUT / "R5_111-GENERIC-VERIFICATION.json").read_text(encoding="utf-8"))
    assert verification["all_pass"] and verification["tests"] == 386
    comparison = json.loads((OUT / "R5_111-COMPARISON.json").read_text(encoding="utf-8"))
    assert comparison["distribution"]["SUCCESS"] == 16 and comparison["external_invocations"] == 447
    assert all(not x["newly_reached"] for x in comparison["cases"])
    assert {x["case"] for x in comparison["cases"] if x["r5_111_blocker"] == "FORMALIZATION"} == {"B17", "B20"}
    status = subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=all"], cwd=ROOT, text=True)
    changed = [line[3:].replace("\\", "/") for line in status.splitlines()]
    approved = {"AGENTS.md", "README.md", "benchmark/README.md", "docs/agent-workflow.md", "docs/project-overview.md", "docs/decisions.md", "docs/research-log.md", "docs/typed-computation-v1.md", "tests/test_computation.py", "tests/test_predicates.py"}
    approved_sources = {"src/air_compiler/" + name + ".py" for name in ("atomic_state", "atomic_state_runtime", "collection_query_runtime", "computation", "computation_runtime", "mutable_values", "mutable_runtime", "predicate_runtime", "predicates", "profiles", "reference_runtime", "references")}
    approved_sources |= {"src/lykoi_pipeline/mutable_profile.py"} | {"src/lykoi_workspace/" + name + ".py" for name in ("atomic_state_schema", "computation_schema", "computation_corpus", "predicate_schema", "reference_schema")}
    assert all(p in approved | approved_sources or p.startswith("benchmark/results/phase5c/R5_111-") for p in changed), changed
    whitespace = subprocess.run(["git", "diff", "--check"], cwd=ROOT, capture_output=True, text=True)
    assert whitespace.returncode == 0, whitespace.stdout + whitespace.stderr
    # git diff excludes untracked prospective files; inspect those prose/code
    # files as well. Existing locked historical trailing space is unchanged.
    untracked_whitespace = []
    for line in status.splitlines():
        p = ROOT / line[3:]
        if line.startswith("?? ") and p.suffix in (".py", ".md"):
            for index, text in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
                if text.rstrip() != text: untracked_whitespace.append(dict(path=line[3:], line=index))
    assert not untracked_whitespace, untracked_whitespace
    summaries = dict(classification="R5_111_TYPED_COMPUTATION_IMPLEMENTED_KERNEL_EXTENDED", implementation_unchanged=True, history_requirements_generated_unchanged=True, all_candidates_unchanged=True, kernel_baseline=23, kernel_final=25, tests=386, synthetic_external_invocations=75, transfer_external_invocations=447, exposed_successes=16, newly_reached_stages=[], ambiguities_preserved=["B17", "B20"], infrastructure_work=False, benchmark_specific_primitive=False)
    files = [OUT / name for name in ("R5_111-REPORT.md", "R5_111-CAPABILITY-MATRIX.md", "R5_111-COMPARISON.json", "R5_111-TRANSFER-EVIDENCE.json", "R5_111-audit.py")]
    files += [ROOT / p for p in approved if (ROOT / p).is_file()]
    assert sys.argv[1:] in ([], ["FINAL-AUDIT-2"])
    name = "R5_111-FINAL-AUDIT-2.json" if sys.argv[1:] else "R5_111-FINAL-AUDIT.json"
    generic.publish(name, dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), summaries=summaries, changed_paths=changed, whitespace=dict(tracked_diff_exit=whitespace.returncode, untracked_new_code_prose_violations=untracked_whitespace), final_documents=generic.pins(files), result_pins=generic.pins(OUT.glob("R5_111-B??-RESULT.json")), supersedes_document_pins_only="R5_111-FINAL-AUDIT.json" if sys.argv[1:] else None))
    print(json.dumps(summaries, indent=2))


if __name__ == "__main__": main()
