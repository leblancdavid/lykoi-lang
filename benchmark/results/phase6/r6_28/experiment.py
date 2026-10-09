"""R6.28 coordinator, actual MCP bridge and offline evaluator; frozen semantics."""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
TEMP = Path(r'C:\Users\lblan\AppData\Local\Temp\opencode')
MODEL = 'openai/gpt-6.1-sol'
EXE = Path(os.environ['APPDATA']) / 'npm/node_modules/opencode-ai/bin/opencode.exe'

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

tools = load('r628_tools', HERE.parent/'r6_24/tools.py')
transport = load('r628_transport', HERE.parent/'r6_25/transport.py')
annotation = load('r628_annotation', HERE.parent/'r6_27/adapter.py')
a = tools.a

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def identity(value):
    return hashlib.sha256(a.c.canonical(value)).hexdigest()

def now():
    return datetime.now(timezone.utc).isoformat()

def save(name, value):
    p = HERE/name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, indent=2, ensure_ascii=True)+'\n', encoding='utf-8')

def read(name):
    return json.loads((HERE/name).read_text(encoding='utf-8'))

def definitions():
    return [dict(name=t['function']['name'], description=t['function']['description'],
                 inputSchema=annotation.publish(t['function']['parameters']))
            for t in tools.definitions(['value', 'check', 'compose'])]

def config():
    return {'$schema':'https://opencode.ai/config.json','model':MODEL,'small_model':MODEL,
        'share':'disabled','autoupdate':False,'snapshot':False,'instructions':[],'plugin':[],
        'lsp':False,'formatter':False,'compaction':{'auto':False},'enabled_providers':['openai'],
        'permission':{'*':'deny','lykoi_*':'allow'},'tools':{'*':False,'lykoi_*':True},
        'agent':{'r628':{'mode':'primary','model':MODEL,'variant':'high','steps':17,
            'options':{'maxOutputTokens':4096},'permission':{'*':'deny','lykoi_*':'allow'},
            'prompt':'Construct the requested symbolic program using only the four Lykoi semantic tools. They mutate a real in-memory construction session and validate via the deterministic backend. Stop immediately on completed validation. Do not use files, shell, other tools or delegate. Maximum12 tool calls and4 correction turns.'}},
        'mcp':{'lykoi':{'type':'local','command':[sys.executable,str(HERE/'experiment.py'),'bridge'],'enabled':True},
            'codegraphcontext':{'enabled':False},'shadcn':{'enabled':False},'pixellab':{'enabled':False}}}

def verify_protected():
    pins = read('BASELINE.json')['protected_files']
    assert all(sha(ROOT/p)==h for p,h in pins.items()), 'protected identity mismatch'
    return len(pins)

def verify_freeze():
    assert all(sha(HERE/p)==h for p,h in read('FREEZE.json')['files'].items()), 'freeze mismatch'
    verify_protected()

def prepare():
    assert not (HERE/'BASELINE.json').exists()
    old = HERE.parent/'r6_27'
    pins = json.loads((old/'BASELINE.json').read_text())['protected_files']
    manifest = old/'PUBLICATION-IDENTITIES.json'
    receipt = json.loads((old/'VERIFICATION.json').read_text())
    assert receipt['passed'] and receipt['publication_manifest_sha256']==sha(manifest)
    publication = json.loads(manifest.read_text())
    for p,v in publication['files'].items():
        assert sha(ROOT/p)==v['sha256'], p
        pins[p]=v['sha256']
    for n in ('PUBLICATION-IDENTITIES.json','VERIFICATION.json'):
        p=old/n
        pins[p.relative_to(ROOT).as_posix()]=sha(p)
    assert all(sha(ROOT/p)==h for p,h in pins.items())
    ledger=json.loads((HERE.parent/'r6_25/BASELINE.json').read_text())['kernel_ledger']
    assert len(ledger['baseline_kernel'])+len(ledger['preserved_additions'])==26
    assert json.loads((old/'RESULT.json').read_text())['classification']=='R6_27_TOOL_EXPOSURE_QUALIFIED'
    executable=next(v for v in [json.loads((old/'EXACT-LIVE-3/DELIVERY.json').read_text())])
    assert sha(EXE)==executable['executable_sha256']
    save('BASELINE.json',dict(timestamp=now(),protected_files=pins,protected_count=len(pins),kernel=26,
        kernel_ledger=ledger,R6_27_publication_verified=True,R6_27_publication_sha256=sha(manifest),
        qualified_executable_sha256=sha(EXE),qualification='R6_27_TOOL_EXPOSURE_QUALIFIED',
        backend_paths=[str(a.HERE/'adapter.py'),str(a.c.HERE/'composition.py')],
        git_status=subprocess.run(['git','status','--short'],capture_output=True,text=True).stdout))
    requirement='Create target TwiceRight(left:Int64,right:Int64). Compute the sum of left and right as a stored Int64 value, then add right to that stored sum as a second dependent Int64 operation. Return the second value. Exactly two ordered value operations in one definition. Keep native signed64 addition overflow and fixed UInt16BE encoding errors; add no guards or other operations. Inputs are typed literals supplied by the host, with empty byte input.'
    save('REQUIREMENT.json',dict(id='R628-TINY-1',requirement=requirement,scored=False,
        source='Fresh coordinator-authored capability-tailored synthetic requirement; no supplied solution',
        target='TwiceRight',inputs=[['left','Int64'],['right','Int64']],operations=['value','value'],result_type='Int64'))
    cases=[]
    for left,right,value in [(7,11,29),(0,0,0),(65535,0,65535),(1,32767,65535),(-2,1,0)]:
        cases.append(dict(args=dict(left=left,right=right),expected=dict(status='success',value=value,output_hex=value.to_bytes(2,'big').hex(),consumed=0)))
    for args,code,stage in [(dict(left=0,right=32768),'ENCODE_RANGE','encode'),
        (dict(left=-1,right=0),'ENCODE_RANGE','encode'),
        (dict(left=2**63-1,right=1),'OVERFLOW','structure'),
        (dict(left=2**63-2,right=1),'OVERFLOW','structure')]:
        cases.append(dict(args=args,expected=dict(status='reject',code=code,stage=stage)))
    cases += [dict(args=dict(left=True,right=1),expected=dict(status='wrapper_reject',code='TYPE')),
              dict(args=dict(left=1),expected=dict(status='wrapper_reject',code='SHAPE'))]
    save('ACCEPTANCE.json',dict(cases=cases,all_required=True,ordering='First stored sum then dependent second value; no topological resort',
        repeat_comparison='Entire envelopes, entry traces, package and expanded identities; timing excluded'))
    prompt='R6.28 authorized real semantic construction, not inert qualification.\n'+requirement+'\nUse the actual Lykoi tools to declare, construct, finalize and validate. Maximum12 semantic calls and4 correction turns. Stop on completed validation. Dependencies list every referenced input or prior alias exactly; expressions use $name or [add|le|eq, operand, operand]. Input names can be referenced in expressions. Values are immutable. define_result finalizes without later edits. validate_candidate seals and expands the real artifact; target must return Int64. No earlier solution is supplied. The tools perform only local deterministic symbolic construction, without external effects. Do not answer with a proposed JSON program instead of calling tools.'
    save('PROMPT.json',dict(text=prompt))
    save('TOOL-EXPOSURE.json',dict(original=tools.definitions(['value','check','compose']),published=definitions(),
        semantic_backend='unchanged R6.24 Session.dispatch -> R6.23 adapter -> R6.18 wrapper -> R6.10 VM',
        schema_delta='Only root type object annotation on object-only apply_operation oneOf',echo=False))
    save('OPENCODE-CONFIG.json',config())
    save('MODEL-CONFIG.json',dict(selected=MODEL,reasoning_requested='high',effective_reasoning='UNATTESTED',
        max_output_tokens=4096,max_completion_steps=17,max_semantic_calls=12,max_correction_turns=4,
        executable_sha256=sha(EXE),version=subprocess.run([str(EXE),'--version'],capture_output=True,text=True).stdout.strip(),
        installed_configuration_changed=False))
    # Neutral backend connectivity control, no requirement solution and no model.
    s=tools.Session(['value','check','compose'])
    call={'function':{'name':'declare_input','arguments':{'definition':'Connectivity','inputs':[]}}}
    response=s.dispatch(call)
    assert response['success'] and s.packet['definitions'][0]['name']=='Connectivity'
    save('BACKEND-CONTROL.json',dict(call=call,response=response,packet=s.packet,model_calls=0,
        real_mutation_observed=True,requirement_solution_constructed=False))
    names=['experiment.py','PROTOCOL.md','BASELINE.json','REQUIREMENT.json','ACCEPTANCE.json','PROMPT.json',
           'TOOL-EXPOSURE.json','OPENCODE-CONFIG.json','MODEL-CONFIG.json','BACKEND-CONTROL.json']
    save('FREEZE.json',dict(timestamp=now(),files={n:sha(HERE/n) for n in names},model_calls=0))
    print('Frozen requirement, acceptance, route and real backend; protected',len(pins))

def bridge():
    verify_freeze()
    session=tools.Session(['value','check','compose'])
    seen=set()
    count=corrections=0
    correcting=False
    for line in sys.stdin:
        request=transport.strict_loads(line,allow_provider_numbers=True)
        if 'id' not in request:
            continue
        method=request.get('method')
        record=dict(timestamp=now(),request=request)
        try:
            if method=='initialize':
                result=dict(protocolVersion=request['params']['protocolVersion'],capabilities={'tools':{}},serverInfo={'name':'r628-semantic','version':'1'})
            elif method=='tools/list':
                result={'tools':definitions()}
            elif method=='ping':
                result={}
            elif method=='tools/call':
                count+=1
                if correcting:
                    corrections+=1
                if count>12 or corrections>4:
                    response=dict(ok=False,error=dict(code='R628_BUDGET',detail='construction budget exhausted'))
                    dispatch=dict(success=False,arguments_valid=False,seconds=0)
                else:
                    p=request['params']
                    native=dict(id='mcp:'+str(request['id']),type='function',function=dict(name=p['name'],arguments=json.dumps(p.get('arguments'))))
                    try:
                        envelope=transport.normalize([native],'openai-compatible','gpt-6.1-sol',count-1,session.schemas,seen)[0]
                        record['normalized']=envelope
                        dispatch=session.dispatch(transport.semantic_call(envelope))
                        response=dispatch['response']
                    except Exception as exc:
                        response=dict(ok=False,error=dict(code='TRANSPORT',detail=str(exc)))
                        dispatch=dict(success=False,arguments_valid=False,seconds=0)
                correcting=not dispatch['success']
                record.update(dispatch=dispatch,semantic_call_count=count,correction_turns=corrections)
                result=dict(content=[dict(type='text',text=json.dumps(response))],structuredContent=response,isError=not dispatch['success'])
                save('LIVE/STATE.json',dict(packet=session.packet,finalized=sorted(session.finalized),completed=session.completed,
                    semantic_calls=count,correction_turns=corrections))
                if session.completed:
                    if not (HERE/'LIVE/ARTIFACT.json').exists():
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

def author():
    verify_freeze()
    assert TEMP.is_dir() and not (HERE/'LIVE').exists()
    (HERE/'LIVE').mkdir()
    cfg=read('OPENCODE-CONFIG.json')
    env=os.environ.copy()
    env.update(OPENCODE_CONFIG_CONTENT=json.dumps(cfg),OPENCODE_DISABLE_PROJECT_CONFIG='1',
        OPENCODE_DISABLE_EXTERNAL_SKILLS='1',OPENCODE_DISABLE_CLAUDE_CODE_SKILLS='1',OPENCODE_PURE='1')
    args=['run','--pure','--model',MODEL,'--variant','high','--agent','r628','--format','json','--title','R6.28 single semantic attempt']
    prompt=read('PROMPT.json')['text']
    save('LIVE/REQUEST.json',dict(timestamp=now(),command=['opencode']+args,stdin_prompt=prompt,cwd=str(TEMP),configuration=cfg))
    begin=time.perf_counter()
    proc=subprocess.Popen([str(EXE)]+args,cwd=TEMP,env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    try:
        out,err=proc.communicate(prompt.encode('utf-8'),timeout=240)
        termination='COMPLETED'
    except subprocess.TimeoutExpired:
        subprocess.run(['taskkill','/PID',str(proc.pid),'/T','/F'],capture_output=True)
        out,err=proc.communicate()
        termination='TIMEOUT'
    (HERE/'LIVE/EVENTS.jsonl').write_bytes(out)
    (HERE/'LIVE/STDERR.txt').write_bytes(err)
    save('LIVE/RESULT.json',dict(timestamp=now(),returncode=proc.returncode,termination=termination,
        wall_seconds=time.perf_counter()-begin,author_process_terminated=proc.poll() is not None))
    events=[json.loads(line) for line in out.decode('utf-8').splitlines() if line.startswith('{')]
    sessions={e['sessionID'] for e in events if 'sessionID' in e}
    if len(sessions)==1:
        exported=subprocess.run([str(EXE),'export',next(iter(sessions))],capture_output=True,encoding='utf-8',timeout=30)
        data=json.loads(exported.stdout)
        save('LIVE/SESSION-EXPORT.json',data)
        users=[p['text'] for m in data['messages'] if m['info']['role']=='user' for p in m['parts'] if p['type']=='text']
        save('LIVE/DELIVERY.json',dict(matches_requested=users==[prompt],user_text=users,session=next(iter(sessions))))
    print('One author session ended:',termination,'artifact:',(HERE/'LIVE/ARTIFACT.json').exists())

def serial(x):
    if type(x) is bytes:
        return {'bytes_hex':x.hex()}
    if type(x) is dict:
        return {k:serial(v) for k,v in x.items()}
    if type(x) in (list,tuple):
        return [serial(v) for v in x]
    return x

def observe(artifact,case):
    times={}
    begin=time.perf_counter()
    try:
        pkg=a.package(artifact,case['args'])
        a.c.validate(pkg)
        times['validation_seconds']=time.perf_counter()-begin
        begin=time.perf_counter()
        expanded=a.c.expand(pkg)
        times['expansion_including_validation_seconds']=time.perf_counter()-begin
        begin=time.perf_counter()
        result=a.c.vm.execute(expanded['plan'],b'')
        times['execution_including_VM_validation_seconds']=time.perf_counter()-begin
        trace=[]
        original=a.c.vm.Machine
        class TraceMachine(original):
            def run(self,node,env,depth=1):
                trace.append(dict(node=node['id'],cursor=self.i,work_before=self.work,depth=depth))
                return super().run(node,env,depth)
        with patch.object(a.c.vm,'Machine',TraceMachine):
            traced=a.c.vm.execute(expanded['plan'],b'')
        assert traced==result
        value=dict(observation=serial(result),ordered_entry_trace=trace,expanded=expanded,package=pkg,
            package_identity=identity(pkg),result_type='Int64' if result['status']=='success' else None)
    except a.c.Diagnostic as exc:
        times['wrapper_rejection_seconds']=time.perf_counter()-begin
        value=dict(observation=dict(status='wrapper_reject',diagnostic=exc.data),ordered_entry_trace=[],result_type=None)
    return value,times

def evaluate():
    verify_freeze()
    assert read('LIVE/RESULT.json')['author_process_terminated']
    assert not (HERE/'RESULT.json').exists()
    events=[json.loads(s) for s in (HERE/'LIVE/EVENTS.jsonl').read_text().splitlines() if s.startswith('{')]
    steps=[e for e in events if e['type']=='step_finish']
    rows=[json.loads(s) for s in (HERE/'LIVE/MCP.jsonl').read_text().splitlines()] if (HERE/'LIVE/MCP.jsonl').exists() else []
    calls=[r for r in rows if r['request'].get('method')=='tools/call']
    metrics=dict(model=MODEL,completion_steps=len(steps),semantic_tool_calls=len(calls),
        argument_valid=sum(r.get('dispatch',{}).get('arguments_valid',False) for r in calls),
        construction_failures=sum(not r.get('dispatch',{}).get('success',False) for r in calls),
        correction_turns=read('LIVE/STATE.json')['correction_turns'] if (HERE/'LIVE/STATE.json').exists() else 0,
        tokens={k:sum(e['part']['tokens'][k] for e in steps) for k in ('input','output','reasoning','total')},
        cached_read=sum(e['part']['tokens']['cache']['read'] for e in steps),SDK_cost=sum(e['part']['cost'] for e in steps),
        author_session_wall_seconds=read('LIVE/RESULT.json')['wall_seconds'],
        deterministic_tool_dispatch_seconds=sum(r.get('dispatch',{}).get('seconds',0) for r in calls),
        API_billing=None,pure_inference_seconds=None,hidden_provider_retries=None,effective_reasoning='UNATTESTED',
        provider_errors=[e for e in events if e['type']=='error'])
    # SDK times from the exported actual assistant messages, not inferred model time.
    export=read('LIVE/SESSION-EXPORT.json') if (HERE/'LIVE/SESSION-EXPORT.json').exists() else {'messages':[]}
    metrics['assistant_message_metadata']=[m['info'] for m in export['messages'] if m['info']['role']=='assistant']
    metrics['model_calls_observed']=len(metrics['assistant_message_metadata'])
    functional=replay=False
    complete=(HERE/'LIVE/ARTIFACT.json').exists()
    if complete:
        artifact=read('LIVE/ARTIFACT.json')
        req=read('REQUIREMENT.json')
        ds=artifact['definitions']
        structural=len(ds)==1 and artifact['target']==req['target'] and [[p['name'],p['type']] for p in ds[0]['params']]==req['inputs'] and [s['node']['op'] for s in ds[0]['steps']]==req['operations'] and ds[0]['result_type']=='Int64'
        observations=[]
        timings=[]
        for case in read('ACCEPTANCE.json')['cases']:
            obs,t=observe(artifact,case)
            actual=obs['observation']
            expected=case['expected']
            matched=actual['status']==expected['status']
            if matched and actual['status']=='success':
                matched=type(actual['value']) is int and actual['value']==expected['value'] and actual['output']['bytes_hex']==expected['output_hex'] and actual['consumed']==expected['consumed']
            elif matched and actual['status']=='reject':
                matched=all(actual['error'][k]==expected[k] for k in ('code','stage'))
            elif matched:
                matched=actual['diagnostic']['code']==expected['code']
            observations.append(dict(expected=case,evidence=obs,passed=matched,observation_identity=identity(obs)))
            timings.append(t)
        functional=structural and all(o['passed'] for o in observations)
        save('FUNCTIONAL.json',dict(artifact_sha256=sha(HERE/'LIVE/ARTIFACT.json'),artifact_content_identity=identity(artifact),structural_valid=structural,
            passed=functional,observations=observations,timings=timings,model_calls=0))
        # Saved-file reload for every replay pass; author session is already disconnected.
        passes=[]
        for pass_no in range(3):
            saved=read('LIVE/ARTIFACT.json')
            records=[]
            for original in observations:
                obs,t=observe(saved,original['expected'])
                records.append(dict(evidence=obs,times=t,identity=identity(obs),equal=obs==original['evidence']))
            passes.append(dict(pass_number=pass_no+1,records=records,all_equal=all(r['equal'] for r in records)))
        replay=all(p['all_equal'] for p in passes)
        save('REPLAY.json',dict(model_calls=0,provider_imports=False,artifact_reloaded=True,author_process_terminated=True,
            artifact_sha256=sha(HERE/'LIVE/ARTIFACT.json'),passes=passes,all_equal=replay,
            compared=['typed results','error behavior','provenance','logical work','observable entry ordering','package/expanded/observation identities']))
        metrics['functional_timings']=timings
        metrics['adapter_construction_times']=read('LIVE/STATE.json')['completed']['times']
    else:
        save('FUNCTIONAL.json',dict(status='NOT_REACHED',reason='No completed artifact',model_calls=0))
        save('REPLAY.json',dict(status='NOT_REACHED',reason='No completed artifact',model_calls=0))
    delivery=(HERE/'LIVE/DELIVERY.json').exists() and read('LIVE/DELIVERY.json')['matches_requested']
    exposure=next((r['response'].get('result',{}).get('tools') for r in rows if r['request'].get('method')=='tools/list'),None)
    protocol_valid=delivery and len(calls)<=12 and metrics['correction_turns']<=4 and exposure==definitions()
    classification='R6_28_SEMANTIC_CONSTRUCTION_SUPPORTED' if functional and replay else 'R6_28_CONSTRUCTION_PARTIAL' if calls else 'R6_28_MODEL_AUTHORING_GAP'
    if not protocol_valid:
        classification='R6_28_TOOL_INTEGRATION_GAP' if exposure!=definitions() else 'R6_28_PROTOCOL_HALT'
    if metrics['construction_failures'] and not complete and (len(calls)>=12 or metrics['correction_turns']>=4):
        classification='R6_28_MODEL_AUTHORING_GAP'
    save('MEASUREMENTS.json',metrics)
    save('RESULT.json',dict(timestamp=now(),classification=classification,model=MODEL,complete_artifact=complete,
        functional_acceptance=functional,AI_independent_replay=replay,protocol_valid=protocol_valid,
        byte_exact_prompt_delivery=delivery,tool_exposure_verified=exposure==definitions(),stopped=True))
    print(classification,'functional',functional,'replay',replay,'calls',len(calls))

def publish():
    verify_freeze()
    result=read('RESULT.json')
    sources=[p for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name not in ('PUBLICATION-IDENTITIES.json','VERIFICATION.json')]
    sources += [HERE.parent/'R6_28-REPORT.md']
    sources += [ROOT/'docs'/n for n in ('project-overview-r6.28.md','research-log-r6.28.md','decisions-r6.28.md')]
    files={}
    for p in sorted(sources):
        text=p.read_text(encoding='utf-8')
        if p.suffix=='.json':
            json.loads(text)
        if p.suffix=='.jsonl':
            for line in text.splitlines():
                if line.startswith('{'):
                    json.loads(line)
        if p.suffix in ('.md','.py'):
            assert all(line==line.rstrip() for line in text.splitlines()),p
        if p.suffix=='.md':
            for link in re.findall(r'\]\(([^)]+)\)',text):
                if not link.startswith(('http:','https:')):
                    assert (p.parent/link.split('#')[0]).resolve().exists(),link
        assert not re.search(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|\bsk-[A-Za-z0-9_-]{20,}',text),p
        files[p.relative_to(ROOT).as_posix()]=dict(sha256=sha(p),bytes=p.stat().st_size)
    diff=subprocess.run(['git','diff','--check'],cwd=ROOT,capture_output=True,text=True)
    assert diff.returncode==0,diff.stderr
    save('PUBLICATION-IDENTITIES.json',dict(timestamp=now(),files=files))
    save('VERIFICATION.json',dict(timestamp=now(),passed=True,classification=result['classification'],
        protected_count=verify_protected(),protected_mismatches=[],kernel=26,freeze_verified=True,
        R6_27_publication_verified=True,tool_exposure_verified=result['tool_exposure_verified'],
        publication_manifest_sha256=sha(HERE/'PUBLICATION-IDENTITIES.json'),publication_files=len(files),
        JSON_links_whitespace_checked=True,credentials_published=False,git_diff_check=dict(returncode=diff.returncode,stdout=diff.stdout,stderr=diff.stderr),
        inference_calls_during_publication=0,P6_A04_acceptance=False,P6_A05_access=False,stopped=True))
    assert all(sha(ROOT/p)==v['sha256'] for p,v in read('PUBLICATION-IDENTITIES.json')['files'].items())
    print('Publication integrity verified;',len(files),'files;',verify_protected(),'protected identities')

if __name__=='__main__':
    {'prepare':prepare,'bridge':bridge,'author':author,'evaluate':evaluate,'publish':publish}[sys.argv[1]]()
