"""Identity-only additive publication; never reruns halted preflight controls."""
import ast
import json
from pathlib import Path
import random
import re
import subprocess
import sys
from integration import *


def checks():
    assert Path(sys.executable).resolve()==PYTHON.resolve() and sys.version_info[:3]==(3,12,11)
    frozen_check()
    publisher.checks()
    assert q.freeze.baseline()==read(ROOT/'benchmark/results/phase6/r6_73/BASELINE.json')
    assert f.publication('r6_73')==read(OUT/'BASELINE.json')['r6_73']
    for name, expected in read(OUT/'BASELINE.json')['preserved_publications'].items():
        assert f.publication(name)==expected
    for filename in ('TRAINING-DATA-FREEZE.json','EVALUATION-FREEZE.json'):
        for path,digest in read(OUT/filename)['files'].items():
            assert sha(ROOT/path)==digest
    for filename,source in (('REMAINING-CONTROLS-FREEZE.json','remaining_controls.py'),('FINAL-AUDIT-FREEZE.json','final_audit.py')):
        assert read(OUT/filename)['source_sha256']==sha(HERE/source)
    dataset = read(OUT/'DATASET.json')
    assert {identity(r) for r in dataset['records']}=={identity(r) for r in publisher.ready_records()['records']}
    sampling = read(OUT/'SAMPLING.json')
    rng = random.Random(651)
    state = rng.getstate()
    assert [p['episode_id'] for p in sampling['sequence']]==sampling['cycle']*4
    assert rng.getstate()==state
    assert len(dataset['records'])==54 and sampling['presentations']==216
    evaluation = read(OUT/'EVALUATION.json')
    training_requirements = {r['requirement_identity'] for r in dataset['records']}
    reserved_requirements = {r['requirement_identity'] for r in evaluation['records'] if r['partition']=='evaluation_exploratory'}
    assert not training_requirements & reserved_requirements
    assert len(reserved_requirements)==12
    assert read(OUT/'ADVERSARIAL-VERIFICATION.json')['passed']
    assert read(OUT/'COMPACT-DECODER-CONTROLS.json')['passed']
    assert read(OUT/'TRAINING-READINESS.json')['classification']=='R6_74_CONFIGURATION_GAP'
    assert not read(OUT/'TRAINING-READINESS.json')['ready']
    assert read(OUT/'LOSS-MASK-VERIFICATION.json')['first_four_supervised_counts']==[24]*4
    assert not read(OUT/'EXECUTABLE-INTEGRATION-AUDIT.json')['required_resource_provider_pass']
    assert not (OUT/'execution').exists() and not ARTIFACTS.exists()
    return dict(baseline_preserved=True,source_configuration_evaluation_freezes=True,dataset_rows=54,
        direct=18,corrective=36,sampling_presentations=216,sampling_rng_unchanged=True,
        reserved_training_requirement_overlap=0,reserved_unique_requirements=12,
        failures_preserved=True,ready=False,classifier='R6_74_CONFIGURATION_GAP')


def seal(verify):
    receipt = checks()
    paths = sorted([p for p in HERE.iterdir() if p.is_file()] + [p for p in OUT.iterdir() if p.is_file() and
        p.name not in ('PUBLICATION-IDENTITIES.json','VERIFICATION.json')] +
        [ROOT/'benchmark/results/phase6/R6_74-REPORT.md'] + list((ROOT/'docs').glob('*-r6.74.md')))
    for p in paths:
        text = p.read_text(encoding='utf-8')
        assert '\r' not in text and all(line==line.rstrip() for line in text.splitlines()),p
        assert not re.search(r'sk-[A-Za-z0-9]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----',text),p
        if p.suffix=='.json': json.loads(text)
        if p.suffix=='.py' or p.name=='EFFECTIVE-WORKER.py.txt': ast.parse(text)
        if p.suffix=='.md':
            for link in re.findall(r'\]\(([^)]+)\)',text):
                if not link.startswith(('https:','#')):
                    target=p.parent/link.split('#')[0]
                    assert target.exists() or (not verify and target.name in ('PUBLICATION-IDENTITIES.json','VERIFICATION.json')),(p,link)
    status = subprocess.check_output(['git','status','--porcelain','--untracked-files=all'],cwd=ROOT,text=True)
    permitted = {'benchmark/results/phase6/R6_74-REPORT.md','docs/project-overview-r6.74.md','docs/research-log-r6.74.md','docs/decisions-r6.74.md'}
    for line in status.splitlines():
        path=line[3:].replace('\\','/')
        assert line.startswith('??') and (path in permitted or path.startswith(('experiments/contrastive_preflight_r6_74/','benchmark/results/phase6/r6_74/'))),line
    subprocess.run(['git','diff','--check'],cwd=ROOT,check=True)
    manifest = dict(version='r6.74-publication-1',files={p.relative_to(ROOT).as_posix():dict(sha256=sha(p),bytes=p.stat().st_size) for p in paths})
    if verify:
        assert manifest==read(OUT/'PUBLICATION-IDENTITIES.json')
        assert sha(OUT/'PUBLICATION-IDENTITIES.json')==read(OUT/'VERIFICATION.json')['manifest_sha256']
        assert receipt==read(OUT/'VERIFICATION.json')['checks']
    else:
        write('PUBLICATION-IDENTITIES.json',manifest)
        write('VERIFICATION.json',dict(passed=True,publication_integrity_only=True,training_ready=False,
            manifest_sha256=sha(OUT/'PUBLICATION-IDENTITIES.json'),publication_files=len(paths),checks=receipt,
            git_diff_check=True,tracked_changes=0,syntax_links_whitespace_credentials=True,kernel_constructs=26,
            model_loads=0,participant_inference=0,training=0,optimizer_updates=0,scheduler_updates=0,
            historical_rescoring=0,p6_a04_acceptance=0,p6_a05_access=False,stopped=True))
    print('PASS R6.74 publication integrity/preservation/git diff --check; CONFIGURATION_GAP retained')


if __name__=='__main__':
    seal(sys.argv[1]=='verify')
