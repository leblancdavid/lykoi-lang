"""Scripted client and negative controls; never exposed to the model."""
import copy
import json
from tools import Session, a

def call(name, **arguments):
    return dict(function=dict(name=name, arguments=arguments))

def run():
    s = Session(['value', 'check', 'compose'])
    calls = [call('declare_input', definition='Control24', inputs=[dict(name='z', type='Int64')]),
        call('apply_operation', definition='Control24', alias='v', operation='value', type='Int64',
            expression=['add', '$z', 17], dependencies=['z']),
        call('define_result', definition='Control24', result='$v', result_type='Int64'),
        call('validate_candidate', target='Control24')]
    transcript = []
    for x in calls:
        r = s.dispatch(x)
        transcript.append(dict(call=x, result=r))
        assert r['success'], r
    artifact = s.completed['artifact']
    observations = []
    for z, expected in [(0, 17), (18, 35), (-17, 0), (65518, 65535)]:
        expanded = a.c.expand(a.package(artifact, {'z': z}))
        obs = a.c.vm.execute(expanded['plan'], b'')
        assert obs['status'] == 'success' and obs['value'] == expected
        observations.append(dict(args={'z': z}, expected=expected, expanded=expanded, observation=obs))
    bads = [({}, 'TOOL_SYNTAX'), (call('unknown'), 'TOOL_SYNTAX'),
        (call('declare_input', definition='Bad', inputs='Int64'), 'ARGUMENT_SCHEMA')]
    failures = []
    for x, code in bads:
        client = Session(['value'])
        before = copy.deepcopy(client.packet)
        r = client.dispatch(x)
        assert not r['success'] and r['response']['error']['code'] == code and client.packet == before
        failures.append(dict(call=x, result=r, transactional=True))
    for expression, deps, typ, code in [('$missing', ['missing'], 'Int64', 'UNKNOWN_REFERENCE'),
            (['add', '$z', 1], [], 'Int64', 'DEPENDENCY'),
            (['add', '$z', 1], ['z'], 'Bool', 'TYPE')]:
        client = Session(['value'])
        assert client.dispatch(calls[0])['success']
        before = copy.deepcopy(client.packet)
        x = call('apply_operation', definition='Control24', alias='bad', operation='value', type=typ,
            expression=expression, dependencies=deps)
        r = client.dispatch(x)
        assert not r['success'] and r['response']['error']['code'] == code and client.packet == before
        failures.append(dict(call=x, result=r, transactional=True))
    # Schema-valid, executable and deliberately wrong is a separate acceptance control.
    wrong = copy.deepcopy(s.packet)
    wrong['definitions'][0]['ops'][0][3][2] = 16
    result = a.construct(json.dumps(wrong), 'B')
    assert result['typed_valid']
    obs = a.c.vm.execute(a.c.expand(a.package(result['artifact'], {'z': 0}))['plan'], b'')
    assert obs['value'] != 17
    return dict(passed=True, scripted_transcript=transcript, observations=observations,
        negative_controls=failures, valid_but_wrong=obs, participant_success=False)
