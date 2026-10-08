"""Explicit local evidence writer; not accessible from semantic plans."""
import hashlib
import io
import json
from pathlib import Path
import platform
import unittest
from baseline import inventory, verify_publications
from interpreter import execute, validate

HERE = Path(__file__).resolve().parent


def serial(x):
    if isinstance(x, bytes): return {'bytes_hex':x.hex()}
    if isinstance(x, dict): return {k:serial(v) for k,v in x.items()}
    if isinstance(x, (list,tuple)): return [serial(v) for v in x]
    return x


if __name__=='__main__':
    target=HERE/'evidence'
    if target.exists(): raise SystemExit('Evidence already exists; use a new publication directory')
    target.mkdir()
    transcript=io.StringIO()
    suite=unittest.defaultTestLoader.discover(str(HERE),pattern='test_interpreter.py')
    result=unittest.TextTestRunner(stream=transcript,verbosity=2).run(suite)
    (target/'tests.txt').write_text(transcript.getvalue(),encoding='utf-8')
    summary=dict(tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),skips=len(result.skipped),
                 python=platform.python_version(),platform=platform.system(),machine=platform.machine(),
                 independent=False,production_kernel=26,acceptance_executions=0,
                 command='python -m unittest discover -s experiments/semantic_interpreter -p test_interpreter.py -v')
    (target/'TEST-RESULTS.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    samples={
        'CFG66':b'title="a\\n\\"b"\ncount=007\nenabled=true\nnote=none\n',
        'DSV66':b'k1,"a,b",007\nk2,"say ""hi""",0\n',
        'BXC66':bytes.fromhex('52 36 36 43 01 01 01 61 00 02 FF 00 00 02 00 10')}
    runs={}
    for fmt,data in samples.items():
        p=json.loads((HERE/f'{fmt}.plan.json').read_text(encoding='utf-8'))
        first=execute(p,data)
        assert first['status']=='success',first
        results=[execute(p,data) for _ in range(10)]
        assert all(r==first for r in results)
        runs[fmt]=dict(nodes=validate(p),input_hex=data.hex(),repetitions=10,identical=True,result=serial(first))
    (target/'REPRODUCIBILITY.json').write_text(json.dumps(runs,indent=2)+'\n',encoding='utf-8')
    baseline=json.loads((HERE/'BASELINE.json').read_text(encoding='utf-8'))
    assert inventory()==baseline['protected_files']
    verified=verify_publications()
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(HERE.iterdir()) if p.is_file()}
    (target/'IMPLEMENTATION-IDENTITIES.json').write_text(json.dumps(dict(files=hashes,preserved_files=len(baseline['protected_files']),verified_publications=len(verified)),indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2))
    if not result.wasSuccessful(): raise SystemExit(1)
