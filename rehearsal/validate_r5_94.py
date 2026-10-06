"""Explicit synthetic/public verification and new exclusive-create freeze evidence."""
import argparse
import hashlib
import io
import json
import re
from pathlib import Path
import sys
import subprocess
import unittest

from lykoi_pipeline.controller import ROOT, digest
from lykoi_protected.freeze import seal_snapshot, integrity, EXTRA
from lykoi_rehearsal.public_freeze_r5_91 import integrity as historical_integrity
from rehearsal.verify_r5_91 import SELECTIONS

DESTINATION = ROOT / "benchmark/results/phase5c/r5_94"
KNOWN = {
    "benchmark.evaluation.test_formal_requirements_r5_80.FormalRequirementQualification.test_reproducible_results_and_exact_coverage_locators",
    "benchmark.evaluation.test_source_coverage_r5_84.CoverageTests.test_independent_disagreement_and_public_b01_calibration",
}


def write(path, value):
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(value, indent=2, sort_keys=True) + "\n")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(resume=False):
    sys.path.insert(0, str(ROOT / "tests"))
    DESTINATION.mkdir(parents=True, exist_ok=True)
    selections = {"protected": ["test_protected_evaluation"], **SELECTIONS,
                  "external_baseline": ["benchmark.harness.test_baseline"]}
    summary = {"scope": "SYNTHETIC_PUBLIC_ONLY", "suites": {}}
    for name, modules in selections.items():
        stream = io.StringIO()
        suite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromName(m) for m in modules)
        def test_ids(node):
            if isinstance(node, unittest.TestSuite):
                return [identity for item in node for identity in test_ids(item)]
            return [node.id()]
        identities = test_ids(suite)
        if resume:
            log = (DESTINATION / (name + ".txt")).read_text(encoding="utf-8")
            count = int(re.search(r"Ran (\d+) tests", log).group(1))
            assert count == len(identities)
            failures = sorted(KNOWN) if name == "guarded_historical" else []
            if failures:
                assert "FAILED (failures=2)" in log
                assert all("FAIL: " + identity.rsplit(".", 1)[-1] in log for identity in failures)
            else:
                assert log.rstrip().endswith("OK")
            record = {"tests": count, "passed": count - len(failures), "failures": failures,
                      "errors": [], "skipped": 0, "test_ids": identities, "expected_result": True}
        else:
            result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
            failures = [test.id() for test, _ in result.failures]
            record = {"tests": result.testsRun, "passed": result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped),
                      "failures": failures, "errors": [test.id() for test, _ in result.errors], "skipped": len(result.skipped), "test_ids": identities}
            record["expected_result"] = result.wasSuccessful() or (name == "guarded_historical" and set(failures) == KNOWN and not result.errors and not result.skipped)
        summary["suites"][name] = record
        if not resume:
            with (DESTINATION / (name + ".txt")).open("x", encoding="utf-8", newline="\n") as log:
                log.write(stream.getvalue())
        print(json.dumps({"suite": name, **{k: record[k] for k in ("tests", "passed", "failures", "errors", "skipped", "expected_result")}}), flush=True)
    assert all(r["expected_result"] for r in summary["suites"].values()), summary
    from air_compiler.cli import main
    import contextlib
    stream = io.StringIO()
    with contextlib.redirect_stdout(stream):
        for command in ("validate", "safety"):
            assert main([command, "air/task_manager.json"]) == 0
    if not resume:
        with (DESTINATION / "model-checks.txt").open("x", encoding="utf-8", newline="\n") as log:
            log.write(stream.getvalue())
    summary["model_checks"] = stream.getvalue()
    scope = subprocess.run(["git", "diff", "--name-only"], cwd=ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    assert set(scope) <= {"README.md", "docs/project-overview.md", "docs/decisions.md", "docs/research-log.md"}, scope
    subprocess.run(["git", "diff", "--check"], cwd=ROOT, check=True)
    for relative in EXTRA:
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert all(line == line.rstrip() for line in text.splitlines()), relative
    summary["change_scope"] = {"tracked_changes": scope, "historical_evidence_changes": [],
                              "language_compiler_mapping_changes": [], "whitespace": "PASS"}
    summary["raw_logs"] = {name + ".txt": sha(DESTINATION / (name + ".txt")) for name in selections}
    summary["resumed_after_evidence_writer_timeout"] = resume
    write(DESTINATION / "verification.json", summary)
    # Produce synthetic content-bound success/unsupported evidence in isolated stores.
    from test_protected_evaluation import ProtectedTests, IDENTITY, RUN, CREDENTIALS
    if not resume:
        test = ProtectedTests("test_provenance_invariance")
        test.setUp()
        try:
            test.test_provenance_invariance()
            write(DESTINATION / "provenance-invariance.json", test.invariance_evidence)
        finally:
            test.tearDown()
        write(DESTINATION / "unauthorized-access.json", {
        "synthetic_only": True, "all_assertions_passed": True,
        "test_ids": [identity for identity in summary["suites"]["protected"]["test_ids"]
                     if any(word in identity for word in ("denied", "without_", "wrong_", "stale_", "scope_", "before_commitment", "relabeling"))],
            "evidence": "protected.txt", "mechanism": "asserted denial, audited event, callback-not-invoked or zero forbidden exposures"})
    for unsupported in (False, True):
        test = ProtectedTests("test_synthetic_success_and_exact_roles")
        test.setUp()
        try:
            w, fid, _, _, auth = test.workspace(unsupported=unsupported)
            w.approve(CREDENTIALS["owner"], fid)
            seal = w.seal(fid)
            pipeline = test.pipeline(auth)
            prepared = pipeline.prepare(seal, RUN, review_rationale="Synthetic engineering calibration")
            result = prepared if unsupported else pipeline.execute(prepared)
            expected = "UNREPRESENTABLE_SOURCE" if unsupported else "BEHAVIORALLY_VERIFIED"
            assert result["outcome"] == expected, result
            record = {"synthetic_only": True, "result": result, "ledger": test.c.ledger(IDENTITY),
                      "artifacts": pipeline.audit(result)["artifacts"], "journal": test.c.events()}
            write(DESTINATION / ("unsupported.json" if unsupported else "success.json"), record)
        finally:
            test.tearDown()
    historical = json.loads((ROOT / "benchmark/results/phase5c/r5_91/public-freeze-final.json").read_text())
    assert historical_integrity(historical)
    candidate = seal_snapshot()
    candidate["validation_evidence"] = {name: sha(DESTINATION / name) for name in
                                         ("verification.json", "success.json", "unsupported.json", "provenance-invariance.json", "unauthorized-access.json", "protected.txt")}
    # Validation is separately bound to the canonical machinery candidate; keeping
    # it outside snapshot prevents a circular candidate/evidence dependency.
    validation_evidence = candidate.pop("validation_evidence")
    assert integrity(candidate)
    write(DESTINATION / "protected-freeze-candidate.json", candidate)
    inherited = json.loads((ROOT / "benchmark/results/phase5c/r5_92a/preaccess.json").read_text())
    final = {"classification": "R5_94_GENERIC_PROTECTED_EVALUATION_IMPLEMENTED",
             "candidate_identity": candidate["identity"], "freeze_integrity": integrity(candidate),
             "historical_r5_91_integrity": historical_integrity(historical), "validation_evidence": validation_evidence,
             "candidate_active": False, "target_authorizations": [],
             "B03_round_counters": {key: 0 for key in inherited["B03_round_counters"]},
             "B03_counter_basis": "Inherited R5.92A declaration plus this round's explicitly synthetic-only operations; no target or protected metadata inspected",
             "B03_states": inherited["B03_state"], "stop": "GENERIC_FREEZE_CREATED_NO_TARGET_AUTHORIZATION"}
    write(DESTINATION / "final-checks.json", {**final, "identity": digest(final)})
    print(json.dumps(final), flush=True)


def check():
    candidate = json.loads((DESTINATION / "protected-freeze-candidate.json").read_text())
    final = json.loads((DESTINATION / "final-checks.json").read_text())
    assert integrity(candidate)
    assert final["identity"] == digest({k: v for k, v in final.items() if k != "identity"})
    assert final["candidate_identity"] == candidate["identity"]
    assert all(sha(DESTINATION / name) == pin for name, pin in final["validation_evidence"].items())
    verification = json.loads((DESTINATION / "verification.json").read_text())
    assert all(sha(DESTINATION / name) == pin for name, pin in verification["raw_logs"].items())
    assert not final["target_authorizations"] and all(v == 0 for v in final["B03_round_counters"].values())
    print(json.dumps({"freeze_integrity": True, "evidence_integrity": True, "candidate_identity": candidate["identity"], "target_authorizations": []}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["run", "resume", "check"])
    args = parser.parse_args()
    check() if args.command == "check" else run(resume=args.command == "resume")
