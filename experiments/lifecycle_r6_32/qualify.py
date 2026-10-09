"""AI-free qualification; each invocation writes a new immutable attempt directory."""
import copy
import hashlib
import itertools
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import traceback

from baseline import OUT, ROOT, save, sha
from lifecycle import Journal, Registry, c, digest, publish
import fixture

sys.path.insert(0, str(ROOT / 'experiments/value_added_r6_16'))
from generate import generate, lower
from air_compiler.parser import parse
from air_compiler.semantics import impact, diff
from examples import definition, step, ref, const, call

ID = '00000000-0000-4000-8000-000000000001'
NOW = '2026-01-01T00:00:00Z'


def simple(name, delta=1):
    return definition(name, [('x', 'Int64')], {}, [step('sum', 'Int64', ['x'],
        dict(op='value', expr={'add': [ref('x'), const(delta)]}))], ref('sum'))


def caller(name, target):
    return definition(name, [('x', 'Int64')], {target['name']: target['identity']},
        [step('use', 'Int64', ['x'], call(target, {'x': ref('x')}))], ref('use'))


def registry_qualification(attempt, journal):
    registry = Registry(attempt / 'registry', journal)
    rows = []

    def rejection(name, expected, f, proposal=None):
        start = time.perf_counter()
        try:
            f()
        except c.Diagnostic as exc:
            actual = exc.data['code']
            row = dict(control=name, expected=expected, actual=actual, diagnostic=exc.data,
                       proposal=proposal, passed=actual == expected, tool_seconds=time.perf_counter() - start)
        else:
            row = dict(control=name, expected=expected, actual='ACCEPTED', passed=False, proposal=proposal)
        rows.append(row)
        journal.record('validation_control', row)
        assert row['passed'], row

    with journal.stage('registry', {'implementation': sha(Path(__file__).with_name('lifecycle.py'))}):
        old = simple('Increment')
        a, b = caller('CallerA', old), caller('CallerB', old)
        token = registry.admit([old, a, b], None)['token']
        original_snapshot = copy.deepcopy(registry.read())
        new = simple('Increment', 2)
        token = registry.admit([new], token, old['identity'])['token']
        updated = caller('CallerA', new)
        token = registry.admit([updated], token, a['identity'])['token']
        dependents = registry.dependents(old['identity'])
        assert dependents['direct'] == sorted([a['identity'], b['identity']])
        rejection('partial-caller-migration', 'PARTIAL_MIGRATION', lambda: registry.migrate(
            old['identity'], new['identity'], {a['identity']: updated['identity']}, token))
        rejection('invalid-caller-successor', 'INVALID_MIGRATION', lambda: registry.migrate(
            old['identity'], new['identity'], {a['identity']: new['identity'], b['identity']: None}, token))
        token = registry.migrate(old['identity'], new['identity'],
                                 {a['identity']: updated['identity'], b['identity']: None}, token)
        assert registry.retrieve(pin=old['identity']) == [old]
        assert registry.retrieve(pin=b['identity']) == sorted([old, b], key=lambda d: d['identity'])
        assert registry.retrieve(pin=updated['identity']) == sorted([new, updated], key=lambda d: d['identity'])
        search = registry.retrieve(name='Increment', signature=[old['params'], 'Int64'])
        assert [d['identity'] for d in search] == sorted([old['identity'], new['identity']])
        assert Registry(attempt / 'registry').retrieve(name='Increment') == search
        rejection('ambiguous-unpinned-reference', 'AMBIGUOUS_REFERENCE', lambda: registry.resolve('Increment'))
        rejection('duplicate-identity', 'DUPLICATE_IDENTITY', lambda: registry.admit([old], token), old)
        tampered = copy.deepcopy(old)
        tampered['result'] = const(99)
        # Use a fresh registry so duplicate precedence does not mask content tampering.
        empty = Registry(attempt / 'tamper-registry', journal)
        rejection('identity-tampering', 'IDENTITY', lambda: empty.admit([tampered], None), tampered)
        missing = caller('MissingCaller', simple('Absent'))
        rejection('missing-dependency', 'MISSING_DEPENDENCY', lambda: registry.admit([missing], token), missing)
        cyclic_a, cyclic_b = caller('CycleA', simple('CycleB')), caller('CycleB', simple('CycleA'))
        cyclic_a['identity'], cyclic_b['identity'] = 'a' * 64, 'b' * 64
        cyclic_a['dependencies']['CycleB'] = cyclic_b['identity']
        cyclic_a['steps'][0]['node']['identity'] = cyclic_b['identity']
        cyclic_b['dependencies']['CycleA'] = cyclic_a['identity']
        cyclic_b['steps'][0]['node']['identity'] = cyclic_a['identity']
        rejection('dependency-cycle', 'CYCLE', lambda: registry.admit([cyclic_a, cyclic_b], token), [cyclic_a, cyclic_b])
        invalid = simple('Other', 3)
        rejection('invalid-successor-reference', 'INVALID_SUCCESSOR', lambda: registry.admit(
            [invalid], token, 'f' * 64), invalid)
        changed_type = definition('Increment', [('x', 'Bool')], {},
                                  [step('same', 'Bool', ['x'], dict(op='value', expr=ref('x')))], ref('same'), 'Bool')
        rejection('invalid-type-change', 'TYPE_CHANGE', lambda: registry.admit(
            [changed_type], token, old['identity']), changed_type)
        malformed = copy.deepcopy(invalid)
        malformed['extra'] = 1
        rejection('invalid-schema', 'SHAPE', lambda: registry.admit([malformed], token), malformed)
        incompatible = copy.deepcopy(invalid)
        incompatible['steps'][0]['type'] = 'Bool'
        incompatible = c.seal(incompatible)
        rejection('incompatible-step-type', 'TYPE', lambda: registry.admit([incompatible], token), incompatible)
        unsupported = copy.deepcopy(invalid)
        unsupported['steps'][0]['node'] = dict(op='host_callback')
        unsupported = c.seal(unsupported)
        rejection('new-meaning', 'UNSUPPORTED', lambda: registry.admit([unsupported], token), unsupported)
        rejection('expansion-exhaustion', 'EXPANSION_LIMIT', lambda: registry.admit([invalid], token, budget=1), invalid)
        mutated = copy.deepcopy(registry.read()['state'])
        mutated['definitions'][old['identity']]['result'] = const(99)
        rejection('unauthorized-mutation', 'UNAUTHORIZED_MUTATION', lambda: registry.commit(mutated, token, 'tamper'))
        rejection('stale-registry-read', 'STALE_READ', lambda: registry.retrieve(pin=old['identity'],
            expected=original_snapshot['token']))
        rejection('stale-registry-write', 'STALE_READ', lambda: registry.admit([invalid], original_snapshot['token']))
        mixed = definition('Mixed', [('x', 'Int64')], {'CallerA': updated['identity'], 'CallerB': b['identity']},
            [step('a', 'Int64', ['x'], call(updated, {'x': ref('x')})),
             step('b', 'Int64', ['x'], call(b, {'x': ref('x')}))], ref('a'))
        rejection('mixed-version-closure', 'AMBIGUOUS_REFERENCE', lambda: registry.admit([mixed], token), mixed)
        # Typed expression cycle (no cryptographic fixed-point assumption).
        local_cycle = definition('LocalCycle', [], {}, [step('a', 'Int64', ['b'], dict(op='value', expr=ref('b'))),
            step('b', 'Int64', ['a'], dict(op='value', expr=ref('a')))], ref('a'))
        rejection('local-value-cycle', 'CYCLE', lambda: registry.admit([local_cycle], token), local_cycle)
        # Exact functional execution of selected and retained callers, same old pin.
        executions = []
        for target, delta in [(a, 1), (updated, 2), (b, 1)]:
            program = definition('Run', [], {target['name']: target['identity']},
                [step('n', 'Int64', [], dict(op='atom', codec='uint8')),
                 step('out', 'Int64', ['n'], call(target, {'x': ref('n')})),
                 step('end', 'Unit', [], dict(op='end'))], ref('out'))
            package = dict(version=c.VERSION, foundation=c.FOUNDATION,
                definitions=registry.retrieve(pin=target['identity']), program=program)
            expanded = c.expand(package)
            for n in (0, 1, 253, 255):
                observed = c.vm.execute(expanded['plan'], bytes([n]))
                assert observed['status'] == 'success', observed
                assert observed['value'] == n + delta, observed
                observed = dict(observed, output_hex=observed['output'].hex())
                del observed['output']
                executions.append(dict(caller=target['identity'], input=n, expected=n + delta, observation=observed))
        result = dict(accepted_definitions=len(registry.read()['state']['definitions']),
            controls=rows, dependents=dependents, retrieval=search, token=token,
            predecessor_preserved=True, unaffected_caller_preserved=True, executions=executions,
            migrations=registry.read()['state']['migrations'])
        save(attempt / 'REGISTRY.json', result)
    return result


def run_request(application, workspace, request, journal, stage):
    store = workspace / 'records.json'
    before = store.read_bytes() if store.exists() else None
    start = time.perf_counter()
    child = subprocess.run([sys.executable, '-B', str(ROOT / 'experiments/value_added_r6_16/transport.py'),
                            str(application)], cwd=workspace, input=json.dumps(request),
                           text=True, capture_output=True, timeout=30)
    duration = time.perf_counter() - start
    after = store.read_bytes() if store.exists() else None
    row = dict(request=request, returncode=child.returncode, stderr=child.stderr,
        observation=json.loads(child.stdout) if child.returncode == 0 else None,
        before_sha256=hashlib.sha256(before).hexdigest() if before is not None else None,
        after_sha256=hashlib.sha256(after).hexdigest() if after is not None else None,
        rejection_bytes_unchanged=before == after, tool_seconds=duration)
    journal.record('functional_observation', dict(stage=stage, application_sha256=sha(application), **row))
    assert child.returncode == 0, row
    if 'error' in row['observation']:
        assert row['rejection_bytes_unchanged'], row
    return row


def stateful_qualification(attempt, journal):
    original, modified = fixture.copies()
    save(attempt / 'fixture/original.intent.json', original)
    save(attempt / 'fixture/modified.intent.json', modified)
    assert (attempt / 'fixture/original.intent.json').exists()
    models = []
    functional = []
    with journal.stage('stateful', dict(original=digest(original), modified=digest(modified),
                                       source_sha256=sha(fixture.SOURCE))):
        for changed, intent in [(False, original), (True, modified)]:
            label = 'modified' if changed else 'original'
            start = time.perf_counter()
            source, ir = generate(intent, 'C')
            again, again_ir = generate(copy.deepcopy(intent), 'C')
            assert source == again and ir == again_ir
            journal.record('generation', dict(stage='stateful', input=digest(intent),
                source_sha256=hashlib.sha256(source.encode()).hexdigest(), ir=digest(ir),
                deterministic=True, tool_seconds=time.perf_counter() - start))
            application = attempt / 'fixture' / (label + '.py')
            with application.open('x', encoding='utf-8', newline='\n') as stream:
                stream.write(source)
            save(attempt / 'fixture' / (label + '.ir.json'), ir)
            models.append(ir)
            for repeat in range(2):
                for phase, vent, load in itertools.product(('cold', 'firing'), ('open', 'closed'), ('ordinary', 'emergency')):
                    record = dict(id=ID, created_at=NOW, label='Control', phase=phase, vent=vent, load=load)
                    for op, value in [('ignite', None), ('set_gate', 'open'), ('set_gate', 'closed'), ('list', None)]:
                        key = f'{label}-{repeat}-{phase}-{vent}-{load}-{op}-{value}'
                        workspace = attempt / 'workspaces' / key
                        workspace.mkdir(parents=True)
                        save(workspace / 'records.json', [record])
                        request = dict(op=op, args={'id': ID}, providers={})
                        if value is not None:
                            request['args']['value'] = value
                        row = run_request(application, workspace, request, journal, key)
                        row.update(case=key, expected=fixture.expected(op, record, changed, value))
                        row['passed'] = row['observation'] == row['expected']
                        functional.append(row)
                        assert row['passed'], row
                        if 'ok' in row['observation'] and op != 'list':
                            actual_record = row['observation']['ok']
                            assert fixture.valid_record(actual_record['phase'], actual_record['vent'], actual_record['load'], changed)
                # Fresh create, ignition, gate change and reload sequence, plus invalid input.
                workspace = attempt / 'workspaces' / f'{label}-{repeat}-sequence'
                workspace.mkdir(parents=True)
                for sequence_index, (op, args, expected) in enumerate([
                    ('create', dict(label='Control', vent='open', load='ordinary'),
                     {'ok': dict(id=ID, created_at=NOW, label='Control', phase='cold', vent='open', load='ordinary')}),
                    ('ignite', dict(id=ID), {'ok': dict(id=ID, created_at=NOW, label='Control', phase='firing', vent='open', load='ordinary')}),
                    ('set_gate', dict(id=ID, value='closed'), {'error': 'gate_locked'}),
                    ('list', {}, {'ok': [dict(id=ID, created_at=NOW, label='Control', phase='firing', vent='open', load='ordinary')]}),
                    ('create', dict(label=' ', vent='open', load='ordinary'), {'error': 'invalid_label'})]):
                    row = run_request(application, workspace, dict(op=op, args=args,
                        providers=dict(uuid_v4=ID, utc_clock=NOW)), journal, f'{label}-{repeat}-sequence-{sequence_index}-{op}')
                    row.update(case=f'{label}-{repeat}-sequence-{sequence_index}-{op}', expected=expected,
                               passed=row['observation'] == expected)
                    functional.append(row)
                    assert row['passed'], row
        before, after = (parse(json.dumps(ir['base'])) for ir in models)
        native = impact(before, 'field:vent')
        changes = diff(before, after)
        extension_probes = []
        for identifier in sorted(fixture.REQUIRED):
            try:
                observation = impact(after, identifier)
            except Exception as exc:
                observation = dict(exception=type(exc).__name__, diagnostic=str(exc))
            extension_probes.append(dict(identifier=identifier, observation=observation))
        # Native IDs have no counterparts for extension predicates/mutations. Map only
        # actual behavior IDs; preserve all other native hits as unmapped, never omit.
        mapping = {b['id']: 'behavior:' + next(cmd['token'] for cmd in models[0]['base']['commands']
                    if cmd['behavior'] == b['id']) for b in models[0]['base']['behaviors']}
        actual = {mapping.get(hit['id'], 'native:' + hit['id']) for hit in native['impacts']}
        impact_result = dict(expected_affected=sorted(fixture.REQUIRED),
            expected_unaffected=sorted(fixture.UNAFFECTED), native=native, scalar_diff=changes,
            extension_probes=extension_probes, mapping=mapping, actual_mapped=sorted(actual),
            false_negatives=sorted(fixture.REQUIRED - actual), false_positives=sorted(actual - fixture.REQUIRED),
            true_positives=sorted(actual & fixture.REQUIRED),
            scope='Legacy scalar impact; changed extension facts are not indexed; coarse vent-field seed over-approximates unchanged create/list')
        save(attempt / 'IMPACT.json', impact_result)
        deps_before, deps_after = fixture.dependencies(original), fixture.dependencies(modified)
        save(attempt / 'DEPENDENCIES.json', dict(before=deps_before, after=deps_after,
            supersedes=deps_before['identity'], explicit_selected_consumers=sorted(deps_after['consumers']),
            unchanged_operations=['create', 'list'], adapter_logic='only declarative guard/invariant copy edits'))
        by_case = {}
        for row in functional:
            parts = row['case'].split('-')
            parts[1] = 'repeat'
            key = '-'.join(parts)
            comparable = {k: v for k, v in row.items() if k not in ('case', 'tool_seconds')}
            if key in by_case:
                assert by_case[key] == comparable, key
            else:
                by_case[key] = comparable
        result = dict(total=len(functional), passed=sum(r['passed'] for r in functional),
            repeats=2, observations=functional, deterministic_replay=True,
            source_sha256=sha(fixture.SOURCE), genuine_existing_operations_changed=['ignite', 'set_gate'],
            invariants_preserved=True, original_unmodified=True)
        save(attempt / 'FUNCTIONAL.json', result)
    return result, impact_result


def recovery_qualification(attempt, journal):
    with journal.stage('recovery', {'journal_implementation': sha(Path(__file__).with_name('lifecycle.py'))}):
        registry_path = attempt / 'crash-registry'
        registry = Registry(registry_path)
        old = simple('Survivor')
        token = registry.admit([old], None)['token']
        candidate = simple('Interrupted')
        save(attempt / 'crash-proposal.json', candidate)
        crash_journal = Journal(attempt / 'crash-journal')
        crash_journal.record('start', dict(stage='completed-authoring', inputs={'proposal': candidate['identity']}))
        crash_journal.record('complete', dict(stage='completed-authoring', artifact=candidate['identity'],
            tool_seconds=None, wall_seconds=None, missing_reason='stub stage; no authoring/tool interval was measured'))
        crash_journal.record('start', dict(stage='publish', inputs={'proposal': candidate['identity'], 'token': token}))
        # A real child exits abruptly after fsyncing partial telemetry and registry
        # staging bytes. Prior completed authoring is recovered, never repeated.
        command = [sys.executable, '-B', str(Path(__file__).resolve()), 'crash', str(attempt)]
        start = time.perf_counter()
        child = subprocess.run(command, capture_output=True, text=True, timeout=30)
        duration = time.perf_counter() - start
        assert child.returncode == 73, child
        recovered_registry = Registry(registry_path).read()
        recovered_journal = Journal(attempt / 'crash-journal').recover()
        assert recovered_registry['token'] == token and recovered_registry['pending']
        assert recovered_journal['completed'] == ['completed-authoring']
        assert recovered_journal['incomplete'] == ['publish'] and recovered_journal['pending']
        assert registry.retrieve(pin=old['identity']) == [old]
        try:
            registry.admit([candidate], token)
        except c.Diagnostic as exc:
            assert exc.data['code'] == 'INCOMPLETE_WRITE'
        else:
            raise AssertionError('incomplete write unexpectedly accepted')
        # Recovery is an explicit branch from complete records; retain failed bytes.
        branch = attempt / 'recovered-registry'
        branch.mkdir()
        for path in sorted(registry_path.glob('*.json')):
            with (branch / path.name).open('xb') as stream:
                stream.write(path.read_bytes())
        recovered = Registry(branch)
        completed = recovered.admit([candidate], token)
        assert recovered.retrieve(pin=candidate['identity']) == [candidate]
        # Incomplete telemetry is read-only until explicitly branching.
        try:
            crash_journal.record('complete', dict(stage='publish'))
        except c.Diagnostic as exc:
            assert exc.data['code'] == 'INCOMPLETE_WRITE'
        else:
            raise AssertionError('telemetry incomplete write unexpectedly accepted')
        branch_journal = Journal(attempt / 'recovered-journal')
        for path in sorted((attempt / 'crash-journal').glob('*.json')):
            with (branch_journal.path / path.name).open('xb') as stream:
                stream.write(path.read_bytes())
        branch_journal.record('interruption', dict(stage='publish', returncode=73,
            wall_seconds=None, tool_seconds=duration, missing_reason='child exited before stage completion',
            pending_sha256={p.name: sha(p) for p in (attempt / 'crash-journal').glob('*.pending')}))
        branch_journal.record('complete', dict(stage='publish', recovered=True,
            artifact=completed['token'], authoring_repeated=False, wall_seconds=None,
            missing_reason='original interrupted stage elapsed time unavailable'))
        save(attempt / 'RECOVERY.json', dict(child=dict(command=command, returncode=child.returncode,
            stdout=child.stdout, stderr=child.stderr, tool_seconds=duration),
            registry=recovered_registry, telemetry=recovered_journal,
            resumed_registry_token=completed['token'], resumed_telemetry=branch_journal.recover(),
            completed_authoring_repeated=False, preserved_pending_bytes=True,
            durability_scope='process exit and atomic filesystem publication; no power-loss or hostile-host guarantee'))


def crash(attempt):
    journal = attempt / 'crash-journal/000004.json.pending'
    with journal.open('xb') as stream:
        stream.write(b'{"sequence":4,"kind":"complete",')
        stream.flush()
        os.fsync(stream.fileno())
    registry = Registry(attempt / 'crash-registry')
    current = registry.read()
    candidate = json.loads((attempt / 'crash-proposal.json').read_text())
    state = copy.deepcopy(current['state'])
    state['definitions'][candidate['identity']] = candidate
    body = dict(generation=2, previous=current['token'], operation='interrupted-admit', state=state)
    try:
        publish(attempt / 'crash-registry/000002.json', dict(body, identity=digest(body)), interrupt=True)
    except InterruptedError:
        os._exit(73)


def main():
    attempt = OUT / sys.argv[1]
    attempt.mkdir()  # no overwrite of an earlier attempt
    journal = Journal(attempt / 'telemetry')
    inputs = {p.relative_to(ROOT).as_posix(): sha(p) for p in Path(__file__).parent.glob('*.py')}
    inputs['benchmark/results/phase6/r6_32/PROTOCOL.md'] = sha(OUT / 'PROTOCOL.md')
    save(attempt / 'FREEZE.json', dict(inputs=inputs, model_calls=0, coordinator_scripted=True,
                                     expected_impact=sorted(fixture.REQUIRED)))
    try:
        registry = registry_qualification(attempt, journal)
        functional, impact_result = stateful_qualification(attempt, journal)
        recovery_qualification(attempt, journal)
        save(attempt / 'RESULT.json', dict(classification='R6_32_LIFECYCLE_PARTIAL',
            registry_definitions=registry['accepted_definitions'], controls=len(registry['controls']),
            functional_passed=functional['passed'], functional_total=functional['total'],
            impact_false_negatives=len(impact_result['false_negatives']),
            impact_false_positives=len(impact_result['false_positives']),
            model_calls=0, kernel=26, telemetry_recovery_passed=True,
            blocker='Production impact omits extension predicates/mutations; independent explicit impact sets remain necessary'))
    except BaseException as exc:
        save(attempt / 'FAILED.json', dict(exception=type(exc).__name__, diagnostic=str(exc),
                                          traceback=traceback.format_exc(), recovery=journal.recover()))
        raise
    print(json.dumps(json.loads((attempt / 'RESULT.json').read_text()), indent=2))


if __name__ == '__main__':
    if sys.argv[1] == 'crash':
        crash(Path(sys.argv[2]))
    else:
        main()
