"""Typed persistence decoding from checked descriptors; never repairs content."""

import json

if __package__:
    from benchmark.semantic.refined_runtime_r5_28 import valid
else:
    from refined_runtime_r5_28 import valid


def at(value, path):
    for key in path:
        value = value[key]
    return value


def conforms(value, descriptor):
    if not valid(value, descriptor['codec']):
        return False
    for constraint in descriptor['constraints']:
        target = at(value, constraint['path'])
        kind = constraint['kind']
        if kind == 'equals' and (type(target) is not type(constraint['value']) or target != constraint['value']):
            return False
        if kind == 'population':
            seen = set()
            for row in target:
                identity = constraint['identity']
                if identity is not None:
                    key = row[identity]
                    if key in seen:
                        return False
                    seen.add(key)
                for field in constraint['nonblank']:
                    if not row[field].strip():
                        return False
                for field, domain in constraint['domains'].items():
                    if not any(type(row[field]) is type(member) and row[field] == member for member in domain):
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
