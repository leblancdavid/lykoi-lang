"""R6.26 evidence and read-only imports; no semantic changes."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def now():
    return datetime.now(timezone.utc).isoformat()

def save(name, value):
    p = HERE / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, indent=2, default=lambda x: {'bytes_hex': x.hex()} if isinstance(x, bytes) else str(x)) + '\n', encoding='utf-8')

def read(name):
    return json.loads((HERE / name).read_text(encoding='utf-8'))

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

tools = load('r626_frozen_tools', HERE.parent / 'r6_24/tools.py')
transport = load('r626_frozen_transport', HERE.parent / 'r6_25/transport.py')
sys.modules['tools'] = tools
sys.modules['baseline'] = load('r626_frozen_baseline', HERE.parent / 'r6_24/baseline.py')
runner = load('r626_frozen_evaluator', HERE.parent / 'r6_24/run.py')
