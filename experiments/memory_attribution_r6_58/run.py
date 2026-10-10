"""Bounded R6.58 orchestration; historical source is read-only."""
import importlib.util
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = ROOT / 'benchmark/results/phase6/r6_58'
spec = importlib.util.spec_from_file_location('r57_orchestrator', ROOT / 'experiments/memory_diagnostic_r6_57/run.py')
prior = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prior)
c = prior.c


def write(name, value):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n', encoding='utf-8', newline='\n')


def baseline():
    result = prior.baseline()
    assert result == c.read(ROOT / 'benchmark/results/phase6/r6_57/BASELINE.json')
    assert prior.manifest() == c.read(ROOT / 'benchmark/results/phase6/r6_57/PUBLICATION-IDENTITIES.json')
    assert prior.historical().manifest() == c.read(c.OUT / 'PUBLICATION-IDENTITIES.json')
    result['r57_manifest_sha256'] = c.sha(ROOT / 'benchmark/results/phase6/r6_57/PUBLICATION-IDENTITIES.json')
    return result


def census():
    commands = [
        ['nvidia-smi', '--query-gpu=index,name,memory.total,memory.used,memory.free,driver_version', '--format=csv'],
        ['nvidia-smi', '--query-compute-apps=pid,process_name,used_gpu_memory', '--format=csv'],
        ['nvidia-smi'],
    ]
    packets = []
    for command in commands:
        try:
            p = subprocess.run(command, capture_output=True, text=True, timeout=10)
            packets.append({'command': command, 'returncode': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr})
        except Exception as exc:
            packets.append({'command': command, 'error': str(exc)})
    return {'time_ns': time.time_ns(), 'commands': packets}


def freeze():
    assert not (OUT / 'PREFLIGHT.json').exists()
    write('BASELINE.json', baseline())
    write('DEVICE-PREFLIGHT.json', census())
    write('PADDING-INSPECTION.json', {
        'frozen_worker_sha256': c.sha(ROOT / 'experiments/lora_smoke_r6_56/worker.py'),
        'records': c.read(c.OUT / 'SOURCE-DATASET-IDENTITIES.json')['records'],
        'finding': 'batch1 actual token lengths; tensor([ids]), ones_like attention mask; no static2048 padding',
        'E01_E04_shapes': [[1, n] for n in (702, 752, 827, 855)],
        'dynamic_padding_condition': 'SKIPPED: no unnecessary static padding',
    })
    write('PREFLIGHT.json', {'round': 'R6.58', 'status': 'PASS',
        'worker_sha256': c.sha(HERE / 'worker.py'), 'run_sha256': c.sha(HERE / 'run.py'),
        'sequence': c.read(c.OUT / 'SAMPLING.json')['sequence'][:4],
        'protocol_sha256': c.sha(OUT / 'PROTOCOL.md'),
        'loss_rtol': 1e-6, 'loss_atol': 1e-7, 'gradient_rtol': 1e-5, 'gradient_atol': 1e-7})


def execute(condition):
    assert condition in ('baseline', 'cache_release')
    assert baseline() == c.read(OUT / 'BASELINE.json')
    f = c.read(OUT / 'PREFLIGHT.json')
    assert c.sha(HERE / 'worker.py') == f['worker_sha256']
    assert c.sha(HERE / 'run.py') == f['run_sha256']
    folder = OUT / condition
    folder.mkdir(exist_ok=True)
    with (folder / 'DISPATCH-CLAIM.json').open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(json.dumps({'condition': condition, 'dispatches': 1}) + '\n')
    start = time.perf_counter()
    command = [str(c.PYTHON), str(HERE / 'worker.py'), condition]
    try:
        p = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=1800)
        packet = {'command': command, 'returncode': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr}
    except subprocess.TimeoutExpired as exc:
        packet = {'command': command, 'timeout': True, 'stdout': str(exc.stdout), 'stderr': str(exc.stderr)}
    packet['seconds'] = time.perf_counter() - start
    write(condition + '/PROCESS.json', packet)
    write(condition + '/POSTPROCESS-CENSUS.json', census())
    print(json.dumps(packet, indent=2))


if __name__ == '__main__':
    if sys.argv[1] == 'freeze':
        freeze()
    elif sys.argv[1] == 'execute':
        execute(sys.argv[2])
