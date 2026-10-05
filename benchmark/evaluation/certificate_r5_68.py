"""CertificateV3: explicit modes, externally pinned declarations, no opening API.

V2 and its R5.66 synthetic adapter remain unchanged. This cooperative control
plane validates owner-supplied trust pins; a payload cannot appoint its own pin.
"""
from benchmark.evaluation import certificate_r5_55 as v2
from benchmark.evaluation import sealed_authority_r5_66 as sealed
from benchmark.evaluation import preexposure_r5_45 as envelopes
from benchmark.evaluation import publication_r5_59 as publication
from benchmark.evaluation import publication_schema_r5_64 as schemas
from benchmark.evaluation import tier2_r5_51 as tier
from benchmark.evaluation.recorder_r5_43 import ProtocolFailure, canonical, digest

PROTOCOL = 'lykoi-production-certificate-v3'
DECLARATION_PROTOCOL = 'lykoi-certificate-mode-declaration-r5.68-v1'
SYNTHETIC = 'SYNTHETIC_QUALIFICATION'
PRODUCTION = 'PRODUCTION_SEALED'
OPERATIONS = {SYNTHETIC: 'SYNTHETIC_GATE_QUALIFIED', PRODUCTION: 'PRODUCTION_GATE_QUALIFIED'}
SCOPES = {SYNTHETIC: 'SYNTHETIC_ONLY', PRODUCTION: 'PRODUCTION_SEALED_ONLY'}
ZERO = {'exposures': 0, 'reservations': 0, 'dispatches': 0, 'completions': 0}
DECLARATION_SCHEMA = schemas.PublicationSchema.declare(schemas.object_schema({
    **{n: schemas.field(schemas.PROTOCOL_IDENTITY) for n in
       ('protocol', 'experiment', 'mode', 'scope', 'allowed_operation', 'sealed_policy', 'observation_state')},
    **{n: schemas.field(schemas.CONTENT_IDENTITY) for n in
       ('schema_binding', 'qualification', 'authority', 'qualified_authority', 'resource_policy',
        'capsule', 'certificate_policy')},
    'seal_open_authorized': schemas.field(value_type='boolean'),
}, classification=schemas.PROTOCOL_AUTHORIZATION))
# Producer-owned schema identity, fixed independently of evidence.
DECLARATION_SCHEMA_PIN = 'f3648f3ce5bb2e8ff4f105dd0af82db096b77de33ad2e78d5586ff02fd10ea17'


def fail():
    raise ProtocolFailure('R5.68 certificate mode or binding rejected; details withheld')


def eligibility(declaration, *, trusted_declaration_identity, mode, qualification,
                qualified, capsule, policy):
    publication.safe_bytes(declaration, schema=DECLARATION_SCHEMA,
                           schema_identity=DECLARATION_SCHEMA_PIN)
    if (mode not in OPERATIONS or not trusted_declaration_identity or
            digest(canonical(declaration)) != trusted_declaration_identity or
            not isinstance(qualification, str) or len(qualification) != 64):
        fail()
    expected = {
        'protocol': DECLARATION_PROTOCOL, 'schema_binding': DECLARATION_SCHEMA_PIN,
        'experiment': policy['experiment'], 'qualification': qualification,
        'mode': mode, 'scope': SCOPES[mode], 'authority': qualified['authority'],
        'qualified_authority': qualified['identity'], 'resource_policy': qualified['policy_binding'],
        'capsule': capsule['identity'], 'certificate_policy': digest(canonical(policy)),
        'allowed_operation': OPERATIONS[mode], 'sealed_policy': 'CLOSED_NO_OPEN_NO_OBSERVATION',
        'observation_state': 'ZERO_UNOBSERVED', 'seal_open_authorized': False,
    }
    if declaration != expected:
        fail()
    return True


def certificate(qualified, capsule, evidence, policy, authority, declaration, *,
                trusted_declaration_identity, mode, qualification):
    eligibility(declaration, trusted_declaration_identity=trusted_declaration_identity,
                mode=mode, qualification=qualification, qualified=qualified, capsule=capsule, policy=policy)
    link = sealed.certificate_link(qualified, authority)
    publication.safe_bytes([qualified, capsule, evidence, policy])
    tier.check(capsule)
    if (set(policy) != v2.POLICY_FIELDS or not policy['experiment'] or
            policy['qualified_authority'] != qualified['identity'] or
            not v2.REQUIRED.issubset(policy['stages']) or set(evidence) != set(policy['stages']) or
            policy['authority_role'] != capsule['roles']['authority'] or
            type(policy['semantic_count']) is not int or policy['semantic_count'] != 30 or
            policy['canonical_protocol'] != tier.CANONICAL_PROTOCOL or
            policy['recorder'] != capsule['policy']['recorder'] or
            canonical(policy['observation_state']) != canonical({k: 0 for k in ZERO if k != 'exposures'})):
        fail()
    for name, value in evidence.items():
        row = envelopes.unseal(value)
        if (row.get('protocol') != tier.PROTOCOL or row.get('kind') != 'receipt' or
                row.get('capsule') != capsule['identity'] or row.get('experiment') != policy['experiment'] or
                row.get('stage') != name or row.get('mechanism') != policy['stages'][name] or
                row.get('status') != 'PASS' or row.get('result', {}).get('successful') is not True):
            fail()
    if (evidence['authority']['result'].get('qualified_authority') != qualified['identity'] or
            evidence['identity']['result'].get('semantic_count') != 30 or
            evidence['identity']['result'].get('qualification') != qualification or
            evidence['contamination']['result'].get('findings') != [] or
            evidence['workspace']['result'].get('dedicated') is not True):
        fail()
    return tier.seal({'protocol': PROTOCOL, 'kind': 'certificate', 'version': 3, **link,
        'capsule': capsule['identity'], 'policy': policy, 'qualification': qualification,
        'receipts': {n: evidence[n]['identity'] for n in sorted(evidence)},
        'canonical_protocol': tier.CANONICAL_PROTOCOL, 'recorder': policy['recorder'],
        'semantic_count': 30, 'contamination': 'clean', 'observation_state': policy['observation_state'],
        'mode': mode, 'authorization_binding': trusted_declaration_identity,
        'authorization_schema': DECLARATION_SCHEMA_PIN, 'issuance_scope': SCOPES[mode],
        'allowed_operation': OPERATIONS[mode], 'seal_open_authorized': False,
        'b02_observation_authorized': False})


def validate(cert, qualified, capsule, evidence, policy, current, authority, declaration, **binding):
    envelopes.unseal(cert)
    if current != capsule or cert != certificate(
            qualified, current, evidence, policy, authority, declaration, **binding):
        fail()
    return True


def require_operation(cert, operation, qualified, capsule, evidence, policy,
                      current, authority, declaration, **binding):
    """Validate full evidence before considering a gate qualification operation.

    Neither mode is an opening grant, including for synthetic resources. Actual
    B02 reservation requires a future separately qualified two-object consumer.
    """
    validate(cert, qualified, capsule, evidence, policy, current, authority, declaration, **binding)
    if operation != OPERATIONS[binding['mode']]:
        fail()
    return True
