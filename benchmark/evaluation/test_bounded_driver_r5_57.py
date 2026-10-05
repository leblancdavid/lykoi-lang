"""Adversarial independent scheduler witnesses, entirely synthetic."""

import subprocess
import sys
import unittest

from benchmark.evaluation import bounded_driver_r5_57 as budget
from benchmark.evaluation import tier2_r5_51 as tier
from benchmark.evaluation.recorder_r5_43 import canonical, loads, ProtocolFailure
from benchmark.evaluation import test_tier2_r5_51 as fixtures


class BudgetTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.Tier2Tests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.now = 0
        self.calls = []
        self.authority = 'synthetic-authority'
        self.cost = budget.Cost(1, 1, 2, 1, 1, 1, 1, 1)
        self.stages = {f'stage-{i}': {'mechanism': f'mechanism-{i}', 'cost': self.cost,
                                    'run': self.run_stage} for i in range(6)}
        self.driver = self.make()
        self.driver.initialize()

    def make(self, **changes):
        args = {'output': self.fixture.output, 'experiment': 'synthetic:r557-fresh',
                'capsule': self.fixture.frozen, 'authority': 'synthetic-authority',
                'stages': self.stages, 'capture': self.fixture.capture,
                'live_authority': lambda: self.authority, 'clock': lambda: self.now}
        args.update(changes)
        return budget.Driver(**args)

    def run_stage(self, timeout):
        self.calls.append(timeout)
        self.now += 10
        return {'successful': True}

    def test_full_lifecycle_accounting(self):
        self.assertEqual(self.cost.total(), 9)
        self.assertEqual(self.cost.required(), 24)

    def test_margin_floor_and_proportional(self):
        self.assertEqual(self.cost.margin(), 15)
        self.assertEqual(budget.Cost(worker=100).margin(), 34)

    def test_enough_budget(self):
        row = self.driver.batch(29)
        self.assertEqual(len(self.calls), 1)
        self.assertTrue(row['decisions'][0]['admitted'])

    def test_barely_insufficient(self):
        row = self.driver.batch(28.999)
        self.assertFalse(row['decisions'][0]['admitted'])
        self.assertEqual(self.calls, [])

    def test_worker_fits_lifecycle_does_not(self):
        # R5.56 elapsed<70 admits at t=69 with 51 seconds left, child<=65.
        self.assertLess(69, 70)
        self.assertGreater(budget.Cost(worker=40).required() + 5, 51)
        self.driver.batch(8)
        self.assertEqual(self.calls, [])

    def test_variance_margin_prevents_start(self):
        self.driver.batch(self.cost.total() + 5 + 14.99)
        self.assertEqual(self.calls, [])

    def test_no_partial_start(self):
        row = self.driver.batch(20)
        self.assertEqual(list(self.fixture.output.glob('attempt-*')), [])
        self.assertEqual(list(self.fixture.output.glob('receipt-*')), [])
        self.assertEqual(row['next'], 'stage-0')

    def test_boundary_persisted_and_canonical(self):
        row = self.driver.batch(49)
        self.assertEqual(row['disposition'], 'BOUNDARY')
        self.assertEqual(budget.reload(self.fixture.output / 'batch-0000.json'), row)
        self.assertEqual(len(row['receipts']), 3)

    def test_three_batches_complete(self):
        rows = [self.driver.batch(n) for n in (49, 39, 29)]
        self.assertEqual([len(r['receipts']) for r in rows], [3, 2, 1])
        self.assertEqual([r['disposition'] for r in rows], ['BOUNDARY', 'BOUNDARY', 'COMPLETE'])
        self.assertEqual(rows[1]['previous'], rows[0]['identity'])
        self.assertEqual(rows[2]['previous'], rows[1]['identity'])
        self.assertEqual(len(self.driver.validate()[0]), 6)

    def test_same_state_identity(self):
        self.driver.batch(29)
        self.assertEqual(len(self.make().validate()[0]), 1)

    def test_nonlexical_stage_order_survives_canonical_reload(self):
        output = self.fixture.parent / 'nonlexical-evidence'
        output.mkdir()
        stages = {name: self.stages['stage-0'] for name in ('zeta', 'alpha', 'mu')}
        driver = self.make(output=output, stages=stages)
        driver.initialize()
        driver.batch(39)
        driver.batch(29)
        self.assertEqual(list(driver.validate()[0]), ['zeta', 'alpha', 'mu'])

    def test_state_mutation_rejected(self):
        self.driver.batch(29)
        (self.fixture.root / 'subject/input.txt').write_bytes(b'mutated')
        with self.assertRaises(ProtocolFailure):
            self.driver.batch(49)
        self.assertEqual(len(self.calls), 1)

    def test_authority_mutation_rejected(self):
        self.driver.batch(29)
        self.authority = 'mutated'
        with self.assertRaises(ProtocolFailure):
            self.driver.batch(49)

    def test_receipt_mutation_rejected_even_resealed(self):
        self.driver.batch(29)
        path = self.fixture.output / 'receipt-stage-0.json'
        value = loads(path.read_bytes())
        value.pop('identity')
        value['result']['extra'] = True
        path.write_bytes(canonical(tier.seal(value)) + b'\n')
        with self.assertRaises(ProtocolFailure):
            self.driver.batch(49)

    def test_driver_version_mismatch(self):
        self.driver.batch(29)
        with self.assertRaises(ProtocolFailure):
            self.make(version='future').batch(49)

    def test_different_fresh_qualification_rejected(self):
        self.driver.batch(29)
        with self.assertRaises(ProtocolFailure):
            self.make(experiment='synthetic:r558').batch(49)

    def test_definition_mutation_rejected(self):
        self.driver.batch(29)
        self.stages['stage-1']['mechanism'] = 'changed'
        with self.assertRaises(ProtocolFailure):
            self.make().batch(49)

    def test_interrupted_stage_incomplete_no_retry(self):
        def interrupt(timeout):
            raise subprocess.TimeoutExpired('withheld', timeout)
        self.stages['stage-0']['run'] = interrupt
        row = self.driver.batch(49)
        receipt = budget.reload(self.fixture.output / 'receipt-stage-0.json')
        self.assertEqual(receipt['status'], 'INCOMPLETE')
        self.assertFalse(receipt['result']['successful'])
        self.assertEqual(row['disposition'], 'STOPPED')
        with self.assertRaises(ProtocolFailure):
            self.driver.batch(49)

    def test_hard_kill_orphan_attempt_no_retry(self):
        self.driver.write('attempt-stage-0', {'binding': budget.digest(canonical(self.driver.binding)),
                                            'stage': 'stage-0', 'status': 'INCOMPLETE'})
        with self.assertRaisesRegex(ProtocolFailure, 'INCOMPLETE'):
            self.driver.batch(49)
        self.assertEqual(self.calls, [])

    def test_unadmitted_not_incomplete(self):
        self.driver.batch(20)
        self.assertEqual(self.driver.validate()[0], {})

    def test_final_completion_recognized(self):
        self.driver.batch(100)
        row = self.driver.batch(20)
        self.assertEqual(row['disposition'], 'COMPLETE')
        self.assertEqual(row['next'], None)
        self.assertEqual(len(self.calls), 6)

    def test_secret_safe_diagnostics(self):
        marker = 'sk-' + 'Q' * 24
        def interrupt(timeout):
            raise RuntimeError(marker)
        self.stages['stage-0']['run'] = interrupt
        self.driver.batch(49)
        for path in self.fixture.output.glob('*.json'):
            self.assertNotIn(marker.encode(), path.read_bytes())

    def test_secret_worker_result_rejected(self):
        self.stages['stage-0']['run'] = lambda timeout: {'successful': True, 'pass' + 'word': 'private'}
        self.driver.batch(49)
        self.assertEqual(budget.reload(self.fixture.output / 'receipt-stage-0.json')['status'], 'INCOMPLETE')

    def test_real_child_interrupted_after_result_still_incomplete(self):
        path = self.fixture.output / 'child-result.json'
        command = [sys.executable, '-B', '-S', '-c',
                   "from pathlib import Path; import sys,time; Path(sys.argv[1]).write_bytes(b'{\"successful\":true}\\n'); time.sleep(5)", str(path)]
        callback = budget.child(command, self.fixture.root, {}, path)
        self.stages['stage-0']['run'] = lambda timeout: callback(.1)
        self.driver.batch(49)
        self.assertEqual(budget.reload(self.fixture.output / 'receipt-stage-0.json')['status'], 'INCOMPLETE')
        with self.assertRaises(ProtocolFailure):
            self.driver.batch(49)

    def test_real_child_failure_diagnostics_withheld(self):
        command = [sys.executable, '-B', '-S', '-c', "import sys; print('private diagnostic'); sys.exit(1)"]
        callback = budget.child(command, self.fixture.root, {}, self.fixture.output / 'absent.json')
        self.stages['stage-0']['run'] = callback
        self.driver.batch(49)
        row = budget.reload(self.fixture.output / 'receipt-stage-0.json')
        self.assertEqual(row['status'], 'FAIL')
        self.assertNotIn('private diagnostic', str(row))

    def test_unknown_cost_conservative(self):
        self.assertGreater(budget.production_cost().required() + 5, 120)
        self.assertGreater(budget.production_cost(103.157).required() + 5, 120)

    def test_invalid_budget_rejected(self):
        with self.assertRaises(ProtocolFailure):
            budget.Cost(worker=float('nan')).required()

    def test_b02_and_r556_prohibited(self):
        for name in ('synthetic:B02', 'R5.56-fresh'):
            with self.assertRaises(ProtocolFailure):
                self.make(experiment=name)

    def test_observation_retry_rules_unchanged(self):
        # Exercise the actual recorder: interrupted observation permanently halts.
        self.fixture.output = self.fixture.parent / 'observation-evidence'
        self.fixture.output.mkdir()
        gate = self.fixture.gate()
        with self.assertRaises(ProtocolFailure):
            gate.observe_synthetic('synthetic:mineral', lambda: (_ for _ in ()).throw(RuntimeError()))
        with self.assertRaises(ProtocolFailure):
            gate.observe_synthetic('synthetic:mineral', lambda: {'successful': True})


if __name__ == '__main__':
    unittest.main()
