"""Independent read-only evidence/content checks; no certificate constructor."""

from collections import Counter
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]
from benchmark.evaluation.recorder_r5_43 import canonical, digest, loads
from benchmark.evaluation.security_r5_47 import persist, safe_bytes
from benchmark.results.phase5c.r5_55_qualification import OUT, WORK, CURRENT


def read(name):
    raw = (OUT / (name + '.json')).read_bytes()
    value = loads(raw)
    assert raw == canonical(value) + b'\n'
    safe_bytes(value)
    if value.get('kind') in {'qualified-authority', 'capsule', 'certificate', 'receipt'}:
        assert digest(canonical({k: v for k, v in value.items() if k != 'identity'})) == value['identity']
    return value


def main():
    policy = read('authorization')
    assert digest(canonical(policy)) == read('authorization-pin')['identity']
    baseline_raw = (WORK / policy['manifest']).read_bytes()
    baseline = loads(baseline_raw)
    assert baseline_raw == canonical(baseline) + b'\n'
    assert digest(baseline_raw) == policy['manifest_sha256']
    assert baseline['identity'] == CURRENT
    assert digest(canonical({k: v for k, v in baseline.items() if k != 'identity'})) == CURRENT
    relations = Counter()
    for name, row in baseline['members'].items():
        physical = (WORK / name).read_bytes()
        repository = physical if row['blob'] is None else subprocess.check_output(
            ['git', '--no-replace-objects', 'cat-file', 'blob', row['blob']], cwd=WORK, timeout=10)
        assert digest(repository) == row['sha256']
        if physical == repository:
            relations['EXACT'] += 1
        else:
            assert row['kind'] == 'utf8-lf-text' and b'\r' not in repository and b'\0' not in repository
            repository.decode('utf-8')
            assert physical.replace(b'\r\n', b'\n') == repository
            relations['LF_CRLF_REPRESENTATION'] += 1
    assert baseline['frozen_authority'] == policy['frozen_authority']
    for name, expected in ((policy['qualification'], policy['qualification_sha256']),
                           (policy['audit'], policy['audit_sha256'])):
        assert digest((WORK / name).read_bytes()) == expected
    for previous in baseline['predecessors']:
        raw = (WORK / policy['predecessor_root'] / previous['path']).read_bytes()
        assert digest(raw) == previous['raw_sha256']
        assert previous['historical_physical_status'] == 'FAIL'
        assert subprocess.run(['git', '--no-replace-objects', 'merge-base', '--is-ancestor',
                               loads(raw)['head'], baseline['head']], cwd=WORK,
                              capture_output=True, timeout=10).returncode == 0
    for name, pin in policy['frozen_authority'].items():
        assert baseline['members'][name]['sha256'] == pin
    assert all(digest((WORK / n).read_bytes()) == h for n, h in policy['historical_evidence'].items())
    qualified, capsule, certificate, experiment = [read(n) for n in
        ('qualified-authority', 'capsule', 'certificate', 'certificate-policy')]
    assert qualified['authority'] == CURRENT and qualified['status'] == 'QUALIFIED'
    assert certificate['qualified_authority'] == qualified['identity']
    assert certificate['capsule'] == capsule['identity']
    assert certificate['frozen_authority'] == policy['frozen_authority']
    assert certificate['semantic_count'] == 30 and certificate['version'] == 2
    assert certificate['contamination'] == 'clean'
    assert certificate['observation_state'] == {'reservations': 0, 'dispatches': 0, 'completions': 0}
    for name, row in capsule['repository'].items():
        if row['physical'] is not None:
            assert digest((WORK / name).read_bytes()) == row['physical']['sha256']
    for name, mechanism in experiment['stages'].items():
        receipt = read('receipt-' + name)
        assert receipt['identity'] == certificate['receipts'][name]
        assert receipt['capsule'] == capsule['identity'] and receipt['experiment'] == experiment['experiment']
        assert receipt['mechanism'] == mechanism and receipt['status'] == 'PASS'
        assert receipt['result']['successful'] is True
    assert read('synthetic-qualification')['mutation_rejected'] is True
    initial = read('initial')
    assert all(digest((ROOT / n).read_bytes()) == h for n, h in initial['historical'].items())
    assert subprocess.run(['git', 'diff', '--check'], cwd=ROOT, capture_output=True, timeout=10).returncode == 0
    record = {'independent_audit': 'PASS', 'authority': CURRENT,
              'auditor_development_correction': 'initial audit treated external policy pin as self-sealed envelope; corrected typed interpretation',
              'members': len(baseline['members']), 'checkout_relationships': dict(relations),
              'certificate': certificate['identity'], 'historical_files_unchanged': len(initial['historical']),
              'b02_exposure': 0, 'core_semantics': 30, 'phase5c': 'paused',
              'production_observations': 0, 'full_production_qualification': False,
              'git_diff_check': 'PASS',
              'new_prose': {n: digest((ROOT / n).read_bytes()) for n in (
                  'docs/qualified-authority-certificate-r5.55.md', 'docs/project-overview.md',
                  'docs/decisions.md', 'docs/research-log.md',
                  'benchmark/results/phase5c/R5_55-SUCCESSOR-AWARE-PRODUCTION-CERTIFICATE-AND-LIVE-AUTHORITY-ADAPTER.md')}}
    persist(OUT / 'independent-final-audit.json', record)
    print(record)


if __name__ == '__main__':
    main()
