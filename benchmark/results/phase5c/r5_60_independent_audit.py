"""Independent stopped-candidate audit; no dispatch, retry or repair entry point."""

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]
from benchmark.evaluation import publication_r5_59 as publication
from benchmark.evaluation import tier2_r5_51 as tier
from benchmark.evaluation import qualified_authority_r5_55 as authority
from benchmark.evaluation import certificate_r5_55 as certificates
from benchmark.evaluation.recorder_r5_43 import canonical, digest, loads
from benchmark.results.phase5c import r5_60_qualification as experiment


def main():
    out, work = experiment.OUT, experiment.WORK
    read = experiment.read
    summary, plan, identity = [read(n) for n in ('summary', 'stage-plan', 'qualification-identity')]
    tier.envelopes.unseal(plan)
    tier.envelopes.unseal(identity)
    assert identity['plan'] == plan['identity'] == summary['plan']
    assert identity['identity'] == summary['qualification']
    assert identity['orchestration'] == digest((ROOT / experiment.DRIVER).read_bytes())
    baseline = read('preservation-baseline')['files']
    assert all(digest((ROOT / n).read_bytes()) == pin for n, pin in baseline.items())
    linkage, previous, receipts, journals = 'NOT_REACHED', None, {}, []
    if (out / 'batches/qualification.json').exists():
        binding = loads((out / 'batches/qualification.json').read_bytes())
        tier.envelopes.unseal(binding)
        assert binding['experiment'] == experiment.EXPERIMENT
        assert binding['version'] == experiment.bounded.VERSION
        assert binding['implementation'] == identity['driver_implementation']
        capsule, qualified, policy = [read(n) for n in ('capsule', 'qualified-authority', 'authority-policy')]
        assert experiment.capture() == capsule
        assert authority.qualify(work, policy, trusted_policy_identity=experiment.prior.inherited.PIN) == qualified
        assert binding['capsule'] == capsule['identity'] and binding['authority'] == qualified['identity']
        ordered = [s['name'] for s in plan['regressions']]
        stopped = False
        for i, path in enumerate(sorted((out / 'batches').glob('batch-*.json'))):
            row = loads(path.read_bytes())
            tier.envelopes.unseal(row)
            assert not stopped and path.name == f'batch-{i:04d}.json'
            assert row['previous'] == previous
            assert row['binding'] == digest(canonical({k: v for k, v in binding.items() if k != 'identity'}))
            for n in ordered[len(receipts):len(receipts) + len(row['receipts'])]:
                raw = (out / 'batches' / ('receipt-' + n + '.json')).read_bytes()
                receipt = loads(raw)
                tier.envelopes.unseal(receipt)
                assert digest(raw) == row['receipts'][n]
                assert receipt['stage'] == n and receipt['experiment'] == experiment.EXPERIMENT
                assert receipt['capsule'] == capsule['identity']
                assert receipt['mechanism'] == experiment.mechanism(plan['regressions'][len(receipts)])
                attempt = loads((out / 'batches' / ('attempt-' + n + '.json')).read_bytes())
                tier.envelopes.unseal(attempt)
                assert attempt['binding'] == row['binding'] and attempt['stage'] == n
                if receipt['status'] == 'PASS':
                    assert receipt['result']['successful'] is True
                receipts[n] = receipt
            assert row['next'] == (ordered[len(receipts)] if len(receipts) < len(ordered) else None)
            previous, stopped = row['identity'], row['disposition'] == 'STOPPED'
            journals.append({'number': i, 'receipts': len(row['receipts']), 'disposition': row['disposition']})
        assert {n: r['identity'] for n, r in receipts.items()} == summary['receipts']
        assert len(list((out / 'batches').glob('attempt-*.json'))) == len(receipts)
        if summary['production_certificate_issued']:
            assert certificates.validate(read('certificate'), qualified, capsule, receipts,
                read('certificate-policy'), experiment.capture(), work, policy,
                trusted_policy_identity=experiment.prior.inherited.PIN)
        linkage = 'PASS'
    assert summary['b02_exposure'] == 0
    assert summary['production_b02_accounting'] == {'reservations': 0, 'dispatches': 0, 'completions': 0}
    assert summary['synthetic_reservations'] == summary['synthetic_dispatches'] == summary['synthetic_completions'] == 0
    assert sorted(p.name for p in (out / 'production-gate').glob('*')) in ([], ['workspace.json'])
    from benchmark.results.phase5c.r5_43_qualification import contamination
    from benchmark.semantic.application_boundary_r5_41 import SCHEMA
    assert not contamination()['findings'] and SCHEMA['core_constructs'] == 30
    evidence = {}
    for path in out.rglob('*.json'):
        raw = path.read_bytes()
        value = loads(raw)
        assert raw == canonical(value) + b'\n'
        publication.safe_bytes(value)
        if 'identity' in value:
            tier.envelopes.unseal(value)
        evidence[path.relative_to(out).as_posix()] = digest(raw)
    names = subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard', '--modified'],
                                     cwd=ROOT, text=True).splitlines()
    sources = {}
    for n in sorted(set(names)):
        path = ROOT / n
        if path.suffix in ('.py', '.md', '.txt', '.json'):
            sources[n] = publication.check_source(n, path.read_bytes())
            result = subprocess.run(['git', 'diff', '--no-index', '--check', '--', 'NUL', str(path)],
                                    cwd=ROOT, capture_output=True, timeout=10)
            assert result.returncode in (0, 1) and not result.stdout
    assert subprocess.run(['git', 'diff', '--check'], cwd=ROOT, capture_output=True, timeout=10).returncode == 0
    record = {'independent_audit': 'PASS', 'audit_scope': 'stopped-candidate integrity; not production qualification',
        'qualification_result': summary['primary_classification'], 'production_qualified': False,
        'plan_unchanged': True, 'cross_batch_linkage': linkage, 'receipt_count': len(receipts),
        'batches': journals, 'historical_files_unchanged': len(baseline),
        'evidence_sha256': evidence, 'source_dispositions': sources,
        'publication': 'PASS', 'contamination': 'clean', 'core_semantics': 30,
        'b02_exposure': 0, 'production_b02_accounting': summary['production_b02_accounting'],
        'synthetic_reservations': 0, 'synthetic_dispatches': 0, 'synthetic_completions': 0,
        'no_repair': True, 'git_diff_check': 'PASS', 'phase5c': 'paused'}
    publication.persist(out / 'independent-final-audit.json', record)
    print({k: v for k, v in record.items() if k not in ('evidence_sha256', 'source_dispositions', 'batches')})


if __name__ == '__main__':
    main()
