"""Post-author timing attribution from actual dispatch/acceptance records."""
import json
import experiment as e

def main():
    totals={t:dict(development_validation_seconds=0,development_generation_compilation_seconds=0,
        development_successful_test_calls=0,development_failed_test_calls=0,
        acceptance_validation_seconds=0,acceptance_expansion_including_validation_seconds=0,
        acceptance_VM_including_validation_seconds=0,acceptance_wrapper_rejection_seconds=0) for t in 'ABC'}
    for run,m in e.read('MEASUREMENTS.json')['stages'].items():
        track=run.split('-')[1];t=totals[track]
        rows=[json.loads(l) for l in (e.HERE/run/'MCP.jsonl').read_text().splitlines()]
        for r in rows:
            if r['request']['method']!='tools/call': continue
            name=r['request']['params']['name']
            if name=='validate_candidate': t['development_validation_seconds']+=r['dispatch']['seconds']
            if name=='submit_candidate': t['development_generation_compilation_seconds']+=r['seconds']
            if name=='run_case':
                key='development_failed_test_calls' if r['response']['result'].get('isError') else 'development_successful_test_calls'
                t[key]+=1
        for row in e.read('FUNCTIONAL.json')['results'][run]['final']['records']:
            times=row.get('times',{})
            for source,dest in [('validation_seconds','acceptance_validation_seconds'),('expansion_including_validation_seconds','acceptance_expansion_including_validation_seconds'),('execution_including_VM_validation_seconds','acceptance_VM_including_validation_seconds'),('wrapper_rejection_seconds','acceptance_wrapper_rejection_seconds')]:
                t[dest]+=times.get(source,0)
    e.save('EFFORT-BREAKDOWN.json',dict(totals=totals,
        scope='Five stages per track; additive to frozen measurement record. Development validation dispatch includes strict arguments, adapter construction, wrapper validation and expansion. Acceptance execution timing excludes trace rerun but includes public VM validation.',
        B_interrupted_completed_dispatch_times_available=True,coordinator_model_tokens=None,API_cost=None,
        total_wall_time_comparison='Unavailable for B; no inferred replacement. Report complete A/C session wall and known B subset. Runtime timings are separate from author development.'))
    print(json.dumps(totals,indent=2))

if __name__=='__main__': main()
