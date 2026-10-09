"""Bounded neutral discovery and invocation, no historical task reads."""
import json
import os
import shutil
import subprocess
import sys
import time
from common import HERE, ROOT, TEMP, now, read, save, sha

MODEL = 'openai/gpt-6.1-sol'
EXECUTABLE = __import__('pathlib').Path(os.environ['APPDATA']) / 'npm/node_modules/opencode-ai/bin/opencode.exe'

def baseline():
    assert not (HERE / 'BASELINE.json').exists()
    old = HERE.parent / 'r6_26'
    pins = json.loads((old / 'BASELINE.json').read_text())['protected_files']
    verified = {}
    for round_name in ('r6_25', 'r6_26'):
        directory = HERE.parent / round_name
        receipt = json.loads((directory / 'VERIFICATION.json').read_text())
        manifest = directory / 'PUBLICATION-IDENTITIES.json'
        assert receipt['passed'] and receipt['publication_manifest_sha256'] == sha(manifest)
        publication = json.loads(manifest.read_text())
        for p, identity in publication['files'].items():
            assert sha(ROOT / p) == identity['sha256'], p
            pins[p] = identity['sha256']
        for name in ('PUBLICATION-IDENTITIES.json', 'VERIFICATION.json'):
            p = directory / name
            pins[p.relative_to(ROOT).as_posix()] = sha(p)
        verified[round_name] = dict(manifest_sha256=sha(manifest), files=len(publication['files']))
    assert all(sha(ROOT / p) == h for p, h in pins.items())
    save('BASELINE.json', dict(timestamp=now(), protected_files=pins, protected_count=len(pins), publications=verified, kernel=26,
                              git_status=subprocess.run(['git', 'status', '--short'], capture_output=True, text=True).stdout))

def config(label, mode):
    return {'$schema': 'https://opencode.ai/config.json', 'model': MODEL, 'small_model': MODEL,
            'share': 'disabled', 'autoupdate': False, 'snapshot': False, 'instructions': [], 'plugin': [],
            'lsp': False, 'formatter': False, 'compaction': {'auto': False}, 'enabled_providers': ['openai'],
            'permission': {'*': 'deny', 'lykoi_*': 'allow'}, 'tools': {'*': False, 'lykoi_*': True},
            'agent': {'r627': {'mode': 'primary', 'model': MODEL, 'variant': 'high', 'prompt': 'Perform only the requested inert tool calls. Do not use files or other tools. No symbolic program construction.',
                              'steps': 16, 'options': {'maxOutputTokens': 4096}, 'permission': {'*': 'deny', 'lykoi_*': 'allow'}}},
            'mcp': {'lykoi': {'type': 'local', 'command': [sys.executable, str(HERE / 'bridge.py'), label, mode], 'enabled': True},
                    'codegraphcontext': {'enabled': False}, 'shadcn': {'enabled': False}, 'pixellab': {'enabled': False}}}

def invoke(label, mode, message=None):
    assert TEMP.is_dir()
    directory = HERE / label
    assert not directory.exists()
    directory.mkdir()
    cfg = config(label, mode)
    env = os.environ.copy()
    env.update(OPENCODE_CONFIG_CONTENT=json.dumps(cfg), OPENCODE_DISABLE_PROJECT_CONFIG='1', OPENCODE_DISABLE_EXTERNAL_SKILLS='1',
               OPENCODE_DISABLE_CLAUDE_CODE_SKILLS='1', OPENCODE_PURE='1')
    args = ['run', '--pure', '--model', MODEL, '--variant', 'high', '--agent', 'r627', '--format', 'json', '--title', 'R6.27 ' + label] if message else ['mcp', 'list', '--pure', '--print-logs', '--log-level', 'DEBUG']
    save(label + '/REQUEST.json', dict(timestamp=now(), command=['opencode'] + args, stdin_prompt=message, cwd=str(TEMP), configuration=cfg, model_calls_requested=1 if message else 0))
    begin = time.perf_counter()
    assert EXECUTABLE.is_file()
    proc = subprocess.Popen([str(EXECUTABLE)] + args, cwd=TEMP, env=env, stdin=subprocess.PIPE if message else None, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        out, err = proc.communicate(input=message.encode('utf-8') if message else None, timeout=180 if message else 60)
        termination = 'COMPLETED'
    except subprocess.TimeoutExpired:
        subprocess.run(['taskkill', '/PID', str(proc.pid), '/T', '/F'], capture_output=True)
        out, err = proc.communicate()
        termination = 'TIMEOUT'
    # CLI stderr is local diagnostic output, not HTTP headers or authentication.
    (directory / ('EVENTS.jsonl' if message else 'STATUS.txt')).write_bytes(out)
    (directory / 'STDERR.txt').write_bytes(err)
    save(label + '/RESULT.json', dict(returncode=proc.returncode, termination=termination, wall_seconds=time.perf_counter()-begin))
    if message and out:
        events = [json.loads(s) for s in out.decode('utf-8').splitlines() if s.startswith('{')]
        sessions = {e['sessionID'] for e in events if 'sessionID' in e}
        if len(sessions) == 1:
            exported = subprocess.run([str(EXECUTABLE), 'export', next(iter(sessions))], capture_output=True, encoding='utf-8', timeout=30)
            data = json.loads(exported.stdout)
            user = [p['text'] for m in data['messages'] if m['info']['role']=='user' for p in m['parts'] if p['type']=='text']
            save(label + '/DELIVERY.json', dict(session=next(iter(sessions)), user_text=user, matches_requested=user==[message],
                                              executable=str(EXECUTABLE), executable_sha256=sha(EXECUTABLE)))
    print(label, out.decode('utf-8', errors='replace').encode('ascii', errors='backslashreplace').decode() if not message else termination)

if __name__ == '__main__':
    if sys.argv[1] == 'baseline':
        baseline()
    elif sys.argv[1] == 'matrix':
        from bridge import SCHEMAS
        for key in SCHEMAS:
            invoke('SCHEMA-' + key, key)
        invoke('ORIGINAL', 'original')
        invoke('ANNOTATED', 'exact')
