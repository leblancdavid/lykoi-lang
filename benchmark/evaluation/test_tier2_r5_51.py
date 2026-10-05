"""Independent synthetic Tier-2 lifecycle and mutation challenges; no B02 data."""

import copy
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from benchmark.evaluation import tier2_r5_51 as tier
from benchmark.evaluation import security_r5_47 as security
from benchmark.evaluation.recorder_r5_43 import ProtocolFailure, canonical, loads


class Tier2Tests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.parent = Path(self.temporary.name)
        self.root = self.parent / 'inputs'
        self.output = self.parent / 'evidence'
        self.root.mkdir()
        self.output.mkdir()
        for role in tier.ROLES:
            (self.root / role).mkdir()
            (self.root / role / 'input.txt').write_bytes(role.encode())
        self.dep = self.parent / 'resolved-package.py'
        self.dep.write_bytes(b'implementation-v1')
        self.dependencies = [tier.dependency('mineral-package', '1', self.dep, 'selected result decoding')]
        self.boundary = {'scopes': {r: [r] for r in tier.ROLES}, 'unknown': [],
                         'recorder': 'synthetic-recorder-content-id',
                         'consumer': 'explicit synthetic callback; no ambient authoring inputs',
                         'native_materiality': [], 'exclusions': 'authoring roots are not consumed'}
        self.environment = tier.controlled_environment({}, self.root)
        self.git_rows = {'ls-tree': b'', 'ls-files': b''}
        self.mock = patch.object(tier, 'git', side_effect=lambda root, command, *args: self.git_rows[command])
        self.mock.start()
        self.addCleanup(self.mock.stop)
        self.frozen = self.capture()
        self.policy = {'experiment': 'r5.51-synthetic-mineral',
                       'stages': {n: 'qualified-' + n for n in tier.REQUIRED},
                       'required_locks': {'historical': 'synthetic-historical',
                                          'prospective': 'synthetic-prospective',
                                          'infrastructure': tier.INFRASTRUCTURE},
                       'infrastructure': tier.INFRASTRUCTURE, 'semantic_count': 30,
                       'canonical_protocol': tier.CANONICAL_PROTOCOL,
                       'authority': self.frozen['roles']['authority'],
                       'recorder': self.boundary['recorder']}
        self.results = {'identity': {'successful': True, 'semantic_count': 30},
                        'locks': {'successful': True, 'required_lock_state': self.policy['required_locks']},
                        'contamination': {'successful': True, 'findings': []},
                        'workspace': {'successful': True, 'dedicated': True}}
        self.evidence = {n: self.receipt(n) for n in tier.REQUIRED}
        self.cert = tier.certificate(self.frozen, self.evidence, self.policy)

    def capture(self):
        return tier.capture(self.root, self.boundary, self.environment, self.dependencies)

    def receipt(self, name, status='PASS', frozen=None):
        frozen = self.frozen if frozen is None else frozen
        return tier.receipt(frozen, frozen, self.policy['experiment'], name,
                            self.policy['stages'][name], status, self.results[name])

    def gate(self):
        workspace = tier.Workspace(self.root, self.output, self.policy['experiment'])
        workspace.enter()
        self.live = {'locks': self.policy['required_locks'],
                     'authority': self.policy['authority'], 'contamination': []}
        gate = tier.StaticGate(workspace, self.cert, self.frozen, self.evidence, self.policy,
                              self.capture, {n: lambda n=n: self.live[n] for n in self.live})
        gate.prepare()
        return gate

    def mutate(self, role):
        (self.root / role / 'input.txt').write_bytes(b'changed')

    def reject_mutation(self, role):
        gate = self.gate()
        self.mutate(role)
        calls = []
        with self.assertRaises(ProtocolFailure):
            gate.observe_synthetic('synthetic:mineral', lambda: calls.append(True))
        self.assertEqual(calls, [])
        self.assertEqual(gate.recorder.counts()['disposition'], 'zero')

    def test_deterministic_capture(self):
        self.assertEqual(self.frozen, self.capture())

    def test_canonical_round_trip(self):
        self.assertEqual(self.frozen, loads(canonical(self.frozen)))
        tier.check(loads(canonical(self.frozen)))

    def test_source_mutation(self):
        self.reject_mutation('subject')

    def test_compiler_mutation(self):
        self.reject_mutation('compiler')

    def test_semantic_registry_mutation(self):
        self.reject_mutation('semantics')

    def test_profile_mutation(self):
        self.reject_mutation('profiles')

    def test_authority_mutation(self):
        self.reject_mutation('authority')

    def test_evaluator_mutation(self):
        self.reject_mutation('evaluator')

    def test_dependency_same_version_mutation(self):
        gate = self.gate()
        self.dep.write_bytes(b'implementation-v2')
        with self.assertRaises(ProtocolFailure):
            gate.observe_synthetic('synthetic:mineral', lambda: self.fail('dispatch'))

    def test_effective_configuration_mutation(self):
        gate = self.gate()
        self.environment['LYKOI_STORE_POLICY'] = 'changed'
        with self.assertRaises(ProtocolFailure):
            gate.observe_synthetic('synthetic:mineral', lambda: self.fail('dispatch'))

    def test_untracked_membership_mutation(self):
        (self.root / 'compiler' / 'new-helper.py').write_bytes(b'new')
        self.assertNotEqual(self.frozen, self.capture())

    def test_staged_only_content_mutation(self):
        self.git_rows['ls-files'] = b'100644 ' + b'a' * 40 + b' 0\tcompiler/input.txt\0'
        self.assertNotEqual(self.frozen, self.capture())
        self.assertEqual(self.frozen['repository']['compiler/input.txt']['physical'],
                         self.capture()['repository']['compiler/input.txt']['physical'])

    def test_committed_content_mutation(self):
        self.git_rows['ls-tree'] = b'100644 blob ' + b'a' * 40 + b'\tcompiler/input.txt\0'
        self.assertNotEqual(self.frozen, self.capture())

    def test_declared_platform(self):
        self.assertIn('python_version_build', self.frozen['platform'])
        self.assertIn('native_boundary', self.frozen['platform'])
        self.assertNotIn('native_descendants', self.frozen)

    def test_ai_credential_independence(self):
        for ambient in ({'OPENAI_API_KEY': 'synthetic-one'}, {'OPENAI_API_KEY': 'synthetic-two'}, {}):
            self.environment = tier.controlled_environment(ambient, self.root)
            self.assertEqual(self.frozen, self.capture())
            self.assertNotIn('OPENAI_API_KEY', self.environment)

    def test_authoring_model_independence(self):
        ambient = {'OPENCODE_MODEL': 'synthetic-model', 'CHATGPT_MODEL': 'synthetic-model',
                   'DEVELOPMENT_MODEL': 'synthetic-model', 'AI_PROVIDER_ACCOUNT': 'synthetic-account'}
        self.environment = tier.controlled_environment(ambient, self.root)
        self.assertEqual(self.frozen, self.capture())

    def test_opencode_authoring_state_independence(self):
        (self.root / '.opencode').mkdir()
        (self.root / '.opencode' / 'authoring.json').write_bytes(b'{"model":"synthetic"}')
        self.assertEqual(self.frozen, self.capture())

    def test_editor_and_prompt_history_independence(self):
        (self.root / '.idea').mkdir()
        (self.root / '.idea' / 'editor.xml').write_bytes(b'metadata')
        (self.root / 'prompt-history.txt').write_bytes(b'synthetic prompt')
        self.environment = tier.controlled_environment({'EDITOR': 'synthetic-editor'}, self.root)
        self.assertEqual(self.frozen, self.capture())

    def test_unrelated_environment_independence(self):
        self.environment = tier.controlled_environment({'UNRELATED_SYNTHETIC': 'changed'}, self.root)
        self.assertEqual(self.frozen, self.capture())

    def test_authoring_named_file_inside_consumed_root_is_material(self):
        (self.root / 'compiler' / 'opencode.json').write_bytes(b'consumed fixture')
        self.assertNotEqual(self.frozen, self.capture())

    def test_secret_safe_capsule_publication(self):
        self.environment['application_password'] = 'synthetic-raw-value'
        with self.assertRaises(security.SecretRejected):
            self.capture()
        self.assertEqual(list(self.output.iterdir()), [])

    def test_secret_safe_result_publication(self):
        gate = self.gate()
        with self.assertRaises(ProtocolFailure):
            gate.observe_synthetic('synthetic:mineral', lambda: {'password': 'synthetic-raw-value'})
        self.assertFalse(gate.recorder.path('observation-1').exists())
        self.assertNotIn(b'synthetic-raw-value', b''.join(p.read_bytes() for p in self.output.iterdir()))

    def test_deterministic_certificate(self):
        self.assertEqual(self.cert, tier.certificate(self.frozen, self.evidence, self.policy))

    def test_stale_certificate(self):
        self.mutate('subject')
        with self.assertRaises(ProtocolFailure):
            tier.validate(self.cert, self.frozen, self.evidence, self.policy, self.capture())

    def test_mixed_state_evidence(self):
        self.mutate('compiler')
        self.evidence['identity'] = self.receipt('identity', frozen=self.capture())
        with self.assertRaises(ProtocolFailure):
            tier.certificate(self.frozen, self.evidence, self.policy)

    def test_cross_experiment_evidence(self):
        self.policy['experiment'] = 'other-experiment'
        with self.assertRaises(ProtocolFailure):
            tier.certificate(self.frozen, self.evidence, self.policy)

    def test_incomplete_stage(self):
        self.evidence['workspace'] = self.receipt('workspace', 'INCOMPLETE')
        with self.assertRaises(ProtocolFailure):
            tier.certificate(self.frozen, self.evidence, self.policy)

    def test_positive_exactly_one_lifecycle(self):
        gate = self.gate()
        calls = []
        def observe():
            calls.append(True)
            return {'mineral_count': 3, 'behavior': 'synthetic-only'}
        self.assertEqual(gate.observe_synthetic('synthetic:mineral', observe)['mineral_count'], 3)
        self.assertEqual(calls, [True])
        self.assertEqual(gate.recorder.counts(), {'reservations': 1, 'completed_observations': 1,
                         'disposition': 'one', 'observation_occurred': True})
        self.assertTrue((self.output / 'pre-state.json').exists())
        self.assertTrue((self.output / 'post-state.json').exists())
        self.assertEqual(loads((self.output / 'gate-result.json').read_bytes())['status'], 'PASS')

    def test_incomplete_observation(self):
        gate = self.gate()
        def fail():
            raise RuntimeError('synthetic interrupted observation')
        with self.assertRaises(ProtocolFailure):
            gate.observe_synthetic('synthetic:mineral', fail)
        self.assertEqual(gate.recorder.counts()['disposition'], 'indeterminate')
        self.assertEqual(gate.recorder.read('final')['status'], 'HALT')

    def test_second_observation_prevented(self):
        gate = self.gate()
        gate.observe_synthetic('synthetic:mineral', lambda: {'ok': True})
        with self.assertRaises(ProtocolFailure):
            gate.observe_synthetic('synthetic:mineral', lambda: self.fail('second dispatch'))
        self.assertEqual(gate.recorder.counts()['completed_observations'], 1)

    def test_during_observation_material_mutation(self):
        gate = self.gate()
        def observe():
            self.mutate('compiler')
            return {'ok': True}
        with self.assertRaises(ProtocolFailure):
            gate.observe_synthetic('synthetic:mineral', observe)
        self.assertEqual(gate.recorder.counts()['disposition'], 'one')
        self.assertEqual(gate.recorder.read('final')['status'], 'HALT')
        self.assertFalse((self.output / 'gate-result.json').exists())

    def test_repair_prohibited_and_restoration_cannot_resume(self):
        gate = self.gate()
        gate.observe_synthetic('synthetic:mineral', lambda: {'ok': True})
        with self.assertRaises(ProtocolFailure):
            gate.prohibit_repair()
        self.mutate('compiler')
        (self.root / 'compiler' / 'input.txt').write_bytes(b'compiler')
        with self.assertRaises(ProtocolFailure):
            gate.observe_synthetic('synthetic:mineral', lambda: self.fail('repair retry'))

    def test_contamination_rejection(self):
        gate = self.gate()
        self.live['contamination'] = ['synthetic-contamination']
        with self.assertRaises(ProtocolFailure):
            gate.observe_synthetic('synthetic:mineral', lambda: self.fail('dispatch'))

    def test_lock_rejection(self):
        gate = self.gate()
        self.live['locks'] = {}
        with self.assertRaises(ProtocolFailure):
            gate.observe_synthetic('synthetic:mineral', lambda: self.fail('dispatch'))

    def test_evidence_integrity_rejection(self):
        gate = self.gate()
        (self.output / 'identity-staged.json').write_bytes(b'{}')
        with self.assertRaises(ProtocolFailure):
            gate.observe_synthetic('synthetic:mineral', lambda: self.fail('dispatch'))

    def test_workspace_reentry_rejection(self):
        gate = self.gate()
        with self.assertRaises(ProtocolFailure):
            gate.workspace.enter()

    def test_overlapping_workspace_output_rejection(self):
        nested = self.root / 'output'
        nested.mkdir()
        with self.assertRaises(ProtocolFailure):
            tier.Workspace(self.root, nested, 'synthetic').enter()

    def test_bounded_pre_observation(self):
        gate = self.gate()
        gate.seconds = -1
        with self.assertRaises(ProtocolFailure):
            gate.observe_synthetic('synthetic:mineral', lambda: self.fail('dispatch'))
        self.assertEqual(gate.recorder.counts()['disposition'], 'zero')

    def test_bounded_post_observation(self):
        gate = self.gate()
        def observe():
            gate.seconds = -1
            return {'ok': True}
        with self.assertRaises(ProtocolFailure):
            gate.observe_synthetic('synthetic:mineral', observe)
        self.assertEqual(gate.recorder.read('final')['status'], 'HALT')

    def test_input_bytecode_rejected(self):
        (self.root / 'compiler' / 'input.pyc').write_bytes(b'cache')
        with self.assertRaises(ProtocolFailure):
            self.capture()

    def test_unmerged_index_rejected(self):
        self.git_rows['ls-files'] = b'100644 ' + b'a' * 40 + b' 1\tcompiler/input.txt\0'
        with self.assertRaises(ProtocolFailure):
            self.capture()

    def test_unknown_material_dependency_rejected(self):
        self.boundary['unknown'] = ['unresolved plugin']
        with self.assertRaises(ProtocolFailure):
            self.capture()

    def test_stage_drift_cannot_produce_pass(self):
        self.mutate('profiles')
        row = tier.receipt(self.frozen, self.capture(), 'synthetic', 'identity', 'mechanism',
                           'PASS', {'successful': True})
        self.assertEqual(row['status'], 'FAIL')


if __name__ == '__main__':
    unittest.main()
