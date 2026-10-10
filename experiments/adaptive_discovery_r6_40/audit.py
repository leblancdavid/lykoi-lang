"""Post-score audit only; never repairs artifacts, libraries, or expectations."""
from collections import Counter
import json
import math
import sys
from common import ROOT,OUT,Registry,Journal,c,save,load,normalize,digest
from tasks import TASKS,score
from run import usage

def calls(folder):
    return [e for e in map(json.loads,(folder/'MCP.jsonl').read_text().splitlines()) if e['request']['method']=='tools/call']

def analyze():
    runs={}; ledger=[]; provenance={}; diagnostics=[]; failures=[]; sessions=[]
    vocabulary=load(OUT/'C-VOCABULARY.json')['entries']
    reusable={e['definition']['identity']:e['relation'] for e in vocabulary}
    for name in ['qualification','D1','D2','D3']+[t['id']+'-'+k for t in TASKS for k in ['A','B','C','X']]:
        folder=OUT/name; measured=load(folder/'MEASUREMENT.json'); exported=load(folder/'EXPORT.json')
        rows=[]; all_tokens=[]
        for m in exported['messages']:
            info=m['info']
            if info['role']!='assistant' or 'tokens' not in info: continue
            assert info['modelID']=='gpt-6.1-sol' and info['providerID']=='openai'
            all_tokens.append(dict(tokens=info['tokens']))
            row=dict(run=name,message=info['id'],session=info['sessionID'],usage=info['tokens'],
                created_ms=info['time']['created'],completed_ms=info['time'].get('completed'),
                provider=info['providerID'],model=info['modelID'],message_identity=digest(m),
                exact_upstream_HTTP_calls=None)
            ledger.append(row); rows.append(row)
        exported_usage=usage(all_tokens)
        # Interrupted final message may be unmetered; preserve explicit reconciliation.
        match=exported_usage==measured['tokens']
        if not match: diagnostics.append(dict(run=name,kind='TOKEN_RECONCILIATION',events=measured['tokens'],export=exported_usage))
        sessions.append(measured['session'])
        exchanges=calls(folder); rejected=[e for e in exchanges if e['response']['result']['isError']]
        retrieval=[e for e in exchanges if e['request']['params']['name'] in ['lykoi_library','lykoi_retrieve']]
        tool_names=Counter(e['request']['params']['name'] for e in exchanges)
        assert len(exchanges)==measured['tool_calls'],(name,len(exchanges),measured['tool_calls'])
        reg=Registry(folder/'registry'); state=reg.read()['state']['definitions']
        admitted=[]
        for e in exchanges:
            if e['response']['result']['isError']: continue
            n=e['request']['params']['name']; args=e['request']['params']['arguments']
            if n=='lykoi_admit': ds=args['action']['definitions']
            elif n=='lykoi_propose': ds=[args['definition']]
            else: continue
            for d in ds:
                sealed=c.seal(d); assert state[sealed['identity']]==sealed
                admitted.append(sealed['identity'])
        if name!='qualification':
            spec=load(folder/'SESSION.json')
            seeds={e['definition']['identity']:e['definition'] for e in spec['library'] if 'definition' in e}
            assert all(state[p]==d for p,d in seeds.items())
            assert set(state)==set(seeds)|set(admitted),name
            if spec['phase']=='evaluation':
                assert not tool_names['lykoi_propose'],'evaluation cannot modify vocabulary'
        else: seeds={}
        journal=Journal(folder/'telemetry').recover()
        assert not journal['pending'] and not journal['incomplete']
        validation_events=[e for e in journal['events'] if e['kind']=='admission']
        provenance[name]=dict(model_authored_pins=admitted,seeds_unchanged=True,coordinator_semantic_repairs=0,
            registry_generation=reg.read()['generation'],registry_integrity=True,telemetry_integrity=True)
        for e in rejected: diagnostics.append(dict(run=name,kind='REJECTED_TOOL',exchange=e))
        metrics=dict(tokens=measured['tokens'],export_usage=exported_usage,usage_reconciled=match,
            model_completions=measured['completions'],MCP_calls=len(exchanges),tool_names=dict(tool_names),
            retrieval_calls=len(retrieval),retrieval_seconds=sum(e['wall_seconds'] for e in retrieval),
            retrieval_response_bytes=sum(len(json.dumps(e['response']['result']).encode()) for e in retrieval),
            retrieval_tokens_provider_exact=None,retrieval_token_local_estimate=sum(math.ceil(len(json.dumps(e['response']['result']))/4) for e in retrieval),
            MCP_seconds=sum(e['wall_seconds'] for e in exchanges),rejected_calls=len(rejected),
            registry_calls=len([e for e in journal['events'] if e['kind'] in ('admission','retrieval')]),
            registry_admission_seconds=sum(e['data']['tool_seconds'] for e in validation_events),
            validation_MCP_calls=tool_names['lykoi_validate'],execution_MCP_calls=tool_names['lykoi_execute'],
            validation_MCP_seconds=sum(e['wall_seconds'] for e in exchanges if e['request']['params']['name']=='lykoi_validate'),
            execute_MCP_seconds=sum(e['wall_seconds'] for e in exchanges if e['request']['params']['name']=='lykoi_execute'),
            participant_wall_seconds=measured['wall_seconds'],budget_stop=measured['budget_stop'],
            token_cap_exceeded=measured['token_cap_exceeded'],actual_API_billing=None,
            SDK_reported_cost=sum(p.get('cost',0) for p in measured['step_finishes']))
        if name.startswith('E'):
            result=load(sorted(folder.glob('ACCEPTANCE-*.json'))[-1]); first=load(folder/'ACCEPTANCE-1.json')
            library_paths=[(path,meta['definition']) for path,meta in result['expansion']['map'].items()
                if meta['local']=='region' and meta['definition'] in reusable]
            reuse_counts=Counter(reusable[pin] for path,pin in library_paths)
            bad=[r for r in result['rows'] if not r['passed']]
            offset_only=[]
            for r in bad:
                expected=r['case']['expected']; err=r['actual'].get('error',{})
                offset_only.append(isinstance(expected,list) and r['actual'].get('status')=='reject'
                    and err.get('code')==expected[0] and err.get('stage')=='validation' and err.get('offset')!=expected[1])
            if bad:
                failures.append(dict(run=name,count=len(bad),all_failures_offset_only=all(offset_only),
                    samples=bad[:4],candidate_repaired_after_acceptance=False))
            metrics.update(first_passed=first['all_passed'],final_passed=result['all_passed'],
                observations=result['total'],passed_observations=result['passed'],
                validation_lowering_seconds=result['validation_seconds'],scored_execution_seconds=result['execution_seconds'],
                acceptance_wall_seconds=result['wall_seconds'],submissions=len(list(folder.glob('SUBMISSION-*.json'))),
                semantic_revisions=max(0,len(list(folder.glob('SUBMISSION-*.json')))-1),
                learned_reuse=dict(reuse_counts),full_successful_transfer=dict(reuse_counts) if result['all_passed'] else {},
                successful_inputs=sum(r['actual'].get('status')=='success' for r in result['rows']),
                dynamic_reuse_evidence='Ordered branch-free foundation: all compose regions entered on each successful execution',
                values_and_codes_pass_ignoring_offset=all(offset_only) if bad else True)
            # A second independent fresh reload/replay also reproduces failed scores.
            task=next(t for t in TASKS if t['id']==name.split('-')[0])
            second=normalize(score(Registry(folder/'registry'),result['root'],task,load(OUT/(task['id']+'-EXPECTATIONS.json'))))
            assert all(second[k]==result[k] for k in ('rows','expansion','root','closure'))
            save(folder/'REPLAY-SECOND.json',second)
        runs[name]=metrics
    assert len(sessions)==len(set(sessions))==28
    totals={}
    numeric=['model_completions','MCP_calls','retrieval_calls','retrieval_seconds','retrieval_response_bytes','MCP_seconds',
        'rejected_calls','registry_calls','registry_admission_seconds','validation_MCP_calls','execution_MCP_calls',
        'validation_MCP_seconds','execute_MCP_seconds','participant_wall_seconds','SDK_reported_cost']
    for k in ['A','B','C','X','DISCOVERY','QUALIFICATION']:
        chosen=[v for n,v in runs.items() if (n.startswith('E') and n.endswith('-'+k)) or
            (k=='DISCOVERY' and n in ('D1','D2','D3')) or (k=='QUALIFICATION' and n=='qualification')]
        total={key:sum(v[key] for v in chosen) for key in numeric}
        total['tokens']=dict(sum((Counter(v['tokens']) for v in chosen),Counter()))
        if k in ['A','B','C','X']:
            total.update(first_passed=sum(v['first_passed'] for v in chosen),final_passed=sum(v['final_passed'] for v in chosen),
                observations=sum(v['observations'] for v in chosen),passed_observations=sum(v['passed_observations'] for v in chosen),
                budget_stops=sum(v['budget_stop'] for v in chosen),
                semantic_revisions=sum(v['semantic_revisions'] for v in chosen),
                validation_lowering_seconds=sum(v['validation_lowering_seconds'] for v in chosen),
                scored_execution_seconds=sum(v['scored_execution_seconds'] for v in chosen),
                acceptance_wall_seconds=sum(v['acceptance_wall_seconds'] for v in chosen))
        totals[k]=total
    save(OUT/'MEASUREMENTS.json',dict(runs=runs,totals=totals,fully_accounted_effort=False,
        coordinator_tokens=None,API_billing=None,hidden_provider_retries=None,tokenizer=None,
        timing='Participant wall includes initialization/inference/MCP; export and scorer run afterward. MCP/registry/validation overlap participant wall; do not add them again.',
        cache_tokens_not_free=True,SDK_zero_cost_not_actual_free_billing=True))
    save(OUT/'REQUEST-LEDGER.json',dict(rows=sorted(ledger,key=lambda r:(r['created_ms'],r['message'])),
        visible_author_completions_only=True,exact_HTTP_requests=None,coordinator_usage=None))
    save(OUT/'PROVENANCE.json',provenance); save(OUT/'FAILURES-AND-DIAGNOSTICS.json',dict(functional=failures,tool_and_telemetry=diagnostics))
    rejected_proposals=[p for p in load(OUT/'PROPOSALS.json') if p['response']['result']['isError']]
    save(OUT/'REJECTED-ABSTRACTIONS.json',dict(entries=rejected_proposals,count=len(rejected_proposals),invented_rejections=False))
    body_steps={k:sum(len(e['definition']['steps']) for e in load(OUT/(k+'-VOCABULARY.json'))['entries']) for k in ('B','C')}
    docs_bytes={k:sum(len(c.canonical({x:e.get(x) for x in ('semantics','non_applicability')}))
        for e in load(OUT/(k+'-VOCABULARY.json'))['entries']) for k in ('B','C')}
    tolerance=max(1,0.1*body_steps['C'])
    save(OUT/'CONTROL-LIMITATIONS.json',dict(human_library=False,owner_authorized_AI_proxy=True,
        proxy_pre_discovery_freeze=True,proxy_evaluation_results_seen=False,coordinator_knows_planned_design=True,
        per_entry_step_matching=load(OUT/'B-VOCABULARY.json')['capacity_matched'],total_body_steps=body_steps,
        total_step_capacity_matched=abs(body_steps['B']-body_steps['C'])<=tolerance,total_step_tolerance=tolerance,
        applicability_document_bytes=docs_bytes,docs_within_10_percent=abs(docs_bytes['B']-docs_bytes['C'])<=0.1*docs_bytes['C'],
        exact_document_provider_tokens=None,all_signature_multisets_and_nesting_matched=True,
        task_oracle_ambiguity='Task text names derived check sites but does not explicitly require byte-origin offsets across compose/seq boundaries. Frozen oracle expects origin offsets; unchanged VM gives completed seq-result its region span. Preserve original failed scores; source-offset attribution underdetermined.',
        protocol_pre_selection_claim='Proxy pool froze before evaluation files were authored, but coordinator already knew planned task skeletons. No cognitively blind control-design claim.',
        E4_B_token_limit='Observed processed input+output crossed48000 after a sealed candidate; whole child tree stopped, no retry. Budget stop is not a server/provider error.'))
    discovery=totals['DISCOVERY']; amortization={}
    successful_reuses=sum(sum(v.get('full_successful_transfer',{}).values()) for n,v in runs.items() if n.endswith('-C'))
    for reference in ('A','B','X'):
        input_savings=totals[reference]['tokens']['processed_input']-totals['C']['tokens']['processed_input']
        output_savings=totals[reference]['tokens']['output']-totals['C']['tokens']['output']
        token_savings=input_savings+output_savings
        seconds_savings=totals[reference]['participant_wall_seconds']-totals['C']['participant_wall_seconds']
        amortization[reference]=dict(evaluation_processed_input_savings=input_savings,evaluation_output_savings=output_savings,
            evaluation_processed_plus_output_savings=token_savings,
            per_full_successful_reuse_savings=token_savings/successful_reuses if successful_reuses else None,
            token_break_even_reuses=math.ceil((discovery['tokens']['processed_input']+discovery['tokens']['output'])/
                (token_savings/successful_reuses)) if token_savings>0 and successful_reuses else None,
            measured_evaluation_wall_savings=seconds_savings,
            C_discovery_charged_net_wall_savings=seconds_savings-discovery['participant_wall_seconds'],
            C_discovery_charged_net_token_savings=token_savings-discovery['tokens']['processed_input']-discovery['tokens']['output'],
            missing_full_effort_and_billing_prevent_economic_break_even=True,
            matched_success_comparison=False if reference in ('A','X') else True)
    per_entry=[]
    for t,e in zip(['D1','D2','D3'],vocabulary):
        use=[n for n,v in runs.items() if n.endswith('-C') and e['relation'] in v.get('learned_reuse',{})]
        transferred=[n for n in use if runs[n]['final_passed']]
        per_entry.append(dict(relation=e['relation'],identity=e['definition']['identity'],discovery_tokens=runs[t]['tokens'],
            discovery_wall_seconds=runs[t]['participant_wall_seconds'],static_reuse_tasks=use,
            full_successful_transfer_tasks=transferred,total_static_references=sum(runs[n]['learned_reuse'][e['relation']] for n in use)))
    save(OUT/'AMORTIZATION.json',dict(discovery_cost=discovery,entries=per_entry,
        full_successful_reuses=successful_reuses,comparisons=amortization,
        X_discovery_charged_tokens=dict(Counter(totals['X']['tokens'])+Counter(discovery['tokens'])),
        C_discovery_charged_tokens=dict(Counter(totals['C']['tokens'])+Counter(discovery['tokens'])),
        X_discovery_charged_wall_seconds=totals['X']['participant_wall_seconds']+discovery['participant_wall_seconds'],
        C_discovery_charged_wall_seconds=totals['C']['participant_wall_seconds']+discovery['participant_wall_seconds'],
        discovery_allocated_to_C_and_X_separately_not_split=True,net_economic_advantage_established=False))
    save(OUT/'RESULT.json',dict(round='R6.40',classification='R6_40_COMPARISON_INCONCLUSIVE',
        proposed=3,admitted=3,rejected=0,fully_accepted_transfer_relations=2,full_combination_transfer=False,
        correctness={k:totals[k]['final_passed'] for k in ['A','B','C','X']},tasks_per_condition=6,
        negative_transfer={k:sum(runs[t['id']+'-'+k]['final_passed'] for t in TASKS if t['kind']=='negative') for k in ['A','B','C','X']},
        advantage_beyond_human_macros=False,human_control_unavailable=True,fully_accounted_efficiency=False,
        source_offset_contract_ambiguity=True,exploratory=True,hidden_context_separation_attested=False,
        AI_independent_replay_passes=2,all28_visible_sessions_distinct=True,kernel=26,
        production_and_semantic_machinery_unchanged=True,full_R6_31_study=False,model_training=False,
        P6_A04_acceptance=False,P6_A05_access=False,stopped_after_publication=True))
    print(json.dumps(dict(totals=totals,body_steps=body_steps,document_bytes=docs_bytes,
        amortization=amortization,entries=per_entry,failures=failures),indent=2))

if __name__=='__main__': analyze()
