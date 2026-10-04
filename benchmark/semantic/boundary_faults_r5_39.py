"""Disposable infrastructure faults challenged by independent physical observation."""

import copy
import json
from pathlib import Path
import tempfile

from benchmark.semantic import boundary_study_r5_39 as study
from benchmark.semantic import application_boundary_r5_39 as boundary
from benchmark.semantic import checked_transport_r5_35 as transport
from benchmark.semantic import checked_launch_r5_36 as launch
from benchmark.semantic.refined_generator_r5_28 import canonical, sha


def faults():
    app, spec, state, config = study.setup()
    report = {}
    for name in 'ABCDEFGHIJKL':
        app, spec, state, config = study.setup()
        if name == 'D':
            spec['operations'][0]['alternatives']['V1']['arguments'][0]['representation'] = 'json'
        with tempfile.TemporaryDirectory() as bundle, tempfile.TemporaryDirectory() as directory:
            root, cwd = Path(bundle), Path(directory)
            boundary.generate(app, root, spec, state, config)
            store = cwd / config['store']['path']
            if name in 'ABCD':
                store.write_bytes(canonical({'revision': 1, 'seeds': []}))
                argv = ['query', '--filter', {'A': 'null', 'B': '"bad"', 'C': '"3"', 'D': 'null'}[name]]
                target = root / 'transport_runtime_r5_35.py'
                source = target.read_text(encoding='utf-8')
                if name == 'A':
                    injection = "    if raw.get('filter', 1) is None:\n        raw = {k: v for k, v in raw.items() if k != 'filter'}\n"
                elif name in 'BC':
                    injection = "    if 'filter' in raw:\n        raw = {**raw, 'filter': None}\n"
                else:
                    # Null to non-nullable code; false binder returns a typed null.
                    argv = ['create', '--code', 'null', '--label', 'Iris']
                    injection = "    if raw.get('code') is None:\n        return {'slots': {'code': {'supplied': True, 'state': 'BOUND_TYPED'}, 'label': {'supplied': True, 'state': 'BOUND_TYPED'}, 'harvest': {'supplied': False, 'state': 'OMITTED'}}, 'input': {'code': None, 'label': raw['label']}, 'failures': []}\n"
                source = source.replace('    slots, inp, failures = {}, {}, []', injection + '    slots, inp, failures = {}, {}, []', 1)
                target.write_bytes(source.encode())
            elif name in 'EFGH':
                content = {'revision': 1, 'seeds': []} if name in 'EGH' else {'revision': 2, 'seeds': []}
                store.write_bytes(canonical(content))
                argv = ['migrate'] if name == 'G' else ['query']
                profile_path = root / 'transport.json'
                profile = json.loads(profile_path.read_bytes())
                route = profile['operations']['query']['alternatives']
                if name == 'E':
                    route['V1'] = copy.deepcopy(route['V2'])
                elif name == 'F':
                    route['V2'] = copy.deepcopy(route['V1'])
                elif name == 'G':
                    profile['operations']['migrate']['alternatives']['V1'] = copy.deepcopy(route['V1'])
                else:
                    profile['state_profile']['alternatives']['V1']['codec'] = copy.deepcopy(study.V2)
                profile_path.write_bytes(canonical(profile))
                # Honest integrity reseal does not make the substituted profile authoritative.
                manifest = json.loads((root / 'provenance.json').read_bytes())
                config_launch = launch.profile(config, profile, manifest, {})
                (root / 'launch.json').write_bytes(canonical(config_launch))
                aggregate = json.loads((root / 'application_boundary.json').read_bytes())
                aggregate['transport'], aggregate['launch'] = profile, config_launch
                aggregate['state'] = profile['state_profile']
                aggregate['binding'] = {p: {v: r['arguments'] for v, r in e['alternatives'].items()}
                    for p, e in profile['operations'].items()}
                (root / 'application_boundary.json').write_bytes(canonical(aggregate))
                (root / 'application_boundary_provenance.json').write_bytes(canonical({
                    'generation': manifest['generation'], 'profile': sha(canonical(aggregate))}))
                launch.seal(root)
            else:
                invalid = {'revision': 2, 'seeds': [{'code': 'S1', 'label': 'Iris'}]}
                if name in 'IK':
                    invalid['seeds'] = [{'code': 'S1', 'label': 'Iris', 'storage': 'dry'}, 3]
                store.write_bytes(canonical(invalid))
                argv = ['query']
                target = root / 'state_runtime_r5_39.py'
                source = target.read_text(encoding='utf-8')
                if name in 'IJ':
                    injection = "    value = json.loads(data)\n    return {'category': None, 'variant': 'V2', 'value': value}\n"
                    source = source.replace('def decode(data, profile):\n', 'def decode(data, profile):\n' + injection)
                else:
                    # K drops an invalid element; L fills an undeclared missing field.
                    target = root / 'transport_runtime_r5_35.py'
                    source = target.read_text(encoding='utf-8')
                    repaired = "{'revision': 2, 'seeds': [{'code': 'S1', 'label': 'Iris', 'storage': 'dry'}]}"
                    source = source.replace("        variant = decoded['variant']", "        state.write_bytes(canonical(" + repaired + "))\n        effective = state.read_bytes()\n        decoded = state_codec.decode(effective, profile['state_profile'])\n        variant = decoded['variant']", 1)
                target.write_bytes(source.encode())
            transport.seal(root)
            call = study.capture(app, root, cwd, spec, state, config, argv)
            report[name] = call
    return report
