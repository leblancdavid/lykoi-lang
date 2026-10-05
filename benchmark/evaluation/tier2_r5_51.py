"""Tier-2 state, certificates and cooperative single-observation gate.

No request loader is provided. R5.51 dispatch is restricted to explicitly named
synthetic observations. Platform services are declared, not recursively hashed.
All publication uses the R5.47 guard; all reservations use the R5.43 recorder.
"""

import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time

from benchmark.evaluation import preexposure_r5_45 as envelopes
from benchmark.evaluation import security_r5_47 as security
from benchmark.evaluation.recorder_r5_43 import PROTOCOL as CANONICAL_PROTOCOL
from benchmark.evaluation.recorder_r5_43 import ProtocolFailure, canonical, digest, loads

PROTOCOL = 'lykoi-tier2-experimental-capsule-r5.51-v1'
INFRASTRUCTURE = '31339cb73996c9ee728656558477436d9a5ba1cfbd0272c771720e6a1f6bf084'
ROLES = ('subject', 'compiler', 'semantics', 'profiles', 'authority', 'evaluator')
CONTROLS = {'PYTHONHASHSEED': '0', 'PYTHONUTF8': '1', 'PYTHONDONTWRITEBYTECODE': '1'}
REQUIRED = ('identity', 'locks', 'contamination', 'workspace')


def seal(body):
    security.safe_bytes(body)
    return envelopes.seal(body)


def check(value):
    security.safe_bytes(value)
    body = envelopes.unseal(value)
    if (body.get('protocol') != PROTOCOL or body.get('kind') != 'capsule' or
            type(body.get('semantic_count')) is not int or body['semantic_count'] != 30 or
            set(body.get('roles', {})) != set(ROLES) or
            any(not body['roles'][r] for r in ROLES) or body.get('unknown') != []):
        raise ProtocolFailure('invalid or incomplete Tier-2 capsule')
    return body


def relative(name):
    path = Path(name)
    if (type(name) is not str or not name or path.is_absolute() or
            '..' in path.parts or name != path.as_posix() or name == '.'):
        raise ProtocolFailure('invalid scoped path')
    security.safe_bytes(name)
    return name


def regular(path):
    path = Path(path)
    if path.is_symlink() or any(p.is_symlink() for p in path.parents) or not path.is_file():
        raise ProtocolFailure('unresolved or nonregular material input')
    return {'sha256': digest(path.read_bytes()),
            'mode': (path.stat().st_mode & 0o777) if os.name != 'nt' else None}


def selected(root, scopes, *, export=False):
    """Explicit file/directory roles; directory membership includes ignored inputs.

    Bytecode is rejected rather than silently excluded: -B does not prevent reads.
    Authoring state is outside these consumer roots, never name-exempted inside them.
    """
    result = {}
    for role, names in scopes.items():
        for name in names:
            path = root / relative(name)
            if path.is_symlink():
                raise ProtocolFailure('linked material root')
            if path.is_file():
                result.setdefault(name, []).append(role)
            elif path.is_dir():
                for directory, dirs, files in os.walk(path, followlinks=False):
                    parent = Path(directory)
                    if any((parent / n).is_symlink() for n in dirs):
                        raise ProtocolFailure('linked material directory')
                    if export:
                        dirs[:] = [n for n in dirs if n != '__pycache__']
                        files = [n for n in files if not n.endswith(('.pyc', '.pyo'))]
                    elif '__pycache__' in dirs or any(n.endswith(('.pyc', '.pyo')) for n in files):
                        raise ProtocolFailure('input bytecode is prohibited')
                    for n in files:
                        item = (parent / n).relative_to(root).as_posix()
                        result.setdefault(item, []).append(role)
            else:
                raise ProtocolFailure('required material root absent')
    return {n: sorted(set(r)) for n, r in sorted(result.items())}


def git(root, *args):
    # Only object/index inspection: no filters, hooks, network or ancestry checks.
    tool = shutil.which('git')
    if not tool:
        raise ProtocolFailure('required Git tool unavailable')
    env = {n: os.environ[n] for n in ('SYSTEMROOT', 'WINDIR', 'PATH', 'TEMP', 'TMP') if n in os.environ}
    env.update({'GIT_CONFIG_NOSYSTEM': '1', 'GIT_CONFIG_GLOBAL': os.devnull,
                'GIT_NO_REPLACE_OBJECTS': '1', 'GIT_OPTIONAL_LOCKS': '0'})
    p = subprocess.run([tool, '--no-replace-objects', '-c', 'core.fsmonitor=false', *args],
                       cwd=root, env=env, capture_output=True, timeout=10)
    if p.returncode:
        raise ProtocolFailure('Git content inspection failed; details withheld')
    return p.stdout


def repository(root, scopes):
    root = Path(root).resolve()
    names = selected(root, scopes)
    def relevant(name):
        return any(name == s or name.startswith(s + '/') for group in scopes.values() for s in group)
    def entries(data, index=False):
        result = {}
        for row in data.split(b'\0'):
            if not row:
                continue
            meta, raw = row.split(b'\t', 1)
            name = os.fsdecode(raw)
            if not relevant(name):
                continue
            parts = meta.decode('ascii').split()
            if parts[0] in {'120000', '160000'} or (index and parts[2] != '0'):
                raise ProtocolFailure('linked, submodule or unmerged material input')
            oid = parts[1] if index else parts[2]
            # Git blob IDs are content identities, independent of index storage,
            # branch/reflog/packing trivia. Physical execution bytes use SHA-256.
            result[name] = {'mode': parts[0], 'git_blob': oid}
        return result
    committed = entries(git(root, 'ls-tree', '-rz', 'HEAD'))
    index = entries(git(root, 'ls-files', '--stage', '-z'), True)
    return {name: {'roles': names.get(name, []),
                   'physical': regular(root / name) if name in names else None,
                   'committed': committed.get(name), 'index': index.get(name)}
            for name in sorted(set(names) | set(committed) | set(index))}


def declared_platform():
    return {'os_family': platform.system(), 'os_version_build': platform.version(),
            'architecture': platform.machine(), 'python_implementation': sys.implementation.name,
            'python_version_build': sys.version, 'filesystem_encoding': sys.getfilesystemencoding(),
            'filesystem_errors': sys.getfilesystemencodeerrors(),
            'assumptions': ['local reliable exclusive-create and fsync', 'no malicious concurrent host',
                            'case/path rules of declared OS', 'ordinary unmodified Python stdlib and native OS services'],
            'native_boundary': 'CRT, crypto, kernel and ordinary system libraries declared; no recursive closure'}


def dependency(name, version, path, reason):
    if not name or not version or not reason:
        raise ProtocolFailure('dependency lacks resolved version or materiality reason')
    return {'name': name, 'version': version, 'resolved': str(Path(path).resolve()),
            'implementation': regular(path), 'materiality': reason}


def controlled_environment(ambient, root):
    """Effective worker environment, not an ambient variable inventory.

    The observation consumer must use this mapping and explicit -B -S startup.
    No provider credentials, authoring config or unrelated variables are forwarded.
    Host substrate values are declared working context, not authoring identifiers.
    """
    values = {n: ambient[n] for n in ('SYSTEMROOT', 'WINDIR', 'TEMP', 'TMP', 'PATH', 'PATHEXT', 'COMSPEC',
                                    'LYKOI_R551_EVIDENCE') if n in ambient}
    values.update(CONTROLS)
    values['PYTHONPATH'] = str(Path(root).resolve() / 'src')
    security.safe_bytes(values)
    return values


def capture(root, policy, environment, dependencies=(), tools=(), platform_state=None):
    root = Path(root).resolve()
    security.safe_bytes(policy)
    if set(policy['scopes']) != set(ROLES) or policy.get('unknown') != []:
        raise ProtocolFailure('material boundary incomplete')
    if any(environment.get(k) != v for k, v in CONTROLS.items()):
        raise ProtocolFailure('required execution controls absent')
    files = repository(root, policy['scopes'])
    roles = {r: digest(canonical({n: v for n, v in files.items() if r in v['roles']})) for r in ROLES}
    if any(not any(r in v['roles'] for v in files.values()) for r in ROLES):
        raise ProtocolFailure('required role empty')
    # Re-resolve bytes on every capture, not supplied hashes from an old inventory.
    resolved = [dependency(d['name'], d['version'], d['resolved'], d['materiality']) for d in dependencies]
    resolved_tools = [dependency(d['name'], d['version'], d['resolved'], d['materiality']) for d in tools]
    value = seal({'protocol': PROTOCOL, 'kind': 'capsule', 'policy': policy,
                  'semantic_count': 30, 'roles': roles, 'repository': files,
                  'dependencies': sorted(resolved, key=lambda d: d['name']),
                  'tools': sorted(resolved_tools, key=lambda d: d['name']),
                  'python': dependency('python', sys.version, sys.executable, 'parsing, lowering and evaluator execution'),
                  'effective_environment': environment,
                  'context': {'root': str(root), 'startup': '-B -S; input bytecode absent',
                              'outputs': 'outside all material/import/discovery roots'},
                  'platform': declared_platform() if platform_state is None else platform_state,
                  'unknown': []})
    check(value)
    return value


def receipt(before, after, experiment, name, mechanism, status, result):
    check(before)
    check(after)
    if status not in ('PASS', 'FAIL', 'INCOMPLETE'):
        raise ProtocolFailure('invalid stage status')
    if before != after:
        status, result = 'FAIL', {'successful': False, 'reason': 'material stage drift'}
    return seal({'protocol': PROTOCOL, 'kind': 'receipt', 'capsule': before['identity'],
                 'experiment': experiment, 'stage': name, 'mechanism': mechanism,
                 'status': status, 'result': result})


def certificate(capsule, evidence, policy):
    check(capsule)
    security.safe_bytes(policy)
    if (not set(REQUIRED).issubset(policy['stages']) or set(evidence) != set(policy['stages']) or
            policy['infrastructure'] != INFRASTRUCTURE or policy['semantic_count'] != 30 or
            policy['canonical_protocol'] != CANONICAL_PROTOCOL or
            policy['authority'] != capsule['roles']['authority'] or
            policy['recorder'] != capsule['policy']['recorder']):
        raise ProtocolFailure('certificate policy incomplete or incompatible')
    for name, value in evidence.items():
        b = envelopes.unseal(value)
        if (b.get('protocol') != PROTOCOL or b.get('kind') != 'receipt' or
                b.get('capsule') != capsule['identity'] or b.get('experiment') != policy['experiment'] or
                b.get('stage') != name or b.get('mechanism') != policy['stages'][name] or
                b.get('status') != 'PASS' or b['result'].get('successful') is not True):
            raise ProtocolFailure('missing, mixed, stale or unsuccessful stage')
    locks = evidence['locks']['result']
    if (locks.get('required_lock_state') != policy['required_locks'] or
            set(policy['required_locks']) != {'historical', 'prospective', 'infrastructure'} or
            policy['required_locks']['infrastructure'] != INFRASTRUCTURE):
        raise ProtocolFailure('required locks not established')
    if evidence['contamination']['result'].get('findings') != []:
        raise ProtocolFailure('contamination not clean')
    if (evidence['identity']['result'].get('semantic_count') != 30 or
            evidence['workspace']['result'].get('dedicated') is not True):
        raise ProtocolFailure('semantic identity or dedicated workspace not established')
    return seal({'protocol': PROTOCOL, 'kind': 'certificate', 'capsule': capsule['identity'],
                 'policy': policy, 'receipts': {n: evidence[n]['identity'] for n in sorted(evidence)},
                 'infrastructure': INFRASTRUCTURE, 'canonical_protocol': CANONICAL_PROTOCOL,
                 'recorder': policy['recorder'], 'authority': policy['authority'],
                 'semantic_count': 30, 'contamination': 'clean', 'locks': policy['required_locks']})


def validate(cert, capsule, evidence, policy, current):
    check(current)
    if current != capsule or cert != certificate(capsule, evidence, policy):
        raise ProtocolFailure('stale capsule or certificate')
    return True


class Workspace:
    """Fresh durable ownership marker for a cooperative, dedicated directory.

    The root is a materialized input copy, never an authoring checkout. Evidence
    sits outside it. A marker is retained forever: stopped runs cannot re-enter.
    This discourages accidents; it is not adversarial isolation or an ABA proof.
    """

    def __init__(self, root, evidence, experiment):
        self.root, self.evidence = Path(root).resolve(), Path(evidence).resolve()
        self.experiment = experiment
        self.marker = self.evidence / 'workspace.json'

    @staticmethod
    def materialize(source, destination, scopes):
        """Fresh cooperative copy of actual bytes and original scoped Git state.

        No checkout/filter/line-ending conversion. Shared Git objects are used
        only for read-only provenance; physical experiment inputs are independent.
        No authoring credentials/config are copied, and no input caches survive.
        """
        source, destination = Path(source).resolve(), Path(destination).resolve()
        if destination.exists() or not destination.parent.is_dir():
            raise ProtocolFailure('materialization requires a fresh root and existing parent')
        scoped = selected(source, scopes, export=True)
        tracked = [os.fsdecode(n) for n in git(source, 'ls-files', '-z').split(b'\0') if n]
        names = sorted(set(tracked) | set(scoped))
        # Keep unrelated authoring files out even if somebody tracks them. They
        # must not also occur in a consumed root: that would be a boundary error.
        def authoring(name):
            return name.startswith(('.opencode/', '.idea/', '.vscode/')) or name in {'opencode.json', 'opencode.jsonc'}
        if any(authoring(n) for n in scoped):
            raise ProtocolFailure('authoring exclusion overlaps a material input')
        names = [relative(n) for n in names if not authoring(n) and '__pycache__' not in Path(n).parts and
                 not n.endswith(('.pyc', '.pyo')) and (source / n).is_file()]
        before = {n: regular(source / n) for n in names}
        tool = shutil.which('git')
        env = controlled_environment(os.environ, source)
        env.update({'GIT_CONFIG_NOSYSTEM': '1', 'GIT_CONFIG_GLOBAL': os.devnull,
                    'GIT_NO_REPLACE_OBJECTS': '1'})
        process = subprocess.run([tool, '-c', 'core.hooksPath=' + os.devnull, 'clone',
                                  '--no-checkout', '--shared', '--local', '--', str(source), str(destination)],
                                 env=env, capture_output=True, timeout=30)
        if process.returncode:
            raise ProtocolFailure('cooperative source materialization failed')
        index = git(source, 'ls-files', '--stage', '-z')
        for args, data in [(['read-tree', '--empty'], None), (['update-index', '-z', '--index-info'], index)]:
            p = subprocess.run([tool, *args], cwd=destination, env=env, input=data,
                               capture_output=True, timeout=10)
            if p.returncode:
                raise ProtocolFailure('Git content/index materialization failed')
        for n in names:
            target = destination / n
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source / n, target)
        after = {n: regular(source / n) for n in names}
        copied = {n: regular(destination / n) for n in names}
        if before != after or before != copied or index != git(source, 'ls-files', '--stage', '-z'):
            raise ProtocolFailure('materialization drift; copied workspace invalid')
        return seal({'protocol': PROTOCOL, 'kind': 'materialization', 'files': copied,
                     'source': str(source), 'root': str(destination),
                     'cache_policy': 'fresh inputs; all pyc/pyo and __pycache__ omitted',
                     'source_index': digest(index), 'successful': True})

    def enter(self):
        if (not self.root.is_dir() or not self.evidence.is_dir() or
                self.evidence == self.root or self.evidence.is_relative_to(self.root) or
                self.root.is_relative_to(self.evidence)):
            raise ProtocolFailure('workspace and output paths must be separate')
        if any(self.evidence.iterdir()):
            raise ProtocolFailure('dedicated evidence directory must be fresh')
        security.persist(self.marker, seal({'protocol': PROTOCOL, 'experiment': self.experiment,
                                           'root': str(self.root), 'dedicated': True,
                                           'cooperative': True, 'automatic_updates': 'disabled by operator',
                                           'no_intentional_mutation': True}))
        return self.verify()

    def verify(self):
        marker = envelopes.reload(self.marker)
        if (marker['experiment'] != self.experiment or marker['root'] != str(self.root) or
                marker.get('dedicated') is not True or marker.get('cooperative') is not True):
            raise ProtocolFailure('workspace ownership mismatch')
        return marker


class StaticGate:
    def __init__(self, workspace, cert, capsule, evidence, policy, capture_state, checks, seconds=10):
        self.workspace, self.cert, self.capsule = workspace, cert, capsule
        self.evidence, self.policy, self.capture = evidence, policy, capture_state
        self.checks, self.seconds = checks, seconds
        self.recorder = security.PublicationRecorder(workspace.evidence)

    def prepare(self):
        self.workspace.verify()
        validate(self.cert, self.capsule, self.evidence, self.policy, self.capture())
        # Persist the certificate and all required evidence, then protect their bytes.
        for name, item in [('capsule', self.capsule), ('certificate', self.cert), *self.evidence.items()]:
            security.persist(self.workspace.evidence / (name + '-staged.json'), item)
        protected = list(self.workspace.evidence.glob('*-staged.json')) + [self.workspace.marker]
        self.recorder.freeze({'certificate': self.cert['identity'], 'capsule': self.capsule['identity'],
                              'experiment': self.policy['experiment']}, protected)

    def live_checks(self):
        if set(self.checks) != {'locks', 'authority', 'contamination'}:
            raise ProtocolFailure('live verification mechanisms absent')
        for name in sorted(self.checks):
            result = self.checks[name]()
            security.safe_bytes(result)
            expected = (self.policy['required_locks'] if name == 'locks' else
                        self.policy['authority'] if name == 'authority' else [])
            if result != expected:
                raise ProtocolFailure('live verification failed')

    def observe_synthetic(self, name, callback):
        # No B02 identifier or production request can enter the R5.51 dispatch path.
        if not name.startswith('synthetic:') or 'b02' in name.casefold():
            raise ProtocolFailure('R5.51 permits only synthetic qualification')
        started = time.monotonic()
        try:
            self.recorder.open_run()
            self.workspace.verify()
            self.live_checks()
            self.recorder.integrity()
            if self.recorder.counts()['disposition'] != 'zero':
                raise ProtocolFailure('one observation only')
            current = self.capture()
            validate(self.cert, self.capsule, self.evidence, self.policy, current)
            if time.monotonic() - started > self.seconds:
                raise ProtocolFailure('bounded pre-observation check exceeded')
            security.persist(self.workspace.evidence / 'pre-state.json', current)
            baseline = self.recorder.read('baseline')['evidence']
            self.recorder.verify(baseline)
            result = self.recorder.observe(callback)
            # First action after recorder completion: independently recapture state.
            post_started = time.monotonic()
            after = self.capture()
            security.persist(self.workspace.evidence / 'post-state.json', after)
            validate(self.cert, self.capsule, self.evidence, self.policy, after)
            self.workspace.verify()
            self.live_checks()
            self.recorder.integrity()
            if self.recorder.counts()['disposition'] != 'one':
                raise ProtocolFailure('exactly one completed observation required')
            if time.monotonic() - post_started > self.seconds:
                raise ProtocolFailure('bounded post-observation check exceeded')
            self.recorder.verify(baseline)
            final = self.recorder.finish()
            security.persist(self.workspace.evidence / 'gate-result.json', seal({
                'protocol': PROTOCOL, 'status': 'PASS', 'certificate': self.cert['identity'],
                'observation': name, 'counts': final['counts'], 'result': result,
                'repair_permitted': False}))
            return result
        except Exception:
            self.recorder.halt('Tier-2 gate failed; details withheld')
            if not self.recorder.path('final').exists():
                self.recorder.finish()
            raise ProtocolFailure('Tier-2 observation invalid; repair/retry prohibited') from None

    def prohibit_repair(self):
        if self.recorder.counts()['disposition'] != 'zero':
            raise ProtocolFailure('post-exposure repair prohibited')
        self.recorder.open_run()
