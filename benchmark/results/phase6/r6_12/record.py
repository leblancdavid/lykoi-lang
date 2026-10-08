"""Small provider-neutral recorder; no AI dispatch or task behavior."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def save(path, value):
    assert not path.exists(), path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()


def protected():
    prefixes = ['src/', 'schema/', 'air/', 'generated/', 'tools/',
                'experiments/semantic_interpreter/', 'benchmark/harness/',
                'benchmark/evaluation/', 'benchmark/conventional/',
                'benchmark/results/phase5c/R5_114-KERNEL-ACCOUNTING.json']
    for n in range(3, 12):
        prefixes += [f'benchmark/results/phase6/r6_{n}/',
                     f'benchmark/results/phase6/R6_{n}-REPORT.md']
    return {p: sha(ROOT / p) for p in git('ls-files').splitlines()
            if any(p.startswith(prefix) for prefix in prefixes)}


def baseline():
    count = load(ROOT / 'benchmark/results/phase5c/R5_114-KERNEL-ACCOUNTING.json')['final_count']
    assert count == 26
    previous = load(ROOT / 'benchmark/results/phase6/r6_11/BASELINE.json')
    for name, identity in previous['protected'].items():
        assert sha(ROOT / name) == identity, name
    records = []
    commands = [
        [sys.executable, '-B', '-m', 'air_compiler.cli', 'validate', 'air/task_manager.json'],
        [sys.executable, '-B', '-m', 'air_compiler.cli', 'safety', 'air/task_manager.json'],
        *[[sys.executable, '-B', '-m', 'unittest', 'discover', '-s', folder, '-p', pattern, '-v']
          for folder, pattern in [('tests', 'test_compiler.py'), ('tests', 'test_application.py'),
                                  ('benchmark/harness', 'test_baseline.py'),
                                  ('experiments/semantic_interpreter', 'test_interpreter.py')]],
        ['git', '--version'], ['opencode', '--version']]
    env = dict(os.environ, PYTHONPATH=str(ROOT / 'src'), PYTHONDONTWRITEBYTECODE='1')
    for command in commands:
        started = time.perf_counter()
        try:
            proc = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True, timeout=180)
            record = dict(command=command, returncode=proc.returncode, stdout=proc.stdout,
                          stderr=proc.stderr, seconds=time.perf_counter()-started)
        except FileNotFoundError:
            record = dict(command=command, unavailable=True)
        records.append(record)
        if command[0] == sys.executable:
            assert record['returncode'] == 0, record
    save(HERE / 'BASELINE.json', dict(utc=now(), head=git('rev-parse', 'HEAD'),
         tree=git('rev-parse', 'HEAD^{tree}'), initial_status='clean before R6.12 files',
         kernel=count, protected=protected(), prior_protected_verified=len(previous['protected']),
         python=sys.version, platform=platform.platform(), checks=records,
         model='openai/gpt-6.1-sol', provider='OpenAI (harness-reported)',
         other_configurations='Not enumerated: no targeted non-secret configuration interface exposed',
         reasoning_configuration=None, input_tokens=None, output_tokens=None,
         reasoning_tokens=None, cached_tokens=None, model_calls=None, cost_usd=None,
         isolation='Fresh Task sessions and own directories available; no filesystem/provider attestation'))
    print('Baseline frozen; production validation/safety and 116 baseline methods passed')


def freeze():
    assert (HERE / 'BASELINE.json').exists()
    paths = [HERE / 'PROTOCOL.md', HERE / 'record.py']
    paths += sorted((HERE / 'tasks').rglob('*'))
    paths = [p for p in paths if p.is_file()]
    assert len(list((HERE / 'tasks').glob('T*/contract.md'))) == 5
    save(HERE / 'FREEZE.json', dict(utc=now(), files={p.relative_to(HERE).as_posix():sha(p) for p in paths}))
    print('Shared requirements, acceptance and staged modifications frozen')


def verify_freeze():
    for name, identity in load(HERE / 'FREEZE.json')['files'].items():
        assert sha(HERE / name) == identity, name


def start(track, task, stage):
    verify_freeze()
    directory = HERE / 'workspaces' / track / task / stage
    assert not directory.exists(), directory
    save(directory / 'START.json', dict(utc=now(), epoch=time.time(), track=track,
         task=task, stage=stage, baseline_sha256=sha(HERE / 'BASELINE.json'),
         freeze_sha256=sha(HERE / 'FREEZE.json'), budget_seconds=900,
         input_tokens=None, output_tokens=None, reasoning_tokens=None, cached_tokens=None,
         model_calls=None, cost_usd=None, model='openai/gpt-6.1-sol',
         provider='OpenAI (inherited harness; subagent routing unattested)'))


def evaluate(track, task, stage, attempt):
    verify_freeze()
    directory = HERE / 'workspaces' / track / task / stage
    start_record = load(directory / 'START.json')
    assert 1 <= attempt <= 3
    if attempt > 1:
        assert not load(directory / f'RESULT-{attempt-1}.json')['passed']
    candidate = directory / f'attempt{attempt}.py'
    assert candidate.exists()
    assert time.time()-start_record['epoch'] <= 900, 'Budget exceeded'
    suites = [('base', HERE / 'tasks' / task / 'acceptance.json')]
    if stage != 'base':
        suites += [('new', HERE / 'tasks' / task / 'modification' / 'acceptance.json')]
    cases = []
    for suite, path in suites:
        for index, case in enumerate(load(path)):
            command = [sys.executable, '-B', str(candidate)]
            before = time.perf_counter()
            try:
                proc = subprocess.run(command, input=json.dumps(case['input']), text=True,
                    capture_output=True, cwd=directory, timeout=10,
                    env=dict(os.environ, PYTHONPATH=str(ROOT / 'src'), PYTHONDONTWRITEBYTECODE='1'))
                try:
                    actual = json.loads(proc.stdout)
                except ValueError:
                    actual = None
                exact = lambda v: json.dumps(v, sort_keys=True, separators=(',', ':'))
                passed = proc.returncode == 0 and exact(actual) == exact(case['expected'])
                row = dict(suite=suite, case=index, input=case['input'], expected=case['expected'],
                    actual=actual, passed=passed, returncode=proc.returncode,
                    stdout=proc.stdout, stderr=proc.stderr, command=command)
            except subprocess.TimeoutExpired:
                row = dict(suite=suite, case=index, input=case['input'], expected=case['expected'],
                           passed=False, failure='TIMEOUT', command=command)
            row['test_seconds'] = time.perf_counter()-before
            cases.append(row)
    artifacts = {p.name:sha(p) for p in directory.iterdir()
                 if p.is_file() and p.name not in ['START.json'] and not p.name.startswith('RESULT-')}
    elapsed = time.time()-start_record['epoch']
    result = dict(track=track, task=task, stage=stage, attempt=attempt, utc=now(),
        elapsed_seconds=elapsed, test_seconds=sum(c['test_seconds'] for c in cases),
        passed=all(c['passed'] for c in cases), passed_cases=sum(c['passed'] for c in cases),
        total_cases=len(cases), repairs=attempt-1, artifacts=artifacts, cases=cases)
    save(directory / f'RESULT-{attempt}.json', result)
    print(f'{track}/{task}/{stage}/{attempt}: {result["passed_cases"]}/{len(cases)} in {elapsed:.3f}s')
    for c in cases:
        if not c['passed']:
            print(json.dumps(c))


def gap(track, task, stage, code, evidence):
    verify_freeze()
    directory = HERE / 'workspaces' / track / task / stage
    beginning = load(directory / 'START.json')
    elapsed = time.time()-beginning['epoch']
    assert elapsed <= 900
    save(directory / 'GAP.json', dict(track=track, task=task, stage=stage,
         utc=now(), elapsed_seconds=elapsed, status='CAPABILITY_GAP', code=code,
         evidence=evidence, acceptance_executed=False, repairs=0))
    print(f'{track}/{task}/{stage}: {code}; {elapsed:.3f}s')


def verify():
    verify_freeze()
    assert protected() == load(HERE / 'BASELINE.json')['protected']
    for path in HERE.glob('workspaces/*/*/*/RESULT-*.json'):
        for name, identity in load(path)['artifacts'].items():
            assert sha(path.parent / name) == identity, path.parent / name
    subprocess.run(['git', 'diff', '--check'], cwd=ROOT, check=True)
    print('Frozen inputs, candidate hashes and protected implementation/history intact')


if __name__ == '__main__':
    operation, *args = sys.argv[1:]
    if operation == 'evaluate':
        evaluate(*args[:3], int(args[3]))
    else:
        globals()[operation](*args)
