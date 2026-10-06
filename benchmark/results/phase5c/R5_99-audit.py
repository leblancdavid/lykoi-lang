"""Exact-artifact final integrity/accounting. No requirement/log discovery."""
import datetime
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent


def read(name):
    return json.loads((OUT / name).read_text(encoding="utf-8"))


def check_pins(name):
    return {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() == h for p, h in read(name)["files"].items()}


def main():
    current, previous = check_pins("R5_99-GENERIC-FREEZE.json"), check_pins("R5_98-SYNTHETIC-FREEZE.json")
    counts, steps = {}, 0
    for case in read("R5_99-SYNTHETIC-EVIDENCE.json")["cases"]:
        e = case["evidence"]
        counts[e["outcome"]] = counts.get(e["outcome"], 0) + 1
        audit = e.get("audit", {})
        run, artifacts = audit.get("run", {}), audit.get("artifacts", {})
        if "verification" in run:
            v = artifacts[run["verification"]]["content"]
            steps += sum(len(c["steps"]) for c in v["cases"])
    verification = read("R5_99-VERIFICATION-2.json")
    commands = [{"argv": c["argv"], "exit": c["exit"], "tests": c["tests"]} for c in verification["commands"]]
    status = subprocess.run(["git", "status", "--short"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    changed = subprocess.run(["git", "diff", "--name-only"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.splitlines()
    whitespace = subprocess.run(["git", "diff", "--check"], cwd=ROOT, capture_output=True, text=True)
    intended = {"README.md", "docs/decisions.md", "docs/project-overview.md", "docs/research-log.md", "src/air_compiler/cli.py",
                "src/lykoi_pipeline/author_worker.py", "src/lykoi_pipeline/contracts.py", "src/lykoi_pipeline/controller.py",
                "src/lykoi_pipeline/pipeline.py", "src/lykoi_pipeline/plans.py", "src/lykoi_rehearsal/adapters.py", "src/lykoi_workspace/workspace.py"}
    unexpected = sorted(set(changed) - intended)
    new_files = ["src/air_compiler/profile_runtime.py", "src/air_compiler/profiles.py", "src/lykoi_pipeline/query_profile.py",
                 "src/lykoi_workspace/query_corpus.py", "src/lykoi_workspace/query_schema.py", "tests/test_query_normal_path.py",
                 "docs/collection-query-normal-path-v1.md", "schema/frc-collection-query-1.schema.json", "schema/lykoi-contract-v1.schema.json",
                 "benchmark/results/phase5c/R5_99-verify.py", "benchmark/results/phase5c/R5_99-public-transfer.py",
                 "benchmark/results/phase5c/R5_99-audit.py", "benchmark/results/phase5c/R5_99-FIREWALL-INCIDENT.md",
                 "benchmark/results/phase5c/R5_99-COLLECTION-QUERY-NORMAL-PATH-INTEGRATION.md"]
    new_whitespace = [{"path": p, "line": i} for p in new_files
                      for i, line in enumerate((ROOT / p).read_text(encoding="utf-8").splitlines(), 1) if line.rstrip() != line]
    result = {"utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "classification": "R5_99_NORMAL_PATH_INTEGRATION_IMPLEMENTED_FIREWALL_VIOLATION",
              "generic_pins": current, "r5_98_pins": previous, "generic_freeze_unchanged": all(current.values()), "r5_98_freeze_unchanged": all(previous.values()),
              "tests": verification["tests"], "commands": commands, "synthetic_outcomes": counts, "synthetic_external_invocations": steps,
              "public_transfer": read("R5_99-PUBLIC-TRANSFER.json")["outcome"], "B03_POST_EXPOSURE_TRANSFER_2": "NOT_RUN_FIREWALL_INCIDENT",
              "B03_FIRST_RESULT": "DECISION_DISCOVERY_UNSUPPORTED", "R5_98_B03_POST_EXPOSURE_TRANSFER": "STRUCTURAL_COVERAGE_FAILURE",
              "git_status": status, "tracked_changes": changed, "unexpected_tracked_changes": unexpected,
              "new_file_trailing_whitespace": new_whitespace,
              "whitespace_exit": whitespace.returncode, "whitespace_stdout": whitespace.stdout, "whitespace_stderr": whitespace.stderr,
              "b04_requirement_file_opened": False, "b04_and_later_indirect_log_disclosure": True, "benchmark_nonexposure_eligibility": False,
              "formalizer_evidence": "Source-bound active-agent captures, replay through normal interfaces; no live general-source formalization accuracy claim"}
    with (OUT / "R5_99-AUDIT.json").open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(result, stream, indent=2, ensure_ascii=False); stream.write("\n")
    print("tests", result["tests"], "external synthetic invocations", steps, "outcomes", counts)
    print("generic pins", sum(current.values()), "/", len(current), "R5.98 pins", sum(previous.values()), "/", len(previous))
    print("whitespace", whitespace.returncode, "unexpected tracked changes", unexpected)
    if not all(current.values()) or not all(previous.values()) or unexpected or whitespace.returncode or new_whitespace:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
