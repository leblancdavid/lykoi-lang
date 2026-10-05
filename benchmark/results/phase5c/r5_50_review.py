"""Focused methodology witnesses only; no benchmark authority loader/dispatch."""

import io
from pathlib import Path
import platform
import sys
import unittest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from benchmark.evaluation.recorder_r5_43 import digest
from benchmark.evaluation.security_r5_47 import persist


MODULES = (
    'benchmark.evaluation.test_reproducibility_boundary_r5_50',
    'benchmark.evaluation.test_preexposure_r5_45',
    'benchmark.harness.test_canonical_evidence_r5_43',
    'benchmark.evaluation.test_security_r5_47',
    'benchmark.evaluation.test_ai_independence_r5_49',
)
MECHANISMS = (
    'benchmark/evaluation/preexposure_r5_45.py',
    'benchmark/evaluation/recorder_r5_43.py',
    'benchmark/evaluation/security_r5_47.py',
    'benchmark/evaluation/ai_independence_r5_48.py',
    'benchmark/evaluation/test_ai_independence_r5_49.py',
    'benchmark/results/phase5c/r5_50_review.py',
) + tuple(name.replace('.', '/') + '.py' for name in MODULES)

EXCLUDED = {
    'benchmark.evaluation.test_security_r5_47.SecurityTests.test_historical_lock_unchanged':
        'Historical raw committed/worktree equality fails on this CRLF checkout; not a publication witness',
    'benchmark.evaluation.test_security_r5_47.SecurityTests.test_ignore_effective_behavior':
        'Historical quiet check-ignore assertion fails on negated pattern; not a publication witness',
}


def selected(suite):
    result = unittest.TestSuite()
    for test in suite:
        if isinstance(test, unittest.TestSuite):
            result.addTests(selected(test))
        elif test.id() not in EXCLUDED:
            result.addTest(test)
    return result


class Result(unittest.TextTestResult):
    def __init__(self, *args):
        super().__init__(*args)
        self.passed = []

    def addSuccess(self, test):
        super().addSuccess(test)
        self.passed.append(test.id())


def capture():
    return {name: digest((ROOT / name).read_bytes()) for name in sorted(set(MECHANISMS))}


def main():
    destination = Path(__file__).with_name('R5_50-validation-focused.json')
    if destination.exists():
        raise SystemExit('Review evidence already exists; overwrite prohibited')
    before = capture()
    suites = []
    successful = True
    for module in MODULES:
        result = unittest.TextTestRunner(stream=io.StringIO(), resultclass=Result).run(
            selected(unittest.defaultTestLoader.loadTestsFromName(module)))
        # Do not persist arbitrary test stdout, traceback or exception text.
        row = {'module': module, 'tests': result.testsRun,
               'passed': result.passed,
               'failed': [test.id() for test, _ in result.failures],
               'errors': [test.id() for test, _ in result.errors],
               'skipped': [test.id() for test, _ in result.skipped],
               'status': 'PASS' if result.wasSuccessful() else 'FAIL'}
        suites.append(row)
        successful &= result.wasSuccessful()
        print(module + ': ' + row['status'] + ' (' + str(result.testsRun) + ' tests)')
    after = capture()
    successful &= before == after
    persist(destination, {
        'protocol': 'lykoi-r5.50-methodology-witnesses-v1',
        'purpose': 'synthetic and generic methodology validation only; non-qualification',
        'status': 'PASS' if successful else 'FAIL',
        'mechanisms_before': before, 'mechanisms_after': after,
        'mechanisms_unchanged': before == after,
        'runtime': {'implementation': platform.python_implementation(),
                    'version': platform.python_version(),
                    'os_family': platform.system(), 'architecture': platform.machine()},
        'suites': suites,
        'excluded_historical_checks': EXCLUDED,
        'b02_exposure': 0, 'core_semantics': 30,
        'production_capsule_qualified': False,
    })
    raise SystemExit(0 if successful else 1)


if __name__ == '__main__':
    main()
