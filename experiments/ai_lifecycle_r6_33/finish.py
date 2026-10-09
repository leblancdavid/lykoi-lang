"""Publish the terminal transport halt; no model calls or candidate construction."""
import json
from pathlib import Path
import re
import subprocess
import sys
from pilot import OUT, ROOT, HERE, TEMP, save, sha, load, protected, Journal


def redact(value, locations, path='$'):
    if isinstance(value, dict):
        for key in value:
            if key.lower() in ('set-cookie', 'authorization', 'cookie', 'x-api-key'):
                locations.append(path+'/'+key)
                value[key] = '<REDACTED_RESPONSE_CREDENTIAL>'
            else:
                redact(value[key],locations,path+'/'+key)
    elif isinstance(value,list):
        for i,item in enumerate(value): redact(item,locations,path+'/'+str(i))


def finalize_halt():
    result=load(OUT/'AUTHORING-RESULT.json')
    assert result['status']=='R6_33_PROTOCOL_HALT' and not result['artifact_keys']
    redactions=[]
    for p in (OUT/'calls/01/stdout.jsonl',OUT/'SESSION-EXPORT.json'):
        original=p.read_bytes()
        raw_path=TEMP/(p.name+'.private-original')
        assert not raw_path.exists()
        raw_path.write_bytes(original)
        values=[json.loads(line) for line in original.decode().splitlines()] if p.suffix=='.jsonl' else [json.loads(original)]
        locations=[]
        for value in values: redact(value,locations)
        text='\n'.join(json.dumps(v,separators=(',',':')) for v in values)+'\n' if p.suffix=='.jsonl' else json.dumps(values[0],indent=2)+'\n'
        p.write_text(text,encoding='utf-8',newline='\n')
        redactions.append(dict(file=p.relative_to(ROOT).as_posix(),original_sha256=sha(raw_path),
            published_sha256=sha(p),redacted_locations=locations,
            original_preserved_outside_publication=True))
    save(OUT/'REDACTION.json',dict(reason='No response cookies/credentials in publication',files=redactions,
        semantic_response_unchanged=True,provider_error_code='credit_balance_exhausted'))
    session=load(OUT/'SESSION-EXPORT.json')
    events=Journal(OUT/'telemetry').recover()
    call=result['model_invocations']
    error=load(OUT/'calls/01/stdout.jsonl')
    save(OUT/'RESULT.json',dict(round='R6.33',classification='R6_33_PROTOCOL_HALT',
        terminal_stage='discovery_transport',http_status=error['error']['data']['statusCode'],
        provider_error_type='insufficient_quota',provider_error_code='credit_balance_exhausted',
        authoring_session_terminated=True,model_selection_unchanged=True,
        lifecycle={name:'NOT_REACHED' for name in ('proposal','admission','retrieval','two_caller_reuse',
            'successor','selective_migration','functional_acceptance','AI_independent_replay')},
        AI_authored_artifacts=0,admitted_definitions=0,executed_observations=0,
        semantic_repairs=0,P6_A04_acceptance=False,P6_A05_access=False))
    save(OUT/'REPLAY.json',dict(classification='R6_33_PROTOCOL_HALT',status='NOT_REACHED',
        reason='No AI-authored/admitted executable artifacts; transport halted first authoring invocation',
        model_calls=0,replay_process_executed=False,executed_observations=0,
        authoring_closed_receipt_sha256=sha(OUT/'AUTHORING-CLOSED.json')))
    save(OUT/'FUNCTIONAL-STATUS.json',dict(status='NOT_REACHED',passed=None,total=None,
        reason='No candidate exists; frozen scorer was not executed and is not qualified by this round'))
    save(OUT/'REGISTRY-STATUS.json',dict(status='initialized_empty',snapshot_files=0,
        definitions=0,admission_calls=0,retrieval_calls=0,migration_calls=0,
        initialization_note='Registry and Journal directories initialized before model call'))
    save(OUT/'MEASUREMENTS.json',dict(
        model_CLI_invocations=call,completed_model_responses=0,provider_HTTP_attempts=None,
        provider_HTTP_attempts_missing_reason='CLI may internally retry429; raw final error does not enumerate requests',
        participant_tool_calls=0,broker_semantic_tool_calls=0,
        input_tokens=None,output_tokens=None,reasoning_tokens=None,cached_read_tokens=None,cached_write_tokens=None,
        token_missing_reason='No step_finish/provider usage; export zero counters are unpopulated failed-session counters',
        exported_session_counters=session['info']['tokens'],exported_cost_counter=session['info']['cost'],
        provider_billing=None,provider_effective_reasoning_configuration=None,provider_effective_tool_definitions=None,
        model_CLI_wall_seconds=load(OUT/'calls/01/MEASUREMENT.json')['wall_seconds'],
        authoring_lifecycle_wall_seconds=result['wall_seconds'],
        workflow_total_wall_seconds=None,coordinator_input_tokens=None,coordinator_output_tokens=None,
        overhead_missing_reason='Coordinator planning/inventory/publication/harness usage and time not instrumented; no fully costed total',
        validation_seconds=None,retrieval_seconds=None,registry_admission_seconds=None,
        unexecuted_stage_times='NOT_REACHED, not zero-duration performance measurements',
        failed_semantic_proposals=0,correction_turns=0,transport_failed_invocations=1,
        telemetry_events=len(events['events']),incomplete_journal_stages=events['incomplete'],
        timing_scope='CLI includes startup, requested inference and any internal transport retries; workflow also includes session export'))
    print('Terminal halt evidence prepared; response cookies redacted')


def verify():
    manifest=load(OUT/'PUBLICATION-IDENTITIES.json')
    receipt=load(OUT/'VERIFICATION.json')
    assert receipt['manifest_sha256']==sha(OUT/'PUBLICATION-IDENTITIES.json')
    pins=protected()
    assert len(pins)==receipt['protected_verified']
    for name,meta in manifest['files'].items():
        p=ROOT/name
        assert sha(p)==meta['sha256'] and p.stat().st_size==meta['bytes'],name
        text=p.read_text(encoding='utf-8')
        assert not any(line.endswith((' ','\t')) for line in text.splitlines()),name
        if p.suffix=='.md':
            for link in re.findall(r'\]\(([^)]+)\)',text):
                if '://' not in link and not link.startswith('#'):
                    assert (p.parent/link.split('#')[0]).resolve().exists(),(name,link)
        assert not re.search(r'"set-cookie"\s*:\s*"(?!<REDACTED_RESPONSE_CREDENTIAL>)',text),name
    for name,pin in load(OUT/'FREEZE.json')['inputs'].items(): assert sha(ROOT/name)==pin,name
    result=subprocess.run(['git','diff','--check'],cwd=ROOT,capture_output=True,text=True)
    assert result.returncode==0,result.stdout+result.stderr
    events=Journal(OUT/'telemetry').recover()
    assert not events['incomplete'] and not events['pending']
    assert load(OUT/'RESULT.json')['classification']=='R6_33_PROTOCOL_HALT'
    assert not list((OUT/'registry').glob('*.json'))
    print('R6.33 independently re-read publication:',len(manifest['files']),'files;',len(pins),
        'protected identities; frozen inputs, links, whitespace, credentials and git diff --check PASS')


if __name__=='__main__':
    {'finalize':finalize_halt,'verify':verify}[sys.argv[1]]()
