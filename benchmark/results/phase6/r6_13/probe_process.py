"""Budgeted successor execution method for the preserved capability probes."""
import json
import os
import subprocess
import sys
import time

from audit import HERE, ROOT, load, now, save, sha, verify, verify_map
from scorer import raw_text


def worker(name):
    import probes as p
    specs = load(HERE/'PROBE-INPUTS.json')
    if name == 'B-record-collection':
        try:
            value = p.predicates.scalar_type(specs['production_record_collection'])
            return dict(status='accepted',actual=value)
        except Exception as exc:
            return dict(status='rejected',exception_type=type(exc).__name__,detail=str(exc))
    if name == 'B-absent':
        typ = dict(type='string',domain=[])
        tree = specs['production_absent']
        p.predicates.validate(tree,parameters={'old':typ,'original_slice':typ})
        return dict(status='validated',observations=[dict(old=a,original_slice=b,expected=e,
            actual=p.predicate_eval(tree,inputs={'old':a,'original_slice':b}))
            for a,b,e in [('aa','bb',True),('aa','aa',False),('','',False)]])
    if name.startswith('B-direct-'):
        op = name.removeprefix('B-direct-')
        graph = dict(nodes=[dict(binding='result',operator=op,type=p.computation.INTEGER,
            operands=[],depends_on=[],error='BAD')],policy=p.computation.POLICY)
        try:
            value = p.computation.validate(graph,{'row':{}},'row',{})
            return dict(status='accepted',construction=graph,actual=value)
        except Exception as exc:
            return dict(status='rejected',construction=graph,exception_type=type(exc).__name__,detail=str(exc))
    plan = specs[name]
    try:
        count = p.validate(plan)
    except Exception as exc:
        return dict(status='plan_reject',exception_type=type(exc).__name__,detail=str(exc))
    if name == 'vm_nibble_xor':
        observations = []
        for a in range(16):
            for b in range(16):
                result = p.execute(plan,bytes([a,b]))
                observations.append(dict(input_hex=bytes([a,b]).hex(),expected=a ^ b,
                    passed=result.get('value')==a ^ b and result.get('output')==bytes([a ^ b]),result=p.serial(result)))
        return dict(status='executed',structural_nodes=count,observations=observations,
                    outside_domain=p.serial(p.execute(plan,b'\x10\x00')))
    return dict(status='executed',structural_nodes=count,result=p.serial(p.execute(plan,b'\x01\x02\x03')))


def main():
    verify()
    verify_map(HERE,load(HERE/'PROBE-FREEZE.json')['files'])
    save(HERE/'PROBE-PROCESS-START.json',dict(utc=now(),method='r6.13-probe-process-2',
        driver_sha256=sha(HERE/'probe_process.py'),process_seconds=10,session_seconds=900,
        prior_attempt='PROBE-INTERRUPTION.md'))
    start = time.monotonic()
    deadline = start + 900
    rows = []
    names = ['B-record-collection','B-absent','B-direct-xor','B-direct-slice','B-direct-permutations',
             'vm_direct_xor','vm_direct_slice','vm_prefix','vm_nibble_xor','vm_full_byte_lookup']
    for name in names:
        before = time.monotonic()
        row = dict(id=name,start_utc=now(),stdout='',stderr='',returncode=None)
        remaining = deadline - before
        if remaining <= 0:
            row['status'] = 'NOT_REACHED_SESSION_BUDGET'
        else:
            command = [sys.executable,'-B',str(HERE/'probe_process.py'),'worker',name]
            row.update(command=command,effective_timeout_seconds=min(10,remaining))
            try:
                proc = subprocess.run(command,capture_output=True,cwd=HERE,
                    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'),timeout=min(10,remaining))
                row.update(stdout=raw_text(proc.stdout),stderr=raw_text(proc.stderr),returncode=proc.returncode,
                           status='COMPLETED' if proc.returncode==0 else 'EXECUTION_ERROR')
                if proc.returncode==0:
                    row['actual'] = json.loads(proc.stdout)
                if time.monotonic()>deadline:
                    row['status']='SESSION_TIMEOUT'
            except subprocess.TimeoutExpired as exc:
                row.update(status='PROCESS_TIMEOUT' if remaining>10 else 'SESSION_TIMEOUT',
                           stdout=raw_text(exc.stdout),stderr=raw_text(exc.stderr))
        row.update(completion_utc=now(),seconds=time.monotonic()-before)
        rows.append(row)
        print(name,row['status'],row.get('actual',{}).get('status',''))
    verify()
    save(HERE/'PROBE-RESULTS-2.json',dict(start_utc=load(HERE/'PROBE-PROCESS-START.json')['utc'],
        completion_utc=now(),seconds=time.monotonic()-start,method='r6.13-probe-process-2',
        inputs_sha256=sha(HERE/'PROBE-INPUTS.json'),observations=rows,
        scope='Partial new constructions only; no full-task acceptance or authoring credit'))


if __name__ == '__main__':
    if sys.argv[1:] and sys.argv[1]=='worker':
        print(json.dumps(worker(sys.argv[2])))
    else:
        main()
