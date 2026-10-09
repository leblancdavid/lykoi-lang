"""Frozen external evaluation and publication for the bounded R6.30 workflows."""
import json
from pathlib import Path
import subprocess
import sys
import time
import experiment as e

def candidate(run,path,cases,signature):
    begin=time.perf_counter()
    track=run.split('-')[1]
    value=e.read(path)
    fn=None
    compilation=0
    if track!='C':
        try:
            source,fn,compilation=e.candidate_python(track,value)
        except Exception as exc:
            return dict(passed=0,total=len(cases),full_acceptance=False,compiler_error=str(exc),records=[])
    rows=[]
    for case in cases:
        started=time.perf_counter()
        try:
            if track=='C':
                actual,times=e.norm(value,case['args'])
            else:
                actual=e.runtime.execute(fn,case['args'],signature)
                times={}
            passed=actual==case['expected']
            rows.append(dict(case=case,actual=actual,passed=passed,times=times,wall_seconds=time.perf_counter()-started))
        except Exception as exc:
            rows.append(dict(case=case,passed=False,runtime_error=type(exc).__name__+': '+str(exc),wall_seconds=time.perf_counter()-started))
    return dict(passed=sum(r['passed'] for r in rows),total=len(rows),full_acceptance=all(r['passed'] for r in rows),
        records=rows,compilation_seconds=compilation,evaluation_wall_seconds=time.perf_counter()-begin,candidate_sha256=e.digest(e.HERE/path))

def telemetry(run):
    rows=[json.loads(l) for l in (e.HERE/run/'MCP.jsonl').read_text().splitlines()] if (e.HERE/run/'MCP.jsonl').exists() else []
    calls=[r for r in rows if r['request']['method']=='tools/call']
    events=[json.loads(l) for l in (e.HERE/run/'EVENTS.jsonl').read_text().splitlines() if l.startswith('{')]
    steps=[x['part'] for x in events if x['type']=='step_finish']
    session=e.read(run+'/SESSION.json') if (e.HERE/run/'SESSION.json').exists() else None
    assistants=[m['info'] for m in session['messages'] if m['info']['role']=='assistant'] if session else []
    failed=[r for r in calls if r['response'].get('result',{}).get('isError')]
    model_match=bool(assistants) and all(m['providerID']=='openai' and m['modelID']=='gpt-6.1-sol' for m in assistants)
    delivery=e.read(run+'/DELIVERY.json') if (e.HERE/run/'DELIVERY.json').exists() else {}
    native=[x['part'] for x in events if x['type']=='tool_use']
    lineage=[]
    for r in calls:
        p=r['request']['params']
        matches=[x for x in native if x['tool']=='work_'+p['name'] and x['state'].get('input')==p['arguments']]
        lineage.append(bool(matches))
    return dict(run=run,model_verified=model_match,delivery_matches=delivery.get('matches_requested',False),
        model_calls=len(assistants),tool_calls=len(calls),tool_failures=len(failed),failures=failed,
        tool_argument_lineage_verified=all(lineage) and len(native)==len(calls),
        tokens={k:sum(x['tokens'][k] for x in steps) for k in ('input','output','reasoning','total')},
        cached_read=sum(x['tokens']['cache']['read'] for x in steps),cached_write=sum(x['tokens']['cache'].get('write',0) for x in steps),
        SDK_cost=sum(x['cost'] for x in steps),API_billing=None,effective_reasoning='UNATTESTED',pure_inference_seconds=None,
        session_wall_seconds=e.read(run+'/PROCESS.json')['wall_seconds'],
        assistant_message_elapsed_seconds=sum((m['time']['completed']-m['time']['created'])/1000 for m in assistants if 'completed' in m['time']),
        deterministic_dispatch_seconds=sum(r['seconds'] for r in calls),
        compilation_seconds=sum(e.read(p.relative_to(e.HERE).as_posix())['compilation_seconds'] for p in (e.HERE/run).glob('COMPILED-*.json')),
        semantic_validation_expansion_times=[r['dispatch']['response'] for r in calls if 'dispatch' in r and r['request']['params']['name']=='validate_candidate'],
        complete_candidate_attempts=len(list((e.HERE/run).glob('ATTEMPT-*.json'))) if run.split('-')[1]!='C' else 1+sum(r['request']['params']['name']=='reset_candidate' for r in calls),
        provider_errors=[x for x in events if x['type']=='error'],fresh_session=delivery.get('session'),
        hidden_context_exclusion='UNATTESTED',SDK_cost_is_billing=False)

def evaluate():
    e.verify()
    tasks=e.read('TASKS.json')['tasks']
    suites=e.read('ACCEPTANCE.json')
    results={};measurements={}
    for run in e.read('FREEZE.json')['order']+[r+'-M' for r in e.read('FREEZE.json')['modification_order']]:
        t=next(t for t in tasks if t['id']==run.split('-')[0])
        modified=run.endswith('-M')
        signature=t.get('mod_signature',t['signature']) if modified else t['signature']
        cases=suites['modified' if modified else 'base'][t['id']]
        measurements[run]=telemetry(run)
        assert e.read(run+'/PROCESS.json')['author_process_terminated']
        attempts=sorted((e.HERE/run).glob('ARTIFACT-*.json' if run.split('-')[1]=='C' else 'ATTEMPT-*.json'))
        final=run+'/FINAL-CANDIDATE.json'
        result=dict(status='NOT_REACHED',reason='No completed candidate')
        if (e.HERE/final).exists():
            result=dict(first=candidate(run,attempts[0].relative_to(e.HERE).as_posix(),cases,signature),final=candidate(run,final,cases,signature))
            if modified:
                base=run[:-2]
                result['original_regression']=candidate(base,base+'/FINAL-CANDIDATE.json',suites['base'][t['id']],t['signature'])
                result['original_artifact_preserved']=e.digest(e.HERE/(base+'/FINAL-CANDIDATE.json'))==results[base]['final']['candidate_sha256']
                result['regressions']=sum(old['passed'] and not new['passed'] for old,new in zip(results[base]['final']['records'],result['original_regression']['records']))
                result['withholding']='CONTAMINATED_UNENFORCED'
        results[run]=result
    sessions=[v['fresh_session'] for v in measurements.values()]
    protocol=all(v['model_verified'] and v['delivery_matches'] and v['tool_argument_lineage_verified'] and v['tool_calls']<=32 and v['complete_candidate_attempts']<=4 for v in measurements.values()) and len(set(sessions))==len(sessions)
    totals={}
    for track in 'ABC':
        rows=[v for k,v in measurements.items() if k.split('-')[1]==track]
        totals[track]={k:sum(v[k] for v in rows) for k in ('model_calls','tool_calls','tool_failures','cached_read','cached_write','session_wall_seconds','assistant_message_elapsed_seconds','deterministic_dispatch_seconds','compilation_seconds','complete_candidate_attempts')}
        totals[track]['tokens']={k:sum(v['tokens'][k] for v in rows) for k in ('input','output','reasoning','total')}
        totals[track]['base_completed']=sum(results[t['id']+'-'+track].get('final',{}).get('full_acceptance',False) for t in tasks)
        totals[track]['modifications_completed']=sum(results[t['id']+'-'+track+'-M'].get('final',{}).get('full_acceptance',False) for t in tasks[:2])
        totals[track]['regressions']=sum(results[t['id']+'-'+track+'-M'].get('regressions',0) for t in tasks[:2])
        totals[track]['repairs']=sum(max(0,v['complete_candidate_attempts']-1) for v in rows)
        totals[track]['API_cost']=None
    # A tiny exploratory study with incomplete total workflow cost cannot establish
    # an architectural winner from author-session timing alone.
    classification='R6_30_COMPARISON_INCONCLUSIVE' if protocol else 'R6_30_PROTOCOL_HALT'
    e.save('FUNCTIONAL.json',dict(model_calls=0,results=results))
    e.save('MEASUREMENTS.json',dict(stages=measurements,totals=totals,
        coordinator_input_tokens=None,coordinator_output_tokens=None,coordinator_cost=None,
        coordinator_preparation_elapsed_seconds=(__import__('datetime').datetime.fromisoformat(e.read('FREEZE.json')['timestamp'])-__import__('datetime').datetime.fromisoformat(e.read('BASELINE.json')['timestamp'])).total_seconds(),
        preparation_includes_correction=True,total_workflow_cost_attested=False,pure_inference_time=None,
        session_wall_includes_prompt_schema_tools_and_deterministic_dispatch=True))
    e.save('RESULT.json',dict(timestamp=e.h.now(),classification=classification,protocol_valid=protocol,
        exploratory=True,modifications_contaminated=True,successor_correction_passed='23/23',historical_result='19/23',
        C_value_beyond_B_demonstrated=False,totals=totals,stopped=True))
    print(classification)
    print(json.dumps(totals,indent=2))

def publish():
    e.verify()
    files={}
    paths=[p for p in e.HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name not in ('PUBLICATION-IDENTITIES.json','VERIFICATION.json')]
    paths+=[e.HERE.parent/'R6_30-REPORT.md']+[e.ROOT/'docs'/n for n in ('project-overview-r6.30.md','research-log-r6.30.md','decisions-r6.30.md')]
    for p in paths:
        text=p.read_text(encoding='utf-8')
        if p.suffix=='.json': json.loads(text)
        if p.suffix=='.jsonl':
            for line in text.splitlines(): json.loads(line)
        if p.suffix in ('.md','.py'):
            assert all(x==x.rstrip() for x in text.splitlines()),p
        assert not e.h.re.search(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|\bsk-[A-Za-z0-9_-]{20,}',text),p
        if p.suffix=='.md':
            for link in e.h.re.findall(r'\]\(([^)]+)\)',text):
                if not link.startswith(('https:','http:')):
                    assert (p.parent/link.split('#')[0]).resolve().exists(),(p,link)
        files[p.relative_to(e.ROOT).as_posix()]=dict(sha256=e.digest(p),bytes=p.stat().st_size)
    diff=subprocess.run(['git','diff','--check'],cwd=e.ROOT,capture_output=True,text=True)
    assert diff.returncode==0,diff.stderr
    e.save('PUBLICATION-IDENTITIES.json',dict(timestamp=e.h.now(),files=files))
    e.save('VERIFICATION.json',dict(timestamp=e.h.now(),passed=True,classification=e.read('RESULT.json')['classification'],
        publication_manifest_sha256=e.digest(e.HERE/'PUBLICATION-IDENTITIES.json'),publication_files=len(files),
        protected_count=e.read('BASELINE.json')['protected_count'],protected_mismatches=[],kernel=26,freeze_verified=True,
        JSON_links_whitespace_checked=True,credentials_published=False,git_diff_check=dict(returncode=diff.returncode,stdout=diff.stdout,stderr=diff.stderr),
        P6_A04_acceptance=False,P6_A05_access=False,semantic_implementation_changes=False,stopped=True))
    assert all(e.digest(e.ROOT/p)==v['sha256'] for p,v in files.items())
    print('Publication verified:',len(files),'files;',e.read('BASELINE.json')['protected_count'],'protected identities')

if __name__=='__main__':
    {'evaluate':evaluate,'publish':publish}[sys.argv[1]]()
