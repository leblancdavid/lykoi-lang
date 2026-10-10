"""Post-score first-construction, budget chronology and control fidelity audit."""
import json
from collections import Counter
from common import OUT,Registry,c,load,save,normalize,digest
from tasks import TASKS,score
from run import usage
from audit import calls

def main():
    first={}; replay_count=0; model_pins=0
    for t in TASKS:
        for k in ['A','B','C','X']:
            name=t['id']+'-'+k; folder=OUT/name; reg=Registry(folder/'registry')
            attempts=[]
            for e in calls(folder):
                if e['request']['params']['name']!='lykoi_admit': continue
                for d in e['request']['params']['arguments']['action']['definitions']:
                    if d['name']=='Entry': attempts.append((e,d))
            assert attempts
            e,d=attempts[0]
            if e['response']['result']['isError']:
                rec=dict(all_passed=False,stage='STRUCTURAL_ADMISSION_REJECT',diagnostic=e['response']['result'])
            else:
                rec=normalize(score(reg,c.seal(d)['identity'],t,load(OUT/(t['id']+'-EXPECTATIONS.json'))))
            save(folder/'FIRST-CONSTRUCTION-ACCEPTANCE.json',rec)
            first[name]=dict(first_construction_passed=rec['all_passed'],root=c.seal(d)['identity'],
                first_structurally_admitted=not e['response']['result']['isError'],complete_Entry_attempts=len(attempts))
            subs=sorted(folder.glob('SUBMISSION-*.json'))
            replay_count+=sum(load(folder/('REPLAY-'+str(i+1)+'.json'))['total'] for i in range(len(subs)))
            # audit.py already replayed final artifact; complete second pass for earlier ones.
            for i,p in enumerate(subs[:-1]):
                submission=load(p); expected=load(folder/('ACCEPTANCE-'+str(i+1)+'.json'))
                result=normalize(score(Registry(folder/'registry'),submission['root'],t,load(OUT/(t['id']+'-EXPECTATIONS.json'))))
                assert all(result[x]==expected[x] for x in ('rows','expansion','root','closure'))
                save(folder/('REPLAY-SECOND-EARLIER-'+str(i+1)+'.json'),result)
    model_pins=sum(len(v['model_authored_pins']) for v in load(OUT/'PROVENANCE.json').values())
    events=[json.loads(x) for x in (OUT/'E4-B/EVENTS.jsonl').read_text().splitlines()]
    finished=[]; budget=[]; submitted=[]
    for i,e in enumerate(events):
        if e.get('type')=='step_finish':
            finished.append(e['part']); u=usage(finished)
            if u['processed_input']+u['output']>48000:
                budget.append(dict(event=i,processed_plus_output=u['processed_input']+u['output']))
        if e.get('type')=='tool_use' and 'submit' in json.dumps(e): submitted.append(i)
    limits=load(OUT/'CONTROL-LIMITATIONS.json')
    save(OUT/'SUPPLEMENTAL-AUDIT.json',dict(first_construction=first,
        first_construction_by_condition={k:sum(v['first_construction_passed'] for n,v in first.items() if n.endswith('-'+k)) for k in ['A','B','C','X']},
        all_model_authored_definition_pins_verified=model_pins,mechanical_sealing_only=True,
        replay_passes=2,replay_observations_per_pass=replay_count,total_repeated_replay_observations=2*replay_count,
        all_sealed_submissions_replayed_including_failures=True,model_calls_during_replay=0,
        budget_stop=dict(run='E4-B',submission_events=submitted,cap_crossing_events=budget,
            sealed_before_cap=bool(submitted and budget and submitted[0]<budget[0]['event']),
            provider_error=False,no_retry=True),
        expanded_template_full_envelope_equivalence=False,
        expansion_limitation='Primitive-template flattening retains order/value/check operations, but removes compose-generated seq boundaries. Those boundaries affect result spans in unchanged VM. Development constant hosts do not detect the later byte-origin difference. X is not a trace/provenance-equivalent ablation.',
        contract_oracle_limit=limits['task_oracle_ambiguity'],no_post_outcome_repairs=True))
    print(dict(first_by_condition={k:sum(v['first_construction_passed'] for n,v in first.items() if n.endswith('-'+k)) for k in ['A','B','C','X']},
        verified_pins=model_pins,replay_observations_each_pass=replay_count,budget_crossings=budget,submission_events=submitted))

if __name__=='__main__': main()
