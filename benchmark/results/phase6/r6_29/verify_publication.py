"""Post-result integrity audit; retains and explains frozen expectation mismatch."""
import json
import subprocess
import sys
from experiment import HERE, ROOT, h, read, save, sha, identity, tools, a, matched, now

def main():
    h.verify_freeze()
    for path in HERE.rglob('*.jsonl'):
        for line in path.read_text(encoding='utf-8').splitlines():
            json.loads(line)
    f,r,m=read('FUNCTIONAL.json'),read('REPLAY.json'),read('MEASUREMENTS.json')
    assert read('RESULT.json')['classification']=='R6_29_CONSTRUCTION_PARTIAL'
    cases=read('ACCEPTANCE.json')['cases']
    assert [row['case'] for row in f['records']]==cases
    assert len(cases)==23 and sum(row['passed'] for row in f['records'])==19
    failures=[row for row in f['records'] if not row['passed']]
    assert [row['case']['id'] for row in failures]==['guard','guard_first_overflow','guard_second_overflow','guard_underflow']
    artifact=read('LIVE/ARTIFACT.json')
    d=artifact['definitions'][0]
    p,g,first,second=d['steps']
    assert p['type']=='Bool' and p['node']['expr']=={'le':[{'ref':'x'},{'ref':'y'}]}
    assert g['node']==dict(op='check',test={'ref':p['id']},site={'const':0},code='GuardDenied')
    assert first['node']['expr']=={'add':[{'ref':'x'},{'ref':'y'}]}
    assert second['node']['expr']=={'add':[{'ref':first['id']},{'ref':'x'}]}
    assert d['result']=={'ref':second['id']} and d['result_type']=='Int64'
    conflicts=[]
    for row in failures:
        obs=row['evidence']
        err=obs['observation']['error']
        assert err['code']=='GuardDenied' and err['stage']=='validation' and err['offset']==0
        assert obs['expanded']['map'][err['node']]['local']==g['id']
        entered=[obs['expanded']['map'][v['node']]['local'] for v in obs['ordered_entry_trace']]
        assert entered==['region','region',p['id'],g['id']]
        assert obs['observation']['work']==9
        x,y=row['case']['args']['x'],row['case']['args']['y']
        assert x>y
        total=x+y
        next_total=total+x
        conflict=not -(2**63)<=total<2**63 or not -(2**63)<=next_total<2**63
        if row['case']['id']!='guard':
            assert conflict
            conflicts.append(dict(case=row['case']['id'],x=x,y=y,guard=False,mathematical_first_sum=total,
                mathematical_second_sum=next_total,competing_overflow=True,observed_code=err['code'],observed_stage=err['stage'],
                arithmetic_entered=False,work=9))
    assert len(r['passes'])==3 and r['all_equal'] and r['model_calls']==0
    for pass_record in r['passes']:
        assert len(pass_record['records'])==23
        assert pass_record['artifact_sha256']==sha(HERE/'LIVE/ARTIFACT.json')
        for repeated,initial in zip(pass_record['records'],f['records']):
            assert repeated['equal'] and repeated['evidence']==initial['evidence'] and repeated['identity']==initial['identity']
    rows=[json.loads(line) for line in (HERE/'LIVE/MCP.jsonl').read_text().splitlines()]
    events=[json.loads(line) for line in (HERE/'LIVE/EVENTS.jsonl').read_text().splitlines()]
    calls=[v for v in rows if v['request'].get('method')=='tools/call']
    native=[v['part'] for v in events if v['type']=='tool_use']
    assert len(calls)==len(native)==m['semantic_tool_calls']==7
    session=tools.Session(['value','check','compose'])
    for call,event in zip(calls,native):
        params=call['request']['params']
        assert event['tool']=='lykoi_'+params['name']
        assert event['state']['input']==params['arguments']
        assert json.loads(event['state']['output'])==call['response']['result']['structuredContent']
        assert call['normalized']['semantic_arguments']==params['arguments']
        dispatch=session.dispatch({'function':dict(name=params['name'],arguments=params['arguments'])})
        assert dispatch['response']==call['dispatch']['response'] and dispatch['success']
    assert session.packet==read('LIVE/SYMBOLIC-PACKET.json') and session.completed['artifact']==artifact
    assert m['model_calls']==8 and m['argument_valid']==7 and m['argument_invalid']==m['construction_failures']==m['correction_turns']==0
    assert all(v['providerID']=='openai' and v['modelID']=='gpt-6.1-sol' for v in m['assistant_metadata'])
    assert read('LIVE/DELIVERY.json')['matches_requested']
    assert read('LIVE/RESULT.json')['author_process_terminated']
    suite=subprocess.run([sys.executable,'-m','unittest','discover','-s','.','-p','test_transport.py','-v'],cwd=HERE.parent/'r6_25',capture_output=True,text=True,timeout=120)
    assert suite.returncode==0 and 'Ran 17 tests' in suite.stderr,suite.stderr
    save('PRECEDENCE-AUDIT.json',dict(timestamp=now(),model_calls=0,conflicts=conflicts,behavioral_guard_first_observations=3,
        scored_guard_cases_passed=0,frozen_expected_stage='structure',native_observed_stage='validation',
        frozen_contract_changed=False,model_artifact_changed=False,kind='Post-result explanatory audit, not rescored acceptance'))
    save('OFFLINE-CHECKS.json',dict(timestamp=now(),passed=True,integrity_only=True,full_functional_acceptance=False,
        lineage_verified=True,native_event_arguments_and_feedback_verified=True,frozen_expectations_verified=23,
        frozen_acceptance_passed=19,replay_records_verified=69,model_calls=0,manual_semantic_repairs=0,
        frozen_transport_tests=dict(methods=17,returncode=suite.returncode,stdout=suite.stdout,stderr=suite.stderr),
        prior_verify_assertion='Original verifier requires full acceptance; fails at assert f[passed] and r[all_equal]. Preserved, not repaired.'))
    timings=[v['times'] for v in f['records']]
    totals={key:sum(t.get(key,0) for t in timings) for key in {key for t in timings for key in t}}
    save('SUMMARY.json',dict(timestamp=now(),artifact_sha256=sha(HERE/'LIVE/ARTIFACT.json'),artifact_content_identity=identity(artifact),definition_identity=d['identity'],
        acceptance_passed=19,acceptance_total=23,replay_observations=69,replay_passes=3,precedence_conflicts_native_correct=3,
        successful_work=[v['evidence']['observation']['work'] for v in f['records'] if v['evidence']['observation']['status']=='success'],
        functional_time_totals=totals,adapter_times=m['adapter_times'],coordinator_expectation_defect=True))
    print('Integrity PASS; frozen acceptance remains19/23; replay69/69; native precedence3/3; transport17/17')

if __name__=='__main__':
    main()
