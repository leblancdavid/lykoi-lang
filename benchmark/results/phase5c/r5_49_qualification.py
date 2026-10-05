"""Bounded fresh diagnostics; no benchmark-request or production dispatch.

All receipts bind one explicitly incomplete diagnostic state. A dependency
closure gap stops qualification; diagnostics cannot promote it to a capsule.
"""

import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from benchmark.evaluation import dependency_provenance_r5_49 as provenance
from benchmark.evaluation import execution_identity_r5_48 as previous
from benchmark.evaluation import security_r5_47 as security
from benchmark.evaluation.recorder_r5_43 import canonical, digest, loads, ProtocolFailure

OUTPUT = ROOT / 'benchmark/results/phase5c/R5_49-evidence'


def write(name, value):
    security.persist(OUTPUT / (name + '.json'), value)


def read(name):
    return loads((OUTPUT / (name + '.json')).read_bytes())


def capture():
    paths = [p.relative_to(ROOT).as_posix() for prefix in
             ('src', 'air', 'schema', 'generated', 'tests', 'benchmark')
             for p in (ROOT / prefix).rglob('*') if p.is_file() and
             p.suffix in {'.py', '.json'} and '__pycache__' not in p.parts and
             'R5_49-evidence' not in p.parts]
    bound = provenance.members(ROOT, paths)
    history = {p.relative_to(ROOT).as_posix(): digest(p.read_bytes()) for version in ('R5_46', 'R5_48')
               for p in (ROOT / ('benchmark/results/phase5c/' + version + '-evidence')).glob('*.json')}
    body = {'protocol': 'lykoi-r5.49-incomplete-diagnostic-state',
            'files': sorted(bound.values(), key=lambda r: r['path']),
            'runtime': previous.runtime(), 'historical_evidence': history,
            'head': previous.git(ROOT, 'rev-parse', 'HEAD').decode().strip(),
            'index_sha256': digest(previous.git(ROOT, 'ls-files', '--stage', '-z')),
            'qualified_capsule': False, 'exclusive_ownership': False}
    return {'identity': digest(canonical(body)), **body}


def definitions():
    result = {'harness-' + p.stem: ['suite', 'benchmark/harness', p.name, True]
              for p in sorted((ROOT / 'benchmark/harness').glob('test*.py'))}
    result.update({
        'application': ['suite', 'tests', 'test*.py', False],
        'focused': ['suite', 'benchmark/harness', 'test_optional_support_r5_41.py', True],
        'recorder': ['suite', 'benchmark/harness', 'test_canonical_evidence_r5_43.py', True],
        'certificate': ['suite', 'benchmark/evaluation', 'test_preexposure_r5_45.py', False],
        'security': ['suite', 'benchmark/evaluation', 'test_security_r5_47.py', False],
        'publication': ['suite', 'benchmark/evaluation', 'test_environment_snapshot.py', False],
        'prior-identity-fresh': ['suite', 'benchmark/evaluation', 'test_execution_identity_r5_48.py', False],
        'provenance': ['suite', 'benchmark/evaluation', 'test_dependency_provenance_r5_49.py', False],
        'ai-independence': ['suite', 'benchmark/evaluation', 'test_ai_independence_r5_49.py', False],
        'ownership-counterexample': ['suite', 'benchmark/evaluation', 'test_ownership_boundary_r5_49.py', False],
        'core-inventory': ['inventory'], 'deployment-inventory': ['deployment'],
        'coherence': ['coherence'], 'locks': ['locks'],
        'validate': ['command', 'validate'], 'safety': ['command', 'safety'], 'diff': ['diff']})
    return result


def worker(name):
    definition = definitions()[name]
    kind = definition[0]
    if kind == 'suite':
        from benchmark.results.phase5c.r5_38_review import run_suite
        result = run_suite(*definition[1:])
        result.pop('output')
        result['failures'] = [r['test'] for r in result['failures']]
        result['errors'] = [r['test'] for r in result['errors']]
    elif kind == 'locks':
        from benchmark.results.phase5c.r5_48_qualification import boundary
        result = boundary()  # Read-only independently rerun implementation, no prior receipt.
    elif kind in {'inventory', 'deployment'}:
        from benchmark.evaluation import dependency_inventory_r5_49 as inventory
        result = inventory.observe(ROOT) if kind == 'inventory' else inventory.deployment(ROOT)
    elif kind == 'coherence':
        from benchmark.results.phase5c.r5_41_review import matrix
        from benchmark.harness.test_optional_support_r5_41 import setup
        from benchmark.semantic import profile_audit_r5_41 as audit
        app, spec, state, config = setup()
        configuration = {'transport': spec, 'state': state, 'launch': config}
        reference = 'benchmark/harness/test_optional_support_r5_41.py'
        traces = [{'path': p, 'value': v, 'artifact': reference,
                   'sha256': digest((ROOT / reference).read_bytes()), 'clause': 'setup',
                   'interpretation': 'Independent declared shape and public mapping.'}
                  for p, v in audit.leaves(configuration)]
        first, second = matrix(), matrix()
        saved = loads((ROOT / 'benchmark/results/phase5c/R5_41-independent-coherence-matrix.json').read_bytes())
        result = {'profiles': len(first['profiles']), 'rows': len(first['rows']),
                  'canonical_equal': canonical(first) == canonical(saved),
                  'deterministic': canonical(first) == canonical(second),
                  'structure': audit.structure(configuration),
                  'traceability': audit.traceability(configuration, traces, ROOT, {reference}),
                  'contamination': audit.contamination(configuration)}
        result['successful'] = (result['profiles'] == 16 and result['rows'] == 84 and
            result['canonical_equal'] and result['deterministic'] and result['structure']['valid'] and
            result['traceability']['valid'] and not result['contamination'])
    else:
        command = ['git', 'diff', '--check'] if kind == 'diff' else [
            sys.executable, '-B', '-S', '-m', 'air_compiler.cli', definition[1], 'air/task_manager.json']
        process = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=30)
        result = {'successful': process.returncode == 0, 'exit': process.returncode, 'output_withheld': True}
    write(name + '-worker', result)
    if not result['successful']:
        raise SystemExit(1)


def initialize():
    OUTPUT.mkdir(exist_ok=False)
    write('state', capture())
    write('definitions', definitions())
    print({'stages': len(definitions()), 'production_reusable': False})


def halt(category):
    if not (OUTPUT / 'quarantine.json').exists():
        write('quarantine', {'primary_classification': 'R5_49_PROTOCOL_HALT',
                            'reason': category, 'reusable': False,
                            'receipts': {p.name: digest(p.read_bytes()) for p in OUTPUT.glob('*.json')}})
    raise ProtocolFailure('R5.49 halted; details withheld')


def batch():
    if (OUTPUT / 'quarantine.json').exists() or (OUTPUT / 'summary.json').exists():
        raise ProtocolFailure('stopped run cannot resume')
    frozen = read('state')
    if capture() != frozen:
        halt('diagnostic state drift')
    start = time.monotonic()
    for name, definition in definitions().items():
        if (OUTPUT / (name + '.json')).exists():
            continue
        if (OUTPUT / (name + '-attempt.json')).exists():
            halt('incomplete prior attempt; retry forbidden')
        remaining = 85 - (time.monotonic() - start)
        if remaining < 25:
            break
        write(name + '-attempt', {'state': frozen['identity'], 'status': 'INCOMPLETE',
                                  'mechanism': digest(canonical(definition))})
        try:
            process = subprocess.run([sys.executable, '-B', '-S', str(Path(__file__).resolve()),
                                      'worker', name], cwd=ROOT,
                                     env=previous.isolated_environment(os.environ, ROOT),
                                     capture_output=True, timeout=min(65, remaining - 5))
        except subprocess.TimeoutExpired:
            halt('bounded stage incomplete')
        if capture() != frozen:
            halt('diagnostic state drift during stage')
        if process.returncode or not (OUTPUT / (name + '-worker.json')).exists():
            halt('verification stage failure')
        result = read(name + '-worker')
        write(name, {'protocol': 'lykoi-r5.49-diagnostic-receipt', 'state': frozen['identity'],
                     'name': name, 'mechanism': digest(canonical(definition)), 'status': 'PASS',
                     'production_reusable': False, 'result': result})
        print({'stage': name, 'status': 'PASS'}, flush=True)
    print({'completed': sum((OUTPUT / (n + '.json')).exists() for n in definitions()),
           'required': len(definitions())})


def final():
    if (OUTPUT / 'quarantine.json').exists():
        raise ProtocolFailure('halted run')
    frozen = read('state')
    if frozen != capture():
        halt('final diagnostic state drift')
    if any(not (OUTPUT / (n + '.json')).exists() for n in definitions()):
        halt('incomplete staged verification')
    receipts = {n: read(n) for n in definitions()}
    if any(r['state'] != frozen['identity'] or r['status'] != 'PASS' or
           r['mechanism'] != digest(canonical(definitions()[n])) for n, r in receipts.items()):
        halt('mixed or invalid receipts')
    harness = [r['result'] for n, r in receipts.items() if n.startswith('harness-')]
    counts = {'discovered': sum(r['discovered'] for r in harness),
              'passed': sum(r['passed'] for r in harness),
              'skipped': sum(len(r['skipped']) for r in harness)}
    if counts != {'discovered': 429, 'passed': 393, 'skipped': 36}:
        halt('restricted harness denominator changed')
    inventory = receipts['core-inventory']['result']
    if (inventory['closure_complete'] is not False or not inventory['native_images'] or
            any(r['category'] == 'UNKNOWN' for r in inventory['resolved_modules'])):
        halt('closure-gap evidence inconsistent')
    write('summary', {'primary_classification': 'R5_49_DEPENDENCY_CLOSURE_GAP',
          'halt_condition': 'DEPENDENCY_CLOSURE_INCOMPLETE', 'diagnostic_state': frozen['identity'],
          'receipt_count': len(receipts), 'restricted_harness': counts,
          'receipts': {n: digest(canonical(r)) for n, r in receipts.items()},
          'native_descendants_qualified': False, 'production_certificate_issued': False,
          'execution_capsule_qualified': False, 'exclusive_ownership_qualified': False,
          'production_reusable': False, 'core_semantics': 30, 'b02_exposure': 0,
          'phase5c': 'paused'})
    print({'classification': 'R5_49_DEPENDENCY_CLOSURE_GAP', 'receipts': len(receipts)})


if __name__ == '__main__':
    try:
        {'initialize': initialize, 'batch': batch, 'worker': lambda: worker(sys.argv[2]),
         'final': final}[sys.argv[1]]()
    except Exception:
        print('R5.49 operation failed; raw diagnostics withheld', file=sys.stderr)
        raise SystemExit(1)
