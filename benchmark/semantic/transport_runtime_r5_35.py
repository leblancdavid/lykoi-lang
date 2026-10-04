"""R5.34 boundary extension: collections, public documents and persistence policy.

No semantic ASTs, domain defaults, normalization or state transitions here.
Missing state is staged from a checked declaration and materialized only on a
generated attempted write. Physical absence and effective semantic pre-state
are recorded separately. This is not a transactional persistence implementation.
"""

import json
from pathlib import Path
import subprocess
import sys
import tempfile

if __package__:
    from benchmark.semantic import transport_runtime_r5_34 as base
    from benchmark.semantic import input_binding_r5_32 as scalar
    from benchmark.semantic.refined_runtime_r5_28 import valid
else:
    import transport_runtime_r5_34 as base
    import input_binding_r5_32 as scalar
    from refined_runtime_r5_28 import valid

canonical, sha = base.canonical, base.sha
FILES = ('transport_runtime_r5_35.py',)


def load(root):
    profile = base.load(root)
    manifest = json.loads((root / 'boundary_provenance.json').read_bytes())
    if manifest != {'generation': profile['generation'], 'files': {
            name: sha((root / name).read_bytes()) for name in FILES}}:
        raise ValueError('stale or corrupt boundary artifact')
    return profile


def snapshot(path):
    return path.read_bytes() if path.exists() else None


def digest(data):
    return None if data is None else sha(data)


def raw_arguments(argv, route):
    if len(argv) % 2:
        raise ValueError('unpaired arguments')
    raw = {}
    for flag, text in zip(argv[::2], argv[1::2]):
        if not flag.startswith('--'):
            raise ValueError('invalid argument')
        name = flag[2:]
        field = route['arguments'].get(name)
        value = json.loads(text) if field and field['representation'] == 'json' else text
        if field and field['mode'] == 'repeat':
            raw.setdefault(name, []).append(value)
        elif name in raw:
            raise ValueError('duplicate single argument')
        else:
            raw[name] = value
    return raw


def bind(operation, raw, route):
    """Every collection element uses the unchanged R5.32 scalar binder."""
    slots, inp, failures = {}, {}, []
    for name in sorted(set(raw) - set(route['arguments'])):
        failures.append(scalar.failure(name, None, None, 'unknown_argument'))
    for name, field in sorted(route['arguments'].items()):
        slot = field['slot']
        if name not in raw:
            slots[slot] = {'supplied': False, 'state': 'OMITTED'}
            if not field['optional']:
                failures.append(scalar.failure(name, slot, field['type'], 'missing_required'))
            continue
        sequence = isinstance(field['type'], dict) and 'sequence' in field['type']
        values = raw[name] if sequence else [raw[name]]
        if type(values) is not list:
            slots[slot] = {'supplied': True, 'state': 'BINDING_FAILED'}
            failures.append(scalar.failure(name, slot, field['type'], 'malformed_scalar'))
            continue
        element_type = field['type']['sequence'] if sequence else field['type']
        metadata = {'operations': {operation: {name: {'slot': slot, 'type': element_type,
            'optional': False, 'domain': field['domain']}}}}
        decoded, element_failures = [], []
        for index, value in enumerate(values):
            result = scalar.bind(operation, json.dumps({name: value}), metadata)
            for error in result['failures']:
                element_failures.append({**error, **({'index': index} if sequence else {})})
            if not result['failures']:
                decoded.append(result['input'][slot])
        slots[slot] = {'supplied': True, 'state': 'BINDING_FAILED' if element_failures else 'BOUND_TYPED'}
        failures.extend(element_failures)
        if not element_failures:
            inp[slot] = decoded if sequence else decoded[0]
    return {'slots': slots, 'input': None if failures else inp, 'failures': failures}


def encode(payload, kind, descriptor):
    if not valid(payload, descriptor['type']):
        raise ValueError('public payload violates checked type')
    presentation = descriptor['presentation']
    if presentation['mode'] == 'direct':
        return payload
    visible = {}
    for field in presentation['fields']:
        source = field['source']
        value = field.get('value') if source == 'constant' else kind if source == 'kind' else payload
        for key in field.get('path', []):
            value = value[key]
        visible[field['name']] = value
    return visible


def failure_code(route, binding):
    error = binding['failures'][0]
    return route['argument_codes'].get(error['argument'], {}).get(
        error['category'], route['error_codes'][error['category']])


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
    route = profile['operations'].get(requested)
    raw, binding, result, effective = None, None, None, None
    invoked, initialized = False, False
    category, payload = 'transport_failure', {'code': 'unknown_public_operation'}
    if route is not None:
        try:
            raw = raw_arguments(argv[1:], route)
        except (ValueError, TypeError):
            payload = {'code': 'malformed_public_arguments'}
        else:
            binding = bind(route['semantic'], raw, route)
            if binding['failures']:
                category, payload = 'binding_failure', {'code': failure_code(route, binding)}
            else:
                policy = profile['persistence']
                category = None
                if before is None:
                    if policy['missing'] == 'REQUIRE_EXISTING':
                        category = 'persistence_missing'
                    else:
                        effective = canonical(profile['state_profile']['initial'][policy['initial']]['value'])
                        initialized = True
                else:
                    effective = before
                if category is None:
                    try:
                        pre = json.loads(effective)
                    except ValueError:
                        category = 'persistence_invalid_json'
                    else:
                        if not any(valid(pre, shape) for shape in profile['state_profile']['versions'].values()):
                            category = 'persistence_invalid_state'
                if category is not None:
                    payload = {'code': category}
                else:
                    # Staging supplies declared semantic pre-state without equating
                    # physical absence with an empty collection or creating a store
                    # for a read. Only the generated operation decides to write.
                    with tempfile.TemporaryDirectory() as folder:
                        target = Path(folder) / 'state.json' if initialized else state
                        if initialized:
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
                            if initialized and semantic['attempted_write']:
                                state.write_bytes(target.read_bytes())
                            category, payload = outcome['kind'], outcome['value']
    descriptor = route['outcomes'][category] if route and category in route['outcomes'] else profile['failures'][category]
    visible = encode(payload, category, descriptor)
    document = json.dumps(visible, sort_keys=True) + '\n'
    stdout, stderr = (document, '') if descriptor['stream'] == 'stdout' else ('', document)
    after = snapshot(state)
    event = {'argv': argv, 'requested': requested, 'raw': raw,
        'operation': route['semantic'] if route else None, 'binding': binding,
        'semantic_invoked': invoked, 'semantic_result': result, 'category': category,
        'initialized': initialized, 'effective_pre': None if effective is None else effective.decode(),
        'invocation': invocation, 'generation': profile['generation'],
        'stdout': stdout, 'stderr': stderr, 'exit': descriptor['exit'], 'classification': descriptor['status'],
        'pre_digest': digest(before), 'post_digest': digest(after)}
    Path(transport_trace).write_bytes(canonical(event))
    sys.stdout.write(stdout)
    sys.stderr.write(stderr)
    return descriptor['exit']


if __name__ == '__main__':
    sys.exit(main())
