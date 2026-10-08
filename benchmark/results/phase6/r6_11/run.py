"""Bounded artifact/acceptance recorder. Does not call any AI provider."""
import datetime
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def save(p, value):
    assert not p.exists(), f'write-once record exists: {p}'
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def load(p):
    return json.loads(p.read_text(encoding='utf-8'))


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()


def protected():
    prefixes = ['src/', 'schema/', 'air/', 'generated/', 'tools/',
                'experiments/semantic_interpreter/', 'benchmark/harness/',
                'benchmark/evaluation/', 'benchmark/conventional/',
                'benchmark/results/phase5c/R5_114-KERNEL-ACCOUNTING.json']
    for n in range(3, 11):
        prefixes += [f'benchmark/results/phase6/r6_{n}/',
                     f'benchmark/results/phase6/R6_{n}-REPORT.md']
    return {p: sha(ROOT / p) for p in git('ls-files').splitlines()
            if any(p.startswith(prefix) for prefix in prefixes)}


def freeze_check():
    frozen = load(HERE / 'FREEZE.json')
    for name, expected in frozen['files'].items():
        assert sha(HERE / name) == expected, f'freeze changed: {name}'


def baseline():
    sys.path.insert(0, str(ROOT / 'experiments/semantic_interpreter'))
    from baseline import verify_publications
    previous = load(ROOT / 'experiments/semantic_interpreter/PUBLICATION-IDENTITIES.json')
    verified = verify_publications()
    for p, expected in previous['publication_sha256'].items():
        if p.startswith('experiments/semantic_interpreter/') or p == 'benchmark/results/phase6/R6_10-REPORT.md':
            assert sha(ROOT / p) == expected, p
            verified[p] = expected
    count = load(ROOT / 'benchmark/results/phase5c/R5_114-KERNEL-ACCOUNTING.json')['final_count']
    assert count == 26
    save(HERE / 'BASELINE.json', dict(utc=now(), head=git('rev-parse', 'HEAD'),
         tree=git('rev-parse', 'HEAD^{tree}'), initial_status=git('status', '--porcelain'),
         kernel=count, protected=protected(), historical_hashes_verified=len(verified),
         python=sys.version, executable=sys.executable, platform=platform.platform(),
         model='openai/gpt-6.1-sol', provider='OpenAI (session-reported)',
         reasoning_configuration=None, tokens=None, cost_usd=None,
         provider_configuration='Active harness only; no credential/config inspection or separate API calls'))
    print('Recorded protected baseline and historical publication verification')


def freeze():
    sys.path.insert(0, str(ROOT))
    from benchmark.evaluation.formal_requirements_r5_80 import validate
    text = (HERE / 'TASKS.md').read_text(encoding='utf-8')
    common = text.split('## T1')[0]
    for task in ('T1', 'T2', 'T3', 'T4'):
        section = next(s for s in text.split('\n## ') if s.startswith(task))
        source = common + '\n## ' + section
        contract = dict(schema_version='FormalRequirementContract-0.1',
            contract_id=f'R6.11-{task}', revision=1,
            source=dict(id=task, text=source, sha256=hashlib.sha256(source.encode()).hexdigest(), classification='SYNTHETIC'),
            context=dict(scope='exploratory pure byte-input pilot', domains={'input':'bytes <=64'},
                         assumptions=['Same-agent synthetic source; no independent review'], component_authority=None),
            obligations=[dict(id=f'{task}-behavior', basis='STATED', source_quote=section,
                derived_from=[], relation=dict(kind='effects', parameters={'observation_specification': section}), statement=section)],
            issues=[], unspecified=[], implementation_choices=['Python or explicit semantic-plan-1'],
            lineage=[], formalizer='OpenAI gpt-6.1-sol active session', review=None)
        validate(contract)
        save(HERE / f'contracts/{task}.json', contract)
    names = ['PROTOCOL.md','TASKS.md','ACCEPTANCE.json','transport.py','run.py']
    names += [f'contracts/{t}.json' for t in ('T1','T2','T3','T4')]
    save(HERE / 'FREEZE.json', dict(utc=now(), files={n:sha(HERE/n) for n in names},
                                  modification_freeze='M2/M4 sections and tests included', frc_envelopes_validated=4))
    print('Frozen four shared contracts, acceptance and both modifications before authoring')


def start(task, track, stage):
    freeze_check()
    directory = HERE / f'workspaces/{task}/{track}/{stage}'
    assert not directory.exists(), 'workspace must be clean'
    save(directory / 'START.json', dict(utc=now(), epoch=time.time(), task=task,
        track=track, stage=stage, initial_files=[], baseline_sha256=sha(HERE/'BASELINE.json'),
        freeze_sha256=sha(HERE/'FREEZE.json'), model='openai/gpt-6.1-sol',
        time_budget_seconds=900, nominal_token_budget=8000, token_budget_enforced=False))
    print(f'Started {task}/{track}/{stage}')


def evaluate(task, track, stage, attempt):
    freeze_check()
    directory = HERE / f'workspaces/{task}/{track}/{stage}'
    beginning = load(directory / 'START.json')
    suffix = 'py' if track == 'conventional' else 'json'
    artifact = directory / f'attempt{attempt}.{suffix}'
    assert artifact.is_file()
    assert 1 <= attempt <= 3
    if attempt > 1:
        prior = load(directory / f'RESULT-{attempt-1}.json')
        assert not prior['passed'], 'stop at success'
    assert time.time() - beginning['epoch'] <= 900, 'development budget exhausted'
    cases = load(HERE / 'ACCEPTANCE.json')
    suites = [task] if stage == 'base' else [task, 'M' + task[1:]]
    records = []
    # Common maximum-input boundary is part of every frozen suite.
    for suite in suites:
        for index, case in enumerate(cases[suite] + [['00' * 65, 'INPUT_LIMIT', 64]]):
            expected = ({'status':'success','value':case[1]} if len(case) == 2 else
                        {'status':'reject','code':case[1],'offset':case[2]})
            command = [sys.executable, '-B', str(HERE/'transport.py'), track, str(artifact)]
            started = time.perf_counter()
            try:
                proc = subprocess.run(command, input=json.dumps({'hex':case[0]}),
                    text=True, capture_output=True, cwd=directory, timeout=10)
                try:
                    actual = json.loads(proc.stdout)
                except ValueError:
                    actual = None
                ok = proc.returncode == 0 and actual == expected
                record = dict(suite=suite, case=index, command=command, input_hex=case[0],
                    expected=expected, actual=actual, passed=ok, returncode=proc.returncode,
                    stdout=proc.stdout, stderr=proc.stderr)
            except subprocess.TimeoutExpired:
                record = dict(suite=suite, case=index, passed=False, failure='INFRASTRUCTURE_TIMEOUT')
            record['process_seconds'] = time.perf_counter()-started
            records.append(record)
    result = dict(task=task, track=track, stage=stage, attempt=attempt, ended_utc=now(),
        elapsed_seconds=time.time()-beginning['epoch'], artifact_sha256=sha(artifact),
        passed=all(r['passed'] for r in records), passed_cases=sum(r['passed'] for r in records),
        total_cases=len(records), repairs=attempt-1, tokens=None, cost_usd=None, cases=records)
    save(directory / f'RESULT-{attempt}.json', result)
    print(f"{task}/{track}/{stage} attempt {attempt}: {result['passed_cases']}/{len(records)}; elapsed {result['elapsed_seconds']:.3f}s")
    for record in records:
        if not record['passed']:
            print(json.dumps(record))


def verify():
    freeze_check()
    assert protected() == load(HERE/'BASELINE.json')['protected'], 'protected files changed'
    subprocess.run(['git','diff','--check'], cwd=ROOT, check=True)
    for p in HERE.rglob('*'):
        if p.is_file() and p.suffix in ('.py','.md','.json'):
            assert all(not line.endswith((' ','\t')) for line in p.read_text(encoding='utf-8').splitlines()), p
    print('Frozen acceptance/contracts intact; protected bytes unchanged; diff and publication whitespace clean')


if __name__ == '__main__':
    operation, *args = sys.argv[1:]
    if operation == 'baseline': baseline()
    elif operation == 'freeze': freeze()
    elif operation == 'start': start(*args)
    elif operation == 'evaluate': evaluate(*args[:3], int(args[3]))
    elif operation == 'verify': verify()
    else: raise ValueError(operation)
