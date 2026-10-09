"""Post-inference accounting and integrity only; never sends inference requests."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]


def read(name):
    return json.loads((HERE/name).read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(name,value):
    (HERE/name).write_text(json.dumps(value,indent=2,ensure_ascii=True)+'\n',encoding='utf-8')


def total(records):
    tokens={}
    for key in ('prompt_eval_count','prompt_eval_cached_count','eval_count'):
        values=[r['tokens'][key] for r in records]
        tokens[key]=dict(reported_sum=sum(x for x in values if x is not None),missing_calls=sum(x is None for x in values))
    times={}
    for key in ('total_duration','load_duration','prompt_eval_duration','eval_duration'):
        values=[r['durations_ns'][key] for r in records]
        times[key]=dict(reported_seconds=sum(x for x in values if x is not None)/1e9,missing_calls=sum(x is None for x in values))
    return dict(calls=len(records),http_statuses=dict(Counter(str(r['http_status']) for r in records)),
                tokens=tokens,durations=times,call_wall_seconds=sum(r['latency_seconds'] for r in records))


def collect():
    calls=[json.loads(p.read_text()) for p in sorted((HERE/'calls').glob('*.json'))]
    calls.sort(key=lambda x:x['timestamp'])
    runtime=read('STRUCTURED-RESULTS.json')['rows']; features=read('FEATURE-RESULTS.json')['rows']; pairs=read('COMPARISON.json')['rows']
    log=(HERE/'SERVER.log').read_bytes()
    delivery=[]; resources=[]
    for call in calls:
        begin,end=call['log_byte_span']
        text=log[begin:end].decode('utf-8',errors='replace')
        truncations=[dict(limit=int(a),original_tokens=int(b),keep=int(c),new_tokens=int(d)) for a,b,c,d in
                     re.findall(r'truncating input prompt" limit=(\d+) prompt=(\d+) keep=(\d+) new=(\d+)',text)]
        delivery.append(dict(call=call['id'],prompt_sha256=call['prompt_sha256'],schema_sha256=call['schema_sha256'],
             prompt_tokens_reported=call['tokens']['prompt_eval_count'],truncations=truncations,
             done_reason=call['response'].get('done_reason') if call['response'] else None,
             post_version_responsive='error' not in call['post_health']['/api/version'],
             post_ps_responsive='error' not in call['post_health']['/api/ps']))
        for sample in call['resources']:
            sample=dict(sample,call=call['id'])
            gpu=sample.get('gpu',{})
            if gpu.get('returncode')==0:
                try:
                    nums=[int(x.strip()) for x in gpu['stdout'].strip().split(',')]
                    sample['gpu_values']=dict(zip(('total_mib','used_mib','utilization_percent','memory_utilization_percent'),nums))
                except ValueError:
                    sample['gpu_parse_error']=True
            resources.append(sample)
    save('PROMPT-DELIVERY.json',dict(rows=delivery,truncated_calls=sum(bool(x['truncations']) for x in delivery),
         actual_retained_prompt='UNAVAILABLE: raw submitted messages preserved; runtime logs record lengths/keep only',
         qualification='symbolic message delivery compromised; no post-outcome runner/prompt/schema correction'))
    gpu=[x['gpu_values'] for x in resources if 'gpu_values' in x]
    ram=[x['ram_available_bytes'] for x in resources if x.get('ram_available_bytes') is not None]
    working=[x['server_working_set_bytes'] for x in resources if x.get('server_working_set_bytes') is not None]
    private=[x['server_private_bytes'] for x in resources if x.get('server_private_bytes') is not None]
    resource_summary=dict(samples=len(resources),gpu_valid_samples=len(gpu),ram_valid_samples=len(ram),
       gpu_used_mib_min=min(x['used_mib'] for x in gpu),gpu_used_mib_max=max(x['used_mib'] for x in gpu),
       gpu_utilization_min=min(x['utilization_percent'] for x in gpu),gpu_utilization_max=max(x['utilization_percent'] for x in gpu),
       available_ram_bytes_min=min(ram),available_ram_bytes_max=max(ram),
       ollama_parent_working_set_bytes_min=min(working) if working else None,ollama_parent_working_set_bytes_max=max(working) if working else None,
       ollama_parent_private_bytes_min=min(private) if private else None,ollama_parent_private_bytes_max=max(private) if private else None,
       sampling='approximately1s plus command overhead; shared desktop GPU, not process-isolated peaks',
       runner_per_call_working_set='UNAVAILABLE; end-of-run process snapshot in LOCALITY.json',
       telemetry_missing_is_not_zero=True)
    save('RESOURCES.json',dict(summary=resource_summary,samples=resources))
    group_records={
       'runtime':[x for x in calls if not x['id'].startswith(('feature_','N'))],
       'features':[x for x in calls if x['id'].startswith('feature_')],
       'A':[x for x in calls if '_A_' in x['id']],
       'B':[x for x in calls if '_B_' in x['id']]}
    measurements={}
    for group,records in group_records.items():
        measurements[group]=total(records)
        if group=='runtime':
            measurements[group]['validation_seconds']=sum(x['validation_seconds'] for x in runtime)
        elif group=='features':
            measurements[group]['validation_seconds']=sum(x['result']['validation_seconds'] for x in features)
        else:
            sessions=[x for x in pairs if x['interface']==group]
            results=[a['result'] for x in sessions for a in x['attempts'] if 'result' in a]
            measurements[group].update(validation_seconds=sum(x.get('validation_seconds',0) for x in results),
               total_session_seconds=sum(x['total_seconds'] for x in sessions),
               assembly_seconds=sum(x['assembly_seconds'] for x in sessions),
               repair_attempts=sum(x['repair_attempts'] for x in sessions),
               objectives_completed=sum(x['objective_complete'] for x in sessions),objectives=len(sessions),
               final_compositions_valid=sum(x['composition_valid'] for x in sessions),
               valid_json_messages=sum(x.get('json_valid',False) for x in results),schema_valid_messages=sum(x.get('schema_valid',False) for x in results),
               unused_generated_token_budget=sum(x['remaining_output_budget'] for x in sessions))
    save('MEASUREMENTS.json',dict(groups=measurements,all_calls=total(calls),resources=resource_summary,run=read('RUN-STATUS.json'),
         timing_notes='call latency excludes postcall GETs/monitor join; session includes prompts, GETs, monitor/validation; run includes inventory and cleanup-independent work; publication wall separate',
         cached_tokens='kept separate, not assumed additive billing; prefix-cache reuse observed',
         expansion_execution_timing='NOT_REACHED for model outputs; host control composite validation times separate',
         billing_energy='UNAVAILABLE',repair_note='12 A regenerations; B stage1 failures terminal; zero manual repairs'))
    response_results=runtime+[x['result'] for x in features]+[a['result'] for x in pairs for a in x['attempts'] if 'result' in a]
    save('FAILURE-CLASSIFICATIONS.json',dict(observed=dict(Counter(x['classification'] for x in response_results)),
       failures=[dict(call=call['id'],http_status=call['http_status'],error=call['error']) for call in calls if call['http_status']!=200],
       diagnostic_precedence='first error only; feature and comparison all stop at JSON/schema, types/deps/pins/expansion NOT_REACHED',
       runtime_http_failures=0,critical_historical_failure='R6.19 HTTP500 unresolved; current HTTP500 response bodies absent because none occurred',
       controls='HOST-CONTROLS.json separately qualifies downstream rejection classes; not participant successes'))
    save('COMPLEXITY-MATRIX.json',dict(rows=[dict(feature=x['feature'],call='feature_'+x['id'],
       json_valid=x['result']['json_valid'],schema_valid=x['result']['schema_valid'],composition_valid=x['result']['composition_valid'],
       first_failure=x['result']['diagnostic'],feature_specific_cause='UNRESOLVED: common schema failure plus input truncation',
       downstream='NOT_REACHED') for x in features],classification='representation delivery/shape failure, no isolated feature attribution'))
    old=ROOT/'benchmark/results/phase6/r6_19'
    old_log=(old/'SERVER.log').read_text()
    history=[dict(line=i,text=line) for i,line in enumerate(old_log.splitlines(),1) if i>=968]
    save('HTTP500-INVESTIGATION.json',dict(original_round='R6.19',historical_log_sha256=sha(old/'SERVER.log'),
       failed_request_sha256=sha(old/'FAILED-CALL.json'),failed_request_provenance='historical deterministic reconstruction, never replayed',
       original_response_body=None,original_failed_call_tokens=None,original_error_sha256=sha(old/'HALT.json'),
       tail=history,observed_context=dict(n_ctx_slot=8192,prompt_tokens=2771,last_logged_generated_tokens=908),
       context_note='last logged generation plus prompt is3679; no logged context exhaustion, later generation unknown',
       previous_successful_calls='two immediate prior HTTP200 requests; historical warm generation ~75tokens/s',
       current_statuses=dict(Counter(str(x['http_status']) for x in calls)),
       longest_current_output_tokens=max(x['tokens']['eval_count'] for x in calls if x['tokens']['eval_count'] is not None),
       cause='UNDETERMINED: HTTP endpoint reports failure during active generation; no causal runtime error/body/dump retained',
       most_likely_cause='No specific mechanism can be ranked responsibly from available evidence. Inference-serving path failed; OOM, backend disconnect/crash, output/parser failure remain unproved hypotheses.',
       evidence_against_assumptions='historical no OOM log; current sampled VRAM/RAM not exhausted and2457-token outputs succeed; current resources cannot reconstruct historical peaks',
       reproduction='NOT_REPRODUCED by49 neutral requests; scored historical request not replayed',
       next_diagnostic='qualify compact nontruncating prompts first, then separately authorize longer sequential neutral soak with full body capture and backend process/exit sampling'))
    save('RELIABILITY.json',dict(classification='R6_20_PROTOCOL_HALT',repeatable_local_inference='49/49 HTTP200 in one bounded session; narrow support only',
       unresolved_critical_failure='historical HTTP500 cause unresolved',structured_output='15/15 schema-constrained runtime requests pass; generic long JSON1/1; deliberate cap truncation3/3 invalid JSON',
       valid_model_composition='0 accepted; feature8/8 and A/B all failed schema or JSON; full semantics not delivered',
       failure_accounting='all49 raw calls, logs, feedback and sampled resources retained; historical body/tokens and exact posttruncation prompt missing explicitly',
       comparison='A0/4 B0/4 objectives; B stops stage1 in every case; no incremental-validity benefit established',
       gate_passed=False,next_discovery_recommended=False,
       smallest_next_step='Separately authorized compact prompt-budget integrity qualification: deduplicate schemas, keep common semantics and library within observed4098-token input bound, preflight token/delivery guard, freeze fresh neutral objectives. Do not reuse this comparison as favorable evidence.',
       followup='Only after intact prompt delivery, separately bounded runtime soak and symbolic interface comparison; no discovery until unresolved reliability/valid-composition gates cleared',
       stop='published; await explicit owner authorization'))
    print(json.dumps(dict(measurements=measurements,resources=resource_summary,failures=Counter(x['classification'] for x in response_results)),indent=2))


def verify():
    b=read('BASELINE.json')
    assert all(sha(ROOT/p)==h for p,h in b['protected_files'].items())
    f=read('FREEZE.json'); assert all(sha(HERE/p)==h for p,h in f['files'].items())
    assert sha(HERE/'BASELINE.json')==f['baseline']
    assert b['kernel']==26
    assert read('HOST-CONTROLS.json')['passed']==9
    assert read('RUN-STATUS.json')['participant_calls']==49
    assert read('RELIABILITY.json')['classification']=='R6_20_PROTOCOL_HALT'
    paths=list(HERE.rglob('*'))+[ROOT/'benchmark/results/phase6/R6_20-REPORT.md']
    paths += [ROOT/'docs'/p for p in ('project-overview-r6.20.md','research-log-r6.20.md','decisions-r6.20.md')]
    files={}
    for p in paths:
        if not p.is_file() or '__pycache__' in p.parts or p.name in ('PUBLICATION-IDENTITIES.json','VERIFICATION.json'): continue
        if p.suffix=='.json': json.loads(p.read_text())
        if p.suffix in ('.py','.md','.txt','.json'):
            assert all(line.rstrip()==line for line in p.read_text().splitlines()), str(p)
        files[p.relative_to(ROOT).as_posix()]=dict(sha256=sha(p),bytes=p.stat().st_size)
    report=ROOT/'benchmark/results/phase6/R6_20-REPORT.md'
    for link in re.findall(r'\]\(([^)]+)\)',report.read_text()):
        if not link.startswith(('http:','https:','#')):
            target=report.parent/link.split('#')[0]
            assert target.exists() or target in (HERE/'PUBLICATION-IDENTITIES.json',HERE/'VERIFICATION.json'),link
    diff=subprocess.run(['git','diff','--check'],cwd=ROOT,capture_output=True,text=True)
    assert diff.returncode==0,diff.stdout+diff.stderr
    # The original R6.19 publication pinned guidance files. New guidance is additive.
    status=subprocess.run(['git','status','--short'],cwd=ROOT,capture_output=True,text=True)
    assert all(line.startswith('?? ') for line in status.stdout.splitlines()),status.stdout
    save('PUBLICATION-IDENTITIES.json',dict(round='R6.20',classification='R6_20_PROTOCOL_HALT',files=files,
        exclusions='manifest and verification receipt exclude themselves; disposable bytecode excluded'))
    pub=read('PUBLICATION-IDENTITIES.json')
    assert all(sha(ROOT/p)==x['sha256'] and (ROOT/p).stat().st_size==x['bytes'] for p,x in pub['files'].items())
    import datetime
    timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
    start=read('FREEZE.json')['timestamp']
    save('VERIFICATION.json',dict(timestamp=timestamp,classification='R6_20_PROTOCOL_HALT',kernel=26,
        protected_count=len(b['protected_files']),protected_mismatches=0,r6_19_publication_files=b['r6_19_publication_count'],
        publication_count=len(files),publication_mismatches=0,manifest_sha256=sha(HERE/'PUBLICATION-IDENTITIES.json'),
        freeze='PASS',all_json_parse='PASS',new_text_whitespace='PASS',report_links='PASS',git_diff_check='PASS',
        tracked_changes='NONE',inference_replay='NOT_RUN',P6_A04_acceptance='NOT_RUN',P6_A05_access='NOT_ACCESSED',
        freeze_through_publication_elapsed_seconds=(datetime.datetime.fromisoformat(timestamp)-datetime.datetime.fromisoformat(start)).total_seconds(),
        elapsed_note='includes local inference and interactive analysis/publication; not active labor or inference-only timing'))
    for link in re.findall(r'\]\(([^)]+)\)',report.read_text()):
        if not link.startswith(('http:','https:','#')): assert (report.parent/link.split('#')[0]).exists(),link
    print('Verified',len(files),'publication identities;',len(b['protected_files']),'protected; kernel26; no tracked edits.')


if __name__=='__main__':
    if sys.argv[1]=='collect': collect()
    elif sys.argv[1]=='verify': verify()
    else: raise ValueError(sys.argv[1])
