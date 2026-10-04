"""R5.42 observation recorder. One locked static exposure; no implementation edits."""

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
RESULTS = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from benchmark.results.phase5c.r5_38_review import run_suite
from benchmark.results.phase5c import r5_41_review as inherited
from benchmark.semantic import application_boundary_r5_41 as boundary
from benchmark.semantic import readiness_r5_41 as readiness
from benchmark.semantic import profile_audit_r5_41 as audit
from benchmark.semantic import current_pipeline as pipeline
from benchmark.semantic import refined_generator_r5_28 as emitter

SOURCE = 'R5_40-b02-semantic-application.json'
DOCS = {'docs/project-overview.md', 'docs/decisions.md', 'docs/research-log.md'}


def read(name):
    return json.loads((RESULTS / name).read_bytes())


def write(name, value):
    (RESULTS / name).write_bytes(emitter.canonical(value) + b'\n')


def head():
    return subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()


def check_lock(name, current_head=False):
    record = read(name)
    identity = record.pop('identity')
    mismatches = [name for name, digest in record['files'].items()
                  if not (ROOT / name).exists() or emitter.sha((ROOT / name).read_bytes()) != digest]
    if emitter.sha(emitter.canonical(record)) != identity or mismatches:
        raise ValueError({'lock': name, 'mismatches': mismatches, 'identity': identity})
    if current_head and record['head'] != head():
        raise ValueError('R5.42 HEAD changed')
    # Inherited locks were sealed before their evidence commit. Verify ancestry
    # and every pinned byte, retaining their original HEAD without replacement.
    if subprocess.run(['git', 'merge-base', '--is-ancestor', record['head'], head()], cwd=ROOT).returncode:
        raise ValueError('locked HEAD is not an ancestor')
    return {'valid': True, 'identity': identity, 'protected_files': len(record['files']),
            'mismatches': mismatches, 'recorded_head': record['head'], 'current_head': head(),
            'head_policy': 'exact' if current_head else 'historical pre-commit ancestry plus exact bytes'}


def authority():
    expected = {
        'benchmark/requirements/B01.md': 'b7b2d714db5cee566e9e55982dd4c4d95d3d57f0c341e04ba1e15c24e9a8e94d',
        'benchmark/requirements/B02.md': '8a76e276240fa840c473be60a8e7ed0e10bd0c165426b1bfc84741e69872032b',
        'benchmark/harness/profiles/B02.json': '46ff02e3ff6ea48a7990c2f522fb9fa7bbefcab3c88550be007e0c2c1b75972f',
        'benchmark/results/phase5c/R5_40-frozen-regression-authority.txt': '16d55bac4dc1efa3debc6764ddde9dc27c16b7538de476a0fae9cf7db7519596'}
    for name, digest in expected.items():
        if emitter.sha((ROOT / name).read_bytes()) != digest:
            raise ValueError('frozen authority mismatch: ' + name)
    original = subprocess.check_output(['git', 'show', '5064950:benchmark/harness/regression.py'], cwd=ROOT)
    if emitter.sha(original) != expected['benchmark/results/phase5c/R5_40-frozen-regression-authority.txt']:
        raise ValueError('original frozen oracle hash mismatch')
    return {'verified': True, 'members': expected, 'oracle_executed': False,
            'baseline_sha256': emitter.sha((ROOT / 'benchmark/baseline.md').read_bytes())}


def contamination():
    forbidden = ('B02', 'B03', 'B17', 'due_date', 'due-date', 'task_manager', 'invalid_due_date')
    findings = [str(path.relative_to(ROOT)) for path in (ROOT / 'benchmark/semantic').glob('*r5_41.py')
                if any(token in path.read_text() for token in forbidden)]
    if findings:
        raise ValueError({'implementation_contamination': findings})
    return findings


def prepass():
    if (RESULTS / 'R5_42-prepass.json').exists() or (RESULTS / 'R5_42-static-pass-start.json').exists():
        raise ValueError('pre-pass replacement prohibited')
    historical = check_lock('R5_40-implementation-profile-lock.json')
    prospective = check_lock('R5_41-implementation-lock.json')
    previous = read('R5_41-verification.json')
    if not all(s['successful'] for s in previous['suites']) or not all(c['exit'] == 0 for c in previous['commands']):
        raise ValueError('inherited verification incomplete')
    if boundary.SCHEMA['core_constructs'] != 30:
        raise ValueError('core count changed')
    suite = run_suite('benchmark/harness', 'test_optional_support_r5_41.py')
    if not suite['successful'] or suite['passed'] != 14:
        raise ValueError('focused starting-state reproduction failed')
    matrix = inherited.matrix()
    if len(matrix['profiles']) != 16 or len(matrix['rows']) != 84:
        raise ValueError('independent matrix reproduction failed')
    saved = read('R5_41-independent-coherence-matrix.json')
    if matrix != saved:
        raise ValueError('independent matrix differs from sealed evidence')
    # No B02 semantic/profile evaluation in this phase: only sealed authority bytes.
    result = {'classification': 'R5_41_SUPPORT_COHERENCE_READY', 'core_constructs': 30,
              'semantic_31_introduced': False, 'historical_lock': historical,
              'prospective_baseline': prospective, 'frozen_authority': authority(),
              'implementation_contamination': contamination(), 'focused_suite': suite,
              'matrix_profiles': 16, 'matrix_rows': 84, 'matrix_matches_sealed_evidence': True,
              'supported_profiles': sum(p['admitted'] for p in matrix['profiles']),
              'coherent_profiles': 16, 'b02_static_passes': 0,
              'b03_prospectively_touched': False, 'b17_exposed': False, 'b17_classified': False,
              'scope_evidence': 'clean initial git status and exact inherited authority bytes'}
    write('R5_42-prepass.json', result)
    names = subprocess.check_output(['git', 'ls-files', '--cached', '--others', '--exclude-standard'], cwd=ROOT, text=True).splitlines()
    names = sorted({n for n in names if n not in DOCS and not Path(n).name.startswith('R5_42-')})
    lock = {'version': 'R5.42', 'time': datetime.now(timezone.utc).isoformat(), 'head': head(),
            'files': {name: emitter.sha((ROOT / name).read_bytes()) for name in names},
            'inherited_baseline': prospective, 'permitted_document_updates': sorted(DOCS),
            'permitted_artifacts': 'R5_42-* observational records only; recorder itself locked',
            'authorization': 'exactly one whole-contract static pass; no generation/execution/acceptance/repair'}
    lock['identity'] = emitter.sha(emitter.canonical(lock))
    write('R5_42-observation-lock.json', lock)
    print(json.dumps({'prepass': 'PASS', 'profiles': 16, 'rows': 84,
                      'lock': check_lock('R5_42-observation-lock.json', True)}, indent=2))


def static():
    if (RESULTS / 'R5_42-static-pass-start.json').exists():
        raise ValueError('single static pass already consumed; retry prohibited')
    if read('R5_42-prepass.json')['classification'] != 'R5_41_SUPPORT_COHERENCE_READY':
        raise ValueError('starting state unverified')
    before = check_lock('R5_42-observation-lock.json', True)
    # Exclusive reservation precedes loading the B02 application or profiles.
    with (RESULTS / 'R5_42-static-pass-start.json').open('xb') as stream:
        stream.write(emitter.canonical({'time': datetime.now(timezone.utc).isoformat(), 'lock': before,
            'pass_number': 1, 'whole_contract': True, 'retry_permitted': False,
            'authorization': 'readiness, supplemental audit and aggregate admission through the unchanged R5.41 shared compatible-path model'}) + b'\n')
    try:
        application = read(SOURCE)
        configuration = read('R5_40-B02-profiles.json')
        obligations = read('R5_40-B02-obligations.json')
        with (patch.object(pipeline, 'generate', side_effect=AssertionError('B02 generation prohibited')),
              patch.object(emitter, 'generated_unit', side_effect=AssertionError('B02 rendering prohibited')),
              patch.object(boundary, 'generate', side_effect=AssertionError('B02 bundle generation prohibited'))):
            prediction = readiness.inspect(application, configuration['transport'], configuration['state'],
                                           configuration['launch'], obligations['readiness'])
            supplemental = audit.inspect(application, configuration)
            manifest = {'application': emitter.sha(emitter.canonical(application)), 'generation': 'static-readiness-r541',
                        'units': {name: row['digest'] for name, row in prediction['operations'].items() if row['status'] == 'SUPPORTED'}}
            try:
                aggregate = boundary.aggregate(application, configuration['transport'], configuration['state'],
                                               configuration['launch'], manifest)
                admission = {'status': 'ADMITTED', 'aggregate': aggregate}
            except (ValueError, KeyError, TypeError) as exc:
                admission = {'status': 'REJECTED', 'reason': str(exc)}
            from benchmark.results.phase5c.r5_40_review import AUTHORITIES
            traces = audit.traceability(configuration, read('R5_40-profile-source-traceability.json'), ROOT, AUTHORITIES)
        states = [prediction['status'] == 'READY', supplemental['status'] == 'SUPPORTED', admission['status'] == 'ADMITTED']
        if not all(states) and any(states):
            decision = 'R5_42_SUPPORT_COHERENCE_GAP'
        elif all(states):
            decision = 'R5_42_STATIC_SUPPORT_TRANSFER_READY'
        else:
            decision = 'R5_42_GENERIC_CAPABILITY_GAP'
        if not supplemental['structure']['valid'] or supplemental['contamination'] or not traces['valid']:
            decision = 'R5_42_PROTOCOL_HALT'
        result = {'primary_classification': decision, 'static_passes': 1, 'core_constructs': 30,
                  'readiness': prediction, 'supplemental_audit': supplemental, 'admission': admission,
                  'traceability': traces, 'whole_contract_supported': decision == 'R5_42_STATIC_SUPPORT_TRANSFER_READY',
                  'checked_plans': sum(row['status'] == 'SUPPORTED' for row in prediction['operations'].values()),
                  'public_state_pairs': obligations['public_state_pairs'],
                  'unsupported_requirements': prediction['gaps'] + supplemental['findings'],
                  'shared_compatible_path': 'application_boundary_r5_41.support_report / aggregate / validate',
                  'lock_before': before, 'lock_after': check_lock('R5_42-observation-lock.json', True),
                  'historical_lock_after': check_lock('R5_40-implementation-profile-lock.json'),
                  'prospective_lock_after': check_lock('R5_41-implementation-lock.json'),
                  'b02_generated': False, 'b02_executed': False, 'frozen_acceptance_ran': False,
                  'post_pass_repairs': 0, 'static_prediction_only': True}
    except Exception as exc:
        result = {'primary_classification': 'R5_42_PROTOCOL_HALT', 'static_passes': 1,
                  'reason': repr(exc), 'retry_permitted': False}
    write('R5_42-B02-static-support.json', result)
    print(json.dumps({k: v for k, v in result.items() if k not in ('readiness', 'supplemental_audit', 'admission', 'public_state_pairs')}, indent=2))


def verify():
    if (RESULTS / 'R5_42-postpass-verification.json').exists():
        raise ValueError('post-pass verification replacement prohibited')
    result = {'suites': [], 'commands': []}
    for directory, pattern, restrictions in [('benchmark/harness', 'test*.py', True), ('tests', 'test*.py', False)]:
        suite = run_suite(directory, pattern, restrictions)
        for skip in suite['skipped']:
            skip['reason'] = skip['reason'].replace('R5.38', 'R5.42')
        result['suites'].append(suite)
    for command in ([sys.executable, '-m', 'air_compiler.cli', 'validate', 'air/task_manager.json'],
                    [sys.executable, '-m', 'air_compiler.cli', 'safety', 'air/task_manager.json'], ['git', 'diff', '--check']):
        completed = subprocess.run(command, cwd=ROOT, env={**os.environ, 'PYTHONPATH': 'src'}, capture_output=True, text=True)
        result['commands'].append({'command': command, 'exit': completed.returncode,
                                   'stdout': completed.stdout, 'stderr': completed.stderr})
    result['historical_lock'] = check_lock('R5_40-implementation-profile-lock.json')
    result['prospective_lock'] = check_lock('R5_41-implementation-lock.json')
    result['observation_lock'] = check_lock('R5_42-observation-lock.json', True)
    result['frozen_authority'] = authority()
    result['implementation_contamination'] = contamination()
    result['matrix_matches_sealed_evidence'] = inherited.matrix() == read('R5_41-independent-coherence-matrix.json')
    result['successful'] = (all(s['successful'] for s in result['suites']) and
                            all(c['exit'] == 0 for c in result['commands']) and result['matrix_matches_sealed_evidence'])
    write('R5_42-postpass-verification.json', result)
    print(json.dumps({'successful': result['successful'], 'command_exits': [c['exit'] for c in result['commands']]}))


if __name__ == '__main__':
    {'prepass': prepass, 'static': static, 'verify': verify}[sys.argv[1]]()
