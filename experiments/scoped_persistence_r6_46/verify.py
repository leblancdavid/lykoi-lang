"""AI-free acceptance, deterministic replay and focused production regression."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from prepare import ROOT, HERE, OUT, load, sha, save, verify
from build import generate

sys.path.insert(0, str(ROOT / 'experiments/stateful_modification_r6_44'))
from run import evaluate, equal, TEMP

TEMP_ROOT = Path(r'C:\Users\lblan\AppData\Local\Temp\opencode')
APP = OUT / 'build/application.py'


def projection(result):
    return [{k: v for k, v in row.items() if k != 'seconds'} for row in result['observations']]


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def matrix():
    rows = []
    for fixture in load(OUT / 'MATRIX.json'):
        with tempfile.TemporaryDirectory(prefix='r646-', dir=TEMP_ROOT) as tmp:
            store = Path(tmp) / 'records.json'
            if fixture['initial_hex'] is not None:
                store.write_bytes(bytes.fromhex(fixture['initial_hex']))
            for index, step in enumerate(fixture['steps']):
                before = store.read_bytes() if store.exists() else None
                request = dict(op=step['op'], args=step['args'], providers={})
                process = subprocess.run([sys.executable, '-B', str(ROOT / 'experiments/value_added_r6_16/transport.py'), str(APP)],
                    input=json.dumps(request), cwd=tmp, capture_output=True, text=True, timeout=30,
                    env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
                after = store.read_bytes() if store.exists() else None
                try:
                    observed = json.loads(process.stdout)
                    persisted = json.loads(after) if after is not None else None
                except (ValueError, TypeError):
                    observed, persisted = None, None
                result_ok = process.returncode == 0 and equal(observed, step['expected'])
                state_ok = equal(persisted, step['state'])
                bytes_ok = not step['unchanged'] or before == after
                rows.append(dict(case=fixture['id'], variant=fixture['variant'], step=index,
                    request=request, expected=step['expected'], expected_state=step['state'],
                    observed=observed, persisted=persisted, stdout=process.stdout, stderr=process.stderr,
                    returncode=process.returncode, before_hex=None if before is None else before.hex(),
                    after_hex=None if after is None else after.hex(),
                    result_ok=result_ok, state_ok=state_ok, bytes_ok=bytes_ok,
                    passed=result_ok and state_ok and bytes_ok))
    groups = {key: all(r['passed'] for r in rows if r['case'] == key) for key in sorted({r['case'] for r in rows})}
    return dict(application_sha256=sha(APP), observations=rows, row_results=groups,
                passed=sum(r['passed'] for r in rows), total=len(rows),
                rows_passed=sum(groups.values()), rows_total=len(groups), accepted=all(groups.values()))


def regressions():
    commands = [[sys.executable, '-B', str(HERE / 'test_adapter.py')]]
    for name in ('test_compiler.py', 'test_application.py', 'test_mutable_values.py',
                 'test_predicates.py', 'test_historical_state.py', 'test_authorization_composition.py'):
        commands.append([sys.executable, '-B', '-m', 'unittest', 'discover', '-s', 'tests', '-p', name, '-v'])
    commands.append([sys.executable, '-B', '-m', 'unittest', 'discover', '-s', 'benchmark/harness', '-p', 'test_baseline.py', '-v'])
    records = []
    env = {**os.environ, 'PYTHONPATH': str(ROOT / 'src'), 'PYTHONDONTWRITEBYTECODE': '1'}
    for index, command in enumerate(commands):
        path = OUT / f'regression/command-{index+1}.json'
        if path.exists():
            record = load(path)
            assert record['command'] == command
        else:
            try:
                p = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True, timeout=180)
                record = dict(command=command, returncode=p.returncode, stdout=p.stdout, stderr=p.stderr, passed=p.returncode == 0)
            except subprocess.TimeoutExpired as exc:
                record = dict(command=command, returncode=None, stdout=str(exc.stdout), stderr=str(exc.stderr), passed=False, timeout_seconds=180)
            save(path, record)
        records.append(record)
    return dict(commands=records, passed=all(r['passed'] for r in records))


def main():
    assert TEMP_ROOT.is_dir() and TEMP.is_dir()
    verify(load(OUT / 'BASELINE.json')['protected_files'])
    verify(load(OUT / 'FREEZE.json')['files'])
    implementation = load(OUT / 'IMPLEMENTATION.json')
    verify(implementation['inputs'])
    assert sha(APP) == implementation['application_sha256']
    source, ir = generate(load(ROOT / 'benchmark/results/phase6/r6_44/submissions/B/final.json'), load(HERE / 'profile.json'))
    assert source.encode() == APP.read_bytes() and ir == load(OUT / 'build/ir.json')
    if len(sys.argv) > 1 and sys.argv[1] == 'resume':
        first = load(OUT / 'MATRIX-RESULTS.json')
        replay = load(OUT / 'MATRIX-REPLAY.json')
        retained = load(OUT / 'KILN-REGRESSION.json')
        repeated = load(OUT / 'KILN-REPLAY.json')
        assert all(r['application_sha256'] == sha(APP) for r in (first, replay, retained, repeated))
    else:
        first = matrix()
        save(OUT / 'MATRIX-RESULTS.json', first)
        replay = matrix()
        save(OUT / 'MATRIX-REPLAY.json', replay)
        expectations = load(ROOT / 'benchmark/results/phase6/r6_44/MODIFIED-EXPECTATIONS-v2.json')
        retained = evaluate(APP, expectations)
        save(OUT / 'KILN-REGRESSION.json', retained)
        repeated = evaluate(APP, expectations)
        save(OUT / 'KILN-REPLAY.json', repeated)
    prior = load(ROOT / 'benchmark/results/phase6/r6_44/FUNCTIONAL-B-final.json')
    historical_same = projection(prior) == projection(retained)
    tests = regressions()
    save(OUT / 'REGRESSION.json', tests)
    replay_same = (projection(first) == projection(replay) and projection(retained) == projection(repeated))
    save(OUT / 'REPLAY.json', dict(ai_calls=0, fresh_process_per_operation=True, deterministic=replay_same,
        application_identity_unchanged=sha(APP) == implementation['application_sha256'],
        matrix_projection_sha256=digest(projection(first)),
        matrix_replay_projection_sha256=digest(projection(replay)),
        kiln_projection_sha256=digest(projection(retained)),
        kiln_replay_projection_sha256=digest(projection(repeated)),
        comparison='outputs, errors, return codes, stdout/stderr, persisted values and exact before/after bytes; excludes wall-clock timings'))
    closed = first['accepted'] and replay['accepted'] and retained['accepted'] and repeated['accepted'] and tests['passed'] and replay_same and historical_same
    save(OUT / 'RESULT.json', dict(classification='R6_46_PERSISTENCE_CONTRACT_CLOSED' if closed else 'R6_46_REGRESSION_GAP',
        matrix_rows_passed=first['rows_passed'], matrix_rows_total=18, matrix_observations_passed=first['passed'], matrix_observations_total=25,
        kiln_regression_passed=retained['passed'], kiln_regression_total=retained['total'],
        historical_accepted_projection_exact=historical_same, deterministic_replay=replay_same,
        regression_commands_pass=tests['passed'], kernel=26, ai_calls_during_execution=0,
        historical_rescoring=False, p6_a04_acceptance_executions=0, p6_a05_access=False))
    verify(load(OUT / 'BASELINE.json')['protected_files'])
    print(json.dumps(load(OUT / 'RESULT.json'), indent=2))


if __name__ == '__main__':
    main()
