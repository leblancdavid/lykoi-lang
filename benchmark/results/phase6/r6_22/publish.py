"""Posthoc accounting, privacy filtering and integrity. No inference endpoints."""
from collections import Counter, defaultdict
import json
from pathlib import Path
import re
import statistics

import run as r


def sanitize():
    assert not (r.HERE / 'PRIVACY.json').exists(), 'do not refilter evidence'
    path = r.HERE / 'SERVER.log'
    original = path.read_bytes()
    pattern = r'(?<![A-Z_])PATH="[^"\r\n]*"'
    text = original.decode()
    filtered, count = re.subn(pattern, 'PATH="[REDACTED_UNRELATED_SEARCH_PATH]"', text)
    path.write_bytes(filtered.encode())
    rows = r.read('RESULTS.json')['rows']
    changed = []
    for row in rows:
        excerpt, n = re.subn(pattern, 'PATH="[REDACTED_UNRELATED_SEARCH_PATH]"', row['log_excerpt'])
        if n:
            p = r.HERE / 'calls' / (row['id'] + '-result.json')
            changed.append(dict(path=p.name, original_sha256=r.sha(p), substitutions=n))
            row['log_excerpt'] = excerpt
            r.save('calls/' + p.name, row)
    r.save('RESULTS.json', dict(rows=rows))
    r.save('PRIVACY.json', dict(timestamp=r.now(), rule=pattern, substitutions=count,
        original_log_sha256=r.hashlib.sha256(original).hexdigest(), published_log_sha256=r.sha(path),
        changed_results=changed, scope='only new runtime PATH fields; historical artifacts untouched',
        byte_spans='recorded log_byte_span refers to original capture; publication filtering changes offsets, line numbers unchanged',
        raw_generation='all request bytes and raw stream events untouched'))


def analyze():
    rows = r.read('RESULTS.json')['rows']
    manifest = r.read('REQUESTS.json')
    tasks = {t['id']: t for t in manifest['tasks']}
    groups = defaultdict(list)
    failures = []
    for row in rows:
        p = r.HERE / 'calls' / (row['id'] + '-request.json')
        req = json.loads(p.read_text())
        assert r.wire(req['request']) == req['serialized_request']
        assert r.hashlib.sha256(req['serialized_request'].encode()).hexdigest() == req['sha256']
        events = [json.loads(s) for s in (r.HERE / 'calls' / (row['id'] + '-stream.jsonl')).read_text().splitlines()]
        chunks = [json.loads(e['raw']) for e in events]
        assert len(chunks) == row['chunks']
        assert ''.join(c.get('response', '') for c in chunks) == row['output']
        assert all(a['elapsed_seconds'] <= b['elapsed_seconds'] for a, b in zip(events, events[1:]))
        assert r.evaluate(row['output'], tasks[row['task']]) == row['validation']
        repetition = {}
        if row['task'] == 'array':
            repetition = dict(requested_entries=128, visible_zero_lexemes=len(re.findall(r'(?<!\d)0(?!\d)', row['output'])),
                              note='lexeme count in incomplete JSON, not decoded array length')
        if row['task'] == 'identifiers':
            try:
                values = r.strict(row['output'])['symbols']
                repetition = dict(requested_entries=64, decoded_entries=len(values),
                    sym_alpha_entries=values.count('sym_alpha'), different_entries=[v for v in values if v != 'sym_alpha'])
            except (ValueError, KeyError):
                repetition = dict(requested_entries=64, incomplete_json=True,
                                  visible_sym_alpha=row['output'].count('sym_alpha'))
        row['posthoc_repetition'] = repetition
        if row['id'] != 'warmup':
            groups[(row['task'], row['config'])].append(row)
            if not row['completion'] or not row['validation']['schema_valid']:
                failures.append(dict(id=row['id'], category='Output-budget exhaustion' if row['final'].get('done_reason') == 'length'
                    else 'Model repetition observed; decoder contribution undetermined', evidence=repetition,
                    runtime_error=row['error'], tokens=row['usage']['eval_count']))
    matrix = []
    for (task, config), xs in groups.items():
        matrix.append(dict(task=task, config=config, attempts=len(xs), completed=sum(x['completion'] for x in xs),
            json_valid=sum(x['validation']['json_valid'] for x in xs), schema_valid=sum(x['validation']['schema_valid'] for x in xs),
            expected_equal=sum(x['validation']['expected_equal'] for x in xs),
            guard_aborts=sum(x['repetition']['guard_abort'] for x in xs),
            runtime_failures=sum(x['error'] is not None for x in xs),
            known_input_tokens=sum(x['usage']['prompt_eval_count'] or 0 for x in xs),
            cached_input_tokens=sum(x['usage']['prompt_eval_cached_count'] or 0 for x in xs),
            known_output_tokens=sum(x['usage']['eval_count'] or 0 for x in xs),
            missing_usage=sum(x['usage']['eval_count'] is None for x in xs),
            latency_mean_seconds=statistics.mean(x['wall_seconds'] for x in xs),
            latency_range_seconds=[min(x['wall_seconds'] for x in xs), max(x['wall_seconds'] for x in xs)],
            repetitions=[x['posthoc_repetition'] for x in xs],
            output_sha256=[r.hashlib.sha256(x['output'].encode()).hexdigest() for x in xs]))
    scored = [x for x in rows if x['id'] != 'warmup']
    summary = dict(attempts=len(scored), completion=sum(x['completion'] for x in scored),
        json_valid=sum(x['validation']['json_valid'] for x in scored),
        schema_valid=sum(x['validation']['schema_valid'] for x in scored),
        expected_equal=sum(x['validation']['expected_equal'] for x in scored),
        output_budget_exhaustions=sum(x['final'].get('done_reason') == 'length' for x in scored),
        generation_runtime_errors=sum(x['error'] is not None for x in scored),
        repeat_guard_aborts=sum(x['repetition']['guard_abort'] for x in scored),
        intact_delivery=sum(x['delivery']['intact'] for x in scored),
        inference_known_input_tokens=sum(x['usage']['prompt_eval_count'] or 0 for x in rows),
        inference_cached_input_tokens=sum(x['usage']['prompt_eval_cached_count'] or 0 for x in rows),
        inference_known_output_tokens=sum(x['usage']['eval_count'] or 0 for x in rows),
        inference_wall_seconds=sum(x['wall_seconds'] for x in rows),
        inference_latency_range_seconds=[min(x['wall_seconds'] for x in scored), max(x['wall_seconds'] for x in scored)],
        missing_final_usage=0, unexecuted_schedule=manifest['schedule'][len(scored):],
        attempted_preflight_but_not_generated=manifest['schedule'][len(scored)],
        repetitions='identical seed, sequential cache; not independent trials',
        classification='R6_22_PROTOCOL_HALT')
    r.save('MEASUREMENTS.json', dict(summary=summary, matrix=matrix, per_call_repetition=[dict(id=x['id'], **x['posthoc_repetition']) for x in rows]))
    r.save('FAILURE-CLASSIFICATIONS.json', dict(failures=failures,
        terminal=dict(category='Undetermined within runtime categories; established harness stale-port defect',
            stage='preflight tokenizer before scheduled35', inference_sent=False,
            explanation='context reload replaced backend52283 with62254; frozen runner retained52283',
            original_error=r.read('HALT.json')['error']),
        historical=dict(category='Undetermined underlying generation; repeat-guard abort established',
            body='{"error":"prediction aborted, token repeat limit reached"}',
            generated_output='unavailable in R6.21; never reconstructed')))
    lines = (r.HERE / 'SERVER.log').read_text().splitlines()
    observations = [dict(line=i, text=s) for i, s in enumerate(lines, 1) if any(term in s for term in
        ('starting llama-server', 'msg=reloading', 'llama-server stopped', 'offloaded 37/37',
         'successfully fit params', 'no changes needed', 'n_ctx_seq ', 'repeat_last_n =', 'sampling order:', 'token repeat limit',
         'out of memory', 'truncating input prompt'))]
    r.save('RUNTIME-ANALYSIS.json', dict(observations=observations, log_lines=len(lines),
        repeat_guard_error_lines=[i for i, s in enumerate(lines, 1) if 'token repeat limit' in s],
        oom_error_lines=[i for i, s in enumerate(lines, 1) if 'out of memory' in s.lower()],
        context_reload='normal requested reload, not evidenced backend crash',
        resource_assessment='model fit/offload and point snapshots; no resource-failure evidence, no peak claim',
        privacy='PATH fields filtered; relevant settings and log line identities retained'))
    print(json.dumps(summary, indent=2))
    for m in matrix:
        print(m['task'], m['config'], m['attempts'], m['completed'], m['schema_valid'],
              m['known_output_tokens'], round(m['latency_mean_seconds'], 3), m['repetitions'][:1])


def verify():
    pending_outputs = {r.HERE / 'PUBLICATION-IDENTITIES.json', r.HERE / 'VERIFICATION.json'}
    pins = r.read('BASELINE.json')['protected_files']
    assert all(r.sha(r.ROOT / p) == h for p, h in pins.items())
    assert all(r.sha(r.HERE / p) == h for p, h in r.read('FREEZE.json')['files'].items())
    files = [p for p in r.HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name not in ('PUBLICATION-IDENTITIES.json', 'VERIFICATION.json')]
    files += [r.HERE.parent / 'R6_22-REPORT.md']
    files += [r.ROOT / 'docs' / name for name in ('project-overview-r6.22.md', 'research-log-r6.22.md', 'decisions-r6.22.md')]
    for p in files:
        if p.suffix == '.json':
            json.loads(p.read_text())
        if p.suffix in ('.md', '.py'):
            assert not any(line.rstrip() != line for line in p.read_text().splitlines()), p
        if p.suffix == '.md':
            for target in re.findall(r'\]\(([^)]+)\)', p.read_text()):
                if not target.startswith(('http', '#')):
                    destination = p.parent / target.split('#')[0]
                    assert destination.exists() or destination in pending_outputs, (p, target)
    diff = r.cmd(['git', 'diff', '--check'])
    assert diff['returncode'] == 0, diff
    r.save('PUBLICATION-IDENTITIES.json', dict(round='R6.22', classification='R6_22_PROTOCOL_HALT',
        files={p.relative_to(r.ROOT).as_posix(): dict(sha256=r.sha(p), bytes=p.stat().st_size) for p in files}))
    r.save('VERIFICATION.json', dict(timestamp=r.now(), protected_count=len(pins), protected_mismatches=[],
        freeze_matches=True, json_valid=True, stream_reassembly=True, request_hashes=True,
        posthoc_validation_recomputed=True, links=True, new_source_whitespace=True, git_diff_check=diff,
        publication_manifest_sha256=r.sha(r.HERE / 'PUBLICATION-IDENTITIES.json'),
        kernel=26, production_vm_wrapper='byte-identical protected identities', stopped=True))
    pub = r.read('PUBLICATION-IDENTITIES.json')
    assert all(r.sha(r.ROOT / p) == v['sha256'] for p, v in pub['files'].items())
    assert all(p.exists() for p in pending_outputs)
    print('Publication and protected identities verified:', len(pins), len(files))


if __name__ == '__main__':
    import sys
    if sys.argv[1] == 'analyze':
        sanitize()
        analyze()
    elif sys.argv[1] == 'verify':
        verify()
