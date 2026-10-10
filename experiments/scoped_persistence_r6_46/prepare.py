"""Read-only historical verification and preimplementation fixture freeze."""
import hashlib
import json
from pathlib import Path
import subprocess
from datetime import datetime, timezone
from matrix import fixtures

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = ROOT / 'benchmark/results/phase6/r6_46'


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='\n') as f:
        f.write(json.dumps(value, indent=2, sort_keys=True) + '\n')


def verify(files):
    for name, identity in files.items():
        expected = identity if isinstance(identity, str) else identity['sha256']
        assert sha(ROOT / name) == expected, name
    return len(files)


def main():
    assert not OUT.exists()
    files = dict(load(ROOT / 'benchmark/results/phase6/r6_44/BASELINE.json')['protected_files'])
    counts = {}
    for round_ in ('44', '45'):
        folder = ROOT / f'benchmark/results/phase6/r6_{round_}'
        manifest = load(folder / 'PUBLICATION-IDENTITIES.json')
        counts[round_] = verify(manifest['files'])
        receipt = load(folder / 'VERIFICATION.json')
        assert receipt['passed'] and receipt['manifest_sha256'] == sha(folder / 'PUBLICATION-IDENTITIES.json')
        files.update({k: v['sha256'] for k, v in manifest['files'].items()})
        for name in ('PUBLICATION-IDENTITIES.json', 'VERIFICATION.json'):
            p = folder / name
            files[p.relative_to(ROOT).as_posix()] = sha(p)
    verify(files)
    for name in ('r6_44/FREEZE.json', 'r6_16/TASK-FREEZE.json'):
        counts[name] = verify(load(ROOT / 'benchmark/results/phase6' / name)['files'])
    assert load(ROOT / 'benchmark/results/phase5c/R5_114-KERNEL-ACCOUNTING.json')['final_count'] == 26
    save(OUT / 'BASELINE.json', dict(kernel=26, protected_files=files, protected_count=len(files),
        publication_and_freeze_counts=counts, preservation_failures=[],
        head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        initial_status='clean before any editing; new R6.46 files only',
        kernel_basis='unchanged R5.114 accounting and production identities; no independent recount'))
    save(OUT / 'MATRIX.json', fixtures())
    authority = ['benchmark/results/phase6/r6_16/tasks/COMMON.md',
        'experiments/stateful_modification_r6_44/CONTRACT.md',
        'benchmark/results/phase6/r6_45/PROSPECTIVE-ACCEPTANCE.md']
    save(OUT / 'EXPECTATION-CHECK.json', dict(method='source-based candidate-output-independent same-agent review',
        independent_human_review=False, checked_before_implementation=True,
        authority={p: sha(ROOT / p) for p in authority}, rows=18, observations=25,
        findings='All K01–K18 supported: list-only/no migrations; exact record validity; same-schema old lists; store-first/lookup/guard/input order; byte preservation. V01–V04 excluded.',
        source_to_rows={'COMMON:3–13': ['K01','K02','K03','K04','K05','K08','K09','K10','K11','K12','K13'],
            'CONTRACT:44–58': ['K06','K07','K14','K15','K16','K17','K18']}))
    names = authority + [p.relative_to(ROOT).as_posix() for p in
        (HERE / 'CONTRACT.md', HERE / 'matrix.py', OUT / 'MATRIX.json', OUT / 'EXPECTATION-CHECK.json')]
    save(OUT / 'FREEZE.json', dict(utc=datetime.now(timezone.utc).isoformat(),
        files={p: sha(ROOT / p) for p in names}, status='FROZEN_BEFORE_IMPLEMENTATION'))
    print(json.dumps(dict(preserved=len(files), counts=counts, frozen_rows=18, observations=25)))


if __name__ == '__main__':
    main()
