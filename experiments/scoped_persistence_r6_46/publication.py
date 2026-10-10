"""Integrity-only publication and preservation checks; no application execution."""
from datetime import datetime, timezone
import json
import re
import subprocess
import sys
from prepare import ROOT, HERE, OUT, load, sha, save, verify
from build import generate


def paths():
    candidates = [ROOT / 'benchmark/results/phase6/R6_46-REPORT.md']
    candidates += list(OUT.rglob('*')) + list(HERE.rglob('*'))
    candidates += [ROOT / f'docs/{name}-r6.46.md' for name in ('project-overview', 'research-log', 'decisions')]
    return sorted(p for p in candidates if p.is_file() and '__pycache__' not in p.parts
                  and p.name not in ('PUBLICATION-IDENTITIES.json', 'VERIFICATION.json'))


def projection(result):
    return [{k: v for k, v in row.items() if k != 'seconds'} for row in result['observations']]


def checks(pending=False):
    count = verify(load(OUT / 'BASELINE.json')['protected_files'])
    frozen = verify(load(OUT / 'FREEZE.json')['files'])
    implementation = load(OUT / 'IMPLEMENTATION.json')
    verify(implementation['inputs'])
    app = OUT / 'build/application.py'
    assert sha(app) == implementation['application_sha256']
    assert sha(OUT / 'build/ir.json') == implementation['ir_sha256']
    source, ir = generate(load(ROOT / 'benchmark/results/phase6/r6_44/submissions/B/final.json'), load(HERE / 'profile.json'))
    assert source.encode('utf-8') == app.read_bytes() and ir == load(OUT / 'build/ir.json')
    assert load(ROOT / 'benchmark/results/phase5c/R5_114-KERNEL-ACCOUNTING.json')['final_count'] == 26
    result = load(OUT / 'RESULT-v3.json')
    assert result['classification'] == 'R6_46_PERSISTENCE_CONTRACT_CLOSED'
    assert result['scoped_regression_controls_pass'] and result['completed_regression_methods'] == 53
    assert not result['full_additional_workflow_suites_complete']
    for first, repeated, total in [('MATRIX-RESULTS.json', 'MATRIX-REPLAY.json', 25),
                                   ('KILN-REGRESSION.json', 'KILN-REPLAY.json', 188)]:
        a, b = load(OUT / first), load(OUT / repeated)
        assert a['accepted'] and b['accepted'] and a['passed'] == b['passed'] == a['total'] == b['total'] == total
        assert a['application_sha256'] == b['application_sha256'] == sha(app)
        assert projection(a) == projection(b)
    assert projection(load(OUT / 'KILN-REGRESSION.json')) == projection(load(ROOT / 'benchmark/results/phase6/r6_44/FUNCTIONAL-B-final.json'))
    assert load(OUT / 'MATRIX-RESULTS.json')['rows_passed'] == 18
    assert load(OUT / 'REPLAY.json')['ai_calls'] == 0
    for index in (1, 2, 3, 4, 8):
        assert load(OUT / f'regression/command-{index}.json')['passed']
    assert load(OUT / 'regression/direct-runtime-controls-v2.json')['passed']
    for index in (5, 6, 7):
        record = load(OUT / f'regression/command-{index}.json')
        assert record['returncode'] is None and record['timeout_seconds'] == 180
    counts = dict(json=0, python=0, links=0)
    for path in paths():
        content = path.read_text(encoding='utf-8')
        if path.suffix == '.json':
            load(path); counts['json'] += 1
        if path.suffix == '.py':
            compile(content, str(path), 'exec'); counts['python'] += 1
        for n, line in enumerate(content.splitlines(), 1):
            assert line.rstrip(' \t') == line, (str(path), n)
        assert not re.search(r'\bsk-[A-Za-z0-9_-]{24,}|Bearer\s+[A-Za-z0-9_.-]{24,}', content), str(path)
        if path.suffix == '.md':
            for link in re.findall(r'\]\(([^)]+)\)', content):
                if link.startswith(('http:', 'https:', '#')): continue
                target = (path.parent / link.split('#')[0]).resolve()
                allow = pending and target in (OUT / 'PUBLICATION-IDENTITIES.json', OUT / 'VERIFICATION.json')
                assert target.exists() or allow, (str(path), link)
                counts['links'] += 1
    diff = subprocess.run(['git', 'diff', '--check'], cwd=ROOT, capture_output=True, text=True)
    assert diff.returncode == 0, diff.stdout + diff.stderr
    tracked = subprocess.check_output(['git', 'diff', '--name-only', 'HEAD'], cwd=ROOT, text=True)
    assert not tracked.strip(), tracked
    status = subprocess.check_output(['git', 'status', '--short'], cwd=ROOT, text=True)
    allowed = ('benchmark/results/phase6/R6_46-REPORT.md', 'benchmark/results/phase6/r6_46/',
               'experiments/scoped_persistence_r6_46/', 'docs/project-overview-r6.46.md',
               'docs/research-log-r6.46.md', 'docs/decisions-r6.46.md')
    assert all(line.startswith('?? ') and line[3:] in allowed for line in status.splitlines()), status
    return dict(passed=True, round='R6.46', kernel=26, protected_identities=count, preservation_failures=[],
        frozen_identities=frozen, predecessor_and_successor_identities_verified=True,
        regeneration_exact=True, ir_unchanged=True, production_files_unchanged=True,
        matrix_rows=18, matrix_observations=25, kiln_regressions=188, completed_regression_methods=53,
        additional_workflow_suites_incomplete=3, retained_execution_attempts=True,
        ai_independent_replay_exact=True, historical_rescoring=False,
        p6_a04_acceptance_executions=0, p6_a05_access=False,
        credential_patterns_checked=True, new_file_whitespace_checked=True,
        git_diff_check_returncode=diff.returncode, tracked_diff_empty=True, implementation_scope_verified=True,
        status=status, integrity_counts=counts)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == 'verify':
        verify(load(OUT / 'PUBLICATION-IDENTITIES.json')['files'])
        report = checks()
        receipt = load(OUT / 'VERIFICATION.json')
        assert receipt['passed'] and receipt['manifest_sha256'] == sha(OUT / 'PUBLICATION-IDENTITIES.json')
    else:
        report = checks(pending=True)
        files = {p.relative_to(ROOT).as_posix(): dict(sha256=sha(p), bytes=p.stat().st_size) for p in paths()}
        save(OUT / 'PUBLICATION-IDENTITIES.json', dict(round='R6.46', files=files,
            excluded=['PUBLICATION-IDENTITIES.json', 'VERIFICATION.json']))
        verify(files)
        report.update(manifest_sha256=sha(OUT / 'PUBLICATION-IDENTITIES.json'), publication_files=len(files),
                      utc=datetime.now(timezone.utc).isoformat())
        save(OUT / 'VERIFICATION.json', report)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
