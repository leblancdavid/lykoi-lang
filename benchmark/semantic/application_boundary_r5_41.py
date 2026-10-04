"""Prospective optional-boundary policy using the existing aggregate schema."""

from pathlib import Path

from benchmark.semantic import application_boundary_r5_39 as historical
from benchmark.semantic import checked_transport_r5_41 as transport
from benchmark.semantic import checked_transport_r5_35 as old_transport
from benchmark.semantic import checked_launch_r5_36 as launch
from benchmark.semantic import current_pipeline as pipeline
from benchmark.semantic import optional_support_r5_41 as support
from benchmark.semantic import state_runtime_r5_41 as codec
from benchmark.semantic.refined_generator_r5_28 import canonical, sha

SCHEMA = {'version': 'R5.41', 'aggregate': historical.SCHEMA, 'core_constructs': 30,
          'composition': 'nullable-underlying-decoder; optional-present-domain'}
SCHEMA_ID = sha(canonical(SCHEMA))


def check_state(application, declaration):
    # Historical structural checks are reusable; initial content must be checked
    # by the prospective codec, rather than the historically defective one.
    historical.check_state(application, {**declaration, 'initial': {}})
    for desc in declaration['alternatives'].values():
        for rule in desc['constraints']:
            if rule['kind'] == 'population':
                fields = historical.shape_at(desc['codec'], rule['path'])['sequence']['record']
                for field, domain in rule['domains'].items():
                    if not support.domain_supported(fields[field], domain):
                        raise ValueError('unsupported present-value domain composition')
    for item in declaration['initial'].values():
        if (set(item) != {'version', 'value'} or item['version'] not in declaration['versions'] or
                codec.decode(canonical(item['value']), declaration)['variant'] != item['version']):
            raise ValueError('initial state content/alternative mismatch')


def validate(application, plans, spec, declaration):
    check_state(application, declaration)
    if set(spec) != {'operations', 'failures', 'persistence'}:
        raise ValueError('invalid alternative transport specification')
    routes, covered = {}, set()
    for route in spec['operations']:
        if set(route) != {'public', 'alternatives'} or route['public'] in routes or not route['alternatives']:
            raise ValueError('invalid/duplicate alternative route')
        choices = {}
        for variant, item in route['alternatives'].items():
            if variant not in declaration['alternatives']:
                raise ValueError('route references missing state alternative')
            one = {**spec, 'operations': [{**item, 'public': route['public']}]}
            checked = transport.validate(application, plans, one, historical.legacy_state(declaration))[route['public']]
            if checked['applicability']['pre'] != declaration['versions'][variant]:
                raise ValueError('operation dispatched using incompatible state codec')
            targets = [name for name, shape in declaration['versions'].items() if shape == checked['applicability']['post']]
            if not targets:
                raise ValueError('migration target has no state alternative')
            checked['state_transition'] = {'pre': variant, 'post': targets}
            choices[variant] = checked
            covered.add(item['semantic'])
        routes[route['public']] = {'alternatives': choices}
    if covered != set(plans):
        raise ValueError('public boundary omits CheckedPlan operation')
    return routes


def transport_profile(application, spec, declaration, manifest):
    plans = pipeline.checked(application)
    return {'version': 'R5.39', 'id': application['id'], 'application': sha(canonical(application)),
            'generation': manifest['generation'], 'units': {name: plan.digest for name, plan in plans.items()},
            'operations': validate(application, plans, spec, declaration), 'state_profile': declaration,
            'persistence': spec['persistence'], 'failures': spec['failures']}


def aggregate(application, spec, declaration, config, manifest):
    boundary = transport_profile(application, spec, declaration, manifest)
    if manifest['application'] != boundary['application'] or ('units' in manifest and manifest['units'] != boundary['units']):
        raise ValueError('stale semantic application/CheckedPlan artifact identity')
    caps = launch.requirements(application)
    launched = launch.profile(config, boundary, manifest, caps)
    return {'version': 'R5.39', 'schema': historical.SCHEMA_ID, 'application': sha(canonical(application)),
            'plans': boundary['units'], 'artifact': manifest, 'transport': boundary,
            'binding': {public: {variant: route['arguments'] for variant, route in entry['alternatives'].items()}
                        for public, entry in boundary['operations'].items()},
            'state': declaration, 'launch': launched, 'provider': {'requirements': caps, **config['provider']},
            'trace': {'application': manifest['application'], 'generation': manifest['generation'],
                      'provenance': sha(canonical(manifest)), 'policy': config['trace']}}


def generate(application, root, spec, declaration, config):
    aggregate(application, spec, declaration, config, {'application': sha(canonical(application)), 'generation': 'static'})
    manifest = pipeline.generate(application, root)
    profile = aggregate(application, spec, declaration, config, manifest)
    (root / 'transport.json').write_bytes(canonical(profile['transport']))
    # Preserve compatibility filenames at public launch; every byte is sealed.
    from benchmark.semantic import transport_runtime_r5_41 as runtime
    directory = Path(__file__).parent
    copies = {'transport_runtime_r5_35.py': 'transport_runtime_r5_41.py',
              'transport_helpers_r5_41.py': 'transport_runtime_r5_35.py',
              'state_runtime_r5_39.py': 'state_runtime_r5_41.py',
              'optional_support_r5_41.py': 'optional_support_r5_41.py',
              'transport_runtime_r5_34.py': 'transport_runtime_r5_34.py',
              'input_binding_r5_32.py': 'input_binding_r5_32.py'}
    for target, source in copies.items():
        (root / target).write_bytes((directory / source).read_bytes())
    old_transport.base.seal(root)
    (root / 'boundary_provenance.json').write_bytes(canonical({'generation': manifest['generation'],
        'files': {name: sha((root / name).read_bytes()) for name in runtime.FILES}}))
    (root / 'launch.json').write_bytes(canonical(profile['launch']))
    (root / 'capabilities.json').write_bytes(canonical(launch.requirements(application)))
    (root / launch.runtime.FILES[0]).write_bytes(Path(launch.runtime.__file__).read_bytes())
    launch.seal(root)
    (root / 'application_boundary.json').write_bytes(canonical(profile))
    (root / 'application_boundary_provenance.json').write_bytes(canonical({
        'generation': manifest['generation'], 'profile': sha(canonical(profile))}))
    return profile


def support_report(application, specification, declaration, configuration, manifest):
    """One compatible-path assessment for readiness and supplemental audit."""
    findings, routes, expected = [], None, None
    def check(path, stage, action):
        try:
            return action()
        except (ValueError, KeyError, TypeError) as exc:
            findings.append({'path': path, 'stage': stage, 'reason': str(exc)})
    plans = check(['application'], 'semantic', lambda: pipeline.checked(application))
    if declaration is None:
        findings.append({'path': ['state'], 'stage': 'state', 'reason': 'checked durable declaration missing'})
    else:
        check(['state'], 'state', lambda: check_state(application, declaration))
    if specification is None:
        findings.append({'path': ['transport'], 'stage': 'transport', 'reason': 'complete checked specification missing'})
    elif declaration is not None and plans is not None:
        routes = check(['transport'], 'transport', lambda: validate(application, plans, specification, declaration))
        check(['composition'], 'composition', lambda: findings.extend(support.capability_findings(
            {'transport': specification, 'state': declaration})))
    if configuration is None:
        findings.append({'path': ['launch'], 'stage': 'launch', 'reason': 'checked launch configuration missing'})
    elif specification is not None and declaration is not None:
        check(['launch'], 'launch', lambda: launch.profile(configuration,
              {'persistence': specification['persistence'], 'state_profile': declaration}, manifest,
              launch.requirements(application)))
        expected = check(['aggregate'], 'application_profile', lambda: aggregate(
            application, specification, declaration, configuration, manifest))
    return {'findings': findings, 'routes': routes, 'aggregate': expected,
            'status': 'SUPPORTED' if not findings else 'UNSUPPORTED'}
