"""R6.13 write-once evidence inventory and preservation checks."""
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OLD = HERE.parent / 'r6_12'


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def save(path, value):
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(json.dumps(value, indent=2) + '\n')


def verify_map(base, identities):
    for name, identity in identities.items():
        if sha(base / name) != identity:
            raise ValueError(f'Identity mismatch: {base / name}')


def baseline():
    verify_map(OLD, load(OLD / 'FREEZE.json')['files'])
    verify_map(ROOT, load(OLD / 'BASELINE.json')['protected'])
    verify_map(ROOT, load(OLD / 'PUBLICATION-IDENTITIES.json')['files'])
    candidates = {}
    results = []
    for path in sorted(OLD.glob('workspaces/*/*/*/RESULT-*.json')):
        result = load(path)
        verify_map(path.parent, result['artifacts'])
        candidate = path.parent / 'attempt1.py'
        candidates[candidate.relative_to(ROOT).as_posix()] = sha(candidate)
        results.append({k: result[k] for k in ('track', 'task', 'stage', 'passed_cases',
                                              'total_cases', 'elapsed_seconds', 'repairs')})
    preserved = dict(load(OLD / 'BASELINE.json')['protected'])
    for path in sorted(OLD.rglob('*')):
        if path.is_file():
            preserved[path.relative_to(ROOT).as_posix()] = sha(path)
    report = HERE.parent / 'R6_12-REPORT.md'
    preserved[report.relative_to(ROOT).as_posix()] = sha(report)
    status = subprocess.check_output(['git', 'status', '--short'], cwd=ROOT, text=True)
    save(HERE / 'BASELINE.json', dict(utc=now(), kernel=26, initial_status=status,
         original_freeze_verified=True, publication_identities_verified=True,
         candidate_identities=candidates, historical_results=results,
         historical_counts=dict(base=80, new_modification=24, repeated_original=48,
                                scored_observations=152, prior_replays=152),
         preserved=preserved, python=sys.version))
    print(f'Baseline verified: {len(candidates)} candidates, {len(preserved)} preserved files')


def verify():
    record = load(HERE / 'BASELINE.json')
    verify_map(ROOT, record['preserved'])
    verify_map(ROOT, record['candidate_identities'])
    if load(ROOT / 'benchmark/results/phase5c/R5_114-KERNEL-ACCOUNTING.json')['final_count'] != 26:
        raise ValueError('Kernel changed')
    print(f'Preserved {len(record["preserved"])} file identities; kernel 26')


if __name__ == '__main__':
    {'baseline': baseline, 'verify': verify}[sys.argv[1]]()
