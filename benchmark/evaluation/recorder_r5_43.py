"""Versioned canonical evidence and fail-closed locked observation recorder."""

import hashlib
import json
import math
from pathlib import Path

PROTOCOL = 'lykoi-canonical-evidence-r5.43'


class ProtocolFailure(ValueError):
    pass


def canonical(value):
    """Return detached, immutable protocol bytes; reject lossy JSON inputs."""
    active = set()

    def tree(item):
        kind = type(item)
        if item is None or kind in (str, bool, int):
            return item
        if kind is float:
            if not math.isfinite(item):
                raise ProtocolFailure('non-finite evidence number')
            return item
        if kind not in (dict, list, tuple):
            raise ProtocolFailure('unsupported evidence type')
        if id(item) in active:
            raise ProtocolFailure('cyclic evidence')
        active.add(id(item))
        try:
            if kind is dict:
                if any(type(key) is not str for key in item):
                    raise ProtocolFailure('evidence keys must be strings')
                return {key: tree(child) for key, child in item.items()}
            return [tree(child) for child in item]
        finally:
            active.remove(id(item))

    try:
        return json.dumps(tree(value), sort_keys=True, ensure_ascii=True,
                          separators=(',', ':'), allow_nan=False).encode('utf-8')
    except (RecursionError, TypeError, ValueError) as exc:
        raise ProtocolFailure(str(exc)) from exc


def digest(content):
    return hashlib.sha256(content).hexdigest()


def loads(content):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ProtocolFailure('duplicate evidence key')
            result[key] = value
        return result

    def constant(value):
        raise ProtocolFailure('invalid JSON constant: ' + value)

    try:
        value = json.loads(content.decode('utf-8'), object_pairs_hook=pairs,
                           parse_constant=constant)
        canonical(value)
        return value
    except (UnicodeError, ValueError, RecursionError) as exc:
        raise ProtocolFailure('corrupt persisted evidence: ' + str(exc)) from exc


def equivalent(left, right):
    return canonical(left) == canonical(right)


def persist(path, value):
    content = canonical(value) + b'\n'
    with Path(path).open('xb') as stream:
        stream.write(content)
        stream.flush()
        # A receipt is not reported until its write is flushed to the OS.
        import os
        os.fsync(stream.fileno())


class Recorder:
    def __init__(self, directory):
        self.directory = Path(directory)

    def path(self, name):
        return self.directory / (name + '.json')

    def read(self, name):
        return loads(self.path(name).read_bytes())

    def write(self, name, value):
        persist(self.path(name), value)

    def open_run(self):
        if self.path('halt').exists() or self.path('final').exists():
            raise ProtocolFailure('run is stopped; repair/retry prohibited')

    def freeze(self, evidence, protected=()):
        self.open_run()
        authority = canonical(evidence)
        self.write('baseline', {'protocol': PROTOCOL, 'evidence': loads(authority),
                                'identity': digest(authority)})
        files = {str(Path(p).resolve()): digest(Path(p).read_bytes()) for p in protected}
        files[str(self.path('baseline').resolve())] = digest(self.path('baseline').read_bytes())
        lock = {'protocol': PROTOCOL, 'files': files}
        lock['identity'] = digest(canonical(lock))
        self.write('lock', lock)
        return self.integrity()

    def integrity(self):
        lock = self.read('lock')
        if type(lock) is not dict or set(lock) != {'protocol', 'files', 'identity'}:
            raise ProtocolFailure('invalid lock envelope')
        body = {key: value for key, value in lock.items() if key != 'identity'}
        if lock['protocol'] != PROTOCOL or lock['identity'] != digest(canonical(body)):
            raise ProtocolFailure('lock identity mismatch')
        if type(lock['files']) is not dict or str(self.path('baseline').resolve()) not in lock['files']:
            raise ProtocolFailure('baseline missing from lock')
        for name, expected in lock['files'].items():
            if not Path(name).is_file() or digest(Path(name).read_bytes()) != expected:
                raise ProtocolFailure('protected bytes changed: ' + name)
        baseline = self.read('baseline')
        if type(baseline) is not dict or set(baseline) != {'protocol', 'evidence', 'identity'}:
            raise ProtocolFailure('invalid baseline envelope')
        if baseline['protocol'] != PROTOCOL or baseline['identity'] != digest(canonical(baseline['evidence'])):
            raise ProtocolFailure('baseline identity mismatch')
        return {'valid': True, 'identity': lock['identity'], 'protected_files': len(lock['files'])}

    def counts(self):
        reservations = sorted(self.directory.glob('reservation-*.json'))
        observations = sorted(self.directory.glob('observation-*.json'))
        for index, path in enumerate(reservations, 1):
            record = loads(path.read_bytes())
            if path.name != f'reservation-{index}.json' or not equivalent(record, {
                    'protocol': PROTOCOL, 'number': index, 'lock': self.read('lock')['identity']}):
                raise ProtocolFailure('invalid reservation receipt')
        for index, path in enumerate(observations, 1):
            record = loads(path.read_bytes())
            if (path.name != f'observation-{index}.json' or type(record) is not dict or
                    set(record) != {'protocol', 'number', 'reservation', 'evidence', 'identity'} or
                    record['protocol'] != PROTOCOL or type(record['number']) is not int or
                    record['number'] != index or index > len(reservations) or
                    record['reservation'] != digest(reservations[index - 1].read_bytes()) or
                    record['identity'] != digest(canonical({k: v for k, v in record.items() if k != 'identity'}))):
                raise ProtocolFailure('invalid observation receipt')
        completed, reserved = len(observations), len(reservations)
        disposition = ('multiple' if max(completed, reserved) > 1 else
                       'indeterminate' if reserved != completed else 'one' if completed else 'zero')
        return {'reservations': reserved, 'completed_observations': completed,
                'disposition': disposition,
                'observation_occurred': None if disposition == 'indeterminate' else bool(completed)}

    def halt(self, reason):
        if not self.path('halt').exists():
            try:
                counts = self.counts()
            except (ValueError, OSError) as exc:
                counts = {'disposition': 'corrupt', 'observation_occurred': None,
                          'count_error': str(exc)}
            self.write('halt', {'protocol': PROTOCOL, 'reason': str(reason), 'counts': counts,
                               'stage': ('pre-pass' if counts.get('disposition') == 'zero' else
                                         'post-observation' if counts.get('completed_observations', 0) else 'post-reservation'),
                               'repair_permitted': False})

    def verify(self, evidence):
        self.open_run()
        try:
            integrity = self.integrity()
            if not equivalent(evidence, self.read('baseline')['evidence']):
                raise ProtocolFailure('canonical evidence mismatch')
            if self.counts()['disposition'] not in ('zero', 'one'):
                raise ProtocolFailure('observation discipline violated')
            phase = 'pre' if self.counts()['disposition'] == 'zero' else 'post'
            self.write('verification-' + phase, {'protocol': PROTOCOL, 'integrity': integrity,
                                               'canonical_identity': digest(canonical(evidence))})
            return True
        except (ValueError, OSError) as exc:
            self.halt(exc)
            raise ProtocolFailure(str(exc)) from exc

    def observe(self, callback):
        self.open_run()
        try:
            self.integrity()
            if not self.path('verification-pre').exists() or self.counts()['disposition'] != 'zero':
                raise ProtocolFailure('one authorized observation only, after verification')
            expected = {'protocol': PROTOCOL, 'integrity': self.integrity(),
                        'canonical_identity': self.read('baseline')['identity']}
            if not equivalent(self.read('verification-pre'), expected):
                raise ProtocolFailure('invalid pre-pass verification receipt')
            self.write('reservation-1', {'protocol': PROTOCOL, 'number': 1,
                                        'lock': self.read('lock')['identity']})
            evidence = callback()
            receipt = {'protocol': PROTOCOL, 'number': 1,
                       'reservation': digest(self.path('reservation-1').read_bytes()), 'evidence': evidence}
            receipt['identity'] = digest(canonical(receipt))
            self.write('observation-1', receipt)
            self.integrity()
            return evidence
        except Exception as exc:
            self.halt(exc)
            raise ProtocolFailure(str(exc)) from exc

    def finish(self):
        if self.path('final').exists():
            raise ProtocolFailure('final replacement prohibited')
        try:
            integrity = self.integrity()
            counts = self.counts()
            if counts['disposition'] not in ('zero', 'one'):
                raise ProtocolFailure('observation discipline violated')
            if not self.path('halt').exists() and not self.path('verification-pre').exists():
                raise ProtocolFailure('unverified run')
        except (ValueError, OSError) as exc:
            self.halt(exc)
            integrity = {'valid': False, 'reason': str(exc)}
            counts = self.read('halt')['counts']
        result = {'protocol': PROTOCOL, 'status': 'HALT' if self.path('halt').exists() else 'STOP',
                  'counts': counts, 'integrity': integrity, 'repair_permitted': False}
        self.write('final', result)
        return result
