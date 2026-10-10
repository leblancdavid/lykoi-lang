"""Publication-only integrity checking, never application/model execution."""
from datetime import datetime
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from run import ROOT, HERE, OUT, R43, load, save, sha, now, verify, equal


def paths():
    selected = [ROOT / 'benchmark/results/phase6/R6_44-REPORT.md']
    selected += list(OUT.rglob('*')) + list(HERE.rglob('*'))
    selected += [ROOT / f'docs/{name}-r6.44.md' for name in ('project-overview', 'research-log', 'decisions')]
    return sorted(p for p in selected if p.is_file() and '__pycache__' not in p.parts and
                  p.name not in ('PUBLICATION-IDENTITIES.json', 'VERIFICATION.json'))


def checks(pending_publication=False):
    baseline = load(OUT / 'BASELINE.json')
    protected = verify(baseline['protected_files'])
    frozen = verify(load(OUT / 'FREEZE.json')['files'])
    publication43 = verify(load(R43 / 'PUBLICATION-IDENTITIES.json')['files'])
    receipt43 = load(R43 / 'VERIFICATION.json')
    assert receipt43['passed'] and receipt43['manifest_sha256'] == sha(R43 / 'PUBLICATION-IDENTITIES.json')
    archive = load(R43 / 'RAW-ARCHIVE.json')
    compressed = (R43 / 'QUALIFICATION.json.gz').read_bytes()
    raw = gzip.decompress(compressed)
    assert hashlib.sha256(compressed).hexdigest() == archive['archive_sha256']
    assert len(compressed) == archive['archive_bytes']
    assert hashlib.sha256(raw).hexdigest() == archive['raw_sha256']
    assert len(raw) == archive['raw_bytes'] and raw == (R43 / 'QUALIFICATION.json').read_bytes()
    assert load(ROOT / 'benchmark/results/phase5c/R5_114-KERNEL-ACCOUNTING.json')['final_count'] == 26
    result = load(OUT / 'RESULT-v2.json')
    assert result['classification'] == 'R6_44_COMPARISON_INCONCLUSIVE'
    assert result['identical_cross_track_functional_projection']
    for track in ('A', 'B'):
        a = load(OUT / f'AUTHOR-{track}.json')
        verify(a['files'])
        audit = load(OUT / f'AUDIT-{track}.json')
        assert audit['starting_baseline_preserved'] and audit['first_final_identical']
        assert audit['marker_audit_complete'] and not audit['forbidden_input_markers']
        assert audit['tool_budget_ok'] and audit['wall_budget_ok']
        assert a['process_exited'] and not a['timed_out']
        assert a['utc_start'] > load(OUT / 'FREEZE.json')['utc']
        assert load(OUT / f'BASELINE-ACCEPTED-v2-{track}.json')['accepted']
        for candidate in ('first', 'final'):
            r = load(OUT / f'FUNCTIONAL-{track}-{candidate}.json')
            assert r['accepted'] and r['passed'] == r['total'] == 188
            assert all(row['result_ok'] and row['state_ok'] and row['rejection_or_read_bytes_ok'] for row in r['observations'])
        original = load(OUT / f'FUNCTIONAL-{track}-final.json')
        replay = load(OUT / f'REPLAY-{track}.json')
        assert original['application_sha256'] == replay['application_sha256']
        project = lambda r: [{k: v for k, v in row.items() if k != 'seconds'} for row in r['observations']]
        assert project(original) == project(replay)
        reg = load(OUT / f'REGRESSION-v2-{track}.json')
        assert reg['retained_count'] == 177 and reg['superseded_count'] == 5 and reg['observed_regressions'] == 0
        assert load(OUT / f'INSTALL-{track}.json')['accepted']
        assert load(OUT / f'DIAGNOSTIC-{track}.json')['inherited_if_baseline_equals_modified']
    # Declarative B central behavior is regenerated identically by external evaluation.
    participant_bytes = (OUT / 'submissions/B/build-final/application.py').read_bytes()
    external_bytes = (OUT / 'build/submitted/B/final/application.py').read_bytes()
    assert participant_bytes.replace(b'\r\n', b'\n') == external_bytes
    json_count = link_count = source_count = 0
    for p in paths():
        content = p.read_text(encoding='utf-8')
        if p.suffix == '.json': load(p); json_count += 1
        if p.suffix == '.jsonl':
            for line in content.splitlines():
                if line: json.loads(line)
        if p.suffix == '.py': compile(content, str(p), 'exec'); source_count += 1
        # Preserve submission bytes; detect rather than repair defects.
        for number, line in enumerate(content.splitlines(), 1):
            assert line.rstrip(' \t') == line, (str(p), number, 'trailing whitespace')
        assert not re.search(r'\bsk-[A-Za-z0-9_-]{24,}|Bearer\s+[A-Za-z0-9_.-]{24,}', content), str(p)
        if p.suffix == '.md':
            for link in re.findall(r'\]\(([^)]+)\)', content):
                if link.startswith(('http:', 'https:', '#')): continue
                target = link.split('#')[0]
                resolved = (p.parent / target).resolve()
                pending = pending_publication and resolved in (OUT / 'PUBLICATION-IDENTITIES.json', OUT / 'VERIFICATION.json')
                assert resolved.exists() or pending, (str(p), link)
                link_count += 1
    diff = subprocess.run(['git', 'diff', '--check'], cwd=ROOT, capture_output=True, text=True)
    assert diff.returncode == 0, diff.stdout + diff.stderr
    # Tracked history has no agent modifications; new round is additive only.
    tracked_diff = subprocess.check_output(['git', 'diff', '--name-only', 'HEAD'], cwd=ROOT, text=True)
    assert not tracked_diff.strip(), tracked_diff
    status = subprocess.check_output(['git', 'status', '--short'], cwd=ROOT, text=True)
    allowed = ('benchmark/results/phase6/R6_44-REPORT.md', 'benchmark/results/phase6/r6_44/',
               'experiments/stateful_modification_r6_44/', 'docs/project-overview-r6.44.md',
               'docs/research-log-r6.44.md', 'docs/decisions-r6.44.md')
    assert all(line.startswith('?? ') and line[3:] in allowed for line in status.splitlines()), status
    return dict(passed=True, protected_identities=protected, frozen_identities=frozen,
        r6_43_publication_files=publication43, r6_43_lossless_archive_verified=True, kernel=26,
        json_files=json_count, compiled_python_sources=source_count, relative_links=link_count,
        submission_identities_verified=True, replay_identities_verified=True,
        participant_external_generation_differs_only_crlf=True,
        new_file_whitespace_checked=True, credential_patterns_checked=True,
        git_diff_check_returncode=diff.returncode, tracked_diff_empty=True, status=status)


def main(mode):
    if mode == 'create':
        stamp = now()
        start = datetime.fromisoformat(load(OUT / 'MEASUREMENTS.json')['workflow_start_utc'])
        end = datetime.fromisoformat(stamp)
        wall_name = 'WORKFLOW-WALL.json'
        version = 2
        while (OUT / wall_name).exists():
            wall_name = f'WORKFLOW-WALL-v{version}.json'
            version += 1
        save(OUT / wall_name, dict(utc_start=start.isoformat(), utc_publication_checkpoint=stamp,
            measurable_workflow_elapsed_seconds=(end-start).total_seconds(),
            coverage='coordinator session creation through publication checkpoint, including elapsed setup/review/authoring/scoring/documentation; excludes final verification execution and final response',
            active_stage_attribution_complete=False, total_billable_time=None))
        report = checks(pending_publication=True)
        records = {p.relative_to(ROOT).as_posix(): dict(sha256=sha(p), bytes=p.stat().st_size) for p in paths()}
        save(OUT / 'PUBLICATION-IDENTITIES.json', dict(utc=now(), files=records,
            excluded=['PUBLICATION-IDENTITIES.json', 'VERIFICATION.json'], round='R6.44'))
        verify(records)
        report.update(utc=now(), manifest_sha256=sha(OUT / 'PUBLICATION-IDENTITIES.json'), publication_files=len(records))
        save(OUT / 'VERIFICATION.json', report)
    elif mode == 'verify':
        verify(load(OUT / 'PUBLICATION-IDENTITIES.json')['files'])
        report = checks()
        receipt = load(OUT / 'VERIFICATION.json')
        assert receipt['passed'] and receipt['manifest_sha256'] == sha(OUT / 'PUBLICATION-IDENTITIES.json')
    else:
        raise ValueError(mode)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'create')
