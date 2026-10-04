"""Aggregate infrastructure profiles around the single current semantic authority.

Profiles are explicit infrastructure declarations, not additional semantic source.
Content predicates are bounded checks of already declared shape/domain/identity
constraints. Arbitrary new application invariants are outside this interface.
"""

import copy
import json
from pathlib import Path

from benchmark.semantic import current_pipeline as pipeline
from benchmark.semantic import unified_types_r5_27 as types
from benchmark.semantic import checked_transport_r5_35 as transport
from benchmark.semantic import checked_launch_r5_36 as launch
from benchmark.semantic import state_runtime_r5_39 as state_runtime
from benchmark.semantic.refined_generator_r5_28 import canonical, sha
from benchmark.semantic.refined_runtime_r5_28 import valid

SCHEMA = {'version': 'R5.39', 'fields': ['application', 'plans', 'artifact', 'transport',
    'binding', 'state', 'launch', 'provider', 'trace'], 'core_constructs': 30}
SCHEMA_ID = sha(canonical(SCHEMA))


def shape_at(shape, path):
    for key in path:
        shape = shape['record'][key]
    return shape


def state_profile(application, alternatives, initial=None):
    result = {'version': 'R5.39', 'versions': copy.deepcopy(application['state']['versions']),
              'alternatives': copy.deepcopy(alternatives), 'initial': copy.deepcopy(initial or {})}
    check_state(application, result)
    return result


def check_state(application, declaration):
    versions = application['state']['versions']
    if (set(declaration) != {'version', 'versions', 'alternatives', 'initial'} or
            declaration['version'] != 'R5.39' or declaration['versions'] != versions or
            set(declaration['alternatives']) != set(versions)):
        raise ValueError('incomplete/incompatible state alternatives')
    for name, descriptor in declaration['alternatives'].items():
        if set(descriptor) != {'codec', 'constraints'} or descriptor['codec'] != versions[name]:
            raise ValueError('state discriminator/codec mismatch')
        for rule in descriptor['constraints']:
            if type(rule) is not dict or type(rule.get('path')) is not list:
                raise ValueError('invalid declared persistence constraint')
            shape = shape_at(descriptor['codec'], rule['path'])
            if rule['kind'] == 'equals':
                if set(rule) != {'kind', 'path', 'value'} or not valid(rule['value'], shape):
                    raise ValueError('incompatible state discriminator')
            elif rule['kind'] == 'population':
                if (set(rule) != {'kind', 'path', 'identity', 'nonblank', 'domains'} or
                        not isinstance(shape, dict) or set(shape) != {'sequence'} or
                        set(shape['sequence']) != {'record'}):
                    raise ValueError('invalid population declaration')
                fields = shape['sequence']['record']
                if rule['identity'] is not None and fields.get(rule['identity']) != 'string':
                    raise ValueError('population identity type mismatch')
                if any(fields.get(field) != 'string' for field in rule['nonblank']):
                    raise ValueError('nonblank content type mismatch')
                for field, domain in rule['domains'].items():
                    if field not in fields or not domain or any(not valid(v, fields[field]) for v in domain):
                        raise ValueError('content domain type mismatch')
            else:
                raise ValueError('unsupported state constraint; separate semantic review required')
    for item in declaration['initial'].values():
        if set(item) != {'version', 'value'} or item['version'] not in versions:
            raise ValueError('invalid initial state reference')
        decoded = state_runtime.decode(canonical(item['value']), declaration)
        if decoded['variant'] != item['version']:
            raise ValueError('initial state content/alternative mismatch')


def legacy_state(declaration):
    return {key: declaration[key] for key in ('versions', 'initial')}


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
            checked = transport.validate(application, plans, one, legacy_state(declaration))[route['public']]
            if checked['applicability']['pre'] != declaration['versions'][variant]:
                raise ValueError('operation dispatched using incompatible state codec')
            targets = [name for name, shape in declaration['versions'].items()
                       if shape == checked['applicability']['post']]
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
    boundary = transport.profile(application, spec, declaration, manifest)
    if manifest['application'] != boundary['application'] or ('units' in manifest and manifest['units'] != boundary['units']):
        raise ValueError('stale semantic application/CheckedPlan artifact identity')
    caps = launch.requirements(application)
    launched = launch.profile(config, boundary, manifest, caps)
    return {'version': 'R5.39', 'schema': SCHEMA_ID, 'application': sha(canonical(application)),
        'plans': boundary['units'], 'artifact': manifest, 'transport': boundary,
        'binding': {public: {variant: route['arguments'] for variant, route in entry.get('alternatives', {'state': entry}).items()}
                    for public, entry in boundary['operations'].items()},
        'state': declaration, 'launch': launched, 'provider': {'requirements': caps, **config['provider']},
        'trace': {'application': manifest['application'], 'generation': manifest['generation'],
                  'provenance': sha(canonical(manifest)), 'policy': config['trace']}}


def check_aggregate(application, spec, declaration, config, manifest, profile):
    expected = aggregate(application, spec, declaration, config, manifest)
    if profile != expected:
        raise ValueError('incompatible aggregate application/profile/provenance identity')
    return expected


def generate(application, root, spec, declaration, config):
    # Entire boundary is checked before emission. No independent compiler path.
    aggregate(application, spec, declaration, config,
              {'application': sha(canonical(application)), 'generation': 'static'})
    launch.generate(application, root, spec, declaration, config)
    manifest = json.loads((root / 'provenance.json').read_bytes())
    profile = aggregate(application, spec, declaration, config, manifest)
    (root / 'application_boundary.json').write_bytes(canonical(profile))
    (root / 'application_boundary_provenance.json').write_bytes(canonical({
        'generation': manifest['generation'], 'profile': sha(canonical(profile))}))
    return profile
