"""Scoring integrity controls, not mirrors of application implementation."""
import json
import unittest
from run import equal, pairs
from evidence import OUT, load


class Scoring(unittest.TestCase):
    def test_nested_duplicate_output_key_is_rejected(self):
        with self.assertRaises(ValueError):
            json.loads('{"ok":{"phase":"cold","phase":"firing"}}', object_pairs_hook=pairs)

    def test_boolean_integer_substitution_cannot_pass(self):
        self.assertFalse(equal({'ok': [True]}, {'ok': [1]}))

    def test_extra_fields_and_reordered_records_cannot_pass(self):
        self.assertFalse(equal({'ok': {'id': 'x', 'extra': 1}}, {'ok': {'id': 'x'}}))
        self.assertFalse(equal({'ok': ['a', 'b']}, {'ok': ['b', 'a']}))

    def test_existing_failure_not_erased_by_no_regressions(self):
        old = load(OUT / 'results/A-kiln-0.json')
        new = load(OUT / 'results/A-kiln-2.json')
        initial = [r for r in new['observations'] if r['group'] == 'base']
        self.assertFalse(new['accepted'])
        self.assertEqual(sum(a['pass_result'] and not b['pass_result'] for a, b in zip(old['observations'], initial)), 0)

    def test_unavailable_first_candidates_stay_in_denominator(self):
        r = load(OUT / 'results/C-kiln-0-first.json')
        self.assertEqual(r['status'], 'UNAVAILABLE')
        self.assertEqual(r['groups']['base'], {'passed': 0, 'total': 26})
        self.assertFalse(r['accepted'])


if __name__ == '__main__':
    unittest.main()
