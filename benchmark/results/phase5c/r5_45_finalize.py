"""Stopped qualification integrity/report accounting; no evaluation entry."""

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from benchmark.evaluation.preexposure_r5_45 import reload, tree
from benchmark.evaluation.recorder_r5_43 import canonical, digest, loads, persist
from benchmark.results.phase5c.r5_43_qualification import historical_lock, check_qualification_lock, contamination
from benchmark.results.phase5c.r5_42_review import authority

OUTPUT = ROOT / 'benchmark/results/phase5c/R5_45-evidence'
RESULTS = OUTPUT.parent


def summary():
    frozen = reload(OUTPUT / 'state.json')
    stages = {p.stem: reload(p) for p in OUTPUT.glob('*.json')
              if p.stem not in ('state', 'summary', 'final-integrity', 'classification') and
              not p.stem.endswith(('-worker', '-attempt'))}
    suites = [s['result'] for n, s in stages.items() if n.startswith('harness-')]
    costs = {n: s['result']['supervision']['elapsed_seconds'] for n, s in stages.items()}
    result = {'primary_classification': 'R5_45_STATE_IDENTITY_GAP',
              'qualification_stopped': True, 'production_certificate_issued': False,
              'repository_snapshot': frozen['identity'], 'snapshot_files': len(frozen['files']),
              'stages': {n: s['identity'] for n, s in sorted(stages.items())},
              'stage_statuses': {n: s['status'] for n, s in sorted(stages.items())},
              'harness': {'modules': len(suites), 'discovered': sum(s['discovered'] for s in suites),
                          'passed': sum(s['passed'] for s in suites),
                          'skipped': [skip for s in suites for skip in s['skipped']]},
              'costs_seconds': costs, 'total_subprocess_seconds': sum(costs.values()),
              'harness_subprocess_seconds': sum(c for n, c in costs.items() if n.startswith('harness-')),
              'slowest_stage': max(costs, key=costs.get),
              'remaining_identity_obligations': [
                  'Git HEAD/ancestry/configuration are used by lock gates but excluded from repository snapshot',
                  'Python executable is hashed, but libraries, user site, startup customization and native tool dependencies are not',
                  'snapshot environment is parent environment; worker environment overrides PYTHONPATH and bytecode policy',
                  'supervisor uses captured configuration during rehash, not an independent fresh external configuration identity',
                  'output exclusion and whole execution input closure are not yet independently qualified'],
              'b02': {'reservations': 0, 'dispatches': 0, 'completed_observations': 0,
                      'support_evaluations': 0, 'generation': 0, 'execution': 0, 'frozen_acceptance': 0},
              'core_semantics': 30, 'b03_prospectively_touched': False,
              'b17_exposed': False, 'b17_classified': False, 'phase5c': 'paused',
              'next_gate': 'Separately authorized complete state/dependency identity qualification; no transfer experiment yet'}
    persist(OUTPUT / 'summary.json', result)
    print({k: result[k] for k in ('primary_classification', 'snapshot_files', 'total_subprocess_seconds',
                                'harness_subprocess_seconds', 'slowest_stage')})
    print({'harness': {k: v for k, v in result['harness'].items() if k != 'skipped'},
           'skipped': len(result['harness']['skipped']),
           'other_costs': {n: c for n, c in costs.items() if not n.startswith('harness-')}})


def final():
    frozen = reload(OUTPUT / 'state.json')
    current = tree(ROOT, frozen['exclusions'])
    old = frozen['files']
    changed = [n for n in old if old[n] != current.get(n)]
    added = [n for n in current if n not in old]
    historical_names = [n for n in old if '/R5_42-' in n or '/R5_44-' in n or
                        n.endswith(('r5_42_review.py', 'r5_44_review.py', 'r5_44_halt.py'))]
    if any(old[n] != current.get(n) for n in historical_names):
        raise ValueError('historical halt mutation')
    p = subprocess.run(['git', 'diff', '--check'], cwd=ROOT, capture_output=True, text=True)
    result = {'historical_lock': historical_lock('R5_40-implementation-profile-lock.json'),
              'prospective_lock': historical_lock('R5_41-implementation-lock.json'),
              'infrastructure_lock': check_qualification_lock(), 'authority': authority(),
              'contamination': contamination(),
              'historical_halt_files_verified': len(historical_names),
              'historical_halt_files_unchanged': True,
              'post_investigation_changes': changed, 'post_investigation_additions': added,
              'results_are_not_a_current_production_certificate': True,
              'diff_check': {'exit': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr},
              'evidence_hashes': {path.name: digest(path.read_bytes()) for path in OUTPUT.glob('*.json')},
              'new_infrastructure_hashes': {n: current[n] for n in current if 'r5_45' in n.lower() or 'r5.45' in n.lower()}}
    if p.returncode:
        raise ValueError('diff check failed')
    persist(OUTPUT / 'final-integrity.json', result)
    persist(OUTPUT / 'classification.json', {'primary_classification': 'R5_45_STATE_IDENTITY_GAP',
            'production_certificate_issued': False, 'b02_dispatches': 0,
            'summary_sha256': digest((OUTPUT / 'summary.json').read_bytes()),
            'final_integrity_sha256': digest((OUTPUT / 'final-integrity.json').read_bytes())})
    print({'locks': [result[k]['protected_files'] for k in ('historical_lock', 'prospective_lock', 'infrastructure_lock')],
           'halt_files_unchanged': result['historical_halt_files_unchanged'],
           'changed_after_investigation': changed, 'added_after_investigation': added,
           'diff_check': result['diff_check']})


if __name__ == '__main__':
    {'summary': summary, 'final': final}[sys.argv[1]]()
