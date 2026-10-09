"""Scripted copied exposed fixture; decisions stay in production predicates."""
import copy
import json
from lifecycle import ROOT, digest

SOURCE = ROOT / 'benchmark/results/phase6/r6_16/submissions/C/kiln/base/intent.json'
REQUIRED = {'definition:vent_policy', 'predicate:ignite_gate', 'predicate:set_gate_lock',
            'invariant:firing_vent', 'transition:ignite', 'transition:set_gate'}
UNAFFECTED = {'behavior:create', 'behavior:list', 'field:id', 'field:created_at',
              'field:label', 'field:load', 'field:phase', 'field:vent'}


def copies():
    original = json.loads(SOURCE.read_text())
    modified = copy.deepcopy(original)
    emergency = dict(op='eq',
        left=dict(kind='field', value='load', **original['fields']['load']),
        right=dict(kind='literal', value='emergency', **original['fields']['load']))
    gate = modified['operations']['ignite']['guards'][1]
    gate['condition'] = dict(op='or', children=[gate['condition'], copy.deepcopy(emergency)])
    gate = modified['operations']['set_gate']['guards'][0]
    gate['condition'] = dict(op='or', children=[gate['condition'], copy.deepcopy(emergency)])
    modified['invariants'][0]['children'].append(copy.deepcopy(emergency))
    return original, modified


def dependencies(intent):
    """Explicit fixture policy snapshots, not a substitute for production impact."""
    rule = dict(ignite=intent['operations']['ignite']['guards'][1]['condition'],
                set_gate=intent['operations']['set_gate']['guards'][0]['condition'],
                invariant=intent['invariants'][0])
    pin = digest(rule)
    return dict(policy=rule, identity=pin,
        consumers={'transition:ignite': pin, 'transition:set_gate': pin,
                   'invariant:firing_vent': pin})


def valid_record(phase, vent, load, changed):
    return phase == 'cold' or vent == 'open' or (changed and load == 'emergency')


def expected(op, record, changed, value=None):
    """Requirement-derived oracle, never reads candidate predicates or generated IR."""
    phase, vent, load = (record[k] for k in ('phase', 'vent', 'load'))
    if not valid_record(phase, vent, load, changed):
        return {'error': 'invalid_state'}
    result = copy.deepcopy(record)
    if op == 'ignite':
        if phase != 'cold':
            return {'error': 'invalid_transition'}
        if vent == 'closed' and not (changed and load == 'emergency'):
            return {'error': 'gate_required'}
        result['phase'] = 'firing'
    elif op == 'set_gate':
        if phase == 'firing' and value == 'closed' and not (changed and load == 'emergency'):
            return {'error': 'gate_locked'}
        result['vent'] = value
    elif op == 'list':
        return {'ok': [record]}
    return {'ok': result}
