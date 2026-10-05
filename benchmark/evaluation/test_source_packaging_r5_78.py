"""Public/synthetic packaging checks; never accesses protected source."""
import ast
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from benchmark.evaluation import benchmark_documents_v1 as v1
from benchmark.evaluation import phase5_runner_v2 as runner
from benchmark.evaluation import source_packaging_r5_78 as packaging
from benchmark.evaluation.test_benchmark_documents_v1 import fixture, schema_accepts
from benchmark.semantic import current_pipeline, readiness_r5_41, profile_audit_r5_41, application_boundary_r5_41

ROOT = Path(__file__).resolve().parents[2]


def explicit(real=False):
    return {'components': v1.canonical(fixture(real=real)['payload'])}


def public_bundle():
    return {name: (ROOT / path).read_bytes() for name, path in {
        'request': 'benchmark/requirements/B01.md',
        'profile': 'benchmark/harness/profiles/B01.json',
        'capability': 'benchmark/harness/capabilities/B01.json'}.items()}


class PackagingQualification(unittest.TestCase):
    def reject(self, interface, resources, code):
        with self.assertRaises(packaging.PackagingError) as caught:
            packaging.transform(interface, resources)
        self.assertEqual(caught.exception.record(), {'code': code})
        self.assertEqual(str(caught.exception), code)

    def test_deterministic_transformation(self):
        self.assertEqual(packaging.transform('explicit-components', explicit()),
                         packaging.transform('explicit-components', explicit()))

    def test_simple_valid_schema(self):
        raw, receipt = packaging.transform('explicit-components', explicit())
        schema = json.loads((ROOT / 'schema/benchmark-document-contract-v1.schema.json').read_bytes())
        self.assertTrue(schema_accepts(v1.parse(raw)[0], schema))
        self.assertEqual(receipt['schema_version'], v1.VERSION)

    def test_public_real_components(self):
        raw, receipt = packaging.transform('explicit-components', explicit(real=True))
        self.assertEqual(v1.assemble(v1.parse(raw))['identity'], receipt['behavioral_commitment'])

    def test_malformed_rejection(self):
        self.reject('explicit-components', {'components': b'{invalid'}, 'MALFORMED_SOURCE')

    def test_unrepresentable_synthetic(self):
        self.reject('frozen-request-bundle', {'request': b'Public synthetic prose',
                    'profile': b'{}', 'capability': b'{}'}, 'UNREPRESENTABLE_SOURCE')

    def test_public_historical_source_gate(self):
        self.reject('frozen-request-bundle', public_bundle(), 'UNREPRESENTABLE_SOURCE')

    def test_single_behavioral_role(self):
        raw, receipt = packaging.transform('explicit-components', explicit())
        self.assertEqual([d['role'] for d in v1.parse(raw)], ['behavioral'])
        self.assertEqual(receipt['behavioral_documents'], 1)

    def test_metadata_closed(self):
        source = fixture()['payload']
        source['metadata'] = {'description': 'synthetic'}
        self.reject('explicit-components', {'components': v1.canonical(source)}, 'INVALID_V1_STRUCTURE')
        self.assertEqual(packaging.transform('explicit-components', explicit())[1]['metadata_documents'], 0)

    def test_no_references(self):
        source = fixture()['payload']
        source['references'] = ['synthetic']
        self.reject('explicit-components', {'components': v1.canonical(source)}, 'INVALID_V1_STRUCTURE')

    def test_package_commitment(self):
        raw, receipt = packaging.transform('explicit-components', explicit())
        self.assertEqual(packaging.digest(raw), receipt['package_commitment'])
        source = fixture()['payload']
        source['obligations'].reverse()
        self.assertEqual(raw, packaging.transform('explicit-components', {'components': v1.canonical(source)})[0])

    def test_behavioral_commitment(self):
        raw, receipt = packaging.transform('explicit-components', explicit())
        self.assertEqual(v1.assemble(v1.parse(raw))['identity'], receipt['behavioral_commitment'])

    def test_no_evaluator_calls(self):
        targets = [(current_pipeline, 'checked'), (readiness_r5_41, 'inspect'),
                   (profile_audit_r5_41, 'inspect'), (application_boundary_r5_41, 'aggregate'),
                   (application_boundary_r5_41, 'support_report'), (v1, 'from_opened'), (v1, 'assemble')]
        from contextlib import ExitStack
        resources = explicit()
        with ExitStack() as stack:
            for module, name in targets:
                stack.enter_context(patch.object(module, name, side_effect=AssertionError('forbidden call')))
            packaging.transform('explicit-components', resources)

    def test_closed_publication(self):
        source = fixture()['payload']
        marker = 'synthetic-protected-publication-witness'
        source['application']['id'] = marker
        raw, receipt = packaging.transform('explicit-components', {'components': v1.canonical(source)})
        self.assertIn(marker.encode(), raw)
        self.assertNotIn(marker, json.dumps(receipt))
        self.assertEqual(set(receipt), {'schema_version', 'package_identity', 'package_commitment',
            'behavioral_commitment', 'document_commitment', 'provenance_identity',
            'behavioral_documents', 'metadata_documents', 'status'})

    def test_error_redaction(self):
        source = fixture()['payload']
        source['obligations'][0]['requirement'] = {'synthetic-sensitive-key': 'synthetic-sensitive-value'}
        self.reject('explicit-components', {'components': v1.canonical(source)}, 'INVALID_V1_STRUCTURE')
        self.reject('explicit-components', {'components': b'{"x":1,"x":2}'}, 'MALFORMED_SOURCE')

    def test_metadata_only_runner_eligibility(self):
        _, receipt = packaging.transform('explicit-components', explicit())
        commitment = runner.seal({'kind': 'public-stand-in', 'authority_class': runner.ACTUAL_HELD_OUT,
            'precommitted': True, 'resources': {'opaque': {'seal': 'CLOSED', 'frozen': True,
                'commitment': receipt['document_commitment'], 'provenance': receipt['provenance_identity']}}})
        with patch.object(runner, 'authorize', side_effect=AssertionError('issuance forbidden')), \
             patch.object(runner, 'observe', side_effect=AssertionError('observation forbidden')):
            self.assertTrue(runner.eligible(commitment, runner.ACTUAL_HELD_OUT, commitment['identity']))
        self.assertEqual(receipt['status'], 'VALIDATED_NOT_SEALED')

    def test_no_io_or_dynamic_dispatch(self):
        tree = ast.parse((ROOT / 'benchmark/evaluation/source_packaging_r5_78.py').read_text(encoding='utf-8'))
        imports = [n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)]
        self.assertEqual(imports, ['benchmark.evaluation'])
        calls = {n.func.id for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
        self.assertFalse(calls & {'open', 'print', 'eval', 'exec', '__import__'})


if __name__ == '__main__':
    unittest.main()
