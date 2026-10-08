"""Publication summaries and regression transcripts, no new construction/acceptance."""
import json
import os
import subprocess
import sys
import time
from audit import HERE, ROOT, OLD, load, now, save, sha, verify, verify_map


def main():
    verify()
    for name in ['SPEC-FREEZE.json','RUN-FREEZE.json','FOLLOWUP-SPEC-FREEZE.json','FOLLOWUP-RUN-FREEZE.json']:
        verify_map(HERE,load(HERE/name)['files'])
    from run import structure
    # Nonexecuting structural accounting of the already timed-out comparison.
    naive=structure(load(HERE/'naive-xor8.plan.json'))
    naive['published_json_bytes']=(HERE/'naive-xor8.plan.json').stat().st_size
    naive['validation']=dict(status='PROCESS_TIMEOUT',seconds=load(HERE/'RUN-RESULTS.json')['observations'][0]['seconds'],
        traversals='UNAVAILABLE: killed before validator response',repeated=False)
    save(HERE/'naive-xor8-structure.json',naive)
    historical=load(OLD/'PROBE-RESULTS-2.json')
    nibble=[]
    for observation in historical['observations']:
        actual=observation.get('actual',{})
        if isinstance(actual,dict) and 'observations' in actual:
            nibble.extend(x for x in actual['observations'] if x.get('id')=='C-nibble-XOR')
    # Historical probe worker uses a compact aggregate rather than the original
    # unsupervised observations; publish its exact relevant record unchanged.
    historical_records=[x for x in historical['observations'] if 'nibble' in x['id'] or 'full_byte' in x['id']]
    save(HERE/'HISTORICAL-XOR-EVIDENCE.json',dict(source_sha256=sha(OLD/'PROBE-RESULTS-2.json'),
        records=historical_records,baseline_replay_pairs=256,baseline_replay_nodes=21))
    summary={}
    for name in ['xor8-consuming','addmod8','parity8']:
        structural=load(HERE/(name+'-structure.json'))
        acceptance=load(HERE/(name+'-acceptance.json'))
        runs=acceptance['passes']
        assert acceptance['status']=='COMPLETE' and acceptance['deterministic']
        assert all(p['covered']==p['total'] and not p['failures'] for p in runs)
        assert all(x['passed'] for x in acceptance['negative_observations'])
        summary[name]=dict(nodes=structural['structural_nodes'],canonical_bytes=structural['canonical_json_bytes'],
            published_bytes=structural['published_json_bytes'],tree_depth=structural['structural_tree_depth'],
            runtime_depth=structural['expanded_runtime_node_depth'],expression_depth=structural['expression_depth'],
            expression_occurrences=structural['expression_occurrences'],
            validation_median_seconds=structural['validation']['median_seconds'],
            validation_traversals=structural['validation']['traversal_counts'],
            coverage_per_pass=runs[0]['covered'],passes=3,runtime_seconds=[p['seconds'] for p in runs],
            work_min=runs[0]['work_min'],work_max=runs[0]['work_max'],work_sum=runs[0]['work_sum'],
            deterministic=acceptance['deterministic'],public_api=acceptance['public_api_crosscheck'],
            memory=acceptance['memory'],negative_entries=len(acceptance['negative_observations']),
            work_cutoffs=sum(x['actual']['cutoffs'] for x in acceptance['negative_observations'] if x['id']=='work-cutoffs'))
    checks=[];env=dict(os.environ,PYTHONPATH='src',PYTHONDONTWRITEBYTECODE='1')
    commands=[['-m','air_compiler.cli','validate','air/task_manager.json'],
        ['-m','air_compiler.cli','safety','air/task_manager.json'],
        ['-m','unittest','discover','-s','tests','-p','test_compiler.py','-v'],
        ['-m','unittest','discover','-s','tests','-p','test_application.py','-v'],
        ['-m','unittest','discover','-s','benchmark/harness','-p','test_baseline.py','-v'],
        ['-m','unittest','discover','-s','experiments/semantic_interpreter','-p','test_interpreter.py','-v'],
        ['-m','unittest','discover','-s','benchmark/results/phase6/r6_13','-p','test_scorer.py','-v']]
    for args in commands:
        begin=time.perf_counter();command=[sys.executable,'-B']+args
        result=subprocess.run(command,cwd=ROOT,env=env,capture_output=True,text=True,timeout=180)
        checks.append(dict(command=command,returncode=result.returncode,stdout=result.stdout,
            stderr=result.stderr,seconds=time.perf_counter()-begin))
        print('Regression',args[-1],result.returncode,flush=True)
    verify()
    save(HERE/'CHECKS.json',dict(utc=now(),checks=checks,
        preserved_identities=len(load(HERE/'BASELINE.json')['preserved']),kernel=26))
    assert all(x['returncode']==0 for x in checks)
    save(HERE/'SUMMARY.json',dict(utc=now(),classification='R6_14_FINITE_RELATIONS_SUPPORTED',relations=summary,
        first_experiment='Two accepted relations; XOR8 static progress rejection; naive lookup timeout',
        second_experiment='One explicitly separately frozen consuming-atom repair, exhaustive XOR8 success'))
    print(json.dumps(summary,indent=2))


if __name__=='__main__':
    main()
