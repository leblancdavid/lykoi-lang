"""Development-only contracts and independently pre-discovery B-proxy pool."""
from common import c

DEVELOPMENT = [
    dict(id='D1', relation='interval_fee', params=['x','floor','ceiling','fee'],
         requirement='Accept floor<=x, else RANGE_LOW at site x; then x<=ceiling, else RANGE_HIGH at site x. Return checked x+fee.'),
    dict(id='D2', relation='pair_envelope', params=['x','y','floor','cap'],
         requirement='Check floor<=x (FIRST_LOW, site x), then floor<=y (SECOND_LOW, site y), then x+y<=cap (TOTAL_HIGH, site y). Return checked x+y.'),
    dict(id='D3', relation='echo_charge', params=['x','y','expected','limit','bias'],
         requirement='Check x==expected (KEY_MISMATCH, site x), then y<=limit (LOAD_HIGH, site y). Return checked ((x+y)+y)+bias.')]

def ref(x): return {'ref':x}
def const(x): return {'const':x}
def add(a,b): return {'add':[a,b]}
def le(a,b): return {'le':[a,b]}

def step(label, test, site, code):
    _, deps=c.expression(test,{x:'Int64' for x in ['x','y','floor','ceiling','fee','cap','expected','limit','bias']},'$')
    return dict(id=label,type='Unit',deps=sorted(deps|{site}),node=dict(op='check',test=test,site=ref(site),code=code))

def proxy_pool():
    # Only DEVELOPMENT is consulted. No discovered definitions/evaluation inputs.
    x,y=ref('x'),ref('y')
    specs=[('ProxyInterval',DEVELOPMENT[0],[
        step('lo',le(ref('floor'),x),'x','RANGE_LOW'),step('hi',le(x,ref('ceiling')),'x','RANGE_HIGH')],add(x,ref('fee'))),
        ('ProxyPair',DEVELOPMENT[1],[
        step('first',le(ref('floor'),x),'x','FIRST_LOW'),step('second',le(ref('floor'),y),'y','SECOND_LOW'),
        step('total',le(add(x,y),ref('cap')),'y','TOTAL_HIGH')],add(x,y)),
        ('ProxyEcho',DEVELOPMENT[2],[
        step('key',{'eq':[x,ref('expected')]},'x','KEY_MISMATCH'),step('load',le(y,ref('limit')),'y','LOAD_HIGH')],
        add(add(add(x,y),y),ref('bias')))]
    return [dict(definition=c.seal(dict(name=name,revision=1,params=[dict(name=p,type='Int64') for p in task['params']],
        dependencies={},steps=steps,order=[s['id'] for s in steps],result=result,result_type='Int64')),
        relation=task['relation'],semantics=task['requirement']) for name,task,steps,result in specs]

def expected(relation,args):
    if relation=='interval_fee':
        x,lo,hi,fee=[args[p] for p in DEVELOPMENT[0]['params']]
        if x<lo: return 'RANGE_LOW'
        if x>hi: return 'RANGE_HIGH'
        return x+fee
    if relation=='pair_envelope':
        x,y,lo,cap=[args[p] for p in DEVELOPMENT[1]['params']]
        if x<lo: return 'FIRST_LOW'
        if y<lo: return 'SECOND_LOW'
        if x+y>cap: return 'TOTAL_HIGH'
        return x+y
    x,y,key,limit,bias=[args[p] for p in DEVELOPMENT[2]['params']]
    if x!=key: return 'KEY_MISMATCH'
    if y>limit: return 'LOAD_HIGH'
    return x+y+y+bias

def witnesses(task):
    # Frozen from relations before any proposals; not model-provided answers.
    if task['id']=='D1':
        groups=[[(x,11,143,5) for x in range(256)],[(x,73,61,9) for x in range(256)]]
    elif task['id']=='D2':
        points=[0,1,12,13,14,65,120,121,122,180,255]
        groups=[[(x,y,13,121) for x in points for y in points],[(x,y,0,299) for x in points for y in points]]
    else:
        points=[0,1,53,54,55,119,120,121,199,255]
        groups=[[(x,y,54,120,8) for x in points for y in points],[(x,y,119,199,3) for x in points for y in points]]
    return [dict(context=i,args=dict(zip(task['params'],a)),expected=expected(task['relation'],dict(zip(task['params'],a))))
        for i,g in enumerate(groups) for a in g]

def development_check(definition,relation,definitions,cases):
    task=next(t for t in DEVELOPMENT if t['relation']==relation)
    assert definition['params']==[dict(name=p,type='Int64') for p in task['params']]
    assert definition['result_type']=='Int64'
    rows=[]
    # Parameterized functions are exercised by mechanically authored closed hosts.
    for row in cases:
        host=c.seal(dict(name='DevelopmentHost',revision=1,params=[],dependencies={definition['name']:definition['identity']},
            steps=[dict(id='call',type='Int64',deps=[],node=dict(op='compose',symbol=definition['name'],
            identity=definition['identity'],args={k:const(v) for k,v in row['args'].items()}))],
            order=['call'],result=ref('call'),result_type='Int64'))
        ex=c.expand(dict(version=c.VERSION,foundation=c.FOUNDATION,definitions=definitions,program=host))
        actual=c.vm.execute(ex['plan'],b'')
        want=row['expected']
        passed=(actual.get('status')=='success' and type(actual.get('value')) is int and actual['value']==want
            and actual['output']==want.to_bytes(2,'big')) if type(want) is int else (
            actual.get('status')=='reject' and actual.get('error',{}).get('code')==want)
        rows.append(dict(case=row,passed=passed,actual=actual))
    return dict(passed=all(r['passed'] for r in rows),observations=len(rows),rows=rows)
