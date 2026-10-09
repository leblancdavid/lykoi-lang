"""Collect qualification evidence and actual stdio malformed-input controls."""
import copy
import json
import subprocess
import sys
from common import HERE, ROOT, read, save, sha, now, tools
from bridge import SCHEMAS, definitions
from adapter import publish

def rows(label):
    return [json.loads(s) for s in (HERE / label / 'MCP.jsonl').read_text().splitlines()]

def collect():
    matrix = []
    for name, schema in SCHEMAS.items():
        label = 'SCHEMA-' + name
        data = rows(label)
        listed = next(r['response']['result']['tools'] for r in data if r['request']['method']=='tools/list')
        assert listed[0]['inputSchema'] == schema
        status = (HERE/label/'STATUS.txt').read_text(encoding='utf-8')
        matrix.append(dict(form=name, server_published=True, opencode_discovery='connected' if 'connected' in status else 'failed',
                           SDK_provider_invocation='NOT_REACHED' if name=='root_union' else 'See synthetic live invocations',
                           discriminator_semantics='Annotation only; oneOf+const enforces disjoint branches' if name=='discriminator' else None))
    save('SCHEMA-MATRIX.json', dict(timestamp=now(), matrix=matrix, actual_route='OpenCode1.18.32 / stdio MCP2025-11-25 / openai/gpt-6.1-sol'))
    sdk = subprocess.run(['node', str(HERE/'sdk_probe.mjs')], capture_output=True, text=True, encoding='utf-8', timeout=30)
    assert sdk.returncode == 0, sdk.stderr
    save('SDK-VALIDATION.json', json.loads(sdk.stdout))

    # Actual stdio boundary controls; no model and no semantic session instantiated.
    label = 'BRIDGE-CONTROLS'
    directory = HERE/label
    assert not directory.exists()
    directory.mkdir()
    valid = [dict(name='declare_input', arguments={'definition':'Neutral','inputs':[]}),
             dict(name='apply_operation', arguments={'definition':'Neutral','alias':'v','operation':'value','type':'Int64','expression':4,'dependencies':[]}),
             dict(name='apply_operation', arguments={'definition':'Neutral','alias':'c','operation':'check','expression':True,'site':1,'code':'NEUTRAL','dependencies':[]}),
             dict(name='apply_operation', arguments={'definition':'Neutral','alias':'p','operation':'compose','symbol':'Other','arguments':{},'dependencies':[]}),
             dict(name='define_result', arguments={'definition':'Neutral','result':0,'result_type':'Int64'}),
             dict(name='validate_candidate', arguments={'target':'Neutral'})]
    invalid = []
    for call in valid:
        for field in call['arguments']:
            item = copy.deepcopy(call)
            del item['arguments'][field]
            invalid.append(item)
        invalid.append(dict(name=call['name'], arguments=dict(call['arguments'], provider_metadata={'id':'x'})))
    invalid += [dict(name='apply_operation', arguments=dict(valid[1]['arguments'],site=1)),
                dict(name='apply_operation', arguments=dict(valid[1]['arguments'],operation='unknown')),
                dict(name='apply_operation', arguments=dict(valid[1]['arguments'],dependencies=['x','x'])),
                dict(name='apply_operation', arguments=dict(valid[3]['arguments'],expression=4)),
                dict(name='not_allowed', arguments={})]
    requests = [dict(jsonrpc='2.0', id=0, method='initialize', params={'protocolVersion':'2025-11-25'}),
                dict(jsonrpc='2.0', id=1, method='tools/list')]
    requests += [dict(jsonrpc='2.0',id=i+2,method='tools/call',params=call) for i,call in enumerate(valid+invalid)]
    proc = subprocess.run([sys.executable,str(HERE/'bridge.py'),label,'exact'],input='\n'.join(json.dumps(r) for r in requests)+'\n',
                          capture_output=True,text=True,encoding='utf-8',timeout=30)
    assert proc.returncode==0,proc.stderr
    (directory/'STDOUT.jsonl').write_text(proc.stdout,encoding='utf-8')
    (directory/'STDERR.txt').write_text(proc.stderr,encoding='utf-8')
    responses=[json.loads(s) for s in proc.stdout.splitlines()][2:]
    assert all(not r['result']['isError'] for r in responses[:len(valid)])
    assert all(r['result']['isError'] for r in responses[len(valid):])
    save(label+'/RESULT.json',dict(valid=len(valid),invalid=len(invalid),all_matched=True,model_calls=0,semantic_dispatches=0))

    sessions = {}
    for label in ('SYNTHETIC-LIVE','SYNTHETIC-LIVE-2','SYNTHETIC-LIVE-3','EXACT-LIVE','EXACT-LIVE-2','EXACT-LIVE-3'):
        events=[json.loads(s) for s in (HERE/label/'EVENTS.jsonl').read_text().splitlines()]
        calls=[r for r in rows(label) if r['request']['method']=='tools/call']
        steps=[e for e in events if e['type']=='step_finish']
        sessions[label]=dict(completion_steps=len(steps),tool_calls=len(calls),accepted=sum(not r['response']['result']['isError'] for r in calls),
                             rejected=sum(r['response']['result']['isError'] for r in calls),tokens={k:sum(e['part']['tokens'][k] for e in steps) for k in ('input','output','reasoning','total')},
                             cached_read=sum(e['part']['tokens']['cache']['read'] for e in steps),SDK_cost=sum(e['part']['cost'] for e in steps),
                             wall_seconds=read(label+'/RESULT.json')['wall_seconds'])
    assert sessions['SYNTHETIC-LIVE-3']['accepted']==10 and sessions['SYNTHETIC-LIVE-3']['rejected']==1
    assert sessions['EXACT-LIVE-3']['accepted']==4
    assert read('SYNTHETIC-LIVE-3/DELIVERY.json')['matches_requested'] and read('EXACT-LIVE-3/DELIVERY.json')['matches_requested']
    live = [r for r in rows('EXACT-LIVE-3') if r['request']['method']=='tools/call']
    assert [r['request']['params']['name'] for r in live] == [t['name'] for t in definitions('exact')]
    for r in live:
        result=r['response']['result']
        assert result['structuredContent']['echoed']==r['request']['params']['arguments']
        assert result['structuredContent']['inert']
        assert json.loads(result['content'][0]['text'])==result['structuredContent']
    save('MEASUREMENTS.json',dict(sessions=sessions,API_billing=None,raw_upstream_HTTP=None,hidden_context_exclusion='UNATTESTED',
                                SDK_zero_cost_is_not_billing=True,semantic_dispatches=0,scored_tasks_exposed=False,programs_constructed=0))
    original=tools.definitions(['value','check','compose'])
    save('SCHEMA-PUBLICATION.json',dict(original=original,annotated=definitions('exact'),neutral_exposure=definitions('exact-neutral'),
                                      conversion='Only apply_operation adds root type:object. Every branch already requires object; no accepted-instance-set change.',
                                      validation='Original frozen schemas authoritative; no argument conversion',provider_description_metadata='Inert prefix plus full original description in final neutral endpoint'))
    save('RESULT.json',dict(timestamp=now(),classification='R6_27_TOOL_EXPOSURE_QUALIFIED',selected_model='openai/gpt-6.1-sol',
                          neutral_synthetic_passed=True,exact_schema_inert_invocation_passed=True,semantic_contracts_preserved=True,
                          semantic_dispatches=0,scored_exposure=False,stopped=True))

if __name__ == '__main__':
    collect()
