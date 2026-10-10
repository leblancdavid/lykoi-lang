"""Preserve and prospectively correct an internal-default assertion before training."""
import sys
from pathlib import Path
from common import OUT, ROOT, read, sha, write

worker = Path(__file__).parent / 'worker.py'
if sys.argv[1] == 'archive':
    assert not (OUT / 'TRAINING-RUN-CLAIM.json').exists()
    original = OUT / 'WORKER-INITIAL.py.txt'
    assert not original.exists()
    original.write_bytes(worker.read_bytes())
    write('PREFLIGHT-INITIAL.json', read(OUT / 'PREFLIGHT.json'))
elif sys.argv[1] == 'bind':
    assert not (OUT / 'TRAINING-RUN-CLAIM.json').exists()
    freeze = read(OUT / 'PREFLIGHT.json')
    original = read(OUT / 'PREFLIGHT-INITIAL.json')
    assert freeze == original
    write('PREUPDATE-ASSERTION-CORRECTION.json', {
        'reason': 'Installed AdamW inherits Adam and adds decoupled_weight_decay=True to optimizer.defaults internally; compare against public kwargs plus that fixed implementation invariant.',
        'initial_worker_sha256': sha(OUT / 'WORKER-INITIAL.py.txt'), 'corrected_worker_sha256': sha(worker),
        'initial_preflight_sha256': sha(OUT / 'PREFLIGHT-INITIAL.json'),
        'training_configuration_identity_unchanged': freeze['training_configuration_identity'],
        'diagnostic_protocol_unchanged': True, 'training_runs_so_far': 0, 'optimizer_steps_so_far': 0,
        'hyperparameter_change': False, 'prospective_instrumentation_correction': True})
    freeze['frozen_payloads'][worker.relative_to(ROOT).as_posix()] = sha(worker)
    freeze['preupdate_assertion_correction_sha256'] = sha(OUT / 'PREUPDATE-ASSERTION-CORRECTION.json')
    write('PREFLIGHT.json', freeze)
    print('PASS pre-update assertion corrected; settings, diagnostics and original evidence preserved')
else:
    raise ValueError('unknown mode')
