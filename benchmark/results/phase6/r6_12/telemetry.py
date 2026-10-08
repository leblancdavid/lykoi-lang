"""Targeted sanitized CLI metadata probe; never retain transcript/credentials."""
import json
import subprocess
import time

from record import HERE, now, save

SESSIONS = {
    'preparation': 'ses_ee2a25ef2ffedAvqa312t0J36l',
    'A/base': 'ses_ee29b7b0fffeN2wEsLELSrbi10',
    'B/base': 'ses_ee29b7b01ffe6xuCOeXlVFJnzc',
    'C/base': 'ses_ee29b7aeeffeUTHpnFdCHxY47e',
    'C/modification': 'ses_ee29443e2ffe1PsG3vx8FzJXXe',
    'B/modification': 'ses_ee29443d7ffe2gQwC9Kxus8a06',
    'A/modification': 'ses_ee29443cfffe2ngPOZBcLdGPwI',
}


def cli(arguments):
    before = time.perf_counter()
    try:
        process = subprocess.run(['pwsh', '-NoProfile', '-Command', 'opencode ' + arguments],
            capture_output=True, text=True, timeout=60)
        return process, time.perf_counter()-before
    except subprocess.TimeoutExpired:
        return None, time.perf_counter()-before


def main():
    # Model identifiers only, not private configuration or credentials.
    proc, seconds = cli('models --pure')
    identifiers = [] if proc is None else [s.strip() for s in proc.stdout.splitlines()
        if '/' in s and ' ' not in s.strip() and '\\' not in s and not s.startswith('http')]
    inventory = dict(utc=now(), timing='post-evaluation supplementary discovery; not pre-selection attestation',
        command='opencode models --pure', seconds=seconds,
        returncode=None if proc is None else proc.returncode,
        model_identifiers=identifiers, providers=sorted({s.split('/')[0] for s in identifiers}),
        note='Availability/listing does not establish configured credentials or routing; no provider generation dispatched')
    save(HERE / 'MODEL-INVENTORY-SUPPLEMENT.json', inventory)
    rows = []
    for scope, session in SESSIONS.items():
        proc, seconds = cli('export ' + session + ' --sanitize --pure')
        row = dict(scope=scope, task_session_id=session, seconds=seconds,
            command='opencode export <own-task-session> --sanitize --pure',
            returncode=None if proc is None else proc.returncode, export_available=False,
            input_tokens=None, output_tokens=None, reasoning_tokens=None,
            cached_tokens=None, model_calls=None, cost_usd=None)
        if proc is not None and proc.returncode == 0:
            try:
                data = json.loads(proc.stdout)
                messages = data.get('messages', [])
                infos = [m.get('info', m) for m in messages if isinstance(m, dict)]
                assistants = [m for m in infos if m.get('role') == 'assistant']
                row['export_available'] = True
                row['reported_assistant_metadata'] = [
                    {k:m[k] for k in ('modelID', 'providerID', 'tokens', 'cost', 'time', 'finish') if k in m}
                    for m in assistants]
                # Preserve actual provider metadata; no inferred aggregation from source text.
            except (ValueError, AttributeError):
                row['limitation'] = 'No parseable export metadata returned'
        if not row['export_available']:
            row['limitation'] = 'Installed CLI could not export assigned harness task session; no usage data recovered'
        rows.append(row)
    save(HERE / 'TELEMETRY.json', dict(utc=now(), sessions=rows,
        model='openai/gpt-6.1-sol (harness identity)', provider='OpenAI (harness identity)',
        full_prompt_and_routing_attestation=None, task_dispatches=7,
        task_dispatches_are_model_calls=False, cost_estimate_usd=None,
        note='Only own assigned session IDs probed. Transcripts and stderr not retained. Missing counts stay null.'))
    print(json.dumps(dict(models_listed=len(identifiers),
                         sessions_exported=sum(r['export_available'] for r in rows))))


if __name__ == '__main__':
    main()
