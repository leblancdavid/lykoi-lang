"""Summarize existing frozen observations; never revises or reexecutes candidates."""
import json
import statistics
from evidence import HERE, ROOT, now, load, save, sha, verify, cli
from run import BASE_SESSIONS, equal


def metrics(result):
    observations=result['observations']
    times=[s for r in observations for s in r['seconds']]
    work=[w for r in observations for w in r['work'] if w is not None]
    return dict(source_bytes=result['source_bytes'],accepted=result['accepted'],
        unique_observations=len(observations),repeats_per_observation=3,
        deterministic=all(r['deterministic'] for r in observations),
        runtime_public_api_median_seconds=statistics.median(times),
        runtime_public_api_total_seconds=sum(times),
        vm_work=None if not work else dict(min=min(work),max=max(work),sum=sum(work)),
        vm_structure=result.get('vm_structure'),python_structure=result.get('python_structure'))


def access_audit():
    sessions=dict(BASE_SESSIONS)
    sessions.update({'C/modification':'ses_ee247d6e2ffeQyv42rmZd6R79I',
                     'A/modification':'ses_ee247d6d8ffewKzmKG6WJPa5SZ'})
    rows=[]
    for scope,session in sessions.items():
        p,_=cli('export '+session+' --sanitize --pure')
        data=json.loads(p.stdout)
        findings=[];calls=0; timings=[];failed_tools=[]
        for message in data.get('messages',[]):
            for part in message.get('parts',[]):
                if part.get('type')!='tool':
                    continue
                calls+=1
                state=part.get('state',{})
                arguments=json.dumps(state.get('input',{})).replace('\\\\','/').replace('\\','/').lower()
                forbidden=['r6_15/acceptance/','r6_15/results/','base-results.json','modified-results.json',
                           'r6_15/prepare.py','r6_15/'+('c/' if scope.startswith('A') else 'a/')]
                if 'modification' not in scope:
                    forbidden+=['r6_15/sealed/','m1.md','m2.md']
                else:
                    forbidden+=['sealed/m1.json','sealed/m2.json']
                hit=[s for s in forbidden if s in arguments]
                if hit:
                    findings.append(dict(tool=part.get('tool'),markers=hit))
                t=state.get('time',{})
                if 'start' in t and 'end' in t:
                    timings.append(dict(tool=part.get('tool'),start=t['start'],end=t['end']))
                if state.get('status')!='completed':
                    failed_tools.append(dict(tool=part.get('tool'),status=state.get('status')))
        rows.append(dict(scope=scope,session=session,tool_parts=calls,
            forbidden_argument_markers=findings,failed_tools=failed_tools,
            first_tool_to_last_tool_seconds=(max(t['end'] for t in timings)-min(t['start'] for t in timings))/1000,
            methodology='Targeted own assigned session export; metadata/input-marker scan, transcripts not published',
            limitation='Marker scan and self-disclosures do not attest hidden context or enforce filesystem isolation'))
    save(HERE/'ACCESS-AUDIT.json',dict(utc=now(),sessions=rows,
        staged_disclosure='CONTAMINATED_UNENFORCED: no observed premature access; hard disclosure enforcement unavailable'))


def main():
    verify(load(HERE/'BASE-FREEZE.json')['files'])
    verify(load(HERE/'MODIFIED-FREEZE.json')['files'])
    for freeze in ('TASK-FREEZE.json','MODIFICATION-SEAL.json'):
        for name,digest in load(HERE/freeze)['files'].items():
            assert sha(HERE/name)==digest
    base={}
    structures={}
    for track in ('A','C'):
        rows=[]
        for task in ('T1','T2','T3','T4'):
            r=load(HERE/'results'/f'{track}-base-{task}.json')
            assert sha(HERE/track/'base'/(task+('.py' if track=='A' else '.plan.json')))==sha(
                HERE/track/'first'/(task+('.py' if track=='A' else '.plan.json')))
            rows.append(dict(task=task,accepted=r['accepted'],passed=r['passed'],total=r['total'],
                first_attempt_accepted=r['accepted'],repairs=0,classification=r['classification']))
            structures[f'{track}/base/{task}']=metrics(r)
        base[track]=dict(tasks=rows,accepted_tasks=sum(r['accepted'] for r in rows),total_tasks=4,
            passed_observations=sum(r['passed'] for r in rows),total_observations=sum(r['total'] for r in rows))
    modified={}
    for track in ('A','C'):
        rows=[]
        for task in ('T1','T2'):
            old=load(HERE/'results'/f'{track}-base-{task}.json')
            new=load(HERE/'results'/f'{track}-modified-{task}.json')
            assert sha(HERE/track/'modified'/(task+('.py' if track=='A' else '.plan.json')))==sha(
                HERE/track/'mod-first'/(task+('.py' if track=='A' else '.plan.json')))
            original=[r for r in new['observations'] if r['scope']=='original']
            regressions=sum(a['passed'] and not b['passed'] for a,b in zip(old['observations'],original))
            changed=sum(not equal(a['actual'],b['actual']) for a,b in zip(old['observations'],original))
            rows.append(dict(task=task,accepted=new['accepted'],counts=new['scope_counts'],
                first_revision_accepted=new['accepted'],repairs=0,regressions=regressions,
                changed_original_observations=changed))
            structures[f'{track}/modified/{task}']=metrics(new)
        modified[track]=dict(tasks=rows,accepted_modifications=sum(r['accepted'] for r in rows),total=2)
    telemetry=load(HERE/'BASE-TELEMETRY.json')['sessions']+load(HERE/'MODIFIED-TELEMETRY.json')['sessions']
    efficiency=[{k:r[k] for k in ('scope','actual_usage','model_calls','development_wall_seconds',
        'tool_calls','tool_execution_seconds','budget_within_600_seconds','budget_within_20_tools')}
        for r in telemetry]
    identities=sorted({(m.get('providerID'),m.get('modelID')) for r in telemetry for m in r['metadata']})
    totals={}
    for track in ('A','C'):
        totals[track]={}
        for phase in ('base','modification'):
            selected=[r for r in telemetry if r['scope'].startswith(track) and
                (('modification' in r['scope'])==(phase=='modification'))]
            totals[track][phase]=dict(
                usage={k:sum(r['actual_usage'][k] for r in selected) for k in selected[0]['actual_usage']},
                model_calls=sum(r['model_calls'] for r in selected),
                development_wall_seconds=sum(r['development_wall_seconds'] for r in selected),
                tool_execution_seconds=sum(r['tool_execution_seconds'] for r in selected))
    save(HERE/'COMPARISON.json',dict(utc=now(),classification='R6_15_EXPLORATORY_COMPARISON_ONLY',
        base=base,modified=modified,representation=structures,effort=efficiency,totals=totals,
        observed_provider_models=identities,api_cost_usd=None,
        matched_success_effort_group='A/13 versus C/13: T1 and T3 both accepted',
        excluded_from_primary_efficiency='A/24 versus C/24 and modification pairs include C/T2 failure; still fully reported',
        staged_disclosure='CONTAMINATED_UNENFORCED',
        note='No independently attested separation, routing/reasoning equivalence or billing. No universal superiority claim.'))
    access_audit()
    print(json.dumps(dict(base=base,modified=modified,effort=efficiency,identities=identities),indent=2))


if __name__=='__main__':
    main()
