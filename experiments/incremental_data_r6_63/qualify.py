"""Assembly/behavior replay, counterexamples and matched supervision records."""
import copy
import time
from freeze import OUT, ROOT, c, read, sha, pin, write
from assembly import apply, behavior, agrees
from expert import actions


def artifact(path):
    return dict(path=path.relative_to(ROOT).as_posix(),sha256=sha(path))


def frozen_check():
    f = read(OUT/'SOURCE-FREEZE.json')
    assert all(sha(ROOT/p) == h for p,h in f['files'].items())
    s = read(OUT/'SELECTION-FREEZE.json')
    assert sha(OUT/'SOURCE-FREEZE.json') == s['source_freeze_sha256']
    assert sha(OUT/'SELECTION-ACCEPTANCE.json') == s['selection_acceptance_sha256']


def observation_pass(after, fixtures):
    rows = []
    for f in fixtures:
        actual = behavior(after,f['arguments'])
        rows.append(dict(arguments=f['arguments'],expected=f['expected'],actual=actual,passed=agrees(actual,f['expected'])))
    return rows


def qualify():
    frozen_check()
    expected = read(OUT/'SELECTION-ACCEPTANCE.json')['requirements']
    all_actions = actions()
    summaries = []
    for eid, action in all_actions.items():
        folder = OUT/'episodes'/eid
        before = read(folder/'BEFORE.json')
        source = read(folder/'SOURCE.json')
        fixtures = read(folder/'ACCEPTANCE.json')['cases']
        write(folder/'ACTION.json',action)
        op,args = next(iter(action['node']['expr'].items()))
        selection = dict(operation=op,arguments=args,type=action['type'],deps=action['deps'])
        assert selection == expected[eid]
        started = time.perf_counter_ns()
        after, validation = apply(before,action)
        assembly_ns = time.perf_counter_ns()-started
        replay, replay_validation = apply(c.load(c.canonical(before).decode()),c.load(c.canonical(action).decode()))
        assert c.canonical(after) == c.canonical(replay) and validation == replay_validation
        write(folder/'AFTER.json',after)
        write(folder/'A-TARGET.json',after['package'])
        write(folder/'VALIDATION.json',dict(passed=True, native=validation,
             operation_selection=selection, exact_source_selection=True, unchanged_prefix=True,
             before_identity=before['identity'],after_identity=after['identity'], deterministic_replay=True,
             assembly_ns=assembly_ns,identity_method='SHA256 canonical body; native definition pins unchanged'))
        p1 = observation_pass(after,fixtures)
        p2 = observation_pass(replay,fixtures)
        assert p1 == p2 and all(r['passed'] for r in p1)
        write(folder/'OBSERVATIONS.json',dict(passed=True,pass1=p1,pass2=p2,replay_identical=True))
        write(folder/'ADMISSION.json',dict(status='T_CANDIDATE_ADMITTED',tier_e='NOT_QUALIFIED',
              authoritative_synthetic_source=True,source_bound_frc=True,frozen_preconstruction_acceptance=True,
              semantic_validation=True,behavioral_acceptance=True,deterministic_replay=True,
              stable_identities=True,no_known_evaluation_solution_leakage=True,no_unresolved_contradiction=True,
              authorized_research_preparation=True,actual_training_authorized=False,
              provenance='deterministic_expert_demonstration',independent_authorship_or_review=False))
        # Same information for both objectives, with mechanical serialization instructions.
        context = dict(requirement=source['requirement'],before_state=before,
            instruction='Select one native value step: add/le/eq, two direct refs or available literals, exact sorted deps. '
                        'A returns the complete sealed package; B returns the selected step. Mechanical HostEntry calls task with typed defaults and returns Int64 zero.')
        messages = [dict(role='user',content=c.canonical(context).decode())]
        write(folder/'CONTEXT.json',dict(messages=messages,required_context='requirement, full immutable typed scope, literals, schema/skill, foundation and mechanical HostEntry rules'))
        shared = dict(requirement=dict(episode=eid,source=artifact(folder/'SOURCE.json'),frc=artifact(folder/'FRC.json'),
                    family=source['family'],component=source['component']),
            profile=dict(name='r6.63-one-value-step',contract=artifact(OUT/'SKILL-1.md'),
                         foundation=artifact(ROOT/'experiments/semantic_interpreter/interpreter.py')),
            evidence=dict(status='QUALIFIED',target_source=artifact(folder/'ACTION.json'),validation=artifact(folder/'VALIDATION.json'),
                    acceptance=artifact(folder/'ACCEPTANCE.json'),observations=artifact(folder/'OBSERVATIONS.json'),admission=artifact(folder/'ADMISSION.json')),
            provenance=dict(class_='deterministic_expert_demonstration',trace=None,limitations=[
                'Same coordinator source/FRC/oracle/expert; capability-aware synthetic development data.',
                'No observed AI semantic tool trajectory, invented reasoning, independent human review or Tier E qualification.',
                'Finite acceptance and description-only future evaluation reservation.']),
            partition=dict(split='training_development',export='training_allowed',ledger=artifact(OUT/'PARTITIONS.json')))
        shared['provenance']['class'] = shared['provenance'].pop('class_')
        b = dict(shared,version='lykoi-supervision-B-1',context=dict(messages=messages,state=artifact(folder/'BEFORE.json'),interface=artifact(OUT/'step-1.schema.json')),
            target=dict(format='bounded_structured_update',text=c.canonical(action).decode(),schema=artifact(OUT/'step-1.schema.json'),ordinal=len(before['steps']),after=artifact(folder/'AFTER.json')))
        a = dict(shared,version='lykoi-supervision-A-1',context=dict(messages=messages,state=None,
            interface=artifact(ROOT/'experiments/typed_composition_r6_18/typed-composition-1.schema.json')),
            target=dict(format='complete_symbolic_package',text=c.canonical(after['package']).decode(),
            schema=artifact(ROOT/'experiments/typed_composition_r6_18/typed-composition-1.schema.json')))
        write(folder/'B-RECORD.json',b)
        write(folder/'A-RECORD.json',a)
        summaries.append(dict(episode=eid,family=source['family'],operation=op,result_type=action['type'],
            distinct_direct_refs=len(action['deps']),prior_steps=len(before['steps']),
            cases=len(fixtures),behavioral_observations=2*len(fixtures),before=artifact(folder/'BEFORE.json'),
            after=artifact(folder/'AFTER.json'),B=artifact(folder/'B-RECORD.json'),A=artifact(folder/'A-RECORD.json')))
    write(OUT/'DEMONSTRATIONS.json',dict(provenance='deterministic_expert_demonstration',verified=len(summaries),entries=summaries,
          actual_ai_selected_semantic_trajectories=0,reasoning_traces=0))
    print('PASS ten expert demonstrations, two identical assembly/behavior passes')


def controls():
    frozen_check()
    rows = []
    def control(label,eid,mutate,code):
        folder = OUT/'episodes'/eid
        before,action = read(folder/'BEFORE.json'),read(folder/'ACTION.json')
        before_pin = pin(before)
        mutate(before,action)
        mutated_pin = pin(before)
        try:
            apply(before,action)
        except c.Diagnostic as exc:
            assert exc.data['code'] == code, (label,exc.data)
            assert pin(before) == mutated_pin
            rows.append(dict(label=label,passed=True,diagnostic=exc.data,before_original_pin=before_pin,
                             input_mutated_pin=mutated_pin,rejected_state_unchanged=True,after_state=None))
        else:
            raise AssertionError(label+' accepted')
    control('Bool plus Int64','D01',lambda b,a:a['node']['expr']['add'].__setitem__(0,{'ref':'decoy'}),'TYPE')
    control('Boolean le forbidden','D09',lambda b,a:a['node'].__setitem__('expr',{'le':[{'ref':'first'},{'ref':'second'}]}),'TYPE')
    control('Mixed equality forbidden','D09',lambda b,a:a['node']['expr']['eq'].__setitem__(1,{'ref':'decoy'}),'TYPE')
    control('Wrong declared result','D01',lambda b,a:a.__setitem__('type','Bool'),'TYPE')
    control('Missing direct dependency','D01',lambda b,a:a.__setitem__('deps',['arrivals']),'DEPENDENCY')
    control('Unused extra dependency','D05',lambda b,a:a.__setitem__('deps',['cap','load']),'DEPENDENCY')
    control('Duplicate dependency','D03',lambda b,a:a.__setitem__('deps',['batch','batch']),'DEPENDENCY')
    control('Unknown operand','D01',lambda b,a:a['node']['expr']['add'].__setitem__(0,{'ref':'absent'}),'UNKNOWN_REFERENCE')
    control('Forward self-reference','D01',lambda b,a:a['node']['expr']['add'].__setitem__(0,{'ref':'selected'}),'UNKNOWN_REFERENCE')
    control('New operation forbidden','D01',lambda b,a:a['node'].__setitem__('expr',{'mul':[{'ref':'arrivals'},{'ref':'reserve'}]}),'UNSUPPORTED')
    control('Unlisted literal','D02',lambda b,a:a['node']['expr']['add'].__setitem__(0,{'const':2}),'LITERAL')
    control('Tampered state identity','D01',lambda b,a:b['params'][0].__setitem__('type','Bool'),'IDENTITY')
    # Wrong but well-typed semantic choices must fail the independent frozen acceptance.
    for label,eid,mutate in [
       ('Wrong eq instead of le','D05',lambda a:a['node'].__setitem__('expr',{'eq':[{'ref':'load'},{'const':5}]})),
       ('Reversed ordered comparison','D07',lambda a:a['node']['expr']['le'].reverse()),
       ('Original base instead of subtotal','D04',lambda a:(a['node']['expr']['add'].__setitem__(0,{'ref':'base'}),a.__setitem__('deps',['adjustment','base']))),
       ('Distractor instead of count','D02',lambda a:(a['node']['expr']['add'].__setitem__(1,{'ref':'bonus'}),a.__setitem__('deps',['bonus']))),
       ('Repeated ref instead of pair','D01',lambda a:(a['node']['expr']['add'].__setitem__(1,{'ref':'arrivals'}),a.__setitem__('deps',['arrivals']))),
       ('Wrong Boolean literal','D10',lambda a:a['node']['expr']['eq'].__setitem__(1,{'const':False}))]:
        folder=OUT/'episodes'/eid
        action=read(folder/'ACTION.json')
        mutate(action)
        after,_=apply(read(folder/'BEFORE.json'),action)
        observed=observation_pass(after,read(folder/'ACCEPTANCE.json')['cases'])
        assert not all(r['passed'] for r in observed)
        rows.append(dict(label=label,passed=True,static_valid=True,behavioral_rejected=True,observations=observed))
    # Commutativity alone cannot enforce explicitly requested operand identity/order.
    folder=OUT/'episodes/D02'
    action=read(folder/'ACTION.json')
    action['node']['expr']['add'].reverse()
    after,_=apply(read(folder/'BEFORE.json'),action)
    observations=observation_pass(after,read(folder/'ACCEPTANCE.json')['cases'])
    assert all(r['passed'] for r in observations)
    assert action != read(folder/'ACTION.json')
    rows.append(dict(label='Commutative order mutation',passed=True,static_valid=True,behavioral_equal=True,
        exact_source_selection_rejected=True,note='Exact binding contract required in addition to finite behavior.'))
    write(OUT/'CONTROLS.json',dict(passed=True,controls=len(rows),entries=rows))
    print('PASS',len(rows),'type/dependency/identity and well-typed semantic mutation controls')


if __name__ == '__main__':
    qualify()
    controls()
