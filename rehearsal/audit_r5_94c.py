"""Final offline audit of a blocked transport. Never upgrades failed live evidence."""
import argparse
import json
import subprocess
import sys

from lykoi_pipeline.controller import ROOT, digest
from lykoi_runtime.verify import sha, verify_selected
from lykoi_transport.freeze import build, verify_content
from lykoi_transport.opencode import OpenCodeTransport
from rehearsal.validate_r5_94c import regressions, DEST, write


def run(executable, fresh=False):
    first = json.loads((DEST / "verification.json").read_text(encoding="utf-8"))
    restart = json.loads((DEST / "restart-verification.json").read_text(encoding="utf-8"))
    saved = json.loads((DEST / "final-checks.json").read_text(encoding="utf-8"))
    assert saved["identity"] == digest({k: v for k, v in saved.items() if k != "identity"})
    assert all(sha(DEST / name) == identity for name, identity in saved["evidence"].items())
    # No reuse of passing live receipts: this audit only carries forward failures.
    assert first["transport"]["status"] == restart["transport"]["status"] == "TRANSPORT_INCOMPATIBLE"
    assert all(not r["passed"] for check in (first, restart) for r in check["transport"]["roles"].values())
    transport = OpenCodeTransport(executable)
    candidate = build(transport)
    manifest = json.loads((DEST / "dependency-manifest.json").read_text(encoding="utf-8"))
    # The invocation implementation/contract/prompt/input schemas are unchanged
    # from the failed live probes. Only prospective regression classification in
    # the publication driver changed; we never turn old failures into success.
    current = {e["dependency"]: e.get("content_sha256") for e in candidate["dependencies"]}
    for e in manifest["dependencies"]:
        if (e["dependency"].startswith("src/lykoi_transport/") and e["dependency"] != "src/lykoi_transport/freeze.py") or e["dependency"] in {
                "docs/ai-worker-transport-contract-v1.md", "rehearsal/ai-worker-transport-contract-v1.json"}:
            assert current[e["dependency"]] == e["content_sha256"], "TRANSPORT_SURFACE_CHANGED_AFTER_LIVE_FAILURE"
    regression = regressions()
    runtime = verify_selected(sys.executable)
    content = verify_content(candidate, candidate["identity"])
    checks = []
    for argv in ([sys.executable, "-m", "air_compiler.cli", "validate", "air/task_manager.json"],
                 [sys.executable, "-m", "air_compiler.cli", "safety", "air/task_manager.json"],
                 [sys.executable, "-m", "unittest", "discover", "-s", "benchmark/harness", "-p", "test_baseline.py", "-v"],
                 ["git", "diff", "--check"]):
        child = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", timeout=120)
        checks.append({"argv": argv, "passed": child.returncode == 0, "stdout": child.stdout, "stderr": child.stderr})
    from lykoi_rehearsal.public_freeze_r5_91 import snapshot
    try:
        observed = snapshot()
        old = json.loads((ROOT / "benchmark/results/phase5c/r5_91/public-freeze-final.json").read_text(encoding="utf-8"))
        historical_diagnostic = {"snapshot_available": True, "changed_top_level_fields": [k for k, v in observed.items() if old.get(k) != v]}
    except (OSError, ValueError, TypeError, KeyError) as exc:
        historical_diagnostic = {"snapshot_available": False, "reason": type(exc).__name__}
    tracked = subprocess.run(["git", "diff", "--name-only"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", timeout=30)
    permitted = {"README.md", "docs/project-overview.md", "docs/decisions.md", "docs/research-log.md"}
    scope = {"changed_tracked_paths": tracked.stdout.splitlines(),
             "passed": tracked.returncode == 0 and set(tracked.stdout.splitlines()) <= permitted}
    new_paths = [e["dependency"] for e in candidate["dependencies"] if e["dependency"] not in
                 {old["dependency"] for old in manifest["dependencies"][:141]}]
    whitespace = []
    for name in new_paths:
        path = ROOT / name
        if not path.is_file():
            continue
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if line.rstrip() != line:
                whitespace.append({"path": name, "line": number})
    scope["new_infrastructure_whitespace_failures"] = whitespace
    scope["passed"] = scope["passed"] and not whitespace
    result = {"eligible": False, "classification": "R5_94C_BLOCKED_NO_FUNCTIONING_TRANSPORT_FOR_FROZEN_MODEL",
              "candidate_created": False, "engineering_identity": candidate["identity"], "content": content,
              "python": runtime, "regression": regression, "auxiliary_checks": checks, "change_scope": scope,
              "historical_installation_diagnostic": historical_diagnostic,
              "transport": {"status": "TRANSPORT_INCOMPATIBLE", "provenance": transport.provenance(),
                            "live_failure_evidence": {name: sha(DEST / name) for name in ("verification.json", "restart-verification.json")},
                            "new_live_attempts": 0},
              "active": False, "target_authorizations": [], "B03_round_counters": saved["B03_round_counters"],
              "B03_states": saved["B03_states"], "published_engineering_evidence_integrity": True}
    result["non_transport_checks_passed"] = (content["passed"] and runtime["status"] == "RUNTIME_COMPATIBLE" and regression["passed"]
                                             and all(c["passed"] for c in checks) and scope["passed"])
    if not result["non_transport_checks_passed"]:
        result["classification"] = "R5_94C_BLOCKED_MACHINE_PREFLIGHT_FAILURE"
    if fresh:
        print(json.dumps(result))
        return
    write("prospective-tests.json", regression)
    write("prospective-dependency-manifest.json", {"engineering_identity": candidate["identity"], "dependencies": candidate["dependencies"], "models": candidate["models"], "candidate_published": False})
    write("final-machine-eligibility.json", result)
    child = subprocess.run([sys.executable, "-X", "utf8", "-m", "rehearsal.audit_r5_94c", "--executable", executable, "--fresh"],
                           cwd=ROOT, capture_output=True, text=True, encoding="utf-8", timeout=900)
    fresh_result = json.loads(child.stdout)
    write("final-fresh-process-eligibility.json", fresh_result)
    assert fresh_result["engineering_identity"] == result["engineering_identity"]
    final = {"classification": result["classification"], "current_machine_eligible": False, "candidate_created": False,
             "fresh_process_non_transport_checks_passed": fresh_result["non_transport_checks_passed"],
             "B03_round_counters": saved["B03_round_counters"], "B03_states": saved["B03_states"],
             "target_authorizations": [], "candidate_active": False,
             "evidence": {name: sha(DEST / name) for name in ("prospective-tests.json", "prospective-dependency-manifest.json",
                          "final-machine-eligibility.json", "final-fresh-process-eligibility.json", "final-checks.json")},
             "audit_procedure_sha256": sha(ROOT / "rehearsal/audit_r5_94c.py"), "stop": "NO_ACTIVATION_OR_TARGET_AUTHORIZATION"}
    if not fresh_result["non_transport_checks_passed"]:
        final["classification"] = "R5_94C_BLOCKED_MACHINE_PREFLIGHT_FAILURE"
    write("final-status.json", {**final, "identity": digest(final)})
    print(json.dumps(final))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--executable", required=True)
    parser.add_argument("--fresh", action="store_true")
    args = parser.parse_args()
    run(args.executable, args.fresh)
