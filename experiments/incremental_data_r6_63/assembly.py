"""One-step immutable construction; reuse frozen typing, expansion and VM execution."""
import copy
from freeze import c, pin


def definition(before, steps, result, result_type):
    return c.seal(dict(name=before['name'], revision=1, params=copy.deepcopy(before['params']),
        dependencies={}, steps=copy.deepcopy(steps), order=[s['id'] for s in steps],
        result=result, result_type=result_type))


def package(task, arguments=None):
    if arguments is None:
        arguments = {p['name']: {'Int64':0, 'Bool':False, 'Unit':None}[p['type']] for p in task['params']}
    host = c.seal(dict(name='HostEntry',revision=1,params=[],dependencies={task['name']:task['identity']},
        steps=[dict(id='invoke',type=task['result_type'],deps=[],node=dict(op='compose',symbol=task['name'],
        identity=task['identity'],args={k:{'const':v} for k,v in arguments.items()}))],
        order=['invoke'],result={'const':0},result_type='Int64'))
    return dict(version=c.VERSION,foundation=c.FOUNDATION,definitions=[task],program=host)


def check_before(before):
    c._tree_bound(before)
    c.shape(before, {'version','foundation','name','params','steps','order','literals','output_id','result_type','identity'}, '$/before')
    if before['identity'] != pin({k:v for k,v in before.items() if k != 'identity'}):
        c.fail('IDENTITY','$/before','state content tampered')
    if before['version'] != 'r6.63-state-1' or before['foundation'] != c.FOUNDATION:
        c.fail('FOUNDATION','$/before','version/foundation mismatch')
    if (type(before['params']) is not list or len(before['params']) > 4
            or type(before['steps']) is not list or len(before['steps']) > 2):
        c.fail('RESOURCE','$/before','at most four params and two prefix steps')
    if any(s.get('node', {}).get('op') != 'value' for s in before['steps']):
        c.fail('UNSUPPORTED','$/before','value-only frozen prefix')
    if before['order'] != [s['id'] for s in before['steps']] or before['output_id'] != 'selected':
        c.fail('ORDER','$/before','prefix order/output id mismatch')
    # Existing validator checks the entire prefix, including unused typed values.
    sentinel = dict(id='StateSentinel',type='Int64',deps=[],node=dict(op='value',expr={'const':0}))
    c.validate(package(definition(before, before['steps']+[sentinel], {'const':0}, 'Int64')))
    for literal in before['literals']:
        c.expression({'const':literal},{},'$/before/literals')


def apply(before, action):
    original = c.canonical(before)
    check_before(before)
    c.shape(action, {'id','type','deps','node'}, '$/action')
    c.shape(action['node'], {'op','expr'}, '$/action/node')
    if action['id'] != before['output_id'] or action['node']['op'] != 'value':
        c.fail('SHAPE','$/action','mechanical value-step envelope required')
    expr = action['node']['expr']
    if type(expr) is not dict or len(expr) != 1 or next(iter(expr)) not in ('add','le','eq'):
        c.fail('UNSUPPORTED','$/action','add/le/eq only')
    operands = next(iter(expr.values()))
    if type(operands) is not list or len(operands) != 2:
        c.fail('SHAPE','$/action','two ordered operands required')
    for arg in operands:
        if type(arg) is not dict or set(arg) not in ({'ref'}, {'const'}):
            c.fail('SHAPE','$/action','direct reference or literal only')
        if 'const' in arg and not any(type(v) is type(arg['const']) and v == arg['const'] for v in before['literals']):
            c.fail('LITERAL','$/action','literal absent from frozen scope')
    env = {p['name']:p['type'] for p in before['params']}
    env.update({s['id']:s['type'] for s in before['steps']})
    inferred, refs = c.expression(expr,env,'$/action')
    if action['type'] != inferred or action['type'] != before['result_type']:
        c.fail('TYPE','$/action','result obligation/type mismatch')
    if action['deps'] != sorted(refs):
        c.fail('DEPENDENCY','$/action','exact sorted distinct direct refs required')
    task = definition(before, before['steps']+[action], {'ref':action['id']}, action['type'])
    complete = package(task)
    validation = c.validate(complete)
    c.expand(complete)
    body = dict(version='r6.63-after-1', parent_identity=before['identity'], action_identity=pin(action), package=complete)
    after = dict(body,identity=pin(body))
    assert c.canonical(before) == original
    assert task['steps'][:-1] == before['steps'] and task['params'] == before['params']
    return after, validation


def behavior(after, arguments):
    task = after['package']['definitions'][0]
    if type(arguments) is not dict or set(arguments) != {p['name'] for p in task['params']}:
        return dict(status='reject',code='ARGUMENT_SHAPE',work=0)
    for p in task['params']:
        try:
            typ, _ = c.expression({'const':arguments[p['name']]},{},'$/arguments')
        except c.Diagnostic:
            return dict(status='reject',code='ARGUMENT_TYPE',work=0)
        if typ != p['type']:
            return dict(status='reject',code='ARGUMENT_TYPE',work=0)
    expanded = c.expand(package(task, arguments))
    plan = copy.deepcopy(expanded['plan'])
    # Unchanged generated task region; preserve native ids, bindings and operations.
    plan['decode'] = plan['decode']['steps'][0]['node']
    raw = c.vm.execute(plan, b'', assemble=False)
    if raw['status'] == 'success':
        typ = 'Bool' if type(raw['value']) is bool else ('Int64' if type(raw['value']) is int else 'Unit')
        result = dict(status='success',type=typ,value=raw['value'],work=raw['work'])
    else:
        result = dict(status='reject',code=raw['error']['code'],work=raw['work'],error=raw['error'])
    return result


def agrees(observation, expected):
    return all(k in observation and type(observation[k]) is type(v) and observation[k] == v for k,v in expected.items())
