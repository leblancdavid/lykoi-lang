"""Read-only offline attribution and additive publication integrity."""
from collections import Counter
import hashlib
import json
import math
import re
import subprocess
import sys
from transport import ROOT, HERE, OUT, TOOLS, AGENT_PROMPT, c, Registry, Journal, load, save, raw, sha

CLASSIFICATION='R6_37_LIFECYCLE_SUPPORTED_ATTRIBUTION_PARTIAL'


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(',',':'), ensure_ascii=True)


def tally(parts):
    counts=Counter()
    for p in parts:
        t=p['tokens']
        for k in ('input','output','reasoning','total'):
            counts[k]+=t.get(k,0)
        for k in ('read','write'):
            counts['cache_'+k]+=t['cache'][k]
    counts['processed_input']=counts['input']+counts['cache_read']+counts['cache_write']
    return dict(counts)


def accounting():
    catalog={}; ledger=[]; phase_counts=Counter()

    def section(category, text, label):
        text_hash=hashlib.sha256(text.encode()).hexdigest()
        identity=category+':'+text_hash
        if identity not in catalog:
            catalog[identity]=dict(category=category,label=label,characters=len(text),
                local_estimated_tokens=math.ceil(len(text)/4),text_sha256=text_hash,
                content=text)
        return identity

    a=section('A',AGENT_PROMPT,'Configured participant agent instructions; other system instructions unknown')
    b=section('B',(OUT/'GUIDE.txt').read_text().rstrip('\n'),'Supplied semantic guide')
    schemas=section('C',encode(TOOLS),'Actual tools/list names/descriptions/schemas; upstream serialization unknown')
    base=(OUT/'REQUIREMENT.txt').read_text().rstrip('\n')
    mod=(OUT/'MODIFICATION.txt').read_text().rstrip('\n')
    dbase=section('D',base,'Original requirement')
    dmod=section('D',mod,'Staged modification')
    pre=load(OUT/'PREFLIGHT-RESULT.json')
    neutral_a=section('A','Follow the neutral request. Do not use tools.','Neutral configured instructions')
    neutral_d=section('D',(OUT/'NEUTRAL-PROMPT.txt').read_text().rstrip('\n'),'Tiny neutral request')

    def row(phase,stage,info,ids,generated,toolcalls,wall=None):
        phase_counts[phase]+=1
        estimates=Counter()
        for identity in ids:
            item=catalog[identity]; estimates[item['category']]+=item['local_estimated_tokens']
        for k in ('A','B','C','D','E','F'):
            estimates.setdefault(k,0)
        reported=info['tokens']
        processed=reported['input']+reported['cache']['read']+reported['cache']['write']
        elapsed=None
        if info.get('time',{}).get('completed') is not None:
            elapsed=(info['time']['completed']-info['time']['created'])/1000
        ledger.append(dict(sequence=len(ledger)+1,phase=phase,stage=stage,
            phase_sequence=phase_counts[phase],message_id=info.get('id',info.get('messageID')),
            provider=info.get('providerID','openai'),model=info.get('modelID','gpt-6.1-sol'),
            requested_reasoning='high',provider_reported_usage=reported,
            provider_processed_input=processed,model_calls=1,MCP_tool_calls=toolcalls,
            input_payload_section_identities=ids,local_input_estimates_by_section=dict(estimates),
            local_generated_G_estimated_tokens=sum(catalog[i]['local_estimated_tokens'] for i in generated),
            generated_section_identities=generated,
            H_reported_reasoning_tokens=reported.get('reasoning'),
            I_reported_cached_tokens=reported['cache']['read'],
            J_unattributed_provider_minus_local_estimate=processed-sum(estimates.values()),
            reconciliation='Signed estimate residual, not inferred hidden-token count. '
                'Repeated schemas are a local hypothesis, not attested request serialization.',
            local_output_residual=reported['output']-sum(catalog[i]['local_estimated_tokens'] for i in generated),
            provider_bucket_sum_matches_total=reported.get('total')==processed+reported['output']+reported['reasoning'],
            inference_seconds=None,provider_inference_timing_missing=True,
            assistant_message_interval_seconds=elapsed,CLI_stage_wall_seconds=wall,
            input_history_subtotal_estimate=sum(estimates[k] for k in ('B','D','E','F')),
            attribution_confidence='Low for section token estimates; actual usage buckets are directly observed'))

    for finish in pre['step_finishes']:
        g=section('G','NEUTRAL_OK','Neutral output')
        row('preflight','neutral',finish,[neutral_a,neutral_d],[g],0,pre['wall_seconds'])
    for phase,export_path in [('qualification',OUT/'qualification/live/EXPORT.json'),
            ('authoring',OUT/'authoring/modification/EXPORT.json')]:
        exported=load(export_path); history=[]; stage='neutral-semantic'
        for message in exported['messages']:
            info=message['info']
            if info['role']=='user':
                text='\n'.join(p['text'] for p in message['parts'] if p['type']=='text')
                if phase=='authoring':
                    if text.rstrip('\n')==mod:
                        assert stage=='original'
                        stage='modification'; history.append(dmod)
                    else:
                        assert text.rstrip('\n')==(OUT/'GUIDE.txt').read_text()+'\n'+base
                        stage='original'; history.extend([b,dbase])
                else:
                    history.append(section('D',text,'Neutral semantic qualification request'))
                continue
            if info['role']!='assistant' or 'tokens' not in info:
                continue
            generated=[]; feedback=[]; prior_outputs=[]; toolcalls=0
            for part in message['parts']:
                if part['type']=='text':
                    generated.append(section('G',part['text'],'New model text'))
                    prior_outputs.append(section('E',part['text'],'Prior model text in conversation history'))
                elif part['type']=='tool':
                    toolcalls+=1
                    text=encode(dict(tool=part['tool'],arguments=part['state']['input']))
                    generated.append(section('G',text,'New model MCP name and arguments'))
                    prior_outputs.append(section('E',text,'Prior model MCP name and arguments'))
                    output=part['state'].get('output',part['state'].get('error',''))
                    feedback.append(section('F',output if isinstance(output,str) else encode(output),
                        'MCP result or diagnostic in history'))
                # Reasoning content is deliberately excluded; only usage count is recorded.
            row(phase,stage,info,[a,schemas]+history,generated,toolcalls)
            history.extend(prior_outputs+feedback)
    save(OUT/'SECTION-CATALOG.json',dict(estimator='ceil(characters/4), no tokenizer/provider calls',
        categories='A/B/C/D/E/F exclusive input origin labels; G new output only; H/I usage counters; J signed residual',
        repeated_output_policy='Each generated payload is G only in its generating call, E only in later inputs; '
            'tool responses are F only. No G+E double count within one call. Unique-volume totals deduplicate hashes.',
        sections=catalog))
    save(OUT/'TOKEN-LEDGER.json',dict(calls=ledger,exact_request_serialization=False,
        hidden_instruction_contents_inferred=False,reasoning_contents_inferred=False,
        repeated_schema_processing_attested=False,provider_usage_separate_from_estimates=True))
    groups={}
    for phase,stage in sorted({(r['phase'],r['stage']) for r in ledger}):
        rows=[r for r in ledger if (r['phase'],r['stage'])==(phase,stage)]
        estimates=Counter()
        for r in rows:
            estimates.update(r['local_input_estimates_by_section'])
        groups[phase+'/'+stage]=dict(completions=len(rows),MCP_calls=sum(r['MCP_tool_calls'] for r in rows),
            reported=tally([{'tokens':r['provider_reported_usage']} for r in rows]),
            repeated_local_input_estimates=dict(estimates),
            generated_G_estimate=sum(r['local_generated_G_estimated_tokens'] for r in rows),
            input_growth=[r['provider_processed_input'] for r in rows],
            assistant_message_intervals_seconds=[r['assistant_message_interval_seconds'] for r in rows])
    scored=[r for r in ledger if r['phase']=='authoring']
    unique_ids={i for r in scored for i in r['input_payload_section_identities']+r['generated_section_identities']}
    unique=Counter()
    # Category G and E may share exact content identities; classify unique generated
    # bodies as construction once, independent of their later history role.
    seen=set()
    for i in sorted(unique_ids):
        item=catalog[i]
        if item['text_sha256'] in seen:
            continue
        seen.add(item['text_sha256'])
        category='G' if item['category']=='E' else item['category']
        unique[category]+=item['local_estimated_tokens']
    analysis=dict(per_stage=groups,unique_visible_content_estimates=dict(unique),
        scored_first_processed_input=scored[0]['provider_processed_input'],
        scored_last_processed_input=scored[-1]['provider_processed_input'],
        schema_unique_local_estimate=catalog[schemas]['local_estimated_tokens'],
        guide_unique_local_estimate=catalog[b]['local_estimated_tokens'],
        fixed_agent_unique_local_estimate=catalog[a]['local_estimated_tokens'],
        schema_repeat_count_hypothesis=len(scored),
        hypotheses={'E1':'Not established: exact fixed context and repeated provider schema serialization unavailable',
            'E2':'Visible-history growth and large tool retrieval/validation feedback are consistent with construction '
                'overhead; semantic reasoning effort cannot be isolated from these counts',
            'dominant_cause':'Inconclusive at provider-token attribution level; local section volumes only'},
        caching='Reported cache-read tokens show reused processing. Actual price/cost savings and cache-category allocation unknown.',
        complexity_scaling='Two sequential lifecycle stages in one task cannot establish proportional complexity scaling; '
            'stage, history, retrieval size and caching are confounded',
        billing_USD=None,provider_serialization=None,system_overhead=None,
        local_estimate_warning='Signed residuals may be negative. This estimator cannot support exact percentages or hidden-context claims.')
    save(OUT/'TOKEN-ANALYSIS.json',analysis)
    print(json.dumps(analysis,indent=2))


def records():
    accounting()
    closed=load(OUT/'AUTHORING-CLOSED.json')
    assert closed['failure'] is None
    functional=load(OUT/'FUNCTIONAL.json'); original=load(OUT/'ORIGINAL-ACCEPTANCE.json')
    replay=load(OUT/'REPLAY.json')
    exchanges=[json.loads(line) for line in (OUT/'authoring/MCP.jsonl').read_text().splitlines()]
    calls=[r for r in exchanges if r['request']['method']=='tools/call']
    failures=[r for r in calls if r['response']['result']['isError']]
    assert not failures
    proposals=[]
    state=Registry(OUT/'authoring/registry').read()['state']
    for call in calls:
        if call['request']['params']['name']=='lykoi_admit':
            action=call['request']['params']['arguments']['action']
            if action['action']=='admit':
                for d in action['definitions']:
                    sealed=c.seal(d)
                    assert state['definitions'][sealed['identity']]==sealed
                    proposals.append(dict(identity=sealed['identity'],exact_raw_model_semantics=True))
    assert len(proposals)==5
    ledger=load(OUT/'TOKEN-LEDGER.json')['calls']
    scored=[r for r in ledger if r['phase']=='authoring']
    assert len(scored)==sum(len(call['step_finishes']) for call in closed['calls'])
    assert sum(r['MCP_tool_calls'] for r in scored)==len(calls)==38
    assert tally([{'tokens':r['provider_reported_usage']} for r in scored])==tally(
        [p for call in closed['calls'] for p in call['step_finishes']])
    first_export=load(OUT/'authoring/original/EXPORT.json')
    assert not any((OUT/'MODIFICATION.txt').read_text().strip() in p.get('text','')
        for m in first_export['messages'] for p in m['parts'])
    journal=Journal(OUT/'authoring/telemetry').recover()
    counts=Counter(e['kind'] for e in journal['events'])
    timing={k:sum(e['data'].get('tool_seconds',0) for e in journal['events'] if e['kind']==k)
        for k in ('admission','retrieval')}
    metrics=dict(classification=CLASSIFICATION,original_acceptance={'passed':original['passed'],'total':original['total']},
        functional_acceptance={'passed':functional['passed'],'total':functional['total']},
        replay=replay['runs'],actual_MCP_semantic_authoring=True,abstraction_reused=True,
        first_attempt_admissions=5,rejected_scored_calls=len(failures),correction_turns=0,
        model_completions=len(scored),MCP_calls=len(calls),CLI_invocations=2,
        authoring_usage=tally([{'tokens':r['provider_reported_usage']} for r in scored]),
        preflight_and_qualification_usage=tally([{'tokens':r['provider_reported_usage']} for r in ledger if r['phase']!='authoring']),
        authoring_wall_seconds=closed['wall_seconds'],CLI_intervals=[r['wall_seconds'] for r in closed['calls']],
        registry_event_counts=dict(counts),registry_timing_seconds=timing,
        original_validation_expansion_seconds=sum(x['validation_seconds'] for x in original['expansions'].values()),
        final_validation_expansion_seconds=sum(x['validation_seconds'] for x in functional['expansions'].values()),
        original_acceptance_seconds=original['wall_seconds'],final_acceptance_seconds=functional['wall_seconds'],
        semantic_MCP_dispatch_seconds=sum(r['wall_seconds'] for r in calls),
        timing_overlap='CLI includes tool calls, admission includes validation, acceptance includes expansion; do not sum overlaps',
        inference_seconds=None,billing_USD=None,provider_HTTP_attempts=None,effective_authentication=None,
        effective_reasoning=None,exact_request_serialization=None,coordinator_usage=None,
        attribution_confidence='Partial; observed usage exact as exposed by SDK, section estimates low confidence',
        staged_modification_withheld_in_observed_participant_session=True,
        hidden_context_exclusion_attested=False,budget_within_observed_limits=True,
        total_completion_budget_hard_enforced_within_stage=False)
    save(OUT/'MEASUREMENTS.json',metrics)
    save(OUT/'PROVENANCE.json',dict(proposals=proposals,passed=True,coordinator_semantic_repairs=0,
        only_mechanical_seal=True,actual_MCP_exchange_matches_artifacts=True,
        final_registry=state,staged_modification_absent_from_original_export=True))
    save(OUT/'RESULT.json',dict(round='R6.37',classification=CLASSIFICATION,kernel=26,
        actual_MCP_authoring_succeeded=True,fresh_task_transfer_supported_bounded=True,
        functional_acceptance_passed=True,replay_passed=True,token_attribution_partial=True,
        full_comparative_study=False,P6_A04_acceptance=False,P6_A05_access=False,
        stopped_after_one_attempt=True))
    print(json.dumps(metrics,indent=2))


def paths():
    result=[p for folder in (HERE,OUT) for p in folder.rglob('*') if p.is_file()
        and '__pycache__' not in p.parts and p.name not in ('PUBLICATION-IDENTITIES.json','VERIFICATION.json')]
    result += [ROOT/'benchmark/results/phase6/R6_37-REPORT.md']
    result += [ROOT/f'docs/{stem}-r6.37.md' for stem in ('project-overview','research-log','decisions')]
    return sorted(result)


def supplemental_checks():
    original=load(OUT/'ORIGINAL-ACCEPTANCE.json'); final=load(OUT/'FUNCTIONAL.json')
    replay=[load(OUT/f'REPLAY-{n}.json') for n in (1,2,3)]
    expected={k:v['expansion'] for k,v in final['expansions'].items()}
    assert all({k:v['expansion'] for k,v in run['expansions'].items()}==expected for run in replay)
    assert all(run['identities']==final['identities'] for run in replay)
    assert all(run['rows']==final['rows'] for run in replay)
    journal=Journal(OUT/'authoring/telemetry').recover()
    assert not journal['pending'] and not journal['incomplete']
    sizes={}
    for key in ('old','new','a','b','a_new'):
        d=load(OUT/(key+'.json'))
        assert d['identity']==final['identities'][key]==c.identity(d)
        proposal={k:v for k,v in d.items() if k!='identity'}
        sizes[key]=dict(identity=d['identity'],canonical_symbolic_bytes=len(c.canonical(d)),
            model_definition_characters=len(encode(proposal)),
            local_definition_token_estimate=math.ceil(len(encode(proposal))/4),
            steps=len(d['steps']))
    save(OUT/'SUPPLEMENTAL-INTEGRITY.json',dict(passed=True,
        full_expansion_plans_maps_identities_equal_across_three_replays=True,
        complete_result_envelopes_equal_to_frozen_final_acceptance=True,
        journal_complete=True,symbolic_artifacts=sizes,
        definitions_estimated_tokens=sum(s['local_definition_token_estimate'] for s in sizes.values()),
        definitions_estimates_are_not_provider_output_attribution=True,
        corrected_intermediate_commentary='Original acceptance is448/448; an intermediate message stated456/456. '
            'Saved evidence and final report use448; no evidence was changed.'))
    print(json.dumps(sizes,indent=2))


def verify(publish=False):
    pins=load(OUT/'BASELINE.json')['protected_files']
    for name,pin in pins.items():
        assert sha(ROOT/name)==pin,name
    for record in ('PREFLIGHT-FREEZE.json','QUALIFICATION-FREEZE.json','TASK-FREEZE.json'):
        for name,pin in load(OUT/record)['inputs'].items():
            assert sha(ROOT/name)==pin,name
    for p in paths():
        text=p.read_text(encoding='utf-8')
        assert not any(line.endswith((' ','\t')) for line in text.splitlines()),p
        if p.suffix=='.json':
            json.loads(text)
        if p.suffix=='.jsonl':
            for line in text.splitlines():
                json.loads(line)
        assert not re.search(r'\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}',text),p
        assert not re.search(r'\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+',text),p
        if p.suffix=='.md':
            for link in re.findall(r'\]\(([^)]+)\)',text):
                if '://' not in link and not link.startswith('#'):
                    assert (p.parent/link.split('#')[0]).resolve().exists(),(p,link)
    subprocess.run(['git','diff','--check'],cwd=ROOT,check=True)
    assert not subprocess.check_output(['git','diff','--name-only','HEAD'],cwd=ROOT,text=True).strip()
    manifest=OUT/'PUBLICATION-IDENTITIES.json'
    if publish:
        save(manifest,dict(round='R6.37',files={p.relative_to(ROOT).as_posix():
            dict(sha256=sha(p),bytes=p.stat().st_size) for p in paths()}))
        save(OUT/'VERIFICATION.json',dict(passed=True,kernel=26,classification=CLASSIFICATION,
            protected_count=len(pins),publication_files=len(paths()),manifest_sha256=sha(manifest),
            tracked_files_unchanged=True,git_diff_check=True,freezes_preserved=True,
            sensitive_credentials_not_published=True,stopped_after_publication=True))
    receipt=load(OUT/'VERIFICATION.json')
    assert receipt['manifest_sha256']==sha(manifest)
    entries=load(manifest)['files']
    assert set(entries)=={p.relative_to(ROOT).as_posix() for p in paths()}
    for name,meta in entries.items():
        assert sha(ROOT/name)==meta['sha256'] and (ROOT/name).stat().st_size==meta['bytes'],name
    print('R6.37 publication verified:',len(pins),'protected identities;',len(paths()),'publication files')


if __name__=='__main__':
    if sys.argv[1]=='records':
        records()
    elif sys.argv[1]=='supplement':
        supplemental_checks()
    else:
        verify(sys.argv[1]=='publish')
