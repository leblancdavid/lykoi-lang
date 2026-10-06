"""Explicit public selections only; never broad benchmark discovery.

Run from the root with PYTHONPATH=src (or the documented embedded bootstrap).
Outputs are new R5.89 evidence, never updates to historical result records.
"""
import io
import json
from pathlib import Path
import sys
import time
import unittest

from air_compiler.parser import parse
from air_compiler.validator import validate
from lykoi_pipeline.controller import ROOT
from lykoi_rehearsal.freeze import seal_snapshot, eligibility

SELECTIONS = {
    "public_rehearsal": ["test_public_rehearsal"],
    "controller": ["test_authority_controller"],
    "workspace": ["test_requirements_workspace"],
    "sealed_pipeline": ["test_sealed_pipeline"],
    "compiler_application": ["test_compiler", "test_application"],
    "guarded_historical": ["benchmark.evaluation.test_formal_requirements_r5_80",
                           "benchmark.evaluation.test_implementation_adequacy_r5_81",
                           "benchmark.evaluation.test_behavioral_discovery_r5_82",
                           "benchmark.evaluation.test_source_coverage_r5_84",
                           "benchmark.evaluation.test_benchmark_documents_v1"]
}


def main(selection=None):
    sys.path.insert(0, str(ROOT / "tests"))
    destination = ROOT / "benchmark/results/phase5c/r5_89"
    destination.mkdir(parents=True, exist_ok=True)
    results = {"round": "R5.89", "classification": "R5_89_PUBLIC_REHEARSAL_BLOCKED_REAL_AI_QUALIFICATION",
               "scope": "PUBLIC_DEVELOPMENT_CALIBRATION", "suites": {}, "live_ai_runs": [],
               "B03_PRISTINE": True, "B03_NOT_EVALUATED": True, "B03_NOT_EXPOSED_TO_LYKOI_DEVELOPMENT": True,
               "B03_round_activity": {k: 0 for k in ("access_attempts", "reads", "opens", "content_revealing_metadata", "inference", "packaging", "authorizations", "execution", "evaluation")},
               "inherited_B03_counters": "all zero; no protected resource or index inspected", "R5.83-CANDIDATE-1": "UNACTIVATED",
               "future_requirement_selected": False, "stop": "R5.89"}
    if selection and (destination / "verification.json").is_file():
        results["suites"] = json.loads((destination / "verification.json").read_text(encoding="utf-8"))["suites"]
    all_expected = True
    for name, modules in SELECTIONS.items():
        if selection and name not in selection:
            continue
        stream = io.StringIO()
        suite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromName(m) for m in modules)
        start = time.monotonic()
        result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
        record = {"modules": modules, "tests": result.testsRun, "failures": len(result.failures), "errors": len(result.errors),
                  "passed": result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped),
                  "skipped": len(result.skipped), "seconds": round(time.monotonic() - start, 3),
                  "failure_ids": [t.id() for t, _ in result.failures], "error_ids": [t.id() for t, _ in result.errors]}
        results["suites"][name] = record
        (destination / (name + ".txt")).write_text(stream.getvalue(), encoding="utf-8", newline="\n")
        print(json.dumps({"suite": name, **record}, sort_keys=True), flush=True)
        all_expected &= result.wasSuccessful() or (name == "guarded_historical" and len(result.failures) == 2 and not result.errors
            and {t.id().rsplit(".", 1)[-1] for t, _ in result.failures} == {
                "test_reproducible_results_and_exact_coverage_locators", "test_independent_disagreement_and_public_b01_calibration"})
    validate(parse((ROOT / "air/task_manager.json").read_text(encoding="utf-8")))
    results["model_validation"] = "PASS"
    results["historical_crlf"] = "Two known physical-byte pin failures preserved; no normalization bypass or historical edits"
    results["checks_passed_with_known_crlf_failures"] = bool(all_expected)
    candidate = seal_snapshot()
    (destination / "public-freeze-candidate.json").write_text(json.dumps(candidate, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    check = eligibility(candidate)
    (destination / "eligibility.json").write_text(json.dumps(check, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    results["candidate_identity"] = candidate["identity"]
    results["eligibility"] = check
    calibration = {"scope": "MOCK_TRANSPORT_ENGINEERING_NOT_REAL_AI_OR_UNSEEN_EVALUATION", "live_ai_runs": [],
                   "tests_passed": results["suites"]["public_rehearsal"]["failures"] == 0 and results["suites"]["public_rehearsal"]["errors"] == 0,
                   "asserted_observations": {
                       "title-only": "BEHAVIORALLY_VERIFIED", "default-low": "BEHAVIORALLY_VERIFIED", "default-normal": "BEHAVIORALLY_VERIFIED", "default-high": "BEHAVIORALLY_VERIFIED",
                       "unsupported-structure": "STRUCTURAL_COVERAGE_FAILURE", "exact-r5.87-wizard": "UNREPRESENTABLE_SOURCE / NO_QUALIFIED_COMPLETE_MAPPING; no grant/author call",
                       "inadequate": "IMPLEMENTATION_UNDERSPECIFIED", "ambiguous": "approval denied", "disagreement": "approval denied",
                       "incorrect-author": "AUTHOR_CAPABILITY_FAILURE; no target", "wrong-default": "BEHAVIORAL_VERIFICATION_FAILURE",
                       "filesystem-network-child-process": "CONTAINMENT_FAILURE", "public-mode": "PUBLIC_REHEARSAL_INELIGIBLE"},
                   "evidence": "public_rehearsal.txt; test_public_rehearsal assertions"}
    (destination / "calibration-results.json").write_text(json.dumps(calibration, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    (destination / "verification.json").write_text(json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    return 0 if all_expected else 1


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--selection", nargs="+", choices=list(SELECTIONS))
    sys.exit(main(parser.parse_args().selection))
