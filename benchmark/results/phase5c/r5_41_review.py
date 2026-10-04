"""Independent R5.41 evidence and lock; no benchmark evaluation entry."""

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]
RESULTS = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from benchmark.harness.test_optional_support_r5_41 import setup, admitted
from benchmark.results.phase5c.r5_38_review import run_suite
from benchmark.semantic import application_boundary_r5_41 as boundary
from benchmark.semantic import checked_launch_r5_36 as launch
from benchmark.semantic import current_pipeline as pipeline
from benchmark.semantic import profile_audit_r5_41 as audit
from benchmark.semantic import readiness_r5_41 as readiness
from benchmark.semantic import state_runtime_r5_41 as codec
from benchmark.semantic import transport_runtime_r5_41 as runtime
from benchmark.semantic.refined_generator_r5_28 import canonical, sha


def write(name, value):
    (RESULTS / name).write_bytes(canonical(value) + b'\n')


def read(name):
    return json.loads((RESULTS / name).read_bytes())


def matrix():
    rows, profiles = [], []
    values = {'integer': ('17', 17, 'bad', True, 19),
              'string': ('north', 'north', None, 17, 'south'),
              'instant': ('2030-01-02T03:04:05Z', '2030-01-02T03:04:05Z', 'yesterday', 17, '2031-01-02T03:04:05Z'),
              'boolean': ('true', True, 'bad', 17, False)}
    for base, (text, value, invalid, wrong, outside) in values.items():
        for optional in (True, False):
            for representation in ('text', 'json'):
                current = setup(base, optional, representation, [None, value])
                app, spec, state, config = current
                configuration = {'transport': spec, 'state': state, 'launch': config}
                prediction = readiness.inspect(*current)
                supplemental = audit.inspect(app, configuration)
                try:
                    profile = admitted(current)
                    actual_support = True
                except ValueError:
                    profile, actual_support = None, False
                if (prediction['status'] == 'READY') != actual_support or (supplemental['status'] == 'SUPPORTED') != actual_support:
                    raise ValueError('SUPPORT_MODEL_INCOHERENT')
                identity = f'{base}/{optional}/{representation}'
                profiles.append({'id': identity, 'readiness': prediction, 'audit': supplemental,
                                 'admitted': actual_support, 'application': app, **configuration})
                if profile is None:
                    continue
                route = profile['transport']['operations']['store']['alternatives']['V1']
                cases = [('omitted', {}, optional), ('explicit_null', {'value': None}, True),
                         ('valid_supplied', {'value': value if representation == 'json' else text}, True),
                         ('invalid_supplied', {'value': invalid}, base == 'string'),
                         ('type_failure', {'value': wrong}, False),
                         ('present_outside_durable_domain', {'value': outside}, True)]
                for label, raw, bind_expected in cases:
                    raw = {'code': 'sample', **raw}
                    binding = runtime.bind('store', raw, route)
                    binding_ok = binding['input'] is not None
                    if binding_ok != bind_expected:
                        raise ValueError('binding matrix mismatch')
                    durable = None if not binding_ok else {'revision': 1, 'samples': [binding['input']]}
                    domain = None if durable is None else codec.decode(canonical(durable), state)
                    domain_ok = domain is not None and domain['category'] is None
                    expected_domain = bind_expected and label != 'present_outside_durable_domain'
                    if domain_ok != expected_domain:
                        raise ValueError('domain matrix mismatch')
                    rows.append({'profile': identity, 'public_state': label, 'raw': raw, 'binding': binding,
                                 'explicit_null_public_path': representation == 'json',
                                 'null_probe_scope': 'raw binder; JSON public transfer is separately grounded' if label == 'explicit_null' and representation == 'text' else 'declared representation',
                                 'durable': durable, 'domain': domain, 'profile_readiness': prediction['status'],
                                 'value_disposition': 'ACCEPTED' if domain_ok else 'REJECTED',
                                 'audit_support': supplemental['status'], 'actual_profile_support': actual_support})
    return {'core_constructs': 30, 'profiles': profiles, 'rows': rows,
            'interpretation': 'Readiness predicts supported handling including rejection, not validity of every future input.'}


def public_evidence():
    calls = []
    for base, token, value in [('integer', '17', 17), ('string', 'north', 'north'),
                               ('instant', '2030-01-02T03:04:05Z', '2030-01-02T03:04:05Z')]:
        for representation in ('text', 'json'):
            current = setup(base, representation=representation, domain=[None, value])
            app, spec, state, config = current
            with tempfile.TemporaryDirectory() as bundle, tempfile.TemporaryDirectory() as directory:
                root, cwd = Path(bundle), Path(directory)
                boundary.generate(app, root, spec, state, config)
                supplied = token if representation == 'text' else json.dumps(value)
                scenarios = [('omitted', ['store', '--code', 'a'], {'code': 'a'}),
                             ('supplied', ['store', '--code', 'b', '--value', supplied], {'code': 'b', 'value': value})]
                if representation == 'json':
                    scenarios.append(('null', ['store', '--code', 'c', '--value', 'null'], {'code': 'c', 'value': None}))
                for label, argv, expected in scenarios:
                    event, public, before, after = launch.observe(root, cwd, config, argv)
                    semantic = event['semantic'] if event else None
                    grounded = (event is not None and event['pid'] == public['pid'] and
                                all(event[key] == public[key] for key in ('argv', 'cwd', 'stdout', 'stderr', 'exit')) and
                                event['pre_digest'] == runtime.digest(before) and event['post_digest'] == runtime.digest(after))
                    challenged = pipeline.challenge(app, root, semantic,
                        {'operation': 'store', 'invocation': event['invocation'], 'input': expected,
                         **event['transport']['semantic_result']},
                        event['transport']['effective_pre'].encode(), after)
                    conformant = (public['exit'] == 0 and semantic['input'] == expected and
                                  json.loads(after)['samples'][-1] == expected and
                                  codec.decode(after, state)['category'] is None and
                                  challenged['grounded'] and challenged['conformant'])
                    if not grounded or not conformant:
                        raise ValueError('independent public composition failed')
                    calls.append({'type': base, 'representation': representation, 'case': label,
                                  'event': event, 'public': public, 'pre': None if before is None else before.decode(),
                                  'post': after.decode(), 'grounded': grounded, 'conformant': conformant,
                                  'semantic_challenge': challenged})
    return calls


def integrity():
    historical = read('R5_40-implementation-profile-lock.json')
    identity = historical.pop('identity')
    mismatches = [name for name, digest in historical['files'].items() if sha((ROOT / name).read_bytes()) != digest]
    if mismatches or sha(canonical(historical)) != identity:
        raise ValueError({'PROTOCOL_FAILURE': mismatches})
    files = subprocess.check_output(['git', 'ls-files', 'benchmark', 'src', 'schema', 'air', 'generated'], cwd=ROOT, text=True).splitlines()
    altered = subprocess.check_output(['git', 'diff', '--name-only', 'HEAD', '--',
                                      'benchmark', 'src', 'schema', 'air', 'generated'], cwd=ROOT, text=True).splitlines()
    if altered:
        raise ValueError({'FROZEN_AUTHORITY_CONFLICT': altered})
    implementations = sorted((ROOT / 'benchmark/semantic').glob('*r5_41.py'))
    forbidden = ('B02', 'B03', 'B17', 'due_date', 'due-date', 'task_manager', 'invalid_due_date')
    contaminated = [str(path.relative_to(ROOT)) for path in implementations if any(token in path.read_text() for token in forbidden)]
    if contaminated:
        raise ValueError({'CONTAMINATION': contaminated})
    traces = []
    reference = 'benchmark/harness/test_optional_support_r5_41.py'
    for path, value in audit.leaves({'transport': setup()[1], 'state': setup()[2], 'launch': setup()[3]}):
        traces.append({'path': path, 'value': value, 'artifact': reference, 'sha256': sha((ROOT / reference).read_bytes()),
                       'clause': 'setup', 'interpretation': 'Independent measurement profile composed from declared shapes and public mappings.'})
    current = setup()
    config = {'transport': current[1], 'state': current[2], 'launch': current[3]}
    traceability = audit.traceability(config, traces, ROOT, {reference})
    write('R5_41-independent-profile-traceability.json', traces)
    return {'historical_lock_valid': True, 'historical_protected_files': len(historical['files']),
            'historical_head_checked': False, 'historical_head_reason': 'historical pre-commit lock; files and identity checked',
            'tracked_authority_files_unchanged': len(files), 'altered_authority_files': altered,
            'implementation_contamination': contaminated, 'traceability': traceability,
            'structure': audit.structure(config), 'profile_contamination': audit.contamination(config)}


def verify():
    if (RESULTS / 'R5_41-implementation-lock.json').exists():
        raise ValueError('verification replacement after lock prohibited')
    report = {'environment': {'python': sys.version, 'platform': platform.platform()},
              'suites': [], 'commands': [], 'b02_generated': False, 'b02_executed': False,
              'b02_static_passes': 0, 'b03_prospectively_exposed': False, 'b17_exposed': False}
    for directory, pattern, restrictions in [('benchmark/harness', 'test*.py', True), ('tests', 'test*.py', False),
                                            ('benchmark/results/phase5c', 'test_r5_37_evaluation.py', True),
                                            ('benchmark/harness', 'test_optional_support_r5_41.py', False)]:
        result = run_suite(directory, pattern, restrictions)
        for skip in result['skipped']:
            skip['reason'] = skip['reason'].replace('R5.38', 'R5.41')
        report['suites'].append(result)
    for command in ([sys.executable, '-m', 'air_compiler.cli', 'validate', 'air/task_manager.json'],
                    [sys.executable, '-m', 'air_compiler.cli', 'safety', 'air/task_manager.json'], ['git', 'diff', '--check']):
        completed = subprocess.run(command, cwd=ROOT, env={**os.environ, 'PYTHONPATH': 'src'}, capture_output=True, text=True)
        report['commands'].append({'command': command, 'exit': completed.returncode,
                                   'stdout': completed.stdout, 'stderr': completed.stderr})
    success = all(s['successful'] for s in report['suites']) and all(c['exit'] == 0 for c in report['commands'])
    if success:
        write('R5_41-independent-coherence-matrix.json', matrix())
        write('R5_41-independent-public-evidence.json', public_evidence())
        report['integrity'] = integrity()
    write('R5_41-verification.json', report)
    return success


def lock():
    if (RESULTS / 'R5_41-implementation-lock.json').exists():
        raise ValueError('lock replacement prohibited')
    verification = read('R5_41-verification.json')
    if not all(s['successful'] for s in verification['suites']) or 'integrity' not in verification:
        raise ValueError('required verification incomplete')
    names = subprocess.check_output(['git', 'ls-files', '--cached', '--others', '--exclude-standard'], cwd=ROOT, text=True).splitlines()
    excluded = ('R5_41-implementation-lock.json', 'R5_41-lock-verification.json',
                'R5_41-INDEPENDENT-OPTIONAL-BOUNDARY-SUPPORT-COHERENCE.md')
    names = sorted({name for name in names if name.startswith(('benchmark/', 'src/', 'schema/', 'air/', 'generated/'))
                    and not name.endswith(excluded)})
    names.append('docs/optional-boundary-support-r5.41.md')
    record = {'version': 'R5.41', 'time': datetime.now(timezone.utc).isoformat(),
              'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'files': {name: sha((ROOT / name).read_bytes()) for name in names}, 'b02_static_passes': 0}
    record['identity'] = sha(canonical(record))
    write('R5_41-implementation-lock.json', record)
    return lock_check()


def lock_check():
    record = read('R5_41-implementation-lock.json')
    identity = record.pop('identity')
    mismatches = [name for name, digest in record['files'].items() if sha((ROOT / name).read_bytes()) != digest]
    if mismatches or sha(canonical(record)) != identity or record['head'] != subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip():
        raise ValueError({'PROTOCOL_FAILURE': mismatches})
    result = {'valid': True, 'identity': identity, 'protected_files': len(record['files']), 'mismatches': mismatches}
    write('R5_41-lock-verification.json', result)
    return result


def summary():
    verification = read('R5_41-verification.json')
    evidence = read('R5_41-independent-coherence-matrix.json')
    calls = read('R5_41-independent-public-evidence.json')
    return {'suites': [{key: suite[key] for key in ('directory', 'pattern', 'discovered', 'passed', 'successful')}
                       for suite in verification['suites']],
            'command_exits': [command['exit'] for command in verification['commands']],
            'matrix_profiles': len(evidence['profiles']), 'matrix_rows': len(evidence['rows']),
            'supported_profiles': sum(p['admitted'] for p in evidence['profiles']),
            'grounded_conformant_public_calls': sum(call['grounded'] and call['conformant'] for call in calls),
            'integrity': verification['integrity'], 'b02_static_passes': 0}


if __name__ == '__main__':
    command = sys.argv[1]
    if command == 'verify':
        sys.exit(0 if verify() else 1)
    elif command == 'lock':
        print(json.dumps(lock()))
    elif command == 'lock-check':
        print(json.dumps(lock_check()))
    elif command == 'summary':
        print(json.dumps(summary(), indent=2))
    else:
        raise ValueError('no benchmark evaluation is authorized by this recorder')
