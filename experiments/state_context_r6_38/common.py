"""Experiment-local helpers; never load credentials or alter execution semantics."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = ROOT / 'benchmark/results/phase6/r6_38'
TEMP = Path('C:/Users/lblan/AppData/Local/Temp/opencode/r6_38')
sys.path.insert(0, str(ROOT / 'experiments/lifecycle_r6_32'))
from lifecycle import Registry, Journal, c, digest


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, value):
    path = Path(path)
    assert path.parent.is_dir()
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(json.dumps(value, sort_keys=True, indent=2) + '\n')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def package(registry, pin):
    closure = registry.retrieve(pin=pin)
    return dict(version=c.VERSION, foundation=c.FOUNDATION,
        definitions=[d for d in closure if d['identity'] != pin],
        program=next(d for d in closure if d['identity'] == pin))


def normalize(value):
    if isinstance(value, bytes):
        return {'bytes_hex': value.hex()}
    if isinstance(value, dict):
        return {k: normalize(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [normalize(v) for v in value]
    return value
