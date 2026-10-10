"""Fresh CLI sessions, sealed submissions and actual exported usage; no scoring."""
import json
import re
import subprocess
import sys
import time
import shutil
from run import ROOT, OUT, TEMP, load, save, text, now, sha, verify


def safe(raw):
    # Preserve evidence, but fail closed if an unexpected credential-like token appears.
    if re.search(r'\bsk-[A-Za-z0-9_-]{24,}|Bearer\s+[A-Za-z0-9_.-]{24,}', raw):
        raise ValueError('credential-like data: raw export withheld')
    return raw


def export(session):
    start = time.perf_counter()
    p = subprocess.run(['pwsh', '-NoProfile', '-Command', f'opencode export {session} --sanitize --pure'],
                       capture_output=True, text=True, timeout=60)
    elapsed = time.perf_counter() - start
    if p.returncode:
        return dict(returncode=p.returncode, stderr=safe(p.stderr), seconds=elapsed), None
    data = json.loads(safe(p.stdout))
    return dict(returncode=0, seconds=elapsed), data


def usage(data):
    if data is None:
        return dict(model_calls=None, tool_calls=None, tokens=None, api_billing_usd=None)
    rows, tools = [], []
    for m in data.get('messages', []):
        info = m.get('info', {})
        if info.get('role') != 'assistant': continue
        r = {k: info[k] for k in ('id', 'providerID', 'modelID', 'tokens', 'cost', 'time', 'finish') if k in info}
        r['tools'] = []
        for part in m.get('parts', []):
            if part.get('type') != 'tool': continue
            state = part.get('state', {})
            t = dict(tool=part.get('tool'), status=state.get('status'), time=state.get('time'), input=state.get('input'))
            r['tools'].append(t); tools.append(t)
        rows.append(r)
    tokens = [r.get('tokens') for r in rows]
    def sum_field(path):
        vals = []
        for t in tokens:
            v = t
            for key in path:
                if not isinstance(v, dict) or key not in v: return None
                v = v[key]
            vals.append(v)
        return sum(vals) if vals else None
    intervals = [t.get('time') for t in tools]
    tool_seconds = (sum((v['end'] - v['start']) / 1000 for v in intervals)
                    if intervals and all(isinstance(v, dict) and 'start' in v and 'end' in v for v in intervals) else None)
    return dict(model_calls=len(rows), visible_completions_only=True, tool_calls=len(tools),
        tokens=dict(input=sum_field(['input']), output=sum_field(['output']), reasoning=sum_field(['reasoning']),
                    cached_input=sum_field(['cache', 'read']), cache_write=sum_field(['cache', 'write'])),
        reported_cost_usd=sum(r['cost'] for r in rows) if rows and all('cost' in r for r in rows) else None,
        api_billing_usd=None, hidden_retries=None, tool_seconds_nested=tool_seconds, metadata=rows)


def main(track):
    verify(load(OUT / 'FREEZE.json')['files'])
    assert track in ('A', 'B') and not (OUT / f'AUTHOR-{track}.json').exists()
    if track == 'B': assert (OUT / 'AUTHOR-A.json').exists()
    prompt = OUT / f'prompts/{track}.txt'
    work = TEMP / track
    cmd = (f"opencode run 'Follow the attached R6.44 participant prompt; implement and submit.' "
           f"--pure --model openai/gpt-6.1-sol --variant high --format json --auto "
           f"--dir '{work}' --title 'R6.44 participant {track}' --file '{prompt}'")
    begin = now(); start = time.perf_counter()
    proc = subprocess.Popen(['pwsh', '-NoProfile', '-Command', cmd], cwd=work,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    timed_out = False
    try:
        stdout, stderr = proc.communicate(timeout=480)
    except subprocess.TimeoutExpired:
        timed_out = True
        subprocess.run(['taskkill', '/PID', str(proc.pid), '/T', '/F'], capture_output=True)
        stdout, stderr = proc.communicate(timeout=30)
    wall = time.perf_counter() - start
    text(OUT / f'authoring/{track}/events.jsonl', safe(stdout))
    text(OUT / f'authoring/{track}/stderr.txt', safe(stderr))
    events = []
    for line in stdout.splitlines():
        try: events.append(json.loads(line))
        except ValueError: pass
    sessions = {e['sessionID'] for e in events if 'sessionID' in e}
    session = next(iter(sessions)) if len(sessions) == 1 else None
    seal = {}
    for p in sorted(work.rglob('*')):
        if p.is_file() and '__pycache__' not in p.parts and not p.name.endswith('.pyc'):
            relative = p.relative_to(work)
            dst = OUT / f'submissions/{track}' / relative
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(p, dst)
            seal[dst.relative_to(ROOT).as_posix()] = sha(dst)
    exp, data = export(session) if session else (dict(returncode=None, seconds=None), None)
    if data is not None: save(OUT / f'authoring/{track}/session-export.json', data)
    row = dict(track=track, utc_start=begin, utc_end=now(), command=cmd, session=session, process_returncode=proc.returncode,
        process_exited=True, timed_out=timed_out, participant_wall_seconds=wall, export=exp,
        telemetry=usage(data), files=seal, effective_reasoning_configuration=None, context_limit=None,
        tool_isolation='cooperative scope plus separate starting directories; no OS attestation')
    save(OUT / f'AUTHOR-{track}.json', row)
    print(json.dumps({k: v for k, v in row.items() if k not in ('files', 'telemetry')}, indent=2))
    print(json.dumps({k: v for k, v in row['telemetry'].items() if k != 'metadata'}, indent=2))


if __name__ == '__main__':
    main(sys.argv[1])
