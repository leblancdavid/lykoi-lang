"""Independent scoring-integrity checks; no candidate authoring or repair."""
import unittest
from evidence import HERE, load, sha
from run import equal


class ScoringTests(unittest.TestCase):
    def test_types_are_exact(self):
        self.assertFalse(equal({'pairs':True},{'pairs':1}))
        self.assertFalse(equal({'offset':1.0},{'offset':1}))
        self.assertTrue(equal({'a':[1,False]},{'a':[1,False]}))

    def test_extra_missing_fields_and_order_reject(self):
        self.assertFalse(equal({'a':1,'extra':0},{'a':1}))
        self.assertFalse(equal([1,2],[2,1]))
        self.assertFalse(equal([1],[1,1]))
        self.assertTrue(equal({'a':1,'b':2},{'b':2,'a':1}))

    def test_frozen_observations_unique_and_reserved_unscored(self):
        for task in ('T1','T2','T3','T4'):
            rows=load(HERE/'acceptance'/f'{task}.json')
            self.assertEqual(len(rows),len({r['hex'] for r in rows}))
            if task in ('T1','T2'):
                self.assertFalse(any(r['hex'].startswith('02') for r in rows))

    def test_discrete_boundary_expectations(self):
        rows={r['hex']:r['expected'] for r in load(HERE/'acceptance'/'T1.json')}
        self.assertEqual(rows['006464'],dict(status='success',value=dict(amount=200,clipped=False),output='c800'))
        self.assertEqual(rows['016464'],dict(status='success',value=dict(amount=200,clipped=True),output='c801'))
        rows={r['hex']:r['expected'] for r in load(HERE/'acceptance'/'T3.json')}
        self.assertEqual(rows['00010002ff'],dict(status='reject',code='OVERLAP',offset=2))
        rows={r['hex']:r['expected'] for r in load(HERE/'acceptance'/'T4.json')}
        self.assertEqual(rows['282828'],dict(status='reject',code='DEPTH',offset=2))
        self.assertEqual(rows['282928292829282958'],dict(status='reject',code='OCCURRENCE_LIMIT',offset=8))

    def test_failures_remain_in_denominator(self):
        comparison=load(HERE/'COMPARISON.json')
        self.assertEqual(comparison['base']['A']['total_tasks'],4)
        self.assertEqual(comparison['base']['C']['total_tasks'],4)
        self.assertEqual(comparison['base']['C']['accepted_tasks'],3)
        self.assertEqual(comparison['modified']['C']['accepted_modifications'],1)

    def test_artifact_and_requirement_freezes_unchanged(self):
        for name in ('TASK-FREEZE.json','MODIFICATION-SEAL.json'):
            for path,digest in load(HERE/name)['files'].items():
                self.assertEqual(sha(HERE/path),digest)


if __name__=='__main__':
    unittest.main()
