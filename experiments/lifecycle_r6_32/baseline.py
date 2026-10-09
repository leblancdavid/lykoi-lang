"""Capture identities before R6.32 implementation; never open withheld material."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'benchmark/results/phase6/r6_32'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    serialized = json.dumps(value, indent=2, sort_keys=True) + '\n'
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(serialized)


def inventory():
    previous = ROOT / 'benchmark/results/phase6/r6_31'
    receipt = json.loads((previous / 'VERIFICATION.json').read_text())
    manifest = json.loads((previous / 'PUBLICATION-IDENTITIES.json').read_text())
    assert all(receipt['checks'].values()), receipt
    assert receipt['manifest_sha256'] == sha(previous / 'PUBLICATION-IDENTITIES.json')
    # Historical inventory includes opaque source hashes; withheld paths are excluded
    # before any file access, including hashing.
    pins = json.loads((ROOT / 'benchmark/results/phase6/r6_30/BASELINE.json').read_text())['protected_files']
    for folder in ('r6_30', 'r6_31'):
        base = ROOT / 'benchmark/results/phase6' / folder
        publication = json.loads((base / 'PUBLICATION-IDENTITIES.json').read_text())
        for name, meta in publication['files'].items():
            assert 'p6_a05' not in name.lower().replace('-', '_')
            assert sha(ROOT / name) == meta['sha256'], name
            pins[name] = meta['sha256']
        for name in ('PUBLICATION-IDENTITIES.json', 'VERIFICATION.json'):
            pins[(base / name).relative_to(ROOT).as_posix()] = sha(base / name)
    extras = ['experiments/value_added_r6_16/generate.py',
              'experiments/value_added_r6_16/schema_check.py',
              'src/air_compiler/semantics.py', 'src/air_compiler/profiles.py',
              'src/air_compiler/mutable_values.py',
              'benchmark/results/phase6/r6_30/experiment.py',
              'benchmark/results/phase6/r6_30/runtime.py',
              'benchmark/results/phase6/r6_16/submissions/C/kiln/base/intent.json']
    for name in extras:
        pins[name] = sha(ROOT / name)
    mismatches = [p for p, h in pins.items() if sha(ROOT / p) != h]
    assert not mismatches, mismatches
    implementation = {p: h for p, h in pins.items()
                      if p.startswith('src/') or p in extras or p.endswith(
                          ('composition.py', 'interpreter.py', 'r6_23/adapter.py'))}
    save(OUT / 'BASELINE.json', dict(round='R6.32', kernel=26,
         head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
         initial_git_status='clean (checked before adding baseline capture script)',
         protected_files=pins, protected_count=len(pins), mismatches=mismatches,
         implementations=implementation, R6_31_publication_verified=True,
         R6_31_manifest_sha256=sha(previous / 'PUBLICATION-IDENTITIES.json'),
         R6_31_report_sha256=manifest['files']['benchmark/results/phase6/R6_31-REPORT.md']['sha256'],
         model_calls=0, P6_A04_acceptance=False, P6_A05_access=False))
    print('Protected baseline verified:', len(pins))


if __name__ == '__main__':
    inventory()
