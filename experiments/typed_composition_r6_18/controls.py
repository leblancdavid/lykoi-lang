"""Predeclared adversarial representations; every attempted payload is retained."""
import copy
from composition import VERSION, FOUNDATION, seal
from examples import examples, const, ref, step, definition, call


def controls():
    original = examples()['pair']
    rows = []

    def add(label, code, mutate, budget=64):
        package = copy.deepcopy(original)
        mutate(package)
        rows.append({'label': label, 'expected': code, 'package': package, 'node_budget': budget})

    def program(p):
        return p['program']

    def reseal(p):
        p['program'] = seal(p['program'])

    add('unknown_symbol', 'UNKNOWN_SYMBOL', lambda p: program(p)['dependencies'].update(missing='0' * 64))
    add('missing_reference', 'UNKNOWN_REFERENCE', lambda p: program(p)['steps'][2]['node']['args'].update(x=ref('absent')))
    add('dotted_reference', 'REFERENCE', lambda p: program(p)['steps'][2]['node']['args'].update(x=ref('x.field')))
    add('type_mismatch_bool_integer', 'TYPE', lambda p: program(p)['steps'][2]['node']['args'].update(delta=const(True)))
    add('parameter_local_capture', 'CAPTURE', lambda p: p['definitions'][0]['steps'][0].update(id='x'))
    add('caller_capture_attempt', 'UNKNOWN_REFERENCE', lambda p: p['definitions'][0]['steps'][0]['node'].update(expr=ref('y')))
    add('duplicate_local', 'CAPTURE', lambda p: program(p)['steps'][1].update(id='x'))
    add('unsupported_opcode', 'UNSUPPORTED', lambda p: program(p)['steps'][0]['node'].update(op='host_callback'))
    add('unsupported_codec', 'UNSUPPORTED', lambda p: program(p)['steps'][0]['node'].update(codec='uint16be'))
    add('unsupported_expression', 'UNSUPPORTED', lambda p: program(p).update(result={'multiply': [ref('x'), ref('y')]}))
    add('computed_argument', 'REFERENCE', lambda p: program(p)['steps'][2]['node']['args'].update(x={'add': [ref('x'), const(1)]}))
    add('invalid_order', 'ORDER', lambda p: program(p).update(order=['total', 'x', 'y', 'complete']))
    add('order_duplicate', 'ORDER', lambda p: program(p).update(order=['x', 'y', 'total', 'total']))
    add('dependency_omission', 'DEPENDENCY', lambda p: program(p)['steps'][2].update(deps=['x']))
    add('malformed_definition', 'SHAPE', lambda p: p['definitions'][0].update(extra=True))
    add('malformed_params', 'SHAPE', lambda p: p['definitions'][0].update(params=[None]))
    add('malformed_node', 'SHAPE', lambda p: program(p)['steps'][0].update(node=[]))
    add('identity_tampering', 'IDENTITY', lambda p: p['definitions'][0]['steps'][1]['node'].update(code='CHANGED'))
    add('call_pin_tampering', 'IDENTITY', lambda p: program(p)['steps'][2]['node'].update(identity='0' * 64))
    add('foundation_tampering', 'FOUNDATION', lambda p: p.update(foundation='0' * 64))
    add('tight_expansion_budget', 'EXPANSION_LIMIT', lambda p: None, budget=3)

    def cycle(p):
        p['definitions'][0]['dependencies']['bounded_add'] = p['definitions'][0]['identity']
    add('symbol_self_cycle', 'CYCLE', cycle)

    def indirect(p):
        a = p['definitions'][0]
        b = copy.deepcopy(a)
        b['name'] = 'second'
        b['dependencies'] = {'bounded_add': a['identity']}
        a['dependencies'] = {'second': b['identity']}
        p['definitions'].append(b)
    add('symbol_indirect_cycle', 'CYCLE', indirect)

    def local_cycle(p):
        s = program(p)['steps']
        s[0] = step('x', 'Int64', ['y'], {'op': 'value', 'expr': ref('y')})
        s[1] = step('y', 'Int64', ['x'], {'op': 'value', 'expr': ref('x')})
        reseal(p)
    add('local_dependency_cycle', 'CYCLE', local_cycle)

    def expansion_bomb(p):
        template = program(p)['steps'][2]
        more = []
        for i in range(24):
            s = copy.deepcopy(template)
            s['id'] = 'copy' + str(i)
            more.append(s)
        program(p)['steps'] = program(p)['steps'][:2] + more
        program(p)['order'] = [s['id'] for s in program(p)['steps']]
        program(p)['result'] = ref('copy23')
        reseal(p)
    add('default_expansion_budget', 'EXPANSION_LIMIT', expansion_bomb)

    return rows


SERIALIZATION = [
    ('duplicate_keys', '{"version":1,"version":2}', 'SERIALIZATION'),
    ('broken_json', '{', 'SERIALIZATION'),
    ('floating_number', '{"x":1.5}', 'SERIALIZATION'),
    ('nonfinite_number', '{"x":NaN}', 'SERIALIZATION'),
    ('oversize_json', ' ' * 65537, 'RESOURCE'),
    ('deep_json', '[' * 30 + '0' + ']' * 30, 'RESOURCE'),
]


def scalar_program(value):
    d = definition('scalar', [], {}, [step('v', 'Int64', [], {'op': 'value', 'expr': const(value)})], ref('v'))
    return {'version': VERSION, 'foundation': FOUNDATION, 'definitions': [], 'program': d}
