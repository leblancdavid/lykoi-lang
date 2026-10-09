"""Pre-participant transport controls and requirement-derived oracle freeze."""
import copy
import json
import os
import subprocess
import sys
from transport import ROOT, HERE, OUT, load, save, raw, sha, config, AGENT_PROMPT, TOOLS, c, Registry, package

REQUIREMENT = '''Construct reusable typed composition WindowCharge(start:Int64,end:Int64,cap:Int64)->Int64.
Check in this order: start>=0 (START_NEGATIVE, source start); end<=cap (END_CAP,
source end); start+start<=end (WINDOW_NARROW, source start). Return end+start.
Checks have local source labels c_start,c_cap,c_width respectively. Use existing
checked signed64 arithmetic. Do not invent subtraction/multiplication or host callbacks.
CallerA reads start then end as two UInt8 bytes, requires end-of-input BEFORE the
composition, calls with cap=200, then adds3 to the composition output. CallerB reads
one UInt8 start, requires end-of-input BEFORE arithmetic/composition, computes
end=start+20, calls with cap=180, and returns the composition output unchanged.
Name roots CallerA and CallerB. Reading steps must be named read_start/read_end,
end check input_end, composition invocation charge. Immutable identities are returned
by tools. Admit reusable definition, retrieve it, admit both callers, retrieve and
validate both, and execute representative success and ordered failure inputs.
Stop after the original stage. No successor is requested yet.'''

MODIFICATION = '''Create a signature-preserving WindowCharge successor retaining all original checks,
their order, codes and source labels. Its result becomes end+start+start instead of
end+start. Admit against the exact predecessor and retrieve the successor.
Create the exact CallerA successor by changing only its WindowCharge dependency
and compose-call pins. Preserve all other CallerA content including revision1.
Admit against CallerA's predecessor. Explicitly migrate the family using total
decisions: CallerA updated to its successor, CallerB retained via null.
Retrieve all predecessor/successor identities, validate and execute selected CallerA
and retained CallerB, and verify the final dependency graph. Do not redirect CallerB.'''

GUIDE = '''Definition fields exactly: name,revision=1,params:[{name,type}],dependencies:
symbol->pin,steps:[{id,type,deps,node}],order:[step IDs],result:expression,result_type.
Omit identity only on admission; use tool-returned immutable pins afterward.
Types Int64/Bool/Unit. Expressions {ref:name},{const:int/bool/null},{add:[e,e]},
{le:[e,e]},{eq:[e,e]}. Nodes {op:value,expr:e}, {op:check,test:e,site:e,code:CODE},
{op:atom,codec:uint8},{op:end},{op:compose,symbol:name,identity:pin,args:{param:ref/const}}.
deps exactly enumerate all referenced local IDs/parameters, including check site.
Check/end return Unit; atom returns Int64; value/compose types follow expressions.
Order is an exact dependency-respecting permutation; no shadowing or cycles.
Root params[] and result_type Int64; final root encoded UInt16BE. Max32 steps,
8 definitions/closure,64 expanded nodes,depth4. Admission does static validation,
not functional acceptance. Retrieval provides closed definitions and dependency
impact. Validate/execute take admitted closed-root identity; execute also input_hex.
Use actual MCP tools. No host JSON-action broker exists in this round.'''


def qualify_controls():
    live = [json.loads(line) for line in (OUT / 'qualification/MCP.jsonl').read_text().splitlines()]
    calls = [r for r in live if r['request']['method'] == 'tools/call']
    assert {r['request']['params']['name'] for r in calls} == {t['name'] for t in TOOLS}
    assert any(r['response']['result'].get('structuredContent', {}).get('value') == 11 for r in calls)
    assert any(r['response']['result'].get('structuredContent', {}).get('code') == 'TYPE' for r in calls)
    registry = Registry(OUT / 'qualification/registry')
    original = next(iter(registry.read()['state']['definitions'].values()))
    env = os.environ.copy()
    env['R637_PHASE'] = 'qualification'
    child = subprocess.Popen([sys.executable, '-B', str(HERE / 'tools.py')], env=env,
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    exchanges = []

    def invoke(name, args, error=None):
        request = dict(jsonrpc='2.0', id=100+len(exchanges), method='tools/call',
            params={'name': name, 'arguments': args})
        child.stdin.write(json.dumps(request)+'\n'); child.stdin.flush()
        response = json.loads(child.stdout.readline())
        exchanges.append(dict(request=request, response=response))
        result = response['result']
        assert result['isError'] == (error is not None), result
        value = result['structuredContent']
        if error:
            assert value['code'] == error, result
        return value

    old = original['identity']
    invoke('lykoi_retrieve', {}, 'SHAPE')
    invoke('lykoi_execute', {'identity': old, 'input_hex': 'z'}, 'ARGUMENT_SCHEMA')
    invoke('lykoi_retrieve', {'identity': 'bad'}, 'IDENTITY')
    before = registry.read()['token']
    bad = {k: v for k, v in original.items() if k != 'identity'}
    bad = copy.deepcopy(bad); bad['name'] = 'NoHost'; bad['steps'][0]['node']['op'] = 'python'
    invoke('lykoi_admit', {'action': dict(action='admit', definitions=[bad], predecessor=None)}, 'UNSUPPORTED')
    assert registry.read()['token'] == before
    caller = dict(name='NeutralCaller', revision=1, params=[], dependencies={'NeutralProbe': old},
        steps=[dict(id='call', type='Int64', deps=[], node=dict(op='compose', symbol='NeutralProbe',
            identity=old, args={}))], order=['call'], result={'ref': 'call'}, result_type='Int64')
    caller_pin = invoke('lykoi_admit', {'action': dict(action='admit', definitions=[caller],
        predecessor=None)})['pins'][0]
    new = {k: copy.deepcopy(v) for k, v in original.items() if k != 'identity'}
    new['steps'][0]['node']['expr'] = {'const': 12}
    new_pin = invoke('lykoi_admit', {'action': dict(action='admit', definitions=[new],
        predecessor=old)})['pins'][0]
    invoke('lykoi_admit', {'action': dict(action='migrate', predecessor=old, successor=new_pin,
        decisions={})}, 'PARTIAL_MIGRATION')
    newcaller = copy.deepcopy(caller)
    newcaller['dependencies']['NeutralProbe'] = new_pin
    newcaller['steps'][0]['node']['identity'] = new_pin
    cp = invoke('lykoi_admit', {'action': dict(action='admit', definitions=[newcaller],
        predecessor=caller_pin)})['pins'][0]
    invoke('lykoi_admit', {'action': dict(action='migrate', predecessor=old, successor=new_pin,
        decisions={caller_pin: cp})})
    assert invoke('lykoi_execute', {'identity': caller_pin, 'input_hex': ''})['value'] == 11
    assert invoke('lykoi_execute', {'identity': cp, 'input_hex': ''})['value'] == 12
    child.stdin.close(); child.wait(timeout=10)
    save(OUT / 'QUALIFICATION-CONTROLS.json', dict(passed=True, exchanges=exchanges,
        discovery_observed=True, actual_model_semantic_MCP_calls=len(calls),
        first_live_proposal_rejected=True, model_corrected_live_shape=True,
        live_TYPE_rejection=True, backend='unchanged R6.32/R6.18/R6.10',
        lifecycle_successor_and_migration_controls=True, invalid_mutation_rollback=True,
        original_four_tool_gap='R6.25 declare/apply/result/validate has no persistent registry '
            'admit/retrieve/successor/migrate operations; R6.27 qualified echoes only',
        adapter_scope='Transport-only lifecycle facade, exact R6.32 contracts remain authoritative'))


def freeze():
    assert load(OUT / 'QUALIFICATION-CONTROLS.json')['passed']
    raw(OUT / 'REQUIREMENT.txt', REQUIREMENT+'\n')
    raw(OUT / 'MODIFICATION.txt', MODIFICATION+'\n')
    raw(OUT / 'GUIDE.txt', GUIDE+'\n')
    points = [0, 1, 10, 20, 40, 80, 100, 160, 180, 199, 200, 201, 255]
    save(OUT / 'ACCEPTANCE-EXPECTATIONS.json', dict(
        source='Requirement-derived, frozen before participant authoring; same coordinator, no independent cognition',
        A_pairs=[[s,e] for s in points for e in points], B_starts=list(range(256)),
        invalid_A=['', '01', '010200', 'c9ffff'], invalid_B=['', '0100', 'ff00'],
        constant_probes=[[-1,999,200], [10,9,8], [10,19,200], [10,20,200],
            [0,0,0], [0,65535,65535], [0,65536,65536]],
        expected_check_precedence=['START_NEGATIVE','END_CAP','WINDOW_NARROW'],
        check_sources={'START_NEGATIVE':['c_start','start'], 'END_CAP':['c_cap','end'],
            'WINDOW_NARROW':['c_width','start']},
        error_stages={'checks':'validation', 'TRUNCATED':'structure','TRAILING':'structure',
            'ENCODE_RANGE':'encode','INPUT_TYPE':'plan_reject','Bool_argument':'TYPE static'},
        dependencies={'A':'old','B':'old','A_new':'new','B_retained':'old'},
        original_formula='end+start', successor_formula='end+start+start',
        invalid_order='end-of-input before arithmetic/checks; END_CAP before WINDOW_NARROW',
        successful_root_provenance='span=[0,input_length],origins=[]; UInt16BE output',
        work='Requirement does not prescribe graph implementation work; compare all work on replay, '
            'require positive bounded work and frozen VM work-limit classifications',
        error_nodes='exact required source labels substituted into hygienic pinned expansion path'))
    save(OUT / 'TASK-PROVENANCE.json', dict(fresh_synthetic_requirement=True,
        selection='Coordinator designed ordered geometric-window pricing relation after qualification; '
            'distinct from prior Increment, OffsetTotal and BoundedScore examples inspected',
        limitations=['Capability-tailored and coordinator-designed', 'No exhaustive historical uniqueness proof',
            'Fresh participant lacks task/oracle file access via denied tools; hidden provider context exclusion unattested'],
        staged_modification='Only sent after original acceptance; no file tools permitted',
        fresh_session=True, full_R6_31_study=False))
    save(OUT / 'MODEL.json', dict(config=config('authoring'), provider='openai', model='gpt-6.1-sol',
        requested_reasoning={'reasoningEffort':'high'}, effective_reasoning=None,
        budget={'model_completions':30,'MCP_calls':40,'wall_seconds':1200,'corrections_per_stage':2},
        section_estimator='UTF-8 content characters /4 rounded up, not a model tokenizer; low confidence',
        exact_request_serialization=False, instrumentation='Read-only JSON events, MCP exchange log and session export; '
            'no request hooks or model behavior changes; visible section accounting reconstructed per completion'))
    paths = [p for p in HERE.iterdir() if p.is_file()] + [OUT / n for n in
        ('REQUIREMENT.txt','MODIFICATION.txt','GUIDE.txt','ACCEPTANCE-EXPECTATIONS.json',
         'TASK-PROVENANCE.json','MODEL.json','QUALIFICATION-CONTROLS.json')]
    save(OUT / 'TASK-FREEZE.json', dict(participant_completions=0,
        inputs={p.relative_to(ROOT).as_posix(): sha(p) for p in paths}))
    print('Actual semantic MCP qualification and fresh task/oracle freeze complete')


if __name__ == '__main__':
    qualify_controls()
    freeze()
