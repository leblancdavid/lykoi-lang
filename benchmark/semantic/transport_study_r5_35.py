"""Independent acoustic calibration and specimen persistence boundary evidence."""

import copy
import json
from pathlib import Path
import sys
import tempfile

from benchmark.semantic import checked_transport_r5_35 as transport
from benchmark.semantic import current_pipeline as pipeline
from benchmark.semantic import evolution_study_r5_33 as evolution
from benchmark.semantic.refined_generator_r5_28 import canonical, sha


def ref(*path):
    return {'ref': list(path)}


def lit(value, shape):
    return {'literal': {'value': value, 'type': shape}}


def application():
    strings, integers = {'sequence': 'string'}, {'sequence': 'integer'}
    labels = {'fallback': {'value': ref('input', 'channels'), 'default': lit([], strings)}}
    samples = {'fallback': {'value': ref('input', 'samples'), 'default': lit([], integers)}}
    result = {'record': {'channels': strings, 'samples': integers, 'count': 'integer'}}
    normal = {'stable_unique': {'sequence': {'map': {'sequence': labels, 'transform': 'trim'}},
                                'equality': 'case_sensitive_string'}}
    yes = {'for_each': {'sequence': labels, 'bind': 'channel',
                        'property': {'nonblank': {'trim': ref('channel')}}}}
    operation = {'id': 'acoustic.calibrate', 'version': 'R5.27',
        'input': {'record': {'channels': {'optional': strings}, 'samples': {'optional': integers}}},
        'state': integers, 'branches': [
            {'tag': 'calibrated', 'when': yes, 'value': {'record': {
                'channels': normal, 'samples': samples, 'count': {'cardinality': samples}}},
             'value_type': result, 'transition': {'preserve': True}},
            {'tag': 'rejected', 'when': None, 'value': {'record': {'reason': lit('blank_channel', 'string')}},
             'value_type': {'record': {'reason': 'string'}}, 'transition': {'preserve': True}}]}
    return {'id': 'acoustic.calibration', 'state': integers, 'operations': {'calibrate': operation}}


def envelope(desc, name='data', success=True):
    desc['presentation'] = {'mode': 'object', 'coverage': 'full', 'fields': [
        {'name': 'ok', 'source': 'constant', 'type': 'boolean', 'value': success},
        {'name': name, 'source': 'payload', 'type': copy.deepcopy(desc['type']), 'path': []}]}


def specification(model):
    spec = transport.specification(pipeline.checked(model))
    route = spec['operations'][0]
    for argument in route['arguments']:
        argument['mode'], argument['representation'] = 'repeat', 'text'
    envelope(route['outcomes']['calibrated'])
    failure = route['outcomes']['rejected']
    failure['status'], failure['stream'], failure['exit'] = 'SEMANTIC_FAILURE', 'stderr', 1
    envelope(failure, 'error', False)
    route['argument_codes']['samples'] = {'malformed_scalar': 'invalid_sample'}
    json_route = copy.deepcopy(route)
    json_route['public'] = 'calibrate-json'
    for argument in json_route['arguments']:
        argument['mode'], argument['representation'] = 'collection', 'json'
    spec['operations'].append(json_route)
    return spec


def declaration_b(model):
    return transport.state_profile(model, {
        'origin': {'version': 'V1', 'value': evolution.initial(False)},
        'empty_v1': {'version': 'V1', 'value': {'revision': 1, 'specimens': [],
                    'metadata': {'collection': 'empty-declared-register'}}},
        'current_origin': {'version': 'V2', 'value': {'revision': 2, 'specimens': [],
                           'metadata': {'collection': 'current-declared-register'}}}})


def specification_b(model, initialize=True):
    spec = transport.specification(pipeline.checked(model))
    if initialize:
        spec['persistence'] = {'missing': 'INITIALIZE_DECLARED_STATE', 'initial': 'origin'}
    for route in spec['operations']:
        for desc in route['outcomes'].values():
            envelope(desc, 'result')
    return spec


def capture(model, root, spec, declaration, argv):
    event, semantic, public, before, after = transport.observe(root, argv)
    return {'event': event, 'semantic': semantic, 'public': public,
        'pre_bytes': None if before is None else before.decode(),
        'post_bytes': None if after is None else after.decode(),
        'verdict': transport.challenge(model, root, spec, declaration, event, semantic, public, before, after)}


FAULTS = {
    'A': ("            binding = bind(route['semantic'], raw, route)",
          "            raw = {k: list(reversed(v)) if isinstance(v, list) else v for k, v in raw.items()}\n            binding = bind(route['semantic'], raw, route)"),
    'B': ("            binding = bind(route['semantic'], raw, route)",
          "            raw = {k: list(dict.fromkeys(v)) if isinstance(v, list) else v for k, v in raw.items()}\n            binding = bind(route['semantic'], raw, route)"),
    'C': ("            binding = bind(route['semantic'], raw, route)",
          "            raw = {k: [x for x in v if x != 'bad'] if isinstance(v, list) else v for k, v in raw.items()}\n            binding = bind(route['semantic'], raw, route)"),
    'D': ("    visible = encode(payload, category, descriptor)",
          "    visible = {'ok': False, 'error': payload}"),
    'E': ("    visible = encode(payload, category, descriptor)",
          "    visible = encode(payload, category, descriptor)\n    visible.pop('data', None)"),
    'F': ("                        category = 'persistence_missing'",
          "                        state.write_bytes(canonical([]))\n                        category = 'persistence_missing'"),
    'G': ("                        initialized = True",
          "                        effective = canonical(profile['state_profile']['initial']['current_origin']['value'])\n                        initialized = True"),
    'H': ("    visible = encode(payload, category, descriptor)",
          "    visible = {'error': 'incorrect_public_report'}"),
    'stream': ("    stdout, stderr = (document, '') if descriptor['stream'] == 'stdout' else ('', document)",
               "    stdout, stderr = ('', document) if descriptor['stream'] == 'stdout' else (document, '')"),
    'exit': ("    after = snapshot(state)", "    descriptor = {**descriptor, 'exit': 7}\n    after = snapshot(state)"),
}


def fault(root, name):
    path = root / 'transport_runtime_r5_35.py'
    source = path.read_text(encoding='utf-8')
    old, new = FAULTS[name]
    if source.count(old) != 1:
        raise ValueError('fault injection drift: ' + name)
    path.write_bytes(source.replace(old, new).encode())
    transport.seal(root)


def study():
    model = application()
    spec, declaration = specification(model), transport.state_profile(model)
    cases = {
        'omitted': ['calibrate'], 'one': ['calibrate', '--channels', 'left'],
        'multiple': ['calibrate', '--channels', ' right ', '--channels', 'left', '--samples', '3', '--samples', '+1'],
        'duplicates_case': ['calibrate', '--channels', 'left', '--channels', 'left', '--channels', 'Left'],
        'malformed': ['calibrate', '--samples', '3', '--samples', 'bad', '--samples', '1'],
        'empty': ['calibrate-json', '--channels', '[]', '--samples', '[]'],
        'encoded': ['calibrate-json', '--channels', '[" right ","left","left","Left"]', '--samples', '[3,"1"]'],
        'semantic_failure': ['calibrate', '--channels', ' '],
        'malformed_collection': ['calibrate-json', '--samples', '3'],
        'unknown': ['calibrate', '--absent', 'x'], 'route': ['absent'],
        'grammar': ['calibrate', '--channels'],
    }
    report = {'version': 'R5.35', 'entry_point': 'benchmark.semantic.current_pipeline',
              'candidate_core_constructs': 30, 'A': {}, 'B': {}, 'faults': {}, 'mutations': {}}
    with tempfile.TemporaryDirectory() as folder:
        root = Path(folder)
        manifest = transport.generate(model, root, spec, declaration)
        (root / 'state.json').write_bytes(canonical([]))
        report['A'] = {'source': model, 'specification': spec, 'state_profile': declaration,
                       'manifest': manifest, 'calls': {name: capture(model, root, spec, declaration, argv) for name, argv in cases.items()}}
    model_b = evolution.application(False)
    spec_b, state_b = specification_b(model_b), declaration_b(model_b)
    with tempfile.TemporaryDirectory() as folder:
        root = Path(folder)
        manifest = transport.generate(model_b, root, spec_b, state_b)
        calls = [capture(model_b, root, spec_b, state_b, [name]) for name in (
            'legacy', 'legacy_insert', 'legacy', 'migrate', 'current', 'current_insert', 'current', 'legacy')]
        report['B'] = {'source': model_b, 'specification': spec_b, 'state_profile': state_b, 'manifest': manifest, 'calls': calls}
    for name, contents in [('require', None), ('invalid_json', b'{'), ('invalid_state', b'{}')]:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            checked_spec = specification_b(model_b, False)
            transport.generate(model_b, root, checked_spec, state_b)
            if contents is not None:
                (root / 'state.json').write_bytes(contents)
            report['B'][name] = capture(model_b, root, checked_spec, state_b, ['legacy'])
    for name in FAULTS:
        is_b = name in ('F', 'G', 'H')
        source, rule, state = (model_b, specification_b(model_b, name != 'F'), state_b) if is_b else (model, spec, declaration)
        argv = ['legacy_insert'] if name == 'H' else ['legacy'] if is_b else cases['malformed'] if name == 'C' else cases['duplicates_case']
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            transport.generate(source, root, rule, state)
            if not is_b:
                (root / 'state.json').write_bytes(canonical([]))
            fault(root, name)
            report['faults'][name] = capture(source, root, rule, state, argv)
    for name in ('argument_name', 'envelope_name', 'stream', 'status', 'missing_policy', 'initial_reference'):
        is_b = name in ('missing_policy', 'initial_reference')
        source, rule, state = (model_b, copy.deepcopy(spec_b), state_b) if is_b else (model, copy.deepcopy(spec), declaration)
        argv = ['legacy'] if is_b else list(cases['one'])
        if name == 'argument_name':
            rule['operations'][0]['arguments'][0]['public'] = 'channel'
            argv[1] = '--channel'
        elif name == 'envelope_name':
            rule['operations'][0]['outcomes']['calibrated']['presentation']['fields'][1]['name'] = 'reading'
        elif name == 'stream':
            rule['operations'][0]['outcomes']['calibrated']['stream'] = 'stderr'
        elif name == 'status':
            rule['operations'][0]['outcomes']['calibrated']['exit'] = 5
        elif name == 'missing_policy':
            rule['persistence'] = {'missing': 'REQUIRE_EXISTING', 'initial': None}
        elif name == 'initial_reference':
            rule['persistence']['initial'] = 'empty_v1'
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            transport.generate(source, root, rule, state)
            if not is_b:
                (root / 'state.json').write_bytes(canonical([]))
            call = capture(source, root, rule, state, argv)
            call['adapter_digest'] = sha((root / 'transport_runtime_r5_35.py').read_bytes())
            report['mutations'][name] = call
    locked = [
        'benchmark/semantic/checked_transport_r5_35.py',
        'benchmark/semantic/transport_runtime_r5_35.py',
        'benchmark/semantic/transport_study_r5_35.py',
        'benchmark/semantic/verify_transport_r5_35.py',
        'benchmark/harness/test_transport_boundary_r5_35.py',
        'benchmark/semantic/current_pipeline.py',
        'benchmark/semantic/checked_transport_r5_34.py',
        'benchmark/semantic/transport_runtime_r5_34.py',
        'benchmark/semantic/input_binding_r5_32.py',
        'benchmark/semantic/public_binding_r5_32.py',
        'benchmark/semantic/refined_runtime_r5_28.py',
        'benchmark/semantic/refined_generator_r5_28.py',
        'benchmark/semantic/refined_evidence_r5_28.py',
        'benchmark/semantic/unified_types_r5_27.py',
    ]
    report['implementation_lock'] = {'purpose': 'independent implementation locked before descriptive frozen comparison',
                                   'files': {name: sha(Path(name).read_bytes()) for name in locked}}
    return report


if __name__ == '__main__':
    report = study()
    if len(sys.argv) == 2:
        Path(sys.argv[1]).write_bytes(canonical(report) + b'\n')
        print(json.dumps({'A': len(report['A']['calls']), 'B': len(report['B']['calls']) + 3,
            'faults': {name: call['verdict'] for name, call in report['faults'].items()},
            'mutations': len(report['mutations'])}, sort_keys=True))
    else:
        print(json.dumps(report, indent=2))
