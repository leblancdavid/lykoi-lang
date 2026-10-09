"""Posthoc publication verification. No inference, tokenizer or remote requests."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
from datetime import datetime, timezone

from baseline import sha
from run import controls, read, save, wire, Session

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]

def without_times(x):
    if isinstance(x, bytes):
        return {'bytes_hex': x.hex()}
    if isinstance(x, dict):
        return {k: without_times(v) for k, v in x.items() if k not in ('seconds', 'times')}
    if isinstance(x, list):
        return [without_times(v) for v in x]
    return x

def main():
    baseline = read('BASELINE.json')
    assert all(sha(ROOT / p) == h for p, h in baseline['protected_files'].items())
    freeze = read('FREEZE.json')
    assert all(sha(HERE / p) == h for p, h in freeze['files'].items())
    qualified = controls.run()
    assert without_times(qualified) == without_times(read('SCRIPTED-QUALIFICATION.json'))
    rows = read('INFERENCE.json')['rows']
    calls = []
    for row in rows:
        request = read('calls/' + row['id'] + '-request.json')
        assert wire(request['request']) == request['serialized']
        assert hashlib.sha256(request['serialized'].encode()).hexdigest() == request['request_sha256']
        assert request['request']['model'] == 'qwen3:8b' and request['request']['think'] is False
        events = [json.loads(s) for s in (HERE / 'calls' / (row['id'] + '-stream.jsonl')).read_text().splitlines()]
        chunks = [json.loads(e['raw']) for e in events]
        content = ''.join(c.get('message', {}).get('content', '') for c in chunks)
        tools = [t for c in chunks for t in c.get('message', {}).get('tool_calls', [])]
        assert content == row['message']['content']
        assert tools == row['message'].get('tool_calls', [])
        assert all(events[i]['elapsed_seconds'] <= events[i+1]['elapsed_seconds'] for i in range(len(events)-1))
        assert row['delivery']['intact']
        assert row == read('calls/' + row['id'] + '-result.json')
        calls.append(dict(id=row['id'], request_sha256=request['request_sha256'], stream_reassembly=True,
            native_delivery_intact=True))
    assert len(rows) == 2 and read('RUN-STATUS.json')['candidates'] == 0
    native = rows[1]['message']['tool_calls']
    assert len(native) == 1 and native[0]['function']['name'] == 'echo' and native[0]['function']['arguments'] == {'text': 'local24'}
    assert set(native[0]) == {'id', 'function'} and set(native[0]['function']) == {'index', 'name', 'arguments'}
    # Read-only defect control: a legal construction name/arguments with the actual
    # native transport envelope also rejects. No candidate repair/model inference.
    shape_control = json.loads(json.dumps(native[0]))
    shape_control['function']['name'] = 'declare_input'
    shape_control['function']['arguments'] = {'definition': 'MetadataControl', 'inputs': []}
    replay = Session(['value']).dispatch(shape_control)
    assert replay['response']['error']['code'] == 'TOOL_SYNTAX'
    missing = [{k: v for k, v in row['tokens'].items() if v is None} for row in rows]
    assert not any(missing)
    measurements = dict(
        provenance='terminal Ollama API counters; posthoc accounting; no inference here',
        actual_model_calls=2, task_model_calls=0, neutral_model_tool_selections=1,
        construction_tool_calls=0, neutral_semantic_name_arguments_correct=dict(numerator=1, denominator=1),
        task_tool_syntax_rate=None, task_argument_rate=None, task_semantic_append_rate=None,
        task_valid_constructions=0, task_functional_acceptances=0,
        task_rate_denominators=0, task_status='NOT_REACHED',
        input_tokens=sum(r['tokens']['prompt_eval_count'] for r in rows),
        cached_input_tokens=sum(r['tokens']['prompt_eval_cached_count'] for r in rows),
        output_tokens=sum(r['tokens']['eval_count'] for r in rows),
        inference_wall_seconds=sum(r['wall_seconds'] for r in rows),
        prompt_eval_seconds=sum(r['durations_ns']['prompt_eval_duration'] for r in rows) / 1e9,
        generation_seconds=sum(r['durations_ns']['eval_duration'] for r in rows) / 1e9,
        total_runtime_seconds=sum(r['durations_ns']['total_duration'] for r in rows) / 1e9,
        per_call=[dict(id=r['id'], tokens=r['tokens'], wall_seconds=r['wall_seconds'], durations_ns=r['durations_ns']) for r in rows],
        whole_run_seconds=read('RUN-STATUS.json')['total_seconds'],
        task_construction_seconds=None, task_validation_seconds=None, task_expansion_seconds=None, task_execution_seconds=None,
        scripted_tool_seconds=sum(t['result']['seconds'] for t in read('SCRIPTED-QUALIFICATION.json')['scripted_transcript']),
        model_repair_attempts=0, manual_repairs=0, runtime_aborts=0,
        missing_telemetry=['billing', 'energy', 'peak_resource_usage'],
        tokenizer_overhead='included in whole-run time; not separately metered',
        publication_overhead='not included in bounded run',
        cached_input_note='cached input is a subset of input, not added again')
    save('MEASUREMENTS.json', measurements)
    failure = dict(classification='R6_24_PROTOCOL_HALT', mechanism='HOST_NATIVE_TOOL_ENVELOPE_MISMATCH',
        halted_at='neutral tool interface control, before task exposure',
        request_sha256=calls[1]['request_sha256'], raw_tool_call=native[0],
        expected_by_frozen_harness={'function': {'name': 'echo', 'arguments': {'text': 'local24'}}},
        model_name_and_arguments_correct=True, native_extra_fields=['id', 'function.index'],
        runtime_completed=True, runtime_http=200, runtime_abort=False,
        model_authoring_verdict='NOT_REACHED', comparative_verdict='NOT_REACHED',
        posthoc_metadata_shape_rejection=dict(call=shape_control, response=replay,
            provenance='host synthetic replay of actual native envelope shape; not a participant candidate'),
        limitation='scripted controls exercised the stripped function envelope, not the native API envelope',
        prior_token_repeat_evidence_preserved=baseline['prior_abort_evidence'],
        host_repair_or_rerun=False)
    save('FAILURE-ANALYSIS.json', failure)
    save('FUNCTIONAL-RESULTS.json', dict(classification='R6_24_PROTOCOL_HALT',
        completed_model_candidates=0, executed_model_cases=0, authored_task_cases=26,
        rows=[dict(task=t['id'], track=tr, model_calls=0, tool_calls=0, candidate='NOT_REACHED',
            dag_validation='NOT_REACHED', expansion='NOT_REACHED', execution='NOT_REACHED', acceptance='NOT_REACHED',
            scheduled_cases=len(t['cases'])) for t in read('TASKS.json')['tasks'] for tr in ('T', 'A', 'B')],
        scripted_control_cases=4, scripted_success_not_model_success=True))
    save('MODEL-REPRESENTATIONS.json', dict(candidates=[], expanded_plans=[], incomplete_candidates=[],
        status='NOT_REACHED: no task prompt submitted'))
    save('INTERACTION-RESULTS.json', dict(neutral_native_control=rows[1]['message'],
        task_tool_transcripts=[], status='NOT_REACHED', no_tool_execution_after_halt=True))
    print(json.dumps(measurements, indent=2))
    # Identity manifest includes the report and additive guidance. Receipt is kept
    # outside the manifest to avoid a self-hash cycle; manifest hash in receipt.
    sources = [p for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts
        and p.name not in ('PUBLICATION-IDENTITIES.json', 'VERIFICATION.json')]
    sources += [HERE.parent / 'R6_24-REPORT.md']
    sources += [ROOT / 'docs' / n for n in ('project-overview-r6.24.md', 'research-log-r6.24.md', 'decisions-r6.24.md')]
    files = {}
    links = []
    for path in sorted(sources):
        if path.suffix == '.json':
            json.loads(path.read_text())
        if path.suffix in ('.md', '.py'):
            text = path.read_text()
            assert not any(line.rstrip() != line for line in text.splitlines()), str(path)
            if path.suffix == '.md':
                for match in re.finditer(r'\]\(([^)]+)\)', text):
                    link = match.group(1).split('#')[0]
                    if link and not link.startswith(('https:', 'http:')):
                        destination = (path.parent / link).resolve()
                        links.append((path, destination))
                        if destination not in (HERE / 'VERIFICATION.json', HERE / 'PUBLICATION-IDENTITIES.json'):
                            assert destination.exists(), (path, link)
        files[path.relative_to(ROOT).as_posix()] = dict(sha256=sha(path), bytes=path.stat().st_size)
    diff = subprocess.run(['git', 'diff', '--check'], capture_output=True, text=True)
    assert diff.returncode == 0, diff.stdout + diff.stderr
    save('PUBLICATION-IDENTITIES.json', dict(timestamp=datetime.now(timezone.utc).isoformat(), files=files))
    save('VERIFICATION.json', dict(passed=True, timestamp=datetime.now(timezone.utc).isoformat(),
        protected_count=len(baseline['protected_files']), protected_mismatches=[], kernel=26,
        frozen_files=len(freeze['files']), freeze_verified=True, scripted_requalification=True,
        stream_request_delivery_checks=calls, raw_native_metadata_defect_verified=True,
        new_json_parses=True, new_text_whitespace=True, relative_links=True,
        git_diff_check=dict(returncode=diff.returncode, stdout=diff.stdout, stderr=diff.stderr),
        publication_manifest_sha256=sha(HERE / 'PUBLICATION-IDENTITIES.json'),
        publication_files=len(files), inference_calls_during_publication=0,
        production_tests='NOT_RUN: no production edits', stopped=True))
    assert all(destination.exists() for _, destination in links)
    assert all(sha(ROOT / p) == entry['sha256'] for p, entry in read('PUBLICATION-IDENTITIES.json')['files'].items())
    assert sha(HERE / 'PUBLICATION-IDENTITIES.json') == read('VERIFICATION.json')['publication_manifest_sha256']
    print('Publication verified:', len(files), 'published files;', len(baseline['protected_files']), 'protected identities')

if __name__ == '__main__':
    main()
