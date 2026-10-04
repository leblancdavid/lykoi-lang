"""Checked local process bootstrap. No application AST or binding logic."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import uuid

if __package__:
    from benchmark.semantic import transport_runtime_r5_35 as transport
    from benchmark.semantic.refined_runtime_r5_28 import CAPABILITY_TYPES, CAPS_ENV, _typed
else:
    import transport_runtime_r5_35 as transport
    from refined_runtime_r5_28 import CAPABILITY_TYPES, CAPS_ENV, _typed

canonical, sha = transport.canonical, transport.sha
FILES = ('launch_runtime_r5_36.py', 'launch.json', 'capabilities.json')


def path_rule(policy):
    if (type(policy) is not dict or set(policy) != {'base', 'path', 'parent'} or
            policy['base'] != 'cwd' or policy['parent'] not in ('require_existing', 'create')):
        raise ValueError('invalid cwd path policy')
    text = policy['path']
    if (type(text) is not str or not text or any(c in text for c in '\\:\x00') or
            any(part in ('', '.', '..') for part in text.split('/')) or
            any(ord(c) < 32 for c in text) or
            any(part.endswith((' ', '.')) for part in text.split('/'))):
        raise ValueError('disallowed relative path')


def resolve(policy, cwd):
    path_rule(policy)
    return cwd.joinpath(*policy['path'].split('/')).resolve()


def validate(profile, boundary, manifest, requirements):
    if (type(profile) is not dict or set(profile) != {'version', 'id', 'application', 'generation',
            'provenance', 'transport', 'persistence', 'capabilities', 'store', 'trace', 'runtime', 'provider'} or
            profile['version'] != 'R5.36' or type(profile['id']) is not str or not profile['id']):
        raise ValueError('invalid launch profile')
    wanted = {'application': manifest['application'], 'generation': manifest['generation'],
              'provenance': sha(canonical(manifest)), 'transport': sha(canonical(boundary)),
              'persistence': sha(canonical({'policy': boundary['persistence'], 'state': boundary['state_profile']})),
              'capabilities': sha(canonical(requirements))}
    if any(profile[key] != value for key, value in wanted.items()):
        raise ValueError('stale application/transport/persistence/capability launch reference')
    if profile['runtime'] != 'current_pipeline.python.local.v1':
        raise ValueError('incompatible runtime profile')
    path_rule(profile['store'])
    if profile['store']['parent'] != 'require_existing':
        raise ValueError('store directory must already exist')
    if type(profile['trace']) is not dict or set(profile['trace']) != {'mode', 'directory'} or profile['trace']['mode'] != 'local_required':
        raise ValueError('incompatible trace configuration')
    path_rule(profile['trace']['directory'])
    store, trace = profile['store']['path'], profile['trace']['directory']['path']
    if store == trace or store.startswith(trace + '/') or trace.startswith(store + '/'):
        raise ValueError('overlapping state/evidence paths')
    provider = profile['provider']
    if (type(provider) is not dict or set(provider) != {'mode', 'types', 'values'} or
            provider['mode'] not in ('production', 'controlled_test') or provider['types'] != requirements or
            any(CAPABILITY_TYPES.get(name) != kind for name, kind in requirements.items())):
        raise ValueError('incompatible capability provider')
    values = provider['values']
    if provider['mode'] == 'production':
        if values != {}:
            raise ValueError('production provider cannot declare values')
    elif (type(values) is not dict or set(values) != set(requirements) or
            any(not _typed(values[name], kind) for name, kind in requirements.items())):
        raise ValueError('missing or incompatible controlled capability')


def load(root):
    boundary = transport.load(root)
    manifest = json.loads((root / 'provenance.json').read_bytes())
    requirements = json.loads((root / 'capabilities.json').read_bytes())
    profile = json.loads((root / 'launch.json').read_bytes())
    seal = json.loads((root / 'launch_provenance.json').read_bytes())
    if seal != {'generation': manifest['generation'], 'files': {name: sha((root / name).read_bytes()) for name in FILES}}:
        raise ValueError('stale or corrupt launch artifact')
    validate(profile, boundary, manifest, requirements)
    if boundary['version'] == 'R5.39' or (root / 'application_boundary.json').exists():
        aggregate = json.loads((root / 'application_boundary.json').read_bytes())
        aggregate_seal = json.loads((root / 'application_boundary_provenance.json').read_bytes())
        if (aggregate['version'] != 'R5.39' or
                set(aggregate) != {'version', 'schema', 'application', 'plans', 'artifact', 'transport', 'binding',
                                   'state', 'launch', 'provider', 'trace'} or
                aggregate['schema'] != sha(canonical({'version': 'R5.39', 'fields': ['application', 'plans', 'artifact',
                    'transport', 'binding', 'state', 'launch', 'provider', 'trace'], 'core_constructs': 30})) or
                aggregate_seal != {'generation': manifest['generation'], 'profile': sha(canonical(aggregate))} or
                aggregate['application'] != manifest['application'] or aggregate['artifact'] != manifest or
                aggregate['plans'] != manifest['units'] or aggregate['transport'] != boundary or
                aggregate['state'] != boundary['state_profile'] or aggregate['launch'] != profile or
                aggregate['provider'] != {'requirements': requirements, **profile['provider']} or
                aggregate['binding'] != {public: {variant: route['arguments'] for variant, route in entry.get('alternatives', {'state': entry}).items()}
                    for public, entry in boundary['operations'].items()} or
                aggregate['trace'] != {'application': manifest['application'], 'generation': manifest['generation'],
                    'provenance': sha(canonical(manifest)), 'policy': profile['trace']}):
            raise ValueError('incompatible aggregate application boundary')
    return profile


def main():
    root, cwd, argv = Path(__file__).resolve().parent, Path.cwd().resolve(), sys.argv[1:]
    try:
        profile = load(root)
        state = resolve(profile['store'], cwd)
        directory = resolve(profile['trace']['directory'], cwd)
        if not state.parent.is_dir() or state.is_dir():
            raise ValueError('store parent missing or store is a directory')
        if profile['trace']['directory']['parent'] == 'create':
            directory.mkdir(parents=True, exist_ok=True)
        if not directory.is_dir():
            raise ValueError('trace directory missing')
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print(json.dumps({'status': 'LAUNCH_FAILURE', 'error': str(exc)}), file=sys.stderr)
        return 4
    invocation = uuid.uuid4().hex
    identity = sha(canonical(profile))
    before = transport.snapshot(state)
    provider = profile['provider']
    env = {k: v for k, v in os.environ.items() if not k.upper().startswith('PYTHON')}
    env[CAPS_ENV] = json.dumps({'mode': 'real'} if provider['mode'] == 'production' else
                              {'mode': 'controlled', 'values': provider['values']})
    with tempfile.TemporaryDirectory() as folder:
        semantic, event = Path(folder) / 'semantic.json', Path(folder) / 'transport.json'
        completed = subprocess.run([sys.executable, '-E', str(root / 'transport_runtime_r5_35.py'),
            str(state), str(semantic), str(event), invocation, *argv], capture_output=True, text=True, env=env)
        evidence = {'version': 'R5.36', 'application': profile['application'], 'launch': identity,
            'profile_id': profile['id'], 'generation': profile['generation'], 'provenance': profile['provenance'],
            'transport_identity': profile['transport'], 'invocation': invocation, 'pid': os.getpid(),
            'executable': sys.executable, 'entry': str(root / 'launch_runtime_r5_36.py'),
            'argv': argv, 'cwd': str(cwd), 'store': str(state), 'trace_directory': str(directory),
            'pre_digest': transport.digest(before), 'post_digest': transport.digest(transport.snapshot(state)),
            'stdout': completed.stdout, 'stderr': completed.stderr, 'exit': completed.returncode,
            'transport': json.loads(event.read_bytes()) if event.exists() else None,
            'semantic': json.loads(semantic.read_bytes()) if semantic.exists() else None}
        with (directory / (invocation + '.json')).open('xb') as target:
            target.write(canonical(evidence))
    sys.stdout.write(completed.stdout)
    sys.stderr.write(completed.stderr)
    return completed.returncode


if __name__ == '__main__':
    sys.exit(main())
