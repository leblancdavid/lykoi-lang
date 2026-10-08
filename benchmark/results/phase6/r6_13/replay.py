"""Replay unchanged snapshots with frozen suites; no candidate authoring."""
from collections import Counter
import os
import sys
import time

from audit import HERE, OLD, ROOT, load, now, save, sha, verify, verify_map
from scorer import execute, VERSION


def main():
    verify()
    frozen = load(HERE / 'FREEZE.json')
    verify_map(HERE, frozen['files'])
    verify_map(ROOT, frozen['candidate_identities'])
    suite = load(HERE / 'ADVERSARIAL-1.json')
    save(HERE / 'REPLAY-START.json', dict(utc=now(), scorer_version=VERSION,
         replay_driver_sha256=sha(HERE / 'replay.py'), freeze_sha256=sha(HERE / 'FREEZE.json'),
         process_seconds=10, session_seconds=900, authoring_trials=0))
    start = time.monotonic()
    deadline = start + 900
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONPATH=str(ROOT / 'src'))
    results = []
    for name, identity in frozen['candidate_identities'].items():
        path = ROOT / name
        _, task, stage, _ = path.parts[-4:]
        original = [('original-base', load(OLD / 'tasks' / task / 'acceptance.json'))]
        if stage == 'modification':
            original += [('original-new', load(OLD / 'tasks' / task / 'modification' / 'acceptance.json'))]
        adversarial = [('adversarial-base', [c for c in suite['cases'] if c['task']==task and c['stage']=='base'])]
        if stage == 'modification':
            adversarial += [('adversarial-new', [c for c in suite['cases'] if c['task']==task and c['stage']=='modification'])]
        observations = []
        # Per-candidate identity checked immediately before/after execution.
        assert sha(path) == identity
        for suite_name, cases in original + adversarial:
            for index, case in enumerate(cases):
                row = execute([sys.executable, '-B', str(path)], case, path.parent, env, deadline)
                row.update(suite=suite_name, case=index, case_id=case.get('id'),
                           repeated_base=stage=='modification' and suite_name.endswith('-base'))
                observations.append(row)
        assert sha(path) == identity
        result = dict(track='A', task=task, stage=stage, candidate=name, sha256=identity,
                      identity_verified_before_after=True, observations=observations,
                      counts=dict(Counter(c['status'] for c in observations)))
        results.append(result)
        print(f'A/{task}/{stage}: {result["counts"]}')
    absent = []
    for track in 'BC':
        for task in ['T1','T2','T3','T4','T5']:
            for stage in (['base','modification'] if task in ['T1','T3','T4'] else ['base']):
                directory = OLD / 'workspaces' / track / task / stage
                original_count = len(load(OLD / 'tasks' / task / 'acceptance.json'))
                adversarial_count = sum(c['task']==task and c['stage']=='base' for c in suite['cases'])
                if stage == 'modification':
                    original_count += len(load(OLD / 'tasks' / task / 'modification' / 'acceptance.json'))
                    adversarial_count += sum(c['task']==task and c['stage']=='modification' for c in suite['cases'])
                absent.append(dict(track=track,task=task,stage=stage,status='NOT_REACHED',
                    reason='NO_HISTORICAL_EXECUTABLE', gap_sha256=sha(directory/'GAP.json'),
                    capability_sha256=sha(directory/'CAPABILITY.md'),
                    original_observations_not_reached=original_count,
                    adversarial_observations_not_reached=adversarial_count))
    verify()
    verify_map(HERE, frozen['files'])
    summary = {}
    for group in ('original','adversarial'):
        rows = [c for r in results for c in r['observations'] if c['suite'].startswith(group)]
        summary[group] = dict(observations=len(rows), statuses=dict(Counter(c['status'] for c in rows)),
                             repeats=sum(c['repeated_base'] for c in rows))
    save(HERE / 'REPLAY.json', dict(start_utc=load(HERE/'REPLAY-START.json')['utc'],completion_utc=now(),
         seconds=time.monotonic()-start, session_budget_seconds=900,
         session_budget_enforcement='Cooperative monotonic deadline; direct-child timeout, no descendant containment',
         scorer_version=VERSION,acceptance_version=suite['version'],
         results=results,not_reached=absent,summary=summary,
         scorer_errors=sum(c['status']=='SCORER_ERROR' for r in results for c in r['observations']),
         authoring_trials=0,repairs=0))
    print(summary)


if __name__ == '__main__':
    main()
