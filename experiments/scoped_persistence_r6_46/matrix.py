"""Requirement-derived fixtures; does not import candidate or production code."""
import copy
import json

UID = '00000000-0000-4000-8000-000000000001'
R = dict(id=UID, created_at='2040-01-01T00:00:00Z', label=' kiln ',
         phase='cold', vent='closed', load='emergency')


def fixtures():
    rows = []
    opened = dict(R, vent='open', load='ordinary')
    firing = dict(R, phase='firing')
    bad = dict(firing, load='ordinary')

    def step(op='list', args=None, expected=None, state=None, unchanged=True):
        return dict(op=op, args=args or {}, expected=expected or {'error': 'invalid_state'},
                    state=copy.deepcopy(state), unchanged=unchanged)

    def row(key, initial, steps, absent=False, variant='default'):
        raw = None if absent else (json.dumps(initial, indent=1) + '\n').encode('utf-8').hex()
        rows.append(dict(id=key, variant=variant, initial_hex=raw, steps=steps))

    def invalid(key, value, requests=None, variant='default'):
        row(key, value, [step(op, args, state=value) for op, args in
                        (requests or [('list', {})])], variant=variant)

    invalid('K01', {}, [('list', {}), ('ignite', {'id': UID}), ('set_gate', {'id': UID})])
    invalid('K02', [{k: v for k, v in R.items() if k != 'label'}])
    invalid('K03', [{}])
    row('K04', [], [step(expected={'ok': []}, state=[])])
    row('K05', [opened], [step(expected={'ok': [opened]}, state=[opened])])
    row('K06', [firing], [step(expected={'ok': [firing]}, state=[firing]),
        step('cool', {'id': UID}, {'ok': R}, [R], False)])
    invalid('K07', [bad])
    invalid('K08', dict(schema_version=99, records=[R]))
    invalid('K09', dict(schema_version=1))
    invalid('K10', dict(schema_version=1, records=[R]))
    for name, value in [('label', 0), ('phase', None), ('vent', [])]:
        invalid('K11', [dict(R, **{name: value})], variant=name)
    for name, value in [('null', None), ('number', 0), ('string', 'store')]:
        invalid('K12', value, variant=name)
    row('K13', None, [step(expected={'ok': []}, state=None)], absent=True)
    invalid('K14', [bad], [('set_gate', dict(id='missing', value='bogus'))])
    invalid('K15', [bad], [('ignite', {'id': UID})])
    row('K16', [firing], [step('set_gate', dict(id='missing', value='bogus'),
        {'error': 'not_found'}, [firing])])
    ordinary_firing = dict(opened, phase='firing')
    row('K17', [ordinary_firing], [step('set_gate', dict(id=UID, value='closed'),
        {'error': 'gate_locked'}, [ordinary_firing])])
    row('K18', [firing], [step('set_gate', dict(id=UID, value='bogus'),
        {'error': 'invalid_input'}, [firing])])
    assert len({r['id'] for r in rows}) == 18
    assert sum(len(r['steps']) for r in rows) == 25
    return rows
