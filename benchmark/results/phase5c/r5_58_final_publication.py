"""Final stopped evidence integrity; retains the failed independent source scan."""

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]
from benchmark.evaluation import security_r5_47 as security
from benchmark.evaluation import tier2_r5_51 as tier
from benchmark.evaluation.recorder_r5_43 import canonical, digest, loads


def main():
    out = ROOT / 'benchmark/results/phase5c/R5_58-evidence'
    baseline = loads((out / 'preservation-baseline.json').read_bytes())['files']
    assert all(digest((ROOT / n).read_bytes()) == pin for n, pin in baseline.items())
    assert not Path('C:/Users/lblan/AppData/Local/Temp/opencode/r558-production-workspace').exists()
    assert not list(out.rglob('receipt-*.json')) and not list(out.rglob('reservation-*'))
    assert not (out / 'capsule.json').exists() and not (out / 'certificate.json').exists()
    artifacts = {}
    for path in out.rglob('*.json'):
        raw = path.read_bytes()
        value = loads(raw)
        assert raw == canonical(value) + b'\n'
        security.safe_bytes(value)
        if 'identity' in value:
            tier.envelopes.unseal(value)
        artifacts[path.relative_to(out).as_posix()] = digest(raw)
    from benchmark.results.phase5c.r5_43_qualification import contamination
    from benchmark.semantic.application_boundary_r5_41 import SCHEMA
    assert not contamination()['findings'] and SCHEMA['core_constructs'] == 30
    prose = {}
    for name in ('docs/project-overview.md', 'docs/decisions.md', 'docs/research-log.md',
        'benchmark/results/phase5c/R5_58-FRESH-MULTI-BATCH-PRODUCTION-TIER2-QUALIFICATION.md'):
        security.check_text((ROOT / name).read_text(encoding='utf-8'))
        prose[name] = digest((ROOT / name).read_bytes())
    # Re-observe the failed scan read-only; never change its failing input.
    path = ROOT / 'benchmark/results/phase5c/r5_58_stopped_audit.py'
    try:
        security.check_text(path.read_text(encoding='utf-8'))
    except security.SecretRejected:
        scan = 'FAIL: synthetic credential assignment in stopped-audit source'
    else:
        raise AssertionError('recorded failed source scan no longer reproduces')
    assert subprocess.run(['git', 'diff', '--check'], cwd=ROOT, capture_output=True, timeout=10).returncode == 0
    result = tier.seal({'qualification_result': 'R5_58_PROTOCOL_HALT',
        'evidence_prose_integrity': 'PASS', 'independent_final_audit': 'FAIL',
        'failed_audit_component': scan, 'audit_failure_preserved': True,
        'candidate_resumed': False, 'candidate_repaired': False,
        'historical_files_unchanged': len(baseline), 'evidence_sha256': artifacts,
        'prose_sha256': prose, 'contamination': 'clean', 'semantic_count': 30,
        'bounded_batches': 0, 'production_receipts': 0,
        'production_certificate_issued': False, 'workspace_materialized': False,
        'synthetic_reservations': 0, 'synthetic_dispatches': 0, 'synthetic_completions': 0,
        'b02_exposure': 0, 'production_b02_accounting': {'reservations': 0, 'dispatches': 0, 'completions': 0},
        'git_diff_check': 'PASS', 'phase5c': 'paused'})
    security.persist(out / 'final-publication-integrity.json', result)
    print({k: v for k, v in result.items() if k not in ('evidence_sha256', 'prose_sha256')})


if __name__ == '__main__':
    main()
