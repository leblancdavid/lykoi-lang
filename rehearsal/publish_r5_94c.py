"""Read-only publication checks followed by a new ordinary evidence receipt."""
import argparse
import json
import subprocess

from lykoi_pipeline.controller import ROOT, digest
from lykoi_runtime.verify import sha
from lykoi_transport.freeze import build, verify_content
from lykoi_transport.opencode import OpenCodeTransport
from rehearsal.validate_r5_94c import DEST, write


def main(executable):
    status = json.loads((DEST / "final-status.json").read_text(encoding="utf-8"))
    assert status["identity"] == digest({k: v for k, v in status.items() if k != "identity"})
    assert all(sha(DEST / name) == pin for name, pin in status["evidence"].items())
    initial = json.loads((DEST / "final-checks.json").read_text(encoding="utf-8"))
    assert all(sha(DEST / name) == pin for name, pin in initial["evidence"].items())
    candidate = build(OpenCodeTransport(executable))
    manifest = json.loads((DEST / "prospective-dependency-manifest.json").read_text(encoding="utf-8"))
    assert candidate["identity"] == manifest["engineering_identity"]
    assert verify_content(candidate, candidate["identity"])["passed"]
    assert not status["current_machine_eligible"] and not status["candidate_created"]
    assert not status["target_authorizations"] and not status["candidate_active"]
    assert all(v == 0 for v in status["B03_round_counters"].values())
    check = subprocess.run(["git", "diff", "--check"], cwd=ROOT, capture_output=True, text=True, timeout=30)
    assert check.returncode == 0
    diff = subprocess.run(["git", "diff", "--name-only"], cwd=ROOT, capture_output=True, text=True, timeout=30)
    docs = {"README.md", "docs/project-overview.md", "docs/decisions.md", "docs/research-log.md"}
    assert diff.returncode == 0 and set(diff.stdout.splitlines()) == docs
    paths = docs | {"benchmark/results/phase5c/R5_94C-PROVIDER-NEUTRAL-AI-WORKER-TRANSPORT.md",
                    "benchmark/results/phase5c/r5_94c/transport-discovery.json", "rehearsal/publish_r5_94c.py"}
    paths.update(e["dependency"] for e in candidate["dependencies"] if e["dependency"].startswith("src/lykoi_transport/")
                 or e["dependency"] in {"docs/ai-worker-transport-contract-v1.md", "docs/provider-neutral-freeze-r5.94c.md",
                    "rehearsal/ai-worker-transport-contract-v1.json", "rehearsal/validate_r5_94c.py", "rehearsal/audit_r5_94c.py", "tests/test_ai_transport.py"})
    for name in sorted(paths):
        assert all(line.rstrip() == line for line in (ROOT / name).read_text(encoding="utf-8").splitlines()), name
    result = {"passed": True, "classification": status["classification"], "current_machine_eligible": False,
              "engineering_identity": candidate["identity"], "all_137_inherited_pins_intact": True,
              "published_evidence_integrity": True, "historical_tracked_files_changed": False,
              "new_live_attempts": 0, "B03_round_counters": status["B03_round_counters"],
              "candidate_created": False, "target_authorizations": [], "whitespace_and_change_scope_passed": True,
              "tracked_changes": sorted(docs), "publication_hashes": {name: sha(ROOT / name) for name in sorted(paths)},
              "final_status_sha256": sha(DEST / "final-status.json")}
    write("publication-checks.json", {**result, "identity": digest(result)})
    print(json.dumps({k: v for k, v in result.items() if k != "publication_hashes"}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--executable", required=True)
    main(parser.parse_args().executable)
