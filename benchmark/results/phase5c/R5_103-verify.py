"""Current semantic regressions and checks; evidence, not qualification gates."""
from concurrent.futures import ThreadPoolExecutor
import datetime
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
COMMANDS=[['-m','unittest','discover','-s','tests','-p',p,'-v'] for p in (
    'test_fresh_typed_corpus.py','test_existing_composition.py','test_scalar_normal_path.py','test_query_normal_path.py',
    'test_collection_query.py','test_collection_query_behavior.py','test_compiler.py','test_application.py',
    'test_requirements_workspace.py','test_sealed_pipeline.py','test_authority_controller.py','test_public_rehearsal.py')]
COMMANDS += [['-m','unittest','discover','-s','benchmark/evaluation','-p',p,'-v'] for p in (
    'test_formal_requirements_r5_80.py','test_behavioral_discovery_r5_82.py','test_implementation_adequacy_r5_81.py',
    'test_benchmark_documents_v1.py','test_source_coverage_r5_84.py')]
COMMANDS += [['-m','unittest','discover','-s','benchmark/harness','-p','test_baseline.py','-v'],
             ['-m','air_compiler.cli','validate','air/task_manager.json'],['-m','air_compiler.cli','safety','air/task_manager.json']]


def run(argv):
    p=subprocess.run([sys.executable,*argv],cwd=ROOT,env=dict(os.environ,PYTHONPATH=os.pathsep.join((str(ROOT/'src'),str(ROOT)))),capture_output=True,text=True,encoding='utf-8',timeout=420)
    count=re.search(r'Ran (\d+) tests?',p.stderr)
    row=dict(argv=[sys.executable,*argv],exit=p.returncode,tests=int(count.group(1)) if count else 0,stdout=p.stdout,stderr=p.stderr)
    print(argv,'exit',p.returncode,'tests',row['tests'],flush=True)
    return row


def main():
    start=datetime.datetime.now(datetime.timezone.utc).isoformat()
    with ThreadPoolExecutor(max_workers=2) as pool: rows=list(pool.map(run,COMMANDS))
    result=dict(utc_started=start,utc_finished=datetime.datetime.now(datetime.timezone.utc).isoformat(),commands=rows,tests=sum(r['tests'] for r in rows),all_pass=all(r['exit']==0 for r in rows),scope='Current language/pipeline/application/external regressions; no machine/model/transport qualification')
    label=sys.argv[1] if len(sys.argv)>1 else 'VERIFICATION'
    assert re.fullmatch(r'[A-Z0-9-]+',label)
    with (OUT/('R5_103-'+label+'.json')).open('x',encoding='utf-8',newline='\n') as stream: json.dump(result,stream,indent=2); stream.write('\n')
    return int(not result['all_pass'])


if __name__=='__main__': sys.exit(main())
