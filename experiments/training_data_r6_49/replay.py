"""AI-free, fresh-process state transitions, exact rejection bytes and restart."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from prepare import ROOT, OUT, read, write, canonical, sha, ref, now


def invoke(app, request, directory):
    p = subprocess.run([sys.executable, '-B', str(ROOT / 'experiments/value_added_r6_16/transport.py'),
        str(app)], cwd=directory, input=json.dumps(request), capture_output=True, text=True, timeout=30)
    return p, json.loads(p.stdout) if p.returncode == 0 else None


def run(eid, application=None):
    folder = OUT / 'episodes' / eid
    application = application or folder / 'APPLICATION.py'
    observations = []
    with tempfile.TemporaryDirectory(prefix='lykoi-r649-') as tmp:
        store = Path(tmp) / 'records.json'
        for index, case in enumerate(read(folder / 'ACCEPTANCE.json')['cases']):
            before = store.read_bytes() if store.exists() else None
            p, actual = invoke(application, {k: case[k] for k in ('op', 'args', 'providers')}, tmp)
            after = store.read_bytes() if store.exists() else None
            records = json.loads(after) if after is not None else []
            expected = case['expected_records']
            invariants = all(type(r['label']) is str and bool(r['label'].strip())
                and r['phase'] in read(folder / 'FRC.json')['state_domains']['phase']
                and r['seal'] in ('open', 'closed')
                and (r['phase'] != 'released' or r['seal'] == 'closed') for r in records)
            checks = {'process_success': p.returncode == 0, 'output_match': actual == case['expected'],
                'state_match': records == expected, 'invariants_preserved': invariants,
                'rejection_or_read_bytes_unchanged': not case['rejection_bytes_unchanged'] or before == after}
            observations.append({'index': index, 'request': {k: case[k] for k in ('op', 'args', 'providers')},
                'returncode': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr, 'actual': actual,
                'storage_before_hex': before.hex() if before is not None else None,
                'storage_after_hex': after.hex() if after is not None else None,
                'checks': checks, 'passed': all(checks.values())})
        before = store.read_bytes()
        p, result = invoke(application, {'op': 'list', 'args': {}, 'providers': {}}, tmp)
        restart = {'returncode': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr, 'actual': result,
            'persisted_bytes_hex': before.hex(),
            'passed': p.returncode == 0 and result == {'ok': expected} and store.read_bytes() == before}
    return {'episode_id': eid, 'observations': observations, 'final_restart': restart,
        'passed': all(o['passed'] for o in observations) and restart['passed']}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pass-id', choices=(1, 2), type=int, required=True)
    args = parser.parse_args()
    for seal in ('SOURCE-FREEZE.json', 'CANDIDATE-FREEZE.json'):
        for p, h in read(OUT / seal)['files'].items():
            assert sha(ROOT / p) == h, p
    start = time.perf_counter()
    results = [run(e) for e in ('S01', 'S02')]
    body = {'utc': now(), 'pass_id': args.pass_id, 'ai_calls': 0,
        'execution_ms': round((time.perf_counter() - start) * 1000),
        'candidate_freeze': ref(OUT / 'CANDIDATE-FREEZE.json'), 'results': results,
        'observations_sha256': hashlib.sha256(canonical(results)).hexdigest(),
        'fresh_process_requests': sum(len(r['observations']) + 1 for r in results),
        'passed': all(r['passed'] for r in results)}
    write(OUT / ('REPLAY-%d.json' % args.pass_id), body)
    print(json.dumps({'pass': args.pass_id, 'passed': body['passed'],
        'fresh_process_requests': body['fresh_process_requests'],
        'observations_sha256': body['observations_sha256'], 'execution_ms': body['execution_ms']}))


if __name__ == '__main__':
    main()
