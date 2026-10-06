"""Final change-scope/history/whitespace checks; no implementation repair or rerun."""
import datetime
import hashlib
import json
from pathlib import Path
import subprocess

from lykoi_pipeline.controller import component_paths

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent


def git(*args):
    p = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    return {"argv": ["git", *args], "exit": p.returncode, "stdout": p.stdout, "stderr": p.stderr}


def main():
    freeze = json.loads((OUT / "R5_102-PRE-TRANSFER.json").read_text(encoding="utf-8"))
    implementation = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in component_paths()}
    baseline = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.glob("R5_101-*") if p.is_file()}
    immutable = git("diff", "--exit-code", "--", "air", "generated", "experiments", "schema/axiom-v0.3.schema.json", "src/air_compiler/validator.py", "src/air_compiler/runtime_template.py", "src/air_compiler/generator.py", "benchmark/requirements", "benchmark/harness", "benchmark/conventional", "benchmark/evaluation", "benchmark/semantic")
    whitespace = git("diff", "--check")
    names = git("diff", "--name-only")
    others = git("ls-files", "--others", "--exclude-standard")
    allowed_tracked = {"AGENTS.md", "README.md", "benchmark/README.md", "docs/agent-workflow.md", "docs/decisions.md", "docs/project-overview.md", "docs/research-log.md",
        "src/air_compiler/profiles.py", "src/lykoi_pipeline/author_worker.py", "src/lykoi_pipeline/contracts.py", "src/lykoi_pipeline/controller.py", "src/lykoi_pipeline/plans.py", "src/lykoi_pipeline/query_profile.py",
        "src/lykoi_rehearsal/adapters.py", "src/lykoi_workspace/query_schema.py", "src/lykoi_workspace/workspace.py"}
    allowed_new = {"docs/existing-scalar-normal-path-v1.md", "src/lykoi_pipeline/scalar_profile.py", "src/lykoi_workspace/scalar_corpus.py", "src/lykoi_workspace/scalar_schema.py", "tests/test_scalar_normal_path.py"}
    changed = names["stdout"].splitlines(); new = others["stdout"].splitlines()
    scope = set(changed) <= allowed_tracked and all(p in allowed_new or p.startswith("benchmark/results/phase5c/R5_102-") for p in new)
    new_whitespace = []
    for path in new:
        for n, line in enumerate((ROOT / path).read_text(encoding="utf-8").splitlines(), 1):
            if line.rstrip() != line: new_whitespace.append({"path": path, "line": n})
    verification = json.loads((OUT / "R5_102-VERIFICATION.json").read_text(encoding="utf-8"))
    transfer = json.loads((OUT / "R5_102-TRANSFER-EVIDENCE.json").read_text(encoding="utf-8"))
    checks = {"implementation_fixed_after_transfer": implementation == freeze["implementation"], "r5_101_preserved": baseline == freeze["r5_101_baseline"],
              "immutable_model_runtime_requirements_oracles_unchanged": immutable["exit"] == 0, "tracked_whitespace_clean": whitespace["exit"] == 0,
              "untracked_whitespace_clean": not new_whitespace, "change_scope_expected": scope, "generic_verification_passed": verification["all_pass"],
              "twenty_case_transfer_complete": len(transfer["cases"]) == 20, "b17_b20_unanswered": all(r["native"] == "NEEDS_CLARIFICATION" for r in transfer["cases"] if r["case"] in ("B17", "B20"))}
    result = {"utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "classification": "R5_102_EXISTING_SEMANTICS_NORMAL_PATH_PARTIAL", "checks": checks,
              "tests": verification["tests"], "transfer_distribution": transfer["distribution"], "changed_tracked": changed, "new_files": new,
              "new_whitespace": new_whitespace, "git_checks": [immutable, whitespace, names, others], "all_pass": all(checks.values())}
    with (OUT / "R5_102-FINAL-AUDIT.json").open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(result, stream, indent=2); stream.write("\n")
    print(json.dumps({k: result[k] for k in ("classification", "checks", "tests", "transfer_distribution", "all_pass")}, indent=2))
    assert result["all_pass"]


if __name__ == "__main__":
    main()
