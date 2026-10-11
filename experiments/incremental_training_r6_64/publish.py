"""Publish the terminal preflight gap; never dispatch a model or repair the stack."""
import ast
import json
import re
import subprocess
import sys
import run


def verify():
    r = run
    # Historical helpers import a module named run. Keep their namespace isolated
    # from this publication process's R6.64 run module.
    proc=subprocess.run([str(r.PYTHON),str(r.ROOT/'experiments/incremental_data_r6_63/publish.py'),
                         'baseline-check'],cwd=r.ROOT,capture_output=True,text=True,check=True)
    receipt=r.read(r.OUT/'BASELINE.json')
    assert receipt['inherited']==r.read(r.data.OUT/'BASELINE.json')
    prior=r.read(r.data.OUT/'PUBLICATION-IDENTITIES.json')
    assert r.sha(r.data.OUT/'PUBLICATION-IDENTITIES.json')==receipt['r6_63_publication_sha256']
    for name,item in prior['files'].items():
        assert r.sha(r.ROOT/name)==item['sha256'],name
    home=r.STORE/'python/cpython-3.12.11-windows-x86_64-none'
    binaries=dict(python_executable_sha256=home/'python.exe',python_dll_sha256=home/'python312.dll',
                  venv_executable_sha256=r.PYTHON,uv_executable_sha256=r.STORE/'uv/uv.exe',
                  requirements_lock_sha256=r.ROOT/'benchmark/results/phase6/r6_52/requirements-lock.txt')
    assert {k:r.sha(p) for k,p in binaries.items()}==receipt['executable_supplement']['identities']
    assert not (r.OUT/'PREFLIGHT.json').exists()
    assert not r.ARTIFACTS.exists()
    assert not list(r.OUT.glob('*DISPATCH-CLAIM.json'))
    counts = dict(add=0,le=0,eq=0)
    records = r.rows()
    assert len(records) == 10
    manifest = r.read(r.OUT/'DATASET-IDENTITIES.json')
    for row, entry in zip(records,manifest['records'],strict=True):
        for name, item in entry['files'].items():
            path=r.ROOT/name
            assert r.sha(path)==item['sha256'] and path.stat().st_size==item['bytes'],name
        eid=row['episode_id'].split('/')[-1]
        folder=r.data.OUT/'episodes'/eid
        envelope=r.read(folder/'B-RECORD-2.json')
        assert entry['provenance']==envelope['provenance']['class']=='deterministic_expert_demonstration'
        assert row['completion'][0]['content']==envelope['target']['text']
        assert row['before']==r.read(folder/'BEFORE.json')
        assert row['cases']==r.read(folder/'ACCEPTANCE.json')['cases']
        target=r.read(folder/'ACTION.json')
        counts[next(iter(target['node']['expr']))]+=1
    assert counts==manifest['operations']==dict(add=4,le=3,eq=3)
    result=r.read(r.OUT/'RESULT.json')
    assert result['optimizer_updates']==0 and result['training_attempts_dispatched']==0
    allowed=['experiments/incremental_training_r6_64/', 'benchmark/results/phase6/r6_64/',
             'benchmark/results/phase6/R6_64-REPORT.md','benchmark/results/phase6/R6_64-PROTOCOL.md',
             'docs/research-log-r6.64.md']
    status=subprocess.check_output(['git','status','--porcelain','--untracked-files=all'],cwd=r.ROOT,text=True)
    assert all(any(line[3:].replace('\\','/').startswith(p) for p in allowed) for line in status.splitlines()),status
    paths=list(r.HERE.glob('*.py'))+[r.ROOT/'benchmark/results/phase6/R6_64-REPORT.md',
          r.ROOT/'benchmark/results/phase6/R6_64-PROTOCOL.md',r.ROOT/'docs/research-log-r6.64.md']
    paths += [p for p in r.OUT.iterdir() if p.is_file() and p.name not in ('PUBLICATION-IDENTITIES.json','VERIFICATION.json')]
    for path in paths:
        text=path.read_text(encoding='utf-8')
        assert '\r' not in text and all(line==line.rstrip() for line in text.splitlines()),path
        if path.suffix=='.json': json.loads(text)
        if path.suffix=='.py': ast.parse(text)
        assert not re.search(r'sk-[A-Za-z0-9]{20,}|'+'-----BEGIN '+r'[A-Z ]*'+'PRIVATE KEY-----',text),path
        if path.suffix=='.md':
            for link in re.findall(r'\]\(([^)]+)\)',text):
                if link.startswith(('https:','#')): continue
                target=(path.parent/link.split('#')[0]).resolve()
                assert target.exists() or target in (r.OUT/'PUBLICATION-IDENTITIES.json',r.OUT/'VERIFICATION.json'),(path,link)
    subprocess.run(['git','diff','--check'],cwd=r.ROOT,check=True)
    payload=dict(version='r6.64-publication-1',files={p.relative_to(r.ROOT).as_posix():
                 dict(sha256=r.sha(p),bytes=p.stat().st_size) for p in sorted(paths)})
    if sys.argv[1]=='seal':
        assert not (r.OUT/'PUBLICATION-IDENTITIES.json').exists()
        r.write('PUBLICATION-IDENTITIES.json',payload)
        r.write('VERIFICATION.json',dict(passed=True,manifest_sha256=r.sha(r.OUT/'PUBLICATION-IDENTITIES.json'),
                baseline_and_history='PASS',baseline_process=dict(argv=proc.args,returncode=proc.returncode,
                stdout=proc.stdout,stderr=proc.stderr),dataset_identity_records=10,operation_counts=counts,
                old_adapter_checkpoint_environment_preserved=True,production_kernel_constructs=26,
                no_dispatch_claims_or_adapter_directory=True,publication_json_python_links_whitespace_credentials='PASS',
                git_diff_check='PASS',new_model_calls=0,training_updates=0,behavioral_rescoring=0,
                scorer_schema_preflight='FAIL retained; not repaired',P6_A04_acceptance=0,P6_A05_access=False))
    else:
        assert payload==r.read(r.OUT/'PUBLICATION-IDENTITIES.json')
        assert r.sha(r.OUT/'PUBLICATION-IDENTITIES.json')==r.read(r.OUT/'VERIFICATION.json')['manifest_sha256']
    print('PASS terminal publication integrity,10 B record identities, historical baseline, zero model dispatch')


if __name__=='__main__': verify()
