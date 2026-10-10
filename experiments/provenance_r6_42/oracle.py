"""Independent, hand-specified R6.42 observation schedule; never runs VM or plans.

This is a finite oracle for the contract's fixed behavior, not a second interpreter.
Node/expression/read/output charges below are derived from authoritative semantics.
"""
from common import c, serial
from forms import coordinates
import hashlib


def cell(value, start, end, origins=()):
    return {'type': 'Unit' if value is None else 'Bool' if type(value) is bool else 'Int64',
            'value': value, 'span': [start, end], 'origins': list(origins)}


def trace_digest(events):
    return hashlib.sha256(c.canonical(events)).hexdigest()


class Stop(Exception):
    def __init__(self, error):
        self.error = error


def expected(package, data, flat=False, budget=100000):
    paths = coordinates(package)
    root = 'flat/Entry' if flat else paths['root']
    work, cursor, node = 0, 0, 'preflight'
    events, checks = [], []

    def reject(code, offset, stage='structure'):
        raise Stop({'code': code, 'offset': offset, 'node': node, 'stage': stage, 'path': None, 'expected': []})

    def charge(site=None):
        nonlocal work
        site = cursor if site is None else site
        events.append({'kind': 'charge', 'node': node, 'cursor': cursor, 'work_before': work, 'site': site})
        if work == budget:
            reject('WORK_LIMIT', site, 'limit')
        work += 1

    def enter(at, depth):
        nonlocal node
        previous = node
        events.append({'kind': 'enter', 'node': at, 'cursor': cursor, 'work_before': work, 'depth': depth})
        node = at
        charge()
        return previous

    def leave(previous, at, depth, result):
        nonlocal node
        events.append({'kind': 'return', 'node': at, 'cursor': cursor, 'work_after': work,
                       'depth': depth, 'cell': result})
        node = previous
        return result

    def atom(key):
        nonlocal cursor
        at = root + '/' + key
        previous = enter(at, 2)
        start = cursor
        if cursor == len(data):
            reject('TRUNCATED', cursor)
        charge()
        value = data[cursor]
        cursor += 1
        charge(start)  # numeric conversion sites the original raw span after read
        return leave(previous, at, 2, cell(value, start, cursor, (start,)))

    def guard(at, label, ok, site, expr_charges, depth):
        checks.append(label)
        previous = enter(at, depth)
        # le+two children =3; le+add+two refs+const =5.
        for _ in range(expr_charges):
            charge()
        if not ok:
            charge()  # declared site ref is evaluated only on failure
            reject(label.split(':')[-1], site['span'][0], 'validation')
        return leave(previous, at, depth, cell(None, cursor, cursor))

    def addition(at, value, left_cell, depth):
        previous = enter(at, depth)
        for _ in range(3):
            charge()  # add + left ref + right ref/const
        return leave(previous, at, depth, cell(value, *left_cell['span']))

    def transform(side, source):
        if flat:
            guard(root + '/' + side + '_guard', side + ':INNER', source['value'] <= 3, source, 3, 2)
            return addition(root + '/' + side, source['value'] + 1, source, 2)
        n, g = paths[side], paths[side + '_inner']
        n_prev = enter(n, 2)
        g_prev = enter(g, 3)
        guard(g + '/guard', side + ':INNER', source['value'] <= 3, source, 3, 4)
        summed = addition(g + '/sum', source['value'] + 1, source, 4)
        charge()  # Guarded result ref; seq replaces span with its consumed region
        result = leave(g_prev, g, 3, cell(summed['value'], 2, 2))
        charge()  # Nested result ref, same seq wrapping
        return leave(n_prev, n, 2, cell(result['value'], 2, 2))

    try:
        root_prev = enter(root, 1)
        x, y = atom('x'), atom('y')
        at = root + '/end'
        previous = enter(at, 2)
        if cursor != len(data):
            reject('TRAILING', cursor)
        leave(previous, at, 2, cell(None, cursor, cursor))
        left, right = transform('left', x), transform('right', y)
        guard(root + '/post_low', 'POST_LOW', 3 <= left['value'], left, 3, 2)
        guard(root + '/post_high', 'POST_HIGH', left['value'] + right['value'] <= 6, right, 5, 2)
        total = addition(root + '/total', left['value'] + right['value'], left, 2)
        charge()  # Entry result ref
        result = leave(root_prev, root, 1, cell(total['value'], 0, 2))
        at = root + '/encode'
        previous = enter(at, 1)
        charge()  # root ref
        charge()
        charge()
        leave(previous, at, 1, cell(None, cursor, cursor))
        envelope = {'status': 'success', 'value': result['value'], 'provenance': {'span': [0, 2], 'origins': []},
                    'consumed': 2, 'work': work, 'output': serial(result['value'].to_bytes(2, 'big')),
                    'output_spans': [{'node': at, 'start': 0, 'end': 2}]}
    except Stop as exc:
        envelope = {'status': 'reject', 'error': exc.error, 'work': work}
    return {'envelope': envelope, 'trace': events, 'trace_sha256': trace_digest(events), 'checks': checks}
