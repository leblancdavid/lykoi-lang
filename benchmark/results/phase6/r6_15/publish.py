"""Check preservation/publication without reauthoring or rescoring submissions."""
import os
import re
import subprocess
import sys
import time
from evidence import HERE, ROOT, now, load, save, sha, verify

GUIDANCE=['AGENTS.md','benchmark/README.md','docs/agent-workflow.md',
          'docs/project-overview.md','docs/research-log.md','docs/decisions.md']


def main():
    verify(load(HERE/'BASELINE.json')['preserved'])
    commands=[
        [sys.executable,'-B','-m','unittest','discover','-s','benchmark/results/phase6/r6_15','-p','test_scoring.py','-v'],
        [sys.executable,'-B','-m','unittest','discover','-s','experiments/semantic_interpreter','-p','test_interpreter.py','-v'],
        [sys.executable,'-B','-m','unittest','discover','-s','tests','-p','test_compiler.py','-v'],
        [sys.executable,'-B','-m','unittest','discover','-s','tests','-p','test_application.py','-v'],
        [sys.executable,'-B','-m','unittest','discover','-s','benchmark/harness','-p','test_baseline.py','-v'],
        [sys.executable,'-B','-m','unittest','discover','-s','benchmark/results/phase6/r6_13','-p','test_scorer.py','-v'],
        [sys.executable,'-B','-m','air_compiler.cli','validate','air/task_manager.json'],
        [sys.executable,'-B','-m','air_compiler.cli','safety','air/task_manager.json'],
        ['git','diff','--check']]
    checks=[]
    env={**os.environ,'PYTHONPATH':str(ROOT/'src'),'PYTHONDONTWRITEBYTECODE':'1'}
    for command in commands:
        start=time.perf_counter()
        p=subprocess.run(command,cwd=ROOT,env=env,capture_output=True,text=True,timeout=120)
        row=dict(command=command,returncode=p.returncode,seconds=time.perf_counter()-start,
                 stdout=p.stdout,stderr=p.stderr)
        checks.append(row)
        print('PASS' if p.returncode==0 else 'FAIL',' '.join(command))
        if p.returncode:
            raise RuntimeError(p.stderr)
    report=HERE.parent/'R6_15-REPORT.md'
    paths=[p for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    paths += [report]+[ROOT/n for n in GUIDANCE]
    whitespace=[]
    for p in paths:
        for n,line in enumerate(p.read_text(encoding='utf-8').splitlines(),1):
            if line.rstrip()!=line:
                whitespace.append(dict(file=p.relative_to(ROOT).as_posix(),line=n))
    assert not whitespace,whitespace
    verify(load(HERE/'BASELINE.json')['preserved'])
    assert load(ROOT/'benchmark/results/phase5c/R5_114-KERNEL-ACCOUNTING.json')['final_count']==26
    for freeze in ('BASE-FREEZE.json','MODIFIED-FREEZE.json'):
        verify(load(HERE/freeze)['files'])
    for freeze in ('TASK-FREEZE.json','MODIFICATION-SEAL.json'):
        for name,digest in load(HERE/freeze)['files'].items():
            assert sha(HERE/name)==digest
    save(HERE/'PUBLICATION-CHECKS.json',dict(utc=now(),checks=checks,untracked_whitespace=whitespace,
        preserved_identities=len(load(HERE/'BASELINE.json')['preserved']),kernel=26,
        p6_a04_acceptance_executions=0,p6_a05_access=False,
        frozen_inputs_and_submissions_verified=True,
        regression_methods=sum(int(m.group(1)) for r in checks
            for m in [re.search(r'Ran (\d+) tests?',r['stderr'])] if m)))
    paths += [HERE/'PUBLICATION-CHECKS.json']
    save(HERE/'PUBLICATION-IDENTITIES.json',dict(utc=now(),classification='R6_15_EXPLORATORY_COMPARISON_ONLY',
        files={p.relative_to(ROOT).as_posix():sha(p) for p in sorted(set(paths))}))
    verify(load(HERE/'PUBLICATION-IDENTITIES.json')['files'])
    print('Publication identity and preservation checks passed')


if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='verify':
        verify(load(HERE/'BASELINE.json')['preserved'])
        verify(load(HERE/'PUBLICATION-IDENTITIES.json')['files'])
        print('Publication and preservation verified (read-only)')
    else:
        main()
