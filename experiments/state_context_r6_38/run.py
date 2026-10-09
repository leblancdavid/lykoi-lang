"""Frozen matched authoring orchestration; SDK observations, not HTTP interception."""
import json
import subprocess
import sys
import time
from common import ROOT, HERE, OUT, TEMP, module, save, load, sha, Registry, digest
from snapshot import generate, verify
from tasks import TASKS, requirement, modification, expectations, artifacts, acceptance
from tools import TOOLS

support=module('r638_support',ROOT/'experiments/ai_lifecycle_r6_36/preflight.py')
AGENT='Use actual Lykoi MCP calls for the supplied stage. No files or other tools. Never invent operations. Admission only mechanically seals identities. Stop at the requested stage. Preserve failed calls.'
GUIDE=(ROOT/'benchmark/results/phase6/r6_37/GUIDE.txt').read_text()


def config(run_id):
    permission={'*':'deny','r638_lykoi_*':'allow'}
    return {'$schema':'https://opencode.ai/config.json','share':'disabled','autoupdate':False,'snapshot':False,
        'permission':permission,'agent':{'r638-author':dict(mode='primary',model='openai/gpt-6.1-sol',variant='high',
        description='Bounded state context participant',prompt=AGENT,permission=permission)},'default_agent':'r638-author',
        'mcp':{'r638':dict(type='local',command=[sys.executable,'-B',str(HERE/'tools.py')],environment={'R638_RUN':run_id},enabled=True)}}


def ask(run_id,stage,prompt,session=None,timeout=600):
    folder=OUT/run_id/stage; folder.mkdir(parents=True,exist_ok=False)
    cfg=config(run_id); save(folder/'CONFIG.json',cfg); save(folder/'VISIBLE-DISPATCH.json',dict(prompt=prompt,
        prompt_identity=digest(prompt),schema_identity=digest(TOOLS),instructions_identity=digest(AGENT),
        exact_provider_serialization=False,local_serialization='canonical JSON; not upstream request',tokenizer=None))
    command=[support.EXE,'run','--format','json','--model','openai/gpt-6.1-sol','--variant','high','--agent','r638-author','--title','R6.38 '+run_id]
    if session: command+=['--session',session]
    start=time.perf_counter(); timeout_hit=False
    try:
        child=subprocess.run(command,input=prompt.encode(),cwd=TEMP,env=support.environment(cfg),capture_output=True,timeout=timeout)
        stdout,stderr,code=child.stdout,child.stderr,child.returncode
    except subprocess.TimeoutExpired as exc:
        stdout,stderr,code=exc.stdout or b'',exc.stderr or b'',None; timeout_hit=True
    events=[support.sanitize(json.loads(line)) for line in stdout.decode('utf-8',errors='replace').splitlines() if line.startswith('{')]
    with (folder/'EVENTS.jsonl').open('x',encoding='utf-8',newline='\n') as stream:
        stream.write(''.join(json.dumps(e)+'\n' for e in events))
    sessions=sorted({e['sessionID'] for e in events if e.get('sessionID')}); session=sessions[-1] if sessions else session
    record=dict(stage=stage,session=session,returncode=code,timeout=timeout_hit,wall_seconds=time.perf_counter()-start,
        step_finishes=[e['part'] for e in events if e.get('type')=='step_finish'],tool_calls=sum(e.get('type')=='tool_use' for e in events),
        errors=[e for e in events if e.get('type')=='error'],stderr_bytes=len(stderr),stderr_published=False)
    save(folder/'MEASUREMENT.json',record)
    if session:
        child=subprocess.run([support.EXE,'export',session],cwd=TEMP,env=support.environment(cfg),capture_output=True,timeout=60)
        if child.returncode==0: save(folder/'EXPORT.json',support.sanitize(json.loads(child.stdout)))
    print(json.dumps(dict(run=run_id,stage=stage,seconds=record['wall_seconds'],completions=len(record['step_finishes']),tools=record['tool_calls'],errors=record['errors'])),flush=True)
    return record


def prepare():
    assert OUT.parent.is_dir() and TEMP.parent.is_dir()
    OUT.mkdir(exist_ok=False); TEMP.mkdir(exist_ok=False)
    prior=ROOT/'benchmark/results/phase6/r6_37'
    receipt=load(prior/'VERIFICATION.json'); assert receipt['passed'] and receipt['kernel']==26
    assert sha(prior/'PUBLICATION-IDENTITIES.json')==receipt['manifest_sha256']
    pins=dict(load(prior/'BASELINE.json')['protected_files'])
    for name,meta in load(prior/'PUBLICATION-IDENTITIES.json')['files'].items():
        assert sha(ROOT/name)==meta['sha256'] and (ROOT/name).stat().st_size==meta['bytes']
        pins[name]=meta['sha256']
    for name in ('VERIFICATION.json','PUBLICATION-IDENTITIES.json'): pins[(prior/name).relative_to(ROOT).as_posix()]=sha(prior/name)
    for name,pin in pins.items():
        assert 'p6_a05' not in name.lower().replace('-','_')
        assert sha(ROOT/name)==pin,name
    save(OUT/'BASELINE.json',dict(kernel=26,protected_files=pins,protected_count=len(pins),R6_37_publication_verified=True,
        historical_kernel_accounting_not_new_recount=True,head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        initial_worktree_clean=True,implementation_identities={name:pin for name,pin in pins.items() if name.startswith(('src/','experiments/semantic_interpreter/','experiments/typed_composition_r6_18/','experiments/construction_','experiments/lifecycle_r6_32/'))}))
    tests=subprocess.run([sys.executable,'-B','-m','unittest','discover','-s',str(HERE),'-p','test_snapshot.py','-v'],cwd=ROOT,capture_output=True,text=True)
    save(OUT/'SNAPSHOT-TESTS.json',dict(returncode=tests.returncode,stdout=tests.stdout,stderr=tests.stderr))
    assert tests.returncode==0,tests.stderr
    for t in TASKS:
        save(OUT/(t['id']+'-TASK.json'),dict(task=t,requirement=requirement(t),modification=modification(t)))
        save(OUT/(t['id']+'-EXPECTATIONS.json'),expectations(t))
    save(OUT/'MODEL.json',dict(model='openai/gpt-6.1-sol',requested_variant='high',config=config('qualification'),
        built_in_OAuth_eligible=True,disable_default_plugins_absent=True,OPENCODE_PURE='1',
        effective_authentication=None,effective_reasoning=None,tokenizer=None,serialized_provider_boundary=None,
        budgets={'completions':30,'MCP_calls':50,'seconds_per_stage':600,'seconds_per_track':1200,'corrections_per_stage':2}))
    save(OUT/'INFORMATION-EQUIVALENCE.json',dict(same_original_requirement=True,same_guide_schemas_model=True,
        B_contains_exact_current_closure_types_bindings_constraints=True,all_omitted_registry_history_exactly_retrievable=True,
        asymmetry='A retains prior generated reasoning/text/feedback; B omits it. Registry facts available to both; cognitive history not asserted equivalent.',
        hidden_context_exclusion_attested=False,no_cross_track_artifact_access=True,summary_control='Offline deterministic extraction only; no scored third track'))
    files=[p for p in HERE.iterdir() if p.is_file()]+[p for p in OUT.iterdir() if p.is_file()]
    save(OUT/'TASK-FREEZE.json',dict(participant_calls=0,inputs={p.relative_to(ROOT).as_posix():sha(p) for p in files},order=[(t['id'],t['order']) for t in TASKS]))
    print('Baseline, snapshot tests, 3 fresh tasks and oracle frozen',len(pins),flush=True)


def run_task(task_id):
    for name,pin in load(OUT/'TASK-FREEZE.json')['inputs'].items(): assert sha(ROOT/name)==pin,name
    assert load(OUT/'PREFLIGHT.json')['returncode']==0 and not load(OUT/'PREFLIGHT.json')['errors']
    t=next(t for t in TASKS if t['id']==task_id)
    frozen=load(OUT/(task_id+'-EXPECTATIONS.json'))
    for track in t['order']:
        run_id=task_id+'-'+track; folder=OUT/run_id; folder.mkdir(exist_ok=False)
        started=time.perf_counter(); calls=[]; session=None; failure=None; snapshot_seconds=0
        try:
            for stage in ('base','modification'):
                if stage=='base': prompt=GUIDE+'\n'+requirement(t)
                else:
                    if track=='B':
                        registry=Registry(folder/'registry'); ds=artifacts(registry,t,False)
                        bindings={name:ds[key]['identity'] for name,key in [('CallerA','a'),('CallerB','b')]}
                        before=time.perf_counter()
                        snap=generate(registry,digest(requirement(t)),modification(t),bindings,requirement(t))
                        verify(snap,registry,digest(requirement(t)),modification(t),bindings,requirement(t))
                        snapshot_seconds=time.perf_counter()-before; save(folder/'SNAPSHOT.json',snap)
                        summary=dict(requirement=requirement(t),modification=modification(t),definitions=snap['definitions'],caller_bindings=bindings)
                        save(folder/'ORDINARY-DETERMINISTIC-SUMMARY.json',summary)
                        save(folder/'CONTEXT-SIZES.json',dict(snapshot_bytes=len(json.dumps(snap)),summary_bytes=len(json.dumps(summary)),
                            summary_is_generic_latest_state_extraction=True,authoring_efficacy_not_tested=True))
                        prompt=GUIDE+'\nCurrent requirement:\n'+requirement(t)+'\nDeterministic state snapshot:\n'+json.dumps(snap,sort_keys=True)+'\n'+modification(t)
                        session=None
                    else: prompt=modification(t)
                    prompt+='\nBase frozen acceptance passed. Use bounded lykoi_detail retrieval for omitted registry details if needed.'
                for attempt in range(3):
                    remaining=1200-(time.perf_counter()-started); assert remaining>0,'WALL_BUDGET'
                    rec=ask(run_id,stage+str(attempt),prompt,session,min(600,remaining)); calls.append(rec); session=rec['session']
                    assert rec['returncode']==0 and not rec['timeout'] and not rec['errors'],'PROVIDER_HALT'
                    assert sum(len(x['step_finishes']) for x in calls)<=30,'COMPLETION_BUDGET'
                    assert sum(x['tool_calls'] for x in calls)<=50,'MCP_BUDGET'
                    try:
                        result=acceptance(Registry(folder/'registry'),t,frozen,stage=='modification')
                    except (AssertionError, StopIteration, ValueError) as exc:
                        result=dict(all_passed=False,passed=0,total=0,artifact_failure=str(exc),rows=[])
                    save(folder/(stage+str(attempt)+'-ACCEPTANCE.json'),result)
                    if result['all_passed']: break
                    assert attempt<2,'REPAIR_BUDGET'
                    prompt='Frozen acceptance failed. Repair with existing tools only. Failed observations: '+json.dumps([r for r in result['rows'] if not r['passed']][:8])+str(result.get('artifact_failure',''))
        except Exception as exc:
            failure=type(exc).__name__+': '+str(exc)
        save(folder/'CLOSED.json',dict(task=task_id,track=track,calls=calls,failure=failure,wall_seconds=time.perf_counter()-started,
            snapshot_seconds=snapshot_seconds,coordinator_semantic_repairs=0))
        print(json.dumps(dict(run=run_id,failure=failure)),flush=True)
        if failure: return


def preflight():
    rec=ask('qualification','neutral','Reply exactly NEUTRAL_OK. Do not use tools.',timeout=90)
    events=[json.loads(line) for line in (OUT/'qualification/neutral/EVENTS.jsonl').read_text().splitlines()]
    texts=[e['part']['text'] for e in events if e.get('type')=='text']
    rec['passed']=rec['returncode']==0 and not rec['errors'] and not rec['timeout'] and rec['tool_calls']==0 and ''.join(texts).strip()=='NEUTRAL_OK'
    save(OUT/'PREFLIGHT.json',rec)
    assert rec['passed']


def replay():
    results={}
    for t in TASKS:
        for track in ('A','B'):
            folder=OUT/(t['id']+'-'+track)
            if not (folder/'CLOSED.json').exists() or load(folder/'CLOSED.json')['failure']: continue
            files=sorted(folder.glob('modification*-ACCEPTANCE.json')); original=load(files[-1]); runs=[]
            for index in range(3):
                result=acceptance(Registry(folder/'registry'),t,load(OUT/(t['id']+'-EXPECTATIONS.json')),True)
                equal=(result['rows']==original['rows'] and result['identities']==original['identities'] and
                    {k:v['expansion'] for k,v in result['expansions'].items()}=={k:v['expansion'] for k,v in original['expansions'].items()})
                assert result['all_passed'] and equal
                save(folder/f'REPLAY-{index+1}.json',result); runs.append(dict(passed=result['passed'],total=result['total'],full_equal=equal,rows_digest=digest(result['rows']),wall_seconds=result['wall_seconds']))
            results[t['id']+'-'+track]=runs
    save(OUT/'REPLAY.json',dict(model_calls=0,runs=results))
    print(json.dumps(results))


if __name__=='__main__':
    if sys.argv[1]=='prepare': prepare()
    elif sys.argv[1]=='preflight': preflight()
    elif sys.argv[1]=='replay': replay()
    else: run_task(sys.argv[1])
