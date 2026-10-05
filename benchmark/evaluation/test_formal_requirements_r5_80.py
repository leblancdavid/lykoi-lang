"""Public/synthetic mechanical claims; no broad discovery or held-out reads."""
import copy
import json
import itertools
from pathlib import Path
import re
import unittest
from unittest.mock import patch

from benchmark.evaluation import benchmark_documents_v1 as v1
from benchmark.evaluation import formal_requirements_r5_80 as f
from benchmark.results.phase5c.r5_80 import fixtures

HERE = fixtures.HERE


def schema_accepts(value, schema, root=None):
    """Test-only evaluator for the keyword subset used by the experimental schema.

    No claim of a general JSON Schema implementation. Runtime has extra checks.
    """
    root = root or schema
    if '$ref' in schema:
        target = root
        for key in schema['$ref'][2:].split('/'):
            target = target[key]
        if not schema_accepts(value, target, root):
            return False
    types = {'object': dict, 'array': list, 'string': str, 'integer': int,
             'number': (int, float), 'boolean': bool, 'null': type(None)}
    if 'type' in schema:
        expected = types[schema['type']]
        if type(value) not in (expected if type(expected) is tuple else (expected,)):
            return False
    if 'const' in schema and (value != schema['const'] or type(value) is not type(schema['const'])):
        return False
    if 'enum' in schema and value not in schema['enum']:
        return False
    if 'minimum' in schema and value < schema['minimum']:
        return False
    if type(value) is str:
        if len(value) < schema.get('minLength', 0) or len(value) > schema.get('maxLength', float('inf')):
            return False
        if 'pattern' in schema and re.search(schema['pattern'], value) is None:
            return False
    if type(value) is dict:
        if any(k not in value for k in schema.get('required', [])):
            return False
        props = schema.get('properties', {})
        for key, child in value.items():
            if not schema_accepts(key, schema.get('propertyNames', {}), root):
                return False
            if key in props:
                if not schema_accepts(child, props[key], root):
                    return False
            else:
                extra = schema.get('additionalProperties', True)
                if extra is False or (type(extra) is dict and not schema_accepts(child, extra, root)):
                    return False
    if type(value) is list:
        if len(value) < schema.get('minItems', 0) or len(value) > schema.get('maxItems', float('inf')):
            return False
        if schema.get('uniqueItems') and len({f.canonical(x) for x in value}) != len(value):
            return False
        if any(not schema_accepts(x, schema.get('items', {}), root) for x in value):
            return False
    if any(not schema_accepts(value, part, root) for part in schema.get('allOf', [])):
        return False
    if 'anyOf' in schema and not any(schema_accepts(value, part, root) for part in schema['anyOf']):
        return False
    if 'if' in schema:
        branch = 'then' if schema_accepts(value, schema['if'], root) else 'else'
        if not schema_accepts(value, schema.get(branch, {}), root):
            return False
    return True


class FormalRequirementQualification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.candidates = json.loads((HERE / 'candidates.json').read_text(encoding='utf-8'))
        cls.reviews = json.loads((HERE / 'reviews.json').read_text(encoding='utf-8'))['receipts']

    def error(self, code, function, *args):
        with self.assertRaises(f.ContractError) as caught:
            function(*args)
        self.assertEqual(caught.exception.record(), {'code': code})

    def test_materialized_candidates_reproduce(self):
        rebuilt = fixtures.candidates()
        rebuilt.update(fixtures.adversarial(rebuilt))
        self.assertEqual(rebuilt, self.candidates)

    def test_all_records_schema_runtime_and_review_bindings(self):
        schema = json.loads((fixtures.ROOT / 'schema/formal-requirement-contract-v0.1.schema.json').read_text(encoding='utf-8'))
        self.assertEqual(schema['properties']['schema_version']['const'], f.VERSION)
        self.assertEqual(schema['$defs']['relation']['properties']['kind']['enum'], list(f.KINDS))
        self.assertEqual(set(self.candidates), set(self.reviews))
        for key, candidate in self.candidates.items():
            with self.subTest(key=key):
                self.assertTrue(schema_accepts(candidate, schema))
                self.assertEqual(f.validate(candidate), self.reviews[key]['contract_commitment'])
                self.assertEqual(f.review_gate(candidate, self.reviews[key]), self.reviews[key]['outcome'])

    def test_closed_shapes_quotes_commitments_and_json(self):
        c = copy.deepcopy(self.candidates['S10'])
        for mutation, code in (
                (lambda x: x.update(extra=True), 'MALFORMED_FRC'),
                (lambda x: x.update(schema_version='other'), 'UNSUPPORTED_FRC_VERSION'),
                (lambda x: x['source'].update(text='different'), 'SOURCE_COMMITMENT_MISMATCH'),
                (lambda x: x['obligations'][0].update(source_quote='not in source'), 'UNBOUND_SOURCE_QUOTE'),
                (lambda x: x['obligations'][0]['relation'].update(kind='unknown'), 'UNKNOWN_RELATION'),
                (lambda x: x['obligations'][0]['relation']['parameters'].update(value=float('nan')), 'NON_JSON_VALUE'),
                (lambda x: x['obligations'][0]['relation']['parameters'].update(value=(1, 2)), 'NON_JSON_VALUE'),
                (lambda x: x['obligations'][0]['relation']['parameters'].update({1: 'bad key'}), 'NON_JSON_VALUE'),
                (lambda x: x.update(revision=True), 'MALFORMED_FRC')):
            mutated = copy.deepcopy(c)
            mutation(mutated)
            self.error(code, f.validate, mutated)

    def test_derivation_ids_and_cycles(self):
        c = copy.deepcopy(self.candidates['B01'])
        c['obligations'].append(copy.deepcopy(c['obligations'][0]))
        self.error('DUPLICATE_OBLIGATION', f.validate, c)
        c = copy.deepcopy(self.candidates['B01'])
        c['obligations'][5]['derived_from'] = ['missing']
        self.error('UNBOUND_DERIVATION', f.validate, c)
        c['obligations'][5]['derived_from'] = [c['obligations'][5]['id']]
        self.error('CYCLIC_DERIVATION', f.validate, c)

    def test_draft_is_not_approval(self):
        c, receipt = self.candidates['S10'], copy.deepcopy(self.reviews['S10'])
        receipt['reviewer'] = c['formalizer']
        self.error('NONINDEPENDENT_REVIEW', f.review_gate, c, receipt)
        receipt = copy.deepcopy(self.reviews['S10'])
        del receipt['checks']['fidelity']
        self.error('INCOMPLETE_REVIEW', f.review_gate, c, receipt)
        receipt = copy.deepcopy(self.reviews['S10'])
        receipt['checks']['no_invention'] = False
        self.error('FAILED_APPROVAL_CHECK', f.review_gate, c, receipt)
        c = copy.deepcopy(c)
        c['obligations'][0]['statement'] += ' invented policy'
        self.error('STALE_REVIEW', f.review_gate, c, self.reviews['S10'])

    def test_ambiguity_and_conflict_override_forged_approval(self):
        for key, expected in [('S08', 'NEEDS_CLARIFICATION'), ('S09', 'CONFLICTING_REQUIREMENT')]:
            # An adversarial receipt is not real independent approval evidence.
            receipt = copy.deepcopy(self.reviews[key])
            receipt.update(outcome='APPROVED', checks={k: True for k in f.CHECKS})
            self.assertEqual(f.review_gate(self.candidates[key], receipt), expected)
            self.assertEqual(f.project(self.candidates[key], receipt)['status'], 'NOT_APPROVED')

    def test_adversarial_independent_review_results(self):
        for key, outcome in [('LEAK', 'REJECTED'), ('INVENTED', 'REJECTED'), ('MISSING', 'INCOMPLETE_FORMALIZATION')]:
            self.assertEqual(f.review_gate(self.candidates[key], self.reviews[key]), outcome)
            self.assertEqual(f.project(self.candidates[key], self.reviews[key])['status'], 'NOT_APPROVED')

    def test_success_only_source_has_no_invented_error_or_purity(self):
        c = self.candidates['S10']
        self.assertEqual([o['relation']['kind'] for o in c['obligations']], ['increment'])
        self.assertTrue(any('no rejection policy' in s for s in c['unspecified']))
        self.assertTrue(any('State changes, external effects' in s for s in c['unspecified']))
        self.assertEqual(f.review_gate(c, self.reviews['S10']), 'APPROVED')

    def test_bounded_comparison_ignores_provider_ids_and_clause_order(self):
        a = self.candidates['S01']
        self.assertEqual(f.compare_relations(a, a)['classification'], 'STRUCTURALLY_IDENTICAL')
        b = copy.deepcopy(a)
        b['formalizer'] = 'unrelated-provider'
        b['contract_id'] = 'other-serialization'
        b['obligations'].reverse()
        for index, o in enumerate(b['obligations']):
            o['id'] = 'different-' + str(index)
        self.assertEqual(f.compare_relations(a, b)['classification'], 'EXACT_CLAUSE_EQUIVALENT')

    def test_comparison_does_not_guess_semantics_or_ignore_context(self):
        a = self.candidates['S01']
        b = copy.deepcopy(a)
        b['obligations'].pop()
        self.assertEqual(f.compare_relations(a, b)['classification'], 'CLAUSE_SUBSET_REQUIRES_REVIEW')
        b = copy.deepcopy(a)
        b['obligations'][0]['statement'] += ' and reject everything else'
        self.assertEqual(f.compare_relations(a, b)['classification'], 'REFER_TO_REVIEW')
        b = copy.deepcopy(a)
        b['context']['assumptions'].append('inputs are bounded to 16-bit integers')
        self.assertEqual(f.compare_relations(a, b)['classification'], 'REFER_TO_REVIEW')

    def test_fail_closed_complete_projection(self):
        for key in ('S01', 'S02', 'S04', 'S05', 'S06', 'S07', 'S10', 'S11'):
            result = f.project(self.candidates[key], self.reviews[key])
            self.assertEqual(result['status'], 'UNREPRESENTABLE_SOURCE')
            self.assertNotIn('document', result)
            self.assertEqual(set(result['obligations_without_mapping']), {o['id'] for o in self.candidates[key]['obligations']})

    def test_calibration_projection_all_clauses_context_and_v1_round_trip(self):
        c = self.candidates['P01']
        result = f.project(c, self.reviews['P01'])
        self.assertEqual(result['status'], 'PROJECTED')
        self.assertEqual(len(result['coverage']), len(c['obligations']))
        self.assertEqual(v1.assemble([v1.parse(v1.canonical(result['document']))]), result['normalized'])
        recovered = f.recover(result['normalized'], c)
        self.assertEqual(f.compare_relations(c, recovered)['classification'], 'STRUCTURALLY_IDENTICAL')

    def test_recovery_detects_dropped_added_weakened_and_changed_context(self):
        c = self.candidates['P01']
        document = f.project(c, self.reviews['P01'])['document']
        for mutation, code in (
                (lambda x: x['payload']['obligations'].pop(), 'OBLIGATION_PRESERVATION_FAILURE'),
                (lambda x: x['payload']['obligations'].append({'id': 'invented', 'requirement': {'kind': 'public_state_alternatives', 'public': ['store']}}), 'OBLIGATION_PRESERVATION_FAILURE'),
                (lambda x: x['payload']['application'].update(id='changed'), 'CONTEXT_PRESERVATION_FAILURE')):
            changed = copy.deepcopy(document)
            mutation(changed)
            self.error(code, f.recover, v1.assemble([changed]), c)
        changed = copy.deepcopy(document)
        changed['payload']['obligations'][1]['requirement']['requirements']['V1'].pop()
        recovered = f.recover(v1.assemble([changed]), c)
        self.assertEqual(f.compare_relations(c, recovered)['classification'], 'REFER_TO_REVIEW')

    def test_one_edge_revision_stability(self):
        a = self.candidates['S10']
        b = copy.deepcopy(a)
        b['revision'] += 1
        self.assertEqual(f.check_revision(a, b)['status'], 'REVISION_EDGE_VALID')
        b['obligations'][0]['statement'] += ' additional constraint'
        self.error('UNDECLARED_MEANING_CHANGE', f.check_revision, a, b)
        b['lineage'] = [{'change': 'meaning_change', 'previous': ['S10.O01'], 'current': ['S10.O01'], 'reason': 'Explicitly declared changed clause; not an approved revision.'}]
        self.assertEqual(f.check_revision(a, b)['status'], 'REVISION_EDGE_VALID')
        b = copy.deepcopy(a)
        b['revision'] += 1
        b['obligations'] = []
        self.error('UNDECLARED_RETIREMENT', f.check_revision, a, b)
        b['lineage'] = [{'change': 'retire', 'previous': ['S10.O01'], 'current': [], 'reason': 'Retired; not approved.'}]
        self.assertEqual(f.check_revision(a, b)['retired_ids'], ['S10.O01'])

    def test_separate_projection_review_and_stale_binding(self):
        c = self.candidates['P01']
        projected = f.project(c, self.reviews['P01'])
        receipt = json.loads((HERE / 'projection-review.json').read_text(encoding='utf-8'))
        self.assertEqual(f.projection_gate(c, self.reviews['P01'], projected, receipt)['status'], 'APPROVED_PROJECTION')
        changed = copy.deepcopy(receipt)
        changed['document_commitment'] = '0' * 64
        self.error('STALE_PROJECTION_REVIEW', f.projection_gate, c, self.reviews['P01'], projected, changed)
        changed = copy.deepcopy(projected)
        changed['coverage'].pop()
        self.error('PROJECTION_COVERAGE_MISMATCH', f.projection_gate, c, self.reviews['P01'], changed, receipt)

    def test_bounded_conflict_witness(self):
        # Independent exhaustive enumeration of the two occurrence permutations
        # for this stated witness, not a general consistency decision procedure.
        original = ['z', 'a']
        permissible = [list(p) for p in itertools.permutations(original)
                       if list(p) == original and list(p) == sorted(original)]
        self.assertEqual(permissible, [])
        self.assertEqual(self.candidates['S09']['issues'][0]['witness']['input'], original)

    def test_reproducible_results_and_exact_coverage_locators(self):
        from benchmark.results.phase5c.r5_80 import qualify
        summary, coverage = qualify.run()
        self.assertEqual(summary, json.loads((HERE / 'qualification.json').read_text(encoding='utf-8')))
        self.assertEqual(coverage, json.loads((HERE / 'coverage.json').read_text(encoding='utf-8')))
        for key, record in coverage['sources'].items():
            source = self.candidates[key]['source']['text']
            for row in record['fragments']:
                self.assertEqual(source[row['start']:row['end']], row['text'])

    def test_fixture_read_allowlist_precedes_reads(self):
        original = Path.open
        allowed = {HERE / 'corpus.json', fixtures.ROOT / 'benchmark/requirements/B01.md'}
        attempts = []
        def guarded(path, *args, **kwargs):
            resolved = path.resolve()
            if resolved not in {p.resolve() for p in allowed}:
                attempts.append(str(resolved))
                raise AssertionError('not an admitted source')
            return original(path, *args, **kwargs)
        # Constructors/imports are already loaded; no support generation or
        # execution is called. This bounds fixture source I/O, not the whole OS.
        with patch.object(Path, 'open', guarded):
            fixtures.candidates()
        self.assertEqual(attempts, [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
