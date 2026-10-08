"""Seal newly selected contracts and independent expected observations."""
from evidence import HERE, OUT, ROOT, now, save, sha

UID = '00000000-0000-4000-8000-000000000001'
TIME = '2026-01-01T00:00:00Z'

DOMAINS = {
    'kiln': dict(title='Kiln firing permits', idle='cold', active='firing',
                 gate='vent', allow='open', block='closed', category='load',
                 normal='ordinary', special='emergency', start='ignite', stop='cool', exception='rescue'),
    'custody': dict(title='Evidence custody seal registry', idle='unsealed', active='sealed',
                 gate='witness', allow='present', block='absent', category='material',
                 normal='routine', special='fragile', start='seal', stop='unseal', exception='protect')}


def record(d, gate=None, category=None, phase=None, label='  Batch A  '):
    return dict(id=UID, created_at=TIME, label=label, phase=phase or d['idle'],
                **{d['gate']: gate or d['allow'], d['category']: category or d['normal']})


def create(d, **kwargs):
    return {k: v for k, v in record(d, **kwargs).items() if k not in ('id', 'created_at', 'phase')}


def step(op, args, expected, unchanged=False):
    return dict(op=op, args=args, expected=expected, unchanged=unchanged)


def ok(r):
    return {'ok': r}


def err(code):
    return {'error': code}


def cases(d):
    r = record(d)
    on = record(d, phase=d['active'])
    blocked = record(d, gate=d['block'])
    special = record(d, gate=d['block'], category=d['special'])
    base = [dict(id='missing-list', steps=[step('list', {}, ok([]), True)]),
        dict(id='blank-create', steps=[step('create', create(d, label=' \t '), err('invalid_label'), True)]),
        dict(id='missing-id', steps=[step(d['start'], {'id': UID}, err('not_found'), True)]),
        dict(id='allowed-sequence', steps=[step('create', create(d), ok(r)), step('list', {}, ok([r]), True),
             step(d['start'], {'id': UID}, ok(on)), step(d['start'], {'id': UID}, err('invalid_transition'), True),
             step('set_gate', {'id': UID, 'value': d['block']}, err('gate_locked'), True),
             step('set_gate', {'id': UID, 'value': d['allow']}, ok(on)), step('list', {}, ok([on]), True)]),
        dict(id='blocked-start', steps=[step('create', create(d, gate=d['block']), ok(blocked)),
             step(d['start'], {'id': UID}, err('gate_required'), True),
             step('set_gate', {'id': UID, 'value': d['allow']}, ok(r)), step(d['start'], {'id': UID}, ok(on))]),
        dict(id='special-no-implicit-exception', steps=[step('create', create(d, gate=d['block'], category=d['special']), ok(special)),
             step(d['start'], {'id': UID}, err('gate_required'), True)]),
        dict(id='invalid-gate', steps=[step('create', create(d), ok(r)),
             step('set_gate', {'id': UID, 'value': 'invalid'}, err('invalid_input'), True)]),
        dict(id='missing-gate', steps=[step('create', create(d), ok(r)),
             step('set_gate', {'id': UID}, err('invalid_input'), True)]),
        dict(id='corrupt-domain', initial=[{**r, 'phase': 'bogus'}], steps=[step('list', {}, err('invalid_state'), True)]),
        dict(id='corrupt-duplicate', initial=[r, r], steps=[step('list', {}, err('invalid_state'), True)]),
        dict(id='corrupt-invariant', initial=[record(d, phase=d['active'], gate=d['block'])], steps=[step('list', {}, err('invalid_state'), True)]),
        dict(id='corrupt-blank', initial=[record(d, label=' ')], steps=[step('list', {}, err('invalid_state'), True)]),
        dict(id='collision', steps=[step('create', create(d), ok(r)), step('create', create(d), err('id_collision'), True)])]
    m1 = [dict(id='new-return-cycle', steps=[step('create', create(d), ok(r)), step(d['stop'], {'id': UID}, err('invalid_transition'), True),
        step(d['start'], {'id': UID}, ok(on)), step(d['stop'], {'id': UID}, ok(r)),
        step('set_gate', {'id': UID, 'value': d['block']}, ok(blocked)),
        step(d['start'], {'id': UID}, err('gate_required'), True), step(d['stop'], {'id': UID}, err('invalid_transition'), True)]),
        dict(id='return-missing', steps=[step(d['stop'], {'id': UID}, err('not_found'), True)])]
    emergency_on = record(d, gate=d['block'], category=d['special'], phase=d['active'])
    m2 = [dict(id='exception-cycle', steps=[step('create', create(d, gate=d['block'], category=d['special']), ok(special)),
        step(d['exception'], {'id': UID}, ok(emergency_on)), step('list', {}, ok([emergency_on]), True),
        step(d['exception'], {'id': UID}, err('invalid_transition'), True),
        step('set_gate', {'id': UID, 'value': d['block']}, err('gate_locked'), True),
        step(d['stop'], {'id': UID}, ok(special)), step(d['start'], {'id': UID}, err('gate_required'), True)]),
        dict(id='exception-normal', steps=[step('create', create(d, gate=d['block']), ok(blocked)),
            step(d['exception'], {'id': UID}, err('exception_denied'), True)]),
        dict(id='exception-allowed-gate', steps=[step('create', create(d, category=d['special']), ok(record(d, category=d['special']))),
            step(d['exception'], {'id': UID}, err('exception_denied'), True)]),
        dict(id='exception-missing', steps=[step(d['exception'], {'id': UID}, err('not_found'), True)]),
        dict(id='corrupt-special-permitted', initial=[emergency_on], steps=[step('list', {}, ok([emergency_on]), True)])]
    return base, m1, m2


def main():
    common = '''# Common formal contract and author interface

Standard-library Python 3.10+. Local records.json persistent JSON list, missing file
is empty. Atomic replacement; rejection preserves exact existing bytes or absence.
Every operation reloads/validates the whole store. Record fields exactly id,
created_at, label, phase and the two domain fields below. id is immutable UUID-v4
provider output; created_at immutable UTC provider output; label nonblank but retain
all characters. Creation supplies label and both enum domain fields, phase is the
declared idle literal. Test inputs conform to these creation types except blank label.
Creation duplicate provider identity fails id_collision. Persisted records must have
valid field types/domains, nonblank label, unique IDs and the behavioral invariant.
Invalid persisted state fails invalid_state, even for list; no repair is authorized.
List whole records by created_at then id. No migrations, concurrency or distributed IO.

Each lookup operation takes id. Missing identity fails not_found before guards.
All guards evaluate original state; ordered error precedence as specified.
set_gate takes value, writes the domain gate verbatim; absent/out-of-domain value
fails invalid_input after its guard. Reject gate_locked if active AND supplied
value equals blocked, even if already blocked. Other changes preserve all fields.
Do not change category or label after creation. All other writes preserve identity,
timestamp, label and category. No implicit default, override or history repair.

A: write application.py exposing handle(op, args, providers) -> {"ok": record/list}
or {"error": code}. providers maps uuid_v4 and utc_clock to callables; no external
dependencies. B/C: write intent.json conforming to intent.schema.json; both use the
same fields/create/operations/invariants grammar. create/list implicit commands,
lookup id implicit, ordered guards, simultaneous exact writes. Nonblank creation
fields are also persisted invariants. All supplied mutation inputs required.
Use typed operands with exact declared domains. No arbitrary Python expressions.
Generators are shared infrastructure; authors cannot edit them. Errors as above.
Return authored path and effort: tool/model availability, repairs, timestamps,
self-tests and unsupported behavior. Do not read acceptance, sealed changes, other
track sources or old scored application implementations. Shared access is cooperative.
300 seconds, <=12 tool calls, <=2 self-test batches <=30s, first candidate plus
one repair. Save first candidate before self-testing; final candidate separate.
'''
    save(OUT / 'SELECTION.json', dict(utc=now(), domains=DOMAINS,
        provenance='coordinator synthetic, implementation-aware, nonrandom; no prior scored implementation reused',
        bias='same record-local FSM skeleton in two domains, favors existing scalar/predicate capability; no independent sourcing'))
    (OUT / 'tasks').mkdir(parents=True, exist_ok=True)
    with (OUT / 'tasks/COMMON.md').open('x', encoding='utf-8', newline='\n') as f:
        f.write(common)
    for name, d in DOMAINS.items():
        text = f'''# {d['title']} — base

Use COMMON.md. phase domain [{d['idle']}, {d['active']}], initially {d['idle']}.
{d['gate']} domain [{d['allow']}, {d['block']}].
{d['category']} domain [{d['normal']}, {d['special']}].
Command {d['start']}: require phase={d['idle']} else invalid_transition, then
{d['gate']}={d['allow']} else gate_required; write phase={d['active']}.
Behavioral invariant: phase={d['active']} implies {d['gate']}={d['allow']}.
set_gate guard and create/list are exactly COMMON.md. No return transition yet.
'''
        with (OUT / f'tasks/{name}.md').open('x', encoding='utf-8', newline='\n') as f:
            f.write(text)
        changes = [f'''# {name} stage 1
Add {d['stop']} by id: missing not_found; require phase={d['active']} else
invalid_transition; write phase={d['idle']}. Preserve every other field and all
base behavior. This allows a cycle but does not bypass the gate requirement.
''', f'''# {name} stage 2
Preserve stage 1 and base commands including ordinary start's gate requirement.
Add {d['exception']} by id: missing not_found; first require phase={d['idle']}
else invalid_transition; then require {d['gate']}={d['block']} AND
{d['category']}={d['special']} else exception_denied. Write phase={d['active']}
without changing the gate. Broaden the persisted invariant: active implies gate
allowed OR (gate blocked AND category special). set_gate blocked while active
must still reject gate_locked. {d['stop']} must work for exception-created states.
No base acceptance expectation is superseded; the corrupt-invariant base record
has category ordinary and remains invalid. New special active/blocked state is valid.
''']
        base, m1, m2 = cases(d)
        save(OUT / f'acceptance/{name}-base.json', base)
        for stage, (text, rows) in enumerate(zip(changes, (m1, m2)), 1):
            (OUT / 'sealed').mkdir(exist_ok=True)
            with (OUT / f'sealed/{name}-s{stage}.md').open('x', encoding='utf-8', newline='\n') as f:
                f.write(text)
            save(OUT / f'sealed/{name}-s{stage}.json', rows)
    paths = [HERE / 'PROTOCOL.md', HERE / 'prepare.py', HERE / 'intent.schema.json',
             OUT / 'SELECTION.json'] + list((OUT / 'tasks').glob('*')) + list((OUT / 'acceptance').glob('*'))
    save(OUT / 'TASK-FREEZE.json', dict(utc=now(), files={p.relative_to(ROOT).as_posix(): sha(p) for p in paths}))
    save(OUT / 'MODIFICATION-SEAL.json', dict(utc=now(), withholding='CONTAMINATED_UNENFORCED',
        files={p.relative_to(ROOT).as_posix(): sha(p) for p in (OUT / 'sealed').glob('*')}))
    print('Two contracts, base cases and two cumulative modifications each frozen')


if __name__ == '__main__':
    main()
