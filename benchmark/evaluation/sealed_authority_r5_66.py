"""Prospective sealed authority and cooperative deferred workspace adapters.

Commitments are supplied by an externally pinned historical trust record, never
made by reading sealed content here. Git is a metadata backend, not semantics.
No real-resource seal-opening implementation or grant is provided.
"""
from pathlib import Path, PurePosixPath
import os

from benchmark.evaluation import capability_guard_r5_61 as guard
from benchmark.evaluation import checkout_r5_52 as checkout
from benchmark.evaluation import authority_r5_53 as successor
from benchmark.evaluation import publication_r5_59 as publication
from benchmark.evaluation import preexposure_r5_45 as envelopes
from benchmark.evaluation import tier2_r5_51 as tier
from benchmark.evaluation.recorder_r5_43 import ProtocolFailure, canonical, digest

PROTOCOL = 'lykoi-qualified-authority-sealed-r5.66-v1'
OPEN = 'SEALED_RESOURCE_OPEN'
SEALED = 'SEALED_COMMITMENT_VERIFIED'
ORDINARY = 'BYTE_VERIFIED_FROM_CURRENT_READ'
FIELDS = {'resource', 'classification', 'role', 'sha256', 'blob', 'mode',
          'representation_kind', 'frozen', 'authority', 'policy_binding',
          'provenance', 'source', 'worktree_content_verified', 'checkout_observation'}


def fail():
    raise ProtocolFailure('R5.66 sealed protocol rejected; details withheld')


def safe_name(name):
    if not isinstance(name, str):
        fail()
    p = PurePosixPath(name)
    if (not isinstance(name, str) or p.is_absolute() or not p.parts or
            any(x in ('.', '..', '.git', '.sealed', '__pycache__') for x in p.parts) or
            '\\' in name or ':' in name or p.as_posix() != name or
            name.endswith(('.pyc', '.pyo'))):
        fail()
    return name


def identity(value):
    return digest(canonical(value))


class Authority:
    """Read/verify ordinary members; metadata/commitment verify sealed members.

    The caller's trusted pin must be provided by the experiment owner. An
    observer is a reviewed control-plane adapter, never supplied by a worker.
    """
    def __init__(self, root, policy, *, trusted_policy_identity, observer):
        publication.safe_bytes(policy)
        if (set(policy) != {'authority', 'policy_binding', 'members', 'frozen_authority'} or
                identity(policy) != trusted_policy_identity or not policy['members']):
            fail()
        self.root, self.policy = Path(root).resolve(), policy
        self.pin, self.observer = trusted_policy_identity, observer
        ids = set()
        for name, row in policy['members'].items():
            safe_name(name)
            if (set(row) != FIELDS or row['classification'] not in ('ORDINARY', 'SEALED') or
                    row['authority'] != policy['authority'] or
                    row['policy_binding'] != policy['policy_binding'] or
                    row['resource'] in ids or not row['resource'] or
                    len(row['sha256']) != 64 or any(c not in '0123456789abcdef' for c in row['sha256']) or
                    row['mode'] != '100644' or
                    row['representation_kind'] not in ('utf8-lf-text', 'exact-bytes') or
                    set(row['provenance']) != {'historical_head', 'qualification', 'audit', 'successor'} or
                    not all(row['provenance'].values()) or
                    row['provenance']['successor'] != policy['authority'] or
                    row['worktree_content_verified'] is not False or
                    row['checkout_observation'] != 'DEFERRED_UNTIL_OPEN' or
                    row['frozen'] != (name in policy['frozen_authority']) or
                    (row['frozen'] and policy['frozen_authority'][name] != row['sha256'])):
                fail()
            if row['classification'] == 'SEALED' and (
                    not row['blob'] or row['source'] not in ('immutable-git-object', 'synthetic-immutable-object')):
                fail()
            ids.add(row['resource'])
        if not set(policy['frozen_authority']) <= set(policy['members']):
            fail()

    def ordinary_read(self, name):
        row = self.policy['members'].get(name)
        if row is None or row['classification'] != 'ORDINARY':
            fail()  # Classification checked BEFORE any content API.
        return successor.member_path(self.root, name).read_bytes()

    def qualify(self):
        if identity(self.policy) != self.pin:
            fail()
        verified = {}
        for name, row in sorted(self.policy['members'].items()):
            if row['classification'] == 'SEALED':
                observed = self.observer(name, row)
                expected = {k: row[k] for k in ('resource', 'sha256', 'blob', 'mode', 'provenance', 'source')}
                if observed != expected:
                    fail()
                verified[name] = {'mode': SEALED, 'commitment': row['sha256'],
                    'resource': row['resource'], 'object': row['blob'],
                    'provenance': identity(row['provenance']), 'frozen': row['frozen'],
                    'seal': 'CLOSED', 'checkout': 'DEFERRED_UNTIL_OPEN',
                    'current_content_read': False}
            else:
                physical = self.ordinary_read(name)
                repository = physical.replace(b'\r\n', b'\n') if row['representation_kind'] == 'utf8-lf-text' else physical
                if digest(repository) != row['sha256']:
                    fail()
                verified[name] = {'mode': ORDINARY, 'commitment': row['sha256'],
                    'checkout_sha256': digest(physical), 'current_content_read': True}
        return tier.seal({'protocol': PROTOCOL, 'kind': 'qualified-authority',
            'status': 'QUALIFIED', 'authority': self.policy['authority'],
            'policy_binding': self.pin, 'historical_policy': self.policy['policy_binding'],
            'frozen_authority': self.policy['frozen_authority'], 'verification': verified,
            'members': identity(self.policy['members'])})


class GitMetadata:
    """Resolve historical and current committed mappings without extracting blobs.

    Worktree content is intentionally NOT the sealed source. No Git database is
    copied into the worker workspace, so workers cannot bypass the placeholder.
    """
    def __init__(self, root):
        self.root = root

    def __call__(self, name, row):
        historical = checkout.tree(self.root, row['provenance']['historical_head'])
        current = checkout.tree(self.root, 'HEAD')
        expected = {'mode': row['mode'], 'blob': row['blob']}
        if historical.get(name) != expected or current.get(name) != expected:
            fail()
        result = checkout.git(self.root, 'cat-file', '--batch-check=%(objectname) %(objecttype)',
            input=(row['blob'] + '\n').encode()).decode().strip()
        if result != row['blob'] + ' blob':
            fail()
        return {k: row[k] for k in ('resource', 'sha256', 'blob', 'mode', 'provenance', 'source')}


def placeholder(row, qualified):
    # Closed allowlist: no path, bytes, contract, fixture, role description or URI.
    return {'protocol': 'lykoi-sealed-reference-v1', 'resource': row['resource'],
            'commitment': row['sha256'], 'seal': 'CLOSED',
            'qualified_authority': qualified['identity']}


def materialize(authority, destination, qualified):
    if authority.qualify() != qualified:
        fail()
    destination = Path(destination)
    if destination.exists() or not destination.parent.is_dir():
        fail()
    before = {name: authority.ordinary_read(name) for name, row in authority.policy['members'].items()
              if row['classification'] == 'ORDINARY'}
    destination.mkdir()
    copied, references = {}, {}
    for name, row in sorted(authority.policy['members'].items()):
        if row['classification'] == 'SEALED':
            ref = placeholder(row, qualified)
            target = destination / '.sealed' / (identity(row['resource']) + '.json')
            target.parent.mkdir(exist_ok=True)
            publication.persist(target, ref)
            references[row['resource']] = ref
        else:
            target = destination / safe_name(name)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(before[name])
            copied[name] = digest(target.read_bytes())
    if authority.qualify() != qualified or any(authority.ordinary_read(n) != b for n, b in before.items()):
        fail()
    return tier.seal({'protocol': 'lykoi-deferred-workspace-r5.66-v1',
        'qualified_authority': qualified['identity'], 'files': copied, 'references': references,
        'dedicated': True, 'git_database_present': False, 'sealed_materialized': 0})


def worker_resolve(boundary, resource):
    """Uses the same authoritative registry as mediated R5.62 children."""
    return boundary.read(resource)  # R5.61 denies before a read, records quarantine.


class SyntheticStore:
    """Synthetic-only immutable fixture adapter; no repository path or Git reader.

    Created before qualification. Content reads are counted independently of
    metadata calls. Only synthetic IDs are accepted by the opening prototype.
    """
    def __init__(self, row, data):
        if not row['resource'].startswith('synthetic:') or row['source'] != 'synthetic-immutable-object':
            fail()
        self.mapping = {k: row[k] for k in ('resource', 'sha256', 'blob', 'mode', 'provenance', 'source')}
        self.data, self.reads = data, 0

    def __call__(self, name, row):
        return self.mapping.copy() if self.mapping is not None else None

    def open(self):
        self.reads += 1
        return self.data


def open_synthetic(authority, qualified, reference, store, grant, *, trusted_grant_identity, ledger):
    """Reserve durably before opening; failed/mismatched openings consume the grant.

    A separate externally pinned synthetic grant binds the exact qualified
    authority, resource and commitment. No generic capability implies OPEN.
    Content is returned only after digest verification. This is not a B02 opener.
    """
    ledger = Path(ledger)
    if (not isinstance(store, SyntheticStore) or authority.qualify() != qualified or
            identity(grant) != trusted_grant_identity or set(grant) != {
                'capability', 'scope', 'resource', 'commitment', 'qualified_authority', 'one_time', 'ledger_binding'} or
            grant['capability'] != OPEN or grant['scope'] != 'SYNTHETIC_ONLY' or
            grant['one_time'] is not True or grant['ledger_binding'] != identity(str(ledger.resolve())) or
            grant['qualified_authority'] != qualified['identity'] or
            reference != {'protocol': 'lykoi-sealed-reference-v1', 'resource': grant['resource'],
                'commitment': grant['commitment'], 'seal': 'CLOSED',
                'qualified_authority': qualified['identity']} or
            not grant['resource'].startswith('synthetic:') or not ledger.parent.is_dir()):
        fail()
    rows = [r for r in authority.policy['members'].values() if r['resource'] == grant['resource']]
    if len(rows) != 1 or rows[0]['classification'] != 'SEALED' or rows[0]['sha256'] != grant['commitment']:
        fail()
    expected = {k: rows[0][k] for k in ('resource', 'sha256', 'blob', 'mode', 'provenance', 'source')}
    if store.mapping != expected:
        fail()
    publication.safe_bytes(grant)
    try:
        with ledger.open('xb') as stream:
            stream.write(canonical({'state': 'RESERVED', 'grant': trusted_grant_identity,
                'qualified_authority': qualified['identity'], 'resource': grant['resource']}) + b'\n')
            stream.flush()
            os.fsync(stream.fileno())
    except FileExistsError:
        fail()
    data = store.open()
    if digest(data) != grant['commitment'] or authority.qualify() != qualified:
        publication.persist(ledger.with_suffix('.result.json'), {'state': 'REJECTED', 'accepted': False})
        fail()
    publication.persist(ledger.with_suffix('.result.json'), {'state': 'OPENED', 'accepted': True,
        'opening_count': 1, 'commitment': digest(data), 'grant': trusted_grant_identity})
    return data


def certificate_link(qualified, authority):
    """Fresh, explicit CertificateV2 authority evidence (no certificate issuance)."""
    body = envelopes.unseal(qualified)
    if qualified != authority.qualify() or body['protocol'] != PROTOCOL:
        fail()
    return {'qualified_authority': qualified['identity'], 'policy_binding': body['policy_binding'],
            'frozen_authority': body['frozen_authority'],
            'authority_verification': body['verification']}
