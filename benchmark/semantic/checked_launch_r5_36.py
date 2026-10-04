"""Launch metadata assembly and independent public-process observation/challenge."""

import copy
import json
import os
from pathlib import Path
import subprocess
import sys

from benchmark.semantic import checked_transport_r5_35 as transport
from benchmark.semantic import current_pipeline as pipeline
from benchmark.semantic import launch_runtime_r5_36 as runtime
from benchmark.semantic.refined_generator_r5_28 import canonical, sha


def configuration(identity='local.public', store='register.json', trace='evidence'):
    return {'id': identity, 'store': {'base': 'cwd', 'path': store, 'parent': 'require_existing'},
            'trace': {'mode': 'local_required', 'directory': {'base': 'cwd', 'path': trace, 'parent': 'create'}},
            'runtime': 'current_pipeline.python.local.v1', 'provider': {'mode': 'production', 'types': {}, 'values': {}}}


def requirements(application):
    found = {}
    for plan in pipeline.checked(application).values():
        for name, kind in plan.capabilities.items():
            if name in found and found[name] != kind:
                raise ValueError('incompatible capability requirements')
            found[name] = kind
    return found


def profile(config, boundary, manifest, capabilities):
    if type(config) is not dict or set(config) != {'id', 'store', 'trace', 'runtime', 'provider'}:
        raise ValueError('invalid launch configuration')
    result = {'version': 'R5.36', **copy.deepcopy(config), 'application': manifest['application'],
        'generation': manifest['generation'], 'provenance': sha(canonical(manifest)),
        'transport': sha(canonical(boundary)),
        'persistence': sha(canonical({'policy': boundary['persistence'], 'state': boundary['state_profile']})),
        'capabilities': sha(canonical(capabilities))}
    runtime.validate(result, boundary, manifest, capabilities)
    return result


def seal(root):
    manifest = json.loads((root / 'provenance.json').read_bytes())
    (root / 'launch_provenance.json').write_bytes(canonical({'generation': manifest['generation'],
        'files': {name: sha((root / name).read_bytes()) for name in runtime.FILES}}))


def generate(application, root, spec, declaration, config):
    manifest = transport.generate(application, root, spec, declaration)
    caps = requirements(application)
    boundary = transport.profile(application, spec, declaration, manifest)
    checked = profile(config, boundary, manifest, caps)
    (root / 'launch.json').write_bytes(canonical(checked))
    (root / 'capabilities.json').write_bytes(canonical(caps))
    (root / runtime.FILES[0]).write_bytes(Path(runtime.__file__).read_bytes())
    seal(root)
    return checked


def expected_paths(config, cwd):
    # Independent interpretation of the checked portable slash policy.
    base = Path(cwd).absolute()
    return ((base / config['store']['path']).resolve(),
            (base / config['trace']['directory']['path']).resolve())


def observe(root, cwd, config, argv, environment=None):
    state, directory = expected_paths(config, cwd)
    previous = set(directory.glob('*.json')) if directory.is_dir() else set()
    before = transport.runtime.snapshot(state)
    command = [sys.executable, '-E', str(root / runtime.FILES[0]), *argv]
    process = subprocess.Popen(command, cwd=cwd, env=environment, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate(timeout=30)
    created = set(directory.glob('*.json')) - previous if directory.is_dir() else set()
    evidence = json.loads(next(iter(created)).read_bytes()) if len(created) == 1 else None
    public = {'command': command, 'argv': argv, 'cwd': str(Path(cwd).resolve()), 'pid': process.pid,
              'stdout': stdout, 'stderr': stderr, 'exit': process.returncode,
              'evidence_files': [str(p) for p in sorted(created)]}
    return evidence, public, before, transport.runtime.snapshot(state)


def challenge(application, root, spec, declaration, config, evidence, public, before, after):
    verdict = {'LAUNCH_PROFILE_CONFORMANT': False, 'launch_grounded': False, 'TRANSPORT_CONFORMANT': None,
        'INPUT_BINDING_CONFORMANT': None, 'PERSISTENCE_BOUNDARY_CONFORMANT': None,
        'SEMANTIC_EXECUTION_CONFORMANT': None, 'OUTPUT_CONFORMANT': None}
    try:
        manifest = json.loads((root / 'provenance.json').read_bytes())
        boundary = transport.profile(application, spec, declaration, manifest)
        authority = profile(config, boundary, manifest, requirements(application))
        verdict['LAUNCH_PROFILE_CONFORMANT'] = (runtime.load(root) == authority and
            manifest['application'] == sha(canonical(application)))
        if not verdict['LAUNCH_PROFILE_CONFORMANT'] or evidence is None:
            return verdict
        state, directory = expected_paths(config, public['cwd'])
        invocation = evidence['invocation']
        grounded = (evidence['application'] == authority['application'] and evidence['launch'] == sha(canonical(authority)) and
            evidence['profile_id'] == authority['id'] and evidence['generation'] == authority['generation'] and
            evidence['provenance'] == authority['provenance'] and evidence['transport_identity'] == authority['transport'] and
            evidence['store'] == str(state) and evidence['trace_directory'] == str(directory) and
            evidence['entry'] == str(root / runtime.FILES[0]) and evidence['executable'] == sys.executable and
            public['command'] == [sys.executable, '-E', str(root / runtime.FILES[0]), *public['argv']] and
            public['evidence_files'] == [str(directory / (invocation + '.json'))] and
            all(evidence[k] == public[k] for k in ('argv', 'cwd', 'pid', 'stdout', 'stderr', 'exit')) and
            evidence['pre_digest'] == transport.runtime.digest(before) and evidence['post_digest'] == transport.runtime.digest(after))
        verdict['launch_grounded'] = grounded
        if not grounded:
            return verdict
        observed = {**public, 'invocation': invocation}
        child = transport.challenge(application, root, spec, declaration, evidence['transport'], evidence['semantic'], observed, before, after)
        verdict['TRANSPORT_CONFORMANT'] = (child['TRANSPORT_PROFILE_CONFORMANT'] and child['transport_grounded'] and
                                            child['TRANSPORT_BINDING_CONFORMANT'])
        for key in ('INPUT_BINDING_CONFORMANT', 'PERSISTENCE_BOUNDARY_CONFORMANT', 'SEMANTIC_EXECUTION_CONFORMANT', 'OUTPUT_CONFORMANT'):
            verdict[key] = child[key]
        if evidence['semantic'] is not None:
            logged = evidence['semantic']['externals']
            selected = config['provider']
            if selected['mode'] == 'controlled_test' and any(selected['values'].get(k) != v for k, v in logged.items()):
                verdict['LAUNCH_PROFILE_CONFORMANT'] = False
    except (ValueError, TypeError, KeyError, OSError):
        pass
    return verdict
