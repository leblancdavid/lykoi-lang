"""Fresh adversarial witnesses use synthetic resources, never B02 contents."""

import io
from pathlib import Path
import subprocess
import sys
import threading
import unittest
from unittest.mock import patch

from benchmark.evaluation import capability_guard_r5_61 as guard
from benchmark.evaluation import bounded_driver_r5_57 as bounded
from benchmark.evaluation import restricted_harness_r5_61 as harness
from benchmark.evaluation import test_tier2_r5_51 as fixtures
from benchmark.evaluation import certificate_r5_55 as certificates
from benchmark.evaluation import qualified_authority_r5_55 as authority
from benchmark.evaluation import tier2_r5_51 as tier
from benchmark.evaluation.recorder_r5_43 import ProtocolFailure, canonical, digest


class CapabilityTests(unittest.TestCase):
    def setUp(self):
        fixture = fixtures.Tier2Tests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        self.fixture = fixture
        self.events = []
        self.path = fixture.parent / 'ordinary-name.txt'
        self.path.write_bytes(b'synthetic protected sentinel; no behavioral content')
        self.resource = guard.Resource('synthetic-authority', self.path, 'B02_AUTHORITY_READ')
        self.boundary = guard.Boundary([self.resource], self.events.append)
        self.cost = bounded.Cost(1, 1, 2, 1, 1, 1, 1, 1)

    def driver(self, name, capabilities, run=None, **changes):
        args = dict(output=self.fixture.output, experiment='synthetic:r561',
            capsule=self.fixture.frozen, authority='synthetic-authority',
            stages={name: {'mechanism': 'synthetic-mechanism', 'cost': self.cost,
                          'capabilities': capabilities, 'run': run or (lambda timeout: {'successful': True})}},
            capture=self.fixture.capture, live_authority=lambda: 'synthetic-authority',
            resources=[self.resource], clock=lambda: 0)
        args.update(changes)
        return bounded.Driver(**args)

    def test_harmless_stage_mentions_b02_allowed(self):
        self.driver('confirm_b02_remains_sealed', []).initialize()

    def test_harmless_stage_without_b02_allowed(self):
        self.driver('ordinary_regression', []).initialize()

    def test_harmless_experiment_mentions_b02_allowed(self):
        self.driver('ordinary', [], experiment='confirm_b02_is_sealed').initialize()

    def test_dangerous_harmless_name_rejected(self):
        with self.assertRaises(ProtocolFailure):
            self.driver('generic_regression', ['B02_AUTHORITY_READ'])
        self.assertEqual(list(self.fixture.output.iterdir()), [])

    def test_dangerous_b02_name_rejected(self):
        with self.assertRaises(ProtocolFailure):
            self.driver('b02_regression', ['B02_STATIC_EVALUATION'])

    def test_mixed_capabilities_rejected(self):
        with self.assertRaises(ProtocolFailure):
            self.driver('mixed', ['REGRESSION_EVIDENCE', 'B02_FIXTURE_READ'])

    def test_all_protected_operations_forbidden(self):
        self.assertEqual(len(guard.PROTECTED), 13)
        for capability in guard.PROTECTED:
            with self.subTest(capability=capability), self.assertRaises(ProtocolFailure):
                guard.authorize([capability])

    def test_missing_unknown_duplicate_declarations_rejected(self):
        for declaration in (None, ['unknown'], ['TEST_DISCOVERY', 'TEST_DISCOVERY'], 'TEST_DISCOVERY'):
            with self.subTest(declaration=declaration), self.assertRaises(ProtocolFailure):
                guard.authorize(declaration)

    def test_undeclared_direct_resource_read_denied(self):
        with self.assertRaises(ProtocolFailure), self.boundary.stage(['REGRESSION_EVIDENCE']):
            self.path.read_bytes()
        self.assertEqual(self.events[0]['access'], 'DENIED_BEFORE_CONTENT')
        self.assertTrue(self.events[0]['quarantine'])

    def test_synthetic_authority_read_denied(self):
        with self.assertRaises(ProtocolFailure), self.boundary.stage([]):
            self.boundary.read(self.resource)
        self.assertEqual(self.events[0]['capability'], 'B02_AUTHORITY_READ')

    def test_synthetic_fixture_read_denied(self):
        resource = guard.Resource('synthetic-fixture', self.path, 'B02_FIXTURE_READ')
        boundary = guard.Boundary([resource], self.events.append)
        with self.assertRaises(ProtocolFailure), boundary.stage([]):
            boundary.read(resource)
        self.assertEqual(self.events[0]['capability'], 'B02_FIXTURE_READ')

    def test_synthetic_static_evaluation_denied(self):
        calls = []
        with self.assertRaises(ProtocolFailure), self.boundary.stage([]):
            self.boundary.evaluate(self.resource, calls.append)
        self.assertEqual(calls, [])
        self.assertEqual(self.events[0]['capability'], 'B02_STATIC_EVALUATION')

    def test_false_resource_declaration_rejected(self):
        fake = guard.Resource('generic', self.path, 'REGRESSION_EVIDENCE')
        with self.assertRaises(ProtocolFailure), self.boundary.stage(['REGRESSION_EVIDENCE']):
            self.boundary.read(fake)

    def test_synthetic_hardlink_alias_denied(self):
        alias = self.path.with_name('alias.txt')
        alias.hardlink_to(self.path)
        with self.assertRaises(ProtocolFailure), self.boundary.stage([]):
            alias.read_bytes()

    def test_generic_harness_stage_allowed(self):
        driver = self.driver('restricted_harness_b02_skips', harness.authorization()['capabilities'])
        driver.initialize()
        self.assertEqual(driver.batch(29)['disposition'], 'COMPLETE')

    def test_safe_prohibited_accounting(self):
        # No sealed module import, requirement/profile load or SUT invocation.
        self.assertEqual(harness.accounting()['prohibited_b02_skips'], 36)
        self.assertFalse(harness.accounting()['protected_content_loaded'])

    def test_index_mutation_rejected(self):
        path = self.fixture.parent / 'synthetic-index.json'
        value = harness.index()
        value['tests'].pop(next(iter(value['tests'])))
        path.write_bytes(canonical(value) + b'\n')
        with patch.object(harness, 'INDEX', path), self.assertRaises(ProtocolFailure):
            harness.accounting()

    def test_restricted_harness_excludes_before_sut_exposure(self):
        calls = []
        before = set(sys.modules)
        with self.boundary.stage(['HARNESS_EXECUTION', 'TEST_DISCOVERY']):
            suite = harness.suite(list(harness.index()['tests']), calls.append)
            result = unittest.TextTestRunner(stream=io.StringIO()).run(suite)
        self.assertTrue(result.wasSuccessful())
        self.assertEqual(len(result.skipped), 36)
        self.assertEqual(calls, [])
        self.assertEqual(set(sys.modules), before)

    def test_prohibited_factory_setup_and_test_never_reached(self):
        identity = next(iter(harness.index()['tests']))
        def dangerous_factory(identity):
            raise AssertionError('import/constructor/setup/SUT would expose protected fixture')
        result = unittest.TextTestRunner(stream=io.StringIO()).run(harness.suite([identity], dangerous_factory))
        self.assertEqual(len(result.skipped), 1)
        self.assertEqual(result.errors, [])

    def test_allowed_case_constructed_normally(self):
        calls = []
        def factory(identity):
            calls.append(identity)
            return unittest.FunctionTestCase(lambda: None)
        result = unittest.TextTestRunner(stream=io.StringIO()).run(harness.suite(['ordinary.case'], factory))
        self.assertEqual(calls, ['ordinary.case'])
        self.assertTrue(result.wasSuccessful())

    def test_capability_binding_deterministic(self):
        self.assertEqual(guard.binding(['TEST_DISCOVERY', 'REGRESSION_EVIDENCE']),
                         guard.binding(['REGRESSION_EVIDENCE', 'TEST_DISCOVERY']))
        self.assertEqual(self.driver('ordinary', []).binding, self.driver('ordinary', []).binding)

    def test_capability_mutation_invalidates_binding(self):
        driver = self.driver('ordinary', [])
        driver.initialize()
        driver.stages['ordinary']['capabilities'] = ['TEST_DISCOVERY']
        with self.assertRaises(ProtocolFailure):
            driver.batch(29)

    def test_stage_name_mutation_does_not_change_authorization(self):
        first = self.driver('ordinary', ['REGRESSION_EVIDENCE'])
        second = self.driver('confirm_b02_remains_sealed', ['REGRESSION_EVIDENCE'])
        self.assertEqual(first.binding['stages'][0]['capability_binding'], second.binding['stages'][0]['capability_binding'])
        # Evidence identity still binds descriptive names; rename is not a resume.
        self.assertNotEqual(first.binding, second.binding)

    def test_resource_violation_persisted_and_no_retry(self):
        driver = self.driver('generic_regression', ['REGRESSION_EVIDENCE'],
                             run=lambda timeout: self.path.read_bytes())
        driver.initialize()
        self.assertEqual(driver.batch(29)['disposition'], 'STOPPED')
        evidence = bounded.reload(self.fixture.output / 'quarantine.json')
        self.assertEqual(evidence['classification'], 'R5_61_PROTOCOL_HALT')
        self.assertEqual(bounded.reload(self.fixture.output / 'receipt-generic_regression.json')['status'], 'INCOMPLETE')
        with self.assertRaises(ProtocolFailure):
            driver.batch(29)

    def test_swallowed_denial_still_halts(self):
        with self.assertRaises(ProtocolFailure), self.boundary.stage([]):
            try:
                self.path.read_bytes()
            except ProtocolFailure:
                pass

    def test_subprocess_escape_rejected_without_start(self):
        with self.assertRaises(ProtocolFailure), self.boundary.stage(['HARNESS_EXECUTION']):
            subprocess.run([sys.executable, '-c', 'raise AssertionError("must not start")'])
        self.assertEqual(self.events[0]['capability'], 'UNMEDIATED_EXECUTION')

    def test_cross_thread_direct_read_denied(self):
        errors = []
        def attempt():
            try:
                self.path.read_bytes()
            except ProtocolFailure:
                errors.append('DENIED')
        with self.assertRaises(ProtocolFailure), self.boundary.stage([]):
            thread = threading.Thread(target=attempt)
            thread.start()
            thread.join()
        self.assertEqual(errors, ['DENIED'])

    def test_qualified_authority_identity_linkage(self):
        qualified = tier.seal({'protocol': authority.PROTOCOL, 'kind': 'qualified-authority',
                               'status': 'QUALIFIED', 'policy_binding': 'synthetic-policy',
                               'frozen_authority': {'synthetic': 'sealed'}})
        driver = self.driver('ordinary', [], authority=qualified['identity'],
                             live_authority=lambda: qualified['identity'])
        driver.initialize()
        self.assertEqual(driver.binding['authority'], qualified['identity'])
        driver.live_authority = lambda: 'synthetic-mutated-authority'
        with self.assertRaises(ProtocolFailure):
            driver.batch(29)

    def test_certificate_v2_receipt_linkage_synthetic_qualifier(self):
        # Linkage witness only: no real authority-member reads or new production
        # qualification. Existing independently qualified qualifier is substituted
        # with a sealed synthetic result at its external interface.
        qualified = tier.seal({'protocol': authority.PROTOCOL, 'kind': 'qualified-authority',
                               'status': 'QUALIFIED', 'policy_binding': 'synthetic-policy',
                               'frozen_authority': {'synthetic': 'sealed'}})
        evidence = {}
        mechanisms = {}
        results = {'identity': {'successful': True, 'semantic_count': 30},
                   'authority': {'successful': True, 'qualified_authority': qualified['identity']},
                   'contamination': {'successful': True, 'findings': []},
                   'workspace': {'successful': True, 'dedicated': True}}
        stages = {}
        for name, result in results.items():
            mechanisms[name] = digest(canonical({'capability_binding': guard.binding(['REGRESSION_EVIDENCE']),
                                                  'stage': name}))
            stages[name] = {'mechanism': mechanisms[name], 'cost': self.cost,
                            'capabilities': ['REGRESSION_EVIDENCE'],
                            'run': lambda timeout, result=result: result}
        driver = self.driver('ignored', [], stages=stages, authority=qualified['identity'],
                             live_authority=lambda: qualified['identity'])
        driver.initialize()
        self.assertEqual(driver.batch(100)['disposition'], 'COMPLETE')
        evidence = driver.validate()[0]
        capsule = self.fixture.frozen
        policy = {'experiment': 'synthetic:r561', 'stages': mechanisms,
                  'qualified_authority': qualified['identity'], 'authority_role': capsule['roles']['authority'],
                  'semantic_count': 30, 'canonical_protocol': tier.CANONICAL_PROTOCOL,
                  'recorder': capsule['policy']['recorder'],
                  'observation_state': {'reservations': 0, 'dispatches': 0, 'completions': 0}}
        with patch.object(authority, 'qualify', return_value=qualified):
            certificate = certificates.certificate(qualified, capsule, evidence, policy,
                self.fixture.root, {}, trusted_policy_identity='synthetic-policy')
            self.assertTrue(certificates.validate(certificate, qualified, capsule, evidence, policy,
                capsule, self.fixture.root, {}, trusted_policy_identity='synthetic-policy'))
            changed = dict(policy, qualified_authority='mutated')
            with self.assertRaises(ProtocolFailure):
                certificates.certificate(qualified, capsule, evidence, changed,
                    self.fixture.root, {}, trusted_policy_identity='synthetic-policy')

    def test_observation_controls_unchanged(self):
        gate = self.fixture.gate()
        with self.assertRaises(ProtocolFailure):
            gate.observe_synthetic('synthetic:mineral', lambda: (_ for _ in ()).throw(RuntimeError()))
        with self.assertRaises(ProtocolFailure):
            gate.observe_synthetic('synthetic:mineral', lambda: {'successful': True})


if __name__ == '__main__':
    unittest.main()
