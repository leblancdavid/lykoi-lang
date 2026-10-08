"""Recover only actual author metadata; export transcripts/credentials never saved."""
import json
import subprocess
import sys
import time
from evidence import OUT, load, now, save

SESSIONS = {
    'A/kiln': 'ses_ee230a91dffeygPOyczRkeqY5G',
    'B/custody': 'ses_ee230a914ffdGDakRpTdigCmUg',
    'C/kiln': 'ses_ee230a90effet6SNi8bIE7RQ1W',
    'A/custody': 'ses_ee230a908ffeYxd8QOZJqivbaf',
    'B/kiln': 'ses_ee230a904ffe9ryA0tjOLqbOvz',
    'C/custody': 'ses_ee230a8fbffeEjdvRgJWwkXz39'}


def main():
    stage = int(sys.argv[1])
    rows = []
    for scope, session in SESSIONS.items():
        previous = set()
        for s in range(stage):
            for r in load(OUT / f'TELEMETRY-{s}.json')['sessions']:
                if r['scope'] == scope:
                    previous.update(m['id'] for m in r['metadata'])
        start = time.perf_counter()
        p = subprocess.run(['pwsh', '-NoProfile', '-Command', f'opencode export {session} --sanitize --pure'],
                           capture_output=True, text=True, timeout=60)
        row = dict(scope=scope, session=session, stage=stage, export_returncode=p.returncode,
                   export_seconds=time.perf_counter() - start, metadata=[], api_cost_usd=None,
                   forbidden_markers=[])
        if p.returncode == 0:
            data = json.loads(p.stdout)
            for message in data.get('messages', []):
                info = message.get('info', {})
                if info.get('role') != 'assistant' or info.get('id') in previous:
                    continue
                m = {k: info[k] for k in ('id', 'modelID', 'providerID', 'tokens', 'cost', 'time', 'finish') if k in info}
                m['tools'] = []
                for part in message.get('parts', []):
                    if part.get('type') != 'tool':
                        continue
                    state = part.get('state', {})
                    m['tools'].append(dict(tool=part.get('tool'), status=state.get('status'), time=state.get('time')))
                    arguments = json.dumps(state.get('input', {})).replace('\\', '/').lower()
                    forbidden = ['r6_16/acceptance', 'r6_16/results', 'results-0.json', 'results-1.json',
                                 'results-2.json', 'value_added_r6_16/prepare.py']
                    forbidden += [f'r6_16/submissions/{t.lower()}/' for t in ('A', 'B', 'C') if t != scope[0]]
                    if stage == 0:
                        forbidden.append('r6_16/sealed')
                    elif stage == 1:
                        forbidden += ['-s2.md', '-s2.json']
                    forbidden += ['-s1.json', '-s2.json']
                    hit = [s for s in forbidden if s in arguments]
                    if hit:
                        row['forbidden_markers'].append(dict(tool=part.get('tool'), markers=hit))
                row['metadata'].append(m)
        messages = row['metadata']
        row['model_calls'] = len(messages) if p.returncode == 0 else None
        tokens = [m['tokens'] for m in messages if 'tokens' in m]
        row['usage'] = None if len(tokens) != len(messages) or not tokens else dict(
            input=sum(t.get('input', 0) for t in tokens), output=sum(t.get('output', 0) for t in tokens),
            reasoning=sum(t.get('reasoning', 0) for t in tokens),
            cache_read=sum(t.get('cache', {}).get('read', 0) for t in tokens),
            cache_write=sum(t.get('cache', {}).get('write', 0) for t in tokens))
        times = [m.get('time', {}) for m in messages]
        row['development_wall_seconds'] = ((max(t['completed'] for t in times) - min(t['created'] for t in times)) / 1000
            if times and all('created' in t and 'completed' in t for t in times) else None)
        tools = [t for m in messages for t in m['tools']]
        row['tool_calls'] = len(tools) if messages else None
        tt = [t['time'] for t in tools if isinstance(t.get('time'), dict) and 'start' in t['time'] and 'end' in t['time']]
        row['tool_seconds'] = sum((t['end'] - t['start']) / 1000 for t in tt) if len(tt) == len(tools) and tools else None
        row['budget_first_to_last_tool_seconds'] = (max(t['end'] for t in tt) - min(t['start'] for t in tt)) / 1000 if tt else None
        rows.append(row)
        print(scope, 'calls', row['model_calls'], 'tools', row['tool_calls'], 'wall', row['development_wall_seconds'], 'usage', row['usage'])
    save(OUT / f'TELEMETRY-{stage}.json', dict(utc=now(), sessions=rows,
        independent_separation=False, staged_withholding='CONTAMINATED_UNENFORCED',
        coordinator_usage=None, api_cost_usd=None))


if __name__ == '__main__':
    main()
