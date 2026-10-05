"""Read-only independent R5.66 evidence reconciliation; no production API."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]
from benchmark.results.phase5c import r5_66_qualification as driver
from benchmark.results.phase5c.r5_66_inventory import inventory
from benchmark.evaluation import sealed_authority_r5_66 as sealed
from benchmark.evaluation import preexposure_r5_45 as envelopes
from benchmark.evaluation import publication_r5_59 as publication
from benchmark.evaluation.recorder_r5_43 import canonical, digest, loads


def read(name):
    raw = (driver.OUT / (name + '.json')).read_bytes()
    value = loads(raw)
    assert raw == canonical(value) + b'\n'
    publication.safe_bytes(value)
    return value


def audit():
    summary = read('summary-final-mechanism')
    assert summary['classification'] == 'R5_66_SEALED_AUTHORITY_QUALIFIED'
    assert summary['focused_tests'] == summary['focused_passed'] == 185
    assert summary['b02_accounting'] == [0, 0, 0, 0]
    assert summary['production_batches'] == summary['production_receipts'] == summary['production_certificates'] == 0
    assert summary['core_semantics'] == 30 and not summary['production_qualification_started']
    value = inventory()
    assert value == read('sealed-inventory')
    derived = read('derived-sealed-policy')
    policy = derived['policy']
    assert policy['members'] == value['members']
    assert len(policy['members']) == 11 and len(policy['frozen_authority']) == 2
    auth = sealed.Authority(ROOT, policy, trusted_policy_identity=derived['derived_policy_identity'],
                            observer=sealed.GitMetadata(ROOT))
    qualified = read('sealed-authority')
    assert auth.qualify() == qualified
    envelopes.unseal(qualified)
    assert all(r['mode'] == sealed.SEALED and r['seal'] == 'CLOSED' and not r['current_content_read']
               for r in qualified['verification'].values())
    lifecycle = read('synthetic-lifecycle-final-mechanism')
    assert lifecycle['synthetic_openings'] == 1 and lifecycle['second_open_rejected']
    opening, result = read('synthetic-opening-final-mechanism'), read('synthetic-opening-final-mechanism.result')
    assert opening['state'] == 'RESERVED' and result['state'] == 'OPENED'
    assert opening['grant'] == result['grant'] == digest(canonical(lifecycle['grant']))
    assert lifecycle['grant']['ledger_binding'] == sealed.identity(str(
        (driver.OUT / 'synthetic-opening-final-mechanism.json').resolve()))
    assert result['commitment'] == lifecycle['placeholder']['commitment'] == lifecycle['opened_commitment']
    assert result['opening_count'] == 1 and lifecycle['real_open_grants'] == 0
    assert set(lifecycle['placeholder']) == {'protocol', 'resource', 'commitment', 'seal', 'qualified_authority'}
    assert lifecycle['workspace']['sealed_materialized'] == 0 and not lifecycle['workspace']['git_database_present']
    certificate = read('synthetic-certificate-v2-final-mechanism')
    cert = certificate['certificate']
    envelopes.unseal(cert)
    assert cert['version'] == 2 and cert['issuance_scope'] == 'SYNTHETIC_ONLY'
    assert cert['qualified_authority'] == lifecycle['qualified_authority']['identity']
    assert cert['authority_verification'] == lifecycle['qualified_authority']['verification']
    assert {r['mode'] for r in cert['authority_verification'].values()} == {sealed.SEALED, sealed.ORDINARY}
    assert all(envelopes.unseal(r)['status'] == 'PASS' for r in certificate['evidence'].values())
    preserved = driver.preserve(read('preservation-baseline'))
    assert not driver.ATTEMPTS
    publication.persist(driver.OUT / 'independent-audit.json', {'status': 'PASS',
        'sealed_members': 11, 'frozen_pins': 2, 'all_modes_explicit': True,
        'protected_content_reads': 0, 'production_qualification': 'NOT_RUN',
        'synthetic_final_openings': 1, 'synthetic_certificate_only': True,
        'history': preserved, 'core_semantics': 30})
    print({'independent_audit': 'PASS', 'sealed_members': 11, 'protected_content_reads': 0})


if __name__ == '__main__':
    audit()
