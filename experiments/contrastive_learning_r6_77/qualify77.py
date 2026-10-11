"""Synthetic recovery/resource/process controls only; no GPU or model work."""
import os
from pathlib import Path
import sys
import time
import uuid
from durable77 import Journal, atomic, launch, load

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'experiments/contrastive_preflight_r6_75'))
import resources75 as resource

OUT = ROOT/'benchmark/results/phase6/r6_77'
PYTHON = Path(r'C:\Users\lblan\AppData\Local\Temp\opencode\lykoi-r6-52\venv\Scripts\python.exe')


def worker(output, nonce, delay):
    output = Path(output)
    atomic(output/'HANDSHAKE.json', dict(worker_pid=os.getpid(), parent_pid=os.getppid(),
           interpreter=sys.executable, nonce=nonce))
    time.sleep(float(delay))
    atomic(output/'CONTROL-COMPLETE.json', dict(synthetic=True, model_calls=0))


def main():
    began = time.perf_counter()
    controls = OUT/'controls_2'
    controls.mkdir(exist_ok=False)
    binding = dict(configuration_identity='synthetic-control-only', case_ids=['A', 'B'])
    journal = Journal(controls/'valid', binding)
    index = journal.begin('A')
    journal.commit(index, dict(id='A', raw='synthetic raw text', scores={'accepted': False}))
    assert Journal(controls/'valid', binding).recover() == [dict(id='A', raw='synthetic raw text', scores={'accepted': False})]
    checks = {'fresh_instance_committed_recovery': True}

    def rejects(name, action):
        try:
            action()
        except (AssertionError, ValueError, FileNotFoundError, IndexError, RuntimeError):
            checks[name] = True
        else:
            raise AssertionError('CONTROL_DID_NOT_REJECT:' + name)

    rejects('duplicate_case_generation_refused', lambda: journal.begin('A'))
    rejects('changed_binding_refused', lambda: Journal(controls/'valid', dict(binding, configuration_identity='changed')).recover())
    incomplete = Journal(controls/'interrupted', binding)
    incomplete.begin('A')
    rejects('interrupted_start_no_retry', incomplete.recover)
    rejects('interrupted_generation_refused', lambda: incomplete.begin('A'))
    corrupted = Journal(controls/'corrupt', binding)
    corrupted.commit(corrupted.begin('A'), dict(id='A', raw='original'))
    (controls/'corrupt/000.raw.json').write_text('{"id":"A","raw":"changed"}\n')
    rejects('raw_corruption_refused', corrupted.recover)
    pending = Journal(controls/'pending', binding)
    (pending.root/'000.raw.json.pending').write_text('{}\n')
    rejects('incomplete_atomic_write_refused', pending.recover)
    orphan = Journal(controls/'orphan', binding)
    atomic(orphan.root/'000.commit.json', {})
    rejects('orphan_commit_refused', orphan.recover)
    (controls/'duplicate-key.json').write_text('{"id":"A","id":"B"}\n')
    rejects('duplicate_json_key_refused', lambda: load(controls/'duplicate-key.json'))
    rejects('invalid_pid_refused', lambda: resource.measure(-1))
    invalid = resource.measure(2147483647)
    rejects('unavailable_resource_fails_closed', lambda: resource.validate(invalid, 2147483647, 17179869184))
    sample = resource.measure()
    rejects('wrong_resource_pid_refused', lambda: resource.validate(sample, os.getpid()+1, 17179869184))
    phases = []
    for label, delay, timeout in [('complete', 0.4, 10), ('interruption', 5, 2)]:
        nonce = uuid.uuid4().hex
        destination = controls/label
        result = launch([str(PYTHON), str(Path(__file__)), 'worker', str(destination), nonce, str(delay)],
                        destination, resource, 17179869184, timeout, PYTHON, nonce)
        phases.append(result)
        assert result['worker_pid'], 'CONTROL_HANDSHAKE_NOT_REACHED'
        if label == 'complete':
            assert result['returncode'] == 0 and result['failure'] is None
            assert load(destination/'CONTROL-COMPLETE.json')['model_calls'] == 0
        else:
            assert result['failure'] == 'PROCESS_WALL_LIMIT' and result['returncode'] != 0
            assert not (destination/'CONTROL-COMPLETE.json').exists()
            assert not resource.measure(result['worker_pid'])['available']
            checks['tracked_timeout_child_terminated'] = True
            checks['exit_and_samples_persisted'] = (destination/'EXIT.json').exists() and (destination/'resources.jsonl').stat().st_size > 0
    atomic(OUT/'LAUNCHER-QUALIFICATION.json', dict(passed=True, checks=checks, phases=phases,
           seconds=time.perf_counter()-began, model_calls=0, cuda_initialized=False,
           scope='Synthetic synchronous stdlib launcher, real pinned Python workers and Windows RSS; not model/training launch qualification.',
           tool_timeout_argument_ms=1800000, actual_long_duration_probe=False))
    print('Synthetic durable launcher and interruption controls passed; model calls 0.')


if __name__ == '__main__':
    if len(sys.argv) > 1:
        worker(*sys.argv[2:])
    else:
        main()
