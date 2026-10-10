"""Fresh requirements and pre-author requirement-derived acceptance observations."""
import copy
import time
from common import c, package, normalize

TASKS = [
    dict(id='T1', symbol='WindowCharge', param='limit', constant=190, delta=17, bias=8,
         base='x+y+y', successor='x+x+y', order=['A','B','C'],
         checks='x<=y (WINDOW_ORDER, site x, g1), then y<=limit (WINDOW_LIMIT, site y, g2)',
         change='Reverse the two ordered checks: g2 first, g1 second. Retain each code, site and label.'),
    dict(id='T2', symbol='BatchFee', param='limit', constant=180, delta=19, bias=3,
         base='x+y', successor='x+y+9', order=['B','C','A'],
         checks='x<=limit (ITEM_LIMIT, site x, g1), then x+y<=limit (BATCH_LIMIT, site y, g2)',
         change='Preserve both original ordered checks exactly; the extra 9 is charged after checks.'),
    dict(id='T3', symbol='MinimumLoad', param='floor', constant=21, delta=23, bias=5,
         base='x+x+y', successor='x+y+y+3', order=['C','A','B'],
         checks='floor<=x (FIRST_MINIMUM, site x, g1), then floor<=y (SECOND_MINIMUM, site y, g2)',
         change='Preserve both original ordered checks exactly.')]

def requirement(t):
    return (f"Construct {t['symbol']}(x:Int64,y:Int64,{t['param']}:Int64)->Int64. "
        f"Ordered checks: {t['checks']}. Return {t['base']} with checked signed64 addition. "
        f"CallerA reads x then y UInt8 (read_x/read_y); input_end checks end BEFORE computation; "
        f"compose step call uses {t['param']}={t['constant']}, then adds {t['bias']} and emits UInt16BE. "
        f"CallerB reads x UInt8 (read_x), checks input_end BEFORE computation, derives y=x+{t['delta']}; "
        f"compose step call uses {t['param']}={t['constant']}, returns result and emits UInt16BE. "
        "Each caller has no parameters and Int64 result. Preserve semantic rejection source sites. "
        "Admit one shared definition and two dependent callers, revision1. Retrieve/validate both; "
        "execute representative cases. Stop after original application, no successor.")

def modification(t):
    return (f"Modify existing {t['symbol']} by admitting a signature-preserving successor with "
        f"result {t['successor']}. {t['change']} Admit against exact predecessor. "
        "Create CallerA successor changing ONLY the dependency pin and compose-call identity, "
        "retain revision1 and all other structure. Record total explicit family migration: "
        "CallerA updated, CallerB null/retain. CallerB must keep original behavior and pin. "
        "All predecessors remain immutable and executable. Retrieve/validate active CallerA and "
        "retained CallerB and execute examples. This replaces active CallerA behavior, not an additive-only endpoint.")

def expected(t,x,y,changed,is_a):
    if t['id']=='T1':
        checks=[(x>y,'WINDOW_ORDER'),(y>t['constant'],'WINDOW_LIMIT')]
        if changed: checks.reverse()
        value=x+x+y if changed else x+y+y
    elif t['id']=='T2':
        checks=[(x>t['constant'],'ITEM_LIMIT'),(x+y>t['constant'],'BATCH_LIMIT')]
        value=x+y+(9 if changed else 0)
    else:
        checks=[(x<t['constant'],'FIRST_MINIMUM'),(y<t['constant'],'SECOND_MINIMUM')]
        value=x+y+y+3 if changed else x+x+y
    for bad,code in checks:
        if bad: return code
    return value+(t['bias'] if is_a else 0)

def expectations(t):
    points=sorted({0,1,20,21,22,89,90,91,179,180,181,189,190,191,254,255})
    return dict(A=[dict(hex=bytes([x,y]).hex(),expected=expected(t,x,y,False,True),
        modified=expected(t,x,y,True,True)) for x in points for y in points],
        B=[dict(hex=bytes([x]).hex(),expected=expected(t,x,x+t['delta'],False,False)) for x in range(256)],
        invalid_A={'':'TRUNCATED','01':'TRUNCATED','010200':'TRAILING','ffff00':'TRAILING'},
        invalid_B={'':'TRUNCATED','0100':'TRAILING','ff00':'TRAILING'},
        source='Requirement-derived before artifacts; same coordinator, not independently sourced')

def artifacts(registry,t,final):
    state=registry.read()['state']; ds=state['definitions']; edges=state['successors']
    def original(name):
        found=[d for p,d in ds.items() if d['name']==name and p not in edges]
        assert len(found)==1,('original',name)
        return found[0]
    old,a,b=original(t['symbol']),original('CallerA'),original('CallerB')
    assert a['dependencies']==b['dependencies']=={t['symbol']:old['identity']}
    result=dict(old=old,a=a,b=b)
    if final:
        def successor(d):
            found=[ds[p] for p,oldpin in edges.items() if oldpin==d['identity']]
            assert len(found)==1,('successor',d['name'])
            return found[0]
        new,anew=successor(old),successor(a)
        assert anew['dependencies']=={t['symbol']:new['identity']}
        assert state['migrations']==[dict(predecessor=old['identity'],successor=new['identity'],
            decisions={a['identity']:anew['identity'],b['identity']:None})]
        twin=copy.deepcopy(a); twin['dependencies'][t['symbol']]=new['identity']
        for step in twin['steps']:
            if step['node']['op']=='compose': step['node']['identity']=new['identity']
        twin=c.seal({k:v for k,v in twin.items() if k!='identity'})
        assert twin==anew,'caller changed beyond pins'
        result.update(new=new,a_new=anew)
    for d in result.values(): assert d['identity']==c.identity(d)
    return result

def acceptance(registry,t,frozen,final):
    start=time.perf_counter(); ds=artifacts(registry,t,final); rows=[]; expansions={}; execution=0
    first_codes={'WINDOW_ORDER','ITEM_LIMIT','FIRST_MINIMUM'}
    for key in ['a','b']+(['a_new'] if final else []):
        p=package(registry,ds[key]['identity']); before=time.perf_counter(); ex=c.expand(p)
        expansions[key]=dict(expansion=ex,validation_seconds=time.perf_counter()-before)
        is_a=key!='b'
        for case in frozen['A' if is_a else 'B']:
            want=case['modified'] if key=='a_new' else case['expected']; data=bytes.fromhex(case['hex'])
            before=time.perf_counter(); actual=normalize(c.vm.execute(ex['plan'],data)); execution+=time.perf_counter()-before
            if type(want) is int:
                passed=(actual.get('status')=='success' and type(actual.get('value')) is int and actual['value']==want
                    and actual['output']=={'bytes_hex':want.to_bytes(2,'big').hex()} and actual['consumed']==len(data)
                    and actual['provenance']=={'span':[0,len(data)],'origins':[]})
            else:
                error=actual.get('error',{}); first=want in first_codes
                family=ds['new' if key=='a_new' else 'old']['identity']
                passed=(actual.get('status')=='reject' and error.get('code')==want and error.get('stage')=='validation'
                    and error.get('offset')==(0 if first or not is_a else 1)
                    and error.get('node')=='program/'+ds[key]['identity']+'/call/'+family+('/g1' if first else '/g2'))
            rows.append(dict(root=key,input_hex=case['hex'],expected=want,actual=actual,
                passed=passed and type(actual.get('work')) is int and actual['work']>0))
        for hx,code in frozen['invalid_A' if is_a else 'invalid_B'].items():
            data=bytes.fromhex(hx); actual=normalize(c.vm.execute(ex['plan'],data)); error=actual.get('error',{})
            rows.append(dict(root=key,input_hex=hx,expected=code,actual=actual,passed=error.get('code')==code
                and error.get('stage')=='structure' and error.get('offset')==min(len(data),2 if is_a else 1)))
        actual=normalize(c.vm.execute(ex['plan'],'bad'))
        rows.append(dict(root=key,expected='INPUT_TYPE',actual=actual,
            passed=actual=={'status':'plan_reject','error':{'code':'INPUT_TYPE'},'work':0}))
        for budget in (0,1,5):
            actual=normalize(c.vm.execute(ex['plan'],bytes([22,22]) if is_a else bytes([22]),limits={'work':budget}))
            rows.append(dict(root=key,expected='WORK_LIMIT',actual=actual,
                passed=actual.get('error',{}).get('code')=='WORK_LIMIT' and actual['work']==budget))
    return dict(all_passed=all(r['passed'] for r in rows),passed=sum(r['passed'] for r in rows),total=len(rows),rows=rows,
        identities={k:d['identity'] for k,d in ds.items()},expansions=expansions,execution_seconds=execution,
        wall_seconds=time.perf_counter()-start)
