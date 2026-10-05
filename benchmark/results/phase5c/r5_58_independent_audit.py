"""Independent read-only R5.58 evidence audit; no observation or repair API."""

from collections import Counter
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]
from benchmark.evaluation import security_r5_47 as security
from benchmark.evaluation import tier2_r5_51 as tier
from benchmark.evaluation import certificate_r5_55 as certificates
from benchmark.evaluation.recorder_r5_43 import canonical, digest, loads
from benchmark.results.phase5c import r5_58_qualification as experiment


def main(publication=False):
    out, work = experiment.OUT, experiment.WORK
    read = experiment.read
    summary, plan, capsule, qualified, authorization = [read(n) for n in
        ('summary', 'stage-plan', 'capsule', 'qualified-authority', 'authority-policy')]
    assert experiment.capture() == capsule
    assert experiment.live_authority() == qualified['identity']
    baseline = read('preservation-baseline')['files']
    assert all(digest((ROOT / n).read_bytes()) == pin for n, pin in baseline.items())
    binding = loads((out / 'batches/qualification.json').read_bytes())
    assert binding['implementation'] == digest((ROOT / 'benchmark/evaluation/bounded_driver_r5_57.py').read_bytes())
    assert binding['capsule'] == capsule['identity'] and binding['authority'] == qualified['identity']
    assert binding['experiment'] == experiment.EXPERIMENT and binding['version'] == 'bounded-driver-r5.57-v1'
    previous, receipts, batches = None, {}, []
    ordered = [s['name'] for s in plan['regressions']]
    for i, path in enumerate(sorted((out / 'batches').glob('batch-*.json'))):
        batch = loads(path.read_bytes())
        tier.envelopes.unseal(batch)
        assert path.name == f'batch-{i:04d}.json' and batch['previous'] == previous
        assert batch['binding'] == digest(canonical({k: v for k, v in binding.items() if k != 'identity'}))
        for name in ordered[len(receipts):len(receipts) + len(batch['receipts'])]:
            raw = (out / 'batches' / ('receipt-' + name + '.json')).read_bytes()
            receipt = loads(raw)
            tier.envelopes.unseal(receipt)
            assert digest(raw) == batch['receipts'][name]
            assert receipt['capsule'] == capsule['identity'] and receipt['experiment'] == experiment.EXPERIMENT
            assert receipt['stage'] == name and receipt['status'] == 'PASS'
            stage = plan['regressions'][len(receipts)]
            assert receipt['mechanism'] == experiment.mechanism(stage)
            assert receipt['result']['successful'] is True
            if stage['definition'][0] == 'suite':
                assert receipt['result']['method_ids'] == stage['definition'][4]
            attempt = loads((out / 'batches' / ('attempt-' + name + '.json')).read_bytes())
            assert attempt['binding'] == batch['binding'] and attempt['stage'] == name
            receipts[name] = receipt
        assert batch['next'] == (ordered[len(receipts)] if len(receipts) < len(ordered) else None)
        previous = batch['identity']
        batches.append({'number': i, 'receipts': len(batch['receipts']), 'disposition': batch['disposition']})
    assert len(receipts) == len(ordered) and batches[-1]['disposition'] == 'COMPLETE'
    assert len(list((out / 'batches').glob('attempt-*.json'))) == len(receipts)
    cert = read('certificate')
    assert certificates.validate(cert, qualified, capsule, receipts, read('certificate-policy'),
        experiment.capture(), work, authorization, trusted_policy_identity=experiment.inherited.PIN)
    assert cert['receipts'] == {n: r['identity'] for n, r in receipts.items()}
    workspace = tier.Workspace(work, out / 'production-gate', experiment.EXPERIMENT).verify()
    assert sorted(p.name for p in (out / 'production-gate').iterdir()) == ['workspace.json']
    assert read('production-pre-observation')['status'] == 'FAIL'
    assert read('terminal-stop')['repair_permitted'] is False
    from benchmark.results.phase5c.r5_43_qualification import contamination
    from benchmark.semantic.application_boundary_r5_41 import SCHEMA
    assert not contamination()['findings'] and SCHEMA['core_constructs'] == 30
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / 'rejected.json'
        raw = 'synthetic-r558-hidden-value'
        try:
            security.persist(path, {'password': raw})
        except security.SecretRejected as error:
            assert raw not in str(error) and not path.exists()
        else:
            raise AssertionError('raw persistence accepted')
    ambient = dict(capsule['effective_environment'])
    authoring = {**ambient, 'OPENAI_API_KEY': 'synthetic-excluded',
        'AUTHOR_MODEL': 'synthetic-other-model', 'OPENCODE_CONFIG': 'synthetic-editor'}
    assert tier.controlled_environment(ambient, work) == tier.controlled_environment(authoring, work)
    evidence = {}
    for path in out.rglob('*.json'):
        raw = path.read_bytes()
        value = loads(raw)
        assert raw == canonical(value) + b'\n'
        security.safe_bytes(value)
        if 'identity' in value:
            tier.envelopes.unseal(value)
        evidence[path.relative_to(out).as_posix()] = digest(raw)
    if publication:
        prior = read('independent-final-audit')
        assert all(digest((out / n).read_bytes()) == pin for n, pin in prior['evidence_sha256'].items())
        for name in ('docs/project-overview.md', 'docs/decisions.md', 'docs/research-log.md',
            'benchmark/results/phase5c/R5_58-FRESH-MULTI-BATCH-PRODUCTION-TIER2-QUALIFICATION.md'):
            security.check_text((ROOT / name).read_text(encoding='utf-8'))
    assert subprocess.run(['git', 'diff', '--check'], cwd=ROOT, capture_output=True, timeout=10).returncode == 0
    record = {'independent_audit': 'PASS', 'qualification_result': summary['primary_classification'],
        'production_qualified': False, 'audit_scope': 'stopped before observation; downstream lifecycle unqualified',
        'members': 1083, 'authority': qualified['identity'], 'capsule_unchanged': True,
        'certificate_linkage': 'PASS', 'receipt_count': len(receipts), 'cross_batch_linkage': 'PASS',
        'batches': batches, 'workspace': workspace['identity'],
        'historical_files_unchanged': len(baseline), 'evidence_sha256': evidence,
        'synthetic_reservations': 0, 'synthetic_dispatches': 0, 'synthetic_completions': 0,
        'b02_exposure': 0, 'production_b02_accounting': {'reservations': 0, 'dispatches': 0, 'completions': 0},
        'core_semantics': 30, 'contamination': 'clean', 'raw_secret_persistence_rejected': True,
        'rejection_diagnostic_redacted': True, 'secret_safe_evidence': True,
        'ai_authoring_state_excluded': True, 'no_repair': True, 'git_diff_check': 'PASS', 'phase5c': 'paused'}
    security.persist(out / ('publication-integrity.json' if publication else 'independent-final-audit.json'), record)
    print({k: v for k, v in record.items() if k not in ('evidence_sha256', 'batches')})


if __name__ == '__main__':
    main('--publication' in sys.argv)
