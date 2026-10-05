"""Fresh synthetic adversarial qualification; protected repository content absent."""
import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from benchmark.evaluation import sealed_authority_r5_66 as sealed
from benchmark.evaluation import certificate_r5_66 as certs
from benchmark.evaluation import capability_guard_r5_61 as guard
from benchmark.evaluation import publication_r5_59 as publication
from benchmark.evaluation import tier2_r5_51 as tier
from benchmark.evaluation.recorder_r5_43 import canonical, digest, loads, ProtocolFailure


class SealedAuthorityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.content = b'synthetic exam envelope alpha\n'
        provenance = {'historical_head': 'synthetic-history', 'qualification': 'prior-qualified',
                      'audit': 'prior-independent', 'successor': 'synthetic-authority'}
        self.row = {'resource': 'synthetic:alpha', 'classification': 'SEALED', 'role': 'protected-fixture',
            'sha256': digest(self.content), 'blob': 'synthetic-object-alpha', 'mode': '100644',
            'representation_kind': 'exact-bytes', 'frozen': True, 'authority': 'synthetic-authority',
            'policy_binding': 'historical-policy', 'provenance': provenance,
            'source': 'synthetic-immutable-object', 'worktree_content_verified': False,
            'checkout_observation': 'DEFERRED_UNTIL_OPEN'}
        ordinary = {**copy.deepcopy(self.row), 'resource': 'synthetic:ordinary', 'classification': 'ORDINARY',
                    'sha256': digest(b'ordinary\n'), 'frozen': False}
        (self.root / 'ordinary.txt').write_bytes(b'ordinary\n')
        self.policy = {'authority': 'synthetic-authority', 'policy_binding': 'historical-policy',
            'members': {'protected.txt': self.row, 'ordinary.txt': ordinary},
            'frozen_authority': {'protected.txt': self.row['sha256']}}
        self.pin = sealed.identity(self.policy)
        self.store = sealed.SyntheticStore(self.row, self.content)
        self.auth = sealed.Authority(self.root, self.policy, trusted_policy_identity=self.pin, observer=self.store)
        self.qualified = self.auth.qualify()
        self.reference = sealed.placeholder(self.row, self.qualified)
        self.ledger = self.root / 'open.json'
        self.grant = {'capability': sealed.OPEN, 'scope': 'SYNTHETIC_ONLY', 'resource': self.row['resource'],
            'commitment': self.row['sha256'], 'qualified_authority': self.qualified['identity'], 'one_time': True,
            'ledger_binding': sealed.identity(str(self.ledger.resolve()))}
        self.grant_pin = sealed.identity(self.grant)

    def open(self, **kwargs):
        args = {'store': self.store, 'grant': self.grant, 'trusted_grant_identity': self.grant_pin,
                'ledger': self.ledger}
        args.update(kwargs)
        return sealed.open_synthetic(self.auth, self.qualified, self.reference, **args)

    def test_01_ordinary_member(self):
        self.assertEqual(self.qualified['verification']['ordinary.txt']['mode'], sealed.ORDINARY)

    def test_02_sealed_commitment(self):
        self.assertEqual(self.qualified['verification']['protected.txt']['mode'], sealed.SEALED)
        self.assertFalse(self.qualified['verification']['protected.txt']['current_content_read'])

    def test_03_no_read(self):
        original = Path.read_bytes
        calls = []
        def checked(path):
            calls.append(path.name)
            self.assertNotEqual(path.name, 'protected.txt')
            return original(path)
        with patch.object(Path, 'read_bytes', checked):
            self.auth.qualify()
        self.assertEqual(calls, ['ordinary.txt'])
        self.assertEqual(self.store.reads, 0)

    def test_04_ordinary_route_rejected_before_read(self):
        with patch.object(Path, 'read_bytes', side_effect=AssertionError('read called')):
            with self.assertRaises(ProtocolFailure):
                self.auth.ordinary_read('protected.txt')

    def test_05_missing(self):
        self.store.mapping = None
        with self.assertRaises(ProtocolFailure):
            self.auth.qualify()

    def test_06_substituted_object(self):
        self.store.mapping['blob'] = 'replacement'
        with self.assertRaises(ProtocolFailure):
            self.auth.qualify()

    def test_07_altered_commitment(self):
        self.row['sha256'] = '0' * 64
        with self.assertRaises(ProtocolFailure):
            self.auth.qualify()

    def test_08_broken_provenance(self):
        self.store.mapping['provenance'] = {'broken': True}
        with self.assertRaises(ProtocolFailure):
            self.auth.qualify()

    def test_09_frozen_pin(self):
        self.assertTrue(self.qualified['verification']['protected.txt']['frozen'])
        self.assertEqual(self.qualified['frozen_authority']['protected.txt'], digest(self.content))

    def test_10_placeholder_allowlist(self):
        self.assertEqual(set(self.reference), {'protocol', 'resource', 'commitment', 'seal', 'qualified_authority'})
        self.assertNotIn(self.content.strip(), canonical(self.reference))

    def test_11_worker_cannot_resolve(self):
        resource = guard.Resource('synthetic:alpha', self.root / 'protected.txt', 'B02_FIXTURE_READ')
        events = []
        boundary = guard.Boundary([resource], events.append)
        with self.assertRaises(ProtocolFailure):
            with boundary.stage(['AUTHORITY_LINKAGE']):
                sealed.worker_resolve(boundary, resource)
        self.assertEqual(events[0]['access'], 'DENIED_BEFORE_CONTENT')
        self.assertFalse(self.ledger.exists())

    def test_12_unauthorized_open(self):
        with self.assertRaises(ProtocolFailure):
            self.open(grant={})
        self.assertEqual(self.store.reads, 0)

    def test_13_authorized_open(self):
        self.assertEqual(self.open(), self.content)
        self.assertEqual(self.store.reads, 1)

    def test_14_opened_identity(self):
        self.open()
        result = loads(self.ledger.with_suffix('.result.json').read_bytes())
        self.assertEqual(result['commitment'], self.reference['commitment'])
        self.assertEqual(result['opening_count'], 1)

    def test_15_mismatched_content(self):
        self.store.data = b'wrong synthetic content'
        with self.assertRaises(ProtocolFailure):
            self.open()
        self.assertFalse(loads(self.ledger.with_suffix('.result.json').read_bytes())['accepted'])
        with self.assertRaises(ProtocolFailure):
            self.open()
        self.assertEqual(self.store.reads, 1)

    def test_16_second_open_rejected(self):
        self.open()
        with self.assertRaises(ProtocolFailure):
            self.open()
        self.assertEqual(self.store.reads, 1)

    def fixture_certificate(self):
        capsule = tier.seal({'protocol': tier.PROTOCOL, 'kind': 'capsule', 'semantic_count': 30,
            'roles': {r: 'synthetic-role-' + r for r in tier.ROLES}, 'unknown': [],
            'policy': {'recorder': 'synthetic-recorder'}})
        policy = {'experiment': 'synthetic:r566-certificate', 'stages': {n: 'focused-' + n for n in certs.v2.REQUIRED},
            'qualified_authority': self.qualified['identity'], 'authority_role': capsule['roles']['authority'],
            'semantic_count': 30, 'canonical_protocol': tier.CANONICAL_PROTOCOL,
            'recorder': capsule['policy']['recorder'],
            'observation_state': {'reservations': 0, 'dispatches': 0, 'completions': 0}}
        results = {'identity': {'successful': True, 'semantic_count': 30},
            'authority': {'successful': True, 'qualified_authority': self.qualified['identity']},
            'contamination': {'successful': True, 'findings': []},
            'workspace': {'successful': True, 'dedicated': True}}
        evidence = {n: tier.receipt(capsule, capsule, policy['experiment'], n,
            policy['stages'][n], 'PASS', results[n]) for n in results}
        cert = certs.certificate(self.qualified, capsule, evidence, policy, self.auth)
        return cert, capsule, evidence, policy

    def test_17_certificate_mutation_stales(self):
        cert, capsule, evidence, policy = self.fixture_certificate()
        self.store.mapping['sha256'] = '0' * 64
        with self.assertRaises(ProtocolFailure):
            certs.validate(cert, self.qualified, capsule, evidence, policy, capsule, self.auth)

    def test_18_certificate_v2_modes(self):
        cert, capsule, evidence, policy = self.fixture_certificate()
        self.assertEqual(cert['protocol'], certs.v2.PROTOCOL)
        self.assertEqual(cert['authority_verification']['protected.txt']['mode'], sealed.SEALED)
        self.assertEqual(cert['authority_verification']['ordinary.txt']['mode'], sealed.ORDINARY)
        self.assertTrue(certs.validate(cert, self.qualified, capsule, evidence, policy, capsule, self.auth))
        self.assertEqual(cert, loads(canonical(cert)))

    def test_19_publication_metadata(self):
        publication.safe_bytes(self.reference)
        publication.safe_bytes(self.qualified)
        with self.assertRaises(publication.security.SecretRejected):
            publication.safe_bytes({**self.reference, 'api_key': publication._values()[0]})

    def test_20_repository_inventory_no_protected_read(self):
        from benchmark.results.phase5c.r5_66_inventory import ROOT, inventory
        protected = {r.path.resolve() for r in guard.repository_resources(ROOT)}
        original = Path.read_bytes
        def checked(path):
            self.assertNotIn(path.resolve(), protected)
            return original(path)
        with patch.object(Path, 'read_bytes', checked), patch.object(checkout_proxy(), 'blobs',
                side_effect=AssertionError('blob content requested')):
            result = inventory()
        self.assertEqual(len(result['members']), 11)
        self.assertEqual(result['protected_content_reads'], 0)

    def test_21_wrong_mapping(self):
        self.store.mapping['resource'] = 'synthetic:beta'
        with self.assertRaises(ProtocolFailure):
            self.auth.qualify()

    def test_22_deferred_workspace(self):
        receipt = sealed.materialize(self.auth, self.root / 'workspace', self.qualified)
        self.assertEqual(receipt['sealed_materialized'], 0)
        self.assertEqual((self.root / 'workspace/ordinary.txt').read_bytes(), b'ordinary\n')
        self.assertFalse((self.root / 'workspace/protected.txt').exists())
        self.assertFalse((self.root / 'workspace/.git').exists())
        self.assertEqual(self.store.reads, 0)
        refs = list((self.root / 'workspace/.sealed').glob('*.json'))
        self.assertEqual(len(refs), 1)
        self.assertEqual(loads(refs[0].read_bytes()), self.reference)

    def test_23_mismatched_open_mapping_before_read(self):
        other = sealed.SyntheticStore({**self.row, 'resource': 'synthetic:beta'}, b'beta')
        with self.assertRaises(ProtocolFailure):
            self.open(store=other)
        self.assertEqual(other.reads, 0)

    def test_24_ordinary_capabilities_cannot_grant_open(self):
        with self.assertRaises(ProtocolFailure):
            guard.authorize([sealed.OPEN])

    def test_25_untrusted_policy(self):
        with self.assertRaises(ProtocolFailure):
            sealed.Authority(self.root, self.policy, trusted_policy_identity='wrong', observer=self.store)

    def test_26_path_escape(self):
        for name in ('../protected', '.git/objects/a', '.sealed/a', 'C:/data', 'a\\b'):
            with self.assertRaises(ProtocolFailure):
                sealed.safe_name(name)

    def test_27_provenance_mutation_stales_certificate(self):
        self.fixture_certificate()
        self.row['provenance']['audit'] = 'mutated'
        with self.assertRaises(ProtocolFailure):
            sealed.certificate_link(self.qualified, self.auth)

    def test_28_frozen_pin_metadata_mutation(self):
        self.policy['frozen_authority']['protected.txt'] = '0' * 64
        with self.assertRaises(ProtocolFailure):
            self.auth.qualify()

    def test_29_mediated_worker_source_resolution_denied(self):
        from benchmark.evaluation.test_mediated_child_r5_62 import ChildTests
        fixture = ChildTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        receipt = fixture.execute(inputs={'action': 'protected', 'path': str(fixture.protected)})[2]
        self.assertEqual(receipt['status'], 'INCOMPLETE')
        self.assertEqual(receipt['result']['child_execution']['status'], 'SECURITY_FAILURE')
        self.assertTrue((fixture.fixture.output / 'quarantine.json').exists())

    def test_30_alternate_ledger_cannot_replay_grant(self):
        self.open()
        with self.assertRaises(ProtocolFailure):
            self.open(ledger=self.root / 'alternate.json')
        self.assertEqual(self.store.reads, 1)
        self.assertFalse((self.root / 'alternate.json').exists())

    def test_31_downgraded_classification_rejected(self):
        self.row['classification'] = 'ORDINARY'
        with patch.object(Path, 'read_bytes', side_effect=AssertionError('read called')):
            with self.assertRaises(ProtocolFailure):
                self.auth.qualify()


def checkout_proxy():
    from benchmark.evaluation import checkout_r5_52
    return checkout_r5_52
