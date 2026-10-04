"""Independent adversarial tests; all mutations occur in disposable fixtures."""

import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

from benchmark.evaluation import execution_identity_r5_48 as identity
from benchmark.evaluation import preexposure_r5_45 as prior
from benchmark.evaluation import infrastructure_lock_r5_47 as lock
from benchmark.evaluation import security_r5_47 as security
from benchmark.evaluation.recorder_r5_43 import ProtocolFailure, canonical, loads

ROOT = Path(__file__).resolve().parents[2]


class IdentityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'src').mkdir()
        self.source = self.root / 'src/input.txt'
        self.source.write_bytes(b'independent source')
        self.git('init', '-q')
        self.git('add', 'src/input.txt')
        self.git('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
                 '-c', 'commit.gpgsign=false', 'commit', '-qm', 'fixture')
        self.environment = {'PYTHONUTF8': '1', 'PYTHONDONTWRITEBYTECODE': '1', 'PYTHONHASHSEED': '0'}
        self.parts = {'interpreter': {'implementation': 'fixture', 'version': '1', 'flags': {}},
                      'dependencies': {'stdlib': {'version': '1', 'sha256': 'a' * 64}},
                      'tools': {'fixture-tool': {'version': '1', 'sha256': 'b' * 64}},
                      'context': {'cwd': 'fixture-root', 'inputs': []}}
        self.frozen = self.capture()
        self.policy = {'purpose': 'synthetic-only', 'semantic_count': 30,
                       'infrastructure': identity.BASELINE, 'execution_protocol': identity.PROTOCOL,
                       'recorder': 'fixture-recorder', 'canonical_protocol': prior.CANONICAL_PROTOCOL,
                       'authority': 'fixture-authority',
                       'required_locks': {'historical': 'fixture-historical', 'prospective': 'fixture-prospective',
                                          'infrastructure': identity.BASELINE},
                       'stages': {n: 'qualified-' + n for n in ('identity', 'locks', 'contamination', 'regression')}}
        self.evidence = {}
        for name, mechanism in self.policy['stages'].items():
            result = {'successful': True}
            if name == 'identity':
                result.update({n: self.policy[n] for n in
                               ('semantic_count', 'recorder', 'canonical_protocol', 'authority')})
            if name == 'locks':
                result['infrastructure'] = identity.BASELINE
                result['required_lock_state'] = copy.deepcopy(self.policy['required_locks'])
            if name == 'contamination':
                result['findings'] = []
            self.evidence[name] = identity.stage(self.frozen, self.capture(), name, result, mechanism)

    def git(self, *args):
        return identity.git(self.root, *args)

    def capture(self, **kwargs):
        return identity.compose(identity.repository(self.root),
                                environment=identity.effective_environment(self.environment),
                                scope='closed-fixture', **self.parts, **kwargs)

    def certificate(self):
        return identity.assemble(self.frozen, self.evidence, self.policy)

    def assert_changed(self):
        self.assertNotEqual(self.frozen['identity'], self.capture()['identity'])

    def test_deterministic_capture(self):
        self.assertEqual(canonical(self.frozen), canonical(self.capture()))

    def test_repeated_capture(self):
        self.assertEqual({self.capture()['identity'] for _ in range(4)}, {self.frozen['identity']})

    def test_canonical_round_trip(self):
        self.assertEqual(self.frozen, loads(canonical(self.frozen)))

    def test_canonical_publication_reload(self):
        path = self.root / 'receipt.json'
        security.persist(path, self.frozen)
        self.assertEqual(prior.reload(path), self.frozen)

    def test_source_mutation(self):
        self.source.write_bytes(b'changed')
        self.assert_changed()

    def test_staged_mutation(self):
        self.source.write_bytes(b'index changed')
        self.git('add', 'src/input.txt')
        self.source.write_bytes(b'independent source')
        self.assert_changed()

    def test_unstaged_mutation(self):
        before = self.git('ls-files', '--stage', '-z')
        self.source.write_bytes(b'unstaged')
        self.assertEqual(before, self.git('ls-files', '--stage', '-z'))
        self.assert_changed()

    def test_untracked_mutation(self):
        path = self.root / 'src/new.py'
        path.write_bytes(b'first')
        first = self.capture()
        path.write_bytes(b'second')
        self.assertNotEqual(first['identity'], self.capture()['identity'])

    def test_untracked_membership(self):
        (self.root / 'src/new.py').write_bytes(b'new')
        self.assert_changed()

    def test_ignored_material_input(self):
        (self.root / '.gitignore').write_text('src/new.py\n')
        (self.root / 'src/new.py').write_bytes(b'ignored but executable')
        self.assert_changed()

    def test_committed_content_mutation(self):
        self.source.write_bytes(b'committed')
        self.git('add', 'src/input.txt')
        self.git('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
                 '-c', 'commit.gpgsign=false', 'commit', '-qm', 'change')
        self.assert_changed()

    def test_runtime_mutation(self):
        self.parts['interpreter']['version'] = '2'
        self.assert_changed()

    def test_runtime_flag_mutation(self):
        self.parts['interpreter']['flags']['optimize'] = 1
        self.assert_changed()

    def test_dependency_mutation(self):
        self.parts['dependencies']['stdlib']['sha256'] = 'c' * 64
        self.assert_changed()

    def test_resolved_bytes_not_version_only(self):
        before = identity.implementations({'fixture': ('1', self.source)})
        self.source.write_bytes(b'different implementation same version')
        self.assertNotEqual(before, identity.implementations({'fixture': ('1', self.source)}))

    def test_missing_dependency_rejected(self):
        with self.assertRaises(ProtocolFailure):
            identity.implementations({'fixture': ('1', self.root / 'missing')})

    def test_environment_mutation(self):
        del self.environment['PYTHONHASHSEED']
        self.assert_changed()

    def test_unqualified_control_rejected(self):
        self.environment['PYTHONUTF8'] = '0'
        with self.assertRaises(ProtocolFailure):
            self.capture()

    def test_tool_mutation(self):
        self.parts['tools']['fixture-tool']['sha256'] = 'd' * 64
        self.assert_changed()

    def test_context_mutation(self):
        self.parts['context']['cwd'] = 'other-fixture-root'
        self.assert_changed()

    def test_openai_presence_excluded(self):
        self.environment['OPENAI_API_KEY'] = 'synthetic-development-value-a'
        self.assertEqual(self.frozen['identity'], self.capture()['identity'])
        self.assertNotIn('OPENAI_API_KEY', canonical(self.capture()).decode())

    def test_openai_value_change_excluded(self):
        self.environment['OPENAI_API_KEY'] = 'synthetic-development-value-a'
        before = self.capture()
        self.environment['OPENAI_API_KEY'] = 'synthetic-development-value-b'
        self.assertEqual(before, self.capture())

    def test_development_model_excluded(self):
        for model in ('GPT', 'Claude', 'Gemini', 'local', 'human'):
            self.environment['DEVELOPMENT_MODEL'] = model
            self.assertEqual(self.frozen, self.capture())

    def test_editor_metadata_excluded(self):
        (self.root / '.vscode').mkdir()
        (self.root / '.vscode/settings.json').write_text('{"editor.fontSize": 20}')
        self.environment['EDITOR'] = 'different-editor'
        self.assertEqual(self.frozen, self.capture())

    def test_opencode_authoring_configuration_excluded(self):
        (self.root / 'opencode.json').write_text('{"model": "synthetic/model"}')
        self.environment['OPENCODE_MODEL'] = 'different-model'
        self.assertEqual(self.frozen, self.capture())

    def test_authoring_index_excluded(self):
        (self.root / 'opencode.json').write_text('{"model": "synthetic/model"}')
        self.git('add', 'opencode.json')
        self.assertEqual(self.frozen, self.capture())

    def test_variable_domains(self):
        self.assertEqual(identity.classify_variable('OPENAI_API_KEY'), 'DEVELOPMENT_AUTHORING')
        self.assertEqual(identity.classify_variable('PYTHONUTF8'), 'BUILD_EXECUTION')
        self.assertEqual(identity.classify_variable('LYKOI_NEW_INPUT'), 'UNKNOWN')

    def test_ai_presence_cannot_be_injected_as_execution_control(self):
        body = prior.unseal(self.frozen)
        body['environment']['OPENAI_API_KEY'] = {'present': True}
        with self.assertRaises(ProtocolFailure):
            identity.check(prior.seal(body))

    def test_missing_verification_receipt_rejected(self):
        del self.evidence['locks']
        with self.assertRaises(ProtocolFailure):
            self.certificate()

    def test_cross_batch_agreement(self):
        self.certificate()
        self.assertTrue(identity.validate(self.certificate(), self.frozen, self.evidence,
                                          self.policy, self.capture()))

    def test_mid_stage_material_mutation_rejected(self):
        self.source.write_bytes(b'mid-stage')
        with self.assertRaises(ProtocolFailure):
            identity.stage(self.frozen, self.capture(), 'stage', {'successful': True}, 'mechanism')

    def test_mid_stage_authoring_change_accepted(self):
        self.environment['OPENAI_API_KEY'] = 'synthetic-development-value-a'
        receipt = identity.stage(self.frozen, self.capture(), 'stage', {'successful': True}, 'mechanism')
        self.assertEqual(receipt['status'], 'PASS')

    def test_mixed_state_certificate_rejected(self):
        self.source.write_bytes(b'other-state')
        self.evidence['regression'] = identity.stage(self.capture(), self.capture(), 'regression',
                                                    {'successful': True}, self.policy['stages']['regression'])
        with self.assertRaises(ProtocolFailure):
            self.certificate()

    def test_post_certificate_mutation_rejected(self):
        cert = self.certificate()
        self.source.write_bytes(b'late mutation')
        with self.assertRaises(ProtocolFailure):
            identity.validate(cert, self.frozen, self.evidence, self.policy, self.capture())

    def test_stale_certificate_rejected(self):
        cert = self.certificate()
        cert['state'] = 'stale'
        with self.assertRaises(ProtocolFailure):
            identity.validate(cert, self.frozen, self.evidence, self.policy, self.capture())

    def test_bounded_final_validation(self):
        cert = self.certificate()
        started = time.monotonic()
        identity.validate(cert, self.frozen, self.evidence, self.policy, self.capture())
        self.assertLess(time.monotonic() - started, 5)

    def test_valid_production_shaped_synthetic_assembly(self):
        cert = self.certificate()
        self.assertEqual(cert['status'], 'PASS')
        self.assertEqual(set(cert['stages']), set(self.policy['stages']))
        self.assertIn('no exposure authority', cert['assembly'])

    def test_production_assembly_not_falsely_qualified(self):
        self.policy['purpose'] = 'production'
        with self.assertRaises(ProtocolFailure):
            self.certificate()

    def test_unknown_material_dependency_blocks_assembly(self):
        value = self.capture(unknown=['material input unresolved'])
        with self.assertRaises(ProtocolFailure):
            identity.assemble(value, self.evidence, self.policy)

    def test_scope_promotion_rejected(self):
        with self.assertRaises(ProtocolFailure):
            identity.compose(identity.repository(self.root), environment={}, scope='qualified-capsule', **self.parts)

    def test_wrong_infrastructure_rejected(self):
        self.policy['infrastructure'] = 'wrong'
        with self.assertRaises(ProtocolFailure):
            self.certificate()

    def test_required_lock_state_mismatch_rejected(self):
        result = copy.deepcopy(self.evidence['locks']['result'])
        result['required_lock_state']['prospective'] = 'different-lock'
        self.evidence['locks'] = identity.stage(self.frozen, self.frozen, 'locks', result,
                                               self.policy['stages']['locks'])
        with self.assertRaises(ProtocolFailure):
            self.certificate()

    def test_resolved_token_module_publication_is_safe(self):
        resolved = identity.implementations({'token': ('fixture-version', self.source)})
        security.safe_bytes(resolved)
        self.assertEqual(resolved[0]['name'], 'token')

    def test_contamination_failure_rejected(self):
        self.evidence['contamination'] = identity.stage(self.frozen, self.frozen, 'contamination',
            {'successful': True, 'findings': ['foreign constraint']}, self.policy['stages']['contamination'])
        with self.assertRaises(ProtocolFailure):
            self.certificate()

    def test_secret_publication_rejected_before_write(self):
        path = self.root / 'unsafe.json'
        with self.assertRaises(security.SecretRejected):
            security.persist(path, {'OPENAI_API_KEY': 'synthetic-development-value-a'})
        self.assertFalse(path.exists())

    def test_unsafe_stage_result_rejected(self):
        with self.assertRaises(security.SecretRejected):
            identity.stage(self.frozen, self.frozen, 'stage',
                           {'successful': True, 'password': 'synthetic-development-value-a'}, 'mechanism')

    def recorder(self):
        path = self.root / 'recorder'
        path.mkdir()
        recorder = security.PublicationRecorder(path)
        baseline = {'certificate': self.certificate()['identity']}
        recorder.freeze(baseline, [self.source])
        recorder.verify(baseline)
        return recorder

    def test_synthetic_one_pass_and_second_dispatch_prevention(self):
        recorder = self.recorder()
        cert, calls = self.certificate(), []
        callback = lambda: calls.append('synthetic') or {'mineral': 'quartz'}
        identity.authorize_synthetic(cert, self.frozen, self.evidence, self.policy,
                                     self.capture, recorder, callback)
        with self.assertRaises(ProtocolFailure):
            identity.authorize_synthetic(cert, self.frozen, self.evidence, self.policy,
                                         self.capture, recorder, callback)
        self.assertEqual(calls, ['synthetic'])
        self.assertEqual(recorder.counts()['completed_observations'], 1)

    def test_final_check_prevents_reservation(self):
        recorder, calls = self.recorder(), []
        cert = self.certificate()
        self.source.write_bytes(b'late')
        with self.assertRaises(ProtocolFailure):
            identity.authorize_synthetic(cert, self.frozen, self.evidence, self.policy,
                                         self.capture, recorder, lambda: calls.append('unexpected'))
        self.assertEqual(calls, [])
        self.assertEqual(recorder.counts()['reservations'], 0)


class CoreIndependenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.environment = identity.isolated_environment(os.environ, ROOT)
        cls.command = [sys.executable, '-B', '-S', '-c',
                       'import json,sys;sys.path.insert(0,sys.argv[1]);'
                       'from benchmark.evaluation.ai_independence_r5_48 import probe;'
                       'print(json.dumps(probe(sys.argv[1])))', str(ROOT)]

    def run_probe(self, changes=None):
        result = subprocess.run(self.command, cwd=ROOT, env={**self.environment, **(changes or {})},
                                capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, 'core probe failed; raw diagnostics withheld')
        return json.loads(result.stdout)

    def test_no_credential_no_opencode_no_site_no_network(self):
        result = self.run_probe()
        self.assertTrue(result['successful'])
        self.assertFalse(result['site_enabled'])
        self.assertEqual(result['denied_events'], [])
        self.assertTrue(result['invalid_rejected'])

    def test_ai_provider_outage_equivalence(self):
        absent = self.run_probe()
        changed = self.run_probe({'OPENAI_API_KEY': 'synthetic-development-value-a',
                                  'OPENAI_BASE_URL': 'http://127.0.0.1:1',
                                  'ANTHROPIC_BASE_URL': 'http://127.0.0.1:1'})
        self.assertEqual(absent, changed)

    def test_credential_and_model_change_equivalence(self):
        first = self.run_probe({'OPENAI_API_KEY': 'synthetic-development-value-a', 'OPENCODE_MODEL': 'GPT'})
        second = self.run_probe({'OPENAI_API_KEY': 'synthetic-development-value-b', 'OPENCODE_MODEL': 'Claude'})
        self.assertEqual(first, second)

    def test_r5_47_successor_identity(self):
        path = ROOT / 'benchmark/results/phase5c/R5_47-infrastructure-lock-v2.json'
        value = lock.reload(path)
        self.assertEqual(value['identity'], identity.BASELINE)
        self.assertEqual(lock.verify(ROOT, value)['members'], 1065)
        body = {k: v for k, v in value.items() if k != 'identity'}
        # Independent reconstruction of the canonical digest and physical members.
        import hashlib
        expected = hashlib.sha256(json.dumps(body, sort_keys=True, ensure_ascii=True,
            separators=(',', ':'), allow_nan=False).encode()).hexdigest()
        self.assertEqual(expected, identity.BASELINE)
        for name, expected in value['files'].items():
            self.assertEqual(hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), expected)


if __name__ == '__main__':
    unittest.main()
