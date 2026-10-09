"""One frozen task, metadata-aware workflow and model-free evaluation/replay."""
import copy
import json
import sys
import time
import traceback
import unittest
from common import HERE, ROOT, tools, sha, save, read, now, historical_runner
from transport import normalize, semantic_call, feedback, strict_loads, TransportError

def prepare():
    assert not (HERE / 'RUN-STATUS.json').exists()
    if (HERE / 'FREEZE.json').exists():
        assert not (HERE / 'PREPARATION-FREEZE.json').exists()
        save('PREPARATION-FREEZE.json', read('FREEZE.json'))
        save('PREPARATION-NOTE.json', dict(model_exposure=False, runtime_attempt=False,
            reason='Pre-exposure code review found strict numeric decoding applied globally would reject legitimate provider inventory floats and saved timing measurements. Duplicate-key rejection retained globally; noninteger rejection confined to semantic string arguments. Unknown inert metadata may contain finite numbers.',
            prior_freeze_sha256=sha(HERE / 'FREEZE.json')))
    assert all(sha(ROOT / p) == h for p, h in read('BASELINE.json')['protected_files'].items())
    suite = unittest.defaultTestLoader.discover(str(HERE), pattern='test_transport.py')
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    save('QUALIFICATION.json', dict(tests=result.testsRun, failures=len(result.failures), errors=len(result.errors), passed=result.wasSuccessful(), live_inference=False))
    assert result.wasSuccessful()
    r = historical_runner()
    t = dict(id='F1', target='OffsetTotal', requirement='Construct only OffsetTotal(a:Int64,b:Int64). Store the subtotal of a and b as an immutable Int64 value. In a second value step, increase that stored subtotal by the constant 3. Return the second stored value. Exactly two ordered value steps, with explicit dependencies. Use the native construction tools and finish with validate_candidate.',
        signatures={'OffsetTotal': [['a', 'Int64'], ['b', 'Int64']]}, operations={'OffsetTotal': ['value', 'value']}, edges=[],
        cases=[r.success({'a': 2, 'b': 4}, 9), r.success({'a': -3, 'b': 0}, 0), r.success({'a': 32766, 'b': 32766}, 65535),
            r.reject({'a': 32767, 'b': 32767}, 'ENCODE_RANGE', 'encode', None),
            r.reject({'a': -4, 'b': 0}, 'ENCODE_RANGE', 'encode', None),
            r.reject({'a': 2**63-1, 'b': 1}, 'OVERFLOW', 'structure'), r.invalid({'a': True, 'b': 0})])
    save('REQUIREMENT.json', t)
    shared = (HERE.parent / 'r6_23/CONTRACT.txt').read_text().split('\nTRACK_A\n')[0]
    shared = shared.replace('Do not emit examples, schemas, Markdown or commentary. Return one JSON packet.', '')
    system = shared + '\nUse native tools only. Expressions use scalar literals, $input_or_prior_alias, or [add|le|eq,operand,operand]. dependencies lists all referenced input/local aliases exactly once. No solution is supplied. Finalize using define_result, then validate_candidate. Rejected calls leave state unchanged. Maximum3 definitions/4 inputs/8 steps; expression one binary layer. Target Int64. No chat packet or examples.'
    save('PROMPT.json', [dict(role='system', content=system), dict(role='user', content=t['requirement'])])
    save('TOOLS.json', tools.definitions(['value']))
    save('MODEL-CONFIG.json', dict(provider='ollama', model=r.MODEL, digest=r.DIGEST, weight_sha256=r.WEIGHT,
        options=r.OPTIONS, think=False, reasoning='think:false requested; provider attestation beyond returned fields unavailable',
        native_tools=True, format_override=None, remote_provider_used=False, other_models_attempted=False))
    files = ['common.py', 'baseline.py', 'BASELINE.json', 'transport.py', 'test_transport.py', 'experiment.py',
        'ENVELOPE-1.md', 'PROTOCOL.md', 'REQUIREMENT.json', 'PROMPT.json', 'TOOLS.json', 'MODEL-CONFIG.json', 'QUALIFICATION.json']
    save('FREEZE.json', dict(timestamp=now(), files={p: sha(HERE / p) for p in files}, model_exposure=False))
    print('Frozen one fresh requirement, seven observations, transport and model configuration')

def stable(x):
    if isinstance(x, bytes): return {'bytes_hex': x.hex()}
    if isinstance(x, dict): return {k: stable(v) for k, v in x.items() if k not in ('times', 'seconds', 'expansion_seconds', 'execution_seconds')}
    if isinstance(x, list): return [stable(v) for v in x]
    return x

def evaluate(packet):
    r = historical_runner()
    result = r.evaluate(json.dumps(packet), 'B', read('REQUIREMENT.json'))
    # Require the promised explicit stored-value dependency, in addition to frozen
    # typed validation and behavior; no host synthesis of this relationship.
    if result['typed_valid']:
        d = packet['definitions'][0]
        first, second = d['ops']
        result['stored_dependency_valid'] = second[3] == ['add', '$' + first[0], 3] and second[4] == [first[0]] and d['result'] == '$' + second[0]
        result['functional_success'] &= result['stored_dependency_valid']
    return result

def replay():
    assert (HERE / 'ARTIFACT.json').exists()
    packet = read('SYMBOLIC-PACKET.json')
    original = read('ACCEPTANCE.json')
    passes = []
    for i in range(3):
        result = evaluate(packet)
        same = stable(result) == stable(original)
        save(f'replay/pass-{i+1}.json', result)
        passes.append(dict(pass_number=i+1, identical=same, accepted=result['functional_success'],
            observation_sha256=__import__('hashlib').sha256(json.dumps(stable(result), sort_keys=True).encode()).hexdigest()))
        assert same and result['functional_success']
    save('REPLAY.json', dict(model_connection=False, model_calls=0, artifact_sha256=sha(HERE / 'ARTIFACT.json'),
        passes=passes, compared='entire functional envelopes, packages, expansions, identities, provenance and logical work; timing fields excluded'))
    print('Three offline replay passes identical and accepted')

def run():
    assert not (HERE / 'RUN-STATUS.json').exists(), 'one attempt only'
    assert all(sha(HERE / p) == h for p, h in read('FREEZE.json')['files'].items())
    assert all(sha(ROOT / p) == h for p, h in read('BASELINE.json')['protected_files'].items())
    r = historical_runner()
    # R6.24 imports the shared json module. Swap its decoder read-only in this
    # process so every raw chunk, not merely extracted arguments, rejects duplicates.
    old_loads = json.loads
    def strict(text, **kwargs):
        if kwargs: return old_loads(text, **kwargs)
        return strict_loads(text, allow_provider_numbers=True)
    json.loads = strict
    runner = r.Runner()
    session = tools.Session(['value'])
    messages = copy.deepcopy(read('PROMPT.json'))
    seen, transcript = set(), []
    inputs = outputs = repairs = 0
    reason = fatal = None
    construction_begin = None
    try:
        runner.start()
        warm = runner.call('control_warm', [dict(role='user', content='Reply with the word ready.')], cap=64, warm=True)
        assert warm['completion']
        echo = [dict(type='function', function=dict(name='echo', description='Return requested text inertly.', parameters=dict(type='object', properties={'text': {'type': 'string'}}, required=['text'], additionalProperties=False)))]
        control = runner.call('control_tools', [dict(role='user', content='Call echo with text local25.')], echo, cap=64)
        envelopes = normalize(control['message'].get('tool_calls'), 'ollama', r.MODEL, 0, {'echo'}, set())
        assert control['completion'] and len(envelopes) == 1 and envelopes[0]['semantic_arguments'] == {'text': 'local25'}
        save('CURRENT-ENVELOPE.json', dict(raw=control['message']['tool_calls'], normalized=envelopes, passed=True))
        construction_begin = time.perf_counter()
        deadline = construction_begin + 180
        retry_pending = False
        for turn in range(16):
            if outputs >= 4096 or inputs >= 60000 or time.perf_counter() >= deadline:
                reason = 'TASK_BUDGET'; break
            if retry_pending:
                if repairs >= 3:
                    reason = 'REPAIR_BUDGET'; break
                repairs += 1
                retry_pending = False
            row = runner.call(f'F1_{turn:02d}', messages, read('TOOLS.json'), cap=min(384, 4096-outputs), deadline=deadline)
            inputs += row['tokens']['prompt_eval_count'] or 0
            outputs += row['tokens']['eval_count'] or 0
            if not row['completion']:
                reason = 'RUNTIME_ABORT' if row['error'] else 'OUTPUT_LIMIT'; break
            calls = row['message'].get('tool_calls', [])
            if not calls:
                reason = 'NO_TOOL_CALL'; break
            messages.append(row['message'])
            try:
                envelopes = normalize(calls, 'ollama', r.MODEL, turn, session.schemas, seen)
            except TransportError as e:
                transcript.append(dict(model_call=row['id'], raw_calls=calls, transport_accepted=False, diagnostic=str(e)))
                reason = 'TRANSPORT_REJECTED'; break
            for envelope in envelopes:
                if session.calls >= 24:
                    reason = 'TOOL_BUDGET'; break
                result = session.dispatch(semantic_call(envelope))
                transcript.append(dict(model_call=row['id'], raw_call=calls[envelope['ordering']['position']], normalized=envelope,
                    transport_accepted=True, result=result))
                messages.append(feedback(envelope, result['response']))
                retry_pending |= not result['success']
                if session.completed:
                    acceptance = evaluate(session.packet)
                    save('ACCEPTANCE.json', acceptance)
                    save('SYMBOLIC-PACKET.json', session.packet)
                    save('ARTIFACT.json', session.completed['artifact'])
                    reason = 'CANDIDATE_COMPLETED'; break
            save('INTERACTION.json', dict(messages=messages, transcript=transcript, packet=session.packet, finalized=sorted(session.finalized)))
            if reason: break
        reason = reason or 'MODEL_CALL_BUDGET'
    except Exception as e:
        fatal = repr(e)
        save('HALT.json', dict(timestamp=now(), error=fatal, traceback=traceback.format_exc()))
    finally:
        json.loads = old_loads
        runner.stop()
        save('INTERACTION.json', dict(messages=messages, transcript=transcript, packet=session.packet, finalized=sorted(session.finalized)))
        save('RUN-STATUS.json', dict(timestamp=now(), fatal=fatal, termination=reason, actual_model_calls=len(runner.rows),
            task_model_calls=sum(x['id'].startswith('F1_') for x in runner.rows), tool_calls=session.calls,
            repairs=repairs, manual_repairs=0, construction_seconds=None if construction_begin is None else time.perf_counter()-construction_begin,
            whole_run_seconds=time.perf_counter()-runner.started, stopped=True))
        print('Stopped:', reason, 'fatal:', fatal, 'tools:', session.calls, 'repairs:', repairs)

if __name__ == '__main__':
    {'prepare': prepare, 'run': run, 'replay': replay}[sys.argv[1]]()
