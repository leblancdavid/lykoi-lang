"""Read-only partial evidence analysis and additive publication verification."""
import ast
from collections import Counter
import json
import re
import subprocess
import sys
from run import ROOT, HERE, OUT, f, baseline, check_freeze, write


def derive():
    check_freeze()
    rows = f.read(OUT/'DIAGNOSTICS.json')['records']
    evidence, summaries = [], {}
    for track in ('base','adapter'):
        entries = []
        for row in rows:
            path = OUT/(track.upper()+'-C-'+row['episode_id']+'.json')
            if not path.exists(): continue
            entry = f.read(path)
            s = entry['scores']
            extra = dict(operand_selection=None,operand_order=None,literal_reference_kind=None)
            labels = []
            if s['schema_valid']:
                gold=f.successor.c.load(row['completion'][0]['content'])
                action=f.successor.c.load(entry['output'])
                args=next(iter(action['node']['expr'].values()))
                expected=next(iter(gold['node']['expr'].values()))
                canon=lambda a:f.successor.c.canonical(a).decode()
                extra=dict(operand_selection=sorted(map(canon,args))==sorted(map(canon,expected)),
                           operand_order=args==expected and canon(args)==canon(expected),
                           literal_reference_kind=[list(a) for a in args]==[list(a) for a in expected])
                for key,label in [('operation_correct','operation_selection'),('operands_correct','ordered_binding'),('dependencies_correct','dependency_construction'),('result_type_correct','result_type')]:
                    if not s[key]: labels.append(label)
                if not extra['operand_selection']: labels.append('operand_selection')
                if extra['operand_selection'] and not extra['operand_order']: labels.append('operand_order_only')
                if not extra['literal_reference_kind']: labels.append('literal_reference_selection')
                env={p['name']:p['type'] for p in row['before']['params']}
                env.update({a['id']:a['type'] for a in row['before']['steps']})
                types=[]
                for arg in args:
                    try: types.append(f.successor.c.expression(arg,env,'$/diagnostic')[0])
                    except f.successor.c.Diagnostic: types.append('INVALID_REFERENCE')
                extra['actual_operand_types']=types
                if s.get('error',{}).get('code')=='TYPE': labels.append('type_confusion')
                requested={a['ref'] for a in expected if 'ref' in a}
                actual_refs={a['ref'] for a in args if 'ref' in a}
                if any(a in env and a not in requested for a in actual_refs): labels.append('irrelevant_scope_reference')
            else:
                labels.append('serialization_or_termination')
            if entry['truncated']: labels.append('budget_exhaustion')
            if s['classification']=='ASSEMBLY_FAILURE': labels.append('assembly_rejection')
            if s['stage']=='complete' and not s['behavioral_acceptance']: labels.append('functional_mismatch')
            entry.update(binding_diagnostics=extra,error_labels=labels)
            entries.append(entry)
        valid=[r for r in entries if r['scores']['schema_valid']]
        summaries[track]=dict(completed=len(entries),schema_valid=len(valid),dimensions={k:sum(r['scores'][k] for r in entries) for k in f.successor.DIMENSIONS},
             schema_conditional={k:dict(numerator=sum(r['scores'][k] for r in valid),denominator=len(valid)) for k in f.successor.DIMENSIONS[2:]},
             binding_dimensions={k:dict(numerator=sum(bool(r['binding_diagnostics'][k]) for r in valid),denominator=len(valid)) for k in ('operand_selection','operand_order','literal_reference_kind')},
             per_operation={op:dict(completed=sum(next(iter(f.successor.c.load(row['completion'][0]['content'])['node']['expr']))==op and any(e['episode_id']==row['episode_id'] for e in entries) for row in rows),correct=sum(r['scores']['operation_correct'] for r in valid if next(iter(f.successor.c.load(next(row for row in rows if row['episode_id']==r['episode_id'])['completion'][0]['content'])['node']['expr']))==op)) for op in ('add','le','eq')},
             error_labels=dict(Counter(label for e in entries for label in e['error_labels'])),
             timing={key:sum(r[key] for r in entries) for key in ('inference_seconds','model_forward_seconds','model_forward_calls','constraint_seconds','decoder_setup_seconds','generation_other_seconds','scoring_seconds','output_tokens')})
        evidence.extend(entries)
    assert len(evidence)==10 and (OUT/'DIAGNOSTIC-HALT.json').exists()
    write('SEMANTIC-ANALYSIS.json',dict(summary=summaries,records=evidence,authoritative_scorer_unchanged=True,acceptance_unchanged=True,repair=False,paired_differences='NOT_REACHED',failed_S11='Incomplete prefix unscored; duplicate dependencies observed only as runtime/termination evidence',semantic_before_schema='NOT_REACHED',functional_after_assembly_failure='NOT_REACHED'))
    write('ASSESSMENT.json',dict(classification='R6_72_PROTOCOL_HALT',diagnostic_completed=10,diagnostic_attempted=11,planned=24,base_accepted=0,adapter='NOT_REACHED',neutral_timing_calls=4,training=0,paired_semantic_advantage='NOT_REACHED',stopped=True,summary=summaries))
    print(json.dumps(dict(summary=summaries,raw=[dict(id=r['episode_id'],output=r['output'],scores=r['scores'],bindings=r['binding_diagnostics']) for r in evidence]),indent=2))


def coverage():
    records=[]
    for i in range(1,11):
        eid='D%02d'%i
        folder=ROOT/'benchmark/results/phase6/r6_63/episodes'/eid
        records.append(dict(episode=eid,source=f.read(folder/'SOURCE.json'),before=f.read(folder/'BEFORE.json')))
    spec=__import__('importlib.util',fromlist=['util']).spec_from_file_location('r672_expert',ROOT/'experiments/incremental_data_r6_63/expert.py')
    expert=__import__('importlib.util',fromlist=['util']).module_from_spec(spec)
    spec.loader.exec_module(expert)
    for r in records: r['action']=expert.actions()[r['episode']]
    write('TRAINING-COVERAGE-INVENTORY.json',dict(records=records,operation_counts=dict(Counter(next(iter(r['action']['node']['expr'])) for r in records)),historical_rescoring=False,dataset_expansion=0))


def seal(check=False):
    check_freeze()
    assert baseline()==f.read(OUT/'BASELINE-IDENTITY-VERIFICATION.json')
    paths=sorted(list(HERE.glob('*.py'))+[ROOT/'benchmark/results/phase6/R6_72-PROTOCOL.md',ROOT/'benchmark/results/phase6/R6_72-REPORT.md',ROOT/'docs/research-log-r6.72.md']+[p for p in OUT.iterdir() if p.name not in ('PUBLICATION-IDENTITIES.json','VERIFICATION.json')])
    for p in paths:
        text=p.read_text(encoding='utf-8')
        assert '\r' not in text and all(line==line.rstrip() for line in text.splitlines()),p
        assert not re.search(r'sk-[A-Za-z0-9]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----',text),p
        if p.suffix=='.json': json.loads(text)
        if p.suffix=='.py' or p.name=='EFFECTIVE-WORKER.py.txt': ast.parse(text)
        if p.suffix=='.md':
            for link in re.findall(r'\]\(([^)]+)\)',text):
                if not link.startswith(('https:','#')):
                    target=p.parent/link.split('#')[0]
                    assert target.exists() or (not check and target.name in ('PUBLICATION-IDENTITIES.json','VERIFICATION.json')),(p,link)
    status=subprocess.check_output(['git','status','--porcelain','--untracked-files=all'],cwd=ROOT,text=True)
    allowed=('experiments/semantic_binding_r6_72/','benchmark/results/phase6/r6_72/','benchmark/results/phase6/R6_72-','docs/research-log-r6.72.md','docs/project-overview.md','docs/research-log.md','docs/decisions.md')
    assert all(line[3:].replace('\\','/').startswith(allowed) for line in status.splitlines()),status
    subprocess.run(['git','diff','--check'],cwd=ROOT,check=True)
    manifest=dict(version='r6.72-publication-1',files={p.relative_to(ROOT).as_posix():dict(sha256=f.sha(p),bytes=p.stat().st_size) for p in paths})
    if check:
        assert manifest==f.read(OUT/'PUBLICATION-IDENTITIES.json')
        assert f.sha(OUT/'PUBLICATION-IDENTITIES.json')==f.read(OUT/'VERIFICATION.json')['manifest_sha256']
    else:
        write('PUBLICATION-IDENTITIES.json',manifest)
        write('VERIFICATION.json',dict(passed=True,manifest_sha256=f.sha(OUT/'PUBLICATION-IDENTITIES.json'),publication_files=len(paths),baseline_preserved=True,kernel_constructs=26,git_diff_check=True,syntax_links_credentials=True,training=0,dataset_expansion=0,historical_rescoring=0,p6_a04_acceptance=0,p6_a05_access=False,live_post_diagnostic_tensor_check='NOT_REACHED due halted worker',neutral_before_after_tensor_checks=True))
    print('PASS R6.72 publication integrity and historical identity verification')


if __name__=='__main__':
    {'derive':derive,'coverage':coverage,'seal':seal,'verify':lambda:seal(True)}[sys.argv[1]]()
