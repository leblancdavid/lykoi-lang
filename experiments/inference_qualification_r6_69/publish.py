"""Publish partial qualification, retaining frozen sources and failed dispatch."""
import ast
import copy
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys

from qualify import ROOT,HERE,OUT,h,f,baseline,check_freeze,write


def derive():
    check_freeze()
    assert (OUT/'HALT.json').exists()
    process=f.read(OUT/'BASE-PROCESS.json')
    assert process['returncode']==1 and not (OUT/'ADAPTER-PROCESS.json').exists()
    mapping=f.read(OUT/'BASE-UNWRAPPED-MAPPING.json')
    assert mapping['passed']
    # Post-halt CPU diagnosis only, not another model dispatch or frozen worker repair.
    import torch
    from transformers import AutoTokenizer
    spec=importlib.util.spec_from_file_location('r669_analysis_decoder',ROOT/'experiments/structured_generation_r6_68/decoder.py')
    decoder=importlib.util.module_from_spec(spec); spec.loader.exec_module(decoder)
    tokenizer=AutoTokenizer.from_pretrained(f.STORE/'checkpoint',local_files_only=True,trust_remote_code=False)
    mask=decoder.StructuralMask(tokenizer,0,lambda text:f.successor.validate_action(f.successor.c.load(text)))
    config=f.read(OUT/'QUALIFICATION-CONFIGURATION.json')
    original=json.dumps(config['neutral_action'],separators=(',',':'))
    assert not mask.accepts(original)[0]
    source=config['neutral_action']
    ordered=dict(id=source['id'],type=source['type'],deps=source['deps'],node=dict(op=source['node']['op'],expr=source['node']['expr']))
    correct=json.dumps(ordered,separators=(',',':'))
    assert f.successor.c.canonical(f.successor.c.load(original))==f.successor.c.canonical(f.successor.c.load(correct))
    assert mask.accepts(correct)==(True,True)
    alternatives=[]
    for op in ('add','le','eq'):
        for typ in ('Int64','Bool'):
            action=dict(id='selected',type=typ,deps=['probe'],node=dict(op='value',expr={op:[{'const':True},{'ref':'arbitrary_out_of_scope'}]}))
            text=json.dumps(action,separators=(',',':'))
            assert mask.accepts(text)==(True,True)
            assert all(mask.accepts(text[:i])[0] for i in range(len(text)+1))
            alternatives.append(dict(operation=op,type=typ,complete=True,all_prefixes_viable=True,semantic_type_consistency_not_enforced=True))
    negatives=[]
    mutations=[('missing_required',lambda a:a.pop('id')),('incorrect_type',lambda a:a.update(type='Unit')),
               ('deps_type',lambda a:a.update(deps=1)),('missing_node_field',lambda a:a['node'].pop('op')),
               ('wrong_operation',lambda a:a['node'].update(expr={'sub':[{'const':1},{'const':2}]})),
               ('wrong_operand_type',lambda a:a['node'].update(expr={'eq':[{'ref':1},{'const':True}]})),
               ('duplicate_deps',lambda a:a.update(deps=['probe','probe'])),
               ('overflow_literal',lambda a:a['node'].update(expr={'add':[{'const':9223372036854775808},{'const':1}]}))]
    for label,mutator in mutations:
        bad=copy.deepcopy(ordered); mutator(bad)
        assert not mask.accepts(json.dumps(bad,separators=(',',':')))[0]
        negatives.append(dict(name=label,rejected=True))
    for label,text in [('missing_fields','{}'),('markdown','```json\n'+correct+'\n```'),('trailing_content',correct+'garbage')]:
        assert not mask.accepts(text)[0]
        negatives.append(dict(name=label,rejected=True))
    token_checks=[]
    for prefix in ('','{"id":"selected","type":"Bool","deps":["'):
        ids=tokenizer(prefix,add_special_tokens=False)['input_ids']
        mismatches=[token for token,piece in mask.pieces if tokenizer.decode(ids+[token],skip_special_tokens=False)!=prefix+piece]
        assert not mismatches
        token_checks.append(dict(prefix=prefix,admitted_tokens=len(mask.pieces),mismatches=mismatches))
    write('DECODER-CPU-DIAGNOSIS.json',dict(passed=True,post_halt=True,model_calls=0,original_text=original,
          original_key_order=list(source),original_prefix_rejected=True,grammar_order_text=correct,
          grammar_order_structurally_accepted=True,same_action_content=True,
          alternatives=alternatives,invalid_controls=negatives,token_correspondence=token_checks,
          multichar_tokens=sum(len(piece)>1 for _,piece in mask.pieces),decoder_setup_seconds=mask.setup_seconds,
          meaning='Post-halt neutral CPU analysis only. Original frozen worker/configuration not changed. No grammar or application semantics altered.'))
    write('TENSOR-MAPPING-SUMMARY.json',dict(base_identity_repaired=True,base_entries=mapping['entries'],
          underlying_byte_identity_verified=True,shape_dtype_verified=True,quantization_state_verified=True,
          adapter_file_identity_verified=True,adapter_live_tensor_mapping='NOT_REACHED',
          basis='Real unwrapped base manifest compared bijectively to R6.67 PEFT-wrapped historical base manifest using justified names and exact frozen fingerprints',
          evidence='BASE-UNWRAPPED-MAPPING.json'))
    write('FAILURE-ANALYSIS.json',dict(stage='neutral structural controls before any model generate call',
          error='AssertionError at qualify.py:164',root_cause='Sorted-key qualification JSON round trip changed neutral action insertion order; json.dumps preserved deps,id,node,type rather than frozen grammar id,type,deps,node order',
          decoder_grammar_defect_demonstrated=False,qualification_harness_defect=True,model_calls=0,
          same_neutral_action_passes_when_serialized_in_grammar_order=True,diagnostic_solutions_used=False,
          original_failure_preserved=True,frozen_source_repaired_or_retried=False))
    write('MODEL-TIME-TOKEN-MASK.json',dict(status='NOT_REACHED',generation_calls=0,planned_calls=8,
          tracks={track:{probe:'NOT_REACHED' for probe in config['probes']} for track in config['tracks']},
          allowed_token_gpu_mask='NOT_REACHED',eos_generation='NOT_REACHED',prefix_continuation_generation='NOT_REACHED',
          generation_budget_exhaustion='NOT_REACHED',reason='Frozen worker stopped at incorrectly ordered neutral structural control'))
    write('INFERENCE-READINESS.json',dict(ready=False,classification='R6_69_PROTOCOL_HALT',
          components=dict(base_checkpoint_identity='PASS',adapter_file_identity='PASS',tokenizer_identity='PASS',
          base_tensor_mapping='PASS',adapter_live_tensor_mapping='NOT_REACHED',adversarial_verifier='PASS',
          frozen_grammar_cpu_controls='PASS_POST_HALT_DIAGNOSIS',decoder_generation_integration='NOT_REACHED',
          scorer_availability='PASS',diagnostic_identities='PASS',generation_condition_identities='PASS',
          resource_limit_configuration='PASS',resource_limit_generation_enforcement='NOT_REACHED',
          output_paths='PASS',publication_scope='ADDITIVE'),
          configured_limits={k:config[k] for k in ('per_generation_seconds','process_seconds','max_reserved_bytes','minimum_free_bytes')},
          output_directory=str(OUT),comparison_output_directory='requires fresh successor path, never r6_68',
          blockers=['Neutral action serialization in qualification harness is incompatible with fixed-order grammar',
                    'Adapter live base/adapter tensor correspondence not exercised',
                    'Actual model-time mask, EOS, continuation and budget controls not exercised'],
          frozen_abc_comparison_ready=False,comparison_dispatch_authorized=False,training_authorized=False,
          recommendation='Separately authorize corrected neutral-probe serialization and remaining model-time qualification using unchanged grammar/model/adapter/diagnostics; retain R6.68 and R6.69 first failures. No evidence justifies training.'))
    print('PASS terminal analysis; base mapping repaired, readiness false, generation calls0')


def seal(check):
    check_freeze()
    inherited=baseline()
    assert inherited==f.read(OUT/'PREFLIGHT.json')
    paths=sorted(list(HERE.glob('*.py'))+
          [ROOT/'benchmark/results/phase6/R6_69-REPORT.md',ROOT/'benchmark/results/phase6/R6_69-PROTOCOL.md',ROOT/'docs/research-log-r6.69.md']+
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
    allowed=('experiments/inference_qualification_r6_69/','benchmark/results/phase6/r6_69/',
             'benchmark/results/phase6/R6_69-REPORT.md','benchmark/results/phase6/R6_69-PROTOCOL.md','docs/research-log-r6.69.md')
    status=subprocess.check_output(['git','status','--porcelain','--untracked-files=all'],cwd=ROOT,text=True)
    assert all(line[3:].replace('\\','/').startswith(allowed) for line in status.splitlines()),status
    assert not subprocess.check_output(['git','diff','--name-only'],cwd=ROOT,text=True).strip(),'historical tracked modification'
    subprocess.run(['git','diff','--check'],cwd=ROOT,check=True)
    manifest=dict(version='r6.69-publication-1',files={p.relative_to(ROOT).as_posix():dict(sha256=f.sha(p),bytes=p.stat().st_size) for p in paths})
    if check:
        assert manifest==f.read(OUT/'PUBLICATION-IDENTITIES.json')
        assert f.sha(OUT/'PUBLICATION-IDENTITIES.json')==f.read(OUT/'VERIFICATION.json')['manifest_sha256']
    else:
        assert not (OUT/'PUBLICATION-IDENTITIES.json').exists()
        write('PUBLICATION-IDENTITIES.json',manifest)
        write('VERIFICATION.json',dict(passed=True,manifest_sha256=f.sha(OUT/'PUBLICATION-IDENTITIES.json'),
              r6_68_publication=inherited['r6_68_publication'],preserved_full_baseline='PASS',adapter_file_hashes='PASS',
              frozen_source_and_inputs='PASS',json_python_links_whitespace_credentials='PASS',additive_scope='PASS',git_diff_check='PASS',
              kernel_constructs=26,production_changes=0,experimental_semantic_changes=0,training_calls=0,
              optimizer_updates=0,scheduler_updates=0,model_generation_calls=0,historical_rescoring=False,
              dataset_expansion=0,installations=0,P6_A04_acceptance=0,P6_A05_access=False))
    print('PASS R6.69 publication integrity and historical preservation')


if __name__=='__main__':
    if sys.argv[1]=='derive': derive()
    else: seal(sys.argv[1]=='check')
