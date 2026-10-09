"""Author one reusable composition, nested reuse, and independent expanded twins."""
import copy
from composition import FOUNDATION, VERSION, binding, seal


def ref(x):
    return {'ref': x}


def const(x):
    return {'const': x}


def step(key, typ, deps, node):
    return {'id': key, 'type': typ, 'deps': deps, 'node': node}


def definition(name, params, dependencies, steps, result, typ='Int64'):
    return seal({'name': name, 'revision': 1, 'params': [{'name': p, 'type': t} for p, t in params],
                 'dependencies': dependencies, 'steps': steps, 'order': [s['id'] for s in steps],
                 'result': result, 'result_type': typ})


def call(d, args):
    return {'op': 'compose', 'symbol': d['name'], 'identity': d['identity'], 'args': args}


def examples():
    bounded = definition('bounded_add', [('x', 'Int64'), ('delta', 'Int64'), ('limit', 'Int64')], {}, [
        step('sum', 'Int64', ['x', 'delta'], {'op': 'value', 'expr': {'add': [ref('x'), ref('delta')]}}),
        step('guard', 'Unit', ['sum', 'limit'], {'op': 'check', 'test': {'le': [ref('sum'), ref('limit')]},
                                              'site': ref('sum'), 'code': 'BOUND'})], ref('sum'))
    nested = definition('increment', [('x', 'Int64')], {'bounded_add': bounded['identity']}, [
        step('inner', 'Int64', ['x'], call(bounded, {'x': ref('x'), 'delta': const(1), 'limit': const(255)}))], ref('inner'))
    packages = {}
    for context in ('pair', 'header_increment'):
        steps = []
        deps = {'bounded_add': bounded['identity']}
        if context == 'header_increment':
            deps['increment'] = nested['identity']
            steps += [step('header', 'Int64', [], {'op': 'atom', 'codec': 'uint8'}),
                      step('header_guard', 'Unit', ['header'], {'op': 'check',
                           'test': {'eq': [ref('header'), const(7)]}, 'site': ref('header'), 'code': 'HEADER'})]
        steps += [step('x', 'Int64', [], {'op': 'atom', 'codec': 'uint8'}),
                  step('y', 'Int64', [], {'op': 'atom', 'codec': 'uint8'})]
        x = 'x'
        if context == 'header_increment':
            steps.append(step('bumped', 'Int64', ['x'], call(nested, {'x': ref('x')})))
            x = 'bumped'
        steps += [step('total', 'Int64', [x, 'y'], call(bounded, {'x': ref(x), 'delta': ref('y'), 'limit': const(255)})),
                  step('complete', 'Unit', [], {'op': 'end'})]
        program = definition(context, [], deps, steps, ref('total'))
        packages[context] = {'version': VERSION, 'foundation': FOUNDATION,
                             'definitions': [bounded] + ([nested] if context != 'pair' else []), 'program': program}
    return packages


def explicit_twin(package):
    """Hand-written VM structure; does not inspect/expand symbolic step bodies."""
    d = package['program']
    registry = {x['name']: x for x in package['definitions']}
    p = 'program/' + d['identity']
    bounded_id = registry['bounded_add']['identity']

    def bind(path, key, node):
        return {'node': node, 'bind': binding(path, key)}

    def variable(path, key):
        return ref(binding(path, key))

    def atom(key):
        return bind(p, key, {'id': p + '/' + key, 'op': 'atom', 'codec': 'uint8'})

    def addition(path, x, delta):
        return {'id': path, 'op': 'seq', 'steps': [
            bind(path, 'sum', {'id': path + '/sum', 'op': 'value', 'expr': {'add': [x, delta]}}),
            bind(path, 'guard', {'id': path + '/guard', 'op': 'check',
                               'test': {'le': [variable(path, 'sum'), const(255)]},
                               'site': variable(path, 'sum'), 'code': 'BOUND'})],
            'result': variable(path, 'sum')}

    steps = []
    if d['name'] == 'header_increment':
        steps += [atom('header'), bind(p, 'header_guard', {'id': p + '/header_guard', 'op': 'check',
                  'test': {'eq': [variable(p, 'header'), const(7)]}, 'site': variable(p, 'header'), 'code': 'HEADER'})]
    steps += [atom('x'), atom('y')]
    x = variable(p, 'x')
    if d['name'] == 'header_increment':
        n = p + '/bumped/' + registry['increment']['identity']
        inner = n + '/inner/' + bounded_id
        steps.append(bind(p, 'bumped', {'id': n, 'op': 'seq',
                     'steps': [bind(n, 'inner', addition(inner, x, const(1)))], 'result': variable(n, 'inner')}))
        x = variable(p, 'bumped')
    steps += [bind(p, 'total', addition(p + '/total/' + bounded_id, x, variable(p, 'y'))),
              bind(p, 'complete', {'id': p + '/complete', 'op': 'end'})]
    return {'version': 'semantic-plan-1', 'text': False, 'rules': {},
            'decode': {'id': p, 'op': 'seq', 'steps': steps, 'result': variable(p, 'total')},
            'encode': {'id': p + '/encode', 'op': 'emit', 'codec': 'uint16be', 'expr': ref('root')}}
