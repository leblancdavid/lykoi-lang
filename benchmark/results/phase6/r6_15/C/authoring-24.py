"""Data-only authoring builder; never imported by submitted plans or VM."""
import json
from pathlib import Path

HERE = Path(__file__).parent
serial = 0

def n(op, **kw):
    global serial
    serial += 1
    return dict(id=f'n{serial}', op=op, **kw)

def c(x): return {'const': x}
def r(x): return {'ref': x}
def length(x): return {'length': x}
def eq(a, b): return {'eq': [a, b]}
def le(a, b): return {'le': [a, b]}
def step(node, bind=None):
    return {'node': node, **({'bind': bind} if bind else {})}
def seq(steps, result): return n('seq', steps=steps, result=result)
def check(test, code, site): return n('check', test=test, code=code, site=site)
def repeat(body, **kw):
    return n('repeat', body=body, stop=[], eof=True, max=8,
             occurrence_limit=True, **kw)
def atom(): return n('atom', codec='uint8')
def plan(decode, encode):
    return dict(version='semantic-plan-1', text=False, rules={}, decode=decode, encode=encode)

# T2: partial, exact for all-zero/one counts. Larger valid counts are explicitly
# stopped after full structural validation, rather than publishing wrong values.
record = seq([
    step(atom(), 'count'),
    step(check(le(r('count'), c(4)), 'RUN', r('count'))),
    step(atom(), 'value')], {'record': {'count': r('count'), 'value': r('value')}})
decode2 = seq([
    step(n('literal', bytes=[1], code='VERSION')),
    step(repeat(record), 'records'),
    step(n('map', source=r('records'), body=check(
        le(r('item.count'), c(1)), 'AUTHORING_UNSUPPORTED', r('item.count')))),
    step(n('select', source=r('records'), test=eq(r('item.count'), c(1))), 'nonzero'),
    step(n('map', source=r('nonzero'), body=n('value', expr=r('item.value'))), 'values')
], r('values'))
t2 = plan(decode2, n('each', source=r('root'), body=n('emit', codec='uint8', expr=r('item'))))

# T4: read only min(length,8); raw reads cannot introduce task syntax failures.
# Semantic checks are then ordered by original symbol, with original Cell sites.
read = n('dispatch', expr=le({'input_length': None}, c(8)), branches={
    'True': repeat(atom(), count={'input_length': None}),
    'False': repeat(atom(), count=c(8))})
prefix_checks = seq([
    step(check(le(r('item'), c(41)), 'SYNTAX', r('item'))),
    step(check(le(c(40), r('item')), 'SYNTAX', r('item'))),
    step(n('select', source=r('prefix'), test=eq(r('item'), c(40))), 'opens'),
    step(n('select', source=r('prefix'), test=eq(r('item'), c(41))), 'closes'),
    step(check(le(length(r('closes')), length(r('opens'))), 'UNDERFLOW', r('item'))),
    step(check(le(length(r('opens')), {'add': [length(r('closes')), c(2)]}), 'DEPTH', r('item')))
], c(None))
decode4 = seq([
    step(read, 'symbols'),
    step(n('map', source=r('symbols'), body=prefix_checks)),
    step(n('take', length=c(0), max=0, code='SYNTAX'), 'eof_site'),
    step(check(le({'input_length': None}, c(8)), 'OCCURRENCE_LIMIT', r('eof_site'))),
    step(n('select', source=r('symbols'), test=eq(r('item'), c(40))), 'opens'),
    step(n('select', source=r('symbols'), test=eq(r('item'), c(41))), 'closes'),
    step(check(eq(length(r('opens')), length(r('closes'))), 'UNCLOSED', r('eof_site')))
], {'record': {'pairs': length(r('closes'))}})
t4 = plan(decode4, n('emit', codec='uint8', expr=r('root.pairs')))

if __name__ == '__main__':
    for task, candidate in [('T2', t2), ('T4', t4)]:
        text = json.dumps(candidate, indent=2) + '\n'
        for folder in ['first', 'base']:
            path = HERE / folder / (task + '.plan.json')
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open('x', encoding='utf-8') as f:
                f.write(text)
