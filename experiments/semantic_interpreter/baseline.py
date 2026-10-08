"""Publication-only identity checks; never opens curated sources or oracles."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def inventory():
    prefixes = ['src/', 'schema/', 'air/', 'generated/', 'tools/']
    for n in range(3, 10):
        prefixes += [f'benchmark/results/phase6/r6_{n}/',
                     f'benchmark/results/phase6/R6_{n}-REPORT.md']
    prefixes += ['benchmark/results/phase5c/R5_114-KERNEL-ACCOUNTING.json']
    paths = subprocess.check_output(['git', 'ls-files'], cwd=ROOT, text=True).splitlines()
    return {p: digest(p) for p in paths if any(p.startswith(s) for s in prefixes)}


def verify_publications():
    checked = {}
    for n in range(3, 10):
        p = ROOT / f'benchmark/results/phase6/r6_{n}/PUBLICATION-IDENTITIES.json'
        if not p.exists():
            continue
        doc = json.loads(p.read_text(encoding='utf-8'))
        hashes = doc.get('publication_sha256', {})
        for name, expected in hashes.items():
            # Entry-point guidance advances in later rounds; only frozen round
            # artifacts are historical identity assertions.
            if not name.startswith(f'benchmark/results/phase6/r6_{n}/') and name != f'benchmark/results/phase6/R6_{n}-REPORT.md':
                continue
            assert digest(name) == expected, name
            checked[name] = expected
    return checked


if __name__ == '__main__':
    import sys
    target = HERE / 'BASELINE.json'
    if sys.argv[1:] == ['record']:
        assert not target.exists(), 'baseline already exists'
        data = {'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                'kernel': 26, 'verified_publications': verify_publications(),
                'protected_files': inventory()}
        target.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
        print(f"Baseline recorded: {len(data['protected_files'])} protected files; "
              f"{len(data['verified_publications'])} publication hashes verified")
    else:
        data = json.loads(target.read_text(encoding='utf-8'))
        assert inventory() == data['protected_files'], 'preservation mismatch'
        verify_publications()
        print(f"Preserved {len(data['protected_files'])} protected files; kernel 26")
