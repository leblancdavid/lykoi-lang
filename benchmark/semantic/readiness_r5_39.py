"""Whole-contract readiness v2: exact domains, provider multiplicity and profiles."""

import copy

from benchmark.semantic import readiness_r5_38 as previous
from benchmark.semantic import application_boundary_r5_39 as boundary
from benchmark.semantic import current_pipeline as pipeline
from benchmark.semantic import checked_launch_r5_36 as launch
from benchmark.semantic import checked_transport_r5_35 as transport
from benchmark.semantic.refined_generator_r5_28 import canonical, sha


def decoder_supported(shape):
    if isinstance(shape, dict) and set(shape) == {'sequence'}:
        shape = shape['sequence']
    if isinstance(shape, dict) and set(shape) == {'nullable'}:
        shape = shape['nullable']
    return shape in ('string', 'integer', 'instant', 'boolean')


def inspect(application, specification=None, declaration=None, configuration=None, obligations=None, aggregate=None):
    report = previous.inspect(application)
    # v1 remains reproducible; v2 replaces its boundary capability verdicts.
    report['gaps'] = [g for g in report['gaps'] if g['stage'] not in ('binding', 'transport', 'state', 'launch')]
    report['version'] = 'R5.39'
    report['aggregate_schema'] = boundary.SCHEMA_ID
    gaps = report['gaps']
    def gap(path, stage, reason):
        row = {'path': list(path), 'stage': stage, 'reason': str(reason)}
        if row not in gaps:
            gaps.append(row)
    plans = {}
    for name, contract in application['operations'].items():
        for field, shape in contract['input']['record'].items():
            value = shape['optional'] if isinstance(shape, dict) and set(shape) == {'optional'} else shape
            if not decoder_supported(value):
                gap(('operations', name, 'input', field), 'binding', {'unsupported_decoder_domain': shape})
        if report['operations'][name]['status'] == 'SUPPORTED':
            plan = pipeline.checked({**application, 'operations': {name: contract}})[name]
            plans[name] = plan
            report['operations'][name]['refinement_facts'] = list(plan.refinement_facts.values())
    if specification is None:
        gap(('transport',), 'transport', 'complete checked transport specification missing')
    if declaration is None:
        gap(('state_profile',), 'state', 'checked durable state declaration missing')
    else:
        try:
            if declaration.get('version') == 'R5.39':
                boundary.check_state(application, declaration)
            else:
                transport.check_state(application, declaration)
        except (ValueError, TypeError, KeyError) as exc:
            gap(('state_profile',), 'state', exc)
    routes = None
    if specification is not None:
        covered = set()
        seen = set()
        for index, route in enumerate(specification.get('operations', [])):
            if route.get('public') in seen:
                gap(('transport', index), 'transport', 'duplicate public route')
            seen.add(route.get('public'))
            alternatives = route.get('alternatives', {'state': route})
            for variant, item in alternatives.items():
                name = item.get('semantic')
                covered.add(name)
                if name not in plans:
                    gap(('transport', index, variant), 'transport', 'semantic operation has no CheckedPlan')
                    continue
                mapped = {arg.get('slot') for arg in item.get('arguments', [])}
                if mapped != set(plans[name].slots['input']['record']):
                    gap(('transport', index, variant), 'binding', 'incomplete input binding coverage')
                if declaration is not None:
                    try:
                        single = {**specification, 'operations': [{**item, 'public': route['public']}]}
                        old = boundary.legacy_state(declaration) if declaration.get('version') == 'R5.39' else declaration
                        transport.validate(application, plans, single, old)
                        if 'alternatives' in route and (variant not in declaration['versions'] or
                                plans[name].slots['pre'] != declaration['versions'][variant]):
                            raise ValueError('operation state alternative/codec mismatch')
                    except (ValueError, KeyError, TypeError) as exc:
                        gap(('transport', index, variant), 'transport', exc)
        for name in set(plans) - covered:
            gap(('operations', name), 'transport', 'CheckedPlan has no public route/output mapping')
        if declaration is not None:
            try:
                routes = transport.validate(application, plans, specification, declaration)
            except (ValueError, TypeError, KeyError) as exc:
                gap(('transport',), 'transport', exc)
    static_manifest = {'application': sha(canonical(application)), 'generation': 'static-readiness-v2',
                       'units': {name: plan.digest for name, plan in plans.items()}}
    if configuration is None:
        gap(('launch',), 'launch', 'checked launch configuration missing')
    else:
        # Launch validation still runs when another profile is invalid.
        dummy = {'persistence': specification.get('persistence') if specification else None,
                 'state_profile': declaration, 'operations': routes}
        try:
            launch.profile(configuration, dummy, static_manifest, {name: kind for plan in plans.values()
                           for name, kind in plan.capabilities.items()})
        except (ValueError, TypeError, KeyError) as exc:
            gap(('launch',), 'launch', exc)
    if specification is not None and declaration is not None and configuration is not None:
        try:
            expected = boundary.aggregate(application, specification, declaration, configuration, static_manifest)
            if aggregate is not None and aggregate != expected:
                gap(('application_profile',), 'application_profile', 'stale/incompatible aggregate identity')
            report['boundary_identity'] = sha(canonical(expected))
        except (ValueError, TypeError, KeyError) as exc:
            gap(('application_profile',), 'application_profile', exc)
    else:
        gap(('application_profile',), 'application_profile', 'complete aggregate boundary cannot be formed')
    for index, obligation in enumerate(obligations or []):
        kind = obligation.get('kind')
        if kind == 'public_state_alternatives':
            if declaration is None or declaration.get('version') != 'R5.39' or routes is None:
                gap(('obligations', index), 'transport', 'checked public state-alternative coverage missing')
            elif any(name not in routes for name in obligation.get('public', [])):
                gap(('obligations', index), 'transport', 'required public route missing')
        elif kind == 'durable_content_constraints':
            if declaration is None or declaration.get('version') != 'R5.39' or any(
                    not desc['constraints'] for desc in declaration['alternatives'].values()):
                gap(('obligations', index), 'state', 'declared durable population/content constraint coverage missing')
            elif 'requirements' not in obligation:
                gap(('obligations', index), 'state', 'content obligations lack typed constraint coverage references')
            else:
                for variant, rules in obligation['requirements'].items():
                    existing = declaration['alternatives'].get(variant, {}).get('constraints', [])
                    for rule in rules:
                        if rule not in existing:
                            gap(('obligations', index, variant), 'state', 'required declared content constraint missing: ' + str(rule))
        else:
            gap(('obligations', index), 'readiness', 'unrecognized contract obligation; review required')
    report['status'] = 'READY' if not gaps else 'NOT_READY'
    report['generated'] = report['executed'] = False
    return report


def closure_matrix():
    original = previous.closure_matrix()
    rows = []
    from benchmark.semantic import unified_types_r5_27 as types
    for cell in original['rows']:
        for multiplicity in ('one_provider', 'duplicate_equivalent', 'independent_required', 'conflicting'):
            row = copy.deepcopy(cell)
            row['provider_dimension'] = multiplicity
            row['provider_dimension_applicable'] = (multiplicity == 'one_provider' or
                multiplicity == 'duplicate_equivalent' and bool(row['required_facts']) or
                multiplicity == 'independent_required' and set(row['required_facts']) == {'presence', 'non_null'} or
                multiplicity == 'conflicting' and 'non_null' in row['required_facts'])
            expr = row['expression']
            if multiplicity == 'duplicate_equivalent':
                def duplicate(node):
                    if not isinstance(node, dict):
                        return
                    if 'and' in node:
                        guards = [part for part in node['and'] if 'present' in part or 'not' in part]
                        node['and'].extend(copy.deepcopy(guards))
                    elif 'order' in node:
                        select = node['order']['source']['select']
                        where = select['where']
                        if 'present' in where or 'not' in where:
                            select['where'] = {'and': [where, copy.deepcopy(where)]}
                        else:
                            duplicate(where)
                duplicate(expr)
            elif multiplicity == 'conflicting' and 'non_null' in row['required_facts']:
                # Opposite typed-null premise is not an equivalent non-null fact.
                def conflict(node):
                    if 'and' in node:
                        provider = next((p for p in node['and'] if 'not' in p), None)
                        if provider:
                            node['and'].append(copy.deepcopy(provider['not']))
                    elif 'order' in node:
                        where = node['order']['source']['select']['where']
                        if 'not' in where:
                            node['order']['source']['select']['where'] = {'and': [where, copy.deepcopy(where['not'])]}
                        else:
                            conflict(where)
                conflict(expr)
            try:
                row['effective'] = types.analyze(expr, row['slots'])
                row['status'], row['diagnostic'] = 'SUPPORTED', None
            except ValueError as exc:
                row['effective'], row['status'], row['diagnostic'] = None, 'UNSUPPORTED', str(exc)
            row['boundary_dimensions'] = ['nullable_binding', 'state_alternative_dispatch', 'content_validation', 'aggregate_profile']
            row['binding_domain'] = {'declared': row['declared'], 'decoder_supported': decoder_supported(
                row['declared']['optional'] if isinstance(row['declared'], dict) and 'optional' in row['declared'] else row['declared']),
                'omission': 'omit' if row['domain'] in ('optional', 'optional_nullable') else 'required',
                'null_representation': 'json_null' if row['domain'] in ('nullable', 'optional_nullable') else None}
            row['boundary_evidence'] = 'R5_39-whole-boundary-evidence.json (separate composition evidence; not execution of this cell)'
            rows.append(row)
    return {'version': 'R5.39', 'base_matrix': sha(canonical(original)), 'base_rows': 84,
            'core_constructs': 30, 'rows': rows}
