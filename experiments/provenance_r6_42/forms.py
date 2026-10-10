"""Compact authoring and separately specified exact/flat primitive constructions."""
from common import c
from examples import definition, step, call, ref, const


def compact():
    guarded = definition('Guarded', [('x', 'Int64')], {}, [
        step('guard', 'Unit', ['x'], {'op': 'check', 'test': {'le': [ref('x'), const(3)]},
                                    'site': ref('x'), 'code': 'INNER'}),
        step('sum', 'Int64', ['x'], {'op': 'value', 'expr': {'add': [ref('x'), const(1)]}})], ref('sum'))
    nested = definition('Nested', [('x', 'Int64')], {'Guarded': guarded['identity']}, [
        step('inner', 'Int64', ['x'], call(guarded, {'x': ref('x')}))], ref('inner'))
    entry = definition('Entry', [], {'Nested': nested['identity']}, [
        step('x', 'Int64', [], {'op': 'atom', 'codec': 'uint8'}),
        step('y', 'Int64', [], {'op': 'atom', 'codec': 'uint8'}),
        step('end', 'Unit', [], {'op': 'end'}),
        step('left', 'Int64', ['x'], call(nested, {'x': ref('x')})),
        step('right', 'Int64', ['y'], call(nested, {'x': ref('y')})),
        step('post_low', 'Unit', ['left'], {'op': 'check', 'test': {'le': [const(3), ref('left')]},
                                          'site': ref('left'), 'code': 'POST_LOW'}),
        step('post_high', 'Unit', ['left', 'right'], {'op': 'check',
             'test': {'le': [{'add': [ref('left'), ref('right')]}, const(6)]},
             'site': ref('right'), 'code': 'POST_HIGH'}),
        step('total', 'Int64', ['left', 'right'], {'op': 'value', 'expr': {'add': [ref('left'), ref('right')]}})], ref('total'))
    return {'version': c.VERSION, 'foundation': c.FOUNDATION, 'definitions': [guarded, nested], 'program': entry}


def coordinates(package):
    # Only declared identities are read; never call the expander to specify a twin.
    guarded, nested = package['definitions']
    root = 'program/' + package['program']['identity']
    paths = {'root': root}
    for side in ('left', 'right'):
        paths[side] = root + '/' + side + '/' + nested['identity']
        paths[side + '_inner'] = paths[side] + '/inner/' + guarded['identity']
    return paths


def explicit(package, flat=False):
    paths = coordinates(package)
    p = 'flat/Entry' if flat else paths['root']
    mapping, pairs = {}, {}
    entry = package['program']['identity']
    guarded, nested = package['definitions']

    def claim(path, pin, local):
        mapping[path] = {'definition': pin, 'local': local}

    def bound(path, local, node):
        return {'node': node, 'bind': c.binding(path, local)}

    def variable(path, local):
        return ref(c.binding(path, local))

    def primitive(path, local, op, **fields):
        return {'id': path + '/' + local, 'op': op, **fields}

    claim(paths['root'], entry, 'region')
    steps = []
    for key in ('x', 'y'):
        steps.append(bound(p, key, primitive(p, key, 'atom', codec='uint8')))
    steps.append(bound(p, 'end', primitive(p, 'end', 'end')))
    for key in ('x', 'y', 'end', 'post_low', 'post_high', 'total', 'encode'):
        claim(paths['root'] + '/' + key, entry, key)
        pairs[p + '/' + key] = paths['root'] + '/' + key
    for side, argument in (('left', 'x'), ('right', 'y')):
        n, g = paths[side], paths[side + '_inner']
        claim(n, nested['identity'], 'region')
        claim(g, guarded['identity'], 'region')
        claim(g + '/guard', guarded['identity'], 'guard')
        claim(g + '/sum', guarded['identity'], 'sum')
        if flat:
            key = side + '_guard'
            steps.append(bound(p, key, primitive(p, key, 'check',
                test={'le': [variable(p, argument), const(3)]}, site=variable(p, argument), code='INNER')))
            steps.append(bound(p, side, primitive(p, side, 'value', expr={'add': [variable(p, argument), const(1)]})))
            pairs[p + '/' + key] = g + '/guard'
            pairs[p + '/' + side] = g + '/sum'
        else:
            body = {'id': g, 'op': 'seq', 'steps': [
                bound(g, 'guard', primitive(g, 'guard', 'check', test={'le': [variable(p, argument), const(3)]},
                                           site=variable(p, argument), code='INNER')),
                bound(g, 'sum', primitive(g, 'sum', 'value', expr={'add': [variable(p, argument), const(1)]}))],
                'result': variable(g, 'sum')}
            region = {'id': n, 'op': 'seq', 'steps': [bound(n, 'inner', body)], 'result': variable(n, 'inner')}
            steps.append(bound(p, side, region))
    steps += [bound(p, 'post_low', primitive(p, 'post_low', 'check', test={'le': [const(3), variable(p, 'left')]},
                 site=variable(p, 'left'), code='POST_LOW')),
              bound(p, 'post_high', primitive(p, 'post_high', 'check',
                 test={'le': [{'add': [variable(p, 'left'), variable(p, 'right')]}, const(6)]},
                 site=variable(p, 'right'), code='POST_HIGH')),
              bound(p, 'total', primitive(p, 'total', 'value', expr={'add': [variable(p, 'left'), variable(p, 'right')]}))]
    plan = {'version': 'semantic-plan-1', 'text': False, 'rules': {},
            'decode': {'id': p, 'op': 'seq', 'steps': steps, 'result': variable(p, 'total')},
            'encode': primitive(p, 'encode', 'emit', codec='uint16be', expr=ref('root'))}
    pairs[p] = paths['root']
    return plan, mapping, pairs
