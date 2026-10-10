"""Identity, admission, serialization and leakage controls; no acceptance executions."""
import copy
import unittest
import sys
import convert as c
from jsonschema import Draft202012Validator


class ConversionTests(unittest.TestCase):
    def setUp(self):
        self.entry = c.read(c.OLD / 'DATASET-INDEX.json')['entries'][0]

    def test_exact_cohort_and_schema(self):
        records, assessment = c.build()
        self.assertEqual((len(records), assessment['genuine_tool_records']), (10, 0))
        schema = c.read(c.OUT / 'training-record-1.schema.json')
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema)
        for record in records:
            validator.validate(record)
            target = c.verified(self.entry['direct']['SYMBOLIC.json']) if record['episode_id'] == self.entry['episode_id'] else None
            if target:
                self.assertEqual(c.strict(record['completion'][0]['content']), target)
        self.assertEqual(len(assessment['excluded']), 10)

    def test_every_gate_rejects(self):
        for gate in c.GATES:
            for value in (False, 1, 'true', None):
                entry = copy.deepcopy(self.entry)
                entry['admission_gates'][gate] = value
                with self.assertRaises(ValueError):
                    c.convert_entry(entry)

    def test_missing_gate_and_source(self):
        for field in ('SOURCE.json', 'FRC.json', 'ACCEPTANCE.json', 'VALIDATION.json', 'SYMBOLIC.json'):
            entry = copy.deepcopy(self.entry)
            del entry['direct'][field]
            with self.assertRaises(ValueError):
                c.convert_entry(entry)
        entry = copy.deepcopy(self.entry)
        entry['admission_gates'].pop(next(iter(c.GATES)))
        with self.assertRaises(ValueError):
            c.convert_entry(entry)

    def test_wrong_identity_and_traversal(self):
        entry = copy.deepcopy(self.entry)
        entry['direct']['SOURCE.json']['sha256'] = '0' * 64
        with self.assertRaises(ValueError):
            c.convert_entry(entry)
        with self.assertRaises(ValueError):
            c.verified({'path': '../outside.json', 'sha256': '0' * 64})

    def test_exposed_family_and_component_cannot_split(self):
        records, _ = c.build()
        for record in records:
            with self.assertRaises(ValueError):
                c.partition_guard(records, {record['episode_id']: 'evaluation'})
        entry = copy.deepcopy(self.entry)
        entry['partition'] = 'evaluation'
        with self.assertRaises(ValueError):
            c.convert_entry(entry)

    def test_scripted_or_file_edit_is_not_semantic_decision(self):
        entries = c.read(c.OLD / 'DATASET-INDEX.json')['entries']
        for entry in entries:
            with self.assertRaisesRegex(ValueError, 'NO_OBSERVED'):
                c.tool_record(entry)
        entry = copy.deepcopy(self.entry)
        entry['actual_semantic_tool_trajectory'] = {'fabricated': True}
        with self.assertRaisesRegex(ValueError, 'UNQUALIFIED'):
            c.tool_record(entry)

    def test_strict_json(self):
        for value in ('{"x":1,"x":2}', '{"x":NaN}', '{"x":Infinity}', '{'):
            with self.assertRaises(ValueError):
                c.strict(value)

    def test_target_schemas_and_unchanged_symbolic_validation(self):
        sys.path.insert(0, str(c.ROOT / 'experiments/typed_composition_r6_18'))
        import composition
        records, _ = c.build()
        state_schema = c.read(c.ROOT / 'experiments/value_added_r6_16/intent-2.schema.json')
        for record in records:
            text = record['completion'][0]['content']
            if record['component'] == 'STATELESS_READ_CHECK_ENCODE':
                composition.validate(composition.load(text))
            else:
                Draft202012Validator(state_schema).validate(c.strict(text))
        # B gets only schema/rejection checks; there is no positive observed instance.
        schema = c.read(c.OUT / 'tool-decision-1.schema.json')
        Draft202012Validator.check_schema(schema)
        self.assertFalse(Draft202012Validator(schema).is_valid({}))


if __name__ == '__main__':
    unittest.main()
