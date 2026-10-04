"""Independent publication contract, actual current-entry evidence and faults."""

import copy
import json
from pathlib import Path
import tempfile

from benchmark.semantic import current_pipeline as pipeline
from benchmark.semantic import checked_transport_r5_35 as transport
from benchmark.semantic import checked_launch_r5_36 as launch
from benchmark.semantic.refined_generator_r5_28 import canonical, sha

EARLY = '2030-01-01T00:00:00Z'
CUTOFF = '2030-02-01T00:00:00Z'
LATE = '2030-03-01T00:00:00Z'


def ref(*path):
    return {'ref': list(path)}


def lit(value, shape='string'):
    return {'literal': {'value': value, 'type': shape}}


def non_null(field, base='instant', slot='item'):
    return {'not': {'equals': [ref(slot, field), lit(None, {'nullable': base})]}}


def selected(field='embargo', base='instant', relation=None):
    guard = non_null(field, base)
    predicate = guard if relation is None else {'and': [relation, guard]}
    return {'select': {'source': ref('pre'), 'where': predicate}}


def application():
    row = {'record': {'code': 'string', 'edition': 'integer',
        'embargo': {'nullable': 'instant'}, 'released': {'nullable': 'instant'},
        'caption': {'nullable': 'string'}, 'rating': {'nullable': 'integer'},
        'reviewed': {'optional': 'instant'}, 'window': {'optional': {'nullable': 'instant'}},
        'label': 'string', 'note': 'string'}}
    state = {'sequence': row}
    yes = {'equals': [lit(1, 'integer'), lit(1, 'integer')]}
    before = {'before': [ref('item', 'embargo'), ref('input', 'cutoff')]}
    operations = {}

    def operation(name, value, shape=state, transition=None, when=yes):
        operations[name] = {'id': 'publication.' + name, 'version': 'R5.27',
            'input': {'record': {'cutoff': 'instant', 'preferred': {'optional': 'string'}}},
            'state': state, 'branches': [
                {'tag': 'ok', 'when': when, 'value': value, 'value_type': shape,
                 'transition': transition or {'preserve': True}},
                {'tag': 'unavailable', 'when': None, 'value': lit('unavailable'),
                 'value_type': 'string', 'transition': {'preserve': True}}]}

    operation('earlier', selected(relation=before))
    operation('ordered', {'order': {'source': selected(), 'keys': ['embargo', 'code']}})
    operation('reviewed', {'select': {'source': ref('pre'), 'where': {'and': [
        {'before': [ref('item', 'reviewed'), ref('input', 'cutoff')]},
        {'present': ref('item', 'reviewed')}]}}})
    operation('window', {'order': {'source': {'select': {'source': ref('pre'), 'where': {'and': [
        {'before': [ref('item', 'window'), ref('input', 'cutoff')]}, non_null('window'),
        {'present': ref('item', 'window')}]}}}, 'keys': ['window', 'code']}})
    operation('caption', selected('caption', 'string', {'nonblank': ref('item', 'caption')}))
    operation('rating', selected('rating', 'integer', {'equals': [ref('item', 'rating'), lit(3, 'integer')]}))
    targets = selected(relation={'and': [before, {'equals': [ref('item', 'code'), lit('a')]}]})
    match = {'project': {'row': {'sole': targets}, 'fields': ['code']}}
    # A selected/refined row participates in keyed targeting through existing
    # sole/record equality. No predicate-specific write primitive is introduced.
    target_code = ref('input', 'preferred')
    # match remains a string: sole over a projected collection is not an
    # existing construct, so use the existing sole record equality as a guard.
    eligible = {'equals': [match, {'record': {'code': lit('a')}}]}
    operation('replace', ref('post'), transition={'relations': [{'replace_field': {
        'collection': None, 'key': 'code', 'match': lit('a'), 'field': 'label',
        'value': {'fallback': {'value': target_code, 'default': lit('released')}}}}]}, when=eligible)
    operation('remove', ref('post'), transition={'relations': [{'remove': {
        'collection': None, 'identity': 'code', 'match': lit('a')}}]}, when=eligible)
    return json.loads(json.dumps({'id': 'publication.nullable.coherence', 'state': state, 'operations': operations}))


def population():
    rows = []
    for code, instant, edition in [('null', None, 0), ('b', EARLY, 1), ('a', EARLY, 2),
                                    ('equal', CUTOFF, 3), ('later', LATE, 4)]:
        row = {'code': code, 'edition': edition, 'embargo': instant, 'released': LATE,
               'caption': None if instant is None else ' public ',
               'rating': None if instant is None else 3,
               'label': 'old', 'note': 'preserved'}
        if code != 'null':
            row['reviewed'] = instant
            row['window'] = instant
        rows.append(row)
    rows.append({**rows[0], 'code': 'present-null', 'window': None})
    return rows


def setup(model=None):
    model = application() if model is None else model
    plans = pipeline.checked(model)
    spec = transport.specification(plans)
    declaration = transport.state_profile(model)
    return model, spec, declaration, launch.configuration('publication.public')


def capture(model, root, operation, inp):
    event, public, before, after = pipeline.observe(root, operation, inp)
    return {'event': event, 'public': public, 'pre': before.decode(), 'post': after.decode(),
            'verdict': pipeline.challenge(model, root, event, public, before, after)}


def inject(root, fault):
    """Disposable artifact faults, honestly resealed to isolate semantics."""
    path = root / 'operation.py'
    source = path.read_text(encoding='utf-8')
    # Checked scheduling deliberately puts the guard first.
    old = "if ((not (_element_1['embargo'] == None)) and instant_lt(_element_1['embargo'], input['cutoff']))"
    if fault == 'A':
        new = "if (_element_1['embargo'] is None or instant_lt(_element_1['embargo'], input['cutoff']))"
        if old not in source:
            raise ValueError('nullable predicate injection drift')
        source = source.replace(old, new)
    elif fault == 'B':
        source = source.replace(old, old + " and _element_1['code'] != 'a'")
    elif fault == 'C':
        source = source.replace("if (not (_element_1['embargo'] == None))", 'if True')
        source = source.replace("instant_key(_order_key_1['embargo'])",
                                "instant_key(_order_key_1['embargo'] or '1900-01-01T00:00:00Z')")
    else:
        raise ValueError('unknown fault')
    path.write_bytes(source.encode())
    manifest = json.loads((root / 'provenance.json').read_bytes())
    manifest['artifact'] = sha(path.read_bytes())
    manifest.pop('generation')
    manifest['generation'] = sha(canonical(manifest))
    (root / 'provenance.json').write_bytes(canonical(manifest))


def study():
    model = application()
    report = {'version': 'R5.38', 'source': model, 'population': population(), 'calls': {}, 'faults': {}, 'mutations': {}}
    inp = {'cutoff': CUTOFF}
    with tempfile.TemporaryDirectory() as folder:
        root = Path(folder)
        report['manifest'] = pipeline.generate(model, root)
        for operation in model['operations']:
            (root / 'state.json').write_bytes(canonical(population()))
            report['calls'][operation] = capture(model, root, operation, inp)
    for fault, operation in [('A', 'earlier'), ('B', 'earlier'), ('C', 'ordered')]:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            pipeline.generate(model, root)
            inject(root, fault)
            (root / 'state.json').write_bytes(canonical(population()))
            report['faults'][fault] = capture(model, root, operation, inp)
    for name in ('cutoff', 'field', 'secondary', 'write_field', 'relation'):
        changed = copy.deepcopy(model)
        operation = 'earlier'
        value = changed['operations']['earlier']['branches'][0]['value']
        if name == 'cutoff':
            value['select']['where']['and'][0]['before'][1] = lit(LATE, 'instant')
        elif name == 'field':
            value['select']['where'] = {'and': [non_null('released'),
                {'before': [ref('item', 'released'), ref('input', 'cutoff')]}]}
        elif name == 'secondary':
            operation = 'ordered'
            changed['operations']['ordered']['branches'][0]['value']['order']['keys'] = ['embargo', 'edition']
        elif name == 'write_field':
            operation = 'replace'
            changed['operations']['replace']['branches'][0]['transition']['relations'][0]['replace_field']['field'] = 'note'
        else:
            value['select']['where']['and'][0] = {'before': [ref('input', 'cutoff'), ref('item', 'embargo')]}
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            pipeline.generate(changed, root)
            (root / 'state.json').write_bytes(canonical(population()))
            report['mutations'][name] = capture(changed, root, operation, inp)
    return report
