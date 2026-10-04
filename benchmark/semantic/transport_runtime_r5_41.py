"""Prospective public entry: existing binder plus coherent durable domains."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile

if __package__:
    from benchmark.semantic import transport_runtime_r5_35 as helpers
    from benchmark.semantic import state_runtime_r5_41 as codec
    from benchmark.semantic import optional_support_r5_41 as support
else:
    import transport_helpers_r5_41 as helpers
    import state_runtime_r5_39 as codec
    import optional_support_r5_41 as support

canonical, sha = helpers.canonical, helpers.sha
snapshot, digest, bind, encode = helpers.snapshot, helpers.digest, helpers.bind, helpers.encode
FILES = ('transport_runtime_r5_35.py', 'transport_helpers_r5_41.py',
         'state_runtime_r5_39.py', 'optional_support_r5_41.py')


def load(root):
    profile = helpers.base.load(root)
    manifest = json.loads((root / 'boundary_provenance.json').read_bytes())
    if manifest != {'generation': profile['generation'], 'files': {
            name: sha((root / name).read_bytes()) for name in FILES}}:
        raise ValueError('stale or corrupt boundary artifact')
    return profile


def raw_arguments(argv, route):
    if len(argv) % 2:
        raise ValueError('unpaired arguments')
    raw = {}
    for flag, text in zip(argv[::2], argv[1::2]):
        if not flag.startswith('--'):
            raise ValueError('invalid argument')
        name = flag[2:]
        field = route['arguments'].get(name)
        value = support.public_value(text, field) if field else text
        if field and field['mode'] == 'repeat':
            raw.setdefault(name, []).append(value)
        elif name in raw:
            raise ValueError('duplicate single argument')
        else:
            raw[name] = value
    return raw


def main():
    state_name, trace, transport_trace, invocation, *argv = sys.argv[1:]
    root, state = Path(__file__).parent, Path(state_name)
    try:
        profile = load(root)
    except (ValueError, KeyError, OSError) as exc:
        print(json.dumps({'status': 'TRANSPORT_FAILURE', 'error': str(exc)}), file=sys.stderr)
        return 4
    before = snapshot(state)
    requested = argv[0] if argv else None
    entry = profile['operations'].get(requested)
    route, raw, binding, result, effective = None, None, None, None, before
    invoked, initialized, variant = False, False, None
    category, payload = 'transport_failure', {'code': 'unknown_public_operation'}
    if entry is not None:
        policy = profile['persistence']
        if before is None and policy['missing'] == 'INITIALIZE_DECLARED_STATE':
            effective = canonical(profile['state_profile']['initial'][policy['initial']]['value'])
            initialized = True
        decoded = codec.decode(effective, profile['state_profile']) if effective is not None else {
            'category': 'persistence_missing', 'variant': None}
        variant, category = decoded['variant'], decoded['category']
        if category is None:
            route = entry['alternatives'].get(variant)
            if route is None:
                category = 'invocation_failure'
        payload = {'code': category or 'unknown_public_operation'}
    if route is not None:
        try:
            raw = raw_arguments(argv[1:], route)
        except (ValueError, TypeError):
            category, payload = 'transport_failure', {'code': 'malformed_public_arguments'}
        else:
            binding = bind(route['semantic'], raw, route)
            if binding['failures']:
                category, payload = 'binding_failure', {'code': helpers.failure_code(route, binding)}
            else:
                with tempfile.TemporaryDirectory() as folder:
                    target = Path(folder) / 'state.json'
                    target.write_bytes(effective)
                    invoked = True
                    completed = subprocess.run([sys.executable, str(root / 'operation.py'), route['semantic'],
                        str(target), trace, invocation, json.dumps(binding['input']), profile['generation']],
                        capture_output=True, text=True)
                    result = {'stdout': completed.stdout, 'stderr': completed.stderr, 'exit': completed.returncode}
                    if completed.returncode:
                        category, payload = 'invocation_failure', {'code': 'generated_execution_rejected'}
                    else:
                        outcome = json.loads(completed.stdout)
                        semantic = json.loads(Path(trace).read_bytes())
                        post = codec.decode(target.read_bytes(), profile['state_profile'])
                        if (post['category'] is not None or
                                post['variant'] not in route['state_transition']['post']):
                            category, payload = 'persistence_invalid_state', {'code': 'persistence_invalid_state'}
                        else:
                            if semantic['attempted_write']:
                                state.write_bytes(target.read_bytes())
                            category, payload = outcome['kind'], outcome['value']
    descriptor = route['outcomes'][category] if route and category in route['outcomes'] else profile['failures'][category]
    document = json.dumps(encode(payload, category, descriptor), sort_keys=True) + '\n'
    stdout, stderr = (document, '') if descriptor['stream'] == 'stdout' else ('', document)
    after = snapshot(state)
    event = {'argv': argv, 'requested': requested, 'raw': raw,
        'operation': route['semantic'] if route else None, 'binding': binding,
        'semantic_invoked': invoked, 'semantic_result': result, 'category': category,
        'initialized': initialized, 'effective_pre': None if effective is None else effective.decode(),
        'invocation': invocation, 'generation': profile['generation'],
        'stdout': stdout, 'stderr': stderr, 'exit': descriptor['exit'], 'classification': descriptor['status'],
        'pre_digest': digest(before), 'post_digest': digest(after), 'state_variant': variant}
    Path(transport_trace).write_bytes(canonical(event))
    sys.stdout.write(stdout)
    sys.stderr.write(stderr)
    return descriptor['exit']


if __name__ == '__main__':
    sys.exit(main())
