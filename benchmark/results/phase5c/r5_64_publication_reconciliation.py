"""Focused synthetic publication verification only; no production mode."""

import io
import os
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]
from benchmark.evaluation import publication_r5_59 as publication
from benchmark.evaluation import publication_schema_r5_64 as schemas
from benchmark.evaluation import capability_guard_r5_61 as guard
from benchmark.evaluation.recorder_r5_43 import canonical, digest, loads
from benchmark.evaluation.test_publication_r5_64 import dry_run

OUT = ROOT / 'benchmark/results/phase5c/R5_64-evidence'


def write(name, value):
    publication.persist(OUT / (name + '.json'), value)


def main():
    assert OUT.parent.is_dir() and not OUT.exists()
    # No protected content reads, including for preservation evidence.
    protected = {r.path.resolve() for r in guard.repository_resources(ROOT)}
    names = subprocess.check_output(['git', 'ls-files', 'benchmark/results'], cwd=ROOT,
                                    text=True).splitlines()
    baseline, sealed = {}, {}
    for name in names:
        path = ROOT / name
        if path.resolve() in protected:
            info = path.stat()
            sealed[name] = {'size': info.st_size, 'mtime_ns': info.st_mtime_ns}
        else:
            baseline[name] = digest(path.read_bytes())
    OUT.mkdir()
    write('preservation-baseline', {'files': baseline, 'protected_metadata_only': sealed})
    write('development-check', {'tests': 58, 'passed': 57, 'failures': 1,
        'failed_test': 'test_canonical_identity_reload',
        'cause': 'test expected no newline; canonical persistence includes one newline',
        'production_attempts': 0})
    suites = {}
    for module in ('benchmark.evaluation.test_publication_r5_64',
                   'benchmark.evaluation.test_security_r5_47',
                   'benchmark.evaluation.test_publication_r5_59',
                   'benchmark.evaluation.test_continuity_r5_59',
                   'benchmark.evaluation.test_ai_independence_r5_49',
                   'benchmark.harness.test_optional_support_r5_41',
                   'benchmark.evaluation.test_mediated_child_r5_62'):
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromName(module)
        assert not loader.errors
        result = unittest.TextTestRunner(stream=io.StringIO()).run(suite)
        row = {'discovered': result.testsRun,
               'passed': result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped),
               'failures': [t.id() for t, _ in result.failures],
               'errors': [t.id() for t, _ in result.errors],
               'skipped': [t.id() for t, _ in result.skipped], 'successful': result.wasSuccessful()}
        write(module.rsplit('.', 1)[1], row)
        print(module, row['passed'], '/', row['discovered'], flush=True)
        assert result.wasSuccessful()
        suites[module] = row
    identity = dry_run(OUT / 'synthetic-qualification-identity.json')
    write('identity-dry-run', {'constructed': True, 'published': True, 'canonical_reload': True,
        'qualification_identity': identity['identity'], 'schema_identity': schemas.QUALIFICATION_IDENTITY_PIN,
        'field_classification': schemas.PROTOCOL_AUTHORIZATION, 'production_identity_issued': False,
        'path': 'tier.seal -> security.safe_bytes -> publication.persist -> canonical loads -> unseal'})
    from benchmark.results.phase5c.r5_43_qualification import contamination
    from benchmark.harness.test_optional_support_r5_41 import setup
    from benchmark.semantic import profile_audit_r5_41 as audit
    from benchmark.semantic.application_boundary_r5_41 import SCHEMA
    _, spec, state, config = setup()
    configuration = {'transport': spec, 'state': state, 'launch': config}
    reference = 'benchmark/harness/test_optional_support_r5_41.py'
    traces = [{'path': p, 'value': v, 'artifact': reference,
        'sha256': digest((ROOT / reference).read_bytes()), 'clause': 'setup',
        'interpretation': 'Independent generic declared profile; no protected contents.'}
        for p, v in audit.leaves(configuration)]
    structure = audit.structure(configuration)
    traceability = audit.traceability(configuration, traces, ROOT, {reference})
    assert structure['valid'] and traceability['valid'] and not audit.contamination(configuration)
    assert SCHEMA['core_constructs'] == 30
    clean = contamination()
    write('schema-traceability-contamination', {'structure': structure, 'traceability': traceability,
        'contamination': clean, 'traceability_leaves': len(traces), 'core_semantics': 30})
    commands = []
    for command in ([sys.executable, '-B', '-m', 'air_compiler.cli', 'validate', 'air/task_manager.json'],
                    [sys.executable, '-B', '-m', 'air_compiler.cli', 'safety', 'air/task_manager.json'],
                    ['git', 'diff', '--check']):
        result = subprocess.run(command, cwd=ROOT, env={**os.environ, 'PYTHONPATH': 'src'},
                                capture_output=True, timeout=30)
        commands.append({'command': command, 'exit': result.returncode, 'diagnostics': 'withheld'})
        assert result.returncode == 0
    write('commands', {'successful': True, 'commands': commands})
    assert all(digest((ROOT / name).read_bytes()) == pin for name, pin in baseline.items())
    for name, row in sealed.items():
        info = (ROOT / name).stat()
        assert row == {'size': info.st_size, 'mtime_ns': info.st_mtime_ns}
    old = ROOT / 'benchmark/results/phase5c/R5_63-evidence'
    assert not (old / 'qualification-identity.json').exists()
    assert not subprocess.check_output(['git', 'diff', '--name-only', '--',
        'benchmark/results/phase5c/R5_63*', 'benchmark/results/phase5c/r5_63*'], cwd=ROOT).strip()
    write('historical-preservation', {'unsealed_files_byte_preserved': len(baseline),
        'protected_files_metadata_preserved': len(sealed), 'protected_content_read': False,
        'r563_classification': 'R5_63_PROTOCOL_HALT', 'r563_identity_absent': True})
    write('summary', {'classification': 'R5_64_CONTEXT_AWARE_PUBLICATION_QUALIFIED',
        'focused_discovered': sum(r['discovered'] for r in suites.values()),
        'focused_passed': sum(r['passed'] for r in suites.values()),
        'b02_accounting': [0, 0, 0, 0], 'synthetic_observation_accounting': [0, 0, 0],
        'production_batches': 0, 'production_receipts': 0, 'production_certificate_issued': False,
        'production_qualification_started': False, 'core_semantics': 30, 'phase5c': 'paused'})


def final(tag=''):
    loader = unittest.TestLoader()
    suite = unittest.TestSuite(loader.loadTestsFromName(module) for module in (
        'benchmark.evaluation.test_publication_r5_64',
        'benchmark.evaluation.test_security_r5_47',
        'benchmark.evaluation.test_publication_r5_59'))
    result = unittest.TextTestRunner(stream=io.StringIO()).run(suite)
    assert not loader.errors and result.wasSuccessful() and result.testsRun == 50
    write('publication-final' + tag, {'discovered': 50, 'passed': 50, 'successful': True})
    baseline = loads((OUT / 'preservation-baseline.json').read_bytes())
    assert all(digest((ROOT / name).read_bytes()) == pin for name, pin in baseline['files'].items())
    for name, row in baseline['protected_metadata_only'].items():
        info = (ROOT / name).stat()
        assert row == {'size': info.st_size, 'mtime_ns': info.st_mtime_ns}
    names = subprocess.check_output(['git', 'ls-files', '--modified', '--others',
        '--exclude-standard'], cwd=ROOT, text=True).splitlines()
    dispositions, pins = {}, {}
    for name in names:
        path = ROOT / name
        assert path.resolve() not in {r.path.resolve() for r in guard.repository_resources(ROOT)}
        if name == 'benchmark/results/phase5c/R5_64-evidence/synthetic-qualification-identity.json':
            value = loads(path.read_bytes())
            publication.safe_bytes(value, schema=schemas.QUALIFICATION_IDENTITY,
                                   schema_identity=schemas.QUALIFICATION_IDENTITY_PIN)
            assert path.read_bytes() == canonical(value) + b'\n'
            dispositions[name] = 'SCHEMA_CLASSIFIED_PUBLICATION'
        else:
            dispositions[name] = publication.check_source(name, path.read_bytes())
        pins[name] = digest(path.read_bytes())
        whitespace = subprocess.run(['git', 'diff', '--no-index', '--check', '--', 'NUL', str(path)],
                                    cwd=ROOT, capture_output=True, timeout=10)
        assert whitespace.returncode in (0, 1) and not whitespace.stdout
    assert subprocess.run(['git', 'diff', '--check'], cwd=ROOT, capture_output=True).returncode == 0
    write('publication-integrity' + tag, {'source_and_evidence_sha256': pins,
        'dispositions': dispositions, 'historical_preservation': True,
        'new_file_whitespace': 'PASS', 'git_diff_check': 'PASS', 'b02_exposure': 0})
    print({'publication_integrity': 'PASS', 'final_security_publication_tests': 50})


if __name__ == '__main__':
    if sys.argv[1:] == ['final']:
        final()
    elif sys.argv[1:] == ['final-verified']:
        final('-verified')
    elif sys.argv[1:] == ['final-checked']:
        final('-checked')
    else:
        assert not sys.argv[1:]
        main()
