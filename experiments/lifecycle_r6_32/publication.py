"""Publish/verify R6.32 without rerunning qualification or historical acceptance."""
import json
from pathlib import Path
import re
import subprocess
import sys
from baseline import ROOT, OUT, save, sha
from lifecycle import Journal

REPORT = ROOT / 'benchmark/results/phase6/R6_32-REPORT.md'
EXPERIMENT = Path(__file__).resolve().parent
EXCLUSIONS = {'benchmark/results/phase6/r6_32/PUBLICATION-IDENTITIES.json',
              'benchmark/results/phase6/r6_32/VERIFICATION.json'}
INTENTIONALLY_INVALID = {'benchmark/results/phase6/r6_32/attempt-1/REGISTRY.json'}


def read(path):
    return json.loads(path.read_text())


def files():
    paths = [REPORT] + list(OUT.rglob('*')) + list(EXPERIMENT.rglob('*'))
    paths += [ROOT / ('docs/' + name + '-r6.32.md')
              for name in ('project-overview', 'research-log', 'decisions')]
    return sorted({p for p in paths if p.is_file() and '__pycache__' not in p.parts
        and p.relative_to(ROOT).as_posix() not in EXCLUSIONS})


def basic_checks():
    baseline = read(OUT / 'BASELINE.json')
    mismatches = [p for p, h in baseline['protected_files'].items() if sha(ROOT / p) != h]
    assert not mismatches, mismatches
    previous = ROOT / 'benchmark/results/phase6/r6_31'
    manifest = read(previous / 'PUBLICATION-IDENTITIES.json')
    assert sha(previous / 'PUBLICATION-IDENTITIES.json') == read(previous / 'VERIFICATION.json')['manifest_sha256']
    for p, meta in manifest['files'].items():
        assert sha(ROOT / p) == meta['sha256'] and (ROOT / p).stat().st_size == meta['bytes'], p
    for freeze in (OUT / 'attempt-5/FREEZE.json', OUT / 'supplement-2/FREEZE.json'):
        for p, h in read(freeze)['inputs'].items():
            location = ROOT / p if '/' in p else EXPERIMENT / p
            assert sha(location) == h, (str(freeze), p)
    for p, h in read(OUT / 'TEST-RESULTS-1.json')['inputs'].items():
        assert sha(ROOT / p) == h, p
    assert read(OUT / 'TEST-RESULTS-1.json')['returncode'] == 0
    for p in files():
        name = p.relative_to(ROOT).as_posix()
        raw = p.read_bytes()
        text = raw.decode('utf-8')
        if name not in INTENTIONALLY_INVALID:
            assert not any(line.endswith((' ', '\t')) for line in text.splitlines()), name
        if p.suffix == '.json':
            if name in INTENTIONALLY_INVALID:
                try:
                    json.loads(text)
                except json.JSONDecodeError:
                    pass
                else:
                    raise AssertionError('Expected preserved incomplete JSON: ' + name)
            else:
                json.loads(text)
        if p.suffix == '.md':
            for target in re.findall(r'\]\(([^)]+)\)', text):
                if '://' in target or target.startswith('#'):
                    continue
                assert (p.parent / target.split('#')[0]).resolve().exists(), (name, target)
    for path in ('attempt-1', 'attempt-2', 'attempt-3', 'attempt-4', 'attempt-5', 'supplement-1', 'supplement-2'):
        Journal(OUT / path / 'telemetry').recover()
    result = read(OUT / 'attempt-5/RESULT.json')
    assert result['classification'] == 'R6_32_LIFECYCLE_PARTIAL'
    assert result['functional_passed'] == result['functional_total'] == 148
    assert read(OUT / 'supplement-2/RESULT.json')['same_store']
    diff = subprocess.run(['git', 'diff', '--check'], cwd=ROOT, capture_output=True, text=True)
    assert diff.returncode == 0, diff.stdout + diff.stderr
    tracked = subprocess.check_output(['git', 'diff', '--name-only', 'HEAD'], cwd=ROOT, text=True)
    assert not tracked.strip(), tracked
    return dict(protected_identities_verified=len(baseline['protected_files']),
                protected_mismatches=mismatches, R6_31_publication_verified=True,
                git_diff_check=True, tracked_files_unchanged=True,
                additive_whitespace=True, relative_links=True, final_source_freezes=True,
                intentional_partial_JSON=list(INTENTIONALLY_INVALID),
                preserved_partial_bytes_exempt_from_whitespace=list(INTENTIONALLY_INVALID))


def measurements():
    measurements_path = OUT / 'MEASUREMENTS.json'
    if measurements_path.exists():
        return
    scopes = {}
    for folder in ('attempt-5', 'supplement-2'):
        recovery = Journal(OUT / folder / 'telemetry').recover()
        intervals = [e['data']['tool_seconds'] for e in recovery['events']
                     if type(e['data'].get('tool_seconds')) in (int, float)]
        scopes[folder] = dict(event_count=len(recovery['events']), completed=recovery['completed'],
            incomplete=recovery['incomplete'], pending=recovery['pending'],
            stage_wall_seconds={e['data']['stage']: e['data'].get('wall_seconds')
                for e in recovery['events'] if e['kind'] == 'complete'},
            measured_tool_interval_sum_seconds=sum(intervals), measured_tool_intervals=len(intervals),
            aggregate_caveat='Control intervals can enclose admission intervals; sum is not exclusive wall time',
            metadata_events_without_individual_tool_interval=[e['sequence'] for e in recovery['events']
                if e['kind'] in ('migration', 'validation_control', 'application_install')
                and 'tool_seconds' not in e['data']])
    save(measurements_path, dict(scopes=scopes, focused_test_wall_seconds=read(OUT / 'TEST-RESULTS-1.json')['wall_seconds'],
        complete_workflow_wall_seconds=None, missing_reason='Coordinator preparation/harness intervals not instrumented',
        participant_model_calls=0, model_tokens=None, API_billing=None,
        usage_missing_reason='No participant inference; no provider usage was collected',
        interrupted_stage_wall_seconds=None, interrupted_stub_authoring_seconds=None))


def main():
    mode = sys.argv[1]
    if mode == 'publish':
        measurements()
        checks = basic_checks()
        paths = files()
        save(OUT / 'PUBLICATION-IDENTITIES.json', dict(round='R6.32',
            classification='R6_32_LIFECYCLE_PARTIAL', hash_algorithm='SHA256 raw bytes',
            excluded_self_referential_files=sorted(EXCLUSIONS),
            files={p.relative_to(ROOT).as_posix(): dict(sha256=sha(p), bytes=p.stat().st_size) for p in paths}))
        save(OUT / 'VERIFICATION.json', dict(round='R6.32', passed=True,
            classification='R6_32_LIFECYCLE_PARTIAL', manifest_sha256=sha(OUT / 'PUBLICATION-IDENTITIES.json'),
            publication_files_verified=len(paths), checks=checks, kernel=26,
            model_calls=0, P6_A04_acceptance=False, P6_A05_access=False,
            preservation='Production/R6.10/R6.18/R6.23/R6.25/R6.3-R6.31 unchanged',
            stopped_after_publication=True))
    elif mode == 'verify':
        checks = basic_checks()
        manifest = read(OUT / 'PUBLICATION-IDENTITIES.json')
        receipt = read(OUT / 'VERIFICATION.json')
        assert receipt['passed'] and receipt['checks'] == checks
        assert receipt['manifest_sha256'] == sha(OUT / 'PUBLICATION-IDENTITIES.json')
        assert set(manifest['files']) == {p.relative_to(ROOT).as_posix() for p in files()}
        for p, meta in manifest['files'].items():
            assert sha(ROOT / p) == meta['sha256'] and (ROOT / p).stat().st_size == meta['bytes'], p
    else:
        raise ValueError('publish or verify')
    print('R6.32 integrity verified:', checks['protected_identities_verified'], 'protected identities;',
          len(read(OUT / 'PUBLICATION-IDENTITIES.json')['files']), 'publication files')


if __name__ == '__main__':
    main()
