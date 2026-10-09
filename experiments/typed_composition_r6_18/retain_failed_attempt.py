"""One-time retention of the interrupted first evidence runner, before correction."""
import json
from composition import HERE, expand, vm
from examples import examples
from preservation import sha

if __name__ == '__main__':
    target = HERE / 'FAILED-ATTEMPT-2.json'
    assert not target.exists()
    plan = expand(examples()['header_increment'])['plan']
    source = (HERE / 'run_evidence.py').read_bytes()
    data = {'attempt': 1, 'status': 'INTERRUPTED_TEST_EXPECTATION_FAILURE',
            'runner_source_utf8': source.decode(), 'runner_source_sha256': sha(source),
            'assertion': "a['error']['offset'] == (0 if context == 'pair' else 1)",
            'completed_pair_passes': [
                {'repeat': 1, 'success': 32896, 'BOUND': 32640, 'seconds': 4.623},
                {'repeat': 2, 'success': 32896, 'BOUND': 32640, 'seconds': 4.523},
                {'repeat': 3, 'success': 32896, 'BOUND': 32640, 'seconds': 4.495}],
            'failing_input_hex': '0700ff',
            'observed': vm.execute(plan, bytes.fromhex('0700ff')),
            'inner_failure_control': vm.execute(plan, bytes.fromhex('07ff00')),
            'cause': 'Expected outer sum offset1 ignored existing VM seq result span at call start3; explicit twin and lowered envelopes matched.',
            'correction': 'Expected outer BOUND site is3; nested increment BOUND site remains1. No validator/expander/VM change.'}
    target.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
    print('Retained initial runner, observations and failure:', target.name)
