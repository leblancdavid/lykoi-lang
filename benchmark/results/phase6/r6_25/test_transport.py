"""Synthetic provider regression/adversarial controls, no model exposure."""
import copy
import unittest
from common import tools, read
from transport import normalize, semantic_call, feedback, strict_loads, TransportError

class Qualification(unittest.TestCase):
    def call(self, **extra):
        return dict(function=dict(name='declare_input', arguments=dict(definition='Control', inputs=[])), **extra)

    def norm(self, calls, provider='ollama', seen=None):
        return normalize(calls, provider, 'synthetic-model', 0, tools.Session(['value']).schemas, set() if seen is None else seen)

    def test_native_metadata_regression(self):
        call = self.call(id='native')
        call['function']['index'] = 0
        e = self.norm([call])[0]
        self.assertTrue(tools.Session(['value']).dispatch(semantic_call(e))['success'])
        self.assertEqual(feedback(e, {'ok': True})['tool_call_id'], 'native')
        self.assertNotIn('index', e['semantic_arguments'])

    def test_preserved_actual_envelope(self):
        c = read('BASELINE.json')['preserved_native_envelope']
        e = normalize([c], 'ollama', 'qwen3:8b', 0, {'echo'}, set())[0]
        self.assertEqual(e['semantic_arguments'], {'text': 'local24'})

    def test_no_optional_metadata(self):
        self.assertEqual(self.norm([self.call()])[0]['call_id'], 'host:0:0')

    def test_multiple_ordered(self):
        calls = [self.call(id='one'), self.call(id='two')]
        for i, c in enumerate(calls):
            c['function']['index'] = i
        self.assertEqual([e['ordering']['position'] for e in self.norm(calls)], [0, 1])

    def test_unknown_metadata_quarantined(self):
        c = self.call(trace={'vendor': 4, 'latency': 0.5})
        c['function']['vendor_extension'] = {'id': 'meta'}
        e = self.norm([c])[0]
        self.assertEqual(e['provider_metadata']['envelope']['trace'], {'vendor': 4, 'latency': 0.5})
        self.assertEqual(semantic_call(e)['function']['arguments'], c['function']['arguments'])

    def test_unknown_metadata_does_not_fill_arguments(self):
        c = self.call(inputs=[], definition='Control')
        c['function']['arguments'] = {}
        e = self.norm([c])[0]
        self.assertFalse(tools.Session(['value']).dispatch(semantic_call(e))['arguments_valid'])

    def test_invalid_function_names(self):
        for name in (None, [], 'bad.name', ''):
            c = self.call(); c['function']['name'] = name
            with self.assertRaises(TransportError): self.norm([c])

    def test_unauthorized_requests(self):
        c = self.call(); c['function']['name'] = 'execute_python'
        with self.assertRaises(TransportError): self.norm([c])

    def test_invalid_argument_types(self):
        for args in ([], None, '{"definition":"Control","inputs":[]}'):
            c = self.call(); c['function']['arguments'] = args
            with self.assertRaises(TransportError): self.norm([c])
        c = self.call(); c['function']['arguments']['inputs'] = 1
        self.assertFalse(tools.Session(['value']).dispatch(semantic_call(self.norm([c])[0]))['arguments_valid'])

    def test_missing_required_arguments(self):
        c = self.call(); del c['function']['arguments']['definition']
        self.assertFalse(tools.Session(['value']).dispatch(semantic_call(self.norm([c])[0]))['arguments_valid'])

    def test_extra_semantic_arguments(self):
        c = self.call(); c['function']['arguments']['index'] = 0
        self.assertFalse(tools.Session(['value']).dispatch(semantic_call(self.norm([c])[0]))['arguments_valid'])

    def test_duplicates_atomic_and_cross_turn(self):
        seen = set()
        with self.assertRaises(TransportError): self.norm([self.call(id='same'), self.call(id='same')], seen=seen)
        self.assertEqual(seen, set())
        self.norm([self.call(id='same')], seen=seen)
        with self.assertRaises(TransportError): self.norm([self.call(id='same')], seen=seen)

    def test_malformed_envelopes(self):
        for calls in ([], {}, [None], [{}], [{'function': []}], [self.call(id=0)], [self.call(type='code')], [self.call(arguments={})]):
            with self.assertRaises(TransportError): self.norm(calls)

    def test_bad_indices(self):
        for index in (True, -1, '0', 1):
            c = self.call(); c['function']['index'] = index
            with self.assertRaises(TransportError): self.norm([c])
        calls = [self.call(id='a'), self.call(id='b')]
        calls[0]['function']['index'] = 0
        with self.assertRaises(TransportError): self.norm(calls)

    def test_openai_distinct_profile(self):
        c = self.call(id='oa', type='function')
        c['function']['arguments'] = '{"definition":"Control","inputs":[]}'
        e = self.norm([c], 'openai-compatible')[0]
        self.assertTrue(tools.Session(['value']).dispatch(semantic_call(e))['success'])
        with self.assertRaises(TransportError): self.norm([c])

    def test_duplicate_json_and_floats(self):
        for text in ('{"id":"a","id":"b"}', '{"x":1.0}', '{"x":NaN}'):
            with self.assertRaises(TransportError): strict_loads(text)
        c = self.call(id='oa', type='function')
        c['function']['arguments'] = '{"definition":"Control","definition":"Other","inputs":[]}'
        with self.assertRaises(TransportError): self.norm([c], 'openai-compatible')

    def test_semantic_dependencies_and_types_stay_strict(self):
        for expr, deps in ((['add', '$x', 1], []), (['add', True, 1], []), ('$missing', [])):
            session = tools.Session(['value'])
            session.dispatch(semantic_call(self.norm([dict(function=dict(name='declare_input', arguments=dict(definition='Control', inputs=[dict(name='x', type='Int64')])) )])[0]))
            before = copy.deepcopy(session.packet)
            c = dict(function=dict(name='apply_operation', arguments=dict(definition='Control', alias='v', operation='value', type='Int64', expression=expr, dependencies=deps)), id='metadata')
            c['function']['index'] = 0
            r = session.dispatch(semantic_call(self.norm([c])[0]))
            self.assertFalse(r['success'])
            self.assertEqual(session.packet, before)

if __name__ == '__main__':
    unittest.main(verbosity=2)
