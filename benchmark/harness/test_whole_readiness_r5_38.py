"""Complete contract prediction, all-gap enumeration, static-only and matrix checks."""

import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from benchmark.semantic import nullable_study_r5_38 as study
from benchmark.semantic import readiness_r5_38 as readiness
from benchmark.semantic import checked_launch_r5_36 as launch
from benchmark.semantic import current_pipeline as pipeline
from benchmark.semantic import refined_generator_r5_28 as emitter


class WholeReadiness(unittest.TestCase):
    def test_complete_non_task_static_prediction_then_public_execution(self):
        model, spec, declaration, config = study.setup()
        with (patch.object(pipeline, 'generate', side_effect=AssertionError('static analysis generated')),
              patch.object(emitter, 'generated_unit', side_effect=AssertionError('static analysis rendered'))):
            result = readiness.inspect(model, spec, declaration, config)
        self.assertEqual(result['status'], 'READY', result['gaps'])
        self.assertEqual(len(result['operations']), 8)
        with tempfile.TemporaryDirectory() as bundle, tempfile.TemporaryDirectory() as folder:
            root, cwd = Path(bundle), Path(folder)
            launch.generate(model, root, spec, declaration, config)
            state = cwd / config['store']['path']
            state.write_bytes(emitter.canonical(study.population()))
            for operation in ('earlier', 'ordered', 'reviewed', 'window', 'replace', 'earlier', 'remove'):
                evidence, public, before, after = launch.observe(root, cwd, config, [operation, '--cutoff', study.CUTOFF])
                verdict = launch.challenge(model, root, spec, declaration, config, evidence, public, before, after)
                with self.subTest(operation=operation):
                    self.assertTrue(all(verdict.values()), verdict)
                    self.assertEqual(before == after, operation not in ('replace', 'remove'))

    def test_semantically_safe_nested_selection_is_unsupported_before_generation(self):
        model = study.application()
        order = model['operations']['ordered']['branches'][0]['value']['order']
        order['source'] = {'select': {'source': order['source'], 'where': study.lit(True, 'boolean')}}
        # Both selections exclude no additional records; the nullable field is
        # non-null in every ordered member. Current population-fact propagation
        # is bounded to a direct selection, so this valid composition is a gap.
        with patch.object(pipeline, 'generate', side_effect=AssertionError('generation forbidden')):
            result = readiness.inspect(model)
        self.assertEqual(result['semantic_status'], 'NOT_READY')
        self.assertTrue(any('non-orderable' in g['reason'] for g in result['gaps']))

    def test_all_operations_and_boundary_gaps_collected(self):
        model, spec, declaration, config = study.setup()
        model['operations']['earlier']['branches'][0]['value']['select']['where'] = {
            'before': [study.ref('item', 'embargo'), study.ref('input', 'cutoff')]}
        model['operations']['ordered']['branches'][0]['value']['order']['source'] = study.ref('pre')
        config['store']['path'] = '../outside.json'
        result = readiness.inspect(model, spec, declaration, config, [
            {'kind': 'public_state_alternatives'}, {'kind': 'durable_content_constraints'}])
        text = json.dumps(result['gaps'])
        for needle in ('before requires', 'non-orderable', 'state-shape alternatives', 'population/content'):
            self.assertIn(needle, text)
        self.assertEqual(result['status'], 'NOT_READY')
        self.assertFalse(result['generated'])

    def test_exact_fact_and_stage_reporting(self):
        model, spec, declaration, config = study.setup()
        result = readiness.inspect(model, spec, declaration, config)
        facts = result['operations']['earlier']['facts']
        refined = [f for f in facts if f['kind'] == 'ref' and f['declared'] == {'nullable': 'instant'} and f['effective'] == 'instant']
        self.assertTrue(refined)
        self.assertTrue(all(f['refinement_identity'] for f in refined))
        self.assertTrue(all(f['nullability_domain'] == 'nullable' for f in refined))
        self.assertTrue(all(f['presence_domain'] == 'required' for f in refined))
        self.assertEqual(set(result['operations']['earlier']['stages']), set(readiness.STAGES))

    def test_domain_matrix_all_domains_and_separate_prerequisites(self):
        matrix = readiness.closure_matrix()
        self.assertEqual(len(matrix['rows']), 84)
        for base in ('string', 'integer', 'instant'):
            rows = [r for r in matrix['rows'] if r['base'] == base and r['relation'] == 'equality']
            self.assertEqual([r['required_facts'] for r in rows], [[], ['presence'], ['non_null'], ['presence', 'non_null']])
            self.assertTrue(all(r['status'] == 'SUPPORTED' for r in rows))
        for row in matrix['rows']:
            if row['relation'] == 'before':
                self.assertEqual(row['status'] == 'SUPPORTED', row['base'] == 'instant')
            if row['relation'] == 'fallback':
                self.assertEqual(row['status'] == 'SUPPORTED', row['domain'] in ('optional', 'optional_nullable'))
        recorded = Path('benchmark/results/phase5c/R5_38-domain-refinement-matrix.json')
        if recorded.exists():
            self.assertEqual(json.loads(recorded.read_bytes()), json.loads(emitter.canonical(matrix)))

    def test_every_supported_matrix_combination_transfers_current_pipeline(self):
        report = readiness.validate_matrix_pipeline()
        self.assertEqual(len(report), 84)
        self.assertFalse(any(r['status'] == 'FAILED' for r in report), report)


if __name__ == '__main__':
    unittest.main()
