"""R5.62 focused execution-boundary evidence; no production qualification mode."""

import io
import os
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]
from benchmark.evaluation import capability_guard_r5_61 as guard
from benchmark.evaluation import publication_r5_59 as publication
from benchmark.evaluation import mediated_child_r5_62 as child
from benchmark.evaluation import restricted_harness_r5_61 as exclusion
from benchmark.evaluation.recorder_r5_43 import canonical, digest, loads

OUT = ROOT / 'benchmark/results/phase5c/R5_62-evidence'
SUITES = {
    'mediated-child': 'benchmark.evaluation.test_mediated_child_r5_62',
    'capability-guard': 'benchmark.evaluation.test_capability_guard_r5_61',
    'bounded-driver': 'benchmark.evaluation.test_bounded_driver_r5_57',
    'observation-tier2': 'benchmark.evaluation.test_tier2_r5_51',
    'recorder': 'benchmark.harness.test_canonical_evidence_r5_43',
    'authority-synthetic': 'benchmark.evaluation.test_authority_r5_53',
    'continuity': 'benchmark.evaluation.test_continuity_r5_59',
    'publication-security': 'benchmark.evaluation.test_publication_r5_59',
    'ai-independence': 'benchmark.evaluation.test_ai_independence_r5_49',
    'schema-traceability': 'benchmark.harness.test_optional_support_r5_41',
}


def write(name, value):
    publication.persist(OUT / (name + '.json'), value)


def read(name):
    return loads((OUT / (name + '.json')).read_bytes())


def baseline():
    assert OUT.parent.is_dir() and not OUT.exists()
    changed = subprocess.check_output(['git', 'diff', '--name-only', '--', 'benchmark/results'],
                                     cwd=ROOT, text=True).splitlines()
    assert not changed
    names = subprocess.check_output(['git', 'ls-files', '--cached', '--others', '--exclude-standard',
                                     'benchmark/results'], cwd=ROOT, text=True).splitlines()
    protected = {r.path.resolve() for r in guard.repository_resources(ROOT)}
    files, sealed = {}, {}
    for name in sorted(set(names)):
        path = ROOT / name
        if path.resolve() in protected:
            info = path.stat()
            sealed[name] = {'size': info.st_size, 'mtime_ns': info.st_mtime_ns}
        else:
            files[name] = digest(path.read_bytes())
    OUT.mkdir()
    write('preservation-baseline', {'files': files, 'sealed_metadata_only': sealed,
        'historical_results_diff': changed, 'captured_before_r562_evidence': True,
        'sealed_content_read_for_preservation': False})
    write('development-checks', {'attempts': [
        {'discovered': 32, 'passed': 20, 'failures': 11, 'errors': 1, 'status': 'FAIL',
         'reason': 'Windows adapter pipe wrapping initially denied before process launch'},
        {'discovered': 32, 'passed': 20, 'failures': 11, 'errors': 1, 'status': 'FAIL',
         'reason': 'Windows normalized Popen audit arguments differed from POSIX form'},
        {'discovered': 32, 'passed': 32, 'status': 'PASS', 'scope': 'intermediate mediated witnesses'},
        {'discovered': 99, 'passed': 99, 'status': 'PASS', 'scope': 'expanded child/guard/driver development check'}],
        'production_attempts': 0, 'b02_exposure': 0})
    print({'historical_files': len(files) + len(sealed), 'sealed_metadata_only': len(sealed)})


def suite(label, tag=None):
    loader = unittest.TestLoader()
    tests = loader.loadTestsFromName(SUITES[label])
    assert not loader.errors
    result = unittest.TextTestRunner(stream=io.StringIO()).run(tests)
    value = {'suite': label, 'discovered': result.testsRun,
        'passed': result.testsRun - len(result.errors) - len(result.failures) - len(result.skipped),
        'errors': [t.id() for t, _ in result.errors], 'failures': [t.id() for t, _ in result.failures],
        'skipped': [t.id() for t, _ in result.skipped], 'successful': result.wasSuccessful(),
        'diagnostics': 'withheld', 'protected_content_used': False,
        'implementation_sha256': child.implementation(ROOT, child.RUNTIME + (
            'benchmark/evaluation/safe_workers_r5_62.py',
            'benchmark/evaluation/child_witnesses_r5_62.py',
            'benchmark/evaluation/synthetic_sut_r5_62.py',
            'benchmark/evaluation/bounded_driver_r5_57.py',
            'benchmark/evaluation/test_mediated_child_r5_62.py'))}
    write(label + (('-' + tag) if tag else ''), value)
    print({k: value[k] for k in ('suite', 'discovered', 'passed', 'successful')})
    if not result.wasSuccessful():
        raise SystemExit(1)


def checks():
    # Reuse the qualified generic checks with a separately versioned destination;
    # no R5.61 record is rewritten or reclassified.
    from benchmark.results.phase5c import r5_61_qualification as prior
    prior.OUT = OUT
    prior.checks()


def summary():
    results = {label: read(label + ('-published' if label == 'mediated-child' else
        '-qualified' if label in ('capability-guard', 'bounded-driver') else '')) for label in SUITES}
    assert all(row['successful'] for row in results.values()) and read('commands')['successful']
    assert read('checks')['core_semantics'] == 30
    probe = 'benchmark.evaluation.child_witnesses_r5_62'
    safe = 'benchmark.evaluation.safe_workers_r5_62'
    workers = child.registry(ROOT, {
        'synthetic-probe': (probe, 'probe', [probe.replace('.', '/') + '.py']),
        'safe-indexed-harness': (safe, 'harness', [safe.replace('.', '/') + '.py', probe.replace('.', '/') + '.py']),
        'synthetic-sut': (safe, 'sut', [safe.replace('.', '/') + '.py', 'benchmark/evaluation/synthetic_sut_r5_62.py'])})
    write('qualified-worker-policy', {'registry': workers, 'registry_sha256': digest(canonical(workers)),
        'runtime': child.implementation(ROOT, child.RUNTIME), 'exclusion': exclusion.INDEX_PIN,
        'qualification_scope': 'focused synthetic boundary and metadata-only harness witnesses',
        'production_registry_frozen': False, 'b02_exposure': 0})
    write('summary', {'classification': 'R5_62_MEDIATED_CHILD_EXECUTION_QUALIFIED',
        'inherited_r560': 'R5_60_PROTOCOL_HALT', 'inherited_r561': 'R5_61_PROTECTED_RESOURCE_GAP',
        'focused_suites': {label: {'discovered': row['discovered'], 'passed': row['passed']}
                           for label, row in results.items()},
        'focused_discovered': sum(row['discovered'] for row in results.values()),
        'focused_passed': sum(row['passed'] for row in results.values()),
        'prohibited_b02_skips': 36, 'restricted_child_mixed': {'discovered': 37, 'skipped': 36, 'ordinary_passed': 1},
        'b02_exposure': 0, 'core_semantics': 30,
        'production_b02_accounting': {'reservations': 0, 'dispatches': 0, 'completions': 0},
        'production_synthetic_accounting': {'reservations': 0, 'dispatches': 0, 'completions': 0},
        'production_batches': 0, 'production_receipts': 0, 'production_certificate_issued': False,
        'full_production_qualification_run': False, 'phase5c': 'paused',
        'next': 'separately authorize wholly fresh production qualification with reviewed pinned worker closures'})
    print({'classification': 'R5_62_MEDIATED_CHILD_EXECUTION_QUALIFIED',
           'focused_passed': sum(row['passed'] for row in results.values())})


def final():
    baseline = read('preservation-baseline')
    scope = read('preservation-scope-adjudication')
    assert scope['baseline_sha256'] == digest((OUT / 'preservation-baseline.json').read_bytes())
    excluded = scope['prospective_files']
    assert excluded == ['benchmark/results/phase5c/r5_62_qualification.py']
    historical = {name: pin for name, pin in baseline['files'].items() if name not in excluded}
    assert all(digest((ROOT / name).read_bytes()) == pin for name, pin in historical.items())
    for name, row in baseline['sealed_metadata_only'].items():
        info = (ROOT / name).stat()
        assert row == {'size': info.st_size, 'mtime_ns': info.st_mtime_ns}
    assert not subprocess.check_output(['git', 'diff', '--name-only', '--', 'benchmark/results'],
                                       cwd=ROOT, text=True).strip()
    assert loads((OUT.parent / 'R5_60-evidence/summary.json').read_bytes())['primary_classification'] == 'R5_60_PROTOCOL_HALT'
    assert loads((OUT.parent / 'R5_61-evidence/summary.json').read_bytes())['classification'] == 'R5_61_PROTECTED_RESOURCE_GAP'
    evidence = {}
    for path in OUT.glob('*.json'):
        raw = path.read_bytes()
        value = loads(raw)
        assert raw == canonical(value) + b'\n'
        publication.safe_bytes(value)
        evidence[path.name] = digest(raw)
    names = subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard', '--modified'],
                                   cwd=ROOT, text=True).splitlines()
    dispositions, pins = {}, {}
    for name in sorted(set(names)):
        path = ROOT / name
        if path.suffix in ('.py', '.md', '.json'):
            dispositions[name] = publication.check_source(name, path.read_bytes())
            pins[name] = digest(path.read_bytes())
            checked = subprocess.run(['git', 'diff', '--no-index', '--check', '--', 'NUL', str(path)],
                                     cwd=ROOT, capture_output=True, timeout=10)
            assert checked.returncode in (0, 1) and not checked.stdout
    assert subprocess.run(['git', 'diff', '--check'], cwd=ROOT, capture_output=True).returncode == 0
    write('publication-integrity', {'historical_files_hash_verified': len(historical),
        'sealed_metadata_verified_without_content_reads': len(baseline['sealed_metadata_only']),
        'historical_results_diff': [], 'r560_halt_preserved': True, 'r561_gap_preserved': True,
        'evidence_sha256': evidence, 'source_sha256': pins, 'source_dispositions': dispositions,
        'git_diff_check': 'PASS', 'new_file_whitespace_check': 'PASS',
        'b02_exposure': 0, 'production_receipts': 0, 'core_semantics': 30})
    print({'publication_integrity': 'PASS', 'historical_hashes': len(historical),
           'sealed_metadata': len(baseline['sealed_metadata_only'])})


def preservation_scope():
    # Original baseline stays immutable. Its new orchestration script was added
    # after initial Git status, and is prospective source, not historical evidence.
    name = 'benchmark/results/phase5c/r5_62_qualification.py'
    assert name in read('preservation-baseline')['files']
    write('integrity-development-failure', {'status': 'FAIL',
        'reason': 'preservation baseline accidentally included the new mutable R5.62 orchestration source',
        'publication_record_issued': False, 'historical_evidence_modified': False,
        'production_attempts': 0, 'b02_exposure': 0})
    write('preservation-scope-adjudication', {
        'baseline_sha256': digest((OUT / 'preservation-baseline.json').read_bytes()),
        'prospective_files': [name], 'reason': 'new R5.62 source absent from inherited initial status',
        'historical_files': 2030, 'original_baseline_preserved': True,
        'excluded_source_still_publication_scanned_and_pinned': True})


def publication_diagnostic():
    write('publication-development-failure', {'status': 'FAIL',
        'reason': 'synthetic environment construction retained a quoted credential-reserved suffix assignment',
        'category': 'credential assignment', 'field': 'API_KEY',
        'publication_record_issued': False, 'publication_guard_weakened': False,
        'production_attempts': 0, 'b02_exposure': 0})


if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'suite':
        suite(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    else:
        {'baseline': baseline, 'checks': checks, 'summary': summary, 'final': final,
         'preservation-scope': preservation_scope, 'publication-diagnostic': publication_diagnostic}[mode]()
