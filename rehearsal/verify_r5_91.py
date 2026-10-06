"""Explicit R5.91 selections, writing new evidence without rerunning old drivers."""
import hashlib
import io
import json
import sys
import time
import unittest

from air_compiler.parser import parse
from air_compiler.validator import validate
from lykoi_pipeline.controller import ROOT

SELECTIONS = {
    "live_public_freeze": ["test_live_public_freeze"],
    "r5_89": ["test_public_rehearsal"],
    "r5_86": ["test_authority_controller"],
    "r5_87": ["test_requirements_workspace"],
    "r5_88": ["test_sealed_pipeline"],
    "compiler_application": ["test_compiler", "test_application"],
    "guarded_historical": ["benchmark.evaluation.test_formal_requirements_r5_80",
                           "benchmark.evaluation.test_implementation_adequacy_r5_81",
                           "benchmark.evaluation.test_behavioral_discovery_r5_82",
                           "benchmark.evaluation.test_source_coverage_r5_84",
                           "benchmark.evaluation.test_benchmark_documents_v1"]}


def main(selection=None):
    sys.path.insert(0, str(ROOT / "tests"))
    destination = ROOT / "benchmark/results/phase5c/r5_91"
    summary = {"round": "R5.91", "suites": {}, "checks_passed_with_known_crlf_failures": True}
    if selection:
        summary = json.loads((destination / "verification.json").read_text())
        summary["checks_passed_with_known_crlf_failures"] = True
    for name, modules in SELECTIONS.items():
        if selection and name not in selection:
            continue
        stream = io.StringIO()
        start = time.monotonic()
        suite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromName(m) for m in modules)
        result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
        record = {"modules": modules, "tests": result.testsRun, "passed": result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped),
                  "failures": len(result.failures), "errors": len(result.errors), "skipped": len(result.skipped),
                  "seconds": round(time.monotonic() - start, 3), "failure_ids": [t.id() for t, _ in result.failures]}
        summary["suites"][name] = record
        log = destination / (name + ".txt")
        if log.is_file() and not (destination / (name + "-first.txt")).exists():
            (destination / (name + "-first.txt")).write_bytes(log.read_bytes())
        log.write_text(stream.getvalue(), encoding="utf-8", newline="\n")
        print(json.dumps({"suite": name, **record}), flush=True)
        expected = result.wasSuccessful() or (name == "guarded_historical" and len(result.failures) == 2 and not result.errors
            and {t.id().rsplit(".", 1)[-1] for t, _ in result.failures} == {
                "test_reproducible_results_and_exact_coverage_locators", "test_independent_disagreement_and_public_b01_calibration"})
        summary["checks_passed_with_known_crlf_failures"] &= expected
    summary["checks_passed_with_known_crlf_failures"] &= all(
        r["failures"] == 0 and r["errors"] == 0 for n, r in summary["suites"].items() if n != "guarded_historical")
    validate(parse((ROOT / "air/task_manager.json").read_text(encoding="utf-8")))
    summary["model_validation"] = "PASS"
    summary["historical_crlf"] = "Two known physical-byte pin failures preserved; no normalization or history edits"
    paths = [ROOT / "benchmark/results/phase5c/R5_90-LIVE-AI-WORKER-QUALIFICATION.md"]
    paths += list((ROOT / "benchmark/results/phase5c/r5_90").glob("*"))
    paths += list((ROOT / "benchmark/results/phase5c/r5_89").glob("*"))
    summary["historical_public_bytes"] = {str(p.relative_to(ROOT)).replace("\\", "/"): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths if p.is_file()}
    (destination / "verification.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    return 0 if summary["checks_passed_with_known_crlf_failures"] else 1


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--selection", nargs="+", choices=list(SELECTIONS))
    sys.exit(main(parser.parse_args().selection))
