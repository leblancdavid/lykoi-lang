"""Additive R6.30 coordinator. Historical implementation files are read only."""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import runtime

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
spec = importlib.util.spec_from_file_location('r630_previous', HERE.parent/'r6_29/experiment.py')
old = importlib.util.module_from_spec(spec)
spec.loader.exec_module(old)
h, tools = old.h, old.tools

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def read(p):
    return json.loads((HERE/p).read_text(encoding='utf-8'))

def save(p, value):
    dest = HERE/p
    dest.parent.mkdir(parents=True, exist_ok=True)
    assert not dest.exists(), str(dest)
    dest.write_text(json.dumps(value, indent=2)+'\n', encoding='utf-8')

def baseline():
    prev = HERE.parent/'r6_29'
    receipt = json.loads((prev/'VERIFICATION.json').read_text())
    assert receipt['passed'] and receipt['publication_manifest_sha256']==digest(prev/'PUBLICATION-IDENTITIES.json')
    pins = json.loads((prev/'BASELINE.json').read_text())['protected_files']
    publication = json.loads((prev/'PUBLICATION-IDENTITIES.json').read_text())
    for p, meta in publication['files'].items():
        assert digest(ROOT/p)==meta['sha256'], p
        pins[p]=meta['sha256']
    for name in ('PUBLICATION-IDENTITIES.json','VERIFICATION.json'):
        pins[(prev/name).relative_to(ROOT).as_posix()]=digest(prev/name)
    mismatches = [p for p,v in pins.items() if digest(ROOT/p)!=v]
    save('BASELINE.json', dict(timestamp=h.now(),protected_files=pins,protected_count=len(pins),
        mismatches=mismatches,kernel=26,kernel_ledger=json.loads((prev/'BASELINE.json').read_text())['kernel_ledger'],
        executable_sha256=digest(h.EXE),qualified_executable_matches=digest(h.EXE)==json.loads((prev/'BASELINE.json').read_text())['qualified_executable_sha256'],
        R6_29_publication_verified=True,R6_27_qualification='R6_27_TOOL_EXPOSURE_QUALIFIED',initial_git_status='clean',
        implementations={p:v for p,v in pins.items() if p.endswith(('interpreter.py','composition.py','adapter.py','tools.py','transport.py')) or p.startswith('src/')},
        preservation=['production kernel/compiler/lowerer/runtime','R6.10 VM','R6.18 wrapper','R6.23 adapter','R6.25 contracts','R6.3-R6.29 history']))
    assert not mismatches
    assert read('BASELINE.json')['qualified_executable_matches']
    assert len(read('BASELINE.json')['kernel_ledger']['baseline_kernel'])+len(read('BASELINE.json')['kernel_ledger']['preserved_additions'])==26
    print('Baseline verified:',len(pins),'identities')

def correction():
    # The scripted witness is authored from VM semantics, before loading the AI artifact.
    s=tools.Session(['value','check','compose'])
    calls=[]
    for name,args in [
        ('declare_input',dict(definition='StageControl',inputs=[dict(name='permit',type='Bool'),dict(name='n',type='Int64')])),
        ('apply_operation',dict(definition='StageControl',alias='gate',operation='check',expression='$permit',site=0,code='ControlDenied',dependencies=['permit'])),
        ('apply_operation',dict(definition='StageControl',alias='next',operation='value',type='Int64',expression=['add','$n',1],dependencies=['n'])),
        ('define_result',dict(definition='StageControl',result='$next',result_type='Int64')),
        ('validate_candidate',dict(target='StageControl'))]:
        call={'function':dict(name=name,arguments=args)}
        response=s.dispatch(call)
        assert response['success'],response
        calls.append(dict(call=call,response=response))
    cases=[(dict(permit=False,n=0),('reject','ControlDenied','validation')),
        (dict(permit=False,n=2**63-1),('reject','ControlDenied','validation')),
        (dict(permit=True,n=2**63-1),('reject','OVERFLOW','structure')),
        (dict(permit=True,n=65535),('reject','ENCODE_RANGE','encode')),
        (dict(permit=True,n=0),('success',None,None)),
        (dict(permit=True,n=True),('wrapper_reject','TYPE',None)),
        (dict(permit=True),('wrapper_reject','SHAPE',None))]
    rows=[]
    for args, expected in cases:
        obs,t=old.observe(s.completed['artifact'],dict(args=args))
        o=obs['observation']
        actual=(o['status'],o.get('error',o.get('diagnostic',{})).get('code'),o.get('error',{}).get('stage'))
        assert actual==expected,(actual,expected)
        rows.append(dict(args=args,expected=expected,actual=actual,evidence=obs,times=t))
    vm=ROOT/'experiments/semantic_interpreter/interpreter.py'
    source=vm.read_text()
    assert "self.fail(n['code'], self.expr(n['site'], env).start, 'validation')" in source
    save('CORRECTION-CONTROL.json',dict(timestamp=h.now(),model_calls=0,source_sha256=digest(vm),
        independent_of_model_artifact=True,calls=calls,records=rows,passed=True,
        justification='Machine.run check explicitly selects validation; add defaults to structure; emit chooses encode. Script signature/predicate differs from R6.29.'))
    original=json.loads((HERE.parent/'r6_29/ACCEPTANCE.json').read_text())
    corrected=copy.deepcopy(original)
    disputed=['guard','guard_first_overflow','guard_second_overflow','guard_underflow']
    changes=[]
    for case in corrected['cases']:
        if case['id'] in disputed:
            assert case['expected']['stage']=='structure'
            changes.append(dict(case=case['id'],before='structure',after='validation'))
            case['expected']['stage']='validation'
    assert len(changes)==4
    save('R6_29-ACCEPTANCE-SUCCESSOR-1.json',corrected)
    save('R6_29-CORRECTION-1.json',dict(timestamp=h.now(),version=1,changes=changes,
        original_manifest_sha256=digest(HERE.parent/'r6_29/ACCEPTANCE.json'),successor_manifest_sha256=digest(HERE/'R6_29-ACCEPTANCE-SUCCESSOR-1.json'),
        control_sha256=digest(HERE/'CORRECTION-CONTROL.json'),original_result='19/23',historical_classification='R6_29_CONSTRUCTION_PARTIAL',
        corrected_before_replay=True,artifact_used_to_justify_correction=False))
    artifact=json.loads((HERE.parent/'r6_29/LIVE/ARTIFACT.json').read_text())
    rows=[]
    for case in corrected['cases']:
        obs,t=old.observe(artifact,case)
        rows.append(dict(case=case,evidence=obs,times=t,passed=old.matched(artifact,case,obs)))
    assert all(r['passed'] for r in rows)
    save('R6_29-SUCCESSOR-REPLAY.json',dict(timestamp=h.now(),model_calls=0,passed=23,total=23,records=rows,
        artifact_sha256=digest(HERE.parent/'r6_29/LIVE/ARTIFACT.json'),artifact_unchanged=True,historical_result_unchanged=True,
        classification='R6_29_SUCCESSOR_EXPECTATIONS_23_OF_23'))
    print('Independent control7/7; unchanged R6.29 successor23/23; historical19/23 preserved')

def oracle(task,args,modified=False):
    """Independent explicit mathematical oracle, not candidate/source execution."""
    signature=task['signature'] if not modified else task.get('mod_signature',task['signature'])
    try:
        v=runtime.host(args,signature)
        def plus(a,b,step):
            n=a+b
            if n < -(2**63) or n > 2**63-1:
                raise runtime.Rejection('OVERFLOW','structure',step)
            return n
        def require(p,code,step):
            if p is not True:
                raise runtime.Rejection(code,'validation',step)
        if task['id']=='T1':
            n=plus(v['load'],v['reserve'],0)
            require(n<=v['cap'],'CapacityExceeded',1)
            result=plus(n,3,2)
            if modified:
                require(v['permit'],'AuditDenied',3)
        elif task['id']=='T2':
            require(v['enabled'],'Disabled',0)
            n=plus(v['a'],v['b'],1)
            require(n==v['expected'],'Mismatch',2)
            result=plus(n,1,3)
            if modified:
                result=plus(result,2,4)
                require(result<=1000,'PremiumLimit',5)
        else:
            n=plus(v['seed'],v['delta'],0)
            require(v['floor']<=n,'BelowFloor',1)
            result=plus(n,v['delta'],2)
            require(result<=65535,'AboveCeiling',3)
        if not 0<=result<=65535:
            raise runtime.Rejection('ENCODE_RANGE','encode')
        return dict(status='success',value=result,output_hex=result.to_bytes(2,'big').hex(),consumed=0)
    except runtime.Rejection as e:
        return dict(status='wrapper_reject' if e.stage is None else 'reject',code=e.code,stage=e.stage,step=e.step)

def selection():
    assert read('R6_29-SUCCESSOR-REPLAY.json')['passed']==23
    tasks=[dict(id='T1',target='CapacityFee',signature=dict(load='Int64',reserve='Int64',cap='Int64'),
        requirement='CapacityFee: in order, checked-add load+reserve (step0); check that this total <= cap with code CapacityExceeded (step1); checked-add fixed fee3 to the total (step2); return this result.',
        modification='Add an audited endpoint with signature load:Int64,reserve:Int64,cap:Int64,permit:Bool. Perform all original three steps unchanged, then check permit with code AuditDenied at step3 before return/encoding. Original endpoint remains available.',
        mod_signature=dict(load='Int64',reserve='Int64',cap='Int64',permit='Bool')),
        dict(id='T2',target='ConfirmedIncrement',signature=dict(enabled='Bool',a='Int64',b='Int64',expected='Int64'),
        requirement='ConfirmedIncrement: check enabled with code Disabled (step0); checked-add a+b (step1); check this sum equals expected with code Mismatch (step2); checked-add fixed1 to this sum (step3); return.',
        modification='Add a premium endpoint with the same signature. Perform all four original steps unchanged, then checked-add fixed2 to the prior result (step4), check this new result <=1000 with code PremiumLimit (step5), and return the new result. Original endpoint remains available.'),
        dict(id='T3',target='FloorThenCeiling',signature=dict(seed='Int64',delta='Int64',floor='Int64'),
        requirement='FloorThenCeiling: checked-add seed+delta (step0); check floor <= this first sum with code BelowFloor (step1); checked-add delta to the first sum (step2); check this second sum <=65535 with code AboveCeiling (step3); return the second sum.')]
    M=2**63-1
    raw={
        'T1':[dict(load=2,reserve=5,cap=7),dict(load=-3,reserve=0,cap=0),dict(load=65532,reserve=0,cap=65532),dict(load=1,reserve=1,cap=1),dict(load=M,reserve=1,cap=0),dict(load=M,reserve=0,cap=M),dict(load=M,reserve=0,cap=0),dict(load=-5,reserve=0,cap=0),dict(load=65533,reserve=0,cap=M),dict(load=-(2**63),reserve=-1,cap=0)],
        'T2':[dict(enabled=True,a=2,b=3,expected=5),dict(enabled=True,a=-1,b=0,expected=-1),dict(enabled=True,a=65534,b=0,expected=65534),dict(enabled=False,a=M,b=1,expected=0),dict(enabled=True,a=M,b=1,expected=0),dict(enabled=True,a=3,b=4,expected=8),dict(enabled=True,a=M,b=0,expected=0),dict(enabled=True,a=M,b=0,expected=M),dict(enabled=True,a=-2,b=0,expected=-2),dict(enabled=True,a=65535,b=0,expected=65535)],
        'T3':[dict(seed=5,delta=2,floor=7),dict(seed=0,delta=0,floor=0),dict(seed=65533,delta=1,floor=0),dict(seed=-1,delta=0,floor=-1),dict(seed=M,delta=1,floor=0),dict(seed=M-1,delta=1,floor=M),dict(seed=-(2**63),delta=-1,floor=0),dict(seed=-(2**63)+1,delta=-1,floor=-(2**63)),dict(seed=0,delta=-1,floor=0),dict(seed=65535,delta=1,floor=0),dict(seed=M-1,delta=1,floor=M-1)]}
    suites={}
    for task in tasks:
        cases=raw[task['id']]
        template=copy.deepcopy(cases[0])
        intname=next(n for n,t in task['signature'].items() if t=='Int64')
        for bad in (True,'3',None,1.5,2**63):
            cases.append(dict(template,**{intname:bad}))
        if 'enabled' in template:
            cases.append(dict(template,enabled=1))
        missing=copy.deepcopy(template)
        missing.pop(intname)
        conflict=copy.deepcopy(missing)
        conflict[next(iter(conflict))]=None
        cases.extend([missing,dict(template,extra=0),conflict])
        suites[task['id']]=[dict(id=task['id']+'-'+str(i),args=v,expected=oracle(task,v)) for i,v in enumerate(cases)]
    mods={}
    for task in tasks[:2]:
        cases=copy.deepcopy(raw[task['id']][:10])
        if task['id']=='T1':
            cases=[dict(v,permit=True) for v in cases]
            cases.extend([dict(load=1,reserve=2,cap=3,permit=False),dict(load=M,reserve=1,cap=0,permit=False),dict(load=65533,reserve=0,cap=M,permit=False),dict(load=1,reserve=2,cap=3,permit=1),dict(load=1,reserve=2,cap=3)])
        else:
            cases.extend([dict(enabled=True,a=997,b=0,expected=997),dict(enabled=True,a=998,b=0,expected=998)])
        mods[task['id']]=[dict(id=task['id']+'-M-'+str(i),args=v,expected=oracle(task,v,True)) for i,v in enumerate(cases)]
    save('TASKS.json',dict(tasks=tasks,selection_before_authoring=True,
        provenance='Coordinator-authored fresh synthetic bounded requirements selected once after correction; capability-tailored to fixed add/le/eq/check. No candidate inspected during selection.',
        contamination='Coordinator has R6.28/R6.29 outcomes; tasks differ in signatures, predicates, constants and ordering. Hidden author context exclusion unattested. Not independently sourced generalization.'))
    save('ACCEPTANCE.json',dict(base=suites,modified=mods,oracle='explicit mathematical oracle in frozen experiment.py; conventional host rules independently cross-checked against native wrapper/VM controls'))
    print('Tasks selected:',{k:len(v) for k,v in suites.items()})

def norm(artifact,args):
    obs,t=old.observe(artifact,dict(args=args))
    o=obs['observation']
    if o['status']=='success':
        result=dict(status='success',value=o['value'],output_hex=o['output']['bytes_hex'],consumed=o['consumed'])
    elif o['status']=='wrapper_reject':
        result=dict(status='wrapper_reject',code=o['diagnostic']['code'],stage=None,step=None)
    else:
        e=o['error']
        step=None
        if e['stage']!='encode':
            local=obs['expanded']['map'][e['node']]['local']
            steps=[s for s in artifact['definitions'][0]['steps'] if s.get('type')!='Bool']
            step=next(i for i,s in enumerate(steps) if s['id']==local)
        result=dict(status='reject',code=e['code'],stage=e['stage'],step=step)
    return result,t

def qualification():
    # Independent explicit scripted implementations from the formal requirements,
    # never supplied to author processes. Freeze happens only after native agreement.
    results=[]
    for task in read('TASKS.json')['tasks']:
        for modified in ([False,True] if 'modification' in task else [False]):
            name=task['target']+('Extended' if modified else '')
            signature=task.get('mod_signature',task['signature']) if modified else task['signature']
            s=tools.Session(['value','check','compose'])
            def call(tool,args):
                r=s.dispatch({'function':dict(name=tool,arguments=args)})
                assert r['success'],r
            call('declare_input',dict(definition=name,inputs=[dict(name=n,type=t) for n,t in signature.items()]))
            if task['id']=='T1':
                ops=[('total','value','Int64',['add','$load','$reserve'],None),('capgate','check',None,['le','$total','$cap'],'CapacityExceeded'),('fee','value','Int64',['add','$total',3],None)]
                if modified: ops.append(('audit','check',None,'$permit','AuditDenied'))
                result='$fee'
            elif task['id']=='T2':
                ops=[('gate','check',None,'$enabled','Disabled'),('total','value','Int64',['add','$a','$b'],None),('confirm','check',None,['eq','$total','$expected'],'Mismatch'),('increment','value','Int64',['add','$total',1],None)]
                result='$increment'
                if modified:
                    ops.extend([('premium','value','Int64',['add','$increment',2],None),('limit','check',None,['le','$premium',1000],'PremiumLimit')])
                    result='$premium'
            else:
                ops=[('first','value','Int64',['add','$seed','$delta'],None),('lower','check',None,['le','$floor','$first'],'BelowFloor'),('second','value','Int64',['add','$first','$delta'],None),('upper','check',None,['le','$second',65535],'AboveCeiling')]
                result='$second'
            for alias,op,kind,expr,code in ops:
                deps=[]
                for x in expr if isinstance(expr,list) else [expr]:
                    if isinstance(x,str) and x.startswith('$') and x[1:] not in deps: deps.append(x[1:])
                args=dict(definition=name,alias=alias,operation=op,expression=expr,dependencies=deps)
                if op=='value': args['type']=kind
                else: args.update(site=0,code=code)
                call('apply_operation',args)
            call('define_result',dict(definition=name,result=result,result_type='Int64'))
            call('validate_candidate',dict(target=name))
            cases=read('ACCEPTANCE.json')['modified' if modified else 'base'][task['id']]
            for case in cases:
                actual,t=norm(s.completed['artifact'],case['args'])
                assert actual==case['expected'],(case,actual)
                results.append(dict(task=task['id'],modified=modified,case=case['id'],actual=actual,passed=True,times=t))
    save('PREAUTHOR-QUALIFICATION.json',dict(timestamp=h.now(),model_calls=0,passed=True,records=results,
        checks='Every expected observation agrees with a separately scripted native program before freeze. Scripted programs are never included in author prompts.'))
    print('Pre-author native oracle qualification:',len(results),'PASS')

def freeze():
    assert read('PREAUTHOR-QUALIFICATION.json')['passed']
    files=['experiment.py','runtime.py','evaluate.py','PROTOCOL.md','BASELINE.json','TASKS.json','ACCEPTANCE.json','PREAUTHOR-QUALIFICATION.json','AUTHORING-DOCS.json']
    save('FREEZE.json',dict(timestamp=h.now(),model_calls=0,files={n:digest(HERE/n) for n in files},
        order=['T1-A','T1-B','T1-C','T2-B','T2-C','T2-A','T3-C','T3-A','T3-B'],
        modification_order=['T1-C','T1-B','T1-A','T2-A','T2-C','T2-B']))

def verify():
    assert all(digest(ROOT/p)==v for p,v in read('BASELINE.json')['protected_files'].items())
    assert all(digest(HERE/p)==v for p,v in read('FREEZE.json')['files'].items())

def docs():
    common='Host args must match the exact signature. Signature SHAPE precedes representation SHAPE (any float/list/object value), which precedes TYPE (Bool is not Int64; Int64 signed64 only). Ordered operations stop at first rejection. Native arithmetic overflow is OVERFLOW/structure; guard failures validation; final integer outside0..65535 ENCODE_RANGE/encode. No output on rejection. Failure step is zero-based in the conceptual operations. Fixed UInt16BE encoding, empty byte input, consumed0. Check site always literal0. Use dependent stored values and the stated order. Identical input/output and errors for every track.'
    save('AUTHORING-DOCS.json',dict(common=common,
        A='submit_candidate({source:Python source}) defines compute(v), where v is a validated argument dict. Standard library allowed. Provided checked add(a,b,step), check(predicate,code,step), Rejection(code,stage,step=None). Host validation and final encoding are shared noncentral plumbing. Author all central behavior. No imports from project or other tracks. run_case({args:object}) executes current candidate. Can resubmit bounded repairs.',
        B='submit_candidate({intent:{inputs:[names],statements:[{kind:"assign",name:identifier,expression:Python_expression} OR {kind:"check",expression:Python_expression,code:string,step:integer}],result:Python_expression}}). Generator binds names from validated v, emits ordered assignments/check calls then return expression. Python expressions may use checked add(a,b,step); standard Python comparisons. No Lykoi semantic validation, type graphs or lowering. run_case executes generated Python. Can resubmit repairs.',
        C='Use existing declare_input, apply_operation, define_result, validate_candidate tools. Original descriptions/schemas and fixed backend unchanged. Expressions $input/$alias or [add|le|eq,operand,operand], exact dependencies enumerate each referenced name once, values immutable. Inline Bool expression in check is permitted; site0. Target Int64. No opaque Python for central behavior. run_case executes sealed artifact; reset_candidate starts a new construction after a failed candidate if needed. At most4 complete attempts.' ))

def exposure(track):
    ts=h.definitions() if track=='C' else [dict(name='submit_candidate',description='Compile and retain the complete candidate; syntax feedback only, no hidden acceptance results.',inputSchema=dict(type='object',properties={'source':dict(type='string')} if track=='A' else {'intent':dict(type='object')},required=['source' if track=='A' else 'intent'],additionalProperties=False))]
    ts+= [dict(name='run_case',description='Run a self-selected development input against current candidate and return the observable result.',inputSchema=dict(type='object',properties=dict(args=dict(type='object')),required=['args'],additionalProperties=False))]
    if track=='C':
        ts.append(dict(name='reset_candidate',description='Discard current construction session and begin another bounded complete attempt; previous attempts remain recorded.',inputSchema=dict(type='object',properties={},additionalProperties=False)))
    return ts

def candidate_python(track,args):
    source=args['source'] if track=='A' else runtime.generate(args['intent'])
    scope=dict(add=runtime.add,check=runtime.check,Rejection=runtime.Rejection)
    begin=time.perf_counter()
    exec(compile(source,'<R630-candidate>','exec'),scope)
    assert callable(scope.get('compute')),'compute(v) required'
    return source,scope['compute'],time.perf_counter()-begin

def bridge(run):
    verify()
    track=run.split('-')[1]
    task=next(t for t in read('TASKS.json')['tasks'] if t['id']==run.split('-')[0])
    modified=run.endswith('-M')
    signature=task.get('mod_signature',task['signature']) if modified else task['signature']
    s=tools.Session(['value','check','compose'])
    fn=None
    complete=None
    count=attempts=0
    for line in sys.stdin:
        request=json.loads(line)
        if 'id' not in request: continue
        begin=time.perf_counter()
        record=dict(timestamp=h.now(),request=request)
        try:
            method=request['method']
            if method=='initialize':
                result=dict(protocolVersion=request['params']['protocolVersion'],capabilities={'tools':{}},serverInfo=dict(name='R630-'+track,version='1'))
            elif method=='tools/list': result=dict(tools=exposure(track))
            elif method=='ping': result={}
            elif method=='tools/call':
                count+=1
                p=request['params']; name,args=p['name'],p.get('arguments',{})
                if count>32: raise ValueError('32 development tool-call budget exhausted')
                if name=='run_case':
                    if track=='C':
                        assert complete,'validate_candidate required'
                        output,t=norm(complete,args['args'])
                    else:
                        assert fn,'submit_candidate required'
                        output=runtime.execute(fn,args['args'],signature)
                    feedback=dict(ok=True,observation=output)
                elif name=='submit_candidate' and track in ('A','B'):
                    attempts+=1
                    assert attempts<=4,'four candidate attempts maximum'
                    save(run+'/ATTEMPT-'+str(attempts)+'.json',args)
                    source,fn,seconds=candidate_python(track,args)
                    complete=args
                    save(run+'/COMPILED-'+str(attempts)+'.json',dict(source=source,compilation_seconds=seconds))
                    feedback=dict(ok=True,compiled=True,attempt=attempts)
                elif name=='reset_candidate' and track=='C':
                    attempts+=1
                    assert attempts<4,'four candidate attempts maximum'
                    s=tools.Session(['value','check','compose']); complete=None
                    feedback=dict(ok=True,reset=True)
                elif track=='C':
                    dispatch=s.dispatch({'function':dict(name=name,arguments=args)})
                    record['dispatch']=dispatch
                    feedback=dispatch['response']
                    if s.completed and complete is None:
                        complete=s.completed['artifact']
                        save(run+'/ARTIFACT-'+str(attempts+1)+'.json',complete)
                        save(run+'/PACKET-'+str(attempts+1)+'.json',s.packet)
                else: raise ValueError('unknown tool')
                if complete is not None:
                    # Current selection is maintained in memory; final exported once on shutdown.
                    record['complete']=complete
                result=dict(content=[dict(type='text',text=json.dumps(feedback))],structuredContent=feedback,isError=feedback.get('ok') is False)
            else: raise ValueError('unsupported method')
            response=dict(jsonrpc='2.0',id=request['id'],result=result)
        except Exception as exc:
            feedback=dict(ok=False,error=dict(code='DEVELOPMENT',detail=str(exc)))
            response=dict(jsonrpc='2.0',id=request['id'],result=dict(content=[dict(type='text',text=json.dumps(feedback))],structuredContent=feedback,isError=True))
        record.update(response=response,seconds=time.perf_counter()-begin)
        with (HERE/run/'MCP.jsonl').open('a',encoding='utf-8') as f: f.write(json.dumps(record)+'\n')
        print(json.dumps(response),flush=True)

def author(run):
    verify()
    assert not (HERE/run).exists()
    (HERE/run).mkdir()
    track=run.split('-')[1]
    task=next(t for t in read('TASKS.json')['tasks'] if t['id']==run.split('-')[0])
    modified=run.endswith('-M')
    doc=read('AUTHORING-DOCS.json')
    prompt='R6.30 bounded software development.\n'+task['requirement']+'\nSignature: '+json.dumps(task['signature'])+'\n'+doc['common']+'\n'+doc[track]
    if modified:
        assert (HERE/'BASE-COMPLETE.json').exists()
        original=read(run[:-2]+'/FINAL-CANDIDATE.json')
        prompt+='\nModification disclosed now: '+task['modification']+'\nBuild only the added endpoint; original deployed endpoint is retained byte-for-byte. The new artifact need only implement the added endpoint. Same-track original candidate: '+json.dumps(original)
        prompt+='\nExtended signature: '+json.dumps(task.get('mod_signature',task['signature']))
    prompt+='\nBudget:240s wall,32 tool calls,4 complete candidate attempts,33 completion steps,4096 output tokens/response. Use run_case for ordinary testing/debugging. Stop after constructing a candidate you consider ready. No other tools, filesystem access, repository imports or delegation. You have not been given acceptance cases or other-track implementations.'
    cfg=h.config()
    permission={'*':'deny','work_*':'allow'}
    cfg['permission']=permission;cfg['tools']={'*':False,'work_*':True}
    cfg['mcp']={'work':dict(type='local',command=[sys.executable,str(HERE/'experiment.py'),'bridge',run],enabled=True),**{k:dict(enabled=False) for k in ('lykoi','codegraphcontext','shadcn','pixellab')}}
    cfg['agent']={'r630':dict(mode='primary',model=h.MODEL,variant='high',steps=33,options=dict(maxOutputTokens=4096),permission=permission,
        prompt='Act as an R6.30 author for track '+track+'. Follow the supplied functional requirements and tool documentation. Only work MCP tools are enabled. Do not access other tasks/tracks or delegate.')}
    save(run+'/REQUEST.json',dict(timestamp=h.now(),prompt=prompt,config=cfg,model=h.MODEL,reasoning_requested='high',effective_reasoning='UNATTESTED',tools=exposure(track)))
    env=os.environ.copy()
    env.update(OPENCODE_CONFIG_CONTENT=json.dumps(cfg),OPENCODE_DISABLE_PROJECT_CONFIG='1',OPENCODE_DISABLE_EXTERNAL_SKILLS='1',OPENCODE_DISABLE_CLAUDE_CODE_SKILLS='1',OPENCODE_PURE='1')
    assert h.TEMP.is_dir()
    begin=time.perf_counter()
    proc=subprocess.Popen([str(h.EXE),'run','--pure','--model',h.MODEL,'--variant','high','--agent','r630','--format','json','--title','R6.30 '+run],cwd=h.TEMP,env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    try:
        out,err=proc.communicate(prompt.encode(),timeout=240);termination='COMPLETED'
    except subprocess.TimeoutExpired:
        subprocess.run(['taskkill','/PID',str(proc.pid),'/T','/F'],capture_output=True)
        out,err=proc.communicate();termination='TIMEOUT'
    (HERE/run/'EVENTS.jsonl').write_bytes(out);(HERE/run/'STDERR.txt').write_bytes(err)
    save(run+'/PROCESS.json',dict(timestamp=h.now(),returncode=proc.returncode,termination=termination,wall_seconds=time.perf_counter()-begin,author_process_terminated=proc.poll() is not None))
    events=[json.loads(l) for l in out.decode().splitlines() if l.startswith('{')]
    sessions={e['sessionID'] for e in events if 'sessionID' in e}
    if len(sessions)==1:
        exp=subprocess.run([str(h.EXE),'export',next(iter(sessions))],capture_output=True,encoding='utf-8',timeout=30)
        data=json.loads(exp.stdout)
        save(run+'/SESSION.json',data)
        users=[p['text'] for m in data['messages'] if m['info']['role']=='user' for p in m['parts'] if p['type']=='text']
        save(run+'/DELIVERY.json',dict(session=next(iter(sessions)),matches_requested=users==[prompt],fresh_process=True,hidden_context_exclusion='UNATTESTED'))
    rows=[json.loads(l) for l in (HERE/run/'MCP.jsonl').read_text().splitlines()] if (HERE/run/'MCP.jsonl').exists() else []
    complete=[r['complete'] for r in rows if 'complete' in r]
    if complete: save(run+'/FINAL-CANDIDATE.json',complete[-1])
    print(run,termination,'candidate',bool(complete),flush=True)

def run_all():
    for run in read('FREEZE.json')['order']: author(run)
    save('BASE-COMPLETE.json',dict(timestamp=h.now(),all_processes_terminated=True,
        records={run:read(run+'/PROCESS.json') for run in read('FREEZE.json')['order']},modifications_disclosed=False))
    save('MODIFICATION-DISCLOSURE.json',dict(timestamp=h.now(),base_complete_sha256=digest(HERE/'BASE-COMPLETE.json'),
        withholding='Explicit prompts contain only base requirements before this timestamp. Processes lack enabled file/retrieval tools. Hidden-context/file isolation is unattested: CONTAMINATED_UNENFORCED.',
        tasks_sha256=digest(HERE/'TASKS.json')))
    for run in read('FREEZE.json')['modification_order']: author(run+'-M')

if __name__=='__main__':
    actions=dict(baseline=baseline,correction=correction,selection=selection,qualification=qualification,docs=docs,freeze=freeze,run=run_all)
    if sys.argv[1]=='bridge': bridge(sys.argv[2])
    else: actions[sys.argv[1]]()
