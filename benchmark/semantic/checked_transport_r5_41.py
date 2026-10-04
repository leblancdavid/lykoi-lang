"""Prospective admission; unchanged output/persistence policy, composed decoders."""

from benchmark.semantic import checked_transport_r5_35 as historical
from benchmark.semantic import optional_support_r5_41 as support
from benchmark.semantic import public_binding_r5_32 as scalar_oracle
from benchmark.semantic.refined_generator_r5_28 import canonical

output = historical.output
specification = historical.specification
ERROR_TYPE, FAILURES = historical.ERROR_TYPE, historical.FAILURES


def validate(application, plans, spec, declaration):
    historical.check_state(application, declaration)
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
        historical.check_output(desc, ERROR_TYPE, ('BOUNDARY_FAILURE',))
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
            declaration_shape = fields[slot]
            if not support.argument_supported(declaration_shape, arg):
                raise ValueError('incompatible checked binding')
            shape = support.unwrap(declaration_shape, 'optional')
            element = support.unwrap(shape, 'sequence')
            domain = arg['domain']
            if domain is not None and (not support.domain_supported(element, domain) or
                    len({canonical(v) for v in domain}) != len(domain)):
                raise ValueError('invalid typed element domain')
            args[name] = {'slot': slot, 'type': shape, 'optional': shape != declaration_shape, 'domain': domain,
                          'representation': arg['representation'], 'mode': arg['mode'], 'order': arg['order']}
            slots.add(slot)
        if slots != set(fields):
            raise ValueError('incomplete input binding coverage including optional slots')
        if set(item['outcomes']) != set(plan.outcomes):
            raise ValueError('incompatible outcome variants')
        for tag, desc in item['outcomes'].items():
            historical.check_output(desc, plan.outcomes[tag], ('SUCCESS', 'SEMANTIC_FAILURE'))
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
