"""Frozen-observation scoring of immutable submissions, standard library only."""
import ast
import collections
import importlib.util
import json
import statistics
import subprocess
import sys
import time
from evidence import HERE, ROOT, now, sha, load, save, verify, export

sys.path.insert(0, str(ROOT/'experiments/semantic_interpreter'))
import interpreter as vm

BASE_SESSIONS = {'A/13':'ses_ee254cb2affeVpB6ryUFoky559',
    'C/24':'ses_ee254cb1fffem0rYpnRNQrlC29',
    'C/13':'ses_ee24fc072ffeVDGuuGO6i3owae',
    'A/24':'ses_ee24fc06affeRcJDJTvRm3qG73'}


def equal(a,b):
    if type(a) is not type(b):
        return False
    if isinstance(a,dict):
        return a.keys()==b.keys() and all(equal(a[k],b[k]) for k in a)
    if isinstance(a,list):
        return len(a)==len(b) and all(equal(x,y) for x,y in zip(a,b))
    return a==b


def candidate(track,phase,task):
    return HERE/track/phase/(task+('.py' if track=='A' else '.plan.json'))


def freeze(phase):
    names=[p for track in ('A','C') for p in sorted((HERE/track/phase).glob('*')) if p.is_file()]
    if phase=='base':
        names += [p for track in ('A','C') for p in sorted((HERE/track/'first').glob('*')) if p.is_file()]
        names += [p for track in ('A','C') for p in sorted((HERE/track).glob('AUTHORING-*.json'))]
        names += list((HERE/'C').glob('authoring-*.py'))
    else:
        names += [p for track in ('A','C') for p in sorted((HERE/track/'mod-first').glob('*')) if p.is_file()]
        names += [HERE/track/'AUTHORING-MOD.json' for track in ('A','C')]
        names += list((HERE/'C').glob('MOD-SELFTEST-*.json'))
        names += [HERE/'C'/'build_mod.py']
    save(HERE/f'{phase.upper()}-FREEZE.json',dict(utc=now(),files={
        p.relative_to(ROOT).as_posix():sha(p) for p in names},
        note='Handoff immutable before scored acceptance and staged reveal'))


def observe_c(plan,data):
    if len(data)>64:
        return dict(status='reject',code='INPUT_LIMIT',offset=64),None
    r=vm.execute(plan,data)
    if r['status']=='success':
        return dict(status='success',value=r['value'],output=r['output'].hex()),r['work']
    if r['status']=='reject':
        return dict(status='reject',code=r['error']['code'],offset=r['error']['offset']),r['work']
    return r,r.get('work')


def measure(plan):
    counts=collections.Counter()
    def profile(frame,event,arg):
        if event=='call' and frame.f_code.co_filename==vm.__file__ and frame.f_code.co_name in ('walk','expression','prefixes'):
            counts[frame.f_code.co_name]+=1
    def trace(frame,event,arg):
        if frame.f_code.co_filename==vm.__file__ and frame.f_code.co_name=='prefixes':
            if event=='line' and frame.f_lineno==123:
                counts['selector_pair_comparisons']+=1
            return trace
        return None
    start=time.perf_counter()
    nodes=vm.validate(plan)
    times=[time.perf_counter()-start]
    for _ in range(4):
        start=time.perf_counter()
        vm.validate(plan)
        times.append(time.perf_counter()-start)
    sys.setprofile(profile)
    sys.settrace(trace)
    try:
        vm.validate(plan)
    finally:
        sys.setprofile(None)
        sys.settrace(None)
    return dict(nodes=nodes,canonical_bytes=len(json.dumps(plan,sort_keys=True,separators=(',',':')).encode()),
        validation_seconds=times,median_validation_seconds=statistics.median(times),
        validation_traversal=dict(counts),profiling_not_in_timed_runs=True)


def worker(track,phase,task):
    path=candidate(track,phase,task)
    out=dict(utc=now(),track=track,phase=phase,task=task,artifact_sha256=sha(path),
             source_bytes=path.stat().st_size,observations=[])
    if track=='A':
        source=path.read_text(encoding='utf-8')
        tree=ast.parse(source)
        out['python_structure']={name:sum(isinstance(n,cls) for n in ast.walk(tree))
            for name,cls in [('functions',ast.FunctionDef),('if',ast.If),('for',ast.For),
                ('while',ast.While),('comprehensions',ast.comprehension)]}
        spec=importlib.util.spec_from_file_location('candidate',path)
        module=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        def observe(data):
            return module.solve(data),None
    else:
        plan=load(path)
        try:
            out['vm_structure']=measure(plan)
        except vm.PlanError as e:
            out['classification']='INVALID_SEMANTIC_PLAN'
            out['error']=str(e)
            print(json.dumps(out))
            return
        def observe(data):
            return observe_c(plan,data)
    cases=[('original',r) for r in load(HERE/'acceptance'/f'{task}.json')]
    if phase=='modified':
        cases += [('new',r) for r in load(HERE/'sealed'/('M'+task[1:]+'.json'))]
    start=time.perf_counter()
    for scope,row in cases:
        actual=[]; work=[]; seconds=[]
        for _ in range(3):
            before=time.perf_counter()
            try:
                a,w=observe(bytes.fromhex(row['hex']))
            except Exception as e:
                a=dict(exception=type(e).__name__,message=str(e));w=None
            seconds.append(time.perf_counter()-before)
            actual.append(a);work.append(w)
        out['observations'].append(dict(id=row['id'],scope=scope,hex=row['hex'],expected=row['expected'],
            actual=actual,work=work,seconds=seconds,passed=all(equal(a,row['expected']) for a in actual),
            deterministic=equal(actual[0],actual[1]) and equal(actual[0],actual[2]) and work[0]==work[1]==work[2]))
    out['scoring_seconds']=time.perf_counter()-start
    out['passed']=sum(r['passed'] for r in out['observations'])
    out['total']=len(cases)
    out['accepted']=out['passed']==out['total']
    out['classification']='ACCEPTED' if out['accepted'] else (
        'CONVENTIONAL_IMPLEMENTATION_ERROR' if track=='A' else 'AI_AUTHORING_FAILURE')
    out['scope_counts']={scope:dict(total=sum(r['scope']==scope for r in out['observations']),
        passed=sum(r['scope']==scope and r['passed'] for r in out['observations'])) for scope in ('original','new')}
    print(json.dumps(out))


def score(phase):
    verify(load(HERE/f'{phase.upper()}-FREEZE.json')['files'])
    order=[('A','T1'),('C','T2'),('A','T3'),('C','T4'),('C','T1'),('A','T2'),('C','T3'),('A','T4')]
    if phase=='modified':
        order=[('C','T1'),('C','T2'),('A','T1'),('A','T2')]
    results=[]
    for track,task in order:
        start=time.perf_counter()
        try:
            p=subprocess.run([sys.executable,'-B',__file__,'worker',track,phase,task],
                capture_output=True,text=True,timeout=30)
            row=dict(track=track,task=task,seconds=time.perf_counter()-start,returncode=p.returncode)
            if p.returncode==0:
                result=json.loads(p.stdout)
                save(HERE/'results'/f'{track}-{phase}-{task}.json',result)
                row.update({k:result.get(k) for k in ('accepted','passed','total','classification','scope_counts')})
            else:
                row.update(classification='INFRASTRUCTURE_FAILURE',stderr=p.stderr,stdout=p.stdout)
        except subprocess.TimeoutExpired:
            row=dict(track=track,task=task,seconds=time.perf_counter()-start,
                classification='EXECUTION_TIMEOUT',accepted=False)
        results.append(row)
    save(HERE/f'{phase.upper()}-RESULTS.json',dict(utc=now(),results=results))
    print(json.dumps(results,indent=2))


def telemetry(sessions,name):
    rows=[]
    for scope,session in sessions.items():
        row=export(session)
        row['scope']=scope
        m=row['metadata']
        tokens=[x['tokens'] for x in m if 'tokens' in x]
        row['actual_usage']=None if not tokens else dict(
            input=sum(t.get('input',0) for t in tokens),output=sum(t.get('output',0) for t in tokens),
            reasoning=sum(t.get('reasoning',0) for t in tokens),
            cache_read=sum(t.get('cache',{}).get('read',0) for t in tokens),
            cache_write=sum(t.get('cache',{}).get('write',0) for t in tokens))
        row['model_calls']=len(tokens) if tokens else None
        starts=[x['time']['created'] for x in m if x.get('time',{}).get('created')]
        ends=[x['time']['completed'] for x in m if x.get('time',{}).get('completed')]
        row['development_wall_seconds']=(max(ends)-min(starts))/1000 if starts and ends else None
        tools=[t for x in m for t in x.get('tools',[])]
        row['tool_calls']=len(tools)
        row['tool_execution_seconds']=sum((t['time']['end']-t['time']['start'])/1000
            for t in tools if t.get('time') and 'start' in t['time'] and 'end' in t['time'])
        row['budget_within_600_seconds']=row['development_wall_seconds'] is not None and row['development_wall_seconds']<=600
        row['budget_within_20_tools']=len(tools)<=20
        rows.append(row)
    save(HERE/name,dict(utc=now(),sessions=rows,cost_note='Reported zero cost does not establish actual billing; API cost null',
        tokens_note='Actual exported per-call fields; input excludes separately reported cache; no source-length estimates',
        attribution='Task-pair sessions; no task-level token allocation',preparation_usage=None,
        reasoning_configuration_attested=False))
    print(json.dumps([{k:r[k] for k in ('scope','actual_usage','model_calls','development_wall_seconds',
        'tool_calls','budget_within_600_seconds','budget_within_20_tools')} for r in rows],indent=2))


if __name__=='__main__':
    command=sys.argv[1]
    if command=='worker':
        worker(*sys.argv[2:])
    elif command=='freeze':
        freeze(sys.argv[2])
    elif command=='score':
        score(sys.argv[2])
    elif command=='telemetry-base':
        telemetry(BASE_SESSIONS,'BASE-TELEMETRY.json')
    elif command=='reveal':
        verify(load(HERE/'BASE-FREEZE.json')['files'])
        for name,digest in load(HERE/'MODIFICATION-SEAL.json')['files'].items():
            assert sha(HERE/name)==digest
        save(HERE/'MODIFICATION-REVEAL.json',dict(utc=now(),base_freeze_sha256=sha(HERE/'BASE-FREEZE.json'),
            seal_sha256=sha(HERE/'MODIFICATION-SEAL.json'),all_original_submissions_frozen=True,
            original_scoring_sha256=sha(HERE/'BASE-RESULTS.json'),
            staged_access_enforcement='cooperative; base authors report no sealed access; independently unattested'))
        print('Seals verified; modifications released after base freeze')
    elif command=='telemetry-modified':
        telemetry({'C/modification':'ses_ee247d6e2ffeQyv42rmZd6R79I',
                   'A/modification':'ses_ee247d6d8ffewKzmKG6WJPa5SZ'},'MODIFIED-TELEMETRY.json')
