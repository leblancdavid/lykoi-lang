"""Missing-telemetry collector successor; frozen acceptance and scorer unchanged."""
import json
import time
from datetime import datetime
import evaluate as original
import experiment as e

def recovered_telemetry(run):
    session=e.read(run+'/SESSION.json')
    rows=[json.loads(l) for l in (e.HERE/run/'MCP.jsonl').read_text().splitlines()]
    calls=[r for r in rows if r['request']['method']=='tools/call']
    assistants=[m['info'] for m in session['messages'] if m['info']['role']=='assistant']
    completed=[m for m in assistants if 'completed' in m['time']]
    parts=[p for m in session['messages'] for p in m['parts']]
    native=[p for p in parts if p['type']=='tool']
    lineage=len(native)==len(calls) and all(any(p['tool']=='work_'+r['request']['params']['name'] and p['state']['input']==r['request']['params']['arguments'] and json.loads(p['state']['output'])==r['response']['result']['structuredContent'] for p in native) for r in calls)
    return dict(run=run,model_verified=all(m['providerID']=='openai' and m['modelID']=='gpt-6.1-sol' for m in assistants),
        delivery_matches=e.read(run+'/DELIVERY.json')['matches_requested'],model_calls=len(assistants),completed_model_calls=len(completed),
        incomplete_model_calls=len(assistants)-len(completed),tool_calls=len(calls),tool_failures=sum(r['response']['result'].get('isError',False) for r in calls),
        failures=[r for r in calls if r['response']['result'].get('isError')],tool_argument_lineage_verified=lineage,
        tokens={k:sum(m['tokens'].get(k,0) for m in completed) for k in ('input','output','reasoning','total')},
        usage_complete=False,token_values_are_completed_call_lower_bounds=True,
        cached_read=sum(m['tokens']['cache']['read'] for m in completed),cached_write=sum(m['tokens']['cache'].get('write',0) for m in completed),
        SDK_cost=sum(m['cost'] for m in completed),API_billing=None,effective_reasoning='UNATTESTED',pure_inference_seconds=None,
        session_wall_seconds=None,assistant_message_elapsed_seconds=sum((m['time']['completed']-m['time']['created'])/1000 for m in completed),
        deterministic_dispatch_seconds=sum(r['seconds'] for r in calls),
        compilation_seconds=sum(e.read(p.relative_to(e.HERE).as_posix())['compilation_seconds'] for p in (e.HERE/run).glob('COMPILED-*.json')),
        complete_candidate_attempts=len(list((e.HERE/run).glob('ATTEMPT-*.json'))),provider_errors=[],provider_errors_complete=False,
        fresh_session=session['info']['id'],hidden_context_exclusion='UNATTESTED',SDK_cost_is_billing=False,
        raw_event_stream_available=False,source='Native exported SDK messages and MCP log after outer terminal timeout; no reconstruction of raw stdout.')

def main():
    begin=time.perf_counter()
    e.verify()
    e.save('COLLECTOR-SUCCESSOR-1.json',dict(timestamp=e.h.now(),
        frozen_collector_sha256=e.digest(e.HERE/'evaluate.py'),successor_sha256=e.digest(e.HERE/'evaluate_successor.py'),
        change='Native session export fallback for interrupted T2-B; preserve unknown wall time as null and incomplete usage as measured lower bounds. All acceptance cases, expected observations and candidate scoring functions unchanged.',
        justification='Frozen collector assumed raw event stream and numeric wall time for every stage; outer terminal timeout invalidated that assumption.',acceptance_changes=0,author_reruns=0))
    tasks=e.read('TASKS.json')['tasks']; suites=e.read('ACCEPTANCE.json')
    results={};measurements={}
    for run in e.read('FREEZE.json')['order']+[r+'-M' for r in e.read('FREEZE.json')['modification_order']]:
        t=next(t for t in tasks if t['id']==run.split('-')[0]);modified=run.endswith('-M')
        signature=t.get('mod_signature',t['signature']) if modified else t['signature']
        cases=suites['modified' if modified else 'base'][t['id']]
        measurements[run]=recovered_telemetry(run) if run=='T2-B' else original.telemetry(run)
        measurements[run].setdefault('usage_complete',True)
        assert e.read(run+'/PROCESS.json')['author_process_terminated']
        attempts=sorted((e.HERE/run).glob('ARTIFACT-*.json' if run.split('-')[1]=='C' else 'ATTEMPT-*.json'))
        final=run+'/FINAL-CANDIDATE.json'
        result=dict(status='NOT_REACHED',reason='No completed candidate')
        if (e.HERE/final).exists():
            result=dict(first=original.candidate(run,attempts[0].relative_to(e.HERE).as_posix(),cases,signature),final=original.candidate(run,final,cases,signature))
            if modified:
                base=run[:-2]
                result['original_regression']=original.candidate(base,base+'/FINAL-CANDIDATE.json',suites['base'][t['id']],t['signature'])
                result['original_artifact_preserved']=e.digest(e.HERE/(base+'/FINAL-CANDIDATE.json'))==results[base]['final']['candidate_sha256']
                result['regressions']=sum(old['passed'] and not new['passed'] for old,new in zip(results[base]['final']['records'],result['original_regression']['records']))
                result['withholding']='CONTAMINATED_UNENFORCED'
        results[run]=result
    sessions=[v['fresh_session'] for v in measurements.values()]
    protocol=all(v['model_verified'] and v['delivery_matches'] and v['tool_argument_lineage_verified'] and v['tool_calls']<=32 and v['complete_candidate_attempts']<=4 for v in measurements.values()) and len(set(sessions))==len(sessions)
    totals={}
    for track in 'ABC':
        rows=[v for k,v in measurements.items() if k.split('-')[1]==track]
        totals[track]={k:sum(v[k] for v in rows) for k in ('model_calls','tool_calls','tool_failures','cached_read','cached_write','assistant_message_elapsed_seconds','deterministic_dispatch_seconds','compilation_seconds','complete_candidate_attempts')}
        known=[v['session_wall_seconds'] for v in rows if v['session_wall_seconds'] is not None]
        totals[track]['session_wall_seconds']=sum(known) if len(known)==len(rows) else None
        totals[track]['known_session_wall_seconds']=sum(known)
        totals[track]['missing_session_wall_stages']=len(rows)-len(known)
        totals[track]['tokens']={k:sum(v['tokens'][k] for v in rows) for k in ('input','output','reasoning','total')}
        totals[track]['usage_complete']=all(v['usage_complete'] for v in rows)
        totals[track]['tokens_are_lower_bounds']=not totals[track]['usage_complete']
        totals[track]['base_completed']=sum(results[t['id']+'-'+track].get('final',{}).get('full_acceptance',False) for t in tasks)
        totals[track]['base_first_attempt_completed']=sum(results[t['id']+'-'+track].get('first',{}).get('full_acceptance',False) for t in tasks)
        totals[track]['modifications_completed']=sum(results[t['id']+'-'+track+'-M'].get('final',{}).get('full_acceptance',False) for t in tasks[:2])
        totals[track]['regressions']=sum(results[t['id']+'-'+track+'-M'].get('regressions',0) for t in tasks[:2])
        totals[track]['repairs']=sum(max(0,v['complete_candidate_attempts']-1) for v in rows)
        totals[track]['API_cost']=None
    classification='R6_30_COMPARISON_INCONCLUSIVE' if protocol else 'R6_30_PROTOCOL_HALT'
    e.save('FUNCTIONAL.json',dict(model_calls=0,results=results,scoring_function_sha256=e.digest(e.HERE/'evaluate.py')))
    e.save('MEASUREMENTS.json',dict(stages=measurements,totals=totals,
        coordinator_input_tokens=None,coordinator_output_tokens=None,coordinator_cost=None,
        coordinator_preparation_elapsed_seconds=(datetime.fromisoformat(e.read('FREEZE.json')['timestamp'])-datetime.fromisoformat(e.read('BASELINE.json')['timestamp'])).total_seconds(),
        experiment_elapsed_to_evaluation_seconds=(datetime.fromisoformat(e.h.now())-datetime.fromisoformat(e.read('BASELINE.json')['timestamp'])).total_seconds(),
        preparation_includes_correction=True,total_workflow_cost_attested=False,pure_inference_time=None,evaluation_wall_seconds=time.perf_counter()-begin,
        session_wall_includes_prompt_schema_tools_and_deterministic_dispatch=True,
        interruption='T2-B wall unavailable; fourth started model message has no completed usage, B totals are measured lower bounds. No billing inferred.'))
    e.save('RESULT.json',dict(timestamp=e.h.now(),classification=classification,protocol_valid=protocol,
        exploratory=True,modifications_contaminated=True,successor_correction_passed='23/23',historical_result='19/23',
        C_value_beyond_B_demonstrated=False,totals=totals,orchestration_interruption=True,stopped=True))
    print(classification);print(json.dumps(totals,indent=2))

if __name__=='__main__': main()
