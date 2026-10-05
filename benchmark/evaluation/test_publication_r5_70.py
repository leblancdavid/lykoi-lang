"""Frozen source rejection reproduction and generic typed publication challenges."""
from pathlib import Path
import unittest
import tempfile

from benchmark.evaluation import publication_r5_70 as current
from benchmark.evaluation import publication_r5_59 as old
from benchmark.evaluation import publication_schema_r5_64 as schemas
from benchmark.evaluation.recorder_r5_43 import digest

ROOT = Path(__file__).resolve().parents[2]
SUMMARY_CONTEXT = current.SUMMARY_CONTEXT
SUMMARY_PIN = current.SUMMARY_PIN


class PublicationTests(unittest.TestCase):
    def source(self, field, value):
        return f'x = {{{field!r}: {value!r}}}'.encode()

    def check(self, content, schema=SUMMARY_CONTEXT, pin=SUMMARY_PIN, source_pin=None):
        return current.check_python_source(content, trusted_source_identity=source_pin or
            digest(content.replace(b'\r\n', b'\n')), schema=schema, schema_identity=pin)

    def test_01_frozen_rejection_reproduced(self):
        name = 'benchmark/results/phase5c/r5_69_qualification.py'
        content = (ROOT / name).read_bytes()
        with self.assertRaises(old.security.SecretRejected) as error:
            old.check_source(name, content)
        self.assertEqual(error.exception.field, 'production_authorization')
        self.assertEqual(error.exception.category, 'credential assignment')

    def test_02_root_cause_protocol_metadata(self):
        content = (ROOT / 'benchmark/results/phase5c/r5_69_qualification.py').read_bytes()
        matches = [m for m in old.security.ASSIGNMENT.finditer(content.decode())
                   if old.security.SENSITIVE.search(m[1])]
        self.assertEqual([(m[1], m[2]) for m in matches],
                         [('production_authorization', 'REQUIRED_NOT_ISSUED')])
        old.safe_bytes({'production_authorization': matches[0][2]}, schema=SUMMARY_CONTEXT,
                       schema_identity=SUMMARY_PIN)
        self.assertEqual(self.check(content), old.PUBLISHABLE_SOURCE_OR_EVIDENCE)

    def test_03_prospective_summary_publication(self):
        value = dict(production_authorization=str('REQUIRED_NOT_ISSUED'),
                     classification='prospective', batches=0, observed=False)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'summary.json'
            current.persist_object(path, value, schema=SUMMARY_CONTEXT, schema_identity=SUMMARY_PIN)
            self.assertEqual(path.read_bytes().rstrip(b'\n'), current.safe_object(
                value, schema=SUMMARY_CONTEXT, schema_identity=SUMMARY_PIN))

    def test_04_real_credential_value_rejected(self):
        content = self.source('production_authorization', 'sk-' + 'A' * 24)
        with self.assertRaises(old.security.SecretRejected):
            self.check(content)

    def test_05_opaque_http_credentials_rejected(self):
        for value in ('Bearer opaque', 'Basic abc'):
            with self.subTest(value=value), self.assertRaises(old.security.SecretRejected):
                self.check(self.source('production_authorization', value))

    def test_06_undeclared_credentials_rejected(self):
        with self.assertRaises(old.security.SecretRejected):
            self.check(self.source('api_key', 'opaque-credential'))

    def test_07_fixture_leak_rejected(self):
        with self.assertRaises(old.security.SecretRejected):
            self.check(self.source('production_authorization', old._values()[0]))

    def test_08_no_filename_exemption(self):
        content = self.source('production_authorization', 'REQUIRED_NOT_ISSUED')
        for name in ('arbitrary.py', 'benchmark/results/phase5c/r5_69_qualification.py'):
            with self.subTest(name=name), self.assertRaises(old.security.SecretRejected):
                old.check_source(name, content)
        self.assertEqual(self.check(content), old.PUBLISHABLE_SOURCE_OR_EVIDENCE)

    def test_09_schema_and_source_pins(self):
        content = self.source('production_authorization', 'REQUIRED_NOT_ISSUED')
        for kwargs in ({'pin': '0' * 64}, {'source_pin': '0' * 64}):
            with self.subTest(kwargs=kwargs), self.assertRaises(old.security.SecretRejected):
                self.check(content, **kwargs)

    def test_10_assignment_not_dictionary_context(self):
        with self.assertRaises(old.security.SecretRejected):
            self.check(('production_authorization' + ' = ' + repr('opaque-credential')).encode())

    def test_11_marked_secret_still_rejected(self):
        with self.assertRaises(old.security.SecretRejected):
            old.safe_bytes({'secret': True, 'value': 'opaque'})

    def test_12_redacted_diagnostics(self):
        with self.assertRaises(old.security.SecretRejected) as error:
            self.check(self.source('api_key', 'opaque-credential'))
        self.assertNotIn('opaque-credential', str(error.exception))

    def test_13_remainder_credentials_rejected(self):
        value = dict(production_authorization=str('REQUIRED_NOT_ISSUED'), api_key=str('opaque'))
        with self.assertRaises(old.security.SecretRejected):
            current.safe_object(value, schema=SUMMARY_CONTEXT, schema_identity=SUMMARY_PIN)

    def test_14_source_marked_secret_rejected(self):
        value = dict(secret=True, value='opaque')
        with self.assertRaises(old.security.SecretRejected):
            self.check(('x = ' + repr(value)).encode())

    def test_15_source_unicode_offsets(self):
        content = ('note = ' + repr('λ') + '; ').encode() + self.source(
            'production_authorization', 'REQUIRED_NOT_ISSUED')
        self.assertEqual(self.check(content), old.PUBLISHABLE_SOURCE_OR_EVIDENCE)

    def test_16_nonpublic_root_cannot_grant_public_context(self):
        for classification in (schemas.SECRET_VALUE, schemas.SYNTHETIC_SECURITY_FIXTURE):
            schema = schemas.PublicationSchema.declare(schemas.object_schema({
                'production_authorization': schemas.field(schemas.PROTOCOL_AUTHORIZATION)},
                classification=classification))
            with self.subTest(classification=classification), self.assertRaises(old.security.SecretRejected):
                self.check(self.source('production_authorization', 'REQUIRED_NOT_ISSUED'),
                           schema=schema, pin=schema.identity)
