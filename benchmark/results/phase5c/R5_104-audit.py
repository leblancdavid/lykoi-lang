"""Final content, history, whitespace and change-scope checks; no product repair."""
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
spec = importlib.util.spec_from_file_location('r104_audit_pins', OUT/'R5_104-generic.py')
pins = importlib.util.module_from_spec(spec); spec.loader.exec_module(pins)


def main():
    lock=json.loads((OUT/'R5_104-GENERIC-LOCK.json').read_text(encoding='utf-8'))
    corpus=json.loads((OUT/'R5_104-CORPUS-LOCK.json').read_text(encoding='utf-8'))
    assert pins.implementation_pins()==lock['implementation']
    assert pins.history_pins()==lock['history']
    assert corpus['implementation_lock_sha256']==hashlib.sha256((OUT/'R5_104-GENERIC-LOCK.json').read_bytes()).hexdigest()
    for case, expected in corpus['cases'].items():
        path=OUT/('R5_104-'+case+'-CANDIDATE.json')
        assert hashlib.sha256(path.read_bytes()).hexdigest()==expected
        candidate=json.loads(path.read_text(encoding='utf-8'))['producer_capture']
        for source, source_hash in candidate['source_files'].items():
            assert hashlib.sha256((ROOT/source).read_bytes()).hexdigest()==source_hash
    status=subprocess.check_output(['git','status','--short'],cwd=ROOT,text=True)
    paths=subprocess.check_output(['git','diff','--name-only'],cwd=ROOT,text=True).splitlines()
    paths += subprocess.check_output(['git','ls-files','--others','--exclude-standard'],cwd=ROOT,text=True).splitlines()
    allowed_docs={'AGENTS.md','README.md','benchmark/README.md','docs/agent-workflow.md','docs/decisions.md','docs/project-overview.md','docs/research-log.md','docs/typed-mutable-values-v1.md'}
    allowed_src=set(lock['implementation'])
    assert all(p in allowed_docs or p in allowed_src or p.startswith('benchmark/results/phase5c/R5_104-') for p in paths), paths
    whitespace=[]
    for path in paths:
        content=(ROOT/path).read_text(encoding='utf-8')
        whitespace += [dict(path=path,line=i) for i,line in enumerate(content.splitlines(),1) if line.rstrip()!=line]
        if path.endswith('.json'): json.loads(content)
    assert not whitespace, whitespace
    check=subprocess.run(['git','diff','--check'],cwd=ROOT,capture_output=True,text=True)
    assert check.returncode==0,check.stdout+check.stderr
    product_paths=['src/air_compiler/mutable_values.py','src/air_compiler/mutable_runtime.py','src/lykoi_pipeline/mutable_profile.py','src/lykoi_workspace/mutable_schema.py']
    assert not any(re.search(r'\bB(?:0[1-9]|1[0-9]|20)\b',(ROOT/p).read_text(encoding='utf-8')) for p in product_paths)
    transfer=json.loads((OUT/'R5_104-TRANSFER-EVIDENCE.json').read_text(encoding='utf-8'))
    synthetic=json.loads((OUT/'R5_104-SYNTHETIC-EVIDENCE.json').read_text(encoding='utf-8'))
    verification=json.loads((OUT/'R5_104-GENERIC-FINAL-VERIFICATION.json').read_text(encoding='utf-8'))
    assert verification['all_pass'] and verification['tests']==340
    assert all(r['first_blocker']=='SUCCESS' for r in synthetic['cases'])
    assert [r['case'] for r in transfer['cases'] if r['first_blocker']=='SUCCESS']==['B01','B02','B03','B04','B05','B10']
    assert all(next(r for r in transfer['cases'] if r['case']==case)['first_blocker']=='FORMALIZATION' for case in ('B17','B20'))
    result=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),implementation_lock_matches=True,history_matches=True,corpus_capture_plan_hashes_match=True,
        all_source_hashes_match=True,tests=340,all_checks_pass=True,whitespace_issues=whitespace,git_diff_check=dict(exit=check.returncode,stdout=check.stdout,stderr=check.stderr),
        scope_check=True,benchmark_ids_absent_from_product_mutation_modules=True,changed_files=paths,git_status=status,
        synthetic_external_invocations=synthetic['external_invocations'],transfer_external_invocations=sum(r.get('external_invocations',0) for r in transfer['cases']),
        successes=[dict(case=r['case'],external_invocations=r['external_invocations']) for r in transfer['cases'] if r['first_blocker']=='SUCCESS'],
        stop='R5.104 complete; R5.105 recommendation only; no infrastructure work or outcome-driven product changes')
    pins.publish('R5_104-FINAL-AUDIT.json',result)
    print(json.dumps({k:v for k,v in result.items() if k not in ('changed_files','git_status','git_diff_check')},indent=2))


if __name__=='__main__': main()
