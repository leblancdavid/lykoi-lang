"""Seal every additive attempt, then verify without repeating semantic controls."""
import ast
import json
import re
import subprocess
import sys
from pathlib import Path
import successor3
import context75 as x
import preflight75

PUBLICATION = successor3.successor2.ORIGINAL_OUT


def checks():
    x.guard()
    x.frozen_check()
    assert preflight75.baseline() == x.read(x.OUT/'BASELINE.json')
    for folder in (PUBLICATION,PUBLICATION/'qualification_2',PUBLICATION/'qualification_3'):
        for path, digest in x.read(folder/'PREFLIGHT-FREEZE.json')['files'].items():
            assert x.sha(x.ROOT/path) == digest,path
    assert (PUBLICATION/'HALT-qualify.json').is_file()
    assert (PUBLICATION/'qualification_2/HALT-finish.json').is_file()
    for name in ('CPU-QUALIFICATION.json','NORMALIZATION-VERIFICATION.json','DATASET-MASK-VERIFICATION.json',
                 'SAMPLING-SCHEDULE-VERIFICATION.json','EVALUATION-VERIFICATION.json','RESOURCE-VERIFICATION.json',
                 'DECODER-SCORER-VERIFICATION.json','ADVERSARIAL-PREFLIGHT.json','LAUNCH-INTEGRATION-AUDIT.json'):
        assert x.read(x.OUT/name)['passed'],name
    readiness = x.read(x.OUT/'TRAINING-READINESS.json')
    assert readiness['ready'] and readiness['classification'] == 'R6_75_CONTRASTIVE_TRAINING_READY'
    assert readiness['unresolved_configuration_dependencies'] == []
    assert x.read(x.OUT/'LAUNCH-INTEGRATION-AUDIT.json')['unresolved_configuration_dependencies'] == []
    assert x.read(x.OUT/'dry-launch/RESULT.json')['passed']
    assert not x.ARTIFACTS.exists() and not (x.OUT/'execution').exists()
    assert x.read(x.OLD/'TRAINING-READINESS.json')['classification'] == 'R6_74_CONFIGURATION_GAP'
    subprocess.run(['git','diff','--check'],cwd=x.ROOT,check=True)
    tracked = subprocess.check_output(['git','diff','--name-only','HEAD'],cwd=x.ROOT,text=True)
    assert not tracked.strip(), 'HISTORICAL_TRACKED_CHANGE'
    status = subprocess.check_output(['git','status','--porcelain','--untracked-files=all'],cwd=x.ROOT,text=True)
    allowed = {'benchmark/results/phase6/R6_75-REPORT.md',
               'docs/project-overview-r6.75.md','docs/research-log-r6.75.md','docs/decisions-r6.75.md'}
    for line in status.splitlines():
        path = line[3:].replace('\\','/')
        assert line.startswith('??') and (path in allowed or path.startswith((
            'experiments/contrastive_preflight_r6_75/','benchmark/results/phase6/r6_75/'))),line
    return dict(baseline_preserved=True,all_attempt_freezes_preserved=True,failures_preserved=True,
        original_r6_74_classification='R6_74_CONFIGURATION_GAP',kernel_constructs=26,tracked_changes=0,
        additive_scope=True,git_diff_check=True,training_ready=True,
        classification=readiness['classification'],configuration_identity=readiness['configuration_identity'],
        unresolved_configuration_dependencies=[])


def main():
    verify = sys.argv[1:] == ['verify']
    receipt = checks()
    paths = sorted([p for p in x.HERE.rglob('*') if p.is_file()] +
        [p for p in PUBLICATION.rglob('*') if p.is_file() and p.name not in ('PUBLICATION-IDENTITIES.json','VERIFICATION.json')] +
        [x.ROOT/'benchmark/results/phase6/R6_75-REPORT.md'] + list((x.ROOT/'docs').glob('*-r6.75.md')))
    for path in paths:
        text = path.read_text(encoding='utf-8')
        assert '\r' not in text and all(line == line.rstrip() for line in text.splitlines()),path
        assert not re.search(r'sk-[A-Za-z0-9]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----',text),path
        if path.suffix == '.json':
            json.loads(text)
        if path.suffix == '.py' or path.name in ('EFFECTIVE-WORKER.py.txt','EFFECTIVE-DIAGNOSTIC.py.txt'):
            ast.parse(text)
        if path.suffix == '.md':
            for link in re.findall(r'\]\(([^)]+)\)',text):
                if not link.startswith(('https:','#')):
                    target = path.parent/link.split('#')[0]
                    assert target.exists() or (not verify and target.name in ('PUBLICATION-IDENTITIES.json','VERIFICATION.json')),(path,link)
    manifest = dict(version='r6.75-publication-1',files={p.relative_to(x.ROOT).as_posix():
        dict(sha256=x.sha(p),bytes=p.stat().st_size) for p in paths})
    if verify:
        assert manifest == x.read(PUBLICATION/'PUBLICATION-IDENTITIES.json')
        assert x.sha(PUBLICATION/'PUBLICATION-IDENTITIES.json') == x.read(PUBLICATION/'VERIFICATION.json')['manifest_sha256']
        assert receipt == x.read(PUBLICATION/'VERIFICATION.json')['checks']
    else:
        saved_out = x.OUT
        try:
            x.OUT = PUBLICATION
            x.write('PUBLICATION-IDENTITIES.json',manifest)
            x.write('VERIFICATION.json',dict(passed=True,checks=receipt,publication_files=len(paths),
                manifest_sha256=x.sha(PUBLICATION/'PUBLICATION-IDENTITIES.json'),
                syntax_links_whitespace_credential_patterns=True,model_loads=0,inference_calls=0,
                backward_calls=0,optimizer_instances=0,scheduler_instances=0,optimizer_updates=0,scheduler_updates=0,
                historical_rescoring=0,p6_a04_acceptance=0,p6_a05_access=False,stopped=True))
        finally:
            x.OUT = saved_out
    print('PASS R6.75 publication integrity, preservation, additive scope and git diff --check')


if __name__ == '__main__':
    main()
