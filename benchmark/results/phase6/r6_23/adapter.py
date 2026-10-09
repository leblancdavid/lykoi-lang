"""construct-1: deterministic syntax adapter, no new execution meaning."""
import copy
import json
from pathlib import Path
import sys
import time

import jsonschema

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT / 'experiments/typed_composition_r6_18'))
import composition as c


def obj(props):
    return dict(type='object', properties=props, required=list(props), additionalProperties=False)


def schemas():
    name = dict(type='string', pattern='^[A-Za-z][A-Za-z0-9_]{0,31}$')
    typ = dict(enum=['Int64', 'Bool', 'Unit'])
    arg = dict(oneOf=[dict(type='integer', minimum=-(2**63), maximum=2**63-1),
        dict(type='boolean'), dict(type='null'), dict(type='string', pattern='^\\$[A-Za-z][A-Za-z0-9_]{0,31}$')])
    def tup(items):
        return dict(type='array', prefixItems=items, minItems=len(items), maxItems=len(items), items=False)
    expr = dict(oneOf=[arg, tup([dict(enum=['add', 'le', 'eq']), {'$ref': '#/$defs/expr'}, {'$ref': '#/$defs/expr'}])])
    deps = dict(type='array', items=name, maxItems=32, uniqueItems=True)
    operation = dict(oneOf=[tup([name, {'const': 'value'}, typ, {'$ref': '#/$defs/expr'}, deps]),
        tup([name, {'const': 'check'}, {'$ref': '#/$defs/expr'}, {'$ref': '#/$defs/expr'}, name, deps]),
        tup([name, {'const': 'compose'}, name, dict(type='object', propertyNames=name, additionalProperties=arg, maxProperties=8), deps]),
        tup([name, {'const': 'atom'}]), tup([name, {'const': 'end'}])])
    repeat = obj(dict(repeat=dict(type='integer', minimum=1, maximum=4),
        body=dict(type='array', items={'$ref': '#/$defs/operation'}, minItems=1, maxItems=8)))
    definition = obj(dict(name=name, inputs=dict(type='array', items=tup([name, typ]), maxItems=8),
        ops=dict(type='array', items=dict(oneOf=[{'$ref': '#/$defs/operation'}, repeat]), minItems=1, maxItems=32),
        result={'$ref': '#/$defs/expr'}, result_type=typ))
    compact = obj(dict(version={'const': 'construct-1'}, definitions=dict(type='array', items=definition, minItems=1, maxItems=7), target=name))
    compact.update({'$schema': 'https://json-schema.org/draft/2020-12/schema', '$defs': dict(expr=expr, operation=operation)})
    full = json.loads((ROOT / 'experiments/typed_composition_r6_18/typed-composition-1.schema.json').read_text())
    full['$defs']['definition']['required'].remove('identity')
    del full['$defs']['definition']['properties']['identity']
    full['$defs']['definition']['properties']['dependencies']['additionalProperties'] = {'const': 'AUTO'}
    # Replace cryptographic fields only: semantic dependency declarations remain explicit.
    nodes = full['$defs']['node']['oneOf']
    compose = next(n for n in nodes if n['properties']['op'].get('const') == 'compose')
    compose['properties']['identity'] = {'const': 'AUTO'}
    complete = obj(dict(definitions=dict(type='array', items={'$ref': '#/$defs/definition'}, minItems=1, maxItems=7), target=name))
    complete.update({'$schema': full['$schema'], '$defs': full['$defs']})
    for s in (compact, complete):
        jsonschema.Draft202012Validator.check_schema(s)
    return {'A': complete, 'B': compact}


def compact_expr(x, aliases):
    if type(x) in (int, bool) or x is None:
        return {'const': x}
    if type(x) is str and x.startswith('$'):
        alias = x[1:]
        if alias not in aliases:
            c.fail('UNKNOWN_REFERENCE', '$/compact', alias)
        return {'ref': aliases[alias]}
    if type(x) is list and len(x) == 3 and x[0] in ('add', 'le', 'eq'):
        return {x[0]: [compact_expr(y, aliases) for y in x[1:]]}
    c.fail('UNSUPPORTED', '$/compact/expression', 'literal/ref/binary expression only')


def compact_defs(value):
    signatures = {}
    for d in value['definitions']:
        if d['name'] in signatures:
            c.fail('CAPTURE', '$/definitions', d['name'])
        signatures[d['name']] = d
    definitions = []
    maps = {}
    for d in value['definitions']:
        aliases = {}
        env = {}
        for name, typ in d['inputs']:
            if name in aliases:
                c.fail('CAPTURE', d['name'], name)
            aliases[name] = name
            env[name] = typ
        steps = []
        symbols = set()
        mapping = []
        def append(op, local, scope):
            alias, action = op[:2]
            if alias in local:
                c.fail('CAPTURE', scope, alias)
            sid = 's' + str(len(steps) + 1).zfill(3)
            if sid in env:
                c.fail('CAPTURE', scope, 'generated identifier collides with input')
            used = set()
            def expression(x):
                e = compact_expr(x, local)
                typ, refs = c.expression(e, env, scope)
                used.update(refs)
                return e, typ
            if action == 'value':
                _, _, declared, x, deps = op
                expr, inferred = expression(x)
                if declared != inferred:
                    c.fail('TYPE', scope, 'declared value type differs')
                node = dict(op='value', expr=expr)
            elif action == 'check':
                _, _, x, site, code, deps = op
                test, typ = expression(x)
                loc, _ = expression(site)
                if typ != 'Bool':
                    c.fail('TYPE', scope, 'check test must be Bool')
                inferred = 'Unit'
                node = dict(op='check', test=test, site=loc, code=code)
            elif action == 'compose':
                _, _, symbol, args, deps = op
                if symbol not in signatures:
                    c.fail('UNKNOWN_SYMBOL', scope, symbol)
                target = signatures[symbol]
                if set(args) != {p[0] for p in target['inputs']}:
                    c.fail('SHAPE', scope, 'exact argument names')
                built = {}
                for name, typ in target['inputs']:
                    e, inferred_arg = expression(args[name])
                    if typ != inferred_arg:
                        c.fail('TYPE', scope, 'argument ' + name)
                    built[name] = e
                inferred = target['result_type']
                symbols.add(symbol)
                node = dict(op='compose', symbol=symbol, identity='AUTO', args=built)
            elif action == 'atom':
                inferred, deps, node = 'Int64', [], dict(op='atom', codec='uint8')
            elif action == 'end':
                inferred, deps, node = 'Unit', [], dict(op='end')
            else:
                c.fail('UNSUPPORTED', scope, action)
            if any(dep not in local for dep in deps):
                c.fail('UNKNOWN_REFERENCE', scope, 'dependency not declared earlier')
            resolved = [local[dep] for dep in deps]
            if set(resolved) != used:
                c.fail('DEPENDENCY', scope, 'explicit compact dependencies must be exact')
            steps.append(dict(id=sid, type=inferred, deps=resolved, node=node))
            local[alias] = sid
            env[sid] = inferred
            mapping.append(dict(scope=scope, alias=alias, generated=sid))
            if len(steps) > 32:
                c.fail('RESOURCE', d['name'], 'expanded assembly exceeds32 steps')
        for i, op in enumerate(d['ops']):
            if type(op) is dict:
                for iteration in range(op['repeat']):
                    local = aliases.copy()
                    for child in op['body']:
                        append(child, local, d['name'] + '/repeat' + str(i) + '/' + str(iteration))
            else:
                append(op, aliases, d['name'])
        result = compact_expr(d['result'], aliases)
        typ, _ = c.expression(result, env, d['name'] + '/result')
        if typ != d['result_type']:
            c.fail('TYPE', d['name'], 'result type differs')
        definitions.append(dict(name=d['name'], revision=1,
            params=[dict(name=n, type=t) for n, t in d['inputs']], dependencies={s: 'AUTO' for s in sorted(symbols)},
            steps=steps, order=[s['id'] for s in steps], result=result, result_type=d['result_type']))
        maps[d['name']] = mapping
    return definitions, maps


def seal_all(definitions):
    registry = {}
    for d in definitions:
        if d['name'] in registry:
            c.fail('CAPTURE', '$/definitions', d['name'])
        registry[d['name']] = copy.deepcopy(d)
    active = set()
    sealed = {}
    def seal(name):
        if name in sealed:
            return sealed[name]
        if name not in registry:
            c.fail('UNKNOWN_SYMBOL', '$/dependencies', name)
        if name in active:
            c.fail('CYCLE', '$/dependencies', name)
        active.add(name)
        d = registry[name]
        for symbol in d['dependencies']:
            d['dependencies'][symbol] = seal(symbol)['identity']
        for s in d['steps']:
            node = s['node']
            if node['op'] == 'compose':
                if node['symbol'] not in d['dependencies']:
                    c.fail('DEPENDENCY', name, 'call omitted from declared symbolic dependencies')
                node['identity'] = d['dependencies'][node['symbol']]
        sealed[name] = c.seal(d)
        active.remove(name)
        return sealed[name]
    for name in registry:
        seal(name)
    return [sealed[d['name']] for d in definitions]


def package(artifact, args):
    registry = {d['name']: d for d in artifact['definitions']}
    target = registry[artifact['target']]
    if set(args) != {p['name'] for p in target['params']}:
        c.fail('SHAPE', '$/arguments', 'exact target input signature')
    program = c.seal(dict(name='HostEntry', revision=1, params=[],
        dependencies={target['name']: target['identity']},
        steps=[dict(id='invocation', type=target['result_type'], deps=[], node=dict(op='compose', symbol=target['name'],
            identity=target['identity'], args={k: {'const': v} for k, v in args.items()}))],
        order=['invocation'], result={'ref': 'invocation'}, result_type='Int64'))
    return dict(version=c.VERSION, foundation=c.FOUNDATION, definitions=artifact['definitions'], program=program)


def construct(text, track):
    times = dict(serialization_seconds=0, schema_seconds=0, construction_seconds=0, validation_seconds=0)
    result = dict(json_valid=False, strict_valid=False, schema_valid=False, constructed=False,
                  typed_valid=False, diagnostic=None, times=times)
    phase = 'serialization_seconds'
    try:
        start = time.perf_counter()
        json.loads(text)
        result['json_valid'] = True
        value = c.load(text)
        result['strict_valid'] = True
        times['serialization_seconds'] = time.perf_counter() - start
        start = time.perf_counter()
        phase = 'schema_seconds'
        schema = json.loads((HERE / ('complete.schema.json' if track == 'A' else 'compact.schema.json')).read_text())
        jsonschema.Draft202012Validator(schema).validate(value)
        result['schema_valid'] = True
        times['schema_seconds'] = time.perf_counter() - start
        start = time.perf_counter()
        phase = 'construction_seconds'
        if track == 'B':
            definitions, mapping = compact_defs(value)
        else:
            definitions, mapping = value['definitions'], {}
        if value['target'] not in {d['name'] for d in definitions}:
            c.fail('UNKNOWN_SYMBOL', '$/target', value['target'])
        if 'HostEntry' in {d['name'] for d in definitions}:
            c.fail('CAPTURE', '$/definitions', 'reserved host adapter name')
        artifact = dict(definitions=seal_all(definitions), target=value['target'], identifier_map=mapping)
        result.update(constructed=True, artifact=artifact)
        times['construction_seconds'] = time.perf_counter() - start
        # Dummy typed literals qualify full definitions without guessing acceptance inputs.
        target = next(d for d in artifact['definitions'] if d['name'] == artifact['target'])
        dummy = {p['name']: {'Int64': 0, 'Bool': False, 'Unit': None}[p['type']] for p in target['params']}
        start = time.perf_counter()
        phase = 'validation_seconds'
        c.validate(package(artifact, dummy))
        times['validation_seconds'] = time.perf_counter() - start
        result['typed_valid'] = True
    except (ValueError, jsonschema.ValidationError, c.Diagnostic) as e:
        times[phase] = time.perf_counter() - start
        result['diagnostic'] = e.data if isinstance(e, c.Diagnostic) else dict(code='SCHEMA' if isinstance(e, jsonschema.ValidationError) else 'JSON', detail=str(e)[:1500])
    return result
