"""Content-bound cooperative Tier-2 children; no arbitrary command authority.

Registry trust is an external qualification pin, not a worker display name.
The argv digest is a parent-to-child integrity commitment, not hostile-OS defense.
"""

from pathlib import Path
import os
import math
import subprocess
import sys
import time

from benchmark.evaluation import capability_guard_r5_61 as guard
from benchmark.evaluation import restricted_harness_r5_61 as exclusion
from benchmark.evaluation import security_r5_47 as security
from benchmark.evaluation.recorder_r5_43 import canonical, digest, loads, ProtocolFailure

VERSION = 'lykoi-mediated-child-r5.62-v1'
FLAGS = ['-S', '-B']
RUN = subprocess.run
ROOT = Path(__file__).resolve().parents[2]
RUNTIME = ('benchmark/evaluation/mediated_child_r5_62.py',
           'benchmark/evaluation/child_startup_r5_62.py',
           'benchmark/evaluation/capability_guard_r5_61.py',
           'benchmark/evaluation/restricted_harness_r5_61.py',
           'benchmark/evaluation/prohibited_test_index_r5_61.json',
           'benchmark/evaluation/security_r5_47.py',
           'benchmark/evaluation/recorder_r5_43.py')


def reject():
    raise ProtocolFailure('R5_62_PROTOCOL_HALT: child binding rejected; details withheld')


class ChildFailure(ProtocolFailure):
    def __init__(self, status, worker_started):
        self.execution = {'status': status, 'worker_started': worker_started,
                          'diagnostics': 'withheld'}
        super().__init__('R5_62 child execution failed; details withheld')


def implementation(root, paths):
    root = Path(root).resolve()
    boundary = guard.Boundary(guard.repository_resources(root), lambda row: None)
    result = {}
    for name in paths:
        path = (root / name).resolve()
        if not path.is_relative_to(root):
            reject()
        boundary.audit('open', (str(path), 'r', 0))
        result[name] = digest(path.read_bytes())
    return result


def environment(parent):
    # Absolute interpreter, -S -B, explicit bootstrap root: no PATH/PYTHONPATH,
    # site hooks, editor/provider state or credential propagation is needed.
    result = {name: parent[name] for name in ('SYSTEMROOT', 'WINDIR', 'TEMP', 'TMP') if name in parent}
    result.update({'PYTHONUTF8': '1', 'PYTHONDONTWRITEBYTECODE': '1', 'PYTHONHASHSEED': '0'})
    security.safe_bytes(result)
    return result


def registry(root, definitions):
    """Prepare prospective definitions for independent review and external pinning.

    Each function's complete declared implementation closure is content-bound.
    Merely constructing this document does not qualify its workers.
    """
    rows = {}
    for name, definition in definitions.items():
        module, function, paths = definition
        path = module.replace('.', '/') + '.py'
        if path not in paths or any(Path(p).is_absolute() or '..' in Path(p).parts for p in paths):
            reject()
        rows[name] = {'module': module, 'function': function,
                      'implementation': implementation(root, sorted(set(paths)))}
    return {'version': VERSION, 'workers': rows}


def worker_identity(definition):
    return digest(canonical(definition))


def validate(value, expected):
    """Runs before worker import/discovery. Never reads protected resources."""
    try:
        current, depth = value, 0
        while 'ancestor' in current:
            depth += 1
            if depth > 8:
                reject()
            current = current['ancestor']
        if digest(canonical(value)) != expected or value['version'] != VERSION:
            reject()
        parent = value['parent']
        if digest(canonical(parent)) != value['qualification']:
            reject()
        stages = [s for s in parent['stages'] if s['name'] == value['stage']]
        if len(stages) != 1:
            reject()
        stage = stages[0]
        caps = guard.authorize(value['capabilities'])
        if not set(caps) <= set(stage['capability_binding']['capabilities']):
            reject()
        descriptor = stage['child']
        ancestor = value.get('ancestor')
        if ancestor is None:
            if descriptor != value['selection']:
                reject()
        else:
            validate(ancestor, value['ancestor_integrity'])
            if (ancestor['parent'] != parent or ancestor['stage'] != value['stage'] or
                    ancestor['qualification'] != value['qualification'] or
                    ancestor['resources'] != value['resources'] or
                    not set(caps) <= set(ancestor['capabilities'])):
                reject()
            original = ancestor['selection']
            descriptor = value['selection']
            if any(descriptor[k] != original[k] for k in ('registry', 'runtime', 'exclusion', 'interpreter', 'flags')):
                reject()
        if descriptor['capabilities'] != list(caps):
            reject()
        if value['authority'] != parent['authority']:
            reject()
        resources = tuple(guard.Resource(r['identity'], Path(r['path']), r['capability'])
                          for r in value['resources'])
        boundary = guard.Boundary(resources, lambda row: None)
        if boundary.identity() != parent['resource_policy']:
            reject()
        if boundary.implementation() != parent['capability_guard']:
            reject()
        root = Path(value['root'])
        if implementation(root, RUNTIME) != descriptor['runtime']:
            reject()
        if digest(canonical(value['registry'])) != descriptor['registry']:
            reject()
        definition = value['registry']['workers'][descriptor['worker']]
        for name in definition['implementation']:
            boundary.audit('open', (str(root / name), 'r', 0))
        if worker_identity(definition) != descriptor['worker_identity']:
            reject()
        if implementation(root, definition['implementation']) != definition['implementation']:
            reject()
        if definition['module'] == 'benchmark.evaluation.safe_workers_r5_62' and definition['function'] == 'sut':
            inputs = descriptor['inputs']
            if definition['implementation'].get(inputs['path']) != inputs['sha256']:
                reject()
        if descriptor['exclusion'] != exclusion.INDEX_PIN or exclusion.accounting()['index_sha256'] != exclusion.INDEX_PIN:
            reject()
        if definition['module'] == 'benchmark.evaluation.safe_workers_r5_62' and definition['function'] == 'harness':
            prohibited = exclusion.index()['tests']
            modules = [p[:-3].replace('/', '.') for p in definition['implementation'] if p.endswith('.py')]
            for identity in descriptor['inputs']['identities']:
                if identity not in prohibited and not any(identity.startswith(module + '.') for module in modules):
                    reject()
        security.safe_bytes(value)
        return boundary, definition
    except Exception:
        reject()


class Child:
    def __init__(self, root, workers, trusted_registry, worker, capabilities, inputs=None, *, parent_environment=None):
        self.root = Path(root).resolve()
        # Freeze caller-owned structures; mutations are never incorporated silently.
        self.workers = loads(canonical(workers))
        self.worker = worker
        self.capabilities = list(guard.authorize(capabilities))
        self.inputs = loads(canonical(inputs or {}))
        self.environment = environment(os.environ if parent_environment is None else parent_environment)
        if digest(canonical(self.workers)) != trusted_registry or worker not in self.workers['workers']:
            reject()
        definition = self.workers['workers'][worker]
        if implementation(self.root, definition['implementation']) != definition['implementation']:
            reject()
        self.descriptor = {'version': VERSION, 'registry': trusted_registry, 'worker': worker,
            'worker_identity': worker_identity(definition), 'capabilities': self.capabilities,
            'inputs': self.inputs, 'runtime': implementation(self.root, RUNTIME),
            'flags': FLAGS,
            'exclusion': exclusion.INDEX_PIN, 'environment': digest(canonical(self.environment)),
            'interpreter': digest(Path(sys.executable).read_bytes())}
        security.safe_bytes(self.descriptor)

    def bind(self, parent, stage, boundary):
        if not set(self.capabilities) <= set(next(s for s in parent['stages'] if s['name'] == stage)
                                           ['capability_binding']['capabilities']):
            reject()
        self.boundary = boundary
        self.value = {'version': VERSION, 'parent': parent, 'qualification': digest(canonical(parent)),
            'stage': stage, 'authority': parent['authority'], 'capabilities': self.capabilities,
            'selection': self.descriptor, 'root': str(self.root), 'registry': self.workers,
            'resources': [{'identity': r.identity, 'path': str(r.path.resolve()), 'capability': r.capability}
                          for r in boundary.resources]}
        self.expected = digest(canonical(self.value))
        validate(self.value, self.expected)

    def check_result(self, result, status):
        proof = result.get('mediated_child', {})
        worker_result = {k: v for k, v in result.items() if k != 'mediated_child'}
        expected = {'binding': self.expected, 'qualification': self.value['qualification'],
            'stage': self.value['stage'], 'authority': self.value['authority'],
            'worker_identity': self.descriptor['worker_identity'],
            'capability_binding': guard.binding(self.capabilities), 'exclusion': exclusion.INDEX_PIN,
            'status': status, 'evidence_integrity': digest(canonical(
                {'binding': self.expected, 'status': status, 'result': worker_result}))}
        if proof != expected:
            reject()

    def bind_descendant(self, ancestor, boundary):
        # Same qualification/stage, and additionally linked to the immediate
        # parent's execution commitment. Attenuation uses immediate child rights.
        self.boundary = boundary
        self.value = {**ancestor, 'selection': self.descriptor, 'capabilities': self.capabilities,
                      'ancestor': ancestor, 'ancestor_integrity': digest(canonical(ancestor))}
        self.expected = digest(canonical(self.value))
        validate(self.value, self.expected)

    def __call__(self, timeout):
        started = time.monotonic()
        try:
            validate(self.value, self.expected)
            if (digest(canonical(self.environment)) != self.descriptor['environment'] or
                    digest(Path(sys.executable).read_bytes()) != self.descriptor['interpreter']):
                reject()
        except Exception:
            raise ChildFailure('LAUNCH_REJECTED', False) from None
        remaining = timeout - (time.monotonic() - started)
        if not math.isfinite(remaining) or remaining <= 0:
            raise ChildFailure('LAUNCH_REJECTED', False)
        command = [sys.executable, *FLAGS,
                   str(self.root / 'benchmark/evaluation/child_startup_r5_62.py'), self.expected,
                   str(started + timeout)]
        # Exactly this reviewed launch consumes a single audit permit. No callback
        # or worker code runs while the permit is active in the parent.
        try:
            with self.boundary.mediated_launch(command, str(self.root), self.environment):
                process = RUN(command, cwd=str(self.root), env=self.environment,
                    input=canonical(self.value), stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                    timeout=remaining, close_fds=True)
        except subprocess.TimeoutExpired:
            raise ChildFailure('INCOMPLETE', None) from None
        except Exception:
            raise ChildFailure('LAUNCH_REJECTED', False) from None
        try:
            value = loads(process.stdout)
            if process.stdout != canonical(value) + b'\n' or value['binding'] != self.expected:
                reject()
            security.safe_bytes(value)
            if value['status'] == 'REJECTED':
                raise ChildFailure('LAUNCH_REJECTED', False)
            if value['status'] == 'INCOMPLETE':
                raise ChildFailure('INCOMPLETE', True)
            if value['status'] == 'SECURITY_FAILURE':
                self.boundary.denied = True
                self.boundary.record({'classification': 'R5_62_PROTOCOL_HALT', 'quarantine': True,
                    'access': 'DENIED_BEFORE_CONTENT', 'child_binding': self.expected})
                raise ChildFailure('SECURITY_FAILURE', True)
            if process.returncode or value['status'] not in ('PASS', 'FAIL'):
                reject()
            result = value['result']
            if 'mediated_child' in result:
                reject()
            if (value['status'] == 'PASS') != (result.get('successful') is True):
                reject()
            return {**result, 'mediated_child': {'binding': self.expected,
                'qualification': self.value['qualification'], 'stage': self.value['stage'],
                'authority': self.value['authority'], 'worker_identity': self.descriptor['worker_identity'],
                'capability_binding': guard.binding(self.capabilities), 'exclusion': exclusion.INDEX_PIN,
                'status': value['status'], 'evidence_integrity': digest(canonical(value))}}
        except ChildFailure:
            raise
        except Exception:
            if self.boundary.denied:
                raise ChildFailure('SECURITY_FAILURE', True) from None
            raise ChildFailure('INCOMPLETE', None) from None


def install_descendants(value, boundary, deadline):
    """Cooperative compatibility bridge for frozen Python external-oracle callers.

    Only an absolute interpreter plus a registry-bound SUT script is recognized.
    Shells, -c, arbitrary executables and unknown scripts retain fail-closed denial.
    """
    def run(command, *, cwd=None, env=None, text=False, capture_output=False,
            timeout=None, **options):
        if (options or not capture_output or not text or not isinstance(command, (list, tuple)) or
                len(command) < 2 or Path(command[0]).resolve() != Path(sys.executable).resolve()):
            boundary.deny('UNMEDIATED_EXECUTION')
        path = Path(command[1]).resolve()
        root = Path(value['root'])
        if not path.is_relative_to(root):
            boundary.deny('UNMEDIATED_EXECUTION')
        relative = path.relative_to(root).as_posix()
        selected = []
        for name, definition in value['registry']['workers'].items():
            if (definition['module'] == 'benchmark.evaluation.safe_workers_r5_62' and
                    definition['function'] == 'sut' and relative in definition['implementation']):
                selected.append((name, definition))
        if len(selected) != 1:
            boundary.deny('UNMEDIATED_EXECUTION')
        name, definition = selected[0]
        adapter = Child(root, value['registry'], value['selection']['registry'], name,
            value['capabilities'], {'path': relative, 'sha256': definition['implementation'][relative],
                'argv': list(command[2:]), 'cwd': str(Path(cwd or root).resolve()), 'capture': True},
            parent_environment=os.environ if env is None else env)
        adapter.bind_descendant(value, boundary)
        allowance = min(timeout if timeout is not None else 35, deadline - time.monotonic() - .5)
        if allowance <= 0:
            raise ChildFailure('LAUNCH_REJECTED', False)
        result = adapter(allowance)
        return subprocess.CompletedProcess(command, result['exit'], result['stdout'], result['stderr'])
    subprocess.run = run
