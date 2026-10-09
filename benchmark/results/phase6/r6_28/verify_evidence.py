"""Offline publication checks: transcript lineage, acceptance, replay and preservation."""
import json
import subprocess
import sys
from experiment import HERE, ROOT, a, definitions, identity, now, observe, read, save, sha, tools, verify_freeze

def verify():
    verify_freeze()
    result=read('RESULT.json')
    functional=read('FUNCTIONAL.json')
    replay=read('REPLAY.json')
    metrics=read('MEASUREMENTS.json')
    events=[json.loads(s) for s in (HERE/'LIVE/EVENTS.jsonl').read_text().splitlines()]
    rows=[json.loads(s) for s in (HERE/'LIVE/MCP.jsonl').read_text().splitlines()]
    calls=[r for r in rows if r['request'].get('method')=='tools/call']
    listed=next(r['response']['result']['tools'] for r in rows if r['request'].get('method')=='tools/list')
    assert listed==definitions()
    native=[e['part'] for e in events if e['type']=='tool_use']
    assert len(calls)==len(native)==metrics['semantic_tool_calls']==5
    session=tools.Session(['value','check','compose'])
    for call,event in zip(calls,native):
        params=call['request']['params']
        assert event['tool']=='lykoi_'+params['name']
        assert event['state']['input']==params['arguments']
        assert json.loads(event['state']['output'])==call['response']['result']['structuredContent']
        assert call['normalized']['semantic_arguments']==params['arguments']
        dispatched=session.dispatch({'function':{'name':params['name'],'arguments':params['arguments']}})
        assert dispatched['success'] and dispatched['arguments_valid']
        assert dispatched['response']==call['dispatch']['response']
    # Reconstruction here is a lineage control; execution replay uses saved artifact only.
    artifact=read('LIVE/ARTIFACT.json')
    assert session.packet==read('LIVE/SYMBOLIC-PACKET.json')
    assert session.completed['artifact']==artifact
    assert sha(HERE/'LIVE/ARTIFACT.json')==functional['artifact_sha256']==replay['artifact_sha256']
    assert identity(artifact)==functional['artifact_content_identity']
    assert read('LIVE/DELIVERY.json')['matches_requested']
    requirement=read('REQUIREMENT.json')
    acceptance=read('ACCEPTANCE.json')
    assert [o['expected'] for o in functional['observations']]==acceptance['cases']
    d=artifact['definitions'][0]
    assert len(artifact['definitions'])==1 and artifact['target']==requirement['target']
    assert [[p['name'],p['type']] for p in d['params']]==requirement['inputs']
    assert len(d['steps'])==2 and d['order']==[s['id'] for s in d['steps']]
    assert d['steps'][1]['node']['expr']['add'][0]=={'ref':d['steps'][0]['id']}
    assert d['result']=={'ref':d['steps'][1]['id']} and d['result_type']=='Int64'
    assert functional['structural_valid'] and functional['passed']
    for case,record in zip(acceptance['cases'],functional['observations']):
        obs,_=observe(artifact,case)
        assert obs==record['evidence'] and identity(obs)==record['observation_identity']
        x=obs['observation']
        e=case['expected']
        assert x['status']==e['status']
        if e['status']=='success':
            assert type(x['value']) is int and x['value']==e['value']
            assert x['output']['bytes_hex']==e['output_hex'] and x['consumed']==0
        elif e['status']=='reject':
            assert x['error']['code']==e['code'] and x['error']['stage']==e['stage']
        else:
            assert x['diagnostic']['code']==e['code']
        assert record['passed']
    assert len(replay['passes'])==3 and replay['model_calls']==0 and replay['all_equal']
    for p in replay['passes']:
        assert len(p['records'])==11 and p['all_equal']
        for row,original in zip(p['records'],functional['observations']):
            assert row['equal'] and row['evidence']==original['evidence']
            assert row['identity']==original['observation_identity']
    assert result['classification']=='R6_28_SEMANTIC_CONSTRUCTION_SUPPORTED'
    assert metrics['model_calls_observed']==metrics['completion_steps']==6
    assert metrics['argument_valid']==5 and metrics['construction_failures']==metrics['correction_turns']==0
    assert all(m['providerID']=='openai' and m['modelID']=='gpt-6.1-sol' and m['variant']=='high'
               for m in metrics['assistant_message_metadata'])
    suite=subprocess.run([sys.executable,'-m','unittest','discover','-s','.','-p','test_transport.py','-v'],
        cwd=HERE.parent/'r6_25',capture_output=True,text=True,encoding='utf-8',timeout=120)
    assert suite.returncode==0 and 'Ran 17 tests' in suite.stderr,suite.stderr
    save('OFFLINE-CHECKS.json',dict(timestamp=now(),passed=True,model_calls=0,
        frozen_transport_tests=dict(methods=17,stdout=suite.stdout,stderr=suite.stderr),
        lineage_reconstruction_matches=True,native_event_arguments_match=True,feedback_matches=True,
        structural_dependency_and_result_verified=True,frozen_acceptance_rechecked=11,replay_records_verified=33,
        additional_publication_execution_check=True,manual_semantic_repairs=0))
    types={s:sum(o['evidence']['observation']['status']==s for o in functional['observations'])
           for s in ('success','reject','wrapper_reject')}
    times=metrics['functional_timings']
    totals={key:sum(t.get(key,0) for t in times) for key in set(k for t in times for k in t)}
    successes=[o['evidence']['observation']['work'] for o in functional['observations'] if o['evidence']['observation']['status']=='success']
    assistant_wall=sum((m['time']['completed']-m['time']['created'])/1000 for m in metrics['assistant_message_metadata'])
    save('SUMMARY.json',dict(timestamp=now(),artifact_sha256=sha(HERE/'LIVE/ARTIFACT.json'),
        definition_identity=d['identity'],artifact_content_identity=identity(artifact),acceptance_types=types,
        acceptance_passed=11,replay_passes=3,replay_observations=33,successful_VM_work=successes,
        functional_timing_totals=totals,assistant_message_elapsed_seconds=assistant_wall,
        assistant_elapsed_is_not_pure_inference=True,adapter_construction_times=metrics['adapter_construction_times'],
        publication_checks_model_calls=0))
    print('Offline lineage, 11 acceptance observations, 33 replay records and 17 transport methods verified.')

if __name__=='__main__':
    verify()
