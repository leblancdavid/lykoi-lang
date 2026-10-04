"""Integrity checks for collected R5.37 evidence, without retry or repair."""
import hashlib
import json
from pathlib import Path
import unittest

RESULTS = Path(__file__).resolve().parent
ROOT = RESULTS.parents[2]


def read(name):
    return json.loads((RESULTS / name).read_bytes())


class FrozenEvaluationEvidence(unittest.TestCase):
    def test_lock_and_frozen_artifacts_remain_byte_identical(self):
        lock = read('R5_37-implementation-lock.json')
        self.assertEqual(len(lock['files']), 224)
        for path, expected in lock['files'].items():
            with self.subTest(path=path):
                self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), expected)

    def test_source_identity_matches_failed_generation(self):
        evidence = read('R5_37-generation-evidence.json')
        self.assertEqual(hashlib.sha256((RESULTS / 'R5_37-b02-semantic-application.json').read_bytes()).hexdigest(),
                         evidence['source_sha256'])
        self.assertFalse(evidence['complete_candidate'])
        self.assertEqual(evidence['generated_files'], [])
        self.assertEqual(evidence['classification'], 'UNKNOWN_TYPE_COHERENCE_GAP')
        self.assertIn('current_pipeline.generate', evidence['traceback'])
        self.assertIn('types.checked_plan', evidence['traceback'])

    def test_null_is_not_replaced_by_optional_absence_or_string_sentinel(self):
        model = read('R5_37-b02-semantic-application.json')
        operation = model['operations']['list-overdue']
        shape = operation['state']['pre']['record']['records']['sequence']['record']['due_date']
        self.assertEqual(shape, {'nullable': 'instant'})
        predicates = operation['branches'][0]['value']['order']['source']['select']['where']['and']
        self.assertEqual(predicates[1]['not']['equals'][1]['literal']['value'], None)
        self.assertEqual(predicates[2]['before'][0], {'ref': ['item', 'due_date']})

    def test_complete_frozen_method_inventory_is_blocked_not_passed(self):
        matrix = read('R5_37-evaluation-matrix.json')
        frozen = (ROOT / 'benchmark/harness/regression.py').read_text(encoding='utf-8')
        import ast
        module = ast.parse(frozen)
        methods = {method.name for cls in module.body if isinstance(cls, ast.ClassDef) and cls.name == 'Regression'
                   for method in cls.body if isinstance(method, ast.FunctionDef) and method.name.startswith('test_')}
        self.assertEqual({case['case'] for case in matrix['cases']}, methods)
        self.assertTrue(all(case['frozen_acceptance'] == 'BLOCKED' for case in matrix['cases']))
        self.assertEqual(matrix['acceptance_totals'], {'PASS': 0, 'FAIL': 0, 'SKIP': 0, 'BLOCKED': 7})

    def test_execution_and_proof_claims_are_not_invented(self):
        matrix = read('R5_37-evaluation-matrix.json')
        self.assertEqual(matrix['public_executions'], 0)
        self.assertEqual(matrix['grounded_executions'], 0)
        self.assertEqual(matrix['new_demonstrated_frozen_b02_transfers'], 0)
        self.assertFalse(matrix['universal_implementation_correctness_established'])
        self.assertEqual(matrix['candidate_core_constructs'], 30)
        self.assertEqual(matrix['implementation_repairs'], 0)

    def test_lock_seal_and_recorder_identity(self):
        lock = read('R5_37-implementation-lock.json')
        identity = lock.pop('identity')
        self.assertEqual(hashlib.sha256(json.dumps(lock, sort_keys=True).encode()).hexdigest(), identity)
        for path, expected in lock['evaluation_files_at_lock'].items():
            self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), expected)


if __name__ == '__main__':
    unittest.main()
