"""R5.43 independent infrastructure qualification; no benchmark exposure entry."""

import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
RESULTS = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from benchmark.evaluation.recorder_r5_43 import (
    Recorder, ProtocolFailure, canonical, digest, equivalent, loads, persist)
from benchmark.harness.test_canonical_evidence_r5_43 import evidence
from benchmark.harness.test_optional_support_r5_41 import setup
from benchmark.results.phase5c.r5_38_review import run_suite
from benchmark.results.phase5c.r5_41_review import matrix
from benchmark.semantic import application_boundary_r5_41 as boundary
from benchmark.semantic import profile_audit_r5_41 as audit
from benchmark.semantic.refined_generator_r5_28 import canonical as historical_canonical


def read(name):
    return loads((RESULTS / name).read_bytes())


def write(name, value):
    persist(RESULTS / name, value)


def historical_lock(name):
    lock = read(name)
    identity = lock.pop('identity')
    mismatches = [name for name, expected in lock['files'].items()
                  if not (ROOT / name).is_file() or digest((ROOT / name).read_bytes()) != expected]
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    ancestor = subprocess.run(['git', 'merge-base', '--is-ancestor', lock['head'], head], cwd=ROOT).returncode == 0
    if mismatches or digest(historical_canonical(lock)) != identity or not ancestor:
        raise ProtocolFailure('inherited authority violation')
    return {'valid': True, 'identity': identity, 'protected_files': len(lock['files']),
            'mismatches': mismatches, 'recorded_head': lock['head'], 'current_head': head,
            'head_policy': 'historical pre-commit ancestry and exact bytes'}


def protected():
    names = subprocess.check_output(['git', 'ls-files', '--cached', '--others', '--exclude-standard'],
                                    cwd=ROOT, text=True).splitlines()
    allowed_docs = {'docs/project-overview.md', 'docs/decisions.md', 'docs/research-log.md'}
    return sorted({name for name in names if name not in allowed_docs and
                   not Path(name).name.startswith('R5_43-') and '/R5_43-' not in name})


def check_qualification_lock():
    lock = read('R5_43-infrastructure-lock.json')
    body = {k: v for k, v in lock.items() if k != 'identity'}
    mismatches = [name for name, expected in lock['files'].items()
                  if not (ROOT / name).is_file() or digest((ROOT / name).read_bytes()) != expected]
    if mismatches or lock['identity'] != digest(canonical(body)):
        raise ProtocolFailure('qualification lock violation')
    return {'valid': True, 'identity': lock['identity'], 'protected_files': len(lock['files']),
            'mismatches': mismatches}


def simulate(name, mode):
    directory = RESULTS / 'R5_43-simulations' / name
    directory.mkdir(parents=True, exist_ok=False)
    r = Recorder(directory)
    r.freeze(evidence(), [ROOT / 'benchmark/evaluation/recorder_r5_43.py',
                          ROOT / 'docs/canonical-evidence-r5.43.md'])
    callbacks = []
    def observe():
        callbacks.append('independent synthetic observation')
        return {'profile': 'mineral-independent', 'classification': 'synthetic-observed',
                'provenance': {'source': 'synthetic callback'}, 'members': (1, 2)}
    try:
        candidate = evidence()
        if mode == 'prepass-mismatch':
            candidate['classification'] = 'unsupported'
        r.verify(candidate)
        r.observe(observe)
        candidate = loads(canonical(evidence()))
        if mode == 'post-observation-mismatch':
            candidate['provenance']['source'] = 'mutated'
        r.verify(candidate)
        if mode == 'second-observation':
            r.observe(observe)
    except ProtocolFailure:
        if mode == 'success':
            raise
    final = r.finish()
    expected = 'STOP' if mode == 'success' else 'HALT'
    if final['status'] != expected or len(callbacks) != (0 if mode == 'prepass-mismatch' else 1):
        raise ProtocolFailure('simulation outcome differs')
    return {'mode': mode, 'callbacks': len(callbacks), 'final': final,
            'records': {p.name: loads(p.read_bytes()) for p in sorted(directory.glob('*.json'))}}


def contamination():
    forbidden = ('B02', 'B03', 'B17', 'due_date', 'due-date', 'task_manager', 'invalid_due_date')
    paths = [ROOT / 'benchmark/evaluation/recorder_r5_43.py',
             ROOT / 'benchmark/harness/test_canonical_evidence_r5_43.py']
    paths += list((ROOT / 'benchmark/semantic').glob('*r5_41.py'))
    findings = [str(p.relative_to(ROOT)) for p in paths if any(word in p.read_text() for word in forbidden)]
    if findings:
        raise ProtocolFailure('implementation contamination')
    return {'valid': True, 'findings': findings, 'checked_files': len(paths)}


def qualify():
    if (RESULTS / 'R5_43-infrastructure-lock.json').exists():
        raise ProtocolFailure('qualification replacement prohibited')
    names = protected()
    lock = {'protocol': 'r5.43-infrastructure-qualification',
            'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            'files': {name: digest((ROOT / name).read_bytes()) for name in names},
            'permitted_updates': ['docs/project-overview.md', 'docs/decisions.md', 'docs/research-log.md'],
            'permitted_outputs': 'R5_43-* qualification evidence only'}
    lock['identity'] = digest(canonical(lock))
    write('R5_43-infrastructure-lock.json', lock)
    result = {'suites': [], 'commands': [], 'b02_static_passes': 0, 'b02_generated': False,
              'b02_executed': False, 'frozen_acceptance_ran': False,
              'core_constructs': boundary.SCHEMA['core_constructs'],
              'b03_prospectively_touched': False, 'b17_exposed': False, 'b17_classified': False,
              'phase5c': 'paused', 'post_observation_semantic_profile_repairs': 0}
    result['historical_lock'] = historical_lock('R5_40-implementation-profile-lock.json')
    result['prospective_lock'] = historical_lock('R5_41-implementation-lock.json')
    result['r5_42_historical_state'] = read('R5_42-halt-verification.json')['primary_classification']
    for directory, pattern, restrictions in (
            ('benchmark/harness', 'test_canonical_evidence_r5_43.py', True),
            ('benchmark/harness', 'test_canonical_evidence_r5_43.py', True),
            ('benchmark/harness', 'test*.py', True),
            ('tests', 'test*.py', False),
            ('benchmark/harness', 'test_optional_support_r5_41.py', True)):
        suite = run_suite(directory, pattern, restrictions)
        for skip in suite['skipped']:
            skip['reason'] = skip['reason'].replace('R5.38', 'R5.43')
        result['suites'].append(suite)
    for command in ([sys.executable, '-m', 'air_compiler.cli', 'validate', 'air/task_manager.json'],
                    [sys.executable, '-m', 'air_compiler.cli', 'safety', 'air/task_manager.json'],
                    ['git', 'diff', '--check']):
        completed = subprocess.run(command, cwd=ROOT, env={**os.environ, 'PYTHONPATH': 'src'},
                                   capture_output=True, text=True)
        result['commands'].append({'command': command, 'exit': completed.returncode,
                                   'stdout': completed.stdout, 'stderr': completed.stderr})
    matrices = [matrix(), matrix()]
    saved = read('R5_41-independent-coherence-matrix.json')
    result['matrix'] = {'profiles': len(saved['profiles']), 'rows': len(saved['rows']),
                        'coherent_profiles': len(matrices[0]['profiles']),
                        'native_python_equal': matrices[0] == saved,
                        'canonical_equal': all(equivalent(value, saved) for value in matrices),
                        'deterministic': canonical(matrices[0]) == canonical(matrices[1]),
                        'canonical_sha256': digest(canonical(saved)),
                        'historical_canonical_sha256': digest(historical_canonical(saved)),
                        'round_trip': all(canonical(value) == canonical(loads(canonical(value))) for value in matrices)}
    app, spec, state, config = setup()
    configuration = {'transport': spec, 'state': state, 'launch': config}
    reference = 'benchmark/harness/test_optional_support_r5_41.py'
    traces = [{'path': path, 'value': value, 'artifact': reference,
               'sha256': digest((ROOT / reference).read_bytes()), 'clause': 'setup',
               'interpretation': 'Independent profile from declared shape and public mapping.'}
              for path, value in audit.leaves(configuration)]
    result['independent_structure'] = audit.structure(configuration)
    result['independent_traceability'] = audit.traceability(configuration, traces, ROOT, {reference})
    result['independent_profile_contamination'] = audit.contamination(configuration)
    result['implementation_contamination'] = contamination()
    result['simulations'] = [simulate(mode, mode) for mode in (
        'success', 'prepass-mismatch', 'post-observation-mismatch', 'second-observation')]
    result['qualification_lock'] = check_qualification_lock()
    result['historical_lock_after'] = historical_lock('R5_40-implementation-profile-lock.json')
    result['prospective_lock_after'] = historical_lock('R5_41-implementation-lock.json')
    result['absence_of_exposure_artifacts'] = {name: not (RESULTS / name).exists() for name in (
        'R5_42-prepass.json', 'R5_42-observation-lock.json', 'R5_42-static-pass-start.json',
        'R5_42-B02-static-support.json')}
    passed = (all(s['successful'] for s in result['suites']) and
              all(c['exit'] == 0 for c in result['commands']) and
              len(result['suites'][2]['skipped']) == 36 and
              result['matrix']['canonical_equal'] and result['matrix']['deterministic'] and
              result['matrix']['round_trip'] and result['core_constructs'] == 30 and
              result['independent_structure']['valid'] and result['independent_traceability']['valid'] and
              not result['independent_profile_contamination'] and
              all(result['absence_of_exposure_artifacts'].values()) and
              result['r5_42_historical_state'] == 'R5_42_PROTOCOL_HALT')
    result['successful'] = passed
    result['primary_classification'] = ('R5_43_EVALUATION_INFRASTRUCTURE_QUALIFIED' if passed else 'R5_43_PROTOCOL_HALT')
    write('R5_43-qualification.json', result)
    print({k: result[k] for k in ('primary_classification', 'matrix', 'qualification_lock')})
    if not passed:
        raise ProtocolFailure('qualification failed; stop')


def final_integrity():
    report = {'qualification_lock': check_qualification_lock(),
              'historical_lock': historical_lock('R5_40-implementation-profile-lock.json'),
              'prospective_lock': historical_lock('R5_41-implementation-lock.json'),
              'implementation_contamination': contamination()}
    command = subprocess.run(['git', 'diff', '--check'], cwd=ROOT, capture_output=True, text=True)
    report['diff_check'] = {'exit': command.returncode, 'stdout': command.stdout, 'stderr': command.stderr}
    if command.returncode:
        raise ProtocolFailure('final diff check failure')
    artifacts = sorted(RESULTS.glob('R5_43-*'))
    files = [p for p in artifacts if p.is_file()]
    files += sorted((RESULTS / 'R5_43-simulations').rglob('*.json'))
    report['artifact_sha256'] = {p.relative_to(ROOT).as_posix(): digest(p.read_bytes()) for p in files}
    write('R5_43-final-integrity.json', report)
    print(report['qualification_lock'])


if __name__ == '__main__':
    {'qualify': qualify, 'final-integrity': final_integrity}[sys.argv[1]]()
