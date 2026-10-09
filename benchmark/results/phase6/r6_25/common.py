"""R6.25 experiment-owned evidence utilities and read-only historical imports."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1048576), b''):
            h.update(block)
    return h.hexdigest()

def now():
    return datetime.now(timezone.utc).isoformat()

def save(name, value):
    p = HERE / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, indent=2, default=lambda x: {'bytes_hex': x.hex()} if isinstance(x, bytes) else str(x)) + '\n', encoding='utf-8')

def read(name):
    return json.loads((HERE / name).read_text(encoding='utf-8'))

def historical(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

tools = historical('r625_readonly_tools', HERE.parent / 'r6_24/tools.py')

def historical_runner():
    # Frozen source stays byte-identical. Only its module-local evidence directory
    # and seed are rebound for the successor's experiment-owned provider harness.
    sys.modules['tools'] = tools
    sys.modules['baseline'] = historical('r625_readonly_baseline', HERE.parent / 'r6_24/baseline.py')
    m = historical('r625_provider_harness', HERE.parent / 'r6_24/run.py')
    m.HERE = HERE
    m.OPTIONS = dict(m.OPTIONS, seed=625)
    return m
