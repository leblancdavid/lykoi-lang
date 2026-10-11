"""One authorized R6.67 invocation of the byte-identical R6.66 worker."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'experiments/incremental_training_r6_66'))
import run as frozen

OUT = ROOT / 'benchmark/results/phase6/r6_67'
INPUT = frozen.OUT
EXPECTED = {
    'DATASET.json': '75b78ccf27a6043af05cb197fc4c36d73aebbfd244b6fcbc55087d635746daf9',
    'SAMPLING.json': '554dc5e8d15b2371088c10ed0c211fd570a58e1f586c1a58795dfb144015a38f',
}


def preflight():
    assert Path(sys.executable).resolve() == frozen.PYTHON.resolve()
    publication = frozen.publication('r6_66')
    freeze = frozen.frozen_check()
    baseline = frozen.baseline()
    for name, digest in EXPECTED.items():
        assert frozen.identity(frozen.read(INPUT / name)) == digest
    config = frozen.read(INPUT / 'TRAINING-CONFIGURATION.json')
    assert config['canonical_sha256'] == frozen.identity(config['configuration']) == 'b7f02ba671c78baf243148a4ed49b8e143775538bb5cbd82369ee2294d096ca5'
    ready = frozen.read(INPUT / 'TRAINING-READINESS.json')
    assert ready['ready'] and all(v == 'QUALIFIED' for v in ready['components'].values())
    diagnostics = frozen.read(INPUT / 'DIAGNOSTICS.json')
    assert len(diagnostics['records']) == len(diagnostics['expectations']) == 13
    for row, expected in zip(diagnostics['records'], diagnostics['expectations']):
        assert frozen.identity(row['prompt']) == expected['prompt_identity']
        assert frozen.score(row['completion'][0]['content'], row)['accepted']
    assert not frozen.ARTIFACTS.exists()
    return dict(status='PASS', publication=publication, baseline=baseline,
                configuration_identity=config['canonical_sha256'], canonical_identities=EXPECTED,
                diagnostics=diagnostics['expectations'], worker_sha256=config['configuration']['worker_sha256'],
                readiness=ready, kernel_constructs=26, model_calls=0,
                execution='Exact frozen worker; read-only R6.66 inputs; additive R6.67 telemetry routing; frozen external checkpoint paths unchanged')


def route():
    original_read = frozen.read
    original_check = frozen.frozen_check
    def read(path):
        path = Path(path)
        if path.parent == OUT and (INPUT / path.name).exists():
            path = INPUT / path.name
        return original_read(path)
    def check():
        frozen.OUT = INPUT
        try:
            return original_check()
        finally:
            frozen.OUT = OUT
    frozen.OUT = OUT
    frozen.read = read
    frozen.frozen_check = check


def worker(mode):
    route()
    source = (INPUT / 'EFFECTIVE-WORKER.py.txt').read_text(encoding='utf-8')
    frozen.frozen_check()
    namespace = {'__name__': 'r667_exact_frozen_worker'}
    exec(compile(source, 'R6.66-effective-worker', 'exec'), namespace)
    namespace[mode if mode in ('train', 'reload') else 'diagnostics'](*([] if mode in ('train', 'reload') else [mode]))


def dispatch(mode):
    with (OUT / (mode.upper() + '-DISPATCH-CLAIM.json')).open('x', encoding='utf-8') as stream:
        json.dump(dict(round='R6.67', mode=mode, attempts=1), stream)
        stream.write('\n')
    if mode == 'base':
        frozen.ARTIFACTS.mkdir(exist_ok=False)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', HF_HUB_OFFLINE='1', HF_HUB_DISABLE_TELEMETRY='1',
               HF_HOME=str(frozen.STORE / 'hf-cache'), TOKENIZERS_PARALLELISM='false')
    env.pop('CUDA_VISIBLE_DEVICES', None)
    args = [str(frozen.PYTHON), '-B', str(Path(__file__).resolve()), 'worker', mode]
    started = time.perf_counter()
    try:
        process = subprocess.run(args, cwd=ROOT, env=env, capture_output=True, text=True,
                                 timeout=120 if mode == 'reload' else 1800)
        packet = dict(argv=args, returncode=process.returncode, stdout=process.stdout, stderr=process.stderr)
    except subprocess.TimeoutExpired as exc:
        packet = dict(argv=args, returncode=None, stdout=str(exc.stdout), stderr=str(exc.stderr), error='PROCESS_TIMEOUT')
    frozen.write(mode.upper() + '-PROCESS.json', dict(packet, seconds=time.perf_counter() - started))
    assert packet['returncode'] == 0, 'Single authorized dispatch halted; no retry'


def execute():
    assert not OUT.exists()
    receipt = preflight()
    OUT.mkdir()
    frozen.OUT = OUT
    frozen.write('PREFLIGHT.json', receipt)
    try:
        for mode, result in [('base', 'DIAGNOSTIC-BASE.json'), ('train', 'TRAINING-RESULT.json'),
                             ('reload', 'ADAPTER-RELOAD.json'), ('adapter', 'DIAGNOSTIC-ADAPTER.json')]:
            dispatch(mode)
            assert frozen.read(OUT / result)['status'] == 'PASS'
            print('PASS', mode, flush=True)
    except BaseException as exc:
        frozen.write('HALT.json', dict(error=str(exc), traceback=traceback.format_exc(), retry=False))
        raise


if __name__ == '__main__':
    if sys.argv[1] == 'execute':
        execute()
    elif sys.argv[1] == 'worker':
        worker(sys.argv[2])
    else:
        raise ValueError(sys.argv[1])
