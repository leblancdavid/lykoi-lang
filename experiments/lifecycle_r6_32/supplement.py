"""Additional predeclared controls and same-store in-place installation witness."""
import copy
import json
import sys
from baseline import OUT, save, sha
from lifecycle import Journal, Registry, c, digest, publish
from qualify import simple, run_request, ID, NOW
from edit import revise, install
from generate import generate
import fixture


def main():
    base = OUT / (sys.argv[1] if len(sys.argv) > 1 else 'supplement-1')
    base.mkdir()
    journal = Journal(base / 'telemetry')
    save(base / 'FREEZE.json', dict(inputs={p.name: sha(p) for p in __import__('pathlib').Path(__file__).parent.glob('*.py')},
        expected_controls=['stale_application', 'partial_application_migration', 'invalid_application_migration',
                           'unauthorized_application_edit', 'stale_installation', 'registry_tamper', 'telemetry_tamper'],
        expected_sequence=['gate_required', 'success:firing', 'success:closed', 'invalid_transition', 'list:one_record'],
        negative_candidate='modified rule with original ignite gate must fail the emergency/closed ignition case',
        model_calls=0))
    original, modified = fixture.copies()
    controls = []

    def rejected(name, code, operation):
        try:
            operation()
        except c.Diagnostic as exc:
            row = dict(name=name, expected=code, diagnostic=exc.data, passed=exc.data['code'] == code)
        else:
            row = dict(name=name, expected=code, passed=False)
        controls.append(row)
        journal.record('validation_control', row)
        assert row['passed'], row

    selected = ['ignite', 'set_gate', 'invariant:0']
    rejected('stale_application', 'STALE_APPLICATION', lambda: revise(original, modified, 'f' * 64, selected, []))
    rejected('partial_application_migration', 'PARTIAL_MIGRATION', lambda: revise(original, modified, digest(original), ['ignite'], []))
    rejected('invalid_application_migration', 'INVALID_MIGRATION', lambda: revise(original, modified, digest(original), ['ignite'], ['set_gate', 'invariant:0']))
    unauthorized = copy.deepcopy(modified)
    unauthorized['create']['nonblank'] = []
    rejected('unauthorized_application_edit', 'UNAUTHORIZED_MUTATION', lambda: revise(original, unauthorized, digest(original), selected, []))
    revision = revise(original, modified, digest(original), selected, [])
    save(base / 'REVISION.json', {k: v for k, v in revision.items() if k != 'source'})
    workspace = base / 'live'
    workspace.mkdir()
    target = workspace / 'application.py'
    source, _ = generate(original, 'C')
    with target.open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(source)
    original_source = sha(target)
    record = dict(id=ID, created_at=NOW, label='Control', phase='cold', vent='closed', load='emergency')
    save(workspace / 'records.json', [record])
    rows = []
    row = run_request(target, workspace, dict(op='ignite', args={'id': ID}, providers={}), journal, 'before')
    assert row['observation'] == {'error': 'gate_required'}
    rows.append(row)
    rejected('stale_installation', 'STALE_APPLICATION', lambda: install(revision, target, 'f' * 64, journal))
    state_pin = sha(workspace / 'records.json')
    install(revision, target, original_source, journal)
    assert sha(workspace / 'records.json') == state_pin
    assert sha(target) == revision['source_sha256']
    assert sha(workspace / (original_source + '.predecessor')) == original_source
    for op, args in [('ignite', {'id': ID}), ('set_gate', {'id': ID, 'value': 'closed'}),
                     ('ignite', {'id': ID}), ('list', {})]:
        row = run_request(target, workspace, dict(op=op, args=args, providers={}), journal, 'after-' + op)
        expected = {'error': 'invalid_transition'} if op == 'ignite' and len(rows) == 3 else (
            {'ok': [dict(record, phase='firing')]} if op == 'list' else {'ok': dict(record, phase='firing')})
        assert row['observation'] == expected, (row, expected)
        row['expected'] = expected
        rows.append(row)
    # Oracle sensitivity: a well-typed incomplete behavioral edit compiles but fails
    # the intended changed behavior. Preserve it rather than "repairing" it.
    wrong = copy.deepcopy(modified)
    wrong['operations']['ignite']['guards'][1] = original['operations']['ignite']['guards'][1]
    source, ir = generate(wrong, 'C')
    save(base / 'wrong.intent.json', wrong)
    wrong_target = workspace / 'wrong.py'
    with wrong_target.open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(source)
    wrong_workspace = base / 'negative-control'
    wrong_workspace.mkdir()
    save(wrong_workspace / 'records.json', [record])
    wrong_row = run_request(wrong_target, wrong_workspace, dict(op='ignite', args={'id': ID}, providers={}), journal, 'wrong')
    assert wrong_row['observation'] == {'error': 'gate_required'}
    # Committed registry/telemetry corruption must reject rather than silently skip.
    registry = Registry(base / 'corrupt-registry')
    d = simple('Integrity')
    registry.admit([d], None)
    committed = json.loads((registry.path / '000001.json').read_text())
    committed['state']['definitions'][d['identity']]['result'] = {'const': 99}
    corrupt_registry = Registry(base / 'corrupt-registry-copy')
    publish(corrupt_registry.path / '000001.json', committed)
    rejected('registry_tamper', 'REGISTRY_INTEGRITY', corrupt_registry.read)
    telemetry = Journal(base / 'corrupt-telemetry')
    event = dict(journal.recover()['events'][0])
    event['data'] = {'tampered': True}
    publish(telemetry.path / '000001.json', event)
    rejected('telemetry_tamper', 'TELEMETRY_INTEGRITY', telemetry.recover)
    save(base / 'RESULT.json', dict(controls=controls, observations=rows, same_store=True,
        same_installed_path=True, persisted_state_unchanged_by_install=True,
        predecessor_preserved=True, negative_control=wrong_row, well_typed_wrong_behavior_detected=True,
        model_calls=0, classification='R6_32_LIFECYCLE_PARTIAL'))
    print('Supplement: seven rejection controls; five live before/after observations; negative scorer control passes')


if __name__ == '__main__':
    main()
