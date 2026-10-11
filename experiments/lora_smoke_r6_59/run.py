"""One authorized R6.59 attempt, reusing exact historical model and scorer helpers."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = ROOT / 'benchmark/results/phase6/r6_59'
WRITE_LOCK = threading.RLock()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


r58 = load('r59_prior', 'experiments/memory_attribution_r6_58/run.py')
c = r58.c
STORE, PYTHON = c.STORE, c.PYTHON
ARTIFACTS = STORE / 'r6-59'
canonical, file_manifest, identity, q52, read, rows, score, sha = (
    c.canonical, c.file_manifest, c.identity, c.q52, c.read, c.rows, c.score, c.sha)


def write(name, value):
    with WRITE_LOCK:
        OUT.mkdir(parents=True, exist_ok=True)
        path = OUT / name
        temporary = path.with_suffix(path.suffix + '.pending')
        temporary.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n', encoding='utf-8', newline='\n')
        temporary.replace(path)


def baseline():
    result = r58.baseline()
    assert result == read(r58.OUT / 'BASELINE.json')
    manifest = read(r58.OUT / 'PUBLICATION-IDENTITIES.json')
    for path, entry in manifest['files'].items():
        assert sha(ROOT / path) == entry['sha256'], path
    assert read(r58.OUT / 'VERIFICATION.json')['passed'] is True
    return dict(result, r58_publication_sha256=sha(r58.OUT / 'PUBLICATION-IDENTITIES.json'))


def frozen_check():
    c.frozen_check()
    freeze = read(OUT / 'PREFLIGHT.json')
    for path, digest in freeze['frozen_payloads'].items():
        assert sha(ROOT / path) == digest, path
    assert identity(read(OUT / 'TRAINING-CONFIGURATION.json')['configuration']) == freeze['training_configuration_identity']
    return freeze


def accounting_control():
    import torch
    from transformers.optimization import get_linear_schedule_with_warmup
    kwargs = dict(read(c.OUT / 'TRAINING-CONFIGURATION.json')['configuration']['optimizer_configuration']['kwargs'])
    kwargs['betas'] = tuple(kwargs['betas'])
    pairs = []
    for _ in range(2):
        p = torch.nn.Parameter(torch.tensor([1.0, -2.0]))
        opt = torch.optim.AdamW([p], **kwargs)
        sched = get_linear_schedule_with_warmup(opt, 2, 20)
        pairs.append((p, opt, sched))
    observations = []
    for step in range(1, 21):
        for index, (p, opt, sched) in enumerate(pairs):
            opt.zero_grad(set_to_none=True)
            for micro in range(4):
                ((p.square().mean() + micro * p.mean()) / 4).backward()
                if index == 1:
                    # Read-only accounting cannot add attributes or mutate live state.
                    before = copy.deepcopy(sched.state_dict())
                    copy.deepcopy(opt.state_dict())
                    assert before == sched.state_dict() and 'step' not in before
            torch.nn.utils.clip_grad_norm_([p], 1, error_if_nonfinite=True, foreach=None)
            opt.step()
            sched.step()
        a, b = pairs
        assert torch.equal(a[0], b[0]) and a[2].state_dict() == b[2].state_dict()
        for key, value in a[1].state[a[0]].items():
            assert torch.equal(value, b[1].state[b[0]][key])
        observations.append({'step': step, 'exact_parameters_moments_scheduler_equal': True, 'lr': b[1].param_groups[0]['lr']})
    return {'status': 'PASS', 'cpu_synthetic_only': True, 'model_updates': 0, 'comparisons': observations,
            'method': 'local counters after native calls, read-only state_dict; no method reassignment'}


def freeze():
    assert not (OUT / 'PREFLIGHT.json').exists()
    assert ARTIFACTS.parent.is_dir() and not ARTIFACTS.exists()
    write('BASELINE.json', baseline())
    for name in ('TRAINING-CONFIGURATION.json', 'SAMPLING.json', 'LOSS-NORMALIZATION.json',
                 'OPTIMIZER-CONFIGURATION.json', 'DIAGNOSTIC-PROTOCOL.json', 'DIAGNOSTIC-BASE-SUMMARY.json'):
        # Preserve exact bytes and R6.56 identities, including historical round fields.
        (OUT / name).write_bytes((c.OUT / name).read_bytes())
    write('ACCOUNTING-QUALIFICATION.json', accounting_control())
    worker = load('r59_worker_source', 'experiments/lora_smoke_r6_59/worker.py')
    source = worker.effective_source()
    compile(source, 'R6.59-effective-worker', 'exec')
    (OUT / 'EFFECTIVE-WORKER.py.txt').write_text(source, encoding='utf-8', newline='\n')
    write('CACHE-RELEASE-QUALIFICATION.json', {'inherited_round': 'R6.58',
          'evidence_sha256': sha(r58.OUT / 'ANALYSIS.json'), 'gradient_bytes_preserved': True,
          'release_order': 'backward, scalar telemetry, delete graph/input references, synchronize, finite-gradient hashes, empty_cache, memory and exact gradient-hash verification',
          'zero_grad_between_microbatches': False, 'new_gpu_qualification_runs': 0})
    write('BASELINE-REUSE.json', {'status': 'PASS', 'source': 'r6_56/DIAGNOSTIC-BASE-SUMMARY.json',
          'source_sha256': sha(c.OUT / 'DIAGNOSTIC-BASE-SUMMARY.json'), 'scorer_sha256': sha(ROOT / 'experiments/lora_smoke_r6_56/common.py'),
          'protocol_sha256': sha(c.OUT / 'DIAGNOSTIC-PROTOCOL.json'), 'configuration_differences': [], 'base_reruns': 0})
    write('DEVICE-PREFLIGHT.json', r58.census())
    paths = list(HERE.glob('*.py')) + list(OUT.iterdir())
    write('PREFLIGHT.json', {'status': 'PASS', 'round': 'R6.59', 'training_configuration_identity': c.frozen_check()['training_configuration_identity'],
          'amendment': 'controlled post-backward cache release; nonintrusive diagnostics only',
          'frozen_payloads': {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted(paths) if p.is_file()},
          'kernel_constructs': 26, 'attempts_authorized': 1, 'optimizer_updates_planned': 20})
    print('PASS preserved baseline, frozen source, CPU accounting control; no model training dispatched')


def dispatch(name, args, timeout):
    frozen_check()
    ARTIFACTS.mkdir(exist_ok=True)
    with (OUT / (name + '-DISPATCH-CLAIM.json')).open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(json.dumps({'round': 'R6.59', 'dispatch': name, 'args': args}) + '\n')
    start = time.perf_counter()
    argv = [str(PYTHON), str(HERE / 'worker.py'), *args]
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', HF_HUB_OFFLINE='1', HF_HUB_DISABLE_TELEMETRY='1', HF_HOME=str(STORE / 'hf-cache'))
    try:
        p = subprocess.run(argv, cwd=ROOT, env=env, capture_output=True, text=True, timeout=timeout)
        packet = {'argv': argv, 'returncode': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr, 'external_abort': None}
    except subprocess.TimeoutExpired as exc:
        packet = {'argv': argv, 'returncode': None, 'stdout': str(exc.stdout), 'stderr': str(exc.stderr), 'external_abort': 'PROCESS_WALL_TIMEOUT'}
    packet.update(seconds=time.perf_counter() - start, timeout_seconds=timeout)
    write(name + '-PROCESS.json', packet)
    print(json.dumps(packet, indent=2))
    return packet


if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'freeze':
        freeze()
    elif mode == 'train':
        assert baseline() == read(OUT / 'BASELINE.json')
        packet = dispatch('TRAINING', ['train'], 1800)
        write('POSTPROCESS-CENSUS.json', r58.census())
        if packet['returncode'] != 0:
            raise RuntimeError('single training attempt halted; no restart')
    elif mode == 'reload':
        assert read(OUT / 'TRAINING-RESULT.json')['status'] == 'PASS'
        assert dispatch('RELOAD', ['reload'], 120)['returncode'] == 0
    elif mode == 'post':
        old = load('r59_diagnostics', 'experiments/lora_smoke_r6_56/run.py')
        old.OUT, old.ARTIFACTS, old.write, old.dispatch = OUT, ARTIFACTS, write, dispatch
        old.diagnostics('adapter')
    else:
        raise ValueError(mode)
