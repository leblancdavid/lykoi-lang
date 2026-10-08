"""Publication aggregation, usage attribution and exact fresh-process replay."""
import datetime
import json
import subprocess
import sys
import time

from record import HERE, ROOT, git, load, now, protected, save, sha, verify
from telemetry import SESSIONS, cli


def milliseconds(utc):
    return datetime.datetime.fromisoformat(utc).timestamp()*1000


def usage(infos):
    keys = ('input', 'output', 'reasoning', 'total')
    result = {key+'_tokens':sum(m['tokens'].get(key, 0) for m in infos) for key in keys}
    result.update(cached_read_tokens=sum(m['tokens'].get('cache', {}).get('read', 0) for m in infos),
                  cached_write_tokens=sum(m['tokens'].get('cache', {}).get('write', 0) for m in infos),
                  reported_model_responses=len(infos),
                  reported_harness_cost=sum(m.get('cost', 0) for m in infos),
                  actual_api_cost_usd=None, estimated_cost_usd=None,
                  response_seconds=sum((m['time']['completed']-m['time']['created'])/1000 for m in infos))
    return result


def accounting():
    raw = load(HERE / 'TELEMETRY.json')
    summaries = []
    audit = []
    for session in raw['sessions']:
        infos = session.get('reported_assistant_metadata', [])
        assert infos and all('tokens' in m and 'completed' in m['time'] for m in infos)
        summary = dict(scope=session['scope'], task_session_id=session['task_session_id'],
            models=sorted({m['modelID'] for m in infos}),
            providers=sorted({m['providerID'] for m in infos}), usage=usage(infos))
        allocated = set()
        tasks = []
        if session['scope'] != 'preparation':
            track, stage = session['scope'].split('/')
            for directory in sorted((HERE / 'workspaces' / track).glob('T*/'+stage)):
                beginning = load(directory / 'START.json')
                ends = sorted(directory.glob('RESULT-*.json')) or [directory / 'GAP.json']
                terminal = load(ends[-1])
                end_utc = terminal['utc']
                start_ms, end_ms = milliseconds(beginning['utc']), milliseconds(end_utc)
                indices = [i for i, m in enumerate(infos)
                           if m['time']['created'] >= start_ms and m['time']['completed'] <= end_ms]
                allocated.update(indices)
                boundary = [i for i, m in enumerate(infos)
                            if m['time']['created'] < end_ms and m['time']['completed'] > start_ms
                            and i not in indices]
                tasks.append(dict(task=beginning['task'], stage=stage, interval_usage=usage([infos[i] for i in indices]),
                    fully_contained_response_indices=indices, boundary_response_indices=boundary,
                    note='Boundary-straddling responses excluded from interval allocation, not fractionally estimated'))
        summary['task_intervals'] = tasks
        summary['outside_task_intervals_usage'] = usage([m for i,m in enumerate(infos) if i not in allocated])
        summaries.append(summary)
        proc, _ = cli('export ' + session['task_session_id'] + ' --sanitize --pure')
        assert proc and proc.returncode == 0
        data = json.loads(proc.stdout)
        reads, tool_seconds, tool_count = [], 0, 0
        for message in data['messages']:
            for part in message.get('parts', []):
                if part.get('type') != 'tool':
                    continue
                tool_count += 1
                state = part.get('state', {})
                timing = state.get('time', {})
                if 'start' in timing and 'end' in timing:
                    tool_seconds += (timing['end']-timing['start'])/1000
                inputs = state.get('input', {})
                tool = part.get('tool', '')
                if tool in ('read', 'glob', 'grep'):
                    # Only path/scope fields, never transcript content or arbitrary commands.
                    reads.append(dict(tool=tool, start=timing.get('start'),
                        scope={k:inputs[k] for k in ('filePath', 'path', 'include', 'pattern') if k in inputs}))
        audit.append(dict(scope=session['scope'], tool_calls=tool_count,
            summed_reported_tool_seconds=tool_seconds, explicit_read_search_scopes=reads,
            note='Reported tool intervals can overlap; not OS access logs or pure AI-time allocation'))
    save(HERE / 'USAGE-SUMMARY.json', dict(utc=now(), sessions=summaries,
        accounting='Actual OpenCode assistant-response usage; input/cache/output/reasoning fields separately summed as reported',
        calls='Completed assistant responses with token metadata; underlying retries/provider HTTP requests unobservable',
        cost='Harness reports zero for every response; unknown pricing/billing, not a free-API conclusion',
        reasoning_configuration=None, late_discovery=True))
    save(HERE / 'ACCESS-TOOL-AUDIT.json', dict(utc=now(), sessions=audit,
        attestation='Sanitized reported tool metadata only; filesystem and provider hidden context remain unattested'))
    for row in summaries:
        print(row['scope'], json.dumps(row['usage']))


def collect():
    verify()
    rows, replay = [], []
    for directory in sorted((HERE / 'workspaces').glob('*/*/*')):
        if not directory.is_dir() or not (directory / 'START.json').exists():
            continue
        start = load(directory / 'START.json')
        assert start['utc'] > load(HERE / 'FREEZE.json')['utc']
        results = sorted(directory.glob('RESULT-*.json'))
        original_count = len(load(HERE / 'tasks' / start['task'] / 'acceptance.json'))
        new_count = 0 if start['stage'] == 'base' else len(load(HERE / 'tasks' / start['task'] / 'modification' / 'acceptance.json'))
        if not results:
            terminal = load(directory / 'GAP.json')
            row = dict(track=start['track'], task=start['task'], stage=start['stage'],
                status='CAPABILITY_GAP', passed=False, code=terminal['code'],
                elapsed_seconds=terminal['elapsed_seconds'], test_seconds=0,
                cases_executed=0, cases_passed=0, cases_failed=0,
                cases_not_reached=original_count+new_count, attempts=0, repairs=0,
                regressions=None, original_cases=original_count, new_cases=new_count,
                record=(directory / 'GAP.json').relative_to(HERE).as_posix())
        else:
            terminal = load(results[-1])
            tests = sum(load(p)['test_seconds'] for p in results)
            row = dict(track=start['track'], task=start['task'], stage=start['stage'],
                status='ACCEPTED' if terminal['passed'] else 'ACCEPTANCE_FAILURE', passed=terminal['passed'],
                elapsed_seconds=terminal['elapsed_seconds'], test_seconds=tests,
                cases_executed=terminal['total_cases'], cases_passed=terminal['passed_cases'],
                cases_failed=terminal['total_cases']-terminal['passed_cases'], cases_not_reached=0,
                attempts=len(results), repairs=terminal['repairs'],
                regressions=sum(not c['passed'] for c in terminal['cases'] if c['suite']=='base')
                    if start['stage'] != 'base' else None,
                original_cases=original_count, new_cases=new_count,
                record=results[-1].relative_to(HERE).as_posix())
            for case in terminal['cases']:
                before = time.perf_counter()
                process = subprocess.run(case['command'], input=json.dumps(case['input']),
                    text=True, capture_output=True, cwd=directory, timeout=10)
                actual = json.loads(process.stdout)
                exact = lambda value: json.dumps(value, sort_keys=True, separators=(',', ':'))
                assert process.returncode == 0 and exact(actual) == exact(case['expected'])
                replay.append(dict(track=start['track'], task=start['task'], stage=start['stage'],
                    suite=case['suite'], case=case['case'], passed=True, seconds=time.perf_counter()-before))
        assert row['elapsed_seconds'] <= 900
        rows.append(row)
    assert len(rows) == 24
    totals = {}
    for track in ('A', 'B', 'C'):
        totals[track] = {}
        for stage, denominator in [('base', 5), ('modification', 3)]:
            subset = [r for r in rows if r['track']==track and r['stage']==stage]
            assert len(subset)==denominator
            totals[track][stage] = dict(tasks=denominator, completed=sum(r['passed'] for r in subset),
                capability_gaps=sum(r['status']=='CAPABILITY_GAP' for r in subset),
                cases_passed=sum(r['cases_passed'] for r in subset),
                cases_executed=sum(r['cases_executed'] for r in subset),
                cases_not_reached=sum(r['cases_not_reached'] for r in subset),
                terminal_interval_seconds=sum(r['elapsed_seconds'] for r in subset),
                test_seconds=sum(r['test_seconds'] for r in subset), repairs=sum(r['repairs'] for r in subset),
                regressions=sum(r['regressions'] for r in subset if r['regressions'] is not None)
                    if any(r['regressions'] is not None for r in subset) else None,
                successful_development_mean_seconds=sum(r['elapsed_seconds'] for r in subset if r['passed'])/
                    sum(r['passed'] for r in subset) if any(r['passed'] for r in subset) else None)
    save(HERE / 'COMPARISON.json', dict(utc=now(), classification='R6_12_EXPLORATORY_COMPARISON_ONLY',
        rows=rows, totals=totals, matched_successful_tasks_all_three=0,
        actual_billing_cost_usd=None, repeated_development_trials=1))
    save(HERE / 'REPLAY.json', dict(utc=now(), cases=len(replay), passed=len(replay), observations=replay))
    print(json.dumps(totals, indent=2))


def ledgers():
    comparison = load(HERE / 'COMPARISON.json')
    summaries = load(HERE / 'USAGE-SUMMARY.json')['sessions']
    tools = {s['scope']:s for s in load(HERE / 'ACCESS-TOOL-AUDIT.json')['sessions']}
    text = ['# Actual development usage and effort', '',
        'Source: sanitized OpenCode exports of the assigned sessions. These are actual',
        'reported token fields, not source-size estimates. Whole sessions include setup,',
        'documentation, artifact bookkeeping and final responses. Input and cached-read',
        'tokens are separate fields; reported total equals their sum plus output and',
        'reasoning in these exports. All cache-write counts are zero.', '',
        '| Session | Input | Cached read | Output | Reasoning | Reported total | Responses | Response s | Tool s |',
        '| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
    for s in summaries:
        u = s['usage']
        text.append(f'| {s["scope"]} | {u["input_tokens"]:,} | {u["cached_read_tokens"]:,} | {u["output_tokens"]:,} | {u["reasoning_tokens"]:,} | {u["total_tokens"]:,} | {u["reported_model_responses"]} | {u["response_seconds"]:.3f} | {tools[s["scope"]]["summed_reported_tool_seconds"]:.3f} |')
    text += ['', 'Responses count completed assistant messages with reported usage. Internal',
        'provider retries/HTTP calls remain unobservable. Response time is reported',
        'created→completed duration, not pure reasoning time. Tool intervals may overlap.',
        'Sanitized exports redact read/search inputs: empty scope objects in the tool',
        'audit cannot independently attest paths. Author disclosures supply observed',
        'path histories. Billing remains unavailable; harness cost=0 is not a zero bill.', '',
        '## Task terminal intervals and partial usage allocation', '',
        'Interval tokens below include only responses completely contained between',
        'START and terminal result. Boundary-straddling responses are excluded and',
        'explicitly indexed in USAGE-SUMMARY.json. These partial columns must not be',
        'treated as complete task token costs or added to reconstruct whole sessions.', '',
        '| Track/task/stage | Outcome | Wall s | Test s | Contained input | Cached read | Output | Reasoning | Responses |',
        '| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
    for row in comparison['rows']:
        session = next(s for s in summaries if s['scope']==row['track']+'/'+row['stage'])
        task = next(t for t in session['task_intervals'] if t['task']==row['task'])
        u = task['interval_usage']
        text.append(f'| {row["track"]}/{row["task"]}/{row["stage"]} | {row["status"]} | {row["elapsed_seconds"]:.3f} | {row["test_seconds"]:.3f} | {u["input_tokens"]:,} | {u["cached_read_tokens"]:,} | {u["output_tokens"]:,} | {u["reasoning_tokens"]:,} | {u["reported_model_responses"]} |')
    text += ['', 'Gap intervals measure assessment only, not successful development. No matched',
        'all-track successful task exists, so token/time/cost efficiency rankings are',
        'undefined. Original and modification attempts have zero repairs. A has zero',
        'regressions on 48 original cases; B/C regressions are unavailable.', '',
        '## Post-result review overhead', '',
        'The additional verifier session is outside scored development. Its reported',
        'usage is retained separately in REVIEW-USAGE.json. Coordinator/setup/publication',
        'conversation usage is not fully allocated; no experiment-wide cost is asserted.']
    target = HERE / 'EFFORT.md'
    assert not target.exists()
    target.write_text('\n'.join(text)+'\n', encoding='utf-8')
    session_id = 'ses_ee28c1adcffez3nQTPujm7CBFN'
    proc, seconds = cli('export '+session_id+' --sanitize --pure')
    assert proc and proc.returncode == 0
    data = json.loads(proc.stdout)
    infos = [m['info'] for m in data['messages'] if m.get('info', {}).get('role')=='assistant']
    save(HERE / 'REVIEW-USAGE.json', dict(utc=now(), scope='post-result manual publication review',
        task_session_id=session_id, export_seconds=seconds, usage=usage(infos),
        scored_development=False, reported_assistant_metadata=[
            {k:m[k] for k in ('modelID', 'providerID', 'tokens', 'cost', 'time', 'finish') if k in m}
            for m in infos]))
    print('Actual usage/effort ledger and separate post-result review usage published')


def publication():
    verify()
    allowed = {'AGENTS.md', 'README.md', 'benchmark/README.md', 'docs/project-overview.md',
               'docs/agent-workflow.md', 'docs/research-log.md', 'docs/decisions.md'}
    changed = git('diff', '--name-only').splitlines()
    assert set(changed) <= allowed, changed
    for name in changed:
        original = subprocess.check_output(['git', 'show', 'HEAD:'+name], cwd=ROOT).decode().splitlines()
        iterator = iter((ROOT / name).read_text(encoding='utf-8').splitlines())
        assert all(any(line == candidate for candidate in iterator) for line in original), name
    paths = [p for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts
             and p.name != 'PUBLICATION-IDENTITIES.json']
    paths += [ROOT / 'benchmark/results/phase6/R6_12-REPORT.md'] + [ROOT / n for n in changed]
    for p in paths:
        if p.suffix in ('.md', '.py', '.json'):
            assert all(not line.endswith((' ', '\t')) for line in p.read_text(encoding='utf-8').splitlines()), p
    hashes = {p.relative_to(ROOT).as_posix():sha(p) for p in sorted(paths)}
    target = HERE / 'PUBLICATION-IDENTITIES.json'
    if target.exists():
        assert load(target)['files'] == hashes
    else:
        save(target, dict(utc=now(), classification='R6_12_EXPLORATORY_COMPARISON_ONLY',
                         self_hashed=False, files=hashes, protected_files=len(protected())))
    print(f'Publication integrity passed: {len(hashes)} files, {len(protected())} protected files unchanged')


if __name__ == '__main__':
    globals()[sys.argv[1]]()
