"""Capture fresh CLI qualification output without altering frozen procedures."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

from lykoi_pipeline.controller import ROOT, digest
from lykoi_runtime.verify import sha

IDENTITY = "060adb4e30505f3488e36502626f20c4e58a8aa2742b635ddbaca4ce2b943915"
DESTINATION = ROOT / "benchmark/results/phase5c/r5_94b/final"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--opencode", required=True)
    args = parser.parse_args()
    child = subprocess.run([sys.executable, "-X", "utf8", "-m", "rehearsal.validate_r5_94b", "check", "--opencode", args.opencode,
                            "--expected-identity", IDENTITY], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", timeout=1200)
    result = json.loads(child.stdout)
    record = {"command_exit_status": child.returncode, "reporter_sha256": sha(Path(__file__)),
              "result": result, "result_identity": digest(result), "contract_modified": False}
    with (DESTINATION / "publication-check-attempt-2.json").open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(record, sort_keys=True, indent=2) + "\n")
    status = {"classification": "R5_94B_CROSS_MACHINE_PROTECTED_FREEZE_IMPLEMENTED" if result["eligible"] and child.returncode == 0 else
              "R5_94B_CURRENT_MACHINE_ELIGIBILITY_BLOCKED_LIVE_OPENCODE_ADAPTER_CONTRACT",
              "candidate_identity": IDENTITY, "eligible": result["eligible"] and child.returncode == 0,
              "initial_first_and_restart_verification": "final-checks.json",
              "post_publication_failure_preserved": "publication-check-attempt-1.json",
              "unchanged_contract_requalification": "publication-check-attempt-2.json",
              "evidence": {name: sha(DESTINATION / name) for name in ("final-checks.json", "publication-check-attempt-1.json", "publication-check-attempt-2.json")},
              "failures": result["failures"], "active": False, "target_authorizations": [],
              "B03_round_counters": json.loads((DESTINATION / "final-checks.json").read_text(encoding="utf-8"))["B03_round_counters"]}
    with (DESTINATION / "current-machine-status.json").open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps({**status, "identity": digest(status)}, sort_keys=True, indent=2) + "\n")
    print(json.dumps(status))
    return child.returncode


if __name__ == "__main__":
    raise SystemExit(main())
