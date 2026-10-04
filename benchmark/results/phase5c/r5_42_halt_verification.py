"""Integrity checks for the stopped R5.42 run; no B02 support evaluation."""

import os
import subprocess
import sys
from datetime import datetime, timezone

from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from benchmark.results.phase5c import r5_42_review as recorder
from benchmark.results.phase5c.r5_38_review import run_suite
from benchmark.results.phase5c.r5_40_review import AUTHORITIES


def main():
    if (recorder.RESULTS / 'R5_42-halt-verification.json').exists():
        raise ValueError('halt verification replacement prohibited')
    result = {'time': datetime.now(timezone.utc).isoformat(),
              'primary_classification': 'R5_42_PROTOCOL_HALT',
              'halt_stage': 'pre-pass matrix evidence comparison',
              'prepass_command': 'python benchmark/results/phase5c/r5_42_review.py prepass',
              'prepass_error': "ValueError('independent matrix differs from sealed evidence')",
              'prepass_focused_tests': {'discovered': 14, 'passed': 14},
              'b02_static_passes': 0, 'checked_plans_formed_for_b02': 0,
              'b02_generated': False, 'b02_executed': False, 'frozen_acceptance_ran': False,
              'post_observation_implementation_profile_repairs': 0,
              'suites': [], 'commands': []}
    for directory, pattern, restrictions in [('benchmark/harness', 'test*.py', True), ('tests', 'test*.py', False)]:
        suite = run_suite(directory, pattern, restrictions)
        for skip in suite['skipped']:
            skip['reason'] = skip['reason'].replace('R5.38', 'R5.42')
        result['suites'].append(suite)
    for command in ([sys.executable, '-m', 'air_compiler.cli', 'validate', 'air/task_manager.json'],
                    [sys.executable, '-m', 'air_compiler.cli', 'safety', 'air/task_manager.json'], ['git', 'diff', '--check']):
        completed = subprocess.run(command, cwd=recorder.ROOT, env={**os.environ, 'PYTHONPATH': 'src'}, capture_output=True, text=True)
        result['commands'].append({'command': command, 'exit': completed.returncode,
                                   'stdout': completed.stdout, 'stderr': completed.stderr})
    result['historical_lock'] = recorder.check_lock('R5_40-implementation-profile-lock.json')
    result['prospective_baseline'] = recorder.check_lock('R5_41-implementation-lock.json')
    result['frozen_authority'] = recorder.authority()
    result['implementation_contamination'] = recorder.contamination()
    # Diagnose the failed recorder comparison without retrying prepass or exposing
    # B02. This is only the independent synthetic matrix, not the frozen contract.
    current = recorder.inherited.matrix()
    saved = recorder.read('R5_41-independent-coherence-matrix.json')
    result['independent_matrix_integrity'] = {
        'profiles': len(current['profiles']), 'rows': len(current['rows']),
        'supported_profiles': sum(p['admitted'] for p in current['profiles']),
        'native_python_equal': current == saved,
        'canonical_json_equal': recorder.emitter.canonical(current) == recorder.emitter.canonical(saved),
        'current_canonical_sha256': recorder.emitter.sha(recorder.emitter.canonical(current)),
        'sealed_canonical_sha256': recorder.emitter.sha(recorder.emitter.canonical(saved)),
        'explanation': 'In-memory analyzer facts contain tuples; JSON round-trip represents them as lists. Native Python equality is not serialized-evidence equality. No correction or prepass retry performed.'}
    config = recorder.read('R5_40-B02-profiles.json')
    result['configuration_integrity_only'] = {
        'structure': recorder.audit.structure(config),
        'contamination': recorder.audit.contamination(config),
        'traceability': recorder.audit.traceability(config, recorder.read('R5_40-profile-source-traceability.json'), recorder.ROOT, AUTHORITIES),
        'support_evaluated': False}
    result['inherited_verification'] = recorder.inherited.summary()
    result['absence_of_exposure_artifacts'] = {name: not (recorder.RESULTS / name).exists() for name in (
        'R5_42-prepass.json', 'R5_42-observation-lock.json', 'R5_42-static-pass-start.json', 'R5_42-B02-static-support.json')}
    result['integrity_regressions_passed'] = (
        all(s['successful'] for s in result['suites']) and all(c['exit'] == 0 for c in result['commands'])
        and result['independent_matrix_integrity']['canonical_json_equal']
        and all(result['absence_of_exposure_artifacts'].values()))
    recorder.write('R5_42-halt-verification.json', result)
    print({k: result[k] for k in ('primary_classification', 'b02_static_passes', 'integrity_regressions_passed', 'independent_matrix_integrity')})


if __name__ == '__main__':
    main()
