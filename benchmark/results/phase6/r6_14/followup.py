"""One separately frozen repair experiment; original evidence is write-once."""
import copy
import json
import subprocess
import sys
import time
from audit import HERE, ROOT, load, now, save, sha, verify, verify_map


def main():
    verify()
    save(HERE/'FOLLOWUP-SPEC-FREEZE.json',dict(utc=now(),files={name:sha(HERE/name)
        for name in ['FOLLOWUP-PROTOCOL.md','followup.py','RUN-RESULTS.json','RUN-FREEZE.json']},
        unchanged_spec_sha256=sha(HERE/'SPEC-FREEZE.json')))
    begin=time.perf_counter()
    original=load(HERE/'xor8.plan.json');successor=copy.deepcopy(original)
    successor['rules']['bits']['steps'][2]['node']=dict(id='consume',op='atom',codec='uint8')
    save(HERE/'xor8-consuming.plan.json',successor)
    save(HERE/'FOLLOWUP-CONSTRUCTION.json',dict(utc=now(),seconds=time.perf_counter()-begin,
        original_sha256=sha(HERE/'xor8.plan.json'),successor_sha256=sha(HERE/'xor8-consuming.plan.json'),
        changed_path='rules.bits.steps[2].node',from_operation='take',to_operation='atom',attempts=1))
    save(HERE/'FOLLOWUP-RUN-FREEZE.json',dict(utc=now(),files={name:sha(HERE/name)
        for name in ['xor8-consuming.plan.json','FOLLOWUP-CONSTRUCTION.json','followup.py']},
        original_runner_sha256=sha(HERE/'run.py')))
    command=[sys.executable,'-B',str(HERE/'followup.py'),'worker']
    started=time.perf_counter();record=dict(start_utc=now(),timeout_seconds=180,command=command)
    try:
        result=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,timeout=180)
        record.update(status='COMPLETED' if result.returncode==0 else 'EXECUTION_ERROR',
            returncode=result.returncode,stdout=result.stdout,stderr=result.stderr)
    except subprocess.TimeoutExpired as exc:
        record.update(status='PROCESS_TIMEOUT',stdout=str(exc.stdout),stderr=str(exc.stderr))
    record.update(completion_utc=now(),seconds=time.perf_counter()-started)
    verify();save(HERE/'FOLLOWUP-RESULTS.json',record)
    print(record['status'],round(record['seconds'],3))


def worker():
    verify();verify_map(HERE,load(HERE/'FOLLOWUP-SPEC-FREEZE.json')['files'])
    verify_map(HERE,load(HERE/'FOLLOWUP-RUN-FREEZE.json')['files'])
    from run import structure, validation, acceptance
    plan=load(HERE/'xor8-consuming.plan.json')
    measured=structure(plan);measured['published_json_bytes']=(HERE/'xor8-consuming.plan.json').stat().st_size
    measured['validation']=validation(plan)
    save(HERE/'xor8-consuming-structure.json',measured)
    result=acceptance(plan,'xor8',time.perf_counter()+170)
    save(HERE/'xor8-consuming-acceptance.json',result)
    print(json.dumps(dict(status=result['status'],file='xor8-consuming-acceptance.json')))


if __name__=='__main__':
    worker() if len(sys.argv)>1 else main()
