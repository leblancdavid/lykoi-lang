"""Non-task standalone launch witnesses, disposable faults and metadata changes."""

import copy
import json
import os
from pathlib import Path
import sys
import tempfile

from benchmark.semantic import checked_launch_r5_36 as launch
from benchmark.semantic import checked_transport_r5_35 as transport
from benchmark.semantic import current_pipeline as pipeline
from benchmark.semantic import evolution_study_r5_33 as evolution
from benchmark.semantic import transport_study_r5_35 as prior
from benchmark.semantic.refined_generator_r5_28 import canonical, sha


def application_a():
    model = prior.application()
    model['id'] = 'acoustic.public.station'
    shape = {'record': {'identity': 'string', 'observed': 'instant'}}
    model['operations']['stamp'] = {'id': 'acoustic.stamp', 'version': 'R5.27',
        'input': {'record': {}}, 'state': model['state'], 'branches': [
            {'tag': 'stamped', 'when': {'equals': [prior.lit(1, 'integer'), prior.lit(1, 'integer')]}, 'value': {'record': {
                'identity': {'external': {'source': 'fresh_unique_id'}},
                'observed': {'external': {'source': 'utc_clock'}}}},
             'value_type': shape, 'transition': {'preserve': True}},
            {'tag': 'unavailable', 'when': None, 'value': prior.lit('unavailable', 'string'),
             'value_type': 'string', 'transition': {'preserve': True}}]}
    return model


def setup_a():
    model = application_a()
    spec = prior.specification(model)
    declaration = transport.state_profile(model, {'origin': {'version': 'state', 'value': []}})
    spec['persistence'] = {'missing': 'INITIALIZE_DECLARED_STATE', 'initial': 'origin'}
    config = launch.configuration('acoustic.public')
    config['provider']['types'] = launch.requirements(model)
    return model, spec, declaration, config


def setup_b(require=False):
    model = evolution.application(False)
    return model, prior.specification_b(model, not require), prior.declaration_b(model), launch.configuration('specimen.public')


def capture(model, root, cwd, spec, declaration, config, argv, environment=None):
    evidence, public, before, after = launch.observe(root, cwd, config, argv, environment)
    return {'evidence': evidence, 'public': public, 'pre_bytes': None if before is None else before.decode(),
        'post_bytes': None if after is None else after.decode(),
        'verdict': launch.challenge(model, root, spec, declaration, config, evidence, public, before, after)}


FAULTS = {
    'B': ("        state = resolve(profile['store'], cwd)", "        state = cwd / 'other-register.json'"),
    'C': ("'profile_id': profile['id']", "'profile_id': 'different.application.profile'"),
    'D': ("        profile = load(root)", "        if not argv or argv[0] != '--research-helper':\n            raise ValueError('hidden research helper required')\n        profile = load(root)"),
    'F': ("    invocation = uuid.uuid4().hex", "    argv = argv[1:]\n    invocation = uuid.uuid4().hex"),
}


def inject(root, name):
    if name in ('A', 'E'):
        path = root / 'launch.json'
        changed = json.loads(path.read_bytes())
        if name == 'A':
            changed['application'] = 'stale.application'
        else:
            changed['provider']['types']['utc_clock'] = 'integer'
        path.write_bytes(canonical(changed))
    else:
        path = root / 'launch_runtime_r5_36.py'
        source = path.read_text(encoding='utf-8')
        old, new = FAULTS[name]
        if source.count(old) != 1:
            raise ValueError('launch fault injection drift: ' + name)
        path.write_bytes(source.replace(old, new).encode())
    launch.seal(root)


def study():
    report = {'version': 'R5.36', 'candidate_core_constructs': 30,
        'entry_point': 'benchmark.semantic.current_pipeline', 'A': {}, 'B': {}, 'faults': {}, 'mutations': {}, 'paths': {}}
    for label, setup, commands in [
        ('A', setup_a(), [['calibrate'], ['calibrate', '--channels', ' left ', '--channels', 'left', '--samples', '3'],
                          ['calibrate-json', '--samples', '[]'], ['stamp'], ['calibrate', '--samples', 'bad']]),
        ('B', setup_b(), [[name] for name in ('legacy', 'legacy_insert', 'legacy', 'migrate', 'current', 'current_insert', 'current', 'legacy')])]:
        model, spec, declaration, config = setup
        with tempfile.TemporaryDirectory() as bundle, tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            root = Path(bundle)
            profile = launch.generate(model, root, spec, declaration, config)
            report[label] = {'source': model, 'specification': spec, 'state_profile': declaration, 'config': config,
                'profile': profile, 'calls': [capture(model, root, Path(first), spec, declaration, config, argv) for argv in commands],
                'changed_cwd': capture(model, root, Path(second), spec, declaration, config, commands[0])}
    for name, require in [('require_existing', True), ('initialize_read', False)]:
        model, spec, declaration, config = setup_b(require)
        with tempfile.TemporaryDirectory() as bundle, tempfile.TemporaryDirectory() as folder:
            root, cwd = Path(bundle), Path(folder)
            launch.generate(model, root, spec, declaration, config)
            report['paths'][name] = capture(model, root, cwd, spec, declaration, config, ['legacy'])
    for name in ('nested', 'missing_parent', 'trace_require_missing'):
        model, spec, declaration, config = setup_b()
        config['store']['path'] = 'durable/archive/register.json'
        if name == 'trace_require_missing':
            config['trace']['directory']['parent'] = 'require_existing'
        with tempfile.TemporaryDirectory() as bundle, tempfile.TemporaryDirectory() as folder:
            root, cwd = Path(bundle), Path(folder)
            launch.generate(model, root, spec, declaration, config)
            if name != 'missing_parent':
                (cwd / 'durable/archive').mkdir(parents=True)
            report['paths'][name] = capture(model, root, cwd, spec, declaration, config, ['legacy_insert'])
    model, spec, declaration, config = setup_a()
    with tempfile.TemporaryDirectory() as bundle, tempfile.TemporaryDirectory() as folder:
        root, cwd = Path(bundle), Path(folder)
        launch.generate(model, root, spec, declaration, config)
        environment = {**os.environ, 'LYKOI_R5_22_CAPS': json.dumps({'mode': 'controlled', 'values': {
            'fresh_unique_id': 'ambient-intrusion', 'utc_clock': '1900-01-01T00:00:00Z'}}),
            'LYKOI_STORE': 'ignored.json', 'LYKOI_TRACE': 'ignored-trace', 'PYTHONPATH': 'nonexistent-python-path'}
        report['paths']['environment_isolation'] = capture(model, root, cwd, spec, declaration, config, ['stamp'], environment)
    for name in ('A', 'B', 'C', 'D', 'E', 'F'):
        model, spec, declaration, config = setup_a() if name == 'E' else setup_b()
        with tempfile.TemporaryDirectory() as bundle, tempfile.TemporaryDirectory() as folder:
            root, cwd = Path(bundle), Path(folder)
            launch.generate(model, root, spec, declaration, config)
            inject(root, name)
            report['faults'][name] = capture(model, root, cwd, spec, declaration, config,
                                            ['stamp'] if name == 'E' else ['legacy_insert'])
            report['faults'][name]['unexpected_store_exists'] = (cwd / 'other-register.json').exists()
    for name in ('store', 'trace', 'profile_id', 'persistence_reference', 'transport_reference', 'controlled_provider'):
        model, spec, declaration, config = setup_b() if name == 'store' else setup_a()
        with tempfile.TemporaryDirectory() as bundle, tempfile.TemporaryDirectory() as folder:
            root, cwd = Path(bundle), Path(folder)
            original = launch.generate(model, root, spec, declaration, config)
            original_artifact = sha((root / 'operation.py').read_bytes())
            changed = copy.deepcopy(config)
            if name == 'store':
                changed['store']['path'] = 'alternate-register.json'
            elif name == 'trace':
                changed['trace']['directory']['path'] = 'alternate-evidence'
            elif name == 'profile_id':
                changed['id'] = 'acoustic.alternate'
            elif name == 'controlled_provider':
                changed['provider']['mode'] = 'controlled_test'
                changed['provider']['values'] = {'fresh_unique_id': 'controlled-acoustic', 'utc_clock': '2031-02-03T04:05:06Z'}
            metadata = launch.profile(changed, json.loads((root / 'transport.json').read_bytes()),
                json.loads((root / 'provenance.json').read_bytes()), launch.requirements(model))
            if name in ('persistence_reference', 'transport_reference'):
                metadata['persistence' if name == 'persistence_reference' else 'transport'] = 'incompatible.reference'
            (root / 'launch.json').write_bytes(canonical(metadata))
            launch.seal(root)
            call = capture(model, root, cwd, spec, declaration, changed, ['legacy_insert'] if name == 'store' else ['stamp'])
            call['launcher_digest'] = sha((root / 'launch_runtime_r5_36.py').read_bytes())
            call['artifact_digest'] = sha((root / 'operation.py').read_bytes())
            call['original_artifact_digest'] = original_artifact
            call['original_profile'] = original
            report['mutations'][name] = call
    return report


def lock():
    files = [str(p).replace('\\', '/') for p in Path('benchmark/semantic').glob('*.py')]
    files += ['benchmark/harness/test_public_launch_r5_36.py']
    return {'purpose': 'implementation complete before descriptive frozen comparison',
            'files': {name: sha(Path(name).read_bytes()) for name in sorted(files)}}


if __name__ == '__main__':
    report = study()
    report['implementation_lock'] = lock()
    if len(sys.argv) == 2:
        Path(sys.argv[1]).write_bytes(canonical(report) + b'\n')
        print(json.dumps({'normal': 21, 'faults': {k: v['verdict'] for k, v in report['faults'].items()},
                          'mutations': len(report['mutations'])}, sort_keys=True))
    else:
        print(json.dumps(report, indent=2))
