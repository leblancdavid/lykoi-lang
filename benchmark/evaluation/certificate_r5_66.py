"""Prospective CertificateV2 sealed-evidence adapter; synthetic issuance only."""
from benchmark.evaluation import certificate_r5_55 as v2
from benchmark.evaluation import sealed_authority_r5_66 as sealed
from benchmark.evaluation import preexposure_r5_45 as envelopes
from benchmark.evaluation import publication_r5_59 as publication
from benchmark.evaluation import tier2_r5_51 as tier
from benchmark.evaluation.recorder_r5_43 import ProtocolFailure


def certificate(qualified, capsule, evidence, policy, authority):
    link = sealed.certificate_link(qualified, authority)
    publication.safe_bytes([qualified, capsule, evidence, policy])
    tier.check(capsule)
    if (set(policy) != v2.POLICY_FIELDS or not policy['experiment'].startswith('synthetic:') or
            policy['qualified_authority'] != qualified['identity'] or
            not v2.REQUIRED.issubset(policy['stages']) or set(evidence) != set(policy['stages']) or
            policy['authority_role'] != capsule['roles']['authority'] or policy['semantic_count'] != 30 or
            policy['canonical_protocol'] != tier.CANONICAL_PROTOCOL or
            policy['recorder'] != capsule['policy']['recorder'] or
            policy['observation_state'] != {'reservations': 0, 'dispatches': 0, 'completions': 0}):
        raise ProtocolFailure('incompatible synthetic CertificateV2 policy')
    for name, value in evidence.items():
        row = envelopes.unseal(value)
        if (row.get('protocol') != tier.PROTOCOL or row.get('kind') != 'receipt' or
                row.get('capsule') != capsule['identity'] or row.get('experiment') != policy['experiment'] or
                row.get('stage') != name or row.get('mechanism') != policy['stages'][name] or
                row.get('status') != 'PASS' or row.get('result', {}).get('successful') is not True):
            raise ProtocolFailure('missing, mixed, stale or unsuccessful receipt')
    if (evidence['authority']['result'].get('qualified_authority') != qualified['identity'] or
            evidence['identity']['result'].get('semantic_count') != 30 or
            evidence['contamination']['result'].get('findings') != [] or
            evidence['workspace']['result'].get('dedicated') is not True):
        raise ProtocolFailure('CertificateV2 evidence incomplete')
    return tier.seal({'protocol': v2.PROTOCOL, 'kind': 'certificate', 'version': 2, **link,
        'capsule': capsule['identity'], 'policy': policy,
        'receipts': {n: evidence[n]['identity'] for n in sorted(evidence)},
        'canonical_protocol': tier.CANONICAL_PROTOCOL, 'recorder': policy['recorder'],
        'semantic_count': 30, 'contamination': 'clean', 'observation_state': policy['observation_state'],
        'issuance_scope': 'SYNTHETIC_ONLY'})


def validate(cert, qualified, capsule, evidence, policy, current, authority):
    if current != capsule or cert != certificate(qualified, current, evidence, policy, authority):
        raise ProtocolFailure('stale sealed authority, capsule or CertificateV2')
    return True
