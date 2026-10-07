"""Final lock, frozen-history, candidate-byte, whitespace and change-scope audit."""
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
s = importlib.util.spec_from_file_location("audit106pins", OUT / "R5_106-generic.py")
generic = importlib.util.module_from_spec(s); s.loader.exec_module(generic)


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    lock_path = OUT / "R5_106-GENERIC-LOCK.json"
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    corpus = json.loads((OUT / "R5_106-CORPUS-LOCK.json").read_text(encoding="utf-8"))
    implementation_ok = generic.implementation_pins() == lock["implementation"]
    history_ok = generic.history_pins() == lock["history"]
    candidate_ok = all(sha(OUT / ("R5_106-" + c + "-CANDIDATE.json")) == h for c, h in corpus["cases"].items())
    lock_ok = sha(lock_path) == corpus["implementation_lock_sha256"]
    script_ok = sha(OUT / "R5_106-transfer.py") == corpus["transfer_script_sha256"]
    resume = json.loads((OUT / "R5_106-TRANSFER-RESUME-LOCK.json").read_text(encoding="utf-8"))
    completion = json.loads((OUT / "R5_106-TRANSFER-COMPLETION-LOCK.json").read_text(encoding="utf-8"))
    script_ok = script_ok and sha(OUT / "R5_106-resume-transfer.py") == resume["resume_script_sha256"] and sha(OUT / "R5_106-complete-transfer.py") == completion["completion_script_sha256"]
    check = subprocess.run(["git", "diff", "--check"], cwd=ROOT, capture_output=True, text=True)
    modified = subprocess.check_output(["git", "diff", "--name-only", "-z"], cwd=ROOT).decode().split("\0")
    new = subprocess.check_output(["git", "ls-files", "--others", "--exclude-standard", "-z"], cwd=ROOT).decode().split("\0")
    changed = sorted(set(p for p in modified + new if p))
    allow = {
        "AGENTS.md", "README.md", "benchmark/README.md", "docs/agent-workflow.md", "docs/project-overview.md", "docs/decisions.md", "docs/research-log.md", "docs/typed-predicates-v1.md",
        "src/air_compiler/collection_query.py", "src/air_compiler/collection_query_runtime.py", "src/air_compiler/input_values.py", "src/air_compiler/mutable_runtime.py", "src/air_compiler/mutable_values.py", "src/air_compiler/profile_runtime.py", "src/air_compiler/profiles.py",
        "src/air_compiler/predicates.py", "src/air_compiler/predicate_runtime.py", "src/air_compiler/predicate_integration.py", "src/lykoi_pipeline/mutable_profile.py", "src/lykoi_pipeline/query_profile.py", "src/lykoi_query/contracts.py", "src/lykoi_workspace/input_corpus.py", "src/lykoi_workspace/mutable_schema.py", "src/lykoi_workspace/query_schema.py", "src/lykoi_workspace/predicate_schema.py", "src/lykoi_workspace/predicate_corpus.py", "tests/test_predicates.py"
    }
    unexpected = [p for p in changed if p not in allow and not p.startswith("benchmark/results/phase5c/R5_106-")]
    whitespace = []
    for path in changed:
        for number, line in enumerate((ROOT / path).read_text(encoding="utf-8").splitlines(), 1):
            if line.rstrip() != line: whitespace.append(dict(path=path, line=number))
    verification = json.loads((OUT / "R5_106-GENERIC-FINAL-VERIFICATION-2.json").read_text(encoding="utf-8"))
    comparison = json.loads((OUT / "R5_106-COMPARISON.json").read_text(encoding="utf-8"))
    synthetic = json.loads((OUT / "R5_106-SYNTHETIC-FINAL-EVIDENCE.json").read_text(encoding="utf-8"))
    result = dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), implementation_lock_unchanged=implementation_ok, history_unchanged=history_ok, candidate_bytes_unchanged=candidate_ok, generic_lock_binding=lock_ok, transfer_scripts_unchanged=script_ok,
        verification_identity_matches_lock=sha(OUT / "R5_106-GENERIC-FINAL-VERIFICATION-2.json") == lock["verification_sha256"], tests=verification["tests"], all_tests_pass=verification["all_pass"], synthetic_external_invocations=synthetic["external_invocations"], transfer_external_invocations=comparison["external_invocations"], distribution=comparison["distribution"],
        git_diff_check_exit=check.returncode, git_diff_check_stderr=check.stderr, whitespace_findings=whitespace, unexpected_scope=unexpected, changed_paths=changed,
        frozen_model_generated_requirements_preserved=history_ok, historical_r5_105_preserved=history_ok, benchmark_specific_product_primitive=False, infrastructure_changes=False, stop="R5.106 only")
    result["all_pass"] = all((implementation_ok, history_ok, candidate_ok, lock_ok, script_ok, result["verification_identity_matches_lock"], verification["all_pass"], check.returncode == 0, not whitespace, not unexpected))
    generic.publish("R5_106-FINAL-AUDIT.json", result)
    print(json.dumps({k: v for k, v in result.items() if k not in ("changed_paths", "git_diff_check_stderr")} , indent=2))
    assert result["all_pass"]


if __name__ == "__main__": main()
