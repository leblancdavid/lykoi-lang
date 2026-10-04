"""Shared public-representation and present-value domain composition rules.

Optional is record membership, nullable is a value alternative. Neither grants
permission to skip the underlying value decoder or a present-value constraint.
"""

import json

if __package__:
    from benchmark.semantic.refined_runtime_r5_28 import valid
else:
    from refined_runtime_r5_28 import valid


def unwrap(shape, kind):
    return shape[kind] if isinstance(shape, dict) and set(shape) == {kind} else shape


def decoder_supported(shape, representation):
    # Only the established scalar decoder family is available. Nullable wraps
    # that decoder; it cannot manufacture support for records or collections.
    base = unwrap(shape, 'nullable')
    return (base in ('string', 'integer', 'instant', 'boolean') and
            representation in ('text', 'json') and
            (representation == 'json' or base != 'boolean'))


def argument_supported(declaration, argument):
    optional = unwrap(declaration, 'optional') != declaration
    shape = unwrap(declaration, 'optional')
    sequence = isinstance(shape, dict) and set(shape) == {'sequence'}
    element = unwrap(shape, 'sequence')
    return (argument['decoder'] == element and
            argument['omission'] == ('omit' if optional else 'required') and
            argument['mode'] in (('repeat', 'collection') if sequence else ('single',)) and
            argument['order'] == ('encounter' if sequence else None) and
            decoder_supported(element, argument['representation']) and
            (argument['mode'] != 'collection' or argument['representation'] == 'json'))


def public_value(text, descriptor):
    shape = unwrap(descriptor['type'], 'sequence')
    if not decoder_supported(shape, descriptor['representation']):
        raise ValueError('unsupported public decoder composition')
    # Plain text is always a supplied non-null representation. In particular,
    # the text "null" is not silently reinterpreted as JSON null.
    return json.loads(text) if descriptor['representation'] == 'json' else text


def domain_supported(declaration, domain):
    shape = unwrap(declaration, 'optional')
    return (type(domain) is list and bool(domain) and
            all(valid(member, shape) for member in domain))


def domain_conforms(row, field, declaration, domain):
    if not domain_supported(declaration, domain):
        return False
    if field not in row:
        return isinstance(declaration, dict) and set(declaration) == {'optional'}
    value = row[field]
    return (valid(value, unwrap(declaration, 'optional')) and
            any(type(value) is type(member) and value == member for member in domain))


def capability_findings(configuration):
    findings = []
    for index, route in enumerate(configuration['transport']['operations']):
        for variant, item in route.get('alternatives', {'state': route}).items():
            for argument in item['arguments']:
                if (not decoder_supported(argument['decoder'], argument['representation']) or
                        argument['mode'] == 'collection' and argument['representation'] != 'json'):
                    findings.append({'path': ['transport', 'operations', index, variant, 'arguments', argument['public']],
                                     'stage': 'binding', 'reason': 'unsupported public decoder composition'})
    state = configuration['state']
    for variant, desc in state['alternatives'].items():
        for index, rule in enumerate(desc['constraints']):
            if rule['kind'] != 'population':
                continue
            shape = desc['codec']
            for key in rule['path']:
                shape = shape['record'][key]
            fields = shape['sequence']['record']
            for field, domain in rule['domains'].items():
                if field not in fields or not domain_supported(fields[field], domain):
                    findings.append({'path': ['state', 'alternatives', variant, 'constraints', index, 'domains', field],
                                     'stage': 'state', 'reason': 'unsupported present-value domain composition'})
    return findings
