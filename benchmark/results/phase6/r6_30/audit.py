"""Offline lineage, withholding, deterministic replay and immutable regressions."""
import json
import subprocess
import sys
import time
import experiment as e

def main():
    e.verify()
    lineage=[]
    replays=[]
    runs=e.read('FREEZE.json')['order']+[r+'-M' for r in e.read('FREEZE.json')['modification_order']]
    for run in runs:
        data=e.read(run+'/SESSION.json')
        parts=[p for m in data['messages'] for p in m['parts'] if p['type']=='tool']
        rows=[json.loads(l) for l in (e.HERE/run/'MCP.jsonl').read_text().splitlines()]
        calls=[r for r in rows if r['request']['method']=='tools/call']
        assert len(parts)==len(calls)
        assert all(any(p['tool']=='work_'+r['request']['params']['name'] and p['state']['input']==r['request']['params']['arguments'] and json.loads(p['state'].get('output',p['state'].get('error')))==r['response']['result']['structuredContent'] for p in parts) for r in calls)
        req=e.read(run+'/REQUEST.json')
        assert req['model']=='openai/gpt-6.1-sol' and req['reasoning_requested']=='high'
        if not run.endswith('-M'):
            assert 'Modification disclosed now:' not in req['prompt'] and 'Same-track original candidate:' not in req['prompt']
        else:
            assert 'Modification disclosed now:' in req['prompt']
            assert req['timestamp']>e.read('BASE-COMPLETE.json')['timestamp']
        if run.split('-')[1]=='C':
            s=e.tools.Session(['value','check','compose'])
            semantic=0
            for row in calls:
                p=row['request']['params']
                if p['name']=='reset_candidate': s=e.tools.Session(['value','check','compose'])
                if p['name'] in ('declare_input','apply_operation','define_result','validate_candidate'):
                    r=s.dispatch({'function':dict(name=p['name'],arguments=p['arguments'])})
                    assert r['response']==row['dispatch']['response']
                    semantic+=1
            assert s.completed['artifact']==e.read(run+'/FINAL-CANDIDATE.json')
            initial=e.read('FUNCTIONAL.json')['results'][run]['final']['records']
            for row in initial:
                obs,t=e.norm(e.read(run+'/FINAL-CANDIDATE.json'),row['case']['args'])
                assert obs==row['actual']
                replays.append(dict(run=run,case=row['case']['id'],equal=True,times=t))
            lineage.append(dict(run=run,semantic_calls=semantic,artifact_reconstructed=True,arguments_and_feedback_verified=True))
        else:
            lineage.append(dict(run=run,calls=len(calls),arguments_and_feedback_verified=True))
    tests=[]
    for path,pattern in [('benchmark/results/phase6/r6_25','test_transport.py'),('experiments/typed_composition_r6_18','test_composition.py'),('experiments/semantic_interpreter','test_interpreter.py')]:
        begin=time.perf_counter()
        p=subprocess.run([sys.executable,'-m','unittest','discover','-s','.','-p',pattern,'-v'],cwd=e.ROOT/path,capture_output=True,text=True,timeout=120)
        tests.append(dict(path=path,pattern=pattern,returncode=p.returncode,stdout=p.stdout,stderr=p.stderr,wall_seconds=time.perf_counter()-begin))
        assert p.returncode==0,p.stderr
    e.verify()
    e.save('OFFLINE-AUDIT.json',dict(timestamp=e.h.now(),passed=True,model_calls=0,lineage=lineage,C_replay=replays,
        C_replay_observations=len(replays),explicit_base_prompts_omit_modifications=True,modification_disclosure_after_all_base_processes=True,
        hidden_context_withholding='CONTAMINATED_UNENFORCED',regression_suites=tests,protected_count=e.read('BASELINE.json')['protected_count'],
        original_R6_29_acceptance_passes=19,original_R6_29_total=23,original_R6_29_classification='R6_29_CONSTRUCTION_PARTIAL'))
    print('Offline lineage15/15; C replay',len(replays),'observations; immutable regressions PASS')

if __name__=='__main__': main()
