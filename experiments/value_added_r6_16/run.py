"""External restart-per-operation oracle; records all outcomes, including failures."""
import json
import os
import subprocess
import sys
import tempfile
import time
from evidence import HERE, OUT, ROOT, load, now, save, sha, verify
from generate import generate

UID = '00000000-0000-4000-8000-000000000001'
TIME = '2026-01-01T00:00:00Z'


def equal(a, b):
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        return set(a) == set(b) and all(equal(a[k], b[k]) for k in a)
    if isinstance(a, list):
        return len(a) == len(b) and all(equal(x, y) for x, y in zip(a, b))
    return a == b


def pairs(items):
    d = {}
    for k, v in items:
        if k in d:
            raise ValueError('duplicate output key')
        d[k] = v
    return d


def acceptance(domain, stage):
    rows = [('base', c) for c in load(OUT / f'acceptance/{domain}-base.json')]
    for s in range(1, stage + 1):
        rows += [(f's{s}', c) for c in load(OUT / f'sealed/{domain}-s{s}.json')]
    return rows


def evaluate(track, domain, stage, candidate='final'):
    phase = 'base' if stage == 0 else f's{stage}'
    folder = OUT / f'submissions/{track}/{domain}/{phase}'
    path = folder / ('application.py' if track == 'A' else 'intent.json')
    if candidate == 'first':
        path = folder / ('first.py' if track == 'A' else 'first.json')
    build = OUT / f'build/{track}/{domain}/{phase}/{candidate}'
    build.mkdir(parents=True, exist_ok=True)
    result = dict(track=track, domain=domain, stage=stage, candidate=candidate, utc=now(),
                  status='AVAILABLE', validation_seconds=None, observations=[])
    start = time.perf_counter()
    try:
        if track == 'A':
            source, ir = path.read_text(encoding='utf-8'), None
            compile(source, str(path), 'exec')
        else:
            source, ir = generate(load(path), track)
        result['validation_seconds'] = time.perf_counter() - start
        result['source_bytes'] = len(source.encode())
        result['authored_bytes'] = path.stat().st_size
        result['candidate_sha256'] = sha(path)
        application = build / 'application.py'
        with application.open('x', encoding='utf-8', newline='\n') as f:
            f.write(source)
        if ir is not None:
            save(build / 'ir.json', ir)
    except Exception as e:
        result.update(status='UNAVAILABLE', failure_type=type(e).__name__, failure=str(e),
                      validation_seconds=time.perf_counter() - start)
        application = None
    for group, case in acceptance(domain, stage):
        with tempfile.TemporaryDirectory(prefix='lykoi-r616-') as tmp:
            storage = os.path.join(tmp, 'records.json')
            if 'initial' in case:
                with open(storage, 'w', encoding='utf-8') as f:
                    json.dump(case['initial'], f)
            for i, step in enumerate(case['steps']):
                before = open(storage, 'rb').read() if os.path.exists(storage) else None
                row = dict(group=group, case=case['id'], step=i, op=step['op'], expected=step['expected'])
                if application is None:
                    row.update(pass_result=False, failure='UNAVAILABLE')
                else:
                    request = dict(op=step['op'], args=step['args'], providers=dict(uuid_v4=UID, utc_clock=TIME))
                    t = time.perf_counter()
                    try:
                        p = subprocess.run([sys.executable, '-B', str(HERE / 'transport.py'), str(application)],
                            cwd=tmp, input=json.dumps(request), capture_output=True, text=True, timeout=30,
                            env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
                        row.update(returncode=p.returncode, stderr=p.stderr, stdout=p.stdout,
                                   tool_seconds=time.perf_counter() - t)
                        observed = json.loads(p.stdout, object_pairs_hook=pairs) if p.returncode == 0 else None
                        after = open(storage, 'rb').read() if os.path.exists(storage) else None
                        row.update(observed=observed, rejection_bytes_unchanged=(before == after) if step['unchanged'] else None,
                            pass_result=p.returncode == 0 and equal(observed, step['expected']) and
                                (not step['unchanged'] or before == after))
                    except Exception as e:
                        row.update(pass_result=False, failure=type(e).__name__ + ': ' + str(e), tool_seconds=time.perf_counter() - t)
                result['observations'].append(row)
    result['groups'] = {g: dict(passed=sum(r['pass_result'] for r in result['observations'] if r['group'] == g),
                        total=sum(r['group'] == g for r in result['observations'])) for g in ('base', 's1', 's2')}
    result['accepted'] = all(r['pass_result'] for r in result['observations'])
    return result


def main():
    stage = int(sys.argv[1])
    verify(load(OUT / 'TASK-FREEZE.json')['files'])
    verify(load(OUT / 'MODIFICATION-SEAL.json')['files'])
    verify(load(OUT / 'INFRASTRUCTURE-FREEZE.json')['files'])
    files = {}
    for track in ('A', 'B', 'C'):
        for domain in ('kiln', 'custody'):
            folder = OUT / f'submissions/{track}/{domain}' / ('base' if stage == 0 else f's{stage}')
            for p in folder.glob('*'):
                if p.is_file() and p.suffix in ('.py', '.json', '.md'):
                    files[p.relative_to(ROOT).as_posix()] = sha(p)
    save(OUT / f'SUBMISSION-FREEZE-{stage}.json', dict(utc=now(), files=files))
    results = []
    for track in ('A', 'B', 'C'):
        for domain in ('kiln', 'custody'):
            final = evaluate(track, domain, stage)
            save(OUT / f'results/{track}-{domain}-{stage}.json', final)
            results.append({k: v for k, v in final.items() if k != 'observations'})
            first = evaluate(track, domain, stage, 'first')
            save(OUT / f'results/{track}-{domain}-{stage}-first.json', first)
            print(track, domain, stage, final['accepted'], final['groups'])
    save(OUT / f'RESULTS-{stage}.json', dict(utc=now(), results=results))


if __name__ == '__main__':
    main()
