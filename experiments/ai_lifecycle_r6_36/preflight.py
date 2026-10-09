"""One neutral child request; lifecycle content is never loaded into its prompt."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from urllib.parse import urlsplit
from tools import TOOLS

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = ROOT / 'benchmark/results/phase6/r6_36'
TEMP = Path('C:/Users/lblan/AppData/Local/Temp/opencode/r6_36')
EXE = str(Path(os.environ['APPDATA']) / 'npm/node_modules/opencode-ai/bin/opencode.exe')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, obj):
    assert Path(path).parent.is_dir()
    with Path(path).open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(json.dumps(obj, indent=2, sort_keys=True) + '\n')


def raw(path, text):
    with Path(path).open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(text)


def sanitize(value):
    if isinstance(value, dict):
        return {k: ('<REDACTED_RESPONSE_CREDENTIAL>' if k.lower() in
            ('authorization', 'cookie', 'set-cookie', 'x-api-key', 'apikey', 'access',
             'refresh', 'access_token', 'refresh_token', 'id_token') else sanitize(v))
            for k, v in value.items()}
    if isinstance(value, list):
        return [sanitize(v) for v in value]
    if isinstance(value, str):
        # ResponseBody may be JSON encoded inside a string.
        try:
            decoded = json.loads(value)
            if isinstance(decoded, (dict, list)):
                return json.dumps(sanitize(decoded), separators=(',', ':'))
        except (ValueError, TypeError):
            pass
        value = re.sub(r'\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}', '<REDACTED>', value)
        value = re.sub(r'\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+', '<REDACTED>', value)
    return value


def environment(config):
    env = os.environ.copy()
    env.pop('OPENCODE_DISABLE_DEFAULT_PLUGINS', None)
    env.update(OPENCODE_PURE='1', OPENCODE_DISABLE_PROJECT_CONFIG='1',
        OPENCODE_DISABLE_EXTERNAL_SKILLS='1', OPENCODE_DISABLE_CLAUDE_CODE_SKILLS='1',
        OPENCODE_CONFIG_CONTENT=json.dumps(config))
    assert 'OPENCODE_DISABLE_DEFAULT_PLUGINS' not in env
    assert env['OPENCODE_PURE'] == '1'
    return env


def preserve():
    prior = ROOT / 'benchmark/results/phase6/r6_35'
    pins = dict(load(prior / 'BASELINE.json')['protected_files'])
    for round_id in ('33', '34', '35'):
        folder = ROOT / ('benchmark/results/phase6/r6_' + round_id)
        receipt = load(folder / 'VERIFICATION.json')
        assert receipt['passed'] and receipt['kernel'] == 26
        assert sha(folder / 'PUBLICATION-IDENTITIES.json') == receipt['manifest_sha256']
        for name, meta in load(folder / 'PUBLICATION-IDENTITIES.json')['files'].items():
            assert 'p6_a05' not in name.lower().replace('-', '_')
            assert sha(ROOT / name) == meta['sha256']
            assert (ROOT / name).stat().st_size == meta['bytes']
            pins[name] = meta['sha256']
        for name in ('PUBLICATION-IDENTITIES.json', 'VERIFICATION.json'):
            pins[(folder / name).relative_to(ROOT).as_posix()] = sha(folder / name)
    for name, pin in pins.items():
        assert sha(ROOT / name) == pin, name
    frozen = load(ROOT / 'benchmark/results/phase6/r6_33/FREEZE.json')['inputs']
    assert all(sha(ROOT / name) == pin for name, pin in frozen.items())
    save(OUT / 'BASELINE.json', dict(kernel=26, protected_files=pins, protected_count=len(pins),
        R6_33_freeze_verified=True, R6_33_R6_34_R6_35_publications_verified=True,
        initial_worktree='Only existing R6.35 files were untracked before R6.36 additions',
        head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()))


def config():
    permission = {'*': 'deny', 'r636_lykoi_*': 'allow'}
    return {'$schema': 'https://opencode.ai/config.json', 'share': 'disabled',
        'autoupdate': False, 'snapshot': False, 'permission': permission,
        'agent': {'r636-author': dict(mode='primary', model='openai/gpt-6.1-sol',
            variant='high', description='Bounded Lykoi symbolic participant', permission=permission,
            prompt='Follow only the supplied request. Do not access files or other tools. '
                   'Only Lykoi construction tools are permitted. Never invent semantic operations.')},
        'default_agent': 'r636-author',
        'mcp': {'r636': dict(type='local', command=[sys.executable, '-B', str(HERE / 'tools.py')], enabled=True)}}


def main():
    start = time.perf_counter()
    assert OUT.parent.is_dir() and TEMP.parent.is_dir()
    OUT.mkdir(exist_ok=False)
    TEMP.mkdir(exist_ok=False)
    preserve()
    cfg = config()
    env = environment(cfg)
    version = subprocess.run([EXE, '--version'], env=env, cwd=TEMP, capture_output=True, timeout=30)
    assert version.stdout.decode().strip() == '1.18.32'
    credentials = subprocess.run([EXE, 'auth', 'list'], env=env, cwd=TEMP, capture_output=True, timeout=30)
    listing = re.sub(r'\x1b\[[0-9;]*m', '', credentials.stdout.decode())
    assert re.search(r'OpenAI\s+oauth', listing, re.I), 'Stored OpenAI OAuth not listed'
    save(OUT / 'ENVIRONMENT-CHANGE.json', dict(removed=['OPENCODE_DISABLE_DEFAULT_PLUGINS'],
        disable_default_plugins_absent='OPENCODE_DISABLE_DEFAULT_PLUGINS' not in env,
        OPENCODE_PURE=env['OPENCODE_PURE'], built_in_plugins_eligible=True,
        external_plugins_disabled=True, global_environment_modified=False,
        OPENAI_API_KEY_inherited_unchanged=True, OPENAI_API_KEY_present='OPENAI_API_KEY' in env,
        stored_OpenAI_OAuth_listed=True, credential_store_read=False,
        authentication_headers_overridden=False, endpoints_overridden=False))
    save(OUT / 'PREFLIGHT-CONFIG.json', dict(config=cfg, tools=TOOLS, provider='openai',
        model='gpt-6.1-sol', variant='high', requested_reasoning={'reasoningEffort': 'high'},
        effective_reasoning=None, effective_authentication=None, opencode_version='1.18.32',
        budget={'CLI_invocations': 1, 'deadline_seconds': 90}, lifecycle_requirements_included=False))
    prompt = 'Reply NEUTRAL_OK followed by the names of all four available Lykoi construction tools. Do not invoke tools.'
    raw(OUT / 'NEUTRAL-PROMPT.txt', prompt + '\n')
    save(OUT / 'PREFLIGHT-FREEZE.json', dict(utc=datetime.now(timezone.utc).isoformat(), model_calls=0,
        inputs={p.relative_to(ROOT).as_posix(): sha(p) for p in
            (HERE / 'PROTOCOL.md', HERE / 'preflight.py', HERE / 'tools.py',
             OUT / 'PREFLIGHT-CONFIG.json', OUT / 'ENVIRONMENT-CHANGE.json', OUT / 'NEUTRAL-PROMPT.txt')}))
    t = time.perf_counter()
    timeout = False
    try:
        run = subprocess.run([EXE, 'run', '--format', 'json', '--print-logs', '--log-level', 'DEBUG',
            '--model', 'openai/gpt-6.1-sol', '--variant', 'high', '--agent', 'r636-author',
            '--title', 'R6.36 neutral access preflight', prompt], cwd=TEMP, env=env,
            capture_output=True, timeout=90)
        stdout, stderr, code = run.stdout, run.stderr, run.returncode
    except subprocess.TimeoutExpired as exc:
        stdout, stderr, code = exc.stdout or b'', exc.stderr or b'', None
        timeout = True
    elapsed = time.perf_counter() - t
    events = [sanitize(json.loads(line)) for line in stdout.decode('utf-8', errors='replace').splitlines()
              if line.startswith('{')]
    raw(OUT / 'NEUTRAL-EVENTS.jsonl', ''.join(json.dumps(e) + '\n' for e in events))
    # Retain no raw stderr. Keep allowlisted endpoint locations and plugin names only.
    logs = stderr.decode('utf-8', errors='replace')
    endpoints = []
    for url in re.findall(r'https://[^\s"<>]+', logs + json.dumps(events)):
        parsed = urlsplit(url.rstrip('.,;'))
        if parsed.hostname in ('chatgpt.com', 'api.openai.com', 'auth.openai.com'):
            item = dict(scheme=parsed.scheme, host=parsed.hostname,
                        path=parsed.path, query_omitted=bool(parsed.query))
            if item not in endpoints:
                endpoints.append(item)
    plugin_lines = [line for line in logs.splitlines() if 'plugin' in line.lower()]
    plugins = sorted(set(re.findall(r'\b(?:CodexAuthPlugin|OpenAIAuthPlugin|ChatGPTAuthPlugin)\b', '\n'.join(plugin_lines))))
    save(OUT / 'ROUTE-EVIDENCE.json', dict(endpoints=endpoints, built_in_plugin_names=plugins,
        stderr_bytes=len(stderr), stderr_raw_published=False,
        route_source='Allowlisted host/path from captured runtime stderr or sanitized JSON events',
        effective_authentication=None, effective_authentication_missing_reason='No credential-free authentication attestation exposed',
        stored_oauth_is_not_effective_route_attestation=True, headers_read=False,
        CLI_internal_HTTP_attempts=None, CLI_internal_retries='Not observable/control-attested; no coordinator retry'))
    finishes = [e['part'] for e in events if e.get('type') == 'step_finish']
    texts = [e['part']['text'] for e in events if e.get('type') == 'text']
    errors = [e for e in events if e.get('type') == 'error']
    tool_events = [e for e in events if e.get('type') == 'tool_use']
    completion = not timeout and code == 0 and not errors and bool(finishes) and 'NEUTRAL_OK' in '\n'.join(texts)
    discovery = (OUT / 'MCP-DISCOVERY.jsonl').exists() and all(tool['name'] in '\n'.join(texts) for tool in TOOLS)
    passed = completion and discovery and not tool_events
    status = 'PASSED' if passed else ('R6_36_PROVIDER_ACCESS_BLOCKED' if errors or timeout else 'R6_36_PROTOCOL_HALT')
    save(OUT / 'PREFLIGHT-RESULT.json', dict(status=status, neutral_completion=completion,
        four_tool_model_discovery=discovery, MCP_tools_list_observed=(OUT / 'MCP-DISCOVERY.jsonl').exists(),
        passed=passed, returncode=code, timeout=timeout, wall_seconds=elapsed,
        total_preflight_seconds=time.perf_counter()-start, errors=errors, step_finishes=finishes,
        texts=texts, tool_calls=len(tool_events), participant_requirement_exposure=False,
        usage=finishes or None, usage_missing_reason=None if finishes else 'No completed step_finish usage',
        session_ids=sorted({e['sessionID'] for e in events if e.get('sessionID')}),
        coordinator_retries=0, provider_switches=0, purchases=0))
    print('R6.36 neutral gate:', status, '; seconds:', round(elapsed, 6))


if __name__ == '__main__':
    main()
