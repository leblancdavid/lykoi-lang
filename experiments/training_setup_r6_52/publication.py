"""Additive publication seal, read-only inherited/model/adapter/stack checks."""
import importlib.metadata
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from setup import ROOT, OUT, STORE, PYTHON, sha, write, run

HERE = Path(__file__).resolve().parent
MANIFEST = OUT / 'PUBLICATION-IDENTITIES.json'
RECEIPT = OUT / 'VERIFICATION.json'


def baseline():
    sys.path.insert(0, str(ROOT / 'experiments/training_infrastructure_r6_51'))
    from convert import seal_check
    result = seal_check()
    previous = ROOT / 'benchmark/results/phase6/r6_51'
    manifest = json.loads((previous / 'PUBLICATION-IDENTITIES.json').read_text())
    receipt = json.loads((previous / 'VERIFICATION.json').read_text())
    assert sha(previous / 'PUBLICATION-IDENTITIES.json') == receipt['manifest_sha256']
    for name, record in manifest['files'].items():
        p = ROOT / name
        assert sha(p) == record['sha256'] and p.stat().st_size == record['bytes'], name
    result['r6_51_manifest_sha256'] = sha(previous / 'PUBLICATION-IDENTITIES.json')
    result['r6_51_payload_files'] = len(manifest['files'])
    return result


def external():
    checkpoint = json.loads((OUT / 'CHECKPOINT.json').read_text())
    for name, record in checkpoint['files'].items():
        assert sha(STORE / 'checkpoint' / name) == record['sha256']
    backward = json.loads((OUT / 'BACKWARD.json').read_text())
    for name, record in backward['saved_adapter_files'].items():
        assert sha(STORE / 'untrained-adapter' / name) == record['sha256']
    return {'checkpoint_files': len(checkpoint['files']), 'adapter_files': len(backward['saved_adapter_files'])}


def package_identity():
    records = {}
    for d in importlib.metadata.distributions():
        name = d.metadata['Name']
        files = {}
        tree = hashlib.sha256()
        checked = 0
        for f in sorted(d.files or [], key=str):
            p = Path(d.locate_file(f))
            if not p.is_file():
                raise ValueError('missing installed file: ' + str(p))
            digest = sha(p)
            tree.update(str(f).encode() + b'\0' + digest.encode() + b'\n')
            if f.hash and f.hash.mode == 'sha256':
                expected = base64.urlsafe_b64encode(bytes.fromhex(digest)).decode().rstrip('=')
                assert expected == f.hash.value, str(p)
                checked += 1
            if str(f).endswith(('.dist-info/RECORD', '.dist-info/METADATA', '.dist-info/WHEEL')):
                files[str(f)] = digest
        records[name] = {'version': d.version, 'metadata_hashes': files,
                         'installed_record_tree_sha256': tree.hexdigest(), 'record_file_hashes_checked': checked}
    return records


def environment_identity():
    groups = {}
    distinct = set()
    total_unique = 0
    for folder in STORE.iterdir():
        if not folder.is_dir():
            continue
        size = 0
        count = 0
        for p in folder.rglob('*'):
            if p.is_file():
                s = p.stat()
                size += s.st_size
                count += 1
                key = (s.st_dev, s.st_ino)
                if key not in distinct:
                    total_unique += s.st_size
                    distinct.add(key)
        groups[folder.name] = {'logical_bytes': size, 'file_count': count}
    import shutil
    write('STORAGE.json', {'groups': groups, 'distinct_file_bytes': total_unique,
          'note': 'logical lengths with hardlink identities deduplicated, not allocated filesystem clusters; root loose files excluded',
          'free_bytes_on_store_volume': shutil.disk_usage(STORE).free})
    python_home = STORE / 'python/cpython-3.12.11-windows-x86_64-none'
    write('ENVIRONMENT-IDENTITIES.json', {'packages': package_identity(),
          'python_executable_sha256': sha(python_home / 'python.exe'),
          'python_dll_sha256': sha(python_home / 'python312.dll'),
          'venv_executable_sha256': sha(PYTHON),
          'uv_executable_sha256': sha(STORE / 'uv/uv.exe'), 'requirements_lock_sha256': sha(OUT / 'requirements-lock.txt')})


def inventory():
    paths = [ROOT / 'benchmark/results/phase6/R6_52-REPORT.md']
    paths += [ROOT / f'docs/{name}-r6.52.md' for name in ('project-overview', 'research-log', 'decisions')]
    for folder in (HERE, OUT):
        paths += [p for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p not in (MANIFEST, RECEIPT)]
    return sorted(paths)


def manifest():
    return {'round': 'R6.52', 'baseline': baseline(),
          'files': {p.relative_to(ROOT).as_posix(): {'sha256': sha(p), 'bytes': p.stat().st_size} for p in inventory()},
          'excluded': [MANIFEST.name, RECEIPT.name], 'head_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()}


def verify():
    saved = json.loads(MANIFEST.read_text())
    assert saved == manifest(), 'publication identity mismatch'
    counts = external()
    assert package_identity() == json.loads((OUT / 'ENVIRONMENT-IDENTITIES.json').read_text())['packages']
    assert not subprocess.check_output(['git', 'diff', '--name-only'], cwd=ROOT, text=True).strip()
    allowed = set(saved['files']) | {p.relative_to(ROOT).as_posix() for p in (MANIFEST, RECEIPT)}
    status = subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=all'], cwd=ROOT, text=True)
    for line in status.splitlines():
        assert line.startswith('?? ') and line[3:].replace('\\', '/') in allowed, line
    links = 0
    for p in inventory():
        data = p.read_bytes()
        text = data.decode('utf-8')
        assert not data or data.endswith(b'\n')
        assert b'\r' not in data and not any(s.endswith((' ', '\t')) for s in text.splitlines()), str(p)
        assert not re.search(r'(?:sk-[A-Za-z0-9_-]{32,}|ghp_[A-Za-z0-9]{32,}|hf_[A-Za-z0-9]{32,})', text)
        if p.suffix == '.json':
            json.loads(text)
        if p.suffix == '.py':
            compile(text, str(p), 'exec')
        if p.suffix == '.md':
            for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)', text):
                if '://' not in target and not target.startswith('#'):
                    resolved = (p.parent / target.split('#')[0]).resolve()
                    assert resolved.is_relative_to(ROOT) and (resolved.exists() or resolved == RECEIPT), target
                    links += 1
    p = subprocess.run(['git', 'diff', '--check'], cwd=ROOT, capture_output=True, text=True)
    assert p.returncode == 0
    for name in ('INVENTORY', 'ASSETS', 'TOKENIZE', 'BACKWARD', 'RELOAD', 'MASK-CONTROLS'):
        assert json.loads((OUT / (name + '-PROCESS.json')).read_text())['returncode'] == 0
    assert json.loads((OUT / 'LOSS-MASK.json').read_text())['status'] == 'PASS'
    b = json.loads((OUT / 'BACKWARD.json').read_text())
    a = json.loads((OUT / 'ADAPTER-RELOAD.json').read_text())
    assert b['optimizer_steps'] == b['parameter_updates'] == 0 and a['parameters_exactly_preserved']
    tests = json.loads((OUT / 'R6_51-CONVERTER-TESTS.json').read_text())
    assert tests['returncode'] == 0 and 'Ran 8 tests' in tests['stderr']
    return {'round': 'R6.52', 'classification': 'R6_52_TRAINING_ENVIRONMENT_QUALIFIED',
          'passed': True, 'manifest_sha256': sha(MANIFEST), **saved['baseline'], **counts,
          'publication_payload_files': len(saved['files']), 'relative_links_checked': links,
          'git_diff_check_returncode': 0, 'tracked_diff_empty': True, 'preservation_failures': [],
          'optimizer_steps': 0, 'parameter_updates': 0, 'fine_tuning_runs': 0,
          'historical_acceptance_executions': 0, 'P6_A05_content_access': False,
          'cuda_backward_tests': 2, 'adapter_reload': 'PASS', 'record_mask_controls': 10,
          'twenty_step_training_executed': False}


if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'environment':
        environment_identity()
    elif mode == 'baseline':
        write('BASELINE.json', baseline())
    elif mode == 'tests':
        run('R6_51-CONVERTER-TESTS', [sys.executable, '-m', 'unittest', 'discover', '-s',
            'experiments/training_infrastructure_r6_51', '-p', 'test_convert.py', '-v'])
    elif mode == 'seal':
        write(MANIFEST.name, manifest())
        write(RECEIPT.name, verify())
    elif mode == 'check':
        result = verify()
        assert result == json.loads(RECEIPT.read_text())
        print(json.dumps(result, sort_keys=True))
