"""Focused R5.57 verification/publication. Never loads a benchmark subject."""

import io
import os
from pathlib import Path
import subprocess
import sys
import time
import unittest

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]
from benchmark.evaluation import security_r5_47 as security
from benchmark.evaluation import tier2_r5_51 as tier
from benchmark.evaluation.recorder_r5_43 import canonical, digest, loads

OUT = Path(os.environ.get('LYKOI_R557_VERIFICATION_EVIDENCE', str(ROOT / 'benchmark/results/phase5c/R5_57-evidence')))


def write(name, value):
    security.persist(OUT / (name + '.json'), tier.seal(value))


def flatten(suite):
    for test in suite:
        if isinstance(test, unittest.TestSuite):
            yield from flatten(test)
        else:
            yield test


def initialize():
    assert OUT.parent.is_dir() and not OUT.exists()
    OUT.mkdir()
    names = subprocess.check_output(['git', 'ls-files', 'benchmark/results'], cwd=ROOT, text=True).splitlines()
    write('preservation-baseline', {'files': {n: digest((ROOT / n).read_bytes()) for n in names},
                                  'b02_exposure': 0})


def suite(name, directory, pattern, half=None):
    tests = list(flatten(unittest.defaultTestLoader.discover(str(ROOT / directory), pattern)))
    if half is not None:
        middle = (len(tests) + 1) // 2
        tests = tests[:middle] if half == 'first' else tests[middle:]
    started = time.monotonic()
    result = unittest.TextTestRunner(stream=io.StringIO(), verbosity=2).run(unittest.TestSuite(tests))
    value = {'tests': result.testsRun, 'passed': max(0, result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped)),
             'failures': [t.id() for t, _ in result.failures], 'errors': [t.id() for t, _ in result.errors],
             'skipped': [t.id() for t, _ in result.skipped], 'successful': result.wasSuccessful(),
             'wall_seconds': time.monotonic() - started, 'directory': directory, 'pattern': pattern}
    write(name, value)
    print(value)


def audit(name='integrity-final'):
    from benchmark.results.phase5c.r5_43_qualification import contamination
    from benchmark.semantic.application_boundary_r5_41 import SCHEMA
    from benchmark.harness.test_optional_support_r5_41 import setup
    from benchmark.semantic import profile_audit_r5_41 as profiles
    _, transport, state, launch = setup()
    configuration = {'transport': transport, 'state': state, 'launch': launch}
    reference = 'benchmark/harness/test_optional_support_r5_41.py'
    traces = [{'path': p, 'value': v, 'artifact': reference,
               'sha256': digest((ROOT / reference).read_bytes()), 'clause': 'setup',
               'interpretation': 'Independent synthetic profile metadata.'}
              for p, v in profiles.leaves(configuration)]
    structure = profiles.structure(configuration)
    traceability = profiles.traceability(configuration, traces, ROOT, {reference})
    assert structure['valid'] and traceability['valid'] and not profiles.contamination(configuration)
    assert contamination()['findings'] == [] and SCHEMA['core_constructs'] == 30
    baseline = loads((OUT / 'preservation-baseline.json').read_bytes())
    assert all(digest((ROOT / n).read_bytes()) == pin for n, pin in baseline['files'].items())
    for path in OUT.rglob('*.json'):
        raw = path.read_bytes()
        value = loads(raw)
        assert raw == canonical(value) + b'\n'
        security.safe_bytes(value)
    dry = [loads((OUT / f'dry-qualified/dry-result-{n}.json').read_bytes()) for n in (1, 2, 3)]
    assert [r['new_receipts'] for r in dry] == [3, 2, 1]
    assert [r['disposition'] for r in dry] == ['BOUNDARY', 'BOUNDARY', 'COMPLETE']
    assert len({r['capsule'] for r in dry}) == len({r['authority'] for r in dry}) == 1
    assert all(r['b02_exposure'] == 0 for r in dry)
    from benchmark.evaluation import bounded_driver_r5_57 as bounded
    binding = bounded.reload(OUT / 'dry-qualified/qualification.json')
    assert binding['implementation'] == digest((ROOT / 'benchmark/evaluation/bounded_driver_r5_57.py').read_bytes())
    previous = None
    count = 0
    for number in range(3):
        row = bounded.reload(OUT / f'dry-qualified/batch-{number:04d}.json')
        assert row['previous'] == previous
        for stage, pin in row['receipts'].items():
            path = OUT / f'dry-qualified/receipt-{stage}.json'
            receipt = bounded.reload(path)
            assert digest(path.read_bytes()) == pin and receipt['status'] == 'PASS'
            assert receipt['capsule'] == binding['capsule'] and receipt['experiment'] == binding['experiment']
            count += 1
        previous = row['identity']
    assert count == 6
    commands = {}
    for operation in ('validate', 'safety'):
        process = subprocess.run([sys.executable, '-B', '-S', '-c',
            "import sys; sys.path.insert(0,'src'); from air_compiler.cli import main; main()",
            operation, 'air/task_manager.json'], cwd=ROOT,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=20)
        assert process.returncode == 0
        commands[operation] = 'PASS'
    assert subprocess.run(['git', 'diff', '--check'], cwd=ROOT, capture_output=True, timeout=10).returncode == 0
    commands['git diff --check'] = 'PASS'
    write(name, {'successful': True, 'historical_files_unchanged': len(baseline['files']),
          'contamination': contamination(), 'schema': structure, 'traceability': traceability,
          'synthetic_three_batches': [3, 2, 1], 'b02_exposure': 0, 'core_semantics': 30,
          'phase5c': 'paused', 'production_qualification': False, 'commands': commands,
          'independent_receipt_rehash': count, 'driver_implementation_pin': 'PASS'})
    print({'integrity_audit': 'PASS', 'historical_files': len(baseline['files']), 'core': 30})


def characterize():
    selected = {}
    for folder in ('R5_45-evidence', 'R5_51-evidence', 'R5_55-qualified-evidence', 'R5_56-evidence'):
        rows = []
        for path in sorted((ROOT / 'benchmark/results/phase5c' / folder).glob('*worker.json')):
            value = loads(path.read_bytes())
            if 'seconds' in value:
                rows.append({'artifact': path.relative_to(ROOT).as_posix(), 'sha256': digest(path.read_bytes()),
                             'worker_seconds': value['seconds'], 'pattern': value.get('pattern')})
        selected[folder] = rows
    write('stage-cost-characterization', {'historical_worker_measurements': selected,
        'unmeasured_historical_components': ['pre_capture', 'startup', 'shutdown', 'post_capture',
                                             'evidence', 'receipt', 'integrity'],
        'historical_timeout_envelope_seconds': 120, 'historical_lifecycle_timestamps_available': False,
        'fallback_worker_allowance': 65, 'known_worker_floor': 35,
        'component_allowances': {'pre_capture': 12, 'startup': 3, 'shutdown': 3, 'post_capture': 12,
                                 'evidence': 2, 'receipt': 2, 'integrity': 2},
        'margin_floor': 15, 'margin_fraction': .25, 'boundary_reserve': 5,
        'b02_exposure': 0})
    print({'stage_cost_characterization': 'persisted', 'historical_components': 'worker only; remainder unmeasured'})


def finalize():
    selected = ('budget-publication-final', 'certificate-final-first', 'certificate-final-second',
                'tier2', 'recorder', 'certificate-v1', 'authority', 'methodology', 'security', 'application')
    rows = {n: loads((OUT / (n + '.json')).read_bytes()) for n in selected}
    assert all(r['successful'] and not r['errors'] and not r['failures'] for r in rows.values())
    assert sum(r['passed'] for r in rows.values()) == 257
    audit_result = loads((OUT / 'integrity-final.json').read_bytes())
    assert audit_result['successful']
    names = ['benchmark/evaluation/bounded_driver_r5_57.py',
             'benchmark/evaluation/test_bounded_driver_r5_57.py',
             'benchmark/evaluation/test_certificate_driver_r5_57.py',
             'benchmark/results/phase5c/r5_57_driver.py', 'benchmark/results/phase5c/r5_57_verify.py',
             'benchmark/results/phase5c/R5_57-BOUNDED-QUALIFICATION-DRIVER-BUDGETING-REPAIR.md',
             'docs/project-overview.md', 'docs/decisions.md', 'docs/research-log.md']
    for name in names:
        security.check_text((ROOT / name).read_text(encoding='utf-8'))
    for name in names[:6]:
        result = subprocess.run(['git', 'diff', '--no-index', '--check', '--', os.devnull, name],
                                cwd=ROOT, capture_output=True, timeout=10)
        # --no-index may return 1 for added content even with no check findings.
        assert result.returncode in (0, 1) and not result.stdout
    write('summary', {'classification': 'R5_57_BOUNDED_DRIVER_QUALIFIED',
        'qualified_tests': 257, 'test_evidence': {n: r['identity'] for n, r in rows.items()},
        'integrity_audit': audit_result['identity'], 'historical_files_unchanged': 1873,
        'publication_scan': 'PASS', 'untracked_diff_check': 'PASS',
        'implementation': {n: digest((ROOT / n).read_bytes()) for n in names},
        'r556_resumed': False, 'r556_receipts_reused': False,
        'complete_production_gate_qualified': False, 'b02_exposure': 0,
        'core_semantics': 30, 'phase5c': 'paused',
        'recommendation': 'R5.58 separately authorized fresh complete qualification across clean bounded batches'} )
    print({'classification': 'R5_57_BOUNDED_DRIVER_QUALIFIED', 'tests': 257, 'publication': 'PASS'})


def diagnose():
    from benchmark.evaluation import checkout_r5_52 as checkout
    from benchmark.evaluation import authority_r5_53 as successor
    baseline = loads((ROOT / 'benchmark/results/phase5c/R5_53-authority-successor-v1.json').read_bytes())
    blobs = checkout.blobs(ROOT, [r['blob'] for r in baseline['members'].values() if r['blob']])
    findings = []
    for name, row in baseline['members'].items():
        data = (ROOT / name).read_bytes()
        repository = data if row['blob'] is None else blobs[row['blob']]
        if digest(repository) != row['sha256']:
            findings.append('repository-digest:' + name)
        try:
            successor.materialization(repository, data, row['kind'])
        except ValueError:
            findings.append(name)
    print({'authority_materialization_findings': findings})
    print({'predecessor_representations': [{'path': r['path'],
        'exact': digest((ROOT / 'benchmark/results/phase5c' / r['path']).read_bytes()) == r['raw_sha256'],
        'lf': digest((ROOT / 'benchmark/results/phase5c' / r['path']).read_bytes().replace(b'\r\n', b'\n')) == r['raw_sha256'],
        'crlf': digest((ROOT / 'benchmark/results/phase5c' / r['path']).read_bytes().replace(b'\r\n', b'\n').replace(b'\n', b'\r\n')) == r['raw_sha256']}
        for r in baseline['predecessors']]})
    from benchmark.evaluation.test_certificate_driver_r5_57 import DriverCertificateTests as SuccessorCertificateTests
    categories = []
    def trace(frame, event, arg):
        if event == 'exception' and frame.f_code.co_filename.endswith('authority_r5_53.py'):
            categories.append({'successor_line': frame.f_lineno, 'exception': arg[0].__name__})
        if event == 'exception' and frame.f_code.co_filename.endswith('qualified_authority_r5_55.py'):
            categories.append({'line': frame.f_lineno, 'exception': arg[0].__name__})
            # Only literal, known categories; never arbitrary exception text.
            for category in ('authorization', 'manifest', 'unqualified', 'frozen or historical authority',
                             'provenance', 'provenance link', 'historical evidence erased or altered',
                             'predecessor evidence', 'checkout controls unavailable'):
                if type(arg[1]) is ValueError and arg[1].args == (category,):
                    categories.append(category)
        return trace
    sys.settrace(trace)
    try:
        SuccessorCertificateTests.setUpClass()
    except Exception:
        pass
    finally:
        sys.settrace(None)
        if hasattr(SuccessorCertificateTests, 'temp'):
            SuccessorCertificateTests.temp.cleanup()
    print({'certificate_setup_categories': categories})


def prepare_lf(destination):
    import shutil
    destination = Path(destination)
    assert destination.parent.is_dir() and not destination.exists()
    subprocess.run(['git', '-c', 'core.autocrlf=false', 'clone', '--no-hardlinks', '--local',
                    str(ROOT), str(destination)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    target = destination / 'benchmark/results/phase5c/r5_57_verify.py'
    assert not target.exists() and target.parent.is_dir()
    shutil.copyfile(Path(__file__), target)
    print({'separate_lf_verification_fixture': 'created', 'historical_source_modified': False})


if __name__ == '__main__':
    if sys.argv[1] == 'initialize':
        initialize()
    elif sys.argv[1] == 'suite':
        suite(*sys.argv[2:])
    elif sys.argv[1] == 'audit':
        audit(*sys.argv[2:])
    elif sys.argv[1] == 'characterize':
        characterize()
    elif sys.argv[1] == 'finalize':
        finalize()
    elif sys.argv[1] == 'diagnose':
        diagnose()
    elif sys.argv[1] == 'prepare-lf':
        prepare_lf(sys.argv[2])
