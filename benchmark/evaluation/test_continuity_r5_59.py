"""Independent synthetic continuity qualification, no benchmark subjects."""

import unittest
from benchmark.evaluation import continuity_r5_59 as continuity
from benchmark.evaluation.checkout_r5_52 import sha


class ContinuityTests(unittest.TestCase):
    def verify(self, repository, physical, **kwargs):
        return continuity.verify(repository, physical, repository_sha256=sha(repository),
                                 kind=kwargs.pop('kind', 'utf8-lf-text'), **kwargs)

    def test_lf_to_crlf(self):
        row = self.verify(b'alpha\nbeta\n', b'alpha\r\nbeta\r\n')
        self.assertEqual(row['relationship'], 'LF_CRLF_ONLY')
        self.assertEqual(row['checkout_representation']['form'], 'CRLF')

    def test_crlf_to_lf(self):
        # Both checkouts compare with the independently pinned LF repository.
        repository = b'alpha\nbeta\n'
        before = self.verify(repository, repository.replace(b'\n', b'\r\n'))
        after = self.verify(repository, repository)
        self.assertEqual(before['continuity_identity'], after['continuity_identity'])
        self.assertNotEqual(before['checkout_sha256'], after['checkout_sha256'])

    def test_text_mutation(self):
        with self.assertRaises(ValueError):
            self.verify(b'alpha\n', b'changed\r\n')

    def test_binary_mutation(self):
        with self.assertRaises(ValueError):
            self.verify(b'\0alpha\n', b'\0alpha\r\n', kind='binary')

    def test_exact_authority(self):
        self.assertEqual(self.verify(b'alpha\n', b'alpha\n', exact_bytes=True)['comparison'], 'exact-bytes')
        with self.assertRaises(ValueError):
            self.verify(b'alpha\n', b'alpha\r\n', exact_bytes=True)

    def test_unclassified_and_bare_cr(self):
        for repository, physical, kind in [(b'a\n', b'a\r\n', 'unknown'),
                (b'a\r', b'a\n', 'utf8-lf-text'), (b'a\n', b'a\r', 'utf8-lf-text')]:
            with self.assertRaises(ValueError):
                self.verify(repository, physical, kind=kind)

    def test_wrong_repository_pin(self):
        with self.assertRaises(ValueError):
            continuity.verify(b'a\n', b'a\n', repository_sha256=sha(b'b\n'), kind='utf8-lf-text')

    def test_determinism(self):
        self.assertEqual(self.verify(b'a\n', b'a\r\n'), self.verify(b'a\n', b'a\r\n'))
