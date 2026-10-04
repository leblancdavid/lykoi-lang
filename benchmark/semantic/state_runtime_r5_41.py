"""Prospective typed persistence codec with membership-aware finite domains."""

import json

if __package__:
    from benchmark.semantic.refined_runtime_r5_28 import valid
    from benchmark.semantic.optional_support_r5_41 import domain_conforms
else:
    from refined_runtime_r5_28 import valid
    from optional_support_r5_41 import domain_conforms


def at(value, path):
    for key in path:
        value = value[key]
    return value


def conforms(value, descriptor):
    if not valid(value, descriptor['codec']):
        return False
    for constraint in descriptor['constraints']:
        target = at(value, constraint['path'])
        shape = descriptor['codec']
        for key in constraint['path']:
            shape = shape['record'][key]
        if constraint['kind'] == 'equals':
            if type(target) is not type(constraint['value']) or target != constraint['value']:
                return False
        elif constraint['kind'] == 'population':
            seen = set()
            for row in target:
                identity = constraint['identity']
                if identity is not None:
                    key = row[identity]
                    if key in seen:
                        return False
                    seen.add(key)
                if any(not row[field].strip() for field in constraint['nonblank']):
                    return False
                for field, domain in constraint['domains'].items():
                    if not domain_conforms(row, field, shape['sequence']['record'][field], domain):
                        return False
        else:
            return False
    return True


def decode(data, profile):
    try:
        value = json.loads(data)
    except (ValueError, TypeError):
        return {'category': 'persistence_invalid_json', 'variant': None, 'value': None}
    matches = []
    for name, descriptor in profile['alternatives'].items():
        try:
            if conforms(value, descriptor):
                matches.append(name)
        except (KeyError, TypeError, ValueError):
            pass
    if len(matches) != 1:
        return {'category': 'persistence_invalid_state', 'variant': None, 'value': None}
    return {'category': None, 'variant': matches[0], 'value': value}
