"""Independent mode confusion and binding challenges; no actual opening calls."""
import copy
from pathlib import Path
import unittest
from unittest.mock import patch

from benchmark.evaluation import certificate_r5_68 as modes
from benchmark.evaluation import certificate_r5_66 as historical
from benchmark.evaluation import sealed_authority_r5_66 as sealed
from benchmark.evaluation import publication_r5_59 as publication
from benchmark.evaluation import checkout_r5_52 as checkout
from benchmark.evaluation import tier2_r5_51 as tier
from benchmark.evaluation import capability_guard_r5_61 as guard
from benchmark.evaluation import test_sealed_authority_r5_66 as fixtures
from benchmark.evaluation.recorder_r5_43 import canonical, digest, loads, ProtocolFailure


def declaration(qualified, capsule, policy, qualification, mode):
    # Fixture construction is not a trust registry. The reviewed caller supplies
    # the separate external pin, never an identity read from an arbitrary payload.
    return {'protocol': modes.DECLARATION_PROTOCOL, 'schema_binding': modes.DECLARATION_SCHEMA_PIN,
        'experiment': policy['experiment'], 'qualification': qualification, 'mode': mode,
        'scope': modes.SCOPES[mode], 'authority': qualified['authority'],
        'qualified_authority': qualified['identity'], 'resource_policy': qualified['policy_binding'],
        'capsule': capsule['identity'], 'certificate_policy': digest(canonical(policy)),
        'allowed_operation': modes.OPERATIONS[mode], 'sealed_policy': 'CLOSED_NO_OPEN_NO_OBSERVATION',
        'observation_state': 'ZERO_UNOBSERVED', 'seal_open_authorized': False}


def fixture_inputs(qualified, experiment, qualification):
    capsule = tier.seal({'protocol': tier.PROTOCOL, 'kind': 'capsule', 'semantic_count': 30,
        'roles': {r: digest(canonical([qualification, r])) for r in tier.ROLES}, 'unknown': [],
        'policy': {'recorder': 'r568-focused-recorder'}, 'fixture_scope': 'non-B02 mechanism candidate'})
    policy = {'experiment': experiment, 'stages': {n: 'r568-focused-' + n for n in modes.v2.REQUIRED},
        'qualified_authority': qualified['identity'], 'authority_role': capsule['roles']['authority'],
        'semantic_count': 30, 'canonical_protocol': tier.CANONICAL_PROTOCOL,
        'recorder': capsule['policy']['recorder'],
        'observation_state': {'reservations': 0, 'dispatches': 0, 'completions': 0}}
    results = {'identity': {'successful': True, 'semantic_count': 30, 'qualification': qualification},
        'authority': {'successful': True, 'qualified_authority': qualified['identity']},
        'contamination': {'successful': True, 'findings': []},
        'workspace': {'successful': True, 'dedicated': True}}
    evidence = {n: tier.receipt(capsule, capsule, experiment, n, policy['stages'][n], 'PASS', results[n])
                for n in results}
    return capsule, policy, evidence


class CertificateModeTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.SealedAuthorityTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.qualified = self.fixture.qualified
        self.authority = self.fixture.auth
        self.qualification = digest(canonical({'experiment': 'R5.68-production-mode-independent'}))
        self.mode = modes.PRODUCTION
        self.capsule, self.policy, self.evidence = fixture_inputs(
            self.qualified, 'R5.68-production-mode-independent', self.qualification)
        self.refresh()

    def refresh(self):
        self.declaration = declaration(self.qualified, self.capsule, self.policy, self.qualification, self.mode)
        self.pin = digest(canonical(self.declaration))

    def binding(self):
        return {'trusted_declaration_identity': self.pin, 'mode': self.mode, 'qualification': self.qualification}

    def assemble(self):
        return modes.certificate(self.qualified, self.capsule, self.evidence, self.policy,
                                 self.authority, self.declaration, **self.binding())

    def validate(self, cert):
        return modes.validate(cert, self.qualified, self.capsule, self.evidence, self.policy,
                              self.capsule, self.authority, self.declaration, **self.binding())

    def operation(self, cert, op):
        return modes.require_operation(cert, op, self.qualified, self.capsule, self.evidence, self.policy,
            self.capsule, self.authority, self.declaration, **self.binding())

    def rename(self, name):
        self.capsule, self.policy, self.evidence = fixture_inputs(self.qualified, name, self.qualification)
        self.refresh()

    def test_01_synthetic_mode_preserved(self):
        self.mode = modes.SYNTHETIC
        self.refresh()
        self.assertEqual(self.assemble()['issuance_scope'], 'SYNTHETIC_ONLY')

    def test_02_production_eligibility(self):
        self.assertTrue(self.operation(self.assemble(), 'PRODUCTION_GATE_QUALIFIED'))

    def test_03_arbitrary_identity_rejected(self):
        self.policy['experiment'] = 'production:fully-approved'
        with self.assertRaises(ProtocolFailure):
            self.assemble()

    def test_04_explicit_declaration_required(self):
        for value in ({}, None):
            self.declaration = value
            with self.assertRaises((ProtocolFailure, publication.security.SecretRejected)):
                self.assemble()

    def test_05_every_declaration_field_pinned(self):
        original = copy.deepcopy(self.declaration)
        for field in original:
            with self.subTest(field=field):
                self.declaration = {**original, field: True if field == 'seal_open_authorized' else 'changed'}
                with self.assertRaises(ProtocolFailure):
                    self.assemble()
        self.declaration = original

    def test_06_mode_mutation_after_seal(self):
        cert = self.assemble()
        cert['mode'] = modes.SYNTHETIC
        with self.assertRaises(ProtocolFailure):
            self.validate(cert)
        cert = tier.seal({k: v for k, v in cert.items() if k != 'identity'})
        with self.assertRaises(ProtocolFailure):
            self.validate(cert)

    def test_07_synthetic_cannot_satisfy_production(self):
        self.mode = modes.SYNTHETIC
        self.refresh()
        cert = self.assemble()
        with self.assertRaises(ProtocolFailure):
            self.operation(cert, 'PRODUCTION_GATE_QUALIFIED')
        self.mode = modes.PRODUCTION
        self.refresh()
        with self.assertRaises(ProtocolFailure):
            self.validate(cert)

    def test_08_no_seal_open_operation(self):
        cert = self.assemble()
        for op in (sealed.OPEN, 'B02_SEAL_OPEN_AUTHORIZED', 'B02_OBSERVATION', 'SYNTHETIC_GATE_QUALIFIED'):
            with self.subTest(op=op), self.assertRaises(ProtocolFailure):
                self.operation(cert, op)
        self.assertFalse(cert['seal_open_authorized'])
        self.assertFalse(cert['b02_observation_authorized'])

    def test_09_production_cannot_open_synthetic_without_grant(self):
        with self.assertRaises(ProtocolFailure):
            self.fixture.open(grant=self.assemble())
        self.assertEqual(self.fixture.store.reads, 0)
        self.assertFalse(self.fixture.ledger.exists())

    def test_10_actual_b02_operation_denied_before_opener(self):
        # A real opener is deliberately absent. Test the operation boundary,
        # never invoke a protected resource read or actual observation API.
        with self.assertRaises(ProtocolFailure):
            self.operation(self.assemble(), 'B02_SEAL_OPEN_AUTHORIZED')

    def actual(self):
        from benchmark.results.phase5c.r5_66_inventory import ROOT, inventory
        protected = {r.path.resolve() for r in guard.repository_resources(ROOT)}
        original = Path.read_bytes
        calls = []
        def checked(path):
            self.assertNotIn(path.resolve(), protected)
            calls.append(path)
            return original(path)
        with patch.object(Path, 'read_bytes', checked), patch.object(checkout, 'blobs',
                side_effect=AssertionError('blob content requested')):
            value = inventory()
            policy = {k: value[k] for k in ('authority', 'policy_binding', 'members')}
            policy['frozen_authority'] = {n: r['sha256'] for n, r in value['members'].items() if r['frozen']}
            auth = sealed.Authority(ROOT, policy, trusted_policy_identity=sealed.identity(policy),
                                    observer=sealed.GitMetadata(ROOT))
            qualified = auth.qualify()
        return qualified

    def test_11_actual_eleven_no_reads(self):
        qualified = self.actual()
        self.assertEqual(len(qualified['verification']), 11)
        for row in qualified['verification'].values():
            self.assertEqual(row['mode'], sealed.SEALED)
            self.assertEqual(row['seal'], 'CLOSED')
            self.assertFalse(row['current_content_read'])

    def test_12_actual_two_frozen_pins(self):
        qualified = self.actual()
        self.assertEqual(len(qualified['frozen_authority']), 2)
        for name, commitment in qualified['frozen_authority'].items():
            self.assertEqual(qualified['verification'][name]['commitment'], commitment)
            self.assertTrue(qualified['verification'][name]['frozen'])

    def test_13_canonical_reload(self):
        cert = loads(canonical(self.assemble()))
        self.assertTrue(self.validate(cert))

    def test_14_deterministic_reproduction(self):
        self.assertEqual(canonical(self.assemble()), canonical(self.assemble()))

    def test_15_authority_linkage(self):
        self.fixture.store.mapping['sha256'] = '0' * 64
        with self.assertRaises(ProtocolFailure):
            self.assemble()

    def test_16_capsule_linkage(self):
        self.capsule = tier.seal({**{k: v for k, v in self.capsule.items() if k != 'identity'}, 'changed': True})
        with self.assertRaises(ProtocolFailure):
            self.assemble()

    def test_17_receipt_linkage(self):
        for field, value in (('experiment', 'other'), ('capsule', '0' * 64), ('status', 'FAIL'),
                             ('stage', 'other'), ('mechanism', 'other')):
            before = self.evidence['identity']
            self.evidence['identity'] = tier.seal({**{k: v for k, v in before.items() if k != 'identity'}, field: value})
            with self.subTest(field=field), self.assertRaises(ProtocolFailure):
                self.assemble()
            self.evidence['identity'] = before

    def test_18_prefix_independence(self):
        for name in ('synthetic:production-descriptive-name', 'production:approved', 'B02-seal-open-authorized'):
            self.rename(name)
            self.assertTrue(self.validate(self.assemble()))
        self.mode = modes.SYNTHETIC
        self.rename('plain-independent-qualification')
        self.assertEqual(self.assemble()['mode'], modes.SYNTHETIC)
        self.declaration['scope'] = 'PRODUCTION_SEALED_ONLY'
        with self.assertRaises(ProtocolFailure):
            self.assemble()

    def test_19_issuance_preserves_ledger(self):
        self.assemble()
        self.assertFalse(self.fixture.ledger.exists())
        self.assertFalse(self.fixture.ledger.with_suffix('.result.json').exists())
        self.assertEqual(self.fixture.store.reads, 0)

    def test_20_issuance_preserves_accounting(self):
        before = copy.deepcopy(self.policy['observation_state'])
        self.assemble()
        self.assertEqual(before, self.policy['observation_state'])
        self.policy['observation_state']['reservations'] = 1
        with self.assertRaises(ProtocolFailure):
            self.assemble()

    def test_21_publication_no_fixture_or_credentials(self):
        cert = self.assemble()
        raw = publication.safe_bytes(cert)
        self.assertNotIn(self.fixture.content.strip(), raw)
        for value in ({**cert, 'api_key': publication._values()[0]},
                      {**cert, 'fixture': publication._values()[0]}):
            with self.assertRaises(publication.security.SecretRejected):
                publication.safe_bytes(value)

    def test_22_historical_synthetic_interpretation(self):
        cert, capsule, evidence, policy = self.fixture.fixture_certificate()
        self.assertEqual(cert['version'], 2)
        self.assertEqual(cert['issuance_scope'], 'SYNTHETIC_ONLY')
        self.assertNotIn('mode', cert)
        self.assertTrue(historical.validate(cert, self.qualified, capsule, evidence, policy,
                                            capsule, self.authority))
        with self.assertRaises(ProtocolFailure):
            self.validate(cert)

    def test_23_cross_mode_declarations(self):
        for changed_mode in (modes.SYNTHETIC,):
            self.mode = changed_mode
            with self.assertRaises(ProtocolFailure):
                self.assemble()
        self.refresh()
        self.mode = modes.PRODUCTION
        with self.assertRaises(ProtocolFailure):
            self.assemble()

    def test_24_authorization_mutation_after_seal(self):
        cert = self.assemble()
        cert['authorization_binding'] = '0' * 64
        cert = tier.seal({k: v for k, v in cert.items() if k != 'identity'})
        with self.assertRaises(ProtocolFailure):
            self.validate(cert)

    def test_25_payload_pin_not_authority(self):
        self.pin = '0' * 64
        with self.assertRaises(ProtocolFailure):
            self.assemble()

    def test_26_schema_mutation_rejected(self):
        with self.assertRaises(ValueError):
            modes.DECLARATION_SCHEMA.resolve('0' * 64)
        self.declaration['model_identity'] = 'unused'
        with self.assertRaises(publication.security.SecretRejected):
            self.assemble()

    def test_27_declaration_publication(self):
        raw = publication.safe_bytes(self.declaration, schema=modes.DECLARATION_SCHEMA,
                                     schema_identity=modes.DECLARATION_SCHEMA_PIN)
        self.assertEqual(loads(raw), self.declaration)

    def test_28_repin_cannot_permit_open(self):
        self.declaration['seal_open_authorized'] = True
        self.pin = digest(canonical(self.declaration))
        with self.assertRaises(ProtocolFailure):
            self.assemble()
