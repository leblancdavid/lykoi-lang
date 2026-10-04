"""Bounded configuration integrity audit, not arbitrary-code security.

Closed schemas are delegated to the existing checked boundary validators.
Each leaf (including empty containers) requires exact source traceability.
Unadmitted configuration is reported separately from behavioral contamination.
"""

from pathlib import Path

from benchmark.semantic import application_boundary_r5_39 as boundary
from benchmark.semantic import application_boundary_r5_40 as admission
from benchmark.semantic import checked_transport_r5_35 as transport
from benchmark.semantic import checked_launch_r5_36 as launch
from benchmark.semantic.refined_generator_r5_28 import canonical, sha

SCHEMA = {'version': 'R5.40', 'configuration_fields': ['transport', 'state', 'launch'],
          'trace_fields': ['path', 'value', 'artifact', 'sha256', 'clause', 'interpretation'],
          'allowed_output_constants': 'authority-backed interface labels only',
          'provider': 'production; no fixture values', 'core_constructs': 30}
FORBIDDEN = {'code', 'python', 'algorithm', 'predicate', 'transform', 'filter', 'sort',
             'expected', 'expected_output', 'fixture', 'lookup_table', 'migration_algorithm'}


def leaves(value, path=()):
    if isinstance(value, dict) and value:
        for key, child in value.items():
            yield from leaves(child, (*path, key))
    elif isinstance(value, list) and value:
        for index, child in enumerate(value):
            yield from leaves(child, (*path, index))
    else:
        yield list(path), value


def structure(configuration):
    """Closed declarative key schema, independent of compatibility admission.

    An incompatible decoder representation can still be configuration data;
    arbitrary executable/behavior fields cannot. Both gates are mandatory.
    """
    from benchmark.semantic import unified_types_r5_27 as types
    def keys(value, expected):
        if type(value) is not dict or set(value) != set(expected):
            raise ValueError('undeclared configuration fields: ' + str(expected))
    def output(value):
        keys(value, ('type', 'status', 'stream', 'exit', 'presentation'))
        types.general.shape_valid(value['type'])
        presentation = value['presentation']
        if presentation == {'mode': 'direct'}:
            return
        keys(presentation, ('mode', 'coverage', 'fields'))
        for field in presentation['fields']:
            extra = {'constant': 'value', 'payload': 'path', 'kind': None}.get(field.get('source'), 'unknown')
            if extra == 'unknown':
                raise ValueError('undeclared output source')
            keys(field, ('name', 'source', 'type', *([extra] if extra else [])))
            types.general.shape_valid(field['type'])
    keys(configuration, SCHEMA['configuration_fields'])
    spec, state, config = (configuration[key] for key in SCHEMA['configuration_fields'])
    keys(spec, ('operations', 'failures', 'persistence'))
    keys(spec['persistence'], ('missing', 'initial'))
    for desc in spec['failures'].values():
        output(desc)
    for route in spec['operations']:
        keys(route, ('public', 'alternatives'))
        for item in route['alternatives'].values():
            keys(item, ('semantic', 'arguments', 'outcomes', 'error_codes', 'argument_codes'))
            for arg in item['arguments']:
                keys(arg, ('public', 'slot', 'decoder', 'domain', 'representation', 'mode', 'omission', 'order'))
                types.general.shape_valid(arg['decoder'])
            for desc in item['outcomes'].values():
                output(desc)
    keys(state, ('version', 'versions', 'alternatives', 'initial'))
    for shape in state['versions'].values():
        types.general.shape_valid(shape)
    for desc in state['alternatives'].values():
        keys(desc, ('codec', 'constraints'))
        types.general.shape_valid(desc['codec'])
        for rule in desc['constraints']:
            if rule.get('kind') == 'population':
                keys(rule, ('kind', 'path', 'identity', 'nonblank', 'domains'))
            elif rule.get('kind') == 'equals':
                keys(rule, ('kind', 'path', 'value'))
            else:
                raise ValueError('undeclared persistence constraint kind')
    for item in state['initial'].values():
        keys(item, ('version', 'value'))
    keys(config, ('id', 'store', 'trace', 'runtime', 'provider'))
    keys(config['store'], ('base', 'path', 'parent'))
    keys(config['trace'], ('mode', 'directory'))
    keys(config['trace']['directory'], ('base', 'path', 'parent'))
    keys(config['provider'], ('mode', 'types', 'values'))
    return {'valid': True, 'version': SCHEMA['version']}


def contamination(configuration):
    findings = []
    def walk(value, path=()):
        if isinstance(value, dict):
            if value.get('source') == 'constant' and (
                    value.get('name') not in ('error', 'status') or
                    value.get('type') != 'string' or type(value.get('value')) is not str):
                findings.append({'path': list(path), 'reason': 'fixture/result constant forbidden; interface labels only'})
            for key, child in value.items():
                # A typed record may legitimately have a field named "code";
                # field identities are not configuration instructions.
                if key in FORBIDDEN and (not path or path[-1] != 'record'):
                    findings.append({'path': list((*path, key)), 'reason': 'behavioral field prohibited'})
                walk(child, (*path, key))
        elif isinstance(value, list):
            for index, child in enumerate(value):
                walk(child, (*path, index))
        elif not (value is None or type(value) in (str, int, bool)):
            findings.append({'path': list(path), 'reason': 'non-JSON/executable value'})
    walk(configuration)
    provider = configuration['launch']['provider']
    if provider['mode'] != 'production' or provider['values'] != {}:
        findings.append({'path': ['launch', 'provider'], 'reason': 'fixture provider forbidden'})
    return findings


def traceability(configuration, records, root, authorities):
    expected = {canonical(path): value for path, value in leaves(configuration)}
    seen = set()
    for record in records:
        if set(record) != set(SCHEMA['trace_fields']):
            raise ValueError('invalid source trace schema')
        path = canonical(record['path'])
        if path in seen or path not in expected or record['value'] != expected[path]:
            raise ValueError('duplicate/stale/unexplained profile field')
        seen.add(path)
        artifact = record['artifact']
        if artifact not in authorities or sha((Path(root) / artifact).read_bytes()) != record['sha256']:
            raise ValueError('unapproved/stale authority')
        if not record['clause'] or not record['interpretation']:
            raise ValueError('missing authority interpretation')
    if seen != set(expected):
        raise ValueError('incomplete profile-source traceability')
    return {'valid': True, 'fields': len(seen), 'authority_artifacts': sorted(authorities)}


def schema_findings(application, configuration):
    """Collect independent schema failures without emitting any target behavior."""
    spec, state, config = (configuration[key] for key in SCHEMA['configuration_fields'])
    findings = []
    plans = admission.complete_inputs(application, spec)
    def check(path, function):
        try:
            function()
        except (ValueError, KeyError, TypeError) as exc:
            findings.append({'path': path, 'reason': str(exc)})
    # Check constraints individually: one unsupported declaration must not hide others.
    for variant, descriptor in state['alternatives'].items():
        for index, rule in enumerate(descriptor['constraints']):
            single = {**state, 'initial': {}, 'alternatives': {
                name: {**desc, 'constraints': [rule] if name == variant else []}
                for name, desc in state['alternatives'].items()}}
            check(['state', 'alternatives', variant, 'constraints', index],
                  lambda single=single: boundary.check_state(application, single))
    for index, route in enumerate(spec['operations']):
        for variant, item in route['alternatives'].items():
            one = {**spec, 'operations': [{**item, 'public': route['public']}]}
            check(['transport', 'operations', index, 'alternatives', variant],
                  lambda one=one: transport.validate(application, plans, one, boundary.legacy_state(state)))
    manifest = {'application': sha(canonical(application)), 'generation': 'static-readiness-v2',
                'units': {name: plan.digest for name, plan in plans.items()}}
    dummy = {'persistence': spec['persistence'], 'state_profile': state}
    check(['launch'], lambda: launch.profile(config, dummy, manifest, launch.requirements(application)))
    check(['aggregate'], lambda: admission.aggregate(application, spec, state, config, manifest))
    return findings


def capability_findings(configuration):
    """Static checks of independently witnessed limits in the current profiles.

    No request identities, field names, input populations or benchmark expected
    outputs are inspected. These checks describe current boundary support, not
    a new implementation of decoding or content predicates.
    """
    findings = []
    for index, route in enumerate(configuration['transport']['operations']):
        for variant, item in route['alternatives'].items():
            for argument in item['arguments']:
                shape = argument['decoder']
                if isinstance(shape, dict) and set(shape) == {'nullable'} and argument['representation'] == 'text':
                    findings.append({'path': ['transport', 'operations', index, 'alternatives', variant,
                                             'arguments', argument['public']],
                        'stage': 'binding', 'classification': 'MISSING_GENERIC_CAPABILITY',
                        'reason': 'plain-text nullable element decoder is not admitted; current profile requires JSON'})
    for variant, desc in configuration['state']['alternatives'].items():
        for index, rule in enumerate(desc['constraints']):
            if rule['kind'] != 'population':
                continue
            shape = boundary.shape_at(desc['codec'], rule['path'])
            for field in rule['domains']:
                declaration = shape['sequence']['record'][field]
                if isinstance(declaration, dict) and set(declaration) == {'optional'}:
                    findings.append({'path': ['state', 'alternatives', variant, 'constraints', index, 'domains', field],
                        'stage': 'state', 'classification': 'MISSING_GENERIC_CAPABILITY',
                        'reason': 'population-domain runtime indexes absent optional field; no present-only domain policy'})
    return findings
