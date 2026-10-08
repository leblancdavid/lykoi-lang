"""Supervised unchanged-VM construction measurements; write-once results."""
import collections
import copy
import gc
import hashlib
import itertools
import json
import os
import platform
import statistics
import subprocess
import sys
import time
import tracemalloc

from audit import HERE, ROOT, VM, load, now, save, sha, verify, verify_map
from boundary import pack
sys.path.insert(0,str(VM))
import interpreter as vm


def serial(value):
    if isinstance(value, bytes):
        return {'hex':value.hex()}
    if isinstance(value, dict):
        return {key:serial(val) for key,val in value.items()}
    if isinstance(value, (list,tuple)):
        return [serial(val) for val in value]
    return value


def native(plan, data, limits=None):
    """Exact execute nontext byte path after validation, using unchanged VM methods."""
    limits = dict(vm.DEFAULT_LIMITS, **(limits or {}))
    m = vm.Machine(data, limits, plan['rules'])
    try:
        if len(data)>limits['input']:
            m.fail('INPUT_LIMIT',limits['input'],'limit')
        result = m.run(plan['decode'],{})
        m.run(plan['encode'],{'root':result})
        return dict(status='success',value=vm.plain(result),provenance=vm.provenance(result),
            consumed=m.i,work=m.work,output=bytes(m.out),output_spans=m.spans)
    except vm.Rejection as exc:
        if exc.error['stage']=='encode':
            exc.error['offset']=None
        return dict(status='reject',error=exc.error,work=m.work)
    except (TypeError,KeyError,AttributeError,IndexError):
        return dict(status='reject',error=dict(code='TYPE',offset=m.i,node=m.node,
            stage='typing',path=None),work=m.work)


def structure(plan):
    nodes=[]; expressions=[]; prefixes=[]; calls=[]
    structural_depth=0; expression_depth=0
    def visit(value, depth=0, edepth=0):
        nonlocal structural_depth,expression_depth
        if isinstance(value,dict):
            if 'op' in value:
                depth+=1; structural_depth=max(structural_depth,depth);nodes.append(value)
                if value['op']=='call':
                    calls.append(value['rule'])
                if value['op']=='choice':
                    prefixes.extend(p for branch in value['branches'] for p in branch['prefixes'])
            elif len(value)==1 and next(iter(value)) in vm.EXPRS:
                edepth+=1;expression_depth=max(expression_depth,edepth)
                expressions.append(json.dumps(value,sort_keys=True,separators=(',',':')))
            for child in value.values():
                visit(child,depth,edepth)
        elif isinstance(value,list):
            for child in value:
                visit(child,depth,edepth)
    visit(plan)
    repeated=collections.Counter(expressions)
    def expanded_depth(n, depth=1):
        ds=[depth]
        if n['op']=='call':
            ds.append(expanded_depth(plan['rules'][n['rule']],depth+1))
        elif n['op']=='seq':
            ds.extend(expanded_depth(s['node'],depth+1) for s in n['steps'])
        elif n['op']=='choice':
            ds.extend(expanded_depth(b['node'],depth+1) for b in n['branches'])
        elif n['op']=='dispatch':
            ds.extend(expanded_depth(b,depth+1) for b in n['branches'].values())
        elif 'body' in n:
            ds.append(expanded_depth(n['body'],depth+1))
        return max(ds)
    return dict(structural_nodes=len(nodes),expression_occurrences=len(expressions),
        structural_tree_depth=structural_depth,expanded_runtime_node_depth=max(
            expanded_depth(plan['decode']),expanded_depth(plan['encode'])),
        expression_depth=expression_depth,selector_prefixes=len(prefixes),
        selector_bytes=sum(map(len,prefixes)),rule_calls=dict(collections.Counter(calls)),
        repeated_expression_shapes={k:v for k,v in repeated.items() if v>1},
        repeated_expressions_are='serialized duplicates, not memoized; refs reuse bound values',
        canonical_json_bytes=len(json.dumps(plan,sort_keys=True,separators=(',',':')).encode()))


def validation(plan):
    times=[]; statuses=[]
    for _ in range(5):
        begin=time.perf_counter()
        try:
            statuses.append(dict(status='VALID',nodes=vm.validate(plan)))
        except Exception as exc:
            statuses.append(dict(status='REJECT',exception=type(exc).__name__,detail=str(exc)))
        times.append(time.perf_counter()-begin)
    counts=collections.Counter()
    def profile(frame,event,arg):
        if event=='call' and frame.f_code.co_filename==vm.__file__:
            if frame.f_code.co_name in ('walk','expression','prefixes'):
                counts[frame.f_code.co_name]+=1
    def trace(frame,event,arg):
        if frame.f_code.co_filename==vm.__file__ and frame.f_code.co_name=='prefixes':
            if event=='line' and frame.f_lineno==123:
                counts['prefix_pair_comparisons']+=1
            return trace
        return None
    sys.setprofile(profile);sys.settrace(trace)
    try:
        vm.validate(plan)
    except Exception:
        pass
    finally:
        sys.setprofile(None);sys.settrace(None)
    return dict(wall_seconds=times,median_seconds=statistics.median(times),
        outcomes=statuses,traversal_counts=dict(counts),
        determinism=all(s==statuses[0] for s in statuses))


def oracle(name,args):
    if name=='xor8':
        return args[0]^args[1]
    if name=='addmod8':
        return (args[0]+args[1])%256
    return args[0].bit_count()%2


def negative(plan,name):
    arity=1 if name=='parity8' else 2
    records=[]
    def note(identity, actual, passed):
        records.append(dict(id=identity,actual=serial(actual),passed=passed))
        assert passed, identity
    # Boundary cases never compute the relation. Repeat deterministic rejections.
    cases=[]
    for count in range(arity):
        cases.append(([0]*count,dict(code='MISSING',index=count)))
    cases.append(([0]*(arity+1),dict(code='ARITY',index=arity)))
    for index in range(arity):
        for value in [-1,-256,256,65535,True,False,1.0,'1',None,[],{}]:
            args=[0]*arity;args[index]=value
            cases.append((args,dict(code='RANGE' if type(value)is int else 'TYPE',index=index)))
    if arity==2:
        cases.extend([([-1,'1'],dict(code='RANGE',index=0)),(['1',-1],dict(code='TYPE',index=0))])
    for index,(args,expected) in enumerate(cases):
        observed=[pack(args,arity) for _ in range(3)]
        note('boundary-'+str(index),dict(arguments=args,result=observed[0]),
            all(x==(None,expected) for x in observed))
    for length in range(arity):
        observed=[native(plan,bytes(length)) for _ in range(3)]
        note('truncated-'+str(length),observed[0],all(x==observed[0] for x in observed)
            and observed[0]['error']['code']=='TRUNCATED')
    observed=[native(plan,bytes(arity+1)) for _ in range(3)]
    note('trailing',observed[0],all(x==observed[0] for x in observed) and observed[0]['error']['code']=='TRAILING')
    for value in [None,0,'',[],bytearray(arity)]:
        observed=[vm.execute(plan,value) for _ in range(3)]
        note('native-input-type',observed[0],all(x==observed[0] for x in observed)
            and observed[0]==dict(status='plan_reject',error={'code':'INPUT_TYPE'},work=0))
    representatives=[(0,),(255,),(85,)] if arity==1 else [(0,0),(255,255),(85,170)]
    for args in representatives:
        data=bytes(args);result=native(plan,data)
        cutoff_hash=hashlib.sha256()
        for cutoff in range(result['work']):
            observations=[native(plan,data,{'work':cutoff}) for _ in range(3)]
            assert all(x==observations[0] for x in observations)
            assert observations[0]['work']==cutoff and observations[0]['error']['code']=='WORK_LIMIT'
            cutoff_hash.update(json.dumps(serial(observations[0]),sort_keys=True).encode())
        note('work-cutoffs',dict(input=list(args),cutoffs=result['work'],repeats=3,
             digest=cutoff_hash.hexdigest()),True)
        for limits,code in [({'input':arity-1},'INPUT_LIMIT'),({'output':0},'OUTPUT_LIMIT'),({'depth':1},'DEPTH_LIMIT')]:
            observed=[native(plan,data,limits) for _ in range(3)]
            note('resource-'+code,observed[0],all(x==observed[0] for x in observed)
                and observed[0]['error']['code']==code)
        public=vm.execute(plan,data,{'work':result['work']-1})
        note('public-cutoff-crosscheck',public,public==native(plan,data,{'work':result['work']-1}))
    invalid=vm.execute(plan,bytes(arity),{'work':100001})
    note('limit-vector',invalid,invalid==dict(status='plan_reject',error={'code':'LIMIT_VECTOR'},work=0))
    bad=[]
    base=copy.deepcopy(plan);base['decode']['op']='xor';bad.append(('unknown-op',base))
    base=copy.deepcopy(plan);base['encode']['id']=base['decode']['id'];bad.append(('duplicate-id',base))
    base=copy.deepcopy(plan);base['encode']['expr']={'ref':'missing'};bad.append(('undeclared-ref',base))
    base=copy.deepcopy(plan);base['rules']['cycle']=dict(id='cycle',op='call',rule='cycle');bad.append(('cycle',base))
    base=copy.deepcopy(plan);base['decode']=dict(id='overlap',op='choice',code='BAD',branches=[
        dict(prefixes=[[0],[0]],node=dict(id='v',op='value',expr={'const':0}))]);bad.append(('overlap',base))
    base=copy.deepcopy(plan)
    node=dict(id='deepvalue',op='value',expr={'const':0})
    for i in range(17):
        node=dict(id=f'deep{i}',op='seq',steps=[dict(node=node)],result={'const':0})
    base['decode']=node;bad.append(('depth',base))
    for identity,base in bad:
        observations=[vm.execute(base,b'') for _ in range(3)]
        note('malformed-'+identity,observations[0],all(x==observations[0] for x in observations)
             and observations[0]==dict(status='plan_reject',error={'code':'PLAN'},work=0))
    return records


def acceptance(plan,name,deadline):
    vm.validate(plan)
    arity=1 if name=='parity8' else 2
    passes=[]
    total=256**arity
    for run in range(3):
        begin=time.perf_counter();digest=hashlib.sha256();hist=collections.Counter();covered=0;failed=[]
        for args in itertools.product(range(256),repeat=arity):
            data,error=pack(args,arity);assert error is None
            expected=oracle(name,args);actual=native(plan,data)
            passed=(actual['status']=='success' and type(actual['value'])is int
                and actual['value']==expected and actual['output']==bytes([expected])
                and actual['consumed']==arity)
            if not passed:
                failed.append(dict(input=list(args),expected=expected,actual=serial(actual)))
            hist[actual['work']]+=1;covered+=1
            digest.update(json.dumps(dict(input=list(args),actual=serial(actual)),sort_keys=True,separators=(',',':')).encode()+b'\n')
            if covered%4096==0:
                checkpoint=dict(utc=now(),relation=name,run=run,covered=covered,total=total,
                    failures=failed,seconds=time.perf_counter()-begin,digest=digest.hexdigest())
                with (HERE/(name+'-progress.jsonl')).open('a',encoding='utf-8') as out:
                    out.write(json.dumps(checkpoint)+'\n')
            if time.perf_counter()>deadline:
                break
        passes.append(dict(covered=covered,total=total,failures=failed,seconds=time.perf_counter()-begin,
            digest=digest.hexdigest(),work_min=min(hist),work_max=max(hist),
            work_sum=sum(k*v for k,v in hist.items()),work_histogram=dict(sorted(hist.items()))))
        if covered!=total:
            return dict(status='PARTIAL',passes=passes)
    grid=range(256) if arity==1 else [0,1,15,16,127,128,254,255]
    begin=time.perf_counter();crosschecked=0
    for args in itertools.product(grid,repeat=arity):
        assert vm.execute(plan,bytes(args))==native(plan,bytes(args))
        crosschecked+=1
    public_seconds=time.perf_counter()-begin
    negatives=negative(plan,name)
    tracemalloc.start();begin=time.perf_counter()
    for i in range(256):
        args=(i,) if arity==1 else (i,255-i)
        vm.execute(plan,bytes(args))
    current,peak=tracemalloc.get_traced_memory();tracemalloc.stop()
    return dict(status='COMPLETE',passes=passes,
        deterministic=len({p['digest'] for p in passes})==1,
        public_api_crosscheck=dict(cases=crosschecked,seconds=public_seconds),
        negative_observations=negatives,
        memory=dict(method='tracemalloc public execute 256 cases; separate from timing',
            peak_bytes=peak,current_bytes=current,seconds=time.perf_counter()-begin,
            excludes='process RSS and native allocator; not exhaustive peak'))


def worker(kind,name):
    verify();verify_map(HERE,load(HERE/'RUN-FREEZE.json')['files'])
    path=HERE/(name+'.plan.json');plan=load(path)
    if kind=='structure':
        measured=structure(plan);measured['published_json_bytes']=path.stat().st_size
        measured['validation']=validation(plan)
        save(HERE/(name+'-structure.json'),measured)
        print(json.dumps(dict(status='RECORDED',file=name+'-structure.json')))
    else:
        result=acceptance(plan,name,time.perf_counter()+170)
        save(HERE/(name+'-acceptance.json'),result)
        print(json.dumps(dict(status=result['status'],file=name+'-acceptance.json')))


def supervise():
    verify();verify_map(HERE,load(HERE/'SPEC-FREEZE.json')['files'])
    files={p.name:sha(p) for p in HERE.glob('*.plan.json')}
    files.update({name:sha(HERE/name) for name in ['build.py','run.py','boundary.py','CONSTRUCTION.json']})
    save(HERE/'RUN-FREEZE.json',dict(utc=now(),files=files,spec_freeze_sha256=sha(HERE/'SPEC-FREEZE.json')))
    start=time.perf_counter();deadline=start+900;records=[]
    save(HERE/'RUN-START.json',dict(utc=now(),freeze_sha256=sha(HERE/'RUN-FREEZE.json'),
        python=sys.version,executable=sys.executable,platform=platform.platform(),
        processor=platform.processor(),machine=platform.machine(),logical_cpus=os.cpu_count(),
        clock=vars(time.get_clock_info('perf_counter')),gc_enabled=gc.isenabled(),gc_threshold=gc.get_threshold(),
        process_environment='same interpreter, serial fresh subprocess per measurement; no affinity or idle-host guarantee'))
    jobs=[('structure',name) for name in ['naive-xor8','xor8','addmod8','parity8','expression-limit','node-limit']]
    jobs += [('acceptance',name) for name in ['xor8','addmod8','parity8']]
    for kind,name in jobs:
        begin=time.perf_counter();remaining=deadline-begin
        if remaining<=0:
            records.append(dict(kind=kind,name=name,status='SESSION_TIMEOUT'));continue
        timeout=min(10 if name=='naive-xor8' else 180,remaining)
        command=[sys.executable,'-B',str(HERE/'run.py'),'worker',kind,name]
        record=dict(kind=kind,name=name,start_utc=now(),timeout_seconds=timeout,command=command)
        try:
            result=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,timeout=timeout)
            record.update(status='COMPLETED' if result.returncode==0 else 'EXECUTION_ERROR',
                returncode=result.returncode,stdout=result.stdout,stderr=result.stderr)
        except subprocess.TimeoutExpired as exc:
            record.update(status='PROCESS_TIMEOUT',stdout=serial(exc.stdout),stderr=serial(exc.stderr))
        record.update(completion_utc=now(),seconds=time.perf_counter()-begin)
        records.append(record)
        print(kind,name,record['status'],round(record['seconds'],3),flush=True)
    verify()
    save(HERE/'RUN-RESULTS.json',dict(completion_utc=now(),seconds=time.perf_counter()-start,observations=records))


if __name__=='__main__':
    if sys.argv[1]=='worker':
        worker(*sys.argv[2:])
    else:
        supervise()
