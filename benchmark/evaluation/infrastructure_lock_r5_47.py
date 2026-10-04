"""Deterministic successor byte lock; no execution-identity qualification."""

from pathlib import Path

from benchmark.evaluation.recorder_r5_43 import canonical, digest, loads


def manifest(root, names, metadata):
    root = Path(root)
    files = {}
    for name in sorted(set(names)):
        path = root / name
        if path.is_symlink() or not path.is_file() or '..' in Path(name).parts or Path(name).is_absolute():
            raise ValueError('nonregular or invalid lock member')
        files[name] = digest(path.read_bytes())
    body = {**metadata, 'files': files}
    return {**body, 'identity': digest(canonical(body))}


def verify(root, lock):
    body = {k: v for k, v in lock.items() if k != 'identity'}
    if digest(canonical(body)) != lock['identity']:
        raise ValueError('successor identity mismatch')
    reproduced = manifest(root, lock['files'], {k: v for k, v in body.items() if k != 'files'})
    if reproduced != lock:
        raise ValueError('successor member mismatch')
    return {'valid': True, 'members': len(lock['files']), 'identity': lock['identity']}


def reload(path):
    return loads(Path(path).read_bytes())
