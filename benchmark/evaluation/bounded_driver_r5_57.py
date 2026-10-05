"""Prospective pre-exposure production qualification scheduler; no observation API.

Receipts retain the unchanged Tier-2 format. Immutable journal entries bind their
bytes to one fresh qualification. An orphan attempt is terminal, never retried.
"""

from dataclasses import dataclass, asdict
import math
from pathlib import Path
import re
import time

from benchmark.evaluation import security_r5_47 as security
from benchmark.evaluation import tier2_r5_51 as tier
from benchmark.evaluation import capability_guard_r5_61 as capabilities
from benchmark.evaluation.recorder_r5_43 import canonical, digest, loads, ProtocolFailure

PROTOCOL = 'lykoi-bounded-qualification-r5.62-v1'
VERSION = 'bounded-driver-r5.62-v1'
NAME = re.compile(r'[A-Za-z0-9_-]{1,100}\Z')


@dataclass(frozen=True)
class Cost:
    pre_capture: float = 12
    startup: float = 3
    worker: float = 35
    shutdown: float = 3
    post_capture: float = 12
    evidence: float = 2
    receipt: float = 2
    integrity: float = 2
    mediation: float = 0
    child_validation: float = 0
    exclusion_setup: float = 0

    def total(self):
        values = asdict(self).values()
        if any(type(v) not in (int, float) or not math.isfinite(v) or v < 0 for v in values):
            raise ProtocolFailure('invalid lifecycle budget')
        return sum(asdict(self).values())

    def margin(self):
        return max(15, self.total() * .25)

    def required(self):
        return self.total() + self.margin()


def production_cost(worker_seconds=None):
    # Unmeasured classes get a 65-second worker allowance, not a fast-suite guess.
    return Cost(worker=65 if worker_seconds is None else max(35, worker_seconds),
                mediation=2, child_validation=2, exclusion_setup=2)


def reload(path):
    try:
        raw = Path(path).read_bytes()
        value = loads(raw)
        if raw != canonical(value) + b'\n':
            raise ValueError()
        security.safe_bytes(value)
        tier.envelopes.unseal(value)
        return value
    except Exception:
        raise ProtocolFailure('qualification evidence invalid; details withheld') from None


class Driver:
    def __init__(self, output, experiment, capsule, authority, stages, capture,
                 live_authority, *, version=VERSION, clock=time.monotonic, resources=None):
        if ('r5.56' in experiment.casefold() or
                any(not NAME.fullmatch(n) for n in stages)):
            raise ProtocolFailure('R5_57_PROTOCOL_HALT: prohibited qualification')
        declarations = {n: capabilities.binding(s.get('capabilities')) for n, s in stages.items()}
        tier.check(capsule)
        self.output, self.capture, self.live_authority = Path(output), capture, live_authority
        self.capsule, self.stages, self.clock = capsule, stages, clock
        if resources is None:
            resources = capabilities.repository_resources(Path(__file__).resolve().parents[2])
        self.boundary = capabilities.Boundary(resources, lambda evidence: self.write('quarantine', evidence))
        self.binding = {'protocol': PROTOCOL, 'version': version,
            'implementation': digest(Path(__file__).read_bytes()), 'experiment': experiment,
            'capsule': capsule['identity'], 'authority': authority,
            'resource_policy': self.boundary.identity(),
            'capability_guard': self.boundary.implementation(),
            'stages': [{'name': n, 'mechanism': s['mechanism'], 'cost': asdict(s['cost']),
                        'capability_binding': declarations[n], **self.child_definition(s)} for n, s in stages.items()]}
        security.safe_bytes(self.binding)
        for name, stage in stages.items():
            if self.child_definition(stage):
                if any(getattr(stage['cost'], field) <= 0 for field in
                       ('mediation', 'child_validation', 'exclusion_setup')):
                    raise ProtocolFailure('mediated lifecycle budget required')
                stage['run'].bind(self.binding, name, self.boundary)

    @staticmethod
    def child_definition(stage):
        from benchmark.evaluation.mediated_child_r5_62 import Child
        return {'child': stage['run'].descriptor} if isinstance(stage['run'], Child) else {}

    def write(self, name, body):
        value = tier.seal(body)
        security.persist(self.output / (name + '.json'), value)
        if reload(self.output / (name + '.json')) != value:
            raise ProtocolFailure('persisted evidence mismatch')
        return value

    def initialize(self):
        if not self.output.is_dir() or any(self.output.iterdir()):
            raise ProtocolFailure('fresh dedicated evidence required')
        self.write('qualification', self.binding)

    def validate(self):
        if (self.output / 'quarantine.json').exists() or self.boundary.denied:
            raise ProtocolFailure('R5_61_PROTOCOL_HALT: qualification quarantined')
        current = [{'name': n, 'mechanism': s['mechanism'], 'cost': asdict(s['cost']),
                    'capability_binding': capabilities.binding(s.get('capabilities')), **self.child_definition(s)}
                   for n, s in self.stages.items()]
        if (current != self.binding['stages'] or self.boundary.identity() != self.binding['resource_policy'] or
                self.boundary.implementation() != self.binding['capability_guard']):
            raise ProtocolFailure('R5_61_PROTOCOL_HALT: stage authorization binding changed')
        if reload(self.output / 'qualification.json') != tier.seal(self.binding):
            raise ProtocolFailure('qualification identity incompatible')
        if self.capture() != self.capsule or self.live_authority() != self.binding['authority']:
            raise ProtocolFailure('qualification state or authority changed')
        receipts, previous, stopped = {}, None, False
        journals = sorted(self.output.glob('batch-*.json'))
        for number, path in enumerate(journals):
            row = reload(path)
            if (path.name != f'batch-{number:04d}.json' or row['binding'] != digest(canonical(self.binding))
                    or row['previous'] != previous or stopped):
                raise ProtocolFailure('batch linkage invalid')
            ordered = list(self.stages)[len(receipts):len(receipts) + len(row['receipts'])]
            if set(ordered) != set(row['receipts']):
                raise ProtocolFailure('receipt order invalid')
            for name in ordered:
                pin = row['receipts'][name]
                if name in receipts or name != list(self.stages)[len(receipts)]:
                    raise ProtocolFailure('receipt order invalid')
                raw = (self.output / ('receipt-' + name + '.json')).read_bytes()
                receipt = reload(self.output / ('receipt-' + name + '.json'))
                if (digest(raw) != pin or receipt['capsule'] != self.capsule['identity'] or
                        receipt['experiment'] != self.binding['experiment'] or receipt['stage'] != name or
                        receipt['mechanism'] != self.stages[name]['mechanism']):
                    raise ProtocolFailure('receipt continuation invalid')
                attempt = reload(self.output / ('attempt-' + name + '.json'))
                if attempt != tier.seal({'binding': digest(canonical(self.binding)), 'stage': name,
                                         'status': 'INCOMPLETE'}):
                    raise ProtocolFailure('attempt linkage invalid')
                if receipt['status'] == 'PASS' and receipt['result'].get('successful') is not True:
                    raise ProtocolFailure('invalid PASS')
                if self.child_definition(self.stages[name]) and receipt['status'] in ('PASS', 'FAIL'):
                    self.stages[name]['run'].check_result(receipt['result'], receipt['status'])
                receipts[name] = receipt
            stopped = row['disposition'] == 'STOPPED'
            next_name = list(self.stages)[len(receipts)] if len(receipts) < len(self.stages) else None
            if row['next'] != next_name or row['disposition'] not in ('BOUNDARY', 'COMPLETE', 'STOPPED'):
                raise ProtocolFailure('batch state invalid')
            if (row['disposition'] == 'COMPLETE') != (next_name is None and not stopped):
                raise ProtocolFailure('completion mismatch')
            previous = row['identity']
        known = set(receipts)
        attempts = {p.stem[len('attempt-'):] for p in self.output.glob('attempt-*.json')}
        persisted = {p.stem[len('receipt-'):] for p in self.output.glob('receipt-*.json')}
        if attempts != known or persisted != known:
            # Durable INCOMPLETE attempt remains the only evidence after hard kill.
            raise ProtocolFailure('interrupted admitted stage: INCOMPLETE; retry prohibited')
        if stopped or any(r['status'] != 'PASS' for r in receipts.values()):
            raise ProtocolFailure('qualification stopped; retry prohibited')
        return receipts, previous, len(journals)

    def batch(self, seconds=110, *, started=None, boundary_reserve=5):
        # Caller passes entry timestamp to include import/startup time in envelope.
        started = self.clock() if started is None else started
        if not math.isfinite(seconds) or seconds <= 0 or boundary_reserve < 5:
            raise ProtocolFailure('invalid invocation budget')
        receipts, previous, number = self.validate()
        added, decisions = {}, []
        disposition = 'COMPLETE'
        for name, stage in self.stages.items():
            if name in receipts:
                continue
            cost = stage['cost']
            remaining = seconds - (self.clock() - started)
            required = cost.required() + boundary_reserve
            admitted = remaining >= required
            decisions.append({'stage': name, 'remaining': remaining, 'required': required,
                              'lifecycle': asdict(cost), 'margin': cost.margin(), 'admitted': admitted})
            if not admitted:
                disposition = 'BOUNDARY'
                break
            self.write('attempt-' + name, {'binding': digest(canonical(self.binding)),
                                         'stage': name, 'status': 'INCOMPLETE'})
            status, result = 'INCOMPLETE', {'successful': False, 'reason': 'stage interrupted; details withheld'}
            try:
                before = self.capture()
                if before != self.capsule or self.live_authority() != self.binding['authority']:
                    raise ProtocolFailure('state changed')
                # Execution timeout includes startup and shutdown; post costs stay reserved.
                tail = cost.post_capture + cost.evidence + cost.receipt + cost.integrity
                timeout = min(cost.startup + cost.worker + cost.shutdown + cost.mediation +
                              cost.child_validation + cost.exclusion_setup,
                              seconds - (self.clock() - started) - tail - cost.margin() - boundary_reserve)
                if timeout <= 0:
                    raise ProtocolFailure('admitted capture exceeded allowance')
                with self.boundary.stage(stage['capabilities']):
                    result = stage['run'](timeout)
                security.safe_bytes(result)
                after = self.capture()
                if self.live_authority() != self.binding['authority']:
                    raise ProtocolFailure('authority changed')
                row = tier.receipt(before, after, self.binding['experiment'], name,
                                   stage['mechanism'], 'PASS' if result.get('successful') is True else 'FAIL', result)
                status = row['status']
            except Exception as error:
                # No worker result is inferred, even if a child wrote output before timeout.
                result = {'successful': False, 'reason': 'stage interrupted; details withheld'}
                from benchmark.evaluation.mediated_child_r5_62 import ChildFailure
                if isinstance(error, ChildFailure):
                    result['child_execution'] = error.execution
                row = tier.receipt(self.capsule, self.capsule, self.binding['experiment'], name,
                                   stage['mechanism'], 'INCOMPLETE', result)
            security.persist(self.output / ('receipt-' + name + '.json'), row)
            reload(self.output / ('receipt-' + name + '.json'))
            added[name] = digest((self.output / ('receipt-' + name + '.json')).read_bytes())
            receipts[name] = row
            if status != 'PASS':
                disposition = 'STOPPED'
                break
        next_name = list(self.stages)[len(receipts)] if len(receipts) < len(self.stages) else None
        return self.write(f'batch-{number:04d}', {'binding': digest(canonical(self.binding)),
            'previous': previous, 'receipts': added, 'next': next_name, 'disposition': disposition,
            'decisions': decisions, 'elapsed': self.clock() - started, 'b02_exposure': 0})


def child(command, cwd, environment, result_path):
    """Historical command interface is closed prospectively; use qualified_child."""
    def run(timeout):
        if capabilities._active is not None:
            capabilities._active.deny('UNMEDIATED_EXECUTION')
        raise ProtocolFailure('R5_62_PROTOCOL_HALT: arbitrary worker command rejected')
    return run


def qualified_child(root, registry, trusted_registry, worker, capabilities, inputs=None, **options):
    from benchmark.evaluation.mediated_child_r5_62 import Child
    return Child(root, registry, trusted_registry, worker, capabilities, inputs, **options)
