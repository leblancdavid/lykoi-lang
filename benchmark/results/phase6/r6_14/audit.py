"""Write-once R6.14 baseline, freeze and preservation checks."""
import datetime
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
VM = ROOT / 'experiments/semantic_interpreter'
OLD = HERE.parent / 'r6_13'


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def save(path, value):
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(json.dumps(value, indent=2) + '\n')


def verify_map(base, files):
    for name, identity in files.items():
        if sha(base / name) != identity:
            raise ValueError('Identity mismatch: ' + name)


def verify():
    verify_map(ROOT, load(HERE / 'BASELINE.json')['preserved'])
    if load(ROOT / 'benchmark/results/phase5c/R5_114-KERNEL-ACCOUNTING.json')['final_count'] != 26:
        raise ValueError('kernel changed')


def baseline():
    verify_map(ROOT, load(OLD / 'BASELINE.json')['preserved'])
    verify_map(ROOT, load(OLD / 'PUBLICATION-IDENTITIES.json')['files'])
    publication = load(VM / 'PUBLICATION-IDENTITIES.json')['publication_sha256']
    vm_key = 'experiments/semantic_interpreter/interpreter.py'
    assert sha(VM / 'interpreter.py') == publication[vm_key]
    verify_map(OLD, load(OLD / 'PROBE-FREEZE.json')['files'])
    inputs = load(OLD / 'PROBE-INPUTS.json')
    evidence = load(OLD / 'PROBE-RESULTS-2.json')
    assert evidence['inputs_sha256'] == sha(OLD / 'PROBE-INPUTS.json')
    # Preserve the exact historical witness as data, without reauthoring it.
    witness = inputs['vm_nibble_xor']
    sys.path.insert(0, str(VM))
    import interpreter as vm
    assert vm.validate(witness) == 21
    results = []
    for a in range(16):
        for b in range(16):
            result = vm.execute(witness, bytes([a, b]))
            assert result['value'] == a ^ b and result['output'] == bytes([a ^ b])
            results.append(result['work'])
    save(HERE / 'NIBBLE-WITNESS.plan.json', witness)
    preserved = dict(load(OLD / 'BASELINE.json')['preserved'])
    for folder in (OLD, VM):
        for path in sorted(folder.rglob('*')):
            if path.is_file() and '__pycache__' not in path.parts:
                preserved[path.relative_to(ROOT).as_posix()] = sha(path)
    report = HERE.parent / 'R6_13-REPORT.md'
    preserved[report.relative_to(ROOT).as_posix()] = sha(report)
    save(HERE / 'BASELINE.json', dict(utc=now(), preserved=preserved,
        vm_sha256=sha(VM / 'interpreter.py'), historical_vm_identity_verified=True,
        historical_probe_freeze_verified=True, nibble_nodes=21, nibble_pairs_passed=256,
        nibble_work_min=min(results), nibble_work_max=max(results),
        limits=vm.DEFAULT_LIMITS, static_limits=dict(nodes=64, depth=16, expressions=2048),
        initial_status=subprocess.check_output(['git','status','--short'], cwd=ROOT,text=True),
        head=subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT,text=True).strip(),
        python=sys.version, platform=platform.platform(), kernel=26))
    save(HERE / 'SPEC-FREEZE.json', dict(utc=now(), files={name:sha(HERE/name)
        for name in ('PROTOCOL.md','audit.py','BASELINE.json','NIBBLE-WITNESS.plan.json')}))
    print('Baseline and specifications frozen:', len(preserved), 'preserved identities; 21-node witness 256/256')


if __name__ == '__main__':
    {'baseline':baseline, 'verify':verify}[sys.argv[1]]()
