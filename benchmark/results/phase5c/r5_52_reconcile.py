"""R5.52 read-only diagnostic inventory. B02 authority bytes are hash-only inputs."""

from collections import Counter
import difflib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]
from benchmark.evaluation import checkout_r5_52 as check
from benchmark.evaluation import security_r5_47 as security

RESULTS = ROOT / 'benchmark/results/phase5c'
LOCKS = {'historical': 'R5_40-implementation-profile-lock.json',
         'prospective': 'R5_41-implementation-lock.json',
         'infrastructure': 'R5_47-infrastructure-lock-v2.json'}
PINS = {
    'benchmark/requirements/B01.md': 'b7b2d714db5cee566e9e55982dd4c4d95d3d57f0c341e04ba1e15c24e9a8e94d',
    'benchmark/requirements/B02.md': '8a76e276240fa840c473be60a8e7ed0e10bd0c165426b1bfc84741e69872032b',
    'benchmark/harness/profiles/B02.json': '46ff02e3ff6ea48a7990c2f522fb9fa7bbefcab3c88550be007e0c2c1b75972f',
    'benchmark/results/phase5c/R5_40-frozen-regression-authority.txt':
        '16d55bac4dc1efa3debc6764ddde9dc27c16b7538de476a0fae9cf7db7519596'}


def inventory():
    locks = {name: json.loads((RESULTS / path).read_bytes()) for name, path in LOCKS.items()}
    names = sorted(set(PINS) | {p for lock in locks.values() for p in lock['files']})
    commits = check.git(ROOT, 'rev-list', '--first-parent', 'HEAD').decode().splitlines()
    trees = {commit: check.tree(ROOT, commit) for commit in commits}
    objects = check.blobs(ROOT, [row['blob'] for t in trees.values()
                                for name, row in t.items() if name in names])
    attrs = check.attributes(ROOT, names)
    current = {name: (ROOT / name).read_bytes() if (ROOT / name).is_file() else None for name in names}
    candidates = {name: [] for name in names}
    for name in names:
        seen = set()
        for commit in commits:
            row = trees[commit].get(name)
            if row and row['blob'] not in seen:
                candidates[name].append((commit + ':' + name, objects[row['blob']]))
                seen.add(row['blob'])
    index = {}
    for row in check.git(ROOT, 'ls-files', '-s', '-z').split(b'\0'):
        if row:
            meta, name = row.split(b'\t', 1)
            mode, blob, stage = meta.decode().split()
            if stage != '0':
                raise ValueError('unmerged checkout')
            index[name.decode()] = blob

    def diagnose(name, expected):
        authority, recovery = check.recover(expected, candidates[name])
        if authority is None:
            authority, recovery = check.recover_mixed(expected, candidates[name])
        actual = current[name]
        head = trees[commits[0]].get(name)
        repo = objects[head['blob']] if head else None
        row = {'path': name, 'authority_sha256': expected,
               'checkout_sha256': check.sha(actual) if actual is not None else None,
               'class': check.classify(authority, actual), 'recovery': recovery,
               'attributes': attrs[name], 'authority_endings': check.endings(authority) if authority is not None else None,
               'checkout_endings': check.endings(actual) if actual is not None else None,
               'head_blob': head['blob'] if head else None, 'index_blob': index.get(name),
               'repository_sha256': check.sha(repo) if repo is not None else None,
               'normalized_equal': authority is not None and actual is not None and
                                   check.normalize(authority) == check.normalize(actual),
               'checkout_vs_head': check.classify(repo, actual)}
        if row['class'] == 'CONTENT_DIFFERENT':
            row['diff'] = list(difflib.unified_diff(check.normalize(authority).decode().splitlines(),
                check.normalize(actual).decode().splitlines(), fromfile='pinned authority', tofile='checkout', lineterm=''))
            row['changes'] = check.git(ROOT, 'log', '--format=%H %s', '--', name).decode().splitlines()
            row['authority_repository_sha256'] = check.sha(check.normalize(authority))
        return row

    result = {'protocol': check.PROTOCOL, 'head': commits[0], 'locks': {},
              'frozen_pins': [diagnose(n, h) for n, h in PINS.items()],
              'b02_exposure': 0, 'core_semantics': 30, 'historical_results_requalified': False}
    for name, lock in locks.items():
        rows = [diagnose(n, h) for n, h in sorted(lock['files'].items())]
        body = {k: v for k, v in lock.items() if k != 'identity'}
        from benchmark.evaluation.recorder_r5_43 import canonical
        result['locks'][name] = {'manifest': LOCKS[name], 'manifest_sha256': check.sha((RESULTS / LOCKS[name]).read_bytes()),
            'head': lock['head'], 'metadata': {k: v for k, v in lock.items() if k != 'files'},
            'identity_valid': 'identity' not in lock or check.sha(canonical(body)) == lock['identity'],
            'ancestry_valid': __import__('subprocess').run(['git', 'merge-base', '--is-ancestor', lock['head'], 'HEAD'],
                cwd=ROOT, capture_output=True).returncode == 0,
            'counts': dict(Counter(r['class'] for r in rows)), 'members': rows,
            'unexpected_scope': 'Historical manifests enumerate protected members, not a closed-world checkout. Later tracked additions are separately inventoried, not historical lock violations.',
            'later_tracked_paths': sorted(set(trees[commits[0]]) - set(lock['files']))}
    security.persist(RESULTS / 'R5_52-inventory-v3.json', result)
    print(json.dumps({n: r['counts'] for n, r in result['locks'].items()}, indent=2))
    print(json.dumps([{'path': r['path'], 'class': r['class']} for r in result['frozen_pins']], indent=2))
    print(json.dumps([{'path': r['path'], 'recovery': r['recovery'], 'changes': r.get('changes')}
                      for r in result['locks']['infrastructure']['members'] if r['class'] in {'CONTENT_DIFFERENT', 'UNCLASSIFIED'}], indent=2))


if __name__ == '__main__':
    inventory()
