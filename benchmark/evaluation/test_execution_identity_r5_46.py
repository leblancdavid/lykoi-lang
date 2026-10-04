"""Independent adversarial probes on a disposable Git repository and dependency."""

import copy
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

from benchmark.evaluation import execution_identity_r5_46 as gate
from benchmark.evaluation import preexposure_r5_45 as prior
from benchmark.evaluation.recorder_r5_43 import Recorder, ProtocolFailure, canonical, loads, persist


class ExecutionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / 'repo'
        self.repo.mkdir()
        self.source = self.repo / 'mineral.txt'
        self.source.write_bytes(b'quartz')
        self.git('init', '-q')
        self.git('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
                 'add', 'mineral.txt')
        self.git('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
                 '-c', 'core.hooksPath=', 'commit', '-qm', 'fixture')
        self.key = b'qualification-key-not-a-production-secret'  # fixture-only
        self.lib = self.root / 'library.py'
        self.lib.write_bytes(b'VALUE = 1\n')
        self.resolved = {'mineral-library': ('1.0', self.lib)}
        self.interpreter = {'implementation': 'synthetic', 'version': '1.0', 'flags': {'cache': 0}}
        self.env = {'MODE': 'controlled', 'TOKEN': 'synthetic-credential'}
        self.tools = {'fixture-tool': {'version': '1', 'implementation': 'fixture-bytes'}}
        self.context = {'cwd_role': 'repository-root', 'case_sensitive': False}
        self.policy = {'purpose': 'synthetic-only', 'semantic_count': 30,
                       'recorder': 'qualified-recorder-digest',
                       'canonical_protocol': prior.CANONICAL_PROTOCOL,
                       'authority': 'synthetic-authority',
                       'stages': {name: 'qualified-' + name for name in
                                  ('identity', 'locks', 'regression', 'contamination')}}
        self.frozen = self.capture()
        self.evidence = {}
        for name, mechanism in self.policy['stages'].items():
            result = {'successful': True}
            if name == 'identity':
                result.update({k: self.policy[k] for k in
                               ('semantic_count', 'recorder', 'canonical_protocol', 'authority')})
            self.evidence[name] = gate.stage(self.frozen, self.capture(), name, result, mechanism)

    def git(self, *arguments):
        return gate.git(self.repo, *arguments)

    def capture(self):
        return gate.compose(gate.repository(self.repo, self.key), self.interpreter,
                            gate.dependencies(self.resolved, ['mineral-library']),
                            gate.environment(self.env, ['MODE', 'TOKEN'], ['TOKEN'], self.key),
                            self.tools, self.context)

    def changed(self):
        self.assertNotEqual(self.frozen['identity'], self.capture()['identity'])

    def certificate(self):
        return gate.assemble(self.frozen, self.evidence, self.policy)

    def recorder(self):
        directory = self.root / 'receipts'
        directory.mkdir()
        recorder = Recorder(directory)
        baseline = {'certificate': self.certificate()['identity']}
        recorder.freeze(baseline, [self.source])
        recorder.verify(baseline)
        return recorder

    def test_repository_determinism(self):
        self.assertEqual(self.frozen['repository'], self.capture()['repository'])

    def test_source_mutation(self):
        self.source.write_bytes(b'granite')
        self.changed()

    def test_dirty_tree(self):
        self.source.write_bytes(b'dirty')
        self.assertEqual(self.frozen['repository']['head'], self.capture()['repository']['head'])
        self.changed()

    def test_staged_only_mutation(self):
        self.source.write_bytes(b'staged')
        self.git('add', 'mineral.txt')
        self.source.write_bytes(b'quartz')
        self.assertEqual(self.frozen['repository']['files'], self.capture()['repository']['files'])
        self.changed()

    def test_unstaged_mutation(self):
        self.source.write_bytes(b'unstaged')
        self.changed()

    def test_untracked_mutation(self):
        (self.repo / 'module.py').write_bytes(b'new relevant input')
        self.changed()

    def test_ignored_input_mutation(self):
        (self.repo / '.gitignore').write_bytes(b'cached.py\n')
        before = self.capture()
        (self.repo / 'cached.py').write_bytes(b'ignored executable input')
        self.assertNotEqual(before['identity'], self.capture()['identity'])

    def test_git_config_mutation(self):
        self.git('config', 'core.autocrlf', 'false')
        self.changed()

    def test_git_secret_not_persisted(self):
        secret = 'synthetic-private-git-value'
        self.git('config', 'fixture.credential', secret)
        self.assertNotIn(secret.encode(), canonical(self.capture()))

    def test_runtime_determinism(self):
        self.assertEqual(canonical(gate.runtime()), canonical(gate.runtime()))

    def test_runtime_version_mutation(self):
        self.interpreter['version'] = '2.0'
        self.changed()

    def test_runtime_flags_mutation(self):
        self.interpreter['flags']['cache'] = 1
        self.changed()

    def test_dependencies_determinism(self):
        self.assertEqual(self.capture()['dependencies'], self.frozen['dependencies'])

    def test_dependency_version_mutation(self):
        self.resolved['mineral-library'] = ('2.0', self.lib)
        self.changed()

    def test_dependency_same_version_different_bytes(self):
        self.lib.write_bytes(b'VALUE = 2\n')
        self.changed()

    def test_missing_dependency(self):
        self.lib.unlink()
        with self.assertRaises(ProtocolFailure):
            self.capture()

    def test_unexpected_dependency(self):
        self.resolved['unexpected'] = ('1', self.lib)
        with self.assertRaises(ProtocolFailure):
            self.capture()

    def test_environment_determinism(self):
        self.assertEqual(self.capture()['environment'], self.frozen['environment'])

    def test_relevant_environment_mutation(self):
        self.env['MODE'] = 'other'
        self.changed()

    def test_present_to_absent(self):
        del self.env['MODE']
        self.changed()

    def test_absent_to_present(self):
        del self.env['MODE']
        before = self.capture()
        self.env['MODE'] = ''
        self.assertNotEqual(before['identity'], self.capture()['identity'])

    def test_empty_distinct_from_value(self):
        self.env['MODE'] = ''
        self.changed()

    def test_irrelevant_environment_stability(self):
        self.env['TERMINAL_COLOR'] = 'purple'
        self.assertEqual(self.frozen, self.capture())

    def test_external_tool_identity(self):
        self.assertEqual(self.frozen['tools'], self.capture()['tools'])

    def test_external_tool_mutation(self):
        self.tools['fixture-tool']['version'] = '2'
        self.changed()

    def test_context_mutation(self):
        self.context['cwd_role'] = 'external-data-root'
        self.changed()

    def test_filesystem_semantics_mutation(self):
        self.context['case_sensitive'] = True
        self.changed()

    def test_secret_safe_identity(self):
        self.assertNotIn(b'synthetic-credential', canonical(self.frozen))
        self.env['TOKEN'] = 'different-synthetic-secret'
        self.changed()

    def test_weak_secret_key_rejected(self):
        with self.assertRaises(ProtocolFailure):
            gate.private_identity(b'weak', 'token', 'value')

    def test_key_rotation_invalidates(self):
        self.key = b'different-key-for-synthetic-qualification'
        self.changed()

    def test_canonical_serialization(self):
        self.assertEqual(canonical(self.frozen), canonical(dict(reversed(list(self.frozen.items())))))

    def test_round_trip(self):
        path = self.root / 'state.json'
        persist(path, self.frozen)
        self.assertEqual(self.frozen, prior.reload(path))
        gate.validate_state(prior.reload(path))

    def test_repeated_capture(self):
        for _ in range(3):
            self.assertEqual(self.frozen, self.capture())

    def test_process_invocation_determinism(self):
        command = [sys.executable, '-B', '-c',
                   'from benchmark.evaluation.execution_identity_r5_46 import runtime; '
                   'from benchmark.evaluation.recorder_r5_43 import canonical; '
                   'import sys; sys.stdout.buffer.write(canonical(runtime()))']
        first = subprocess.check_output(command, timeout=10)
        self.assertEqual(first, subprocess.check_output(command, timeout=10))

    def test_full_identity_across_processes(self):
        program = (
            'import sys; from benchmark.evaluation import execution_identity_r5_46 as g; '
            'from benchmark.evaluation.recorder_r5_43 import canonical, loads; '
            'v=loads(sys.stdin.buffer.read()); '
            's=g.compose(g.repository(v["repo"],v["key"].encode()),v["runtime"],'
            'g.dependencies({"mineral-library":("1.0",v["lib"])},["mineral-library"]),'
            'g.environment(v["env"],["MODE","TOKEN"],["TOKEN"],v["key"].encode()),'
            'v["tools"],v["context"]); sys.stdout.buffer.write(canonical(s))')
        inputs = canonical({'repo': str(self.repo), 'lib': str(self.lib),
                            'key': self.key.decode(), 'runtime': self.interpreter,
                            'env': self.env, 'tools': self.tools, 'context': self.context})
        for _ in range(2):
            captured = subprocess.check_output([sys.executable, '-B', '-c', program],
                                               input=inputs, timeout=10)
            self.assertEqual(canonical(self.frozen), captured)

    def test_submodule_fails_closed(self):
        head = self.git('rev-parse', 'HEAD').decode().strip()
        self.git('update-index', '--add', '--cacheinfo', '160000,' + head + ',nested')
        with self.assertRaises(ProtocolFailure):
            self.capture()

    def test_aba_is_not_claimed_detectable(self):
        original = self.lib.read_bytes()
        self.lib.write_bytes(b'transient mutation')
        self.lib.write_bytes(original)
        self.assertEqual(self.frozen, self.capture())
        # Endpoint equality alone cannot prove immutability during a stage.

    def test_cross_batch_agreement(self):
        states = {value['state'] for value in self.evidence.values()}
        self.assertEqual(states, {gate.bridge(self.capture())['identity']})
        self.certificate()

    def test_mid_stage_mutation(self):
        self.lib.write_bytes(b'changed during verification')
        with self.assertRaises(ProtocolFailure):
            gate.stage(self.frozen, self.capture(), 'regression', {'successful': True}, 'qualified')

    def test_mixed_execution_certificate(self):
        self.env['MODE'] = 'other'
        self.evidence['locks'] = gate.stage(self.capture(), self.capture(), 'locks',
                                          {'successful': True}, self.policy['stages']['locks'])
        with self.assertRaises(ProtocolFailure):
            self.certificate()

    def test_post_certificate_mutation(self):
        certificate = self.certificate()
        self.lib.write_bytes(b'changed after certificate')
        with self.assertRaises(ProtocolFailure):
            gate.validate(certificate, self.frozen, self.evidence, self.policy, self.capture())

    def test_irrelevant_mutation_certificate_stability(self):
        certificate = self.certificate()
        self.env['TERMINAL_COLOR'] = 'green'
        self.assertTrue(gate.validate(certificate, self.frozen, self.evidence, self.policy, self.capture()))

    def test_unknown_closure_blocks_assembly(self):
        body = prior.unseal(self.frozen)
        body['unknown'] = ['native transitive closure']
        with self.assertRaises(ProtocolFailure):
            gate.assemble(prior.seal(body), self.evidence, self.policy)

    def test_production_assembly_rejected(self):
        policy = {**self.policy, 'purpose': 'production'}
        with self.assertRaises(ProtocolFailure):
            gate.assemble(self.frozen, self.evidence, policy)

    def test_bounded_capture(self):
        started = time.monotonic()
        self.capture()
        self.assertLess(time.monotonic() - started, 5)

    def test_bounded_final_validation(self):
        certificate = self.certificate()
        started = time.monotonic()
        gate.validate(certificate, self.frozen, self.evidence, self.policy, self.capture())
        self.assertLess(time.monotonic() - started, 5)

    def test_valid_authorization_and_second_prevention(self):
        certificate, recorder = self.certificate(), self.recorder()
        calls = []
        callback = lambda: calls.append('mineral') or {'mineral': 'quartz'}
        gate.authorize(certificate, self.frozen, self.evidence, self.policy, self.capture, recorder, callback)
        with self.assertRaises(ProtocolFailure):
            gate.authorize(certificate, self.frozen, self.evidence, self.policy, self.capture, recorder, callback)
        self.assertEqual(calls, ['mineral'])
        self.assertEqual(recorder.counts()['completed_observations'], 1)
        self.assertEqual(recorder.finish()['status'], 'STOP')

    def test_stale_authorization_no_reservation(self):
        certificate, recorder = self.certificate(), self.recorder()
        self.resolved['mineral-library'] = ('2.0', self.lib)
        with self.assertRaises(ProtocolFailure):
            gate.authorize(certificate, self.frozen, self.evidence, self.policy, self.capture,
                           recorder, lambda: self.fail('stale dispatch'))
        self.assertEqual(recorder.counts()['reservations'], 0)

    def test_irrelevant_mutation_authorization(self):
        certificate, recorder = self.certificate(), self.recorder()
        self.env['TERMINAL_COLOR'] = 'yellow'
        gate.authorize(certificate, self.frozen, self.evidence, self.policy, self.capture,
                       recorder, lambda: {'mineral': 'quartz'})
        self.assertEqual(recorder.counts()['completed_observations'], 1)


if __name__ == '__main__':
    unittest.main()
