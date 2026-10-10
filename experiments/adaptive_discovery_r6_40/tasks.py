"""Unseen-to-discovery contracts and candidate-independent finite expectations."""
import time
from common import c,package,normalize

TASKS=[
    dict(id='E1',kind='direct',width=2,order=['A','B','C','X'],
         requirement='Read a then b UInt8, check input end before computation. Let x=a+b. Check 31<=x (RANGE_LOW at x), then x<=177 (RANGE_HIGH at x). Return (x+14)+7.'),
    dict(id='E2',kind='direct',width=2,order=['B','C','X','A'],
         requirement='Read x then y UInt8, check input end before computation. Check 17<=x (FIRST_LOW at x), then 17<=y (SECOND_LOW at y), then x+y<=271 (TOTAL_HIGH at y). Return (x+y)+9.'),
    dict(id='E3',kind='combination',width=2,order=['C','X','A','B'],
         requirement='Read x then y UInt8, check input end before computation. First check 9<=x (RANGE_LOW at x), x<=163 (RANGE_HIGH at x), then let u=x+4. Next check 9<=y (RANGE_LOW at y), y<=163 (RANGE_HIGH at y), then let v=y+4. Next check 13<=u (FIRST_LOW at u), 13<=v (SECOND_LOW at v), u+v<=245 (TOTAL_HIGH at v). Return (u+v)+1. Preserve this order.'),
    dict(id='E4',kind='combination',width=2,order=['X','A','B','C'],
         requirement='Read x then y UInt8, check input end before computation. Check x==77 (KEY_MISMATCH at x), then y<=189 (LOAD_HIGH at y). Let t=((x+y)+y)+6. Check 200<=t (RANGE_LOW at t), then t<=403 (RANGE_HIGH at t). Return t+5.'),
    dict(id='E5',kind='negative',width=1,order=['A','C','B','X'],
         requirement='Read x UInt8, check input end before computation. Check x<=176 (RANGE_HIGH at x) BEFORE 32<=x (RANGE_LOW at x). These bounds are exclusive relative to 31 and177: reject x=31 and x=177. Return (x+x)+14. No interval_fee relation has these semantics unchanged.'),
    dict(id='E6',kind='negative',width=2,order=['X','B','C','A'],
         requirement='Read x then y UInt8, check input end before computation. Check y<=189 (LOAD_HIGH at y) BEFORE x<=77 (KEY_HIGH at x). All x from0 through77 are allowed; equality is not required. Return (x+y)+6, counting y only once. No echo_charge relation has these semantics unchanged.')]

def answer(task,values):
    x=values[0]; y=values[-1]
    # Return error and requirement-defined input-source offset, or typed value.
    if task['id']=='E1':
        v=x+y
        if v<31: return ('RANGE_LOW',0)
        if v>177: return ('RANGE_HIGH',0)
        return v+21
    if task['id']=='E2':
        if x<17: return ('FIRST_LOW',0)
        if y<17: return ('SECOND_LOW',1)
        if x+y>271: return ('TOTAL_HIGH',1)
        return x+y+9
    if task['id']=='E3':
        if x<9: return ('RANGE_LOW',0)
        if x>163: return ('RANGE_HIGH',0)
        if y<9: return ('RANGE_LOW',1)
        if y>163: return ('RANGE_HIGH',1)
        u,v=x+4,y+4
        if u<13: return ('FIRST_LOW',0)
        if v<13: return ('SECOND_LOW',1)
        if u+v>245: return ('TOTAL_HIGH',1)
        return u+v+1
    if task['id']=='E4':
        if x!=77: return ('KEY_MISMATCH',0)
        if y>189: return ('LOAD_HIGH',1)
        t=x+y+y+6
        if t<200: return ('RANGE_LOW',0)
        if t>403: return ('RANGE_HIGH',0)
        return t+5
    if task['id']=='E5':
        if x>176: return ('RANGE_HIGH',0)
        if x<32: return ('RANGE_LOW',0)
        return x+x+14
    if y>189: return ('LOAD_HIGH',1)
    if x>77: return ('KEY_HIGH',0)
    return x+y+6

def expectations(task):
    # Same coordinator froze before authors; no candidate-derived expected values.
    points=[0,1,8,9,16,17,30,31,32,58,59,60,76,77,78,120,121,122,159,160,163,164,175,176,177,178,188,189,190,254,255]
    if task['width']==1: values=[(x,) for x in range(256)]
    else: values=sorted(set((x,y) for x in points for y in points)|{(77,y) for y in range(256)})
    return dict(cases=[dict(input_hex=bytes(v).hex(),expected=answer(task,v)) for v in values],
        malformed=[dict(input_hex='00'*n,code='TRUNCATED',offset=n) for n in range(task['width'])]+
            [dict(input_hex='ff'*(task['width']+1),code='TRAILING',offset=task['width']),
             dict(input_hex='00'*(task['width']+1),code='TRAILING',offset=task['width'])],
        source='Requirement-derived same-coordinator pre-author oracle; not human-reviewed/external')

def score(registry,pin,task,frozen):
    started=time.perf_counter(); before=time.perf_counter()
    p=package(registry,pin); root=p['program']
    assert root['name']=='Entry' and root['params']==[] and root['result_type']=='Int64'
    ex=c.expand(p); validation_seconds=time.perf_counter()-before
    assert all(d['identity']==c.identity(d) for d in p['definitions']+[root])
    rows=[]; execution=0
    for case in frozen['cases']:
        data=bytes.fromhex(case['input_hex']); before=time.perf_counter()
        actual=normalize(c.vm.execute(ex['plan'],data)); execution+=time.perf_counter()-before
        want=case['expected']
        if type(want) is int:
            passed=(actual.get('status')=='success' and type(actual.get('value')) is int and actual['value']==want
                and actual['output']=={'bytes_hex':want.to_bytes(2,'big').hex()} and actual['consumed']==task['width']
                and actual['provenance']=={'span':[0,task['width']],'origins':[]})
        else:
            err=actual.get('error',{})
            passed=(actual.get('status')=='reject' and err.get('code')==want[0]
                and err.get('stage')=='validation' and err.get('offset')==want[1]
                and err.get('node') in ex['map'])
        rows.append(dict(case=case,actual=actual,passed=passed))
    for case in frozen['malformed']:
        actual=normalize(c.vm.execute(ex['plan'],bytes.fromhex(case['input_hex'])))
        err=actual.get('error',{})
        rows.append(dict(case=case,actual=actual,passed=err.get('code')==case['code']
            and err.get('stage')=='structure' and err.get('offset')==case['offset']))
    actual=normalize(c.vm.execute(ex['plan'],'invalid'))
    rows.append(dict(control='INPUT_TYPE',actual=actual,passed=actual=={'status':'plan_reject','error':{'code':'INPUT_TYPE'},'work':0}))
    for limit in (0,1,5):
        actual=normalize(c.vm.execute(ex['plan'],b'\x4d'*task['width'],limits={'work':limit}))
        rows.append(dict(control='WORK_LIMIT',budget=limit,actual=actual,
            passed=actual.get('error',{}).get('code')=='WORK_LIMIT' and actual['work']==limit))
    assert time.perf_counter()-started<30,'SCORER_BUDGET'
    return dict(all_passed=all(r['passed'] for r in rows),passed=sum(r['passed'] for r in rows),total=len(rows),rows=rows,
        root=pin,closure=[d['identity'] for d in p['definitions']],expansion=ex,
        validation_seconds=validation_seconds,execution_seconds=execution,wall_seconds=time.perf_counter()-started)
