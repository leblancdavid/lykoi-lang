"""Minimal deterministic JSON Schema subset checker, independent of Lykoi.

Syntax validation only. Cross-reference/type compatibility belongs to downstream
tools. Fail closed on schema keywords the checker does not implement.
"""
import json
from pathlib import Path

SCHEMA = json.loads(Path(__file__).with_name('intent-2.schema.json').read_text())
TYPES = {'object': dict, 'array': list, 'string': str, 'null': type(None), 'integer': int}


def check(value, s=None):
    s = SCHEMA if s is None else s
    supported = {'$schema', '$defs', '$ref', 'title', 'type', 'additionalProperties',
                 'required', 'properties', 'const', 'enum', 'items', 'minItems',
                 'minProperties', 'oneOf'}
    if set(s) - supported:
        raise ValueError('unsupported schema keyword')
    if '$ref' in s:
        return check(value, SCHEMA['$defs'][s['$ref'].split('/')[-1]])
    if 'oneOf' in s:
        matches = 0
        for branch in s['oneOf']:
            try:
                check(value, branch)
                matches += 1
            except ValueError:
                pass
        if matches != 1:
            raise ValueError('oneOf mismatch')
        return
    types = s.get('type')
    if types and type(value) not in [TYPES[t] for t in (types if isinstance(types, list) else [types])]:
        raise ValueError('shape type mismatch')
    if 'const' in s and (type(value) is not type(s['const']) or value != s['const']):
        raise ValueError('constant mismatch')
    if 'enum' in s and value not in s['enum']:
        raise ValueError('enum mismatch')
    if type(value) is dict:
        if not set(s.get('required', [])) <= set(value) or len(value) < s.get('minProperties', 0):
            raise ValueError('missing property')
        props = s.get('properties', {})
        for n, v in value.items():
            if n in props:
                check(v, props[n])
            elif s.get('additionalProperties') is False:
                raise ValueError('unknown property')
            elif isinstance(s.get('additionalProperties'), dict):
                check(v, s['additionalProperties'])
    if type(value) is list:
        if len(value) < s.get('minItems', 0):
            raise ValueError('short array')
        for v in value:
            check(v, s.get('items', {}))
