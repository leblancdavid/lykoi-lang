"""Minimum B/C deterministic generators. C uses existing production semantics."""
import copy
import json
import sys
from pathlib import Path
from schema_check import check

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT))


def value_type(t):
    return dict(type=t['type'], domain=t['domain'], nullable=False)


def predicate(e):
    if e['op'] == 'eq':
        def operand(o):
            return dict(kind=o['kind'], type=value_type(o), **({'value': o['value']} if o['kind'] == 'literal' else {'name': o['value']}))
        return dict(kind='compare', result_type='boolean', operator='eq', left=operand(e['left']),
                    right=operand(e['right']), policy=dict(case='sensitive', normalization='none'), nulls='false')
    if e['op'] == 'not':
        return dict(kind='not', result_type='boolean', child=predicate(e['child']))
    return dict(kind=e['op'], result_type='boolean', children=[predicate(x) for x in e['children']])


def lower(intent):
    from lykoi_pipeline.scalar_profile import lower as scalar_lower
    from air_compiler.mutable_values import compose
    scalar = dict(storage=dict(path=intent['storage'], version=1, missing='empty_collection', write='atomic', rejection='unchanged'),
        fields=[dict(name=n, **t, nullable=False, preservation='verbatim') for n, t in intent['fields'].items()],
        creation=dict(command='create', bindings=[dict(field=n, **b, default=None) for n, b in intent['create']['bindings'].items()],
                      validation=[dict(field=n, rule='nonblank', error='invalid_label') for n in intent['create']['nonblank']]),
        listing=dict(command='list', order=['created_at', 'id'], result='whole_records'), lifecycle=[], evolution=[])
    base = scalar_lower(scalar)
    next(i for i in base['invariants'] if i['id'] == 'valid')['field_rules'] = [
        dict(field='field:' + n, kind='nonblank') for n in intent['create']['nonblank']]
    mutations = []
    for command, m in intent['operations'].items():
        changes = []
        for n, w in m['writes'].items():
            common = dict(field=n, operation='replace', pipeline=[], invalid_error='invalid_input')
            if w['source'] == 'literal':
                common['source'] = dict(kind='literal', type=value_type(intent['fields'][n]), value=w['value'])
            else:
                common.update(input=w['value'], omitted='reject', missing_error='invalid_input')
            changes.append(common)
        mutations.append(dict(command=command, lookup='id', missing_error='not_found', changes=changes,
            guards=[dict(predicate=predicate(g['condition']), error=g['error']) for g in m['guards']],
            effect=dict(atomicity='single_record', persistence='atomic', rejection='unchanged')))
    facts = dict(collections=[], mutations=mutations, creation_pipelines=[],
        predicate_semantics=dict(booleans=[], guards=[], invariants=[dict(predicate=predicate(e), error='invalid_state') for e in intent['invariants']]))
    return compose(base, facts)


C_WRAPPER = '''
def handle(op, args, providers):
    try:
        mutation = next((m for m in MUTABLE['facts']['mutations'] if m['command'] == op), None)
        if mutation is not None:
            result = execute_mutation(mutation, args)
        else:
            command = next(c for c in SPEC['commands'] if c['token'] == op)
            behavior = by_id('behaviors', command['behavior'])
            inputs = {i['id']: args[i['name']] for i in behavior['inputs'] if i['name'] in args}
            result = execute(behavior, inputs, providers=providers if op == 'create' else {})
        return {'ok': result}
    except Failure as e:
        return {'error': e.code}
'''


def generate(intent, track):
    check(intent)
    if track == 'B':
        return (HERE / 'b_runtime.py').read_text().replace('INTENT = {}  # deterministic insertion', 'INTENT = ' + repr(intent)), None
    if track != 'C':
        raise ValueError('generator track')
    from air_compiler.profiles import generate_mutable
    ir = lower(intent)
    return generate_mutable(ir, []) + C_WRAPPER, ir


if __name__ == '__main__':
    intent = json.loads(Path(sys.argv[2]).read_text())
    source, ir = generate(intent, sys.argv[1])
    destination = Path(sys.argv[3])
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open('x', encoding='utf-8', newline='\n') as f:
        f.write(source)
    if ir:
        with destination.with_suffix('.ir.json').open('x', encoding='utf-8', newline='\n') as f:
            json.dump(ir, f, indent=2)
            f.write('\n')
