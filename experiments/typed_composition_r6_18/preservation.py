"""Read only protected paths; never opens curated sources or acceptance suites."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def sha(data):
    return hashlib.sha256(data).hexdigest()


def inventory():
    prefixes = ['src/', 'schema/', 'air/', 'generated/', 'tools/',
                'experiments/semantic_interpreter/', 'experiments/value_added_r6_16/',
                'benchmark/results/phase5c/R5_114-KERNEL-ACCOUNTING.json',
                'docs/symbolic-research-charter-r6.17.md']
    for n in range(3, 18):
        prefixes += [f'benchmark/results/phase6/r6_{n}/',
                     f'benchmark/results/phase6/R6_{n}-REPORT.md']
    paths = subprocess.check_output(['git', 'ls-files'], cwd=ROOT, text=True).splitlines()
    return {p: sha((ROOT / p).read_bytes()) for p in paths
            if any(p.startswith(s) for s in prefixes)}


def verify_prior():
    manifest = json.loads((ROOT / 'benchmark/results/phase6/r6_17/PUBLICATION-IDENTITIES.json').read_text())
    for p, row in manifest['files'].items():
        assert sha((ROOT / p).read_bytes()) == row['sha256'], p
        assert (ROOT / p).stat().st_size == row['bytes'], p
    # Verify the exact R6.17 protected Git blobs, including working-tree identities.
    tree = subprocess.check_output(['git', 'ls-tree', '-r', manifest['head'], '--',
                                    *manifest['protected_pathspecs']], cwd=ROOT)
    assert sha(tree) == manifest['protected_git_ls_tree_sha256']
    rows = tree.decode().splitlines()
    assert len(rows) == manifest['protected_tracked_blobs_verified']
    for row in rows:
        meta, p = row.split('\t')
        observed = subprocess.check_output(['git', 'hash-object', '--', p], cwd=ROOT, text=True).strip()
        assert observed == meta.split()[2], p
    kernel = json.loads((ROOT / 'benchmark/results/phase5c/R5_114-KERNEL-ACCOUNTING.json').read_text())
    assert kernel['final_count'] == 26
    vm = ROOT / 'experiments/semantic_interpreter'
    identities = json.loads((vm / 'PUBLICATION-IDENTITIES.json').read_text())['publication_sha256']
    checked = 0
    for p, h in identities.items():
        if p.startswith('experiments/semantic_interpreter/') and p != 'experiments/semantic_interpreter/PUBLICATION-IDENTITIES.json':
            assert sha((ROOT / p).read_bytes()) == h, p
            checked += 1
    return {'r6_17_publication_files': len(manifest['files']),
            'r6_17_protected_blobs': len(rows), 'r6_10_publication_files': checked,
            'kernel': 26}


def record():
    target = HERE / 'BASELINE.json'
    assert not target.exists()
    verification = verify_prior()
    data = {'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            'prior_verification': verification, 'protected_files': inventory()}
    target.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
    print(verification, 'protected:', len(data['protected_files']))


def verify():
    data = json.loads((HERE / 'BASELINE.json').read_text())
    assert inventory() == data['protected_files'], 'protected identities changed'
    print('Protected identities preserved:', len(data['protected_files']), 'kernel: 26')


if __name__ == '__main__':
    import sys
    record() if sys.argv[1:] == ['record'] else verify()
