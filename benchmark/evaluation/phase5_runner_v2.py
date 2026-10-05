"""Small cooperative Tier-2 experiment runner. No historical runtime stack.

R5.72 has no real benchmark opener or authorization issuer. Only synthetic
resources may traverse the observation lifecycle. Git calls inspect metadata.
"""
from contextlib import contextmanager
import ast
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys


class Rejected(ValueError):
    pass


def require(condition, reason):
    if not condition:
        raise Rejected(reason)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=False, allow_nan=False).encode('utf-8')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def seal(value):
    require('identity' not in value, 'identity already present')
    return {**value, 'identity': digest(canonical(value))}


def verify(value):
    body = {k: v for k, v in value.items() if k != 'identity'}
    require(value.get('identity') == digest(canonical(body)), 'evidence identity mismatch')
    return body


def safe_bytes(value):
    """Closed credential-field rejection plus recognizable/marked secret values.

    Protocol authorization is an artifact type, not a credential-bearing field.
    Diagnostics never echo rejected values. Environment values are never published.
    """
    reserved = re.compile(r'(secret|password|credential|api.?key|token|private.?key)', re.I)
    recognizable = re.compile(r'(sk-[A-Za-z0-9_-]{12,}|AKIA[A-Z0-9]{16}|-----BEGIN .*PRIVATE KEY|Bearer\s+\S+|SECRET\[)', re.I)
    def walk(item):
        if isinstance(item, dict):
            for key, child in item.items():
                require(type(key) is str and not reserved.search(key), 'unsafe publication field')
                walk(child)
        elif isinstance(item, (list, tuple)):
            for child in item:
                walk(child)
        elif isinstance(item, str):
            require(not recognizable.search(item), 'unsafe publication value')
    walk(value)
    return canonical(value) + b'\n'


def persist(path, value):
    raw = safe_bytes(value)
    path = Path(path)
    require(path.parent.is_dir(), 'missing evidence parent')
    with path.open('xb') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())


def load(path):
    raw = Path(path).read_bytes()
    def pairs(items):
        require(len(dict(items)) == len(items), 'duplicate evidence keys')
        return dict(items)
    value = json.loads(raw, object_pairs_hook=pairs)
    require(raw == safe_bytes(value), 'noncanonical evidence')
    return value


# These are safe metadata Git object pins, already present at the R5.71 boundary.
# Their content is policy/index metadata, never a protected contract or fixture.
METADATA = {
    'benchmark/results/phase5c/R5_71-evidence/authority-policy.json': '0f786e167fe63633f80c503d5130be7de35646c5',
    'benchmark/results/phase5c/R5_71-evidence/sealed-members.json': 'd389f7237389ad3dff43cb5e2a6ec3277c39aadc',
    'benchmark/evaluation/prohibited_test_index_r5_61.json': '125c9c37e5193b4e2a3f348a0818a4c7998889c6',
}
RESOURCE_PATHS = (
    'benchmark/requirements/B02.md', 'benchmark/harness/profiles/B02.json',
    'benchmark/harness/capabilities/B02.json',
    'benchmark/results/phase5c/R5_37-b02-semantic-application.json',
    'benchmark/results/phase5c/R5_40-b02-semantic-application.json',
    'benchmark/results/phase5c/R5_40-B02-profiles.json',
    'benchmark/results/phase5c/R5_40-B02-obligations.json',
    *(f'benchmark/harness/{name}.py' for name in (
        'test_b02_retry_r5_17', 'test_b02_retry_r5_19',
        'test_b02_retry_r5_21', 'test_b02_integration_r5_23')),
)


def protected_paths(root):
    paths = [Path(root) / n for n in RESOURCE_PATHS]
    for path in tuple(paths):
        if path.suffix == '.py':
            for optimization in ('', '1', '2'):
                paths.append(Path(importlib.util.cache_from_source(str(path), optimization=optimization)))
    return paths


_boundaries = []


def _audit(event, args):
    if event == 'open' and isinstance(args[0], (str, bytes, os.PathLike)):
        path = Path(os.fsdecode(args[0])).resolve()
        for boundary in tuple(_boundaries):
            denied = path in boundary.paths
            if not denied and path.exists():
                stat = path.stat()
                denied = (stat.st_dev, stat.st_ino) in boundary.inodes
            if denied:
                boundary.attempts += 1
                raise Rejected('R5_72_PROTOCOL_HALT')


sys.addaudithook(_audit)


class Boundary:
    def __init__(self, root, extra=()):
        self.paths = {p.resolve() for p in [*protected_paths(root), *map(Path, extra)]}
        self.inodes = set()
        for path in self.paths:
            if path.exists():
                stat = path.stat()
                self.inodes.add((stat.st_dev, stat.st_ino))
        self.attempts = 0

    @contextmanager
    def active(self):
        _boundaries.append(self)
        try:
            yield self
            require(self.attempts == 0, 'R5_72_PROTOCOL_HALT')
        finally:
            _boundaries.remove(self)


def metadata(root, name):
    raw = (Path(root) / name).read_bytes().replace(b'\r\n', b'\n')
    blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    require(blob == METADATA[name], 'trusted metadata changed')
    return json.loads(raw)


def git(root, *args):
    result = subprocess.run(['git', *args], cwd=root, capture_output=True, timeout=15)
    require(result.returncode == 0, 'Git metadata unavailable')
    return result.stdout.decode().strip()


def benchmark_commitment(root):
    """Validate final trusted sealed identities; never qualify ordinary authority."""
    policy = metadata(root, next(iter(METADATA)))
    evidence = metadata(root, 'benchmark/results/phase5c/R5_71-evidence/sealed-members.json')
    rows = {name: row for name, row in policy['members'].items() if row['classification'] == 'SEALED'}
    require(set(rows) == set(RESOURCE_PATHS) and len(rows) == 11, 'sealed resource set mismatch')
    resources = {}
    for name, row in sorted(rows.items()):
        recorded = evidence['resources'][row['resource']]
        require(recorded['seal'] == 'CLOSED' and recorded['current_content_read'] is False
                and recorded['commitment'] == row['sha256'] and recorded['object'] == row['blob']
                and recorded['provenance'] == digest(canonical(row['provenance']))
                and row['provenance']['successor'] == policy['authority']
                and row['worktree_content_verified'] is False
                and row['checkout_observation'] == 'DEFERRED_UNTIL_OPEN', 'sealed provenance mismatch')
        expected = f"{row['mode']} blob {row['blob']}\t{name}"
        for revision in ('HEAD', row['provenance']['historical_head']):
            require(git(root, 'ls-tree', revision, '--', name) == expected, 'sealed mapping changed')
        require(git(root, 'cat-file', '-t', row['blob']) == 'blob', 'sealed object missing')
        require((Path(root) / name).is_file(), 'sealed worktree resource missing')
        resources[row['resource']] = {'commitment': row['sha256'], 'object': row['blob'],
            'representation': row['representation_kind'], 'provenance': recorded['provenance'],
            'frozen': row['frozen'], 'seal': 'CLOSED'}
    require(sum(r['frozen'] for r in resources.values()) == 2, 'frozen pin count mismatch')
    for name, row in rows.items():
        require(not row['frozen'] or policy['frozen_authority'][name] == row['sha256'], 'frozen pin mismatch')
    return seal({'kind': 'B02', 'expected_benchmark': 'Phase5/B02', 'resources': resources,
                 'trusted_metadata': METADATA, 'protected_content_reads': 0})


def verify_commitment(value, trusted_identity, observed):
    verify(value)
    require(value['identity'] == trusted_identity and value == observed, 'benchmark commitment mismatch')
    require(value['resources'] and all(r['seal'] == 'CLOSED' for r in value['resources'].values()),
            'benchmark not sealed')


def current_state(root, extra=()):
    root = Path(root)
    from benchmark.semantic.application_boundary_r5_41 import SCHEMA
    names = {'air/task_manager.json', 'schema/axiom-v0.3.schema.json', 'docs/axiom-v0.3.md',
             'schema/axiom-v0.2.schema.json', 'experiments/task_manager-v0.2-before-priority.json',
             *(f'benchmark/semantic/{name}.json' for name in (
                 'operation-contract-fixtures', 'invariant-fixtures', 'selection-fixtures', 'state-relation-fixtures')),
             'generated/task_manager.py', 'generated/task_manager.manifest.json',
             'benchmark/evaluation/phase5_runner_v2.py', 'benchmark/evaluation/phase5_worker_v2.py',
             'benchmark/evaluation/test_phase5_runner_v2.py',
             'benchmark/results/phase5c/r5_72_qualification.py', *METADATA, *extra}
    for directory in ('src/air_compiler', 'benchmark/semantic', 'tests'):
        names.update(p.relative_to(root).as_posix() for p in (root / directory).glob('*.py'))
    # Bind only selected generic tests and their direct/transitive test helpers.
    # This is Python source linkage, not native/machine dependency closure.
    from benchmark.evaluation.phase5_worker_v2 import SUPPORT
    pending = list(SUPPORT)
    seen = set()
    while pending:
        module = pending.pop()
        if module in seen:
            continue
        seen.add(module)
        name = 'benchmark/harness/' + module + '.py'
        require(name not in RESOURCE_PATHS, 'R5_72_PROTOCOL_HALT')
        names.add(name)
        for node in ast.walk(ast.parse((root / name).read_text(encoding='utf-8'))):
            imported = ([a.name for a in node.names] if isinstance(node, ast.Import) else
                        [node.module or ''] if isinstance(node, ast.ImportFrom) else [])
            pending.extend(n.split('.')[-1] for n in imported if n.startswith('benchmark.harness.test_'))
    files = {n: digest((root / n).read_bytes().replace(b'\r\n', b'\n')) for n in sorted(names)}
    return seal({'kind': 'CurrentState', 'files': files, 'registry': digest(canonical(SCHEMA)),
        'semantic_count': SCHEMA['core_constructs'], 'platform': {
            'system': platform.system(), 'machine': platform.machine(),
            'python': platform.python_version(), 'implementation': platform.python_implementation()},
        'direct_dependencies': {'third_party': [], 'stdlib': platform.python_version()},
        'configuration': {'python_site': False, 'python_hash_seed': '0', 'network_inference': False,
                          'text_identity': 'UTF8 repository text; CRLF normalized to LF'},
        'runner': {n: files[n] for n in files if n.endswith(('phase5_runner_v2.py', 'phase5_worker_v2.py'))}})


HEALTH_STAGES = ('application', 'support', 'matrix-schema-trace-contamination',
                 'validate', 'safety', 'ai-independence', 'runner', 'safe-exclusion')


def health_record(state, results):
    verify(state)
    require(set(results) == set(HEALTH_STAGES) and all(r['status'] == 'PASS' and
            r['state'] == state['identity'] for r in results.values()), 'missing or stale health evidence')
    return seal({'kind': 'GenericHealthCheck', 'state': state['identity'], 'results': results})


def freeze(state, commitment, health):
    for value in (state, commitment, health):
        verify(value)
    require(health['state'] == state['identity'] and state['semantic_count'] == 30, 'stale health/state')
    require(health_record(state, health['results']) == health, 'invalid health record')
    return seal({'kind': 'ExperimentFreeze', 'state': state['identity'],
                 'benchmark': commitment['identity'], 'health': health['identity'],
                 'runner': state['runner'], 'observation_count': 0, 'repair_state': 'clean'})


TRANSITIONS = ('AUTHORIZED', 'OPENING_RESERVED', 'OPENING_CONSUMED', 'DISPATCHED', 'COMPLETED')


class Ledger:
    """One append-only exclusive-create event sequence. Interrupted work cannot retry.

    Cooperative single-controller use; no hostile-host or concurrent-writer claim.
    Every authorization binds this durable directory, never an in-memory counter.
    """
    def __init__(self, directory):
        self.directory = Path(directory).resolve()
        require(self.directory.is_dir(), 'ledger directory missing')

    def events(self):
        paths = sorted(self.directory.glob('*.json'))
        events = []
        for i, path in enumerate(paths):
            require(path.name == f'{i:02d}.json', 'invalid ledger sequence')
            event = load(path)
            verify(event)
            require(event['previous'] == (events[-1]['identity'] if events else None), 'ledger chain mismatch')
            expected = TRANSITIONS[i] if i < len(TRANSITIONS) else 'INVALIDATED'
            require(event['transition'] == expected or
                    (event['transition'] == 'INVALIDATED' and i > 0 and i == len(paths) - 1), 'invalid ledger transition')
            require(not events or event['freeze'] == events[0]['freeze'], 'ledger freeze mismatch')
            events.append(event)
        return events

    def append(self, transition, frozen, **details):
        events = self.events()
        require(not events or events[-1]['transition'] != 'INVALIDATED', 'experiment invalidated')
        expected = TRANSITIONS[len(events)] if len(events) < len(TRANSITIONS) else None
        require(transition == expected or (transition == 'INVALIDATED' and events), 'second observation or replay')
        event = seal({'kind': 'ObservationLedger', 'transition': transition, 'freeze': frozen,
                      'previous': events[-1]['identity'] if events else None, 'details': details})
        persist(self.directory / f'{len(events):02d}.json', event)
        return event

    def status(self):
        events = self.events()
        if not events:
            return 'zero'
        if events[-1]['transition'] == 'INVALIDATED':
            return 'multiple/invalid'
        return 'one' if events[-1]['transition'] == 'COMPLETED' else 'incomplete'


def authorize_synthetic(frozen, commitment, ledger, state):
    for value in (frozen, commitment, state):
        verify(value)
    require(commitment['kind'] == 'synthetic' and all(n.startswith('synthetic:') for n in commitment['resources']),
            'R5_72_PROTOCOL_HALT: actual benchmark authorization prohibited')
    require(frozen['state'] == state['identity'] and frozen['benchmark'] == commitment['identity']
            and frozen['runner'] == state['runner'] and ledger.status() == 'zero', 'authorization binding mismatch')
    grant = seal({'kind': 'OneTimeObservationAuthorization', 'freeze': frozen['identity'],
                  'benchmark': commitment['identity'], 'operation': 'static-whole-contract',
                  'scope': 'synthetic-only', 'ledger': str(ledger.directory), 'repair': False,
                  'generation': False, 'execution': False, 'acceptance': False})
    ledger.append('AUTHORIZED', frozen['identity'], grant=grant['identity'])
    return grant


def observe(frozen, commitment, grant, ledger, capture, metadata_check, opener, evaluator,
            operation='static-whole-contract'):
    for value in (frozen, commitment, grant):
        verify(value)
    events = ledger.events()
    require(operation == 'static-whole-contract' and grant['operation'] == operation
            and grant['scope'] == 'synthetic-only' and commitment['kind'] == 'synthetic'
            and all(n.startswith('synthetic:') for n in commitment['resources'])
            and all(grant[k] is False for k in ('repair', 'generation', 'execution', 'acceptance')),
            'unauthorized operation')
    require(len(events) == 1 and events[0]['details']['grant'] == grant['identity']
            and grant['ledger'] == str(ledger.directory) and grant['freeze'] == frozen['identity']
            and events[0]['freeze'] == frozen['identity'] and grant['benchmark'] == frozen['benchmark'],
            'second observation or replay')
    state = capture()
    verify(state)
    require(state['identity'] == frozen['state'] and state['runner'] == frozen['runner'], 'state/runner drift')
    verify_commitment(commitment, frozen['benchmark'], metadata_check())
    ledger.append('OPENING_RESERVED', frozen['identity'], grant=grant['identity'])
    opened = opener()
    ledger.append('OPENING_CONSUMED', frozen['identity'], grant=grant['identity'])
    require(set(opened) == set(commitment['resources']), 'substituted or missing sealed resource')
    for name, raw in opened.items():
        require(digest(raw) == commitment['resources'][name]['commitment'], 'opened commitment mismatch')
    ledger.append('DISPATCHED', frozen['identity'], grant=grant['identity'])
    result = evaluator(opened)
    # Publication failure leaves dispatch incomplete, never permits another call.
    safe_bytes(result)
    ledger.append('COMPLETED', frozen['identity'], result=result, benchmark=commitment['identity'])
    return result


def invalidate_repair(frozen, ledger):
    ledger.append('INVALIDATED', frozen['identity'], reason='repair occurred')


def post_check(frozen, commitment, ledger, capture, metadata_check):
    verify(frozen)
    state = capture()
    verify(state)
    require(state['identity'] == frozen['state'] and state['runner'] == frozen['runner'], 'post-observation state drift')
    verify_commitment(commitment, frozen['benchmark'], metadata_check())
    events = ledger.events()
    require(ledger.status() == 'one' and len(events) == 5
            and all(e['freeze'] == frozen['identity'] for e in events)
            and events[-1]['details']['benchmark'] == frozen['benchmark'], 'incomplete/multiple/repair')
    return {'status': 'PASS', 'observations': 1, 'repair_state': 'clean', 'state': state['identity']}


def controlled_environment(root):
    # Necessary Windows runtime/process context only. Never propagate authoring AI.
    env = {key: os.environ[key] for key in ('SYSTEMROOT', 'WINDIR', 'TEMP', 'TMP', 'COMSPEC') if key in os.environ}
    env.update(PYTHONPATH=os.pathsep.join((str(root), str(Path(root) / 'src'))),
               PYTHONHASHSEED='0', PYTHONDONTWRITEBYTECODE='1', PYTHONIOENCODING='utf-8')
    return env


def run_health_stage(root, state, stage):
    require(stage in HEALTH_STAGES, 'unknown worker selection')
    require(current_state(root) == state, 'state changed before health')
    command = [sys.executable, '-B', '-S', '-m', 'benchmark.evaluation.phase5_worker_v2', stage]
    result = subprocess.run(command, cwd=root, env=controlled_environment(root),
                            capture_output=True, timeout=85)
    require(result.returncode == 0, 'generic health worker failed; output withheld')
    evidence = json.loads(result.stdout)
    require(evidence['status'] == 'PASS' and evidence['protected_read_attempts'] == 0
            and current_state(root) == state, 'health drift or protocol halt')
    return {**evidence, 'kind': 'GenericHealthCheck', 'state': state['identity'], 'worker': state['runner']}
