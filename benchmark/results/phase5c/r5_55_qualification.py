"""Bounded certificate-only qualification. No dispatcher or benchmark subject."""

import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]
from benchmark.evaluation import qualified_authority_r5_55 as authority
from benchmark.evaluation import certificate_r5_55 as certificates
from benchmark.evaluation import security_r5_47 as security
from benchmark.evaluation import tier2_r5_51 as tier
from benchmark.evaluation.recorder_r5_43 import canonical, digest, loads

RESULTS = ROOT / 'benchmark/results/phase5c'
OUT = RESULTS / 'R5_55-qualified-evidence'
WORK = Path('C:/Users/lblan/AppData/Local/Temp/opencode/r555-qualified-certificate-workspace')
CURRENT = '5dd2e7e645c1736f23a80bff755d347da5688cc9e8b7f7df515bd7110d1534ea'


def authorization(root):
    """Explicit owner-authorized current selection, outside certificate schema.

    This is policy construction, never qualification. The independently pinned
    policy digest must be supplied to the verifier; there is no newest discovery.
    """
    prefix = 'benchmark/results/phase5c/'
    manifest = prefix + 'R5_53-authority-successor-v1.json'
    baseline = loads((root / manifest).read_bytes())
    if baseline['identity'] != CURRENT:
        raise ValueError('wrong authorized selection')
    qualification = prefix + 'R5_53-evidence/qualification.json'
    audit = prefix + 'R5_53-evidence/independent-audit.json'
    historical = [prefix + n for n in (
        'R5_51-evidence/summary.json', 'R5_52-inventory-v3.json',
        'R5_53-evidence/historical-lock-status.json', 'R5_54-evidence/summary.json')]
    return {'protocol': authority.POLICY, 'manifest': manifest,
            'authority_identity': CURRENT, 'manifest_sha256': digest((root / manifest).read_bytes()),
            'qualification': qualification, 'qualification_sha256': digest((root / qualification).read_bytes()),
            'audit': audit, 'audit_sha256': digest((root / audit).read_bytes()),
            'decision': 'docs/authority-successor-r5.53.md',
            'adjudication': prefix + 'R5_53-evidence/adjudication.json',
            'predecessor_root': prefix.rstrip('/'),
            'historical_evidence': {n: digest((root / n).read_bytes()) for n in historical},
            'frozen_authority': baseline['frozen_authority'],
            'checkout_policy': authority.REPRESENTATION, 'status': 'QUALIFIED'}


def boundary():
    return {'scopes': {r: [n] for r, n in zip(tier.ROLES, (
        'air/task_manager.json', 'src/air_compiler', 'schema',
        'benchmark/semantic/application_boundary_r5_41.py',
        'benchmark/results/phase5c/R5_53-authority-successor-v1.json',
        'benchmark/evaluation'))}, 'unknown': [],
        'recorder': digest((ROOT / 'benchmark/evaluation/recorder_r5_43.py').read_bytes()),
        'purpose': 'synthetic CertificateV2 eligibility only; no observation'}


def initialize():
    assert OUT.parent.is_dir() and not OUT.exists() and WORK.parent.is_dir() and not WORK.exists()
    OUT.mkdir()
    historical = {p.relative_to(ROOT).as_posix(): digest(p.read_bytes())
                  for p in RESULTS.parent.rglob('*') if p.is_file() and OUT not in p.parents
                  and '__pycache__' not in p.parts and p != Path(__file__)}
    security.persist(OUT / 'initial.json', {'historical': historical})
    security.persist(OUT / 'development-disposition.json', {
        'prior_workspace': 'r555-certificate-workspace', 'prior_evidence': 'R5_55-evidence',
        'qualification_attempt': 'FAIL: secret-publication field-name conflict; no certificate',
        'diagnostic_probe': 'same rejected assembly; no certificate',
        'first_test_run': 'ERROR in setup: fixture restored raw historical evidence as repository text',
        'second_test_run': '30 PASS', 'prior_evidence_reused': False,
        'fresh_workspace_required': True, 'reservations': 0, 'dispatches': 0, 'completions': 0})
    material = tier.Workspace.materialize(ROOT, WORK, boundary()['scopes'])
    security.persist(OUT / 'materialization.json', material)
    policy = authorization(WORK)
    security.persist(OUT / 'authorization.json', policy)
    security.persist(OUT / 'authorization-pin.json', {'identity': digest(canonical(policy)),
                                                    'authority': CURRENT})
    print({'materialized': len(material['files']), 'authorization': digest(canonical(policy))})


def qualify():
    policy = loads((OUT / 'authorization.json').read_bytes())
    pin = loads((OUT / 'authorization-pin.json').read_bytes())['identity']
    qualified = authority.qualify(WORK, policy, trusted_policy_identity=pin)
    capture = lambda: tier.capture(WORK, boundary(), tier.controlled_environment({}, WORK))
    capsule = capture()
    from benchmark.results.phase5c.r5_43_qualification import contamination
    from benchmark.semantic.application_boundary_r5_41 import SCHEMA
    results = {'identity': {'successful': True, 'semantic_count': SCHEMA['core_constructs']},
               'authority': {'successful': True, 'qualified_authority': qualified['identity']},
               'contamination': {'successful': True, 'findings': contamination()['findings']},
               'workspace': {'successful': True, 'dedicated': WORK != ROOT}}
    cert_policy = {'experiment': 'R5.55-synthetic-certificate-only',
                   'stages': {n: digest(canonical({'driver': digest(Path(__file__).read_bytes()), 'stage': n}))
                              for n in results}, 'qualified_authority': qualified['identity'],
                   'authority_role': capsule['roles']['authority'], 'semantic_count': 30,
                   'canonical_protocol': tier.CANONICAL_PROTOCOL, 'recorder': capsule['policy']['recorder'],
                   'observation_state': {'reservations': 0, 'dispatches': 0, 'completions': 0}}
    evidence = {n: tier.receipt(capsule, capture(), cert_policy['experiment'], n,
                              cert_policy['stages'][n], 'PASS', row) for n, row in results.items()}
    cert = certificates.certificate(qualified, capsule, evidence, cert_policy, WORK, policy,
                                    trusted_policy_identity=pin)
    for name, value in {'qualified-authority': qualified, 'capsule': capsule, 'certificate': cert,
                        'certificate-policy': cert_policy, **{'receipt-' + n: v for n, v in evidence.items()}}.items():
        security.persist(OUT / (name + '.json'), value)
    reloaded = loads((OUT / 'certificate.json').read_bytes())
    assert certificates.validate(reloaded, qualified, capsule, evidence, cert_policy, capture(), WORK, policy,
                                 trusted_policy_identity=pin)
    assert cert == certificates.certificate(qualified, capsule, evidence, cert_policy, WORK, policy,
                                            trusted_policy_identity=pin)
    target = WORK / 'air/task_manager.json'
    original = target.read_bytes()
    try:
        target.write_bytes(original + b' ')
        try:
            certificates.validate(cert, qualified, capsule, evidence, cert_policy, capture(), WORK, policy,
                                  trusted_policy_identity=pin)
        except tier.ProtocolFailure:
            rejected = True
        else:
            raise AssertionError('authority mutation accepted')
    finally:
        target.write_bytes(original)
    assert capture() == capsule
    assert certificates.validate(cert, qualified, capsule, evidence, cert_policy, capture(), WORK, policy,
                                 trusted_policy_identity=pin)
    security.persist(OUT / 'synthetic-qualification.json', {
        'status': 'PASS', 'qualified_authority': qualified['identity'], 'certificate': cert['identity'],
        'deterministic': True, 'canonical_round_trip': True, 'mutation_rejected': rejected,
        'restored_synthetic_state': True, 'full_production_qualification': False,
        'reservations': 0, 'dispatches': 0, 'completions': 0, 'b02_exposure': 0, 'core_semantics': 30})
    print({'certificate': cert['identity'], 'synthetic_certificate_qualification': 'PASS'})


def final():
    initial = loads((OUT / 'initial.json').read_bytes())
    assert all(digest((ROOT / n).read_bytes()) == h for n, h in initial['historical'].items())
    artifacts = {}
    for path in OUT.glob('*.json'):
        raw = path.read_bytes()
        value = loads(raw)
        security.safe_bytes(value)
        assert raw == canonical(value) + b'\n'
        artifacts[path.name] = digest(raw)
    security.persist(OUT / 'final-integrity.json', {'historical_files_unchanged': len(initial['historical']),
        'canonical_secret_safe_artifacts': artifacts, 'b02_exposure': 0, 'core_semantics': 30,
        'phase5c': 'paused', 'full_production_qualification': False})
    print({'historical_files_unchanged': len(initial['historical']), 'integrity': 'PASS'})


def regression():
    name = sys.argv[2]
    from benchmark.results.phase5c import r5_51_qualification as previous
    if name in {'authority-focused', 'successor-certificate'}:
        from benchmark.results.phase5c.r5_38_review import run_suite
        pattern = 'test_authority_r5_53.py' if name == 'authority-focused' else 'test_certificate_r5_55.py'
        result = run_suite('benchmark/evaluation', pattern, False)
        result.pop('output')
        result['failures'] = [r['test'] for r in result['failures']]
        result['errors'] = [r['test'] for r in result['errors']]
        security.persist(OUT / (name + '-worker.json'), result)
    else:
        previous.OUTPUT = OUT
        previous.worker(name)
        result = loads((OUT / (name + '-worker.json')).read_bytes())
    print({name: {n: v for n, v in result.items() if n in
                 ('successful', 'discovered', 'passed', 'failures', 'errors', 'semantic_count')}})


if __name__ == '__main__':
    {'initialize': initialize, 'qualify': qualify, 'final': final, 'regression': regression}[sys.argv[1]]()
