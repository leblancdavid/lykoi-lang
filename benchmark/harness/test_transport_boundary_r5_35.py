"""Generic collection, presentation and persistence boundary challenges."""

import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from benchmark.semantic import checked_transport_r5_35 as transport
from benchmark.semantic import current_pipeline as pipeline
from benchmark.semantic import transport_study_r5_35 as study
from benchmark.semantic import evolution_study_r5_33 as evolution
from benchmark.semantic.refined_generator_r5_28 import canonical


class TransportBoundaryR535(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = study.study()

    def assert_layers(self, call):
        verdict = call['verdict']
        for name, value in verdict.items():
            self.assertIn(value, (True, None), (name, call))
        self.assertIs(verdict['TRANSPORT_PROFILE_CONFORMANT'], True)
        self.assertIs(verdict['transport_grounded'], True)
        self.assertIs(verdict['OUTPUT_CONFORMANT'], True)
        self.assertIs(verdict['SEMANTIC_EXECUTION_CONFORMANT'], True if call['semantic'] else None)

    def test_independent_collection_calls_and_normalization(self):
        calls = self.report['A']['calls']
        for call in calls.values():
            self.assert_layers(call)
        self.assertEqual(calls['multiple']['event']['binding']['input']['channels'], [' right ', 'left'])
        self.assertEqual(calls['multiple']['semantic']['outcome']['value']['channels'], ['right', 'left'])
        self.assertEqual(calls['duplicates_case']['event']['binding']['input']['channels'], ['left', 'left', 'Left'])
        self.assertEqual(calls['duplicates_case']['semantic']['outcome']['value']['channels'], ['left', 'Left'])
        self.assertEqual(calls['multiple']['semantic']['outcome']['value']['samples'], [3, 1])
        self.assertEqual(calls['encoded']['semantic']['outcome']['value']['channels'], ['right', 'left', 'Left'])

    def test_collection_suppliedness_and_all_or_failure(self):
        calls = self.report['A']['calls']
        self.assertFalse(calls['omitted']['event']['binding']['slots']['channels']['supplied'])
        self.assertTrue(calls['empty']['event']['binding']['slots']['channels']['supplied'])
        self.assertEqual(calls['empty']['event']['binding']['input']['channels'], [])
        malformed = calls['malformed']
        self.assertIsNone(malformed['semantic'])
        self.assertIsNone(malformed['event']['binding']['input'])
        self.assertEqual(malformed['event']['binding']['failures'][0]['index'], 1)
        self.assertEqual(json.loads(malformed['public']['stderr']), {'code': 'invalid_sample'})
        self.assertEqual(malformed['public']['stdout'], '')

    def test_cross_shape_missing_state_and_materialization(self):
        calls = self.report['B']['calls']
        for call in calls:
            self.assert_layers(call)
        self.assertIsNone(calls[0]['pre_bytes'])
        self.assertIsNone(calls[0]['post_bytes'])
        self.assertEqual(calls[0]['semantic']['pre']['revision'], 1)
        self.assertIsNone(calls[1]['pre_bytes'])
        self.assertEqual(json.loads(calls[1]['post_bytes'])['revision'], 1)
        for before, after in zip(calls, calls[1:]):
            self.assertEqual(before['post_bytes'], after['pre_bytes'])
        self.assertEqual(json.loads(calls[-1]['post_bytes'])['revision'], 2)
        self.assertIsNone(calls[-1]['semantic'])
        self.assertEqual(calls[-1]['public']['exit'], 1)

    def test_persistence_failures_do_not_execute_or_create(self):
        for name in ('require', 'invalid_json', 'invalid_state'):
            call = self.report['B'][name]
            self.assert_layers(call)
            self.assertIsNone(call['semantic'])
            self.assertFalse(call['event']['semantic_invoked'])
            self.assertEqual(call['pre_bytes'], call['post_bytes'])
        self.assertIsNone(self.report['B']['require']['post_bytes'])

    def test_disposable_fault_layers(self):
        faults = self.report['faults']
        for name in ('A', 'B', 'C'):
            self.assertIs(faults[name]['verdict']['TRANSPORT_BINDING_CONFORMANT'], False)
            self.assertIs(faults[name]['verdict']['INPUT_BINDING_CONFORMANT'], False)
        for name in ('D', 'E', 'H', 'stream', 'exit'):
            self.assertIs(faults[name]['verdict']['SEMANTIC_EXECUTION_CONFORMANT'], True)
            self.assertIs(faults[name]['verdict']['OUTPUT_CONFORMANT'], False)
        for name in ('F', 'G'):
            self.assertIs(faults[name]['verdict']['PERSISTENCE_BOUNDARY_CONFORMANT'], False)
        self.assertIs(faults['H']['verdict']['PERSISTENCE_BOUNDARY_CONFORMANT'], True)

    def test_metadata_only_mutations(self):
        mutations = self.report['mutations']
        for call in mutations.values():
            self.assert_layers(call)
        self.assertEqual(len({call['adapter_digest'] for call in mutations.values()}), 1)
        self.assertIn('reading', json.loads(mutations['envelope_name']['public']['stdout']))
        self.assertEqual(mutations['stream']['public']['stdout'], '')
        self.assertEqual(mutations['status']['public']['exit'], 5)
        self.assertEqual(mutations['initial_reference']['semantic']['pre']['specimens'], [])
        self.assertIsNone(mutations['missing_policy']['semantic'])

    def test_invalid_checked_profiles(self):
        model = study.application()
        plans, spec, state = pipeline.checked(model), study.specification(model), transport.state_profile(model)
        def desc(s):
            return s['operations'][0]['outcomes']['calibrated']
        mutations = {
            'element_type': lambda s: s['operations'][0]['arguments'][0].__setitem__('decoder', 'integer'),
            'mode': lambda s: s['operations'][0]['arguments'][0].__setitem__('mode', 'single'),
            'order': lambda s: s['operations'][0]['arguments'][0].__setitem__('order', 'sort'),
            'omission': lambda s: s['operations'][0]['arguments'][0].__setitem__('omission', 'empty'),
            'unknown_result': lambda s: desc(s)['presentation']['fields'][1].__setitem__('path', ['absent']),
            'wrong_payload_type': lambda s: desc(s)['presentation']['fields'][1].__setitem__('type', 'string'),
            'missing_payload': lambda s: desc(s)['presentation']['fields'].pop(),
            'collision': lambda s: desc(s)['presentation']['fields'][1].__setitem__('name', 'ok'),
            'wrong_variant': lambda s: s['operations'][0]['outcomes'].__setitem__('foreign', desc(s)),
            'wrong_outcome_type': lambda s: desc(s).__setitem__('type', 'integer'),
            'wrong_failure_type': lambda s: s['failures']['binding_failure'].__setitem__('type', 'string'),
            'wrong_stream': lambda s: desc(s).__setitem__('stream', 'network'),
            'wrong_exit': lambda s: desc(s).__setitem__('exit', True),
            'unknown_initial': lambda s: s.__setitem__('persistence', {'missing': 'INITIALIZE_DECLARED_STATE', 'initial': 'invented'}),
        }
        for name, mutation in mutations.items():
            with self.subTest(name=name):
                changed = copy.deepcopy(spec)
                mutation(changed)
                with self.assertRaises(ValueError):
                    transport.validate(model, plans, changed, state)
        with patch('benchmark.semantic.unified_types_r5_27.analyze', side_effect=AssertionError('retyped')):
            transport.validate(model, plans, spec, state)

    def test_state_profile_and_stale_generation(self):
        model = evolution.application(False)
        state, spec = study.declaration_b(model), study.specification_b(model)
        for change in ('shape', 'value', 'version'):
            altered = copy.deepcopy(state)
            if change == 'shape':
                altered['versions']['V1'] = 'string'
            elif change == 'value':
                altered['initial']['origin']['value'] = []
            else:
                altered['initial']['origin']['version'] = 'absent'
            with self.assertRaises(ValueError):
                transport.validate(model, pipeline.checked(model), spec, altered)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            transport.generate(model, root, spec, state)
            pipeline.generate(evolution.application(False, default='crystal'), root)
            event, semantic, public, before, after = transport.observe(root, ['legacy'])
            self.assertIsNone(event)
            self.assertIsNone(semantic)
            self.assertIsNone(before)
            self.assertIsNone(after)
            self.assertEqual(public['exit'], 4)
            self.assertIn('stale or corrupt', public['stderr'])

    def test_required_collection_zero_not_invented(self):
        model = study.application()
        model['operations']['calibrate']['input']['record']['samples'] = {'sequence': 'integer'}
        # Remove semantic optional fallback after changing the checked slot.
        branch = model['operations']['calibrate']['branches'][0]['value']['record']
        branch['samples'] = study.ref('input', 'samples')
        branch['count'] = {'cardinality': study.ref('input', 'samples')}
        spec = study.specification(model)
        state = transport.state_profile(model)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            transport.generate(model, root, spec, state)
            (root / 'state.json').write_bytes(canonical([]))
            omitted = study.capture(model, root, spec, state, ['calibrate'])
            empty = study.capture(model, root, spec, state, ['calibrate-json', '--samples', '[]'])
            self.assert_layers(omitted)
            self.assert_layers(empty)
            self.assertIsNone(omitted['semantic'])
            self.assertEqual(empty['semantic']['outcome']['value']['samples'], [])

    def test_projection_direct_and_error_policies(self):
        model = study.application()
        state, spec = transport.state_profile(model), study.specification(model)
        desc = spec['operations'][0]['outcomes']['calibrated']
        desc['presentation'] = {'mode': 'object', 'coverage': 'full', 'fields': [
            {'name': key, 'source': 'payload', 'path': [key], 'type': shape}
            for key, shape in desc['type']['record'].items()]}
        error = spec['failures']['binding_failure']
        error['presentation'] = {'mode': 'object', 'coverage': 'full', 'fields': [
            {'name': 'error', 'source': 'payload', 'path': ['code'], 'type': 'string'}]}
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            transport.generate(model, root, spec, state)
            (root / 'state.json').write_bytes(canonical([]))
            success = study.capture(model, root, spec, state, ['calibrate', '--channels', 'L'])
            failed = study.capture(model, root, spec, state, ['calibrate', '--samples', 'bad'])
            self.assert_layers(success)
            self.assert_layers(failed)
            self.assertEqual(json.loads(success['public']['stdout']), {'channels': ['L'], 'samples': [], 'count': 0})
            self.assertEqual(json.loads(failed['public']['stderr']), {'error': 'invalid_sample'})
            spec['operations'][0]['outcomes']['calibrated']['presentation'] = {'mode': 'direct'}
            transport.generate(model, root, spec, state)
            self.assert_layers(study.capture(model, root, spec, state, ['calibrate']))

    def test_collection_binder_visits_every_element(self):
        from benchmark.semantic import transport_runtime_r5_35 as runtime
        from benchmark.semantic import input_binding_r5_32 as scalar
        model = study.application()
        spec, state = study.specification(model), transport.state_profile(model)
        route = transport.validate(model, pipeline.checked(model), spec, state)['calibrate']
        with patch.object(scalar, 'bind', wraps=scalar.bind) as binder:
            result = runtime.bind('calibrate', {'samples': ['3', 'bad', 'bad', '+1']}, route)
            self.assertEqual(binder.call_count, 4)
            self.assertEqual([error['index'] for error in result['failures']], [1, 2])
            self.assertIsNone(result['input'])

    def test_resealed_incompatible_state_policy_rejected_by_authority(self):
        model = evolution.application(False)
        state, spec = study.declaration_b(model), study.specification_b(model)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            transport.generate(model, root, spec, state)
            path = root / 'transport.json'
            profile = json.loads(path.read_bytes())
            profile['persistence']['initial'] = 'current_origin'
            path.write_bytes(canonical(profile))
            transport.seal(root)
            call = study.capture(model, root, spec, state, ['legacy'])
            self.assertIs(call['verdict']['TRANSPORT_PROFILE_CONFORMANT'], False)

    def test_empty_declared_initial_migration_and_missing_read_no_file(self):
        model = evolution.application(True)
        spec = transport.specification(pipeline.checked(model))
        state = transport.state_profile(model, {'empty': {'version': 'V1', 'value': []}})
        spec['persistence'] = {'missing': 'INITIALIZE_DECLARED_STATE', 'initial': 'empty'}
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            transport.generate(model, root, spec, state)
            read = study.capture(model, root, spec, state, ['legacy'])
            migration = study.capture(model, root, spec, state, ['migrate'])
            self.assert_layers(read)
            self.assert_layers(migration)
            self.assertIsNone(read['post_bytes'])
            self.assertEqual(migration['semantic']['outcome']['value'], 0)
            self.assertEqual(json.loads(migration['post_bytes'])['revision'], 2)

    def test_capability_matrix(self):
        matrix = json.loads(Path('benchmark/results/phase5c/R5_24-type-matrix.json').read_bytes())
        profile = matrix['r5_35_transport_boundary']
        self.assertEqual(profile['candidate_core_constructs'], 30)
        self.assertEqual(profile['entry_point'], 'benchmark.semantic.current_pipeline')
        self.assertEqual(set(profile['dimensions']), set(profile['per_dimension']))
        self.assertTrue(all(row['supported'] and row['evidence'] and row['limits']
                            for row in profile['per_dimension'].values()))


if __name__ == '__main__':
    unittest.main()
