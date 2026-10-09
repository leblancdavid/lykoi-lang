"""R6.21 bounded nonproduction authoring; no historical writes or remote calls."""
import copy
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

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT / 'experiments/typed_composition_r6_18'))
import composition as c
import jsonschema

MODEL = 'qwen3:8b'
DIGEST = '500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41'
WEIGHT = 'a3de86cd1c132c822487ededd47a324c50491393e6565cd14bafa40d0b8e686f'
BASE = 'http://127.0.0.1:11435'
OPTIONS = dict(temperature=0, seed=621, num_ctx=8192, top_k=20,
               top_p=.95, repeat_penalty=1)
HTTP = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def wire(x):
    return json.dumps(x, ensure_ascii=True, separators=(',', ':'))


def save(name, x):
    p = HERE / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(x, indent=2, ensure_ascii=True,
                 default=lambda v: {'bytes_hex': v.hex()} if isinstance(v, bytes) else str(v)) + '\n', encoding='utf-8')


def read(name):
    return json.loads((HERE / name).read_text())


def cmd(args):
    p = subprocess.run(args, capture_output=True, text=True, timeout=30)
    return dict(args=args, returncode=p.returncode, stdout=p.stdout, stderr=p.stderr)


def api(path, data=None, base=BASE):
    assert base.startswith('http://127.0.0.1:')
    assert path in ('/api/version', '/api/tags', '/api/show', '/api/ps', '/api/generate', '/tokenize')
    request = urllib.request.Request(base + path, data=wire(data).encode() if data is not None else None,
                                     headers={'Content-Type': 'application/json'})
    with HTTP.open(request, timeout=180) as response:
        return json.load(response)


def preservation():
    old = ROOT / 'benchmark/results/phase6/r6_20'
    pins = read_old = json.loads((old / 'BASELINE.json').read_text())['protected_files'].copy()
    for round_name in ('r6_19', 'r6_20'):
        directory = old.parent / round_name
        pub = json.loads((directory / 'PUBLICATION-IDENTITIES.json').read_text())
        for p, item in pub['files'].items():
            assert sha(ROOT / p) == item['sha256'], p
            pins[p] = item['sha256']
        for name in ('PUBLICATION-IDENTITIES.json', 'VERIFICATION.json'):
            p = directory / name
            pins[p.relative_to(ROOT).as_posix()] = sha(p)
    assert all(sha(ROOT / p) == h for p, h in pins.items())
    ledger = json.loads((ROOT / 'benchmark/results/phase6/r6_19/BASELINE.json').read_text())['kernel_ledger']
    assert len(ledger['baseline_kernel']) + len(ledger['preserved_additions']) == 26
    return dict(timestamp=now(), protected_files=pins, protected_count=len(pins), mismatches=[],
                kernel=26, foundation=c.FOUNDATION, wrapper=sha(Path(c.__file__)),
                initial_git=cmd(['git', 'status', '--short']), head=cmd(['git', 'rev-parse', 'HEAD']))


def region(name, steps, result, params=None, dependencies=None):
    return dict(name=name, revision=1, params=params or [], dependencies=dependencies or {},
                steps=steps, order=[s['id'] for s in steps], result=result, result_type='Int64')


def step(name, typ, node, deps=None):
    return dict(id=name, type=typ, deps=deps or [], node=node)


def obj(properties):
    return dict(type='object', properties=properties, required=list(properties), additionalProperties=False)


def schemas():
    full = json.loads((ROOT / 'experiments/typed_composition_r6_18/typed-composition-1.schema.json').read_text())
    d = full['$defs']['definition']
    d['required'].remove('identity')
    del d['properties']['identity']
    definition = dict(d, **{'$defs': full['$defs']})
    props = d['properties']
    header = obj({k: props[k] for k in ('name', 'revision', 'params', 'dependencies', 'result_type')})
    header['properties'].update(operations=dict(type='array', uniqueItems=True,
        items={'enum': ['value', 'check', 'compose']}), steps=dict(type='array', minItems=1, maxItems=32,
        items=obj({'id': {'$ref': '#/$defs/name'}, 'type': {'$ref': '#/$defs/type'}})))
    header['required'] += ['operations', 'steps']
    bodies = obj({'bodies': dict(type='array', minItems=1, maxItems=32,
        items=obj({k: full['$defs']['step']['properties'][k] for k in ('id', 'deps', 'node')}))})
    stages = [header, bodies, obj({'order': props['order']}), obj({'result': props['result']})]
    for schema in stages:
        schema['$defs'] = full['$defs']
    return dict(definition=definition, stages=stages)


def task(i, requirement, params, cases, feature, structure):
    return dict(id=i, requirement=requirement, params=params, cases=cases, feature=feature, structure=structure)


def success(args, value):
    return dict(args=args, status='success', value=value, output=[value >> 8, value & 255], consumed=0)


def reject(args, code):
    return dict(args=args, status='reject', code=code)


def prepare():
    assert not (HERE / 'FREEZE.json').exists(), 'do not overwrite frozen experiment'
    save('BASELINE.json', preservation())
    save('SCHEMAS.json', schemas())
    library = json.loads((ROOT / 'benchmark/results/phase6/r6_20/LIBRARY.json').read_text())
    save('LIBRARY.json', library)
    integer = [dict(name='n', type='Int64')]
    boolean = [dict(name='flag', type='Bool')]
    features = [
        task('F1', 'Declare no parameters. Materialize integer83, Boolean false and Unit null as three value steps; return the integer step.', [], [success({}, 83)], 'operation selection / typed values', 'typed'),
        task('F2', 'Declare parameter n:Int64. One value step copies n; return that step.', integer, [success({'n': n}, n) for n in (0, 17, 65535)], 'typed input declarations', 'copy'),
        task('F3', 'No parameters. Materialize integer13 then a second value step that adds the first step to itself. Return the second.', [], [success({}, 26)], 'local dependency references', 'double'),
        task('F4', 'Declare flag:Bool. Two ordered Unit checks test flag then const false, code BEFORE then AFTER, site const12. Return const12.', boolean, [reject({'flag': False}, 'BEFORE'), reject({'flag': True}, 'AFTER')], 'ordered composition', 'ordered'),
        task('F5', 'Declare n:Int64. One step calls fixed Relay(q=ref n); return that step. Direct dependency Relay only.', integer, [success({'n': n}, n) for n in (0, 37, 65535)], 'nested reuse', 'relay'),
        task('F6', 'Declare n:Int64. Materialize add(ref n,const3) as one value step; return it.', integer, [success({'n': n}, n + 3) for n in (0, 23, 65532)], 'deterministic output', 'offset3')]
    objectives = [
        task('N1', 'No parameters. Materialize integer97, Boolean true and Unit null as three value steps; return the integer step.', [], [success({}, 97)], 'typed values', 'typed'),
        task('N2', 'Declare n:Int64. First value copies n; second value adds first step to itself; return second.', integer, [success({'n': n}, n * 2) for n in (0, 29, 32767)], 'typed dependency computation', 'param_double'),
        task('N3', 'Declare flag:Bool. Two ordered Unit checks test flag then const false, code PRIMARY then SECONDARY, site const14. Return const14.', boolean, [reject({'flag': False}, 'PRIMARY'), reject({'flag': True}, 'SECONDARY')], 'ordered failure', 'ordered'),
        task('N4', 'Declare n:Int64. First step calls fixed Relay(q=ref n); second value adds first result and const2. Return second; direct dependency Relay only.', integer, [success({'n': n}, n + 2) for n in (0, 31, 65533)], 'nested reuse and output', 'relay_offset2')]
    save('TASKS.json', dict(features=features, objectives=objectives,
        schedule=[['N1', 'A'], ['N1', 'B'], ['N2', 'B'], ['N2', 'A'], ['N3', 'A'], ['N3', 'B'], ['N4', 'B'], ['N4', 'A']]))
    controls()
    files = ('run.py', 'PROTOCOL.md', 'CONTRACT-1.txt', 'SCHEMAS.json', 'TASKS.json', 'LIBRARY.json', 'HOST-CONTROLS.json')
    save('FREEZE.json', dict(timestamp=now(), files={p: sha(HERE / p) for p in files},
        baseline=sha(HERE / 'BASELINE.json'), model=MODEL, digest=DIGEST, weight=WEIGHT,
        options=OPTIONS, transport='raw ChatML /api/generate', format='json', safe_input=3584,
        caps=dict(A=2048, B_stage=512, feature=2048), manual_repairs=0))
    print('Frozen; controls pass; no inference performed.', flush=True)


def package(definition, library, args):
    sealed = c.seal(definition)
    adapter = region('Runner', [step('called', 'Int64', dict(op='compose', symbol=sealed['name'],
        identity=sealed['identity'], args={k: {'const': v} for k, v in args.items()}))],
        {'ref': 'called'}, dependencies={sealed['name']: sealed['identity']})
    return dict(version=c.VERSION, foundation=c.FOUNDATION,
                definitions=copy.deepcopy(library) + [sealed], program=c.seal(adapter))


def structure(d, t):
    if d['params'] != t['params']:
        return False
    nodes = [s['node'] for s in d['steps']]
    mode = t['structure']
    if mode == 'typed':
        return len(nodes) == 3 and all(n['op'] == 'value' for n in nodes) and sorted(s['type'] for s in d['steps']) == ['Bool', 'Int64', 'Unit']
    if mode == 'copy':
        return len(nodes) == 1 and nodes[0] == {'op': 'value', 'expr': {'ref': 'n'}}
    if mode in ('double', 'param_double'):
        return len(nodes) == 2 and nodes[0]['op'] == 'value' and nodes[1] == {'op': 'value', 'expr': {'add': [{'ref': d['steps'][0]['id']}] * 2}} and (mode == 'double' or nodes[0]['expr'] == {'ref': 'n'})
    if mode == 'ordered':
        codes = ['BEFORE', 'AFTER'] if t['id'] == 'F4' else ['PRIMARY', 'SECONDARY']
        return len(nodes) == 2 and d['order'] == [s['id'] for s in d['steps']] and [n.get('code') for n in nodes] == codes and nodes[0].get('test') == {'ref': 'flag'} and nodes[1].get('test') == {'const': False}
    if mode.startswith('relay'):
        first = len(nodes) >= 1 and nodes[0].get('op') == 'compose' and nodes[0].get('symbol') == 'Relay' and nodes[0].get('args') == {'q': {'ref': 'n'}}
        return first and (len(nodes) == 1 if mode == 'relay' else len(nodes) == 2 and nodes[1] == {'op': 'value', 'expr': {'add': [{'ref': d['steps'][0]['id']}, {'const': 2}]}})
    return len(nodes) == 1 and nodes[0] == {'op': 'value', 'expr': {'add': [{'ref': 'n'}, {'const': 3}]}}


def classify(text, schema, t=None):
    begin = time.perf_counter()
    out = dict(json_valid=False, strict_valid='NOT_REACHED', schema_valid='NOT_REACHED',
        type_valid='NOT_REACHED', semantic_valid='NOT_REACHED', executable_correct='NOT_REACHED',
        composition_valid=False, objective_complete=False, classification=None)
    try:
        json.loads(text)
        out['json_valid'] = True
        value = c.load(text)
        out['strict_valid'] = True
        jsonschema.Draft202012Validator(schema).validate(value)
        out['schema_valid'] = True
        out['value'] = value
        if t is None:
            out['classification'] = 'STAGE_VALID'
        else:
            library = read('LIBRARY.json')
            pkg = package(value, library, t['cases'][0]['args'])
            c.validate(pkg)
            out['type_valid'] = True
            expanded = c.expand(pkg)
            out.update(semantic_valid=True, composition_valid=True, package=pkg, expanded_nodes=expanded['nodes'])
            envelopes = []
            correct = structure(value, t)
            for case in t['cases']:
                plan = c.expand(package(value, library, case['args']))['plan']
                obs = c.vm.execute(plan, b'')
                repeated = c.vm.execute(plan, b'')
                assert obs == repeated, 'nondeterministic unchanged VM'
                envelopes.append(dict(case=case, envelope=obs, repeat_equal=True))
                if case['status'] == 'success':
                    correct &= obs['status'] == 'success' and obs['value'] == case['value'] and list(obs['output']) == case['output'] and obs['consumed'] == case['consumed']
                else:
                    correct &= obs['status'] != 'success' and obs['error']['code'] == case['code']
            out.update(executable_correct=bool(correct), objective_complete=bool(correct), envelopes=envelopes,
                       classification='PASS' if correct else 'OBJECTIVE_FAILURE')
    except json.JSONDecodeError as exc:
        out.update(classification='INVALID_JSON', diagnostic=str(exc))
    except jsonschema.ValidationError as exc:
        out.update(schema_valid=False, classification='SCHEMA_VIOLATION', diagnostic=dict(path=list(exc.path), message=exc.message))
    except c.Diagnostic as exc:
        code = exc.data['code']
        if code == 'TYPE':
            out['type_valid'] = False
        elif out['schema_valid'] is True:
            out['semantic_valid'] = False
        out.update(classification=code, diagnostic=exc.data)
    out['validation_seconds'] = time.perf_counter() - begin
    return out


def controls():
    schema = read('SCHEMAS.json')['definition']
    good = region('Control', [step('v', 'Int64', {'op': 'value', 'expr': {'const': 3}})], {'ref': 'v'})
    t = task('C', '', [], [success({}, 3)], '', 'copy')
    rows = []
    def check(label, value, expected, raw=None):
        out = classify(raw if raw is not None else wire(value), schema, t)
        assert out['classification'] == expected, (label, out)
        rows.append(dict(id=label, expected=expected, result=out))
    # Structural obligation deliberately differs, distinguishing valid program from objective.
    check('valid_composition_wrong_objective', good, 'OBJECTIVE_FAILURE')
    check('invalid_json', good, 'INVALID_JSON', '{')
    check('duplicate_key', good, 'SERIALIZATION', '{"name":1,"name":2}')
    bad = copy.deepcopy(good); del bad['order']; check('schema', bad, 'SCHEMA_VIOLATION')
    bad = copy.deepcopy(good); bad['steps'][0]['type'] = 'Bool'; check('type', bad, 'TYPE')
    bad = copy.deepcopy(good); bad['steps'][0]['deps'] = ['v']; check('deps', bad, 'DEPENDENCY')
    bad = copy.deepcopy(good); bad['steps'][0]['node']['expr']['const'] = 70000; check('encoding', bad, 'OBJECTIVE_FAILURE')
    save('HOST-CONTROLS.json', dict(passed=len(rows), rows=rows))


def prompt(system, user):
    return '<|im_start|>system\n' + system + '<|im_end|>\n<|im_start|>user\n' + user + '<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n'


class Runner:
    def __init__(self):
        self.proc = None
        self.log = None
        self.backend = None
        self.records = []
        self.tokenizations = []
        self.delivery = []
        self.started = time.perf_counter()
        self.reason = None

    def start(self):
        try:
            api('/api/version')
        except OSError:
            pass
        else:
            raise RuntimeError('dedicated port occupied')
        env = os.environ.copy()
        env.update(OLLAMA_HOST='127.0.0.1:11435', OLLAMA_NO_CLOUD='1',
            OLLAMA_MODELS=r'D:\Software\.ollama\models', OLLAMA_NUM_PARALLEL='1',
            OLLAMA_CONTEXT_LENGTH='8192', OLLAMA_MAX_LOADED_MODELS='1', OLLAMA_DEBUG='1',
            HTTP_PROXY='http://127.0.0.1:9', HTTPS_PROXY='http://127.0.0.1:9', NO_PROXY='127.0.0.1,localhost')
        self.log = open(HERE / 'SERVER.log', 'ab')
        self.proc = subprocess.Popen(['ollama', 'serve'], env=env, stdout=self.log, stderr=self.log)
        for _ in range(60):
            assert self.proc.poll() is None
            try:
                api('/api/version'); break
            except OSError:
                time.sleep(.5)
        else:
            raise RuntimeError('startup timeout')
        selected = next(x for x in api('/api/tags')['models'] if x['name'] == MODEL)
        assert selected['digest'] == DIGEST
        blob = Path(r'D:\Software\.ollama\models\blobs') / ('sha256-' + WEIGHT)
        assert sha(blob) == WEIGHT
        version = api('/api/version')
        assert version['version'] == '0.35.0'
        save('INVENTORY.json', dict(timestamp=now(), version=version, selected=selected,
            show=api('/api/show', {'model': MODEL}), weight_sha256=WEIGHT, weight_bytes=blob.stat().st_size,
            options=OPTIONS, output_limits=dict(A=2048, B=512, total_per_objective=2048), format='json',
            raw=True, reasoning='explicit empty closed ChatML thinking prefix',
            overrides={k: env[k] for k in ('OLLAMA_HOST', 'OLLAMA_NO_CLOUD', 'OLLAMA_MODELS', 'OLLAMA_NUM_PARALLEL', 'OLLAMA_CONTEXT_LENGTH', 'OLLAMA_MAX_LOADED_MODELS', 'HTTP_PROXY', 'HTTPS_PROXY', 'NO_PROXY')},
            python=cmd(['python', '--version']), gpu=cmd(['nvidia-smi', '--query-gpu=name,memory.total,memory.used,driver_version', '--format=csv']),
            inherited_schema='unchanged R6.18, model identity omitted and mechanically sealed',
            foundation_subset='seq/UInt8 atom/value/check/end/UInt16BE emit; ref/const/add/le/eq',
            authoring_subset='value/check/compose and ref/const/add/le/eq; task-specific nodes filtered in prompt',
            locality='loopback allowlist, local digest and GGUF, offline backend; no OS firewall claim'))

    def tokenize(self, label, text):
        begin = time.perf_counter()
        response = api('/tokenize', {'content': text, 'add_special': True, 'parse_special': True}, self.backend)
        record = dict(id=label, timestamp=now(), prompt_sha256=hashlib.sha256(text.encode()).hexdigest(),
            response=response, count=len(response['tokens']), seconds=time.perf_counter() - begin,
            options=dict(add_special=True, parse_special=True), backend=self.backend)
        self.tokenizations.append(record)
        save('TOKENIZATIONS.json', dict(rows=self.tokenizations))
        return record['count']

    def call(self, label, text, cap, expected=None, warm=False):
        if self.reason:
            raise RuntimeError(self.reason)
        assert self.proc.poll() is None, 'owned server exited'
        if len(self.records) >= 30 or time.perf_counter() - self.started > 1200:
            self.reason = 'call/time ceiling'; raise RuntimeError(self.reason)
        if not warm:
            expected = self.tokenize(label, text)
            if expected > 3584 or expected + cap + 256 > 8192:
                save('REJECTED-' + label + '.json', dict(prompt=text, count=expected, cap=cap, reason='SAFE_INPUT_BUDGET', inference_sent=False))
                self.reason = 'safe input budget'; raise RuntimeError(self.reason)
        request = dict(model=MODEL, prompt=text, raw=True, stream=False, format='json',
                       keep_alive='10m', options=dict(OPTIONS, num_predict=cap))
        serialized = wire(request)
        begin = time.perf_counter()
        offset = (HERE / 'SERVER.log').stat().st_size
        status = None; body = None; response = None; error = None
        try:
            req = urllib.request.Request(BASE + '/api/generate', data=serialized.encode(), headers={'Content-Type': 'application/json'})
            with HTTP.open(req, timeout=180) as r:
                status = r.status; body = r.read().decode(); response = json.loads(body)
        except urllib.error.HTTPError as exc:
            status = exc.code; body = exc.read().decode(errors='replace'); error = repr(exc)
        except (OSError, ValueError) as exc:
            error = repr(exc)
        latency = time.perf_counter() - begin
        time.sleep(.1)
        end = (HERE / 'SERVER.log').stat().st_size
        log = (HERE / 'SERVER.log').read_bytes()[offset:end].decode(errors='replace')
        try:
            loaded = api('/api/ps')
        except OSError as exc:
            loaded = {'error': repr(exc)}
        counts = {k: response.get(k) if response else None for k in ('prompt_eval_count', 'prompt_eval_cached_count', 'eval_count')}
        slots = [int(x) for x in re.findall(r'n_ctx_slot = (\d+)', log)]
        tasks = [int(x) for x in re.findall(r'task.n_tokens = (\d+)', log)]
        intact = (status == 200 and expected is not None and counts['prompt_eval_count'] == expected
            and 'truncating input prompt' not in log and bool(slots) and all(x == 8192 for x in slots)
            and bool(tasks) and tasks[0] == expected and any(x.get('context_length') == 8192 for x in loaded.get('models', [])))
        delivery = dict(id=label, expected_input=expected, reported_input=counts['prompt_eval_count'],
            slots=slots, task_tokens=tasks, truncation='truncating input prompt' in log,
            intact=intact if not warm else 'WARMUP_NOT_QUALIFIED', output_cap=cap,
            context=8192, utilization=expected / 8192 if expected is not None else None,
            reserved_utilization=(expected + cap) / 8192 if expected is not None else None,
            done_reason=response.get('done_reason') if response else None)
        record = dict(id=label, timestamp=now(), request=request, serialized_request=serialized,
            request_sha256=hashlib.sha256(serialized.encode()).hexdigest(),
            prompt_sha256=hashlib.sha256(text.encode()).hexdigest(), status=status,
            body=body, response=response, error=error, tokens=counts,
            durations_ns={k: response.get(k) if response else None for k in ('total_duration', 'load_duration', 'prompt_eval_duration', 'eval_duration')},
            wall_seconds=latency, log_byte_span=[offset, end], loaded=loaded, delivery=delivery)
        self.records.append(record); self.delivery.append(delivery)
        save('calls/' + label + '.json', record)
        save('PROMPT-DELIVERY.json', dict(rows=self.delivery, safe_input=3584, effective_context=8192,
            gate='exact local tokenizer/report/log counts plus no truncation; conservative half-context input bound'))
        print(label, status, counts, 'intact', delivery['intact'], flush=True)
        if status != 200:
            self.reason = 'runtime failure'; raise RuntimeError(self.reason)
        if not warm and not intact:
            self.reason = 'prompt delivery gap'; raise RuntimeError(self.reason)
        return record

    def qualify(self):
        short = prompt('Extract exactly the requested JSON.', 'Return {"marker":"warm","number":21}.')
        self.call('warmup', short, 64, warm=True)
        text = (HERE / 'SERVER.log').read_text(errors='replace')
        ports = re.findall(r'--port (\d+) --host 127\.0\.0\.1', text)
        if not ports:
            self.reason = 'backend tokenizer unavailable'; raise RuntimeError(self.reason)
        self.backend = 'http://127.0.0.1:' + ports[-1]
        count = self.tokenize('warmup_recount', short)
        if count != self.records[0]['tokens']['prompt_eval_count']:
            self.reason = 'tokenizer count mismatch'; raise RuntimeError(self.reason)
        rows = []
        for index, padding in enumerate((0, 800, 1400)):
            text = prompt('Extract the first and last sentinel; ignore padding.',
                'FIRST=cerulean\n' + ' pebble' * padding + '\nLAST=amber\nReturn {"first":"cerulean","last":"amber"}.')
            rec = self.call('delivery_' + str(index), text, 128)
            observed = json.loads(rec['response']['response'])
            passed = observed == {'first': 'cerulean', 'last': 'amber'}
            rows.append(dict(id=rec['id'], passed=passed, observed=observed))
            save('DELIVERY-CONTROLS.json', dict(rows=rows))
            if not passed:
                self.reason = 'neutral sentinel failure'; raise RuntimeError(self.reason)
        text = prompt('Do not run this oversized control.', ' pebble' * 2000)
        count = self.tokenize('oversized_guard', text)
        assert count > 3584
        save('OVERSIZED-GUARD.json', dict(prompt=text, count=count, safe_input=3584, inference_sent=False, rejected=True))

    def stop(self):
        if self.proc:
            save('LOCALITY.json', dict(timestamp=now(), owned_pid=self.proc.pid, backend=self.backend,
                process_snapshot=cmd(['pwsh', '-NoProfile', '-Command', "Get-CimInstance Win32_Process -Filter \"Name like '%ollama%' or Name='llama-server.exe'\" | Select-Object ProcessId,ParentProcessId,Name,CommandLine,WorkingSetSize | ConvertTo-Json"])))
            save('CLEANUP.json', dict(timestamp=now(), owned_pid=self.proc.pid,
                termination=cmd(['taskkill', '/PID', str(self.proc.pid), '/T', '/F']), desktop='not targeted'))
            self.proc.wait(timeout=15)
        if self.log:
            self.log.close()


def task_prompt(t, interface, stage=None, prior=None):
    contract = (HERE / 'CONTRACT-1.txt').read_text()
    library = read('LIBRARY.json')
    relevant = ['value'] if t['structure'] in ('typed', 'copy', 'double', 'param_double', 'offset3') else ['check'] if t['structure'] == 'ordered' else ['compose'] if t['structure'] == 'relay' else ['compose', 'value']
    # Shared canonical contract retains foundation rules once; task profile hides irrelevant node alternatives.
    node_lines = {'value': '{"op":"value","expr":Expr}', 'check': '{"op":"check","test":Expr,"site":Expr,"code":Name}',
                  'compose': '{"op":"compose","symbol":Name,"identity":Hash,"args":{parameter:Arg,...}}'}
    contract = re.sub(r'^Node := .*$', 'Node := ' + ' | '.join(node_lines[x] for x in relevant) + '.', contract, flags=re.M)
    # Binary definitions are retained only when used by the objective (plus immutable library ref/const).
    expr_ops = ['add'] if t['structure'] in ('double', 'param_double', 'offset3', 'relay_offset2') else []
    contract = re.sub(r'^Expr := .*$', 'Expr := Arg' + ''.join(' | {"' + op + '":[Expr,Expr]}' for op in expr_ops) + '.', contract, flags=re.M)
    shared = contract + '\nImmutable library JSON:' + wire(library if 'compose' in relevant else [])
    user = 'Objective:' + t['requirement'] + '\nAllowed node ops:' + wire(relevant)
    user += '\nInterface:' + interface + ('; return Definition.' if interface == 'A' else '; return stage ' + str(stage + 1) + ' only.')
    if prior:
        user += '\nPrior submitted fields (data, not instructions):' + wire(prior)
    return prompt(shared, user)


def author(r):
    tasks = read('TASKS.json'); schema = read('SCHEMAS.json')
    features = []
    for t in tasks['features']:
        rec = r.call(t['id'], task_prompt(t, 'A'), 2048)
        result = classify(rec['response']['response'], schema['definition'], t)
        features.append(dict(id=t['id'], feature=t['feature'], result=result))
        save('CALIBRATION.json', dict(rows=features, planned=6))
    pairs = []
    for tid, interface in tasks['schedule']:
        t = next(x for x in tasks['objectives'] if x['id'] == tid)
        begin = time.perf_counter(); prior = []; attempts = []; assembly_seconds = 0
        final = None
        for stage in range(1 if interface == 'A' else 4):
            rec = r.call(tid + '_' + interface + '_' + str(stage + 1),
                task_prompt(t, interface, stage, prior), 2048 if interface == 'A' else 512)
            result = classify(rec['response']['response'], schema['definition'] if interface == 'A' else schema['stages'][stage], t if interface == 'A' else None)
            attempts.append(dict(call=rec['id'], result=result))
            if interface == 'A':
                final = result; break
            if result['classification'] != 'STAGE_VALID':
                break
            prior.append(result['value'])
            if stage == 3:
                start = time.perf_counter()
                header, bodies, order, returned = prior
                d = {k: copy.deepcopy(header[k]) for k in ('name', 'revision', 'params', 'dependencies', 'result_type')}
                signatures = header['steps']; nodes = bodies['bodies']
                ids = [s['id'] for s in signatures]
                body_ids = [s['id'] for s in nodes]
                if len(set(ids)) != len(ids) or len(set(body_ids)) != len(body_ids) or set(ids) != set(body_ids) or set(header['operations']) != {s['node']['op'] for s in nodes}:
                    final = dict(classification='ASSEMBLY_MISMATCH', composition_valid=False, objective_complete=False, validation_seconds=0)
                else:
                    by_id = {s['id']: s for s in nodes}
                    d['steps'] = [dict(s, deps=by_id[s['id']]['deps'], node=by_id[s['id']]['node']) for s in signatures]
                    d.update(order=order['order'], result=returned['result'])
                    assembly_seconds = time.perf_counter() - start
                    final = classify(wire(d), schema['definition'], t)
                    save('assembled/' + tid + '_B.json', d)
        row = dict(id=tid, interface=interface, attempts=attempts, final=final,
            objective_complete=bool(final and final['objective_complete']), composition_valid=bool(final and final['composition_valid']),
            repair_attempts=0, assembly_seconds=assembly_seconds, session_seconds=time.perf_counter() - begin,
            unused_output_budget=2048 - sum(read('calls/' + x['call'] + '.json')['tokens']['eval_count'] for x in attempts))
        pairs.append(row)
        save('COMPARISON.json', dict(rows=pairs, planned=8, not_reached=tasks['schedule'][len(pairs):]))


def run():
    assert not (HERE / 'RUN-STATUS.json').exists(), 'do not replay qualification'
    frozen = read('FREEZE.json')
    assert all(sha(HERE / p) == h for p, h in frozen['files'].items())
    assert all(sha(ROOT / p) == h for p, h in read('BASELINE.json')['protected_files'].items())
    r = Runner(); error = None; qualified = False
    try:
        r.start(); r.qualify(); qualified = True; author(r)
    except Exception as exc:
        error = repr(exc)
        save('HALT.json', dict(timestamp=now(), reason=r.reason, error=error,
            traceback=__import__('traceback').format_exc(), delivery_qualified=qualified))
    finally:
        r.stop()
        save('RUN-STATUS.json', dict(timestamp=now(), calls=len(r.records), tokenizer_calls=len(r.tokenizations),
            delivery_qualified=qualified, error=error, reason=r.reason, total_seconds=time.perf_counter() - r.started,
            manual_repairs=0, inference_retry=0, stopped=True))


if __name__ == '__main__':
    {'prepare': prepare, 'run': run}[sys.argv[1]]()
