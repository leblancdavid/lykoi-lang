"""Round-local evidence I/O; historical paths are read-only."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = ROOT / 'benchmark/results/phase6/r6_43'
OLD = ROOT / 'benchmark/results/phase6/r6_42'


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                   allow_nan=False).encode('utf-8')).hexdigest()


def save(name, value):
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / name).open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n')


def verify(files):
    for name, record in files.items():
        expected = record if isinstance(record, str) else record['sha256']
        assert sha(ROOT / name) == expected, name
    return len(files)


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()


def serial(value):
    if isinstance(value, bytes):
        return {'bytes_hex': value.hex()}
    if isinstance(value, (tuple, list)):
        return [serial(v) for v in value]
    if isinstance(value, dict):
        return {k: serial(v) for k, v in value.items()}
    return value
