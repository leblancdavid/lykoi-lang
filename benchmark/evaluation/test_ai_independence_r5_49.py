"""Fresh execution of core independence probes, not reuse of R5.48 receipts."""

import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

from benchmark.evaluation import execution_identity_r5_48 as previous
from benchmark.evaluation import ai_independence_r5_48 as probes
from benchmark.evaluation import security_r5_47 as security

ROOT = Path(__file__).resolve().parents[2]


class FreshIndependenceTests(unittest.TestCase):
    def probe(self, additions=None):
        environment = previous.isolated_environment(os.environ, ROOT)
        # No external executable search is required by the core operation.
        environment['PATH'] = ''
        environment.update(additions or {})
        command = [sys.executable, '-B', '-S', '-c',
                   'import json,sys;sys.path.insert(0,sys.argv[1]);'
                   'from benchmark.evaluation.ai_independence_r5_48 import probe;'
                   'print(json.dumps(probe(sys.argv[1])))', str(ROOT)]
        result = subprocess.run(command, cwd=ROOT, env=environment,
                                capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, 'core probe failed; output withheld')
        value = json.loads(result.stdout)
        self.assertTrue(value['successful'])
        return value

    def test_validation_lowering_readonly_offline_no_opencode(self):
        value = self.probe()
        self.assertEqual(value['validation'], 'valid')
        self.assertTrue(value['invalid_rejected'])
        self.assertFalse(value['site_enabled'])
        self.assertEqual(value['denied_events'], [])

    def test_unreachable_endpoint(self):
        self.assertEqual(self.probe(), self.probe({'OPENAI_BASE_URL': 'http://127.0.0.1:1'}))

    def test_synthetic_credential_and_model_mutation(self):
        first = {'OPENAI_API_KEY': 'synthetic-development-value-a', 'DEVELOPMENT_MODEL': 'author-one'}
        second = {'OPENAI_API_KEY': 'synthetic-development-value-b', 'DEVELOPMENT_MODEL': 'author-two'}
        self.assertEqual(self.probe(first), self.probe(second))
        self.assertEqual(previous.effective_environment(first), previous.effective_environment(second))
        self.assertNotIn('synthetic-development', security.safe_bytes(previous.effective_environment(first)).decode())

    def test_authoring_and_unrelated_environment_not_core_inputs(self):
        changes = {'EDITOR': 'different-editor', 'OPENCODE_MODEL': 'author-model',
                   'UNRELATED_FIXTURE_VARIABLE': 'different'}
        self.assertEqual(self.probe(), self.probe(changes))

    def test_core_direct_imports_no_provider_inference(self):
        forbidden = {'openai', 'anthropic', 'google', 'opencode', 'requests', 'httpx'}
        for names in probes.imports(ROOT).values():
            self.assertFalse({n.split('.')[0] for n in names} & forbidden)


if __name__ == '__main__':
    unittest.main()
