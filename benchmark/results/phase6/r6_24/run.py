"""Frozen local native-tool authoring; no outcome-informed retries by host."""
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

from tools import Session, definitions, a
from baseline import sha

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
control_spec = importlib.util.spec_from_file_location('r6_24_controls', HERE / 'controls.py')
controls = importlib.util.module_from_spec(control_spec)
control_spec.loader.exec_module(controls)
spec = importlib.util.spec_from_file_location('r6_24_endpoint', HERE.parent / 'r6_23/endpoint.py')
endpoint = importlib.util.module_from_spec(spec)
spec.loader.exec_module(endpoint)
BASE = 'http://127.0.0.1:11435'
MODEL = 'qwen3:8b'
DIGEST = '500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41'
WEIGHT = 'a3de86cd1c132c822487ededd47a324c50491393e6565cd14bafa40d0b8e686f'
OPTIONS = dict(temperature=0, seed=624, num_ctx=8192, num_predict=384, top_k=20, top_p=.95, repeat_penalty=1)
HTTP = urllib.request.build_opener(urllib.request.ProxyHandler({}))

def now():
    return datetime.now(timezone.utc).isoformat()

def wire(x):
    return json.dumps(x, ensure_ascii=True, separators=(',', ':'))

def save(name, value):
    path = HERE / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, default=lambda v: {'bytes_hex': v.hex()} if isinstance(v, bytes) else str(v)) + '\n', encoding='utf-8')

def read(name):
    return json.loads((HERE / name).read_text())

def api(path, data=None, base=BASE):
    assert base.startswith('http://127.0.0.1:')
    req = urllib.request.Request(base + path, data=wire(data).encode() if data is not None else None,
        headers={'Content-Type': 'application/json'})
    with HTTP.open(req, timeout=30) as response:
        return json.load(response)

def success(args, value):
    return dict(args=args, status='success', value=value, output=[value >> 8, value & 255], consumed=0)

def reject(args, code, stage='validation', offset=0):
    return dict(args=args, status='reject', code=code, stage=stage, offset=offset)

def invalid(args):
    return dict(args=args, validation_error='TYPE')

def prepare():
    assert not (HERE / 'FREEZE.json').exists()
    assert all(sha(ROOT / p) == h for p, h in read('BASELINE.json')['protected_files'].items())
    tasks = [
        dict(id='U1', requirement='Target TwiceSum(x:Int64,y:Int64): materialize add(x,y), then materialize add of that subtotal to itself. Return the second value. Exactly two value steps; only this definition.',
            target='TwiceSum', signatures={'TwiceSum': [['x', 'Int64'], ['y', 'Int64']]}, operations={'TwiceSum': ['value', 'value']}, edges=[],
            cases=[success({'x': 2, 'y': 5}, 14), success({'x': -8, 'y': 8}, 0), success({'x': 16380, 'y': 16387}, 65534),
                reject({'x': 32768, 'y': 0}, 'ENCODE_RANGE', 'encode', None),
                reject({'x': 2**63-1, 'y': 1}, 'OVERFLOW', 'structure'), invalid({'x': True, 'y': 0})]),
        dict(id='U2', requirement='Target Match(a:Int64,b:Int64): materialize Bool eq(a,b), then check that stored Bool with code DIFFERENT and site literal47. Return literal12. Exactly value then check; only this definition.',
            target='Match', signatures={'Match': [['a', 'Int64'], ['b', 'Int64']]}, operations={'Match': ['value', 'check']}, edges=[],
            cases=[success({'a': 0, 'b': 0}, 12), success({'a': -4, 'b': -4}, 12),
                reject({'a': 1, 'b': 2}, 'DIFFERENT'), invalid({'a': None, 'b': 0})]),
        dict(id='U3', requirement='Target Priority(first:Bool,second:Bool): check first with code EARLY/site literal49, then check second with code LATE/site literal51. Return literal44. Exactly these two ordered checks; only this definition.',
            target='Priority', signatures={'Priority': [['first', 'Bool'], ['second', 'Bool']]}, operations={'Priority': ['check', 'check']}, edges=[],
            cases=[reject({'first': False, 'second': False}, 'EARLY'), reject({'first': False, 'second': True}, 'EARLY'),
                reject({'first': True, 'second': False}, 'LATE'), success({'first': True, 'second': True}, 44), invalid({'first': 1, 'second': True})]),
        dict(id='U4', requirement='Author reusable Double(v:Int64): one value add(v,v), returning it. Target Combine(n:Int64,m:Int64) calls the SAME Double with n, then m, then materializes addition of the two call results and returns it. Three target steps compose,compose,value; exactly these two definitions, no inlining.',
            target='Combine', signatures={'Double': [['v', 'Int64']], 'Combine': [['n', 'Int64'], ['m', 'Int64']]},
            operations={'Double': ['value'], 'Combine': ['compose', 'compose', 'value']}, edges=[['Combine', 'Double'], ['Combine', 'Double']],
            cases=[success({'n': 3, 'm': 7}, 20), success({'n': -3, 'm': 3}, 0), success({'n': 16000, 'm': 16000}, 64000),
                reject({'n': 2**62, 'm': 0}, 'OVERFLOW', 'structure')]),
        dict(id='U5', requirement='Author Leaf(v:Int64): check le(0,v) code NEGATIVE/site literal53, then value add(v,2), returning it. Middle(v:Int64) has one compose Leaf(v=ref v), returning it. Target Shell(v:Int64,permit:Bool): check permit code DENIED/site literal55, then compose Middle(v=ref v), returning that call result. Exactly three definitions and these ordered steps; no inlining.',
            target='Shell', signatures={'Leaf': [['v', 'Int64']], 'Middle': [['v', 'Int64']], 'Shell': [['v', 'Int64'], ['permit', 'Bool']]},
            operations={'Leaf': ['check', 'value'], 'Middle': ['compose'], 'Shell': ['check', 'compose']}, edges=[['Middle', 'Leaf'], ['Shell', 'Middle']],
            cases=[success({'v': 0, 'permit': True}, 2), success({'v': 65533, 'permit': True}, 65535),
                reject({'v': -1, 'permit': True}, 'NEGATIVE'), reject({'v': -1, 'permit': False}, 'DENIED'),
                reject({'v': 2**63-1, 'permit': False}, 'DENIED'), reject({'v': 2**63-1, 'permit': True}, 'OVERFLOW', 'structure'),
                invalid({'v': 0, 'permit': 0})])]
    schedules = [['T', 'A', 'B'], ['A', 'B', 'T'], ['B', 'T', 'A']]
    save('TASKS.json', dict(tasks=tasks, schedule=[[t['id'], tr] for i, t in enumerate(tasks) for tr in schedules[i % 3]],
        scored_discovery=False, cases=26, source='new coordinator-authored synthetic requirements'))
    toolsets = {t['id']: definitions(sorted(set(sum(t['operations'].values(), [])))) for t in tasks}
    save('TOOLS.json', toolsets)
    contract = (HERE.parent / 'r6_23/CONTRACT.txt').read_text()
    shared, rest = contract.split('\nTRACK_A\n')
    full, compact = rest.split('\nTRACK_B\n')
    tool_contract = shared.replace('Do not emit examples, schemas, Markdown or commentary. Return one JSON packet.', '') + '\nUse the supplied native tools to author each definition and explicitly finalize its result. Finish by validate_candidate. No packet in chat content. Errors leave construction unchanged; retry only within the fixed budget. No supplied library.'
    prompts = {}
    for t in tasks:
        prompts[t['id']] = {}
        for track, system in [('T', tool_contract), ('A', shared + '\n' + full), ('B', shared + '\n' + compact)]:
            prompts[t['id']][track] = [dict(role='system', content=system), dict(role='user', content=t['requirement'])]
    save('PROMPTS.json', prompts)
    save('SCRIPTED-QUALIFICATION.json', controls.run())
    files = ['baseline.py', 'BASELINE.json', 'tools.py', 'controls.py', 'run.py', 'PROTOCOL.md', 'INTERFACE.md',
        'TASKS.json', 'TOOLS.json', 'PROMPTS.json', 'SCRIPTED-QUALIFICATION.json']
    save('FREEZE.json', dict(timestamp=now(), files={p: sha(HERE / p) for p in files}, model=MODEL, digest=DIGEST,
        options=OPTIONS, think=False, native_tools=True, no_format_override=True))
    print('Frozen5 tasks/26 cases, three tracks and scripted qualification; no inference')

def evaluate(text, track, task):
    result = a.construct(text, 'A' if track == 'A' else 'B')
    result.update(structural_valid='NOT_REACHED', functional_success=False, cases=[], expansion_seconds=None, execution_seconds=None)
    if not result['typed_valid']:
        return result
    artifact = result['artifact']
    defs = {d['name']: d for d in artifact['definitions']}
    signatures = {n: [[p['name'], p['type']] for p in d['params']] for n, d in defs.items()}
    operations = {n: [next(s['node']['op'] for s in d['steps'] if s['id'] == sid) for sid in d['order']] for n, d in defs.items()}
    edges = sorted([[n, s['node']['symbol']] for n, d in defs.items() for s in d['steps'] if s['node']['op'] == 'compose'])
    structural = artifact['target'] == task['target'] and signatures == task['signatures'] and operations == task['operations'] and edges == sorted(task['edges'])
    result.update(structural_valid=structural, observed_structure=dict(signatures=signatures, operations=operations, edges=edges), expansion_seconds=0, execution_seconds=0)
    for case in task['cases']:
        begin = time.perf_counter()
        try:
            pkg = a.package(artifact, case['args'])
            expanded = a.c.expand(pkg)
        except a.c.Diagnostic as e:
            result['expansion_seconds'] += time.perf_counter() - begin
            result['cases'].append(dict(expected=case, diagnostic=e.data,
                passed=case.get('validation_error') == e.data['code'], execution='NOT_REACHED'))
            continue
        result['expansion_seconds'] += time.perf_counter() - begin
        begin = time.perf_counter()
        obs = a.c.vm.execute(expanded['plan'], b'')
        result['execution_seconds'] += time.perf_counter() - begin
        match = 'validation_error' not in case and obs['status'] == case['status']
        if match and case['status'] == 'success':
            match = obs['value'] == case['value'] and list(obs['output']) == case['output'] and obs['consumed'] == case['consumed']
        elif match:
            match = all(obs['error'][k] == case[k] for k in ('code', 'stage', 'offset'))
        result['cases'].append(dict(expected=case, observation=obs, package=pkg, expanded=expanded, passed=match))
    result['functional_success'] = structural and all(c['passed'] for c in result['cases'])
    return result

class Runner:
    def __init__(self):
        self.proc = None
        self.started = time.perf_counter()
        self.rows = []
        self.log = HERE / 'SERVER.log'

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
        with self.log.open('xb') as f:
            self.proc = subprocess.Popen(['ollama', 'serve'], env=env, stdout=f, stderr=f)
        for _ in range(60):
            assert self.proc.poll() is None
            try:
                api('/api/version')
                break
            except OSError:
                time.sleep(.5)
        version = api('/api/version')
        selected = next(m for m in api('/api/tags')['models'] if m['name'] == MODEL)
        assert version['version'] == '0.35.0' and selected['digest'] == DIGEST
        show = api('/api/show', {'model': MODEL})
        assert 'tools' in show.get('capabilities', []), 'model native tools unsupported'
        save('INVENTORY.json', dict(timestamp=now(), version=version, selected=selected, show=show,
            options=OPTIONS, overrides=overrides, pid=self.proc.pid,
            weight_sha256=read('BASELINE.json')['weight_sha256'], effective_context='verified per request after warmup'))

    def call(self, label, messages, toolset=None, cap=384, warm=False, deadline=None):
        assert len(self.rows) < 132 and time.perf_counter() - self.started < 1200
        if deadline and time.perf_counter() >= deadline:
            raise TimeoutError('task wall bound before inference')
        pre = None
        if not warm:
            loaded = api('/api/ps')
            ep = endpoint.discover(self.log, self.proc.pid, loaded, DIGEST, WEIGHT)
            proxy = wire(dict(messages=messages, tools=toolset or []))
            tokens = api('/tokenize', dict(content=proxy, add_special=True, parse_special=True), ep['base'])
            count = len(tokens['tokens'])
            pre = dict(endpoint=ep, proxy_tokens=count, template_reserve=1024)
            assert count + 1024 <= 6144 and count + 1024 + cap + 256 <= 8192, 'input guard'
        request = dict(model=MODEL, messages=messages, think=False, stream=True, keep_alive='10m', options=dict(OPTIONS, num_predict=cap))
        if toolset:
            request['tools'] = toolset
        serialized = wire(request)
        save('calls/' + label + '-request.json', dict(request=request, serialized=serialized,
            request_sha256=hashlib.sha256(serialized.encode()).hexdigest(), preflight=pre))
        begin = time.perf_counter()
        offset = self.log.stat().st_size
        chunks, error, status, body = [], None, None, None
        with (HERE / 'calls' / (label + '-stream.jsonl')).open('x', encoding='utf-8') as f:
            try:
                req = urllib.request.Request(BASE + '/api/chat', data=serialized.encode(), headers={'Content-Type': 'application/json'})
                with HTTP.open(req, timeout=60) as response:
                    status = response.status
                    for line in response:
                        event = dict(timestamp=now(), elapsed_seconds=time.perf_counter() - begin, raw=line.decode(errors='replace'))
                        f.write(wire(event) + '\n')
                        f.flush()
                        chunk = json.loads(line)
                        chunks.append(chunk)
                        if 'error' in chunk:
                            error, body = chunk['error'], event['raw']
                        if time.perf_counter() - begin > 60 or (deadline and time.perf_counter() > deadline):
                            error = 'CLIENT_WALL_LIMIT'
                            break
            except urllib.error.HTTPError as e:
                status, error, body = e.code, str(e), e.read().decode(errors='replace')
                f.write(wire(dict(timestamp=now(), elapsed_seconds=time.perf_counter() - begin, raw=body, http_status=status)) + '\n')
            except (OSError, ValueError) as e:
                error = repr(e)
        wall = time.perf_counter() - begin
        time.sleep(.1)
        end = self.log.stat().st_size
        excerpt = self.log.read_bytes()[offset:end].decode(errors='replace')
        final = next((x for x in reversed(chunks) if x.get('done')), {})
        msg = dict(role='assistant', content=''.join(x.get('message', {}).get('content', '') for x in chunks))
        tc = [t for x in chunks for t in x.get('message', {}).get('tool_calls', [])]
        if tc:
            msg['tool_calls'] = tc
        thinking = ''.join(x.get('message', {}).get('thinking', '') for x in chunks)
        if thinking:
            msg['thinking'] = thinking
        row = dict(id=label, timestamp=now(), http_status=status, error=error, error_body=body, final=final,
            message=msg, wall_seconds=wall, preflight=pre, log_excerpt=excerpt, log_byte_span=[offset, end],
            tokens={k: final.get(k) for k in ('prompt_eval_count', 'prompt_eval_cached_count', 'eval_count')},
            durations_ns={k: final.get(k) for k in ('total_duration', 'load_duration', 'prompt_eval_duration', 'eval_duration')},
            completion=bool(final.get('done') and final.get('done_reason') == 'stop' and not error))
        self.rows.append(row)
        save('calls/' + label + '-result.json', row)
        save('INFERENCE.json', dict(rows=self.rows))
        print(label, 'stop', final.get('done_reason'), 'tools', len(tc), 'tokens', row['tokens'], 'error', error, flush=True)
        if error and 'token repeat limit' not in str(error) and 'token repeat limit' not in str(body):
            raise RuntimeError('transport/runtime failure: ' + str(error))
        if not error and final:
            loaded = api('/api/ps')
            slots = [int(n) for n in re.findall(r'n_ctx_slot = (\d+)', excerpt)]
            counts = [int(n) for n in re.findall(r'task.n_tokens = (\d+)', excerpt)]
            intact = (len(loaded['models']) == 1 and loaded['models'][0]['digest'] == DIGEST and loaded['models'][0]['context_length'] == 8192
                and bool(slots) and all(n == 8192 for n in slots) and bool(counts) and counts[0] == final['prompt_eval_count']
                and final['prompt_eval_count'] <= 6144 and final['prompt_eval_count'] + cap + 256 <= 8192
                and 'truncating input prompt' not in excerpt)
            row['delivery'] = dict(intact=intact, slots=slots, logged_tokens=counts, loaded=loaded)
            save('calls/' + label + '-result.json', row)
            save('INFERENCE.json', dict(rows=self.rows))
            assert intact, 'native chat delivery mismatch'
        return row

    def stop(self):
        if self.proc:
            p = subprocess.run(['taskkill', '/PID', str(self.proc.pid), '/T', '/F'], capture_output=True, text=True, timeout=30)
            self.proc.wait(timeout=15)
            save('CLEANUP.json', dict(owned_pid=self.proc.pid, returncode=p.returncode, stdout=p.stdout, stderr=p.stderr))

def run():
    assert not (HERE / 'RUN-STATUS.json').exists(), 'no replay'
    assert all(sha(HERE / p) == h for p, h in read('FREEZE.json')['files'].items())
    assert all(sha(ROOT / p) == h for p, h in read('BASELINE.json')['protected_files'].items())
    runner, outcomes, aborts, fatal = Runner(), [], 0, None
    try:
        runner.start()
        warm = runner.call('control_warm', [dict(role='user', content='Reply with the word ready.')], cap=64, warm=True)
        assert warm['completion']
        echo = [dict(type='function', function=dict(name='echo', description='Select this inert tool with the requested text.',
            parameters=dict(type='object', properties={'text': {'type': 'string'}}, required=['text'], additionalProperties=False)))]
        control = runner.call('control_tools', [dict(role='user', content='Call echo with text local24.')], echo, cap=64)
        assert control['completion'] and control['message'].get('tool_calls') == [dict(function=dict(name='echo', arguments=dict(text='local24')))], 'native tool calibration failed'
        save('MODEL-INTERFACE-CONTROL.json', dict(passed=True, call=control['id'], scripted_program=False))
        tasks = {t['id']: t for t in read('TASKS.json')['tasks']}
        for tid, track in read('TASKS.json')['schedule']:
            task = tasks[tid]
            messages = copy.deepcopy(read('PROMPTS.json')[tid][track])
            deadline = time.perf_counter() + 180
            rows, transcripts, reason, evaluation = [], [], None, None
            toolset = read('TOOLS.json')[tid] if track == 'T' else None
            session = Session(sorted(set(sum(task['operations'].values(), [])))) if track == 'T' else None
            inputs, outputs, retry_pending, repairs = 0, 0, False, 0
            for index in range(24 if track == 'T' else 1):
                if outputs >= 4096 or inputs >= 60000 or time.perf_counter() >= deadline:
                    reason = 'TASK_BUDGET'
                    break
                if retry_pending:
                    repairs += 1
                    retry_pending = False
                row = runner.call(f'{tid}_{track}_{index:02d}', messages, toolset,
                    cap=min(384 if track == 'T' else 4096, 4096 - outputs), deadline=deadline)
                rows.append(row['id'])
                inputs += row['tokens']['prompt_eval_count'] or 0
                outputs += row['tokens']['eval_count'] or 0
                if not row['completion']:
                    reason = 'RUNTIME_ABORT' if row['error'] else 'OUTPUT_BUDGET'
                    if row['error']:
                        aborts += 1
                    break
                if track != 'T':
                    evaluation = evaluate(row['message']['content'], track, task)
                    reason = 'CANDIDATE_RETURNED'
                    break
                messages.append(row['message'])
                calls = row['message'].get('tool_calls', [])
                if not calls:
                    reason = 'NO_TOOL_CALL'
                    break
                for x in calls:
                    if session.calls >= 24:
                        reason = 'TOOL_BUDGET'
                        break
                    result = session.dispatch(x)
                    transcripts.append(dict(model_call=row['id'], call=x, result=result))
                    # Native tool results are compact response objects; no argument repair.
                    messages.append(dict(role='tool', tool_name=x.get('function', {}).get('name', 'invalid'), content=wire(result['response'])))
                    retry_pending |= not result['success']
                    if session.completed:
                        evaluation = evaluate(wire(session.packet), 'B', task)
                        reason = 'CANDIDATE_COMPLETED'
                        break
                save('interactions/' + tid + '_T.json', dict(messages=messages, tool_transcript=transcripts,
                    incomplete_packet=session.packet, finalized=sorted(session.finalized)))
                if reason:
                    break
            outcome = dict(task=tid, track=track, calls=rows, tool_transcript=transcripts, repairs=repairs,
                termination=reason or 'MODEL_CALL_BUDGET', evaluation=evaluation,
                incomplete_packet=session.packet if session else None, finalized=sorted(session.finalized) if session else None)
            outcomes.append(outcome)
            save('candidates/' + tid + '_' + track + '.json', outcome)
            save('ACCEPTANCE.json', dict(rows=outcomes))
            print(tid, track, outcome['termination'], 'accepted', bool(evaluation and evaluation['functional_success']), flush=True)
            if aborts >= 2:
                reason = 'REPEATED_RUNTIME_ABORTS'
                break
    except Exception as e:
        fatal = repr(e)
        save('HALT.json', dict(timestamp=now(), error=fatal, traceback=__import__('traceback').format_exc()))
    finally:
        runner.stop()
        save('RUN-STATUS.json', dict(timestamp=now(), calls=len(runner.rows), candidates=len(outcomes),
            fatal=fatal, runtime_aborts=aborts, total_seconds=time.perf_counter() - runner.started,
            stopped=True, manual_repairs=0))

if __name__ == '__main__':
    {'prepare': prepare, 'run': run}[sys.argv[1]]()
