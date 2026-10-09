"""Read-only accounting and publication; no participant or semantic repairs."""
from collections import Counter
import json
import math
import re
import subprocess
import sys
from common import ROOT, HERE, OUT, load, save, sha, digest, c, Registry, Journal
from run import AGENT, GUIDE
from tools import TOOLS
from tasks import TASKS, requirement, modification, artifacts

CLASSIFICATION='R6_38_COMPARISON_INCONCLUSIVE'


def tally(parts):
    result=Counter()
    for part in parts:
        t=part['tokens']
        for key in ('input','output','reasoning'): result[key]+=t.get(key,0)
        for key in ('read','write'): result['cache_'+key]+=t.get('cache',{}).get(key,0)
    result['processed_input']=result['input']+result['cache_read']+result['cache_write']
    return dict(result)


def accounting():
    catalog={}; ledger=[]; runs={}; provenance={}
    def section(category,text):
        if not isinstance(text,str): text=json.dumps(text,sort_keys=True,separators=(',',':'))
        pin=digest(text); key=category+':'+pin
        catalog.setdefault(key,dict(category=category,content=text,content_identity=pin,characters=len(text),local_estimated_tokens=math.ceil(len(text)/4)))
        return key
    fixed=section('fixed_instructions',AGENT); schemas=section('tool_schemas',TOOLS)
    for t in TASKS:
        for track in ('A','B'):
            run_id=t['id']+'-'+track; folder=OUT/run_id; closed=load(folder/'CLOSED.json')
            assert not closed['failure']
            messages={}; stage_by_message={}; exports=[]
            for call in closed['calls']:
                stage=call['stage']; exported=load(folder/stage/'EXPORT.json'); exports.append(exported)
                for msg in exported['messages']: messages[msg['info']['id']]=msg
                for finish in call['step_finishes']: stage_by_message[finish['messageID']]=stage
            sessions={}
            for msg in messages.values(): sessions.setdefault(msg['info']['sessionID'],[]).append(msg)
            local_rows=[]
            for session,msgs in sessions.items():
                history=[]
                for msg in sorted(msgs,key=lambda m:m['info']['time']['created']):
                    info=msg['info']
                    if info['role']=='user':
                        text='\n'.join(p['text'] for p in msg['parts'] if p['type']=='text')
                        if text.startswith(GUIDE): history.append(section('Lykoi_guidance',GUIDE)); text=text[len(GUIDE):]
                        if 'Deterministic state snapshot:\n' in text:
                            before,tail=text.split('Deterministic state snapshot:\n',1)
                            snaptext,after=tail.split('\n'+modification(t),1)
                            history.extend([section('task_requirements',before),section('current_symbolic_state',snaptext),section('task_requirements',modification(t)+after)])
                        else: history.append(section('task_requirements',text))
                        continue
                    if info['role']!='assistant' or 'tokens' not in info: continue
                    generated=[]; next_history=[]; tools=0
                    for part in msg['parts']:
                        if part['type']=='text':
                            generated.append(section('model_generated_output',part['text']))
                            next_history.append(section('historical_conversation',part['text']))
                        elif part['type']=='tool':
                            tools+=1; state=part['state']; body=dict(tool=part['tool'],arguments=state['input'])
                            generated.append(section('model_generated_output',body)); next_history.append(section('historical_conversation',body))
                            category='retrieval_results' if part['tool'].endswith(('lykoi_retrieve','lykoi_detail')) else 'tool_feedback'
                            next_history.append(section(category,state.get('output',state.get('error',''))))
                    ids=[fixed,schemas]+history; counts=Counter()
                    for key in ids: counts[catalog[key]['category']]+=catalog[key]['local_estimated_tokens']
                    usage=info['tokens']; processed=usage['input']+usage['cache']['read']+usage['cache']['write']
                    row=dict(sequence=len(ledger)+1,run=run_id,stage=stage_by_message[info['id']],session=session,message_id=info['id'],
                        provider=info.get('providerID'),model=info.get('modelID'),usage=usage,processed_input=processed,
                        input_section_identities=ids,generated_section_identities=generated,local_estimates=dict(counts),
                        unattributed_signed_estimate_residual=processed-sum(counts.values()),MCP_calls=tools,
                        observable_message_identity=digest({k:info[k] for k in ('id','role','sessionID')}),
                        message_payload_identity=digest([p for p in msg['parts'] if p['type'] in ('text','tool')]),
                        tool_schema_section_identity=schemas,exact_upstream_request=False,tokenizer=None,
                        assistant_interval_seconds=(info['time']['completed']-info['time']['created'])/1000)
                    ledger.append(row); local_rows.append(row); history.extend(next_history)
            assert tally([{'tokens':r['usage']} for r in local_rows])==tally([p for call in closed['calls'] for p in call['step_finishes']])
            exchanges=[json.loads(line) for line in (folder/'MCP.jsonl').read_text().splitlines()]
            calls=[r for r in exchanges if r['request']['method']=='tools/call']
            assert len(calls)==sum(r['MCP_calls'] for r in local_rows)==sum(x['tool_calls'] for x in closed['calls'])
            retrievals=[r for r in calls if r['request']['params']['name'] in ('lykoi_retrieve','lykoi_detail')]
            details=[r for r in retrievals if r['request']['params']['name']=='lykoi_detail']
            rejects=[r for r in calls if r['response']['result']['isError']]
            proposals=[]
            state=Registry(folder/'registry').read()['state']
            for call in calls:
                if call['request']['params']['name']=='lykoi_admit':
                    action=call['request']['params']['arguments']['action']
                    if action['action']=='admit' and not call['response']['result']['isError']:
                        for d in action['definitions']:
                            sealed=c.seal(d); assert state['definitions'][sealed['identity']]==sealed
                            proposals.append(sealed['identity'])
            assert len(proposals)==5
            base=load(sorted(folder.glob('base*-ACCEPTANCE.json'))[-1]); final=load(sorted(folder.glob('modification*-ACCEPTANCE.json'))[-1])
            assert base['all_passed'] and final['all_passed']
            provenance[run_id]=dict(exact_model_proposals_after_only_sealing=proposals,coordinator_semantic_repairs=0,identities=final['identities'],
                preserved_predecessor_rows=all(row in final['rows'] for row in base['rows']),
                base_modification_not_disclosed=all(modification(t) not in p.get('text','') for m in load(folder/'base0/EXPORT.json')['messages'] for p in m['parts']))
            bystage={}
            for stage in sorted({r['stage'] for r in local_rows}):
                rows=[r for r in local_rows if r['stage']==stage]; estimates=Counter()
                for r in rows: estimates.update(r['local_estimates'])
                bystage[stage]=dict(usage=tally([{'tokens':r['usage']} for r in rows]),completions=len(rows),MCP_calls=sum(r['MCP_calls'] for r in rows),
                    repeated_local_estimates=dict(estimates),input_growth=[r['processed_input'] for r in rows])
            journal=Journal(folder/'telemetry').recover(); assert not journal['pending'] and not journal['incomplete']
            runs[run_id]=dict(usage=tally([{'tokens':r['usage']} for r in local_rows]),completions=len(local_rows),MCP_calls=len(calls),retrieval_calls=len(retrievals),
                bounded_detail_calls=len(details),retrieval_response_estimate=sum(math.ceil(len(json.dumps(r['response']['result']))/4) for r in retrievals),
                retrieval_seconds=sum(r['wall_seconds'] for r in retrievals),MCP_dispatch_seconds=sum(r['wall_seconds'] for r in calls),
                rejected_MCP_calls=len(rejects),acceptance_repair_turns=len(closed['calls'])-2,
                authoring_wall_seconds=closed['wall_seconds'],CLI_wall_seconds=sum(x['wall_seconds'] for x in closed['calls']),snapshot_seconds=closed['snapshot_seconds'],
                base_passed=base['passed'],base_total=base['total'],final_passed=final['passed'],final_total=final['total'],
                regressions=sum(not r['passed'] for r in final['rows'] if r['root'] in ('a','b')),
                validation_lowering_seconds=sum(v['validation_seconds'] for result in (base,final) for v in result['expansions'].values()),
                acceptance_seconds=base['wall_seconds']+final['wall_seconds'],by_stage=bystage,
                registry_admission_seconds=sum(e['data'].get('tool_seconds',0) for e in journal['events'] if e['kind']=='admission'),
                registry_retrieval_seconds=sum(e['data'].get('tool_seconds',0) for e in journal['events'] if e['kind']=='retrieval'))
    totals={}
    for track in ('A','B'):
        selected=[v for k,v in runs.items() if k.endswith('-'+track)]; total=Counter(); usage=Counter()
        for r in selected:
            usage.update(r['usage'])
            for key in ('completions','MCP_calls','retrieval_calls','bounded_detail_calls','retrieval_response_estimate','retrieval_seconds','authoring_wall_seconds',
                'CLI_wall_seconds','snapshot_seconds','base_passed','base_total','final_passed','final_total','regressions','rejected_MCP_calls','acceptance_repair_turns',
                'validation_lowering_seconds','acceptance_seconds','MCP_dispatch_seconds','registry_admission_seconds','registry_retrieval_seconds'): total[key]+=r[key]
        totals[track]=dict(total,usage=dict(usage))
    differences={key:totals['B'][key]-totals['A'][key] for key in totals['A'] if key!='usage'}
    differences['usage']={key:totals['B']['usage'][key]-totals['A']['usage'][key] for key in totals['A']['usage']}
    visible={}
    for track in ('A','B'):
        unique=set(); repeated=Counter(); generated=Counter()
        for row in ledger:
            if not row['run'].endswith('-'+track): continue
            for key in row['input_section_identities']:
                item=catalog[key]; repeated[item['category']]+=item['local_estimated_tokens']; unique.add(key)
            for key in row['generated_section_identities']:
                generated['new_output_estimate']+=catalog[key]['local_estimated_tokens']; unique.add(key)
        u=Counter(); seen=set()
        for key in sorted(unique):
            item=catalog[key]
            if item['content_identity'] in seen: continue
            seen.add(item['content_identity']); category=item['category']
            if category=='historical_conversation': category='model_generated_output'
            u[category]+=item['local_estimated_tokens']
        visible[track]=dict(unique_estimates=dict(u),repeated_estimates=dict(repeated),generated_estimates=dict(generated),
            signed_residual=totals[track]['usage']['processed_input']-sum(repeated.values()))
    save(OUT/'SECTION-CATALOG.json',dict(estimator='ceil(characters/4), not tokenizer',sections=catalog))
    save(OUT/'REQUEST-LEDGER.json',dict(exact_upstream_boundaries=False,schema_delivery_hypothesis=True,completion_rows=ledger,
        credentials_or_private_headers_accessed=False,provider_HTTP_attempts=None))
    save(OUT/'PROVENANCE.json',provenance)
    save(OUT/'MEASUREMENTS.json',dict(runs=runs,totals=totals,difference_B_minus_A=differences,visible_estimates=visible,
        qualification_usage=tally(load(OUT/'PREFLIGHT.json')['step_finishes']),billing=None,coordinator_usage=None,
        model_tokenizer=None,exact_provider_serialization=None,fully_accounted_workflow=False,
        timing_overlap='Authoring includes CLI and snapshot. CLI includes MCP. Acceptance includes validation/VM. Do not add overlapping intervals.',
        classification=CLASSIFICATION))
    print(json.dumps(dict(totals=totals,differences=differences,per_run={k:{x:v[x] for x in ('usage','completions','MCP_calls','retrieval_calls','rejected_MCP_calls','authoring_wall_seconds')} for k,v in runs.items()}),indent=2))


def supplement():
    tests=subprocess.run([sys.executable,'-B','-m','unittest','discover','-s',str(HERE),'-p','test_continuation.py','-v'],capture_output=True,text=True,cwd=ROOT)
    save(OUT/'CONTINUATION-TESTS.json',dict(returncode=tests.returncode,stdout=tests.stdout,stderr=tests.stderr,post_authoring_unscored=True))
    assert tests.returncode==0,tests.stderr
    comparisons={}
    for t in TASKS:
        a=load(OUT/(t['id']+'-A')/'CLOSED.json'); b=load(OUT/(t['id']+'-B')/'CLOSED.json')
        assert a['calls'][0]['session']==a['calls'][1]['session']
        assert b['calls'][0]['session']!=b['calls'][1]['session']
        cfgs=[load(OUT/(t['id']+'-'+track)/call['stage']/'CONFIG.json') for track,closed in [('A',a),('B',b)] for call in closed['calls']]
        for cfg in cfgs:
            assert cfg['agent']==cfgs[0]['agent'] and cfg['permission']==cfgs[0]['permission']
        snap=load(OUT/(t['id']+'-B')/'SNAPSHOT.json')
        comparisons[t['id']]=dict(A_accumulating_session=True,B_fresh_modification_session=True,same_model_configuration=True,
            snapshot_requirement_matches=digest(requirement(t))==snap['requirement'],snapshot_constraints_verbatim=requirement(t)==snap['constraints'],
            snapshot_objective_verbatim=modification(t)==snap['objective'],offline_summary=load(OUT/(t['id']+'-B')/'CONTEXT-SIZES.json'))
    save(OUT/'CONTINUATION-EQUIVALENCE.json',comparisons)
    save(OUT/'RESULT.json',dict(round='R6.38',classification=CLASSIFICATION,kernel=26,snapshots_qualified_bounded=True,
        correctness_all_six_runs=True,AI_independent_replay_passed=True,fully_accounted_effort_advantage=False,
        token_attribution_partial=True,beyond_ordinary_summary_value_not_established=True,
        production_semantics_changed=False,full_R6_31_study=False,P6_A04_acceptance=False,P6_A05_access=False,stopped_after_publication=True))


def chronological_ledger():
    original=load(OUT/'REQUEST-LEDGER.json'); rows=original['completion_rows']; infos={}
    for t in TASKS:
        for track in ('A','B'):
            folder=OUT/(t['id']+'-'+track)
            for call in load(folder/'CLOSED.json')['calls']:
                for message in load(folder/call['stage']/'EXPORT.json')['messages']:
                    infos[message['info']['id']]=message['info']
    for row in rows:
        row['initial_catalog_iteration']=row.pop('sequence')
        row['created_ms']=infos[row['message_id']]['time']['created']
        row['completed_ms']=infos[row['message_id']]['time']['completed']
    rows.sort(key=lambda row:(row['created_ms'],row['message_id']))
    for index,row in enumerate(rows,1): row['sequence']=index
    original['sequence_basis']='Actual exported assistant creation timestamps; scored completions only, neutral preflight separate. Not provider HTTP attempts.'
    original['initial_ledger_preserved']='REQUEST-LEDGER.json used task/track catalog iteration, not global request order; corrected prospectively without usage changes.'
    save(OUT/'REQUEST-LEDGER-CHRONOLOGICAL.json',original)
    pins=load(OUT/'BASELINE.json')['protected_files']
    prefixes=('experiments/semantic_interpreter/','experiments/typed_composition_r6_18/','experiments/lifecycle_r6_32/',
        'benchmark/results/phase6/r6_23/','benchmark/results/phase6/r6_25/','benchmark/results/phase6/r6_27/')
    save(OUT/'IMPLEMENTATION-IDENTITIES.json',dict(kernel=26,exact_protected_implementation_and_contract_identities={name:pin for name,pin in pins.items()
        if name.startswith(prefixes) and name.endswith(('.py','.json','.md')) and (name.endswith('.py') or 'CONTRACT' in name or 'SEMANTICS' in name or 'TOOLS' in name or 'ENVELOPE' in name or 'SPEC' in name)}))


def paths():
    files=[p for folder in (HERE,OUT) for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name not in ('PUBLICATION-IDENTITIES.json','VERIFICATION.json')]
    files+=[ROOT/'benchmark/results/phase6/R6_38-REPORT.md']
    files+=[ROOT/f'docs/{name}-r6.38.md' for name in ('project-overview','research-log','decisions')]
    return sorted(files)


def verify(publish=False):
    pins=load(OUT/'BASELINE.json')['protected_files']
    for name,pin in pins.items(): assert sha(ROOT/name)==pin,name
    for name,pin in load(OUT/'TASK-FREEZE.json')['inputs'].items(): assert sha(ROOT/name)==pin,name
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
                    if publish and target == (OUT/'VERIFICATION.json').resolve():
                        continue  # Receipt is installed only after the manifest checks pass.
                    assert target.exists(),(p,link)
    subprocess.run(['git','diff','--check'],cwd=ROOT,check=True)
    assert not subprocess.check_output(['git','diff','--name-only','HEAD'],cwd=ROOT,text=True).strip()
    manifest=OUT/'PUBLICATION-IDENTITIES.json'
    if publish:
        save(manifest,dict(round='R6.38',files={p.relative_to(ROOT).as_posix():dict(sha256=sha(p),bytes=p.stat().st_size) for p in paths()}))
        save(OUT/'VERIFICATION.json',dict(passed=True,kernel=26,protected_count=len(pins),publication_files=len(paths()),
            manifest_sha256=sha(manifest),tracked_files_unchanged=True,git_diff_check=True,freezes_preserved=True,credentials_not_published=True))
    receipt=load(OUT/'VERIFICATION.json'); assert receipt['manifest_sha256']==sha(manifest)
    entries=load(manifest)['files']; assert set(entries)=={p.relative_to(ROOT).as_posix() for p in paths()}
    for name,meta in entries.items(): assert sha(ROOT/name)==meta['sha256'] and (ROOT/name).stat().st_size==meta['bytes'],name
    print('R6.38 verified:',len(pins),'protected identities;',len(entries),'publication files')


if __name__=='__main__':
    if sys.argv[1]=='accounting': accounting()
    elif sys.argv[1]=='supplement': supplement()
    elif sys.argv[1]=='chronology': chronological_ledger()
    else: verify(sys.argv[1]=='publish')
