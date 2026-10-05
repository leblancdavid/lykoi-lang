"""Real subprocess adversaries, synthetic resources and content-free skip metadata."""

import copy
import os
import py_compile
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from benchmark.evaluation import mediated_child_r5_62 as child
from benchmark.evaluation import bounded_driver_r5_57 as budget
from benchmark.evaluation import capability_guard_r5_61 as guard
from benchmark.evaluation import restricted_harness_r5_61 as exclusion
from benchmark.evaluation import tier2_r5_51 as tier
from benchmark.evaluation import test_tier2_r5_51 as fixtures
from benchmark.evaluation import qualified_authority_r5_55 as authority
from benchmark.evaluation import certificate_r5_55 as certificates
from benchmark.evaluation.recorder_r5_43 import canonical, digest, ProtocolFailure

ROOT = Path(__file__).resolve().parents[2]
PROBE = 'benchmark.evaluation.child_witnesses_r5_62'
SAFE = 'benchmark.evaluation.safe_workers_r5_62'


class ChildTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.Tier2Tests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.workers = child.registry(ROOT, {
            'probe': (PROBE, 'probe', [PROBE.replace('.', '/') + '.py']),
            'harness': (SAFE, 'harness', [SAFE.replace('.', '/') + '.py', PROBE.replace('.', '/') + '.py']),
            'sut': (SAFE, 'sut', [SAFE.replace('.', '/') + '.py', 'benchmark/evaluation/synthetic_sut_r5_62.py'])})
        self.pin = digest(canonical(self.workers))
        self.protected = self.fixture.parent / 'sealed-synthetic'
        self.protected.write_text('synthetic protected content')
        self.ordinary = self.fixture.parent / 'ordinary'
        self.ordinary.write_text('ordinary')
        self.resources = guard.repository_resources(ROOT) + (
            guard.Resource('synthetic', self.protected, 'B02_AUTHORITY_READ'),)
        self.cost = budget.Cost(1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1)

    def make(self, caps=None, parent=None, inputs=None, worker='probe', environment=None):
        caps = ['REGRESSION_EVIDENCE'] if caps is None else caps
        adapter = child.Child(ROOT, self.workers, self.pin, worker, caps, inputs,
                              parent_environment=environment)
        stages = {'generic': {'capabilities': caps if parent is None else parent,
                  'mechanism': 'synthetic-mediated', 'cost': self.cost, 'run': adapter}}
        driver = budget.Driver(self.fixture.output, 'synthetic:r562', self.fixture.frozen,
            'synthetic-authority', stages, self.fixture.capture, lambda: 'synthetic-authority',
            resources=self.resources)
        driver.initialize()
        return driver, adapter

    def execute(self, **kwargs):
        driver, adapter = self.make(**kwargs)
        driver.batch(60)
        receipt = budget.reload(self.fixture.output / 'receipt-generic.json')
        return driver, adapter, receipt

    def test_generic_same_capabilities(self):
        _, _, receipt = self.execute()
        self.assertEqual(receipt['status'], 'PASS')
        self.assertEqual(receipt['result']['mediated_child']['stage'], 'generic')

    def test_narrower_capabilities(self):
        _, adapter, receipt = self.execute(parent=['REGRESSION_EVIDENCE', 'TEST_DISCOVERY'])
        self.assertEqual(receipt['status'], 'PASS')
        self.assertEqual(adapter.value['capabilities'], ['REGRESSION_EVIDENCE'])

    def test_empty_attenuation(self):
        self.assertEqual(self.execute(caps=[], parent=['REGRESSION_EVIDENCE'])[2]['status'], 'PASS')

    def test_escalation_rejected(self):
        with self.assertRaises(ProtocolFailure):
            self.make(caps=['REGRESSION_EVIDENCE', 'TEST_DISCOVERY'], parent=['REGRESSION_EVIDENCE'])
        self.assertFalse(list(self.fixture.output.glob('attempt-*')))

    def test_protected_escalation_rejected(self):
        with self.assertRaises(ProtocolFailure):
            self.make(caps=['B02_AUTHORITY_READ'])

    def mutate(self, field, value):
        _, adapter = self.make()
        changed = copy.deepcopy(adapter.value)
        changed[field] = value
        with self.assertRaises(ProtocolFailure):
            child.validate(changed, adapter.expected)

    def test_stage_mutation(self):
        self.mutate('stage', 'forged')

    def test_qualification_mutation(self):
        self.mutate('qualification', 'forged')

    def test_capability_mutation(self):
        self.mutate('capabilities', ['TEST_DISCOVERY'])

    def test_resource_mutation(self):
        self.mutate('resources', [])

    def test_authority_mutation(self):
        self.mutate('authority', 'forged')

    def test_worker_mutation(self):
        driver, adapter = self.make()
        adapter.value['selection']['worker'] = 'unknown'
        with self.assertRaises(ProtocolFailure):
            driver.batch(60)

    def test_unknown_worker(self):
        with self.assertRaises(ProtocolFailure):
            child.Child(ROOT, self.workers, self.pin, 'unknown', [])

    def test_alias_substitution(self):
        changed = copy.deepcopy(self.workers)
        changed['workers']['probe'] = changed['workers']['harness']
        with self.assertRaises(ProtocolFailure):
            child.Child(ROOT, changed, self.pin, 'probe', [])

    def test_modified_implementation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            module = root / 'worker.py'
            module.write_text('def run(context): return {"successful": True}\n')
            registry = child.registry(root, {'known': ('worker', 'run', ['worker.py'])})
            module.write_text('raise AssertionError("substitution")\n')
            with self.assertRaises(ProtocolFailure):
                child.Child(root, registry, digest(canonical(registry)), 'known', [])

    def test_exclusion_binding_mutation(self):
        _, adapter = self.make()
        adapter.value['selection']['exclusion'] = 'forged'
        with self.assertRaises(ProtocolFailure):
            child.validate(adapter.value, adapter.expected)

    def test_exclusion_index_mutation(self):
        driver, adapter = self.make()
        with patch.object(exclusion, 'INDEX_PIN', 'forged'):
            with self.assertRaises(ProtocolFailure):
                child.validate(adapter.value, adapter.expected)

    def test_protected_access_child_quarantine(self):
        driver, _, receipt = self.execute(inputs={'action': 'protected', 'path': str(self.protected)})
        self.assertEqual(receipt['status'], 'INCOMPLETE')
        self.assertEqual(budget.reload(self.fixture.output / 'quarantine.json')['classification'], 'R5_62_PROTOCOL_HALT')
        with self.assertRaises(ProtocolFailure):
            driver.batch(60)

    def test_ordinary_resource_allowed(self):
        self.assertEqual(self.execute(inputs={'action': 'ordinary', 'path': str(self.ordinary)})[2]['status'], 'PASS')

    def test_order_exclusion_before_discovery(self):
        result = self.execute()[2]['result']
        self.assertEqual(result['startup_order'], ['binding-validation', 'safe-exclusion-installation',
                                                  'worker-discovery', 'execution'])

    def test_restricted_harness_36_metadata_skips(self):
        ids = list(exclusion.index()['tests'])
        _, _, receipt = self.execute(worker='harness', inputs={'identities': ids},
            caps=['HARNESS_EXECUTION', 'TEST_DISCOVERY', 'REGRESSION_EVIDENCE'])
        self.assertEqual(receipt['status'], 'PASS')
        self.assertEqual(receipt['result']['skipped'], 36)
        self.assertEqual(receipt['result']['discovered'], 36)

    def test_sealed_modules_not_needed(self):
        ids = list(exclusion.index()['tests'])
        # Registered sealed test modules cannot be opened in the child. PASS proves
        # indexed placeholders bypass those imports, fixtures and SUT invocation.
        self.assertEqual(self.execute(worker='harness', inputs={'identities': ids})[2]['status'], 'PASS')

    def test_environment_secret_and_ai_state_excluded(self):
        provider_name = 'OPENAI_' + 'API_KEY'
        second_provider = 'ANTHROPIC_' + 'API_KEY'
        environment = {provider_name: 'synthetic-private-value', second_provider: 'private',
                       'PATH': 'private', 'OPENCODE_CONFIG': 'private', 'PYTHONPATH': 'private'}
        receipt = self.execute(inputs={'action': 'environment'}, environment=environment)[2]
        self.assertEqual(receipt['status'], 'PASS')
        self.assertNotIn(b'synthetic-private-value', canonical(receipt))

    def test_ai_credentials_not_required(self):
        self.assertEqual(self.execute(environment={})[2]['status'], 'PASS')

    def test_secret_diagnostics_withheld(self):
        private = 'sk-' + 'A' * 24
        receipt = self.execute(inputs={'action': 'secret'})[2]
        self.assertEqual(receipt['status'], 'INCOMPLETE')
        self.assertNotIn(private.encode(), canonical(receipt))

    def test_fail_receipt(self):
        driver, _, receipt = self.execute(inputs={'action': 'fail'})
        self.assertEqual(receipt['status'], 'FAIL')
        self.assertEqual(receipt['result']['mediated_child']['status'], 'FAIL')
        with self.assertRaises(ProtocolFailure):
            driver.validate()

    def test_interrupted_child_incomplete_no_retry(self):
        marker = self.fixture.parent / 'worker-started'
        driver, adapter = self.make(inputs={'action': 'interrupt', 'marker': str(marker)})
        original = adapter.__class__.__call__
        with patch.object(adapter.__class__, '__call__', lambda instance, timeout: original(instance, 1)):
            driver.batch(60)
        self.assertTrue(marker.exists())
        receipt = budget.reload(self.fixture.output / 'receipt-generic.json')
        self.assertEqual(receipt['status'], 'INCOMPLETE')
        self.assertEqual(receipt['result']['child_execution']['status'], 'INCOMPLETE')
        with self.assertRaises(ProtocolFailure):
            driver.batch(60)

    def test_mediation_budget_required(self):
        adapter = child.Child(ROOT, self.workers, self.pin, 'probe', [])
        with self.assertRaises(ProtocolFailure):
            budget.Driver(self.fixture.output, 'synthetic:r562', self.fixture.frozen, 'synthetic-authority',
                {'generic': {'capabilities': [], 'mechanism': 'm', 'cost': budget.Cost(), 'run': adapter}},
                self.fixture.capture, lambda: 'synthetic-authority', resources=self.resources)

    def test_mediation_budget_admission(self):
        driver, _ = self.make()
        row = driver.batch(self.cost.required() + 5 - .001)
        self.assertEqual(row['disposition'], 'BOUNDARY')
        self.assertFalse(list(self.fixture.output.glob('attempt-*')))
        self.assertEqual(row['decisions'][0]['lifecycle']['child_validation'], 1)

    def test_arbitrary_subprocess_inside_child_rejected(self):
        self.assertEqual(self.execute(inputs={'action': 'subprocess'})[2]['status'], 'INCOMPLETE')
        self.assertTrue((self.fixture.output / 'quarantine.json').exists())

    def test_deterministic_binding(self):
        first = child.Child(ROOT, self.workers, self.pin, 'probe', ['TEST_DISCOVERY', 'REGRESSION_EVIDENCE'])
        second = child.Child(ROOT, self.workers, self.pin, 'probe', ['REGRESSION_EVIDENCE', 'TEST_DISCOVERY'])
        self.assertEqual(first.descriptor, second.descriptor)

    def test_mixed_restricted_harness(self):
        ids = list(exclusion.index()['tests']) + [PROBE + '.OrdinaryTest.test_ordinary']
        receipt = self.execute(worker='harness', inputs={'identities': ids})[2]
        self.assertEqual(receipt['status'], 'PASS')
        self.assertEqual(receipt['result']['discovered'], 37)
        self.assertEqual(receipt['result']['skipped'], 36)

    def test_content_bound_sut_allowed(self):
        path = 'benchmark/evaluation/synthetic_sut_r5_62.py'
        receipt = self.execute(worker='sut', inputs={'path': path, 'sha256': digest((ROOT / path).read_bytes()), 'argv': []})[2]
        self.assertEqual(receipt['status'], 'PASS')

    def test_registered_sut_descendant_from_generic_worker(self):
        receipt = self.execute(inputs={'action': 'sut'})[2]
        self.assertEqual(receipt['status'], 'PASS')
        self.assertEqual(receipt['result']['sut_exit'], 0)

    def test_registered_sut_descendant_fail(self):
        self.assertEqual(self.execute(inputs={'action': 'sut', 'argv': ['fail']})[2]['status'], 'FAIL')

    def test_registered_sut_descendant_protected_access_quarantines(self):
        receipt = self.execute(inputs={'action': 'sut', 'argv': ['read', str(self.protected)]})[2]
        self.assertEqual(receipt['status'], 'INCOMPLETE')
        self.assertEqual(receipt['result']['child_execution']['status'], 'SECURITY_FAILURE')
        self.assertTrue((self.fixture.output / 'quarantine.json').exists())

    def test_descendant_escalation_rejected(self):
        driver, adapter = self.make(caps=['REGRESSION_EVIDENCE'], parent=['REGRESSION_EVIDENCE', 'TEST_DISCOVERY'])
        descendant = child.Child(ROOT, self.workers, self.pin, 'probe', ['REGRESSION_EVIDENCE', 'TEST_DISCOVERY'])
        with self.assertRaises(ProtocolFailure):
            descendant.bind_descendant(adapter.value, driver.boundary)

    def test_sut_fail_represented(self):
        path = 'benchmark/evaluation/synthetic_sut_r5_62.py'
        receipt = self.execute(worker='sut', inputs={'path': path, 'sha256': digest((ROOT / path).read_bytes()), 'argv': ['fail']})[2]
        self.assertEqual(receipt['status'], 'FAIL')

    def test_sut_not_in_registry_rejected(self):
        with self.assertRaises(ProtocolFailure):
            self.make(worker='sut', inputs={'path': 'arbitrary.py', 'sha256': 'forged', 'argv': []})

    def test_arbitrary_test_module_not_in_registry(self):
        with self.assertRaises(ProtocolFailure):
            self.make(worker='harness', inputs={'identities': ['arbitrary.Worker.test_run']})

    def test_legacy_command_adapter_closed_outside_driver(self):
        with self.assertRaises(ProtocolFailure):
            budget.child(['arbitrary'], ROOT, {}, self.fixture.output / 'unused')(10)

    def test_production_adapter_selects_qualified_worker(self):
        adapter = budget.qualified_child(ROOT, self.workers, self.pin, 'probe', [])
        self.assertIsInstance(adapter, child.Child)

    def test_child_receipt_proof_mutation_rejected(self):
        _, adapter, receipt = self.execute()
        adapter.check_result(receipt['result'], 'PASS')
        changed = copy.deepcopy(receipt['result'])
        changed['mediated_child']['worker_identity'] = 'substituted'
        with self.assertRaises(ProtocolFailure):
            adapter.check_result(changed, 'PASS')

    def test_worker_result_mutation_rejected(self):
        _, adapter, receipt = self.execute()
        changed = copy.deepcopy(receipt['result'])
        changed['extra'] = 'mutated'
        with self.assertRaises(ProtocolFailure):
            adapter.check_result(changed, 'PASS')

    def test_substituted_bytecode_not_worker_authority(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in child.RUNTIME:
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((ROOT / name).read_bytes())
            module = root / 'witness.py'
            permitted = b"def run(context): return {'successful': True} \n"
            substituted = b"def run(context): return {'successful': False}\n"
            self.assertEqual(len(permitted), len(substituted))
            module.write_bytes(substituted)
            stamp = module.stat()
            py_compile.compile(str(module), doraise=True)
            module.write_bytes(permitted)
            os.utime(module, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))
            workers = child.registry(root, {'known': ('witness', 'run', ['witness.py'])})
            adapter = child.Child(root, workers, digest(canonical(workers)), 'known', [])
            stages = {'generic': {'capabilities': [], 'mechanism': 'synthetic-bytecode',
                                 'cost': self.cost, 'run': adapter}}
            driver = budget.Driver(self.fixture.output, 'synthetic:r562', self.fixture.frozen,
                'synthetic-authority', stages, self.fixture.capture, lambda: 'synthetic-authority',
                resources=self.resources)
            driver.initialize()
            driver.batch(60)
            self.assertEqual(driver.validate()[0]['generic']['status'], 'PASS')

    def test_environment_mutation_launch_rejected_without_worker(self):
        driver, adapter = self.make()
        adapter.environment['EXTRA'] = 'changed'
        driver.batch(60)
        receipt = budget.reload(self.fixture.output / 'receipt-generic.json')
        self.assertEqual(receipt['status'], 'INCOMPLETE')
        self.assertEqual(receipt['result']['child_execution']['status'], 'LAUNCH_REJECTED')
        self.assertIs(receipt['result']['child_execution']['worker_started'], False)

    def test_forged_rehashed_capabilities(self):
        _, adapter = self.make()
        changed = copy.deepcopy(adapter.value)
        changed['capabilities'] = ['REGRESSION_EVIDENCE', 'TEST_DISCOVERY']
        with self.assertRaises(ProtocolFailure):
            child.validate(changed, digest(canonical(changed)))

    def test_certificate_v2_child_receipt_linkage(self):
        qualified = tier.seal({'protocol': authority.PROTOCOL, 'kind': 'qualified-authority',
            'status': 'QUALIFIED', 'policy_binding': 'synthetic-policy', 'frozen_authority': {'synthetic': 'sealed'}})
        results = {'identity': {'successful': True, 'semantic_count': 30},
            'authority': {'successful': True, 'qualified_authority': qualified['identity']},
            'contamination': {'successful': True, 'findings': []},
            'workspace': {'successful': True, 'dedicated': True}}
        stages = {}
        for name, result in results.items():
            adapter = child.Child(ROOT, self.workers, self.pin, 'probe', ['REGRESSION_EVIDENCE'],
                                  {'action': 'payload', 'result': result})
            stages[name] = {'capabilities': ['REGRESSION_EVIDENCE'], 'cost': self.cost,
                'mechanism': digest(canonical(adapter.descriptor)), 'run': adapter}
        driver = budget.Driver(self.fixture.output, 'synthetic:r562', self.fixture.frozen,
            qualified['identity'], stages, self.fixture.capture, lambda: qualified['identity'], resources=self.resources)
        driver.initialize()
        self.assertEqual(driver.batch(110)['disposition'], 'COMPLETE')
        evidence = driver.validate()[0]
        capsule = self.fixture.frozen
        policy = {'experiment': 'synthetic:r562', 'stages': {n: s['mechanism'] for n, s in stages.items()},
            'qualified_authority': qualified['identity'], 'authority_role': capsule['roles']['authority'],
            'semantic_count': 30, 'canonical_protocol': tier.CANONICAL_PROTOCOL,
            'recorder': capsule['policy']['recorder'],
            'observation_state': {'reservations': 0, 'dispatches': 0, 'completions': 0}}
        with patch.object(authority, 'qualify', return_value=qualified):
            certificate = certificates.certificate(qualified, capsule, evidence, policy, self.fixture.root,
                {}, trusted_policy_identity='synthetic-policy')
            self.assertTrue(certificates.validate(certificate, qualified, capsule, evidence, policy,
                capsule, self.fixture.root, {}, trusted_policy_identity='synthetic-policy'))


if __name__ == '__main__':
    unittest.main()
