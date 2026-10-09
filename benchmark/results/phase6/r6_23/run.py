"""Frozen bounded local A/B authoring, no production writes or remote calls."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

import adapter as a
import endpoint

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
control_spec = importlib.util.spec_from_file_location('r6_23_controls', HERE / 'controls.py')
controls = importlib.util.module_from_spec(control_spec)
control_spec.loader.exec_module(controls)
BASE = 'http://127.0.0.1:11435'
MODEL = 'qwen3:8b'
DIGEST = '500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41'
WEIGHT = 'a3de86cd1c132c822487ededd47a324c50491393e6565cd14bafa40d0b8e686f'
OPTIONS = dict(temperature=0, seed=623, num_ctx=8192, num_predict=2048, top_k=20, top_p=.95, repeat_penalty=1)
HTTP = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda: f.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def wire(x):
    return json.dumps(x, separators=(',', ':'), ensure_ascii=True)


def save(name, value):
    p = HERE / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, indent=2, default=lambda v: {'bytes_hex': v.hex()} if isinstance(v, bytes) else str(v)) + '\n', encoding='utf-8')


def read(name):
    return json.loads((HERE / name).read_text())


def api(path, data=None, base=BASE):
    assert base.startswith('http://127.0.0.1:')
    assert path in ('/api/version', '/api/tags', '/api/show', '/api/ps', '/tokenize')
    req = urllib.request.Request(base + path, data=wire(data).encode() if data is not None else None,
                                 headers={'Content-Type': 'application/json'})
    with HTTP.open(req, timeout=30) as response:
        return json.load(response)


def cmd(args):
    p = subprocess.run(args, capture_output=True, text=True, timeout=30)
    return dict(returncode=p.returncode, stdout=p.stdout, stderr=p.stderr)


def prompt(system, user):
    return '<|im_start|>system\n' + system + '<|im_end|>\n<|im_start|>user\n' + user + '<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n'


def task_prompt(task, track):
    text = (HERE / 'CONTRACT.txt').read_text()
    shared, interfaces = text.split('\nTRACK_A\n')
    full, compact = interfaces.split('\nTRACK_B\n')
    system = shared + '\nFORMAT:\n' + (full if track == 'A' else compact)
    return prompt(system, 'Objective ' + task['id'] + ': ' + task['requirement'])


def prepare():
    assert not (HERE / 'FREEZE.json').exists()
    assert all(sha(ROOT / p) == h for p, h in read('BASELINE.json')['protected_files'].items())
    schemas = a.schemas()
    save('complete.schema.json', schemas['A'])
    save('compact.schema.json', schemas['B'])
    def success(args, value):
        return dict(args=args, status='success', value=value, output=[value >> 8, value & 255], consumed=0)
    def failure(args, code, stage='validation', offset=0):
        return dict(args=args, status='reject', code=code, stage=stage, offset=offset)
    def task(i, requirement, target, signatures, operations, edges, cases):
        return dict(id=i, requirement=requirement, target=target, signatures=signatures,
                    operations=operations, edges=edges, cases=cases)
    tasks = [
        task('T1', 'Author target Shift(n:Int64,d:Int64). Exactly two value steps: first add n and d; second adds literal7 to that first value. Return second. No other definitions.',
            'Shift', {'Shift': [['n', 'Int64'], ['d', 'Int64']]}, {'Shift': ['value', 'value']}, [],
            [success(dict(n=n, d=d), n+d+7) for n, d in [(0, 0), (8, 5), (-5, 6), (65520, 8)]]),
        task('T2', 'Author target Threshold(n:Int64,limit:Int64). First materialize Bool le(n,limit), then check that stored predicate, code EXCEEDS, site literal31. Return input n. Exactly these two steps, no other definitions.',
            'Threshold', {'Threshold': [['n', 'Int64'], ['limit', 'Int64']]}, {'Threshold': ['value', 'check']}, [],
            [success(dict(n=5, limit=5), 5), success(dict(n=0, limit=9), 0), failure(dict(n=6, limit=5), 'EXCEEDS'), failure(dict(n=65535, limit=0), 'EXCEEDS')]),
        task('T3', 'Author target Ordered(flag:Bool,gate:Bool). Execute check flag/code ALPHA once, then check gate/code OMEGA twice, all sites literal33. Exactly three ordered check operations. Return literal29. No other definitions. Compact may use bounded repetition for the identical last two checks.',
            'Ordered', {'Ordered': [['flag', 'Bool'], ['gate', 'Bool']]}, {'Ordered': ['check', 'check', 'check']}, [],
            [failure(dict(flag=False, gate=False), 'ALPHA'), failure(dict(flag=False, gate=True), 'ALPHA'), failure(dict(flag=True, gate=False), 'OMEGA'), success(dict(flag=True, gate=True), 29)]),
        task('T4', 'Author all three reusable definitions, no supplied library: Lift(n:Int64) has one value step add(n,11) and returns it; Bridge(n:Int64) has one compose step Lift(n=ref n) and returns it; target Outer(n:Int64) has one compose step Bridge(n=ref n) and returns it. No inlining or other steps/definitions.',
            'Outer', {'Lift': [['n', 'Int64']], 'Bridge': [['n', 'Int64']], 'Outer': [['n', 'Int64']]}, {'Lift': ['value'], 'Bridge': ['compose'], 'Outer': ['compose']}, [['Bridge', 'Lift'], ['Outer', 'Bridge']],
            [success(dict(n=n), n+11) for n in [0, 18, -11, 65524]]),
        task('T5', 'Author reusable Offset(x:Int64,d:Int64), exactly one value step add(x,d), returning it. Author target Reuse(n:Int64): call Offset(x=ref n,d=literal4), call the SAME Offset(x=ref n,d=literal9), then a value step adding those two call results, returning that sum. Exactly three target steps, no other definitions. Preserve both calls rather than inlining.',
            'Reuse', {'Offset': [['x', 'Int64'], ['d', 'Int64']], 'Reuse': [['n', 'Int64']]}, {'Offset': ['value'], 'Reuse': ['compose', 'compose', 'value']}, [['Reuse', 'Offset'], ['Reuse', 'Offset']],
            [success(dict(n=n), 2*n+13) for n in [0, 12, 100, 32761]]),
        task('T6', 'Author target Guarded(n:Int64,permit:Bool). First check permit, code BLOCKED, site literal35. Then one value step add(n,9); return that value. Exactly two steps, no other definitions. Existing check failure must precede arithmetic overflow, and fixed UInt16BE encoding failures must remain native; do not add bounds checks.',
            'Guarded', {'Guarded': [['n', 'Int64'], ['permit', 'Bool']]}, {'Guarded': ['check', 'value']}, [],
            [failure(dict(n=2**63-1, permit=False), 'BLOCKED'), failure(dict(n=2**63-1, permit=True), 'OVERFLOW', 'structure'),
             success(dict(n=0, permit=True), 9), success(dict(n=-9, permit=True), 0), failure(dict(n=65530, permit=True), 'ENCODE_RANGE', 'encode', None)])]
    schedule = [(t['id'], tr) for index, t in enumerate(tasks) for tr in (['A', 'B'] if index % 2 == 0 else ['B', 'A'])]
    save('TASKS.json', dict(tasks=tasks, schedule=schedule, attempts_per_track=1, repairs=0, scored=False))
    try:
        save('HOST-CONTROLS.json', controls.run())
    except Exception as e:
        save('PREPARATION-FAILURE.json', dict(error=repr(e), traceback=__import__('traceback').format_exc()))
        raise
    prompts = {t['id']: {tr: task_prompt(t, tr) for tr in ('A', 'B')} for t in tasks}
    save('PROMPTS.json', dict(prompts=prompts, shared_contract_sha256=hashlib.sha256((HERE / 'CONTRACT.txt').read_text().split('\nTRACK_A\n')[0].encode()).hexdigest(),
        requirement_hashes={t['id']: hashlib.sha256(t['requirement'].encode()).hexdigest() for t in tasks}))
    names = ['baseline.py', 'BASELINE.json', 'PROTOCOL.md', 'SEMANTICS-1.md', 'CONTRACT.txt', 'adapter.py',
        'endpoint.py', 'controls.py', 'run.py', 'compact.schema.json', 'complete.schema.json', 'TASKS.json', 'PROMPTS.json', 'HOST-CONTROLS.json']
    save('FREEZE.json', dict(timestamp=now(), files={p: sha(HERE / p) for p in names}, options=OPTIONS,
        model=MODEL, digest=DIGEST, weight=WEIGHT, format='json', stream=True, raw=True))
    print('Frozen tasks, requests, adapters, schemas and controls; no inference.')


def evaluate(text, track, task):
    outcome = a.construct(text, track)
    outcome.update(expanded_valid='NOT_REACHED', structural_valid='NOT_REACHED', functional_success=False,
                   cases=[], expansion_seconds=0, execution_seconds=0)
    if not outcome['typed_valid']:
        return outcome
    artifact = outcome['artifact']
    definitions = {d['name']: d for d in artifact['definitions']}
    signatures = {n: [[p['name'], p['type']] for p in d['params']] for n, d in definitions.items()}
    operations = {n: [next(s['node']['op'] for s in d['steps'] if s['id'] == sid) for sid in d['order']] for n, d in definitions.items()}
    edges = sorted([[n, s['node']['symbol']] for n, d in definitions.items() for s in d['steps'] if s['node']['op'] == 'compose'])
    structural = artifact['target'] == task['target'] and signatures == task['signatures'] and operations == task['operations'] and edges == sorted(task['edges'])
    outcome.update(structural_valid=structural, observed_structure=dict(signatures=signatures, operations=operations, edges=edges))
    passed = structural
    for case in task['cases']:
        try:
            pkg = a.package(artifact, case['args'])
            begin = time.perf_counter()
            expanded = a.c.expand(pkg)
            outcome['expansion_seconds'] += time.perf_counter() - begin
            outcome['expanded_valid'] = True
            begin = time.perf_counter()
            observation = a.c.vm.execute(expanded['plan'], b'')
            repeated = a.c.vm.execute(expanded['plan'], b'')
            outcome['execution_seconds'] += time.perf_counter() - begin
            match = observation['status'] == case['status']
            if match and case['status'] == 'success':
                match = observation['value'] == case['value'] and list(observation['output']) == case['output'] and observation['consumed'] == case['consumed']
            elif match:
                match = all(observation['error'][key] == case[key] for key in ('code', 'stage', 'offset'))
            deterministic = observation == repeated
            passed &= match and deterministic
            outcome['cases'].append(dict(expected=case, observation=observation, repeat_equal=deterministic, passed=match,
                package=pkg, expanded=expanded, expanded_bytes=len(a.c.canonical(expanded['plan'])), package_bytes=len(a.c.canonical(pkg))))
        except a.c.Diagnostic as e:
            outcome.update(expanded_valid=False, expansion_diagnostic=e.data)
            passed = False
            break
    outcome['functional_success'] = bool(passed and len(outcome['cases']) == len(task['cases']))
    return outcome


class Runner:
    def __init__(self):
        self.proc = None
        self.started = time.perf_counter()
        self.rows = []
        self.endpoints = []
        self.logpath = HERE / 'SERVER.log'

    def fresh_endpoint(self, label):
        loaded = api('/api/ps')
        evidence = endpoint.discover(self.logpath, self.proc.pid, loaded, DIGEST, WEIGHT)
        evidence.update(label=label, timestamp=now())
        self.endpoints.append(evidence)
        save('ENDPOINTS.json', dict(rows=self.endpoints, no_cached_endpoint_reuse=True))
        return evidence

    def tokenize(self, label, text):
        evidence = self.fresh_endpoint(label)
        begin = time.perf_counter()
        response = api('/tokenize', dict(content=text, add_special=True, parse_special=True), evidence['base'])
        return dict(endpoint=evidence, response=response, count=len(response['tokens']), timestamp=now(),
                    tokenization_seconds=time.perf_counter() - begin)

    def start(self):
        try:
            api('/api/version')
        except OSError:
            pass
        else:
            raise RuntimeError('dedicated port occupied')
        env = os.environ.copy()
        overrides = dict(OLLAMA_HOST='127.0.0.1:11435', OLLAMA_NO_CLOUD='1', OLLAMA_MODELS=r'D:\Software\.ollama\models',
            OLLAMA_NUM_PARALLEL='1', OLLAMA_CONTEXT_LENGTH='8192', OLLAMA_MAX_LOADED_MODELS='1', OLLAMA_DEBUG='1',
            HTTP_PROXY='http://127.0.0.1:9', HTTPS_PROXY='http://127.0.0.1:9', NO_PROXY='127.0.0.1,localhost')
        env.update(overrides)
        with self.logpath.open('xb') as logfile:
            self.proc = subprocess.Popen(['ollama', 'serve'], env=env, stdout=logfile, stderr=logfile)
        for _ in range(60):
            assert self.proc.poll() is None
            try:
                api('/api/version')
                break
            except OSError:
                time.sleep(.5)
        version = api('/api/version')
        assert version['version'] == '0.35.0'
        selected = next(x for x in api('/api/tags')['models'] if x['name'] == MODEL)
        assert selected['digest'] == DIGEST
        blob = Path(overrides['OLLAMA_MODELS']) / 'blobs' / ('sha256-' + WEIGHT)
        assert sha(blob) == WEIGHT
        show = api('/api/show', dict(model=MODEL))
        save('INVENTORY.json', dict(timestamp=now(), version=version, selected=selected,
            model_info=show['model_info'], parameters=show['parameters'], template=show['template'],
            weight_sha256=WEIGHT, weight_bytes=blob.stat().st_size, options=OPTIONS, overrides=overrides,
            owned_pid=self.proc.pid, gpu=cmd(['nvidia-smi', '--query-gpu=name,memory.total,memory.used', '--format=csv'])))

    def call(self, label, text, options, warm=False):
        assert len(self.rows) < 15 and time.perf_counter() - self.started < 1200, 'run ceiling'
        assert self.proc.poll() is None
        pre = None if warm else self.tokenize(label + '/before', text)
        if pre:
            assert pre['count'] <= 3584 and pre['count'] + options['num_predict'] + 256 <= options['num_ctx'], 'unsafe input budget'
        request = dict(model=MODEL, prompt=text, raw=True, stream=True, format='json', keep_alive='10m', options=options)
        serialized = wire(request)
        save('calls/' + label + '-request.json', dict(request=request, serialized=serialized,
            request_sha256=hashlib.sha256(serialized.encode()).hexdigest(), preflight=pre))
        offset = self.logpath.stat().st_size
        begin = time.perf_counter()
        chunks = []
        status = None
        error = None
        error_body = None
        with (HERE / 'calls' / (label + '-stream.jsonl')).open('x', encoding='utf-8') as stream:
            try:
                req = urllib.request.Request(BASE + '/api/generate', data=serialized.encode(), headers={'Content-Type': 'application/json'})
                with HTTP.open(req, timeout=180) as response:
                    status = response.status
                    for line in response:
                        event = dict(timestamp=now(), elapsed_seconds=time.perf_counter() - begin, raw=line.decode(errors='replace'))
                        stream.write(wire(event) + '\n')
                        stream.flush()
                        chunk = json.loads(line)
                        chunks.append(chunk)
                        if 'error' in chunk:
                            error, error_body = chunk['error'], event['raw']
            except urllib.error.HTTPError as e:
                status, error = e.code, str(e)
                error_body = e.read().decode(errors='replace')
                stream.write(wire(dict(timestamp=now(), elapsed_seconds=time.perf_counter() - begin, raw=error_body, http_status=status)) + '\n')
            except (OSError, ValueError) as e:
                error = repr(e)
        wall = time.perf_counter() - begin
        time.sleep(.1)
        end = self.logpath.stat().st_size
        log = self.logpath.read_bytes()[offset:end].decode(errors='replace')
        final = next((x for x in reversed(chunks) if x.get('done')), {})
        output = ''.join(x.get('response', '') for x in chunks)
        row = dict(id=label, timestamp=now(), http_status=status, error=error, final_error_body=error_body,
            final=final, output=output, chunks=len(chunks), wall_seconds=wall,
            tokens={k: final.get(k) for k in ('prompt_eval_count', 'prompt_eval_cached_count', 'eval_count')},
            durations_ns={k: final.get(k) for k in ('total_duration', 'load_duration', 'prompt_eval_duration', 'eval_duration')},
            log_byte_span=[offset, end], log_excerpt=log,
            completion=bool(final.get('done') and final.get('done_reason') == 'stop' and not error), preflight=pre)
        self.rows.append(row)
        save('calls/' + label + '-result.json', row)
        save('INFERENCE.json', dict(rows=self.rows))
        print(label, 'HTTP', status, 'stop', final.get('done_reason'), 'tokens', row['tokens'], flush=True)
        assert row['completion'], 'runtime/budget failure: ' + str(error or final.get('done_reason'))
        post = self.tokenize(label + '/after', text)
        slots = [int(n) for n in re.findall(r'n_ctx_slot = (\d+)', log)]
        task_counts = [int(n) for n in re.findall(r'task.n_tokens = (\d+)', log)]
        intact = post['count'] == final['prompt_eval_count'] and (pre is None or pre['count'] == post['count']) and bool(slots) and all(n == options['num_ctx'] for n in slots) and bool(task_counts) and task_counts[0] == post['count'] and post['endpoint']['context'] == options['num_ctx'] and 'truncating input prompt' not in log
        row.update(postflight=post, delivery=dict(intact=intact, slots=slots, logged_tokens=task_counts, expected=post['count'],
            pre_endpoint=pre['endpoint']['base'] if pre else None, post_endpoint=post['endpoint']['base']))
        save('calls/' + label + '-result.json', row)
        save('INFERENCE.json', dict(rows=self.rows))
        assert intact, 'endpoint/delivery mismatch'
        return row

    def qualify(self):
        text = prompt('Return only JSON.', 'Return {"marker":"endpoint","number":23}.')
        rows = []
        for index, context in enumerate([8192, 4096, 8192]):
            row = self.call('endpoint_' + str(index), text, dict(OPTIONS, num_ctx=context, num_predict=64), warm=index == 0)
            assert json.loads(row['output']) == dict(marker='endpoint', number=23)
            rows.append(dict(id=row['id'], context=context, delivery=row['delivery'], verified=True))
        ports = [row['delivery']['post_endpoint'] for row in rows]
        assert len(set(ports)) == 3, 'reload endpoint controls must change backend'
        save('ENDPOINT-VERIFICATION.json', dict(passed=True, rows=rows, three_distinct_ports=True,
            stale_endpoint_failure_preserved=sha(HERE.parent / 'r6_22/HALT.json'),
            rule='rediscover+verify each pre/post accounting; no generation on unverified preflight'))

    def stop(self):
        if self.proc:
            termination = cmd(['taskkill', '/PID', str(self.proc.pid), '/T', '/F'])
            self.proc.wait(timeout=15)
            save('CLEANUP.json', dict(timestamp=now(), owned_pid=self.proc.pid, termination=termination))


def run():
    assert not (HERE / 'RUN-STATUS.json').exists(), 'no replay'
    assert all(sha(HERE / p) == h for p, h in read('FREEZE.json')['files'].items())
    assert all(sha(ROOT / p) == h for p, h in read('BASELINE.json')['protected_files'].items())
    runner = Runner()
    fatal = None
    qualified = False
    outcomes = []
    try:
        runner.start()
        runner.qualify()
        qualified = True
        tasks = {t['id']: t for t in read('TASKS.json')['tasks']}
        for tid, track in read('TASKS.json')['schedule']:
            rec = runner.call(tid + '_' + track, read('PROMPTS.json')['prompts'][tid][track], OPTIONS)
            start = time.perf_counter()
            result = evaluate(rec['output'], track, tasks[tid])
            row = dict(id=tid, track=track, result=result, validation_and_execution_wall=time.perf_counter() - start,
                       first_attempt=True, repairs=0)
            outcomes.append(row)
            save('candidates/' + tid + '_' + track + '.json', row)
            save('ACCEPTANCE.json', dict(rows=outcomes))
            print(tid, track, 'typed', result['typed_valid'], 'functional', result['functional_success'], 'diagnostic', result['diagnostic'], flush=True)
    except Exception as e:
        fatal = repr(e)
        save('HALT.json', dict(timestamp=now(), error=fatal, qualified=qualified, traceback=__import__('traceback').format_exc()))
    finally:
        runner.stop()
        save('RUN-STATUS.json', dict(timestamp=now(), calls=len(runner.rows), candidates=len(outcomes), endpoint_qualified=qualified,
            fatal=fatal, total_seconds=time.perf_counter() - runner.started, stopped=True, manual_repairs=0))


if __name__ == '__main__':
    {'prepare': prepare, 'run': run}[sys.argv[1]]()
