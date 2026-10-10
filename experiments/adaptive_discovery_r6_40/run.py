"""Frozen bounded participant driver with retained exports and usage."""
import json
import subprocess
import sys
import time
import threading
import queue
from datetime import datetime, timezone
from common import ROOT,HERE,OUT,TEMP,module,save,load,sha,Registry,c,digest
from development import DEVELOPMENT
from tasks import TASKS,expectations
from tools import TOOLS

support=module('r640_route',ROOT/'experiments/ai_lifecycle_r6_36/preflight.py')
GUIDE=(ROOT/'benchmark/results/phase6/r6_37/GUIDE.txt').read_text()
AGENT='Use only supplied Lykoi MCP tools and requirements. No file or other tools. Never invent semantics. No other candidate access. Stop after the requested stage. Keep failed calls.'

def config(run_id):
    permission={'*':'deny','r640_lykoi_*':'allow'}
    return {'$schema':'https://opencode.ai/config.json','share':'disabled','autoupdate':False,'snapshot':False,
        'permission':permission,'agent':{'r640-author':dict(mode='primary',model='openai/gpt-6.1-sol',variant='high',
        steps=24,description='Bounded symbolic discovery participant',prompt=AGENT,permission=permission)},
        'default_agent':'r640-author','mcp':{'r640':dict(type='local',command=[sys.executable,'-B',str(HERE/'tools.py')],
            environment={'R640_RUN':run_id},enabled=True)}}

def usage(parts):
    totals=dict(input=0,cached_input=0,cache_write=0,output=0,reasoning=0)
    for p in parts:
        t=p.get('tokens',{})
        totals['input']+=t.get('input',0); totals['output']+=t.get('output',0)
        totals['reasoning']+=t.get('reasoning',0)
        totals['cached_input']+=t.get('cache',{}).get('read',0); totals['cache_write']+=t.get('cache',{}).get('write',0)
    totals['processed_input']=totals['input']+totals['cached_input']+totals['cache_write']
    return totals

def ask(run_id,prompt,timeout=360):
    folder=OUT/run_id; folder.mkdir(exist_ok=True)
    cfg=config(run_id); save(folder/'CONFIG.json',cfg)
    save(folder/'VISIBLE-DISPATCH.json',dict(prompt=prompt,schemas=TOOLS,instructions=AGENT,
        identity=digest([prompt,TOOLS,AGENT]),exact_provider_serialization=False))
    cmd=[support.EXE,'run','--format','json','--model','openai/gpt-6.1-sol','--variant','high',
        '--agent','r640-author','--title','R6.40 '+run_id]
    start=time.perf_counter(); timeout_hit=False; budget_stop=False
    child=subprocess.Popen(cmd,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
        cwd=TEMP,env=support.environment(cfg))
    lines=queue.Queue(); stderr_bytes=[0]
    def reader():
        for line in child.stdout: lines.put(line)
    def errors():
        for line in child.stderr: stderr_bytes[0]+=len(line)
    threads=[threading.Thread(target=reader),threading.Thread(target=errors)]
    for thread in threads: thread.start()
    child.stdin.write(prompt.encode()); child.stdin.close()
    events=[]
    while child.poll() is None or not lines.empty():
        try:
            line=lines.get(timeout=0.1)
            if line.startswith(b'{'): events.append(support.sanitize(json.loads(line)))
        except queue.Empty: pass
        if child.poll() is None:
            parts=[e['part'] for e in events if e.get('type')=='step_finish']
            tokens=usage(parts)
            timeout_hit=time.perf_counter()-start>timeout
            budget_stop=len(parts)>24 or tokens['processed_input']+tokens['output']>48000
            calls=sum(e.get('type')=='tool_use' for e in events)
            budget_stop=budget_stop or calls>36
            if timeout_hit or budget_stop:
                subprocess.run(['taskkill','/PID',str(child.pid),'/T','/F'],capture_output=True,timeout=20)
                if child.poll() is None: child.kill()
    for thread in threads: thread.join(timeout=5)
    code=child.wait()
    while not lines.empty():
        line=lines.get()
        if line.startswith(b'{'): events.append(support.sanitize(json.loads(line)))
    with (folder/'EVENTS.jsonl').open('x',encoding='utf-8',newline='\n') as stream:
        stream.write(''.join(json.dumps(e)+'\n' for e in events))
    sessions=sorted({e['sessionID'] for e in events if e.get('sessionID')})
    finishes=[e['part'] for e in events if e.get('type')=='step_finish']; tokens=usage(finishes)
    rec=dict(session=sessions[-1] if sessions else None,returncode=code,timeout=timeout_hit,
        wall_seconds=time.perf_counter()-start,step_finishes=finishes,tokens=tokens,
        completions=len(finishes),tool_calls=sum(e.get('type')=='tool_use' for e in events),
        errors=[e for e in events if e.get('type')=='error'],stderr_bytes=stderr_bytes[0],stderr_published=False,
        token_cap_exceeded=tokens['processed_input']+tokens['output']>48000,budget_stop=budget_stop)
    save(folder/'MEASUREMENT.json',rec)
    if rec['session']:
        export=subprocess.run([support.EXE,'export',rec['session']],cwd=TEMP,env=support.environment(cfg),capture_output=True,timeout=60)
        if export.returncode==0: save(folder/'EXPORT.json',support.sanitize(json.loads(export.stdout)))
        else: save(folder/'EXPORT-FAILURE.json',dict(returncode=export.returncode))
    print(json.dumps(dict(run=run_id,seconds=rec['wall_seconds'],completions=rec['completions'],tokens=tokens,
        calls=rec['tool_calls'],errors=rec['errors'],timeout=timeout_hit)),flush=True)
    return rec

def freeze():
    for name,pin in load(OUT/'DEVELOPMENT-FREEZE.json')['inputs'].items(): assert sha(ROOT/name)==pin,name
    save(OUT/'EVALUATION-TASKS.json',TASKS)
    for t in TASKS: save(OUT/(t['id']+'-EXPECTATIONS.json'),expectations(t))
    save(OUT/'MODEL.json',dict(model='openai/gpt-6.1-sol',requested_variant='high',config=config('qualification'),
        built_in_plugins_eligible=True,credential_store_read=False,effective_authentication=None,effective_reasoning=None,
        billing=None,coordinator_model_tokens=None,child_route='R6.36 environment, default plugins eligible',
        exposure_risks=['Coordinator authored tasks/oracles/proxy and knows both partitions; participant hidden-context exclusion unattested',
            'Narrow capability-tailored synthetic tasks; new exact contracts, related historical arithmetic skeletons'],
        bounds=dict(seconds=360,completions=24,MCP=36,processed_input_plus_output=48000,proposals=3,submissions=3,
            execute_calls=12,expanded_nodes=64,VM_work=100000)))
    paths=list(HERE.glob('*.py'))+[HERE/'PROTOCOL.md']+list(OUT.glob('*.json'))
    save(OUT/'TASK-FREEZE.json',dict(utc=datetime.now(timezone.utc).isoformat(),participant_calls=0,
        inputs={p.relative_to(ROOT).as_posix():sha(p) for p in paths},evaluation_revealed_to_discovery=False,
        human_macro_control=False,owner_authorized_AI_proxy=True))
    print('R6.40 task/design freeze installed before participant calls.')

def preflight():
    rec=ask('qualification','Reply exactly NEUTRAL_OK. Do not invoke tools.',90)
    ev=[json.loads(x) for x in (OUT/'qualification/EVENTS.jsonl').read_text().splitlines()]
    text=''.join(e['part']['text'] for e in ev if e.get('type')=='text').strip()
    rec['passed']=rec['returncode']==0 and not rec['timeout'] and not rec['errors'] and not rec['tool_calls'] and text=='NEUTRAL_OK'
    rec['opencode_version']=subprocess.check_output([support.EXE,'--version'],cwd=TEMP,env=support.environment(config('qualification')),text=True).strip()
    save(OUT/'PREFLIGHT.json',rec); assert rec['passed'],'PREFLIGHT_HALT'

def verify_freeze():
    for name,pin in load(OUT/'TASK-FREEZE.json')['inputs'].items(): assert sha(ROOT/name)==pin,name

def discovery(task_id):
    verify_freeze(); assert load(OUT/'PREFLIGHT.json')['passed']
    t=next(t for t in DEVELOPMENT if t['id']==task_id)
    entries=[]
    for previous in DEVELOPMENT:
        if previous['id']==task_id: break
        entries+= [load(p) for p in sorted((OUT/previous['id']).glob('ADMITTED-*.json'))]
    folder=OUT/task_id; folder.mkdir(exist_ok=False)
    reg=Registry(folder/'registry')
    if entries: reg.admit([e['definition'] for e in entries],reg.read()['token'])
    save(folder/'SESSION.json',dict(phase='discovery',condition='discovery',relation=t['relation'],library=entries))
    prompt=GUIDE+'\nDevelopment requirement: '+json.dumps(t)+'\nDiscover one useful reusable parameterized composition for this relation. '
    prompt+='Use lykoi_propose with exact signature parameter names/order from this task, Int64 params and result. '
    prompt+='Provide precise semantics and a non-applicability example. At most three proposals; prior library available through lykoi_library. '
    prompt+='Do not submit closed tasks or add new primitives. Behavioral checks are finite, not a proof. Stop after admitted proposal or exhausted attempts.'
    rec=ask(task_id,prompt)
    save(folder/'CLOSED.json',dict(provider_halt=rec['returncode']!=0 or rec['timeout'] or bool(rec['errors']),
        budget_exceeded=rec['token_cap_exceeded'],coordinator_semantic_repairs=0))

if __name__=='__main__':
    if sys.argv[1]=='freeze': freeze()
    elif sys.argv[1]=='preflight': preflight()
    else: discovery(sys.argv[1])
