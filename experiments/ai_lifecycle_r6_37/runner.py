"""Supported OpenCode child orchestration; actual MCP calls only."""
import json
from pathlib import Path
import subprocess
import sys
import time
import importlib.util
_spec = importlib.util.spec_from_file_location('r637_preflight', Path(__file__).with_name('preflight.py'))
_preflight = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_preflight)
ROOT, HERE, OUT, TEMP, EXE = (_preflight.ROOT, _preflight.HERE, _preflight.OUT, _preflight.TEMP, _preflight.EXE)
environment, sanitize, save, raw, sha, load = (_preflight.environment, _preflight.sanitize,
    _preflight.save, _preflight.raw, _preflight.sha, _preflight.load)
from tools import TOOLS

AGENT_PROMPT = ('Follow the supplied lifecycle stage using actual Lykoi MCP calls. '
    'Do not output JSON actions for a host broker. Do not access files or other tools. '
    'Never invent operations. Only mechanical identity sealing is done by admission. '
    'Stop at the requested stage, preserving all failed calls.')


def config(phase):
    permission = {'*': 'deny', 'r637_lykoi_*': 'allow'}
    return {'$schema': 'https://opencode.ai/config.json', 'share': 'disabled',
        'autoupdate': False, 'snapshot': False, 'permission': permission,
        'agent': {'r637-author': dict(mode='primary', model='openai/gpt-6.1-sol',
            variant='high', description='Bounded MCP lifecycle participant',
            prompt=AGENT_PROMPT, permission=permission)}, 'default_agent': 'r637-author',
        'mcp': {'r637': dict(type='local', command=[sys.executable, '-B', str(HERE / 'tools.py')],
            environment={'R637_PHASE': phase}, enabled=True)}}


def ask(phase, stage, prompt, session=None, timeout=300):
    folder = OUT / phase / stage
    folder.mkdir(parents=True, exist_ok=False)
    raw(folder / 'PROMPT.txt', prompt + '\n')
    cfg = config(phase)
    save(folder / 'CONFIG.json', cfg)
    command = [EXE, 'run', '--format', 'json', '--model', 'openai/gpt-6.1-sol',
        '--variant', 'high', '--agent', 'r637-author', '--title', 'R6.37 ' + phase]
    if session:
        command += ['--session', session]
    start = time.perf_counter()
    timed_out = False
    try:
        child = subprocess.run(command, input=prompt.encode('utf-8'), cwd=TEMP,
            env=environment(cfg), capture_output=True, timeout=timeout)
        stdout, stderr, code = child.stdout, child.stderr, child.returncode
    except subprocess.TimeoutExpired as exc:
        stdout, stderr, code = exc.stdout or b'', exc.stderr or b'', None
        timed_out = True
    events = [sanitize(json.loads(line)) for line in stdout.decode('utf-8', errors='replace').splitlines()
              if line.startswith('{')]
    raw(folder / 'EVENTS.jsonl', ''.join(json.dumps(e) + '\n' for e in events))
    sessions = sorted({e['sessionID'] for e in events if e.get('sessionID')})
    session = sessions[-1] if sessions else session
    finishes = [e['part'] for e in events if e.get('type') == 'step_finish']
    record = dict(phase=phase, stage=stage, session=session, returncode=code, timeout=timed_out,
        wall_seconds=time.perf_counter()-start, step_finishes=finishes,
        tool_calls=sum(e.get('type') == 'tool_use' for e in events),
        errors=[e for e in events if e.get('type') == 'error'],
        stderr_bytes=len(stderr), stderr_raw_published=False)
    save(folder / 'MEASUREMENT.json', record)
    if session:
        child = subprocess.run([EXE, 'export', session], cwd=TEMP,
            env=environment(cfg), capture_output=True, timeout=60)
        if child.returncode == 0:
            save(folder / 'EXPORT.json', sanitize(json.loads(child.stdout)))
    print(json.dumps(record))
    return record


def qualify():
    assert load(OUT / 'PREFLIGHT-RESULT.json')['passed']
    prompt = '''This is neutral unscored qualification, no lifecycle requirement.
Discover and name all four tools. Use actual MCP calls to:
1. Admit NeutralProbe, revision1, params[], dependencies{}, one Int64 value step named v
with deps[] and expr const11, order[v], result ref v, result_type Int64. predecessor=null.
2. Retrieve its returned pin, validate it, and execute it on empty input_hex.
3. Submit a second definition BadProbe with the same shape but declared step type Bool
while expr is const11. This must reject with TYPE; do not repair it.
Then summarize exact observed effects and diagnostic. Do not produce broker actions.'''
    save(OUT / 'QUALIFICATION-FREEZE.json', dict(inputs={p.relative_to(ROOT).as_posix(): sha(p)
        for p in (HERE / 'tools.py', HERE / 'runner.py')}, tools=TOOLS, prompt=prompt,
        task_exposure=False, budget={'invocations': 1, 'seconds': 300}))
    ask('qualification', 'live', prompt)


if __name__ == '__main__':
    {'qualify': qualify}[sys.argv[1]]()
