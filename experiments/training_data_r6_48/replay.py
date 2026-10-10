"""Fresh-process AI-free execution and literal frozen acceptance comparison."""
import argparse
import copy
import hashlib
import json
import sys
from datetime import datetime, timezone

from prepare import ROOT, EVIDENCE, canonical, read, sha, write
from construct import verify_freeze, c


def json_result(result):
    result = copy.deepcopy(result)
    if 'output' in result:
        result['output_hex'] = result.pop('output').hex()
    return result


def compare(expected, actual, root):
    expected = copy.deepcopy(expected)
    if 'error' in expected:
        role = expected['error'].pop('role')
        expected['error']['node'] = root if role == 'program' else root + '/' + role
    differences = []
    for key, value in expected.items():
        if key not in actual or type(actual[key]) is not type(value) or actual[key] != value:
            differences.append({'field': key, 'expected': value, 'actual': actual.get(key)})
    return differences


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pass-id', type=int, required=True, choices=[1, 2, 3])
    args = parser.parse_args()
    source_hash = verify_freeze()
    freeze = read(EVIDENCE / 'CANDIDATE-FREEZE.json')
    assert freeze['source_freeze_sha256'] == source_hash
    for name, digest in freeze['files'].items():
        assert sha(ROOT / name) == digest, name
    results = []
    for n in range(1, 9):
        eid = 'E%02d' % n
        folder = EVIDENCE / 'episodes' / eid
        package = c.load((folder / 'SYMBOLIC.json').read_text(encoding='ascii'))
        diagnostic = c.diagnose(package)
        expanded = c.expand(package)
        assert canonical(expanded['plan']) == canonical(read(folder / 'EXECUTABLE.json'))
        validation = read(folder / 'VALIDATION.json')
        assert diagnostic == validation['diagnostic']
        cases = read(folder / 'ACCEPTANCE.json')['cases']
        root = 'program/' + package['program']['identity']
        observations = []
        for i, case in enumerate(cases):
            actual = json_result(c.vm.execute(expanded['plan'], bytes.fromhex(case['input_hex']), case.get('limits')))
            differences = compare(case['expected'], actual, root)
            observations.append({'case_index': i, 'input_hex': case['input_hex'],
                                 'limits': case.get('limits'), 'actual': actual,
                                 'acceptance_matches': not differences, 'differences': differences})
        results.append({'episode_id': eid, 'validation': diagnostic,
                        'symbolic_sha256': sha(folder / 'SYMBOLIC.json'),
                        'acceptance_sha256': sha(folder / 'ACCEPTANCE.json'), 'observations': observations,
                        'all_acceptance_matches': all(o['acceptance_matches'] for o in observations)})
    body = {'version': 'lykoi-pilot-replay-1', 'pass_id': args.pass_id,
            'utc': datetime.now(timezone.utc).isoformat(), 'python': sys.version,
            'source_freeze_sha256': source_hash, 'candidate_freeze_sha256': sha(EVIDENCE / 'CANDIDATE-FREEZE.json'),
            'ai_calls': 0, 'results': results,
            'observations_identity': hashlib.sha256(canonical(results)).hexdigest(),
            'all_acceptance_matches': all(r['all_acceptance_matches'] for r in results)}
    write(EVIDENCE / ('REPLAY-%d.json' % args.pass_id), body)
    print(json.dumps({'pass': args.pass_id, 'cases': sum(len(r['observations']) for r in results),
                      'acceptance_matches': body['all_acceptance_matches'],
                      'observations_identity': body['observations_identity']}))


if __name__ == '__main__':
    main()
