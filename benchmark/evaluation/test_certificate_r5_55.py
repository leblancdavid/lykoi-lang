"""Independent authority and CertificateV2 challenges; no benchmark subjects."""

import copy
import os
from pathlib import Path
import tempfile
import unittest

from benchmark.evaluation import certificate_r5_55 as certs
from benchmark.evaluation import checkout_r5_52 as checkout
from benchmark.evaluation import qualified_authority_r5_55 as authority
from benchmark.evaluation import security_r5_47 as security
from benchmark.evaluation import tier2_r5_51 as tier
from benchmark.evaluation.recorder_r5_43 import canonical, digest, loads, ProtocolFailure
from benchmark.results.phase5c import r5_55_qualification as driver


class SuccessorCertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temp.name) / 'qualified-fixture'
        tier.Workspace.materialize(driver.ROOT, cls.root, driver.boundary()['scopes'])
        # Explicit baseline fixture, not current-checkout qualification. Restore
        # pinned repository bytes so documentation evolution cannot rewrite tests.
        baseline = loads((cls.root / 'benchmark/results/phase5c/R5_53-authority-successor-v1.json').read_bytes())
        blobs = checkout.blobs(cls.root, [r['blob'] for r in baseline['members'].values() if r['blob']])
        for name, row in baseline['members'].items():
            if row['blob'] and name in {'docs/project-overview.md', 'docs/decisions.md', 'docs/research-log.md'}:
                (cls.root / name).write_bytes(blobs[row['blob']])
        cls.auth = driver.authorization(cls.root)
        cls.pin = digest(canonical(cls.auth))
        cls.qualified = authority.qualify(cls.root, cls.auth, trusted_policy_identity=cls.pin)
        cls.capsule = tier.capture(cls.root, driver.boundary(), tier.controlled_environment({}, cls.root))

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def setUp(self):
        self.policy = {'experiment': 'synthetic:independent-r555',
            'stages': {n: 'focused-' + n for n in certs.REQUIRED},
            'qualified_authority': self.qualified['identity'],
            'authority_role': self.capsule['roles']['authority'], 'semantic_count': 30,
            'canonical_protocol': tier.CANONICAL_PROTOCOL, 'recorder': self.capsule['policy']['recorder'],
            'observation_state': {'reservations': 0, 'dispatches': 0, 'completions': 0}}
        self.results = {'identity': {'successful': True, 'semantic_count': 30},
            'authority': {'successful': True, 'qualified_authority': self.qualified['identity']},
            'contamination': {'successful': True, 'findings': []},
            'workspace': {'successful': True, 'dedicated': True}}
        self.evidence = {n: self.receipt(n) for n in certs.REQUIRED}

    def receipt(self, n, **changes):
        row = tier.receipt(self.capsule, self.capsule, self.policy['experiment'], n,
                           self.policy['stages'][n], 'PASS', self.results[n])
        return tier.seal({**{k: v for k, v in row.items() if k != 'identity'}, **changes})

    def assemble(self, qualified=None, capsule=None):
        return certs.certificate(self.qualified if qualified is None else qualified,
            self.capsule if capsule is None else capsule, self.evidence, self.policy, self.root, self.auth,
            trusted_policy_identity=self.pin)

    def qualify(self, policy=None, pin=None):
        return authority.qualify(self.root, self.auth if policy is None else policy,
                                  trusted_policy_identity=self.pin if pin is None else pin)

    def mutation(self, name, transform, callback=None):
        path = self.root / name
        before = path.read_bytes()
        try:
            path.write_bytes(transform(before))
            with self.assertRaises(ProtocolFailure):
                (callback or self.qualify)()
        finally:
            path.write_bytes(before)

    def manifest_mutation(self, update):
        def transform(raw):
            value = loads(raw)
            update(value)
            value['identity'] = digest(canonical({k: v for k, v in value.items() if k != 'identity'}))
            return canonical(value) + b'\n'
        self.mutation(self.auth['manifest'], transform)

    def test_01_canonical_identity(self):
        body = {k: v for k, v in self.qualified.items() if k != 'identity'}
        self.assertEqual(digest(canonical(body)), self.qualified['identity'])

    def test_02_current_r553_accepted(self):
        self.assertEqual(self.qualify()['authority'], driver.CURRENT)

    def test_03_historical_r547_as_current_rejected(self):
        old = self.root / 'benchmark/results/phase5c/R5_47-infrastructure-lock-v2.json'
        # Historical manifest bytes cannot substitute for the current selection.
        self.mutation(self.auth['manifest'], lambda raw: old.read_bytes())

    def test_04_arbitrary_manifest_rejected(self):
        self.mutation(self.auth['manifest'], lambda raw: canonical({'identity': 'unrelated'}) + b'\n')

    def test_05_authority_member_mutation(self):
        self.mutation('air/task_manager.json', lambda raw: raw + b' ')

    def test_06_authority_identity_mutation(self):
        self.mutation(self.auth['manifest'], lambda raw: raw.replace(driver.CURRENT.encode(), b'0' * 64))

    def test_07_independent_frozen_contract_binding(self):
        # Even a re-authorized infrastructure selection cannot change independent
        # frozen pins. No frozen B02 subject is loaded or parsed.
        changed = copy.deepcopy(self.auth)
        changed['frozen_authority'] = {n: '0' * 64 for n in changed['frozen_authority']}
        with self.assertRaises(ProtocolFailure):
            self.qualify(changed, digest(canonical(changed)))

    def test_08_broken_predecessor_link(self):
        self.manifest_mutation(lambda m: m['predecessors'][0].update(raw_sha256='0' * 64))

    def test_09_missing_provenance(self):
        self.mutation(self.auth['adjudication'], lambda raw: canonical({'files': []}) + b'\n')

    def test_10_wrong_checkout_policy(self):
        changed = {**self.auth, 'checkout_policy': 'normalize-everything'}
        with self.assertRaises(ProtocolFailure):
            self.qualify(changed, digest(canonical(changed)))

    def test_11_historical_failure_preservation(self):
        for name in self.auth['historical_evidence']:
            with self.subTest(name=name):
                self.mutation(name, lambda raw: raw.replace(b'FAIL', b'PASS') + b' ')

    def test_12_unqualified_newer_successor(self):
        self.manifest_mutation(lambda m: m.update(head='f' * 40))
        changed = {**self.auth, 'status': 'NEWER'}
        with self.assertRaises(ProtocolFailure):
            self.qualify(changed, digest(canonical(changed)))

    def test_13_deterministic_assembly(self):
        self.assertEqual(self.assemble(), self.assemble())

    def test_14_canonical_round_trip(self):
        cert = self.assemble()
        self.assertEqual(cert, loads(canonical(cert)))

    def test_15_valid_authority_capsule(self):
        cert = self.assemble()
        self.assertTrue(certs.validate(cert, self.qualified, self.capsule, self.evidence, self.policy,
            self.capsule, self.root, self.auth, trusted_policy_identity=self.pin))

    def test_16_wrong_authority(self):
        fake = tier.seal({**{k: v for k, v in self.qualified.items() if k != 'identity'}, 'authority': '0' * 64})
        with self.assertRaises(ProtocolFailure):
            self.assemble(qualified=fake)

    def test_17_stale_capsule(self):
        changed = tier.seal({**{k: v for k, v in self.capsule.items() if k != 'identity'},
                             'context': {'changed': True}})
        with self.assertRaises(ProtocolFailure):
            self.assemble(capsule=changed)

    def test_18_mixed_receipts(self):
        self.evidence['identity'] = self.receipt('identity', experiment='other')
        with self.assertRaises(ProtocolFailure):
            self.assemble()

    def test_19_semantic_count_mismatch(self):
        self.results['identity']['semantic_count'] = 31
        self.evidence['identity'] = self.receipt('identity')
        with self.assertRaises(ProtocolFailure):
            self.assemble()

    def test_20_contamination_failure(self):
        self.results['contamination']['findings'] = ['unexpected material']
        self.evidence['contamination'] = self.receipt('contamination')
        with self.assertRaises(ProtocolFailure):
            self.assemble()

    def test_21_incomplete_receipt(self):
        self.evidence['workspace'] = self.receipt('workspace', status='INCOMPLETE')
        with self.assertRaises(ProtocolFailure):
            self.assemble()

    def test_22_authority_after_certificate_mutation(self):
        cert = self.assemble()
        self.mutation('air/task_manager.json', lambda raw: raw + b' ', lambda: certs.validate(
            cert, self.qualified, self.capsule, self.evidence, self.policy, self.capsule,
            self.root, self.auth, trusted_policy_identity=self.pin))

    def test_23_ai_authoring_independence(self):
        cert = self.assemble()
        editor = self.root / 'opencode.json'
        editor.write_bytes(b'{"model":"synthetic-authoring"}')
        self.addCleanup(editor.unlink)
        env = tier.controlled_environment({'OPENAI_API_KEY': 'synthetic-unused',
                                          'OPENCODE_MODEL': 'synthetic-unused'}, self.root)
        fresh = tier.capture(self.root, driver.boundary(), env)
        self.assertEqual(fresh, self.capsule)
        self.assertTrue(certs.validate(cert, self.qualified, self.capsule, self.evidence, self.policy,
            fresh, self.root, self.auth, trusted_policy_identity=self.pin))

    def test_24_secret_safe_publication(self):
        cert = self.assemble()
        for item in (self.qualified, cert, self.evidence, self.auth):
            security.safe_bytes(item)
        output = Path(self.temp.name) / 'secret-rejection.json'
        for item in (self.qualified, cert, self.evidence['identity'], self.auth):
            with self.assertRaises(security.SecretRejected):
                security.persist(output, {**item, 'api_key': 'synthetic-forbidden'})
            self.assertFalse(output.exists())

    def test_25_exact_material_mutation(self):
        with self.assertRaises(ValueError):
            from benchmark.evaluation.authority_r5_53 import materialization
            materialization(b'\x00\n', b'\x00\r\n', 'exact-bytes')

    def test_26_representation_policy(self):
        from benchmark.evaluation.authority_r5_53 import materialization
        self.assertEqual(materialization(b'hello\n', b'hello\r\n', 'utf8-lf-text'),
                         'LF_CRLF_REPRESENTATION')

    def test_27_altered_provenance_evidence(self):
        self.mutation(self.auth['decision'], lambda raw: raw + b' ')

    def test_28_missing_qualification(self):
        self.mutation(self.auth['qualification'], lambda raw: b'{}\n')

    def test_29_nonzero_observation_rejected(self):
        self.policy['observation_state']['reservations'] = 1
        with self.assertRaises(ProtocolFailure):
            self.assemble()

    def test_30_ai_metadata_rejected(self):
        changed = {**self.auth, 'model_identity': 'synthetic'}
        with self.assertRaises(ProtocolFailure):
            self.qualify(changed, digest(canonical(changed)))

    def test_31_frozen_physical_contract_mutation(self):
        name = next(iter(self.auth['frozen_authority']))
        self.mutation(name, lambda raw: raw + b' ')

    def test_32_required_receipt_missing(self):
        del self.evidence['workspace']
        with self.assertRaises(ProtocolFailure):
            self.assemble()

    def test_33_untrusted_policy_identity(self):
        with self.assertRaises(ProtocolFailure):
            self.qualify(pin='0' * 64)


if __name__ == '__main__':
    unittest.main()
