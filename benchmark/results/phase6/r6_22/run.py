"""Experiment-local frozen neutral streaming diagnosis; stdlib plus jsonschema."""
import hashlib
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

import jsonschema

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OLD = HERE.parent / 'r6_21'
BASE = 'http://127.0.0.1:11435'
MODEL = 'qwen3:8b'
DIGEST = '500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41'
WEIGHT = 'a3de86cd1c132c822487ededd47a324c50491393e6565cd14bafa40d0b8e686f'
OPTIONS = dict(temperature=0, seed=621, num_ctx=8192, num_predict=2048,
               top_k=20, top_p=.95, repeat_penalty=1)
HTTP = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def wire(x):
    return json.dumps(x, ensure_ascii=True, separators=(',', ':'))


def save(name, x):
    p = HERE / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(x, indent=2, ensure_ascii=True) + '\n', encoding='utf-8')


def read(name):
    return json.loads((HERE / name).read_text(encoding='utf-8'))


def cmd(args):
    p = subprocess.run(args, capture_output=True, text=True, timeout=30)
    return dict(returncode=p.returncode, stdout=p.stdout, stderr=p.stderr)


def api(path, data=None, base=BASE):
    assert base.startswith('http://127.0.0.1:')
    assert path in ('/api/version', '/api/tags', '/api/show', '/api/ps', '/tokenize')
    req = urllib.request.Request(base + path, data=wire(data).encode() if data is not None else None,
                                 headers={'Content-Type': 'application/json'})
    with HTTP.open(req, timeout=30) as r:
        return json.load(r)


def prompt(user):
    return ('<|im_start|>system\nReturn only the requested JSON, no commentary.'
            '<|im_end|>\n<|im_start|>user\n' + user +
            '<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n')


def obj(properties):
    return dict(type='object', properties=properties, required=list(properties), additionalProperties=False)


def prepare():
    assert not (HERE / 'FREEZE.json').exists()
    pins = json.loads((OLD / 'BASELINE.json').read_text())['protected_files'].copy()
    pub = json.loads((OLD / 'PUBLICATION-IDENTITIES.json').read_text())
    for p, v in pub['files'].items():
        assert sha(ROOT / p) == v['sha256'], p
        pins[p] = v['sha256']
    for name in ('PUBLICATION-IDENTITIES.json', 'VERIFICATION.json'):
        p = OLD / name
        pins[p.relative_to(ROOT).as_posix()] = sha(p)
    assert all(sha(ROOT / p) == h for p, h in pins.items())
    save('BASELINE.json', dict(timestamp=now(), protected_files=pins, protected_count=len(pins),
        kernel=26, git=cmd(['git', 'status', '--short']), original_failure=json.loads((OLD / 'FAILURE-ANALYSIS.json').read_text())))
    tasks = []
    def add(i, instruction, schema, expected):
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.validate(expected, schema)
        tasks.append(dict(id=i, prompt=prompt(instruction), schema=schema, expected=expected))
    add('short', 'Return {"label":"cobalt","ok":true,"count":3}.',
        obj(dict(label={'const': 'cobalt'}, ok={'const': True}, count={'const': 3})),
        dict(label='cobalt', ok=True, count=3))
    array = lambda item, n: dict(type='array', items=item, minItems=n, maxItems=n)
    add('long', 'Return an object with key rows, an array of exactly64 objects. Each object has index (0 through63 in order) and label ("item" followed by its index).',
        obj(dict(rows=array(obj(dict(index={'type': 'integer'}, label={'type': 'string'})), 64))),
        dict(rows=[dict(index=i, label='item' + str(i)) for i in range(64)]))
    nested = dict(value=7)
    for _ in range(8):
        nested = dict(child=nested)
    def exact_schema(v):
        return obj({k: exact_schema(x) if isinstance(x, dict) else {'const': x} for k, x in v.items()})
    add('nested', 'Return exactly this nested JSON: ' + wire(nested), exact_schema(nested), nested)
    add('array', 'Return {"values":[...]} with exactly128 entries, all integer0.',
        obj(dict(values=array({'const': 0}, 128))), dict(values=[0] * 128))
    add('identifiers', 'Return {"symbols":[...]} with exactly64 entries, all the string "sym_alpha". Stop after the64th entry.',
        obj(dict(symbols=array({'const': 'sym_alpha'}, 64))), dict(symbols=['sym_alpha'] * 64))
    add('constrained', 'Return {"status":"ready","flags":[true,false,true],"code":22}.',
        obj(dict(status={'enum': ['ready', 'waiting']}, flags=array({'type': 'boolean'}, 3), code={'type': 'integer', 'minimum': 0, 'maximum': 99})),
        dict(status='ready', flags=[True, False, True], code=22))
    add('unconstrained', 'Return {"colors":["cyan","amber","plum"]}.',
        obj(dict(colors=array({'type': 'string'}, 3))), dict(colors=['cyan', 'amber', 'plum']))
    configs = [dict(id='baseline', options=OPTIONS, mode='json', variable='none')]
    for key, value in [('temperature', .6), ('top_p', .8), ('repeat_penalty', 1.1), ('num_predict', 512), ('num_ctx', 4096)]:
        configs.append(dict(id=key, options=dict(OPTIONS, **{key: value}), mode='json', variable=key))
    configs += [dict(id='schema', options=OPTIONS, mode='schema', variable='format'),
                dict(id='free', options=OPTIONS, mode='none', variable='format')]
    schedule = [dict(task=t['id'], config='baseline', repeat=r) for t in tasks for r in range(1, 4)]
    # Unconstrained challenge must actually use unconstrained decoding.
    for row in schedule:
        if row['task'] == 'unconstrained':
            row['config'] = 'free'
        elif row['task'] == 'constrained':
            row['config'] = 'schema'
    schedule += [dict(task='identifiers', config=c['id'], repeat=r) for c in configs[1:] for r in range(1, 4)]
    save('REQUESTS.json', dict(tasks=tasks, schedule=schedule, maximum_inference_calls=43))
    save('CONFIGURATIONS.json', dict(configurations=configs, single_variable=True,
        caveat='top_p at temperature0 may have no effect; identical seeds and cache histories are not independent trials'))
    files = ['run.py', 'PROTOCOL.md', 'REQUESTS.json', 'CONFIGURATIONS.json', 'BASELINE.json']
    save('FREEZE.json', dict(timestamp=now(), files={p: sha(HERE / p) for p in files}, model=MODEL, digest=DIGEST, weight=WEIGHT))
    print('Frozen neutral suite; identities verified; no inference.')


def gpu():
    return cmd(['nvidia-smi', '--query-gpu=name,memory.total,memory.used', '--format=csv'])


def strict(text):
    def pairs(items):
        d = {}
        for k, v in items:
            if k in d:
                raise ValueError('duplicate key ' + k)
            d[k] = v
        return d
    return json.loads(text, object_pairs_hook=pairs,
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError('nonfinite ' + x)))


def evaluate(text, task):
    result = dict(json_valid=False, schema_valid=False, expected_equal=False)
    try:
        value = strict(text)
        result['json_valid'] = True
        jsonschema.Draft202012Validator(task['schema']).validate(value)
        result.update(schema_valid=True, expected_equal=value == task['expected'])
    except (ValueError, jsonschema.ValidationError) as e:
        result['diagnostic'] = str(e)[:1000]
    return result


def run():
    assert not (HERE / 'RUN-STATUS.json').exists(), 'no replay'
    assert all(sha(HERE / p) == h for p, h in read('FREEZE.json')['files'].items())
    assert all(sha(ROOT / p) == h for p, h in read('BASELINE.json')['protected_files'].items())
    started = time.perf_counter()
    proc = None
    rows = []
    fatal = None
    backend = None
    logpath = HERE / 'SERVER.log'
    def call(label, task, config, warm=False):
        assert time.perf_counter() - started < 1200, 'whole-run ceiling'
        assert proc.poll() is None, 'server exited'
        text = task['prompt']
        tokenization = None
        if not warm:
            tokenization = api('/tokenize', dict(content=text, add_special=True, parse_special=True), backend)
            count = len(tokenization['tokens'])
            assert count <= 1536 and count + config['options']['num_predict'] + 256 <= config['options']['num_ctx'], 'unsafe prompt'
        request = dict(model=MODEL, prompt=text, raw=True, stream=True, keep_alive='10m', options=config['options'])
        if config['mode'] != 'none':
            request['format'] = task['schema'] if config['mode'] == 'schema' else 'json'
        serialized = wire(request)
        save('calls/' + label + '-request.json', dict(request=request, serialized_request=serialized,
             sha256=hashlib.sha256(serialized.encode()).hexdigest(), tokenization=tokenization))
        offset = logpath.stat().st_size
        before = gpu()
        begin = time.perf_counter()
        chunks = []
        status = None
        error = None
        error_body = None
        with (HERE / 'calls' / (label + '-stream.jsonl')).open('x', encoding='utf-8') as capture:
            try:
                req = urllib.request.Request(BASE + '/api/generate', data=serialized.encode(), headers={'Content-Type': 'application/json'})
                with HTTP.open(req, timeout=180) as response:
                    status = response.status
                    for line in response:
                        event = dict(timestamp=now(), elapsed_seconds=time.perf_counter() - begin,
                                     raw=line.decode(errors='replace'))
                        capture.write(wire(event) + '\n')
                        capture.flush()
                        chunk = json.loads(line)
                        chunks.append(chunk)
                        if 'error' in chunk:
                            error = chunk['error']
                            error_body = event['raw']
            except urllib.error.HTTPError as e:
                status = e.code
                error_body = e.read().decode(errors='replace')
                error = str(e)
                capture.write(wire(dict(timestamp=now(), elapsed_seconds=time.perf_counter() - begin, http_status=status, raw=error_body)) + '\n')
            except (OSError, ValueError) as e:
                error = repr(e)
        wall = time.perf_counter() - begin
        time.sleep(.1)
        end = logpath.stat().st_size
        log = logpath.read_bytes()[offset:end].decode(errors='replace')
        final = next((c for c in reversed(chunks) if c.get('done')), {})
        output = ''.join(c.get('response', '') for c in chunks)
        loaded = api('/api/ps')
        slots = [int(n) for n in re.findall(r'n_ctx_slot = (\d+)', log)]
        tasks = [int(n) for n in re.findall(r'task.n_tokens = (\d+)', log)]
        expected = len(tokenization['tokens']) if tokenization else None
        delivery = dict(expected=expected, reported=final.get('prompt_eval_count'), slots=slots,
            logged_input=tasks, truncation='truncating input prompt' in log,
            context_matches=any(m.get('context_length') == config['options']['num_ctx'] for m in loaded.get('models', [])))
        delivery['intact'] = bool(expected is not None and tasks and tasks[0] == expected and
            slots and all(n == config['options']['num_ctx'] for n in slots) and delivery['context_matches'] and
            not delivery['truncation'] and (not final or final.get('prompt_eval_count') == expected))
        complete = bool(final.get('done') and final.get('done_reason') == 'stop' and not error)
        repeated = 'token repeat limit reached' in (str(error) + str(error_body) + log)
        category = ('Model repetition / decoder interaction undetermined' if repeated else
                    'Runtime resource failure undetermined' if error else
                    'Output-budget exhaustion' if final.get('done_reason') == 'length' else
                    'None' if complete else 'Undetermined')
        runlength = maximum = 0
        previous = None
        for chunk in chunks:
            s = chunk.get('response', '')
            if not s:
                continue
            runlength = runlength + 1 if s == previous else 1
            maximum = max(maximum, runlength)
            previous = s
        row = dict(id=label, task=task['id'], config=config['id'], timestamp=now(), http_status=status,
            error=error, final_error_body=error_body, completion=complete, final=final, output=output,
            chunks=len(chunks), wall_seconds=wall, usage={k: final.get(k) for k in
                ('prompt_eval_count', 'prompt_eval_cached_count', 'eval_count')},
            validation=evaluate(output, task), delivery=delivery, repetition=dict(guard_abort=repeated,
                sym_alpha_occurrences=output.count('sym_alpha'), max_adjacent_equal_chunks=maximum),
            failure_category=category, log_byte_span=[offset, end], log_excerpt=log,
            loaded=loaded, gpu_before=before, gpu_after=gpu(), server_exit=proc.poll())
        save('calls/' + label + '-result.json', row)
        rows.append(row)
        save('RESULTS.json', dict(rows=rows))
        print(label, 'complete', complete, 'schema', row['validation']['schema_valid'],
              'usage', row['usage']['eval_count'], 'error', error, flush=True)
        assert not delivery['truncation'], 'input truncated'
        if not warm:
            assert delivery['intact'], 'delivery gap'
        if error:
            assert repeated and proc.poll() is None and api('/api/version')['version'] == '0.35.0', 'fatal runtime failure'
        return row
    try:
        try:
            api('/api/version')
        except OSError:
            pass
        else:
            raise RuntimeError('dedicated port occupied')
        env = os.environ.copy()
        overrides = dict(OLLAMA_HOST='127.0.0.1:11435', OLLAMA_NO_CLOUD='1',
            OLLAMA_MODELS=r'D:\Software\.ollama\models', OLLAMA_NUM_PARALLEL='1',
            OLLAMA_CONTEXT_LENGTH='8192', OLLAMA_MAX_LOADED_MODELS='1', OLLAMA_DEBUG='1',
            HTTP_PROXY='http://127.0.0.1:9', HTTPS_PROXY='http://127.0.0.1:9', NO_PROXY='127.0.0.1,localhost')
        env.update(overrides)
        with logpath.open('xb') as logfile:
            proc = subprocess.Popen(['ollama', 'serve'], env=env, stdout=logfile, stderr=logfile)
        for _ in range(60):
            assert proc.poll() is None
            try:
                api('/api/version')
                break
            except OSError:
                time.sleep(.5)
        selected = next(m for m in api('/api/tags')['models'] if m['name'] == MODEL)
        assert selected['digest'] == DIGEST
        blob = Path(overrides['OLLAMA_MODELS']) / 'blobs' / ('sha256-' + WEIGHT)
        assert sha(blob) == WEIGHT
        version = api('/api/version')
        assert version['version'] == '0.35.0'
        show = api('/api/show', dict(model=MODEL))
        save('INVENTORY.json', dict(timestamp=now(), version=version, selected=selected,
            model_info=show['model_info'], parameters=show['parameters'], template=show['template'],
            weight_sha256=WEIGHT, weight_bytes=blob.stat().st_size, overrides=overrides,
            owned_pid=proc.pid, baseline_options=OPTIONS, gpu=gpu(), safeguards='unchanged'))
        configs = {c['id']: c for c in read('CONFIGURATIONS.json')['configurations']}
        tasks = {t['id']: t for t in read('REQUESTS.json')['tasks']}
        warm = dict(configs['baseline'], options=dict(OPTIONS, num_predict=64))
        warmrow = call('warmup', tasks['short'], warm, warm=True)
        assert warmrow['completion']
        ports = re.findall(r'--port (\d+) --host 127\.0\.0\.1', logpath.read_text(errors='replace'))
        assert ports, 'tokenizer unavailable'
        backend = 'http://127.0.0.1:' + ports[-1]
        for i, item in enumerate(read('REQUESTS.json')['schedule'], 1):
            call(f'{i:02d}-{item["task"]}-{item["config"]}-{item["repeat"]}', tasks[item['task']], configs[item['config']])
    except Exception as e:
        fatal = repr(e)
        save('HALT.json', dict(timestamp=now(), error=fatal, traceback=__import__('traceback').format_exc()))
    finally:
        if proc is not None:
            cleanup = cmd(['taskkill', '/PID', str(proc.pid), '/T', '/F'])
            proc.wait(timeout=15)
            save('CLEANUP.json', dict(timestamp=now(), owned_pid=proc.pid, termination=cleanup))
        save('RUN-STATUS.json', dict(timestamp=now(), calls=len(rows), planned=43, fatal=fatal,
            elapsed_seconds=time.perf_counter() - started, stopped=True))


if __name__ == '__main__':
    {'prepare': prepare, 'run': run}[sys.argv[1]]()
