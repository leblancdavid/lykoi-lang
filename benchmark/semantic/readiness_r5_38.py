"""Static whole-document domain/composition readiness; never emits or executes.

Authoritative analysis is the only type authority. Consumer capability tables
describe implementation boundaries, not semantic types. Missing profiles or
unrepresented boundary obligations fail closed instead of becoming READY.
"""

import copy
from benchmark.semantic import current_pipeline as pipeline
from benchmark.semantic import unified_types_r5_27 as types
from benchmark.semantic import checked_transport_r5_35 as transport
from benchmark.semantic import checked_launch_r5_36 as launch
from benchmark.semantic.refined_generator_r5_28 import canonical, sha

EXPRESSION_CONSUMERS = frozenset(('ref', 'literal', 'present', 'equals', 'and', 'not',
    'select', 'order', 'record', 'cardinality', 'sole', 'project', 'fallback', 'external',
    'trim', 'nonblank', 'map', 'stable_unique', 'for_each', 'before'))
STAGES = ('authoritative_analysis', 'checked_plan', 'current_pipeline', 'semantic_verifier')


def inspect(application, specification=None, declaration=None, configuration=None, obligations=None):
    """Collect every operation and boundary gap in one invocation.

    Stable document paths identify evidence; no Python node ID escapes this
    report. Failed operations are additionally walked under their actual scopes
    to enumerate later independent operand failures without generation.
    """
    gaps, operations, plans = [], {}, {}

    def gap(path, stage, reason):
        row = {'path': list(path), 'stage': stage, 'reason': str(reason)}
        if row not in gaps:
            gaps.append(row)

    def scan(expr, slots, path, guards=frozenset()):
        if not isinstance(expr, dict) or len(expr) != 1:
            return
        kind, arg = next(iter(expr.items()))
        if kind not in EXPRESSION_CONSUMERS:
            gap(path, 'current_pipeline', 'unsupported expression consumer: ' + kind)
        try:
            types.analyze(expr, slots, guards)
        except ValueError as exc:
            gap(path, 'authoritative_analysis', exc)
        if kind == 'and':
            try:
                _, local = types.conjunction(arg, slots)
            except ValueError:
                local = set()
            for index, part in enumerate(arg):
                scan(part, slots, (*path, kind, index), guards | local)
        elif kind == 'select':
            scan(arg['source'], slots, (*path, kind, 'source'), guards)
            try:
                element = types.analyze(arg['source'], slots, guards)['sequence']
                scan(arg['where'], {**slots, 'item': element}, (*path, kind, 'where'))
            except (ValueError, TypeError, KeyError):
                pass  # the source failure was already collected
        elif kind == 'not':
            witness = types.non_null_witness(expr, slots)
            scope = guards - {('non_null', *witness)} if witness is not None else guards
            scan(arg, slots, (*path, kind), scope)
        elif kind == 'order':
            source = arg.get('source')
            if isinstance(source, dict) and 'ref' in source and source['ref'][0] not in ('input', 'pre', 'post'):
                gap(path, 'current_pipeline', 'ordering a local binding is unsupported')
            scan(source, slots, (*path, kind, 'source'), guards)
        elif kind in ('equals', 'before'):
            for index, operand in enumerate(arg):
                scan(operand, slots, (*path, kind, index), guards)
        elif kind == 'record':
            for key, value in arg.items():
                scan(value, slots, (*path, kind, key), guards)
        elif kind == 'for_each':
            scan(arg['sequence'], slots, (*path, kind, 'sequence'), guards)
            scan(arg['property'], {**slots, arg['bind']: 'string'}, (*path, kind, 'property'))
        elif kind in ('trim', 'nonblank', 'cardinality', 'sole'):
            scan(arg, slots, (*path, kind), guards)
        elif kind in ('map', 'stable_unique'):
            scan(arg['sequence'], slots, (*path, kind, 'sequence'), guards)
        elif kind == 'project':
            scan(arg['row'], slots, (*path, kind, 'row'), guards)
        elif kind == 'fallback':
            for key in ('value', 'default'):
                scan(arg[key], slots, (*path, kind, key), guards)

    for name, contract in application['operations'].items():
        path = ('operations', name)
        try:
            one = {**application, 'operations': {name: contract}}
            plan = pipeline.checked(one)[name]
            plan.assert_invariants()
            plans[name] = plan
            facts = []
            for fact in plan.facts.values():
                row = copy.deepcopy(fact)
                row.pop('refinement')  # runtime IDs are source-bound internal handles
                facts.append(row)
                if fact['kind'] not in EXPRESSION_CONSUMERS:
                    gap(fact['identity'][1:], 'current_pipeline', 'unsupported expression consumer')
            orders = [{'source': plan.facts[o['source']]['identity'], 'keys': o['keys'],
                'domains': [{'declared': f['declared'], 'effective': f['effective'],
                    'dependencies': [(plan.facts[p]['identity'], plan.facts[s]['identity'])
                                     for s, p in f['dependencies']]} for f in o['key_facts']]} for o in plan.orders.values()]
            operations[name] = {'status': 'SUPPORTED', 'digest': plan.digest, 'facts': facts,
                'ordering': orders, 'state': plan.slots, 'capabilities': plan.capabilities,
                'contexts': {'read_write': ['write' if 'relations' in b['transition'] else 'read' for b in contract['branches']],
                    'relation_sets': [[next(iter(r)) for r in b['transition'].get('relations', [])] for b in contract['branches']]},
                'stages': {stage: 'SUPPORTED_STATIC' for stage in STAGES}}
        except (ValueError, KeyError, TypeError) as exc:
            gap(path, 'checked_plan', exc)
            operations[name] = {'status': 'UNSUPPORTED', 'stages': {'checked_plan': 'REJECTED'}}
        slots = {'input': contract['input'], **types.state_slots(contract)}
        if 'requires' in contract:
            scan(contract['requires'], {k: v for k, v in slots.items() if k != 'post'}, (*path, 'requires'))
        for index, branch in enumerate(contract['branches']):
            prefix = (*path, 'branches', index)
            if branch['when'] is not None:
                scan(branch['when'], {k: v for k, v in slots.items() if k != 'post'}, (*prefix, 'when'))
            scan(branch['value'], slots, (*prefix, 'value'))
            for number, relation in enumerate(branch['transition'].get('relations', [])):
                kind, rule = next(iter(relation.items()))
                for key in ('match', 'value', 'record'):
                    if key in rule:
                        scan(rule[key], {k: v for k, v in slots.items() if k != 'post'},
                             (*prefix, 'transition', 'relations', number, kind, key))
        # Exact input decoder domains are checked even without a public profile.
        for field, shape in contract['input']['record'].items():
            value = shape.get('optional', shape) if isinstance(shape, dict) else shape
            element = value.get('sequence', value) if isinstance(value, dict) else value
            if element not in ('string', 'integer', 'instant', 'boolean'):
                gap((*path, 'input', field), 'binding', {'unsupported_decoder_domain': shape})

    boundary = None
    if specification is None:
        gap(('transport',), 'transport', 'complete checked transport specification missing')
    if declaration is None:
        gap(('state_profile',), 'state', 'checked durable state declaration missing')
    if configuration is None:
        gap(('launch',), 'launch', 'checked launch configuration missing')
    if specification is not None and declaration is not None:
        # Each route gets its own validation so one bad decoder does not hide
        # a second route failure. Global collisions are checked separately.
        seen = set()
        for index, route in enumerate(specification['operations']):
            if route['public'] in seen:
                gap(('transport', 'operations', index), 'transport', 'duplicate public route; state alternatives unsupported')
            seen.add(route['public'])
            if route['semantic'] not in plans:
                gap(('transport', 'operations', index), 'transport', 'semantic operation has no CheckedPlan')
                continue
            try:
                transport.validate(application, plans, {**specification, 'operations': [route]}, declaration)
            except (ValueError, TypeError, KeyError) as exc:
                gap(('transport', 'operations', index), 'transport', exc)
        try:
            checked_routes = transport.validate(application, plans, specification, declaration)
            boundary = {'version': 'R5.35', 'id': application['id'], 'application': sha(canonical(application)),
                'generation': 'static-readiness-only', 'units': {n: p.digest for n, p in plans.items()},
                'operations': checked_routes, 'state_profile': declaration, 'persistence': specification['persistence'],
                'failures': specification['failures']}
        except (ValueError, TypeError, KeyError) as exc:
            gap(('transport',), 'transport', exc)
    if boundary is not None and configuration is not None:
        try:
            caps = {name: shape for plan in plans.values() for name, shape in plan.capabilities.items()}
            launch.profile(configuration, boundary, {'application': sha(canonical(application)),
                'generation': 'static-readiness-only'}, caps)
        except (ValueError, TypeError, KeyError) as exc:
            gap(('launch',), 'launch', exc)
    for index, obligation in enumerate(obligations or []):
        # Boundary obligations are explicit, independently authored contract
        # coverage, not inferred from generated code or operation names.
        if obligation['kind'] == 'public_state_alternatives':
            gap(('obligations', index), 'transport', 'one public route cannot dispatch state-shape alternatives')
        elif obligation['kind'] == 'durable_content_constraints':
            gap(('obligations', index), 'state', 'structural codec does not enforce declared population/content constraints')
        else:
            gap(('obligations', index), 'readiness', 'unrecognized contract obligation; review required')
    return {'version': 'R5.38', 'application': sha(canonical(application)), 'core_constructs': 30,
        'status': 'READY' if not gaps else 'NOT_READY',
        'semantic_status': 'READY' if len(plans) == len(application['operations']) and
            not any(g['stage'] in STAGES for g in gaps) else 'NOT_READY',
        'operations': operations, 'gaps': gaps, 'generated': False, 'executed': False}


def closure_matrix():
    """Executable domain/refinement probes, not a broad feature checklist."""
    from benchmark.semantic.nullable_study_r5_38 import ref, lit, non_null
    rows = []
    for base, literal in [('string', 'x'), ('integer', 3), ('instant', '2030-01-01T00:00:00Z')]:
        for domain, shape, guards in [
                ('required', base, []), ('optional', {'optional': base}, [{'present': ref('item', 'value')}]),
                ('nullable', {'nullable': base}, [non_null('value', base)]),
                ('optional_nullable', {'optional': {'nullable': base}}, [{'present': ref('item', 'value')}, non_null('value', base)])]:
            state = {'sequence': {'record': {'code': 'string', 'value': shape}}}
            slots = {'pre': state, 'item': state['sequence'], 'input': {'record': {}}}
            comparisons = {'equality': {'equals': [ref('item', 'value'), lit(literal, base)]},
                'before': {'before': [ref('item', 'value'), lit(literal, base)]},
                'selection_predicates': {'equals': [ref('item', 'value'), lit(literal, base)]},
                'write_targeting': {'equals': [ref('item', 'value'), lit(literal, base)]}}
            for relation in ('equality', 'before', 'ordering', 'selection_predicates', 'fallback', 'projection', 'write_targeting'):
                predicate = comparisons.get(relation)
                facts = guards if relation not in ('fallback', 'projection') else []
                if predicate is not None:
                    expr = {'and': [*guards, predicate]} if guards else predicate
                elif relation == 'ordering':
                    where = guards[0] if len(guards) == 1 else {'and': guards} if guards else lit(True, 'boolean')
                    expr = {'order': {'source': {'select': {'source': ref('pre'), 'where': where}}, 'keys': ['value']}}
                elif relation == 'projection':
                    expr = {'project': {'row': ref('item'), 'fields': ['value']}}
                else:
                    inner = shape['optional'] if isinstance(shape, dict) and 'optional' in shape else base
                    expr = {'fallback': {'value': ref('item', 'value'), 'default': lit(None, inner) if isinstance(inner, dict) else lit(literal, inner)}}
                try:
                    effective = types.analyze(expr, slots)
                    status, diagnostic = 'SUPPORTED', None
                except ValueError as exc:
                    effective, status, diagnostic = None, 'UNSUPPORTED', str(exc)
                rows.append({'relation': relation, 'base': base, 'domain': domain, 'declared': shape,
                    'required_facts': ['presence' if 'present' in g else 'non_null' for g in facts],
                    'effective': effective, 'status': status, 'diagnostic': diagnostic,
                    'state_shape': state, 'composition': 'positive selection/conjunction; keyed targeting guard' if relation == 'write_targeting' else relation,
                    'stage': 'authoritative_analysis', 'expression': expr, 'slots': slots})
    return {'version': 'R5.38', 'core_constructs': 30, 'rows': rows}


def validate_matrix_pipeline():
    """Transfer every accepted matrix row through current generation/verification.

    Nullable/optional input here is a typed semantic invocation. Public decoder
    closure is reported separately by inspect(), never inferred from this test.
    """
    import json
    from pathlib import Path
    import tempfile
    from benchmark.semantic.nullable_study_r5_38 import ref, lit
    report = []
    for row in closure_matrix()['rows']:
        identity = [row['base'], row['domain'], row['relation']]
        if row['status'] != 'SUPPORTED':
            report.append({'combination': identity, 'status': 'REJECTED_BEFORE_GENERATION'})
            continue
        state = row['state_shape']
        expr = copy.deepcopy(row['expression'])
        inp_shape = {'record': {}}
        inp = {}
        yes = {'equals': [lit(1, 'integer'), lit(1, 'integer')]}
        transition = {'preserve': True}
        if row['relation'] in ('equality', 'before', 'selection_predicates', 'write_targeting'):
            selection = {'select': {'source': ref('pre'), 'where': expr}}
            if row['relation'] == 'write_targeting':
                yes = {'equals': [{'cardinality': selection}, lit(1, 'integer')]}
                expr = ref('post')
                transition = {'relations': [{'remove': {'collection': None, 'identity': 'code', 'match': lit('a')}}]}
            else:
                expr = selection
            outcome_shape = state
        elif row['relation'] == 'ordering':
            outcome_shape = state
        else:
            def bind(node):
                if isinstance(node, dict):
                    if 'ref' in node and node['ref'][0] == 'item':
                        node['ref'][0] = 'input'
                    for value in node.values():
                        bind(value)
                elif isinstance(node, list):
                    for value in node:
                        bind(value)
            bind(expr)
            inp_shape = state['sequence']
            outcome_shape = row['effective']
        contract = {'id': 'closure.' + '.'.join(identity), 'version': 'R5.27',
            'input': inp_shape, 'state': state, 'branches': [
                {'tag': 'ok', 'when': yes, 'value': expr, 'value_type': outcome_shape, 'transition': transition},
                {'tag': 'other', 'when': None, 'value': lit('other'), 'value_type': 'string', 'transition': {'preserve': True}}]}
        model = {'id': contract['id'], 'state': state, 'operations': {'run': contract}}
        value = {'string': 'x', 'integer': 3, 'instant': '2030-01-01T00:00:00Z'}[row['base']]
        populations = [[{'code': 'a', 'value': value}]]
        if row['domain'] in ('nullable', 'optional_nullable'):
            populations.append([{'code': 'a', 'value': None}])
        if row['domain'] in ('optional', 'optional_nullable'):
            populations.append([{'code': 'a'}])
        verdicts = []
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            pipeline.generate(model, root)
            for population in populations:
                if row['relation'] in ('fallback', 'projection'):
                    inp = population[0]
                (root / 'state.json').write_bytes(canonical(population))
                event, public, before, after = pipeline.observe(root, 'run', inp)
                verdicts.append(pipeline.challenge(model, root, event, public, before, after))
        report.append({'combination': identity, 'status': 'VALIDATED' if all(v['grounded'] and v['conformant'] for v in verdicts) else 'FAILED',
                       'verdicts': verdicts})
    return report
