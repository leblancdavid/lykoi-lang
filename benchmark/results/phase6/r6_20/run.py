"""Frozen neutral R6.20 diagnostics. No production writes or remote inference."""
import copy
import ctypes
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT / 'experiments/typed_composition_r6_18'))
import composition as c
import jsonschema

MODEL = 'qwen3:8b'
DIGEST = '500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41'
WEIGHT = 'a3de86cd1c132c822487ededd47a324c50491393e6565cd14bafa40d0b8e686f'
BASE = 'http://127.0.0.1:11435'
OPTIONS = dict(temperature=0, seed=619, num_ctx=8192, num_predict=4096,
               top_k=20, top_p=.95, repeat_penalty=1)
HTTP = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def save(name, value):
    p = HERE / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, indent=2, ensure_ascii=True,
                 default=lambda x: {'bytes_hex': x.hex()} if isinstance(x, bytes) else str(x)) + '\n', encoding='utf-8')


def command(args):
    p = subprocess.run(args, capture_output=True, text=True, timeout=30)
    return dict(command=args, returncode=p.returncode, stdout=p.stdout, stderr=p.stderr)


def ps(text):
    return command(['pwsh', '-NoProfile', '-Command', text])


def api(path, data=None, timeout=15):
    assert path in ('/api/version', '/api/tags', '/api/show', '/api/ps', '/api/chat')
    req = urllib.request.Request(BASE + path, data=None if data is None else json.dumps(data).encode(),
                                 headers={'Content-Type': 'application/json'})
    with HTTP.open(req, timeout=timeout) as response:
        return json.load(response)


def preservation():
    old = ROOT / 'benchmark/results/phase6/r6_19'
    b = json.loads((old / 'BASELINE.json').read_text())
    pins = dict(b['protected_files'])
    pub = json.loads((old / 'PUBLICATION-IDENTITIES.json').read_text())
    for p, item in pub['files'].items():
        assert sha(ROOT / p) == item['sha256'], p
        pins[p] = item['sha256']
    for name in ('PUBLICATION-IDENTITIES.json', 'VERIFICATION.json'):
        p = old / name
        pins[p.relative_to(ROOT).as_posix()] = sha(p)
    assert all(sha(ROOT / p) == h for p, h in pins.items())
    assert len(b['kernel_ledger']['baseline_kernel']) + len(b['kernel_ledger']['preserved_additions']) == 26
    return dict(timestamp=now(), protected_files=pins, protected_count=len(pins), mismatches=[],
                kernel=26, foundation=c.FOUNDATION, wrapper=sha(Path(c.__file__)),
                r6_19_publication_count=len(pub['files']), initial_git=command(['git', 'status', '--short']),
                head=command(['git', 'rev-parse', 'HEAD']))


def obj(properties):
    return dict(type='object', properties=properties, required=list(properties), additionalProperties=False)


def region(name, steps, result, params=None, dependencies=None):
    return dict(name=name, revision=1, params=params or [], dependencies=dependencies or {},
                steps=steps, order=[s['id'] for s in steps], result=result, result_type='Int64')


def step(name, typ, node, deps=None):
    return dict(id=name, type=typ, deps=deps or [], node=node)


def package(d, library):
    return dict(version=c.VERSION, foundation=c.FOUNDATION,
                definitions=copy.deepcopy(library), program=c.seal(d))


def schemas():
    full = json.loads((ROOT / 'experiments/typed_composition_r6_18/typed-composition-1.schema.json').read_text())
    full['$defs']['definition']['required'].remove('identity')
    del full['$defs']['definition']['properties']['identity']
    definition = dict(full['$defs']['definition'], **{'$defs': full['$defs']})
    name = full['$defs']['name']
    typ = full['$defs']['type']
    strings = dict(type='array', items=name, uniqueItems=True)
    stages = [obj({'operations': dict(type='array', items={'enum': ['atom', 'value', 'check', 'end', 'compose']}, uniqueItems=True)}),
              obj({'name': name, 'revision': {'const': 1}, 'params': full['$defs']['definition']['properties']['params'],
                   'dependencies': full['$defs']['definition']['properties']['dependencies'],
                   'steps': dict(type='array', minItems=1, maxItems=32, items=obj({'id': name, 'type': typ})), 'result_type': typ}),
              obj({'deps': dict(type='object', additionalProperties=strings)}),
              obj({'nodes': dict(type='object', additionalProperties={'$ref': '#/$defs/node'})}),
              obj({'order': strings}), obj({'result': {'$ref': '#/$defs/expr'}})]
    for s in stages:
        s['$defs'] = full['$defs']
    return definition, stages


def prepare():
    assert not (HERE / 'FREEZE.json').exists(), 'never overwrite a freeze'
    save('BASELINE.json', preservation())
    schema, stages = schemas()
    save('SCHEMAS.json', dict(definition=schema, stages=stages))
    echo = c.seal(region('Echo', [step('copy', 'Int64', {'op': 'value', 'expr': {'ref': 'p'}}, ['p'])],
                         {'ref': 'copy'}, [dict(name='p', type='Int64')]))
    relay = c.seal(region('Relay', [step('inner', 'Int64', dict(op='compose', symbol='Echo', identity=echo['identity'],
                                args={'p': {'ref': 'q'}}), ['q'])], {'ref': 'inner'},
                                [dict(name='q', type='Int64')], {'Echo': echo['identity']}))
    library = [echo, relay]
    save('LIBRARY.json', library)
    rules = '''Return JSON only, no Markdown. R6.18 typed composition rules: a closed program is a definition with exact fields name,revision=1,params=[],dependencies={},steps,order,result,result_type=Int64. Omit program identity; host computes it, inserts package version/foundation and immutable library. Every step has exact id,type,deps,node. Types Int64,Bool,Unit (null); booleans are not integers. Names are case-sensitive ASCII letters then alphanumeric/underscore, at most32. Immutable unique step names; deps list exactly all referenced locals/parameters, no duplicates. Order contains every step exactly once, dependencies must precede uses; no shadowing or cycles. Expressions are {"const":integer|boolean|null}, {"ref":"name"}, {"add":[expr,expr]}, {"le":[expr,expr]}, {"eq":[expr,expr]}; add/le require Int64, eq same types. Nodes: {"op":"value","expr":expr}; {"op":"atom","codec":"uint8"}; {"op":"check","test":Bool_expr,"site":expr,"code":"ASCII_NAME"} returns Unit; {"op":"end"} returns Unit; {"op":"compose","symbol":"library_name","identity":"exact library hash","args":{"parameter":ref_or_const}}. Arguments cannot be compound expressions. Direct symbolic dependencies exactly equal called symbols with their supplied identity; transitive dependencies belong to library definitions, not program. The host never repairs semantic fields. Every stored step executes in order, check failure absorbs later operations, program returns result after steps, UInt16BE root output fixed. At least1 at most32 steps, expression depth8, representation depth24, max8 definitions, nesting4, expanded nodes64. Each region costs1 expansion node, each noncompose step1, compose is replaced by its region/steps, final encode1. For all closed neutral tasks input is empty, so do not use atom; do not use end unless requested. Unused typed values permitted. No new symbols or opcodes.
Both interfaces receive these rules, objective, same library and schemas. A emits a complete definition. B emits six stages: operations used; header/signatures (name,revision,params,dependencies,steps:[{id,type}],result_type); deps:{id:[refs]}; nodes:{id:node}; order:[ids]; result:expression. Host copies these fields exactly, never infers missing semantics. Shape validation at every stage; provisional validation after nodes uses submitted signature order and dummy const0 result, final validation uses submitted order/result. Choose signature order to be a valid provisional execution order. All semantic constraints apply to A and B.'''
    shared = rules + '\nImmutable library: ' + json.dumps(library) + '\nAll output schemas: ' + json.dumps(dict(definition=schema, stages=stages))
    (HERE / 'INTERFACE.txt').write_text(shared + '\n', encoding='utf-8')
    short_schema = obj({'mark': {'type': 'string'}, 'number': {'type': 'integer'}, 'active': {'type': 'boolean'}})
    expected = dict(mark='cobalt', number=23, active=True)
    runtime = []
    def rt(label, prompt, fmt, cap=4096, expected=None, tools=None):
        runtime.append(dict(id=label, prompt=prompt, format=fmt, cap=cap, expected=expected, tools=tools))
    for i in range(3):
        rt('short_' + str(i+1), 'Return exactly ' + json.dumps(expected), short_schema, expected=expected)
    for n, cap in [(16,256), (128,1024), (512,4096)]:
        rt('length_' + str(n), f'Return object items containing every integer from0 through{n-1} in ascending order.',
           obj({'items': dict(type='array', items={'type': 'integer'}, minItems=n, maxItems=n)}), cap, {'items': list(range(n))})
    nested_expected = {'leaf': 29}
    nested_schema = obj({'leaf': {'type': 'integer'}})
    for _ in range(6):
        nested_expected = {'child': nested_expected}
        nested_schema = obj({'child': nested_schema})
    for i in range(2):
        rt('nested_' + str(i+1), 'Return exactly ' + json.dumps(nested_expected), nested_schema, expected=nested_expected)
    rt('long_generic', 'Return object items containing every integer from0 through511 in ascending order.', 'json', expected={'items': list(range(512))})
    for cap in (16,64,256):
        rt('cap_' + str(cap), 'Return object items containing every integer from0 through127 in ascending order.', 'json', cap, {'items': list(range(128))})
    for words in (1024,4096,7168):
        rt('context_' + str(words), 'Neutral padding, ignore: ' + (' pebble' * words) + '\nReturn exactly ' + json.dumps(expected), short_schema, 256, expected)
    for i in range(3):
        value = dict(mark='sequential', number=31+i, active=False)
        rt('sequence_' + str(i+1), 'Return exactly ' + json.dumps(value), short_schema, 256, value)
    tool = {'type': 'function', 'function': {'name': 'echo', 'description': 'Inert text selection; no execution.',
            'parameters': obj({'text': {'type': 'string'}})}}
    for i in range(2):
        rt('tool_' + str(i+1), 'Select echo once with text neutral-twenty.', None, 256, tools=[tool])
    rt('health_final', 'Return exactly ' + json.dumps(expected), short_schema, 256, expected)
    features = [
        dict(id='typed_values', requirement='Exactly three value steps: integer31 named i, Boolean false named b, Unit null named u; return i.', expected={'status':'ok','value':31}, feature='typed values'),
        dict(id='immutable_refs', requirement='Value a=43, value b references a; return b. Exactly two steps.', expected={'status':'ok','value':43}, feature='immutable references'),
        dict(id='dependencies', requirement='Value a=7 then value b=11 then value c=add(ref a,ref b); return c. Exactly three steps.', expected={'status':'ok','value':18}, feature='exact local dependencies'),
        dict(id='ordered_regions', requirement='Check false code EARLY, then check false code LATE; each site const9, both Unit. Return const9; EARLY must be first failure. Exactly two steps.', expected={'status':'reject','code':'EARLY'}, feature='ordered regions'),
        dict(id='nested_composition', requirement='One compose step calls Relay with q=const47; return its result.', expected={'status':'ok','value':47}, feature='nested composition'),
        dict(id='symbol_identity', requirement='One compose step calls Echo with p=const53; use exact direct identity pin; return its result.', expected={'status':'ok','value':53}, feature='symbol identities'),
        dict(id='type_compatibility', requirement='Value b=eq(const true,const false) typed Bool; value i=const59 typed Int64; return i. Exactly two steps.', expected={'status':'ok','value':59}, feature='type compatibility'),
        dict(id='expansion_bounds', requirement='One compose step calls Relay with q=const61; return its result. Fit expansion node_budget=5 exactly.', expected={'status':'ok','value':61}, feature='expansion bounds', node_budget=5)]
    objectives = [
        dict(id='N1', requirement='Exactly three value steps named whole,flag,empty: whole is integer73, flag Boolean true, empty Unit null. Return whole.', expected={'status':'ok','value':73}),
        dict(id='N2', requirement='Exactly two value steps: source=integer19, doubled=add(ref source,ref source). Return doubled.', expected={'status':'ok','value':38}),
        dict(id='N3', requirement='Exactly two Unit checks named first,second, each testing const false at site const5. First code FIRST then code SECOND. Return const5; FIRST must be the absorbing first failure.', expected={'status':'reject','code':'FIRST'}),
        dict(id='N4', requirement='Exactly one step named relayed calls immutable Relay(q=const41). Return relayed; declare only direct symbol dependency.', expected={'status':'ok','value':41})]
    save('TASKS.json', dict(runtime=runtime, features=features, objectives=objectives,
                           comparison_schedule=[['N1','A'],['N1','B'],['N2','B'],['N2','A'],['N3','A'],['N3','B'],['N4','B'],['N4','A']]))
    controls(schema, library)
    save('FREEZE.json', dict(timestamp=now(), model=MODEL, digest=DIGEST, options=OPTIONS, think=False,
             files={p.name:sha(p) for p in [HERE/n for n in ('PROTOCOL.md','run.py','SCHEMAS.json','TASKS.json','LIBRARY.json','INTERFACE.txt','HOST-CONTROLS.json')]},
             baseline=sha(HERE/'BASELINE.json'), foundation=c.FOUNDATION))
    print('Prepared freeze and qualified host controls; no inference.', flush=True)


def schema_check(value, schema):
    jsonschema.Draft202012Validator(schema).validate(value)


def classify(text, schema, library, objective=None, node_budget=64):
    t = time.perf_counter()
    out = dict(json_valid=False, strict_valid=False, schema_valid=False, composition_valid=False,
               objective_complete=False, classification=None, diagnostic=None)
    try:
        json.loads(text)
        out['json_valid'] = True
        value = c.load(text)
        out['strict_valid'] = True
        schema_check(value, schema)
        out['schema_valid'] = True
        pkg = package(value, library)
        expanded = c.expand(pkg, node_budget)
        out.update(composition_valid=True, package=pkg, expanded_nodes=expanded['nodes'])
        if objective is not None:
            result = c.vm.execute(expanded['plan'], b'')
            obs = {'status':'ok', 'value':result['value']} if result['status']=='success' else {'status':'reject','code':result['error']['code']}
            out.update(observation=obs, envelope=result, objective_complete=obs==objective['expected'])
            # Structural requirements supplement independent value/error observation.
            if objective['id'] == 'N1':
                wanted = [('whole','Int64',73),('flag','Bool',True),('empty','Unit',None)]
                out['objective_complete'] &= [(s['id'],s['type'],s['node'].get('expr',{}).get('const')) for s in value['steps']] == wanted
            elif objective['id'] == 'N2':
                out['objective_complete'] &= len(value['steps'])==2 and value['steps'][1]['node']=={'op':'value','expr':{'add':[{'ref':'source'},{'ref':'source'}]}}
            elif objective['id'] == 'N3':
                out['objective_complete'] &= len(value['steps'])==2 and [s['id'] for s in value['steps']]==['first','second'] and [s['node'].get('code') for s in value['steps']]==['FIRST','SECOND']
            elif objective['id'] == 'N4':
                out['objective_complete'] &= len(value['steps'])==1 and value['steps'][0]['id']=='relayed' and value['steps'][0]['node'].get('symbol')=='Relay'
            out['classification'] = 'PASS' if out['objective_complete'] else 'SEMANTIC_OBJECTIVE_ERROR'
        else:
            out['classification'] = 'PASS'
    except json.JSONDecodeError as exc:
        out.update(classification='INVALID_JSON', diagnostic=str(exc))
    except jsonschema.ValidationError as exc:
        out.update(classification='SCHEMA_VIOLATION', diagnostic=dict(path=list(exc.path), message=exc.message))
    except c.Diagnostic as exc:
        code = exc.data['code']
        category = 'TYPE_ERROR' if code=='TYPE' else 'DEPENDENCY_ERROR' if code in ('DEPENDENCY','ORDER','CYCLE','UNKNOWN_REFERENCE','CAPTURE') else 'EXPANSION_ERROR' if code in ('EXPANSION_LIMIT','RESOURCE') else 'SERIALIZATION_ERROR' if code=='SERIALIZATION' else 'SEMANTIC_ERROR'
        out.update(classification=category, diagnostic=exc.data)
    out['validation_seconds'] = time.perf_counter()-t
    return out


def controls(schema, library):
    good = region('Control', [step('v','Int64',{'op':'value','expr':{'const':17}})], {'ref':'v'})
    rows = []
    def check(label, value, expected, budget=64, objective=None, raw=None):
        result = classify(raw if raw is not None else json.dumps(value), schema, library, objective, budget)
        assert result['classification']==expected, (label,result)
        rows.append(dict(id=label, expected=expected, result=result))
    check('good',good,'PASS')
    check('syntax',good,'INVALID_JSON',raw='{')
    check('duplicate',good,'SERIALIZATION_ERROR',raw='{"name":1,"name":2}')
    bad=copy.deepcopy(good); del bad['order']; check('shape',bad,'SCHEMA_VIOLATION')
    bad=copy.deepcopy(good); bad['steps'][0]['type']='Bool'; check('type',bad,'TYPE_ERROR')
    bad=copy.deepcopy(good); bad['steps'][0]['deps']=['v']; check('deps',bad,'DEPENDENCY_ERROR')
    bad=region('Pin', [step('r','Int64',dict(op='compose',symbol='Echo',identity='0'*64,args={'p':{'const':17}}))],{'ref':'r'},dependencies={'Echo':'0'*64})
    check('identity',bad,'SEMANTIC_ERROR')
    check('bounds',good,'EXPANSION_ERROR',budget=2)
    bad=region('Overflow', [step('v','Int64',{'op':'value','expr':{'const':70000}})], {'ref':'v'})
    check('valid_but_encode_fails',bad,'SEMANTIC_OBJECTIVE_ERROR',objective={'id':'control','expected':{'status':'ok','value':70000}})
    save('HOST-CONTROLS.json',dict(timestamp=now(),rows=rows,passed=len(rows),
                                schema_library_version=jsonschema.__version__))


class MemoryStatus(ctypes.Structure):
    _fields_ = [('length',ctypes.c_ulong),('load',ctypes.c_ulong)] + [(n,ctypes.c_ulonglong) for n in
                ('total_phys','avail_phys','total_page','avail_page','total_virtual','avail_virtual','avail_extended')]


def sample(pid):
    m=MemoryStatus(); m.length=ctypes.sizeof(m)
    ram_ok=bool(ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)))
    gpu=command(['nvidia-smi','--query-gpu=memory.total,memory.used,utilization.gpu,utilization.memory','--format=csv,noheader,nounits'])
    class Counters(ctypes.Structure):
        _fields_=[('cb',ctypes.c_ulong),('faults',ctypes.c_ulong)]+[(n,ctypes.c_size_t) for n in
                 ('peak_working','working','peak_paged','paged','peak_nonpaged','nonpaged','pagefile','peak_pagefile','private')]
    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    kernel.OpenProcess.argtypes=[ctypes.c_ulong,ctypes.c_int,ctypes.c_ulong]
    kernel.OpenProcess.restype=ctypes.c_void_p
    kernel.CloseHandle.argtypes=[ctypes.c_void_p]
    proc=kernel.OpenProcess(0x410,False,pid)
    counters=Counters(); counters.cb=ctypes.sizeof(counters)
    lib=ctypes.WinDLL('psapi',use_last_error=True)
    lib.GetProcessMemoryInfo.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_ulong]
    ok=bool(proc and lib.GetProcessMemoryInfo(proc,ctypes.byref(counters),counters.cb))
    if proc: kernel.CloseHandle(proc)
    return dict(timestamp=now(), ram_available_bytes=m.avail_phys if ram_ok else None,
                ram_total_bytes=m.total_phys if ram_ok else None, gpu=gpu,
                server_pid=pid,server_working_set_bytes=counters.working if ok else None,
                server_private_bytes=counters.private if ok else None,
                process_memory_note='Ollama parent only; runner included in system/GPU observations, per-runner memory unavailable here')


class Runner:
    def __init__(self):
        self.pid=None; self.proc=None; self.log=None; self.records=[]; self.errors=0
        self.started=time.perf_counter(); self.stop_reason=None

    def start(self):
        try:
            api('/api/version')
        except OSError:
            pass
        else:
            raise RuntimeError('11435 already occupied; do not reuse unknown server')
        env=os.environ.copy()
        allowed=['OLLAMA_CONTEXT_LENGTH','OLLAMA_NUM_PARALLEL','OLLAMA_MAX_QUEUE','OLLAMA_FLASH_ATTENTION','OLLAMA_KV_CACHE_TYPE','OLLAMA_GPU_OVERHEAD','OLLAMA_LLM_LIBRARY','OLLAMA_DEBUG','OLLAMA_KEEP_ALIVE','OLLAMA_LOAD_TIMEOUT']
        inherited={k:env.get(k) for k in allowed}
        env.update(OLLAMA_HOST='127.0.0.1:11435',OLLAMA_NO_CLOUD='1',OLLAMA_MODELS=r'D:\Software\.ollama\models',
                   HTTP_PROXY='http://127.0.0.1:9',HTTPS_PROXY='http://127.0.0.1:9',NO_PROXY='127.0.0.1,localhost',OLLAMA_MAX_LOADED_MODELS='1')
        self.log=open(HERE/'SERVER.log','ab')
        self.proc=subprocess.Popen(['ollama','serve'],env=env,stdout=self.log,stderr=self.log)
        self.pid=self.proc.pid
        for _ in range(60):
            if self.proc.poll() is not None:
                raise RuntimeError('server exited during startup')
            try:
                api('/api/version'); break
            except OSError:
                time.sleep(.5)
        else:
            raise RuntimeError('server startup timeout')
        tags=api('/api/tags'); selected=next(x for x in tags['models'] if x['name']==MODEL)
        assert selected['digest']==DIGEST
        blob=Path(r'D:\Software\.ollama\models\blobs')/('sha256-'+WEIGHT)
        assert sha(blob)==WEIGHT
        show=api('/api/show',{'model':MODEL})
        save('INVENTORY.json',dict(timestamp=now(),version=api('/api/version'),selected=selected,show=show,
             weight_sha256=WEIGHT,weight_bytes=blob.stat().st_size,baseline_options=OPTIONS,think=False,
             allowed_inherited_runtime_environment=inherited,server_environment_overrides={k:env[k] for k in ('OLLAMA_HOST','OLLAMA_NO_CLOUD','OLLAMA_MODELS','HTTP_PROXY','HTTPS_PROXY','NO_PROXY','OLLAMA_MAX_LOADED_MODELS')},
             python=command(['python','--version']),ollama=command(['ollama','--version']),
             gpu=command(['nvidia-smi','--query-gpu=name,memory.total,memory.used,utilization.gpu,driver_version','--format=csv']),
             os=ps('Get-CimInstance Win32_OperatingSystem | Select-Object Caption,Version,TotalVisibleMemorySize,FreePhysicalMemory | ConvertTo-Json'),
             processes=ps("Get-CimInstance Win32_Process -Filter \"Name like '%ollama%' or Name='llama-server.exe'\" | Select-Object ProcessId,ParentProcessId,Name,ExecutablePath | ConvertTo-Json"),
             initial_resources=sample(self.pid),schema_library_version=jsonschema.__version__,
             locality='loopback allowlist, verified local GGUF, cloud disabled, no pull/fallback; not OS firewall attestation'))

    def active(self):
        if self.stop_reason:
            return False
        if self.proc.poll() is not None:
            self.stop_reason='runner parent exited'; return False
        if len(self.records)>=80 or time.perf_counter()-self.started>=1200:
            self.stop_reason='precommitted call/time ceiling'; return False
        return True

    def call(self,label,messages,fmt='json',cap=4096,tools=None,health=False):
        if not self.active():
            return None
        request=dict(model=MODEL,messages=messages,options=dict(OPTIONS,num_predict=cap),think=False,stream=False,keep_alive='10m')
        if fmt is not None: request['format']=fmt
        if tools: request['tools']=tools
        start=time.perf_counter(); offset=(HERE/'SERVER.log').stat().st_size
        samples=[]; event=threading.Event()
        def monitor():
            while not event.is_set():
                try: samples.append(sample(self.pid))
                except Exception as exc: samples.append(dict(timestamp=now(),error=str(exc)))
                event.wait(1)
        thread=threading.Thread(target=monitor,daemon=True); thread.start()
        status=None; body=None; response=None; error=None; headers={}
        req=urllib.request.Request(BASE+'/api/chat',data=json.dumps(request).encode(),headers={'Content-Type':'application/json'})
        stamp=now()
        try:
            with HTTP.open(req,timeout=180) as r:
                status=r.status; headers={'content-type':r.headers.get('Content-Type')}
                body=r.read().decode('utf-8',errors='replace'); response=json.loads(body)
        except urllib.error.HTTPError as exc:
            status=exc.code; body=exc.read().decode('utf-8',errors='replace'); error=str(exc)
        except (OSError,ValueError) as exc:
            error=repr(exc)
        latency=time.perf_counter()-start
        event.set(); thread.join(timeout=35)
        post={}
        for path in ('/api/version','/api/ps'):
            try: post[path]=api(path)
            except OSError as exc: post[path]={'error':repr(exc)}
        end=(HERE/'SERVER.log').stat().st_size
        record=dict(id=label,timestamp=stamp,request=request,prompt_sha256=digest(messages),schema_sha256=digest(fmt),
                    http_status=status,error=error,response_body=body,response=response,response_headers=headers,
                    latency_seconds=latency,post_health=post,resources=samples,log_byte_span=[offset,end],
                    tokens={k:response.get(k) if response else None for k in ('prompt_eval_count','prompt_eval_cached_count','eval_count')},
                    durations_ns={k:response.get(k) if response else None for k in ('total_duration','load_duration','prompt_eval_duration','eval_duration')})
        self.records.append(record); save('calls/'+label+'.json',record)
        print(label,status,round(latency,3),'s',record['tokens'],flush=True)
        failure=status is None or status>=500
        if failure:
            self.errors+=1
            if self.errors>=2 or health or any('error' in v for v in post.values()):
                self.stop_reason='repeated instability or failed health check'
            else:
                tasks=json.loads((HERE/'TASKS.json').read_text())
                probe=tasks['runtime'][0]
                follow=self.call(label+'_health',[{'role':'user','content':probe['prompt']}],probe['format'],256,health=True)
                if follow is None or follow['http_status']!=200:
                    self.stop_reason='post-error inference not responsive'
        return record

    def stop(self):
        if self.proc:
            save('LOCALITY.json',dict(timestamp=now(),server_pid=self.pid,
                 processes=ps("Get-CimInstance Win32_Process -Filter \"Name like '%ollama%' or Name='llama-server.exe'\" | Select-Object ProcessId,ParentProcessId,Name,CommandLine,WorkingSetSize | ConvertTo-Json"),
                 connections=ps(f'Get-NetTCPConnection -OwningProcess {self.pid} -ErrorAction SilentlyContinue | Select-Object State,LocalAddress,LocalPort,RemoteAddress,RemotePort | ConvertTo-Json'),
                 loaded=api('/api/ps') if self.proc.poll() is None else None))
            save('CLEANUP.json',dict(timestamp=now(),owned_server_pid=self.pid,
                 termination=command(['taskkill','/PID',str(self.pid),'/T','/F']),desktop='not targeted'))
            self.proc.wait(timeout=15)
        if self.log: self.log.close()


def content(record):
    return record['response']['message']['content'] if record and record['response'] else None


def runtime_tests(r,tasks):
    rows=[]; sequence=[]
    for task in tasks:
        if not r.active(): break
        messages=[dict(role='user',content=task['prompt'])]
        if task['id'].startswith('sequence_'):
            sequence+=messages; messages=sequence
        rec=r.call(task['id'],messages,task['format'],task['cap'],task['tools'])
        t=time.perf_counter()
        row=dict(id=task['id'],http_status=rec['http_status'],json_valid=None,schema_valid=None,objective_complete=False,classification='RUNTIME_FAILURE')
        if rec['http_status']==200:
            if task['tools']:
                calls=rec['response']['message'].get('tool_calls',[])
                row['objective_complete']=len(calls)==1 and calls[0]['function']['name']=='echo' and calls[0]['function']['arguments']=={'text':'neutral-twenty'}
                row['classification']='PASS' if row['objective_complete'] else 'TOOL_SELECTION_ERROR'
            else:
                try:
                    value=json.loads(content(rec)); row['json_valid']=True
                    if isinstance(task['format'],dict):
                        schema_check(value,task['format']); row['schema_valid']=True
                    row['objective_complete']=value==task['expected']
                    row['classification']='PASS' if row['objective_complete'] else 'SEMANTIC_OBJECTIVE_ERROR'
                except json.JSONDecodeError:
                    row.update(json_valid=False,schema_valid=False,classification='INVALID_JSON')
                except jsonschema.ValidationError:
                    row.update(schema_valid=False,classification='SCHEMA_VIOLATION')
        row['validation_seconds']=time.perf_counter()-t
        rows.append(row); save('STRUCTURED-RESULTS.json',dict(rows=rows,planned=len(tasks),not_reached=[x['id'] for x in tasks[len(rows):]]))
        if task['id'].startswith('sequence_') and rec['response']:
            sequence.append(rec['response']['message'])
    return rows


def feedback(result):
    return {k:result[k] for k in ('classification','diagnostic') if k in result}


def assemble(parts):
    _,header,deps,nodes,order,result=parts
    d=copy.deepcopy(header)
    for s in d['steps']:
        s['deps']=copy.deepcopy(deps['deps'][s['id']]); s['node']=copy.deepcopy(nodes['nodes'][s['id']])
    d['order']=order['order']; d['result']=result['result']
    return d


def comparison(r,task,mode,system,schemas,library):
    started=time.perf_counter(); remaining=4096; parts=[]; attempts=[]; messages=[dict(role='system',content=system)]
    final=None; assembly_time=0
    for i in range(6):
        if remaining<=0 or not r.active(): break
        schema=schemas['definition'] if mode=='A' else schemas['stages'][i]
        instruction=task['requirement']+'\n'+('Emit complete definition.' if mode=='A' else f'Emit stage{i+1} only using its shared schema.')
        if i and mode=='A': instruction='Regenerate complete definition within the identical rules and objective.'
        messages.append(dict(role='user',content=instruction))
        rec=r.call(task['id']+'_'+mode+'_'+str(i+1),messages,'json',remaining if mode=='A' else min(1024,remaining))
        if rec is None: break
        tokens=rec['tokens']['eval_count']
        remaining-=tokens if tokens is not None else rec['request']['options']['num_predict']
        if rec['http_status']!=200:
            attempts.append(dict(call=rec['id'],classification='RUNTIME_FAILURE')); break
        text=content(rec)
        if mode=='A':
            result=classify(text,schema,library,task)
            final=result
        else:
            t=time.perf_counter()
            result=dict(json_valid=False,schema_valid=False,classification='PASS',diagnostic=None)
            try:
                json.loads(text); result['json_valid']=True
                value=c.load(text); schema_check(value,schema); result['schema_valid']=True
                parts.append(value)
                if i==1:
                    if value['params']!=[] or value['result_type']!='Int64': c.fail('TYPE','$','closed Int64 required')
                    ids=[s['id'] for s in value['steps']]
                    if len(set(ids))!=len(ids): c.fail('CAPTURE','$','duplicate stage signature')
                if i in (2,3):
                    ids={s['id'] for s in parts[1]['steps']}
                    if set(value['deps'] if i==2 else value['nodes'])!=ids: c.fail('SHAPE','$','stage keys must equal signature IDs')
                if i>=3:
                    st=time.perf_counter()
                    p=parts+[{'order':[s['id'] for s in parts[1]['steps']]},{'result':{'const':0}}] if i==3 else parts+[{'result':{'const':0}}] if i==4 else parts
                    d=assemble(p); assembly_time+=time.perf_counter()-st
                    used={s['node']['op'] for s in d['steps']}
                    if set(parts[0]['operations'])!=used: c.fail('DEPENDENCY','$','operation selection differs from nodes')
                    partial=classify(json.dumps(d),schemas['definition'],library,task if i==5 else None)
                    result.update({k:v for k,v in partial.items() if k not in ('validation_seconds','json_valid','schema_valid')})
                    if i==5: final=partial
            except json.JSONDecodeError as exc:
                result.update(classification='INVALID_JSON',diagnostic=str(exc))
            except jsonschema.ValidationError as exc:
                result.update(classification='SCHEMA_VIOLATION',diagnostic=exc.message)
            except c.Diagnostic as exc:
                result.update(classification='TYPE_ERROR' if exc.data['code']=='TYPE' else 'DEPENDENCY_ERROR' if exc.data['code']=='DEPENDENCY' else 'SEMANTIC_ERROR',diagnostic=exc.data)
            result['validation_seconds']=time.perf_counter()-t
        attempts.append(dict(call=rec['id'],result=result))
        messages.append(rec['response']['message'])
        messages.append(dict(role='user',content='Deterministic validation feedback: '+json.dumps(feedback(result))))
        if mode=='A' and result['composition_valid']:
            break  # No oracle-driven repair of a valid but wrong objective.
        if mode=='B' and result['classification']!='PASS': break
    row=dict(objective=task['id'],interface=mode,attempts=attempts,final=final,
             objective_complete=bool(final and final['objective_complete']),composition_valid=bool(final and final['composition_valid']),
             calls=len(attempts),repair_attempts=max(0,len(attempts)-1) if mode=='A' else 0,
             generated_token_budget=4096,remaining_output_budget=remaining,assembly_seconds=assembly_time,total_seconds=time.perf_counter()-started)
    save('sessions/'+task['id']+'_'+mode+'.json',row)
    return row


def execute():
    freeze=json.loads((HERE/'FREEZE.json').read_text())
    assert all(sha(HERE/p)==h for p,h in freeze['files'].items())
    assert not (HERE/'calls').exists(), 'do not replay/overwrite participant evidence'
    b=json.loads((HERE/'BASELINE.json').read_text()); assert all(sha(ROOT/p)==h for p,h in b['protected_files'].items())
    tasks=json.loads((HERE/'TASKS.json').read_text()); schemas=json.loads((HERE/'SCHEMAS.json').read_text())
    library=json.loads((HERE/'LIBRARY.json').read_text()); system=(HERE/'INTERFACE.txt').read_text()
    r=Runner(); features=[]; pairs=[]
    try:
        r.start()
        runtime_tests(r,tasks['runtime'])
        for task in tasks['features']:
            if not r.active(): break
            rec=r.call('feature_'+task['id'],[dict(role='system',content=system),dict(role='user',content=task['requirement']+' Emit complete definition.')])
            result=classify(content(rec),schemas['definition'],library,task,task.get('node_budget',64)) if rec['http_status']==200 else dict(classification='RUNTIME_FAILURE')
            features.append(dict(id=task['id'],feature=task['feature'],result=result)); save('FEATURE-RESULTS.json',dict(rows=features,planned=8))
        for name,mode in tasks['comparison_schedule']:
            if not r.active(): break
            task=next(x for x in tasks['objectives'] if x['id']==name)
            pairs.append(comparison(r,task,mode,system,schemas,library)); save('COMPARISON.json',dict(rows=pairs,planned=8))
        save('RUN-STATUS.json',dict(timestamp=now(),stop_reason=r.stop_reason,participant_calls=len(r.records),runtime_errors=r.errors,
             elapsed_seconds=time.perf_counter()-r.started,features_completed=len(features),comparison_sessions=len(pairs)))
    except Exception as exc:
        save('HARNESS-HALT.json',dict(timestamp=now(),error=repr(exc),participant_calls=len(r.records)))
        raise
    finally:
        r.stop()


if __name__=='__main__':
    if sys.argv[1]=='prepare': prepare()
    elif sys.argv[1]=='execute': execute()
    else: raise ValueError(sys.argv[1])
