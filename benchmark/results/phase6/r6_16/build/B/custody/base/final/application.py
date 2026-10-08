"""Experimental ordinary Python execution of shared intent; no Lykoi imports."""
import copy
import json
import os
import tempfile
from pathlib import Path

INTENT = {'version': 1, 'storage': 'records.json', 'fields': {'id': {'type': 'identifier', 'domain': []}, 'created_at': {'type': 'timestamp', 'domain': []}, 'label': {'type': 'string', 'domain': []}, 'phase': {'type': 'enum', 'domain': ['unsealed', 'sealed']}, 'witness': {'type': 'enum', 'domain': ['present', 'absent']}, 'material': {'type': 'enum', 'domain': ['routine', 'fragile']}}, 'create': {'bindings': {'id': {'source': 'uuid_v4', 'value': None}, 'created_at': {'source': 'utc_clock', 'value': None}, 'label': {'source': 'input', 'value': 'label'}, 'phase': {'source': 'literal', 'value': 'unsealed'}, 'witness': {'source': 'input', 'value': 'witness'}, 'material': {'source': 'input', 'value': 'material'}}, 'nonblank': ['label']}, 'operations': {'seal': {'guards': [{'condition': {'op': 'eq', 'left': {'kind': 'field', 'value': 'phase', 'type': 'enum', 'domain': ['unsealed', 'sealed']}, 'right': {'kind': 'literal', 'value': 'unsealed', 'type': 'enum', 'domain': ['unsealed', 'sealed']}}, 'error': 'invalid_transition'}, {'condition': {'op': 'eq', 'left': {'kind': 'field', 'value': 'witness', 'type': 'enum', 'domain': ['present', 'absent']}, 'right': {'kind': 'literal', 'value': 'present', 'type': 'enum', 'domain': ['present', 'absent']}}, 'error': 'gate_required'}], 'writes': {'phase': {'source': 'literal', 'value': 'sealed'}}}, 'set_gate': {'guards': [{'condition': {'op': 'not', 'child': {'op': 'and', 'children': [{'op': 'eq', 'left': {'kind': 'field', 'value': 'phase', 'type': 'enum', 'domain': ['unsealed', 'sealed']}, 'right': {'kind': 'literal', 'value': 'sealed', 'type': 'enum', 'domain': ['unsealed', 'sealed']}}, {'op': 'eq', 'left': {'kind': 'parameter', 'value': 'value', 'type': 'enum', 'domain': ['present', 'absent']}, 'right': {'kind': 'literal', 'value': 'absent', 'type': 'enum', 'domain': ['present', 'absent']}}]}}, 'error': 'gate_locked'}], 'writes': {'witness': {'source': 'input', 'value': 'value'}}}}, 'invariants': [{'op': 'or', 'children': [{'op': 'not', 'child': {'op': 'eq', 'left': {'kind': 'field', 'value': 'phase', 'type': 'enum', 'domain': ['unsealed', 'sealed']}, 'right': {'kind': 'literal', 'value': 'sealed', 'type': 'enum', 'domain': ['unsealed', 'sealed']}}}, {'op': 'eq', 'left': {'kind': 'field', 'value': 'witness', 'type': 'enum', 'domain': ['present', 'absent']}, 'right': {'kind': 'literal', 'value': 'present', 'type': 'enum', 'domain': ['present', 'absent']}}]}]}


class Reject(Exception):
    pass


def typed(value, field):
    if type(value) is not str:
        return False
    if field['type'] == 'enum':
        return value in field['domain']
    if field['type'] == 'timestamp':
        import datetime
        try:
            return value.endswith('Z') and datetime.datetime.fromisoformat(value[:-1] + '+00:00').utcoffset().total_seconds() == 0
        except ValueError:
            return False
    return True


def predicate(e, record, args):
    def val(v):
        return v['value'] if v['kind'] == 'literal' else (record if v['kind'] == 'field' else args).get(v['value'])
    if e['op'] == 'eq':
        a, b = val(e['left']), val(e['right'])
        return a is not None and b is not None and type(a) is type(b) and a == b
    if e['op'] == 'not':
        return not predicate(e['child'], record, args)
    values = [predicate(v, record, args) for v in e['children']]
    return all(values) if e['op'] == 'and' else any(values)


def valid(records):
    if type(records) is not list:
        return False
    ids = []
    for r in records:
        if type(r) is not dict or set(r) != set(INTENT['fields']):
            return False
        if not all(typed(r[n], t) for n, t in INTENT['fields'].items()):
            return False
        if any(not r[n].strip() for n in INTENT['create']['nonblank']):
            return False
        if not all(predicate(e, r, {}) for e in INTENT['invariants']):
            return False
        ids.append(r['id'])
    return len(ids) == len(set(ids))


def handle(op, args, providers):
    path = Path(INTENT['storage'])
    try:
        records = json.loads(path.read_text()) if path.exists() else []
        if not valid(records):
            raise Reject('invalid_state')
        if op == 'list':
            return {'ok': sorted(records, key=lambda r: (r['created_at'], r['id']))}
        if op == 'create':
            r = {}
            for n, b in INTENT['create']['bindings'].items():
                r[n] = args.get(n) if b['source'] == 'input' else b['value'] if b['source'] == 'literal' else providers[b['source']]()
            if any(type(r.get(n)) is not str or not r[n].strip() for n in INTENT['create']['nonblank']):
                raise Reject('invalid_label')
            if not all(typed(r.get(n), t) for n, t in INTENT['fields'].items()):
                raise Reject('invalid_input')
            if any(x['id'] == r['id'] for x in records):
                raise Reject('id_collision')
            staged = records + [r]
        else:
            m = INTENT['operations'][op]
            target = next((r for r in records if r['id'] == args.get('id')), None)
            if target is None:
                raise Reject('not_found')
            for g in m['guards']:
                if not predicate(g['condition'], target, args):
                    raise Reject(g['error'])
            r = copy.deepcopy(target)
            for n, w in m['writes'].items():
                r[n] = w['value'] if w['source'] == 'literal' else args.get(w['value'])
                if not typed(r[n], INTENT['fields'][n]):
                    raise Reject('invalid_input')
            staged = [r if x is target else x for x in records]
        if not valid(staged):
            raise Reject('invalid_state')
        fd, temp = tempfile.mkstemp(dir='.', prefix='.records-')
        try:
            with os.fdopen(fd, 'w') as f:
                json.dump(staged, f, sort_keys=True)
                f.flush()
                os.fsync(f.fileno())
            os.replace(temp, path)
        finally:
            if os.path.exists(temp):
                os.unlink(temp)
        return {'ok': r}
    except Reject as e:
        return {'error': str(e)}
    except (OSError, ValueError, KeyError, TypeError):
        return {'error': 'invalid_state'}
