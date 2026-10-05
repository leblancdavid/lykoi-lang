"""Prospective authority adjudication and scoped repository-content baseline.

No subject loader or observation dispatcher. Missing historical preimages are
never reconstructed. The caller supplies reviewed, content-bound decisions.
"""

from pathlib import Path, PurePosixPath

from benchmark.evaluation.checkout_r5_52 import sha, text
from benchmark.evaluation.recorder_r5_43 import canonical, loads

PROTOCOL = 'lykoi-authority-successor-r5.53-v1'
IMPORTANT = {'SEMANTIC_CORE', 'COMPILER_RUNTIME', 'PROFILE_SUPPORT',
             'SECURITY_INFRASTRUCTURE', 'BENCHMARK_INFRASTRUCTURE'}


def exact_preimage(expected, candidates):
    """Only actual available bytes qualify; no newline or content synthesis."""
    for source, data in candidates:
        if sha(data) == expected:
            return {'source': source, 'sha256': expected}
    return None


def adjudicate(expected, current, criticality, evidence, *, recovered=None):
    if recovered and recovered['sha256'] != expected:
        raise ValueError('wrong historical preimage')
    bound = [e for e in evidence if e.get('current_sha256') == sha(current)
             and e.get('source') and e.get('source_sha256')]
    if any(e.get('kind') == 'unauthorized' for e in evidence):
        return 'UNAUTHORIZED_MUTATION'
    if criticality == 'FROZEN_BEHAVIORAL_AUTHORITY' and not recovered:
        # Ordinary change records cannot replace frozen authority. An explicit
        # independent frozen-authority witness must bind the historical identity.
        if not any(e.get('kind') == 'frozen-authority' and
                   e.get('historical_sha256') == expected for e in bound):
            return 'PROVENANCE_INSUFFICIENT'
    kinds = {e['kind'] for e in bound}
    if 'git' not in kinds or 'change-record' not in kinds:
        return 'PROVENANCE_INSUFFICIENT'
    if criticality in IMPORTANT and 'decision' not in kinds:
        return 'PROVENANCE_INSUFFICIENT'
    return 'HISTORICAL_PREIMAGE_RECOVERED' if recovered else 'CURRENT_STATE_PROVEN_AUTHORIZED'


def materialization(repository, physical, kind):
    if repository == physical:
        return 'EXACT'
    # Declared UTF-8 text only; do not normalize bare CR, filters or encoding.
    if kind == 'utf8-lf-text' and text(repository) and b'\r' not in repository:
        if physical.replace(b'\r\n', b'\n') == repository:
            return 'LF_CRLF_REPRESENTATION'
    raise ValueError('unexplained checkout content or binary mutation')


def member_path(root, name):
    path = PurePosixPath(name)
    if path.is_absolute() or '..' in path.parts or '\\' in name or ':' in name:
        raise ValueError('invalid member path')
    result = Path(root) / name
    if any(p.is_symlink() for p in [result, *result.parents]) or not result.is_file():
        raise ValueError('nonregular member')
    return result


def build(repository, metadata):
    """Repository bytes/modes are supplied by the versioned Git tree reader.

    Checkout representation is a separate receipt, never part of baseline ID.
    Scope is enumerated, not an attestation of a complete execution capsule.
    """
    if not metadata.get('predecessors') or not metadata.get('reconciliation_sha256'):
        raise ValueError('missing successor provenance')
    members = {}
    for name, row in sorted(repository.items()):
        data = row['content']
        kind = 'utf8-lf-text' if text(data) and b'\r' not in data else 'exact-bytes'
        members[name] = {'sha256': sha(data), 'mode': row['mode'], 'blob': row['blob'], 'kind': kind}
    for name, pin in metadata.get('frozen_authority', {}).items():
        if name not in members or members[name]['sha256'] != pin:
            raise ValueError('frozen authority identity mismatch')
    body = {**metadata, 'protocol': PROTOCOL, 'members': members}
    return {**body, 'identity': sha(canonical(body))}


def verify(root, baseline, repository, *, trusted_identity):
    body = {k: v for k, v in baseline.items() if k != 'identity'}
    if baseline.get('protocol') != PROTOCOL or sha(canonical(body)) != trusted_identity or baseline['identity'] != trusted_identity:
        raise ValueError('successor identity mismatch')
    if set(repository) != set(baseline['members']):
        raise ValueError('repository membership mismatch')
    rebuilt = build(repository, {k: v for k, v in body.items() if k not in ('members', 'protocol')})
    if rebuilt != baseline:
        raise ValueError('repository content/mode/blob mutation')
    checkout = {}
    for name, row in repository.items():
        physical = member_path(root, name).read_bytes()
        relation = materialization(row['content'], physical, baseline['members'][name]['kind'])
        checkout[name] = {'sha256': sha(physical), 'relationship': relation}
    return {'baseline': trusted_identity, 'members': checkout, 'identity': sha(canonical(checkout))}


def reload(path):
    data = Path(path).read_bytes()
    value = loads(data)
    if data != canonical(value) + b'\n':
        raise ValueError('noncanonical successor encoding')
    return value
