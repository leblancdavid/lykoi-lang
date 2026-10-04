"""Scoped nullable elimination, independent grounded execution and confusion negatives."""

import copy
import itertools
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from benchmark.semantic import nullable_study_r5_38 as study
from benchmark.semantic import current_pipeline as pipeline
from benchmark.semantic import unified_types_r5_27 as types
from benchmark.semantic import refined_generator_r5_28 as emitter
from benchmark.semantic import refined_evidence_r5_28 as verifier


class NullableCoherence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = study.study()

    def test_read_order_write_cross_type_grounded(self):
        for name, call in self.report['calls'].items():
            with self.subTest(operation=name):
                self.assertEqual(call['verdict'], {'provenance_valid': True, 'grounded': True, 'conformant': True})
                self.assertEqual(call['pre'] == call['post'], name not in ('replace', 'remove'))
        def codes(name):
            return [r['code'] for r in self.report['calls'][name]['event']['outcome']['value']]
        self.assertEqual(codes('earlier'), ['b', 'a'])
        self.assertEqual(codes('ordered'), ['a', 'b', 'equal', 'later'])
        self.assertEqual(codes('window'), ['a', 'b'])
        self.assertEqual(codes('caption'), ['b', 'a', 'equal', 'later'])
        self.assertEqual(codes('rating'), ['b', 'a', 'equal', 'later'])
        changed = json.loads(self.report['calls']['replace']['post'])
        self.assertEqual(next(r for r in changed if r['code'] == 'a')['label'], 'released')
        self.assertTrue(all(r['note'] == 'preserved' for r in changed))
        self.assertNotIn('a', codes('remove'))

    def test_faults_ground_but_fail_semantics(self):
        for name, call in self.report['faults'].items():
            with self.subTest(fault=name):
                self.assertEqual(call['verdict'], {'provenance_valid': True, 'grounded': True, 'conformant': False})

    def test_semantic_only_mutations(self):
        for name, call in self.report['mutations'].items():
            with self.subTest(mutation=name):
                self.assertTrue(call['verdict']['grounded'])
                self.assertTrue(call['verdict']['conformant'])
        self.assertEqual(len(self.report['mutations']['cutoff']['event']['outcome']['value']), 3)
        self.assertEqual(self.report['mutations']['field']['event']['outcome']['value'], [])
        self.assertEqual([r['code'] for r in self.report['mutations']['secondary']['event']['outcome']['value']],
                         ['b', 'a', 'equal', 'later'])
        self.assertEqual([r['code'] for r in self.report['mutations']['relation']['event']['outcome']['value']], ['later'])

    def test_all_conjunction_orders_and_combined_domain(self):
        original = study.application()
        parts = original['operations']['window']['branches'][0]['value']['order']['source']['select']['where']['and']
        for permutation in itertools.permutations(parts):
            model = study.application()
            model['operations']['window']['branches'][0]['value']['order']['source']['select']['where']['and'] = copy.deepcopy(list(permutation))
            with tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                pipeline.generate(model, root)
                (root / 'state.json').write_bytes(emitter.canonical(study.population()))
                call = study.capture(model, root, 'window', {'cutoff': study.CUTOFF})
                self.assertTrue(call['verdict']['conformant'])
                self.assertEqual([r['code'] for r in call['event']['outcome']['value']], ['a', 'b'])

    def test_unsafe_wrong_field_wrong_record_and_scope_rejected(self):
        row = study.application()['state']['sequence']
        slots = {'item': row, 'other': row, 'input': {'record': {'cutoff': 'instant'}}}
        before = {'before': [study.ref('item', 'embargo'), study.ref('input', 'cutoff')]}
        for expression in [before, {'and': [study.non_null('released'), before]},
                {'and': [study.non_null('embargo', slot='other'), before]},
                {'and': [{'not': {'and': [study.non_null('embargo'), study.lit(True, 'boolean')]}}, before]},
                {'and': [{'equals': [study.lit(1, 'integer'), study.lit(1, 'integer')]}, before]}]:
            with self.subTest(expression=expression), self.assertRaises(ValueError):
                types.analyze(expression, slots)
        model = study.application()
        model['operations']['ordered']['branches'][0]['value']['order']['source'] = study.ref('pre')
        with self.assertRaisesRegex(ValueError, 'non-orderable'):
            pipeline.checked(model)
        # One alternative's guard cannot refine another payload or post-state.
        model = study.application()
        model['operations']['earlier']['branches'][0]['value']['select']['where'] = before
        model['operations']['earlier']['branches'][0]['when'] = {'equals': [study.lit(True, 'boolean'), study.lit(True, 'boolean')]}
        with self.assertRaisesRegex(ValueError, 'before requires'):
            pipeline.checked(model)
        with self.assertRaises(ValueError):
            types.analyze({'and': [study.non_null('embargo', slot='pre'),
                {'before': [study.ref('post', 'embargo'), study.lit(study.CUTOFF, 'instant')]}]}, {'pre': row, 'post': row})

    def test_presence_and_non_null_are_separate_permanent_regression(self):
        row = study.application()['state']['sequence']
        slots = {'item': row}
        def before(field):
            return {'before': [study.ref('item', field), study.lit(study.CUTOFF, 'instant')]}
        # Required nullable has no optional-membership witness at all.
        with self.assertRaisesRegex(ValueError, 'presence requires optional'):
            types.analyze({'and': [{'present': study.ref('item', 'embargo')}, before('embargo')]}, slots)
        for guard in ({'present': study.ref('item', 'window')}, study.non_null('window')):
            with self.subTest(guard=guard), self.assertRaises(ValueError):
                types.analyze({'and': [guard, before('window')]}, slots)
        self.assertEqual(types.analyze({'and': [{'present': study.ref('item', 'reviewed')}, before('reviewed')]}, slots), 'boolean')
        with self.assertRaises(ValueError):
            types.analyze({'and': [study.non_null('reviewed'), before('reviewed')]}, slots)

    def test_checked_facts_seal_stable_identity_and_downstream_authority(self):
        model = study.application()
        contract = model['operations']['earlier']
        plan = types.checked_plan(contract)
        before = contract['branches'][0]['value']['select']['where']['and'][0]['before'][0]
        fact = plan.facts[id(before)]
        self.assertEqual(fact['declared'], {'nullable': 'instant'})
        self.assertEqual(fact['effective'], 'instant')
        self.assertEqual(fact['non_null'], 'established')
        self.assertEqual(fact['presence'], 'declared')
        self.assertTrue(fact['refinement'])
        clone = copy.deepcopy(contract)
        copied = types.checked_plan(clone)
        operand = clone['branches'][0]['value']['select']['where']['and'][0]['before'][0]
        self.assertEqual(fact['identity'], copied.facts[id(operand)]['identity'])
        with (patch.object(types, 'analyze', side_effect=AssertionError('reanalysis')),
              patch.object(emitter, '_compile', side_effect=AssertionError('alternate authority')),
              patch.object(verifier, '_compile', side_effect=AssertionError('alternate authority'))):
            emitter.generated_unit(contract, plan)
            value = types.interpret(contract['branches'][0]['value'],
                {'pre': study.population(), 'input': {'cutoff': study.CUTOFF}}, plan.slots, plan)
            self.assertEqual([r['code'] for r in value], ['b', 'a'])
        fact['effective'] = 'string'
        with self.assertRaisesRegex(ValueError, 'checked facts changed'):
            plan.assert_invariants()


if __name__ == '__main__':
    unittest.main()
