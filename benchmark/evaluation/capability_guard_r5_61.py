"""Pre-exposure capability policy and cooperative Python resource boundary.

No protected content is read to establish this policy. Names are diagnostics;
trusted Resource objects, not callers' filenames, designate protected access.
This is not an OS sandbox. Unmediated subprocess/native execution is refused.
"""

from contextlib import contextmanager
from dataclasses import dataclass
import importlib.util
from pathlib import Path
import os
import subprocess
import threading
import sys

from benchmark.evaluation.recorder_r5_43 import canonical, digest, ProtocolFailure

GENERIC = frozenset({'HARNESS_EXECUTION', 'TEST_DISCOVERY', 'REGRESSION_EVIDENCE',
                     'AUTHORITY_LINKAGE', 'CERTIFICATE_LINKAGE', 'CONTINUITY',
                     'PUBLICATION', 'VALIDATION', 'SAFETY', 'SCHEMA', 'TRACEABILITY'})
PROTECTED = frozenset('B02_' + operation for operation in (
    'AUTHORITY_READ', 'CONTRACT_READ', 'FIXTURE_READ', 'STATIC_EVALUATION',
    'CHECKEDPLAN', 'READINESS', 'AUDIT', 'ADMISSION', 'RESERVATION', 'DISPATCH',
    'GENERATION', 'EXECUTION', 'ACCEPTANCE'))
POLICY = 'lykoi-pre-exposure-capabilities-r5.61-v1'
_active = None


def authorize(capabilities):
    if not isinstance(capabilities, (tuple, list)) or any(type(c) is not str for c in capabilities):
        raise ProtocolFailure('R5_61_PROTOCOL_HALT: invalid capability declaration')
    requested = frozenset(capabilities)
    if len(requested) != len(capabilities) or not requested <= GENERIC:
        raise ProtocolFailure('R5_61_PROTOCOL_HALT: unauthorized capability')
    return tuple(sorted(requested))


def binding(capabilities):
    return {'policy': POLICY, 'permitted_capabilities': sorted(GENERIC),
            'capabilities': list(authorize(capabilities))}


@dataclass(frozen=True)
class Resource:
    identity: str
    path: Path
    capability: str


def repository_resources(root):
    """Explicit sealed resource designations; no substring classification."""
    root = Path(root)
    rows = [('frozen-request', 'benchmark/requirements/B02.md', 'B02_AUTHORITY_READ'),
            ('frozen-profile', 'benchmark/harness/profiles/B02.json', 'B02_CONTRACT_READ'),
            ('frozen-capabilities', 'benchmark/harness/capabilities/B02.json', 'B02_CONTRACT_READ'),
            ('semantic-fixture-r537', 'benchmark/results/phase5c/R5_37-b02-semantic-application.json', 'B02_FIXTURE_READ'),
            ('semantic-fixture-r540', 'benchmark/results/phase5c/R5_40-b02-semantic-application.json', 'B02_FIXTURE_READ'),
            ('profile-fixture-r540', 'benchmark/results/phase5c/R5_40-B02-profiles.json', 'B02_FIXTURE_READ'),
            ('obligation-fixture-r540', 'benchmark/results/phase5c/R5_40-B02-obligations.json', 'B02_CONTRACT_READ')]
    rows += [(f'sealed-test-module-{i}', 'benchmark/harness/' + module + '.py',
              'B02_CONTRACT_READ') for i, module in enumerate((
        'test_b02_retry_r5_17', 'test_b02_retry_r5_19',
        'test_b02_retry_r5_21', 'test_b02_integration_r5_23'))]
    resources = [Resource(identity, root / path, capability) for identity, path, capability in rows]
    for identity, path, capability in rows:
        if path.endswith('.py'):
            for optimization in ('', '1', '2'):
                bytecode = importlib.util.cache_from_source(str(root / path), optimization=optimization)
                resources.append(Resource(identity + '-bytecode-' + (optimization or 'default'),
                                          Path(bytecode), capability))
    return tuple(resources)


class Boundary:
    def __init__(self, resources, record):
        self.resources = tuple(resources)
        self.record = record
        self.denied = False
        self.launch_permit = None
        self.launch_handles = False
        self.launch_thread = None
        self.paths = {}
        self.inodes = set()
        for resource in self.resources:
            if resource.capability not in PROTECTED:
                raise ProtocolFailure('invalid protected resource designation')
            path = resource.path.resolve()
            self.paths[path] = resource
            if path.exists():
                info = path.stat()
                self.inodes.add((info.st_dev, info.st_ino))

    def identity(self):
        return digest(canonical([{'resource': r.identity, 'path': str(r.path.resolve()),
                                  'capability': r.capability} for r in self.resources]))

    def implementation(self):
        return digest(Path(__file__).read_bytes())

    def deny(self, capability, resource='undeclared'):
        self.denied = True
        self.record({'classification': 'R5_61_PROTOCOL_HALT', 'quarantine': True,
                     'capability': capability, 'resource': resource,
                     'access': 'DENIED_BEFORE_CONTENT'})
        raise ProtocolFailure('R5_61_PROTOCOL_HALT: protected resource denied; quarantine')

    def require(self, capability, resource='undeclared'):
        # No R5.61 or prospective R5.62 B02 grant exists, declared or otherwise.
        if capability in PROTECTED:
            self.deny(capability, resource)
        if capability not in self.declared:
            self.deny('UNDECLARED_ACCESS', resource)

    def read(self, resource):
        # Check the authoritative registry, not a caller-supplied capability.
        if resource not in self.resources:
            self.deny('UNREGISTERED_RESOURCE')
        self.require(resource.capability, resource.identity)
        return resource.path.read_bytes()

    def evaluate(self, resource, evaluator):
        self.require('B02_STATIC_EVALUATION', resource.identity)
        return evaluator(self.read(resource))

    def audit(self, event, args):
        if event == 'open':
            target = args[0]
            if isinstance(target, int):
                if self.launch_handles and self.launch_thread == threading.get_ident():
                    # Adapter-owned pipe wrapping during the synchronous reviewed
                    # launch, not an inherited worker resource handle.
                    return
                # Existing handles cannot be safely assigned resource authority.
                self.deny('UNMEDIATED_DESCRIPTOR')
            try:
                path = Path(os.fsdecode(target)).resolve()
                resource = self.paths.get(path)
                if resource is not None:
                    self.deny(resource.capability, resource.identity)
                if path.exists():
                    info = path.stat()
                    if (info.st_dev, info.st_ino) in self.inodes:
                        self.deny('B02_AUTHORITY_READ', 'protected-alias')
            except (TypeError, ValueError):
                self.deny('UNRESOLVED_RESOURCE')
        elif event == 'subprocess.Popen' and self.launch_permit is not None:
            expected = self.launch_permit
            self.launch_permit = None
            if args != expected or self.launch_thread != threading.get_ident():
                self.deny('UNMEDIATED_EXECUTION')
        elif event in ('subprocess.Popen', 'os.system', 'os.posix_spawn', 'os.exec',
                       'os.fork', 'ctypes.dlopen', 'ctypes.dlsym', 'mmap.__new__'):
            self.deny('UNMEDIATED_EXECUTION')

    @contextmanager
    def mediated_launch(self, command, cwd, environment):
        # Only the content-pinned adapter is permitted to use this cooperative
        # internal API; qualified workers are reviewed, not hostile Python.
        if _active is not self or self.launch_permit is not None:
            self.deny('UNMEDIATED_EXECUTION')
        self.launch_permit = ((None, subprocess.list2cmdline(command), cwd, environment)
                              if os.name == 'nt' else (command[0], command, cwd, environment))
        self.launch_handles = True
        self.launch_thread = threading.get_ident()
        try:
            yield
        finally:
            self.launch_permit = None
            self.launch_handles = False
            self.launch_thread = None

    @contextmanager
    def stage(self, capabilities):
        global _active
        if _active is not None:
            raise ProtocolFailure('nested resource boundary prohibited')
        self.declared = authorize(capabilities)
        _active = self
        try:
            yield self
            if self.denied:
                raise ProtocolFailure('R5_61_PROTOCOL_HALT: denied access swallowed; quarantine')
        finally:
            _active = None


def _audit(event, args):
    boundary = _active
    if boundary is not None:
        boundary.audit(event, args)


sys.addaudithook(_audit)
