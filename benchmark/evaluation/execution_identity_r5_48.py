"""Fresh v2 dependency-domain identity and fail-closed certificate bridge.

Observed host captures are NOT immutable execution capsules. Production assembly
is deliberately rejected until native/import/descendant closure and ownership
are established. No request loader or production dispatch exists here.
"""

import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys

from benchmark.evaluation import preexposure_r5_45 as certificate
from benchmark.evaluation import security_r5_47 as security
from benchmark.evaluation.recorder_r5_43 import ProtocolFailure, canonical, digest

PROTOCOL = 'lykoi-execution-state-identity-v2-r5.48'
BASELINE = '31339cb73996c9ee728656558477436d9a5ba1cfbd0272c771720e6a1f6bf084'
DOMAINS = ('LANGUAGE_CORE', 'PROGRAM_DECLARED', 'BUILD_EXECUTION',
           'DEVELOPMENT_AUTHORING', 'OPTIONAL_TOOLING', 'IRRELEVANT', 'UNKNOWN')
AUTHORING = ('OPENAI_', 'ANTHROPIC_', 'GOOGLE_API_', 'GEMINI_', 'OPENCODE_',
             'CHATGPT_', 'CLAUDE_', 'DEVELOPMENT_MODEL', 'EDITOR', 'VISUAL', 'VSCODE_')
CONTROLS = {'PYTHONHASHSEED': {'0'}, 'PYTHONUTF8': {'1'},
            'PYTHONDONTWRITEBYTECODE': {'1'}}
PREFIXES = ('src/', 'air/', 'schema/', 'generated/', 'tests/', 'benchmark/')
OUTPUT = 'benchmark/results/phase5c/R5_48-evidence/'


def classify_variable(name):
    name = name.upper()
    if name.startswith(AUTHORING):
        return 'DEVELOPMENT_AUTHORING'
    if name in CONTROLS or name in {'PYTHONPATH', 'PATH', 'PATHEXT', 'SYSTEMROOT',
                                   'TEMP', 'TMP', 'COMSPEC'}:
        return 'BUILD_EXECUTION'
    if name.startswith(('PYTHON', 'GIT', 'LYKOI')) or name in {
            'HOME', 'USERPROFILE', 'LANG', 'LC_ALL', 'LC_CTYPE', 'TZ'}:
        return 'UNKNOWN'
    # Unrecognized variables are not assumed irrelevant to arbitrary programs.
    return 'UNKNOWN'


def effective_environment(values):
    """Only explicitly qualified enums enter this component, never AI state.

    Search paths/temp/system roots belong in resolved execution context. Unknown
    ambient variables require a closure investigation or removal in a capsule.
    """
    result = {}
    for name, allowed in CONTROLS.items():
        value = values.get(name)
        if value is not None and value not in allowed:
            raise ProtocolFailure('unqualified execution control')
        result[name] = {'present': value is not None, 'value': value}
    security.safe_bytes(result)
    return result


def isolated_environment(values, root):
    """Child-only sanitized environment; never modifies the authoring session.

    System/temp/search values are still material and recorded as unresolved
    context in observed captures; this is not an OS sandbox.
    """
    result = {n: values[n] for n in ('SYSTEMROOT', 'WINDIR', 'TEMP', 'TMP', 'PATH',
                                  'PATHEXT', 'COMSPEC') if n in values}
    result.update({n: next(iter(v)) for n, v in CONTROLS.items()})
    result['PYTHONPATH'] = str(Path(root) / 'src')
    return result


def relevant(name):
    return (name.startswith(PREFIXES) and not name.startswith(OUTPUT) and
            '/__pycache__/' not in name and not name.endswith(('.pyc', '.pyo')) and
            name != 'benchmark/results/phase5c/R5_48-EXECUTION-STATE-AND-AI-INDEPENDENCE.md')


def git(root, *args):
    process = subprocess.run(['git', *args], cwd=root, capture_output=True, timeout=15)
    if process.returncode:
        raise ProtocolFailure('repository inspection failed; details withheld')
    return process.stdout


def repository(root, predicate=relevant):
    """Physical effective bytes + scoped committed/index objects and modes.

    Author/editor configuration is outside this slice. Includes ignored inputs
    within execution directories; cached bytecode is excluded only for -B/-S
    observations and remains an explicit production closure gap.
    """
    root = Path(root).resolve()
    files = {}
    for directory, dirs, names in os.walk(root, followlinks=False):
        dirs[:] = [n for n in dirs if n not in {'.git', '__pycache__'}]
        for n in dirs:
            if (Path(directory) / n).is_symlink():
                raise ProtocolFailure('linked directory closure unsupported')
        for n in names:
            path = Path(directory) / n
            name = path.relative_to(root).as_posix()
            if predicate(name):
                if path.is_symlink() or not path.is_file():
                    raise ProtocolFailure('nonregular execution input')
                files[name] = {'sha256': digest(path.read_bytes()),
                               'executable': bool(path.stat().st_mode & 0o111) if os.name != 'nt' else None}
    def entries(data):
        selected = []
        for row in data.split(b'\0'):
            if not row:
                continue
            metadata, raw_name = row.split(b'\t', 1)
            name = os.fsdecode(raw_name)
            if predicate(name):
                if metadata.startswith(b'160000 ') or metadata.startswith(b'120000 '):
                    raise ProtocolFailure('submodule or linked input closure unsupported')
                selected.append({'path': name, 'object': metadata.decode('ascii')})
        return sorted(selected, key=lambda r: r['path'])
    committed = entries(git(root, 'ls-tree', '-rz', 'HEAD'))
    index = entries(git(root, 'ls-files', '--stage', '-z'))
    if any(r['object'].split()[-1] != '0' for r in index):
        raise ProtocolFailure('unmerged execution input')
    return certificate.seal({'files': files, 'committed': committed, 'index': index,
                             'slice': 'physical execution directories and scoped Git objects'})


def runtime():
    return {'implementation': sys.implementation.name, 'version': sys.version,
            'executable_sha256': digest(Path(sys.executable).read_bytes()),
            'flags': {n: getattr(sys.flags, n) for n in dir(sys.flags)
                      if not n.startswith('_') and type(getattr(sys.flags, n)) is int},
            'xoptions': dict(sys._xoptions), 'platform': platform.system(),
            'os_version': platform.version(), 'architecture': platform.machine(),
            'filesystem_encoding': sys.getfilesystemencoding(),
            'filesystem_errors': sys.getfilesystemencodeerrors()}


def implementations(resolved):
    result = []
    for name, item in sorted(resolved.items()):
        version, path = item
        path = Path(path)
        if not path.is_file() or path.is_symlink() or not version:
            raise ProtocolFailure('resolved implementation unavailable')
        # Module names such as stdlib "token" are identifiers, not credential
        # fields. Typed rows preserve the publication guard without exceptions.
        result.append({'name': name, 'version': version, 'sha256': digest(path.read_bytes())})
    return result


def compose(repo, interpreter, dependencies, environment, tools, context, *,
            scope='observed-host', unknown=()):
    certificate.unseal(repo)
    if scope not in {'observed-host', 'closed-fixture'}:
        raise ProtocolFailure('unqualified scope promotion')
    body = {'protocol': PROTOCOL, 'scope': scope, 'infrastructure': BASELINE,
            'repository': repo, 'runtime': interpreter, 'dependencies': dependencies,
            'environment': environment, 'tools': tools, 'context': context,
            'unknown': sorted(set(unknown))}
    security.safe_bytes(body)
    result = certificate.seal(body)
    check(result)
    return result


def check(value, complete=False):
    body = certificate.unseal(value)
    if (set(body) != {'protocol', 'scope', 'infrastructure', 'repository', 'runtime',
                     'dependencies', 'environment', 'tools', 'context', 'unknown'} or
            body['protocol'] != PROTOCOL or body['infrastructure'] != BASELINE or
            body['scope'] not in {'observed-host', 'closed-fixture'}):
        raise ProtocolFailure('invalid execution identity')
    certificate.unseal(body['repository'])
    security.safe_bytes(value)
    if set(body['environment']) != set(CONTROLS):
        raise ProtocolFailure('execution environment outside qualified control boundary')
    reconstructed = {}
    for name, item in body['environment'].items():
        if type(item) is not dict or set(item) != {'present', 'value'} or type(item['present']) is not bool:
            raise ProtocolFailure('invalid effective environment entry')
        if item['present']:
            reconstructed[name] = item['value']
        elif item['value'] is not None:
            raise ProtocolFailure('absent environment value must be null')
    if effective_environment(reconstructed) != body['environment']:
        raise ProtocolFailure('unqualified effective environment')
    if (type(body['unknown']) is not list or any(type(n) is not str for n in body['unknown']) or
            body['unknown'] != sorted(set(body['unknown']))):
        raise ProtocolFailure('invalid material unknown inventory')
    if complete and (body['unknown'] or body['scope'] != 'closed-fixture'):
        raise ProtocolFailure('production execution closure or ownership unqualified')
    return body


def bridge(value):
    check(value)
    return certificate.seal({'protocol': certificate.PROTOCOL,
                             'execution_protocol': PROTOCOL, 'execution': value})


def stage(before, after, name, result, mechanism):
    check(before)
    check(after)
    if canonical(before) != canonical(after):
        raise ProtocolFailure('material mid-stage mutation; no reusable PASS')
    security.safe_bytes(result)
    return certificate.stage(bridge(before)['identity'], name, 'PASS', result, mechanism)


def assemble(frozen, evidence, policy):
    check(frozen, complete=True)
    if policy.get('purpose') != 'synthetic-only':
        raise ProtocolFailure('production capsule qualification required')
    if policy.get('infrastructure') != BASELINE or policy.get('execution_protocol') != PROTOCOL:
        raise ProtocolFailure('certificate baseline or execution protocol mismatch')
    if set(evidence) != set(policy['stages']):
        raise ProtocolFailure('incomplete verification set')
    for name in ('identity', 'locks', 'contamination'):
        if name not in policy['stages']:
            raise ProtocolFailure('required certificate guarantee absent')
    if evidence['locks']['result'].get('infrastructure') != BASELINE:
        raise ProtocolFailure('unqualified infrastructure receipt')
    required_locks = policy.get('required_locks')
    if (type(required_locks) is not dict or set(required_locks) != {'historical', 'prospective', 'infrastructure'} or
            required_locks['infrastructure'] != BASELINE or
            evidence['locks']['result'].get('required_lock_state') != required_locks):
        raise ProtocolFailure('required lock state mismatch')
    if evidence['contamination']['result'].get('findings') != []:
        raise ProtocolFailure('contamination receipt not clean')
    security.safe_bytes(policy)
    return certificate.assemble(bridge(frozen), evidence, policy)


def validate(cert, frozen, evidence, policy, current):
    check(current, complete=True)
    expected = assemble(frozen, evidence, policy)
    if canonical(expected) != canonical(cert):
        raise ProtocolFailure('invalid certificate assembly')
    return certificate.validate(cert, bridge(frozen), evidence, policy, bridge(current))


def authorize_synthetic(cert, frozen, evidence, policy, capture, recorder, callback):
    current = capture()
    validate(cert, frozen, evidence, policy, current)
    return certificate.synthetic_authorize(cert, bridge(frozen), evidence, policy,
                                          bridge(current), recorder, callback)


def observed(root, values):
    """Honest bounded observation, never a complete-production assertion."""
    executable = shutil.which('git')
    if not executable:
        raise ProtocolFailure('required evaluator tool unavailable')
    origins = {}
    for name, module in sorted(sys.modules.items()):
        path = getattr(module, '__file__', None)
        if path and Path(path).is_file() and not Path(path).resolve().is_relative_to(Path(root).resolve()):
            origins[name] = (sys.version.split()[0], path)
    environment = isolated_environment(values, root)
    return compose(repository(root), runtime(), implementations(origins),
                   effective_environment(environment),
                   implementations({'git': ('resolved-executable', executable)}),
                   {'cwd': 'repository-root', 'argv_policy': 'bounded stage definition',
                    'child_import_root': 'src', 'child_site': 'disabled with -S',
                    'external_context_presence': {n: {'present': n in environment} for n in
                        ('SYSTEMROOT', 'WINDIR', 'TEMP', 'TMP', 'PATH', 'PATHEXT', 'COMSPEC')}},
                   unknown=('transitive native Python/Git libraries and OS services',
                            'late-loaded and descendant import closure including readable bytecode',
                            'effective Git attributes/config helpers and filesystem ownership',
                            'mutable runtime/tool/context ownership and ABA window'))
