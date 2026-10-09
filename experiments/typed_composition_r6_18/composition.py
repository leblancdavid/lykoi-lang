"""Typed composition 1: closed, bounded hygienic templates over the frozen VM."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
VM_PATH = HERE.parent / 'semantic_interpreter/interpreter.py'
spec = importlib.util.spec_from_file_location('r6_18_frozen_vm', VM_PATH)
vm = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = vm
spec.loader.exec_module(vm)
FOUNDATION = hashlib.sha256(VM_PATH.read_bytes()).hexdigest()
VERSION = 'typed-composition-1'
TYPES = {'Int64', 'Bool', 'Unit'}
NAME = re.compile(r'[A-Za-z][A-Za-z0-9_]{0,31}\Z')
HEX = re.compile(r'[0-9a-f]{64}\Z')
MAX_BYTES = 65536


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True,
                      allow_nan=False).encode('ascii')


def identity(definition):
    return hashlib.sha256(canonical({'version': VERSION, 'foundation': FOUNDATION,
        'definition': {k: v for k, v in definition.items() if k != 'identity'}})).hexdigest()


def seal(definition):
    result = copy.deepcopy(definition)
    result['identity'] = identity(result)
    return result


class Diagnostic(ValueError):
    def __init__(self, code, path, detail):
        self.data = {'code': code, 'path': path, 'detail': detail}
        super().__init__(str(self.data))


def fail(code, path, detail):
    raise Diagnostic(code, path, detail)


def shape(value, keys, path):
    if type(value) is not dict or set(value) != set(keys):
        fail('SHAPE', path, 'exact object fields required: ' + ','.join(sorted(keys)))


def name(value, path):
    if type(value) is not str or not NAME.fullmatch(value):
        fail('REFERENCE', path, 'case-sensitive ASCII identifier required')


def digest(value, path):
    if type(value) is not str or not HEX.fullmatch(value):
        fail('IDENTITY', path, 'SHA256 required')


def typename(value, path):
    if type(value) is not str or value not in TYPES:
        fail('TYPE', path, 'unsupported type')


def load(text):
    """Strict bounded JSON boundary: duplicate keys and noninteger numbers reject."""
    if type(text) is not str or len(text.encode('utf-8')) > MAX_BYTES:
        fail('RESOURCE', '$', 'serialized input exceeds 64KiB')

    def pairs(items):
        out = {}
        for k, v in items:
            if k in out:
                fail('SERIALIZATION', '$', 'duplicate object key: ' + k)
            out[k] = v
        return out

    def bad_number(_):
        fail('SERIALIZATION', '$', 'noninteger JSON number')

    try:
        value = json.loads(text, object_pairs_hook=pairs, parse_float=bad_number,
                           parse_constant=bad_number)
        _tree_bound(value)
        return value
    except Diagnostic:
        raise
    except (ValueError, RecursionError, UnicodeError) as exc:
        fail('SERIALIZATION', '$', type(exc).__name__)


def _tree_bound(value):
    active = set()
    count = 0

    def visit(x, depth):
        nonlocal count
        count += 1
        if count > 8192 or depth > 24:
            fail('RESOURCE', '$', 'representation tree bound')
        if type(x) in (dict, list):
            if id(x) in active:
                fail('SHAPE', '$', 'cyclic host object')
            active.add(id(x))
            if type(x) is dict and any(type(k) is not str for k in x):
                fail('SHAPE', '$', 'string object keys required')
            for child in (x.values() if type(x) is dict else x):
                visit(child, depth + 1)
            active.remove(id(x))
        elif x is not None and type(x) not in (int, bool, str):
            fail('SHAPE', '$', 'JSON domain required')
        elif type(x) is str and len(x) > 256:
            fail('RESOURCE', '$', 'string bound')
        elif type(x) is int and not -(2**63) <= x < 2**63:
            fail('TYPE', '$', 'signed64 integer domain')

    visit(value, 0)
    if len(canonical(value)) > MAX_BYTES:
        fail('RESOURCE', '$', 'representation exceeds 64KiB')


def expression(expr, env, path, depth=0):
    if depth > 8:
        fail('RESOURCE', path, 'expression depth')
    if type(expr) is not dict or len(expr) != 1:
        fail('SHAPE', path, 'one expression operation required')
    op, arg = next(iter(expr.items()))
    if op == 'const':
        if arg is None:
            return 'Unit', set()
        if type(arg) is bool:
            return 'Bool', set()
        if type(arg) is int and -(2**63) <= arg < 2**63:
            return 'Int64', set()
        fail('TYPE', path, 'literal domain')
    if op == 'ref':
        name(arg, path)
        if arg not in env:
            fail('UNKNOWN_REFERENCE', path, arg)
        return env[arg], {arg}
    if op not in {'add', 'le', 'eq'}:
        fail('UNSUPPORTED', path, str(op))
    if type(arg) is not list or len(arg) != 2:
        fail('SHAPE', path, 'binary expression required')
    left, a = expression(arg[0], env, path + '/0', depth + 1)
    right, b = expression(arg[1], env, path + '/1', depth + 1)
    if left != right or (op != 'eq' and left != 'Int64'):
        fail('TYPE', path, 'exact compatible operands required')
    return ('Int64' if op == 'add' else 'Bool'), a | b


def _acyclic(graph, path):
    done, active = set(), set()

    def walk(key, depth):
        if key in active:
            fail('CYCLE', path, key)
        if key in done:
            return
        if depth > 16:
            fail('RESOURCE', path, 'dependency depth')
        active.add(key)
        for dep in sorted(graph[key]):
            walk(dep, depth + 1)
        active.remove(key)
        done.add(key)

    for key in sorted(graph):
        walk(key, 0)


def validate(package):
    """First structured diagnostic wins; validation never invokes model inference."""
    _tree_bound(package)
    shape(package, {'version', 'foundation', 'definitions', 'program'}, '$')
    if package['version'] != VERSION or package['foundation'] != FOUNDATION:
        fail('FOUNDATION', '$', 'version/foundation mismatch')
    defs = package['definitions']
    if type(defs) is not list or len(defs) > 8:
        fail('RESOURCE', '$/definitions', 'at most eight definitions')
    all_defs = defs + [package['program']]
    registry = {}
    for d in all_defs:
        shape(d, {'name', 'revision', 'identity', 'params', 'dependencies', 'steps',
                  'order', 'result', 'result_type'}, '$/definition')
        name(d['name'], '$/name')
        if d['name'] in registry:
            fail('CAPTURE', '$/name', 'duplicate family/program name')
        registry[d['name']] = d
        if type(d['revision']) is not int or d['revision'] != 1:
            fail('SHAPE', d['name'], 'revision 1 only')
        digest(d['identity'], d['name'])
        typename(d['result_type'], d['name'])
        if type(d['params']) is not list or len(d['params']) > 8:
            fail('SHAPE', d['name'], 'parameter list required')
        for p in d['params']:
            shape(p, {'name', 'type'}, d['name'])
            name(p['name'], d['name'])
            typename(p['type'], d['name'])
        if type(d['dependencies']) is not dict or len(d['dependencies']) > 8:
            fail('SHAPE', d['name'], 'dependency pins object required')
        for dep, pin in d['dependencies'].items():
            name(dep, d['name'])
            digest(pin, d['name'])
    library = {d['name']: d for d in defs}
    graph = {d['name']: set(d['dependencies']) for d in all_defs}
    for d in all_defs:
        for dep in sorted(d['dependencies']):
            if dep not in library:
                fail('UNKNOWN_SYMBOL', d['name'], dep)
    _acyclic(graph, '$/dependencies')
    if package['program']['params'] != [] or package['program']['result_type'] != 'Int64':
        fail('TYPE', '$/program', 'closed Int64 program required')
    total_steps = 0
    for d in all_defs:
        path = d['name']
        if type(d['params']) is not list or len(d['params']) > 8:
            fail('SHAPE', path, 'parameter list required')
        env = {}
        for p in d['params']:
            shape(p, {'name', 'type'}, path)
            name(p['name'], path)
            typename(p['type'], path)
            if p['name'] in env:
                fail('CAPTURE', path, p['name'])
            env[p['name']] = p['type']
        params = set(env)
        steps = d['steps']
        if type(steps) is not list or not 1 <= len(steps) <= 32:
            fail('RESOURCE', path, 'one to 32 steps required')
        total_steps += len(steps)
        if total_steps > 128:
            fail('RESOURCE', path, 'stored step bound')
        by_id = {}
        for s in steps:
            shape(s, {'id', 'type', 'deps', 'node'}, path)
            name(s['id'], path)
            typename(s['type'], path)
            if s['id'] in env:
                fail('CAPTURE', path, s['id'])
            env[s['id']] = s['type']
            by_id[s['id']] = s
        order = d['order']
        if (type(order) is not list or any(type(x) is not str for x in order)
                or len(order) != len(by_id) or set(order) != set(by_id)):
            fail('ORDER', path, 'order must be exact step permutation')
        local_graph = {}
        used_symbols = set()
        for s in steps:
            site = path + '/' + s['id']
            deps = s['deps']
            if type(deps) is not list or any(type(x) is not str for x in deps) or len(set(deps)) != len(deps):
                fail('SHAPE', site, 'unique reference dependencies required')
            n = s['node']
            if type(n) is not dict or type(n.get('op')) is not str:
                fail('SHAPE', site, 'node operation required')
            op = n['op']
            used = set()

            def expr(e):
                typ, refs = expression(e, env, site)
                used.update(refs)
                return typ

            if op == 'atom':
                shape(n, {'op', 'codec'}, site)
                if n['codec'] != 'uint8':
                    fail('UNSUPPORTED', site, 'UInt8 atom only')
                typ = 'Int64'
            elif op == 'value':
                shape(n, {'op', 'expr'}, site)
                typ = expr(n['expr'])
            elif op == 'check':
                shape(n, {'op', 'test', 'site', 'code'}, site)
                if expr(n['test']) != 'Bool':
                    fail('TYPE', site, 'Boolean predicate required')
                expr(n['site'])
                name(n['code'], site)
                typ = 'Unit'
            elif op == 'end':
                shape(n, {'op'}, site)
                typ = 'Unit'
            elif op == 'compose':
                shape(n, {'op', 'symbol', 'identity', 'args'}, site)
                symbol = n['symbol']
                name(symbol, site)
                digest(n['identity'], site)
                if symbol not in library:
                    fail('UNKNOWN_SYMBOL', site, symbol)
                target = library[symbol]
                if d['dependencies'].get(symbol) != n['identity'] or n['identity'] != target['identity']:
                    fail('IDENTITY', site, 'call must match direct dependency and definition')
                shape(n['args'], {p['name'] for p in target['params']}, site)
                for p in target['params']:
                    arg = n['args'][p['name']]
                    if type(arg) is not dict or set(arg) not in ({'ref'}, {'const'}):
                        fail('REFERENCE', site, 'call arguments must be immutable references/literals')
                    if expr(arg) != p['type']:
                        fail('TYPE', site, 'argument: ' + p['name'])
                typ = target['result_type']
                used_symbols.add(symbol)
            else:
                fail('UNSUPPORTED', site, op)
            if typ != s['type']:
                fail('TYPE', site, 'declared step type differs')
            if set(deps) != used:
                fail('DEPENDENCY', site, 'dependencies must exactly enumerate expression references')
            local_graph[s['id']] = used - params
        _acyclic(local_graph, path + '/steps')
        seen = set(params)
        for key in order:
            if not set(by_id[key]['deps']) <= seen:
                fail('ORDER', path + '/' + key, 'dependency not evaluated earlier')
            seen.add(key)
        if set(d['dependencies']) != used_symbols:
            fail('DEPENDENCY', path, 'exact direct symbol dependencies required')
        typ, _ = expression(d['result'], env, path + '/result')
        if typ != d['result_type']:
            fail('TYPE', path, 'result type differs')
        if identity(d) != d['identity']:
            fail('IDENTITY', path, 'semantic content tampered')
    return {'status': 'valid', 'definitions': len(defs), 'stored_steps': total_steps}


def binding(path, local):
    return 'b_' + hashlib.sha256((path + '/' + local).encode('ascii')).hexdigest()


def substitute(expr, env):
    op, arg = next(iter(expr.items()))
    if op == 'ref':
        return copy.deepcopy(env[arg])
    if op == 'const':
        return copy.deepcopy(expr)
    return {op: [substitute(e, env) for e in arg]}


def expand(package, node_budget=64):
    """Validate first, expand in exact order, then invoke the original validator."""
    validate(package)
    return _expand_validated(package, node_budget)


def _expand_validated(package, node_budget=64):
    """Internal measurement seam; caller must already have validated the package."""
    if type(node_budget) is not int or not 1 <= node_budget <= 64:
        fail('RESOURCE', '$', 'expansion budget 1..64 required')
    library = {d['name']: d for d in package['definitions']}
    mapping = {}
    count = 0

    def claim(path, definition, local):
        nonlocal count
        count += 1
        if count > node_budget:
            fail('EXPANSION_LIMIT', path, 'expanded node budget exhausted')
        if path in mapping:
            fail('IDENTITY', path, 'derived identity collision')
        mapping[path] = {'definition': definition['identity'], 'local': local}

    def region(d, args, path, depth):
        if depth > 4:
            fail('EXPANSION_LIMIT', path, 'composition nesting exceeds four')
        claim(path, d, 'region')
        env = copy.deepcopy(args)
        by_id = {s['id']: s for s in d['steps']}
        steps = []
        for key in d['order']:
            s = by_id[key]
            n = s['node']
            site = path + '/' + key
            if n['op'] == 'compose':
                target = library[n['symbol']]
                node = region(target, {k: substitute(v, env) for k, v in n['args'].items()},
                              site + '/' + target['identity'], depth + 1)
            else:
                claim(site, d, key)
                node = {'id': site, 'op': n['op']}
                for k, v in n.items():
                    if k != 'op':
                        node[k] = substitute(v, env) if k in {'expr', 'test', 'site'} else v
            bind = binding(path, key)
            steps.append({'node': node, 'bind': bind})
            env[key] = {'ref': bind}
        return {'id': path, 'op': 'seq', 'steps': steps,
                'result': substitute(d['result'], env)}

    program = package['program']
    path = 'program/' + program['identity']
    decode = region(program, {}, path, 0)
    encode_id = path + '/encode'
    claim(encode_id, program, 'encode')
    plan = {'version': 'semantic-plan-1', 'text': False, 'rules': {}, 'decode': decode,
            'encode': {'id': encode_id, 'op': 'emit', 'codec': 'uint16be', 'expr': {'ref': 'root'}}}
    if len(canonical(plan)) > MAX_BYTES:
        fail('EXPANSION_LIMIT', '$', 'expanded bytes exceed 64KiB')
    try:
        vm.validate(plan)
    except vm.PlanError as exc:
        fail('FOUNDATION_PLAN', '$', str(exc))
    return {'plan': plan, 'map': mapping,
            'plan_identity': hashlib.sha256(canonical(plan)).hexdigest(),
            'program_identity': program['identity'], 'nodes': count}


def diagnose(package, node_budget=64):
    try:
        result = expand(package, node_budget)
        return {'status': 'valid', 'plan_identity': result['plan_identity'], 'nodes': result['nodes']}
    except Diagnostic as exc:
        return {'status': 'reject', 'diagnostic': exc.data}
