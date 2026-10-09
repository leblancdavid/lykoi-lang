"""Posthoc R6.21 accounting/integrity. Never calls inference or tokenization."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def read(name):
    return json.loads((HERE / name).read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2, ensure_ascii=True) + '\n', encoding='utf-8')


def metrics(calls):
    tokens = {}
    for key in ('prompt_eval_count', 'prompt_eval_cached_count', 'eval_count'):
        counts = [x['tokens'][key] for x in calls]
        tokens[key] = dict(reported_sum=sum(x for x in counts if x is not None),
                          missing_calls=sum(x is None for x in counts))
    durations = {}
    for key in ('total_duration', 'load_duration', 'prompt_eval_duration', 'eval_duration'):
        counts = [x['durations_ns'][key] for x in calls]
        durations[key] = dict(reported_seconds=sum(x for x in counts if x is not None) / 1e9,
                             missing_calls=sum(x is None for x in counts))
    return dict(calls=len(calls), statuses=dict(Counter(str(x['status']) for x in calls)),
        tokens=tokens, durations=durations, call_wall_seconds=sum(x['wall_seconds'] for x in calls))


def collect():
    calls = [json.loads(p.read_text()) for p in sorted((HERE / 'calls').glob('*.json'))]
    controls = [x for x in calls if not x['id'].startswith('F')]
    authored = [x for x in calls if x['id'].startswith('F')]
    recorded = {x['id']: x for x in read('CALIBRATION.json')['rows']}
    by_id = {x['id']: x for x in calls}
    rows = []
    for t in read('TASKS.json')['features']:
        if t['id'] in recorded:
            row = recorded[t['id']]
            row['status'] = 'EVALUATED_AFTER_INTACT_DELIVERY'
        elif t['id'] in by_id:
            row = dict(id=t['id'], feature=t['feature'], status='RUNTIME_FAILURE',
                output_evaluation='NOT_REACHED', json_valid='NOT_REACHED', schema_valid='NOT_REACHED',
                type_valid='NOT_REACHED', semantic_valid='NOT_REACHED', executable_correct='NOT_REACHED')
        else:
            row = dict(id=t['id'], feature=t['feature'], status='NOT_REACHED')
        rows.append(row)
    save('NEUTRAL-RESULTS.json', dict(rows=rows, planned_objectives=6, attempted=3,
        evaluated=2, completed=1, valid_compositions=1, runtime_failures=1,
        remaining_not_reached=['F4', 'F5', 'F6'], manual_repairs=0,
        type_precedence='F1 first error is DEPENDENCY; a whole-definition type pass is not established'))
    groups = dict(delivery=metrics(controls), neutral_authoring=metrics(authored), all_calls=metrics(calls))
    groups['neutral_authoring'].update(validation_seconds=sum(x['result']['validation_seconds'] for x in recorded.values()),
        completed_objectives=1, valid_compositions=1, repairs=0,
        validation_timing='strict load/schema/static validation/expansion/finite execution combined; phases not separately timed',
        failed_call_validation='NOT_REACHED', failed_call_tokens='UNAVAILABLE: HTTP500 has no final usage fields')
    tokenizations = read('TOKENIZATIONS.json')['rows']
    save('MEASUREMENTS.json', dict(groups=groups, tokenizer_calls=len(tokenizations),
        tokenizer_seconds=sum(x['seconds'] for x in tokenizations), run=read('RUN-STATUS.json'),
        successful_symbolic_input_utilization=[dict(id=x['id'], input=x['delivery']['utilization'],
            input_plus_output_reserve=x['delivery']['reserved_utilization']) for x in authored if x['status'] == 200],
        billing='UNAVAILABLE', energy='UNAVAILABLE', cached_tokens='Separate runtime field, not assumed additive billing',
        failed_request_preflight_tokens=by_id['F3']['delivery']['expected_input'],
        resource_coverage='initial GPU snapshot and final process working-set snapshot only; no sampled peaks or energy',
        A=dict(status='NOT_REACHED', planned_objectives=4, calls=0, completed_objectives='NOT_REACHED', valid_compositions='NOT_REACHED', validation_seconds='NOT_REACHED'),
        B=dict(status='NOT_REACHED', planned_objectives=4, calls=0, completed_objectives='NOT_REACHED', valid_compositions='NOT_REACHED', assembly_seconds='NOT_REACHED', validation_seconds='NOT_REACHED')))
    # Render planned prompts without dispatch, to verify semantic parity and pin formats.
    import run
    parity = []
    for t in read('TASKS.json')['objectives']:
        a = run.task_prompt(t, 'A')
        b = run.task_prompt(t, 'B', 0)
        delimiter = '<|im_end|>\n<|im_start|>user\n'
        a_system, a_user = a.split(delimiter)
        b_system, b_user = b.split(delimiter)
        assert a_system == b_system
        assert a_user.split('\nInterface:')[0] == b_user.split('\nInterface:')[0]
        parity.append(dict(id=t['id'], common_semantic_text_sha256=hashlib.sha256(a_system.encode()).hexdigest(),
            common_objective_sha256=hashlib.sha256(a_user.split('\nInterface:')[0].encode()).hexdigest(),
            semantic_parity='PASS_STATIC', delivery='NOT_REACHED', A_prompt=a, B_stage1_prompt=b,
            A_prompt_sha256=hashlib.sha256(a.encode()).hexdigest(), B_stage1_prompt_sha256=hashlib.sha256(b.encode()).hexdigest(),
            measured_tokens='NOT_REACHED: no tokenization or inference after halt'))
    save('COMPARISON.json', dict(status='NOT_REACHED', reason='F3 HTTP500 halted before paired schedule',
        schedule=read('TASKS.json')['schedule'], parity=parity, result='No observed interface ranking'))
    for interface, cap, stages in [('A', 2048, 1), ('B', 512, 4)]:
        save(('COMPLETE-PLAN' if interface == 'A' else 'INCREMENTAL') + '.json', dict(interface=interface,
            status='NOT_REACHED', planned_objectives=4, attempted_objectives=0, model_calls=0,
            per_call_output_cap=cap, max_stages=stages, total_output_budget=2048,
            final_compositions_valid='NOT_REACHED', completed_objectives='NOT_REACHED',
            accounting='No early-termination efficiency advantage; neither paired track began',
            semantic_parity='Statically verified; empirically delivered parity NOT_REACHED'))
    log = (HERE / 'SERVER.log').read_bytes()
    failed = by_id['F3']; begin, end = failed['log_byte_span']
    failure_log = log[begin:end].decode(errors='replace')
    lines = [dict(line=i, text=line) for i, line in enumerate(log.decode(errors='replace').splitlines(), 1) if i >= 471]
    save('FAILURE-ANALYSIS.json', dict(classification='R6_21_PROTOCOL_HALT',
        first_output=dict(call='F1', diagnosis=recorded['F1']['result']['diagnostic'],
            observation='Schema-valid self references instead of constants; empty deps disagrees with references. No repair; later cycle/type checks not reached.'),
        runtime=dict(call='F3', status=500, raw_body=failed['body'], log_lines=lines,
            observed_mechanism='Ollama prediction aborted at token-repeat guard, explicitly reported in body and server log',
            underlying_repetition_cause='UNDETERMINED: aborted generated sequence not returned',
            preflight_input_tokens=969, logged_task_tokens=969, logged_slot_context=8192,
            logged_release_total_tokens=1159, final_output_tokens=None,
            token_note='Do not subtract log slot totals to invent eval_count; final usage absent',
            truncation='No input truncation logged; release truncated=0; final API delivery equality unavailable',
            postcall_loaded_model_responsive=True, request_sha256=failed['request_sha256'],
            historical_link='Same HTTP status as R6.19; historical cause remains unproved because its error body was not retained',
            hypotheses_not_established=['OOM', 'context exhaustion', 'backend crash', 'same cause as R6.19']),
        downstream=dict(F4='NOT_REACHED', F5='NOT_REACHED', F6='NOT_REACHED', A='NOT_REACHED', B='NOT_REACHED'),
        manual_repairs=0, retries=0, postoutcome_prompt_changes=0))
    save('RELIABILITY.json', dict(classification='R6_21_PROTOCOL_HALT',
        intact_delivery=True, intact_delivery_scope='Three sentinels and two evaluated authoring requests; 2851 max verified input; conservative safe bound3584',
        runtime_reliably_completes=False, responses_completed=6, requests_attempted=7,
        model_authored_valid_executable_compositions=1, executable_cases=3, repeated_execution_observations=6,
        failure_accounting=True, gate_passed=False, discovery_recommended=False,
        next_experiment='Separately authorize neutral token-repeat abort diagnosis using raw streaming output capture and bounded controls; no prompt tuning/retry in this round',
        general_reliability='NOT_ESTABLISHED', stop='Publication only; await authorization'))
    print(json.dumps(dict(protected_count=read('BASELINE.json')['protected_count'], measurements=groups), indent=2))


def verify():
    baseline = read('BASELINE.json'); freeze = read('FREEZE.json')
    assert all(sha(ROOT / p) == h for p, h in baseline['protected_files'].items())
    assert all(sha(HERE / p) == h for p, h in freeze['files'].items())
    assert sha(HERE / 'BASELINE.json') == freeze['baseline']
    assert baseline['kernel'] == 26
    assert read('HOST-CONTROLS.json')['passed'] == 7
    assert read('RUN-STATUS.json')['calls'] == 7
    assert read('RELIABILITY.json')['classification'] == 'R6_21_PROTOCOL_HALT'
    # Verification is deterministic and has no participant requests.
    import run
    calibration = read('CALIBRATION.json')['rows']
    for row in calibration:
        call = read('calls/' + row['id'] + '.json')
        assert call['delivery']['intact'] is True
        t = next(x for x in read('TASKS.json')['features'] if x['id'] == row['id'])
        fresh = run.classify(call['response']['response'], read('SCHEMAS.json')['definition'], t)
        assert fresh['classification'] == row['result']['classification']
        assert fresh['composition_valid'] == row['result']['composition_valid']
        assert fresh['objective_complete'] == row['result']['objective_complete']
        if row['id'] == 'F2':
            encoded = json.loads(json.dumps(fresh['envelopes'], default=lambda v: {'bytes_hex': v.hex()}))
            assert encoded == row['result']['envelopes']
    for p in (HERE / 'calls').glob('*.json'):
        call = json.loads(p.read_text())
        assert hashlib.sha256(call['serialized_request'].encode()).hexdigest() == call['request_sha256']
        assert json.loads(call['serialized_request']) == call['request']
        assert hashlib.sha256(call['request']['prompt'].encode()).hexdigest() == call['prompt_sha256']
    paths = list(HERE.rglob('*')) + [ROOT / 'benchmark/results/phase6/R6_21-REPORT.md']
    paths += [ROOT / 'docs' / name for name in ('project-overview-r6.21.md', 'research-log-r6.21.md', 'decisions-r6.21.md')]
    files = {}; links = []
    for p in paths:
        if not p.is_file() or '__pycache__' in p.parts or p.name in ('PUBLICATION-IDENTITIES.json', 'VERIFICATION.json'):
            continue
        if p.suffix == '.json':
            json.loads(p.read_text())
        if p.suffix in ('.md', '.txt', '.py', '.json'):
            assert all(line == line.rstrip() for line in p.read_text().splitlines()), p
        if p.suffix == '.md':
            for link in re.findall(r'\]\(([^)]+)\)', p.read_text()):
                if not link.startswith(('http:', 'https:', '#')):
                    target = (p.parent / link.split('#')[0]).resolve()
                    assert target.exists() or target in (HERE / 'PUBLICATION-IDENTITIES.json', HERE / 'VERIFICATION.json'), link
                    links.append(target)
        files[p.relative_to(ROOT).as_posix()] = dict(sha256=sha(p), bytes=p.stat().st_size)
    diff = subprocess.run(['git', 'diff', '--check'], cwd=ROOT, capture_output=True, text=True)
    assert diff.returncode == 0, diff.stdout + diff.stderr
    status = subprocess.run(['git', 'status', '--short'], cwd=ROOT, capture_output=True, text=True)
    assert all(line.startswith('?? ') for line in status.stdout.splitlines()), status.stdout
    save('PUBLICATION-IDENTITIES.json', dict(round='R6.21', classification='R6_21_PROTOCOL_HALT', files=files,
        exclusions='manifest and separately bound verification receipt; disposable Python bytecode'))
    assert all(sha(ROOT / p) == item['sha256'] and (ROOT / p).stat().st_size == item['bytes'] for p, item in files.items())
    timestamp = datetime.now(timezone.utc).isoformat()
    save('VERIFICATION.json', dict(timestamp=timestamp, classification='R6_21_PROTOCOL_HALT', kernel=26,
        protected_count=len(baseline['protected_files']), protected_mismatches=0, freeze='PASS',
        publication_count=len(files), publication_mismatches=0, manifest_sha256=sha(HERE / 'PUBLICATION-IDENTITIES.json'),
        all_json_parse='PASS', new_text_whitespace='PASS', relative_links='PASS',
        deterministic_validation_and_execution_recheck='F1/F2 classifications match; F2 exact full envelopes match three cases',
        participant_inference_replay='NOT_RUN', git_diff_check='PASS', tracked_changes='NONE',
        P6_A04_acceptance='NOT_RUN', P6_A05_access='NOT_ACCESSED',
        freeze_to_publication_seconds=(datetime.fromisoformat(timestamp) - datetime.fromisoformat(freeze['timestamp'])).total_seconds(),
        elapsed_note='includes inference, interactive analysis and publication, not active labor'))
    assert all(p.exists() for p in links)
    print('Publication integrity PASS:', len(baseline['protected_files']), 'protected;', len(files), 'published; kernel26')


if __name__ == '__main__':
    {'collect': collect, 'verify': verify}[sys.argv[1]]()
