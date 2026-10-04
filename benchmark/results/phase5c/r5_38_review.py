"""R5.38 evidence recorder. B02 has a static-only entry after byte lock verification.

Full discovery is restriction-aware: historical B02 rendering/execution and
nested frozen acceptance are skipped explicitly, never silently run.
"""

import collections
from datetime import datetime, timezone
import fnmatch
import io
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
RESULTS = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from benchmark.semantic import nullable_study_r5_38 as study
from benchmark.semantic import readiness_r5_38 as readiness
from benchmark.semantic import current_pipeline as pipeline
from benchmark.semantic import refined_generator_r5_28 as emitter


def write(name, value):
    (RESULTS / name).write_bytes(emitter.canonical(value) + b'\n')


def flatten(suite):
    for test in suite:
        if isinstance(test, unittest.TestSuite):
            yield from flatten(test)
        else:
            yield test


def run_suite(directory, pattern='test*.py', restrictions=False):
    suite = unittest.defaultTestLoader.discover(str(ROOT / directory), pattern=pattern)
    tests = list(flatten(suite))
    modules = collections.Counter(t.__class__.__module__ for t in tests)
    for test in tests:
        identity = test.id()
        reason = None
        if restrictions and identity.startswith(('test_b02_retry_r5_17.', 'test_b02_retry_r5_19.',
                                                 'test_b02_retry_r5_21.', 'test_b02_integration_r5_23.')):
            reason = 'R5.38 prohibits B02 generation/retry, including historical diagnostic rendering'
        if restrictions and identity.endswith('test_read_only_validation_of_both_continuation_states'):
            reason = 'R5.38 prohibits nested frozen B02 acceptance; historical checkpoint replay would run it'
        if identity.endswith('test_lock_and_frozen_artifacts_remain_byte_identical'):
            reason = 'R5.37 live-tree architecture lock is historical; two prospective implementations intentionally changed in R5.38'
        if reason:
            def skip(reason=reason):
                raise unittest.SkipTest(reason)
            setattr(test, test._testMethodName, skip)
    stream = io.StringIO()
    started = time.monotonic()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(unittest.TestSuite(tests))
    record = {'directory': directory, 'pattern': pattern, 'discovered': result.testsRun,
        'passed': result.testsRun - len(result.skipped) - len(result.failures) - len(result.errors),
        'skipped': [{'test': t.id(), 'reason': reason} for t, reason in result.skipped],
        'failures': [{'test': t.id(), 'traceback': trace} for t, trace in result.failures],
        'errors': [{'test': t.id(), 'traceback': trace} for t, trace in result.errors],
        'seconds': round(time.monotonic() - started, 3), 'modules': dict(modules),
        'successful': result.wasSuccessful(), 'output': stream.getvalue()}
    print(json.dumps({k: record[k] for k in ('directory', 'pattern', 'discovered', 'passed', 'successful', 'seconds')}))
    return record


def verification():
    report = {'environment': {'python': sys.version, 'executable': sys.executable,
        'platform': platform.platform(), 'shell': 'PowerShell 7',
        'autocrlf': subprocess.check_output(['git', 'config', '--get', 'core.autocrlf'], cwd=ROOT, text=True).strip()},
        'restrictions': {'b02_generation': False, 'frozen_b02_acceptance': False}, 'suites': [], 'commands': []}
    report['suites'].append(run_suite('benchmark/harness', restrictions=True))
    report['suites'].append(run_suite('tests'))
    report['suites'].append(run_suite('benchmark/results/phase5c', 'test_r5_37_evaluation.py', restrictions=True))
    environment = {**os.environ, 'PYTHONPATH': 'src'}
    for command in ([sys.executable, '-m', 'air_compiler.cli', 'validate', 'air/task_manager.json'],
                    [sys.executable, '-m', 'air_compiler.cli', 'safety', 'air/task_manager.json'],
                    ['git', 'diff', '--check']):
        result = subprocess.run(command, cwd=ROOT, env=environment, capture_output=True, text=True)
        report['commands'].append({'command': command, 'exit': result.returncode,
                                   'stdout': result.stdout, 'stderr': result.stderr})
        print(json.dumps(report['commands'][-1]))
    write('R5_38-verification.json', report)
    return all(r['successful'] for r in report['suites']) and all(r['exit'] == 0 for r in report['commands'])


def evidence():
    write('R5_38-domain-refinement-matrix.json', readiness.closure_matrix())
    write('R5_38-domain-pipeline-evidence.json', readiness.validate_matrix_pipeline())
    write('R5_38-nullable-evidence.json', study.study())
    model, spec, declaration, config = study.setup()
    write('R5_38-independent-readiness.json', readiness.inspect(model, spec, declaration, config))
    write('R5_38-independent-contract.json', {'application': model, 'transport': spec, 'state': declaration, 'launch': config})
    calls = []
    import tempfile
    from benchmark.semantic import checked_launch_r5_36 as launch
    with tempfile.TemporaryDirectory() as bundle, tempfile.TemporaryDirectory() as directory:
        root, cwd = Path(bundle), Path(directory)
        launch.generate(model, root, spec, declaration, config)
        (cwd / config['store']['path']).write_bytes(emitter.canonical(study.population()))
        for operation in ('earlier', 'ordered', 'reviewed', 'window', 'replace', 'earlier', 'remove'):
            event, public, before, after = launch.observe(root, cwd, config, [operation, '--cutoff', study.CUTOFF])
            calls.append({'operation': operation, 'event': event, 'public': public,
                'pre': before.decode(), 'post': after.decode(),
                'verdict': launch.challenge(model, root, spec, declaration, config, event, public, before, after)})
    write('R5_38-whole-contract-execution.json', calls)
    negative = study.application()
    order = negative['operations']['ordered']['branches'][0]['value']['order']
    order['source'] = {'select': {'source': order['source'], 'where': study.lit(True, 'boolean')}}
    write('R5_38-negative-readiness.json', {'source': negative, 'readiness': readiness.inspect(negative)})


def lock():
    tracked = subprocess.check_output(['git', 'ls-files'], cwd=ROOT, text=True).splitlines()
    files = [name for name in tracked if name.startswith(('benchmark/', 'src/', 'schema/', 'generated/'))]
    files += [str(p.relative_to(ROOT)).replace('\\', '/') for p in (ROOT / 'benchmark/semantic').glob('*r5_38.py')]
    files += [str(p.relative_to(ROOT)).replace('\\', '/') for p in (ROOT / 'benchmark/harness').glob('*r5_38.py')]
    files += ['benchmark/results/phase5c/r5_38_review.py',
              'benchmark/results/phase5c/R5_38-domain-refinement-matrix.json',
              'docs/nullable-readiness-r5.38.md']
    record = {'version': 'R5.38', 'time': datetime.now(timezone.utc).isoformat(),
        'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'status': subprocess.check_output(['git', 'status', '--short'], cwd=ROOT, text=True),
        'files': {name: emitter.sha((ROOT / name).read_bytes()) for name in sorted(set(files))}}
    record['identity'] = emitter.sha(emitter.canonical(record))
    write('R5_38-implementation-lock.json', record)
    return record


def verify_lock():
    record = json.loads((RESULTS / 'R5_38-implementation-lock.json').read_bytes())
    identity = record.pop('identity')
    mismatches = [name for name, expected in record['files'].items() if emitter.sha((ROOT / name).read_bytes()) != expected]
    valid = (identity == emitter.sha(emitter.canonical(record)) and not mismatches and
        record['head'] == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip())
    result = {'valid': valid, 'identity': identity, 'protected_files': len(record['files']), 'mismatches': mismatches}
    if not valid:
        raise ValueError(result)
    return result


def frozen_static():
    before = verify_lock()
    # The saved reconstruction is read-only. This entry cannot emit even if an
    # accidental downstream call is introduced later.
    path = RESULTS / 'R5_37-b02-semantic-application.json'
    model = json.loads(path.read_bytes())
    obligations = [
        {'kind': 'public_state_alternatives', 'reference': 'R5.37 C18-C23',
         'public': ['list', 'list-high', 'list-overdue', 'migrate']},
        {'kind': 'durable_content_constraints', 'reference': 'R5.37 C07/C18-C23',
         'constraints': ['unique identities', 'nonblank identities/titles', 'status domain', 'priority domain']}]
    with (patch.object(pipeline, 'generate', side_effect=AssertionError('B02 generation prohibited')),
          patch.object(emitter, 'generated_unit', side_effect=AssertionError('B02 target rendering prohibited'))):
        result = readiness.inspect(model, obligations=obligations)
    result['source_sha256'] = emitter.sha(path.read_bytes())
    result['lock_before'] = before
    result['lock_after'] = verify_lock()
    result['obligations'] = obligations
    result['retry_recommended'] = result['status'] == 'READY'
    write('R5_38-B02-static-readiness.json', result)
    print(json.dumps({'status': result['status'], 'semantic_status': result['semantic_status'],
                      'operations': len(result['operations']), 'gaps': result['gaps']}, indent=2))


if __name__ == '__main__':
    command = sys.argv[1]
    if command == 'evidence':
        evidence()
    elif command == 'verify':
        sys.exit(0 if verification() else 1)
    elif command == 'lock':
        print(json.dumps({'identity': lock()['identity']}))
    elif command == 'static':
        frozen_static()
    elif command == 'lock-check':
        print(json.dumps(verify_lock()))
    else:
        raise ValueError('unknown review command')
