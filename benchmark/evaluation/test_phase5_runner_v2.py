"""Independent synthetic/adversarial tests for the complete prospective lifecycle."""
import copy
import os
import json
import subprocess
import sys
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from benchmark.evaluation import phase5_runner_v2 as r

ROOT = Path(__file__).resolve().parents[2]


def synthetic():
    content = {'synthetic:whole-contract': b'{"behavior":"preserve observable sample order"}',
               'synthetic:profile': b'{"static":"whole-contract"}'}
    benchmark = r.seal({'kind': 'synthetic', 'expected_benchmark': 'independent-held-out-fake',
        'authority_class': r.SYNTHETIC_TEST,
        'resources': {name: {'commitment': r.digest(raw), 'seal': 'CLOSED',
                             'provenance': 'synthetic setup before freeze', 'frozen': True}
                      for name, raw in content.items()}})
    return benchmark, content


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.ledger = r.Ledger(self.temp.name)
        self.state = r.seal({'kind': 'CurrentState', 'files': {'subject': 'fixed'}, 'semantic_count': 30,
                             'runner': {'runner': 'fixed'}})
        self.benchmark, self.content = synthetic()
        results = {name: {'status': 'PASS', 'state': self.state['identity']} for name in r.HEALTH_STAGES}
        self.health = r.health_record(self.state, results)
        self.freeze = r.freeze(self.state, self.benchmark, self.health, self.ledger)
        self.reads = self.calls = 0

    def authorize(self):
        return r.authorize_synthetic(self.freeze, self.benchmark, self.ledger, self.state)

    def open(self):
        self.reads += 1
        return self.content

    def evaluate(self, opened):
        self.calls += 1
        self.assertEqual(set(opened), set(self.benchmark['resources']))
        return {'classification': 'synthetic-static-observed', 'whole_contract': True}

    def observe(self, grant=None, **changes):
        args = {'frozen': self.freeze, 'commitment': self.benchmark,
                'grant': grant or self.authorize(), 'ledger': self.ledger,
                'capture': lambda: self.state, 'metadata_check': lambda: self.benchmark,
                'opener': self.open, 'evaluator': self.evaluate, **changes}
        return r.observe(**args)

    def post(self):
        return r.post_check(self.freeze, self.benchmark, self.ledger,
                            lambda: self.state, lambda: self.benchmark)

    def test_complete_synthetic_lifecycle_and_durable_reload(self):
        self.assertEqual(self.ledger.status(), 'zero')
        self.assertEqual(self.freeze, r.freeze(self.state, self.benchmark, self.health, self.ledger))
        r.verify_commitment(self.benchmark, self.benchmark['identity'], copy.deepcopy(self.benchmark))
        grant = self.authorize()
        self.assertEqual(self.ledger.status(), 'incomplete')
        self.observe(grant)
        self.assertEqual((self.reads, self.calls), (1, 1))
        self.assertEqual([e['transition'] for e in r.Ledger(self.temp.name).events()], list(r.TRANSITIONS))
        self.assertEqual(self.ledger.status(), 'one')
        self.assertEqual(self.post()['status'], 'PASS')

    def test_wrong_benchmark_commitment(self):
        grant = self.authorize()
        changed, _ = synthetic()
        body = r.verify(changed)
        body['expected_benchmark'] = 'different'
        with self.assertRaises(r.Rejected):
            self.observe(grant, metadata_check=lambda: r.seal(body))
        self.assertEqual(self.reads, 0)

    def test_substituted_resource(self):
        self.content['synthetic:whole-contract'] = b'substitute'
        with self.assertRaises(r.Rejected):
            self.observe()
        self.assertEqual((self.reads, self.calls), (1, 0))
        self.assertEqual(self.ledger.status(), 'incomplete')

    def test_missing_resource(self):
        del self.content['synthetic:profile']
        with self.assertRaises(r.Rejected):
            self.observe()
        self.assertEqual(self.calls, 0)

    def test_state_mutation_before_observation(self):
        grant = self.authorize()
        body = r.verify(self.state)
        body['files'] = {'subject': 'changed'}
        self.state = r.seal(body)
        with self.assertRaises(r.Rejected):
            self.observe(grant)
        self.assertEqual(self.reads, 0)

    def test_runner_mutation(self):
        grant = self.authorize()
        body = r.verify(self.state)
        body['runner'] = {'runner': 'changed'}
        self.state = r.seal(body)
        with self.assertRaises(r.Rejected):
            self.observe(grant)

    def test_stale_health(self):
        body = r.verify(self.health)
        body['state'] = 'stale'
        with self.assertRaises(r.Rejected):
            r.freeze(self.state, self.benchmark, r.seal(body))

    def test_missing_health(self):
        results = copy.deepcopy(self.health['results'])
        del results['safety']
        with self.assertRaises(r.Rejected):
            r.health_record(self.state, results)

    def test_stale_individual_health_stage(self):
        results = copy.deepcopy(self.health['results'])
        results['safety']['state'] = 'stale'
        with self.assertRaises(r.Rejected):
            r.health_record(self.state, results)

    def test_missing_sealed_metadata(self):
        changed = r.verify(self.benchmark)
        del changed['resources']['synthetic:profile']
        with self.assertRaises(r.Rejected):
            self.observe(metadata_check=lambda: r.seal(changed))
        self.assertEqual(self.reads, 0)

    def test_substituted_sealed_metadata(self):
        changed = r.verify(copy.deepcopy(self.benchmark))
        changed['resources']['synthetic:profile']['commitment'] = r.digest(b'different')
        with self.assertRaises(r.Rejected):
            self.observe(metadata_check=lambda: r.seal(changed))
        self.assertEqual(self.reads, 0)

    def test_second_observation(self):
        grant = self.authorize()
        self.observe(grant)
        with self.assertRaises(r.Rejected):
            self.observe(grant)
        self.assertEqual((self.reads, self.calls), (1, 1))

    def test_second_authorization(self):
        self.observe()
        with self.assertRaises(r.Rejected):
            self.authorize()

    def test_replay_in_different_ledger(self):
        grant = self.authorize()
        self.observe(grant)
        with tempfile.TemporaryDirectory() as directory:
            other = r.Ledger(directory)
            other.append('AUTHORIZED', self.freeze['identity'], grant=grant['identity'])
            with self.assertRaises(r.Rejected):
                self.observe(grant, ledger=other)
        self.assertEqual(self.calls, 1)

    def test_incomplete_opening(self):
        grant = self.authorize()
        def fail():
            raise RuntimeError('synthetic interrupted opening')
        with self.assertRaises(RuntimeError):
            self.observe(grant, opener=fail)
        self.assertEqual(self.ledger.status(), 'incomplete')
        with self.assertRaises(r.Rejected):
            self.observe(grant)
        with self.assertRaises(r.Rejected):
            self.post()

    def test_incomplete_dispatch(self):
        grant = self.authorize()
        def fail(_):
            raise RuntimeError('synthetic interrupted observation')
        with self.assertRaises(RuntimeError):
            self.observe(grant, evaluator=fail)
        self.assertEqual(self.ledger.events()[-1]['transition'], 'DISPATCHED')
        with self.assertRaises(r.Rejected):
            self.observe(grant)

    def test_repair_after_observation_invalidates(self):
        self.observe()
        r.invalidate_repair(self.freeze, self.ledger)
        self.assertEqual(self.ledger.status(), 'multiple/invalid')
        with self.assertRaises(r.Rejected):
            self.post()

    def test_post_observation_mutation(self):
        self.observe()
        body = r.verify(self.state)
        body['files'] = {'subject': 'repair'}
        self.state = r.seal(body)
        with self.assertRaises(r.Rejected):
            self.post()

    def forbidden_operation(self, operation):
        with self.assertRaises(r.Rejected):
            self.observe(operation=operation)
        self.assertEqual((self.reads, self.calls), (0, 0))

    def test_unauthorized_generation(self):
        self.forbidden_operation('generation')

    def test_unauthorized_execution(self):
        self.forbidden_operation('execution')

    def test_unauthorized_acceptance(self):
        self.forbidden_operation('acceptance')

    def test_actual_authorization_prohibited(self):
        body = r.verify(self.benchmark)
        body['kind'] = 'B02'
        actual = r.seal(body)
        frozen = r.freeze(self.state, actual, self.health)
        with self.assertRaises(r.Rejected):
            r.authorize_synthetic(frozen, actual, self.ledger, self.state)
        self.assertEqual(self.ledger.status(), 'zero')

    def test_protected_resource_access_synthetic_designation(self):
        # Never attempt a real B02 read in qualification. Exercise the same hook
        # with a disposable protected fake, including swallowed denial detection.
        fake = Path(self.temp.name) / 'fake-sealed.txt'
        fake.write_bytes(b'not a real benchmark')
        boundary = r.Boundary(ROOT, [fake])
        with self.assertRaisesRegex(r.Rejected, 'R5_72_PROTOCOL_HALT'):
            with boundary.active():
                with self.assertRaises(r.Rejected):
                    fake.read_bytes()
        self.assertEqual(boundary.attempts, 1)

    def test_all_actual_protected_paths_and_bytecode_designated(self):
        boundary = r.Boundary(ROOT)
        self.assertTrue({(ROOT / name).resolve() for name in r.RESOURCE_PATHS} <= boundary.paths)
        self.assertEqual(len(boundary.paths), 23)

    def test_raw_secret_publication(self):
        for value in ({'api_key': 'synthetic'}, {'text': 'sk-' + 'a' * 24},
                      {'text': 'SECRET' + '[' + 'synthetic]'}, {'text': 'Bearer' + ' synthetic'}):
            with self.subTest(value_type=next(iter(value))):
                with self.assertRaises(r.Rejected):
                    r.persist(Path(self.temp.name) / 'unsafe.json', value)
                self.assertFalse((Path(self.temp.name) / 'unsafe.json').exists())

    def test_secret_observation_result_never_completes(self):
        with self.assertRaises(r.Rejected):
            self.observe(evaluator=lambda _: {'text': 'SECRET' + '[' + 'synthetic]'})
        self.assertEqual(self.ledger.status(), 'incomplete')

    def test_development_ai_state_mutation(self):
        state = r.current_state(ROOT)
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'fake-authoring-value', 'OPENCODE_MODEL': 'different'}):
            self.assertEqual(r.current_state(ROOT), state)
            self.assertNotIn('OPENAI_API_KEY', r.controlled_environment(ROOT))

    def test_safe_preimport_exclusion(self):
        from benchmark.evaluation.phase5_worker_v2 import restricted_suite, run_suite
        detail = run_suite(restricted_suite(ROOT))
        self.assertEqual(detail['tests'], 36)
        self.assertEqual(len(detail['skipped']), 36)
        self.assertFalse(any('benchmark.harness.' + name[:-3] in __import__('sys').modules
                             for name in [Path(p).name for p in r.RESOURCE_PATHS if p.endswith('.py')]))

    def test_evidence_corruption(self):
        self.authorize()
        path = Path(self.temp.name) / '00.json'
        path.write_bytes(b'{}\n')
        with self.assertRaises(r.Rejected):
            self.ledger.status()

    def test_immutable_publication(self):
        path = Path(self.temp.name) / 'public.json'
        value = r.seal({'kind': 'synthetic-evidence', 'status': 'PASS'})
        r.persist(path, value)
        self.assertEqual(r.load(path), value)
        with self.assertRaises(FileExistsError):
            r.persist(path, value)


def held_out():
    benchmark, content = synthetic()
    body = r.verify(benchmark)
    body.update(kind='fake-benchmark', authority_class=r.ACTUAL_HELD_OUT, precommitted=True)
    # Deliberately keep synthetic: names: explicit classification confers mode.
    return r.seal(body), content


class ActualModeTests(RunnerTests):
    """Run the identical adversarial lifecycle against actual-mode fake authority."""
    def setUp(self):
        super().setUp()
        self.benchmark, self.content = held_out()
        self.trusted_identity = self.benchmark['identity']
        self.freeze = r.freeze(self.state, self.benchmark, self.health, self.ledger)

    def authorize(self):
        return r.authorize(self.freeze, self.benchmark, self.ledger, self.state,
                           r.ACTUAL_HELD_OUT, self.trusted_identity)

    def test_requires_frozen_commitment(self):
        body = copy.deepcopy(r.verify(self.benchmark))
        for row in body['resources'].values():
            row['frozen'] = False
        changed = r.seal(body)
        frozen = r.freeze(self.state, changed, self.health)
        with self.assertRaises(r.Rejected):
            r.authorize(frozen, changed, self.ledger, self.state, r.ACTUAL_HELD_OUT, changed['identity'])
        self.assertEqual(self.ledger.status(), 'zero')

    def test_requires_precommit_and_trusted_identity(self):
        body = r.verify(self.benchmark)
        body['precommitted'] = False
        with self.assertRaises(r.Rejected):
            r.eligible(r.seal(body), r.ACTUAL_HELD_OUT, self.trusted_identity)
        with self.assertRaises(r.Rejected):
            r.eligible(self.benchmark, r.ACTUAL_HELD_OUT, 'untrusted')

    def test_requires_frozen_zero_observation(self):
        for changes in ({'kind': 'unfrozen'}, {'observation_count': 1}, {'repair_state': 'repaired'}):
            with self.subTest(changes=changes):
                frozen = r.seal({**r.verify(self.freeze), **changes})
                with self.assertRaises(r.Rejected):
                    r.authorize(frozen, self.benchmark, self.ledger, self.state,
                                r.ACTUAL_HELD_OUT, self.trusted_identity)
        self.assertEqual(self.ledger.status(), 'zero')

    def test_cross_mode_rejected_before_issuance(self):
        with self.assertRaises(r.Rejected):
            r.authorize_synthetic(self.freeze, self.benchmark, self.ledger, self.state)
        ordinary, _ = synthetic()
        frozen = r.freeze(self.state, ordinary, self.health)
        with self.assertRaises(r.Rejected):
            r.authorize(frozen, ordinary, self.ledger, self.state,
                        r.ACTUAL_HELD_OUT, ordinary['identity'])
        self.assertEqual(self.ledger.status(), 'zero')

    def test_cross_mode_grant_rejected_before_opening(self):
        grant = self.authorize()
        body = r.verify(grant)
        body['mode'] = r.SYNTHETIC_TEST
        with self.assertRaises(r.Rejected):
            self.observe(r.seal(body))
        self.assertEqual((self.reads, self.calls), (0, 0))

    def test_wrong_commitment_argument_before_opening(self):
        grant = self.authorize()
        other, _ = held_out()
        body = r.verify(other)
        body['expected_benchmark'] = 'commitment-B'
        with self.assertRaises(r.Rejected):
            self.observe(grant, commitment=r.seal(body))
        self.assertEqual(self.reads, 0)

    def test_second_authorization_before_opening(self):
        self.authorize()
        with self.assertRaises(r.Rejected):
            self.authorize()

    def test_new_ledger_cannot_reset_frozen_experiment(self):
        self.observe()
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(r.Rejected):
                r.authorize(self.freeze, self.benchmark, r.Ledger(directory), self.state,
                            r.ACTUAL_HELD_OUT, self.trusted_identity)

    def test_actual_mode_requires_prefrozen_ledger_binding(self):
        frozen = r.freeze(self.state, self.benchmark, self.health)
        with self.assertRaises(r.Rejected):
            r.authorize(frozen, self.benchmark, self.ledger, self.state,
                        r.ACTUAL_HELD_OUT, self.trusted_identity)

    def test_actual_scope_cannot_open_synthetic_only_commitment(self):
        ordinary, _ = synthetic()
        with self.assertRaises(r.Rejected):
            r.eligible(ordinary, r.ACTUAL_HELD_OUT, ordinary['identity'])

    def test_repair_mutates_state_and_blocks_new_authority(self):
        self.observe()
        self.state = r.seal({**r.verify(self.state), 'files': {'subject': 'intentional repair'}})
        with self.assertRaises(r.Rejected):
            self.post()
        r.invalidate_repair(self.freeze, self.ledger)
        with self.assertRaises(r.Rejected):
            self.authorize()
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(r.Rejected):
                r.authorize(self.freeze, self.benchmark, r.Ledger(directory), self.state,
                            r.ACTUAL_HELD_OUT, self.trusted_identity)

    def test_forbidden_operations_reject_at_issuance(self):
        for operation in ('generation', 'execution', 'acceptance', 'repair'):
            with self.subTest(operation=operation), self.assertRaises(r.Rejected):
                r.authorize(self.freeze, self.benchmark, self.ledger, self.state,
                            r.ACTUAL_HELD_OUT, self.trusted_identity, operation)
        self.assertEqual(self.ledger.status(), 'zero')

    def test_b02_structural_eligibility_without_authorization_or_access(self):
        boundary = r.Boundary(ROOT)
        with boundary.active(), patch.object(r, 'authorize', side_effect=AssertionError('no B02 issuer')):
            actual = r.benchmark_commitment(ROOT)
            self.assertTrue(r.eligible(actual, r.ACTUAL_HELD_OUT, actual['identity']))
        self.assertEqual(boundary.attempts, 0)
        self.assertEqual(self.ledger.status(), 'zero')


class InvocationTests(unittest.TestCase):
    def test_structured_pinned_preflight_both_modes_with_space_paths(self):
        state = r.current_state(ROOT)
        results = {name: {'status': 'PASS', 'state': state['identity']} for name in r.HEALTH_STAGES}
        health = r.health_record(state, results)
        for factory, mode in ((synthetic, r.SYNTHETIC_TEST), (held_out, r.ACTUAL_HELD_OUT)):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory(prefix='held out qualification ') as directory:
                parent = Path(directory)
                commitment, _ = factory()
                ledger = parent / 'one time ledger'
                ledger.mkdir()
                frozen = r.freeze(state, commitment, health, r.Ledger(ledger))
                for name, value in (('freeze', frozen), ('commitment', commitment), ('state', state)):
                    r.persist(parent / (name + '.json'), value)
                command = [sys.executable, '-B', '-S', '-m', 'benchmark.evaluation.phase5_runner_v2',
                           'preflight', '--mode', mode, '--trusted-identity', commitment['identity'],
                           '--ledger', str(ledger)]
                for name in ('freeze', 'commitment', 'state'):
                    command.extend(['--' + name, str(parent / (name + '.json'))])
                self.assertNotIn('-c', command)
                result = subprocess.run(command, cwd=ROOT, env=r.controlled_environment(ROOT),
                                        capture_output=True, timeout=30)
                self.assertEqual(result.returncode, 0, result.stderr.decode())
                evidence = json.loads(result.stdout)
                self.assertEqual((evidence['status'], evidence['mode'], evidence['protected_read_attempts']),
                                 ('PASS', mode, 0))
                self.assertEqual(r.Ledger(ledger).status(), 'zero')


if __name__ == '__main__':
    unittest.main()
