"""Authorized isolated native setup. No training or optimizer operations."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(os.environ.get('LYKOI_R6_52_OUT', str(ROOT / 'benchmark/results/phase6/r6_52')))
STORE = Path(os.environ.get('LYKOI_R6_52_STORE', r'C:\Users\lblan\AppData\Local\Temp\opencode\lykoi-r6-52'))
PYTHON = STORE / 'venv/Scripts/python.exe'


def write(name, value):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n', encoding='utf-8', newline='\n')


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def run(name, args, timeout=1200):
    start = time.perf_counter()
    env = dict(os.environ, UV_CACHE_DIR=str(STORE / 'uv-cache'), PYTHONDONTWRITEBYTECODE='1',
               HF_HUB_DISABLE_TELEMETRY='1', HF_HOME=str(STORE / 'hf-cache'))
    p = subprocess.run([str(a) for a in args], cwd=ROOT, env=env, capture_output=True, text=True, timeout=timeout)
    write(name + '.json', {'argv': [str(a) for a in args], 'returncode': p.returncode,
                           'stdout': p.stdout, 'stderr': p.stderr, 'seconds': time.perf_counter() - start})
    print(name, p.returncode, p.stdout, p.stderr, flush=True)
    if p.returncode:
        raise RuntimeError(name + ' failed; diagnostic retained')
    return p


def bootstrap():
    STORE.mkdir(parents=True, exist_ok=True)
    url = 'https://github.com/astral-sh/uv/releases/download/0.8.22/uv-x86_64-pc-windows-msvc.zip'
    archive = STORE / 'uv-0.8.22.zip'
    urllib.request.urlretrieve(url, archive)
    with zipfile.ZipFile(archive) as z:
        z.extractall(STORE / 'uv')
    uv = STORE / 'uv/uv.exe'
    write('BOOTSTRAP.json', {'uv_version': '0.8.22', 'url': url, 'archive_sha256': sha(archive),
                           'executable_sha256': sha(uv), 'store': str(STORE),
                           'system_python_modified': False, 'wsl_installed': False})
    run('PYTHON-INSTALL', [uv, 'python', 'install', '3.12.11', '--install-dir', STORE / 'python'])
    run('VENV-CREATE', [uv, 'venv', '--python', STORE / 'python/cpython-3.12.11-windows-x86_64-none/python.exe', STORE / 'venv'])
    run('TORCH-INSTALL', [uv, 'pip', 'install', '--python', PYTHON, '--index-url',
                         'https://download.pytorch.org/whl/cu128', 'torch==2.7.1+cu128'])
    packages = ['transformers==4.55.4', 'peft==0.17.1', 'trl==0.21.0', 'accelerate==1.10.1',
                'bitsandbytes==0.47.0', 'datasets==4.0.0', 'tokenizers==0.21.4', 'safetensors==0.6.2']
    lock = ROOT / 'benchmark/results/phase6/r6_52/requirements-lock.txt'
    # Initial installation resolved transitive dependencies; publication freezes all47.
    # Subsequent setup uses that exact lock rather than re-resolving transitives.
    selection = ['-r', lock] if lock.exists() else packages
    run('STACK-INSTALL', [uv, 'pip', 'install', '--python', PYTHON, *selection])
    run('PACKAGE-CHECK', [uv, 'pip', 'check', '--python', PYTHON])
    frozen = run('PACKAGE-FREEZE', [uv, 'pip', 'freeze', '--python', PYTHON])
    (OUT / 'requirements-lock.txt').write_text(frozen.stdout, encoding='utf-8', newline='\n')


if __name__ == '__main__':
    bootstrap()
