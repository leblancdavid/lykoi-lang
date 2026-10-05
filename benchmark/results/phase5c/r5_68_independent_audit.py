"""Separate-process structural audit; does not run a production qualification."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]
from benchmark.results.phase5c import r5_68_qualification as driver
from benchmark.evaluation import certificate_r5_68 as modes
from benchmark.evaluation import sealed_authority_r5_66 as sealed
from benchmark.evaluation import preexposure_r5_45 as envelopes
from benchmark.evaluation.recorder_r5_43 import canonical, digest


def audit():
    summary = driver.read('summary')
    assert summary['classification'] == 'R5_68_PRODUCTION_SEALED_CERTIFICATE_QUALIFIED'
    owner = driver.read('production-declaration')
    cert = driver.read('certificate-candidate')
    qualified = driver.read('sealed-authority')
    capsule = driver.read('capsule')
    policy = driver.read('certificate-policy')
    receipts = driver.read('non-b02-receipts')
    qualification = driver.read('qualification')
    for value in (cert, qualified, capsule, qualification, *receipts.values()):
        envelopes.unseal(value)
    assert digest(canonical(owner)) == driver.TRUSTED_DECLARATION == cert['authorization_binding']
    assert digest(canonical(driver.read('declaration-schema'))) == modes.DECLARATION_SCHEMA_PIN
    assert owner['schema_binding'] == cert['authorization_schema'] == modes.DECLARATION_SCHEMA_PIN
    assert owner['qualification'] == cert['qualification'] == qualification['identity']
    assert owner['experiment'] == policy['experiment'] == qualification['experiment'] == driver.EXPERIMENT
    assert owner['mode'] == cert['mode'] == qualification['mode'] == 'PRODUCTION_SEALED'
    assert owner['scope'] == cert['issuance_scope'] == 'PRODUCTION_SEALED_ONLY'
    assert owner['allowed_operation'] == cert['allowed_operation'] == 'PRODUCTION_GATE_QUALIFIED'
    assert owner['sealed_policy'] == 'CLOSED_NO_OPEN_NO_OBSERVATION'
    assert owner['observation_state'] == 'ZERO_UNOBSERVED'
    assert owner['seal_open_authorized'] is cert['seal_open_authorized'] is False
    assert cert['b02_observation_authorized'] is False
    assert owner['certificate_policy'] == digest(canonical(policy))
    assert cert['policy'] == policy
    assert owner['authority'] == qualified['authority']
    assert owner['resource_policy'] == qualified['policy_binding'] == cert['policy_binding']
    assert owner['qualified_authority'] == cert['qualified_authority'] == qualified['identity']
    assert owner['capsule'] == cert['capsule'] == capsule['identity']
    assert cert['receipts'] == {n: receipts[n]['identity'] for n in sorted(receipts)}
    assert set(receipts) == set(policy['stages']) == modes.v2.REQUIRED
    for name, receipt in receipts.items():
        assert receipt['capsule'] == capsule['identity'] and receipt['experiment'] == driver.EXPERIMENT
        assert receipt['stage'] == name and receipt['mechanism'] == policy['stages'][name]
        assert receipt['status'] == 'PASS' and receipt['result']['successful'] is True
    value, sealed_policy, authority, fresh = driver.actual()
    assert fresh == qualified and sealed_policy == driver.read('sealed-policy')
    assert cert['authority_verification'] == qualified['verification']
    assert len(qualified['verification']) == 11
    assert len(cert['frozen_authority']) == 2
    assert cert['frozen_authority'] == qualified['frozen_authority']
    for name, row in qualified['verification'].items():
        assert row['mode'] == sealed.SEALED and row['seal'] == 'CLOSED'
        assert row['current_content_read'] is False and row['checkout'] == 'DEFERRED_UNTIL_OPEN'
        assert row['commitment'] == value['members'][name]['sha256']
    current = driver.capture()
    assert current == capsule
    binding = {'trusted_declaration_identity': driver.TRUSTED_DECLARATION,
               'mode': modes.PRODUCTION, 'qualification': qualification['identity']}
    assert modes.validate(cert, qualified, capsule, receipts, policy, current, authority, owner, **binding)
    workspace = driver.read('workspace')
    assert workspace['qualified_authority'] == qualified['identity']
    assert receipts['workspace']['result']['workspace'] == workspace['identity']
    assert len(workspace['references']) == 11 and workspace['sealed_materialized'] == 0
    assert workspace['git_database_present'] is False and workspace['dedicated'] is True
    files = {p.relative_to(driver.OUT / 'cooperative-workspace').as_posix()
             for p in (driver.OUT / 'cooperative-workspace').rglob('*') if p.is_file()}
    expected = {'.sealed/' + sealed.identity(r) + '.json' for r in workspace['references']}
    assert files == expected
    assert not any((driver.OUT / n).exists() for n in
                   ('opening.json', 'opening.result.json', 'observation-authorization.json'))
    assert summary['b02_accounting'] == [0, 0, 0, 0]
    for key in ('protected_read_attempts', 'protected_content_reads', 'b02_open_grants', 'b02_openings',
                'opening_ledger_reservations', 'opening_ledger_consumptions', 'full_production_batches',
                'full_production_receipts', 'full_production_certificates'):
        assert summary[key] == 0
    assert summary['core_semantics'] == 30 and cert['semantic_count'] == 30
    assert summary['full_production_qualification_started'] is False
    assert summary['future_observation_authorization_created'] is False
    preservation = driver.preserve()
    assert not driver.ATTEMPTS
    driver.write('independent-audit', {'status': 'PASS', 'canonical_bindings': 'PASS',
        'actual_sealed_metadata': 'PASS', 'sealed_members': 11, 'sealed_frozen_pins': 2,
        'candidate_linkage': 'PASS', 'workspace_metadata_only': 'PASS',
        'certificate_mode': 'PRODUCTION_SEALED', 'separate_observation_grant_created': False,
        'opening_ledger_unchanged': True, 'b02_accounting': [0, 0, 0, 0],
        'protected_read_attempts': 0, 'protected_content_reads': 0, 'core_semantics': 30,
        'historical_preservation': preservation, 'full_production_gate_qualified': False})
    print({'independent_audit': 'PASS', 'protected_read_attempts': 0})


if __name__ == '__main__':
    audit()
