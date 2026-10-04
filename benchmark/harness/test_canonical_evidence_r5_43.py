"""Independent synthetic infrastructure qualification; no application evaluator."""

import copy
import tempfile
import unittest
from pathlib import Path

from benchmark.evaluation.recorder_r5_43 import (
    PROTOCOL, ProtocolFailure, Recorder, canonical, digest, equivalent, loads, persist)


def evidence():
    return {'version': 'synthetic-v1', 'profile': 'mineral/nullable/integer',
            'classification': 'supported', 'failure': None,
            'provenance': {'source': 'independent', 'ids': ('alpha', 'beta')},
            'records': ({'values': [1, True, None, '1', (), {}, [([], (2, 3))]]},),
            'optional': None, 'empty': []}


class CanonicalEvidenceTests(unittest.TestCase):
    def test_tuple_origin_list_loaded_and_real_recorder_regression(self):
        original = evidence()
        with tempfile.TemporaryDirectory() as directory:
            recorder = Recorder(directory)
            recorder.freeze(original)
            loaded = recorder.read('baseline')['evidence']
            self.assertNotEqual(original, loaded)
            self.assertIs(type(original['records']), tuple)
            self.assertIs(type(loaded['records']), list)
            self.assertTrue(equivalent(original, loaded))
            self.assertTrue(recorder.verify(original))

    def test_nested_tuple_list_equivalence(self):
        self.assertTrue(equivalent({'a': (1, [({'b': (2, ())},)])},
                                   {'a': [1, [[{'b': [2, []]}]]]}))

    def test_round_trip(self):
        for value in (evidence(), [None, True, False, 0, -1, 1.25, -0.0, 'é', '\ud800'], {}, ()):
            with self.subTest(value=value):
                self.assertEqual(canonical(value), canonical(loads(canonical(value))))

    def test_mapping_order_independence(self):
        self.assertTrue(equivalent({'z': [2], 'a': {'b': 1, 'a': 0}},
                                   {'a': {'a': 0, 'b': 1}, 'z': (2,)}))

    def test_sequence_order(self):
        self.assertFalse(equivalent([1, 2], [2, 1]))

    def test_sequence_member_mutation(self):
        self.assertFalse(equivalent([1, 2], [1, 3]))

    def changed(self, transform):
        original = evidence()
        mutated = copy.deepcopy(original)
        transform(mutated)
        self.assertFalse(equivalent(original, mutated))

    def test_value_mutation(self):
        self.changed(lambda v: v.update(classification='unsupported'))

    def test_missing_field(self):
        self.changed(lambda v: v.pop('profile'))

    def test_extra_field(self):
        self.changed(lambda v: v.update(unexpected='relevant'))

    def test_nested_mutation(self):
        self.changed(lambda v: v['records'][0]['values'].__setitem__(0, 9))

    def test_null_absence(self):
        self.changed(lambda v: v.pop('optional'))
        self.assertFalse(equivalent({}, {'x': None}))

    def test_scalar_types(self):
        for a, b in ((1, '1'), (1, 1.0), (0.0, -0.0), ('é', 'e\u0301')):
            self.assertFalse(equivalent({'x': a}, {'x': b}))

    def test_boolean_numeric_collision(self):
        self.assertEqual(True, 1)  # raw Python equality would be unsafe
        for a, b in ((True, 1), (False, 0), (True, 1.0)):
            self.assertFalse(equivalent([{'x': a}], [{'x': b}]))

    def test_version_mismatch(self):
        self.changed(lambda v: v.update(version='synthetic-v2'))

    def test_corruption(self):
        for data in (b'{', b'{"a":1,"a":2}', b'NaN', b'Infinity', b'1e999',
                     b'{} trailing', b'\xff', b'{"x": [1,]}'):
            with self.subTest(data=data), self.assertRaises(ProtocolFailure):
                loads(data)

    def test_unsafe_runtime_inputs(self):
        cycle = []
        cycle.append(cycle)
        for value in ({1: 'x'}, {True: 'x'}, {1, 2}, b'bytes', float('nan'), float('inf'), cycle):
            with self.subTest(kind=type(value)), self.assertRaises(ProtocolFailure):
                canonical(value)

    def test_determinism(self):
        outputs = [canonical(evidence()) for _ in range(10)]
        self.assertEqual(len(set(outputs)), 1)
        self.assertEqual(len({digest(b) for b in outputs}), 1)

    def test_baseline_immutability(self):
        with tempfile.TemporaryDirectory() as directory:
            original = evidence()
            recorder = Recorder(directory)
            recorder.freeze(original)
            before = recorder.path('baseline').read_bytes()
            authority = canonical(original)
            original['records'][0]['values'][0] = 999
            detached = recorder.read('baseline')
            detached['evidence']['profile'] = 'mutated'
            self.assertEqual(before, recorder.path('baseline').read_bytes())
            self.assertEqual(authority, canonical(recorder.read('baseline')['evidence']))
            self.assertTrue(recorder.integrity()['valid'])


class LockedLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.recorder = Recorder(self.temp.name)
        self.calls = []
        self.recorder.freeze(evidence())

    def callback(self):
        self.calls.append('observation')
        return {'classification': 'synthetic-observed', 'rows': (1, 2), 'version': 'v1'}

    def test_successful_locked_lifecycle(self):
        r = self.recorder
        r.verify(evidence())
        r.observe(self.callback)
        r.verify(loads(canonical(evidence())))
        final = r.finish()
        self.assertEqual(final['status'], 'STOP')
        self.assertEqual(final['counts']['disposition'], 'one')
        self.assertTrue(final['counts']['observation_occurred'])
        self.assertEqual(self.calls, ['observation'])
        self.assertEqual(final, r.read('final'))
        with self.assertRaises(ProtocolFailure):
            r.observe(self.callback)
        with self.assertRaises(ProtocolFailure):
            r.finish()

    def test_prepass_mismatch_halt_zero(self):
        r = self.recorder
        changed = evidence()
        changed['classification'] = 'unsupported'
        with self.assertRaises(ProtocolFailure):
            r.verify(changed)
        self.assertEqual(r.read('halt')['stage'], 'pre-pass')
        self.assertEqual(r.finish()['counts']['disposition'], 'zero')
        self.assertFalse(r.read('final')['counts']['observation_occurred'])
        self.assertEqual(self.calls, [])

    def test_post_observation_mismatch_no_repair(self):
        r = self.recorder
        before = r.path('baseline').read_bytes()
        r.verify(evidence())
        r.observe(self.callback)
        changed = evidence()
        changed['profile'] = 'other'
        with self.assertRaises(ProtocolFailure):
            r.verify(changed)
        self.assertEqual(r.read('halt')['stage'], 'post-observation')
        self.assertEqual(r.finish()['counts']['disposition'], 'one')
        self.assertEqual(before, r.path('baseline').read_bytes())
        with self.assertRaises(ProtocolFailure):
            r.verify(evidence())
        self.assertEqual(len(self.calls), 1)

    def test_second_observation_prevented(self):
        r = self.recorder
        r.verify(evidence())
        r.observe(self.callback)
        with self.assertRaises(ProtocolFailure):
            r.observe(self.callback)
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(r.finish()['status'], 'HALT')
        self.assertEqual(r.read('final')['counts']['completed_observations'], 1)

    def test_multiple_receipts_detected(self):
        r = self.recorder
        r.verify(evidence())
        r.observe(self.callback)
        r.write('reservation-2', {'protocol': PROTOCOL, 'number': 2, 'lock': r.read('lock')['identity']})
        second = {'protocol': PROTOCOL, 'number': 2,
                  'reservation': digest(r.path('reservation-2').read_bytes()), 'evidence': {'synthetic': True}}
        second['identity'] = digest(canonical(second))
        r.write('observation-2', second)
        self.assertEqual(r.counts()['disposition'], 'multiple')
        self.assertEqual(r.finish()['status'], 'HALT')
        self.assertEqual(r.read('final')['counts']['completed_observations'], 2)

    def test_callback_exception_indeterminate_no_retry(self):
        r = self.recorder
        r.verify(evidence())
        def broken():
            self.calls.append('entered')
            raise RuntimeError('synthetic interruption')
        with self.assertRaises(ProtocolFailure):
            r.observe(broken)
        final = r.finish()
        self.assertEqual(final['status'], 'HALT')
        self.assertEqual(final['counts']['disposition'], 'indeterminate')
        self.assertIsNone(final['counts']['observation_occurred'])
        with self.assertRaises(ProtocolFailure):
            r.observe(self.callback)

    def test_lock_mutation_halt(self):
        r = self.recorder
        r.verify(evidence())
        r.path('baseline').write_bytes(b'{}\n')
        with self.assertRaises(ProtocolFailure):
            r.observe(self.callback)
        self.assertEqual(self.calls, [])
        self.assertFalse(r.finish()['integrity']['valid'])

    def test_observation_corruption_halt(self):
        r = self.recorder
        r.verify(evidence())
        r.observe(self.callback)
        changed = r.read('observation-1')
        changed['evidence']['classification'] = 'wrong'
        r.path('observation-1').write_bytes(canonical(changed))
        self.assertEqual(r.finish()['status'], 'HALT')
        self.assertEqual(r.read('final')['counts']['disposition'], 'corrupt')

    def test_verification_receipt_corruption_blocks_dispatch(self):
        r = self.recorder
        r.verify(evidence())
        r.path('verification-pre').write_bytes(b'{}')
        with self.assertRaises(ProtocolFailure):
            r.observe(self.callback)
        self.assertEqual(self.calls, [])

    def test_protected_file_post_observation_mutation(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / 'protected.txt'
            file.write_bytes(b'locked synthetic input')
            with tempfile.TemporaryDirectory() as run:
                r = Recorder(run)
                r.freeze(evidence(), [file])
                r.verify(evidence())
                def callback():
                    file.write_bytes(b'mutated during observation')
                    return {'observed': True}
                with self.assertRaises(ProtocolFailure):
                    r.observe(callback)
                self.assertEqual(r.read('halt')['stage'], 'post-observation')
                self.assertTrue(r.finish()['counts']['observation_occurred'])

    def test_baseline_replacement_prohibited(self):
        before = self.recorder.path('baseline').read_bytes()
        with self.assertRaises(FileExistsError):
            self.recorder.freeze({'new': 'authority'})
        self.assertEqual(before, self.recorder.path('baseline').read_bytes())


if __name__ == '__main__':
    unittest.main()
