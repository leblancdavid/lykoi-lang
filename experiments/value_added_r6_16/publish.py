"""Final preservation, scope, deterministic-output and regression checks."""
import os
import re
import subprocess
import sys
import time
from evidence import HERE, OUT, ROOT, load, now, save, sha, verify
from generate import generate

GUIDANCE = ['AGENTS.md', 'benchmark/README.md', 'docs/agent-workflow.md',
            'docs/project-overview.md', 'docs/research-log.md', 'docs/decisions.md']


def main():
    baseline = load(OUT / 'BASELINE.json')
    verify(baseline['preserved'])
    assert load(ROOT / 'benchmark/results/phase5c/R5_114-KERNEL-ACCOUNTING.json')['final_count'] == 26
    for manifest in ('TASK-FREEZE.json', 'MODIFICATION-SEAL.json', 'INFRASTRUCTURE-FREEZE.json'):
        verify(load(OUT / manifest)['files'])
    for stage in range(3):
        verify(load(OUT / f'SUBMISSION-FREEZE-{stage}.json')['files'])
    deterministic = []
    for track in ('B', 'C'):
        for domain in ('kiln', 'custody'):
            for stage in range(3):
                phase = 'base' if stage == 0 else f's{stage}'
                intent = load(OUT / f'submissions/{track}/{domain}/{phase}/intent.json')
                source, ir = generate(intent, track)
                app = OUT / f'build/{track}/{domain}/{phase}/final/application.py'
                assert source == app.read_text(encoding='utf-8')
                if ir:
                    assert ir == load(app.with_name('ir.json'))
                deterministic.append(dict(track=track, domain=domain, stage=stage, source_sha256=sha(app), equal=True))
    tokens_complete = True
    budget_rows = []
    for stage in range(3):
        for r in load(OUT / f'TELEMETRY-{stage}.json')['sessions']:
            assert not r['forbidden_markers']
            for m in r['metadata']:
                assert m.get('providerID') == 'openai' and m.get('modelID') == 'gpt-6.1-sol'
                t = m.get('tokens', {})
                tokens_complete = tokens_complete and all(k in t for k in ('input', 'output', 'reasoning')) and all(k in t.get('cache', {}) for k in ('read', 'write'))
            assert r['tool_calls'] <= 12
            assert r['budget_first_to_last_tool_seconds'] <= 300
            budget_rows.append(dict(stage=stage, scope=r['scope'], tool_calls=r['tool_calls'],
                first_to_last_tool_seconds=r['budget_first_to_last_tool_seconds'], compliant=True))
    assert tokens_complete, 'Absent usage fields cannot be treated as zero'
    commands = [
        [sys.executable, '-B', '-m', 'unittest', 'discover', '-s', 'experiments/value_added_r6_16', '-p', 'test_*.py', '-v'],
        [sys.executable, '-B', '-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_compiler.py', '-v'],
        [sys.executable, '-B', '-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_application.py', '-v'],
        [sys.executable, '-B', '-m', 'unittest', 'discover', '-s', 'benchmark/harness', '-p', 'test_baseline.py', '-v'],
        [sys.executable, '-B', '-m', 'air_compiler.cli', 'validate', 'air/task_manager.json'],
        [sys.executable, '-B', '-m', 'air_compiler.cli', 'safety', 'air/task_manager.json'],
        ['git', 'diff', '--check']]
    checks = []
    env = {**os.environ, 'PYTHONPATH': str(ROOT / 'src'), 'PYTHONDONTWRITEBYTECODE': '1'}
    for command in commands:
        t = time.perf_counter()
        p = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True, timeout=120)
        checks.append(dict(command=command, returncode=p.returncode, seconds=time.perf_counter() - t,
                           stdout=p.stdout, stderr=p.stderr))
        print('PASS' if p.returncode == 0 else 'FAIL', ' '.join(command))
        if p.returncode:
            raise RuntimeError(p.stderr)
    # Existing R6.15 local files are in the preserved manifest, so source snapshots
    # protect that initial work even when git reports it as untracked.
    changed = subprocess.check_output(['git', 'diff', '--name-only'], cwd=ROOT, text=True).splitlines()
    assert set(changed) <= set(GUIDANCE), changed
    untracked = subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard'], cwd=ROOT, text=True).splitlines()
    allowed = ('experiments/value_added_r6_16/', 'benchmark/results/phase6/r6_16/')
    for name in untracked:
        assert name.startswith(allowed) or name in baseline['preserved'] or name == 'benchmark/results/phase6/R6_16-REPORT.md', name
    paths = [p for folder in (HERE, OUT) for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    paths += [ROOT / 'benchmark/results/phase6/R6_16-REPORT.md'] + [ROOT / n for n in GUIDANCE]
    whitespace = []
    for p in paths:
        for n, line in enumerate(p.read_text(encoding='utf-8').splitlines(), 1):
            if line.rstrip() != line:
                whitespace.append(dict(path=p.relative_to(ROOT).as_posix(), line=n))
    assert not whitespace, whitespace
    verify(baseline['preserved'])
    methods = sum(int(m.group(1)) for c in checks for m in [re.search(r'Ran (\d+) tests?', c['stderr'])] if m)
    save(OUT / 'PUBLICATION-CHECKS.json', dict(utc=now(), classification='R6_16_ARCHITECTURAL_COMPARISON_INCONCLUSIVE',
        kernel=26, preserved_identities=len(baseline['preserved']), checks=checks, regression_methods=methods,
        deterministic_outputs=deterministic, budgets=budget_rows, all_usage_fields_present=tokens_complete,
        tracked_change_scope=changed, untracked_scope_checked=True, whitespace=whitespace,
        p6_a04_acceptance_executions=0, p6_a05_access=False, provider_credentials_published=False))
    paths += [OUT / 'PUBLICATION-CHECKS.json']
    save(OUT / 'PUBLICATION-IDENTITIES.json', dict(utc=now(), classification='R6_16_ARCHITECTURAL_COMPARISON_INCONCLUSIVE',
        files={p.relative_to(ROOT).as_posix(): sha(p) for p in sorted(set(paths))}))
    verify(load(OUT / 'PUBLICATION-IDENTITIES.json')['files'])
    print('Published:', methods, 'test methods;', len(baseline['preserved']), 'identities preserved; kernel26; stop')


if __name__ == '__main__':
    main()
