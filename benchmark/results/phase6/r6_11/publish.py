"""Publication checks and fresh-process replay; never repairs a candidate."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from run import HERE, ROOT, freeze_check, load, now, protected, save, sha


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'))


def collect():
    freeze_check()
    rows = []
    replay = []
    sys.path.insert(0, str(ROOT/'experiments/semantic_interpreter'))
    from interpreter import validate
    for path in sorted(HERE.glob('workspaces/*/*/*/RESULT-1.json')):
        result = load(path)
        directory = path.parent
        start = load(directory/'START.json')
        assert start['utc'] > load(HERE/'FREEZE.json')['utc']
        assert result['elapsed_seconds'] <= start['time_budget_seconds']
        suffix = 'py' if result['track'] == 'conventional' else 'json'
        artifact = directory/f'attempt1.{suffix}'
        assert sha(artifact) == result['artifact_sha256']
        nodes = validate(load(artifact)) if suffix == 'json' else None
        regression_cases = [c for c in result['cases'] if c['suite'] == result['task']]
        new_cases = [c for c in result['cases'] if c['suite'] != result['task']]
        for case in result['cases']:
            # JSON-text equivalence additionally preserves Boolean/integer distinctions.
            assert canonical(case['actual']) == canonical(case['expected'])
            process = subprocess.run(case['command'], input=json.dumps({'hex':case['input_hex']}),
                text=True, capture_output=True, cwd=directory, timeout=10)
            assert process.returncode == 0, process.stderr
            assert canonical(json.loads(process.stdout)) == canonical(case['expected'])
            replay.append(dict(task=result['task'], track=result['track'], stage=result['stage'],
                               suite=case['suite'], case=case['case'], passed=True))
        rows.append(dict(task=result['task'], track=result['track'], stage=result['stage'],
            passed=result['passed'], cases=result['total_cases'], passed_cases=result['passed_cases'],
            first_attempt_success=result['passed'], repairs=0, tokens=None, cost_usd=None,
            elapsed_seconds=result['elapsed_seconds'], regression_failures=sum(not c['passed'] for c in regression_cases)
                if result['stage'] == 'modification' else None,
            original_cases=len(regression_cases), new_cases=len(new_cases),
            source_bytes=artifact.stat().st_size, structural_nodes=nodes,
            result_record=str(path.relative_to(HERE)).replace('\\','/')))
    assert len(rows) == 12
    totals = {}
    for track in ('conventional','experimental'):
        base = [r for r in rows if r['track'] == track and r['stage'] == 'base']
        mod = [r for r in rows if r['track'] == track and r['stage'] == 'modification']
        totals[track] = dict(base_tasks_passed=sum(r['passed'] for r in base), base_tasks=4,
            base_cases=sum(r['cases'] for r in base), base_elapsed_seconds=sum(r['elapsed_seconds'] for r in base),
            modification_tasks_passed=sum(r['passed'] for r in mod), modification_tasks=2,
            modification_cases=sum(r['cases'] for r in mod),
            modification_elapsed_seconds=sum(r['elapsed_seconds'] for r in mod),
            repairs=0, regression_failures=0, tokens=None, cost_usd=None)
    save(HERE/'COMPARISON.json', dict(classification='R6_11_EXPLORATORY_COMPARISON_ONLY',
        model='openai/gpt-6.1-sol', provider='OpenAI (session-reported)',
        production_tasks_scored=0, production_tasks_completed=0,
        production_profile_gap='raw-byte recognition; no integrated production parsing profile',
        rows=rows, totals=totals))
    save(HERE/'REPLAY.json', dict(utc=now(), exact_type_preserving_json=True,
                                cases=len(replay), passed=len(replay), observations=replay))
    print(json.dumps(totals, indent=2))


def checks():
    commands = [
        [sys.executable,'-B','-m','air_compiler.cli','validate','air/task_manager.json'],
        [sys.executable,'-B','-m','air_compiler.cli','safety','air/task_manager.json'],
        [sys.executable,'-B','-m','unittest','discover','-s','tests','-p','test_compiler.py','-v'],
        [sys.executable,'-B','-m','unittest','discover','-s','tests','-p','test_application.py','-v'],
        [sys.executable,'-B','-m','unittest','discover','-s','benchmark/harness','-p','test_baseline.py','-v'],
        [sys.executable,'-B','-m','unittest','discover','-s','experiments/semantic_interpreter','-p','test_interpreter.py','-v'],
        ['git','--version'],
        ['pwsh','-NoProfile','-Command','$PSVersionTable.PSVersion.ToString()'],
        ['pwsh','-NoProfile','-Command',"$tool = Get-Command opencode -ErrorAction SilentlyContinue; if ($tool) { opencode --version } else { 'OpenCode executable version unavailable' }"],
    ]
    env = dict(os.environ, PYTHONPATH=str(ROOT/'src'), PYTHONDONTWRITEBYTECODE='1')
    records = []
    for command in commands:
        started = time.perf_counter()
        proc = subprocess.run(command, cwd=ROOT, env=env, text=True, capture_output=True, timeout=120)
        records.append(dict(command=command, returncode=proc.returncode, stdout=proc.stdout,
                            stderr=proc.stderr, seconds=time.perf_counter()-started))
        print(f'{command}: exit {proc.returncode}')
        assert proc.returncode == 0, proc.stderr
    save(HERE/'CHECKS.json', dict(utc=now(), commands=records))


def publication():
    freeze_check()
    assert protected() == load(HERE/'BASELINE.json')['protected']
    subprocess.run(['git','diff','--check'], cwd=ROOT, check=True)
    for result in HERE.glob('workspaces/*/*/*/RESULT-1.json'):
        data=load(result)
        extension='py' if data['track']=='conventional' else 'json'
        assert sha(result.parent/f'attempt1.{extension}') == data['artifact_sha256']
    allowed = {'AGENTS.md','README.md','benchmark/README.md','docs/project-overview.md',
               'docs/agent-workflow.md','docs/research-log.md','docs/decisions.md'}
    changed = subprocess.check_output(['git','diff','--name-only'], cwd=ROOT, text=True).splitlines()
    assert set(changed) <= allowed, changed
    for name in changed:
        old = subprocess.check_output(['git','show',f'HEAD:{name}'], cwd=ROOT).decode().splitlines()
        current = (ROOT/name).read_text(encoding='utf-8').splitlines()
        iterator = iter(current)
        assert all(any(line==candidate for candidate in iterator) for line in old), name
    files=[p for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts
           and p.name != 'PUBLICATION-IDENTITIES.json']
    files += [ROOT/'benchmark/results/phase6/R6_11-REPORT.md'] + [ROOT/n for n in changed]
    for p in files:
        if p.suffix in ('.md','.py','.json'):
            assert all(not line.endswith((' ','\t')) for line in p.read_text(encoding='utf-8').splitlines()), p
    hashes={p.relative_to(ROOT).as_posix():sha(p) for p in sorted(files)}
    target=HERE/'PUBLICATION-IDENTITIES.json'
    if target.exists():
        assert load(target)['files'] == hashes
    else:
        save(target, dict(utc=now(), classification='R6_11_EXPLORATORY_COMPARISON_ONLY',
             self_hashed=False, protected_files=len(protected()), files=hashes))
    print(f'Publication integrity: {len(hashes)} files; {len(protected())} protected files unchanged; diff clean')


if __name__ == '__main__':
    {'collect':collect,'checks':checks,'publication':publication}[sys.argv[1]]()
