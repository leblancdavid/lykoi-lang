"""Final diagnostic accounting and change-scope checks; no product edits/tests."""
import datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
DOCS = {"AGENTS.md", "README.md", "benchmark/README.md", "docs/agent-workflow.md",
        "docs/decisions.md", "docs/project-overview.md", "docs/research-log.md"}

def git(*args):
    p = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    return {"argv": ["git", *args], "exit": p.returncode, "stdout": p.stdout, "stderr": p.stderr}

def main():
    evidence = json.loads((OUT / "R5_101-CURRENT-EVIDENCE.json").read_text(encoding="utf-8"))
    analysis = json.loads((OUT / "R5_101-CAPABILITY-ANALYSIS.json").read_text(encoding="utf-8"))
    snapshot = (OUT / "R5_101-PRE-EVALUATION-SNAPSHOT.md").read_text(encoding="utf-8")
    tests = [int(n) for n in re.findall(r"^Ran (\d+) tests? in", snapshot, re.M)]
    exits = [int(n) for n in re.findall(r"^Exit code: (\d+)", snapshot, re.M)]
    core = json.loads((OUT / "R5_101-CORE-VERIFICATION.json").read_text(encoding="utf-8"))
    initial_tests = sum(tests)
    tests += [c["tests"] for c in core["commands"]]
    exits += [c["exit"] for c in core["commands"]]
    changed = git("diff", "--name-only", "HEAD")
    whitespace = git("diff", "--check")
    untracked = git("ls-files", "--others", "--exclude-standard")
    intended_prefix = "benchmark/results/phase5c/R5_101-"
    unexpected_tracked = sorted(set(changed["stdout"].splitlines()) - DOCS)
    unexpected_untracked = [p for p in untracked["stdout"].splitlines() if not p.startswith(intended_prefix)]
    product_scope = git("diff", "--exit-code", "HEAD", "--", "src", "schema", "air", "generated", "tests",
                        "benchmark/evaluation", "benchmark/harness", "benchmark/requirements", "benchmark/conventional")
    # Protect every tracked historical result, not just a selected freeze's pins.
    history_scope = git("diff", "--exit-code", "HEAD", "--", "benchmark/results")
    cases = {c["case"]: c for c in evidence["cases"]}
    assert set(cases) == {f"B{i:02d}" for i in range(1, 21)}
    assert {a["case"] for a in analysis["cases"]} == set(cases)
    source_pins = {case: hashlib.sha256((ROOT / "benchmark/requirements" / (case + ".md")).read_bytes()).hexdigest() == c["source_sha256"]
                   for case, c in cases.items()}
    all_after_block_not_reached = True
    for c in cases.values():
        blocked = False
        for status in c["stages"].values():
            if blocked and status != "NOT_REACHED":
                all_after_block_not_reached = False
            blocked |= status == "BLOCKED"
    b05 = cases["B05"]
    audit = b05["audit"]
    verification = audit["artifacts"][audit["run"]["verification"]]["content"]
    external_cases = len(verification["cases"])
    steps = [s for c in verification["cases"] for s in c["steps"]]
    assert external_cases == 6 and len(steps) == 10
    assert all(s["passed"] and not s["unexecutable"] for s in steps)
    new_files = [ROOT / p for p in untracked["stdout"].splitlines() if p.startswith(intended_prefix)]
    trailing = [{"file": str(p.relative_to(ROOT)), "line": i} for p in new_files
                for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1) if line != line.rstrip()]
    # Local documentation links only; skip historical prose and external URLs.
    report = OUT / "R5_101-B01-B20-CURRENT-CAPABILITY-REPORT.md"
    broken_links = [link for link in re.findall(r"\]\(([^)]+)\)", report.read_text(encoding="utf-8"))
                    if not link.startswith(("https:", "http:", "#")) and not (report.parent / link.split("#")[0]).exists()]
    ok = (all(n == 0 for n in exits) and len(exits) == 16 and len(tests) == 14
          and not unexpected_tracked and not unexpected_untracked and not trailing and not broken_links
          and all(source_pins.values()) and all_after_block_not_reached
          and product_scope["exit"] == 0 and history_scope["exit"] == 0 and whitespace["exit"] == 0)
    result = {"utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
              "classification": "R5_101_B01_B20_CAPABILITY_MATRIX_COMPLETE", "audit_pass": ok,
              "baseline_test_counts": tests, "baseline_total_tests": sum(tests), "baseline_command_exits": exits,
              "pre_evaluation_tests": initial_tests, "supplemental_current_core_tests": core["tests"],
              "first_blocker_counts": analysis["first_result_counts"], "primary_gap_counts": analysis["primary_gap_counts"],
              "requirement_pins_preserved": source_pins,
              "all_downstream_blocked_stages_not_reached": all_after_block_not_reached,
              "B05": {"compilation": "PASS", "runtime": "PASS", "behavioral_verification": verification["outcome"],
                      "external_cases": external_cases, "external_invocations": len(steps), "all_observations_pass": True,
                      "scope": "requirement-local current model; not cumulative B01-B05 achievement"},
              "unexpected_tracked": unexpected_tracked, "unexpected_untracked": unexpected_untracked,
              "new_file_trailing_whitespace": trailing, "broken_report_links": broken_links,
              "product_scope_check": product_scope, "historical_result_scope_check": history_scope,
              "whitespace_check": whitespace, "changed_paths": changed, "untracked_paths": untracked,
              "git_status": git("status", "--short"),
              "Lykoi_implementation_unchanged": product_scope["exit"] == 0,
              "historical_evidence_unchanged": history_scope["exit"] == 0,
              "formalization_limit": "Same-agent analytical captures and synthetic owner actions, not independent source approval",
              "no_held_out_generalization_claim": True}
    with (OUT / "R5_101-FINAL-AUDIT.json").open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(result, stream, indent=2, ensure_ascii=False)
        stream.write("\n")
    print("Baseline:", sum(tests), "tests,", len(exits), "commands; exits:", exits)
    print("Cases:", analysis["first_result_counts"], "; B05 external:", external_cases, "cases /", len(steps), "invocations")
    print("Audit:", ok, "; product unchanged:", product_scope["exit"] == 0, "; history unchanged:", history_scope["exit"] == 0)
    if not ok:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
