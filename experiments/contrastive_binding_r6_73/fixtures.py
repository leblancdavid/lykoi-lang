"""Coordinator-written requirements and literal expectations; no candidate execution."""
import copy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'experiments/incremental_data_r6_63'))
from freeze import state, fixture, pin


def ref(name):
    return {'ref': name}


def lit(typ, value):
    return {'literal': {'type': typ, 'value': value}}


def decision(op, left, right, deps):
    return dict(op=op, left=left, right=right, deps=deps)


def expectations():
    rows = []

    def pair(family, params, literals, prefix, entries):
        for index, (requirement, target, result_type, cases, alternatives) in enumerate(entries, 1):
            scope = state('Contrast' + family.replace('-', '') + str(index), params, literals, result_type, prefix)
            rows.append(dict(id=family + '-P' + str(index), family=family,
                contrast_id=family + '-C1', requirement=requirement,
                requirement_identity=pin(requirement), scope=scope, scope_identity=scope['identity'],
                target=target, cases=cases, negatives=alternatives,
                partition='training', provenance='COORDINATOR_AUTHORED_SYNTHETIC',
                review='COORDINATOR_ONLY'))

    def neg(target, field, value, kind, reason):
        wrong = copy.deepcopy(target)
        wrong[field] = value
        return dict(decision=wrong, expected_category=kind, reason=reason)

    R, L, D = ref, lit, decision
    params = [('used', 'Int64'), ('limit', 'Int64'), ('spare', 'Int64')]
    arguments = [dict(used=2, limit=5, spare=9), dict(used=5, limit=2, spare=-4), dict(used=3, limit=3, spare=0)]
    specs = [('add', 'Total used followed by limit; spare is unrelated.', 'Int64', [7, 7, 6]),
             ('le', 'Is used at most limit, including equality? Use used then limit.', 'Bool', [True, False, True]),
             ('eq', 'Do used and limit match exactly? Use used then limit.', 'Bool', [False, False, True])]
    for family, choices in [('F01-add-le', (0, 1)), ('F02-le-eq', (1, 2))]:
        entries = []
        for choice in choices:
            op, req, typ, values = specs[choice]
            target = D(op, R('used'), R('limit'), ['limit', 'used'])
            other = 'le' if op == 'add' else ('eq' if op == 'le' else 'le')
            category = 'semantic_rejection' if family == 'F01-add-le' else 'valid_but_wrong'
            entries.append((req, target, typ, [fixture(a, v) for a, v in zip(arguments, values)],
                [neg(target, 'op', other, category, 'Requirement selects a different relation/result obligation.'),
                 neg(target, 'left', R('spare'), 'semantic_rejection', 'Wrong reference and stale declared dependencies.')]))
        pair(family, params, [], [], entries)

    entries = []
    for left, right, values in [('used', 'limit', [True, False, True]), ('limit', 'used', [False, True, True])]:
        target = D('le', R(left), R(right), ['limit', 'used'])
        wrong = D('le', R(right), R(left), ['limit', 'used'])
        entries.append((f'Is {left} no greater than {right}? Keep that operand order.', target, 'Bool',
            [fixture(a, v) for a, v in zip(arguments, values)],
            [dict(decision=wrong, expected_category='valid_but_wrong', reason='Inclusive comparison direction is reversed.'),
             neg(target, 'op', 'eq', 'valid_but_wrong', 'Equality omits strictly-less cases.')]))
    pair('F03-order', params, [], [], entries)

    entries = []
    for name, values in [('used', [2, 5, 3]), ('spare', [9, -4, 0])]:
        target = D('add', R(name), L('Int64', 0), [name])
        other = 'spare' if name == 'used' else 'used'
        wrong = D('add', R(other), L('Int64', 0), [other])
        entries.append((f'Return the total of {name} and literal zero; other fields are distractors.', target, 'Int64',
            [fixture(a, v) for a, v in zip(arguments, values)],
            [dict(decision=wrong, expected_category='valid_but_wrong', reason='Requirement names the other stored quantity.'),
             neg(target, 'deps', [], 'semantic_rejection', 'Selected reference must remain an explicit direct dependency.')]))
    pair('F04-distractor', params, [0], [], entries)

    args = [dict(reading=0, baseline=4), dict(reading=4, baseline=0), dict(reading=-2, baseline=-2)]
    entries = []
    for right, deps, values, req in [(L('Int64', 0), ['reading'], [True, False, False], 'Compare reading exactly with literal zero, not stored baseline.'),
                                    (R('baseline'), ['baseline', 'reading'], [False, False, True], 'Compare reading exactly with stored baseline, not literal zero.')]:
        target = D('eq', R('reading'), right, deps)
        other = R('baseline') if 'literal' in right else L('Int64', 0)
        wrong = D('eq', R('reading'), other, ['baseline', 'reading'] if 'ref' in other else ['reading'])
        entries.append((req, target, 'Bool', [fixture(a, v) for a, v in zip(args, values)],
            [dict(decision=wrong, expected_category='valid_but_wrong', reason='Literal and stored baseline can differ.'),
             neg(target, 'right', L('Bool', False), 'semantic_rejection', 'Boolean false is not integer zero.')]))
    pair('F05-literal-ref', [('reading', 'Int64'), ('baseline', 'Int64')], [0, False], [], entries)

    prefix = [dict(id='adjusted', type='Int64', deps=['raw'], node=dict(op='value', expr={'add': [R('raw'), {'const': 1}]})),
              dict(id='echo', type='Int64', deps=['raw'], node=dict(op='value', expr=R('raw')))]
    args = [dict(raw=0, noise=10), dict(raw=4, noise=-2), dict(raw=-3, noise=1)]
    entries = []
    for right, deps, values in [(L('Int64', 1), ['adjusted'], [2, 6, -1]), (R('echo'), ['adjusted', 'echo'], [1, 9, -5])]:
        target = D('add', R('adjusted'), right, deps)
        entries.append(('Total adjusted then ' + ('literal one' if 'literal' in right else 'echo') +
            '. Declare only distinct direct operands, excluding their indirect raw source.', target, 'Int64',
            [fixture(a, v) for a, v in zip(args, values)],
            [neg(target, 'deps', ['raw'], 'semantic_rejection', 'Indirect source is not the selected direct dependency.'),
             neg(target, 'deps', [], 'semantic_rejection', 'Direct prior result dependencies cannot be omitted.')]))
    pair('F06-dependencies', [('raw', 'Int64'), ('noise', 'Int64')], [1], prefix, entries)

    args = [dict(count=0, active=True), dict(count=1, active=False), dict(count=0, active=False)]
    entries = []
    for name, right, values in [('count', L('Int64', 0), [True, False, True]), ('active', L('Bool', False), [False, True, True])]:
        target = D('eq', R(name), right, [name])
        bad = L('Bool', False) if name == 'count' else L('Int64', 0)
        entries.append((f'Check {name} exactly against ' + ('integer zero.' if name == 'count' else 'Boolean false.'), target, 'Bool',
            [fixture(a, v) for a, v in zip(args, values)],
            [neg(target, 'right', bad, 'semantic_rejection', 'Equality requires equal authoritative operand types.'),
             neg(target, 'right', L('Int64', False), 'schema_rejection', 'False cannot inhabit an Int64 typed literal.')]))
    pair('F07-typed', [('count', 'Int64'), ('active', 'Bool')], [0, False], [], entries)

    args = [dict(raw=0, noise=10), dict(raw=4, noise=-2), dict(raw=-3, noise=1)]
    entries = []
    for op, typ, values in [('add', 'Int64', [2, 10, -4]), ('eq', 'Bool', [True, True, True])]:
        target = D(op, R('adjusted'), R('adjusted'), ['adjusted'])
        wrong = D(op, R('adjusted'), R('echo'), ['adjusted', 'echo'])
        entries.append((('Total' if op == 'add' else 'Test equality of') + ' adjusted with adjusted. Repeat the reference in both operand slots; list its dependency once.',
            target, typ, [fixture(a, v) for a, v in zip(args, values)],
            [neg(target, 'deps', ['adjusted', 'adjusted'], 'schema_rejection', 'Repeated operands do not authorize duplicate dependencies.'),
             dict(decision=wrong, expected_category='valid_but_wrong', reason='Echo differs from adjusted by one; repeated identity is required.')]))
    pair('F08-repeated', [('raw', 'Int64'), ('noise', 'Int64')], [1], prefix, entries)

    entries = []
    for op, values, req in [('le', [False, False, False], 'Is adjusted at most echo?'), ('eq', [False, False, False], 'Does adjusted exactly equal echo?')]:
        target = D(op, R('adjusted'), R('echo'), ['adjusted', 'echo'])
        other = 'eq' if op == 'le' else 'le'
        # These distinct relations happen to agree on this immutable prefix.
        entries.append((req + ' Use adjusted first, echo second, and their shared direct dependency structure.', target, 'Bool',
            [fixture(a, v) for a, v in zip(args, values)],
            [neg(target, 'op', other, 'valid_but_wrong', 'Requirement selects a distinct operation even though this prefix masks the behavioral difference.'),
             neg(target, 'deps', ['raw'], 'semantic_rejection', 'Shared transitive raw source is not the pair of direct identities.')]))
    pair('F09-shared', [('raw', 'Int64'), ('noise', 'Int64')], [1], prefix, entries)
    return rows
