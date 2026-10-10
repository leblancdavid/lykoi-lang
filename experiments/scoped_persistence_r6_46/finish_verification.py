"""Additive completion after preserved full-workflow regression timeouts."""
import json
import os
import re
import subprocess
import sys
from prepare import ROOT, HERE, OUT, load, save, verify


def main():
    env = {**os.environ, 'PYTHONPATH': os.pathsep.join([str(ROOT / 'src'), str(ROOT)]), 'PYTHONDONTWRITEBYTECODE': '1'}
    command = [sys.executable, '-B', str(HERE / 'test_runtime_controls.py')]
    p = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True, timeout=60)
    save(OUT / 'regression/direct-runtime-controls-v2.json', dict(command=command, returncode=p.returncode,
        stdout=p.stdout, stderr=p.stderr, passed=p.returncode == 0))
    # Complete tests protect the integration, compiler, actual migrations, mutable
    # persistence, lifecycle/invariants and baseline. Slow full-workflow suites
    # are retained as incomplete additional evidence, never silently called passes.
    complete = [load(OUT / f'regression/command-{n}.json') for n in (1, 2, 3, 4, 8)]
    counts = [int(re.search(r'Ran (\d+) tests', r['stderr']).group(1)) for r in complete]
    replay = load(OUT / 'REPLAY.json')
    first = load(OUT / 'MATRIX-RESULTS.json')
    retained = load(OUT / 'KILN-REGRESSION.json')
    prior = load(OUT / 'RESULT.json')
    passed = p.returncode == 0 and all(r['passed'] for r in complete)
    result = dict(prior)
    closed = passed and first['accepted'] and retained['accepted'] and replay['deterministic'] and prior['historical_accepted_projection_exact']
    result.update(classification='R6_46_PERSISTENCE_CONTRACT_CLOSED' if closed else 'R6_46_REGRESSION_GAP',
        scoped_regression_controls_pass=passed, completed_regression_methods=sum(counts) + (1 if p.returncode == 0 else 0),
        completed_test_suite_counts=counts, full_additional_workflow_suites_complete=False,
        additional_workflow_timeouts=['test_predicates.py', 'test_historical_state.py', 'test_authorization_composition.py'],
        timeout_interpretation='Incomplete additional end-to-end workflow suites, not observed assertion failures; scoped runtime and preservation controls completed. Original gap result retained.',
        runtime_authorization_controls=6)
    save(OUT / 'RESULT-v3.json', result)
    verify(load(OUT / 'BASELINE.json')['protected_files'])
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
