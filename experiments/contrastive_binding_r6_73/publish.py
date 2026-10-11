"""Additive publication sealing and fresh-process preservation/record checks."""
import ast
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('r673_publisher_inputs', HERE/'qualify.py')
q = importlib.util.module_from_spec(spec)
spec.loader.exec_module(q)
ROOT, OUT, RESULTS, f = q.ROOT, q.OUT, q.RESULTS, q.f


def write(name, value):
    path = OUT/name
    assert not path.exists(), path
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False)+'\n', encoding='utf-8', newline='\n')


def ready_records():
    source = f.read(RESULTS/'TRAINING-RECORDS.json')['records']
    positives = {q.q.pin(r):r for r in source if r['label']=='positive'}
    by_scope = {(r['requirement_identity'],r['typed_scope_identity']):r for r in positives.values()}
    direct = f.read(RESULTS/'SFT-POSITIVES.json')['records']
    corrective = f.read(RESULTS/'CONTRASTIVE-SFT-POSITIVES.json')['records']
    ready = []
    for row in direct+corrective:
        parent = positives[row['record_identity']] if row['label']=='positive' else by_scope[(row['requirement_identity'],row['typed_scope_identity'])]
        obj = dict(version='r6.73-sft-ready-1', episode_id=row['episode_id'],
            prompt=row['prompt'], completion=row['completion'],
            requirement_identity=parent['requirement_identity'], typed_scope_identity=parent['typed_scope_identity'],
            compact_target_decision=parent['compact_target_decision'],
            reconstructed_action_identity=parent['reconstructed_action_identity'],
            acceptance_evidence=parent['acceptance_evidence'],
            contrast_family_identity=parent['contrast_family_identity'], contrast_identity=parent['contrast_identity'],
            label=row['label'], assistant_target_label='positive', partition='training',
            provenance_classification=parent['provenance_classification'], expectation_review='COORDINATOR_ONLY',
            positive_ledger_identity=q.q.pin(parent),
            input_candidate_label='negative' if row['label']=='positive_corrective_target' else 'NOT_APPLICABLE',
            input_negative_ledger_identity=row.get('negative_ledger_identity'),
            tokenization_evidence='CORRECTIVE-TOKENIZATION.json' if row['label']=='positive_corrective_target' else 'TOKENIZATION.json')
        assert q.q.serialize(obj['compact_target_decision'])==obj['completion'][0]['content']
        ready.append(obj)
    assert len(ready)==54 and len({r['episode_id'] for r in ready})==54
    return dict(version='r6.73-sft-ready-dataset-1', records=ready,
        direct=18, corrective=36, all_assistant_targets_positive=True, reasoning_traces=0,
        underlying_positive_records=18, distinct_requirement_identities=len({r['requirement_identity'] for r in ready}),
        independent_requirements=False, evaluation_records=0)


def checks():
    q.q.freeze.check_freeze()
    for filename in ('EXPECTATION-FREEZE.json',):
        for path,digest in f.read(OUT/filename)['files'].items():
            assert f.sha(ROOT/path)==digest,path
    for path,digest in f.read(OUT/'IMPLEMENTATION-FREEZE.json')['files'].items():
        original=ROOT/path
        if original.name in ('qualify.py','reconstruct.py'):
            original=original.with_name(original.stem+'_v1.py')
        assert f.sha(original)==digest,original
    for path,digest in f.read(RESULTS/'IMPLEMENTATION-FREEZE.json')['files'].items():
        assert f.sha(ROOT/path)==digest,path
    assert f.sha(HERE/'supplement.py')==f.read(RESULTS/'SUPPLEMENT-SOURCE-FREEZE.json')['source_sha256']
    ledger=f.read(RESULTS/'SUPERVISION-LEDGER.json')['records']
    first=f.read(OUT/'SUPERVISION-LEDGER.json')['records']
    assert {r['id']:r['result']['reconstructed_action_identity'] for r in ledger}=={r['id']:r['result']['reconstructed_action_identity'] for r in first}
    expectations=q.q.rows()
    assert len(expectations)==18
    for row in expectations:
        parent=next(r for r in ledger if r['id']==row['id']+'-positive')
        action=parent['result']['reconstructed_action']
        target=row['target']
        assert next(iter(action['node']['expr']))==target['op']
        expected_args=[{'ref':a['ref']} if 'ref' in a else {'const':a['literal']['value']} for a in (target['left'],target['right'])]
        assert q.q.c.canonical(next(iter(action['node']['expr'].values())))==q.q.c.canonical(expected_args)
        assert action['deps']==target['deps'] and action['type']==row['scope']['result_type']
        assert parent['result']['category']=='accepted' and all(o['passed'] for o in parent['result']['observations'])
    assert f.read(RESULTS/'SFT-READY.json')==ready_records()
    assert all(r['partition']=='training' and r['assistant_target_label']=='positive' for r in ready_records()['records'])
    lengths=f.read(RESULTS/'TOKENIZATION.json')['records']+f.read(RESULTS/'CORRECTIVE-TOKENIZATION.json')['records']
    assert len(lengths)==90 and all(not r['truncated'] and not r['exceeds_2048'] for r in lengths)
    assert f.read(RESULTS/'ADVERSARIAL-VERIFICATION.json')['passed']
    assert f.read(RESULTS/'COMPACT-DECODER-CONTROLS.json')['passed']
    assert f.read(RESULTS/'PREFIX-EXTENSION-CONTROLS.json')['passed']
    reservations=f.read(OUT/'EVALUATION-RESERVATIONS.json')
    assert not reservations['solutions_published'] and len(reservations['families'])==3
    return dict(preserved_baseline=True, frozen_expectations=True, frozen_implementation=True,
        first_successor_action_identities_equal=True, exact_action_content_checks=18,
        qualified_decision_records=54, sft_ready_records=54, tokenized_rows=90,
        evaluation_solutions_published=False)


def seal(verify=False):
    receipt=checks()
    paths=sorted(list(HERE.glob('*.py'))+list(HERE.glob('*.md'))+
        [ROOT/'benchmark/results/phase6/R6_73-REPORT.md',ROOT/'docs/project-overview-r6.73.md',ROOT/'docs/research-log-r6.73.md']+
        [p for p in OUT.rglob('*') if p.is_file() and p.name not in ('PUBLICATION-IDENTITIES.json','VERIFICATION.json')])
    expected={'benchmark/results/phase6/R6_73-REPORT.md','docs/project-overview-r6.73.md','docs/research-log-r6.73.md'}
    for path in paths:
        text=path.read_text(encoding='utf-8')
        assert '\r' not in text and all(line==line.rstrip() for line in text.splitlines()),path
        assert not re.search(r'sk-[A-Za-z0-9]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----',text),path
        if path.suffix=='.json': json.loads(text)
        if path.suffix=='.py': ast.parse(text)
        if path.suffix=='.md':
            for link in re.findall(r'\]\(([^)]+)\)',text):
                if not link.startswith(('https:','#')):
                    target=path.parent/link.split('#')[0]
                    assert target.exists() or (not verify and target.name in ('PUBLICATION-IDENTITIES.json','VERIFICATION.json')),(path,link)
    status=subprocess.check_output(['git','status','--porcelain','--untracked-files=all'],cwd=ROOT,text=True)
    for line in status.splitlines():
        path=line[3:].replace('\\','/')
        assert path in expected or path.startswith(('experiments/contrastive_binding_r6_73/','benchmark/results/phase6/r6_73/')),line
        assert line.startswith('??'), 'Historical/tracked changes are not permitted: '+line
    subprocess.run(['git','diff','--check'],cwd=ROOT,check=True)
    manifest=dict(version='r6.73-publication-1', files={p.relative_to(ROOT).as_posix():dict(sha256=f.sha(p),bytes=p.stat().st_size) for p in paths})
    if verify:
        assert manifest==f.read(OUT/'PUBLICATION-IDENTITIES.json')
        assert f.sha(OUT/'PUBLICATION-IDENTITIES.json')==f.read(OUT/'VERIFICATION.json')['manifest_sha256']
        assert f.read(OUT/'VERIFICATION.json')['checks']==receipt
    else:
        write('PUBLICATION-IDENTITIES.json',manifest)
        write('VERIFICATION.json',dict(passed=True,manifest_sha256=f.sha(OUT/'PUBLICATION-IDENTITIES.json'),
            publication_files=len(paths),checks=receipt,kernel_constructs=26,kernel_basis='Preserved accounting and implementation; no new recount',
            git_diff_check=True,tracked_changes=0,syntax_links_whitespace_credentials=True,
            participant_inference=0,model_loads=0,training=0,optimizer_updates=0,scheduler_updates=0,
            historical_rescoring=0,p6_a04_acceptance=0,p6_a05_access=False,stopped=True))
    print('PASS R6.73 publication integrity, all baseline/freeze identities, record linkage and git diff --check')


if __name__=='__main__':
    if sys.argv[1]=='prepare':
        q.write('SFT-READY.json',ready_records())
        print('PASS 54 fully provenance-linked positive-target SFT records')
    else:
        seal(sys.argv[1]=='verify')
