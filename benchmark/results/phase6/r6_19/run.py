"""R6.19 evidence collector; participant inference is pinned loopback Ollama only."""
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT / 'experiments/typed_composition_r6_18'))
import composition as c

MODEL = 'qwen3:8b'
DIGEST = '500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41'
BASE = 'http://127.0.0.1:11435'
OPTIONS = dict(temperature=0, seed=619, num_ctx=8192, num_predict=4096,
               top_k=20, top_p=0.95, repeat_penalty=1)
HTTP = urllib.request.build_opener(urllib.request.ProxyHandler({}))

def now():
    return datetime.now(timezone.utc).isoformat()

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save(name, data):
    path = HERE / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=True,
                    default=lambda x: {'bytes_hex': x.hex()} if isinstance(x, bytes) else str(x)) + '\n', encoding='utf-8')

def api(path, data=None):
    assert path in ('/api/version', '/api/tags', '/api/show', '/api/chat', '/api/ps')
    req = urllib.request.Request(BASE + path, data=None if data is None else json.dumps(data).encode(),
                                 headers={'Content-Type': 'application/json'})
    with HTTP.open(req, timeout=300) as response:
        return json.load(response)

def ps(command):
    p = subprocess.run(['pwsh', '-NoProfile', '-Command', command], capture_output=True, text=True)
    return {'command': command, 'returncode': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr}

def server():
    env = os.environ.copy()
    env.update(OLLAMA_HOST='127.0.0.1:11435', OLLAMA_NO_CLOUD='1',
               OLLAMA_MODELS=r'D:\Software\.ollama\models',
               HTTP_PROXY='http://127.0.0.1:9', HTTPS_PROXY='http://127.0.0.1:9',
               NO_PROXY='127.0.0.1,localhost', OLLAMA_MAX_LOADED_MODELS='1')
    log = open(HERE / 'SERVER.log', 'ab')
    p = subprocess.Popen(['ollama', 'serve'], env=env, stdout=log, stderr=log)
    for _ in range(60):
        try:
            api('/api/version')
            return p, log
        except OSError:
            time.sleep(.5)
    raise RuntimeError('dedicated offline server not ready')

def call(label, messages, fmt='json', tools=None):
    request = dict(model=MODEL, messages=messages, options=OPTIONS, think=False,
                   stream=False, keep_alive='10m')
    if fmt is not None:
        request['format'] = fmt
    if tools:
        request['tools'] = tools
    t = time.perf_counter()
    response = api('/api/chat', request)
    record = dict(label=label, timestamp=now(), request=request, response=response,
                  wall_seconds=time.perf_counter()-t, loaded=api('/api/ps'))
    save('calls/' + label + '.json', record)
    return record

def preservation():
    baseline = json.loads((ROOT/'experiments/typed_composition_r6_18/BASELINE.json').read_text())
    pins = dict(baseline['protected_files'])
    publication = json.loads((ROOT/'experiments/typed_composition_r6_18/PUBLICATION-IDENTITIES.json').read_text())
    for path, item in publication['files'].items():
        if path.startswith('experiments/') or path == 'benchmark/results/phase6/R6_18-REPORT.md':
            pins[path] = item['sha256']
    bad = [path for path, digest in pins.items() if sha(ROOT/path) != digest]
    assert not bad, bad
    ledger = json.loads((ROOT/'benchmark/results/phase5c/R5_114-KERNEL-ACCOUNTING.json').read_text())
    return {'timestamp': now(), 'protected_count': len(pins), 'protected_files': pins,
            'mismatches': bad, 'kernel_ledger': ledger, 'foundation': c.FOUNDATION,
            'wrapper': sha(ROOT/'experiments/typed_composition_r6_18/composition.py'),
            'schema': sha(ROOT/'experiments/typed_composition_r6_18/typed-composition-1.schema.json')}

def inventory():
    save('BASELINE.json', preservation())
    commands = [
        "Get-CimInstance Win32_Processor | Select-Object Name,Architecture,NumberOfCores,NumberOfLogicalProcessors,MaxClockSpeed | ConvertTo-Json",
        "Get-CimInstance Win32_OperatingSystem | Select-Object Caption,Version,BuildNumber,OSArchitecture,TotalVisibleMemorySize,FreePhysicalMemory | ConvertTo-Json",
        "Get-CimInstance Win32_PhysicalMemory | Select-Object Capacity,Speed,ConfiguredClockSpeed | ConvertTo-Json",
        "Get-CimInstance Win32_VideoController | Select-Object Name,AdapterRAM,DriverVersion,DriverDate,Status | ConvertTo-Json",
        "Get-CimInstance Win32_LogicalDisk -Filter 'DriveType=3' | Select-Object DeviceID,Size,FreeSpace | ConvertTo-Json",
        "nvidia-smi --query-gpu=name,memory.total,memory.used,driver_version,compute_cap --format=csv",
        'nvcc --version', 'ollama --version', 'python --version', 'python -m pip list --format=json',
        "@('ollama','llama-cli','llama-server','lms','lmstudio','vllm','nvcc','docker') | ForEach-Object { $c=Get-Command $_ -ErrorAction SilentlyContinue; [ordered]@{name=$_;paths=@($c.Source)} } | ConvertTo-Json",
    ]
    tags = api('/api/tags')
    assert next(m for m in tags['models'] if m['name']==MODEL)['digest']==DIGEST
    show = api('/api/show', {'model': MODEL})
    blob = Path(r'D:\Software\.ollama\models\blobs\sha256-a3de86cd1c132c822487ededd47a324c50491393e6565cd14bafa40d0b8e686f')
    assert sha(blob) == blob.name.removeprefix('sha256-')
    save('INVENTORY.json', dict(timestamp=now(), commands=[ps(x) for x in commands],
         tags=tags, selected_show=show, runtime=api('/api/version'), model_digest=DIGEST,
         weight_path=str(blob), weight_bytes=blob.stat().st_size, weight_sha256=sha(blob),
         config=OPTIONS, think=False, selection='existing 8B chat/tools model fitting GPU; no symbolic outcomes inspected',
         locality='dedicated loopback server; OLLAMA_NO_CLOUD=1; invalid loopback remote proxies; no pull/fallback'))

def calibrate():
    schema = {'type':'object','properties':{'label':{'type':'string'}, 'count':{'type':'integer'},
              'enabled':{'type':'boolean'}},'required':['label','count','enabled'],'additionalProperties':False}
    results=[]
    for i,(label,count,enabled) in enumerate([('amber',3,True),('violet',0,False),('teal',12,True)]):
        expected=dict(label=label,count=count,enabled=enabled)
        r=call('calibration_'+str(i+1), [{'role':'user','content':'Return exactly this data as JSON: '+json.dumps(expected)}],schema)
        got=json.loads(r['response']['message']['content'])
        results.append(dict(passed=got==expected, expected=expected, actual=got,
                            tokens_per_second=r['response']['eval_count']/(r['response']['eval_duration']/1e9)))
    tool={'type':'function','function':{'name':'echo','description':'Return the supplied text unchanged.',
          'parameters':{'type':'object','properties':{'text':{'type':'string'}},'required':['text']}}}
    r=call('calibration_tool', [{'role':'user','content':'Use the echo tool once with text local-check.'}],None,[tool])
    tools=r['response']['message'].get('tool_calls',[])
    passed=len(tools)==1 and tools[0]['function']['name']=='echo' and tools[0]['function']['arguments']=={'text':'local-check'}
    save('CALIBRATION.json',dict(timestamp=now(),structured=results,tool_selection_passed=passed,
          tool_execution='inert selection only; no executable host tools', config=OPTIONS,
          structured_passed=sum(x['passed'] for x in results),local_loaded=r['loaded']))
    assert all(x['passed'] for x in results), 'neutral structured calibration failed'

# Oracle uses requirement relations, never the candidate or wrapper to derive expectations.
def expected(task, data):
    if len(data)<2:
        return {'status':'reject','code':'TRUNCATED'}
    x,y=data[:2]
    value=x+y+task['bias']
    checks=[('EQUAL',x==y)] if task['equal'] else []
    checks += [('LOW',task['low']<=value),('HIGH',value<=task['high'])]
    if task['reverse']:
        checks=checks[::-1]
    for code,ok in checks:
        if not ok:
            return {'status':'reject','code':code}
    if len(data)>2:
        return {'status':'reject','code':'TRAILING'}
    return {'status':'ok','value':value,'output':value.to_bytes(2,'big').hex(),'consumed':2}

def prepare():
    tasks=[]
    for name,bias,low,high,equal,reverse in [
        ('D1',0,5,40,False,False),('D2',2,10,60,False,False),('D3',0,0,80,True,False),
        ('E1',3,12,55,False,False),('E2',1,0,70,True,False),
        ('E3',4,18,90,True,True),('E4',5,25,25,False,True)]:
        task=dict(id=name,bias=bias,low=low,high=high,equal=equal,reverse=reverse)
        task['requirement']=f'Read exactly two uint8 bytes x then y. Compute total=x+y+{bias}. '+(
            'Require x==y with code EQUAL. ' if equal else '')+f'Require {low}<=total with code LOW; require total<={high} with code HIGH. '+(
            'Run these predicates in reverse listed order (HIGH, LOW'+(', EQUAL' if equal else '')+'). ' if reverse else 'Run predicates in listed order. ')+(
            'Compute predicates as typed Bool immutable values before checking them. All checks use total as site. After checks enforce end of input. Return total and encode UInt16BE. Preserve first failing code. Use reusable parameterized operations when useful.')
        values=sorted(set([0,1,4,5,6,9,10,12,18,20,25,30,40,50,70,90,127,254,255]))
        data=[bytes([x,y]) for x in values for y in values]+[b'',b'\x01',b'\x14\x14\x00',b'\x00\x00\x00']
        task['cases']=[{'input':b.hex(),'expected':expected(task,b)} for b in data]
        tasks.append(task)
    save('TASKS.json',{'timestamp':now(),'tasks':tasks,'bias':'coordinator synthetic capability-tailored; unseen only to participant'})
    interface='''Return JSON {"definitions": [...], "program": {...}}. Each definition/program has EXACT fields name, revision:1, params:[{"name":...,"type":"Int64"|"Bool"|"Unit"}], dependencies:{symbol:"AUTO"}, steps:[{"id":...,"type":...,"deps":[exact referenced parameter/local names],"node":...}], order:[every step id in execution order], result:expression, result_type. Program params=[] and result_type="Int64". Identity fields are omitted; harness mechanically seals them and replaces AUTO dependency/call pins. No other semantic correction.
Expressions: {"ref":"local_or_param"}, {"const":integer|boolean|null}, {"add":[expr,expr]}, {"le":[expr,expr]}, {"eq":[expr,expr]}. Bool is not Int64. Nodes: {"op":"atom","codec":"uint8"}; {"op":"value","expr":expr}; {"op":"check","test":Bool_expr,"site":expr,"code":"ASCII_NAME"}; {"op":"end"}; {"op":"compose","symbol":"name","identity":"AUTO","args":{"param":{"ref":"local"}|{"const":literal}}}. Compose args cannot be computed expressions: materialize values first. Definition result_type may be Int64/Bool/Unit. At least one step per region; exact dependencies and execution order; no shadowing/free refs; no cycles. Max 8 definitions,8 params,32 steps/region,64 expanded nodes, nesting4. Definitions may compose prior library definitions by their exact names. All supplied definitions are validated even unused. No Python, new opcodes, comments, Markdown or prose. Never add end inside reusable arithmetic operations. All checks are ordered, not optimized. seq return provenance is region span. Execution has no LLM.'''
    (HERE/'INTERFACE.txt').write_text(interface+'\n',encoding='utf-8')
    save('FREEZE.json',dict(timestamp=now(), model=MODEL,digest=DIGEST,options=OPTIONS,think=False,
         files={p.name:sha(p) for p in [HERE/'TASKS.json',HERE/'INTERFACE.txt',HERE/'PROTOCOL.md',HERE/'run.py']},
         foundation=c.FOUNDATION, wrapper=sha(ROOT/'experiments/typed_composition_r6_18/composition.py')))

def seal_proposal(raw, library, discovery):
    proposal=c.load(raw)
    if set(proposal)!={'definitions','program'}:
        c.fail('SHAPE','$','definitions/program exact fields required')
    new=proposal['definitions']
    if type(new) is not list or (not discovery and new) or len(new)>2:
        c.fail('VOCABULARY','$','evaluation definitions forbidden; discovery at most two')
    registry={d['name']:copy.deepcopy(d) for d in library}
    pending={d['name']:copy.deepcopy(d) for d in new}
    if len(pending)!=len(new) or set(pending)&set(registry):
        c.fail('VOCABULARY','$','duplicate or frozen family')
    active=set()
    def pin(d):
        if 'identity' in d:
            c.fail('SHAPE','$','omit identity; deterministic sealing only')
        for name in list(d['dependencies']):
            if d['dependencies'][name]!='AUTO':
                c.fail('IDENTITY','$','AUTO pins required')
            d['dependencies'][name]=resolve(name)['identity']
        for s in d['steps']:
            n=s['node']
            if n.get('op')=='compose':
                if n['identity']!='AUTO':
                    c.fail('IDENTITY','$','AUTO call pin required')
                n['identity']=resolve(n['symbol'])['identity']
        return c.seal(d)
    def resolve(name):
        if name in registry:
            return registry[name]
        if name not in pending:
            c.fail('UNKNOWN_SYMBOL','$',name)
        if name in active:
            c.fail('CYCLE','$',name)
        active.add(name)
        registry[name]=pin(pending[name])
        active.remove(name)
        return registry[name]
    for name in pending:
        resolve(name)
    return dict(version=c.VERSION,foundation=c.FOUNDATION,definitions=list(registry.values()),
                program=pin(proposal['program'])), [registry[n] for n in pending]

def observation(out):
    if out['status']!='success':
        return {'status':'reject','code':out['error']['code']}
    return dict(status='ok',value=out['value'],output=out['output'].hex(),consumed=out['consumed'])

def score(package, task):
    t=time.perf_counter(); c.validate(package); validation=time.perf_counter()-t
    t=time.perf_counter(); expanded=c._expand_validated(package); expansion=time.perf_counter()-t
    assert expanded==c.expand(package)
    rows=[]; t=time.perf_counter()
    for case in task['cases']:
        out=c.vm.execute(expanded['plan'],bytes.fromhex(case['input']))
        again=c.vm.execute(expanded['plan'],bytes.fromhex(case['input']))
        assert out==again
        got=observation(out)
        rows.append(dict(input=case['input'],expected=case['expected'],actual=got,passed=got==case['expected'],envelope=out))
    execution=time.perf_counter()-t
    controls=[]
    success=next((r for r in rows if r['envelope']['status']=='success'),None)
    if success:
        for budget in range(success['envelope']['work']+2):
            out=c.vm.execute(expanded['plan'],bytes.fromhex(success['input']), {'work':budget})
            assert out==c.vm.execute(expanded['plan'],bytes.fromhex(success['input']),{'work':budget})
            controls.append(dict(budget=budget,result=out))
    calls=[n['node']['symbol'] for d in package['definitions']+[package['program']] for n in d['steps'] if n['node']['op']=='compose']
    return dict(passed=all(r['passed'] for r in rows),correct=sum(r['passed'] for r in rows),cases=len(rows),
                validation_seconds=validation,expansion_seconds=expansion,execution_seconds=execution,
                nodes=expanded['nodes'],plan_identity=expanded['plan_identity'],reuse_calls=calls,
                deterministic=True,rows=rows,limit_controls=controls)

def session(task, library, discovery, label):
    t=time.perf_counter(); retrieval=json.dumps(library); retrieval_time=time.perf_counter()-t
    system=(HERE/'INTERFACE.txt').read_text()+'\nImmutable library: '+retrieval
    instruction=task['requirement']+(' Propose up to two meaningful parameterized reusable compositions with this solution.' if discovery else ' You may not define or change operations. Return definitions:[]; use library if helpful.')
    messages=[dict(role='system',content=system),dict(role='user',content=instruction)]
    attempts=[]; accepted=[]
    for i in range(3):
        r=call(label+'_'+str(i+1),messages)
        text=r['response']['message']['content']
        entry={'attempt':i+1,'call':label+'_'+str(i+1),'valid':False}
        try:
            package,new=seal_proposal(text,library,discovery)
            c.expand(package)
            entry['valid']=True
            entry['package']=package
            result=score(package,task)
            save('scores/'+label+'_'+str(i+1)+'.json',result)
            entry['score']={k:v for k,v in result.items() if k not in ('rows','limit_controls')}
            first=next((x for x in result['rows'] if not x['passed']),None)
            feedback=dict(status='accepted' if result['passed'] else 'behavior_failure',correct=result['correct'],cases=result['cases'],first_mismatch=first)
            if result['passed']:
                accepted=new
        except c.Diagnostic as exc:
            feedback=dict(status='reject',diagnostic=exc.data)
        except (KeyError,TypeError,ValueError) as exc:
            feedback=dict(status='reject',diagnostic=dict(code='PROPOSAL_SHAPE',detail=str(exc)))
        entry['feedback']=feedback
        attempts.append(entry)
        save('sessions/'+label+'.json',dict(task=task['id'],discovery=discovery,retrieval_seconds=retrieval_time,
             library_bytes=len(retrieval.encode()),attempts=attempts))
        print(label,i+1,feedback['status'],flush=True)
        if feedback['status']=='accepted':
            break
        messages += [r['response']['message'],dict(role='user',content='Repair within same rules. Deterministic feedback: '+json.dumps(feedback))]
    return accepted,dict(label=label,task=task['id'],attempts=len(attempts),first_valid=attempts[0]['valid'],
                        accepted=attempts[-1]['feedback']['status']=='accepted',invalid=sum(not x['valid'] for x in attempts),
                        final_score=attempts[-1].get('score'),retrieval_seconds=retrieval_time)

def experiment():
    frozen=json.loads((HERE/'FREEZE.json').read_text())
    assert all(sha(HERE/p)==h for p,h in frozen['files'].items())
    tasks=json.loads((HERE/'TASKS.json').read_text())['tasks']
    start=now(); t=time.perf_counter(); library=[]; development=[]
    for task in tasks[:3]:
        new,result=session(task,library,True,task['id'])
        library+=new; development.append(result)
    overhead=time.perf_counter()-t
    save('VOCABULARY.json',dict(timestamp=now(),definitions=library,identities={d['name']:d['identity'] for d in library},
         canonical_sha256=hashlib.sha256(c.canonical(library)).hexdigest(),bytes=len(c.canonical(library)),
         development=development,discovery_seconds=overhead))
    results=[]
    # Balanced track-first schedule and distinct within-track task order.
    order=[('B','E1'),('C','E2'),('C','E1'),('B','E2'),('B','E3'),('C','E4'),('C','E3'),('B','E4')]
    for track,key in order:
        task=next(x for x in tasks if x['id']==key)
        _,result=session(task,[] if track=='B' else library,False,track+'_'+key)
        results.append(dict(track=track,**result))
        assert hashlib.sha256(c.canonical(library)).hexdigest()==json.loads((HERE/'VOCABULARY.json').read_text())['canonical_sha256']
    save('RESULTS.json',dict(start=start,end=now(),discovery_seconds=overhead,development=development,evaluation=results))

if __name__=='__main__':
    mode=sys.argv[1]
    p,log=server()
    try:
        if mode=='prepare':
            inventory(); calibrate(); prepare()
        elif mode=='experiment':
            experiment()
        else:
            raise ValueError(mode)
        save('LOCALITY-'+mode+'.json',dict(timestamp=now(),pid=p.pid,config=dict(host=BASE,no_cloud=True,remote_proxies='loopback port9'),
             connections=ps(f'Get-NetTCPConnection -OwningProcess {p.pid} -ErrorAction SilentlyContinue | Select-Object State,LocalAddress,LocalPort,RemoteAddress,RemotePort | ConvertTo-Json'),
             loaded=api('/api/ps')))
    finally:
        p.terminate(); p.wait(timeout=30); log.close()
