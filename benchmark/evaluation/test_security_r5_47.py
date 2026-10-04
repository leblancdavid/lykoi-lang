"""Independent publication and successor regressions, synthetic data only."""

import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from benchmark.evaluation import security_r5_47 as security
from benchmark.evaluation import infrastructure_lock_r5_47 as locks
from benchmark.evaluation.recorder_r5_43 import canonical, digest

ROOT = Path(__file__).resolve().parents[2]


class SecurityTests(unittest.TestCase):
    def rejection(self, value, raw):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'evidence.json'
            with self.assertRaises(security.SecretRejected) as caught:
                security.persist(path, value)
            self.assertNotIn(raw, str(caught.exception))
            self.assertFalse(path.exists())

    def test_api_key(self):
        raw = 'synthetic-api-value'
        self.rejection({'environment': {'VENDOR_API_KEY': raw}}, raw)

    def test_token(self):
        raw = 'synthetic-token-value'
        self.rejection({'refresh_token': raw}, raw)

    def test_password(self):
        raw = 'synthetic-password-value'
        self.rejection({'password': raw}, raw)

    def test_marked_value(self):
        raw = 'synthetic-marked-value'
        self.rejection({'sensitive': True, 'value': raw}, raw)

    def test_safe_environment(self):
        self.assertEqual(security.publication_environment({'PYTHONDONTWRITEBYTECODE': '1'}),
                         {'PYTHONDONTWRITEBYTECODE': '1'})

    def test_presence_absence_empty(self):
        self.assertEqual(security.secret_identity('TOKEN', None), {'present': False})
        self.assertEqual(security.secret_identity('TOKEN', ''), {'present': True})
        self.assertEqual(security.secret_identity('TOKEN', 'synthetic'), {'present': True})

    def test_keyed_identity_and_canonical_no_raw(self):
        raw = 'synthetic-low-entropy-value'
        a = security.secret_identity('TOKEN', raw, material=True, key=b'a' * 32, key_id='fixture-a')
        b = security.secret_identity('TOKEN', raw, material=True, key=b'b' * 32, key_id='fixture-b')
        self.assertNotEqual(a['fingerprint'], b['fingerprint'])
        self.assertNotIn(raw.encode(), security.safe_bytes({'TOKEN': a}))
        self.assertEqual(a, security.secret_identity('TOKEN', raw, material=True, key=b'a' * 32, key_id='fixture-a'))

    def test_weak_key_rejected(self):
        with self.assertRaises(security.SecretRejected):
            security.secret_identity('TOKEN', 'synthetic', material=True, key=b'weak', key_id='fixture')

    def test_redacted_diagnostic(self):
        raw = 'synthetic-hidden-value'
        self.rejection({'password': raw}, raw)

    def test_generated_report(self):
        raw = 'synthetic-report-value'
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'report.json'
            with self.assertRaises(security.SecretRejected):
                security.report(path, {'password': raw})
            self.assertFalse(path.exists())
            security.report(path, {'password': security.secret_identity('password', raw)})
            self.assertNotIn(raw.encode(), path.read_bytes())
            self.assertEqual(json.loads(path.read_bytes()), {'password': {'present': True}})

    def test_generic_bearer_and_connection_string(self):
        for raw in ('Bearer ' + 'A' * 30, 'postgresql://' + 'user:synthetic@host/db'):
            self.rejection({'message': raw}, raw)

    def test_private_key_and_token_shape(self):
        for raw in ('-----BEGIN ' + 'PRIVATE KEY-----', 'ghp_' + 'A' * 30):
            self.rejection({'output': raw}, raw)

    def test_free_text_assignment(self):
        raw = 'synthetic-text-value'
        self.rejection({'stderr': 'PASSWORD="' + raw + '"'}, raw)

    def test_unquoted_configuration(self):
        raw = 'synthetic-unquoted-value'
        self.rejection({'log': 'ACCESS_TOKEN=' + raw}, raw)

    def test_recorder_no_bypass(self):
        with tempfile.TemporaryDirectory() as directory:
            recorder = security.PublicationRecorder(directory)
            with self.assertRaises(security.SecretRejected):
                recorder.freeze({'password': 'synthetic-recorder-value'})
            self.assertFalse(recorder.path('baseline').exists())

    def test_callback_exception_redacted(self):
        raw = 'synthetic-exception-value'
        with tempfile.TemporaryDirectory() as directory:
            recorder = security.PublicationRecorder(directory)
            recorder.freeze({'classification': 'synthetic-publication-only'})
            recorder.verify({'classification': 'synthetic-publication-only'})
            def callback():
                raise ValueError(raw)
            # Historical observe rethrows callback text; prospective API must
            # also prevent the exception delivered to its caller leaking it.
            with self.assertRaises(ValueError) as caught:
                recorder.observe(callback)
            self.assertNotIn(raw, str(caught.exception))
            self.assertNotIn(raw.encode(), recorder.path('halt').read_bytes())

    def test_no_entropy_only_rejection(self):
        security.safe_bytes({'sha256': 'a' * 64, 'identity': 'b' * 64})

    def test_public_variable_injection_is_not_published(self):
        raw = 'Bearer ' + 'A' * 30
        self.assertNotIn(raw.encode(), security.safe_bytes(security.publication_environment({'PATH': raw})))

    def test_malformed_fingerprint_rejected(self):
        self.rejection({'TOKEN': {'present': True, 'scheme': 'sha256', 'fingerprint': 'a' * 64}}, 'never-published')

    def test_successor_gitignore_and_security_mutation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ('.gitignore', 'security.py'):
                (root / name).write_bytes(b'original\n')
            lock = locks.manifest(root, ['.gitignore', 'security.py'], {'protocol': 'fixture'})
            path = root / 'lock.json'
            security.persist(path, lock)
            saved = locks.reload(path)
            self.assertEqual(saved, locks.manifest(root, reversed(list(lock['files'])), {'protocol': 'fixture'}))
            for name in ('.gitignore', 'security.py'):
                (root / name).write_bytes(b'mutated\n')
                with self.assertRaises(ValueError):
                    locks.verify(root, saved)
                (root / name).write_bytes(b'original\n')
                self.assertTrue(locks.verify(root, saved)['valid'])

    def test_historical_lock_unchanged(self):
        path = ROOT / 'benchmark/results/phase5c/R5_43-infrastructure-lock.json'
        committed = subprocess.check_output(['git', 'show', 'HEAD:' + path.relative_to(ROOT).as_posix()], cwd=ROOT)
        self.assertEqual(digest(path.read_bytes()), digest(committed))

    def test_ignore_effective_behavior(self):
        ignored = ['.env', '.env.local', 'local/.env.production', '.venv/secret.txt']
        required = ['.env.example', '.env.sample', 'benchmark/evaluation/security_r5_47.py',
                    'benchmark/results/phase5c/R5_47-qualification.json', 'air/task_manager.json']
        for name in ignored + required:
            p = subprocess.run(['git', 'check-ignore', '--no-index', '--quiet', name], cwd=ROOT)
            self.assertEqual(p.returncode, 0 if name in ignored else 1, name)


if __name__ == '__main__':
    unittest.main()
