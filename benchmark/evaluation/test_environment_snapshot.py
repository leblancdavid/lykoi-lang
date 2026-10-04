"""Credential-publication regressions; synthetic values only."""

import json
from pathlib import Path
import tempfile
import unittest

from benchmark.evaluation.environment_snapshot import (
    REDACTED, public_environment, redact_snapshot)
from benchmark.evaluation.preexposure_r5_45 import seal, unseal, ProtocolFailure
from benchmark.evaluation.recorder_r5_43 import canonical


class EnvironmentSnapshotTests(unittest.TestCase):
    def test_unknown_credentials_are_private_by_default(self):
        environment = {'OPENAI_API_KEY': 'synthetic-api-value',
                       'OPENCODE_SERVER_PASSWORD': 'synthetic-password',
                       'UNFAMILIAR_PROVIDER_AUTH': 'synthetic-auth',
                       'PYTHONDONTWRITEBYTECODE': '1'}
        published = public_environment(environment)
        self.assertEqual(published['PYTHONDONTWRITEBYTECODE'], '1')
        for name in environment.keys() - {'PYTHONDONTWRITEBYTECODE'}:
            self.assertEqual(published[name], REDACTED)
        self.assertEqual(environment['OPENAI_API_KEY'], 'synthetic-api-value')

    def test_historical_redaction_preserves_identity_and_invalidates_seal(self):
        original = seal({'configuration': {'environment': {
            'OPENAI_API_KEY': 'synthetic-api-value',
            'OPENCODE_SERVER_PASSWORD': 'synthetic-password', 'OS': 'Windows_NT'}},
            'files': {'example.py': 'historical-file-hash'}})
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'state.json'
            path.write_bytes(canonical(original))
            self.assertEqual(set(redact_snapshot(path)),
                             {'OPENAI_API_KEY', 'OPENCODE_SERVER_PASSWORD'})
            redacted = json.loads(path.read_bytes())
            self.assertEqual(redacted['identity'], original['identity'])
            self.assertEqual(redacted['files'], original['files'])
            self.assertEqual(redacted['configuration']['environment']['OS'], 'Windows_NT')
            self.assertNotIn(b'synthetic-api-value', path.read_bytes())
            self.assertNotIn(b'synthetic-password', path.read_bytes())
            with self.assertRaises(ProtocolFailure):
                unseal(redacted)
            first = path.read_bytes()
            self.assertEqual(redact_snapshot(path), [])
            self.assertEqual(path.read_bytes(), first)


if __name__ == '__main__':
    unittest.main()
