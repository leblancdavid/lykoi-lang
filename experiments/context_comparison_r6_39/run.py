"""Frozen prospective orchestration over unchanged historical machinery."""
import json
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from common import ROOT,HERE,OUT,TEMP,module,save,load,sha,Registry,digest
from snapshot import generate,verify
from tasks import TASKS,requirement,modification,expectations,artifacts,acceptance
from tools import TOOLS

support=module('r639_support',ROOT/'experiments/ai_lifecycle_r6_36/preflight.py')
AGENT='Use actual Lykoi MCP calls for the supplied stage. No files or other tools. Never invent operations. Admission only mechanically seals identities. Stop at the requested stage. Preserve failed calls.'
GUIDE=(ROOT/'benchmark/results/phase6/r6_37/GUIDE.txt').read_text()

def config(run_id):
    permission={'*':'deny','r638_lykoi_*':'allow'}
    return {'$schema':'https://opencode.ai/config.json','share':'disabled','autoupdate':False,'snapshot':False,
        'permission':permission,'agent':{'r639-author':dict(mode='primary',model='openai/gpt-6.1-sol',variant='high',
        description='Bounded three-condition participant',prompt=AGENT,permission=permission)},'default_agent':'r639-author',
        'mcp':{'r638':dict(type='local',command=[sys.executable,'-B',str(HERE/'tools.py')],
            environment={'R638_RUN':run_id},enabled=True)}}

def ask(run_id,stage,prompt,session=None,timeout=600):
    folder=OUT/run_id/stage; folder.mkdir(parents=True,exist_ok=False)
    cfg=config(run_id); save(folder/'CONFIG.json',cfg)
    save(folder/'VISIBLE-DISPATCH.json',dict(prompt=prompt,prompt_identity=digest(prompt),
        schemas=TOOLS,schema_identity=digest(TOOLS),instructions=AGENT,instructions_identity=digest(AGENT),
        exact_provider_serialization=False,tokenizer=None))
    command=[support.EXE,'run','--format','json','--model','openai/gpt-6.1-sol','--variant','high',
        '--agent','r639-author','--title','R6.39 '+run_id]
    if session: command+=['--session',session]
    start=time.perf_counter(); timeout_hit=False
    try:
        child=subprocess.run(command,input=prompt.encode(),cwd=TEMP,env=support.environment(cfg),
            capture_output=True,timeout=timeout)
        stdout,stderr,code=child.stdout,child.stderr,child.returncode
    except subprocess.TimeoutExpired as exc:
        stdout,stderr,code=exc.stdout or b'',exc.stderr or b'',None; timeout_hit=True
    events=[support.sanitize(json.loads(line)) for line in stdout.decode('utf-8',errors='replace').splitlines() if line.startswith('{')]
    with (folder/'EVENTS.jsonl').open('x',encoding='utf-8',newline='\n') as stream:
        stream.write(''.join(json.dumps(e)+'\n' for e in events))
    sessions=sorted({e['sessionID'] for e in events if e.get('sessionID')}); session=sessions[-1] if sessions else session
    rec=dict(stage=stage,session=session,returncode=code,timeout=timeout_hit,wall_seconds=time.perf_counter()-start,
        step_finishes=[e['part'] for e in events if e.get('type')=='step_finish'],
        tool_calls=sum(e.get('type')=='tool_use' for e in events),errors=[e for e in events if e.get('type')=='error'],
        stderr_bytes=len(stderr),stderr_published=False)
    save(folder/'MEASUREMENT.json',rec)
    if session:
        child=subprocess.run([support.EXE,'export',session],cwd=TEMP,env=support.environment(cfg),capture_output=True,timeout=60)
        assert child.returncode==0,'EXPORT_HALT'
        save(folder/'EXPORT.json',support.sanitize(json.loads(child.stdout)))
    print(json.dumps(dict(run=run_id,stage=stage,seconds=rec['wall_seconds'],completions=len(rec['step_finishes']),
        tools=rec['tool_calls'],errors=rec['errors'])),flush=True)
    return rec

def prepare():
    assert OUT.parent.is_dir() and TEMP.parent.is_dir()
    OUT.mkdir(exist_ok=False); TEMP.mkdir(exist_ok=False)
    prior=ROOT/'benchmark/results/phase6/r6_38'; receipt=load(prior/'VERIFICATION.json')
    assert receipt['passed'] and receipt['kernel']==26
    assert sha(prior/'PUBLICATION-IDENTITIES.json')==receipt['manifest_sha256']
    pins=dict(load(prior/'BASELINE.json')['protected_files'])
    publication=load(prior/'PUBLICATION-IDENTITIES.json')['files']
    for name,meta in publication.items():
        assert sha(ROOT/name)==meta['sha256'] and (ROOT/name).stat().st_size==meta['bytes'],name
        pins[name]=meta['sha256']
    for name in ('VERIFICATION.json','PUBLICATION-IDENTITIES.json'):
        pins[(prior/name).relative_to(ROOT).as_posix()]=sha(prior/name)
    for name,pin in pins.items():
        assert 'p6_a05' not in name.lower().replace('-','_')
        assert sha(ROOT/name)==pin,name
    save(OUT/'BASELINE.json',dict(kernel=26,protected_files=pins,protected_count=len(pins),
        R6_38_publication_files=len(publication),R6_38_publication_verified=True,
        initial_worktree_clean_before_R6_39=True,historical_kernel_accounting_not_new_recount=True,
        head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()))
    for t in TASKS:
        save(OUT/(t['id']+'-TASK.json'),dict(task=t,requirement=requirement(t),modification=modification(t)))
        save(OUT/(t['id']+'-EXPECTATIONS.json'),expectations(t))
    save(OUT/'MODEL.json',dict(model='openai/gpt-6.1-sol',requested_variant='high',config=config('qualification'),
        effective_authentication=None,effective_reasoning=None,tokenizer=None,billing=None,
        inherited_route='R6.36 qualified child environment; OPENCODE_PURE=1, default plugins eligible',
        budgets=dict(completions_per_stage=20,MCP_calls_per_stage=40,seconds_per_stage=600,corrections=2)))
    files=[p for p in HERE.iterdir() if p.is_file()]+[p for p in OUT.iterdir() if p.is_file()]
    save(OUT/'TASK-FREEZE.json',dict(utc=datetime.now(timezone.utc).isoformat(),participant_calls=0,
        inputs={p.relative_to(ROOT).as_posix():sha(p) for p in files},order=[(t['id'],t['order']) for t in TASKS]))
    print('Verified protected baseline and froze tasks:',len(pins),flush=True)

def preflight():
    version=subprocess.run([support.EXE,'--version'],capture_output=True,cwd=TEMP,
        env=support.environment(config('qualification')),timeout=30)
    rec=ask('qualification','neutral','Reply exactly NEUTRAL_OK. Do not use tools.',timeout=90)
    events=[json.loads(line) for line in (OUT/'qualification/neutral/EVENTS.jsonl').read_text().splitlines()]
    text=''.join(e['part']['text'] for e in events if e.get('type')=='text').strip()
    rec.update(opencode_version=version.stdout.decode().strip(),passed=rec['returncode']==0 and not rec['errors']
        and not rec['timeout'] and rec['tool_calls']==0 and text=='NEUTRAL_OK')
    save(OUT/'PREFLIGHT.json',rec); assert rec['passed'],'PREFLIGHT_HALT'

def stage(t,run_id,prompt,final):
    started=time.perf_counter(); calls=[]; session=None; failure=None
    folder=OUT/run_id; folder.mkdir(exist_ok=True)
    frozen=load(OUT/(t['id']+'-EXPECTATIONS.json'))
    for attempt in range(3):
        remaining=600-(time.perf_counter()-started)
        if remaining<=0: failure='WALL_BUDGET'; break
        rec=ask(run_id,'attempt'+str(attempt),prompt,session,remaining); calls.append(rec); session=rec['session']
        if rec['returncode']!=0 or rec['timeout'] or rec['errors']: failure='PROVIDER_HALT'; break
        if sum(len(x['step_finishes']) for x in calls)>20 or sum(x['tool_calls'] for x in calls)>40:
            failure='CALL_BUDGET'; break
        try: result=acceptance(Registry(folder/'registry'),t,frozen,final)
        except (AssertionError,StopIteration,ValueError) as exc:
            result=dict(all_passed=False,passed=0,total=0,artifact_failure=str(exc),rows=[])
        save(folder/('ACCEPTANCE-'+str(attempt)+'.json'),result)
        if result['all_passed']: break
        if attempt==2: failure='REPAIR_BUDGET'; break
        prompt='Frozen acceptance failed. Repair with existing tools only. Failed observations: '+json.dumps(
            [r for r in result['rows'] if not r['passed']][:8])+str(result.get('artifact_failure',''))
    closed=dict(calls=calls,failure=failure,wall_seconds=time.perf_counter()-started,coordinator_semantic_repairs=0)
    save(folder/'CLOSED.json',closed)
    if failure in ('PROVIDER_HALT','CALL_BUDGET','WALL_BUDGET'): raise RuntimeError(failure)
    return closed

def contexts(t):
    base=OUT/(t['id']+'-BASE'); closed=load(base/'CLOSED.json'); assert not closed['failure']
    registry=Registry(base/'registry'); ds=artifacts(registry,t,False)
    before=time.perf_counter()
    # Deduplicate cumulative exports by message identity while preserving chronological order.
    messages={}
    for call in closed['calls']:
        for m in load(base/call['stage']/'EXPORT.json')['messages']: messages[m['info']['id']]=m
    history=dict(version='r639-full-relevant-history-1',messages=sorted(messages.values(),key=lambda m:m['info']['time']['created']))
    history_seconds=time.perf_counter()-before
    assert modification(t) not in json.dumps(history),'future objective exposed in base'
    bindings={name:ds[key]['identity'] for name,key in [('CallerA','a'),('CallerB','b')]}
    before=time.perf_counter()
    summary=dict(version='r639-mechanical-summary-1',behavior=requirement(t),objective=modification(t),
        components=[dict(name=d['name'],identity=d['identity'],parameters=d['params'],result=d['result_type'],
            dependencies=d['dependencies']) for d in ds.values()],caller_bindings=bindings,
        retrieval='lykoi_retrieve(identity) for exact definition/body/impact; lykoi_context for all context documents',
        known_constraints='Checked Int64, UInt8 input, UInt16BE output, input_end before computation; immutable predecessors',
        successors=registry.read()['state']['successors'],migrations=registry.read()['state']['migrations'])
    summary_seconds=time.perf_counter()-before
    before=time.perf_counter(); snap=generate(registry,digest(requirement(t)),modification(t),bindings,requirement(t))
    verify(snap,registry,digest(requirement(t)),modification(t),bindings,requirement(t)); snapshot_seconds=time.perf_counter()-before
    for k,d in ds.items():
        assert snap['definitions'][d['identity']]==d
        assert any(x['identity']==d['identity'] and x['dependencies']==d['dependencies'] for x in summary['components'])
        assert d['identity'] in json.dumps(history),'history missing admitted definition identity'
    for track in t['order']:
        folder=OUT/(t['id']+'-'+track); folder.mkdir(exist_ok=False)
        shutil.copytree(base/'registry',folder/'registry')
        assert Registry(folder/'registry').read()==registry.read()
        for name,value in [('HISTORY.json',history),('SUMMARY.json',summary),('SNAPSHOT.json',snap)]: save(folder/name,value)
    save(base/'CONTEXT-AUDIT.json',dict(before_modification_calls=True,exact_same_registry=True,
        history_seconds=history_seconds,summary_seconds=summary_seconds,snapshot_generation_verification_seconds=snapshot_seconds,
        bytes={name:len(json.dumps(v,sort_keys=True).encode()) for name,v in [('A',history),('B',summary),('C',snap)]},
        immediately_supplied={'A':'full original user/assistant/tool export including exact definitions and feedback',
            'B':'behavior, constraints, objective, signatures, dependency identities and caller index; no implementation bodies',
            'C':'full typed closure, immutable identities, bindings, constraints, lifecycle and validation metadata'},
        retrieved='All conditions can retrieve all three documents, exact closure/impact, validation and lifecycle metadata',
        unavailable_to_all=['frozen acceptance cases','other candidates','hidden provider context'],
        missing_task_relevant_information=[],equivalence='Task-relevant facts accessible, not identical immediate content or cognition',
        tooling_asymmetry='None: same registry checks and tools available to B; summary is not credited with uniquely symbolic checks',
        future_requirements_in_base=False,hidden_context_exclusion_attested=False))
    paths=[p for track in t['order'] for p in (OUT/(t['id']+'-'+track)).glob('*.json')]+[base/'CONTEXT-AUDIT.json']
    save(base/'CONTEXT-FREEZE.json',dict(utc=datetime.now(timezone.utc).isoformat(),modification_calls=0,
        inputs={p.relative_to(ROOT).as_posix():sha(p) for p in paths}))

def run_task(task_id):
    for name,pin in load(OUT/'TASK-FREEZE.json')['inputs'].items(): assert sha(ROOT/name)==pin,name
    assert load(OUT/'PREFLIGHT.json')['passed']
    t=next(t for t in TASKS if t['id']==task_id)
    closed=stage(t,task_id+'-BASE',GUIDE+'\n'+requirement(t),False)
    if closed['failure']: raise RuntimeError('BASE_ACCEPTANCE_HALT')
    contexts(t)
    for track in t['order']:
        for name,pin in load(OUT/(task_id+'-BASE')/'CONTEXT-FREEZE.json')['inputs'].items(): assert sha(ROOT/name)==pin
        document={'A':'HISTORY.json','B':'SUMMARY.json','C':'SNAPSHOT.json'}[track]
        context=load(OUT/(task_id+'-'+track)/document)
        prompt=GUIDE+'\nExisting software context:\n'+json.dumps(context,sort_keys=True)+'\n'+modification(t)
        prompt+='\nOriginal acceptance passed. Same bounded retrieval of exact registry facts and all context documents is available.'
        stage(t,task_id+'-'+track,prompt,True)

def replay():
    results={}
    for t in TASKS:
        for track in ('A','B','C'):
            folder=OUT/(t['id']+'-'+track); original=load(sorted(folder.glob('ACCEPTANCE-*.json'))[-1])
            if not original['all_passed']: continue
            runs=[]
            for i in range(3):
                result=acceptance(Registry(folder/'registry'),t,load(OUT/(t['id']+'-EXPECTATIONS.json')),True)
                equal=result['rows']==original['rows'] and result['identities']==original['identities'] and {
                    k:v['expansion'] for k,v in result['expansions'].items()}=={k:v['expansion'] for k,v in original['expansions'].items()}
                assert result['all_passed'] and equal
                save(folder/f'REPLAY-{i+1}.json',result)
                runs.append(dict(passed=result['passed'],total=result['total'],full_equal=equal,rows_digest=digest(result['rows']),wall_seconds=result['wall_seconds']))
            results[t['id']+'-'+track]=runs
    save(OUT/'REPLAY.json',dict(model_calls=0,runs=results)); print(json.dumps(results))

if __name__=='__main__':
    if sys.argv[1]=='prepare': prepare()
    elif sys.argv[1]=='preflight': preflight()
    elif sys.argv[1]=='replay': replay()
    else: run_task(sys.argv[1])
