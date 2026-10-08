"""Finite data authoring only: never imported by the VM execution path."""
import time
from audit import HERE, OLD, load, now, save, sha, verify, verify_map


def n(identity, op, **fields):
    return dict(id=identity, op=op, **fields)


def c(value):
    return {'const':value}


def r(name):
    return {'ref':name}


def add(a, b):
    return {'add':[a,b]}


def step(node, bind=None):
    return dict(node=node, **({'bind':bind} if bind else {}))


def plan(decode, encode=None, rules=None):
    return dict(version='semantic-plan-1', text=False, rules=rules or {}, decode=decode,
        encode=encode or n('emit','emit',codec='uint8',expr=r('root')))


def byte_bits():
    # Two unary finite projections of the SAME unconsumed byte. Both selectors
    # cover all bytes. Consume once after recording high and low nibble bits.
    choices = []
    for label, start in [('hi',4),('lo',0)]:
        branches = []
        for nibble in range(16):
            prefixes = [[byte] for byte in range(256)
                        if (byte // 16 if start else byte % 16) == nibble]
            fields = {f'b{start+j}':c(bool((nibble // (2**j)) % 2)) for j in range(4)}
            branches.append(dict(prefixes=prefixes,
                node=n(f'{label}{nibble}','value',expr={'record':fields})))
        choices.append(n(label,'choice',code='DOMAIN',branches=branches))
    return n('bytebits','seq',steps=[step(choices[0],'hi'),step(choices[1],'lo'),
        step(n('consume','take',length=c(1),max=1,code='BOUND'))],
        result={'record':{f'b{i}':r(f'{"hi" if i>=4 else "lo"}.b{i}') for i in range(8)}})


def xor8():
    steps = [step(n('a','call',rule='bits'),'a'),
        step(n('b','repeat',count=c(1),max=1,stop=[],eof=False,occurrence_limit=True,
               body=n('bcall','call',rule='bits')),'bs'),step(n('end','end'))]
    for i in range(8):
        steps.append(step(n(f's{i}','select',source=r('bs'),
            test={'eq':[{'eq':[r(f'a.b{i}'),r(f'item.b{i}')]},c(False)]}),f's{i}'))
    previous = {'length':r('s7')}
    # Horner reconstruction: double previously bound scalar, add next bit.
    for i in range(6,-1,-1):
        steps.append(step(n(f'v{i}','value',expr=add(add(previous,previous),
                                                    {'length':r(f's{i}')})),f'v{i}'))
        previous = r(f'v{i}')
    return plan(n('xor8','seq',steps=steps,result=previous),rules={'bits':byte_bits()})


def addmod8():
    branch = n('wrap','dispatch',expr={'le':[r('sum'),c(255)]},branches={
        'True':n('unwrapped','value',expr=r('sum')),
        'False':n('wrapped','value',expr=add(r('sum'),c(-256)))})
    return plan(n('addmod8','seq',steps=[step(n('a','atom',codec='uint8'),'a'),
        step(n('b','atom',codec='uint8'),'b'),step(n('end','end')),
        step(n('sum','value',expr=add(r('a'),r('b'))),'sum'),step(branch,'answer')],result=r('answer')))


def parity8():
    expr = r('a.b0')
    for i in range(1,8):
        expr = {'eq':[expr,r(f'a.b{i}')]}
    expr = {'eq':[expr,c(False)]}  # seven equality complements, then invert
    branch = n('parity','dispatch',expr=expr,branches={
        'False':n('even','value',expr=c(0)), 'True':n('odd','value',expr=c(1))})
    return plan(n('parity8','seq',steps=[step(n('a','call',rule='bits'),'a'),
        step(n('end','end')),step(branch,'answer')],result=r('answer')),
        rules={'bits':byte_bits()})


def expression_limit():
    def tree(depth):
        return c(0) if not depth else add(tree(depth-1),tree(depth-1))
    return plan(n('expressionoverflow','value',expr=tree(11)))


def node_limit():
    return plan(n('nodeoverflow','seq',steps=[step(n(f'n{i}','value',expr=c(0)))
        for i in range(65)],result=c(0)))


def main():
    verify()
    verify_map(HERE, load(HERE/'SPEC-FREEZE.json')['files'])
    started = time.perf_counter()
    records = []
    attempts = [('naive-xor8',lambda:load(OLD/'PROBE-INPUTS.json')['vm_full_byte_lookup']),
        ('xor8',xor8),('addmod8',addmod8),('parity8',parity8),
        ('expression-limit',expression_limit),('node-limit',node_limit)]
    for name, make in attempts:
        if time.perf_counter()-started >= 600:
            records.append(dict(attempt=name,status='CONSTRUCTION_TIMEOUT'))
            break
        begin = time.perf_counter()
        try:
            value = make()
            save(HERE/(name+'.plan.json'),value)
            records.append(dict(attempt=name,status='CONSTRUCTED',
                seconds=time.perf_counter()-begin,sha256=sha(HERE/(name+'.plan.json'))))
        except Exception as exc:
            records.append(dict(attempt=name,status='CONSTRUCTION_ERROR',
                exception=type(exc).__name__,detail=str(exc),seconds=time.perf_counter()-begin))
    save(HERE/'CONSTRUCTION.json',dict(utc=now(),seconds=time.perf_counter()-started,
        method='enumerated unary nibble projections; shared rule; cardinality bit conversion; Horner addition',
        authoring_effort='Builder execution measured; AI planning/editing not isolated or token-metered',attempts=records))
    print('Constructed',len(records),'frozen-budget attempts; no execution or validation yet')


if __name__ == '__main__':
    main()
