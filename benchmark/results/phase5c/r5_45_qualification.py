"""Bounded infrastructure investigation; no benchmark exposure entry."""

from pathlib import Path
import os
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from benchmark.evaluation import preexposure_r5_45 as gate
from benchmark.evaluation.environment_snapshot import public_environment
from benchmark.evaluation.recorder_r5_43 import canonical, digest, loads, persist

OUTPUT = ROOT / 'benchmark/results/phase5c/R5_45-evidence'


def definitions():
    items = {'harness-' + p.stem: ['suite', 'benchmark/harness', p.name, 'restricted']
             for p in sorted((ROOT / 'benchmark/harness').glob('test*.py'))}
    items.update({
        'application': ['suite', 'tests', 'test*.py', 'ordinary'],
        'focused': ['suite', 'benchmark/harness', 'test_optional_support_r5_41.py', 'restricted'],
        'recorder': ['suite', 'benchmark/harness', 'test_canonical_evidence_r5_43.py', 'restricted'],
        'certificate': ['suite', 'benchmark/evaluation', 'test_preexposure_r5_45.py', 'ordinary'],
        'locks': ['locks'], 'matrix': ['matrix'], 'profiles': ['profiles'],
        'validate': ['command', '-m', 'air_compiler.cli', 'validate', 'air/task_manager.json'],
        'safety': ['command', '-m', 'air_compiler.cli', 'safety', 'air/task_manager.json'],
        'diff': ['diff'], 'characterization': ['characterization']})
    return items


def worker(name):
    definition = definitions()[name]
    if definition[0] == 'suite':
        from benchmark.results.phase5c.r5_38_review import run_suite
        result = run_suite(definition[1], definition[2], definition[3] == 'restricted')
    elif definition[0] == 'locks':
        from benchmark.results.phase5c.r5_43_qualification import historical_lock, check_qualification_lock, contamination
        from benchmark.results.phase5c.r5_42_review import authority
        from benchmark.semantic.application_boundary_r5_41 import SCHEMA
        result = {'historical': historical_lock('R5_40-implementation-profile-lock.json'),
                  'prospective': historical_lock('R5_41-implementation-lock.json'),
                  'infrastructure': check_qualification_lock(), 'authority': authority(),
                  'contamination': contamination(), 'semantic_count': SCHEMA['core_constructs']}
        source = ROOT / 'benchmark/evaluation/preexposure_r5_45.py'
        tests = ROOT / 'benchmark/evaluation/test_preexposure_r5_45.py'
        forbidden = ('B02', 'B03', 'B17', 'due_date', 'due-date', 'task_manager')
        result['prospective_contamination'] = [p.name for p in (source, tests)
                                               if any(word in p.read_text() for word in forbidden)]
        result['successful'] = result['semantic_count'] == 30 and not result['prospective_contamination']
    elif definition[0] == 'matrix':
        from benchmark.results.phase5c.r5_41_review import matrix
        saved = loads((ROOT / 'benchmark/results/phase5c/R5_41-independent-coherence-matrix.json').read_bytes())
        first, second = matrix(), matrix()
        result = {'profiles': len(first['profiles']), 'rows': len(first['rows']),
                  'canonical_identity': digest(canonical(first)),
                  'deterministic': canonical(first) == canonical(second),
                  'saved_equal': canonical(first) == canonical(saved)}
        result['successful'] = (result['deterministic'] and result['saved_equal'] and
                                result['profiles'] == 16 and result['rows'] == 84)
    elif definition[0] == 'profiles':
        from benchmark.harness.test_optional_support_r5_41 import setup
        from benchmark.semantic import profile_audit_r5_41 as audit
        app, spec, state, config = setup()
        configuration = {'transport': spec, 'state': state, 'launch': config}
        reference = 'benchmark/harness/test_optional_support_r5_41.py'
        traces = [{'path': path, 'value': value, 'artifact': reference,
                   'sha256': digest((ROOT / reference).read_bytes()), 'clause': 'setup',
                   'interpretation': 'Independent declared shape and public mapping.'}
                  for path, value in audit.leaves(configuration)]
        result = {'structure': audit.structure(configuration),
                  'traceability': audit.traceability(configuration, traces, ROOT, {reference}),
                  'contamination': audit.contamination(configuration)}
        result['successful'] = result['structure']['valid'] and result['traceability']['valid'] and not result['contamination']
    elif definition[0] == 'characterization':
        inherited = loads((ROOT / 'benchmark/results/phase5c/R5_43-qualification.json').read_bytes())
        halt = loads((ROOT / 'benchmark/results/phase5c/R5_44-halt-verification.json').read_bytes())
        result = {'successful': halt['primary_classification'] == 'R5_44_PROTOCOL_HALT',
                  'halt_sha256': digest(canonical(halt)), 'timeout_ms': halt['tool_timeout_ms'],
                  'historical_suite_seconds': [{k: s[k] for k in ('directory', 'pattern', 'seconds')}
                                               for s in inherited['suites']],
                  'historical_exact_interruption_stage': 'unknown; buffered output and no stage receipts',
                  'historical_completed_regressions': 'not established',
                  'duplicate_work': 'recorder focused suite then again in full harness; optional focused after full harness',
                  'no_retry': True, 'exposure': 0}
    else:
        command = ['git', 'diff', '--check'] if definition[0] == 'diff' else [sys.executable, *definition[1:]]
        p = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
        result = {'successful': p.returncode == 0, 'exit': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr}
    persist(OUTPUT / (name + '-worker.json'), result)
    if not result['successful']:
        raise SystemExit(1)


def initialize():
    OUTPUT.mkdir(exist_ok=False)
    configuration = {'python': sys.version, 'executable': sys.executable,
                     'executable_sha256': digest(Path(sys.executable).read_bytes()),
                     'environment': public_environment(os.environ),
                     'definitions': definitions(),
                     'identity_qualification': 'repository bytes only; external dependency closure pending'}
    frozen = gate.state(ROOT, configuration, ['benchmark/results/phase5c/R5_45-evidence'])
    persist(OUTPUT / 'state.json', frozen)
    print({'frozen_repository_inputs': len(frozen['files']), 'state': frozen['identity']})


def batch():
    frozen = gate.reload(OUTPUT / 'state.json')
    current = gate.state(ROOT, frozen['configuration'], frozen['exclusions'])
    if canonical(current) != canonical(frozen):
        raise gate.ProtocolFailure('repository changed since investigation freeze')
    started = time.monotonic()
    environment = {**os.environ, 'PYTHONPATH': str(ROOT / 'src'), 'PYTHONDONTWRITEBYTECODE': '1'}
    for name, definition in definitions().items():
        if (OUTPUT / (name + '.json')).exists():
            continue
        remaining = 85 - (time.monotonic() - started)
        if remaining < 15:
            break
        mechanism = digest(canonical(definition))
        attempt = gate.stage(frozen['identity'], name, 'INCOMPLETE',
                             {'successful': False, 'reason': 'started; no completion receipt'}, mechanism)
        persist(OUTPUT / (name + '-attempt.json'), attempt)
        command = [sys.executable, '-B', str(Path(__file__).resolve()), 'worker', name]
        status, telemetry = gate.bounded(command, ROOT, environment, min(70, remaining))
        result = loads((OUTPUT / (name + '-worker.json')).read_bytes()) if status != 'INCOMPLETE' and (OUTPUT / (name + '-worker.json')).exists() else {'successful': False}
        current = gate.state(ROOT, frozen['configuration'], frozen['exclusions'])
        if canonical(current) != canonical(frozen):
            status = 'FAIL'
            result = {'successful': False, 'reason': 'repository changed during stage'}
        evidence = gate.stage(frozen['identity'], name, status, {**result, 'supervision': telemetry}, mechanism)
        persist(OUTPUT / (name + '.json'), evidence)
        print({'stage': name, 'status': status, 'seconds': telemetry['elapsed_seconds']}, flush=True)
        if status != 'PASS':
            raise SystemExit(1)
    print({'completed': sum((OUTPUT / (name + '.json')).exists() for name in definitions()), 'required': len(definitions())})


if __name__ == '__main__':
    {'initialize': initialize, 'batch': batch, 'worker': lambda: worker(sys.argv[2])}[sys.argv[1]]()
