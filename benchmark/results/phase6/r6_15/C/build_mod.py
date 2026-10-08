"""Own staged-modification builder; no runtime task callbacks."""
import argparse
import copy
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent


def publish(task, plan):
    payload = json.dumps(plan, indent=2) + '\n'
    for directory in ('mod-first', 'modified'):
        target = HERE / directory / (task + '.plan.json')
        target.parent.mkdir(exist_ok=True)
        with target.open('x', encoding='utf-8', newline='\n') as stream:
            stream.write(payload)


def build():
    t1 = json.loads((HERE / 'base/T1.plan.json').read_text())
    t1['decode']['steps'][0]['node']['branches'].append({
        'prefixes': [[2]], 'node': {'id': 'M1_superboost', 'op': 'literal',
                                  'bytes': [2], 'value': {'const': 20}}})
    publish('T1', t1)

    t2 = json.loads((HERE / 'base/T2.plan.json').read_text())
    t2['decode']['steps'][0] = {'bind': 'version', 'node': {
        'id': 'M2_version', 'op': 'choice', 'code': 'VERSION', 'branches': [
            {'prefixes': [[v]], 'node': {'id': 'M2_v' + str(v), 'op': 'literal',
                                       'bytes': [v], 'value': {'const': v}}}
            for v in (1, 2)]}}
    # Preserve the frozen version1 partial implementation. For version2, only
    # empty runs can be published faithfully by this candidate.
    original_check = copy.deepcopy(t2['decode']['steps'][2]['node']['body'])
    t2['decode']['steps'][2]['node']['body'] = {
        'id': 'M2_support', 'op': 'dispatch',
        'expr': {'eq': [{'ref': 'version'}, {'const': 1}]},
        'branches': {'True': original_check, 'False': {
            'id': 'M2_empty_only', 'op': 'check',
            'test': {'eq': [{'ref': 'item.count'}, {'const': 0}]},
            'code': 'AUTHORING_UNSUPPORTED', 'site': {'ref': 'item.count'}}}}
    publish('T2', t2)


def observe(vm, plan, data):
    if len(data) > 64:
        return {'status': 'reject', 'code': 'INPUT_LIMIT', 'offset': 64}
    result = vm.execute(plan, data)
    if result['status'] == 'success':
        return {'status': 'success', 'value': result['value'], 'output': result['output'].hex()}
    if result['status'] == 'reject':
        return {'status': 'reject', 'code': result['error']['code'], 'offset': result['error']['offset']}
    return result


def expected(task, data):
    def reject(code, offset):
        return {'status': 'reject', 'code': code, 'offset': offset}
    if len(data) > 64:
        return reject('INPUT_LIMIT', 64)
    if not data:
        return reject('TRUNCATED', 0)
    if task == 'T1':
        if data[0] > 2:
            return reject('MODE', 0)
        if len(data) < 3:
            return reject('TRUNCATED', len(data))
        if len(data) > 3:
            return reject('TRAILING', 3)
        raw = data[1] + data[2] + 10 * data[0]
        amount, clipped = min(raw, 200), raw > 200
        return {'status': 'success', 'value': {'amount': amount, 'clipped': clipped},
                'output': bytes([amount, int(clipped)]).hex()}
    if data[0] not in (1, 2):
        return reject('VERSION', 0)
    values = []
    cursor = 1
    for record in range(9):
        if cursor == len(data):
            return {'status': 'success', 'value': values, 'output': bytes(values).hex()}
        if record == 8:
            return reject('OCCURRENCE_LIMIT', cursor)
        count = data[cursor]
        if count > 4:
            return reject('RUN', cursor)
        cursor += 1
        if cursor == len(data):
            return reject('TRUNCATED', cursor)
        values.extend([data[cursor]] * count)
        if data[0] == 2 and count:
            values.append(255)
        cursor += 1
    raise AssertionError('unreachable')


def test(task):
    import sys
    sys.path.insert(0, str(HERE.parents[4] / 'experiments/semantic_interpreter'))
    import interpreter as vm
    started = time.perf_counter()
    plan = json.loads((HERE / 'modified' / (task + '.plan.json')).read_text())
    if task == 'T1':
        cases = [bytes(x) for x in ([], [0], [1, 255], [2], [2, 0], [3], [255, 0, 0],
                                    [2, 0, 0, 9])]
        cases += [bytes([m, x, y]) for m in range(3)
                  for x, y in ((0, 0), (0, 255), (255, 255), (100, 100),
                               (90, 100), (89, 100), (91, 100), (80, 100),
                               (79, 100), (81, 100))]
        cases += [bytes(65)]
    else:
        cases = [bytes(x) for x in ([], [0], [3], [255], [1], [2], [1, 0], [2, 0],
                                    [1, 5], [2, 5], [1, 1, 255], [2, 1, 255],
                                    [1, 2, 7], [2, 4, 7], [2, 0, 255],
                                    [1, 1, 7, 0, 9, 1, 7], [2, 0, 8, 0, 9])]
        cases += [bytes([v] + [c, 255] * n) for v in (1, 2)
                  for c in (0, 1, 4) for n in (8, 9)]
        cases += [bytes(65)]
    results = []
    for data in cases:
        actual, wanted = observe(vm, plan, data), expected(task, data)
        results.append({'input': data.hex(), 'actual': actual, 'expected': wanted,
                        'pass': actual == wanted})
    report = {'task': task, 'batch': 1, 'utc': datetime.now(timezone.utc).isoformat(),
              'elapsed_seconds': time.perf_counter() - started,
              'nodes': vm.validate(plan), 'passed': sum(r['pass'] for r in results),
              'total': len(results), 'results': results}
    with (HERE / ('MOD-SELFTEST-' + task + '.json')).open('x', encoding='utf-8') as stream:
        json.dump(report, stream, indent=2)
        stream.write('\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'results'}))


def handoff():
    now = datetime.now(timezone.utc)
    artifacts = {}
    for task in ('T1', 'T2'):
        first = HERE / 'mod-first' / (task + '.plan.json')
        final = HERE / 'modified' / (task + '.plan.json')
        assert first.read_bytes() == final.read_bytes()
        artifacts[task] = {
            'first_sha256': hashlib.sha256(first.read_bytes()).hexdigest(),
            'final_sha256': hashlib.sha256(final.read_bytes()).hexdigest(),
            'first_snapshot_utc': datetime.fromtimestamp(first.stat().st_mtime, timezone.utc).isoformat(),
            'repairs': 0, 'development_batches': 1,
            'selftest': json.loads((HERE / ('MOD-SELFTEST-' + task + '.json')).read_text())}
    report = {
        'session': 'R6.15 fresh Track C staged modification T1 then T2',
        'status': 'IMMUTABLE_HANDOFF_PARTIAL', 'handoff_utc': now.isoformat(),
        'originals_edited': False, 'vm_edited': False,
        'central_behavior': 'Explicit plans executed by original interpreter.execute; no callbacks. Self-test oracle is development-only.',
        'candidate_policy': 'One initial revision each; exclusive first snapshots before any tests; final identical; no self-test repairs.',
        'tool_calls': 20,
        'tool_count_convention': 'Count individual underlying calls, including failed read; parallel wrapper is not an additional call.',
        'timing': {
            'first_tool_start': None,
            'first_tool_start_note': 'Not instrumented locally; use harness metadata for exact session wall duration. No invented timestamp.',
            'snapshot_to_handoff_seconds': now.timestamp() - min(
                (HERE / 'mod-first' / (task + '.plan.json')).stat().st_mtime for task in ('T1', 'T2')),
            'test_timeout_seconds_each': 30},
        'exposure': {
            'read': ['tasks/COMMON.md', 'tasks/T1.md', 'tasks/T2.md', 'PROTOCOL.md',
                     'sealed/M1.md', 'sealed/M2.md', 'C/base/T1.plan.json', 'C/base/T2.plan.json',
                     'experiments/semantic_interpreter/CONTRACT-1.md',
                     'experiments/semantic_interpreter/interpreter.py'],
            'failed_read': 'tasks/PROTOCOL.md (absent; corrected to root PROTOCOL.md)',
            'other_access': 'git status --short; own builder and generated own artifacts',
            'inherited_guidance': 'Repository AGENTS.md provided by harness; no additional historical reads.',
            'other_track_acceptance_sealed_json_scoring_sessions': False,
            'delegation': False, 'coordinator_feedback': False},
        'difficulties': [
            'T1 required one new disjoint mode2 branch with boost20; original arithmetic and layout reused.',
            'Frozen T2 already rejects counts2..4 with AUTHORING_UNSUPPORTED. This candidate retains that partial version1 behavior, not full contract compliance.',
            'T2 version2 supports empty input payload and zero-count runs; nonempty runs reject AUTHORING_UNSUPPORTED after structural parsing. Errors RUN/TRUNCATED/OCCURRENCE_LIMIT precede unsupported checks.',
            'VM map/each operate on at most8 items; map preserves one output item per input item. join constructs ASCII strings, not flattened integer lists; const cannot create lists. Consuming repeat can create lists but repeating value nodes alone fails conservative progress. These observations explain difficulty with this approach, not an impossibility proof for every explicit plan.',
            'No full finite alternative or lower-bound proof was established within this session. Failures are retained as partial authoring failure, not missing-capability verdict.',
            'One builder syntax typo corrected before candidate generation and before testing; no candidate repair.'],
        'artifacts': artifacts,
        'stop': 'No post-handoff edits or additional tests authorized.'}
    with (HERE / 'AUTHORING-MOD.json').open('x', encoding='utf-8') as stream:
        json.dump(report, stream, indent=2)
        stream.write('\n')
    print(json.dumps({'status': report['status'], 'handoff_utc': report['handoff_utc'],
                      'snapshot_to_handoff_seconds': report['timing']['snapshot_to_handoff_seconds'],
                      'artifacts': {task: {key: value for key, value in info.items() if key != 'selftest'}
                                    for task, info in artifacts.items()}}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=('build', 'T1', 'T2', 'handoff'))
    args = parser.parse_args()
    if args.action == 'build':
        build()
    elif args.action == 'handoff':
        handoff()
    else:
        test(args.action)
