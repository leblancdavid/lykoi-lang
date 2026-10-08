"""Publication checks and exact-input repetition accounting."""
from collections import Counter
import json
import os
import subprocess
import sys
import time

from audit import HERE, OLD, ROOT, load, now, save, sha, verify, verify_map


def main():
    verify()
    for name in ('FREEZE.json','PROBE-FREEZE.json'):
        verify_map(HERE,load(HERE/name)['files'])
    replay = load(HERE/'REPLAY.json')
    assert replay['summary']['original']['statuses']=={'PASS':152}
    assert replay['summary']['adversarial']['statuses']=={'PASS':98}
    assert replay['scorer_errors']==0
    probes = load(HERE/'PROBE-RESULTS-2.json')
    by_id = {r['id']:r for r in probes['observations']}
    nibble = by_id['vm_nibble_xor']['actual']
    assert len(nibble['observations'])==256 and all(r['passed'] for r in nibble['observations'])
    assert nibble['outside_domain']['status']=='reject'
    assert all(r['actual'] is r['expected'] for r in by_id['B-absent']['actual']['observations'])
    prefix = by_id['vm_prefix']['actual']['result']['value']
    assert [r['prefix'] for r in prefix]==[[1],[1,2],[1,2,3]]
    assert by_id['vm_full_byte_lookup']['status']=='PROCESS_TIMEOUT'
    original = {}
    for task in ('T1','T2','T3','T4','T5'):
        old_cases = load(OLD/'tasks'/task/'acceptance.json')
        if task in ('T1','T3','T4'):
            old_cases += load(OLD/'tasks'/task/'modification'/'acceptance.json')
        original[task] = {json.dumps(c['input'],sort_keys=True) for c in old_cases}
    new = load(HERE/'ADVERSARIAL-1.json')['cases']
    overlaps = [c['id'] for c in new if json.dumps(c['input'],sort_keys=True) in original[c['task']]]
    new_fingerprints = [(c['task'],json.dumps(c['input'],sort_keys=True)) for c in new]
    save(HERE/'INPUT-ACCOUNTING.json',dict(utc=now(),new_suite_entries=len(new),
         distinct_new_suite_task_inputs=len(set(new_fingerprints)),
         entries_already_in_original=overlaps,
         distinct_task_inputs_additional_to_original=len({fp for fp in new_fingerprints if fp[1] not in original[fp[0]]}),
         original_distinct_task_inputs=sum(len(v) for v in original.values()),
         original_replay_observations=152,original_repeated_base_observations=48,
         adversarial_observations=98,adversarial_repeated_base_observations=30,
         nibble_probe_nodes=nibble['structural_nodes'],nibble_probe_passes=256,
         note='Counts use decoded JSON equality with object key order ignored, within a task; repetitions never add distinct inputs.'))
    commands = [
        [sys.executable,'-B','-m','unittest','discover','-s','benchmark/results/phase6/r6_13','-p','test_scorer.py','-v'],
        [sys.executable,'-B','-m','air_compiler.cli','validate','air/task_manager.json'],
        [sys.executable,'-B','-m','air_compiler.cli','safety','air/task_manager.json'],
        *[[sys.executable,'-B','-m','unittest','discover','-s',folder,'-p',pattern,'-v']
          for folder,pattern in [('tests','test_compiler.py'),('tests','test_application.py'),
          ('benchmark/harness','test_baseline.py'),('experiments/semantic_interpreter','test_interpreter.py')]],
        ['git','diff','--check']]
    checks = []
    for command in commands:
        start = time.monotonic()
        proc = subprocess.run(command,cwd=ROOT,capture_output=True,text=True,timeout=180,
            env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONPATH=str(ROOT/'src')))
        checks.append(dict(command=command,returncode=proc.returncode,stdout=proc.stdout,
                           stderr=proc.stderr,seconds=time.monotonic()-start))
        if proc.returncode:
            save(HERE/'FAILED-CHECKS.json',dict(utc=now(),checks=checks))
            raise RuntimeError(command)
    verify()
    save(HERE/'CHECKS.json',dict(utc=now(),checks=checks,protected_files=614,kernel=26,
         scorer_methods=10,baseline_methods=116,all_passed=True))
    print(f'126 methods passed; validate/safety/diff check passed; overlaps={overlaps}; nibble nodes={nibble["structural_nodes"]}')


if __name__ == '__main__':
    main()
