"""Post-authoring evidence reconciliation and additive publication integrity."""
from collections import Counter
import json
import math
import re
import subprocess
import sys
from common import ROOT,HERE,OUT,load,save,sha,digest,c,Registry,Journal
from tasks import TASKS,requirement,modification,artifacts

def tally(parts):
    result=Counter()
    for p in parts:
        t=p['tokens']
        for k in ('input','output','reasoning'): result[k]+=t.get(k,0)
        for k in ('read','write'): result['cache_'+k]+=t.get('cache',{}).get(k,0)
    result['processed_input']=result['input']+result['cache_read']+result['cache_write']
    return dict(result)

def accounting():
    runs={}; ledger=[]; provenance={}; audit={}; manifests={}; sessions=[]
    for t in TASKS:
        base=OUT/(t['id']+'-BASE'); audit[t['id']]=load(base/'CONTEXT-AUDIT.json')
        for track in ('BASE','A','B','C'):
            name=t['id']+'-'+track; folder=OUT/name; closed=load(folder/'CLOSED.json')
            assert not closed['failure']; messages={}
            for call in closed['calls']:
                assert call['returncode']==0 and not call['errors'] and not call['timeout']
                exported=load(folder/call['stage']/'EXPORT.json')
                for m in exported['messages']: messages[m['info']['id']]=m
            rows=[]
            for m in messages.values():
                info=m['info']
                if info['role']!='assistant' or 'tokens' not in info: continue
                assert info['modelID']=='gpt-6.1-sol' and info['providerID']=='openai'
                row=dict(run=name,message_id=info['id'],session=info['sessionID'],usage=info['tokens'],
                    created_ms=info['time']['created'],completed_ms=info['time']['completed'],
                    model=info['modelID'],provider=info['providerID'],visible_message_identity=digest(m),
                    exact_upstream_request=False,tokenizer=None)
                rows.append(row); ledger.append(row)
            usage=tally([{'tokens':r['usage']} for r in rows])
            assert usage==tally([p for call in closed['calls'] for p in call['step_finishes']])
            stage_sessions={call['session'] for call in closed['calls']}; assert len(stage_sessions)==1
            sessions.extend(stage_sessions)
            exchanges=[json.loads(line) for line in (folder/'MCP.jsonl').read_text().splitlines()]
            calls=[e for e in exchanges if e['request']['method']=='tools/call']
            exported_tool_count=sum(p['type']=='tool' for m in messages.values() for p in m['parts'])
            assert len(calls)==exported_tool_count==sum(call['tool_calls'] for call in closed['calls'])
            retrieval=[e for e in calls if e['request']['params']['name'] in ('lykoi_retrieve','lykoi_detail','lykoi_context')]
            rejected=[e for e in calls if e['response']['result']['isError']]
            result=load(sorted(folder.glob('ACCEPTANCE-*.json'))[-1]); assert result['all_passed']
            original=load(sorted(base.glob('ACCEPTANCE-*.json'))[-1]); preserved=[r for r in result['rows'] if r['root'] in ('a','b')]
            assert preserved==original['rows']
            final=track!='BASE'; ds=artifacts(Registry(folder/'registry'),t,final)
            accepted=[]; state=Registry(folder/'registry').read()['state']
            for call in calls:
                if call['request']['params']['name']=='lykoi_admit' and not call['response']['result']['isError']:
                    action=call['request']['params']['arguments']['action']
                    if action['action']=='admit':
                        for d in action['definitions']:
                            sealed=c.seal(d); assert state['definitions'][sealed['identity']]==sealed
                            accepted.append(sealed['identity'])
            assert len(accepted)==(2 if final else 3)
            inherited={p:d for p,d in Registry(base/'registry').read()['state']['definitions'].items()}
            assert all(state['definitions'][p]==d for p,d in inherited.items())
            provenance[name]=dict(model_admitted_definitions_after_mechanical_sealing=accepted,
                inherited_definitions_unchanged=True,coordinator_semantic_repairs=0,
                exact_pins_and_total_migration=final,caller_successor_pin_only=final,identities=result['identities'])
            journal=Journal(folder/'telemetry').recover(); assert not journal['pending'] and not journal['incomplete']
            changed_rows=[r for r in result['rows'] if r['root']=='a_new']
            old_by_hex={r.get('input_hex'):r for r in original['rows'] if r['root']=='a' and 'input_hex' in r}
            required_differences=sum(r['expected']!=old_by_hex[r['input_hex']]['expected'] for r in changed_rows if 'input_hex' in r)
            context_seconds=0 if track=='BASE' else audit[t['id']][{'A':'history_seconds','B':'summary_seconds','C':'snapshot_generation_verification_seconds'}[track]]
            runs[name]=dict(usage=usage,model_completions=len(rows),MCP_calls=len(calls),retrieval_calls=len(retrieval),
                context_retrieval_calls=sum(e['request']['params']['name']=='lykoi_context' for e in retrieval),
                retrieval_response_local_estimate=sum(math.ceil(len(json.dumps(e['response']['result']))/4) for e in retrieval),
                retrieval_seconds=sum(e['wall_seconds'] for e in retrieval),rejected_MCP_calls=len(rejected),
                acceptance_repair_turns=len(closed['calls'])-1,development_wall_seconds=closed['wall_seconds'],
                CLI_wall_seconds=sum(call['wall_seconds'] for call in closed['calls']),
                context_generation_seconds=context_seconds,participant_plus_context_seconds=closed['wall_seconds']+context_seconds,
                passed=result['passed'],total=result['total'],preserved_original_observations=len(preserved),
                modified_caller_observations=len(changed_rows),required_changed_observations=required_differences,
                passing_to_failing_regressions=sum(not r['passed'] for r in preserved),
                validation_lowering_seconds=sum(v['validation_seconds'] for v in result['expansions'].values()),
                functional_execution_seconds=result['execution_seconds'],acceptance_wall_seconds=result['wall_seconds'],
                SDK_cost_field_sum=sum(p.get('cost',0) for call in closed['calls'] for p in call['step_finishes']),
                actual_API_billing=None,tool_names=dict(Counter(e['request']['params']['name'] for e in calls)),
                missing_information_retrieval_errors=[e['response']['result'] for e in rejected if e in retrieval])
            assert len(rows)<=20 and len(calls)<=40 and closed['wall_seconds']<=600
        history=load(OUT/(t['id']+'-A')/'HISTORY.json')
        assert modification(t) not in json.dumps(history)
        manifests[t['id']]=dict(history_identity=digest(history),history_file=f"{t['id']}-A/HISTORY.json",
            source_exports=[dict(file=(base/call['stage']/'EXPORT.json').relative_to(OUT).as_posix(),sha256=sha(base/call['stage']/'EXPORT.json')) for call in load(base/'CLOSED.json')['calls']],
            all_relevant_messages=[dict(id=m['info']['id'],role=m['info']['role'],sha256=digest(m)) for m in history['messages']],
            construction_feedback=(base/'MCP.jsonl').relative_to(OUT).as_posix(),
            exclusions='Session metadata outside messages; raw stderr unavailable/not published; no relevant conversation intentionally omitted')
    assert len(sessions)==len(set(sessions))==12,'fresh task/stage session separation'
    ledger.sort(key=lambda r:(r['created_ms'],r['message_id']))
    for i,r in enumerate(ledger,1): r['sequence']=i
    totals={}
    metrics=('model_completions','MCP_calls','retrieval_calls','context_retrieval_calls','retrieval_response_local_estimate',
        'retrieval_seconds','rejected_MCP_calls','acceptance_repair_turns','development_wall_seconds','CLI_wall_seconds',
        'context_generation_seconds','participant_plus_context_seconds','passed','total','preserved_original_observations',
        'modified_caller_observations','required_changed_observations','passing_to_failing_regressions',
        'validation_lowering_seconds','functional_execution_seconds','acceptance_wall_seconds')
    for track in ('BASE','A','B','C'):
        selected=[v for name,v in runs.items() if name.endswith('-'+track)]
        totals[track]={k:sum(v[k] for v in selected) for k in metrics}
        totals[track]['usage']=dict(sum((Counter(v['usage']) for v in selected),Counter()))
    allocated={}
    for track in ('A','B','C'):
        allocated[track]=dict(usage={k:totals[track]['usage'][k]+totals['BASE']['usage'][k]/3 for k in totals[track]['usage']},
            participant_plus_context_seconds=totals[track]['participant_plus_context_seconds']+totals['BASE']['development_wall_seconds']/3,
            common_base_allocation='1/3 of actual shared construction; not repeated authoring or provider integer counts')
    differences={pair:{'usage':{k:totals[left]['usage'][k]-totals[right]['usage'][k] for k in totals[left]['usage']},
        'participant_plus_context_seconds':totals[left]['participant_plus_context_seconds']-totals[right]['participant_plus_context_seconds']}
        for pair,left,right in [('B_minus_A','B','A'),('C_minus_A','C','A'),('C_minus_B','C','B')]}
    save(OUT/'MEASUREMENTS.json',dict(runs=runs,totals=totals,allocated_shared_base=allocated,differences=differences,
        qualification_usage=tally(load(OUT/'PREFLIGHT.json')['step_finishes']),billing=None,coordinator_tokens=None,
        fully_accounted_development_effort=False,exact_provider_serialization=False,tokenizer=None,
        timing='Context generation added once. Stage wall includes CLI/export/evaluation; retrieval and validation/execution overlap stage. Do not sum them again.',
        SDK_cost_zero_is_not_free_billing=True))
    save(OUT/'REQUEST-LEDGER.json',dict(sequence='exported assistant creation timestamps',completion_rows=ledger,
        exact_provider_HTTP_calls=None,visible_completions_only=True,credentials_accessed=False))
    save(OUT/'PROVENANCE.json',provenance)
    save(OUT/'FULL-HISTORY-MANIFESTS.json',manifests)
    save(OUT/'INFORMATION-EQUIVALENCE.json',dict(tasks=audit,all_12_sessions_distinct=True,
        hidden_context_exclusion_attested=False,exploratory=True,no_cross_candidate_tools=True,
        pre_modification_context_freezes=[f"{t['id']}-BASE/CONTEXT-FREEZE.json" for t in TASKS],
        B_and_C_mechanically_generated=True,summary_inherits_shared_registry_checks=True))
    print(json.dumps(dict(totals=totals,differences=differences),indent=2))

def paths():
    files=[p for folder in (HERE,OUT) for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts
        and p.name not in ('PUBLICATION-IDENTITIES.json','VERIFICATION.json')]
    files+=[ROOT/'benchmark/results/phase6/R6_39-REPORT.md']
    files+=[ROOT/f'docs/{name}-r6.39.md' for name in ('project-overview','research-log','decisions')]
    return sorted(files)

def supplemental():
    """Unscored post-authoring coverage/provenance audit; never amend frozen oracle."""
    from snapshot import generate,verify,retrieve
    checks={}; failures=[]; context_requests=[]
    for t in TASKS:
        base=OUT/(t['id']+'-BASE'); registry=Registry(base/'registry'); ds=artifacts(registry,t,False)
        bindings={'CallerA':ds['a']['identity'],'CallerB':ds['b']['identity']}
        history=load(OUT/(t['id']+'-A')/'HISTORY.json')
        messages=load(base/'attempt0/EXPORT.json')['messages']
        assert history['messages']==sorted(messages,key=lambda m:m['info']['time']['created'])
        for track in ('A','B','C'):
            folder=OUT/(t['id']+'-'+track)
            snap=load(folder/'SNAPSHOT.json'); summary=load(folder/'SUMMARY.json')
            verify(snap,registry,digest(requirement(t)),modification(t),bindings,requirement(t))
            assert snap==generate(registry,digest(requirement(t)),modification(t),bindings,requirement(t))
            assert summary['behavior']==requirement(t) and summary['objective']==modification(t)
            assert summary['caller_bindings']==bindings
            for component in summary['components']:
                pin=component['identity']; d=registry.read()['state']['definitions'][pin]
                assert component==dict(name=d['name'],identity=d['identity'],parameters=d['params'],
                    result=d['result_type'],dependencies=d['dependencies'])
            # Every omitted exact definition/body, history/validation fact is reachable through common retrieval.
            for pin in snap['definitions']:
                for kind in ('definition','dependencies','validation','history','identity'): retrieve(registry,pin,kind)
            for line in (folder/'MCP.jsonl').read_text().splitlines():
                e=json.loads(line)
                if e['request']['method']!='tools/call': continue
                name=e['request']['params']['name']; args=e['request']['params']['arguments']
                if name=='lykoi_context':
                    value=e['response']['result']; source={'history':'HISTORY.json','summary':'SUMMARY.json','snapshot':'SNAPSHOT.json'}[args['kind']]
                    assert not value['isError'] and value['structuredContent']==load(folder/source)
                    context_requests.append(dict(run=t['id']+'-'+track,kind=args['kind'],response_identity=digest(value),
                        response_bytes=len(json.dumps(value).encode()),seconds=e['wall_seconds']))
                if e['response']['result']['isError']:
                    failures.append(dict(run=t['id']+'-'+track,tool=name,args=args,diagnostic=e['response']['result']))
            final=load(folder/'ACCEPTANCE-0.json'); assert final['all_passed']
            assert load(folder/'CLOSED.json')['calls'][0]['session']!=load(base/'CLOSED.json')['calls'][0]['session']
        f=load(OUT/(t['id']+'-EXPECTATIONS.json'))
        checks[t['id']]=dict(history_complete=True,snapshot_recomputed_exact=True,summary_facts_exact=True,
            all_omitted_registry_kinds_retrievable=True,base_registry_after_retrieval=registry.read()['token'],
            original_cases=527,modified_cases=264,
            required_value_or_error_differences=sum(x['expected']!=x['modified'] for x in f['A']),
            full_history_context_rehydrated=True)
    save(OUT/'SUPPLEMENTAL-AUDIT.json',dict(post_authoring_unscored=True,checks=checks,
        rejected_calls=failures,context_retrievals=context_requests,
        cache_write_zero_all_completions=all(r['usage']['cache']['write']==0 for r in load(OUT/'REQUEST-LEDGER.json')['completion_rows']),
        original_frozen_expectations_unchanged=True))
    save(OUT/'RESULT.json',dict(round='R6.39',classification='R6_39_COMPARISON_INCONCLUSIVE',
        all_nine_modification_runs_pass=True,all_three_shared_originals_pass=True,
        no_regressions=True,scored_acceptance_repair_turns=0,AI_independent_replay_pass=True,
        ordinary_summary_functionally_sufficient_in_sample=True,symbolic_unique_advantage_established=False,
        fully_accounted_effort_advantage=False,exploratory=True,production_kernel=26,
        execution_semantics_changed=False,full_R6_31_study=False,P6_A04_acceptance=False,P6_A05_access=False,
        stopped_after_publication=True))
    print(json.dumps(dict(checks=checks,rejected_calls=failures,context_retrievals=context_requests),indent=2))

def verification(publish=False):
    pins=load(OUT/'BASELINE.json')['protected_files']
    for name,pin in pins.items(): assert sha(ROOT/name)==pin,name
    freezes=[OUT/'TASK-FREEZE.json']+[OUT/(t['id']+'-BASE')/'CONTEXT-FREEZE.json' for t in TASKS]
    for freeze in freezes:
        for name,pin in load(freeze)['inputs'].items(): assert sha(ROOT/name)==pin,name
    for p in paths():
        text=p.read_text(encoding='utf-8')
        assert not any(line.endswith((' ','\t')) for line in text.splitlines()),p
        if p.suffix=='.json': json.loads(text)
        if p.suffix=='.jsonl':
            for line in text.splitlines(): json.loads(line)
        assert not re.search(r'\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}',text),p
        assert not re.search(r'\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+',text),p
        if p.suffix=='.md':
            for link in re.findall(r'\]\(([^)]+)\)',text):
                if '://' not in link and not link.startswith('#'):
                    target=(p.parent/link.split('#')[0]).resolve()
                    if publish and target==OUT/'VERIFICATION.json': continue
                    assert target.exists(),(p,link)
    subprocess.run(['git','diff','--check'],cwd=ROOT,check=True)
    assert not subprocess.check_output(['git','diff','--name-only','HEAD'],cwd=ROOT,text=True).strip()
    manifest=OUT/'PUBLICATION-IDENTITIES.json'
    if publish:
        save(manifest,dict(round='R6.39',files={p.relative_to(ROOT).as_posix():dict(sha256=sha(p),bytes=p.stat().st_size) for p in paths()}))
        save(OUT/'VERIFICATION.json',dict(passed=True,kernel=26,protected_count=len(pins),publication_files=len(paths()),
            manifest_sha256=sha(manifest),tracked_files_unchanged=True,git_diff_check=True,freezes_preserved=True,
            credentials_pattern_scan_passed=True,production_VM_wrapper_adapter_contracts_registry_telemetry_unchanged=True))
    receipt=load(OUT/'VERIFICATION.json'); assert receipt['manifest_sha256']==sha(manifest)
    entries=load(manifest)['files']; assert set(entries)=={p.relative_to(ROOT).as_posix() for p in paths()}
    for name,meta in entries.items(): assert sha(ROOT/name)==meta['sha256'] and (ROOT/name).stat().st_size==meta['bytes'],name
    print('R6.39 verified:',len(pins),'protected identities;',len(entries),'publication files')

if __name__=='__main__':
    if sys.argv[1]=='accounting': accounting()
    elif sys.argv[1]=='supplemental': supplemental()
    else: verification(sys.argv[1]=='publish')
