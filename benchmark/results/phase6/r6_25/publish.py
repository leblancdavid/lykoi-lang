"""Evidence accounting and publication integrity; no provider/model requests."""
import json
import re
import subprocess
import sys
import unittest
from common import HERE, ROOT, read, save, sha, tools, now
from experiment import stable
from transport import normalize, semantic_call, strict_loads

def collect():
    rows = read('INFERENCE.json')['rows']
    task = [r for r in rows if r['id'].startswith('F1_')]
    transcript = read('INTERACTION.json')['transcript']
    status = read('RUN-STATUS.json')
    successful = (HERE / 'ACCEPTANCE.json').exists() and read('ACCEPTANCE.json')['functional_success']
    replayed = (HERE / 'REPLAY.json').exists() and all(p['identical'] for p in read('REPLAY.json')['passes'])
    classification = ('R6_25_PROTOCOL_HALT' if status['fatal'] else
        'R6_25_TRANSPORT_COMPATIBILITY_GAP' if status['termination'] == 'TRANSPORT_REJECTED' else
        'R6_25_END_TO_END_CONSTRUCTION_SUPPORTED' if successful and replayed else
        'R6_25_TRANSPORT_REPAIRED_CONSTRUCTION_PARTIAL' if (HERE / 'ARTIFACT.json').exists() else
        'R6_25_MODEL_AUTHORING_GAP')
    def totals(selected):
        return {k: sum(r['tokens'][k] for r in selected) if all(r['tokens'][k] is not None for r in selected) else None
            for k in ('prompt_eval_count', 'prompt_eval_cached_count', 'eval_count')}
    live_calls = sum(len(r['message'].get('tool_calls', [])) for r in task)
    dispatched = [t for t in transcript if t.get('transport_accepted')]
    save('MEASUREMENTS.json', dict(classification=classification,
        provenance='terminal Ollama counters, measured client/tool durations; publication issues no inference',
        actual_model_calls=len(rows), task_model_calls=len(task), neutral_model_calls=len(rows)-len(task),
        task_tool_calls=live_calls, neutral_tool_calls=1,
        transport_acceptance=dict(numerator=len(dispatched), denominator=live_calls),
        authorized_tool_name_validity=dict(numerator=sum(t['result']['syntax_valid'] for t in dispatched), denominator=len(dispatched)),
        semantic_argument_schema_validity=dict(numerator=sum(t['result']['arguments_valid'] for t in dispatched), denominator=len(dispatched)),
        semantic_construction_success=dict(numerator=sum(t['result']['success'] for t in dispatched), denominator=len(dispatched)),
        repairs=status['repairs'], manual_repairs=0, tokens_all=totals(rows), tokens_task=totals(task),
        inference_seconds_all=sum(r['wall_seconds'] for r in rows), inference_seconds_task=sum(r['wall_seconds'] for r in task),
        construction_seconds=status['construction_seconds'], whole_run_seconds=status['whole_run_seconds'],
        tool_dispatch_seconds=sum(t['result']['seconds'] for t in dispatched),
        candidate_validation_seconds=None, expansion_seconds=None, execution_seconds=None,
        timing_note='tool dispatch includes argument/partial validation; isolated validation not metered. Whole construction includes final server cleanup. Executable stages NOT_REACHED.',
        runtime_failures=sum(bool(r['error']) for r in rows), expected_runtime_rejections='NOT_REACHED',
        completed_artifacts=int((HERE / 'ARTIFACT.json').exists()), functional_acceptance='PASS' if successful else 'NOT_REACHED',
        frozen_cases=7, executed_cases=7 if (HERE / 'ACCEPTANCE.json').exists() else 0,
        replay='PASS' if replayed else 'NOT_REACHED',
        per_call=[dict(id=r['id'], tokens=r['tokens'], seconds=r['wall_seconds'], durations_ns=r['durations_ns']) for r in rows],
        unavailable=['billing', 'energy', 'peak resource usage', 'isolated semantic validation time', 'provider reasoning attestation'],
        cached_input_note='cached tokens are a subset of prompt tokens, not added again'))
    if not (HERE / 'ARTIFACT.json').exists():
        save('FUNCTIONAL-RESULTS.json', dict(classification=classification, symbolic_validation='NOT_REACHED',
            expansion='NOT_REACHED', VM_execution='NOT_REACHED', acceptance='NOT_REACHED', scheduled_cases=7, executed_cases=0,
            reason='No operation appended; definition unfinalized; no completed artifact'))
        save('REPLAY-STATUS.json', dict(status='NOT_REACHED', model_calls=0, completed_artifact=False,
            reason='Successful executable construction prerequisite not achieved; no manual repair or replay attempted'))
        save('MODEL-REPRESENTATIONS.json', dict(completed_artifacts=[], partial_packet=read('INTERACTION.json')['packet'],
            finalized=read('INTERACTION.json')['finalized'], provenance='exact model-authored calls after transactional rejection rollback'))
    print(json.dumps(read('MEASUREMENTS.json'), indent=2))

def verify():
    baseline = read('BASELINE.json')
    assert all(sha(ROOT / p) == h for p, h in baseline['protected_files'].items())
    assert all(sha(HERE / p) == h for p, h in read('FREEZE.json')['files'].items())
    suite = unittest.defaultTestLoader.discover(str(HERE), pattern='test_transport.py')
    test = unittest.TextTestRunner(verbosity=2).run(suite)
    assert test.wasSuccessful() and test.testsRun == read('QUALIFICATION.json')['tests']
    rows = read('INFERENCE.json')['rows']
    seen = set()
    session = tools.Session(['value'])
    observed = []
    checks = []
    for row in rows:
        label = row['id']
        req = read('calls/' + label + '-request.json')
        assert __import__('hashlib').sha256(req['serialized'].encode()).hexdigest() == req['request_sha256']
        assert json.loads(req['serialized']) == req['request']
        assert req['request']['model'] == 'qwen3:8b' and req['request']['options']['seed'] == 625
        chunks = [strict_loads(json.loads(line)['raw'], allow_provider_numbers=True)
            for line in (HERE / 'calls' / (label + '-stream.jsonl')).read_text().splitlines()]
        tc = [c for chunk in chunks for c in chunk.get('message', {}).get('tool_calls', [])]
        assert tc == row['message'].get('tool_calls', [])
        assert ''.join(c.get('message', {}).get('content', '') for c in chunks) == row['message']['content']
        assert row['delivery']['intact'] and row['completion']
        assert row == read('calls/' + label + '-result.json')
        if label.startswith('F1_'):
            envs = normalize(tc, 'ollama', 'qwen3:8b', int(label[3:]), session.schemas, seen)
            for e in envs:
                result = session.dispatch(semantic_call(e))
                observed.append(dict(normalized=e, result=stable(result)))
        checks.append(dict(id=label, request_hash=True, raw_stream_reassembly=True, native_delivery=True))
    expected = [dict(normalized=t['normalized'], result=stable(t['result'])) for t in read('INTERACTION.json')['transcript']]
    assert observed == expected
    assert session.packet == read('INTERACTION.json')['packet']
    feedback_messages = [m for m in read('INTERACTION.json')['messages'] if m['role'] == 'tool']
    assert len(feedback_messages) == len(expected)
    assert all(m['tool_call_id'] == t['normalized']['provider_call_id'] and json.loads(m['content']) == t['result']['response']
        for m, t in zip(feedback_messages, read('INTERACTION.json')['transcript']))
    sources = [p for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts
        and p.name not in ('PUBLICATION-IDENTITIES.json', 'VERIFICATION.json')]
    sources += [HERE.parent / 'R6_25-REPORT.md']
    sources += [ROOT / 'docs' / n for n in ('project-overview-r6.25.md', 'research-log-r6.25.md', 'decisions-r6.25.md')]
    files = {}
    for p in sorted(sources):
        if p.suffix == '.json': json.loads(p.read_text())
        if p.suffix == '.jsonl':
            for line in p.read_text().splitlines(): json.loads(line)
        if p.suffix in ('.md', '.py'):
            text = p.read_text()
            assert all(line == line.rstrip() for line in text.splitlines()), str(p)
            if p.suffix == '.md':
                for link in re.findall(r'\]\(([^)]+)\)', text):
                    if not link.startswith(('http:', 'https:')):
                        target = (p.parent / link.split('#')[0]).resolve()
                        if target.name not in ('VERIFICATION.json', 'PUBLICATION-IDENTITIES.json'):
                            assert target.exists(), (p, link)
        files[p.relative_to(ROOT).as_posix()] = dict(sha256=sha(p), bytes=p.stat().st_size)
    diff = subprocess.run(['git', 'diff', '--check'], capture_output=True, text=True)
    assert diff.returncode == 0, diff.stdout + diff.stderr
    save('PUBLICATION-IDENTITIES.json', dict(timestamp=now(), files=files))
    save('VERIFICATION.json', dict(timestamp=now(), passed=True, protected_count=len(baseline['protected_files']),
        protected_mismatches=[], kernel=26, frozen_files_verified=True, test_methods=test.testsRun,
        inference_calls_during_publication=0, raw_call_checks=checks, matching_feedback_ids=True,
        offline_rejected_construction_transcript_replay=True, executable_replay='NOT_REACHED',
        JSON_and_links_verified=True, whitespace_verified=True, git_diff_check=dict(returncode=diff.returncode, stdout=diff.stdout, stderr=diff.stderr),
        publication_manifest_sha256=sha(HERE / 'PUBLICATION-IDENTITIES.json'), publication_files=len(files), stopped=True))
    assert all(sha(ROOT / p) == e['sha256'] for p, e in read('PUBLICATION-IDENTITIES.json')['files'].items())
    print('Publication verified:', len(files), 'files;', len(baseline['protected_files']), 'protected identities unchanged')

if __name__ == '__main__':
    {'collect': collect, 'verify': verify}[sys.argv[1]]()
