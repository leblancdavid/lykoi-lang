"""Non-gating synthetic comparison; does not verify the production candidate."""
import io
import argparse
import json
import sys
import unittest

from lykoi_pipeline.controller import ROOT
from lykoi_runtime.verify import sha
from rehearsal.validate_r5_94a import stable


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--destination", default="benchmark/results/phase5c/r5_94a/comparison-final")
    args = parser.parse_args()
    sys.path.insert(0, str(ROOT / "tests"))
    import test_portable_runtime as tests
    destination = ROOT / args.destination
    destination.mkdir(parents=True, exist_ok=True)
    suite = unittest.defaultTestLoader.loadTestsFromModule(tests)
    log = io.StringIO()
    result = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
    with (destination / "synthetic-calibration-tests.txt").open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(log.getvalue())
    assert result.wasSuccessful() and not result.skipped, log.getvalue()
    comparison = {"scope": "SYNTHETIC_LOCAL_EXACT_PIN_CALIBRATION_NOT_PRODUCTION_FREEZE_VERIFICATION",
                  "historical_runtime": "Preserved CPython 3.12.10 evidence; NOT executed or retroactively contract-qualified",
                  "current_runtime": sys.version, "tests_passed": result.testsRun,
                  "test_log_sha256": sha(destination / "synthetic-calibration-tests.txt"), "comparisons": {}}
    for unsupported in (False, True):
        test = tests.PortableTests("test_synthetic_success_and_exact_roles")
        test.setUp()
        try:
            w, fid, _, _, auth = test.workspace(unsupported=unsupported)
            w.approve(tests.fixtures.CREDENTIALS["owner"], fid)
            seal = w.seal(fid)
            pipeline = test.pipeline(auth)
            prepared = pipeline.prepare(seal, tests.fixtures.RUN, review_rationale="Synthetic engineering calibration")
            outcome = prepared if unsupported else pipeline.execute(prepared)
            record = {"artifacts": pipeline.audit(outcome)["artifacts"], "result": outcome}
            name = "unsupported.json" if unsupported else "success.json"
            historical_path = ROOT / "benchmark/results/phase5c/r5_94" / name
            historical = json.loads(historical_path.read_text(encoding="utf-8"))
            old, new = stable(historical), stable(record)
            assert old == new, (old, new)
            comparison["comparisons"][name] = {"historical_sha256": sha(historical_path), "historical": old, "current": new, "equal": True}
        finally:
            test.tearDown()
            test.doCleanups()
    test = tests.PortableTests("test_provenance_invariance")
    test.setUp()
    try:
        test.test_provenance_invariance()
        invariant = test.invariance_evidence
        historical_path = ROOT / "benchmark/results/phase5c/r5_94/provenance-invariance.json"
        historical = json.loads(historical_path.read_text(encoding="utf-8"))
        keys = [key for key in invariant if key not in {"public_contract_identity", "protected_contract_identity"}]
        assert all(invariant[key] == historical[key] for key in keys)
        comparison["comparisons"]["provenance-invariance"] = {"historical_sha256": sha(historical_path), "current": invariant, "equal_fields": keys}
    finally:
        test.tearDown()
        test.doCleanups()
    comparison["limits"] = ["Synthetic calibration pins current files and executable hash; no live OpenCode calls",
                            "Inherited file differences are separately audited; no historical pin is changed",
                            "Production freeze remains blocked by exact dependencies",
                            "Envelope identities change with new freeze dependencies; compare normalized semantic identity",
                            "Journal runtime provenance, executable/library bytes, paths and timings are environment-dependent",
                            "One runtime executed; no universal cross-version invariance claim"]
    with (destination / "historical-comparison.json").open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(comparison, sort_keys=True, indent=2) + "\n")
    print(json.dumps(comparison))


if __name__ == "__main__":
    main()
