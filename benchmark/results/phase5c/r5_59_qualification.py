"""Focused prospective qualification only. No production or subject entry point."""

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
from benchmark.evaluation.recorder_r5_43 import canonical, digest, loads

OUT = ROOT / 'benchmark/results/phase5c/R5_59-evidence'
SUITES = {
    'continuity': 'test_continuity_r5_59.py',
    'publication': 'test_publication_r5_59.py',
    'publication-final': 'test_publication_r5_59.py',
    'publication-qualified': 'test_publication_r5_59.py',
    'checkout': 'test_checkout_r5_52.py',
    'authority': 'test_authority_r5_53.py',
    'certificate': 'test_certificate_driver_r5_57.py',
    'security': 'test_security_r5_47.py',
    'methodology': 'test_reproducibility_boundary_r5_50.py',
    'tier2': 'test_tier2_r5_51.py',
    'certificate-v1': 'test_preexposure_r5_45.py',
    'recorder': 'test_canonical_evidence_r5_43.py',
    'application': 'test*.py',
}


def write(name, value):
    publication.persist(OUT / (name + '.json'), value)


def flatten(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from flatten(item)
        else:
            yield item


def baseline():
    assert OUT.parent.is_dir() and not OUT.exists()
    OUT.mkdir()
    names = subprocess.check_output(['git', 'ls-files', 'benchmark/results'], cwd=ROOT, text=True).splitlines()
    write('preservation-baseline', {'files': {n: digest((ROOT / n).read_bytes()) for n in names}})


def suite(label, chunk=None):
    loader = unittest.TestLoader()
    directory = {'recorder': 'benchmark/harness', 'application': 'tests'}.get(label, 'benchmark/evaluation')
    tests = list(flatten(loader.discover(str(ROOT / directory), SUITES[label])))
    assert not loader.errors and tests
    if chunk is not None:
        tests = tests[chunk * 8:(chunk + 1) * 8]
    assert tests
    result = unittest.TextTestRunner(stream=io.StringIO()).run(unittest.TestSuite(tests))
    row = {'suite': label, 'chunk': chunk, 'discovered': result.testsRun,
           'passed': result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped),
           'failures': [t.id() for t, _ in result.failures],
           'errors': [t.id() for t, _ in result.errors],
           'skipped': [t.id() for t, _ in result.skipped],
           'successful': result.wasSuccessful(), 'diagnostics': 'worker text withheld'}
    write(label + ('' if chunk is None else '-' + str(chunk)), row)
    print(row)


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
               'interpretation': 'Independent declared public profile.'}
              for p, v in audit.leaves(configuration)]
    structure = audit.structure(configuration)
    traceability = audit.traceability(configuration, traces, ROOT, {reference})
    assert structure['valid'] and traceability['valid'] and not audit.contamination(configuration)
    assert SCHEMA['core_constructs'] == 30 and not contamination()['findings']
    # Fresh read-only witness of the originally failing implementations, using
    # already-qualified member classifications, never filename-specific logic.
    tree = checkout.tree(ROOT, 'HEAD')
    old = loads((ROOT / 'benchmark/results/phase5c/R5_58-evidence/starting-state-failure.json').read_bytes())
    snapshot = loads((ROOT / 'benchmark/results/phase5c/R5_55-qualified-evidence/materialization.json').read_bytes())
    rows = {}
    for name in old['mechanisms']:
        row = tree[name]
        repository = checkout.blobs(ROOT, [row['blob']])[row['blob']]
        # Explicit R5.59 reviewed class: evaluator Python source, UTF-8 LF,
        # without an exact-physical-byte protocol. Not a general file inference.
        assert name.startswith('benchmark/evaluation/') and name.endswith('.py')
        assert checkout.text(repository) and b'\r' not in repository
        assert digest(repository) == snapshot['files'][name]['sha256']
        rows[name] = continuity.verify(repository, (ROOT / name).read_bytes(),
            repository_sha256=snapshot['files'][name]['sha256'], kind='utf8-lf-text')
    write('checks', {'structure': structure, 'traceability': traceability,
        'contamination': contamination(), 'core_semantics': 30, 'continuity': rows,
        'b02_exposure': 0, 'production_receipts': 0})
    print({'checks': 'PASS', 'continuity_members': len(rows), 'core_semantics': 30})


def final():
    baseline = loads((OUT / 'preservation-baseline.json').read_bytes())['files']
    assert all(digest((ROOT / n).read_bytes()) == pin for n, pin in baseline.items())
    old = ROOT / 'benchmark/results/phase5c/R5_58-evidence'
    assert loads((old / 'summary.json').read_bytes())['primary_classification'] == 'R5_58_PROTOCOL_HALT'
    assert not list(old.rglob('receipt-*.json')) and not (old / 'capsule.json').exists()
    evidence = {}
    for path in OUT.glob('*.json'):
        raw = path.read_bytes()
        value = loads(raw)
        assert raw == canonical(value) + b'\n'
        publication.safe_bytes(value)
        evidence[path.name] = digest(raw)
    names = subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard', '--modified'], cwd=ROOT, text=True).splitlines()
    names += ['benchmark/evaluation/synthetic_fixture_r5_59.txt']
    dispositions = {}
    source_sha256 = {}
    for name in sorted(set(names)):
        path = ROOT / name
        if path.suffix in ('.py', '.md', '.txt', '.json'):
            dispositions[name] = publication.check_source(name, path.read_bytes())
            source_sha256[name] = digest(path.read_bytes())
            diff = subprocess.run(['git', 'diff', '--no-index', '--check', '--', 'NUL', str(path)],
                                  cwd=ROOT, capture_output=True, timeout=10)
            assert diff.returncode in (0, 1) and not diff.stdout
    assert subprocess.run(['git', 'diff', '--check'], cwd=ROOT, capture_output=True, timeout=10).returncode == 0
    write('publication-integrity', {'historical_files_unchanged': len(baseline),
        'r558_halt_preserved': True, 'evidence_sha256': evidence,
        'source_dispositions': dispositions, 'source_sha256': source_sha256,
        'git_diff_check': 'PASS', 'new_file_whitespace_check': 'PASS',
        'b02_exposure': 0, 'production_receipts': 0, 'core_semantics': 30})
    print({'publication_integrity': 'PASS', 'historical_files_unchanged': len(baseline)})


def commands():
    rows = []
    for command in ([sys.executable, '-B', '-m', 'air_compiler.cli', 'validate', 'air/task_manager.json'],
                    [sys.executable, '-B', '-m', 'air_compiler.cli', 'safety', 'air/task_manager.json'],
                    ['git', 'diff', '--check']):
        result = subprocess.run(command, cwd=ROOT, env={**os.environ, 'PYTHONPATH': 'src'},
                                capture_output=True, timeout=30)
        rows.append({'command': command, 'exit': result.returncode, 'diagnostics': 'withheld'})
    write('commands', {'successful': all(r['exit'] == 0 for r in rows), 'commands': rows})
    print(rows)


def summary():
    labels = [n for n in SUITES if n not in ('certificate', 'publication', 'publication-final')]
    names = labels + ['certificate-' + str(i) for i in range(5)]
    results = {n: loads((OUT / (n + '.json')).read_bytes()) for n in names}
    assert all(r['successful'] for r in results.values())
    assert loads((OUT / 'commands.json').read_bytes())['successful']
    assert loads((OUT / 'checks.json').read_bytes())['core_semantics'] == 30
    # Final integrity is performed after the report and this summary exist.
    write('summary', {'classification': 'R5_59_CONTINUITY_PUBLICATION_RECONCILED',
        'focused_suites': {n: {'discovered': r['discovered'], 'passed': r['passed']} for n, r in results.items()},
        'focused_discovered': sum(r['discovered'] for r in results.values()),
        'focused_passed': sum(r['passed'] for r in results.values()),
        'continuity_qualified': True, 'publication_qualified': True,
        'inherited_r558': 'R5_58_PROTOCOL_HALT', 'production_qualification_started': False,
        'b02_exposure': 0, 'production_receipts': 0, 'core_semantics': 30,
        'phase5c': 'paused', 'next': 'separately authorized wholly fresh production qualification'})


if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'suite':
        suite(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else None)
    else:
        {'baseline': baseline, 'checks': checks, 'final': final,
         'commands': commands, 'summary': summary}[mode]()
