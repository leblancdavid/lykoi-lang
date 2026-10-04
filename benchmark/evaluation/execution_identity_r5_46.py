"""Closed-fixture execution identity; production dependency closure is unqualified.

No benchmark loader or production authorization entry exists here. Caller-supplied
component descriptions are trusted fixture inputs, not runtime attestation.
"""

import hashlib
import hmac
import os
from pathlib import Path
import platform
import subprocess
import sys

from benchmark.evaluation import preexposure_r5_45 as prior
from benchmark.evaluation.recorder_r5_43 import ProtocolFailure, canonical, digest

PROTOCOL = 'lykoi-execution-identity-r5.46-synthetic'


def private_identity(key, domain, value):
    if type(key) is not bytes or len(key) < 32:
        raise ProtocolFailure('private identity requires an external 256-bit key')
    return hmac.new(key, canonical([PROTOCOL, domain, value]), hashlib.sha256).hexdigest()


def environment(values, material, sensitive, key):
    if not set(sensitive) <= set(material):
        raise ProtocolFailure('sensitive variable missing from material policy')
    result = {}
    for name in sorted(material):
        if name not in values:
            result[name] = {'present': False}
        elif name in sensitive:
            result[name] = {'present': True, 'hmac': private_identity(key, name, values[name])}
        else:
            result[name] = {'present': True, 'value': values[name]}
    return result


def git(root, *arguments):
    process = subprocess.run(['git', *arguments], cwd=root, capture_output=True, timeout=10)
    if process.returncode:
        raise ProtocolFailure('Git identity capture failed')
    return process.stdout


def repository(root, key, excluded=()):
    """Physical bytes plus effective Git inputs; no raw configuration is persisted.

    This broad fixture identity does not claim minimal Git dependency slicing.
    Ancestry output binds effective replacement/shallow traversal, not just HEAD.
    """
    root = Path(root).resolve()
    config = subprocess.run(['git', 'config', '--null', '--list'], cwd=root,
                            capture_output=True, timeout=10)
    if config.returncode:
        raise ProtocolFailure('Git configuration unavailable')
    index = git(root, 'ls-files', '--stage', '-z')
    if b'160000 ' in index:
        raise ProtocolFailure('submodule closure is not qualified')
    return prior.seal({'files': prior.tree(root, excluded),
                       'head': git(root, 'rev-parse', 'HEAD').decode().strip(),
                       'ancestry': digest(git(root, 'rev-list', '--parents', 'HEAD')),
                       'index': digest(index),
                       'config': private_identity(key, 'git-config', config.stdout.hex()),
                       'exclusions': sorted(excluded)})


def runtime():
    """Observed interpreter descriptor, explicitly not native-library closure."""
    return {'implementation': sys.implementation.name, 'version': sys.version,
            'cache_tag': sys.implementation.cache_tag,
            'executable': digest(Path(sys.executable).read_bytes()),
            'flags': {name: getattr(sys.flags, name) for name in dir(sys.flags)
                      if not name.startswith('_') and type(getattr(sys.flags, name)) is int},
            'xoptions': dict(sys._xoptions), 'platform': platform.system(),
            'os_version': platform.version(), 'machine': platform.machine(),
            'filesystem_encoding': sys.getfilesystemencoding(),
            'filesystem_errors': sys.getfilesystemencodeerrors()}


def dependencies(resolved, required):
    """Hash exact implementation bytes, not declaration ranges or version alone."""
    if set(resolved) != set(required):
        raise ProtocolFailure('missing or unexpected relevant dependency')
    result = {}
    for name in sorted(required):
        version, path = resolved[name]
        path = Path(path)
        if not path.is_file() or path.is_symlink() or type(version) is not str or not version:
            raise ProtocolFailure('resolved dependency unavailable')
        result[name] = {'version': version, 'implementation': digest(path.read_bytes())}
    return result


def compose(repo, interpreter, resolved, env, tools, context, unknown=()):
    prior.unseal(repo)
    return prior.seal({'protocol': PROTOCOL, 'scope': 'synthetic-only',
                       'repository': repo, 'runtime': interpreter,
                       'dependencies': resolved, 'environment': env,
                       'tools': tools, 'context': context, 'unknown': sorted(unknown)})


def validate_state(value):
    body = prior.unseal(value)
    required = {'protocol', 'scope', 'repository', 'runtime', 'dependencies',
                'environment', 'tools', 'context', 'unknown'}
    if (set(body) != required or body['protocol'] != PROTOCOL or
            body['scope'] != 'synthetic-only' or body['unknown']):
        raise ProtocolFailure('execution identity is incomplete or outside qualified scope')
    prior.unseal(body['repository'])
    return body


def bridge(value):
    validate_state(value)
    return prior.seal({'protocol': prior.PROTOCOL,
                       'execution_protocol': PROTOCOL, 'execution': value})


def stage(before, after, name, result, mechanism):
    validate_state(before)
    validate_state(after)
    if canonical(before) != canonical(after):
        raise ProtocolFailure('state changed during verification; no reusable PASS')
    return prior.stage(bridge(before)['identity'], name, 'PASS', result, mechanism)


def assemble(frozen, evidence, policy):
    if policy.get('purpose') != 'synthetic-only':
        raise ProtocolFailure('production certificate integration is unqualified')
    return prior.assemble(bridge(frozen), evidence, policy)


def validate(certificate, frozen, evidence, policy, current):
    assemble(frozen, evidence, policy)
    return prior.validate(certificate, bridge(frozen), evidence, policy, bridge(current))


def authorize(certificate, frozen, evidence, policy, capture, recorder, callback):
    """Fresh capture at the boundary; exclusive fixture ownership is required.

    This cannot detect an ABA mutation or lock mutable external dependencies.
    It is equality checking, not an atomic capture-and-execute primitive.
    """
    current = capture()
    validate(certificate, frozen, evidence, policy, current)
    return prior.synthetic_authorize(certificate, bridge(frozen), evidence, policy,
                                     bridge(current), recorder, callback)
