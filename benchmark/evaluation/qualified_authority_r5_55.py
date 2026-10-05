"""Versioned qualified-authority interpretation; no subject or dispatch API.

The experiment owner pins the authorization policy externally. Shape, age and
Git ancestry alone never authorize a manifest. Frozen pins are independent of
the selected infrastructure manifest. Historical physical outcomes are evidence.
"""

import subprocess
from pathlib import Path

from benchmark.evaluation import authority_r5_53 as successor
from benchmark.evaluation import checkout_r5_52 as checkout
from benchmark.evaluation import security_r5_47 as security
from benchmark.evaluation import tier2_r5_51 as tier
from benchmark.evaluation.recorder_r5_43 import ProtocolFailure, canonical, digest, loads

PROTOCOL = 'lykoi-qualified-authority-v1'
POLICY = 'lykoi-qualified-authority-authorization-v1'
REPRESENTATION = 'repository-content+utf8-lf-crlf-exact-material-v1'
FIELDS = {'protocol', 'manifest', 'authority_identity', 'manifest_sha256',
          'qualification', 'qualification_sha256', 'audit', 'audit_sha256',
          'decision', 'adjudication', 'predecessor_root', 'historical_evidence',
          'frozen_authority', 'checkout_policy', 'status'}


def read(root, name):
    return successor.member_path(root, name).read_bytes()


def ancestor(root, older, newer):
    result = subprocess.run(['git', '--no-replace-objects', 'merge-base', '--is-ancestor',
                             older, newer], cwd=root, capture_output=True, timeout=10)
    if result.returncode != 0:
        raise ProtocolFailure('authority ancestry rejected')


def qualify(root, policy, *, trusted_policy_identity):
    """Freshly verify the pinned authorization and its live content evidence.

    Version-aware R5.53 structural interpretation, not an identity/path exception.
    Future qualified manifests of this protocol use a new externally authorized
    policy, retaining independent frozen and historical evidence pins.
    """
    try:
        security.safe_bytes(policy)
        if (set(policy) != FIELDS or digest(canonical(policy)) != trusted_policy_identity or
                policy['protocol'] != POLICY or policy['status'] != 'QUALIFIED' or
                policy['checkout_policy'] != REPRESENTATION):
            raise ValueError('authorization')
        raw = read(root, policy['manifest'])
        baseline = loads(raw)
        if raw != canonical(baseline) + b'\n' or digest(raw) != policy['manifest_sha256']:
            raise ValueError('manifest')
        if baseline['protocol'] != successor.PROTOCOL:
            raise ValueError('unsupported manifest protocol')
        qualification_raw = read(root, policy['qualification'])
        audit_raw = read(root, policy['audit'])
        qualification, audit = loads(qualification_raw), loads(audit_raw)
        if (digest(qualification_raw) != policy['qualification_sha256'] or
                digest(audit_raw) != policy['audit_sha256'] or
                qualification['identity'] != policy['authority_identity'] or
                audit['trusted_baseline'] != policy['authority_identity'] or
                audit['independent_audit'] != 'PASS' or
                any(qualification.get(n) is not True for n in
                    ('canonical_reload', 'deterministic_reproduction',
                     'independent_member_integrity', 'ancestry_verified', 'historical_failures_preserved'))):
            raise ValueError('unqualified')
        if (baseline['historical_physical_failures_preserved'] is not True or
                baseline['core_semantics'] != 30 or baseline['b02_exposure'] != 0 or
                baseline['frozen_authority'] != policy['frozen_authority'] or
                qualification['authority_identities'] != policy['frozen_authority']):
            raise ValueError('frozen or historical authority')
        tree = checkout.tree(root, baseline['head'])
        blobs = checkout.blobs(root, [r['blob'] for r in baseline['members'].values() if r['blob']])
        repository = {}
        for name, row in baseline['members'].items():
            if row['blob'] is None:
                if name not in baseline['authorized_additions'] or row['mode'] != '100644':
                    raise ValueError('unauthorized addition')
                data = read(root, name)
            else:
                if tree[name] != {'mode': row['mode'], 'blob': row['blob']}:
                    raise ValueError('tree membership')
                data = blobs[row['blob']]
            repository[name] = {'content': data, 'mode': row['mode'], 'blob': row['blob']}
        representation = successor.verify(root, baseline, repository,
                                            trusted_identity=policy['authority_identity'])
        if qualification['members'] != len(repository) or audit['members'] != len(repository):
            raise ValueError('qualification scope')
        attrs = checkout.attributes(root, sorted(repository))
        if any(r['filter'] != 'unspecified' or r['working-tree-encoding'] != 'unspecified'
               for r in attrs.values()):
            raise ValueError('unsupported checkout transform')
        controls = subprocess.run(['git', 'config', '--show-origin', '--get-regexp',
                                   r'core\.(autocrlf|eol|safecrlf|attributesfile)'],
                                  cwd=root, capture_output=True, timeout=10)
        if controls.returncode not in (0, 1):
            raise ValueError('checkout controls unavailable')
        decision = read(root, policy['decision'])
        adjudication = loads(read(root, policy['adjudication']))
        if (digest(decision) != baseline['decision_sha256'] or
                digest(canonical(adjudication)) != baseline['reconciliation_sha256']):
            raise ValueError('provenance')
        for row in adjudication['files']:
            if (row['historical_preimage_status'] != 'HISTORICAL_PREIMAGE_UNAVAILABLE' or
                    row['disposition'] != 'CURRENT_STATE_PROVEN_AUTHORIZED' or
                    row['frozen_behavioral_authority'] or
                    baseline['members'][row['path']]['sha256'] != row['current_repository_sha256'] or
                    not {'git', 'change-record', 'decision'}.issubset(
                        {link['kind'] for link in row['current_provenance']})):
                raise ValueError('successor authorization')
            for link in row['current_provenance']:
                data = decision if link['kind'] == 'decision' else checkout.git(root, 'show', link['source'])
                if digest(data) != link['source_sha256']:
                    raise ValueError('provenance link')
        if not baseline['predecessors']:
            raise ValueError('missing predecessors')
        for previous in baseline['predecessors']:
            data = read(root, policy['predecessor_root'] + '/' + previous['path'])
            if digest(data) != previous['raw_sha256'] or previous['historical_physical_status'] != 'FAIL':
                raise ValueError('predecessor evidence')
            ancestor(root, loads(data)['head'], baseline['head'])
        ancestor(root, baseline['head'], 'HEAD')
        for name, expected in policy['historical_evidence'].items():
            if digest(read(root, name)) != expected:
                raise ValueError('historical evidence erased or altered')
        if not policy['historical_evidence']:
            raise ValueError('historical evidence missing')
        return tier.seal({'protocol': PROTOCOL, 'kind': 'qualified-authority',
                          'authority_schema': baseline['protocol'], 'authority': baseline['identity'],
                          'manifest': policy['manifest_sha256'],
                          'policy_binding': trusted_policy_identity, 'qualification': policy['qualification_sha256'],
                          'independent_audit': policy['audit_sha256'],
                          'members': digest(canonical(baseline['members'])),
                          'frozen_authority': policy['frozen_authority'],
                          'provenance': baseline['reconciliation_sha256'],
                          'decision': baseline['decision_sha256'], 'predecessors': baseline['predecessors'],
                          'historical_evidence': policy['historical_evidence'],
                          'checkout_policy': REPRESENTATION, 'checkout': representation,
                          'attributes': attrs, 'effective_eol_settings': controls.stdout.decode(),
                          'status': 'QUALIFIED'})
    except Exception:
        raise ProtocolFailure('qualified authority rejected; details withheld') from None
