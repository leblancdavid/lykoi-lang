"""Review-artifact integrity only; no benchmark authority evaluation."""

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from benchmark.evaluation.recorder_r5_43 import canonical, digest, loads
from benchmark.evaluation.security_r5_47 import persist


def main():
    directory = Path(__file__).parent
    evidence = []
    for name in ('R5_50-validation.json', 'R5_50-validation-focused.json'):
        path = directory / name
        raw = path.read_bytes()
        value = loads(raw)
        assert raw == canonical(value) + b'\n'
        assert value['mechanisms_before'] == value['mechanisms_after']
        assert value['b02_exposure'] == 0 and value['core_semantics'] == 30
        assert value['production_capsule_qualified'] is False
        evidence.append(value)
    initial, focused = evidence
    assert initial['status'] == 'FAIL'
    assert sum(row['tests'] for row in initial['suites']) == 107
    assert sum(len(row['passed']) for row in initial['suites']) == 104
    assert focused['status'] == 'PASS'
    assert sum(row['tests'] for row in focused['suites']) == 105
    assert sum(len(row['passed']) for row in focused['suites']) == 105
    assert len(focused['excluded_historical_checks']) == 2
    for row in focused['suites']:
        assert row['status'] == 'PASS'
        assert not row['failed'] and not row['errors'] and not row['skipped']
    for name, expected in focused['mechanisms_after'].items():
        assert digest((ROOT / name).read_bytes()) == expected
    permitted = {'docs/project-overview.md', 'docs/research-log.md',
                 'docs/decisions.md', 'benchmark/README.md'}
    changed = subprocess.check_output(['git', 'diff', 'HEAD', '--name-only'],
                                      cwd=ROOT, text=True).splitlines()
    assert set(changed) <= permitted, 'Unexpected tracked modification'
    whitespace = subprocess.run(['git', 'diff', '--check'], cwd=ROOT,
                                capture_output=True)
    assert whitespace.returncode == 0, 'Whitespace check failed'
    artifacts = list(directory.glob('R5_50-*.md')) + list(directory.glob('R5_50-validation*.json'))
    artifacts += [directory / 'r5_50_review.py', Path(__file__),
                  ROOT / 'benchmark/evaluation/test_reproducibility_boundary_r5_50.py']
    artifacts += [ROOT / name for name in sorted(permitted)]
    persist(directory / 'R5_50-final-integrity.json', {
        'protocol': 'lykoi-r5.50-review-integrity-v1', 'status': 'PASS',
        'scope': 'methodology artifacts; no production qualification or historical lock replay',
        'focused_mechanisms_unchanged': True,
        'tracked_changes': changed, 'git_diff_check_exit': whitespace.returncode,
        'initial_tests': 107, 'initial_passes': 104,
        'focused_tests': 105, 'focused_passes': 105,
        'artifacts': {path.relative_to(ROOT).as_posix(): digest(path.read_bytes())
                      for path in artifacts},
        'b02_exposure': 0, 'core_semantics': 30,
    })
    print('R5.50 review integrity: PASS; focused 105/105; initial FAIL preserved')


if __name__ == '__main__':
    main()
