"""Prospective requirements and independently requirement-derived finite oracle."""
from common import c, package, normalize
import time

TASKS = [
    dict(id='T1', symbol='ReserveTotal', param='cap', constant=210, delta=7, bias=4,
        checks='x<=y (PAIR_ORDER, site x, label g1), then x+y<=cap (RESERVE_CAP, site y, label g2)',
        base='x+y', successor='x+y+5', order=['A', 'B']),
    dict(id='T2', symbol='DoubleQuota', param='cap', constant=170, delta=11, bias=6,
        checks='x<=cap (FIRST_CAP, site x, label g1), then y<=cap (SECOND_CAP, site y, label g2)',
        base='x+x+y', successor='x+x+y+y', order=['B', 'A']),
    dict(id='T3', symbol='FloorWeight', param='floor', constant=12, delta=9, bias=2,
        checks='floor<=x (BELOW_FLOOR, site x, label g1), then x<=y (WEIGHT_ORDER, site y, label g2)',
        base='x+y+y', successor='x+x+y+y', order=['A', 'B'])]


def requirement(t):
    return (f"Construct {t['symbol']}(x:Int64,y:Int64,{t['param']}:Int64)->Int64. "
        f"Ordered checks: {t['checks']}. Return {t['base']} using checked signed64 addition. "
        f"CallerA reads x then y as UInt8 (read_x/read_y), checks end-of-input (input_end) BEFORE computation, "
        f"composes (call) with {t['param']}={t['constant']}, adds {t['bias']} and returns Int64 encoded UInt16BE. "
        f"CallerB reads x as UInt8 (read_x), checks end-of-input (input_end) BEFORE computation, derives y=x+{t['delta']}, "
        f"composes (call) with {t['param']}={t['constant']} and returns unchanged. "
        "Admit reusable definition then two dependent callers. Retrieve and validate both, execute representative inputs. "
        "All definitions revision1. Stop after base stage. No successor yet.")


def modification(t):
    return (f"Create a signature-preserving {t['symbol']} successor changing result to {t['successor']}. "
        "Retain every original check, order, code and source label. Admit against exact predecessor. "
        "Create CallerA successor changing ONLY dependency and compose-call pins, retaining revision1 and all other content. "
        "Admit against CallerA predecessor. Record total explicit family migration: original CallerA updated, CallerB null/retain. "
        "Retrieve and validate selected CallerA and retained CallerB, execute examples. Preserve executable predecessor behavior.")


def expected(t, x, y, changed, is_a):
    if t['id'] == 'T1':
        if x > y:
            return 'PAIR_ORDER'
        if x+y > t['constant']:
            return 'RESERVE_CAP'
        value = x+y+(5 if changed else 0)
    elif t['id'] == 'T2':
        if x > t['constant']:
            return 'FIRST_CAP'
        if y > t['constant']:
            return 'SECOND_CAP'
        value = x+x+y+(y if changed else 0)
    else:
        if x < t['constant']:
            return 'BELOW_FLOOR'
        if x > y:
            return 'WEIGHT_ORDER'
        value = x+y+y+(x if changed else 0)
    return value+(t['bias'] if is_a else 0)


def expectations(t):
    points = [0, 1, 11, 12, 13, 80, 169, 170, 171, 209, 210, 211, 255]
    return dict(A=[dict(hex=bytes([x,y]).hex(), expected=expected(t,x,y,False,True), modified=expected(t,x,y,True,True)) for x in points for y in points],
        B=[dict(hex=bytes([x]).hex(), expected=expected(t,x,x+t['delta'],False,False)) for x in range(256)],
        invalid_A={'': 'TRUNCATED', '01': 'TRUNCATED', '010200': 'TRAILING', 'ffff00': 'TRAILING'},
        invalid_B={'': 'TRUNCATED', '0100': 'TRAILING', 'ff00': 'TRAILING'},
        expected_dependencies={'CallerA': 'predecessor', 'CallerB': 'predecessor', 'CallerA_successor': 'successor'},
        source='Requirement-derived before model output; same coordinator, AI-independent oracle, not independent cognition')


def artifacts(registry, t, final):
    state = registry.read()['state']; ds = state['definitions']; edges = state['successors']
    def original(name):
        found = [d for p,d in ds.items() if d['name']==name and p not in edges]
        assert len(found)==1, ('original', name)
        return found[0]
    old, a, b = original(t['symbol']), original('CallerA'), original('CallerB')
    result = dict(old=old, a=a, b=b)
    assert a['dependencies']==b['dependencies']=={t['symbol']:old['identity']}
    if final:
        def successor(d):
            found = [ds[p] for p,oldpin in edges.items() if oldpin==d['identity']]
            assert len(found)==1
            return found[0]
        new, anew = successor(old), successor(a)
        assert anew['dependencies']=={t['symbol']:new['identity']}
        assert state['migrations']==[dict(predecessor=old['identity'],successor=new['identity'],decisions={a['identity']:anew['identity'],b['identity']:None})]
        result.update(new=new,a_new=anew)
    for d in result.values():
        assert d['identity']==c.identity(d)
    return result


def acceptance(registry, t, frozen, final):
    started=time.perf_counter(); ds=artifacts(registry,t,final); rows=[]; expansions={}
    for key in ['a','b']+(['a_new'] if final else []):
        p=package(registry,ds[key]['identity']); before=time.perf_counter(); ex=c.expand(p)
        expansions[key]=dict(expansion=ex,validation_seconds=time.perf_counter()-before)
        is_a=key!='b'; cases=frozen['A' if is_a else 'B']
        for case in cases:
            expected_value=case['modified'] if key=='a_new' else case['expected']
            data=bytes.fromhex(case['hex']); actual=normalize(c.vm.execute(ex['plan'],data))
            if type(expected_value) is int:
                passed=(actual.get('status')=='success' and type(actual.get('value')) is int and actual['value']==expected_value
                    and actual['output']=={'bytes_hex':expected_value.to_bytes(2,'big').hex()} and actual['consumed']==len(data)
                    and actual['provenance']=={'span':[0,len(data)],'origins':[]})
            else:
                error=actual.get('error',{}); first=expected_value in ('PAIR_ORDER','FIRST_CAP','BELOW_FLOOR')
                family=ds['new' if key=='a_new' else 'old']['identity']
                site_x=expected_value in ('PAIR_ORDER','FIRST_CAP','BELOW_FLOOR')
                passed=(actual.get('status')=='reject' and error.get('code')==expected_value and error.get('stage')=='validation'
                    and error.get('offset')==(0 if site_x or not is_a else 1)
                    and error.get('node')=='program/'+ds[key]['identity']+'/call/'+family+('/g1' if first else '/g2'))
            passed=passed and type(actual.get('work')) is int and actual['work']>0
            rows.append(dict(root=key,input_hex=case['hex'],expected=expected_value,actual=actual,passed=passed))
        for hx,code in frozen['invalid_A' if is_a else 'invalid_B'].items():
            data=bytes.fromhex(hx); actual=normalize(c.vm.execute(ex['plan'],data)); error=actual.get('error',{})
            needed=2 if is_a else 1
            rows.append(dict(root=key,input_hex=hx,expected=code,actual=actual,passed=error.get('code')==code
                and error.get('stage')=='structure' and error.get('offset')==min(len(data),needed)))
        actual=normalize(c.vm.execute(ex['plan'],'bad'))
        rows.append(dict(root=key,expected='INPUT_TYPE',actual=actual,passed=actual=={'status':'plan_reject','error':{'code':'INPUT_TYPE'},'work':0}))
        for budget in (0,1,5):
            actual=normalize(c.vm.execute(ex['plan'],bytes([13,20]) if is_a else bytes([13]),limits={'work':budget}))
            rows.append(dict(root=key,expected='WORK_LIMIT',actual=actual,passed=actual.get('error',{}).get('code')=='WORK_LIMIT' and actual['work']==budget))
    return dict(all_passed=all(r['passed'] for r in rows),passed=sum(r['passed'] for r in rows),total=len(rows),rows=rows,
        identities={k:d['identity'] for k,d in ds.items()},expansions=expansions,wall_seconds=time.perf_counter()-started)
