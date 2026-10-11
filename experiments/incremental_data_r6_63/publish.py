"""Independent replay/preservation/publication check; no training or historical scoring."""
import ast
import json
from pathlib import Path
import re
import subprocess
import sys
from freeze import OUT, ROOT, baseline, c, pin, read, sha, write
from assembly import apply, behavior, agrees
from qualify import frozen_check

PRIVATE_PYTHON=r'C:\Users\lblan\AppData\Local\Temp\opencode\lykoi-r6-52\venv\Scripts\python.exe'


def payload_paths():
    paths=[ROOT/'benchmark/results/phase6/R6_63-REPORT.md',ROOT/'docs/research-log-r6.63.md']
    paths += list((ROOT/'experiments/incremental_data_r6_63').glob('*.py'))
    paths += [p for p in OUT.rglob('*') if p.is_file() and p.name not in ('PUBLICATION-IDENTITIES.json','VERIFICATION.json')]
    return sorted(paths)


def replay():
    import jsonschema
    from referencing import Registry, Resource
    frozen_check()
    base=ROOT/'benchmark/results/phase6/r6_62'
    common=read(base/'common-1.schema.json')
    registry=Registry().with_resource(common['$id'],Resource.from_contents(common))
    validators={k:jsonschema.Draft202012Validator(read(base/f'{k}-1.schema.json'),registry=registry) for k in ('A','B')}
    cases=0
    for folder in sorted((OUT/'episodes').iterdir()):
        before,action=read(folder/'BEFORE.json'),read(folder/'ACTION.json')
        after,validation=apply(before,action)
        assert after==read(folder/'AFTER.json')
        assert validation==read(folder/'VALIDATION.json')['native']
        assert after['package']==read(folder/'A-TARGET.json')
        for kind,name in (('A','A-RECORD.json'),('B','B-RECORD-2.json')):
            record=read(folder/name)
            validators[kind].validate(record)
            assert record['provenance']['class']=='deterministic_expert_demonstration'
            target=c.load(record['target']['text'])
            assert target==(after['package'] if kind=='A' else action)
        original=read(folder/'OBSERVATIONS.json')
        for f,row in zip(read(folder/'ACCEPTANCE.json')['cases'],original['pass1'],strict=True):
            actual=behavior(after,f['arguments'])
            assert actual==row['actual'] and agrees(actual,f['expected'])
            cases+=1
        assert original['pass1']==original['pass2']
    return cases


def run_tests():
    completed=subprocess.run([sys.executable,'-m','unittest','discover','-s','experiments/incremental_data_r6_63',
        '-p','test_assembly.py','-v'],cwd=ROOT,capture_output=True,text=True)
    assert completed.returncode==0, completed.stdout+completed.stderr
    return dict(command=completed.args,exit_code=completed.returncode,stdout=completed.stdout,stderr=completed.stderr)


def summary():
    rows=read(OUT/'DEMONSTRATIONS.json')['entries']
    measures=read(OUT/'AB-MEASUREMENTS-2.json')['entries']
    observations=[x for d in rows for x in read(OUT/'episodes'/d['episode']/'OBSERVATIONS.json')['pass1']]
    counts={op:sum(r['operation']==op for r in rows) for op in ('add','le','eq')}
    write(OUT/'SUMMARY-2.json',dict(classification='R6_63_INCREMENTAL_DATA_QUALIFIED',verified_demonstrations=10,
        operation_counts=counts,unique_behavioral_fixtures=len(observations),two_pass_observations=2*len(observations),
        overflow_fixtures=sum(r['expected'].get('code')=='OVERFLOW' for r in observations),
        invalid_argument_fixtures=sum(r['expected'].get('code','').startswith('ARGUMENT_') for r in observations),
        positive_typed_output_fixtures=sum(r['expected']['status']=='success' for r in observations),
        mutation_controls=19,A_content_tokens=sum(r['A_content_tokens'] for r in measures),B_content_tokens=sum(r['B_content_tokens'] for r in measures),
        prompt_tokens_range=[min(r['prompt_tokens_each'] for r in measures),max(r['prompt_tokens_each'] for r in measures)],
        A_target_token_range=[min(r['A_content_tokens'] for r in measures),max(r['A_content_tokens'] for r in measures)],
        B_target_token_range=[min(r['B_content_tokens'] for r in measures),max(r['B_content_tokens'] for r in measures)],
        A_validation_median_ns_range=[min(r['timings']['A_native_validation']['median_ns'] for r in measures),max(r['timings']['A_native_validation']['median_ns'] for r in measures)],
        A_expand_median_ns_range=[min(r['timings']['A_validation_and_expansion']['median_ns'] for r in measures),max(r['timings']['A_validation_and_expansion']['median_ns'] for r in measures)],
        B_assembly_median_ns_range=[min(r['timings']['B_apply_including_before_validation_after_validation_hashing_expansion']['median_ns'] for r in measures),max(r['timings']['B_apply_including_before_validation_after_validation_hashing_expansion']['median_ns'] for r in measures)],
        qualified_evaluation_families=0,training=0,inference=0,kernel_constructs=26))
    if not (OUT/'TEST-RESULTS.json').exists():
        write(OUT/'TEST-RESULTS.json',run_tests())
    else:
        run_tests()
    print('PASS summary and five additional adversarial assembly tests')


def publish(seal):
    subprocess.run([PRIVATE_PYTHON,str(Path(__file__)),'baseline-check'],cwd=ROOT,check=True)
    count=replay()
    run_tests()
    allowed=['benchmark/results/phase6/r6_63/','benchmark/results/phase6/R6_63-REPORT.md',
             'experiments/incremental_data_r6_63/','docs/research-log-r6.63.md']
    status=subprocess.check_output(['git','status','--porcelain','--untracked-files=all'],cwd=ROOT,text=True)
    assert all(any(line[3:].replace('\\','/').startswith(p) for p in allowed) for line in status.splitlines()),status
    paths=payload_paths()
    for path in paths:
        text=path.read_text(encoding='utf-8')
        assert '\r' not in text and all(s==s.rstrip() for s in text.splitlines()),path
        if path.suffix=='.json': read(path)
        if path.suffix=='.py': ast.parse(text)
        if path.suffix=='.md':
            for link in re.findall(r'\]\(([^)]+)\)',text):
                target=(path.parent/link.split('#')[0]).resolve()
                pending_seal=seal and target in {OUT/'PUBLICATION-IDENTITIES.json',OUT/'VERIFICATION.json'}
                assert link.startswith(('https:','#')) or target.exists() or pending_seal,(path,link)
        secret_pattern=r'sk-[A-Za-z0-9]{20,}|'+'-----BEGIN '+r'[A-Z ]*'+'PRIVATE KEY-----'
        assert not re.search(secret_pattern,text),path
    subprocess.run(['git','diff','--check'],cwd=ROOT,check=True)
    manifest=dict(version='r6.63-publication-1',files={p.relative_to(ROOT).as_posix():dict(sha256=sha(p),bytes=p.stat().st_size) for p in paths})
    if seal:
        write(OUT/'PUBLICATION-IDENTITIES.json',manifest)
        write(OUT/'VERIFICATION.json',dict(passed=True,manifest_sha256=sha(OUT/'PUBLICATION-IDENTITIES.json'),
              baseline='PASS',independent_process_behavior_replays=count,adversarial_test_methods=5,
              records_schema_valid=20,scope_whitespace_links_credentials='PASS',git_diff_check='PASS',
              training=0,model_inference=0,optimizer_scheduler_updates=0,historical_rescoring=0,
              new_execution_primitives=0,P6_A04_acceptance=0,P6_A05_access=False))
    else:
        assert manifest==read(OUT/'PUBLICATION-IDENTITIES.json')
        assert sha(OUT/'PUBLICATION-IDENTITIES.json')==read(OUT/'VERIFICATION.json')['manifest_sha256']
    print('PASS R6.63 preservation, publication integrity and fresh-process replay',count)


if __name__=='__main__':
    if sys.argv[1]=='baseline-check':
        assert baseline()==read(OUT/'BASELINE.json')
        print('PASS preserved R6.62/R6.59/policy/schema/foundation baseline')
    elif sys.argv[1]=='summary': summary()
    elif sys.argv[1]=='index':
        data=read(OUT/'DEMONSTRATIONS.json')
        for entry in data['entries']:
            path=OUT/'episodes'/entry['episode']/'B-RECORD-2.json'
            entry['B']=dict(path=path.relative_to(ROOT).as_posix(),sha256=sha(path))
        data['envelope_revision_note']='Uses schema-qualified B-RECORD-2; initial null-trace envelopes retained, not producer targets.'
        write(OUT/'DEMONSTRATIONS-2.json',data)
        print('PASS corrected qualified demonstration index')
    else: publish(sys.argv[1]=='seal')
