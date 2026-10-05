"""ProductionCertificateV2: authority-neutral assembly and fresh validation.

Eligibility is relative to an externally pinned experiment authorization and its
required mechanisms. This module does not issue observations or qualify a full
production experiment. V1 evidence and dispatch mechanisms retain their meaning.
"""

from benchmark.evaluation import qualified_authority_r5_55 as authority
from benchmark.evaluation import preexposure_r5_45 as envelopes
from benchmark.evaluation import security_r5_47 as security
from benchmark.evaluation import tier2_r5_51 as tier
from benchmark.evaluation.recorder_r5_43 import ProtocolFailure

PROTOCOL = 'lykoi-production-certificate-v2'
REQUIRED = {'identity', 'authority', 'contamination', 'workspace'}
POLICY_FIELDS = {'experiment', 'stages', 'qualified_authority', 'authority_role',
                 'semantic_count', 'canonical_protocol', 'recorder', 'observation_state'}


def certificate(qualified, capsule, evidence, policy, root, authorization, *, trusted_policy_identity):
    if qualified != authority.qualify(root, authorization, trusted_policy_identity=trusted_policy_identity):
        raise ProtocolFailure('unqualified authority')
    security.safe_bytes([qualified, capsule, evidence, policy])
    tier.check(capsule)
    body = envelopes.unseal(qualified)
    if (body.get('protocol') != authority.PROTOCOL or body.get('kind') != 'qualified-authority' or
            body.get('status') != 'QUALIFIED' or set(policy) != POLICY_FIELDS or
            policy['qualified_authority'] != qualified['identity'] or
            not REQUIRED.issubset(policy['stages']) or set(evidence) != set(policy['stages']) or
            policy['authority_role'] != capsule['roles']['authority'] or
            policy['semantic_count'] != 30 or policy['canonical_protocol'] != tier.CANONICAL_PROTOCOL or
            policy['recorder'] != capsule['policy']['recorder'] or
            policy['observation_state'] != {'reservations': 0, 'dispatches': 0, 'completions': 0}):
        raise ProtocolFailure('incompatible CertificateV2 policy')
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
        raise ProtocolFailure('authority, semantics, contamination or workspace not established')
    return tier.seal({'protocol': PROTOCOL, 'kind': 'certificate', 'version': 2,
                      'qualified_authority': qualified['identity'], 'policy_binding': body['policy_binding'],
                      'frozen_authority': body['frozen_authority'], 'capsule': capsule['identity'],
                      'policy': policy, 'receipts': {n: evidence[n]['identity'] for n in sorted(evidence)},
                      'canonical_protocol': tier.CANONICAL_PROTOCOL, 'recorder': policy['recorder'],
                      'semantic_count': 30, 'contamination': 'clean',
                      'observation_state': policy['observation_state']})


def validate(cert, qualified, capsule, evidence, policy, current, root, authorization,
             *, trusted_policy_identity):
    fresh = authority.qualify(root, authorization, trusted_policy_identity=trusted_policy_identity)
    if fresh != qualified or current != capsule or cert != certificate(
            fresh, current, evidence, policy, root, authorization,
            trusted_policy_identity=trusted_policy_identity):
        raise ProtocolFailure('stale authority, capsule or CertificateV2')
    return True
