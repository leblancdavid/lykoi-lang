"""Non-task seed-bank application: semantic sources and grounded public evidence."""

import copy
import json
from pathlib import Path
import tempfile

from benchmark.semantic import current_pipeline as pipeline
from benchmark.semantic import application_boundary_r5_39 as boundary
from benchmark.semantic import checked_transport_r5_35 as transport
from benchmark.semantic import checked_launch_r5_36 as launch
from benchmark.semantic import verify_boundary_r5_39 as verifier
from benchmark.semantic.nullable_study_r5_38 import ref, lit, non_null
from benchmark.semantic.refined_generator_r5_28 import canonical

ROW1 = {'record': {'code': 'string', 'label': 'string', 'harvest': {'optional': {'nullable': 'instant'}}}}
ROW2 = {'record': {**ROW1['record'], 'storage': 'string'}}
V1 = {'record': {'revision': 'integer', 'seeds': {'sequence': ROW1}}}
V2 = {'record': {'revision': 'integer', 'seeds': {'sequence': ROW2}}}
CUTOFF = '2030-01-01T00:00:00Z'


def operation(name, pre, post, inp, value, shape, transition):
    return {'id': 'seed-bank.' + name, 'version': 'R5.33', 'input': inp,
        'state': {'pre': pre, 'post': post},
        'requires': {'equals': [ref('pre', 'revision'), lit(1 if pre == V1 else 2, 'integer')]},
        'branches': [{'tag': 'ok', 'when': lit(True, 'boolean'), 'value': copy.deepcopy(value),
                      'value_type': shape, 'transition': copy.deepcopy(transition)},
                     {'tag': 'other', 'when': None, 'value': copy.deepcopy(value),
                      'value_type': shape, 'transition': copy.deepcopy(transition)}]}


def application():
    empty = {'record': {}}
    ops = {}
    for variant, state, row in [('v1', V1, ROW1), ('v2', V2, ROW2)]:
        inp = {'record': {'code': 'string', 'label': 'string', 'harvest': {'optional': {'nullable': 'instant'}}}}
        record = {'record': {field: ref('input', field) for field in inp['record']}}
        if variant == 'v2':
            record['record']['storage'] = lit('dry')
        ops[variant + '_create'] = operation(variant + '_create', state, state, inp, lit('stored'), 'string',
            {'relations': [{'exact_frame': {'collection': 'seeds', 'identity': 'code', 'record': record}}]})
        ops[variant + '_query'] = operation(variant + '_query', state, state,
            {'record': {'filter': {'optional': {'nullable': 'integer'}}}},
            {'record': {'seeds': ref('pre', 'seeds'), 'filter': ref('input', 'filter')}},
            {'record': {'seeds': {'sequence': row}, 'filter': {'optional': {'nullable': 'integer'}}}}, {'preserve': True})
        guards = [{'present': ref('item', 'harvest')}, non_null('harvest'),
                  {'before': [ref('item', 'harvest'), lit(CUTOFF, 'instant')]}]
        # Redundant equivalent providers are intentionally part of the whole app.
        where = {'and': [copy.deepcopy(guards[0]), *copy.deepcopy(guards), copy.deepcopy(guards[1])]}
        value = {'order': {'source': {'select': {'source': ref('pre', 'seeds'), 'where': where}}, 'keys': ['harvest', 'code']}}
        ops[variant + '_early'] = operation(variant + '_early', state, state, empty, value, {'sequence': row}, {'preserve': True})
    ops['migrate'] = operation('migrate', V1, V2, empty, {'cardinality': ref('pre', 'seeds')}, 'integer',
        {'relations': [{'default_missing': {'source': ['seeds'], 'target': ['seeds'], 'identity': 'code',
                                          'field': 'storage', 'value': lit('dry')}},
                       {'post_equals': {'field': 'revision', 'value': lit(2, 'integer')}}]})
    return copy.deepcopy({'id': 'seed-bank-r539', 'state': {'versions': {'V1': V1, 'V2': V2}}, 'operations': ops})


def setup():
    app = application()
    alternatives = {}
    for version, state, number in [('V1', V1, 1), ('V2', V2, 2)]:
        alternatives[version] = {'codec': state, 'constraints': [
            {'kind': 'equals', 'path': ['revision'], 'value': number},
            {'kind': 'population', 'path': ['seeds'], 'identity': 'code', 'nonblank': ['code', 'label'],
             'domains': {'storage': ['dry', 'cold']} if version == 'V2' else {}}]}
    declaration = boundary.state_profile(app, alternatives,
        {'empty': {'version': 'V1', 'value': {'revision': 1, 'seeds': []}}})
    old = transport.specification(pipeline.checked(app))
    entries = {item['semantic']: item for item in old['operations']}
    routes = []
    for public in ('create', 'query', 'early'):
        routes.append({'public': public, 'alternatives': {
            version: {key: value for key, value in entries[prefix + '_' + public].items() if key != 'public'}
            for version, prefix in [('V1', 'v1'), ('V2', 'v2')]}})
    routes.append({'public': 'migrate', 'alternatives': {'V1': {
        key: value for key, value in entries['migrate'].items() if key != 'public'}}})
    spec = {**old, 'operations': routes, 'persistence': {'missing': 'INITIALIZE_DECLARED_STATE', 'initial': 'empty'}}
    return app, spec, declaration, launch.configuration('seed-bank.public', 'seeds.json')


def capture(app, root, cwd, spec, declaration, config, argv):
    evidence, public, before, after = launch.observe(root, cwd, config, argv)
    return {'argv': argv, 'evidence': evidence, 'public': public,
        'pre': None if before is None else before.decode(), 'post': None if after is None else after.decode(),
        'verdict': verifier.challenge(app, root, spec, declaration, config, evidence, public, before, after)}


def study():
    app, spec, declaration, config = setup()
    calls = []
    with tempfile.TemporaryDirectory() as bundle, tempfile.TemporaryDirectory() as directory:
        root, cwd = Path(bundle), Path(directory)
        profile = boundary.generate(app, root, spec, declaration, config)
        for argv in [['query'], ['create', '--code', 'S1', '--label', 'Iris', '--harvest', 'null'],
                     ['query', '--filter', 'null'], ['query', '--filter', '"3"'],
                     ['create', '--code', 'S2', '--label', 'Lily', '--harvest', '"2029-01-01T00:00:00Z"'],
                     ['early'], ['migrate'], ['query'],
                     ['create', '--code', 'S3', '--label', 'Fern'], ['early'], ['migrate'],
                     ['query', '--filter', '"bad"'], ['unknown']]:
            calls.append(capture(app, root, cwd, spec, declaration, config, argv))
        store = cwd / config['store']['path']
        saved = store.read_bytes()
        invalids = {
            'wrong_shape': {'revision': 2, 'seeds': ['bad']},
            'wrong_type': {'revision': 2, 'seeds': [{'code': 4, 'label': 'Iris', 'storage': 'dry'}]},
            'wrong_pair': {'revision': 2, 'seeds': [{'code': 'S1', 'label': 'Iris'}]},
            'wrong_row_version': {'revision': 2, 'seeds': [{'code': 'S1', 'label': 'Iris', 'storage': 1}]},
            'blank': {'revision': 2, 'seeds': [{'code': 'S1', 'label': '', 'storage': 'dry'}]},
            'domain': {'revision': 2, 'seeds': [{'code': 'S1', 'label': 'Iris', 'storage': 'wet'}]},
            'duplicate': {'revision': 2, 'seeds': [{'code': 'S1', 'label': 'Iris', 'storage': 'dry'}] * 2}}
        invalid_calls = {}
        for name, content in invalids.items():
            store.write_bytes(canonical(content))
            invalid_calls[name] = capture(app, root, cwd, spec, declaration, config, ['query'])
        store.write_bytes(saved)
        calls.append(capture(app, root, cwd, spec, declaration, config, ['query']))
    return {'source': {'application': app, 'transport': spec, 'state': declaration, 'launch': config},
            'aggregate': profile, 'calls': calls, 'invalid_populations': invalid_calls}
