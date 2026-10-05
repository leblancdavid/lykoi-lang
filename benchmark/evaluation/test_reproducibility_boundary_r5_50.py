"""Methodology witnesses on a synthetic mineral experiment; no benchmark loader.

This fixture illustrates the proposed Tier 2 projection, not a production
capsule implementation or an amendment to historical identity protocols.
"""

import copy
from pathlib import Path
import tempfile
import unittest

from benchmark.evaluation import preexposure_r5_45 as gate
from benchmark.evaluation import security_r5_47 as security
from benchmark.evaluation.recorder_r5_43 import ProtocolFailure, canonical


class BoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.inputs = self.root / 'inputs'
        self.inputs.mkdir()
        self.members = ('mineral.lykoi', 'semantic-registry.json', 'compiler.py',
                        'profile.json', 'mineral-contract.json', 'dependency.py',
                        'recorder.py', 'generated.py')
        for name in self.members:
            (self.inputs / name).write_bytes(('synthetic ' + name).encode())
        self.environment = {'MINERAL_MODE': 'strict', 'AUTHOR_MODEL': 'model-a',
                            'EDITOR': 'editor-a'}
        self.policy = {'purpose': 'synthetic-only', 'semantic_count': 30,
                       'recorder': 'synthetic-recorder',
                       'canonical_protocol': gate.CANONICAL_PROTOCOL,
                       'authority': 'synthetic-mineral-authority',
                       'stages': {'identity': 'synthetic-identity',
                                  'regression': 'synthetic-regression'}}
        self.descriptor = {
            'boundary': 'r5.50-tier2-synthetic', 'policy': self.policy,
            'runtime': {'implementation': 'CPython', 'version': 'fixture-version'},
            'dependencies': [{'name': 'mineral-math', 'version': '1.0',
                              'implementation': 'dependency.py'}],
            'platform': {'family': 'fixture-OS', 'architecture': 'fixture-arch',
                         'filesystem': 'local-exclusive-create'},
            'context': {'cwd_role': 'dedicated-mineral-workspace',
                        'startup': 'no-site-no-input-cache'},
        }
        self.frozen = self.capture()
        result = {'successful': True, **{k: self.policy[k] for k in
                  ('semantic_count', 'recorder', 'canonical_protocol', 'authority')}}
        self.evidence = {
            name: gate.stage(self.frozen['identity'], name, 'PASS',
                             result if name == 'identity' else {'successful': True}, mechanism)
            for name, mechanism in self.policy['stages'].items()}
        self.certificate = gate.assemble(self.frozen, self.evidence, self.policy)

    def capture(self):
        descriptor = copy.deepcopy(self.descriptor)
        # Explicit consumer contract: only MINERAL_MODE is read by this fixture.
        # Missing and empty remain different. No authoring values are persisted.
        descriptor['environment'] = {'MINERAL_MODE': self.environment.get('MINERAL_MODE')}
        return gate.state(self.inputs, descriptor)

    def assert_invalidated(self):
        current = self.capture()
        self.assertNotEqual(self.frozen['identity'], current['identity'])
        with self.assertRaises(ProtocolFailure):
            gate.validate(self.certificate, self.frozen, self.evidence, self.policy, current)

    def mutate_file(self, name):
        (self.inputs / name).write_bytes(b'changed synthetic implementation')
        self.assert_invalidated()

    def test_lykoi_source_mutation(self):
        self.mutate_file('mineral.lykoi')

    def test_semantic_registry_mutation(self):
        self.mutate_file('semantic-registry.json')

    def test_compiler_mutation(self):
        self.mutate_file('compiler.py')

    def test_profile_mutation(self):
        self.mutate_file('profile.json')

    def test_benchmark_authority_mutation(self):
        self.mutate_file('mineral-contract.json')

    def test_direct_dependency_same_version_mutation(self):
        self.mutate_file('dependency.py')

    def test_evaluation_infrastructure_mutation(self):
        self.mutate_file('recorder.py')

    def test_generated_artifact_mutation(self):
        self.mutate_file('generated.py')

    def test_relevant_untracked_membership(self):
        (self.inputs / 'import-shadow.py').write_bytes(b'synthetic new input')
        self.assert_invalidated()

    def test_relevant_environment_mutation(self):
        self.environment['MINERAL_MODE'] = 'relaxed'
        self.assert_invalidated()

    def test_environment_absent_empty_distinction(self):
        self.environment.pop('MINERAL_MODE')
        absent = self.capture()
        self.environment['MINERAL_MODE'] = ''
        self.assertNotEqual(absent['identity'], self.capture()['identity'])

    def test_stale_evidence(self):
        (self.inputs / 'mineral.lykoi').write_bytes(b'new source')
        with self.assertRaises(ProtocolFailure):
            gate.assemble(self.capture(), self.evidence, self.policy)

    def test_mixed_state_evidence(self):
        self.evidence['regression'] = gate.stage('other-state', 'regression', 'PASS',
                                                 {'successful': True}, 'synthetic-regression')
        with self.assertRaises(ProtocolFailure):
            gate.assemble(self.frozen, self.evidence, self.policy)

    def test_authoring_selection_does_not_invalidate(self):
        self.environment.update(AUTHOR_MODEL='model-b', EDITOR='editor-b',
                                AUTHOR_PROVIDER='other-authoring-provider')
        current = self.capture()
        self.assertEqual(canonical(self.frozen), canonical(current))
        self.assertNotIn(b'model-b', canonical(current))
        self.assertTrue(gate.validate(self.certificate, self.frozen, self.evidence,
                                      self.policy, current))

    def test_declared_platform_is_recorded_not_dll_recursion(self):
        self.assertNotIn('native_descendants', self.descriptor)
        self.descriptor['platform']['family'] = 'different-declared-platform'
        self.assert_invalidated()

    def recorder(self):
        recorder = security.PublicationRecorder(self.root / 'receipts')
        recorder.directory.mkdir()
        recorder.freeze({'capsule': self.frozen['identity']}, list(self.inputs.iterdir()))
        recorder.verify({'capsule': self.frozen['identity']})
        return recorder

    def test_repeated_unauthorized_observation(self):
        recorder = self.recorder()
        calls = []
        recorder.observe(lambda: calls.append('mineral') or {'result': 'synthetic'})
        with self.assertRaises(security.SecretRejected):
            recorder.observe(lambda: calls.append('second'))
        self.assertEqual(calls, ['mineral'])
        self.assertEqual(recorder.finish()['status'], 'HALT')

    def test_post_observation_repair_invalidates_no_recovery(self):
        recorder = self.recorder()
        recorder.observe(lambda: {'result': 'synthetic-failure'})
        (self.inputs / 'compiler.py').write_bytes(b'repaired after locked observation')
        with self.assertRaises(ProtocolFailure):
            recorder.verify({'capsule': self.capture()['identity']})
        (self.inputs / 'compiler.py').write_bytes(b'synthetic compiler.py')
        with self.assertRaises(ProtocolFailure):
            recorder.verify({'capsule': self.frozen['identity']})
        self.assertEqual(recorder.finish()['status'], 'HALT')

    def test_raw_secret_persistence_rejected(self):
        path = self.root / 'unsafe.json'
        with self.assertRaises(security.SecretRejected):
            security.persist(path, {'password': 'synthetic-r5.50-secret'})
        self.assertFalse(path.exists())


if __name__ == '__main__':
    unittest.main()
