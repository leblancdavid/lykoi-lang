"""Synthetic protected resources only; prospective consumer adversarial tests."""
import copy
from pathlib import Path
import unittest
from unittest.mock import patch

from benchmark.evaluation import observation_consumer_r5_70 as consumer
from benchmark.evaluation import certificate_r5_68 as modes
from benchmark.evaluation import certificate_r5_66 as historical
from benchmark.evaluation import mediated_child_r5_62 as child
from benchmark.evaluation import capability_guard_r5_61 as guard
from benchmark.evaluation import tier2_r5_51 as tier
from benchmark.evaluation import test_certificate_modes_r5_68 as fixtures
from benchmark.evaluation.recorder_r5_43 import canonical, digest, loads, ProtocolFailure

ROOT = Path(__file__).resolve().parents[2]


class ConsumerTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.CertificateModeTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.sealed = self.fixture.fixture
        self.cert = self.fixture.assemble()
        work, output = self.sealed.root / 'work', self.sealed.root / 'output'
        work.mkdir()
        output.mkdir()
        self.workspace = tier.Workspace(work, output, self.fixture.policy['experiment'])
        self.workspace.enter()
        self.events = []
        self.resources = guard.repository_resources(ROOT) + (guard.Resource(
            self.sealed.row['resource'], self.sealed.root / 'protected.txt', 'B02_FIXTURE_READ'),)
        self.boundary = guard.Boundary(self.resources, self.events.append)
        module = 'benchmark.evaluation.observation_worker_r5_70'
        self.registry = child.registry(ROOT, {'observer': (module, 'observe', [module.replace('.', '/') + '.py'])})
        self.worker = child.Child(ROOT, self.registry, digest(canonical(self.registry)), 'observer',
            ['REGRESSION_EVIDENCE'], {'opening_result': str(self.sealed.ledger.with_suffix('.result.json').resolve()),
                                    'commitment': self.sealed.row['sha256']})
        self.gate = consumer.StaticGate(self.workspace, self.cert, self.fixture.qualified,
            self.fixture.capsule, self.fixture.evidence, self.fixture.policy, lambda: self.fixture.capsule,
            self.fixture.authority, self.fixture.declaration, trusted_declaration_identity=self.fixture.pin,
            qualification=self.fixture.qualification, worker=self.worker, boundary=self.boundary,
            capabilities=['REGRESSION_EVIDENCE', 'CERTIFICATE_LINKAGE'], contamination=lambda: [])
        self.authorization = {'protocol': consumer.PROTOCOL, 'operation': consumer.OBSERVE,
            'certificate': self.cert['identity'], 'qualification': self.fixture.qualification,
            'opening': self.sealed.grant}
        self.pin = digest(canonical(self.authorization))

    def observe(self, authorization=None, pin=None, ledger=None):
        return self.gate.observe_synthetic(self.sealed.reference, self.sealed.store,
            self.authorization if authorization is None else authorization,
            trusted_observation_identity=self.pin if pin is None else pin,
            ledger=self.sealed.ledger if ledger is None else ledger)

    def mutate(self, field, value, reseal=True):
        cert = copy.deepcopy(self.cert)
        cert[field] = value
        self.gate.cert = tier.seal({k: v for k, v in cert.items() if k != 'identity'}) if reseal else cert
        with self.assertRaises(ProtocolFailure):
            self.gate.prepare()
        self.assertEqual(self.sealed.store.reads, 0)

    def test_01_production_prepare_accepts_v3(self):
        self.assertTrue(self.gate.prepare())
        self.assertEqual(self.gate.recorder.counts()['disposition'], 'zero')

    def test_02_synthetic_mode_cannot_prepare_production(self):
        self.fixture.mode = modes.SYNTHETIC
        self.fixture.refresh()
        self.gate.cert = self.fixture.assemble()
        with self.assertRaises(ProtocolFailure):
            self.gate.prepare()

    def test_03_unknown_version(self):
        self.mutate('version', 4)

    def test_04_mutated_v3(self):
        self.mutate('contamination', 'changed', reseal=False)

    def test_05_qualified_authority_link(self):
        self.mutate('qualified_authority', '0' * 64)

    def test_06_capsule_link(self):
        self.mutate('capsule', '0' * 64)

    def test_07_receipt_link(self):
        self.mutate('receipts', {**self.cert['receipts'], 'identity': '0' * 64})

    def test_08_sealed_evidence_accepted(self):
        self.assertTrue(self.gate.prepare())
        row = self.cert['authority_verification']['protected.txt']
        self.assertEqual(row['mode'], consumer.sealed.SEALED)
        self.assertFalse(row['current_content_read'])

    def test_09_prepare_never_opens(self):
        with patch.object(self.sealed.store, 'open', side_effect=AssertionError('opened')):
            self.gate.prepare()
        self.assertFalse(self.sealed.ledger.exists())

    def test_10_certificate_alone_denied(self):
        self.gate.prepare()
        with self.assertRaises(ProtocolFailure):
            self.observe(authorization=self.cert, pin=digest(canonical(self.cert)))
        self.assertEqual(self.sealed.store.reads, 0)
        self.assertFalse(self.sealed.ledger.exists())
        self.assertEqual(self.gate.recorder.counts()['disposition'], 'zero')

    def test_11_synthetic_end_to_end_once(self):
        self.gate.prepare()
        self.assertEqual(self.sealed.store.reads, 0)
        result = self.observe()
        self.assertTrue(result['successful'])
        self.assertEqual(result['opening_count'], 1)
        self.assertIn('mediated_child', result)
        self.assertEqual(self.sealed.store.reads, 1)
        self.assertEqual(self.gate.recorder.counts()['disposition'], 'one')
        self.assertEqual(loads(self.sealed.ledger.read_bytes())['state'], 'RESERVED')
        self.assertEqual(loads(self.sealed.ledger.with_suffix('.result.json').read_bytes())['state'], 'OPENED')
        dispatch = loads((self.workspace.evidence / 'synthetic-dispatch.json').read_bytes())
        completion = loads((self.workspace.evidence / 'synthetic-completion.json').read_bytes())
        self.assertEqual(dispatch['observation_binding'], self.pin)
        self.assertEqual(completion['dispatch'], digest((self.workspace.evidence / 'synthetic-dispatch.json').read_bytes()))
        with self.assertRaises(ProtocolFailure):
            self.observe()
        self.assertEqual(self.sealed.store.reads, 1)

    def test_12_alternate_ledger_denied(self):
        self.gate.prepare()
        with self.assertRaises(ProtocolFailure):
            self.observe(ledger=self.sealed.root / 'alternate.json')
        self.assertEqual(self.sealed.store.reads, 0)

    def test_13_arbitrary_worker_denied(self):
        self.gate.worker = lambda timeout: {'successful': True}
        with self.assertRaises(ProtocolFailure):
            self.gate.prepare()

    def test_14_guard_protected_read_denied(self):
        self.gate.prepare()
        resource = self.resources[-1]
        with self.assertRaises(ProtocolFailure):
            with self.boundary.stage(self.gate.capabilities):
                self.boundary.read(resource)
        self.assertEqual(self.events[0]['access'], 'DENIED_BEFORE_CONTENT')
        with self.assertRaises(ProtocolFailure):
            self.observe()
        self.assertEqual(self.sealed.store.reads, 0)

    def test_15_no_legacy_validator_dependency(self):
        with patch.object(tier, 'certificate', side_effect=AssertionError('legacy assembler')):
            self.assertTrue(self.gate.prepare())

    def test_16_v2_historical_interpretation(self):
        cert, capsule, receipts, policy = self.sealed.fixture_certificate()
        self.assertTrue(historical.validate(cert, self.fixture.qualified, capsule, receipts, policy,
                                            capsule, self.fixture.authority))
        self.gate.cert = cert
        with self.assertRaises(ProtocolFailure):
            self.gate.prepare()

    def test_17_legacy_production_rejected(self):
        self.gate.cert = tier.seal({'protocol': tier.PROTOCOL, 'kind': 'certificate'})
        with self.assertRaises(ProtocolFailure):
            self.gate.prepare()

    def test_18_authorization_bindings(self):
        self.gate.prepare()
        for field in ('certificate', 'qualification', 'operation', 'protocol'):
            changed = {**self.authorization, field: 'changed'}
            with self.subTest(field=field), self.assertRaises(ProtocolFailure):
                self.observe(authorization=changed, pin=digest(canonical(changed)))
        self.assertEqual(self.sealed.store.reads, 0)

    def test_19_missing_guard_member(self):
        self.gate.boundary = guard.Boundary(guard.repository_resources(ROOT), self.events.append)
        with self.assertRaises(ProtocolFailure):
            self.gate.prepare()

    def test_20_worker_escalation(self):
        self.gate.capabilities = []
        with self.assertRaises(ProtocolFailure):
            self.gate.prepare()

    def test_21_fresh_contamination(self):
        self.gate.contamination = lambda: ['finding']
        with self.assertRaises(ProtocolFailure):
            self.gate.prepare()

    def test_22_capture_drift(self):
        self.gate.capture = lambda: tier.seal({**tier.envelopes.unseal(self.fixture.capsule), 'drift': True})
        with self.assertRaises(ProtocolFailure):
            self.gate.prepare()

    def test_23_b02_no_api_or_grant(self):
        self.assertFalse(hasattr(self.gate, 'observe_b02'))
        self.assertFalse(self.cert['b02_observation_authorized'])
        self.assertFalse(self.cert['seal_open_authorized'])
        self.assertEqual(self.sealed.store.reads, 0)

    def test_24_unknown_protocol(self):
        self.mutate('protocol', 'future-certificate')

    def test_25_worker_mutation_after_prepare(self):
        self.gate.prepare()
        self.worker.value['capabilities'] = ['TEST_DISCOVERY']
        with self.assertRaises(ProtocolFailure):
            self.observe()
        self.assertEqual(self.sealed.store.reads, 0)

    def test_26_explicit_synthetic_flow(self):
        self.fixture.mode = modes.SYNTHETIC
        self.fixture.refresh()
        self.gate.cert = self.fixture.assemble()
        self.gate.declaration = self.fixture.declaration
        self.gate.binding.update(mode=modes.SYNTHETIC, trusted_declaration_identity=self.fixture.pin)
        with self.assertRaises(ProtocolFailure):
            self.gate.prepare()
        self.assertTrue(self.gate.prepare_synthetic())
        self.assertEqual(self.sealed.store.reads, 0)

    def test_27_guard_wrong_path(self):
        wrong = guard.Resource(self.sealed.row['resource'], self.sealed.root / 'other.txt', 'B02_FIXTURE_READ')
        self.gate.boundary = guard.Boundary((wrong,), self.events.append)
        with self.assertRaises(ProtocolFailure):
            self.gate.prepare()

    def test_28_observation_state_mutation(self):
        self.mutate('observation_state', {'reservations': 1, 'dispatches': 0, 'completions': 0})

    def test_29_authority_evidence_mutation(self):
        changed = copy.deepcopy(self.cert['authority_verification'])
        changed['protected.txt']['current_content_read'] = True
        self.mutate('authority_verification', changed)

    def test_30_authorization_requires_external_pin(self):
        self.gate.prepare()
        with self.assertRaises(ProtocolFailure):
            self.observe(pin='0' * 64)
        self.assertEqual(self.sealed.store.reads, 0)

    def test_31_no_accounting_reset(self):
        self.gate.prepare()
        with self.assertRaises(FileExistsError):
            self.gate.prepare()
        self.assertEqual(self.sealed.store.reads, 0)

    def test_32_historical_v1_still_validates(self):
        from benchmark.evaluation import test_tier2_r5_51 as legacy
        fixture = legacy.Tier2Tests()
        fixture.setUp()
        try:
            self.assertTrue(tier.validate(fixture.cert, fixture.frozen, fixture.evidence,
                                          fixture.policy, fixture.capture()))
            self.gate.cert = fixture.cert
            with self.assertRaises(ProtocolFailure):
                self.gate.prepare()
        finally:
            fixture.doCleanups()
