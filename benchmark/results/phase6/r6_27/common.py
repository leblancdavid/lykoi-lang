"""Experiment-local evidence utilities and frozen read-only imports."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
TEMP = Path(r'C:\Users\lblan\AppData\Local\Temp\opencode')

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def save(name, value):
    p = HERE / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')

def read(name):
    return json.loads((HERE / name).read_text(encoding='utf-8'))

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

tools = load('r627_frozen_tools', HERE.parent / 'r6_24/tools.py')
transport = load('r627_frozen_transport', HERE.parent / 'r6_25/transport.py')

def now():
    return datetime.now(timezone.utc).isoformat()
