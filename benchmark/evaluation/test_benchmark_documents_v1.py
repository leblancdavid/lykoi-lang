"""Independent V1 qualification using public constructors, never protected inputs."""
import ast
import copy
import json
import re
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from benchmark.evaluation import benchmark_documents_v1 as d
from benchmark.evaluation import phase5_runner_v2 as r
from benchmark.harness.test_optional_support_r5_41 import setup
from benchmark.semantic import application_boundary_r5_41 as boundary
from benchmark.semantic import boundary_study_r5_39 as seed_bank
from benchmark.semantic import current_pipeline as pipeline
from benchmark.semantic import profile_audit_r5_41 as audit
from benchmark.semantic import readiness_r5_41 as readiness

ROOT = Path(__file__).resolve().parents[2]


def schema_accepts(value, schema):
    """Independent evaluator for the explicitly used JSON Schema keyword subset.

    Test-only; component validators/assembly rules remain additional authority.
    """
    types = {'object': dict, 'array': list, 'string': str}
    if 'type' in schema and type(value) is not types[schema['type']]:
        return False
    if 'const' in schema and value != schema['const']:
        return False
    if 'enum' in schema and value not in schema['enum']:
        return False
    if 'pattern' in schema and re.search(schema['pattern'], value) is None:
        return False
    if type(value) is dict:
        props = schema.get('properties', {})
        if any(k not in value for k in schema.get('required', [])):
            return False
        if len(value) < schema.get('minProperties', 0):
            return False
        extra = schema.get('additionalProperties', True)
        for key, child in value.items():
            if not schema_accepts(key, schema.get('propertyNames', {})):
                return False
            if key in props:
                if not schema_accepts(child, props[key]):
                    return False
            elif extra is False or (type(extra) is dict and not schema_accepts(child, extra)):
                return False
    if type(value) is list and any(not schema_accepts(child, schema.get('items', {})) for child in value):
        return False
    if not all(schema_accepts(value, part) for part in schema.get('allOf', [])):
        return False
    if 'if' in schema and schema_accepts(value, schema['if']):
        return schema_accepts(value, schema.get('then', {}))
    return True


def fixture(unsupported=False, real=False):
    app, spec, state, launch = seed_bank.setup() if real else setup('boolean' if unsupported else 'integer')
    public = [item['public'] for item in spec['operations']]
    return {'schema_version': d.VERSION, 'document_id': 'whole-contract', 'role': 'behavioral',
            'payload': {'application': app, 'configuration': {'transport': spec, 'state': state, 'launch': launch},
                        'obligations': [
                            {'id': 'public-coverage', 'requirement': {'kind': 'public_state_alternatives', 'public': public}},
                            {'id': 'durable-coverage', 'requirement': {'kind': 'durable_content_constraints',
                                'requirements': {name: copy.deepcopy(desc['constraints'])
                                                 for name, desc in state['alternatives'].items()}}}]}}


def metadata():
    return {'schema_version': d.VERSION, 'document_id': 'description', 'role': 'metadata',
            'payload': {'description': 'Public prospective representation, not acceptance material.'}}


def static_contract(contract):
    """Existing consumer projection. Only normalized contracts enter this boundary."""
    d.verify_contract(contract)
    app, config = contract['application'], contract['configuration']
    obligations = [entry['requirement'] for entry in contract['obligations']]
    try:
        plans = pipeline.checked(app)
        manifest = {'application': r.digest(r.canonical(app)), 'generation': 'static-v1-only',
                    'units': {name: plan.digest for name, plan in plans.items()}}
        ready = readiness.inspect(app, config['transport'], config['state'], config['launch'], obligations)
        audited = audit.inspect(app, config)
        try:
            admitted = boundary.aggregate(app, config['transport'], config['state'], config['launch'], manifest)
            admission = {'status': 'ADMITTED', 'plans': admitted['plans']}
        except ValueError as exc:
            admission = {'status': 'REJECTED', 'reason': str(exc)}
        compatibility = boundary.support_report(app, config['transport'], config['state'], config['launch'], manifest)
    except (KeyError, IndexError, AttributeError, TypeError, ValueError):
        return {'classification': 'STATIC_INTERFACE_FAILURE', 'static_evaluated': False}
    supported = (ready['status'] == 'READY' and audited['status'] == 'SUPPORTED'
                 and admission['status'] == 'ADMITTED' and compatibility['status'] == 'SUPPORTED')
    return {'classification': 'STATIC_SUPPORTED' if supported else 'STATIC_UNSUPPORTED',
            'static_evaluated': True, 'contract_identity': contract['identity'],
            'checked_plans': manifest['units'], 'readiness': ready, 'audit': audited,
            'admission': admission, 'compatibility': compatibility,
            'whole_contract': 'SUPPORTED' if supported else 'UNSUPPORTED',
            'generation': 0, 'execution': 0, 'acceptance': 0, 'repair': 0}


def consume(opened):
    try:
        contract = d.from_opened(opened)
    except d.DocumentError as exc:
        return {'classification': 'DOCUMENT_FAILURE', 'static_evaluated': False, 'error': exc.record()}
    return static_contract(contract)


def lifecycle(directory, contents, state=None, health=None, capture=None):
    ledger = r.Ledger(directory)
    state = state or r.seal({'kind': 'CurrentState', 'semantic_count': 30, 'runner': {'test': 'fixed'}})
    capture = capture or (lambda: state)
    health = health or r.health_record(state, {name: {'status': 'PASS', 'state': state['identity']}
                                             for name in r.HEALTH_STAGES})
    commitment = r.seal({'kind': 'synthetic', 'authority_class': r.SYNTHETIC_TEST,
                        'expected_benchmark': 'independent-v1-package',
                        'resources': {name: {'commitment': r.digest(raw), 'seal': 'CLOSED', 'frozen': True,
                                            'provenance': 'public prospective V1 constructor'}
                                      for name, raw in contents.items()}})
    frozen = r.freeze(state, commitment, health, ledger)
    grant = r.authorize_synthetic(frozen, commitment, ledger, state)
    with patch.object(pipeline, 'generate', side_effect=AssertionError('generation forbidden')):
        result = r.observe(frozen, commitment, grant, ledger, capture, lambda: commitment,
                           lambda: contents, consume)
    post = r.post_check(frozen, commitment, ledger, capture, lambda: commitment)
    return {'commitment': commitment, 'freeze': frozen, 'authorization': grant, 'result': result,
            'post_check': post, 'events': [e['transition'] for e in ledger.events()]}


class DocumentQualification(unittest.TestCase):
    def error(self, documents, code):
        with self.assertRaises(d.DocumentError) as caught:
            d.assemble(documents)
        self.assertEqual(caught.exception.code, code)
        self.assertEqual(set(caught.exception.record()), {'code', 'path'})

    def test_schema_validation(self):
        schema = json.loads((ROOT / 'schema/benchmark-document-contract-v1.schema.json').read_bytes())
        self.assertEqual(schema['properties']['schema_version']['const'], d.VERSION)
        self.assertEqual(schema['properties']['role']['enum'], list(d.ROLES))
        self.assertEqual(set(schema['required']), {'schema_version', 'document_id', 'role', 'payload'})
        self.assertFalse(schema['additionalProperties'])
        self.assertTrue(schema_accepts(fixture(), schema))
        self.assertTrue(schema_accepts(metadata(), schema))
        self.assertEqual(d.validate_document(fixture()), d.identity(fixture()))
        for field in schema['required']:
            doc = fixture()
            del doc[field]
            self.assertFalse(schema_accepts(doc, schema))
            with self.assertRaises(d.DocumentError):
                d.validate_document(doc)

    def test_independent_schema_payload_rejections(self):
        schema = json.loads((ROOT / 'schema/benchmark-document-contract-v1.schema.json').read_bytes())
        for transform in (
                lambda v: v.update(role='execution'),
                lambda v: v.update(schema_version='unknown'),
                lambda v: v.update(extra=True),
                lambda v: v.update(metadata=[]),
                lambda v: v['payload'].update(obligations={}),
                lambda v: v['payload']['obligations'][0].update(id=''),
                lambda v: v['payload']['obligations'][0].update(requirement=[]),
                lambda v: v['payload'].update(configuration=[])):
            doc = fixture()
            transform(doc)
            self.assertFalse(schema_accepts(doc, schema))
            with self.assertRaises(d.DocumentError):
                d.validate_document(doc)

    def test_document_identity_is_canonical(self):
        doc = fixture()
        self.assertEqual(d.validate_document(doc), d.validate_document(dict(reversed(list(doc.items())))))
        doc['metadata'] = {'note': 'different envelope'}
        self.assertNotEqual(d.validate_document(doc), d.validate_document(fixture()))

    def test_simple_one_obligations_document(self):
        contract = d.assemble([fixture()])
        self.assertEqual(len(contract['obligations']), 2)
        self.assertEqual(set(contract), {'schema_version', 'application', 'configuration', 'obligations', 'identity'})

    def test_multiple_documents(self):
        self.assertEqual(d.assemble([metadata(), fixture()]), d.assemble([fixture()]))

    def test_deterministic_ordering(self):
        first, second = fixture(), fixture()
        second['payload']['obligations'].reverse()
        self.assertEqual(d.assemble([metadata(), first]), d.assemble([second, metadata()]))
        self.assertEqual([o['id'] for o in d.assemble([first])['obligations']], ['durable-coverage', 'public-coverage'])

    def test_duplicate_document_id(self):
        self.error([fixture(), fixture()], 'DUPLICATE_DOCUMENT_ID')

    def test_missing_required_role(self):
        self.error([metadata()], 'MISSING_REQUIRED_ROLE')
        self.error([], 'MISSING_REQUIRED_ROLE')

    def test_malformed_payload(self):
        for payload in ([], {'nested': fixture()['payload']}):
            doc = fixture()
            doc['payload'] = payload
            self.error([doc], 'MALFORMED_PAYLOAD')

    def test_malformed_configuration_is_not_support_gap(self):
        doc = fixture()
        doc['payload']['configuration']['transport']['unknown'] = True
        self.error([doc], 'MALFORMED_PAYLOAD')

    def test_malformed_obligation(self):
        for entry in ({}, {'id': 'x', 'requirement': []}, {'id': 'x', 'requirement': {'kind': 'public_state_alternatives'}},
                      {'id': 'x', 'requirement': {'kind': 'durable_content_constraints', 'requirements': []}},
                      {'ref': 'missing'}):
            doc = fixture()
            doc['payload']['obligations'] = [entry]
            self.error([doc], 'MALFORMED_OBLIGATION')

    def test_unsupported_version(self):
        doc = fixture()
        doc['schema_version'] = 'BenchmarkDocumentContractV2'
        self.error([doc], 'UNSUPPORTED_SCHEMA_VERSION')

    def test_references_intentionally_not_supported(self):
        doc = fixture()
        doc['references'] = [{'document_id': 'missing'}]
        self.error([doc], 'MALFORMED_DOCUMENT')

    def test_conflicting_obligation(self):
        doc = fixture()
        entry = copy.deepcopy(doc['payload']['obligations'][0])
        entry['requirement']['public'] = ['other']
        doc['payload']['obligations'].append(entry)
        self.error([doc], 'CONFLICTING_OBLIGATIONS')

    def test_identical_duplicate_obligation_rejected(self):
        doc = fixture()
        doc['payload']['obligations'].append(copy.deepcopy(doc['payload']['obligations'][0]))
        self.error([doc], 'DUPLICATE_OBLIGATION')

    def test_metadata_stability(self):
        doc = fixture()
        doc['metadata'] = {'note': {'nested': [1, True, None]}}
        self.assertEqual(d.assemble([doc, metadata()]), d.assemble([fixture()]))

    def test_deterministic_contract_identity(self):
        a = d.assemble([fixture()])
        self.assertEqual(a['identity'], d.assemble([fixture()])['identity'])
        doc = fixture()
        doc['document_id'] = 'renamed'
        self.assertEqual(a, d.assemble([doc]))
        doc['payload']['obligations'] = []
        self.assertNotEqual(a['identity'], d.assemble([doc])['identity'])

    def test_adapter_canonical_round_trip(self):
        doc = fixture()
        contract = d.assemble([doc])
        self.assertEqual(d.assemble([d.parse(d.canonical(doc))]), contract)
        self.assertEqual(d.verify_contract(d.parse(d.canonical(contract))), contract)
        prospective = {'schema_version': d.VERSION, 'document_id': 'round-trip', 'role': 'behavioral',
                       'payload': {k: contract[k] for k in ('application', 'configuration', 'obligations')}}
        self.assertEqual(d.assemble([prospective]), contract)

    def test_supported_synthetic_static_pipeline(self):
        with tempfile.TemporaryDirectory() as directory:
            row = lifecycle(directory, {'opaque-a': d.canonical(fixture()), 'opaque-b': d.canonical(metadata())})
        self.assertEqual(row['result']['classification'], 'STATIC_SUPPORTED', row['result'])
        self.assertEqual(row['events'], list(r.TRANSITIONS))
        self.assertEqual(row['post_check']['status'], 'PASS')
        self.assertEqual(row['result']['readiness']['status'], 'READY')
        self.assertEqual(row['result']['audit']['status'], 'SUPPORTED')
        self.assertEqual(row['result']['admission']['status'], 'ADMITTED')
        self.assertEqual(row['result']['compatibility']['status'], 'SUPPORTED')

    def test_unsupported_synthetic_static_pipeline(self):
        with tempfile.TemporaryDirectory() as directory:
            row = lifecycle(directory, {'opaque': d.canonical(fixture(True))})
        self.assertEqual(row['result']['classification'], 'STATIC_UNSUPPORTED', row['result'])
        self.assertEqual(row['result']['readiness']['status'], 'NOT_READY')
        self.assertEqual(row['result']['audit']['status'], 'UNSUPPORTED')
        self.assertEqual(row['result']['admission']['status'], 'REJECTED')
        self.assertEqual(row['result']['compatibility']['status'], 'UNSUPPORTED')
        self.assertEqual(row['post_check']['status'], 'PASS')

    def test_malformed_synthetic_lifecycle(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(pipeline, 'checked', side_effect=AssertionError('partial')):
            row = lifecycle(directory, {'opaque': b'{invalid'})
        self.assertEqual(row['result']['error']['code'], 'MALFORMED_DOCUMENT')
        self.assertEqual(row['events'], list(r.TRANSITIONS))
        self.assertEqual(row['post_check']['status'], 'PASS')

    def test_incomplete_synthetic_lifecycle(self):
        doc = fixture()
        del doc['payload']['obligations']
        with tempfile.TemporaryDirectory() as directory, patch.object(pipeline, 'checked', side_effect=AssertionError('partial')):
            row = lifecycle(directory, {'opaque': d.canonical(doc)})
        self.assertEqual(row['result']['error']['code'], 'INCOMPLETE_CONTRACT')
        self.assertEqual(row['post_check']['status'], 'PASS')

    def test_public_non_heldout_seed_bank_adaptation(self):
        with tempfile.TemporaryDirectory() as directory:
            row = lifecycle(directory, {'public-study': d.canonical(fixture(real=True))})
        self.assertEqual(row['result']['classification'], 'STATIC_SUPPORTED', row['result'])
        self.assertEqual(len(row['result']['checked_plans']), 7)
        self.assertEqual(row['post_check']['status'], 'PASS')

    def test_no_benchmark_specific_filename_behavior(self):
        raw = d.canonical(fixture())
        self.assertEqual(consume({'unrelated.txt': raw}), consume({'B02.md': raw}))
        self.assertEqual(consume({'B03.json': raw}), consume({'no-extension': raw}))

    def test_no_b02_access(self):
        self.protected_fake('B02.md')

    def test_no_b03_access(self):
        self.protected_fake('B03.md')

    def protected_fake(self, name):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / name
            path.write_bytes(b'synthetic protected bytes')
            guard = r.Boundary(directory, [path])
            with self.assertRaises(r.Rejected), guard.active():
                with self.assertRaises(r.Rejected):
                    path.read_bytes()
            self.assertEqual(guard.attempts, 1)

    def test_ai_independent_extraction(self):
        source = Path(d.__file__).read_text()
        imports = [n for n in ast.walk(ast.parse(source)) if isinstance(n, (ast.Import, ast.ImportFrom))]
        names = [a.name for n in imports if isinstance(n, ast.Import) for a in n.names]
        names += [n.module for n in imports if isinstance(n, ast.ImportFrom)]
        self.assertEqual(set(names), {'hashlib', 'json', 'benchmark.semantic'})
        with patch('socket.create_connection', side_effect=AssertionError('network forbidden')):
            self.assertEqual(d.assemble([fixture()]), d.assemble([fixture()]))

    def test_unknown_role_rejects(self):
        doc = metadata()
        doc['role'] = 'acceptance'
        self.error([fixture(), doc], 'UNKNOWN_REQUIRED_ROLE')

    def test_ambiguous_assembly_rejects(self):
        doc = fixture()
        doc['document_id'] = 'second'
        self.error([fixture(), doc], 'AMBIGUOUS_ASSEMBLY')

    def test_explicit_empty_set_permitted(self):
        doc = fixture()
        doc['payload']['obligations'] = []
        self.assertEqual(d.assemble([doc])['obligations'], [])

    def test_unknown_obligation_is_not_silently_dropped(self):
        doc = fixture()
        doc['payload']['obligations'].append({'id': 'new', 'requirement': {'kind': 'unrecognized-generic-kind'}})
        result = consume({'opaque': d.canonical(doc)})
        self.assertEqual(result['classification'], 'STATIC_UNSUPPORTED')
        self.assertTrue(any(g['stage'] == 'readiness' for g in result['readiness']['gaps']))

    def test_strict_json_rejection(self):
        for raw in (b'{"role":1,"role":2}', b'{"x":NaN}', b'\xff', '{}'.encode('utf-16')):
            with self.assertRaises(d.DocumentError):
                d.parse(raw)

    def test_adapter_does_not_call_support(self):
        doc = fixture()
        with patch.object(pipeline, 'checked', side_effect=AssertionError('support in adapter')):
            self.assertEqual(len(d.assemble([doc])['obligations']), 2)


if __name__ == '__main__':
    from benchmark.evaluation.phase5_worker_v2 import run_suite
    guard = r.Boundary(ROOT, [ROOT / 'benchmark/requirements/B03.md',
                            ROOT / 'benchmark/harness/profiles/B03.json',
                            ROOT / 'benchmark/harness/capabilities/B03.json',
                            ROOT / 'benchmark/results/phase5c/R5_75-evidence/opened-static-documents.json'])
    with guard.active():
        detail = run_suite(unittest.defaultTestLoader.loadTestsFromTestCase(DocumentQualification))
    print(json.dumps({'status': 'PASS', 'detail': detail, 'protected_read_attempts': guard.attempts}, sort_keys=True))
