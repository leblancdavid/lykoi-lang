"""Read-only independent R5.56 audit; no certificate constructor or dispatch."""

from collections import Counter
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]
from benchmark.evaluation.recorder_r5_43 import canonical, digest, loads
from benchmark.evaluation import security_r5_47 as security
from benchmark.evaluation import tier2_r5_51 as tier
from benchmark.evaluation.security_r5_47 import persist, safe_bytes
from benchmark.results.phase5c.r5_56_qualification import OUT, WORK, PIN, CURRENT, capture


def read(name):
    raw = (OUT / (name + '.json')).read_bytes()
    value = loads(raw)
    assert raw == canonical(value) + b'\n'
    safe_bytes(value)
    if value.get('kind') in {'capsule', 'qualified-authority', 'certificate', 'receipt'}:
        assert digest(canonical({k: v for k, v in value.items() if k != 'identity'})) == value['identity']
    return value


def main():
    policy = read('authority-policy')
    assert digest(canonical(policy)) == PIN
    raw = (WORK / policy['manifest']).read_bytes()
    baseline = loads(raw)
    assert digest(raw) == policy['manifest_sha256']
    assert baseline['identity'] == CURRENT
    assert digest(canonical({k: v for k, v in baseline.items() if k != 'identity'})) == CURRENT
    relations = Counter()
    # Independent Git batch reads avoid thousands of process starts.
    ids = sorted({r['blob'] for r in baseline['members'].values() if r['blob']})
    data = subprocess.run(['git', '--no-replace-objects', 'cat-file', '--batch'], cwd=WORK,
                          input=('\n'.join(ids) + '\n').encode(), capture_output=True,
                          timeout=30, check=True).stdout
    blobs, offset = {}, 0
    for oid in ids:
        end = data.index(b'\n', offset)
        header = data[offset:end].decode().split()
        assert header[0] == oid and header[1] == 'blob'
        size = int(header[2])
        blobs[oid] = data[end + 1:end + 1 + size]
        offset = end + 2 + size
    assert offset == len(data)
    for name, row in baseline['members'].items():
        physical = (WORK / name).read_bytes()
        repository = physical if row['blob'] is None else blobs[row['blob']]
        assert digest(repository) == row['sha256']
        if physical == repository:
            relations['EXACT'] += 1
        else:
            assert row['kind'] == 'utf8-lf-text' and b'\r' not in repository and b'\0' not in repository
            repository.decode('utf-8')
            assert physical.replace(b'\r\n', b'\n') == repository
            relations['LF_CRLF_REPRESENTATION'] += 1
    assert len(baseline['members']) == 1083
    for name, pin in policy['frozen_authority'].items():
        assert baseline['members'][name]['sha256'] == pin
    for name, expected in ((policy['qualification'], policy['qualification_sha256']),
                           (policy['audit'], policy['audit_sha256'])):
        assert digest((WORK / name).read_bytes()) == expected
    for previous in baseline['predecessors']:
        raw = (WORK / policy['predecessor_root'] / previous['path']).read_bytes()
        assert digest(raw) == previous['raw_sha256']
        assert previous['historical_physical_status'] == 'FAIL'
        assert subprocess.run(['git', '--no-replace-objects', 'merge-base', '--is-ancestor',
            loads(raw)['head'], baseline['head']], cwd=WORK, capture_output=True, timeout=10).returncode == 0
    assert all(digest((WORK / n).read_bytes()) == h for n, h in policy['historical_evidence'].items())
    capsule, qualified, summary = [read(n) for n in ('capsule', 'qualified-authority', 'summary')]
    assert capture() == capsule
    for name, row in capsule['repository'].items():
        if row['physical'] is not None:
            assert digest((WORK / name).read_bytes()) == row['physical']['sha256']
    evidence = {}
    for name in read('definitions'):
        if (OUT / ('receipt-' + name + '.json')).exists():
            row = read('receipt-' + name)
            assert row['capsule'] == capsule['identity']
            evidence[name] = row
    if summary['production_certificate_issued']:
        cert, experiment = read('certificate'), read('certificate-policy')
        assert cert['version'] == 2 and cert['capsule'] == capsule['identity']
        assert cert['qualified_authority'] == qualified['identity']
        assert cert['policy_binding'] == PIN and cert['frozen_authority'] == policy['frozen_authority']
        assert cert['semantic_count'] == 30 and cert['contamination'] == 'clean'
        assert set(cert['receipts']) == set(evidence) == set(experiment['stages'])
        for name, row in evidence.items():
            assert cert['receipts'][name] == row['identity']
            assert row['status'] == 'PASS' and row['result']['successful'] is True
            assert row['experiment'] == experiment['experiment']
            assert row['stage'] == name and row['mechanism'] == experiment['stages'][name]
        assert cert['observation_state'] == {'reservations': 0, 'dispatches': 0, 'completions': 0}
    gate = OUT / 'production-gate'
    assert sorted(p.name for p in gate.iterdir()) == ['workspace.json']
    assert not list(gate.glob('reservation-*')) and not list(gate.glob('observation-*'))
    assert read('terminal-stop')['repair_permitted'] is False
    from benchmark.results.phase5c.r5_43_qualification import contamination
    from benchmark.semantic.application_boundary_r5_41 import SCHEMA
    assert contamination()['findings'] == [] and SCHEMA['core_constructs'] == 30
    # Independent final-publication probe is not a replacement for the unrun
    # required security suite. Synthetic raw values never enter persisted output.
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / 'rejected.json'
        raw_value = 'synthetic-r556-hidden-value'
        try:
            security.persist(path, {'password': raw_value})
        except security.SecretRejected as error:
            assert raw_value not in str(error) and not path.exists()
        else:
            raise AssertionError('raw-secret persistence accepted')
    ambient = dict(capsule['effective_environment'])
    modified = {**ambient, 'OPENAI_API_KEY': 'synthetic-r556-excluded',
                'AUTHOR_MODEL': 'synthetic-other-model', 'OPENCODE_CONFIG': 'synthetic-editor'}
    assert tier.controlled_environment(ambient, WORK) == tier.controlled_environment(modified, WORK)
    initial = read('initial')
    assert all(digest((ROOT / n).read_bytes()) == h for n, h in initial['historical'].items())
    artifacts = {}
    for path in OUT.rglob('*.json'):
        raw = path.read_bytes()
        value = loads(raw)
        assert raw == canonical(value) + b'\n'
        safe_bytes(value)
        artifacts[path.relative_to(OUT).as_posix()] = digest(raw)
    assert subprocess.run(['git', 'diff', '--check'], cwd=ROOT, capture_output=True, timeout=10).returncode == 0
    record = {'independent_audit': 'PASS', 'qualification_result': summary['primary_classification'],
        'production_qualified': False, 'authority': CURRENT, 'members': 1083,
        'checkout_relationships': dict(relations), 'capsule_unchanged': True,
        'receipt_count': len(evidence), 'production_certificate_issued': summary['production_certificate_issued'],
        'historical_files_unchanged': len(initial['historical']), 'evidence_sha256': artifacts,
        'synthetic_reservations': 0, 'synthetic_dispatches': 0, 'synthetic_completions': 0,
        'b02_exposure': 0, 'production_b02_accounting': {'reservations': 0, 'dispatches': 0, 'completions': 0},
        'core_semantics': 30, 'contamination': 'clean', 'secret_safe_structured_evidence': True,
        'raw_secret_persistence_rejected': True, 'rejection_diagnostic_redacted': True,
        'ai_authoring_state_excluded_from_effective_environment': True,
        'required_security_suite': summary['stages']['security-r547'],
        'git_diff_check': 'PASS', 'phase5c': 'paused',
        'audit_boundary': 'stopped candidate; no successful synthetic lifecycle or full production qualification claimed'}
    persist(OUT / 'independent-final-audit.json', record)
    print({k: v for k, v in record.items() if k != 'evidence_sha256'})


def publication():
    """Final read-only linkage/preservation check after report publication."""
    audit = read('independent-final-audit')
    assert all(digest((OUT / n).read_bytes()) == h for n, h in audit['evidence_sha256'].items())
    initial, summary, definitions = [read(n) for n in ('initial', 'summary', 'definitions')]
    assert all(digest((ROOT / n).read_bytes()) == h for n, h in initial['historical'].items())
    driver = digest((WORK / 'benchmark/results/phase5c/r5_56_qualification.py').read_bytes())
    statuses = Counter()
    for name, definition in definitions.items():
        row = read('receipt-' + name)
        assert row['experiment'] == 'R5.56-fresh-complete-production-tier2-qualification-v1'
        assert row['stage'] == name and row['capsule'] == summary['capsule']
        assert row['mechanism'] == digest(canonical({'driver': driver, 'definition': definition, 'stage': name}))
        assert row['status'] == summary['stages'][name]
        assert row['result']['successful'] is (row['status'] == 'PASS')
        statuses[row['status']] += 1
    assert statuses == {'PASS': 5, 'INCOMPLETE': 75}
    assert capture()['identity'] == summary['capsule']
    assert sorted(p.name for p in (OUT / 'production-gate').iterdir()) == ['workspace.json']
    prose = ('docs/project-overview.md', 'docs/decisions.md', 'docs/research-log.md',
             'benchmark/results/phase5c/R5_56-FRESH-COMPLETE-PRODUCTION-TIER2-QUALIFICATION.md')
    assert subprocess.run(['git', 'diff', '--check'], cwd=ROOT, capture_output=True, timeout=10).returncode == 0
    result = {'status': 'PASS', 'receipt_linkage': dict(statuses),
              'historical_files_unchanged': len(initial['historical']),
              'prior_audit': digest((OUT / 'independent-final-audit.json').read_bytes()),
              'auditor': digest(Path(__file__).read_bytes()),
              'new_prose': {n: digest((ROOT / n).read_bytes()) for n in prose},
              'capsule_unchanged': True, 'git_diff_check': 'PASS', 'b02_exposure': 0,
              'production_certificate_issued': False, 'synthetic_observations': 0,
              'production_qualified': False}
    persist(OUT / 'final-publication-audit.json', result)
    print(result)


if __name__ == '__main__':
    publication() if '--publication' in sys.argv else main()
