"""Prospective staged evidence; no benchmark loader or dispatch entry point."""

from pathlib import Path
import os
import subprocess
import sys
import time

from benchmark.evaluation.recorder_r5_43 import (
    PROTOCOL as CANONICAL_PROTOCOL, ProtocolFailure, canonical, digest, loads, persist)

PROTOCOL = 'lykoi-preexposure-r5.45'
STATUSES = ('PASS', 'FAIL', 'INCOMPLETE')


def seal(body):
    body = loads(canonical(body))
    return {**body, 'identity': digest(canonical(body))}


def unseal(value):
    if type(value) is not dict or 'identity' not in value:
        raise ProtocolFailure('missing identity')
    body = {k: v for k, v in value.items() if k != 'identity'}
    if value['identity'] != digest(canonical(body)):
        raise ProtocolFailure('altered evidence')
    return body


def tree(root, excluded=()):
    """Hash physical bytes, including ignored/untracked files and membership."""
    root = Path(root).resolve()
    result = {}
    for directory, dirs, files in os.walk(root, followlinks=False):
        parent = Path(directory)
        for name in list(dirs):
            path = parent / name
            relative = path.relative_to(root).as_posix()
            if path.is_symlink():
                raise ProtocolFailure('linked directory is outside the state model')
            if relative in excluded or name == '.git':
                dirs.remove(name)
        for name in sorted(files):
            path = parent / name
            relative = path.relative_to(root).as_posix()
            if relative in excluded:
                continue
            if path.is_symlink() or not path.is_file():
                raise ProtocolFailure('nonregular state input')
            result[relative] = digest(path.read_bytes())
    return dict(sorted(result.items()))


def state(root, configuration, excluded=()):
    return seal({'protocol': PROTOCOL, 'files': tree(root, excluded),
                 'configuration': configuration, 'exclusions': sorted(excluded)})


def stage(state_identity, name, status, result, mechanism):
    if status not in STATUSES:
        raise ProtocolFailure('invalid stage status')
    return seal({'protocol': PROTOCOL, 'state': state_identity, 'stage': name,
                 'status': status, 'result': result, 'mechanism': mechanism})


def check_stage(value, frozen, name, policy):
    body = unseal(value)
    if set(body) != {'protocol', 'state', 'stage', 'status', 'result', 'mechanism'}:
        raise ProtocolFailure('invalid stage envelope')
    if (body['protocol'] != PROTOCOL or body['state'] != frozen['identity'] or
            body['stage'] != name or body['mechanism'] != policy['stages'][name] or
            body['status'] != 'PASS'):
        raise ProtocolFailure('stage missing, stale, mixed, unqualified or not PASS')
    if type(body['result']) is not dict or body['result'].get('successful') is not True:
        raise ProtocolFailure('stage does not establish its guarantee')
    return body


def assemble(frozen, evidence, policy):
    unseal(frozen)
    if frozen['protocol'] != PROTOCOL or set(evidence) != set(policy['stages']):
        raise ProtocolFailure('incomplete verification set')
    for name, value in evidence.items():
        check_stage(value, frozen, name, policy)
    result = evidence['identity']['result']
    if (type(result.get('semantic_count')) is not int or
            result['semantic_count'] != policy['semantic_count'] or
            result.get('recorder') != policy['recorder'] or
            result.get('canonical_protocol') != policy['canonical_protocol'] or
            result.get('authority') != policy['authority']):
        raise ProtocolFailure('semantic, authority or qualified protocol mismatch')
    return seal({'protocol': PROTOCOL, 'state': frozen['identity'], 'status': 'PASS',
                 'policy': digest(canonical(policy)),
                 'stages': {name: evidence[name]['identity'] for name in sorted(evidence)},
                 'assembly': 'complete qualified verification set; no exposure authority'})


def validate(certificate, frozen, evidence, policy, current):
    unseal(certificate)
    if canonical(current) != canonical(frozen):
        raise ProtocolFailure('state changed after verification')
    expected = assemble(frozen, evidence, policy)
    if canonical(expected) != canonical(certificate):
        raise ProtocolFailure('invalid certificate')
    return True


def reload(path):
    content = Path(path).read_bytes()
    value = loads(content)
    if content != canonical(value) + b'\n':
        raise ProtocolFailure('noncanonical persisted evidence')
    unseal(value)
    return value


def bounded(command, cwd, environment, seconds):
    """Parent records timeout as INCOMPLETE, never reconstructs a PASS."""
    started = time.monotonic()
    try:
        process = subprocess.run(command, cwd=cwd, env=environment,
                                 capture_output=True, text=True, timeout=seconds)
        status = 'PASS' if process.returncode == 0 else 'FAIL'
        result = {'successful': status == 'PASS', 'exit': process.returncode,
                  'stdout': process.stdout, 'stderr': process.stderr}
    except subprocess.TimeoutExpired:
        status = 'INCOMPLETE'
        result = {'successful': False, 'reason': 'execution envelope exceeded'}
    return status, {**result, 'elapsed_seconds': round(time.monotonic() - started, 6),
                    'allowed_seconds': seconds, 'command': command}


def synthetic_authorize(certificate, frozen, evidence, policy, current, recorder, callback):
    """Qualification-only boundary, deliberately limited to synthetic policy."""
    if policy.get('purpose') != 'synthetic-only':
        raise ProtocolFailure('this entry authorizes synthetic qualification only')
    validate(certificate, frozen, evidence, policy, current)
    recorder.open_run()
    recorder.integrity()
    if recorder.counts()['disposition'] != 'zero':
        raise ProtocolFailure('one synthetic observation only')
    if recorder.read('baseline')['evidence'] != {'certificate': certificate['identity']}:
        raise ProtocolFailure('recorder not bound to certificate')
    return recorder.observe(callback)
