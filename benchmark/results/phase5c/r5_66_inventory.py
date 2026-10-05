"""Metadata-only inventory. Never requests Git blob contents or protected files."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]
from benchmark.evaluation import capability_guard_r5_61 as guard
from benchmark.evaluation import checkout_r5_52 as checkout
from benchmark.evaluation import continuity_r5_59 as continuity
from benchmark.evaluation import publication_r5_59 as publication
from benchmark.evaluation.recorder_r5_43 import canonical, digest, loads

POLICY_PIN = '31d4b3632cfcdbf1e928ddf3cbeaf2b88fad97e50ba502b78cf1434d09a114b8'
AUTHORITY_PIN = '5dd2e7e645c1736f23a80bff755d347da5688cc9e8b7f7df515bd7110d1534ea'
OUT = ROOT / 'benchmark/results/phase5c/R5_66-evidence'


def metadata(name, expected):
    physical = (ROOT / name).read_bytes()
    value = loads(physical)
    repository = canonical(value) + b'\n'
    continuity.verify(repository, physical, repository_sha256=expected, kind='utf8-lf-text')
    return value


def inventory():
    events = []
    boundary = guard.Boundary(guard.repository_resources(ROOT), events.append)
    # No subprocess permit is needed for reads of safe metadata. Git metadata
    # commands below are control-plane operations, never worker commands.
    with boundary.stage(['AUTHORITY_LINKAGE']):
        policy = loads((ROOT / 'benchmark/results/phase5c/R5_55-qualified-evidence/authorization.json').read_bytes())
        assert digest(canonical(policy)) == POLICY_PIN
        baseline = metadata(policy['manifest'], policy['manifest_sha256'])
        assert baseline['identity'] == AUTHORITY_PIN == digest(canonical(
            {k: v for k, v in baseline.items() if k != 'identity'}))
        qualification = metadata(policy['qualification'], policy['qualification_sha256'])
        audit = metadata(policy['audit'], policy['audit_sha256'])
        assert qualification['identity'] == audit['trusted_baseline'] == AUTHORITY_PIN
        assert audit['independent_audit'] == 'PASS'
        assert all(qualification[k] is True for k in ('canonical_reload',
            'deterministic_reproduction', 'independent_member_integrity', 'ancestry_verified'))
    tree = checkout.tree(ROOT, baseline['head'])
    current = checkout.tree(ROOT, 'HEAD')
    rows = {}
    for resource in guard.repository_resources(ROOT):
        name = resource.path.relative_to(ROOT).as_posix()
        if name not in baseline['members']:
            continue
        member = baseline['members'][name]
        assert member['blob'] and tree[name] == current[name] == {
            'blob': member['blob'], 'mode': member['mode']}
        # --batch-check only reports object identity/type/size; never its bytes.
        object_metadata = checkout.git(ROOT, 'cat-file', '--batch-check=%(objectname) %(objecttype)',
            input=(member['blob'] + '\n').encode()).decode().strip()
        assert object_metadata == member['blob'] + ' blob'
        frozen = name in policy['frozen_authority']
        assert not frozen or policy['frozen_authority'][name] == member['sha256']
        rows[name] = {'resource': resource.identity, 'classification': 'SEALED',
            'role': resource.capability, 'sha256': member['sha256'], 'blob': member['blob'],
            'mode': member['mode'], 'representation_kind': member['kind'],
            'frozen': frozen, 'authority': AUTHORITY_PIN, 'policy_binding': POLICY_PIN,
            'provenance': {'historical_head': baseline['head'],
                'qualification': policy['qualification_sha256'], 'audit': policy['audit_sha256'],
                'successor': AUTHORITY_PIN}, 'source': 'immutable-git-object',
            'worktree_content_verified': False, 'checkout_observation': 'DEFERRED_UNTIL_OPEN'}
    assert len(rows) == 11 and sum(r['frozen'] for r in rows.values()) == 2
    assert not events
    return {'protocol': 'lykoi-sealed-inventory-r5.66-v1', 'members': rows,
        'authority': AUTHORITY_PIN, 'policy_binding': POLICY_PIN,
        'protected_content_reads': 0, 'guard_events': events,
        'trust_scope': 'historically qualified immutable objects, not current worktree bytes'}


if __name__ == '__main__':
    value = inventory()
    OUT.mkdir(exist_ok=True)
    publication.persist(OUT / 'sealed-inventory.json', value)
    print({'sealed_members': len(value['members']), 'protected_content_reads': 0})
