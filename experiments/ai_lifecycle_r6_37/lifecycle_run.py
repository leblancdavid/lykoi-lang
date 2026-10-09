"""Frozen functional oracle and one actual-MCP staged lifecycle."""
import json
import time
from transport import ROOT, HERE, OUT, load, save, raw, sha, ask, c, Registry, Journal, package, normalize


def verify():
    for record in ('BASELINE.json','TASK-FREEZE.json'):
        pins = load(OUT / record).get('protected_files', load(OUT / record).get('inputs'))
        for name, pin in pins.items():
            assert sha(ROOT / name) == pin, name


def artifacts(final=False):
    state = Registry(OUT / 'authoring/registry').read()['state']
    defs = state['definitions']
    grouped = {name: [d for d in defs.values() if d['name'] == name]
        for name in ('WindowCharge','CallerA','CallerB')}
    old = next(d for d in grouped['WindowCharge'] if d['identity'] not in state['successors'])
    a = next(d for d in grouped['CallerA'] if d['identity'] not in state['successors'])
    b, = grouped['CallerB']
    result = dict(old=old, a=a, b=b)
    if final:
        new, = [d for d in grouped['WindowCharge'] if state['successors'].get(d['identity']) == old['identity']]
        anew, = [d for d in grouped['CallerA'] if state['successors'].get(d['identity']) == a['identity']]
        result.update(new=new, a_new=anew)
        assert len(state['migrations']) == 1
        assert state['migrations'][0] == dict(predecessor=old['identity'], successor=new['identity'],
            decisions={a['identity']: anew['identity'], b['identity']: None})
    for caller, family in (('a','old'),('b','old')) + ((('a_new','new'),) if final else ()):
        assert result[caller]['dependencies'] == {'WindowCharge': result[family]['identity']}
    for d in result.values():
        assert d['identity'] == c.identity(d)
    return result


def expect_charge(start, end, cap, successor):
    if start < 0:
        return 'START_NEGATIVE'
    if end > cap:
        return 'END_CAP'
    if start+start > end:
        return 'WINDOW_NARROW'
    value = end+start+(start if successor else 0)
    return value if 0 <= value <= 65535 else 'ENCODE_RANGE'


def acceptance(final=False):
    started = time.perf_counter()
    ds = artifacts(final)
    expectations = load(OUT / 'ACCEPTANCE-EXPECTATIONS.json')
    rows, expansions = [], {}
    registry = Registry(OUT / 'authoring/registry')

    def evaluate(label, p, data, expected, offset=None, stage=None, node_suffix=None):
        expanded = c.expand(p)
        actual = normalize(c.vm.execute(expanded['plan'], data))
        passed = False
        if type(expected) is int:
            passed = (actual.get('status') == 'success' and type(actual.get('value')) is int
                and actual['value'] == expected and actual['output'] == {'bytes_hex': expected.to_bytes(2,'big').hex()}
                and actual['consumed'] == len(data)
                and actual['provenance'] == {'span':[0,len(data)],'origins':[]})
        elif expected == 'INPUT_TYPE':
            passed = actual == {'status':'plan_reject','error':{'code':'INPUT_TYPE'},'work':0}
        else:
            error = actual.get('error', {})
            passed = (actual.get('status') == 'reject' and error.get('code') == expected
                and error.get('stage') == stage and error.get('offset') == offset
                and error.get('path') == ('value' if expected == 'ENCODE_RANGE' else None)
                and error.get('expected') == [])
            if node_suffix is not None:
                passed = passed and error.get('node') == 'program/'+p['program']['identity']+'/'+node_suffix
        if expected != 'INPUT_TYPE':
            passed = passed and type(actual.get('work')) is int and 0 < actual['work'] <= 100000
        rows.append(dict(label=label, input_hex=data.hex() if isinstance(data,bytes) else None,
            expected=expected, expected_offset=offset, expected_stage=stage,
            expected_node_suffix=node_suffix, actual=actual, passed=passed,
            plan_identity=expanded['plan_identity']))

    roots = [('a','old',False),('b','old',False)]
    if final:
        roots += [('a_new','new',True)]
    for key, familykey, successor in roots:
        root, family = ds[key], ds[familykey]
        p = package(registry, root['identity'])
        t = time.perf_counter(); ex = c.expand(p)
        expansions[key] = dict(expansion=ex, validation_seconds=time.perf_counter()-t)
        is_a = key.startswith('a')
        cases = expectations['A_pairs'] if is_a else [[x,x+20] for x in expectations['B_starts']]
        for start,end in cases:
            data = bytes([start,end]) if is_a else bytes([start])
            expected = expect_charge(start,end,200 if is_a else 180,successor)
            if type(expected) is int and is_a:
                expected += 3
            source = expectations['check_sources'].get(expected) if type(expected) is str else None
            suffix = 'charge/'+family['identity']+'/'+source[0] if source else None
            evaluate(f'{key}:{data.hex()}',p,data,expected,
                (1 if is_a and expected == 'END_CAP' else 0) if source else None,
                'validation' if source else None,suffix)
        for hx in expectations['invalid_A' if is_a else 'invalid_B']:
            data = bytes.fromhex(hx); needed = 2 if is_a else 1
            if len(data)<needed:
                offset=len(data); code='TRUNCATED'; suffix='read_start' if offset==0 else 'read_end'
            else:
                offset=needed; code='TRAILING'; suffix='input_end'
            evaluate(f'{key}:invalid:{hx}',p,data,code,offset,'structure',suffix)
        evaluate(key+':input-type',p,'bad', 'INPUT_TYPE')
        for budget in (0,1,5):
            actual=normalize(c.vm.execute(ex['plan'], bytes([0,20]) if is_a else bytes([0]),
                limits={'work':budget}))
            rows.append(dict(label=f'{key}:work:{budget}',actual=actual,
                passed=actual.get('status')=='reject' and actual['error']['code']=='WORK_LIMIT'
                    and actual['error']['stage']=='limit' and actual['work']==budget))
    for familykey in (['old','new'] if final else ['old']):
        family=ds[familykey]
        for index,(start,end,cap) in enumerate(expectations['constant_probes']):
            probe=c.seal(dict(name='OracleProbe',revision=1,params=[],
                dependencies={'WindowCharge':family['identity']},
                steps=[dict(id='charge',type='Int64',deps=[],node=dict(op='compose',
                    symbol='WindowCharge',identity=family['identity'],
                    args={k:{'const':v} for k,v in zip(('start','end','cap'),(start,end,cap))}))],
                order=['charge'],result={'ref':'charge'},result_type='Int64'))
            p=dict(version=c.VERSION,foundation=c.FOUNDATION,definitions=[family],program=probe)
            expected=expect_charge(start,end,cap,familykey=='new')
            source=expectations['check_sources'].get(expected) if type(expected) is str else None
            evaluate(f'{familykey}:const:{index}',p,b'',expected,0 if source else None,
                'validation' if source else ('encode' if expected=='ENCODE_RANGE' else None),
                'charge/'+family['identity']+'/'+source[0] if source else ('encode' if expected=='ENCODE_RANGE' else None))
        probe['steps'][0]['node']['args']['start']={'const':True}
        probe=c.seal(probe); p['program']=probe
        try:
            c.expand(p); actual={'unexpected':'accepted'}
        except c.Diagnostic as exc:
            actual=exc.data
        rows.append(dict(label=familykey+':bool-argument',actual=actual,
            passed=actual.get('code')=='TYPE' and actual.get('path')=='OracleProbe/charge'))
    return dict(passed=sum(r['passed'] for r in rows),total=len(rows),
        all_passed=all(r['passed'] for r in rows),rows=rows,expansions=expansions,
        identities={k:d['identity'] for k,d in ds.items()},wall_seconds=time.perf_counter()-started,
        dependency_expectations_passed=True)


def run():
    verify()
    started=time.perf_counter(); calls=[]; session=None; failure=None
    try:
        for stage,promptfile in (('original','REQUIREMENT.txt'),('modification','MODIFICATION.txt')):
            prompt=(OUT/promptfile).read_text()
            if stage=='original':
                prompt=(OUT/'GUIDE.txt').read_text()+'\n'+prompt
            remaining=1200-(time.perf_counter()-started)
            assert remaining>0
            record=ask('authoring',stage,prompt,session, min(600,remaining))
            calls.append(record); session=record['session']
            assert not record['errors'] and not record['timeout'] and record['returncode']==0
            assert sum(len(r['step_finishes']) for r in calls)<=30, 'MODEL_COMPLETION_BUDGET'
            assert sum(r['tool_calls'] for r in calls)<=40, 'MCP_BUDGET'
            result=acceptance(stage=='modification')
            save(OUT/('ORIGINAL-ACCEPTANCE.json' if stage=='original' else 'FUNCTIONAL.json'),result)
            assert result['all_passed'], 'FUNCTIONAL_ACCEPTANCE_FAILURE'
    except Exception as exc:
        failure=dict(exception=type(exc).__name__,detail=str(exc))
    save(OUT/'AUTHORING-CLOSED.json',dict(session=session,calls=calls,
        failure=failure,child_processes_terminated=True,model_calls_after_closure=0,
        wall_seconds=time.perf_counter()-started,budget_enforcement='Stage boundary checks; '
            'autonomous within-stage completion count not hard interrupted',
        staged_modification_released=len(calls)>1,coordinator_semantic_repairs=0))
    print('Authoring closed:', failure or 'completed')


def replay():
    verify()
    assert load(OUT/'AUTHORING-CLOSED.json')['child_processes_terminated']
    ds=artifacts(True)
    for key,d in ds.items():
        save(OUT/(key+'.json'),d)
    runs=[]
    for index in range(3):
        result=acceptance(True)
        save(OUT/f'REPLAY-{index+1}.json',result)
        assert result['all_passed']
        digest=__import__('hashlib').sha256(c.canonical(result['rows'])).hexdigest()
        runs.append(dict(passed=result['passed'],total=result['total'],rows_sha256=digest,
            wall_seconds=result['wall_seconds']))
    assert len({r['rows_sha256'] for r in runs})==1
    journal=Journal(OUT/'authoring/telemetry').recover()
    save(OUT/'REPLAY.json',dict(passed=True,runs=runs,model_calls=0,
        journal_recovered=True,registry_reconstructed=True,identities=ds,
        logical_work_errors_provenance_order_and_values_equal=True,
        trace='Frozen VM exposes no execution trace; error precedence and expanded order checked'))
    print('Model-free replay:', runs)


if __name__=='__main__':
    {'run':run,'replay':replay}[__import__('sys').argv[1]]()
