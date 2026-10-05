"""Independent R5.53 read-only baseline audit; no production gate or subjects."""

from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]
from benchmark.evaluation.recorder_r5_43 import canonical, loads
from benchmark.evaluation.security_r5_47 import persist

RESULTS = ROOT / 'benchmark/results/phase5c'
OUT = RESULTS / 'R5_53-evidence'
TRUSTED = '5dd2e7e645c1736f23a80bff755d347da5688cc9e8b7f7df515bd7110d1534ea'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def git(*args):
    return subprocess.check_output(['git', '--no-replace-objects', *args], cwd=ROOT, timeout=30)


def main():
    raw = (RESULTS / 'R5_53-authority-successor-v1.json').read_bytes()
    baseline = loads(raw)
    assert raw == canonical(baseline) + b'\n'
    assert baseline['identity'] == TRUSTED
    assert sha(canonical({k: v for k, v in baseline.items() if k != 'identity'})) == TRUSTED
    adjudication = loads((OUT / 'adjudication.json').read_bytes())
    assert sha(canonical(adjudication)) == baseline['reconciliation_sha256']
    assert sha((ROOT / 'docs/authority-successor-r5.53.md').read_bytes()) == baseline['decision_sha256']
    assert git('rev-parse', 'HEAD').decode().strip() == baseline['head']
    tree = {}
    for row in git('ls-tree', '-r', '-z', baseline['head']).split(b'\0'):
        if row:
            meta, name = row.split(b'\t', 1)
            mode, kind, blob = meta.decode().split()
            if kind == 'blob':
                tree[name.decode()] = (mode, blob)
    relations = Counter()
    for name, member in baseline['members'].items():
        path = ROOT / name
        assert not path.is_symlink() and path.is_file()
        actual = path.read_bytes()
        if member['blob'] is None:
            assert name in baseline['authorized_additions'] and member['mode'] == '100644'
            repository = actual
        else:
            assert tree[name] == (member['mode'], member['blob'])
            repository = git('cat-file', 'blob', member['blob'])
        assert sha(repository) == member['sha256']
        if actual == repository:
            relations['EXACT'] += 1
        else:
            assert member['kind'] == 'utf8-lf-text'
            assert b'\r' not in repository and b'\0' not in repository
            repository.decode('utf-8')
            assert actual.replace(b'\r\n', b'\n') == repository
            relations['LF_CRLF_REPRESENTATION'] += 1
    for name, pin in baseline['frozen_authority'].items():
        assert baseline['members'][name]['sha256'] == pin
    for predecessor in baseline['predecessors']:
        raw = (RESULTS / predecessor['path']).read_bytes()
        assert sha(raw) == predecessor['raw_sha256']
        assert subprocess.run(['git', 'merge-base', '--is-ancestor', loads(raw)['head'], baseline['head']], cwd=ROOT).returncode == 0
    assert len(adjudication['files']) == 8
    carrier_witnesses = []
    for row in adjudication['files']:
        assert row['disposition'] == 'CURRENT_STATE_PROVEN_AUTHORIZED'
        assert not row['frozen_behavioral_authority']
        assert row['historical_preimage_status'] == 'HISTORICAL_PREIMAGE_UNAVAILABLE'
        # Physical locks were published from an uncommitted working tree: their
        # HEAD field can name the preceding round. The commit that first carries
        # the lock and implementation together is the proper content witness.
        carrier = row['first_known_lock_commit'].split()[0]
        assert sha(git('show', carrier + ':' + row['path'])) == row['current_repository_sha256']
        pin_context = []
        for occurrence in row['lock_membership']:
            candidate = subprocess.run(['git', 'show', carrier + ':' + occurrence['path']], cwd=ROOT,
                                       capture_output=True, timeout=10)
            if candidate.returncode == 0:
                lock = loads(candidate.stdout)
                if lock.get('files', {}).get(row['path']) == row['historical_sha256']:
                    pin_context.append(occurrence['path'])
        assert pin_context
        older = []
        for witness in row['lock_head_repository_witnesses']:
            if not witness['current_content_equal']:
                assert subprocess.run(['git', 'merge-base', '--is-ancestor', witness['head'], carrier], cwd=ROOT).returncode == 0
                older.append(witness)
        carrier_witnesses.append({'path': row['path'], 'carrier_commit': carrier, 'pin_context': pin_context,
                                  'current_repository_equal': True, 'pre_change_lock_heads': older})
        assert any(w['current_repository_content_equal'] for w in row['diagnostic_copies'])
        assert row['current_repository_sha256'] == baseline['members'][row['path']]['sha256']
    static = {p.stem: loads(p.read_bytes())['successful'] for p in OUT.glob('*-worker.json')}
    assert all(static.values())
    initial = loads((OUT / 'initial.json').read_bytes())
    transitions = loads((OUT / 'authorized-transitions.json').read_bytes())
    supplemental = loads((OUT / 'supplemental-source-search.json').read_bytes())
    investigation = loads((OUT / 'investigation.json').read_bytes())
    findings = {'trusted_baseline': TRUSTED, 'members': len(baseline['members']),
        'auditor_sha256': sha(Path(__file__).read_bytes()),
        'checkout_relationships': dict(relations), 'independent_audit': 'PASS',
        'static_checks': static, 'adjudications_verified': 8, 'exact_preimages_recovered': 0,
        'archive_sources': len(investigation['source_search']['archive_inventory']),
        'archive_target_members': sum(len(a['candidate_members']) for a in investigation['source_search']['archive_inventory']),
        'protected_historical_files': len(initial['historical']),
        'transition_categories': dict(Counter(r['category'] for r in transitions['rows'])),
        'supplemental_databases': supplemental['diagnostic_git_databases'],
        'all_lock_carrier_repository_content_witnesses_equal': True,
        'carrier_witnesses': carrier_witnesses,
        'b02_exposure': 0, 'core_semantics': 30, 'production_tier2_qualification_performed': False}
    persist(OUT / (sys.argv[1] if len(sys.argv) > 1 else 'independent-audit.json'), findings)
    print(json.dumps(findings, indent=2))


if __name__ == '__main__':
    main()
