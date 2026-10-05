"""Synthetic witnesses only: never create preimages for real authority members."""

import copy
from pathlib import Path
import tempfile
import unittest

from benchmark.evaluation import authority_r5_53 as a
from benchmark.evaluation.recorder_r5_43 import canonical


class AuthorityTests(unittest.TestCase):
    def evidence(self, data):
        return [{'kind': kind, 'source': kind + ':synthetic', 'source_sha256': a.sha(kind.encode()),
                 'current_sha256': a.sha(data)} for kind in ('git', 'change-record', 'decision')]

    def fixture(self, data=b'hello\n'):
        return {'fixture.txt': {'content': data, 'mode': '100644', 'blob': 'synthetic-blob'}}

    def baseline(self, repository):
        return a.build(repository, {'predecessors': [{'identity': 'synthetic-old-lock'}],
                                   'reconciliation_sha256': a.sha(b'synthetic decision')})

    def test_exact_preimage(self):
        data = b'historical\r\n'
        self.assertEqual(a.exact_preimage(a.sha(data), [('backup:synthetic', data)])['sha256'], a.sha(data))

    def test_wrong_preimage(self):
        self.assertIsNone(a.exact_preimage(a.sha(b'old'), [('synthetic', b'new')]))

    def test_normalized_only_is_not_exact(self):
        self.assertIsNone(a.exact_preimage(a.sha(b'a\r\n'), [('synthetic', b'a\n')]))

    def test_authorized_successor(self):
        self.assertEqual(a.adjudicate(a.sha(b'old'), b'new', 'COMPILER_RUNTIME', self.evidence(b'new')),
                         'CURRENT_STATE_PROVEN_AUTHORIZED')

    def test_unauthorized_mutation_rejected(self):
        evidence = self.evidence(b'new') + [{'kind': 'unauthorized'}]
        self.assertEqual(a.adjudicate(a.sha(b'old'), b'new', 'COMPILER_RUNTIME', evidence), 'UNAUTHORIZED_MUTATION')
        self.assertEqual(a.adjudicate(a.sha(b'old'), b'mutated', 'COMPILER_RUNTIME', self.evidence(b'new')),
                         'PROVENANCE_INSUFFICIENT')

    def test_frozen_authority_stronger_rule(self):
        self.assertEqual(a.adjudicate(a.sha(b'old'), b'new', 'FROZEN_BEHAVIORAL_AUTHORITY', self.evidence(b'new')),
                         'PROVENANCE_INSUFFICIENT')

    def test_documentation_infrastructure_distinction(self):
        evidence = self.evidence(b'new')[:2]
        self.assertEqual(a.adjudicate(a.sha(b'old'), b'new', 'NON_AUTHORITATIVE_DOCUMENTATION', evidence),
                         'CURRENT_STATE_PROVEN_AUTHORIZED')
        self.assertEqual(a.adjudicate(a.sha(b'old'), b'new', 'BENCHMARK_INFRASTRUCTURE', evidence), 'PROVENANCE_INSUFFICIENT')

    def test_deterministic_identity(self):
        repo = {**self.fixture(), 'other.txt': self.fixture(b'other\n')['fixture.txt']}
        self.assertEqual(self.baseline(repo), self.baseline(dict(reversed(list(repo.items())))))

    def test_lf_crlf_repository_identity(self):
        repo = self.fixture()
        baseline = self.baseline(repo)
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'fixture.txt'
            p.write_bytes(b'hello\n')
            lf = a.verify(tmp, baseline, repo, trusted_identity=baseline['identity'])
            p.write_bytes(b'hello\r\n')
            crlf = a.verify(tmp, baseline, repo, trusted_identity=baseline['identity'])
            self.assertEqual(lf['baseline'], crlf['baseline'])
            self.assertNotEqual(lf['identity'], crlf['identity'])

    def test_binary_exact_identity(self):
        with self.assertRaises(ValueError):
            a.materialization(b'\0a\n', b'\0a\r\n', 'exact-bytes')

    def test_checkout_mutation_rejection(self):
        repo = self.fixture()
        baseline = self.baseline(repo)
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / 'fixture.txt').write_bytes(b'changed\n')
            with self.assertRaises(ValueError):
                a.verify(tmp, baseline, repo, trusted_identity=baseline['identity'])

    def test_resealed_successor_mutation_rejection(self):
        repo = self.fixture()
        baseline = self.baseline(repo)
        mutated = copy.deepcopy(baseline)
        mutated['members']['fixture.txt']['sha256'] = a.sha(b'changed')
        mutated['identity'] = a.sha(canonical({k: v for k, v in mutated.items() if k != 'identity'}))
        with self.assertRaises(ValueError):
            a.verify('.', mutated, repo, trusted_identity=baseline['identity'])

    def test_historical_lock_preservation(self):
        old = {'files': {'fixture.txt': a.sha(b'old\r\n')}}
        before = canonical(old)
        self.baseline(self.fixture())
        self.assertEqual(canonical(old), before)
        self.assertNotEqual(old['files']['fixture.txt'], a.sha(b'hello\n'))

    def test_canonical_reload(self):
        baseline = self.baseline(self.fixture())
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'baseline.json'
            p.write_bytes(canonical(baseline) + b'\n')
            self.assertEqual(a.reload(p), baseline)
            p.write_bytes(canonical(baseline) + b'\r\n')
            with self.assertRaises(ValueError):
                a.reload(p)

    def test_mode_mutation_rejection(self):
        repo = self.fixture()
        baseline = self.baseline(repo)
        repo['fixture.txt']['mode'] = '100755'
        with self.assertRaises(ValueError):
            a.verify('.', baseline, repo, trusted_identity=baseline['identity'])

    def test_bare_cr_rejected(self):
        with self.assertRaises(ValueError):
            a.materialization(b'a\n', b'a\r', 'utf8-lf-text')

    def test_frozen_baseline_pin_mismatch(self):
        with self.assertRaises(ValueError):
            a.build(self.fixture(), {'predecessors': ['synthetic'], 'reconciliation_sha256': 'synthetic',
                                    'frozen_authority': {'fixture.txt': a.sha(b'wrong')}})

    def test_unbound_frozen_witness_rejected(self):
        evidence = self.evidence(b'new') + [{'kind': 'frozen-authority', 'historical_sha256': a.sha(b'old')}]
        self.assertEqual(a.adjudicate(a.sha(b'old'), b'new', 'FROZEN_BEHAVIORAL_AUTHORITY', evidence),
                         'PROVENANCE_INSUFFICIENT')


if __name__ == '__main__':
    unittest.main()
