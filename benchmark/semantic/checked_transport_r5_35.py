"""Prospective checked extensions to R5.34, using the same current pipeline."""

import copy
import json
from pathlib import Path
import subprocess
import sys
import uuid

from benchmark.semantic import current_pipeline as pipeline
from benchmark.semantic import checked_transport_r5_34 as base
from benchmark.semantic import public_binding_r5_32 as scalar_oracle
from benchmark.semantic import transport_runtime_r5_35 as runtime
from benchmark.semantic.refined_generator_r5_28 import canonical, sha
from benchmark.semantic.refined_runtime_r5_28 import valid

ERROR_TYPE = {'record': {'code': 'string'}}
FAILURES = ('transport_failure', 'binding_failure', 'persistence_missing',
            'persistence_invalid_json', 'persistence_invalid_state', 'invocation_failure')


def output(shape, status='SUCCESS'):
    return {'type': copy.deepcopy(shape), 'status': status, 'stream': 'stdout' if status == 'SUCCESS' else 'stderr',
        'exit': 0 if status == 'SUCCESS' else 1,
        'presentation': {'mode': 'direct'}}


def specification(plans):
    operations = []
    for name, plan in plans.items():
        plan.assert_invariants()
        args = []
        for slot, declaration in plan.slots['input']['record'].items():
            optional = isinstance(declaration, dict) and set(declaration) == {'optional'}
            shape = declaration['optional'] if optional else declaration
            sequence = isinstance(shape, dict) and set(shape) == {'sequence'}
            element = shape['sequence'] if sequence else shape
            args.append({'public': slot, 'slot': slot, 'decoder': element, 'domain': None,
                'representation': 'json' if sequence or element == 'boolean' or isinstance(element, dict) else 'text',
                'mode': 'collection' if sequence else 'single', 'omission': 'omit' if optional else 'required',
                'order': 'encounter' if sequence else None})
        operations.append({'public': name, 'semantic': name, 'arguments': args,
            'outcomes': {tag: output(shape) for tag, shape in plan.outcomes.items()},
            'error_codes': {c: c for c in scalar_oracle.CATEGORIES}, 'argument_codes': {}})
    return {'operations': operations, 'failures': {c: output(ERROR_TYPE, 'BOUNDARY_FAILURE') for c in FAILURES},
            'persistence': {'missing': 'REQUIRE_EXISTING', 'initial': None}}


def state_profile(application, initial=None):
    state = application['state']
    versions = state['versions'] if set(state) == {'versions'} else {'state': state}
    declaration = {'versions': copy.deepcopy(versions), 'initial': copy.deepcopy(initial or {})}
    check_state(application, declaration)
    return declaration


def check_state(application, declaration):
    state = application['state']
    versions = state['versions'] if set(state) == {'versions'} else {'state': state}
    if (type(declaration) is not dict or set(declaration) != {'versions', 'initial'} or
            declaration['versions'] != versions or type(declaration['initial']) is not dict):
        raise ValueError('incompatible checked state profile')
    for name, initial in declaration['initial'].items():
        if (type(name) is not str or not name or type(initial) is not dict or
                set(initial) != {'version', 'value'} or initial['version'] not in versions or
                not valid(initial['value'], versions[initial['version']])):
            raise ValueError('invalid declared initial state')


def check_output(desc, shape, statuses):
    if (type(desc) is not dict or set(desc) != {'type', 'status', 'stream', 'exit', 'presentation'} or
            desc['type'] != shape or desc['status'] not in statuses or
            desc['stream'] not in ('stdout', 'stderr') or type(desc['exit']) is not int or
            not 0 <= desc['exit'] <= 125):
        raise ValueError('incompatible checked public outcome')
    presentation = desc['presentation']
    if presentation == {'mode': 'direct'}:
        return
    if (type(presentation) is not dict or set(presentation) != {'mode', 'coverage', 'fields'} or
            presentation['mode'] != 'object' or presentation['coverage'] not in ('full', 'selected') or
            type(presentation['fields']) is not list or not presentation['fields']):
        raise ValueError('invalid structured envelope')
    names, paths = set(), []
    for field in presentation['fields']:
        if type(field) is not dict or type(field.get('name')) is not str or not field['name'] or field['name'] in names:
            raise ValueError('colliding envelope field')
        names.add(field['name'])
        source = field.get('source')
        if source == 'constant':
            if set(field) != {'name', 'source', 'type', 'value'} or not valid(field['value'], field['type']):
                raise ValueError('invalid envelope constant')
        elif source == 'kind':
            if set(field) != {'name', 'source', 'type'} or field['type'] != 'string':
                raise ValueError('invalid outcome discriminator mapping')
        elif source == 'payload':
            if set(field) != {'name', 'source', 'type', 'path'} or type(field['path']) is not list:
                raise ValueError('invalid payload projection')
            child = shape
            for key in field['path']:
                if (type(key) is not str or not isinstance(child, dict) or 'record' not in child or
                        key not in child['record']):
                    raise ValueError('nonexistent result field')
                child = child['record'][key]
            if child != field['type'] or isinstance(child, dict) and 'optional' in child:
                raise ValueError('incompatible/optional envelope payload')
            paths.append(field['path'])
        else:
            raise ValueError('unknown envelope source')
    if presentation['coverage'] == 'full' and [] not in paths:
        if not isinstance(shape, dict) or 'record' not in shape:
            raise ValueError('required payload omitted')
        required = {k for k, v in shape['record'].items() if not (isinstance(v, dict) and 'optional' in v)}
        if not required <= {p[0] for p in paths if len(p) == 1}:
            raise ValueError('required record payload omitted')


def validate(application, plans, spec, declaration):
    if declaration.get('version') == 'R5.39':
        from benchmark.semantic.application_boundary_r5_39 import validate as validate_alternatives
        return validate_alternatives(application, plans, spec, declaration)
    check_state(application, declaration)
    if type(spec) is not dict or set(spec) != {'operations', 'failures', 'persistence'}:
        raise ValueError('invalid boundary specification')
    policy = spec['persistence']
    if (type(policy) is not dict or set(policy) != {'missing', 'initial'} or
            policy['missing'] not in ('REQUIRE_EXISTING', 'INITIALIZE_DECLARED_STATE') or
            (policy['initial'] is not None if policy['missing'] == 'REQUIRE_EXISTING' else
             policy['initial'] not in declaration['initial'])):
        raise ValueError('invalid missing-store policy/reference')
    if type(spec['failures']) is not dict or set(spec['failures']) != set(FAILURES):
        raise ValueError('complete boundary failure policy required')
    for desc in spec['failures'].values():
        check_output(desc, ERROR_TYPE, ('BOUNDARY_FAILURE',))
    operations = {}
    if type(spec['operations']) is not list or not spec['operations']:
        raise ValueError('nonempty operation list required')
    for item in spec['operations']:
        if type(item) is not dict or set(item) != {'public', 'semantic', 'arguments', 'outcomes', 'error_codes', 'argument_codes'}:
            raise ValueError('invalid operation mapping')
        public, semantic = item['public'], item['semantic']
        if type(public) is not str or not public or public in operations or semantic not in plans:
            raise ValueError('unknown/duplicate operation')
        plan = plans[semantic]
        plan.assert_invariants()
        fields, args, slots = plan.slots['input']['record'], {}, set()
        if type(item['arguments']) is not list:
            raise ValueError('invalid arguments')
        for arg in item['arguments']:
            if type(arg) is not dict or set(arg) != {'public', 'slot', 'decoder', 'representation', 'domain', 'mode', 'omission', 'order'}:
                raise ValueError('invalid collection/scalar binding')
            name, slot = arg['public'], arg['slot']
            if type(name) is not str or not name or name in args or slot not in fields or slot in slots:
                raise ValueError('invalid/duplicate input slot')
            shape = fields[slot]
            optional = isinstance(shape, dict) and set(shape) == {'optional'}
            shape = shape['optional'] if optional else shape
            sequence = isinstance(shape, dict) and set(shape) == {'sequence'}
            element = shape['sequence'] if sequence else shape
            base_type = element['nullable'] if isinstance(element, dict) and set(element) == {'nullable'} else element
            if (base_type not in ('string', 'integer', 'instant', 'boolean') or arg['decoder'] != element or
                    arg['omission'] != ('omit' if optional else 'required') or
                    arg['mode'] not in (('repeat', 'collection') if sequence else ('single',)) or
                    arg['order'] != ('encounter' if sequence else None) or
                    arg['representation'] not in ('text', 'json') or
                    (arg['mode'] == 'collection' or element == 'boolean' or isinstance(element, dict)) and arg['representation'] != 'json'):
                raise ValueError('incompatible checked binding')
            domain = arg['domain']
            if domain is not None and (type(domain) is not list or not domain or
                    any(not valid(v, element) for v in domain) or len({canonical(v) for v in domain}) != len(domain)):
                raise ValueError('invalid typed element domain')
            args[name] = {'slot': slot, 'type': shape, 'optional': optional, 'domain': domain,
                          'representation': arg['representation'], 'mode': arg['mode'], 'order': arg['order']}
            slots.add(slot)
        required = {k for k, v in fields.items() if not (isinstance(v, dict) and 'optional' in v)}
        if not required <= slots:
            raise ValueError('missing required input mapping')
        if set(item['outcomes']) != set(plan.outcomes):
            raise ValueError('incompatible outcome variants')
        for tag, desc in item['outcomes'].items():
            check_output(desc, plan.outcomes[tag], ('SUCCESS', 'SEMANTIC_FAILURE'))
        codes = item['error_codes']
        if set(codes) != set(scalar_oracle.CATEGORIES) or any(type(v) is not str or not v for v in codes.values()):
            raise ValueError('invalid binding error codes')
        if type(item['argument_codes']) is not dict or set(item['argument_codes']) - set(args):
            raise ValueError('unknown argument code policy')
        for codes in item['argument_codes'].values():
            if set(codes) - set(scalar_oracle.CATEGORIES) or any(type(v) is not str or not v for v in codes.values()):
                raise ValueError('invalid argument error policy')
        operations[public] = {'semantic': semantic, 'contract': plan.digest, 'arguments': args,
            'outcomes': item['outcomes'], 'error_codes': item['error_codes'], 'argument_codes': item['argument_codes'],
            'applicability': {'pre': plan.slots['pre'], 'post': plan.slots['post'],
                              'has_semantic_precondition': plan.applicability is not None}}
    return operations


def profile(application, spec, declaration, manifest):
    if declaration.get('version') == 'R5.39':
        from benchmark.semantic.application_boundary_r5_39 import transport_profile
        return transport_profile(application, spec, declaration, manifest)
    plans = pipeline.checked(application)
    return {'version': 'R5.35', 'id': application['id'], 'application': sha(canonical(application)),
        'generation': manifest['generation'], 'units': {n: p.digest for n, p in plans.items()},
        'operations': validate(application, plans, spec, declaration),
        'state_profile': declaration, 'persistence': spec['persistence'], 'failures': spec['failures']}


def seal(root):
    base.seal(root)
    manifest = json.loads((root / 'provenance.json').read_bytes())
    (root / 'boundary_provenance.json').write_bytes(canonical({'generation': manifest['generation'],
        'files': {name: sha((root / name).read_bytes()) for name in runtime.FILES}}))


def generate(application, directory, spec=None, declaration=None):
    plans = pipeline.checked(application)
    spec = specification(plans) if spec is None else spec
    declaration = state_profile(application) if declaration is None else declaration
    validate(application, plans, spec, declaration)
    root = Path(directory)
    manifest = pipeline.generate(application, root)
    (root / 'transport.json').write_bytes(canonical(profile(application, spec, declaration, manifest)))
    for name in (*base.FILES[1:], *runtime.FILES):
        (root / name).write_bytes((base.ROOT / name).read_bytes())
    seal(root)
    return manifest


def observe(root, argv):
    invocation = uuid.uuid4().hex
    state = root / 'state.json'
    trace, transport_trace = root / (invocation + '.semantic.json'), root / (invocation + '.transport.json')
    before = runtime.snapshot(state)
    command = [sys.executable, str(root / runtime.FILES[0]), str(state), str(trace), str(transport_trace), invocation, *argv]
    completed = subprocess.run(command, capture_output=True, text=True)
    public = {'command': command, 'argv': argv, 'invocation': invocation,
              'stdout': completed.stdout, 'stderr': completed.stderr, 'exit': completed.returncode}
    return (json.loads(transport_trace.read_bytes()) if transport_trace.exists() else None,
            json.loads(trace.read_bytes()) if trace.exists() else None, public, before, runtime.snapshot(state))


def expected_raw(argv, route):
    # Independent token accumulation, not a call to runtime.raw_arguments.
    tokens = argv[1:]
    if len(tokens) % 2:
        raise ValueError('unpaired arguments')
    raw = {}
    for index in range(0, len(tokens), 2):
        flag, text = tokens[index:index + 2]
        if flag[:2] != '--':
            raise ValueError('invalid flag')
        name = flag[2:]
        field = route['arguments'].get(name)
        value = json.loads(text) if field and field['representation'] == 'json' else text
        if field and field['mode'] == 'repeat':
            raw[name] = raw.get(name, []) + [value]
        else:
            if name in raw:
                raise ValueError('duplicate')
            raw[name] = value
    return raw


def expected_binding(operation, raw, route):
    slots, inp, errors = {}, {}, []
    for name in sorted(set(raw) - set(route['arguments'])):
        errors.append({'argument': name, 'slot': None, 'expected': None, 'category': 'unknown_argument'})
    for name, field in sorted(route['arguments'].items()):
        slot, shape = field['slot'], field['type']
        collection = isinstance(shape, dict) and 'sequence' in shape
        if name not in raw or not collection:
            metadata = {'operations': {operation: {name: {k: field[k] for k in ('slot', 'type', 'optional', 'domain')}}}}
            result = scalar_oracle.expected_binding(operation, json.dumps({name: raw[name]} if name in raw else {}), metadata)
        elif type(raw[name]) is not list:
            result = {'slots': {slot: {'supplied': True, 'state': 'BINDING_FAILED'}}, 'input': None,
                'failures': [{'argument': name, 'slot': slot, 'expected': shape, 'category': 'malformed_scalar'}]}
        else:
            values, failures = [], []
            for index, value in enumerate(raw[name]):
                metadata = {'operations': {operation: {name: {'slot': slot, 'type': shape['sequence'],
                    'optional': False, 'domain': field['domain']}}}}
                child = scalar_oracle.expected_binding(operation, json.dumps({name: value}), metadata)
                failures.extend({**error, 'index': index} for error in child['failures'])
                if not child['failures']:
                    values.append(child['input'][slot])
            result = {'slots': {slot: {'supplied': True, 'state': 'BINDING_FAILED' if failures else 'BOUND_TYPED'}},
                      'input': None if failures else {slot: values}, 'failures': failures}
        slots.update(result['slots'])
        errors.extend(result['failures'])
        if result['input'] is not None:
            inp.update(result['input'])
    return {'slots': slots, 'input': None if errors else inp, 'failures': errors}


def expected_output(payload, kind, descriptor):
    # Independent structured projection and process observation expectation.
    presentation = descriptor['presentation']
    if presentation['mode'] == 'direct':
        value = payload
    else:
        value = {}
        for field in presentation['fields']:
            if field['source'] == 'constant':
                item = field['value']
            elif field['source'] == 'kind':
                item = kind
            else:
                item = payload
                for key in field['path']:
                    item = item[key]
            value[field['name']] = item
    text = json.dumps(value, sort_keys=True) + '\n'
    return {'stdout': text if descriptor['stream'] == 'stdout' else '',
            'stderr': text if descriptor['stream'] == 'stderr' else '', 'exit': descriptor['exit']}


def challenge(application, root, spec, declaration, event, semantic, public, before, after):
    verdict = {'TRANSPORT_PROFILE_CONFORMANT': False, 'transport_grounded': False,
        'TRANSPORT_BINDING_CONFORMANT': None, 'INPUT_BINDING_CONFORMANT': None,
        'PERSISTENCE_BOUNDARY_CONFORMANT': None, 'SEMANTIC_EXECUTION_CONFORMANT': None, 'OUTPUT_CONFORMANT': None}
    try:
        manifest = json.loads((root / 'provenance.json').read_bytes())
        authority = profile(application, spec, declaration, manifest)
        verdict['TRANSPORT_PROFILE_CONFORMANT'] = runtime.load(root) == authority and manifest['application'] == sha(canonical(application))
        if not verdict['TRANSPORT_PROFILE_CONFORMANT']:
            return verdict
        grounded = (event['argv'] == public['argv'] and event['invocation'] == public['invocation'] and
            event['generation'] == manifest['generation'] and
            all(event[k] == public[k] for k in ('stdout', 'stderr', 'exit')) and
            event['pre_digest'] == runtime.digest(before) and event['post_digest'] == runtime.digest(after))
        verdict['transport_grounded'] = grounded
        if not grounded:
            return verdict
        requested = public['argv'][0] if public['argv'] else None
        route = authority['operations'].get(requested)
        category, payload, expected, effective, initialized = 'transport_failure', {'code': 'unknown_public_operation'}, None, None, False
        if route is not None:
            try:
                raw = expected_raw(public['argv'], route)
            except (ValueError, TypeError):
                payload = {'code': 'malformed_public_arguments'}
            else:
                expected = expected_binding(route['semantic'], raw, route)
                verdict['TRANSPORT_BINDING_CONFORMANT'] = event['operation'] == route['semantic'] and event['raw'] == raw
                verdict['INPUT_BINDING_CONFORMANT'] = event['binding'] == expected
                if expected['failures']:
                    error = expected['failures'][0]
                    code = route['argument_codes'].get(error['argument'], {}).get(error['category'], route['error_codes'][error['category']])
                    category, payload = 'binding_failure', {'code': code}
                else:
                    category = None
                    if before is None:
                        if spec['persistence']['missing'] == 'REQUIRE_EXISTING':
                            category = 'persistence_missing'
                        else:
                            effective = canonical(declaration['initial'][spec['persistence']['initial']]['value'])
                            initialized = True
                    else:
                        effective = before
                    if category is None:
                        try:
                            pre = json.loads(effective)
                        except ValueError:
                            category = 'persistence_invalid_json'
                        else:
                            if not any(valid(pre, shape) for shape in declaration['versions'].values()):
                                category = 'persistence_invalid_state'
                    if category is not None:
                        payload = {'code': category}
                    elif semantic is None:
                        category, payload = 'invocation_failure', {'code': 'generated_execution_rejected'}
                        verdict['PERSISTENCE_BOUNDARY_CONFORMANT'] = (event['semantic_invoked'] and
                            event['effective_pre'] == effective.decode() and event['initialized'] == initialized and
                            event['semantic_result']['exit'] != 0 and before == after)
                    else:
                        outcome = semantic['outcome']
                        category, payload = outcome['kind'], outcome['value']
                        effective_after = after if semantic['attempted_write'] or before is not None else effective
                        persistence_ok = (event['effective_pre'] == effective.decode() and event['initialized'] == initialized and
                            semantic['pre'] == json.loads(effective) and
                            (after is not None if semantic['attempted_write'] else before == after))
                        verdict['PERSISTENCE_BOUNDARY_CONFORMANT'] = persistence_ok
                        internal = {'operation': route['semantic'], 'invocation': public['invocation'],
                            'input': expected['input'], **event['semantic_result']}
                        checked = pipeline.challenge(application, root, semantic, internal, effective, effective_after)
                        verdict['SEMANTIC_EXECUTION_CONFORMANT'] = checked['grounded'] and checked['conformant']
                        verdict['TRANSPORT_BINDING_CONFORMANT'] &= semantic['input'] == expected['input'] and event['semantic_invoked']
        if verdict['PERSISTENCE_BOUNDARY_CONFORMANT'] is None:
            verdict['PERSISTENCE_BOUNDARY_CONFORMANT'] = (before == after and semantic is None and not event['semantic_invoked'])
        if expected is None:
            verdict['TRANSPORT_BINDING_CONFORMANT'] = event['raw'] is None and event['binding'] is None
        desc = route['outcomes'][category] if route and category in route['outcomes'] else authority['failures'][category]
        wanted = expected_output(payload, category, desc)
        verdict['OUTPUT_CONFORMANT'] = (all(public[k] == wanted[k] for k in wanted) and
            event['category'] == category and event['classification'] == desc['status'])
    except (ValueError, KeyError, TypeError, OSError):
        pass
    return verdict
