"""Independent adversarial qualification on a closed synthetic input tree."""

import copy
from pathlib import Path
import sys
import tempfile
import time
import unittest

from benchmark.evaluation import preexposure_r5_45 as gate
from benchmark.evaluation.recorder_r5_43 import Recorder, ProtocolFailure, canonical, persist


class CertificateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.inputs = self.root / 'inputs'
        self.inputs.mkdir()
        (self.inputs / 'source.txt').write_bytes(b'independent mineral input')
        self.policy = {'purpose': 'synthetic-only', 'semantic_count': 30,
                       'recorder': 'qualified-recorder-digest',
                       'canonical_protocol': gate.CANONICAL_PROTOCOL,
                       'authority': 'synthetic-authority-digest',
                       'stages': {name: 'qualified-' + name for name in
                                  ('identity', 'locks', 'regression', 'contamination')}}
        self.frozen = gate.state(self.inputs, {'policy': self.policy})
        self.evidence = {}
        for name, mechanism in self.policy['stages'].items():
            result = {'successful': True}
            if name == 'identity':
                result.update({k: self.policy[k] for k in
                               ('semantic_count', 'recorder', 'canonical_protocol', 'authority')})
            self.evidence[name] = gate.stage(self.frozen['identity'], name, 'PASS', result, mechanism)

    def certificate(self):
        return gate.assemble(self.frozen, self.evidence, self.policy)

    def replace(self, name, **changes):
        body = gate.unseal(self.evidence[name])
        body.update(changes)
        self.evidence[name] = gate.seal(body)

    def reject(self):
        with self.assertRaises(ProtocolFailure):
            self.certificate()

    def test_state_determinism(self):
        self.assertEqual(canonical(self.frozen), canonical(gate.state(self.inputs, {'policy': self.policy})))

    def test_state_mutation(self):
        (self.inputs / 'source.txt').write_bytes(b'changed')
        self.assertNotEqual(self.frozen['identity'], gate.state(self.inputs, {'policy': self.policy})['identity'])

    def test_membership_mutation(self):
        (self.inputs / 'additional.txt').write_bytes(b'new ignored or untracked input')
        self.assertNotEqual(self.frozen['identity'], gate.state(self.inputs, {'policy': self.policy})['identity'])

    def test_configuration_mutation(self):
        self.assertNotEqual(self.frozen['identity'], gate.state(self.inputs, {'policy': 'changed'})['identity'])

    def test_canonical_stage(self):
        value = self.evidence['locks']
        self.assertEqual(canonical(value), canonical(dict(reversed(list(value.items())))))

    def test_persistence_reload(self):
        path = self.root / 'stage.json'
        persist(path, self.evidence['locks'])
        self.assertEqual(canonical(gate.reload(path)), canonical(self.evidence['locks']))
        with self.assertRaises(FileExistsError):
            persist(path, self.evidence['locks'])

    def test_pass_record(self):
        self.assertEqual(self.evidence['locks']['status'], 'PASS')
        self.certificate()

    def test_fail_record(self):
        self.replace('locks', status='FAIL')
        self.reject()

    def test_incomplete_record(self):
        self.replace('locks', status='INCOMPLETE')
        self.reject()

    def test_deterministic_assembly(self):
        first = self.certificate()
        self.evidence = dict(reversed(list(self.evidence.items())))
        self.assertEqual(canonical(first), canonical(self.certificate()))

    def test_complete_acceptance(self):
        self.assertTrue(gate.validate(self.certificate(), self.frozen, self.evidence, self.policy, self.frozen))

    def test_missing_stage(self):
        del self.evidence['locks']
        self.reject()

    def test_extra_stage(self):
        self.evidence['extra'] = self.evidence['locks']
        self.reject()

    def test_mixed_state(self):
        self.replace('locks', state='different-state')
        self.reject()

    def test_stale_stage(self):
        (self.inputs / 'source.txt').write_bytes(b'new state')
        self.frozen = gate.state(self.inputs, {'policy': self.policy})
        self.reject()

    def test_altered_evidence(self):
        self.evidence['locks']['result']['successful'] = False
        self.reject()

    def test_altered_persisted_evidence(self):
        path = self.root / 'stage.json'
        persist(path, self.evidence['locks'])
        path.write_bytes(path.read_bytes().replace(b'PASS', b'FAIL'))
        with self.assertRaises(ProtocolFailure):
            gate.reload(path)

    def test_noncanonical_persistence(self):
        path = self.root / 'stage.json'
        persist(path, self.evidence['locks'])
        path.write_bytes(b' ' + path.read_bytes())
        with self.assertRaises(ProtocolFailure):
            gate.reload(path)

    def identity_mutation(self, field, value):
        result = copy.deepcopy(self.evidence['identity']['result'])
        result[field] = value
        self.replace('identity', result=result)
        self.reject()

    def test_wrong_recorder(self):
        self.identity_mutation('recorder', 'unqualified')

    def test_wrong_canonical_protocol(self):
        self.identity_mutation('canonical_protocol', 'incompatible')

    def test_semantic_count_mutation(self):
        self.identity_mutation('semantic_count', 31)

    def test_semantic_count_scalar_type(self):
        self.identity_mutation('semantic_count', 30.0)

    def test_frozen_authority_mutation(self):
        self.identity_mutation('authority', 'mutated')

    def test_lock_failure(self):
        self.replace('locks', result={'successful': False, 'mismatches': ['protected']})
        self.reject()

    def test_contamination_failure(self):
        self.replace('contamination', result={'successful': False, 'findings': ['forbidden']})
        self.reject()

    def test_wrong_mechanism(self):
        self.replace('locks', mechanism='unqualified')
        self.reject()

    def test_post_certificate_mutation(self):
        cert = self.certificate()
        (self.inputs / 'source.txt').write_bytes(b'mutation after certification')
        with self.assertRaises(ProtocolFailure):
            gate.validate(cert, self.frozen, self.evidence, self.policy,
                          gate.state(self.inputs, {'policy': self.policy}))

    def recorder(self):
        directory = self.root / 'recorder'
        directory.mkdir()
        recorder = Recorder(directory)
        baseline = {'certificate': self.certificate()['identity']}
        recorder.freeze(baseline, list(self.inputs.iterdir()))
        recorder.verify(baseline)
        return recorder

    def test_synthetic_lifecycle_exactly_one_and_second_prevention(self):
        recorder = self.recorder()
        calls = []
        callback = lambda: calls.append('synthetic') or {'mineral': 'quartz'}
        gate.synthetic_authorize(self.certificate(), self.frozen, self.evidence,
                                 self.policy, self.frozen, recorder, callback)
        self.assertEqual(recorder.counts()['completed_observations'], 1)
        with self.assertRaises(ProtocolFailure):
            gate.synthetic_authorize(self.certificate(), self.frozen, self.evidence,
                                     self.policy, self.frozen, recorder, callback)
        recorder.integrity()
        self.assertEqual(recorder.finish()['status'], 'STOP')
        self.assertEqual(calls, ['synthetic'])

    def test_stale_synthetic_authorization(self):
        recorder = self.recorder()
        (self.inputs / 'source.txt').write_bytes(b'stale')
        calls = []
        with self.assertRaises(ProtocolFailure):
            gate.synthetic_authorize(self.certificate(), self.frozen, self.evidence, self.policy,
                                     gate.state(self.inputs, {'policy': self.policy}), recorder,
                                     lambda: calls.append('unexpected'))
        self.assertEqual(calls, [])
        self.assertEqual(recorder.counts()['reservations'], 0)

    def test_negative_synthetic_variants_no_reservation(self):
        recorder = self.recorder()
        cert = self.certificate()
        for change in ('missing', 'incomplete', 'mixed'):
            saved = copy.deepcopy(self.evidence)
            if change == 'missing':
                del self.evidence['regression']
            else:
                self.replace('regression', **({'status': 'INCOMPLETE'} if change == 'incomplete'
                                               else {'state': 'different'}))
            with self.assertRaises(ProtocolFailure):
                gate.synthetic_authorize(cert, self.frozen, self.evidence, self.policy,
                                         self.frozen, recorder, lambda: self.fail('dispatch'))
            self.evidence = saved
        self.assertEqual(recorder.counts()['reservations'], 0)

    def test_timeout_and_recomputation(self):
        status, result = gate.bounded([sys.executable, '-c', 'import time; time.sleep(1)'],
                                      self.root, None, 0.05)
        self.assertEqual(status, 'INCOMPLETE')
        old = gate.stage(self.frozen['identity'], 'locks', status, result, self.policy['stages']['locks'])
        persist(self.root / 'interrupted.json', old)
        self.evidence['locks'] = old
        self.reject()
        status, result = gate.bounded([sys.executable, '-c', 'pass'], self.root, None, 5)
        self.assertEqual(status, 'PASS')
        self.evidence['locks'] = gate.stage(self.frozen['identity'], 'locks', status, result,
                                           self.policy['stages']['locks'])
        self.certificate()
        self.assertEqual(gate.reload(self.root / 'interrupted.json')['status'], 'INCOMPLETE')

    def test_subprocess_failure(self):
        status, result = gate.bounded([sys.executable, '-c', 'raise SystemExit(3)'], self.root, None, 5)
        self.assertEqual(status, 'FAIL')
        self.assertFalse(result['successful'])

    def test_bounded_assembly_and_validation(self):
        started = time.monotonic()
        for _ in range(100):
            cert = self.certificate()
            gate.validate(cert, self.frozen, self.evidence, self.policy, self.frozen)
        self.assertLess(time.monotonic() - started, 5)


if __name__ == '__main__':
    unittest.main()
