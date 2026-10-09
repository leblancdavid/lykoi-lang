"""R6.29 bounded coordinator; imports immutable R6.28 transport/evaluation helpers."""
import importlib.util
import json
import sys
import time
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('r629_helpers', HERE.parent/'r6_28/experiment.py')
h = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)
h.HERE = HERE
ROOT, a, tools, transport = h.ROOT, h.a, h.tools, h.transport
save, read, sha, identity, now = h.save, h.read, h.sha, h.identity, h.now

def baseline():
    assert not (HERE/'BASELINE.json').exists()
    old = HERE.parent/'r6_28'
    pins = json.loads((old/'BASELINE.json').read_text())['protected_files']
    manifest = json.loads((old/'PUBLICATION-IDENTITIES.json').read_text())
    receipt = json.loads((old/'VERIFICATION.json').read_text())
    assert receipt['passed'] and receipt['publication_manifest_sha256']==sha(old/'PUBLICATION-IDENTITIES.json')
    for p, v in manifest['files'].items():
        assert sha(ROOT/p)==v['sha256'], p
        pins[p]=v['sha256']
    for n in ('PUBLICATION-IDENTITIES.json','VERIFICATION.json'):
        pins[(old/n).relative_to(ROOT).as_posix()]=sha(old/n)
    assert all(sha(ROOT/p)==v for p,v in pins.items())
    previous = json.loads((old/'BASELINE.json').read_text())
    assert sha(h.EXE)==previous['qualified_executable_sha256']
    assert json.loads((old/'RESULT.json').read_text())['classification']=='R6_28_SEMANTIC_CONSTRUCTION_SUPPORTED'
    assert len(previous['kernel_ledger']['baseline_kernel'])+len(previous['kernel_ledger']['preserved_additions'])==26
    save('BASELINE.json',dict(timestamp=now(),protected_files=pins,protected_count=len(pins),kernel=26,
        R6_28_publication_verified=True,R6_27_route_qualification='R6_27_TOOL_EXPOSURE_QUALIFIED',
        qualified_executable_sha256=sha(h.EXE),kernel_ledger=previous['kernel_ledger'],
        initial_git_status='clean (checked before creating R6.29 files)',
        unchanged=['production','R6.10 VM','R6.18 wrapper','R6.23 adapter','R6.24 dispatcher','R6.25 contracts/transport','R6.27 annotation']))
    print('Baseline verified',len(pins),'protected identities; kernel26')

def witness():
    h.verify_protected()
    assert not (HERE/'CAPABILITY-WITNESS.json').exists()
    s=tools.Session(['value','check','compose'])
    calls=[]
    def call(name,args):
        request={'function':{'name':name,'arguments':args}}
        response=s.dispatch(request)
        calls.append(dict(request=request,response=response))
        assert response['success'],response
    # Fixed scripted neutral control, no model and no selected task solution.
    call('declare_input',dict(definition='GateWitness',inputs=[dict(name='flag',type='Bool'),dict(name='n',type='Int64')]))
    call('apply_operation',dict(definition='GateWitness',alias='g',operation='check',expression='$flag',site=0,code='WitnessDenied',dependencies=['flag']))
    call('apply_operation',dict(definition='GateWitness',alias='a',operation='value',type='Int64',expression=['add','$n',1],dependencies=['n']))
    call('apply_operation',dict(definition='GateWitness',alias='b',operation='value',type='Int64',expression=['add','$a',1],dependencies=['a']))
    call('define_result',dict(definition='GateWitness',result='$b',result_type='Int64'))
    call('validate_candidate',dict(target='GateWitness'))
    observations=[]
    for args,code in [(dict(flag=True,n=1),None),(dict(flag=False,n=2**63-1),'WitnessDenied'),(dict(flag=True,n=2**63-1),'OVERFLOW')]:
        obs,t=h.observe(s.completed['artifact'],dict(args=args))
        x=obs['observation']
        assert (x['status']=='success' and x['value']==3) if code is None else x['error']['code']==code
        observations.append(dict(args=args,evidence=obs,times=t))
    # A typed computed Boolean is also expressible through the same interface.
    p=tools.Session(['value','check','compose'])
    pred=[]
    for name,args in [('declare_input',dict(definition='PredicateWitness',inputs=[dict(name='n',type='Int64')])),
        ('apply_operation',dict(definition='PredicateWitness',alias='p',operation='value',type='Bool',expression=['le',0,'$n'],dependencies=['n']))]:
        r=p.dispatch({'function':{'name':name,'arguments':args}})
        assert r['success']
        pred.append(dict(name=name,arguments=args,response=r))
    save('CAPABILITY-WITNESS.json',dict(timestamp=now(),passed=True,model_calls=0,calls=calls,
        artifact=s.completed['artifact'],observations=observations,predicate_calls=pred,
        capabilities={k:True for k in ['typed_Boolean_predicate','guard_evaluation','guard_rejection','dependent_arithmetic','ordered_error_precedence']},
        conflict='false guard and n=Int64_MAX: WitnessDenied; same n with true guard: OVERFLOW',
        task_selected_before_gate=False))
    print('Scripted capability gate PASS, including false-guard/overflow conflict')

def freeze():
    assert read('CAPABILITY-WITNESS.json')['passed'] and not (HERE/'FREEZE.json').exists()
    requirement='Create GuardedLeft(x:Int64,y:Int64). First compute and store the Bool predicate x <= y, then enforce that predicate with an ordered check using code GuardDenied and literal site 0. Only after that check passes, store the checked Int64 sum x+y, then store the checked Int64 sum of that first sum and x. Return the second sum as Int64. Exactly four ordered steps: Bool value, check, Int64 value, dependent Int64 value. Native Int64 overflow rejects at the first failing arithmetic step. Fixed UInt16BE output encoding rejects values outside 0..65535. A false guard must reject GuardDenied before either arithmetic step, including when either sum would overflow. Exact signature x,y; typed host literals, empty byte input.'
    save('REQUIREMENT.json',dict(id='R629-TINY-1',requirement=requirement,target='GuardedLeft',inputs=[['x','Int64'],['y','Int64']],operations=['value','check','value','value'],result_type='Int64',scored=False,
        source='Fresh coordinator-authored capability-tailored synthetic requirement selected after scripted gate; no completed implementation supplied',
        invalid_types='Bool/string/null are not Int64: wrapper TYPE. Float is outside the representation domain: wrapper SHAPE. Out-of-range signed integers: wrapper TYPE.',
        invalid_signature='Missing or extra argument names: wrapper SHAPE, before type/VM checks.',
        precedence='Signature then typed wrapper validation, predicate, guard, first add, second add, result, encoding. Guard failure absorbs subsequent overflow.'))
    cases=[]
    for x,y,v in [(2,5,9),(0,0,0),(-2,4,0),(1,65533,65535),(0,65535,65535)]:
        cases.append(dict(id='normal'+str(len(cases)),args=dict(x=x,y=y),expected=dict(status='success',value=v,output_hex=v.to_bytes(2,'big').hex(),consumed=0)))
    for name,x,y,code,step in [('guard',5,2,'GuardDenied',1),('guard_first_overflow',2**63-1,1,'GuardDenied',1),
        ('guard_second_overflow',2**62,0,'GuardDenied',1),('guard_underflow',-2,-(2**63),'GuardDenied',1),
        ('first_overflow',1,2**63-1,'OVERFLOW',2),('second_overflow',2**62-1,2**62-1,'OVERFLOW',3),
        ('first_underflow',-(2**63),-1,'OVERFLOW',2),('second_underflow',-(2**62),-1,'OVERFLOW',3),
        ('encode_high',0,65536,'ENCODE_RANGE',None),('encode_low',-1,0,'ENCODE_RANGE',None)]:
        cases.append(dict(id=name,args=dict(x=x,y=y),expected=dict(status='reject',code=code,stage='encode' if step is None else 'structure',step_index=step)))
    for name,args,code in [('bool',dict(x=True,y=1),'TYPE'),('string',dict(x='1',y=1),'TYPE'),
        ('null',dict(x=None,y=1),'TYPE'),('float',dict(x=1.0,y=1),'SHAPE'),('range',dict(x=2**63,y=1),'TYPE'),
        ('missing',dict(x=1),'SHAPE'),('extra',dict(x=1,y=2,z=3),'SHAPE'),('signature_type_conflict',dict(x=True),'SHAPE')]:
        cases.append(dict(id=name,args=args,expected=dict(status='wrapper_reject',code=code)))
    save('ACCEPTANCE.json',dict(cases=cases,all_required=True,conflict_cases=['guard_first_overflow','guard_second_overflow','guard_underflow'],
        repeat_comparison='Complete typed observations, errors, provenance, work, ordering, package and expansion identities; timing excluded'))
    prompt='R6.29 authorized real guarded semantic construction.\n'+requirement+'\nUse the four existing Lykoi tools with truthful local construction effects. Maximum16 semantic tool calls and4 correction turns, one session. Stop immediately after successful validate_candidate. Dependencies enumerate every referenced input or prior alias exactly, including site references. Expressions are $name, typed literals or [add|le|eq,operand,operand]. No completed implementation is supplied. Construct and validate using tools; do not substitute a JSON proposal.'
    save('PROMPT.json',dict(text=prompt))
    cfg=h.config()
    cfg['agent']['r628']['steps']=21
    cfg['agent']['r628']['prompt']='Construct the requested R6.29 symbolic program using only the four Lykoi semantic tools. They mutate a real local construction Session. Stop on completed validation. Maximum16 semantic calls and4 correction turns. No files, shell, other tools or delegation.'
    save('OPENCODE-CONFIG.json',cfg)
    save('MODEL-CONFIG.json',dict(model=h.MODEL,requested_variant='high',effective_reasoning='UNATTESTED',max_semantic_calls=16,max_correction_turns=4,max_completion_steps=21,max_output_tokens=4096,
        helper_agent_key='r628 retained as a configuration key only; R6.29 prompt and endpoint',executable_sha256=sha(h.EXE)))
    save('TOOL-EXPOSURE.json',dict(original=tools.definitions(['value','check','compose']),published=h.definitions(),echo=False,
        schema_delta='R6.27 qualified object-root annotation only',backend='R6.25 -> R6.24 -> R6.23 -> R6.18 -> R6.10'))
    files=['experiment.py','PROTOCOL.md','BASELINE.json','CAPABILITY-WITNESS.json','REQUIREMENT.json','ACCEPTANCE.json','PROMPT.json','OPENCODE-CONFIG.json','MODEL-CONFIG.json','TOOL-EXPOSURE.json']
    save('FREEZE.json',dict(timestamp=now(),files={p:sha(HERE/p) for p in files},model_calls=0))
    print('Frozen',len(cases),'acceptance cases before model exposure')

def bridge():
    h.verify_freeze()
    session=tools.Session(['value','check','compose'])
    seen=set()
    count=corrections=0
    correcting=False
    for line in sys.stdin:
        request=transport.strict_loads(line,allow_provider_numbers=True)
        if 'id' not in request:
            continue
        record=dict(timestamp=now(),request=request)
        try:
            method=request.get('method')
            if method=='initialize':
                result=dict(protocolVersion=request['params']['protocolVersion'],capabilities={'tools':{}},serverInfo={'name':'r629-semantic','version':'1'})
            elif method=='tools/list':
                result={'tools':h.definitions()}
            elif method=='ping':
                result={}
            elif method=='tools/call':
                count+=1
                if correcting:
                    corrections+=1
                if count>16 or corrections>4:
                    dispatch=dict(success=False,arguments_valid=False,seconds=0,response=dict(ok=False,error=dict(code='R629_BUDGET',detail='bounded authoring exhausted')))
                else:
                    p=request['params']
                    native=dict(id='mcp:'+str(request['id']),type='function',function=dict(name=p['name'],arguments=json.dumps(p.get('arguments'))))
                    try:
                        envelope=transport.normalize([native],'openai-compatible','gpt-6.1-sol',count-1,session.schemas,seen)[0]
                        record['normalized']=envelope
                        dispatch=session.dispatch(transport.semantic_call(envelope))
                    except Exception as exc:
                        dispatch=dict(success=False,arguments_valid=False,seconds=0,response=dict(ok=False,error=dict(code='TRANSPORT',detail=str(exc))))
                correcting=not dispatch['success']
                record.update(dispatch=dispatch,semantic_call_count=count,correction_turns=corrections)
                response=dispatch['response']
                result=dict(content=[dict(type='text',text=json.dumps(response))],structuredContent=response,isError=not dispatch['success'])
                save('LIVE/STATE.json',dict(packet=session.packet,completed=session.completed,semantic_calls=count,correction_turns=corrections))
                if session.completed and not (HERE/'LIVE/ARTIFACT.json').exists():
                    save('LIVE/ARTIFACT.json',session.completed['artifact'])
                    save('LIVE/SYMBOLIC-PACKET.json',session.packet)
            else:
                raise ValueError('unsupported method')
            wire=dict(jsonrpc='2.0',id=request['id'],result=result)
        except Exception as exc:
            wire=dict(jsonrpc='2.0',id=request['id'],error=dict(code=-32602,message=str(exc)))
        record['response']=wire
        with (HERE/'LIVE/MCP.jsonl').open('a',encoding='utf-8') as f:
            f.write(json.dumps(record)+'\n')
        print(json.dumps(wire),flush=True)

def observe(artifact,case):
    # Invalid host floats cannot enter canonical Int64-only identity encoding.
    # The unchanged wrapper rejects them before this encoding is reached.
    return h.observe(artifact,case)

def matched(artifact,case,obs):
    actual,e=obs['observation'],case['expected']
    if actual['status']!=e['status']:
        return False
    if e['status']=='success':
        return type(actual['value']) is int and actual['value']==e['value'] and actual['output']['bytes_hex']==e['output_hex'] and actual['consumed']==0
    if e['status']=='wrapper_reject':
        return actual['diagnostic']['code']==e['code']
    good=actual['error']['code']==e['code'] and actual['error']['stage']==e['stage']
    if e['step_index'] is not None:
        step=artifact['definitions'][0]['steps'][e['step_index']]['id']
        mapping=obs['expanded']['map']
        good=good and any(v['local']==step and k==actual['error']['node'] for k,v in mapping.items())
    return good

def evaluate():
    h.verify_freeze()
    assert read('LIVE/RESULT.json')['author_process_terminated'] and not (HERE/'RESULT.json').exists()
    events=[json.loads(s) for s in (HERE/'LIVE/EVENTS.jsonl').read_text().splitlines() if s.startswith('{')]
    rows=[json.loads(s) for s in (HERE/'LIVE/MCP.jsonl').read_text().splitlines()]
    calls=[r for r in rows if r['request'].get('method')=='tools/call']
    steps=[e for e in events if e['type']=='step_finish']
    export=read('LIVE/SESSION-EXPORT.json')
    assistants=[m['info'] for m in export['messages'] if m['info']['role']=='assistant']
    m=dict(model=h.MODEL,model_calls=len(assistants),semantic_tool_calls=len(calls),argument_valid=sum(r['dispatch']['arguments_valid'] for r in calls),
        successful_operations=sum(r['dispatch']['success'] for r in calls),correction_turns=read('LIVE/STATE.json')['correction_turns'],
        tokens={k:sum(e['part']['tokens'][k] for e in steps) for k in ('input','output','reasoning','total')},
        cached_read=sum(e['part']['tokens']['cache']['read'] for e in steps),SDK_cost=sum(e['part']['cost'] for e in steps),
        session_wall_seconds=read('LIVE/RESULT.json')['wall_seconds'],tool_dispatch_seconds=sum(r['dispatch']['seconds'] for r in calls),
        assistant_message_elapsed_seconds=sum((v['time']['completed']-v['time']['created'])/1000 for v in assistants),
        pure_inference_seconds=None,API_billing=None,effective_reasoning='UNATTESTED',hidden_provider_retries=None,
        provider_errors=[e for e in events if e['type']=='error'],assistant_metadata=assistants)
    m['argument_invalid']=len(calls)-m['argument_valid']
    m['construction_failures']=len(calls)-m['successful_operations']
    complete=(HERE/'LIVE/ARTIFACT.json').exists()
    functional=replay=False
    if complete:
        artifact=read('LIVE/ARTIFACT.json')
        d=artifact['definitions'][0]
        req=read('REQUIREMENT.json')
        structural=len(artifact['definitions'])==1 and artifact['target']==req['target'] and [[p['name'],p['type']] for p in d['params']]==req['inputs'] and [s['node']['op'] for s in d['steps']]==req['operations'] and d['order']==[s['id'] for s in d['steps']]
        records=[]
        for case in read('ACCEPTANCE.json')['cases']:
            obs,t=observe(artifact,case)
            records.append(dict(case=case,evidence=obs,times=t,passed=matched(artifact,case,obs),identity=identity(obs)))
        functional=structural and all(r['passed'] for r in records)
        save('FUNCTIONAL.json',dict(passed=functional,structural_valid=structural,records=records,model_calls=0,artifact_sha256=sha(HERE/'LIVE/ARTIFACT.json'),artifact_content_identity=identity(artifact)))
        passes=[]
        for i in range(3):
            saved=read('LIVE/ARTIFACT.json')
            repeated=[]
            for r in records:
                obs,t=observe(saved,r['case'])
                repeated.append(dict(evidence=obs,times=t,equal=obs==r['evidence'],identity=identity(obs)))
            passes.append(dict(pass_number=i+1,records=repeated,all_equal=all(r['equal'] for r in repeated),artifact_sha256=sha(HERE/'LIVE/ARTIFACT.json')))
        replay=all(p['all_equal'] for p in passes)
        save('REPLAY.json',dict(passes=passes,all_equal=replay,model_calls=0,author_process_terminated=True,artifact_reloaded=True,
            compared=['typed values','errors','provenance','logical work','ordered entry trace','package/expanded plan/observation identities','artifact identity']))
        m['adapter_times']=read('LIVE/STATE.json')['completed']['times']
    else:
        save('FUNCTIONAL.json',dict(status='NOT_REACHED',model_calls=0))
        save('REPLAY.json',dict(status='NOT_REACHED',model_calls=0))
    exposure=next(r['response']['result']['tools'] for r in rows if r['request'].get('method')=='tools/list')
    protocol=read('LIVE/DELIVERY.json')['matches_requested'] and exposure==h.definitions() and len(calls)<=16 and m['correction_turns']<=4
    classification='R6_29_GUARDED_CONSTRUCTION_SUPPORTED' if functional and replay and protocol else 'R6_29_CONSTRUCTION_PARTIAL'
    if not protocol:
        classification='R6_29_PROTOCOL_HALT'
    elif not complete:
        classification='R6_29_MODEL_AUTHORING_GAP' if calls else 'R6_29_TOOL_INTEGRATION_GAP'
    save('MEASUREMENTS.json',m)
    save('RESULT.json',dict(timestamp=now(),classification=classification,capability_gate=True,complete_artifact=complete,functional_acceptance=functional,AI_independent_replay=replay,protocol_valid=protocol,stopped=True))
    print(classification,'functional',functional,'replay',replay)

def verify():
    h.verify_freeze()
    rows=[json.loads(s) for s in (HERE/'LIVE/MCP.jsonl').read_text().splitlines()]
    s=tools.Session(['value','check','compose'])
    for r in rows:
        if r['request'].get('method')=='tools/call':
            p=r['request']['params']
            assert r['normalized']['semantic_arguments']==p['arguments']
            response=s.dispatch({'function':dict(name=p['name'],arguments=p['arguments'])})
            assert response['response']==r['dispatch']['response']
    assert s.completed['artifact']==read('LIVE/ARTIFACT.json') and s.packet==read('LIVE/SYMBOLIC-PACKET.json')
    f,r=read('FUNCTIONAL.json'),read('REPLAY.json')
    assert f['passed'] and r['all_equal']
    assert [row['case'] for row in f['records']]==read('ACCEPTANCE.json')['cases']
    for row in f['records']:
        assert matched(s.completed['artifact'],row['case'],row['evidence'])
    for p in r['passes']:
        assert all(x['evidence']==y['evidence'] and x['identity']==y['identity'] for x,y in zip(p['records'],f['records']))
    suite=subprocess.run([sys.executable,'-m','unittest','discover','-s','.','-p','test_transport.py','-v'],cwd=HERE.parent/'r6_25',capture_output=True,text=True,timeout=120)
    assert suite.returncode==0,suite.stderr
    save('OFFLINE-CHECKS.json',dict(timestamp=now(),passed=True,lineage_verified=True,frozen_expectations_verified=len(f['records']),replay_records_verified=3*len(f['records']),model_calls=0,manual_repairs=0,transport_suite=dict(stdout=suite.stdout,stderr=suite.stderr,returncode=suite.returncode)))
    print('Offline lineage, acceptance, replay and transport verified')

def publish():
    h.verify_freeze()
    assert read('OFFLINE-CHECKS.json')['passed']
    files={}
    paths=[p for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name not in ('PUBLICATION-IDENTITIES.json','VERIFICATION.json')]
    paths += [HERE.parent/'R6_29-REPORT.md']+[ROOT/'docs'/n for n in ('project-overview-r6.29.md','research-log-r6.29.md','decisions-r6.29.md')]
    for p in sorted(paths):
        text=p.read_text(encoding='utf-8')
        if p.suffix=='.json':
            json.loads(text)
        if p.suffix in ('.md','.py'):
            assert all(line==line.rstrip() for line in text.splitlines()),p
        assert not h.re.search(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|\bsk-[A-Za-z0-9_-]{20,}',text),p
        if p.suffix=='.md':
            for link in h.re.findall(r'\]\(([^)]+)\)',text):
                if not link.startswith(('https:','http:')):
                    assert (p.parent/link.split('#')[0]).resolve().exists(),link
        files[p.relative_to(ROOT).as_posix()]=dict(sha256=sha(p),bytes=p.stat().st_size)
    diff=subprocess.run(['git','diff','--check'],capture_output=True,text=True,cwd=ROOT)
    assert diff.returncode==0
    save('PUBLICATION-IDENTITIES.json',dict(timestamp=now(),files=files))
    save('VERIFICATION.json',dict(timestamp=now(),passed=True,classification=read('RESULT.json')['classification'],protected_count=h.verify_protected(),protected_mismatches=[],kernel=26,freeze_verified=True,
        publication_manifest_sha256=sha(HERE/'PUBLICATION-IDENTITIES.json'),publication_files=len(files),JSON_links_whitespace_checked=True,credentials_published=False,
        git_diff_check=dict(returncode=diff.returncode,stdout=diff.stdout,stderr=diff.stderr),inference_calls_during_publication=0,P6_A04_acceptance=False,P6_A05_access=False,stopped=True))
    assert all(sha(ROOT/p)==v['sha256'] for p,v in files.items())
    print('Publication verified',len(files),'files;',h.verify_protected(),'protected identities')

if __name__=='__main__':
    {'baseline':baseline,'witness':witness,'freeze':freeze,'bridge':bridge,'author':h.author,'evaluate':evaluate,'verify':verify,'publish':publish}[sys.argv[1]]()
