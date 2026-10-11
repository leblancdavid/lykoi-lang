"""Read-only analysis of this successor's evidence and publication verification."""
import ast
from collections import Counter
import json
import re
import subprocess
import sys
from run import ROOT, HERE, OUT, f, h, baseline, check_freeze, write


def derive():
    check_freeze()
    records = [f.read(OUT / (track.upper()+'-RESULTS.json'))['records'] for track in ('base','adapter')]
    entries = records[0] + records[1]
    assert len(entries) == 54 and not (OUT / 'HALT.json').exists()
    expected = [(track,condition,'N%02d'%i) for track in ('base','adapter') for condition in 'ABC' for i in range(1,10)]
    assert [(r['track'],r['condition'],r['episode_id']) for r in entries] == expected
    summaries, failures = {}, []
    for track in ('base','adapter'):
        summaries[track] = {}
        for condition in 'ABC':
            group = [r for r in entries if r['track']==track and r['condition']==condition]
            schema = [r for r in group if r['scores']['schema_valid']]
            summaries[track][condition] = dict(completed=len(group),dimensions={k:sum(r['scores'][k] for r in group) for k in f.successor.DIMENSIONS},accepted=sum(r['scores']['accepted'] for r in group),schema_conditional={k:dict(numerator=sum(r['scores'][k] for r in schema),denominator=len(schema)) for k in f.successor.DIMENSIONS[2:]},eos=sum(r['eos_terminated'] for r in group),truncated=sum(r['truncated'] for r in group),markdown=sum('```' in r['output'] for r in group),tokens=sum(r['output_tokens'] for r in group),inference_seconds=sum(r['inference_seconds'] for r in group),mask_seconds=sum(r['constraint_seconds'] for r in group),setup_seconds=sum(r['decoder_setup_seconds'] for r in group),scoring_seconds=sum(r['scoring_seconds'] for r in group),validation_seconds=sum(r.get('validation_seconds',0) for r in group),assembly_seconds=sum(r.get('assembly_seconds',0) for r in group),peak_allocated_bytes=max(r['peak_allocated_bytes'] for r in group),peak_reserved_bytes=max(r['peak_reserved_bytes'] for r in group),runtime_failures=sum(r['runtime_error'] is not None for r in group))
    for r in entries:
        s = r['scores']
        categories = []
        if '```' in r['output']: categories.append('Markdown formatting')
        if not s['strict_serialization']: categories.append('Invalid JSON')
        if s['strict_serialization'] and not s['schema_valid']: categories.append('Schema mismatch')
        if s['schema_valid']:
            for key,label in [('operation_correct','Wrong operation'),('operands_correct','Wrong operands'),('result_type_correct','Wrong result type'),('dependencies_correct','Wrong dependencies')]:
                if not s[key]: categories.append(label)
            if s['classification']=='ASSEMBLY_FAILURE': categories.append('Assembly rejection')
            if s['stage']=='complete' and not s['behavioral_acceptance']: categories.append('Functional mismatch')
        if r['truncated'] or not r['eos_terminated']: categories.append('Truncation or termination')
        if r['runtime_error']: categories.append('Runtime failure')
        failures.append(dict(track=r['track'],condition=r['condition'],episode_id=r['episode_id'],accepted=s['accepted'],categories=categories,first_failure=categories[0] if categories else None,scorer_first_failure=dict(classification=s['classification'],stage=s['stage'],error=s.get('error')),raw_evidence=r['track'].upper()+'-'+r['condition']+'-'+r['episode_id']+'-RAW.json'))
    write('STRUCTURAL-SEMANTIC-SCORING.json',dict(dimensions=list(f.successor.DIMENSIONS),records=[dict(track=r['track'],condition=r['condition'],episode_id=r['episode_id'],scores=r['scores']) for r in entries],unchanged_scorer=True,no_repair=True,expected_source='Frozen R6.68 expert completion and independently frozen fixture values'))
    write('BASE-VERSUS-ADAPTER.json',dict(summary=summaries,paired_differences={c:{k:summaries['adapter'][c]['dimensions'][k]-summaries['base'][c]['dimensions'][k] for k in f.successor.DIMENSIONS} for c in 'ABC'},matched_schema_C=[dict(episode_id=a['episode_id'],base=b['scores'],adapter=a['scores']) for b,a in zip(records[0][-9:],records[1][-9:]) if b['scores']['schema_valid'] and a['scores']['schema_valid']]))
    write('FAILURE-ANALYSIS.json',dict(records=failures,multilabel_counts=dict(Counter(label for r in failures for label in r['categories'])),unreached_semantic_dimensions='False scorer flags before schema/assembly are NOT_REACHED, not evidence of a specific semantic decision',first_failures_preserved=True))
    write('DECODER-INFERENCE-MEASUREMENTS.json',dict(summary=summaries,records=[{k:v for k,v in r.items() if k not in ('output','output_token_ids','scores','allowed_counts')} for r in entries],limitations=['Adapter outer PEFT forward hook is bypassed by generate; model_forward_seconds=0 is unmeasured, not zero model cost. generation_other_seconds on adapter includes actual model forward time.','Mask time is measured enforcement cost including synchronization, not a causal matched-output latency estimate. Setup is outside inference wall time.','Assembly timing is a separate diagnostic attempt, possibly rejected; successful deterministic repeated assembly and functional evaluation are included in scorer time.','VRAM maxima reset per generation; no uninterrupted whole-worker peak or numeric minimum-free time series was recorded.']))
    for track, rows in zip(('base','adapter'), records):
        write('RAW-'+track.upper()+'-OUTPUTS.json',dict(records=[{k:r[k] for k in ('track','condition','episode_id','prompt_identity','output','output_token_ids','output_tokens','eos_terminated','truncated')} for r in rows]))
    classification = 'R6_71_STRUCTURED_GENERATION_ONLY'
    write('ASSESSMENT.json',dict(classification=classification,completed_generations=54,semantic_learning_observed=False,usable_incremental_construction=dict(base=1,adapter=0,denominator_each=27),adapter_semantic_advantage=False,decoder_structural_improvement=True,summary=summaries,independent_generalization=False,language_superiority=False,stopped=True))
    matched = [(b,a) for b,a in zip(records[0][-9:],records[1][-9:]) if b['scores']['schema_valid'] and a['scores']['schema_valid']]
    print(json.dumps(dict(classification=classification,matched_schema_C={track:{k:sum(pair[i]['scores'][k] for pair in matched) for k in f.successor.DIMENSIONS} for i,track in enumerate(('base','adapter'))},failures=dict(Counter(label for r in failures for label in r['categories'])),C_outputs=[dict(track=r['track'],episode_id=r['episode_id'],output=r['output'],classification=r['scores']['classification']) for r in entries if r['condition']=='C']),indent=2))


def seal(check=False):
    check_freeze()
    receipt = baseline()
    assert receipt == f.read(OUT / 'BASELINE-IDENTITY-VERIFICATION.json')
    paths = sorted(list(HERE.glob('*.py'))+[ROOT/'benchmark/results/phase6/R6_71-REPORT.md',ROOT/'benchmark/results/phase6/R6_71-PROTOCOL.md',ROOT/'docs/research-log-r6.71.md']+[p for p in OUT.iterdir() if p.name not in ('PUBLICATION-IDENTITIES.json','VERIFICATION.json')])
    for p in paths:
        text = p.read_text(encoding='utf-8')
        assert '\r' not in text and all(line==line.rstrip() for line in text.splitlines()), p
        assert not re.search(r'sk-[A-Za-z0-9]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----',text), p
        if p.suffix=='.json': json.loads(text)
        if p.suffix=='.py' or p.name=='EFFECTIVE-WORKER.py.txt': ast.parse(text)
        if p.suffix=='.md':
            for link in re.findall(r'\]\(([^)]+)\)',text):
                if not link.startswith(('https:','#')):
                    target=(p.parent/link.split('#')[0]).resolve()
                    assert target.exists() or (not check and target.name in ('PUBLICATION-IDENTITIES.json','VERIFICATION.json')), (p,link)
    allowed=('experiments/semantic_learning_r6_71/','benchmark/results/phase6/r6_71/','benchmark/results/phase6/R6_71-','docs/research-log-r6.71.md')
    status=subprocess.check_output(['git','status','--porcelain','--untracked-files=all'],cwd=ROOT,text=True)
    assert all(line[3:].replace('\\','/').startswith(allowed) for line in status.splitlines()), status
    assert not subprocess.check_output(['git','diff','--name-only'],cwd=ROOT,text=True).strip()
    subprocess.run(['git','diff','--check'],cwd=ROOT,check=True)
    manifest=dict(version='r6.71-publication-1',files={p.relative_to(ROOT).as_posix():dict(sha256=f.sha(p),bytes=p.stat().st_size) for p in paths})
    if check:
        assert manifest == f.read(OUT/'PUBLICATION-IDENTITIES.json')
        assert f.sha(OUT/'PUBLICATION-IDENTITIES.json') == f.read(OUT/'VERIFICATION.json')['manifest_sha256']
    else:
        write('PUBLICATION-IDENTITIES.json',manifest)
        write('VERIFICATION.json',dict(passed=True,manifest_sha256=f.sha(OUT/'PUBLICATION-IDENTITIES.json'),publication_files=len(paths),baseline=receipt,additive_scope=True,tracked_changes=0,git_diff_check=True,credential_pattern_check=True,syntax_and_links=True,kernel_constructs=26,historical_rescoring=0,training=0,p6_a04_acceptance=0,p6_a05_access=False))
    print('PASS R6.71 publication integrity and inherited preservation')


if __name__=='__main__':
    {'derive':derive,'seal':seal,'verify':lambda:seal(True)}[sys.argv[1]]()
