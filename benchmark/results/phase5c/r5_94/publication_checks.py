"""Post-freeze read-only machinery/history/documentation checks; no source custody."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from lykoi_pipeline.controller import ROOT, digest
from lykoi_protected.freeze import integrity, EXTRA
from lykoi_rehearsal.public_freeze_r5_91 import integrity as public_integrity

DIRECTORY = Path(__file__).resolve().parent
DOCUMENTS = ("README.md", "docs/project-overview.md", "docs/decisions.md", "docs/research-log.md",
             "benchmark/results/phase5c/R5_94-GENERIC-PROTECTED-EVALUATION-ADMISSION-REPAIR.md",
             "benchmark/results/phase5c/r5_94/publication_checks.py")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check():
    candidate = json.loads((DIRECTORY / "protected-freeze-candidate.json").read_text())
    final = json.loads((DIRECTORY / "final-checks.json").read_text())
    assert integrity(candidate)
    assert final["identity"] == digest({k: v for k, v in final.items() if k != "identity"})
    assert final["candidate_identity"] == candidate["identity"]
    assert all(sha(DIRECTORY / name) == pin for name, pin in final["validation_evidence"].items())
    verify = json.loads((DIRECTORY / "verification.json").read_text())
    assert all(sha(DIRECTORY / name) == pin for name, pin in verify["raw_logs"].items())
    inherited = json.loads((ROOT / "benchmark/results/phase5c/r5_92a/readiness.json").read_text())
    assert all(sha(ROOT / name) == pin for name, pin in inherited["sources"].items())
    public = json.loads((ROOT / "benchmark/results/phase5c/r5_91/public-freeze-final.json").read_text())
    assert public_integrity(public)
    scope = subprocess.run(["git", "diff", "--name-only"], cwd=ROOT, check=True, capture_output=True, text=True).stdout.splitlines()
    assert set(scope) <= set(DOCUMENTS)
    subprocess.run(["git", "diff", "--check"], cwd=ROOT, check=True)
    for name in set(EXTRA) | set(DOCUMENTS):
        assert all(line == line.rstrip() for line in (ROOT / name).read_text(encoding="utf-8").splitlines()), name
    assert not final["target_authorizations"] and all(v == 0 for v in final["B03_round_counters"].values())
    result = {"candidate_identity": candidate["identity"], "candidate_integrity": True,
              "validation_and_raw_log_integrity": True, "historical_r5_91_integrity": True,
              "r5_92a_bound_history_preserved": True, "tracked_change_scope": scope, "whitespace": "PASS",
              "documentation_sha256": {name: sha(ROOT / name) for name in DOCUMENTS},
              "target_authorizations": [], "B03_round_counters_all_zero": True,
              "counter_basis": final["B03_counter_basis"]}
    if "--record" in sys.argv:
        with (DIRECTORY / "publication-checks.json").open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps({**result, "identity": digest(result)}, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    check()
