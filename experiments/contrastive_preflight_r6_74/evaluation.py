"""Evaluation-only realization. Never imported by training dataset conversion."""
import copy
from integration import OUT, ROOT, q, read, write, identity, serialize, sha
from fixtures import state, ref, lit, decision


def case(arguments, value):
    return dict(arguments=arguments, expected=dict(status='success', type='Bool', value=value))


def realize():
    rows = []
    system = read(ROOT / 'benchmark/results/phase6/r6_73/qualification_2/SFT-POSITIVES.json')['records'][0]['prompt'][0]

    def add(family, index, requirement, params, literals, prefix, target, cases):
        for rendering in (1, 2):
            scope = state(f'R674{family}{index}R{rendering}', params if rendering == 1 else list(reversed(params)),
                          literals, 'Bool', copy.deepcopy(prefix))
            rows.append(dict(id=f'{family}-{index}-R{rendering}', underlying_requirement=f'{family}-{index}',
                family=family, partition='evaluation_exploratory', requirement=requirement,
                requirement_identity=identity(requirement), scope=scope, scope_identity=scope['identity'],
                target=target, cases=cases, review='COORDINATOR_ONLY', provenance='COORDINATOR_AUTHORED_SYNTHETIC',
                prompt=[system, dict(role='user', content=serialize(dict(requirement=requirement, scope=scope)))]))

    lo, hi = -(2**63), 2**63-1
    args = [dict(amount=lo, bound=hi, flag=True), dict(amount=hi, bound=lo, flag=False),
            dict(amount=0, bound=0, flag=True), dict(amount=-1, bound=0, flag=False)]
    specs = [
        ('Is amount not greater than bound, including equality? Keep amount first.', ref('amount'), ref('bound'), ['amount','bound'], [True,False,True,True]),
        ('Is bound not greater than amount, including equality? Keep bound first.', ref('bound'), ref('amount'), ['amount','bound'], [False,True,True,False]),
        ('Is amount not greater than literal integer zero? Do not use bound.', ref('amount'), lit('Int64',0), ['amount'], [True,False,True,True]),
        ('Does amount exactly equal literal integer zero? Do not use bound.', ref('amount'), lit('Int64',0), ['amount'], [False,False,True,False])]
    for i, (req, left, right, deps, values) in enumerate(specs, 1):
        add('E01-boundary-negation', i, req, [('amount','Int64'),('bound','Int64'),('flag','Bool')], [0,False], [],
            decision('eq' if i == 4 else 'le', left, right, deps), [case(a,v) for a,v in zip(args,values)])

    prefix = [dict(id='first', type='Int64', deps=['a'], node=dict(op='value',expr={'add':[ref('a'),{'const':1}]})),
              dict(id='second', type='Int64', deps=['b'], node=dict(op='value',expr=ref('b')))]
    args = [dict(a=1,b=5,flag=True), dict(a=4,b=2,flag=False), dict(a=2,b=3,flag=True), dict(a=-1,b=4,flag=False)]
    specs = [
        ('Is first at most second? First then second, only their direct dependencies.', 'le', ref('first'), ref('second'), ['first','second'], [True,False,True,True]),
        ('Is second at most first? Second then first, only their direct dependencies.', 'le', ref('second'), ref('first'), ['first','second'], [False,True,True,False]),
        ('Does first exactly equal second? First then second, only direct dependencies.', 'eq', ref('first'), ref('second'), ['first','second'], [False,False,True,False]),
        ('Does first exactly equal itself? Repeat first, declare first once; omit indirect a.', 'eq', ref('first'), ref('first'), ['first'], [True,True,True,True])]
    for i,(req,op,left,right,deps,values) in enumerate(specs,1):
        add('E02-two-independent-prefixes', i, req, [('a','Int64'),('b','Int64'),('flag','Bool')], [1,False], prefix,
            decision(op,left,right,deps), [case(a,v) for a,v in zip(args,values)])

    args = [dict(u=None,v=None,flag=True,count=0), dict(u=None,v=None,flag=False,count=3)]
    specs = [
        ('Check Unit u exactly against typed Unit null; ignore flag and count.', ref('u'), lit('Unit',None), ['u']),
        ('Check Unit u exactly against stored Unit v, not the null literal.', ref('u'), ref('v'), ['u','v']),
        ('Check Unit v exactly against Unit u, in that order.', ref('v'), ref('u'), ['u','v']),
        ('Check Unit u exactly against itself; declare u once.', ref('u'), ref('u'), ['u'])]
    for i,(req,left,right,deps) in enumerate(specs,1):
        add('E03-unit-equality', i, req, [('u','Unit'),('v','Unit'),('flag','Bool'),('count','Int64')], [None,False,0], [],
            decision('eq',left,right,deps), [case(a,True) for a in args])

    # Six exposed examples are memorization diagnostics, never reserved evidence.
    for original in q.rows()[:6]:
        row = copy.deepcopy(original)
        row.update(id='CAL-' + row['id'], partition='training_calibration',
                   underlying_requirement=row['id'], prompt=[system,dict(role='user',content=serialize(dict(requirement=row['requirement'],scope=row['scope'])))])
        rows.append(row)
    assert len(rows) == 30
    return dict(records=rows, evaluation_cases=24, underlying_evaluation_requirements=12,
        exposed_calibration_cases=6, reserved_families=3, independent=False,
        withholding='Coordinator reservation only; no independent reviewer or enforced withholding.',
        unit_limitation='All Unit values are null; identity/order/literal distinctions are structural, not behaviorally discriminated.',
        scope_renderings='Same distractors retained; reverse parameter order; correlated renderings, not independent requirements.',
        expectations_source='Literal coordinator requirement choices and hand-calculated fixtures, frozen before controls or inference.')


if __name__ == '__main__':
    write('EVALUATION.json', realize())
    write('EVALUATION-FREEZE.json', dict(stage='BEFORE_CPU_SCORER_CONTROLS_AND_ALL_MODEL_INFERENCE',
        files={str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in (OUT/'EVALUATION.json', __import__('pathlib').Path(__file__))}))
    print('PASS frozen coordinator-only evaluation: 24 reserved/varied cases + six exposed calibrations')
