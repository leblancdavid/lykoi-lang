"""R5.39 independent dependency, binding, boundary and prediction challenges."""

import copy
import itertools
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from benchmark.semantic import boundary_study_r5_39 as study
from benchmark.semantic import nullable_study_r5_38 as nullable
from benchmark.semantic import application_boundary_r5_39 as boundary
from benchmark.semantic import current_pipeline as pipeline
from benchmark.semantic import unified_types_r5_27 as types
from benchmark.semantic import refined_generator_r5_28 as emitter
from benchmark.semantic import input_binding_r5_32 as binder
from benchmark.semantic import public_binding_r5_32 as oracle
from benchmark.semantic import transport_runtime_r5_35 as runtime
from benchmark.semantic import checked_launch_r5_36 as launch
from benchmark.semantic import state_runtime_r5_39 as codec
from benchmark.semantic import verify_boundary_r5_39 as verifier
from benchmark.semantic import readiness_r5_39 as readiness


class RefinementDependencies(unittest.TestCase):
    def test_duplicate_guard_serializations_ground_current_pipeline(self):
        for field, operation in [('reviewed', 'reviewed'), ('embargo', 'ordered'), ('window', 'window')]:
            base = nullable.application()
            contract = base['operations'][operation]
            if operation == 'reviewed':
                contract['branches'][0]['value'] = {'order': {'source': contract['branches'][0]['value'], 'keys': [field, 'code']}}
            selection = contract['branches'][0]['value']['order']['source']['select']
            where = selection['where']
            parts = where.get('and', [where])
            # Include a real dependent P(x) even for the original single guard.
            if len(parts) == 1:
                parts.append({'before': [nullable.ref('item', field), nullable.ref('input', 'cutoff')]})
            guards = [p for p in parts if 'present' in p or 'not' in p]
            consumers = [p for p in parts if p not in guards]
            duplicate_sets = [guards] if field != 'window' else [[guards[0]], [guards[1]], guards]
            arrangements = [arrangement for duplicates in duplicate_sets for arrangement in
                            [guards + copy.deepcopy(duplicates) + consumers,
                             guards + consumers + copy.deepcopy(duplicates),
                             consumers + guards + copy.deepcopy(duplicates)]]
            for arrangement in arrangements:
                model = copy.deepcopy(base)
                model['operations'][operation]['branches'][0]['value']['order']['source']['select']['where'] = {'and': copy.deepcopy(arrangement)}
                plans = pipeline.checked(model)
                plan = plans[operation]
                self.assertTrue(any(len(f['justifications']) == 2 for fs in plan.refinement_facts.values() for f in fs))
                with tempfile.TemporaryDirectory() as folder:
                    root = Path(folder)
                    pipeline.generate(model, root)
                    (root / 'state.json').write_bytes(emitter.canonical(nullable.population()))
                    call = nullable.capture(model, root, operation, {'cutoff': nullable.CUTOFF})
                    self.assertTrue(call['verdict']['grounded'])
                    self.assertTrue(call['verdict']['conformant'])

    def test_missing_wrong_field_scope_and_conflict(self):
        row = nullable.application()['state']['sequence']
        p = {'before': [nullable.ref('item', 'embargo'), nullable.lit(nullable.CUTOFF, 'instant')]}
        g = nullable.non_null('embargo')
        for expr in [p, {'and': [nullable.non_null('released'), p]},
                     {'and': [{'not': {'and': [g, nullable.lit(True, 'boolean')]}}, p]},
                     {'and': [g, copy.deepcopy(g['not']), p]}]:
            with self.subTest(expr=expr), self.assertRaises(ValueError):
                types.analyze(expr, {'item': row})
        # Equal targets with different conditions are not refinement providers.
        plan = pipeline.checked(study.application())['v1_early']
        facts = [f for values in plan.refinement_facts.values() for f in values]
        self.assertEqual({f['kind'] for f in facts}, {'presence', 'non_null'})
        self.assertTrue(all(len(f['justifications']) == 2 for f in facts))
        facts[0]['justifications'] = ()
        with self.assertRaisesRegex(ValueError, 'checked facts changed'):
            plan.assert_invariants()


class NullableBinding(unittest.TestCase):
    def test_omitted_null_value_malformed_required_and_collection(self):
        for base, value, malformed in [('integer', '3', 'bad'), ('instant', study.CUTOFF, 'bad'), ('string', 'x', 3)]:
            shape = {'nullable': base}
            field = {'slot': 'x', 'type': shape, 'optional': True, 'domain': None}
            metadata = {'operations': {'run': {'x': field}}}
            for raw in [{}, {'x': None}, {'x': value}, {'x': malformed}]:
                result = binder.bind('run', json.dumps(raw), metadata)
                expected = oracle.expected_binding('run', json.dumps(raw), metadata)
                self.assertEqual(result, expected)
                if not raw:
                    self.assertEqual(result['input'], {})
                elif raw['x'] is None:
                    self.assertEqual(result['input'], {'x': None})
                elif raw['x'] == malformed:
                    self.assertIsNone(result['input'])
            field['optional'] = False
            self.assertEqual(binder.bind('run', '{}', metadata)['failures'][0]['category'], 'missing_required')
            field['type'] = base
            self.assertIsNone(binder.bind('run', '{"x":null}', metadata)['input'])
        route = {'arguments': {'x': {'slot': 'x', 'type': {'sequence': {'nullable': 'integer'}},
                 'optional': False, 'domain': None}}, 'semantic': 'run'}
        result = runtime.bind('run', {'x': [None, '3']}, route)
        self.assertEqual(result['input'], {'x': [None, 3]})
        self.assertIsNone(runtime.bind('run', {'x': [None, 'bad']}, route)['input'])

    def test_binding_faults_A_to_D_independent_oracle(self):
        metadata = {'operations': {'run': {'x': {'slot': 'x', 'type': {'nullable': 'integer'}, 'optional': True, 'domain': None}}}}
        cases = [({'x': None}, {}), ({'x': 'bad'}, {'x': None}), ({'x': '3'}, {'x': None})]
        for raw, faulty in cases:
            self.assertNotEqual(binder.bind('run', json.dumps(faulty), metadata), oracle.expected_binding('run', json.dumps(raw), metadata))
        metadata['operations']['run']['x']['type'] = 'integer'
        unsafe = {'slots': {'x': {'supplied': True, 'state': 'BOUND_TYPED'}}, 'input': {'x': None}, 'failures': []}
        self.assertNotEqual(unsafe, oracle.expected_binding('run', '{"x":null}', metadata))


class WholeBoundary(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = study.study()

    def test_standalone_lifecycle_all_layers_and_invalid_no_write(self):
        for call in [*self.report['calls'], *self.report['invalid_populations'].values()]:
            self.assertNotIn(False, call['verdict'].values(), call)
        first = self.report['calls'][0]
        self.assertIsNone(first['pre'])
        self.assertIsNone(first['post'])
        null = self.report['calls'][2]['evidence']['semantic']['input']
        value = self.report['calls'][3]['evidence']['semantic']['input']
        self.assertEqual(null, {'filter': None})
        self.assertEqual(value, {'filter': 3})
        for call in self.report['invalid_populations'].values():
            self.assertEqual(call['pre'], call['post'])
            self.assertIsNone(call['evidence']['semantic'])
            self.assertEqual(call['evidence']['transport']['category'], 'persistence_invalid_state')

    def test_disposable_faults_A_to_L_fail_independent_conformance(self):
        from benchmark.semantic.boundary_faults_r5_39 import faults
        report = faults()
        self.assertEqual(set(report), set('ABCDEFGHIJKL'))
        for name, call in report.items():
            with self.subTest(fault=name):
                self.assertIn(False, call['verdict'].values(), call)
        for name in 'ABC':
            self.assertFalse(report[name]['verdict']['INPUT_BINDING'])
        for name in 'KL':
            self.assertNotEqual(report[name]['pre'], report[name]['post'])
            self.assertFalse(report[name]['verdict']['STATE/PERSISTENCE'])

    def test_dispatch_faults_E_to_H_static(self):
        app, spec, state, config = study.setup()
        faulty = copy.deepcopy(spec)
        faulty['operations'][0]['alternatives']['V1'] = copy.deepcopy(faulty['operations'][0]['alternatives']['V2'])
        with self.assertRaisesRegex(ValueError, 'codec'):
            boundary.aggregate(app, faulty, state, config, {'application': 'x', 'generation': 'x'})
        faulty = copy.deepcopy(spec)
        faulty['operations'][-1]['alternatives']['V2'] = copy.deepcopy(faulty['operations'][-1]['alternatives']['V1'])
        with self.assertRaisesRegex(ValueError, 'codec'):
            boundary.aggregate(app, faulty, state, config, {'application': 'x', 'generation': 'x'})
        faulty = copy.deepcopy(spec)
        faulty['operations'][-1]['alternatives']['V1']['semantic'] = 'v2_query'
        with self.assertRaises(ValueError):
            boundary.aggregate(app, faulty, state, config, {'application': 'x', 'generation': 'x'})
        faulty = copy.deepcopy(state)
        faulty['alternatives']['V2']['codec'] = faulty['versions']['V1']
        with self.assertRaisesRegex(ValueError, 'codec'):
            boundary.check_state(app, faulty)

    def test_persistence_faults_I_to_L_are_independently_detected(self):
        app, spec, state, config = study.setup()
        data = emitter.canonical({'revision': 2, 'seeds': [{'code': 'a', 'label': 'Iris'}]})
        for faulty in [{'category': None, 'variant': 'V2', 'value': json.loads(data)},
                       {'category': None, 'variant': 'V1', 'value': json.loads(data)},
                       {'category': None, 'variant': 'V2', 'value': {'revision': 2, 'seeds': []}}]:
            self.assertNotEqual((faulty['category'], faulty['variant']), verifier.expected_state(data, state))
        # Mutation/normalization of invalid content is a physical no-write breach.
        call = copy.deepcopy(self.report['invalid_populations']['wrong_pair'])
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            boundary.generate(app, root, spec, state, config)
            verdict = verifier.challenge(app, root, spec, state, config, call['evidence'], call['public'],
                                        call['pre'].encode(), emitter.canonical({'revision': 2, 'seeds': []}))
            self.assertFalse(verdict['LAUNCH'])

    def test_aggregate_faults_M_to_P_and_cross_profiles(self):
        app, spec, state, config = study.setup()
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            profile = boundary.generate(app, root, spec, state, config)
            manifest = profile['artifact']
            for path in [('transport', 'application'), ('launch', 'persistence'), ('trace', 'provenance')]:
                faulty = copy.deepcopy(profile)
                faulty[path[0]][path[1]] = 'wrong'
                with self.assertRaises(ValueError):
                    boundary.check_aggregate(app, spec, state, config, manifest, faulty)
            faulty = copy.deepcopy(state)
            del faulty['alternatives']['V2']
            with self.assertRaises(ValueError):
                boundary.check_state(app, faulty)
            bad_config = copy.deepcopy(config)
            bad_config['provider']['types'] = {'identity.fresh': 'string'}
            with self.assertRaises(ValueError):
                boundary.aggregate(app, spec, state, bad_config, manifest)
            # Runtime also rejects altered linked metadata before trusted execution.
            faulty = copy.deepcopy(profile)
            faulty['trace']['generation'] = 'wrong'
            (root / 'application_boundary.json').write_bytes(emitter.canonical(faulty))
            with self.assertRaises(ValueError):
                launch.runtime.load(root)

    def test_missing_store_and_invalid_json_boundary_policies(self):
        app, spec, state, config = study.setup()
        spec['persistence'] = {'missing': 'REQUIRE_EXISTING', 'initial': None}
        with tempfile.TemporaryDirectory() as bundle, tempfile.TemporaryDirectory() as directory:
            root, cwd = Path(bundle), Path(directory)
            boundary.generate(app, root, spec, state, config)
            call = study.capture(app, root, cwd, spec, state, config, ['query'])
            self.assertNotIn(False, call['verdict'].values(), call)
            self.assertEqual(call['evidence']['transport']['category'], 'persistence_missing')
            self.assertIsNone(call['post'])
            (cwd / config['store']['path']).write_bytes(b'{bad-json')
            call = study.capture(app, root, cwd, spec, state, config, ['query'])
            self.assertNotIn(False, call['verdict'].values(), call)
            self.assertEqual(call['evidence']['transport']['category'], 'persistence_invalid_json')
            self.assertEqual(call['pre'], call['post'])

    def test_prediction_ready_and_complete_deliberate_gap_set(self):
        legacy_app, legacy_spec, legacy_state, legacy_config = nullable.setup()
        legacy = readiness.inspect(legacy_app, legacy_spec, legacy_state, legacy_config)
        self.assertEqual(legacy['status'], 'READY', legacy['gaps'])
        app, spec, state, config = study.setup()
        with patch.object(pipeline, 'generate', side_effect=AssertionError('static emission')):
            ready = readiness.inspect(app, spec, state, config)
        self.assertEqual(ready['status'], 'READY', ready['gaps'])
        broken = copy.deepcopy(spec)
        broken['operations'][0]['alternatives']['V1']['semantic'] = 'absent'
        broken['operations'][1]['alternatives']['V2']['arguments'] = []
        state = copy.deepcopy(state)
        del state['alternatives']['V2']
        config['store']['path'] = '../wrong'
        result = readiness.inspect(app, broken, state, config)
        self.assertEqual(result['status'], 'NOT_READY')
        self.assertTrue({'transport', 'binding', 'state', 'launch', 'application_profile'} <= {g['stage'] for g in result['gaps']})
        self.assertFalse(result['generated'])

    def test_exact_matrix_retained_and_redundancy_dimension(self):
        matrix = readiness.closure_matrix()
        self.assertEqual(matrix['base_rows'], 84)
        self.assertEqual(len(matrix['rows']), 336)
        from benchmark.semantic.readiness_r5_38 import closure_matrix
        original = closure_matrix()['rows']
        self.assertEqual([row['status'] for row in matrix['rows'] if row['provider_dimension'] == 'one_provider'],
                         [row['status'] for row in original])
        self.assertEqual([row['status'] for row in matrix['rows'] if row['provider_dimension'] == 'duplicate_equivalent'],
                         [row['status'] for row in original])


if __name__ == '__main__':
    unittest.main()
