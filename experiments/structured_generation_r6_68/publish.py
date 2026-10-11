"""Publish the first terminal halt; never dispatch or rescore historical outputs."""
import ast
import json
from pathlib import Path
import re
import subprocess
import sys

from run import ROOT, HERE, OUT, f, audit, check_freeze, write


def derive():
    check_freeze()
    assert (OUT/'HALT.json').exists()
    process=f.read(OUT/'BASE-PROCESS.json')
    assert process['returncode']==1
    assert not list(OUT.glob('BASE-A-*.json')) and not (OUT/'ADAPTER-PROCESS.json').exists()
    rows=f.read(OUT/'DIAGNOSTICS.json')['records']
    old=f.read(ROOT/'benchmark/results/phase6/r6_67/INITIAL-PARAMETERS.json')['base']
    keys=list(old)
    # Static evidence only. The failed in-memory manifest was not saved.
    prefixed=[k for k in keys if 'base_model.model.' in k]
    assert len(prefixed)==len(keys)
    write('FAILURE-ANALYSIS.json',dict(first_failure='runtime/inference failure: pre-generation manifest assertion',
          stage='base load and verification before A/N01',error='AssertionError',generation_calls=0,
          static_cause='R6.67 training INITIAL-PARAMETERS records PEFT-wrapped module names (base_model.model.*, q/v base_layer); R6.68 base branch records unwrapped model names. Exact dictionary equality is incompatible.',
          historical_manifest_entries=len(keys),peft_namespace_entries=len(prefixed),example_keys=keys[:8],
          evidence_paths=['experiments/structured_generation_r6_68/run.py:158-174','benchmark/results/phase6/r6_66/EFFECTIVE-WORKER.py.txt:95-109'],
          limitation='Failed current in-memory manifest was not persisted; tensor-content equality cannot be reconstructed. Static naming incompatibility suffices to reject equality, not to claim any tensor changed.',
          downstream='All54 generation/scoring cells NOT_REACHED; no Markdown/JSON/schema/semantic output failures observed',
          corrected_or_retried=False,qualified_cpu_failure_preserved=True))
    scores=[]
    for track in ('base','adapter'):
        outputs=[]
        for condition in 'ABC':
            for row in rows:
                outputs.append(dict(track=track,condition=condition,episode_id=row['episode_id'],status='NOT_REACHED',
                    raw_output=None,output_token_ids=None,generated_tokens=None,inference_seconds=None,
                    peak_allocated_bytes=None,peak_reserved_bytes=None,constraint_seconds=None))
                scores.append(dict(track=track,condition=condition,episode_id=row['episode_id'],stage='NOT_REACHED',
                    dimensions={d:None for d in f.successor.DIMENSIONS},accepted=None,first_failure='run-level pre-generation verifier assertion'))
        write('RAW-'+track.upper()+'-OUTPUTS.json',dict(generated_records=0,planned_records=27,records=outputs,
              interpretation='Explicit absence records, not generated responses or zero-score observations'))
    write('STRUCTURAL-SEMANTIC-SCORING.json',dict(records=scores,scorer_sha256=f.sha(ROOT/'experiments/incremental_scorer_r6_65/scorer.py'),
          scored_generated_actions=0,historical_rescoring=False,gold_actions_accepted=9,
          result='All six paired cells NOT_REACHED; no scored denominator and no success-rate claim'))
    interface=f.read(OUT/'GENERATION-INTERFACE.json')
    write('OVERHEAD-MEASUREMENTS.json',dict(base_dispatch_wall_seconds=process['seconds'],
          base_load_attempts=1,adapter_load_attempts=0,generation_calls=0,
          cpu_qualification_decoder_setup_seconds=interface['setup_seconds'],
          inference_seconds=None,model_forward_seconds=None,decoder_enforcement_seconds=None,
          peak_allocated_vram_bytes=None,peak_reserved_vram_bytes=None,validation_seconds=None,assembly_seconds=None,
          interpretation='CPU vocabulary/grammar setup only; process time includes failed load/manifest check and is not model inference time. Worker failed before generation/VRAM/timing receipts were written.',
          runtime_errors=[dict(stage='pre-generation identity assertion',type='AssertionError',returncode=1)],provider_calls=0))
    write('ASSESSMENT.json',dict(classification='R6_68_PROTOCOL_HALT',
          formatting_improvement='NOT_MEASURED',constrained_structural_improvement='NOT_MEASURED',
          adapter_semantic_advantage='NOT_MEASURED',operation_transfer='NOT_MEASURED',
          structural_weakness_hidden_by_decoder='NOT_MEASURED',usable_incremental_construction='NOT_DEMONSTRATED_IN_R6_68',
          historical_r6_67_acceptance=dict(base=0,adapter=0,denominator=13,preserved=True),
          recommendation='Retain typed JSON actions and independent semantic validation. Qualify namespace-aware read-only identity checks and actual token masking before a separately authorized fresh bounded inference comparison; no evidence justifies further training.',
          independent_generalization=False,stopped=True,training_calls=0,optimizer_updates=0,scheduler_updates=0))
    print('PASS terminal halt analysis: generated/scored actions0; historical outputs not rescored')


def seal(check):
    check_freeze()
    baseline=audit()
    assert baseline==f.read(OUT/'PREFLIGHT.json')
    paths=sorted(list(HERE.glob('*.py'))+
          [ROOT/'benchmark/results/phase6/R6_68-REPORT.md',ROOT/'benchmark/results/phase6/R6_68-PROTOCOL.md',ROOT/'docs/research-log-r6.68.md']+
          [p for p in OUT.iterdir() if p.name not in ('PUBLICATION-IDENTITIES.json','VERIFICATION.json')])
    for path in paths:
        text=path.read_text(encoding='utf-8')
        assert '\r' not in text and all(line==line.rstrip() for line in text.splitlines()),path
        if path.suffix=='.json': json.loads(text)
        if path.suffix=='.py': ast.parse(text)
        assert not re.search(r'sk-[A-Za-z0-9]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----',text),path
        if path.suffix=='.md':
            for link in re.findall(r'\]\(([^)]+)\)',text):
                if not link.startswith(('https:','#')):
                    target=(path.parent/link.split('#')[0]).resolve()
                    pending=not check and target in (OUT/'PUBLICATION-IDENTITIES.json',OUT/'VERIFICATION.json')
                    assert target.exists() or pending,(path,link)
    status=subprocess.check_output(['git','status','--porcelain','--untracked-files=all'],cwd=ROOT,text=True)
    allowed=('experiments/structured_generation_r6_68/','benchmark/results/phase6/r6_68/',
             'benchmark/results/phase6/R6_68-REPORT.md','benchmark/results/phase6/R6_68-PROTOCOL.md','docs/research-log-r6.68.md')
    assert all(line[3:].replace('\\','/').startswith(allowed) for line in status.splitlines()),status
    assert not subprocess.check_output(['git','diff','--name-only'],cwd=ROOT,text=True).strip(),'historical tracked modification'
    subprocess.run(['git','diff','--check'],cwd=ROOT,check=True)
    manifest=dict(version='r6.68-publication-1',files={p.relative_to(ROOT).as_posix():dict(sha256=f.sha(p),bytes=p.stat().st_size) for p in paths})
    if check:
        assert manifest==f.read(OUT/'PUBLICATION-IDENTITIES.json')
        assert f.sha(OUT/'PUBLICATION-IDENTITIES.json')==f.read(OUT/'VERIFICATION.json')['manifest_sha256']
    else:
        assert not (OUT/'PUBLICATION-IDENTITIES.json').exists()
        write('PUBLICATION-IDENTITIES.json',manifest)
        write('VERIFICATION.json',dict(passed=True,manifest_sha256=f.sha(OUT/'PUBLICATION-IDENTITIES.json'),
              historical_publications=baseline['publications'],full_baseline_audit='PASS',adapter_files='PASS',
              frozen_source_inputs='PASS',json_python_links_whitespace_credentials='PASS',additive_scope='PASS',git_diff_check='PASS',
              kernel_constructs=26,kernel_basis='preserved R6.66 accounting, not a recount',production_changes=0,
              experimental_semantic_changes=0,training_calls=0,optimizer_updates=0,scheduler_updates=0,
              generated_actions=0,historical_rescoring=False,dataset_expansion_for_training=0,installations=0,
              P6_A04_acceptance=0,P6_A05_access=False))
    print('PASS R6.68 publication integrity and preservation')


if __name__=='__main__':
    if sys.argv[1]=='derive': derive()
    else: seal(sys.argv[1]=='check')
