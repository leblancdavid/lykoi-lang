"""Pre-exposure qualification, not participant task solutions."""
import copy
import json
import adapter as a

c = a.c


def fixture():
    return dict(version='construct-1', target='Control', definitions=[dict(name='Control',
        inputs=[['z', 'Int64'], ['permit', 'Bool']], result_type='Int64', result='$base',
        ops=[['base', 'value', 'Int64', ['add', '$z', 4], ['z']],
             ['bound', 'check', ['le', '$base', 40], 3, 'BIG', ['base']],
             dict(repeat=2, body=[['gate', 'check', '$permit', 3, 'FLAG', ['permit']]])])])


def run():
    rows = []
    base = fixture()
    result = a.construct(json.dumps(base), 'B')
    assert result['typed_valid'], result
    # Independently authored full structural twin, no compact-to-full conversion.
    full = dict(target='Control', definitions=[dict(name='Control', revision=1,
        params=[dict(name='z', type='Int64'), dict(name='permit', type='Bool')], dependencies={},
        steps=[dict(id='s001', type='Int64', deps=['z'], node=dict(op='value', expr={'add': [{'ref': 'z'}, {'const': 4}]})),
               dict(id='s002', type='Unit', deps=['s001'], node=dict(op='check', test={'le': [{'ref': 's001'}, {'const': 40}]}, site={'const': 3}, code='BIG')),
               dict(id='s003', type='Unit', deps=['permit'], node=dict(op='check', test={'ref': 'permit'}, site={'const': 3}, code='FLAG')),
               dict(id='s004', type='Unit', deps=['permit'], node=dict(op='check', test={'ref': 'permit'}, site={'const': 3}, code='FLAG'))],
        order=['s001', 's002', 's003', 's004'], result={'ref': 's001'}, result_type='Int64')])
    twin = a.construct(json.dumps(full), 'A')
    assert twin['typed_valid'], twin
    assert twin['artifact']['definitions'] == result['artifact']['definitions']
    observations = []
    for z, permit in [(0, True), (36, True), (37, True), (0, False), (2**63-1, True)]:
        args = dict(z=z, permit=permit)
        package = a.package(result['artifact'], args)
        expanded = c.expand(package)
        # Independent native expanded tree, manually preserving template substitution
        # and all seq/value/check nodes, rather than calling wrapper expansion twice.
        root = 'program/' + package['program']['identity']
        target = root + '/invocation/' + package['definitions'][0]['identity']
        bind = c.binding(target, 's001')
        sequence = dict(id=target, op='seq', steps=[
            dict(bind=bind, node=dict(id=target + '/s001', op='value', expr={'add': [{'const': z}, {'const': 4}]})),
            dict(bind=c.binding(target, 's002'), node=dict(id=target + '/s002', op='check', test={'le': [{'ref': bind}, {'const': 40}]}, site={'const': 3}, code='BIG')),
            dict(bind=c.binding(target, 's003'), node=dict(id=target + '/s003', op='check', test={'const': permit}, site={'const': 3}, code='FLAG')),
            dict(bind=c.binding(target, 's004'), node=dict(id=target + '/s004', op='check', test={'const': permit}, site={'const': 3}, code='FLAG'))], result={'ref': bind})
        native = dict(version='semantic-plan-1', text=False, rules={},
            decode=dict(id=root, op='seq', steps=[dict(bind=c.binding(root, 'invocation'), node=sequence)], result={'ref': c.binding(root, 'invocation')}),
            encode=dict(id=root + '/encode', op='emit', codec='uint16be', expr={'ref': 'root'}))
        assert native == expanded['plan']
        normal = c.vm.execute(native, b'')
        for budget in [None] + list(range(normal['work'] + 2)):
            limits = None if budget is None else {'work': budget}
            left = c.vm.execute(native, b'', limits)
            right = c.vm.execute(expanded['plan'], b'', limits)
            assert left == right
            observations.append(dict(args=args, budget=budget, envelope=left))
    rows.append(dict(id='independent_full_and_native_twins', pass_=True, observations=len(observations)))
    bads = []
    def bad(label, edit, code=None):
        value = copy.deepcopy(base)
        edit(value['definitions'][0], value)
        rejected = a.construct(json.dumps(value), 'B')
        assert not rejected['typed_valid'], label
        if code:
            assert rejected['diagnostic']['code'] == code, (label, rejected)
        bads.append(dict(id=label, diagnostic=rejected['diagnostic']))
    bad('unknown_ref', lambda d, v: d['ops'][0].__setitem__(3, '$missing'), 'UNKNOWN_REFERENCE')
    bad('forward_ref', lambda d, v: d['ops'][0].__setitem__(3, '$bound'), 'UNKNOWN_REFERENCE')
    bad('wrong_type', lambda d, v: d['ops'][0].__setitem__(2, 'Bool'), 'TYPE')
    bad('missing_deps', lambda d, v: d['ops'][0].__setitem__(4, []), 'DEPENDENCY')
    bad('extra_deps', lambda d, v: d['ops'][0].__setitem__(4, ['z', 'permit']), 'DEPENDENCY')
    bad('shadow', lambda d, v: d['ops'][0].__setitem__(0, 'z'), 'CAPTURE')
    bad('unsupported_op', lambda d, v: d['ops'][0].__setitem__(1, 'python'))
    bad('callback_field', lambda d, v: d.__setitem__('callback', 'eval'))
    bad('repeat_escape', lambda d, v: d.__setitem__('result', '$gate'), 'UNKNOWN_REFERENCE')
    bad('repeat_bound', lambda d, v: d['ops'][2].__setitem__('repeat', 5))
    bad('nested_repeat', lambda d, v: d['ops'][2]['body'].__setitem__(0, dict(repeat=2, body=[])))
    bad('step_bound', lambda d, v: d.__setitem__('ops', [dict(repeat=4, body=[['a'+str(i), 'value', 'Int64', i, []] for i in range(8)])] + [['last', 'value', 'Int64', 0, []]]), 'RESOURCE')
    bad('symbol_cycle', lambda d, v: (d.__setitem__('ops', [['selfcall', 'compose', 'Control', {'z': '$z', 'permit': '$permit'}, ['z', 'permit']]]), d.__setitem__('result', '$selfcall')), 'CYCLE')
    bad('computed_call_arg', lambda d, v: d.__setitem__('ops', [['selfcall', 'compose', 'Control', {'z': ['add', '$z', 1], 'permit': '$permit'}, ['z', 'permit']]]))
    for label, text in [('duplicate_keys', '{"version":"construct-1","version":"construct-1"}'),
                        ('float', '{"value":1.2}'), ('nonfinite', '{"value":NaN}')]:
        rejected = a.construct(text, 'B')
        assert not rejected['strict_valid']
        bads.append(dict(id=label, diagnostic=rejected['diagnostic']))
    # Actual model-authored registry capability is exercised with host controls,
    # without providing a library to the participant.
    nested = dict(version='construct-1', target='RootControl', definitions=[
        dict(name='LeafControl', inputs=[['v', 'Int64']], ops=[['x', 'value', 'Int64', '$v', ['v']]], result='$x', result_type='Int64'),
        dict(name='MidControl', inputs=[['v', 'Int64']], ops=[['x', 'compose', 'LeafControl', {'v': '$v'}, ['v']]], result='$x', result_type='Int64'),
        dict(name='RootControl', inputs=[], ops=[['x', 'compose', 'MidControl', {'v': 42}, []]], result='$x', result_type='Int64')])
    nested_result = a.construct(json.dumps(nested), 'B')
    assert nested_result['typed_valid'], nested_result
    plan = c.expand(a.package(nested_result['artifact'], {}))['plan']
    obs = c.vm.execute(plan, b'')
    assert obs['status'] == 'success' and obs['value'] == 42
    rows.append(dict(id='authored_nested_registry', pass_=True, envelope=obs))
    wrong = copy.deepcopy(nested)
    wrong['definitions'][-1]['ops'][0][3]['v'] = 41
    wrong_result = a.construct(json.dumps(wrong), 'B')
    assert wrong_result['typed_valid']
    wrong_obs = c.vm.execute(c.expand(a.package(wrong_result['artifact'], {}))['plan'], b'')
    assert wrong_obs['value'] != 42
    rows.append(dict(id='valid_but_wrong', pass_=True, envelope=wrong_obs))
    # Byte read/end remain frozen semantics; no task uses these controls.
    byte = dict(version='construct-1', target='ByteControl', definitions=[dict(name='ByteControl', inputs=[],
        ops=[['v', 'atom'], ['done', 'end']], result='$v', result_type='Int64')])
    br = a.construct(json.dumps(byte), 'B')
    assert br['typed_valid']
    bp = c.expand(a.package(br['artifact'], {}))['plan']
    assert c.vm.execute(bp, b'\x2a')['value'] == 42
    assert c.vm.execute(bp, b'\x2a\x00')['error']['code'] == 'TRAILING'
    rows.append(dict(id='atom_end', pass_=True))
    return dict(positive_controls=rows, rejections=bads, differential_observations=observations,
        total_controls=len(rows) + len(bads), passed=True,
        participant_exposed=False, qualification='finite mechanical preservation, not universal equivalence')
