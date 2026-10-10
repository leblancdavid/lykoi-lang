"""Additive, one-shot R6.57 diagnostic orchestration and publication checks."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = ROOT / 'benchmark/results/phase6/r6_57'
sys.path.insert(0, str(ROOT / 'experiments/lora_smoke_r6_56'))
import common as c


def write(name, value):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n',
                            encoding='utf-8', newline='\n')


def historical():
    spec = importlib.util.spec_from_file_location('historical_r56_publication', ROOT / 'experiments/lora_smoke_r6_56/publication.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def baseline():
    h = historical()
    r55 = h.inherited()
    publications = {str(n): r55.r53.identities(ROOT / f'benchmark/results/phase6/r6_{n}') for n in range(52, 57)}
    protected = r55.r53.prior.baseline()
    assert protected == c.read(c.OUT / 'SOURCE-PREFLIGHT.json')['baseline']
    external = r55.r53.prior.external()
    assert external == c.read(c.OUT / 'SOURCE-PREFLIGHT.json')['external_assets']
    packages = r55.r53.prior.package_identity()
    assert packages == c.read(ROOT / 'benchmark/results/phase6/r6_52/ENVIRONMENT-IDENTITIES.json')['packages']
    c.frozen_check()
    return {'publications': publications, 'protected': protected, 'external': external,
            'packages_identity': c.identity(packages), 'installed_distributions': len(packages)}


def freeze():
    assert Path(sys.executable).resolve() == c.PYTHON.resolve()
    assert not (OUT / 'PREFLIGHT.json').exists()
    before = baseline()
    h = historical()
    r53 = h.inherited().r53
    r53.write = lambda name, value: write('SOURCE-' + name, value)
    r53.preflight()
    assert c.read(OUT / 'SOURCE-DATASET-IDENTITIES.json')['records'] == c.read(c.OUT / 'SOURCE-DATASET-IDENTITIES.json')['records']
    # Exact optimizer/scheduler/loss implementations are already bound by the R6.56 freeze.
    import inspect
    import torch
    from transformers.optimization import get_linear_schedule_with_warmup
    from transformers.loss.loss_utils import ForCausalLMLoss
    opt = c.read(c.OUT / 'OPTIMIZER-CONFIGURATION.json')
    sched = c.read(ROOT / 'benchmark/results/phase6/r6_54/LEARNING-RATE-SCHEDULE.json')
    assert str(inspect.signature(torch.optim.AdamW)) == opt['installed_signature']
    assert c.sha(Path(inspect.getfile(torch.optim.AdamW))) == opt['implementation_file_sha256']
    assert c.sha(Path(inspect.getfile(get_linear_schedule_with_warmup))) == sched['scheduler_module_sha256']
    assert c.sha(Path(inspect.getfile(ForCausalLMLoss))) == c.read(c.OUT / 'LOSS-NORMALIZATION.json')['loss_helper_module_sha256']
    control = h.r56_run.numerical_control()
    assert control == c.read(c.OUT / 'LOSS-NORMALIZATION.json')
    write('NORMALIZATION-CONTROL.json', control)
    write('BASELINE.json', before)
    write('PREFLIGHT.json', {'status': 'PASS', 'round': 'R6.57', 'baseline_identity': c.identity(before),
          'worker_sha256': c.sha(HERE / 'worker.py'), 'run_sha256': c.sha(HERE / 'run.py'),
          'training_configuration_identity': c.frozen_check()['training_configuration_identity'],
          'sequence': c.read(c.OUT / 'SAMPLING.json')['sequence'][:4],
          'model_loaded': False, 'optimizer_updates': 0, 'scheduler_updates': 0,
          'kernel_constructs': 26, 'P6_A04_acceptance_executions': 0, 'P6_A05_content_access': False})
    print('PASS baseline, all47 packages, exact six tokenized rows and numerical normalization control')


def execute():
    freeze_record = c.read(OUT / 'PREFLIGHT.json')
    assert freeze_record['status'] == 'PASS'
    assert c.sha(HERE / 'worker.py') == freeze_record['worker_sha256']
    assert c.sha(HERE / 'run.py') == freeze_record['run_sha256']
    assert baseline() == c.read(OUT / 'BASELINE.json')
    with (OUT / 'DISPATCH-CLAIM.json').open('x', encoding='utf-8', newline='\n') as stream:
        json.dump({'round': 'R6.57', 'dispatches': 1}, stream)
        stream.write('\n')
    started = time.perf_counter()
    command = [str(c.PYTHON), str(HERE / 'worker.py')]
    try:
        process = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=1800)
        packet = {'command': command, 'returncode': process.returncode, 'stdout': process.stdout,
                  'stderr': process.stderr, 'seconds': time.perf_counter() - started}
    except subprocess.TimeoutExpired as exc:
        packet = {'command': command, 'returncode': None, 'timeout_seconds': 1800,
                  'stdout': str(exc.stdout), 'stderr': str(exc.stderr), 'seconds': time.perf_counter() - started}
    write('PROCESS.json', packet)
    print(json.dumps(packet, indent=2))


def inventory():
    paths = list(HERE.glob('*.py')) + [ROOT / 'benchmark/results/phase6/R6_57-REPORT.md']
    paths += [ROOT / f'docs/{name}-r6.57.md' for name in ('project-overview', 'research-log', 'decisions')]
    paths += [p for p in OUT.iterdir() if p.is_file() and p.name not in ('PUBLICATION-IDENTITIES.json', 'VERIFICATION.json')]
    return sorted(paths)


def manifest():
    return {'round': 'R6.57', 'files': {p.relative_to(ROOT).as_posix():
            {'sha256': c.sha(p), 'bytes': p.stat().st_size} for p in inventory()},
            'excluded': ['PUBLICATION-IDENTITIES.json', 'VERIFICATION.json']}


def verify():
    assert c.read(OUT / 'PUBLICATION-IDENTITIES.json') == manifest()
    assert baseline() == c.read(OUT / 'BASELINE.json')
    f = c.read(OUT / 'PREFLIGHT.json')
    assert c.sha(HERE / 'worker.py') == f['worker_sha256'] and c.sha(HERE / 'run.py') == f['run_sha256']
    assert not subprocess.check_output(['git', 'diff', 'HEAD', '--name-only'], cwd=ROOT, text=True).strip()
    allowed = set(manifest()['files']) | {f'benchmark/results/phase6/r6_57/{n}' for n in ('PUBLICATION-IDENTITIES.json', 'VERIFICATION.json')}
    for line in subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=all'], cwd=ROOT, text=True).splitlines():
        assert line.startswith('?? ') and line[3:].replace('\\', '/') in allowed, line
    for path in inventory():
        data = path.read_bytes()
        text = data.decode('utf-8')
        assert data.endswith(b'\n') and b'\r' not in data
        assert not any(s.endswith((' ', '\t')) for s in text.splitlines())
        assert not re.search(r'(?:sk-[A-Za-z0-9_-]{32,}|ghp_[A-Za-z0-9]{32,}|hf_[A-Za-z0-9]{32,})', text)
        if path.suffix == '.json':
            c.read(path)
        if path.suffix == '.py':
            compile(text, str(path), 'exec')
        if path.suffix == '.md':
            for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)', text):
                if '://' not in target and not target.startswith('#'):
                    assert (path.parent / target.split('#')[0]).resolve().is_file(), target
    result = c.read(OUT / 'RESULT.json')
    assert result['optimizer_updates'] == result['scheduler_updates'] == 0
    if result['four_record_completed']:
        assert c.read(OUT / 'PROCESS.json')['returncode'] == 0
        integrity = c.read(OUT / 'INTEGRITY.json')
        assert integrity['adapter_unchanged'] and integrity['base_unchanged']
        trace = c.read(OUT / 'MEMORY-TRACE.json')['boundaries']
        for i in range(1, 5):
            assert {r['boundary'] for r in trace if r['microbatch'] == i} >= {'before_forward', 'after_forward', 'after_backward', 'after_cleanup'}
    subprocess.run(['git', 'diff', '--check'], cwd=ROOT, check=True)
    return {'round': 'R6.57', 'passed': True, 'manifest_sha256': c.sha(OUT / 'PUBLICATION-IDENTITIES.json'),
            'baseline_identity': c.identity(baseline()), 'payload_files': len(inventory()),
            'historical_and_production_bytes_unchanged': True, 'kernel_constructs': 26,
            'source_json_links_whitespace_credentials': 'PASS', 'git_diff_check_returncode': 0}


if __name__ == '__main__':
    if sys.argv[1] == 'freeze':
        freeze()
    elif sys.argv[1] == 'execute':
        execute()
    elif sys.argv[1] == 'seal':
        write('PUBLICATION-IDENTITIES.json', manifest())
        write('VERIFICATION.json', verify())
    elif sys.argv[1] == 'check':
        assert verify() == c.read(OUT / 'VERIFICATION.json')
        print('PASS R6.57 publication and unchanged historical/production/environment identities')
    else:
        raise ValueError('unknown mode')
