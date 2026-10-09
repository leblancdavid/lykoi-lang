"""Neutral contract-preservation and malformed-input controls."""
import copy
import unittest
import jsonschema
from adapter import publish, validate
from bridge import SCHEMAS, definitions, handle
from common import tools

def accepted(schema, value):
    return jsonschema.Draft202012Validator(schema).is_valid(value)

class ExposureTests(unittest.TestCase):
    def test_adapter_rejects_unsupported(self):
        for schema in ({}, {'oneOf': []}, {'oneOf': [{'type': 'string'}]}, {'anyOf': [{'type': 'object'}]}):
            with self.assertRaises(ValueError):
                publish(schema)

    def test_identity_and_no_mutation(self):
        original = tools.definitions(['value', 'check', 'compose'])
        before = copy.deepcopy(original)
        actual = definitions('exact')
        self.assertEqual(original, before)
        self.assertEqual([x['name'] for x in actual], [x['function']['name'] for x in original])
        for x, y in zip(actual, original):
            self.assertEqual(x['description'], y['function']['description'])
            if x['name'] != 'apply_operation':
                self.assertEqual(x['inputSchema'], y['function']['parameters'])

    def test_argument_acceptance_controls(self):
        original = tools.definitions(['value', 'check', 'compose'])[1]['function']['parameters']
        converted = publish(original)
        values = [
            dict(definition='Neutral', alias='v', operation='value', type='Int64', expression=4, dependencies=[]),
            dict(definition='Neutral', alias='c', operation='check', expression=True, site=1, code='NEUTRAL', dependencies=[]),
            dict(definition='Neutral', alias='p', operation='compose', symbol='Other', arguments={}, dependencies=[]),
        ]
        controls = [None, 1, [], {}, True]
        for value in values:
            self.assertTrue(accepted(original, value))
            controls.append(value)
            for key in value:
                missing = copy.deepcopy(value)
                del missing[key]
                controls.append(missing)
            controls.extend([dict(value, provider_id='x'), dict(value, operation='invalid'), dict(value, dependencies=['x', 'x'])])
        controls.extend([dict(values[0], site=1), dict(values[1], type='Int64'), dict(values[2], expression=4)])
        for control in controls:
            self.assertEqual(accepted(original, control), accepted(converted, control), repr(control))

    def test_neutral_bridge_validation(self):
        cases = [('simple', {'text':'hello'}, {}), ('nested', {'payload': {'count':2}}, {'payload':{'count':True}}),
                 ('required', {'count':2}, {}), ('optional', {'text':'x'}, {'text':'x','unknown':1}),
                 ('enum', {'color':'red'}, {'color':'green'}), ('typed_root_union', {'kind':'alpha','count':2}, {'kind':'alpha','text':'bad'}),
                 ('nested_union', {'payload':{'kind':'beta','text':'x'}}, {'payload':{'kind':'beta','count':2}}),
                 ('discriminator', {'kind':'beta','text':'x'}, {'kind':'beta','count':2})]
        for mode, positive, negative in cases:
            for value, error in ((positive, False), (negative, True)):
                request = dict(id=1, method='tools/call', params=dict(name=mode, arguments=value))
                result = handle(request, mode, set())
                self.assertEqual(result['isError'], error)
                self.assertEqual(result['structuredContent']['ok'], not error)

    def test_exact_inert_all_tools(self):
        cases = [('declare_input', {'definition':'Neutral','inputs':[]}),
                 ('apply_operation', {'definition':'Neutral','alias':'n','operation':'value','type':'Int64','expression':4,'dependencies':[]}),
                 ('define_result', {'definition':'Neutral','result':0,'result_type':'Int64'}),
                 ('validate_candidate', {'target':'Neutral'})]
        for name, args in cases:
            request = dict(id=1, method='tools/call', params=dict(name=name, arguments=args))
            self.assertFalse(handle(request, 'exact', set())['isError'])
            request['params']['arguments']['provider_metadata'] = {'id':'x'}
            self.assertTrue(handle(request, 'exact', set())['isError'])

    def test_neutral_description_metadata_only(self):
        for original, neutral in zip(definitions('exact'), definitions('exact-neutral')):
            self.assertEqual(original['name'], neutral['name'])
            self.assertEqual(original['inputSchema'], neutral['inputSchema'])
            self.assertTrue(neutral['description'].endswith(original['description']))
            self.assertIn('ONLY validates arguments and returns an echo', neutral['description'])

if __name__ == '__main__':
    unittest.main()
