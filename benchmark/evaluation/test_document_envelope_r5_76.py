"""Non-protected diagnostics, NOT a new benchmark-envelope protocol.

The existing protocols do not authorize a generic nested/multi-document layout.
The explicit fixture below is test-local authority only. Successful diagnostics
must not be promoted to qualification of an unspecified benchmark envelope.
"""
import ast
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from benchmark.evaluation import phase5_runner_v2 as r
from benchmark.harness.test_optional_support_r5_41 import setup
from benchmark.semantic import application_boundary_r5_41 as boundary
from benchmark.semantic import current_pipeline as pipeline
from benchmark.semantic import profile_audit_r5_41 as audit
from benchmark.semantic import readiness_r5_41 as readiness

ROOT = Path(__file__).resolve().parents[2]


def historical_expression(document):
    """Execute only the obligation assignment AST, never the old controller."""
    source = ROOT / 'benchmark/results/phase5c/r5_75_experiment.py'
    tree = ast.parse(source.read_text(encoding='utf-8'))
    assignments = [node for node in ast.walk(tree) if isinstance(node, ast.Assign)
                   and any(isinstance(t, ast.Name) and t.id == 'obligations'
                           for t in node.targets)]
    if len(assignments) != 1:
        raise AssertionError('historical assignment changed')
    expression = ast.Expression(assignments[0].value)
    return eval(compile(expression, str(source), 'eval'),
                {'__builtins__': {}, 'isinstance': isinstance, 'dict': dict},
                {'obligation_document': document})


def fixture(unsupported=False):
    app, spec, state, launch = setup('boolean' if unsupported else 'integer')
    return {'application': app,
            'configuration': {'transport': spec, 'state': state, 'launch': launch},
            'obligations': [{'kind': 'public_state_alternatives', 'public': ['store']},
                            {'kind': 'durable_content_constraints',
                             'requirements': {'V1': copy.deepcopy(state['alternatives']['V1']['constraints'])}}]}


def explicit_fixture_consumer(opened):
    """Diagnostic callback for one predetermined fixture, not a generic extractor.

    There is no inference of roles, no recursive obligations search, and no
    benchmark-specific resource selection. Unrecognized containers are a protocol
    gap, not an unsupported requirement. No partial static evaluation follows.
    """
    try:
        if set(opened) != {'synthetic:explicit-fixture'}:
            return {'classification': 'SYNTHETIC_FIXTURE_INCOMPLETE', 'static_evaluated': False}
        value = json.loads(opened['synthetic:explicit-fixture'])
    except (ValueError, UnicodeError, TypeError):
        return {'classification': 'SYNTHETIC_FIXTURE_MALFORMED', 'static_evaluated': False}
    if (type(value) is not dict or set(value) != {'application', 'configuration', 'obligations'}
            or type(value['obligations']) is not list
            or not all(type(o) is dict for o in value['obligations'])):
        return {'classification': 'DOCUMENT_ENVELOPE_GAP', 'static_evaluated': False}
    app, config, obligations = (value[k] for k in ('application', 'configuration', 'obligations'))
    # This fixture's completeness is known from its constructor, not inferred
    # from an external requirement, document inventory or arbitrary envelope.
    try:
        audit.structure(config)
        plans = pipeline.checked(app)
        manifest = {'application': r.digest(r.canonical(app)), 'generation': 'synthetic-static-only',
                    'units': {name: plan.digest for name, plan in plans.items()}}
        ready = readiness.inspect(app, config['transport'], config['state'], config['launch'], obligations)
        audited = audit.inspect(app, config)
        compatible = boundary.support_report(app, config['transport'], config['state'], config['launch'], manifest)
        try:
            admitted = boundary.aggregate(app, config['transport'], config['state'], config['launch'], manifest)
            admission = {'status': 'ADMITTED', 'plans': admitted['plans']}
        except ValueError as exc:
            admission = {'status': 'REJECTED', 'reason': str(exc)}
    except (KeyError, IndexError, AttributeError, TypeError, ValueError):
        return {'classification': 'SYNTHETIC_STATIC_INTERFACE_FAILURE', 'static_evaluated': False}
    supported = (ready['status'] == 'READY' and audited['status'] == 'SUPPORTED'
                 and compatible['status'] == 'SUPPORTED' and admission['status'] == 'ADMITTED')
    return {'classification': 'SYNTHETIC_STATIC_PASS' if supported else 'SYNTHETIC_STATIC_UNSUPPORTED',
            'static_evaluated': True, 'contract_identity': r.digest(r.canonical(value)),
            'checked_plans': manifest['units'], 'readiness': ready, 'audit': audited,
            'admission': admission, 'compatibility': compatible,
            'generation': 0, 'execution': 0, 'acceptance': 0, 'repair': 0}


def lifecycle(directory, contents, state=None):
    ledger = r.Ledger(directory)
    state = state or r.seal({'kind': 'CurrentState', 'semantic_count': 30,
                            'runner': {'diagnostic': 'fixed'}})
    commitment = r.seal({'kind': 'synthetic', 'authority_class': r.SYNTHETIC_TEST,
        'expected_benchmark': 'independent-envelope-diagnostic',
        'resources': {name: {'commitment': r.digest(raw), 'seal': 'CLOSED', 'frozen': True,
                             'provenance': 'test-local synthetic constructor'}
                      for name, raw in contents.items()}})
    # Unit fixture linkage only; the qualification driver separately runs real health.
    health = r.health_record(state, {name: {'status': 'PASS', 'state': state['identity']}
                                    for name in r.HEALTH_STAGES})
    frozen = r.freeze(state, commitment, health, ledger)
    grant = r.authorize_synthetic(frozen, commitment, ledger, state)
    counts = {'openings': 0, 'dispatches': 0}
    def opener():
        counts['openings'] += 1
        return contents
    def evaluator(opened):
        counts['dispatches'] += 1
        return explicit_fixture_consumer(opened)
    with patch.object(pipeline, 'generate', side_effect=AssertionError('static generation forbidden')):
        result = r.observe(frozen, commitment, grant, ledger, lambda: state,
                           lambda: commitment, opener, evaluator)
    post = r.post_check(frozen, commitment, ledger, lambda: state, lambda: commitment)
    return result, post, counts, frozen, commitment, grant, ledger, state


class EnvelopeInvestigation(unittest.TestCase):
    def test_top_level_assumption_works_for_explicit_example(self):
        obligations = fixture()['obligations']
        self.assertEqual(historical_expression({'obligations': obligations}), obligations)

    def test_bare_list_assumption_works(self):
        self.assertEqual(historical_expression(fixture()['obligations']), fixture()['obligations'])

    def test_nested_counterexample_reproduces_keyerror(self):
        # Counterexample only: NOT asserted to be a valid benchmark envelope.
        with self.assertRaisesRegex(KeyError, 'obligations'):
            historical_expression({'payload': {'obligations': fixture()['obligations']}})

    def test_missing_obligations_reproduces_keyerror(self):
        with self.assertRaisesRegex(KeyError, 'obligations'):
            historical_expression({'metadata': {'description': 'synthetic'}})

    def test_optional_metadata_does_not_affect_expression(self):
        obligations = fixture()['obligations']
        self.assertEqual(historical_expression({'obligations': obligations, 'metadata': {}}), obligations)

    def test_expression_does_not_validate_versions(self):
        self.assertEqual(historical_expression({'version': 'unsupported', 'obligations': []}), [])

    def test_expression_does_not_validate_roles(self):
        self.assertEqual(historical_expression({'role': 'not-a-contract', 'obligations': []}), [])

    def test_expression_does_not_resolve_document_references(self):
        refs = [{'ref': 'missing-document'}]
        self.assertEqual(historical_expression({'obligations': refs}), refs)

    def test_expression_does_not_reject_conflicting_identities(self):
        obligations = [{'id': 'same', 'kind': 'first'}, {'id': 'same', 'kind': 'second'}]
        self.assertEqual(historical_expression({'obligations': obligations}), obligations)

    def test_canonical_fixture_round_trip_and_determinism(self):
        value = fixture()
        raw = r.canonical(value)
        self.assertEqual(raw, r.canonical(json.loads(raw)))
        self.assertEqual(explicit_fixture_consumer({'synthetic:explicit-fixture': raw}),
                         explicit_fixture_consumer({'synthetic:explicit-fixture': r.canonical(fixture())}))

    def test_full_supported_synthetic_lifecycle(self):
        with tempfile.TemporaryDirectory() as directory:
            result, post, counts, *rest = lifecycle(directory, {'synthetic:explicit-fixture': r.canonical(fixture())})
            self.assertEqual(result['classification'], 'SYNTHETIC_STATIC_PASS', result)
            self.assertEqual(result['readiness']['status'], 'READY')
            self.assertEqual(result['audit']['status'], 'SUPPORTED')
            self.assertEqual(result['admission']['status'], 'ADMITTED')
            self.assertEqual(result['compatibility']['status'], 'SUPPORTED')
            self.assertEqual(set(result['checked_plans']), {'store'})
            self.assertEqual(counts, {'openings': 1, 'dispatches': 1})
            self.assertEqual(post['observations'], 1)
            self.assertEqual([e['transition'] for e in rest[-2].events()], list(r.TRANSITIONS))

    def test_genuine_supported_shape_but_unsupported_text_boolean(self):
        with tempfile.TemporaryDirectory() as directory:
            result, post, *_ = lifecycle(directory, {'synthetic:explicit-fixture': r.canonical(fixture(True))})
            self.assertEqual(result['classification'], 'SYNTHETIC_STATIC_UNSUPPORTED', result)
            self.assertEqual(result['readiness']['status'], 'NOT_READY')
            self.assertEqual(result['audit']['status'], 'UNSUPPORTED')
            self.assertEqual(result['admission']['status'], 'REJECTED')
            self.assertEqual(result['compatibility']['status'], 'UNSUPPORTED')
            self.assertEqual(post['status'], 'PASS')

    def test_malformed_synthetic_observation_completes_as_infrastructure_result(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(pipeline, 'checked', side_effect=AssertionError('partial evaluation')):
            result, post, *_ = lifecycle(directory, {'synthetic:explicit-fixture': b'{invalid'})
            self.assertEqual(result, {'classification': 'SYNTHETIC_FIXTURE_MALFORMED', 'static_evaluated': False})
            self.assertEqual(post['status'], 'PASS')

    def test_incomplete_synthetic_set_rejects_before_static_consumers(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(pipeline, 'checked', side_effect=AssertionError('partial evaluation')):
            result, post, *_ = lifecycle(directory, {'synthetic:unrelated': b'{}'})
            self.assertEqual(result, {'classification': 'SYNTHETIC_FIXTURE_INCOMPLETE', 'static_evaluated': False})
            self.assertEqual(post['status'], 'PASS')

    def test_unknown_envelope_is_gap_not_invented_obligations(self):
        values = ({'payload': fixture()}, {'documents': [fixture()]},
                  {'schema_version': 'unknown', **fixture()}, {'role': 'unknown', **fixture()})
        with patch.object(pipeline, 'checked', side_effect=AssertionError('partial evaluation')):
            for value in values:
                self.assertEqual(explicit_fixture_consumer({'synthetic:explicit-fixture': r.canonical(value)}),
                                 {'classification': 'DOCUMENT_ENVELOPE_GAP', 'static_evaluated': False})

    def test_replay_rejected_before_callback(self):
        with tempfile.TemporaryDirectory() as directory:
            _, _, _, frozen, commitment, grant, ledger, state = lifecycle(
                directory, {'synthetic:explicit-fixture': r.canonical(fixture())})
            with self.assertRaises(r.Rejected):
                r.observe(frozen, commitment, grant, ledger, lambda: state, lambda: commitment,
                          lambda: self.fail('reopened'), lambda _: self.fail('redispatched'))
            with self.assertRaises(r.Rejected):
                r.authorize_synthetic(frozen, commitment, ledger, state)

    def test_repair_invalidates_completed_synthetic_diagnostic(self):
        with tempfile.TemporaryDirectory() as directory:
            _, _, _, frozen, commitment, _, ledger, state = lifecycle(
                directory, {'synthetic:explicit-fixture': r.canonical(fixture())})
            r.invalidate_repair(frozen, ledger)
            self.assertEqual(ledger.status(), 'multiple/invalid')
            with self.assertRaises(r.Rejected):
                r.post_check(frozen, commitment, ledger, lambda: state, lambda: commitment)

    def test_protected_access_controls_on_fake_files_only(self):
        for name in ('B02.md', 'B03.md'):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / name
                path.write_bytes(b'synthetic denied content')
                guard = r.Boundary(directory, [path])
                with self.assertRaises(r.Rejected), guard.active():
                    with self.assertRaises(r.Rejected):
                        path.read_bytes()
                self.assertEqual(guard.attempts, 1)

    def test_offline_deterministic_fixture_extraction(self):
        with patch('socket.create_connection', side_effect=AssertionError('network forbidden')):
            raw = r.canonical(fixture())
            first = explicit_fixture_consumer({'synthetic:explicit-fixture': raw})
            self.assertEqual(first, explicit_fixture_consumer({'synthetic:explicit-fixture': raw}))
            self.assertEqual(first['classification'], 'SYNTHETIC_STATIC_PASS')


if __name__ == '__main__':
    from benchmark.evaluation.phase5_worker_v2 import run_suite
    guard = r.Boundary(ROOT, [ROOT / 'benchmark/requirements/B03.md',
                             ROOT / 'benchmark/harness/profiles/B03.json',
                             ROOT / 'benchmark/harness/capabilities/B03.json'])
    with guard.active():
        detail = run_suite(unittest.defaultTestLoader.loadTestsFromTestCase(EnvelopeInvestigation))
    print(json.dumps({'status': 'PASS', 'detail': detail,
                      'protected_read_attempts': guard.attempts}, sort_keys=True))
