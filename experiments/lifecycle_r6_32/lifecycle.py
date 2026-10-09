"""External lifecycle plumbing over frozen R6.18; no execution primitives."""
import copy
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import sys
import time
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'experiments/typed_composition_r6_18'))
import composition as c


def digest(value):
    return hashlib.sha256(c.canonical(value)).hexdigest()


def reject(code, detail):
    c.fail(code, '$/lifecycle', detail)


def publish(path, value, interrupt=False):
    """Flush a staging file, then install with no-clobber hard link."""
    path = Path(path)
    pending = path.with_name(path.name + '.pending')
    with pending.open('xb') as stream:
        stream.write(c.canonical(value))
        stream.flush()
        os.fsync(stream.fileno())
    if interrupt:
        raise InterruptedError('injected after fsync, before commit')
    os.link(pending, path)  # atomic name installation; never replaces old bytes
    pending.unlink()


class Journal:
    """Single-writer durable immutable event files; strict hash-chain recovery."""
    def __init__(self, path):
        self.path = Path(path)
        self.path.mkdir(parents=True, exist_ok=True)

    def recover(self):
        events, previous = [], None
        starts, ends = {}, {}
        for index, path in enumerate(sorted(self.path.glob('*.json')), 1):
            event = json.loads(path.read_text())
            body = {k: v for k, v in event.items() if k != 'identity'}
            if (event['sequence'] != index or event['previous'] != previous
                    or event['identity'] != digest(body) or path.name != f'{index:06}.json'):
                reject('TELEMETRY_INTEGRITY', path.name)
            events.append(event)
            previous = event['identity']
            if event['kind'] == 'start':
                stage = event['data']['stage']
                if stage in starts:
                    reject('TELEMETRY_STAGE', 'duplicate start: ' + stage)
                starts[stage] = event
            if event['kind'] == 'complete':
                stage = event['data']['stage']
                if stage not in starts or stage in ends:
                    reject('TELEMETRY_STAGE', 'orphan/duplicate completion: ' + stage)
                ends[stage] = event
        return dict(events=events, completed=sorted(ends),
                    incomplete=sorted(set(starts) - set(ends)),
                    pending=sorted(p.name for p in self.path.glob('*.pending')))

    def record(self, kind, data, interrupt=False):
        recovered = self.recover()
        if recovered['pending']:
            reject('INCOMPLETE_WRITE', 'explicit recovery required; pending bytes retained')
        events = recovered['events']
        if kind == 'start' and any(e['kind'] == 'start' and e['data']['stage'] == data['stage'] for e in events):
            reject('TELEMETRY_STAGE', 'duplicate stage start')
        if kind == 'complete' and (data['stage'] not in recovered['incomplete']):
            reject('TELEMETRY_STAGE', 'completion requires exactly one open stage')
        body = dict(sequence=len(events) + 1, previous=events[-1]['identity'] if events else None,
                    utc=datetime.now(timezone.utc).isoformat(), kind=kind, data=data)
        event = dict(body, identity=digest(body))
        publish(self.path / f'{len(events) + 1:06}.json', event, interrupt)
        return event

    @contextmanager
    def stage(self, name, inputs):
        self.record('start', dict(stage=name, inputs=inputs))
        start = time.perf_counter()
        try:
            yield
        except BaseException as exc:
            self.record('error', dict(stage=name, exception=type(exc).__name__, diagnostic=str(exc),
                                      wall_seconds=time.perf_counter() - start))
            raise
        else:
            self.record('complete', dict(stage=name, wall_seconds=time.perf_counter() - start))


class Registry:
    def __init__(self, path, journal=None):
        self.path = Path(path)
        self.path.mkdir(parents=True, exist_ok=True)
        self.journal = journal

    def read(self):
        previous, state = None, dict(definitions={}, successors={}, migrations=[])
        paths = sorted(self.path.glob('*.json'))
        for index, path in enumerate(paths, 1):
            record = json.loads(path.read_text())
            body = {k: v for k, v in record.items() if k != 'identity'}
            if (record['generation'] != index or record['previous'] != previous
                    or digest(body) != record['identity'] or path.name != f'{index:06}.json'):
                reject('REGISTRY_INTEGRITY', path.name)
            next_state = record['state']
            for pin, definition in next_state['definitions'].items():
                if pin != c.identity(definition) or pin != definition['identity']:
                    reject('IDENTITY', pin)
            for pin, definition in state['definitions'].items():
                if next_state['definitions'].get(pin) != definition:
                    reject('UNAUTHORIZED_MUTATION', pin)
            for pin, predecessor in state['successors'].items():
                if next_state['successors'].get(pin) != predecessor:
                    reject('UNAUTHORIZED_MUTATION', 'supersession')
            if next_state['migrations'][:len(state['migrations'])] != state['migrations']:
                reject('UNAUTHORIZED_MUTATION', 'migration history')
            state, previous = next_state, record['identity']
        return dict(token=previous, generation=len(paths), state=state,
                    pending=sorted(p.name for p in self.path.glob('*.pending')))

    @contextmanager
    def locked(self):
        lock = self.path / 'writer.lock'
        try:
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            reject('WRITER_BUSY', 'single writer or explicit post-interruption recovery required')
        try:
            os.close(fd)
            yield
        finally:
            lock.unlink()

    def commit(self, state, expected, operation, interrupt=False):
        with self.locked():
            current = self.read()
            if current['pending']:
                reject('INCOMPLETE_WRITE', 'pending bytes retained; use new recovery branch')
            if current['token'] != expected:
                reject('STALE_READ', 'exact generation token required')
            for pin, definition in current['state']['definitions'].items():
                if state['definitions'].get(pin) != definition:
                    reject('UNAUTHORIZED_MUTATION', pin)
            for pin, definition in state['definitions'].items():
                if pin != definition['identity'] or pin != c.identity(definition):
                    reject('IDENTITY', pin)
            for pin, predecessor in current['state']['successors'].items():
                if state['successors'].get(pin) != predecessor:
                    reject('UNAUTHORIZED_MUTATION', 'supersession')
            if state['migrations'][:len(current['state']['migrations'])] != current['state']['migrations']:
                reject('UNAUTHORIZED_MUTATION', 'migration history')
            body = dict(generation=current['generation'] + 1, previous=expected,
                        operation=operation, state=state)
            record = dict(body, identity=digest(body))
            publish(self.path / f"{body['generation']:06}.json", record, interrupt)
        return record['identity']

    def closure(self, root, definitions):
        found, active, names = {}, set(), {}

        def walk(pin):
            if pin in active:
                reject('CYCLE', pin)
            if pin in found:
                return
            if pin not in definitions:
                reject('MISSING_DEPENDENCY', pin)
            d = definitions[pin]
            if d['name'] in names and names[d['name']] != pin:
                reject('AMBIGUOUS_REFERENCE', d['name'])
            names[d['name']] = pin
            if len(names) > 8:
                reject('EXPANSION_LIMIT', 'at most eight definitions in admission closure')
            active.add(pin)
            for name, target in sorted(d['dependencies'].items()):
                if target not in definitions:
                    reject('MISSING_DEPENDENCY', target)
                if definitions[target]['name'] != name:
                    reject('IDENTITY', 'dependency name/pin mismatch')
                walk(target)
            active.remove(pin)
            found[pin] = d

        walk(root)
        return [found[p] for p in sorted(found)]

    def probe(self, definition, definitions, budget):
        closure = self.closure(definition['identity'], definitions)
        for p in definition['params']:
            c.typename(p['type'], '$/params')
        args = {p['name']: {'const': {'Int64': 0, 'Bool': False, 'Unit': None}[p['type']]}
                for p in definition['params']}
        probe = c.seal(dict(name='AdmissionProbe', revision=1, params=[],
            dependencies={definition['name']: definition['identity']},
            steps=[dict(id='call', type=definition['result_type'], deps=[],
                node=dict(op='compose', symbol=definition['name'], identity=definition['identity'], args=args))],
            order=['call'], result={'const': 0}, result_type='Int64'))
        return c.expand(dict(version=c.VERSION, foundation=c.FOUNDATION,
                             definitions=closure, program=probe), budget)

    def admit(self, proposals, expected, predecessor=None, budget=64, interrupt=False):
        started = time.perf_counter()
        try:
            current = self.read()
            if expected != current['token']:
                reject('STALE_READ', 'admission input token')
            state = copy.deepcopy(current['state'])
            if type(proposals) is not list or not 1 <= len(proposals) <= 8:
                reject('SCHEMA', 'one to eight exact R6.18 definitions required')
            for d in proposals:
                c._tree_bound(d)
                c.shape(d, {'name', 'revision', 'identity', 'params', 'dependencies', 'steps',
                            'order', 'result', 'result_type'}, '$/proposal')
                c.digest(d['identity'], '$/proposal')
                c.name(d['name'], '$/proposal/name')
                c.typename(d['result_type'], '$/proposal/result_type')
                if type(d['params']) is not list or len(d['params']) > 8:
                    reject('SHAPE', 'at most eight exact parameters required')
                for p in d['params']:
                    c.shape(p, {'name', 'type'}, '$/proposal/params')
                    c.name(p['name'], '$/proposal/params')
                    c.typename(p['type'], '$/proposal/params')
                if type(d['dependencies']) is not dict or len(d['dependencies']) > 8:
                    reject('SHAPE', 'exact dependency map required')
                for name, pin in d['dependencies'].items():
                    c.name(name, '$/proposal/dependencies')
                    c.digest(pin, '$/proposal/dependencies')
                if d['identity'] in state['definitions']:
                    reject('DUPLICATE_IDENTITY', d['identity'])
                state['definitions'][d['identity']] = copy.deepcopy(d)
            # Graph rejection precedes canonical identity checks, including deliberately
            # forged cyclic candidates (true self-pinned SHA256 cycles are infeasible).
            for d in proposals:
                self.closure(d['identity'], state['definitions'])
                if c.identity(d) != d['identity']:
                    reject('IDENTITY', 'content mismatch')
            expanded = [self.probe(d, state['definitions'], budget) for d in proposals]
            if predecessor is not None:
                if len(proposals) != 1 or predecessor not in current['state']['definitions']:
                    reject('INVALID_SUCCESSOR', 'exact admitted predecessor required')
                old, new = current['state']['definitions'][predecessor], proposals[0]
                if (old['name'], old['params'], old['result_type']) != (new['name'], new['params'], new['result_type']):
                    reject('TYPE_CHANGE', 'successor must preserve exact name and signature')
                state['successors'][new['identity']] = predecessor
            token = self.commit(state, expected, dict(kind='admit', pins=[d['identity'] for d in proposals]), interrupt)
            result = dict(status='accepted', token=token, pins=[d['identity'] for d in proposals],
                          nodes=[e['nodes'] for e in expanded])
        except (c.Diagnostic, InterruptedError) as exc:
            if self.journal:
                self.journal.record('admission', dict(proposals=proposals, expected=expected,
                    predecessor=predecessor, status='rejected', diagnostic=getattr(exc, 'data', str(exc)),
                    tool_seconds=time.perf_counter() - started))
            raise
        if self.journal:
            self.journal.record('admission', dict(proposals=proposals, expected=expected,
                predecessor=predecessor, result=result, tool_seconds=time.perf_counter() - started))
        return result

    def retrieve(self, pin=None, name=None, signature=None, expected=None):
        started = time.perf_counter()
        if pin is not None and (name is not None or signature is not None):
            reject('AMBIGUOUS_REFERENCE', 'choose exact pin or search filters')
        current = self.read()
        if expected is not None and current['token'] != expected:
            reject('STALE_READ', 'retrieval token')
        definitions = current['state']['definitions']
        if pin is not None:
            c.digest(pin, '$/retrieve')
            if pin not in definitions:
                reject('MISSING_DEPENDENCY', pin)
            result = self.closure(pin, definitions)
        else:
            result = [definitions[p] for p in sorted(definitions)
                if (name is None or definitions[p]['name'] == name)
                and (signature is None or [definitions[p]['params'], definitions[p]['result_type']] == signature)]
        if self.journal:
            self.journal.record('retrieval', dict(pin=pin, name=name, signature=signature,
                token=current['token'], identities=[d['identity'] for d in result],
                bytes=len(c.canonical(result)), tool_seconds=time.perf_counter() - started))
        return copy.deepcopy(result)

    def resolve(self, name):
        result = self.retrieve(name=name)
        if len(result) != 1:
            reject('AMBIGUOUS_REFERENCE', name)
        return result[0]

    def dependents(self, pin):
        definitions = self.read()['state']['definitions']
        direct = sorted(p for p, d in definitions.items() if pin in d['dependencies'].values())
        all_users = set(direct)
        while True:
            users = {p for p, d in definitions.items() if set(d['dependencies'].values()) & all_users}
            if users <= all_users:
                break
            all_users |= users
        return dict(direct=direct, transitive=sorted(all_users))

    def migrate(self, predecessor, successor, decisions, expected):
        current = self.read()
        state = copy.deepcopy(current['state'])
        if state['successors'].get(successor) != predecessor:
            reject('INVALID_SUCCESSOR', 'no admitted supersession edge')
        required = self.dependents(predecessor)['direct']
        if type(decisions) is not dict or set(decisions) != set(required):
            reject('PARTIAL_MIGRATION', 'explicit update or retain for every direct caller required')
        for old, new in sorted(decisions.items()):
            if new is None:
                continue
            if state['successors'].get(new) != old:
                reject('INVALID_MIGRATION', 'caller successor edge required')
            caller = copy.deepcopy(state['definitions'][old])
            for name, pin in caller['dependencies'].items():
                if pin == predecessor:
                    caller['dependencies'][name] = successor
            for step in caller['steps']:
                if step['node'].get('identity') == predecessor:
                    step['node']['identity'] = successor
            caller = c.seal(caller)
            if caller != state['definitions'][new]:
                reject('INVALID_MIGRATION', 'only exact selected caller pin updates permitted')
        state['migrations'].append(dict(predecessor=predecessor, successor=successor,
                                        decisions=decisions))
        token = self.commit(state, expected, dict(kind='migration', decisions=decisions))
        if self.journal:
            self.journal.record('migration', dict(predecessor=predecessor, successor=successor,
                decisions=decisions, input_token=expected, output_token=token))
        return token
