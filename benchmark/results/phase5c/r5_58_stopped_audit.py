"""Stopped-candidate recording and independent publication audit; no stage runner."""

from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]
from benchmark.evaluation import security_r5_47 as security
from benchmark.evaluation import tier2_r5_51 as tier
from benchmark.evaluation.recorder_r5_43 import canonical, digest, loads

OUT = ROOT / 'benchmark/results/phase5c/R5_58-evidence'
WORK = Path('C:/Users/lblan/AppData/Local/Temp/opencode/r558-production-workspace')
CLASSIFICATION = 'R5_58_PROTOCOL_HALT'


def read(path):
    raw = path.read_bytes()
    value = loads(raw)
    assert raw == canonical(value) + b'\n'
    security.safe_bytes(value)
    return value


def write(name, value):
    security.persist(OUT / (name + '.json'), tier.seal(value))


def record():
    plan = read(OUT / 'stage-plan.json')
    snapshot = loads((ROOT / 'benchmark/results/phase5c/R5_55-qualified-evidence/materialization.json').read_bytes())
    names = ('benchmark/evaluation/qualified_authority_r5_55.py',
        'benchmark/evaluation/certificate_r5_55.py', 'benchmark/evaluation/tier2_r5_51.py',
        'benchmark/evaluation/test_reproducibility_boundary_r5_50.py')
    rows = {}
    for name in names:
        raw = (ROOT / name).read_bytes()
        expected = snapshot['files'][name]['sha256']
        row = {'current_sha256': digest(raw), 'r555_snapshot_sha256': expected,
            'exact': digest(raw) == expected,
            'lf_sha256': digest(raw.replace(b'\r\n', b'\n')),
            'crlf_sha256': digest(raw.replace(b'\r\n', b'\n').replace(b'\n', b'\r\n'))}
        row['representation_only_witness'] = expected in (row['lf_sha256'], row['crlf_sha256'])
        rows[name] = row
    assert any(not row['exact'] for row in rows.values())
    assert not WORK.exists() and not (OUT / 'batches').exists()
    candidate = tier.seal({'experiment': plan['experiment'], 'stage_plan': plan['identity'],
        'driver_version': 'bounded-driver-r5.57-v1',
        'driver_implementation': digest((ROOT / 'benchmark/evaluation/bounded_driver_r5_57.py').read_bytes()),
        'orchestration': digest((ROOT / 'benchmark/results/phase5c/r5_58_qualification.py').read_bytes()),
        'authority_selection': '5dd2e7e645c1736f23a80bff755d347da5688cc9e8b7f7df515bd7110d1534ea',
        'status': 'STOPPED_BEFORE_QUALIFIED_STATE', 'fresh_capsule_issued': False})
    security.persist(OUT / 'qualification-candidate.json', candidate)
    write('starting-state-failure', {'status': 'FAIL', 'classification': CLASSIFICATION,
        'component': 'r5_58_qualification.initialize: implementation continuity raw-byte assertion',
        'inherited_check': 'r5_56_qualification.initialize: R5.55 materialization physical hashes',
        'mechanisms': rows, 'qualified_authority_instantiated': False,
        'capsule_captured': False, 'workspace_materialized': False,
        'production_regression_observed': False,
        'interpretation': 'failed starting-state physical continuity prerequisite; representation diagnostics do not convert FAIL to PASS',
        'repair_permitted': False, 'retry_permitted': False})
    write('summary', {'primary_classification': CLASSIFICATION, 'candidate': candidate['identity'],
        'stage_plan': plan['identity'], 'starting_state': 'FAIL',
        'required_regression_stages': len(plan['regressions']),
        'stages': {s['name']: 'NOT_STARTED' for s in plan['regressions']},
        'integration': {s['name']: 'NOT_REACHED' for s in plan['integration']},
        'bounded_batches': 0, 'production_receipts': 0, 'incomplete_admitted_stages': 0,
        'production_certificate_issued': False, 'production_qualified': False,
        'synthetic_reservations': 0, 'synthetic_dispatches': 0, 'synthetic_completions': 0,
        'b02_exposure': 0, 'production_b02_accounting': {'reservations': 0, 'dispatches': 0, 'completions': 0},
        'core_semantics': 30, 'phase5c': 'paused', 'repair_permitted': False, 'retry_permitted': False})
    print({'classification': CLASSIFICATION, 'mechanism_continuity': rows, 'candidate': candidate['identity']})


def audit(publication=False):
    summary = read(OUT / 'summary.json')
    failure = read(OUT / 'starting-state-failure.json')
    plan = read(OUT / 'stage-plan.json')
    candidate = read(OUT / 'qualification-candidate.json')
    assert summary['primary_classification'] == CLASSIFICATION
    assert candidate['stage_plan'] == plan['identity'] and candidate['status'] == 'STOPPED_BEFORE_QUALIFIED_STATE'
    assert failure['status'] == 'FAIL' and failure['retry_permitted'] is False
    assert not WORK.exists() and not (OUT / 'batches').exists()
    assert not list(OUT.rglob('receipt-*.json')) and not list(OUT.rglob('reservation-*'))
    assert not (OUT / 'certificate.json').exists() and not (OUT / 'capsule.json').exists()
    baseline = read(OUT / 'preservation-baseline.json')['files']
    assert all(digest((ROOT / n).read_bytes()) == pin for n, pin in baseline.items())
    from benchmark.results.phase5c.r5_43_qualification import contamination
    from benchmark.semantic.application_boundary_r5_41 import SCHEMA
    assert not contamination()['findings'] and SCHEMA['core_constructs'] == 30
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / 'rejected.json'
        hidden = 'synthetic-r558-stopped-private-value'
        try:
            security.persist(path, {'password': hidden})
        except security.SecretRejected as error:
            assert hidden not in str(error) and not path.exists()
        else:
            raise AssertionError('raw persistence accepted')
    ambient = {'PYTHONDONTWRITEBYTECODE': '1'}
    authoring = {**ambient, 'OPENAI_API_KEY': 'synthetic-excluded',
        'AUTHOR_MODEL': 'synthetic-other-model', 'OPENCODE_CONFIG': 'synthetic-editor'}
    assert tier.controlled_environment(ambient, ROOT) == tier.controlled_environment(authoring, ROOT)
    evidence = {}
    for path in OUT.rglob('*.json'):
        value = read(path)
        if 'identity' in value:
            tier.envelopes.unseal(value)
        evidence[path.relative_to(OUT).as_posix()] = digest(path.read_bytes())
    prose = {}
    if publication:
        prior = read(OUT / 'independent-stopped-audit.json')
        assert all(digest((OUT / n).read_bytes()) == pin for n, pin in prior['evidence_sha256'].items())
        for name in ('docs/project-overview.md', 'docs/decisions.md', 'docs/research-log.md',
            'benchmark/results/phase5c/R5_58-FRESH-MULTI-BATCH-PRODUCTION-TIER2-QUALIFICATION.md'):
            security.check_text((ROOT / name).read_text(encoding='utf-8'))
            prose[name] = digest((ROOT / name).read_bytes())
    assert subprocess.run(['git', 'diff', '--check'], cwd=ROOT, capture_output=True, timeout=10).returncode == 0
    scripts = ('r5_58_qualification.py', 'r5_58_independent_audit.py', 'r5_58_stopped_audit.py')
    for script in scripts:
        path = ROOT / 'benchmark/results/phase5c' / script
        security.check_text(path.read_text(encoding='utf-8'))
        process = subprocess.run(['git', 'diff', '--no-index', '--check', '--', 'NUL', str(path)],
            cwd=ROOT, capture_output=True, timeout=10)
        assert process.returncode in (0, 1) and not process.stdout
    record = {'independent_stopped_audit': 'PASS', 'qualification_result': CLASSIFICATION,
        'audit_scope': 'stopped starting-state candidate; does not qualify unrun production gates',
        'historical_files_unchanged': len(baseline), 'evidence_sha256': evidence,
        'prose_sha256': prose, 'stage_plan': plan['identity'], 'candidate': candidate['identity'],
        'bounded_batches': 0, 'production_receipts': 0, 'production_certificate_issued': False,
        'workspace_materialized': False, 'no_repair': True, 'no_retry': True,
        'synthetic_reservations': 0, 'synthetic_dispatches': 0, 'synthetic_completions': 0,
        'b02_exposure': 0, 'production_b02_accounting': {'reservations': 0, 'dispatches': 0, 'completions': 0},
        'semantic_count': 30, 'contamination': 'clean', 'secret_safe_evidence': True,
        'raw_secret_persistence_rejected': True, 'redacted_diagnostic': True,
        'ai_authoring_environment_excluded': True, 'full_ai_regression': 'NOT_STARTED',
        'full_security_regression': 'NOT_STARTED', 'git_diff_check': 'PASS', 'phase5c': 'paused'}
    write('publication-integrity' if publication else 'independent-stopped-audit', record)
    print({k: v for k, v in record.items() if k not in ('evidence_sha256', 'prose_sha256')})


if __name__ == '__main__':
    if sys.argv[1] == 'record':
        record()
    else:
        audit(sys.argv[1] == 'publication')
