"""Post-score diagnostic controls; never repair submitted programs."""
import copy
import json
from evidence import HERE, OUT, ROOT, load, now, save, sha
from generate import generate, lower
from schema_check import check
from air_compiler.mutable_values import compose
from air_compiler.parser import parse
from air_compiler.validator import validate
from air_compiler.semantics import impact


def attempt(f):
    try:
        f()
        return dict(accepted=True)
    except Exception as e:
        return dict(accepted=False, exception=type(e).__name__, diagnostic=str(e))


def main():
    intent = load(OUT / 'submissions/C/kiln/s2/intent.json')
    controls = []
    # Predicate declaration corruption, not a runtime guard-value change.
    x = copy.deepcopy(intent)
    operand = x['operations']['ignite']['guards'][0]['condition']['left']
    operand.update(type='string', domain=[])
    controls.append(('operand-type-mismatch', x, 'B ignores redundant tags; runtime behavior unchanged; C additional static check'))
    x = copy.deepcopy(intent)
    x['operations']['ignite']['guards'][0]['condition']['left']['value'] = 'unknown_field'
    controls.append(('unbound-field', x, 'B generation accepts, runtime predicate yields false; C refuses before execution'))
    x = copy.deepcopy(intent)
    x['operations']['ignite']['writes']['phase']['value'] = 'bogus'
    controls.append(('out-of-domain-write', x, 'B ordinary runtime type/invariant checks reject before commit; C also refuses before execution'))
    x = copy.deepcopy(intent)
    x['operations']['ignite']['writes']['phase']['value'] = 'cold'
    controls.append(('well-typed-wrong-transition', x, 'Both generation pipelines accept; tests needed to detect wrong target; no proof of intent correctness'))
    rows = []
    for name, x, meaning in controls:
        save(OUT / f'controls/{name}.json', x)
        rows.append(dict(control=name, interpretation=meaning, schema=attempt(lambda: check(x)),
            B=attempt(lambda: generate(x, 'B')), C=attempt(lambda: generate(x, 'C')),
            A='ordinary Python compilation lacks declarative semantic checks; existing acceptance required'))
    ir = lower(intent)
    unauthorized = copy.deepcopy(ir['base'])
    create = next(b for b in unauthorized['behaviors'] if b['kind'] == 'create')
    create['requires'].remove('write')
    save(OUT / 'controls/unauthorized-base-write.json', unauthorized)
    rows.append(dict(control='unauthorized-base-write', schema='outside common intent; no tunable capabilities in B',
        C=attempt(lambda: validate(parse(json.dumps(unauthorized)))),
        B='generator grants no author-controlled capability declarations; fixed local writes',
        A='no comparable capability algebra', attribution='C internal capability consistency, not a scored common-interface advantage'))
    bad = copy.deepcopy(ir['facts'])
    bad['mutations'][0]['effect']['rejection'] = 'changed'
    save(OUT / 'controls/invalid-effect.json', bad)
    rows.append(dict(control='invalid-effect-contract', C=attempt(lambda: compose(ir['base'], bad)),
        B='rejection unchanged is fixed by generator, not author-tunable',
        attribution='production composition guarantee; not uniquely achieved observable behavior'))
    traversal = impact(parse(json.dumps(ir['base'])), 'field:phase')
    save(OUT / 'IMPACT.json', dict(utc=now(), tool='air_compiler.semantics.impact', actual=traversal,
        scope='legacy scalar base only; mutable operations and extension invariant predicates not indexed',
        missing_semantic_users=['ignite', 'cool', 'rescue', 'set_gate', 'predicate_semantics.invariants'],
        B_equivalent='ordinary static reference traversal could enumerate shared intent users; not measured as AI effort',
        warning='Do not interpret returned traversal as complete change impact'))
    runtime = []
    for track in ('A', 'B', 'C'):
        for domain in ('kiln', 'custody'):
            for stage in range(3):
                r = load(OUT / f'results/{track}-{domain}-{stage}.json')
                selected = [o for o in r['observations'] if o['case'].startswith('corrupt-')
                            or o['expected'].get('error') in ('invalid_transition', 'gate_locked', 'exception_denied', 'gate_required')]
                runtime.append(dict(track=track, domain=domain, stage=stage,
                    observed_guards_invariants=sum(o['pass_result'] for o in selected), total=len(selected),
                    rejected_bytes_preserved=all(o.get('rejection_bytes_unchanged') is True for o in selected if o['expected'].get('error'))))
    save(OUT / 'SEMANTIC-EVIDENCE.json', dict(utc=now(), seeded_controls=rows, runtime=runtime,
        actual_author_defects_detected=[dict(scope='C/kiln/base', cause='input creation value must be null', repair=1),
                                       dict(scope='C/custody/base', cause='input creation value must be null', repair=1)],
        scored_behavioral_defects_uniquely_prevented_by_C=0,
        additional_static_guarantees='typed operand binding, exact literal domains, internal authority/effect consistency',
        requirement_equivalence_proved=False,
        unavailable_required_semantics=[],
        limitations=['guards/invariants are runtime checks, not static proof',
                     'transitions represented as guarded enum writes, not production state-machine declarations',
                     'no full FRC approval/normal-contract guarantees', 'legacy impact is incomplete for extension facts']))
    print('Semantic evidence recorded:', len(rows), 'controls; no scored repairs')


if __name__ == '__main__':
    main()
