"""Posthoc publication only; no local or remote model/tokenizer requests."""
from collections import Counter
import copy
import json
from pathlib import Path
import re
import statistics
from types import SimpleNamespace
from unittest.mock import patch

import run as r


def normalized(value):
    return json.loads(json.dumps(value, default=lambda v: {'bytes_hex': v.hex()} if isinstance(v, bytes) else str(v)))


def privacy():
    assert not (r.HERE / 'PRIVACY.json').exists()
    p = r.HERE / 'SERVER.log'
    original = p.read_bytes()
    pattern = r'(?<![A-Z_])PATH="[^"\r\n]*"'
    text, n = re.subn(pattern, 'PATH="[REDACTED_UNRELATED_SEARCH_PATH]"', original.decode())
    p.write_bytes(text.encode())
    changed = []
    records = r.read('INFERENCE.json')
    for row in records['rows']:
        filtered, count = re.subn(pattern, 'PATH="[REDACTED_UNRELATED_SEARCH_PATH]"', row['log_excerpt'])
        if count:
            destination = r.HERE / 'calls' / (row['id'] + '-result.json')
            changed.append(dict(path=destination.name, substitutions=count, original_sha256=r.sha(destination)))
            row['log_excerpt'] = filtered
            r.save('calls/' + destination.name, row)
    r.save('INFERENCE.json', records)
    r.save('PRIVACY.json', dict(timestamp=r.now(), original_log_sha256=r.hashlib.sha256(original).hexdigest(),
        published_log_sha256=r.sha(p), substitutions=n, changed_results=changed,
        rule=pattern, raw_streams_and_requests='unmodified', historical_files='unmodified',
        byte_spans='original capture spans; filtered log retains lines but changes byte offsets'))


def endpoint_controls():
    reference = r.read('ENDPOINTS.json')['rows'][-1]
    tests = []
    def test(name, log, identity, loaded, returncode=0):
        process = SimpleNamespace(returncode=returncode, stdout=json.dumps(identity), stderr='synthetic unavailable listener' if returncode else '')
        with patch.object(r.endpoint.subprocess, 'run', return_value=process), patch.object(r.endpoint.urllib.request, 'build_opener') as http:
            try:
                r.endpoint.discover(log, reference['process']['ParentProcessId'], loaded, r.DIGEST, r.WEIGHT)
            except RuntimeError as e:
                tests.append(dict(id=name, rejected=True, error=str(e), backend_http_calls=http.call_count))
                assert http.call_count == 0
            else:
                raise AssertionError(name + ' did not fail closed')
    log = SimpleNamespace(read_text=lambda **kwargs: reference['startup'])
    test('missing_start_record', SimpleNamespace(read_text=lambda **kwargs: ''), reference['process'], reference['loaded'])
    test('dead_stale_listener', log, reference['process'], reference['loaded'], 1)
    wrong_parent = dict(reference['process'], ParentProcessId=0)
    test('wrong_owner_parent', log, wrong_parent, reference['loaded'])
    wrong_weight = dict(reference['process'], CommandLine=reference['process']['CommandLine'].replace(r.WEIGHT, '0'*64))
    test('wrong_process_model', log, wrong_weight, reference['loaded'])
    wrong_digest = copy.deepcopy(reference['loaded'])
    wrong_digest['models'][0]['digest'] = '0'*64
    test('wrong_loaded_digest', log, reference['process'], wrong_digest)
    wrong_context = copy.deepcopy(reference['loaded'])
    wrong_context['models'][0]['context_length'] = 1
    test('wrong_loaded_context', log, reference['process'], wrong_context)
    r.save('ENDPOINT-NEGATIVE-CONTROLS.json', dict(passed=True, rows=tests,
        provenance='posthoc synthetic fail-closed checks of frozen endpoint.py; no network or model calls',
        live_reload_qualification='separately retained ENDPOINT-VERIFICATION.json'))


def repetition(row):
    events = [json.loads(s) for s in (r.HERE / 'calls' / (row['id'] + '-stream.jsonl')).read_text().splitlines()]
    chunks = [json.loads(e['raw']) for e in events]
    values = [c.get('response', '') for c in chunks if c.get('response')]
    previous = None
    longest = length = 0
    repeated = None
    for value in values:
        length = length + 1 if value == previous else 1
        if length > longest:
            longest, repeated = length, value
        previous = value
    return dict(id=row['id'], streamed_events=len(events), response_chunks=len(values),
        max_identical_adjacent_chunks=longest, repeated_chunk=repr(repeated),
        output_newlines=row['output'].count('\n'),
        guard_abort='token repeat limit reached' in str(row['error']),
        note='receipt chunks and characters are not token counts')


def analyze():
    rows = r.read('INFERENCE.json')['rows']
    candidates = r.read('ACCEPTANCE.json')['rows'] if (r.HERE / 'ACCEPTANCE.json').exists() else []
    taskset = r.read('TASKS.json')
    tasks = {t['id']: t for t in taskset['tasks']}
    lookup = {x['id']: x for x in rows}
    metrics = {}
    for track in ('A', 'B'):
        calls = [x for x in rows if x['id'].endswith('_' + track)]
        cs = [x for x in candidates if x['track'] == track]
        metrics[track] = dict(planned=6, calls=len(calls), returned_candidates=len(cs),
            json_valid=sum(x['result']['json_valid'] for x in cs), strict_valid=sum(x['result']['strict_valid'] for x in cs),
            schema_valid=sum(x['result']['schema_valid'] for x in cs), typed_valid=sum(x['result']['typed_valid'] for x in cs),
            expanded_valid=sum(x['result']['expanded_valid'] is True for x in cs),
            functional_objectives=sum(x['result']['functional_success'] for x in cs),
            runtime_failures=sum(x['error'] is not None for x in calls),
            known_input_tokens=sum(x['tokens']['prompt_eval_count'] or 0 for x in calls),
            cached_input_tokens=sum(x['tokens']['prompt_eval_cached_count'] or 0 for x in calls),
            known_output_tokens=sum(x['tokens']['eval_count'] or 0 for x in calls),
            missing_usage_calls=[x['id'] for x in calls if x['tokens']['eval_count'] is None],
            inference_wall_seconds=sum(x['wall_seconds'] for x in calls),
            known_runtime_ns={key: sum(x['durations_ns'][key] or 0 for x in calls) for key in
                ('total_duration', 'prompt_eval_duration', 'eval_duration', 'load_duration')},
            deterministic_construction_seconds=sum(x['result']['times']['construction_seconds'] for x in cs),
            schema_seconds=sum(x['result']['times']['schema_seconds'] for x in cs),
            serialization_seconds=sum(x['result']['times']['serialization_seconds'] for x in cs),
            wrapper_validation_seconds=sum(x['result']['times']['validation_seconds'] for x in cs),
            expansion_seconds=sum(x['result']['expansion_seconds'] for x in cs),
            execution_seconds=sum(x['result']['execution_seconds'] for x in cs),
            validation_pipeline_wall_seconds=sum(x['validation_and_execution_wall'] for x in cs),
            acceptance_cases_executed=sum(len(x['result']['cases']) for x in cs),
            repairs=0, first_attempt_success=sum(x['result']['functional_success'] for x in cs))
    pairs = []
    for tid in tasks:
        pair = {tr: lookup.get(tid + '_' + tr) for tr in ('A', 'B')}
        done = all(pair[tr] and pair[tr]['completion'] for tr in ('A', 'B'))
        row = dict(id=tid, paired_completion=bool(done), tracks={tr: 'COMPLETED' if pair[tr] and pair[tr]['completion'] else
            'RUNTIME_ABORT' if pair[tr] else 'NOT_REACHED' for tr in ('A', 'B')})
        if done:
            row.update(input_delta_B_minus_A=pair['B']['tokens']['prompt_eval_count']-pair['A']['tokens']['prompt_eval_count'],
                output_delta_B_minus_A=pair['B']['tokens']['eval_count']-pair['A']['tokens']['eval_count'],
                wall_delta_B_minus_A=pair['B']['wall_seconds']-pair['A']['wall_seconds'])
        pairs.append(row)
    completed_pair_ids = [x['id'] for x in pairs if x['paired_completion']]
    matched = {}
    for tr in ('A', 'B'):
        matched_rows = [lookup[tid + '_' + tr] for tid in completed_pair_ids]
        matched[tr] = dict(input_tokens=sum(x['tokens']['prompt_eval_count'] for x in matched_rows),
            output_tokens=sum(x['tokens']['eval_count'] for x in matched_rows),
            wall_seconds=sum(x['wall_seconds'] for x in matched_rows),
            prompt_eval_seconds=sum(x['durations_ns']['prompt_eval_duration'] for x in matched_rows)/1e9,
            generation_seconds=sum(x['durations_ns']['eval_duration'] for x in matched_rows)/1e9)
    accounting = dict(classification='R6_23_RUNTIME_RELIABILITY_GAP', by_track=metrics, pairs=pairs, matched=matched,
        inference_calls=len(rows), known_total_input=sum(x['tokens']['prompt_eval_count'] or 0 for x in rows),
        known_total_output=sum(x['tokens']['eval_count'] or 0 for x in rows),
        known_total_cached=sum(x['tokens']['prompt_eval_cached_count'] or 0 for x in rows),
        missing_usage=[x['id'] for x in rows if x['tokens']['eval_count'] is None],
        inference_wall_seconds=sum(x['wall_seconds'] for x in rows),
        endpoint_verification_seconds=sum(x['verification_seconds'] for x in r.read('ENDPOINTS.json')['rows']),
        tokenization_seconds=sum((x.get(phase) or {}).get('tokenization_seconds', 0) for x in rows for phase in ('preflight', 'postflight')),
        returned_candidate_count=len(candidates), expanded_participant_plans=0, logical_participant_vm_work='NOT_REACHED',
        remaining_schedule=taskset['schedule'][len([x for x in rows if x['id'].startswith('T')]):])
    r.save('MEASUREMENTS.json', accounting)
    r.save('REPETITION.json', dict(rows=[repetition(x) for x in rows]))
    failed = lookup['T4_A']
    excerpt = failed['log_excerpt']
    r.save('FAILURE-ANALYSIS.json', dict(id='T4_A', classification='repeat-guard runtime abort; underlying decoder/model cause undetermined',
        http_status=failed['http_status'], stream_error=failed['final_error_body'], request_sha256=r.read('calls/T4_A-request.json')['request_sha256'],
        repetition=repetition(failed), preflight_count=failed['preflight']['count'],
        logged_input=[int(n) for n in re.findall(r'task.n_tokens = (\d+)', excerpt)],
        slots=[int(n) for n in re.findall(r'n_ctx_slot = (\d+)', excerpt)],
        truncated='truncating input prompt' in excerpt,
        final_usage='unavailable; chunks/newline counts not converted to tokens',
        log_excerpt=excerpt, same_error_as_r6_21=True,
        transport_difference='R6.21 nonstreaming HTTP500; R6.23 stream established HTTP200 then NDJSON error',
        memory_cause='no supporting OOM evidence', inference_after_abort=0))
    r.save('MODEL-REPRESENTATIONS.json', dict(participant_plans=[], status='NOT_REACHED',
        candidates=[dict(id=x['id'], track=x['track'], status='SCHEMA_REJECTION', diagnostic=x['result']['diagnostic'],
                         functional_execution='NOT_REACHED') for x in candidates],
        aborted_candidate=dict(id='T4', track='A', status='RUNTIME_ABORT_NOT_EVALUATED'),
        host_controls='HOST-EXPANSIONS.json is explicitly not model-authored'))
    host_construction = r.a.construct(json.dumps(r.controls.fixture()), 'B')
    artifact = host_construction['artifact']
    host = []
    for args in [dict(z=0, permit=True), dict(z=37, permit=True), dict(z=0, permit=False)]:
        package = r.a.package(artifact, args)
        begin = r.time.perf_counter()
        expanded = r.a.c.expand(package)
        expansion_seconds = r.time.perf_counter() - begin
        begin = r.time.perf_counter()
        observation = r.a.c.vm.execute(expanded['plan'], b'')
        execution_seconds = r.time.perf_counter() - begin
        host.append(dict(args=args, package=package, expanded=expanded,
            observation=observation, expansion_seconds=expansion_seconds, execution_seconds=execution_seconds,
            package_bytes=len(r.a.c.canonical(package)), plan_bytes=len(r.a.c.canonical(expanded['plan']))))
    r.save('HOST-EXPANSIONS.json', dict(provenance='posthoc expansion of frozen mechanical host-control fixture; no participant candidate',
        construct_times=host_construction['times'], rows=host))
    candidate_lookup = {(x['id'], x['track']): x for x in candidates}
    stages = []
    for tid, tr in taskset['schedule']:
        candidate = candidate_lookup.get((tid, tr))
        call = lookup.get(tid + '_' + tr)
        stages.append(dict(task=tid, track=tr,
            inference='COMPLETE' if call and call['completion'] else 'RUNTIME_ABORT' if call else 'NOT_REACHED',
            schema='REJECT' if candidate else 'NOT_REACHED',
            construction='NOT_REACHED', type_dependency_validation='NOT_REACHED', expansion='NOT_REACHED',
            functional_observations='NOT_REACHED', cases_executed=0,
            required_cases=len(tasks[tid]['cases']), repairs=0))
    r.save('FUNCTIONAL-RESULTS.json', dict(rows=stages, accepted_objectives=0, executed_participant_cases=0,
        interpretation='schema rejection blocks later stages; zero passing objectives does not mean execution failed on cases'))
    # Re-run deterministic controls only; no model or tokenizer usage.
    check = r.controls.run()
    assert normalized(check) == r.read('HOST-CONTROLS.json')
    endpoint_controls()
    print(json.dumps(accounting, indent=2))
    print('Controls', check['total_controls'], 'differential observations', len(check['differential_observations']))
    print('Abort repetition', repetition(failed))


def verify():
    pins = r.read('BASELINE.json')['protected_files']
    assert all(r.sha(r.ROOT / p) == h for p, h in pins.items())
    assert all(r.sha(r.HERE / p) == h for p, h in r.read('FREEZE.json')['files'].items())
    tasks = {t['id']: t for t in r.read('TASKS.json')['tasks']}
    rows = r.read('INFERENCE.json')['rows']
    for row in rows:
        req = r.read('calls/' + row['id'] + '-request.json')
        assert r.wire(req['request']) == req['serialized']
        assert r.hashlib.sha256(req['serialized'].encode()).hexdigest() == req['request_sha256']
        events = [json.loads(s) for s in (r.HERE / 'calls' / (row['id'] + '-stream.jsonl')).read_text().splitlines()]
        chunks = [json.loads(e['raw']) for e in events]
        assert len(chunks) == row['chunks']
        assert ''.join(x.get('response', '') for x in chunks) == row['output']
        assert all(left['elapsed_seconds'] <= right['elapsed_seconds'] for left, right in zip(events, events[1:]))
        if row['completion']:
            assert row['delivery']['intact']
        if row['id'].startswith('T') and row['completion']:
            tid, tr = row['id'].split('_')
            check = r.evaluate(row['output'], tr, tasks[tid])
            original = r.read('candidates/' + row['id'] + '.json')['result']
            assert all(check[k] == original[k] for k in ('json_valid', 'strict_valid', 'schema_valid', 'typed_valid', 'diagnostic', 'functional_success', 'expanded_valid'))
    expected = r.read('ENDPOINT-VERIFICATION.json')
    assert expected['passed'] and expected['three_distinct_ports']
    assert normalized(r.controls.run()) == r.read('HOST-CONTROLS.json')
    files = [p for p in r.HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name not in ('PUBLICATION-IDENTITIES.json', 'VERIFICATION.json')]
    files += [r.HERE.parent / 'R6_23-REPORT.md']
    files += [r.ROOT / 'docs' / name for name in ('project-overview-r6.23.md', 'research-log-r6.23.md', 'decisions-r6.23.md')]
    pending = {r.HERE / 'PUBLICATION-IDENTITIES.json', r.HERE / 'VERIFICATION.json'}
    for p in files:
        if p.suffix == '.json':
            json.loads(p.read_text())
        if p.suffix in ('.md', '.py', '.txt'):
            assert all(line.rstrip() == line for line in p.read_text().splitlines()), p
        if p.suffix == '.md':
            for target in re.findall(r'\]\(([^)]+)\)', p.read_text()):
                if not target.startswith(('http', '#')):
                    destination = (p.parent / target.split('#')[0]).resolve()
                    assert destination.exists() or destination in pending, (p, target)
    diff = r.cmd(['git', 'diff', '--check'])
    assert diff['returncode'] == 0
    r.save('PUBLICATION-IDENTITIES.json', dict(round='R6.23', classification='R6_23_RUNTIME_RELIABILITY_GAP',
        files={p.relative_to(r.ROOT).as_posix(): dict(sha256=r.sha(p), bytes=p.stat().st_size) for p in files}))
    r.save('VERIFICATION.json', dict(timestamp=r.now(), protected_count=len(pins), protected_mismatches=[],
        frozen_hashes=True, publication_sha256=r.sha(r.HERE / 'PUBLICATION-IDENTITIES.json'), kernel=26,
        stream_reassembly=True, request_hashes=True, deterministic_controls_recomputed=True,
        candidate_rejections_recomputed=True, new_text_whitespace=True, json_valid=True, links=True,
        endpoint_reload_qualification=True, endpoint_fail_closed_controls=6, git_diff_check=diff,
        no_further_inference=True, stopped=True))
    assert all(p.exists() for p in pending)
    assert all(r.sha(r.ROOT / p) == v['sha256'] for p, v in r.read('PUBLICATION-IDENTITIES.json')['files'].items())
    print('Publication verified:', len(pins), 'protected identities;', len(files), 'publication files')


if __name__ == '__main__':
    import sys
    if sys.argv[1] == 'analyze':
        if not (r.HERE / 'PRIVACY.json').exists():
            privacy()
        analyze()
    elif sys.argv[1] == 'account':
        analyze()
    elif sys.argv[1] == 'verify':
        verify()
