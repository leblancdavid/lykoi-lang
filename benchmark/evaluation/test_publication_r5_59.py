"""Independent publication boundary witnesses; all rejected inputs are fake."""

from pathlib import Path
import json
import tempfile
import unittest
from benchmark.evaluation import publication_r5_59 as publication
from benchmark.evaluation import security_r5_47 as security

NAME = 'benchmark/evaluation/synthetic_fixture_r5_59.txt'


class PublicationTests(unittest.TestCase):
    def fixture(self):
        return (publication.ROOT / NAME).read_bytes()

    def test_designated_input(self):
        self.assertEqual(publication.check_source(NAME, self.fixture()), publication.SYNTHETIC_SECURITY_FIXTURE)
        self.assertEqual(publication.check_source(NAME, self.fixture().replace(b'\r\n', b'\n').replace(b'\n', b'\r\n')),
                         publication.SYNTHETIC_SECURITY_FIXTURE)

    def test_synthetic_leak_all_output_contexts(self):
        value = publication._fixture(self.fixture())[0]
        for context in ('evidence', 'certificate', 'capsule', 'receipt', 'report', 'publication', 'log'):
            with self.subTest(context=context), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / 'output.json'
                with self.assertRaises(security.SecretRejected) as caught:
                    publication.persist(path, {context: value})
                self.assertNotIn(value, str(caught.exception))
                self.assertFalse(path.exists())
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(security.SecretRejected):
                publication.report(Path(directory) / 'report.md', value)

    def test_unapproved_source(self):
        with self.assertRaises(security.SecretRejected):
            publication.check_source('unapproved.py', self.fixture())

    def test_raw_secret_fail_closed_and_redacted(self):
        # Opaque credential stand-in, never a real credential.
        raw = 'obviously-fake-nonfunctional-opaque'
        with self.assertRaises(security.SecretRejected) as caught:
            publication.safe_bytes({'password': raw})
        self.assertNotIn(raw, str(caught.exception))
        with self.assertRaises(security.SecretRejected):
            publication._fixture('{}={}'.format('PASSWORD', json.dumps(raw)).encode())

    def test_immutable_designation(self):
        with self.assertRaises(TypeError):
            publication.DESIGNATIONS['unapproved.py'] = 'anything'
        with self.assertRaises(security.SecretRejected):
            publication.check_source(NAME, self.fixture() + b'\n# mutation\n')
        with self.assertRaises(security.SecretRejected):
            publication.check_source('unapproved.py', b'# SYNTHETIC_SECURITY_FIXTURE\n' + self.fixture())

    def test_token_shape_not_allowed_in_fixture(self):
        with self.assertRaises(security.SecretRejected):
            value = 'synthetic-ghp_' + 'A' * 30
            publication._fixture('{}={}'.format('PASSWORD', json.dumps(value)).encode())

    def test_publishable_source(self):
        self.assertEqual(publication.check_source('ordinary.py', b'count = 3\n'), publication.PUBLISHABLE_SOURCE_OR_EVIDENCE)
        publication.safe_bytes({'password': security.REDACTED, 'status': 'PASS'})

    def test_historical_audit_not_whitelisted(self):
        name = 'benchmark/results/phase5c/r5_58_stopped_audit.py'
        content = (publication.ROOT / name).read_bytes()
        with self.assertRaises(security.SecretRejected):
            publication.check_source(name, content)
        with self.assertRaises(security.SecretRejected):
            publication.check_text(content.decode())

    def test_recorder_cannot_publish_fixture_value(self):
        value = publication._fixture(self.fixture())[0]
        with tempfile.TemporaryDirectory() as directory:
            recorder = publication.PublicationRecorder(directory)
            with self.assertRaises(security.SecretRejected):
                recorder.freeze({'message': value})
            self.assertFalse(recorder.path('baseline').exists())
