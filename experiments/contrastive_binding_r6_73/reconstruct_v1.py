"""Strict experiment-local renderer; authoritative semantics imported unchanged."""
import copy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'experiments/incremental_scorer_r6_65'))
import scorer

c, assembly = scorer.c, scorer.assembly


class Rejection(Exception):
    def __init__(self, category, code, detail):
        self.category, self.code, self.detail = category, code, detail
        super().__init__(detail)


def reject(code, detail):
    raise Rejection('schema_rejection', code, detail)


def exact(value, keys, location):
    if type(value) is not dict or set(value) != set(keys):
        reject('FIELDS', location + ': exact fields required')


def parse(text):
    try:
        obj = c.load(text)
    except c.Diagnostic as exc:
        raise Rejection('schema_rejection', 'SERIALIZATION', str(exc.data)) from exc
    exact(obj, ('op', 'left', 'right', 'deps'), 'decision')
    if type(obj['op']) is not str or obj['op'] not in ('add', 'le', 'eq'):
        reject('OPERATION', 'unknown operation')
    deps = obj['deps']
    if (type(deps) is not list or len(deps) > 2 or any(type(d) is not str for d in deps)
            or len(set(deps)) != len(deps) or deps != sorted(deps)):
        reject('DEPENDENCIES', 'zero to two sorted distinct identities required')
    args = []
    for key in ('left', 'right'):
        arg = obj[key]
        if type(arg) is not dict or set(arg) not in ({'ref'}, {'literal'}):
            reject('OPERAND', 'exact reference or typed literal required')
        if 'ref' in arg:
            if type(arg['ref']) is not str or not arg['ref']:
                reject('REFERENCE', 'nonempty exact identity required')
            args.append(copy.deepcopy(arg))
        else:
            literal = arg['literal']
            exact(literal, ('type', 'value'), key + '/literal')
            typ, value = literal['type'], literal['value']
            if type(typ) is not str or typ not in ('Int64', 'Bool', 'Unit'):
                reject('LITERAL_TYPE', 'unknown literal type')
            if not ((typ == 'Int64' and type(value) is int and -(2**63) <= value < 2**63)
                    or (typ == 'Bool' and type(value) is bool)
                    or (typ == 'Unit' and value is None)):
                reject('LITERAL_TYPE', 'value does not inhabit declared literal type')
            args.append({'const': value})
    return obj, args


def reconstruct(text, scope):
    original = c.canonical(scope)
    obj, args = parse(text)
    try:
        assembly.check_before(scope)
        names = [p['name'] for p in scope['params']] + [s['id'] for s in scope['steps']]
        if len(names) != len(set(names)):
            raise Rejection('semantic_rejection', 'AMBIGUOUS_SCOPE', 'reference identity collision')
        env = {p['name']: p['type'] for p in scope['params']}
        env.update({s['id']: s['type'] for s in scope['steps']})
        expr = {obj['op']: args}
        inferred, refs = c.expression(expr, env, '$/compact-decision')
        if obj['deps'] != sorted(refs):
            raise Rejection('semantic_rejection', 'DEPENDENCY', 'explicit dependencies must equal selected direct reference set')
        action = dict(id='selected', type=inferred, deps=copy.deepcopy(obj['deps']),
                      node=dict(op='value', expr=expr))
        scorer.validate_action(action)
        after, validation = assembly.apply(scope, action)
    except c.Diagnostic as exc:
        raise Rejection('semantic_rejection', exc.data['code'], str(exc.data)) from exc
    assert c.canonical(scope) == original
    return action, after, validation


def serialize(obj):
    import json
    return json.dumps(obj, separators=(',', ':'), ensure_ascii=True, allow_nan=False)
