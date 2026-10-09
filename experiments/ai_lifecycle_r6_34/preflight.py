"""Access-first evidence capture; does not load frozen lifecycle task content."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = ROOT / 'benchmark/results/phase6/r6_34'
TEMP = Path('C:/Users/lblan/AppData/Local/Temp/opencode/r6_34_preflight')
EXE = str(Path(os.environ['APPDATA']) / 'npm/node_modules/opencode-ai/bin/opencode.exe')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, value):
    with Path(path).open('x', encoding='utf-8', newline='\n') as f:
        f.write(json.dumps(value, indent=2, sort_keys=True) + '\n')


def raw(path, value):
    with Path(path).open('xb') as f:
        f.write(value)


def redact(value):
    if isinstance(value, dict):
        return {k: ('<REDACTED_RESPONSE_CREDENTIAL>' if k.lower() in
            ('authorization', 'cookie', 'set-cookie', 'x-api-key', 'apikey', 'access', 'refresh')
            else redact(v)) for k, v in value.items()}
    if isinstance(value, list):
        return [redact(v) for v in value]
    return value


def baseline():
    previous = ROOT / 'benchmark/results/phase6/r6_33'
    pins = load(previous / 'BASELINE.json')['protected_files']
    counts = {}
    for round_id in ('32', '33'):
        folder = ROOT / ('benchmark/results/phase6/r6_' + round_id)
        manifest = folder / 'PUBLICATION-IDENTITIES.json'
        receipt = load(folder / 'VERIFICATION.json')
        assert receipt['passed'] and receipt['kernel'] == 26
        assert sha(manifest) == receipt['manifest_sha256']
        entries = load(manifest)['files']
        for name, meta in entries.items():
            assert 'p6_a05' not in name.lower().replace('-', '_')
            assert sha(ROOT / name) == meta['sha256'] and (ROOT / name).stat().st_size == meta['bytes'], name
            pins[name] = meta['sha256']
        for name in ('PUBLICATION-IDENTITIES.json', 'VERIFICATION.json'):
            pins[(folder / name).relative_to(ROOT).as_posix()] = sha(folder / name)
        counts['R6_' + round_id] = len(entries)
    for name, pin in pins.items():
        assert sha(ROOT / name) == pin, name
    # Verify the preserved error without sending it to a participant.
    error = load(previous / 'calls/01/stdout.jsonl')['error']['data']
    assert error['statusCode'] == 429
    save(OUT / 'BASELINE.json', dict(kernel=26, protected_files=pins, protected_count=len(pins),
        publications_verified=counts, R6_33_HTTP429_preserved=True,
        historical_error_sha256=sha(previous / 'calls/01/stdout.jsonl'),
        initial_git_status='clean', head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()))


def main():
    start = time.perf_counter()
    assert OUT.parent.exists() and TEMP.parent.exists()
    OUT.mkdir(exist_ok=False)
    TEMP.mkdir(exist_ok=False)
    baseline()
    inventory = {}
    for name, args in [('credentials', ['auth', 'list']), ('models', ['models']),
                       ('openai_metadata', ['models', 'openai', '--verbose']), ('version', ['--version'])]:
        run = subprocess.run([EXE] + args, capture_output=True, timeout=60)
        text = re.sub(r'\x1b\[[0-9;]*m', '', run.stdout.decode('utf-8')).replace('\r\n', '\n')
        raw(OUT / (name + '.txt'), text.encode('utf-8'))
        inventory[name] = dict(returncode=run.returncode, sha256=sha(OUT / (name + '.txt')))
    metadata_text = (OUT / 'openai_metadata.txt').read_text(encoding='utf-8')
    metadata, _ = json.JSONDecoder().raw_decode(metadata_text.split('openai/gpt-6.1-sol\n', 1)[1].lstrip())
    assert metadata['capabilities']['toolcall']
    save(OUT / 'INVENTORY.json', dict(commands=inventory,
        credential_values_read=False, catalog_is_not_access_evidence=True,
        selected_provider='openai', selected_model='gpt-6.1-sol',
        rationale='Existing authorized R6.33 route, advertised frontier reasoning and tool calling; no provider switch',
        alternatives_probed=False))
    permission = {'*': 'deny', 'r634_inert_echo': 'allow'}
    config = {'$schema': 'https://opencode.ai/config.json', 'share': 'disabled',
        'autoupdate': False, 'snapshot': False, 'permission': permission,
        'agent': {'r634-preflight': dict(description='Neutral access and inert tool preflight',
            mode='primary', model='openai/gpt-6.1-sol', variant='high', permission=permission,
            steps=2, prompt='Follow the tiny neutral request. Only inert echo is permitted. No file access or other tools.')},
        'default_agent': 'r634-preflight',
        'mcp': {'r634': dict(type='local', command=[sys.executable, str(HERE / 'inert.py')], enabled=True)}}
    save(OUT / 'PREFLIGHT-CONFIG.json', dict(config=config, metadata=metadata,
        requested_reasoning=metadata['variants']['high'], effective_reasoning=None,
        effective_tool_schema=None, provider_hidden_context_attestation=None,
        budget=dict(max_CLI_invocations=2, seconds_per_invocation=90, total_seconds=240,
                    newly_purchased_USD=0, existing_consumption_ceiling_USD=1),
        lifecycle_requirements_included=False))
    save(OUT / 'PREFLIGHT-FREEZE.json', dict(utc=datetime.now(timezone.utc).isoformat(),
        participant_calls=0, inputs={p.relative_to(ROOT).as_posix(): sha(p)
        for p in (HERE / 'PROTOCOL.md', HERE / 'preflight.py', HERE / 'inert.py', OUT / 'PREFLIGHT-CONFIG.json')}))
    env = os.environ.copy()
    env.update(OPENCODE_DISABLE_PROJECT_CONFIG='1', OPENCODE_CONFIG_CONTENT=json.dumps(config),
        OPENCODE_DISABLE_EXTERNAL_SKILLS='1', OPENCODE_DISABLE_CLAUDE_CODE_SKILLS='1',
        OPENCODE_PURE='1', OPENCODE_DISABLE_DEFAULT_PLUGINS='1')
    calls = []
    passed = True
    for number, prompt in enumerate(('Reply exactly NEUTRAL_OK. Do not call tools.',
        'Discover inert_echo and invoke it once with value neutral. Then reply exactly INERT_OK.'), 1):
        folder = OUT / f'preflight-{number:02}'
        folder.mkdir()
        raw(folder / 'prompt.txt', prompt.encode())
        t = time.perf_counter()
        timed_out = False
        try:
            child = subprocess.run([EXE, 'run', '--format', 'json', '--model', 'openai/gpt-6.1-sol',
                '--variant', 'high', '--agent', 'r634-preflight', prompt],
                cwd=TEMP, env=env, capture_output=True, timeout=min(90, max(1, 240-(t-start))))
            stdout, stderr, code = child.stdout, child.stderr, child.returncode
        except subprocess.TimeoutExpired as exc:
            stdout, stderr, code = exc.stdout or b'', exc.stderr or b'', None
            timed_out = True
        events = [redact(json.loads(line)) for line in stdout.decode('utf-8').splitlines() if line.startswith('{')]
        raw(folder / 'stdout.jsonl', ('\n'.join(json.dumps(e, separators=(',', ':')) for e in events)+'\n').encode())
        raw(folder / 'stderr.txt', stderr)
        finishes = [e['part'] for e in events if e.get('type') == 'step_finish']
        texts = [e['part']['text'].strip() for e in events if e.get('type') == 'text']
        tools = [e for e in events if e.get('type') == 'tool_use']
        errors = [e for e in events if e.get('type') == 'error']
        ok = not timed_out and not errors and code == 0 and bool(finishes) and (
            texts == ['NEUTRAL_OK'] if number == 1 else bool(tools) and texts == ['INERT_OK'])
        record = dict(invocation=number, wall_seconds=time.perf_counter()-t, returncode=code,
            timeout=timed_out, passed=ok, step_finishes=finishes, tool_events=tools,
            errors=errors, usage=None if not finishes else finishes,
            session_ids=sorted({e['sessionID'] for e in events if e.get('sessionID')}))
        save(folder / 'MEASUREMENT.json', record)
        calls.append(record)
        if not ok:
            passed = False
            break
    save(OUT / 'PREFLIGHT-RESULT.json', dict(status='PASSED' if passed else 'PROVIDER_ACCESS_BLOCKED',
        neutral_passed=calls[0]['passed'], inert_gate='PASSED' if passed else 'NOT_REACHED',
        calls=calls, total_wall_seconds=time.perf_counter()-start,
        participant_requirement_exposure=False, model_switches=0,
        credential_publication=False, purchases=0, provider_HTTP_attempts=None,
        billing=None, usage_missing_reason='Failed response has no provider step_finish usage' if not passed else None))
    print('R6.34 neutral preflight:', 'PASSED' if passed else 'PROVIDER_ACCESS_BLOCKED')


if __name__ == '__main__':
    main()
