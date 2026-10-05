"""Focused R5.61 qualification and integrity only; no production entry point."""

import io
import os
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]
from benchmark.evaluation import publication_r5_59 as publication
from benchmark.evaluation import continuity_r5_59 as continuity
from benchmark.evaluation import checkout_r5_52 as checkout
from benchmark.evaluation import restricted_harness_r5_61 as restricted
from benchmark.evaluation.recorder_r5_43 import canonical, digest, loads

OUT = ROOT / 'benchmark/results/phase5c/R5_61-evidence'
SUITES = {
    'capability-guard': 'benchmark.evaluation.test_capability_guard_r5_61',
    'bounded-driver': 'benchmark.evaluation.test_bounded_driver_r5_57',
    'observation-tier2': 'benchmark.evaluation.test_tier2_r5_51',
    'recorder': 'benchmark.harness.test_canonical_evidence_r5_43',
    'authority-synthetic': 'benchmark.evaluation.test_authority_r5_53',
    'continuity': 'benchmark.evaluation.test_continuity_r5_59',
    'publication-security': 'benchmark.evaluation.test_publication_r5_59',
    'schema-traceability': 'benchmark.harness.test_optional_support_r5_41',
}


def write(name, value):
    publication.persist(OUT / (name + '.json'), value)


def read(name):
    return loads((OUT / (name + '.json')).read_bytes())


def baseline():
    assert OUT.parent.is_dir() and not OUT.exists()
    # At this checkpoint only prospective R5.61 files under results may differ.
    changed = subprocess.check_output(['git', 'diff', '--name-only', '--', 'benchmark/results'],
                                      cwd=ROOT, text=True).splitlines()
    assert not changed
    OUT.mkdir()
    names = subprocess.check_output(['git', 'ls-files', 'benchmark/results'], cwd=ROOT, text=True).splitlines()
    write('preservation-baseline', {'files': {n: digest((ROOT / n).read_bytes()) for n in names},
        'initial_status': 'clean before editing', 'historical_results_diff': changed})
    write('development-checks', {'attempts': [
        {'tests': 55, 'errors': 37, 'status': 'FAIL',
         'reason': 'publication guard rejected credential-reserved binding field; no protected access'},
        {'tests': 55, 'passed': 55, 'status': 'PASS',
         'scope': 'intermediate guard/driver witnesses before additional linkage and index tests'}],
        'production_attempts': 0, 'b02_exposure': 0})
    print({'historical_files': len(names)})


def suite(label, tag=None):
    loader = unittest.TestLoader()
    tests = loader.loadTestsFromName(SUITES[label])
    assert not loader.errors
    result = unittest.TextTestRunner(stream=io.StringIO()).run(tests)
    value = {'suite': label, 'discovered': result.testsRun,
             'passed': result.testsRun - len(result.errors) - len(result.failures) - len(result.skipped),
             'errors': [t.id() for t, _ in result.errors], 'failures': [t.id() for t, _ in result.failures],
             'skipped': [t.id() for t, _ in result.skipped], 'successful': result.wasSuccessful(),
             'diagnostics': 'withheld', 'protected_content_used': False}
    if label in ('capability-guard', 'bounded-driver'):
        value['implementation_sha256'] = {name: digest((ROOT / name).read_bytes()) for name in (
            'benchmark/evaluation/capability_guard_r5_61.py',
            'benchmark/evaluation/bounded_driver_r5_57.py',
            'benchmark/evaluation/restricted_harness_r5_61.py',
            'benchmark/evaluation/prohibited_test_index_r5_61.json')}
    write(label + (('-' + tag) if tag else ''), value)
    print(value)
    if not result.wasSuccessful():
        raise SystemExit(1)


def checks():
    from benchmark.results.phase5c.r5_43_qualification import contamination
    from benchmark.harness.test_optional_support_r5_41 import setup
    from benchmark.semantic import profile_audit_r5_41 as audit
    from benchmark.semantic.application_boundary_r5_41 import SCHEMA
    _, spec, state, config = setup()
    configuration = {'transport': spec, 'state': state, 'launch': config}
    reference = 'benchmark/harness/test_optional_support_r5_41.py'
    traces = [{'path': p, 'value': v, 'artifact': reference,
               'sha256': digest((ROOT / reference).read_bytes()), 'clause': 'setup',
               'interpretation': 'Independent generic declared profile; no B02 contents.'}
              for p, v in audit.leaves(configuration)]
    structure = audit.structure(configuration)
    traceability = audit.traceability(configuration, traces, ROOT, {reference})
    assert structure['valid'] and traceability['valid'] and not audit.contamination(configuration)
    assert SCHEMA['core_constructs'] == 30
    # Fresh continuity for unchanged Tier-2/authority/certificate mechanisms.
    tree = checkout.tree(ROOT, 'HEAD')
    names = ('benchmark/evaluation/qualified_authority_r5_55.py',
             'benchmark/evaluation/certificate_r5_55.py', 'benchmark/evaluation/tier2_r5_51.py',
             'benchmark/evaluation/recorder_r5_43.py')
    rows = {}
    for name in names:
        repository = checkout.blobs(ROOT, [tree[name]['blob']])[tree[name]['blob']]
        rows[name] = continuity.verify(repository, (ROOT / name).read_bytes(),
            repository_sha256=digest(repository), kind='utf8-lf-text')
    accounting = restricted.accounting()
    result = unittest.TextTestRunner(stream=io.StringIO()).run(restricted.suite(
        list(restricted.index()['tests']), lambda identity: (_ for _ in ()).throw(AssertionError())))
    assert result.wasSuccessful() and len(result.skipped) == 36
    write('checks', {'structure': structure, 'traceability': traceability,
        'contamination': contamination(), 'core_semantics': 30, 'continuity': rows,
        'safe_skip_accounting': accounting, 'fresh_placeholder_skips': len(result.skipped),
        'prohibited_test_factories_called': 0, 'b02_exposure': 0, 'production_receipts': 0})
    commands = []
    for command in ([sys.executable, '-B', '-m', 'air_compiler.cli', 'validate', 'air/task_manager.json'],
                    [sys.executable, '-B', '-m', 'air_compiler.cli', 'safety', 'air/task_manager.json'],
                    ['git', 'diff', '--check']):
        completed = subprocess.run(command, cwd=ROOT, env={**os.environ, 'PYTHONPATH': 'src'},
                                   capture_output=True, timeout=30)
        commands.append({'command': command, 'exit': completed.returncode, 'diagnostics': 'withheld'})
    write('commands', {'successful': all(c['exit'] == 0 for c in commands), 'commands': commands})
    assert all(c['exit'] == 0 for c in commands)
    print({'checks': 'PASS', 'traceability_leaves': len(traces), 'safe_skips': 36, 'core_semantics': 30})


def summary():
    results = {label: read(label + ('-final' if label in ('capability-guard', 'bounded-driver') else ''))
               for label in SUITES}
    assert all(row['successful'] for row in results.values()) and read('commands')['successful']
    assert read('checks')['core_semantics'] == 30
    write('summary', {'classification': 'R5_61_PROTECTED_RESOURCE_GAP',
        'inherited_r560': 'R5_60_PROTOCOL_HALT', 'capability_model': 'PASS',
        'safe_exclusion_adapter': 'PASS', 'cooperative_python_resource_boundary': 'PASS',
        'production_child_adapter': 'GAP: unmediated subprocess denied before start',
        'complete_production_reconciliation': False,
        'focused_suites': {label: {'discovered': r['discovered'], 'passed': r['passed']}
                           for label, r in results.items()},
        'focused_discovered': sum(r['discovered'] for r in results.values()),
        'focused_passed': sum(r['passed'] for r in results.values()),
        'prohibited_b02_skips': 36, 'b02_exposure': 0,
        'production_b02_accounting': {'reservations': 0, 'dispatches': 0, 'completions': 0},
        'production_synthetic_accounting': {'reservations': 0, 'dispatches': 0, 'completions': 0},
        'production_batches': 0, 'production_receipts': 0, 'production_certificate_issued': False,
        'core_semantics': 30, 'phase5c': 'paused',
        'next': 'qualify mediated execution boundary, then separately authorize wholly fresh production qualification'})
    print({'classification': 'R5_61_PROTECTED_RESOURCE_GAP',
           'focused_passed': sum(r['passed'] for r in results.values())})


def final():
    baseline = read('preservation-baseline')['files']
    assert all(digest((ROOT / n).read_bytes()) == pin for n, pin in baseline.items())
    old = ROOT / 'benchmark/results/phase5c/R5_60-evidence'
    assert loads((old / 'summary.json').read_bytes())['primary_classification'] == 'R5_60_PROTOCOL_HALT'
    assert not list(old.rglob('receipt-*.json'))
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
            diff = subprocess.run(['git', 'diff', '--no-index', '--check', '--', 'NUL', str(path)],
                                  cwd=ROOT, capture_output=True, timeout=10)
            assert diff.returncode in (0, 1) and not diff.stdout
    assert subprocess.run(['git', 'diff', '--check'], cwd=ROOT, capture_output=True).returncode == 0
    write('publication-integrity', {'historical_files_unchanged': len(baseline),
        'r560_halt_preserved': True, 'evidence_sha256': evidence, 'source_sha256': pins,
        'source_dispositions': dispositions, 'git_diff_check': 'PASS', 'new_file_whitespace_check': 'PASS',
        'b02_exposure': 0, 'production_receipts': 0, 'core_semantics': 30})
    print({'publication_integrity': 'PASS', 'historical_files_unchanged': len(baseline)})


def integrity_diagnostic():
    write('integrity-development-failure', {'status': 'FAIL',
        'reason': 'first integrity invocation used classification instead of historical primary_classification',
        'exception_class': 'KeyError', 'publication_record_issued': False,
        'historical_evidence_modified': False, 'production_attempts': 0, 'b02_exposure': 0})


if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'suite':
        suite(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    else:
        {'baseline': baseline, 'checks': checks, 'summary': summary, 'final': final,
         'integrity-diagnostic': integrity_diagnostic}[mode]()
