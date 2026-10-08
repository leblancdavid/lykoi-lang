"""R6.10 pure, bounded semantic-plan VM. No format identities in dispatch."""
from dataclasses import dataclass


@dataclass
class Cell:
    value: object
    start: int
    end: int
    origins: tuple = ()


class PlanError(ValueError):
    pass


class Rejection(Exception):
    def __init__(self, code, offset, node, stage='structure', path=None, expected=()):
        self.error = dict(code=code, offset=offset, node=node, stage=stage, path=path, expected=sorted(expected))


def plain(x):
    if isinstance(x, Cell):
        return plain(x.value)
    if isinstance(x, dict):
        return {k: plain(v) for k, v in x.items()}
    if isinstance(x, list):
        return [plain(v) for v in x]
    return x


FIELDS = {
    'literal': {'bytes', 'value', 'code'}, 'scan': {'first', 'rest', 'stop', 'eof', 'min', 'max', 'code', 'codec'},
    'take': {'length', 'max', 'code', 'allowed'}, 'atom': {'codec'}, 'seq': {'steps', 'result', 'rebase_errors', 'span_end'},
    'choice': {'branches', 'code'}, 'repeat': {'body', 'stop', 'eof', 'max', 'count', 'occurrence_limit'},
    'end': set(), 'check': {'test', 'code', 'site'}, 'value': {'expr'},
    'map': {'source', 'body'}, 'emit': {'codec', 'expr', 'escapes'},
    'each': {'source', 'body'}, 'dispatch': {'expr', 'branches'},
    'unique': {'source', 'field', 'code'},
    'call': {'rule'},
    'bytes_check': {'source', 'allowed', 'code'},
    'select': {'source', 'test'},
}
REQUIRED = {
    'literal': {'bytes'}, 'scan': {'first', 'rest', 'stop', 'eof', 'min', 'max', 'code'},
    'take': {'length', 'max', 'code'}, 'atom': {'codec'}, 'seq': {'steps', 'result'},
    'choice': {'branches', 'code'}, 'repeat': {'body', 'stop', 'eof', 'max', 'occurrence_limit'},
    'end': set(), 'check': {'test', 'code', 'site'}, 'value': {'expr'},
    'map': {'source', 'body'}, 'emit': {'codec', 'expr'}, 'each': {'source', 'body'},
    'dispatch': {'expr', 'branches'}, 'unique': {'source', 'field', 'code'},
    'call': {'rule'},
    'bytes_check': {'source', 'allowed', 'code'},
    'select': {'source', 'test'},
}
EXPRS = {'ref': 1, 'const': 1, 'record': 1, 'decode': 2, 'join': 1,
         'length': 1, 'add': 2, 'eq': 2, 'le': 2, 'nonempty': 1,
         'input_length': 0, 'output_length': 0}
CODECS = {'ascii', 'decimal15', 'uint8', 'uint16be', 'bytes'}
DEFAULT_LIMITS = dict(input=4096, output=4096, work=100000, depth=16, occurrences=8)


def validate(plan):
    """Closed shapes, earlier bindings, selector disjointness and progress checks."""
    if not isinstance(plan, dict) or set(plan) != {'version', 'text', 'rules', 'decode', 'encode'}:
        raise PlanError('plan shape')
    if plan['version'] != 'semantic-plan-1' or type(plan['text']) is not bool:
        raise PlanError('version/text')
    ids = set()
    active = set()
    count = 0
    rules_active = set()
    visited = set()
    expressions = 0

    def expression(e, env):
        nonlocal expressions
        expressions += 1
        if expressions > 2048:
            raise PlanError('expression bound')
        if not isinstance(e, dict) or len(e) != 1:
            raise PlanError('expression shape')
        op, args = next(iter(e.items()))
        if op not in EXPRS:
            raise PlanError('unknown expression')
        if op == 'ref':
            if not isinstance(args, str) or len(args) > 256 or args.split('.')[0] not in env:
                raise PlanError('undeclared dependency')
        elif op == 'const':
            if not (args is None or type(args) in (str, int, bool)):
                raise PlanError('literal domain')
            if type(args) is str and len(args) > 4096:
                raise PlanError('literal bound')
            if type(args) is int and not -(2**63) <= args < 2**63:
                raise PlanError('integer literal domain')
        elif op == 'record':
            if not isinstance(args, dict):
                raise PlanError('record fields')
            for v in args.values():
                expression(v, env)
        elif op in ('input_length', 'output_length'):
            if args is not None:
                raise PlanError('nullary expression')
        elif op == 'decode':
            if not isinstance(args, list) or len(args) != 2 or args[0] not in CODECS:
                raise PlanError('codec')
            expression(args[1], env)
        elif EXPRS[op] == 1:
            expression(args, env)
        else:
            if not isinstance(args, list) or len(args) != EXPRS[op]:
                raise PlanError('expression arity')
            for v in args:
                expression(v, env)

    def prefixes(values):
        if not isinstance(values, list):
            raise PlanError('prefix list')
        for p in values:
            if not isinstance(p, list) or not 1 <= len(p) <= 8 or any(type(b) is not int or not 0 <= b <= 255 for b in p):
                raise PlanError('prefix bytes')
        for i, a in enumerate(values):
            for b in values[i + 1:]:
                if a[:len(b)] == b or b[:len(a)] == a:
                    raise PlanError('ambiguous selectors')

    def walk(n, env):
        nonlocal count
        if not isinstance(n, dict) or id(n) in active:
            raise PlanError('cyclic/non-node plan')
        op = n.get('op')
        if op not in FIELDS or not {'id', 'op'} | REQUIRED[op] <= n.keys() or set(n) - ({'id', 'op'} | FIELDS[op]):
            raise PlanError('unknown operation/shape')
        if not isinstance(n['id'], str) or not n['id'] or (n['id'] in ids and id(n) not in visited):
            raise PlanError('node id')
        ids.add(n['id'])
        if id(n) not in visited:
            count += 1; visited.add(id(n))
        if count > 64 or len(active) >= 16:
            raise PlanError('plan size/depth')
        active.add(id(n))
        for key in ('length', 'expr', 'test', 'site', 'source'):
            if key in n:
                expression(n[key], env | {'item'} if op == 'select' and key == 'test' else env)
        for key in ('max', 'min'):
            if key in n and (type(n[key]) is not int or not 0 <= n[key] <= 4096):
                raise PlanError('bound')
        progress = 0
        if op == 'seq':
            if 'rebase_errors' in n and (not isinstance(n['rebase_errors'], list) or any(type(c) is not str for c in n['rebase_errors'])):
                raise PlanError('error rebasing')
            local = set(env)
            if not isinstance(n['steps'], list):
                raise PlanError('steps')
            for step in n['steps']:
                if not isinstance(step, dict) or set(step) not in ({'node'}, {'node', 'bind'}):
                    raise PlanError('step shape')
                progress += walk(step['node'], local)
                if 'bind' in step:
                    name = step['bind']
                    if not isinstance(name, str) or not name.isidentifier() or name in local:
                        raise PlanError('shadowed binding')
                    local.add(name)
            expression(n['result'], local)
            if 'span_end' in n:
                expression(n['span_end'], local)
        elif op == 'literal':
            if not isinstance(n['bytes'], list) or len(n['bytes']) > 4096 or any(type(b) is not int or not 0 <= b <= 255 for b in n['bytes']):
                raise PlanError('literal bytes')
            progress = len(n['bytes'])
            if 'value' in n:
                expression(n['value'], env)
        elif op == 'scan':
            for key in ('first', 'rest', 'stop'):
                if not isinstance(n[key], list) or len(n[key]) > 256 or any(type(b) is not int or not 0 <= b <= 255 for b in n[key]):
                    raise PlanError('byte class')
            if set(n['rest']) & set(n['stop']) or set(n['first']) & set(n['stop']) or type(n['eof']) is not bool or n['min'] > n['max']:
                raise PlanError('scan classes')
            progress = n['min']
            if 'codec' in n and (n['codec'] != 'decimal15' or set(n['first']) != set(range(48,58)) or set(n['rest']) != set(range(48,58))):
                raise PlanError('scan codec')
        elif op == 'take':
            if 'allowed' in n and (not isinstance(n['allowed'], list) or len(n['allowed']) > 256 or any(type(b) is not int or not 0 <= b <= 255 for b in n['allowed'])):
                raise PlanError('take byte class')
        elif op == 'choice':
            ps = []
            if not isinstance(n['branches'], list) or not n['branches']:
                raise PlanError('choice branches')
            for b in n['branches']:
                if set(b) != {'prefixes', 'node'}:
                    raise PlanError('branch shape')
                ps.extend(b['prefixes'])
            prefixes(ps)
            progress = min(walk(b['node'], env) for b in n['branches'])
        elif op == 'repeat':
            prefixes(n['stop'])
            if type(n['eof']) is not bool or type(n['occurrence_limit']) is not bool or walk(n['body'], env) < 1:
                raise PlanError('nonconsuming repeat')
            if 'count' in n:
                expression(n['count'], env)
        elif op in ('map', 'each'):
            walk(n['body'], env | {'item', 'prefix'})
        elif op == 'bytes_check':
            if not isinstance(n['allowed'], list) or any(type(b) is not int or not 0 <= b <= 255 for b in n['allowed']):
                raise PlanError('allowed bytes')
        elif op == 'dispatch':
            if not isinstance(n['branches'], dict) or not n['branches']:
                raise PlanError('dispatch branches')
            for b in n['branches'].values():
                walk(b, env)
        elif op == 'atom':
            if n['codec'] not in {'uint8', 'uint16be'}:
                raise PlanError('fixed atom codec')
            progress = 1 if n['codec'] == 'uint8' else 2
        elif op == 'call':
            rule = n['rule']
            if rule not in plan['rules'] or rule in rules_active:
                raise PlanError('unknown/cyclic rule')
            rules_active.add(rule)
            progress = walk(plan['rules'][rule], set())
            rules_active.remove(rule)
        elif op == 'emit':
            if n['codec'] not in CODECS:
                raise PlanError('unknown codec')
            if 'escapes' in n:
                for char, spelling in n['escapes'].items():
                    if len(char) != 1 or ord(char) > 127 or not isinstance(spelling, str) or not 1 <= len(spelling) <= 8 or any(ord(c) > 127 for c in spelling):
                        raise PlanError('escape table')
        active.remove(id(n))
        return progress

    if not isinstance(plan['rules'], dict):
        raise PlanError('rules')
    # Even unused definitions must be valid and count toward the 64-node limit.
    for rule in plan['rules']:
        rules_active.add(rule)
        walk(plan['rules'][rule], set())
        rules_active.remove(rule)
    walk(plan['decode'], set())
    walk(plan['encode'], {'root'})
    return count


class Machine:
    def __init__(self, data, limits, rules=None):
        self.data = data; self.i = 0; self.work = 0; self.out = bytearray()
        self.limits = limits; self.spans = []; self.node = 'preflight'
        self.rules = rules or {}

    def fail(self, code, site=None, stage='structure', path=None, expected=()):
        raise Rejection(code, self.i if site is None else site, self.node, stage, path, expected)

    def charge(self, site=None):
        if self.work == self.limits['work']:
            self.fail('WORK_LIMIT', site, 'limit')
        self.work += 1

    def look(self, prefix):
        for j, b in enumerate(prefix):
            if self.i + j == len(self.data):
                return False
            self.charge(self.i + j)
            if self.data[self.i + j] != b:
                return False
        return True

    def expr(self, e, env):
        self.charge()
        op, args = next(iter(e.items()))
        if op == 'ref':
            parts = args.split('.'); x = env[parts[0]]
            for key in parts[1:]:
                x = x.value if isinstance(x, Cell) else x
                x = x[key]
            return x
        if op == 'const':
            return Cell(args, self.i, self.i)
        if op == 'record':
            return Cell({k: self.expr(v, env) for k, v in args.items()}, self.i, self.i)
        if op in ('input_length', 'output_length'):
            return Cell(len(self.data) if op == 'input_length' else len(self.out), self.i, self.i)
        if op == 'decode':
            x = self.expr(args[1], env)
            return self.decode(args[0], x)
        if op == 'join':
            x = self.expr(args, env); values = x.value
            value = ''; origins = []
            for c in values:
                self.charge(c.start)
                s = c.value
                if isinstance(s, bytes):
                    c = self.decode('ascii', c); s = c.value
                if not isinstance(s, str):
                    self.fail('TYPE', c.start)
                if len(value) + len(s) > 256:
                    self.fail('BOUND', c.start)
                value += s; origins.extend(c.origins or (c.start,) * len(s))
            return Cell(value, x.start, x.end, tuple(origins))
        if EXPRS[op] == 1:
            x = self.expr(args, env); a = plain(x)
            v = len(a) if op == 'length' else len(a) > 0
        else:
            x = self.expr(args[0], env); y = self.expr(args[1], env)
            a, b = plain(x), plain(y)
            if op == 'add':
                if type(a) is not int or type(b) is not int:
                    self.fail('TYPE', x.start)
                v = a + b
                if not -(2**63) <= v < 2**63:
                    self.fail('OVERFLOW', x.start)
            elif op == 'eq':
                v = type(a) is type(b) and a == b
            else:
                if type(a) is not type(b) or type(a) not in (int, str):
                    self.fail('TYPE', x.start)
                v = a <= b
        return Cell(v, x.start, x.end)

    def decode(self, codec, x):
        a = plain(x)
        if codec == 'decimal15':
            if not isinstance(a, (str, bytes)) or not a:
                self.fail('DECIMAL', x.start, 'conversion')
            v = 0
            for j, c in enumerate(a):
                site = x.origins[j] if x.origins else x.start + j
                self.charge(site); self.charge(site)
                d = ord(c) if isinstance(c, str) else c
                if not 48 <= d <= 57:
                    self.fail('DECIMAL', site, 'conversion')
                v = v * 10 + d - 48
                if v > 32767:
                    self.fail('OVERFLOW', site, 'conversion')
            return Cell(v, x.start, x.end)
        if codec == 'ascii':
            if not isinstance(a, bytes):
                self.fail('TYPE', x.start)
            s = ''
            for j, b in enumerate(a):
                self.charge(x.start + j)
                if b > 127:
                    self.fail('ENCODING', x.start + j)
                s += chr(b)
            return Cell(s, x.start, x.end, x.origins)
        if codec == 'bytes':
            if not isinstance(a, bytes):
                self.fail('TYPE', x.start)
            return x
        width = 1 if codec == 'uint8' else 2
        if not isinstance(a, bytes) or len(a) != width:
            self.fail('TYPE', x.start)
        v = 0
        for b in a:
            self.charge(x.start); v = v * 256 + b
        return Cell(v, x.start, x.end)

    def encode(self, codec, x, escapes):
        a = plain(x)
        if codec in ('uint8', 'uint16be', 'decimal15'):
            maximum = {'uint8': 255, 'uint16be': 65535, 'decimal15': 32767}[codec]
            if type(a) is not int or not 0 <= a <= maximum:
                self.fail('ENCODE_RANGE', None, 'encode', 'value')
            if codec == 'uint8':
                return bytes([a])
            if codec == 'uint16be':
                return bytes([a // 256, a % 256])
            digits = []
            while True:
                self.charge(None); digits.append(48 + a % 10); a //= 10
                if not a:
                    return bytes(reversed(digits))
        if codec == 'bytes':
            if not isinstance(a, bytes):
                self.fail('TYPE', None, 'encode', 'value')
            return a
        if not isinstance(a, str):
            self.fail('TYPE', None, 'encode', 'value')
        out = bytearray()
        for c in a:
            self.charge()
            if ord(c) > 127:
                self.fail('ENCODING', None, 'encode', 'value')
            for d in escapes.get(c, c):
                out.append(ord(d))
        return bytes(out)

    def run(self, n, env, depth=1):
        previous = self.node; self.node = n['id']; self.charge()
        if depth > self.limits['depth']:
            self.fail('DEPTH_LIMIT', stage='limit')
        start = self.i; op = n['op']
        result = None
        if op == 'literal':
            for b in n['bytes']:
                if self.i == len(self.data):
                    self.fail('TRUNCATED')
                self.charge()
                if self.data[self.i] != b:
                    self.fail(n.get('code', 'SYNTAX'), expected=[f'{b:02x}'])
                self.i += 1
            result = self.expr(n['value'], env) if 'value' in n else Cell(bytes(n['bytes']), start, self.i)
        elif op == 'scan':
            numeric = 0
            while True:
                if self.i == len(self.data):
                    if not n['eof']:
                        self.fail('TRUNCATED')
                    break
                self.charge(); b = self.data[self.i]
                if b in n['stop']:
                    break
                if b not in (n['first'] if self.i == start else n['rest']):
                    self.fail(n['code'])
                if self.i - start == n['max']:
                    self.fail('BOUND')
                if 'codec' in n:
                    self.charge()
                    numeric = numeric * 10 + b - 48
                    if numeric > 32767:
                        self.fail('OVERFLOW', stage='conversion')
                self.i += 1
            if self.i - start < n['min']:
                self.fail(n['code'])
            result = Cell(self.data[start:self.i], start, self.i, tuple(range(start, self.i)))
            if 'codec' in n:
                result = Cell(numeric, start, self.i)
        elif op in ('take', 'atom'):
            if op == 'take':
                x = self.expr(n['length'], env); k = plain(x)
                if type(k) is not int or not 0 <= k <= n['max']:
                    self.fail('BOUND', x.start)
            else:
                k = 1 if n['codec'] == 'uint8' else 2
            for _ in range(k):
                if self.i == len(self.data):
                    self.fail('TRUNCATED')
                self.charge()
                if op == 'take' and 'allowed' in n and self.data[self.i] not in n['allowed']:
                    self.fail(n['code'])
                self.i += 1
            result = Cell(self.data[start:self.i], start, self.i, tuple(range(start, self.i)))
            if op == 'atom':
                result = self.decode(n['codec'], result)
        elif op == 'seq':
            local = dict(env)
            for s in n['steps']:
                try:
                    v = self.run(s['node'], local, depth + 1)
                except Rejection as e:
                    if e.error['code'] in n.get('rebase_errors', []):
                        e.error['offset'] = start
                    raise
                if 'bind' in s:
                    local[s['bind']] = v
            result = self.expr(n['result'], local)
            span_end = self.expr(n['span_end'], local).end if 'span_end' in n else self.i
        elif op == 'choice':
            chosen = None
            for b in n['branches']:
                if any(self.look(p) for p in b['prefixes']):
                    chosen = b['node']; break
            if chosen is None:
                self.fail('TRUNCATED' if self.i == len(self.data) else n['code'], expected=[''.join(f'{b:02x}' for b in p) for branch in n['branches'] for p in branch['prefixes']])
            result = self.run(chosen, env, depth + 1)
        elif op == 'repeat':
            values = []; count = None
            if 'count' in n:
                x = self.expr(n['count'], env); count = plain(x)
                if type(count) is not int or not 0 <= count <= min(n['max'], self.limits['occurrences']):
                    self.fail('BOUND', x.start)
            while True:
                if count is not None:
                    if len(values) == count:
                        break
                elif (n['eof'] and self.i == len(self.data)) or any(self.look(p) for p in n['stop']):
                    break
                if len(values) == n['max'] or (n['occurrence_limit'] and len(values) == self.limits['occurrences']):
                    self.fail('OCCURRENCE_LIMIT', stage='limit')
                value = self.run(n['body'], env, depth + 1)
                self.charge(); values.append(value)
            result = Cell(values, start, self.i)
        elif op == 'end':
            if self.i != len(self.data):
                self.fail('TRAILING')
        elif op == 'check':
            if plain(self.expr(n['test'], env)) is not True:
                self.fail(n['code'], self.expr(n['site'], env).start, 'validation')
        elif op == 'value':
            result = self.expr(n['expr'], env)
        elif op in ('map', 'each'):
            x = self.expr(n['source'], env)
            if not isinstance(x.value, list) or len(x.value) > self.limits['occurrences']:
                self.fail('OCCURRENCE_LIMIT', x.start, 'limit')
            values = []
            prefix = []
            for item in x.value:
                prefix.append(item)
                values.append(self.run(n['body'], {**env, 'item': item, 'prefix': Cell(list(prefix), x.start, item.end)}, depth + 1))
            result = Cell(values, x.start, x.end)
        elif op == 'bytes_check':
            x = self.expr(n['source'], env)
            for j, b in enumerate(x.value):
                self.charge(x.start + j)
                if b not in n['allowed']:
                    self.fail(n['code'], x.start + j, 'validation')
        elif op == 'select':
            x = self.expr(n['source'], env)
            if not isinstance(x.value, list) or len(x.value) > self.limits['occurrences']:
                self.fail('OCCURRENCE_LIMIT', x.start, 'limit')
            values = []
            for item in x.value:
                if plain(self.expr(n['test'], {**env, 'item':item})) is True:
                    self.charge(item.start); values.append(item)
            result = Cell(values, x.start, x.end)
        elif op == 'unique':
            x = self.expr(n['source'], env); seen = []
            for row in x.value:
                c = row.value[n['field']]; key = plain(c)
                self.charge(c.start)
                for earlier in seen:
                    self.charge(c.start)
                    if key == earlier:
                        self.fail(n['code'], c.start, 'validation')
                seen.append(key)
        elif op == 'emit':
            value = self.encode(n['codec'], self.expr(n['expr'], env), n.get('escapes', {}))
            at = len(self.out)
            for b in value:
                self.charge()
                if len(self.out) == self.limits['output']:
                    self.fail('OUTPUT_LIMIT', stage='limit')
                self.out.append(b)
            self.spans.append(dict(node=n['id'], start=at, end=len(self.out)))
        elif op == 'dispatch':
            key = plain(self.expr(n['expr'], env))
            if type(key) is bool:
                key = str(key)
            if key not in n['branches']:
                self.fail('TAG', stage='encode', path='tag')
            result = self.run(n['branches'][key], env, depth + 1)
        elif op == 'call':
            result = self.run(self.rules[n['rule']], {}, depth + 1)
        if result is None:
            result = Cell(None, start, self.i)
        # Literal projections and seq records acquire actual consumed spans.
        if op in ('literal', 'seq'):
            result = Cell(result.value, start, span_end if op == 'seq' else self.i, result.origins or ((start,) * len(result.value) if isinstance(result.value, str) else ()))
        self.node = previous
        return result


def execute(plan, data, limits=None, assemble=True):
    try:
        validate(plan)
    except (PlanError, TypeError, KeyError, RecursionError, ValueError, AttributeError, IndexError):
        return dict(status='plan_reject', error={'code': 'PLAN'}, work=0)
    l = dict(DEFAULT_LIMITS)
    if limits:
        if set(limits) - set(l) or any(type(v) is not int or not 0 <= v <= DEFAULT_LIMITS[k] for k, v in limits.items()):
            return dict(status='plan_reject', error={'code': 'LIMIT_VECTOR'}, work=0)
        l.update(limits)
    if not isinstance(data, bytes):
        return dict(status='plan_reject', error={'code': 'INPUT_TYPE'}, work=0)
    m = Machine(data, l, plan['rules'])
    try:
        if len(data) > l['input']:
            m.fail('INPUT_LIMIT', l['input'], 'limit')
        if plan['text']:
            for j, b in enumerate(data):
                m.charge(j)
                if b > 127:
                    m.fail('ENCODING', j, 'preflight')
        result = m.run(plan['decode'], {})
        if assemble:
            m.run(plan['encode'], {'root': result})
        return dict(status='success', value=plain(result), provenance=provenance(result),
                    consumed=m.i, work=m.work, output=bytes(m.out), output_spans=m.spans)
    except Rejection as e:
        if e.error['stage'] == 'encode':
            e.error['offset'] = None
        return dict(status='reject', error=e.error, work=m.work)
    except (TypeError, KeyError, AttributeError, IndexError):
        return dict(status='reject', error=dict(code='TYPE', offset=m.i, node=m.node,
                                               stage='typing', path=None), work=m.work)


def provenance(c):
    v = c.value
    result = dict(span=[c.start, c.end], origins=list(c.origins))
    if isinstance(v, dict):
        result['fields'] = {k: provenance(x) for k, x in v.items()}
    elif isinstance(v, list):
        result['items'] = [provenance(x) for x in v]
    return result
