"""One neutral provider gate, without loading or exposing a lifecycle task."""
import sys
from pathlib import Path
import subprocess
import json
import time
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'experiments/ai_lifecycle_r6_36'))
from preflight import environment, sanitize, sha, load, save, raw, EXE

HERE = Path(__file__).resolve().parent
OUT = ROOT / 'benchmark/results/phase6/r6_37'
TEMP = Path('C:/Users/lblan/AppData/Local/Temp/opencode/r6_37')


def main():
    assert OUT.parent.is_dir() and TEMP.parent.is_dir()
    OUT.mkdir(exist_ok=False)
    TEMP.mkdir(exist_ok=False)
    prior = ROOT / 'benchmark/results/phase6/r6_36'
    receipt = load(prior / 'VERIFICATION.json')
    assert receipt['passed'] and receipt['kernel'] == 26
    assert sha(prior / 'PUBLICATION-IDENTITIES.json') == receipt['manifest_sha256']
    pins = dict(load(prior / 'BASELINE.json')['protected_files'])
    for name, meta in load(prior / 'PUBLICATION-IDENTITIES.json')['files'].items():
        assert sha(ROOT / name) == meta['sha256']
        assert (ROOT / name).stat().st_size == meta['bytes']
        pins[name] = meta['sha256']
    for name in ('PUBLICATION-IDENTITIES.json', 'VERIFICATION.json'):
        pins[(prior / name).relative_to(ROOT).as_posix()] = sha(prior / name)
    for name, pin in pins.items():
        assert 'p6_a05' not in name.lower().replace('-', '_')
        assert sha(ROOT / name) == pin, name
    save(OUT / 'BASELINE.json', dict(kernel=26, protected_files=pins,
        protected_count=len(pins), R6_36_publication_verified=True,
        baseline_basis='Inherited protected SHA256 accounting, not a new kernel recount',
        head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        initial_status=subprocess.check_output(['git', 'status', '--short'], cwd=ROOT, text=True)))
    cfg = {'$schema': 'https://opencode.ai/config.json', 'share': 'disabled',
        'autoupdate': False, 'snapshot': False, 'permission': {'*': 'deny'},
        'agent': {'r637-preflight': dict(mode='primary', model='openai/gpt-6.1-sol',
            variant='high', description='Neutral provider gate', permission={'*': 'deny'},
            prompt='Follow the neutral request. Do not use tools.')},
        'default_agent': 'r637-preflight'}
    env = environment(cfg)
    version = subprocess.run([EXE, '--version'], cwd=TEMP, env=env,
        capture_output=True, timeout=30).stdout.decode().strip()
    prompt = 'Reply exactly NEUTRAL_OK. Do not use tools.'
    raw(OUT / 'NEUTRAL-PROMPT.txt', prompt + '\n')
    save(OUT / 'PREFLIGHT-CONFIG.json', dict(config=cfg, provider='openai', model='gpt-6.1-sol',
        requested_reasoning={'reasoningEffort': 'high'}, effective_reasoning=None,
        OPENCODE_PURE=env['OPENCODE_PURE'], disable_default_plugins_absent=True,
        built_in_plugins_eligible=True, global_configuration_modified=False,
        credentials_accessed=False, headers_overridden=False, endpoints_overridden=False,
        opencode_version=version, budget={'invocations': 1, 'seconds': 90, 'retries': 0},
        lifecycle_task_selected=False, lifecycle_task_exposed=False))
    save(OUT / 'PREFLIGHT-FREEZE.json', dict(utc=datetime.now(timezone.utc).isoformat(),
        inputs={p.relative_to(ROOT).as_posix(): sha(p) for p in
            (HERE / 'PROTOCOL.md', HERE / 'preflight.py', OUT / 'PREFLIGHT-CONFIG.json',
             OUT / 'NEUTRAL-PROMPT.txt')}, provider_calls_so_far=0))
    start = time.perf_counter()
    timeout = False
    try:
        child = subprocess.run([EXE, 'run', '--format', 'json', '--model', 'openai/gpt-6.1-sol',
            '--variant', 'high', '--agent', 'r637-preflight', '--title', 'R6.37 neutral preflight',
            prompt], cwd=TEMP, env=env, capture_output=True, timeout=90)
        stdout, stderr, code = child.stdout, child.stderr, child.returncode
    except subprocess.TimeoutExpired as exc:
        stdout, stderr, code = exc.stdout or b'', exc.stderr or b'', None
        timeout = True
    elapsed = time.perf_counter() - start
    events = [sanitize(json.loads(line)) for line in stdout.decode('utf-8', errors='replace').splitlines()
              if line.startswith('{')]
    raw(OUT / 'NEUTRAL-EVENTS.jsonl', ''.join(json.dumps(e) + '\n' for e in events))
    finishes = [e['part'] for e in events if e.get('type') == 'step_finish']
    texts = [e['part']['text'] for e in events if e.get('type') == 'text']
    errors = [e for e in events if e.get('type') == 'error']
    passed = (not timeout and code == 0 and not errors and bool(finishes)
              and '\n'.join(texts).strip() == 'NEUTRAL_OK'
              and not any(e.get('type') == 'tool_use' for e in events))
    save(OUT / 'PREFLIGHT-RESULT.json', dict(passed=passed, returncode=code, timeout=timeout,
        wall_seconds=elapsed, step_finishes=finishes, errors=errors, texts=texts,
        stderr_bytes=len(stderr), stderr_raw_published=False, tool_calls=0,
        task_selected=False, participant_task_exposure=False, coordinator_retries=0,
        effective_authentication=None, provider_HTTP_attempts=None,
        usage=finishes or None, usage_missing_reason=None if finishes else 'No completed step_finish',
        session_ids=sorted({e['sessionID'] for e in events if e.get('sessionID')})))
    print(json.dumps(dict(passed=passed, wall_seconds=elapsed, errors=errors, usage=finishes)))


if __name__ == '__main__':
    main()
