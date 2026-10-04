"""Actual public-only processes, independent endpoints and checked launch faults."""

import copy
import json
from pathlib import Path
import tempfile
import unittest

from benchmark.semantic import checked_launch_r5_36 as launch
from benchmark.semantic import launch_runtime_r5_36 as runtime
from benchmark.semantic import launch_study_r5_36 as study
from benchmark.semantic.refined_generator_r5_28 import canonical, sha


class PublicLaunchR536(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = study.study()

    def assert_layers(self, call):
        self.assertIs(call['verdict']['LAUNCH_PROFILE_CONFORMANT'], True, call)
        self.assertIs(call['verdict']['launch_grounded'], True, call)
        for key, value in call['verdict'].items():
            self.assertIn(value, (True, None), (key, call))
        self.assertIs(call['verdict']['OUTPUT_CONFORMANT'], True)
        self.assertIs(call['verdict']['SEMANTIC_EXECUTION_CONFORMANT'],
                      True if call['evidence']['semantic'] else None)

    def test_public_only_two_applications_and_layered_results(self):
        for app in ('A', 'B'):
            for call in self.report[app]['calls']:
                self.assert_layers(call)
                command = call['public']['command']
                self.assertEqual(command[3:], call['public']['argv'])
                self.assertEqual(Path(command[2]).name, 'launch_runtime_r5_36.py')
                self.assertNotIn('state.json', command)
        calls = self.report['A']['calls']
        self.assertEqual(calls[1]['evidence']['semantic']['outcome']['value']['channels'], ['left'])
        self.assertEqual(calls[1]['evidence']['transport']['binding']['input']['channels'], [' left ', 'left'])
        self.assertIsNone(calls[-1]['evidence']['semantic'])
        self.assertTrue(calls[3]['evidence']['semantic']['externals']['fresh_unique_id'])

    def test_cross_shape_lifecycle_and_durable_continuity(self):
        calls = self.report['B']['calls']
        for before, after in zip(calls, calls[1:]):
            self.assertEqual(before['post_bytes'], after['pre_bytes'])
        self.assertIsNone(calls[0]['pre_bytes'])
        self.assertIsNone(calls[0]['post_bytes'])
        self.assertEqual(json.loads(calls[1]['post_bytes'])['revision'], 1)
        self.assertEqual(json.loads(calls[3]['post_bytes'])['revision'], 2)
        self.assertIsNone(calls[-1]['evidence']['semantic'])

    def test_missing_store_policies(self):
        for name in ('require_existing', 'initialize_read'):
            call = self.report['paths'][name]
            self.assert_layers(call)
            self.assertIsNone(call['pre_bytes'])
            self.assertIsNone(call['post_bytes'])
        self.assertIsNone(self.report['paths']['require_existing']['evidence']['semantic'])
        self.assertEqual(self.report['paths']['require_existing']['public']['exit'], 1)
        self.assertIsNotNone(self.report['paths']['initialize_read']['evidence']['semantic'])

    def test_changed_cwd_uses_same_bundle_with_independent_stores(self):
        for app in ('A', 'B'):
            first = self.report[app]['calls'][0]
            second = self.report[app]['changed_cwd']
            self.assert_layers(second)
            self.assertEqual(first['public']['command'], second['public']['command'])
            self.assertNotEqual(first['public']['cwd'], second['public']['cwd'])
            self.assertNotEqual(first['evidence']['store'], second['evidence']['store'])
            self.assertNotEqual(first['evidence']['trace_directory'], second['evidence']['trace_directory'])
            self.assertEqual(first['evidence']['launch'], second['evidence']['launch'])
            self.assertIsNone(second['pre_bytes'])

    def test_nested_paths_and_defined_missing_directory_failure(self):
        self.assert_layers(self.report['paths']['nested'])
        self.assertIsNotNone(self.report['paths']['nested']['post_bytes'])
        for name in ('missing_parent', 'trace_require_missing'):
            call = self.report['paths'][name]
            self.assertEqual(call['public']['exit'], 4)
            self.assertIn('LAUNCH_FAILURE', call['public']['stderr'])
            self.assertIsNone(call['evidence'])
            self.assertIsNone(call['post_bytes'])

    def test_six_fault_matrix(self):
        faults = self.report['faults']
        for name in ('A', 'E'):
            self.assertFalse(faults[name]['verdict']['LAUNCH_PROFILE_CONFORMANT'])
            self.assertEqual(faults[name]['public']['exit'], 4)
            self.assertIsNone(faults[name]['evidence'])
            self.assertIsNone(faults[name]['post_bytes'])
        self.assertFalse(faults['B']['verdict']['launch_grounded'])
        self.assertTrue(faults['B']['unexpected_store_exists'])
        self.assertIsNone(faults['B']['post_bytes'])
        self.assertFalse(faults['C']['verdict']['launch_grounded'])
        self.assertIsNotNone(faults['C']['evidence']['semantic'])
        self.assertFalse(faults['D']['verdict']['launch_grounded'])
        self.assertEqual(faults['D']['public']['exit'], 4)
        self.assertIn('hidden research helper', faults['D']['public']['stderr'])
        self.assertFalse(faults['F']['verdict']['launch_grounded'])
        self.assertEqual(faults['F']['evidence']['argv'], [])
        self.assertIsNone(faults['F']['evidence']['semantic'])

    def test_metadata_only_mutations_keep_algorithm_and_semantics_identical(self):
        mutations = self.report['mutations']
        self.assertEqual(len({c['launcher_digest'] for c in mutations.values()}), 1)
        self.assertTrue(all(c['artifact_digest'] == c['original_artifact_digest'] for c in mutations.values()))
        for name in ('store', 'trace', 'profile_id', 'controlled_provider'):
            self.assert_layers(mutations[name])
        for name in ('persistence_reference', 'transport_reference'):
            self.assertEqual(mutations[name]['public']['exit'], 4)
            self.assertFalse(mutations[name]['verdict']['LAUNCH_PROFILE_CONFORMANT'])
        self.assertTrue(mutations['store']['evidence']['store'].endswith('alternate-register.json'))
        self.assertIsNotNone(mutations['store']['post_bytes'])
        self.assertTrue(mutations['trace']['evidence']['trace_directory'].endswith('alternate-evidence'))
        self.assertEqual(mutations['controlled_provider']['evidence']['semantic']['externals'], {
            'fresh_unique_id': 'controlled-acoustic', 'utc_clock': '2031-02-03T04:05:06Z'})

    def test_environment_cannot_override_declared_provider_or_paths(self):
        call = self.report['paths']['environment_isolation']
        self.assert_layers(call)
        self.assertNotEqual(call['evidence']['semantic']['externals']['fresh_unique_id'], 'ambient-intrusion')
        self.assertNotEqual(call['evidence']['semantic']['externals']['utc_clock'], '1900-01-01T00:00:00Z')
        self.assertTrue(call['evidence']['store'].endswith('register.json'))

    def test_invalid_path_forms_reject_before_process(self):
        for text in ('/absolute.json', 'C:/absolute.json', '../escape.json', 'nested/../escape',
                     './file', 'nested//file', 'nested\\file', '', 'a\x00b', 'trailing.', 'tail /file'):
            with self.subTest(text=text), self.assertRaises(ValueError):
                runtime.path_rule({'base': 'cwd', 'path': text, 'parent': 'require_existing'})
        runtime.path_rule({'base': 'cwd', 'path': 'nested/normal file.json', 'parent': 'require_existing'})

    def test_incompatible_launch_metadata_rejects(self):
        model, spec, state, config = study.setup_a()
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            launch.generate(model, root, spec, state, config)
            boundary = json.loads((root / 'transport.json').read_bytes())
            manifest = json.loads((root / 'provenance.json').read_bytes())
            profile = json.loads((root / 'launch.json').read_bytes())
            changes = {
                'application': lambda p: p.__setitem__('application', 'stale'),
                'generation': lambda p: p.__setitem__('generation', 'stale'),
                'provenance': lambda p: p.__setitem__('provenance', 'stale'),
                'transport': lambda p: p.__setitem__('transport', 'stale'),
                'persistence': lambda p: p.__setitem__('persistence', 'stale'),
                'capabilities': lambda p: p.__setitem__('capabilities', 'stale'),
                'runtime': lambda p: p.__setitem__('runtime', 'foreign'),
                'trace': lambda p: p['trace'].__setitem__('mode', 'disabled'),
                'overlap': lambda p: p['trace']['directory'].__setitem__('path', 'register.json'),
                'store_create': lambda p: p['store'].__setitem__('parent', 'create'),
                'provider_missing': lambda p: p['provider']['types'].pop('utc_clock'),
                'provider_unknown': lambda p: p['provider'].__setitem__('mode', 'arbitrary_plugin'),
                'production_values': lambda p: p['provider'].__setitem__('values', {'utc_clock': '2031-01-01T00:00:00Z'}),
                'controlled_missing': lambda p: p['provider'].__setitem__('mode', 'controlled_test'),
                'unknown_key': lambda p: p.__setitem__('semantic_default', []),
            }
            for name, change in changes.items():
                changed = copy.deepcopy(profile)
                change(changed)
                with self.subTest(name=name), self.assertRaises(ValueError):
                    runtime.validate(changed, boundary, manifest, launch.requirements(model))

    def test_stale_artifacts_and_provider_profile_seals(self):
        for filename in ('operation.py', 'transport.json', 'capabilities.json', 'launch_runtime_r5_36.py', 'launch.json'):
            with self.subTest(filename=filename), tempfile.TemporaryDirectory() as bundle, tempfile.TemporaryDirectory() as folder:
                root, cwd = Path(bundle), Path(folder)
                model, spec, state, config = study.setup_b()
                launch.generate(model, root, spec, state, config)
                path = root / filename
                path.write_bytes(path.read_bytes() + (b'\n# changed' if filename.endswith('.py') else b' '))
                call = study.capture(model, root, cwd, spec, state, config, ['legacy_insert'])
                self.assertEqual(call['public']['exit'], 4)
                self.assertIsNone(call['evidence'])
                self.assertIsNone(call['post_bytes'])

    def test_independent_grounding_refuses_replayed_or_cross_profile_evidence(self):
        model, spec, state, config = study.setup_b()
        with tempfile.TemporaryDirectory() as bundle, tempfile.TemporaryDirectory() as folder:
            root, cwd = Path(bundle), Path(folder)
            launch.generate(model, root, spec, state, config)
            evidence, public, before, after = launch.observe(root, cwd, config, ['legacy'])
            for key in ('application', 'launch', 'generation', 'provenance', 'invocation', 'pid', 'store', 'argv'):
                altered = copy.deepcopy(evidence)
                altered[key] = 'foreign'
                verdict = launch.challenge(model, root, spec, state, config, altered, public, before, after)
                self.assertFalse(verdict['launch_grounded'], key)
            altered = copy.deepcopy(evidence)
            altered['semantic']['invocation'] = 'other.invocation'
            verdict = launch.challenge(model, root, spec, state, config, altered, public, before, after)
            self.assertTrue(verdict['launch_grounded'])
            self.assertFalse(verdict['SEMANTIC_EXECUTION_CONFORMANT'])

    def test_public_argument_resembling_bootstrap_flag_stays_public(self):
        model, spec, state, config = study.setup_a()
        spec['operations'][0]['arguments'][0]['public'] = 'launch-profile'
        with tempfile.TemporaryDirectory() as bundle, tempfile.TemporaryDirectory() as folder:
            root, cwd = Path(bundle), Path(folder)
            launch.generate(model, root, spec, state, config)
            call = study.capture(model, root, cwd, spec, state, config, ['calibrate', '--launch-profile', 'microphone'])
            self.assert_layers(call)
            self.assertEqual(call['evidence']['semantic']['input']['channels'], ['microphone'])

    def test_capability_readiness_matrix(self):
        matrix = json.loads(Path('benchmark/results/phase5c/R5_36-readiness-matrix.json').read_bytes())
        self.assertEqual(matrix['candidate_core_constructs'], 30)
        self.assertEqual(matrix['entry_point'], 'benchmark.semantic.current_pipeline')
        required = {'semantic expressiveness', 'general lowering', 'relation composition', 'ordering', 'optional refinement',
            'single semantic authority', 'input suppliedness', 'malformed-input boundary', 'cross-shape state evolution',
            'checked transport', 'repeated collection arguments', 'output envelope/stream mapping', 'missing-store policy',
            'standalone public launch', 'cwd-relative persistence', 'trace bootstrap'}
        self.assertEqual(set(matrix['readiness']), required)
        for row in matrix['readiness'].values():
            self.assertIn(row['classification'], ('RESOLVED_INDEPENDENTLY', 'PROFILE_CONFIGURATION_ONLY'))
            self.assertTrue(row['evidence'])
            self.assertTrue(row['limits'])
        self.assertEqual(matrix['benchmark_critical_blockers'], [])


if __name__ == '__main__':
    unittest.main()
