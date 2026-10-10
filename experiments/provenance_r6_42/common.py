"""R6.42 evidence helpers; no production or historical writes."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = ROOT / 'benchmark/results/phase6/r6_42'
sys.path.insert(0, str(ROOT / 'experiments/typed_composition_r6_18'))
import composition as c


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n')


def serial(value):
    if type(value) is bytes:
        return {'bytes_hex': value.hex()}
    if type(value) in (list, tuple):
        return [serial(v) for v in value]
    if type(value) is dict:
        return {k: serial(v) for k, v in value.items()}
    return value


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()


def verify_files(files):
    for name, record in files.items():
        expected = record if type(record) is str else record['sha256']
        assert sha(ROOT / name) == expected, name
    return len(files)


def verify_freeze():
    return verify_files(read(OUT / 'FREEZE.json')['files'])
