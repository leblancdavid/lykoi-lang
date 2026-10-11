"""Finish read-only independent controls; publish actual gaps without repair."""
import ast
import importlib
import importlib.metadata
import inspect
import os
from pathlib import Path
import sys
from integration import *


def main():
    assert Path(sys.executable).resolve() == PYTHON.resolve() and sys.version_info[:3] == (3,12,11)
    assert os.environ.get('CUDA_VISIBLE_DEVICES') == ''
    frozen_check()
    write('FINAL-AUDIT-FREEZE.json',dict(stage='AFTER_TWO_PRESERVED_CONTROL_HALTS_BEFORE_INDEPENDENT_COMPLETION',
        source_sha256=sha(Path(__file__)),frozen_configuration_modified=False,readiness=False))
    versions = {}
    for name in ('torch','transformers','peft','trl','accelerate','bitsandbytes','datasets','tokenizers','safetensors'):
        importlib.import_module(name)
        versions[name] = importlib.metadata.version(name)
    assert versions == read(ROOT/'benchmark/results/phase6/r6_52/ENVIRONMENT.json')['packages']
    import torch
    from transformers import AutoTokenizer, GenerationConfig
    from transformers.optimization import _get_linear_schedule_with_warmup_lr_lambda as factor
    cfg = read(OUT/'TRAINING-CONFIGURATION.json')['configuration']
    inspect.signature(torch.optim.AdamW).bind([],**cfg['optimizer_configuration']['kwargs'])
    tokenizer = AutoTokenizer.from_pretrained(STORE/'checkpoint',local_files_only=True,trust_remote_code=False)
    evaluation = read(OUT/'EVALUATION.json')
    gold, decoder = [], []
    seen = set()
    for path,digest in read(OUT/'EVALUATION-FREEZE.json')['files'].items():
        assert sha(ROOT/path)==digest
    generation = GenerationConfig(**{k:v for k,v in cfg['decoding_settings'].items() if k not in ('seed','per_generation_timeout_seconds')})
    assert generation.max_new_tokens == 64 and not generation.do_sample and not generation.use_cache
    for row in evaluation['records']:
        result = score(serialize(row['target']),row)
        gold.append(dict(id=row['id'],partition=row['partition'],scores=result))
        language = CompletionLanguage(row['scope'])
        assert serialize(row['target']) in language.terminals
        key = identity(language.texts)
        if key not in seen:
            seen.add(key)
            maximum, observations = 0, 0
            for text in language.texts:
                ids = tokenizer.encode(text,add_special_tokens=False)
                maximum = max(maximum,len(ids)+1)
                assert tokenizer.decode(ids,skip_special_tokens=False)==text
                for at in range(len(ids)+1):
                    assert language.accepts(tokenizer.decode(ids[:at],skip_special_tokens=False))[0]
                    observations += 1
                assert language.allowed(tokenizer,ids,[]) == [tokenizer.eos_token_id]
            assert maximum <= 64
            decoder.append(dict(language_identity=key,decisions=len(language.texts),prefix_observations=observations,
                maximum_tokens_including_eos=maximum,terminal_eos_only=True,
                qualifier='Syntactic/tokenizer control only; reserved scopes fail semantic identity validation.'))
    reserved = [g for g in gold if g['partition']=='evaluation_exploratory']
    exposed = [g for g in gold if g['partition']=='training_calibration']
    assert len(reserved)==24 and all(g['scores']['category']=='semantic_rejection' and g['scores']['code']=='REFERENCE' for g in reserved)
    assert len(exposed)==6 and all(g['scores']['accepted'] for g in exposed)
    contrasts = []
    for row in q.rows():
        for negative in row['negatives']:
            result = score(serialize(negative['decision']),row)
            assert not result['accepted']
            contrasts.append(dict(id=row['id'],input=negative['decision'],scores=result))
    row = evaluation['records'][0]
    text = serialize(row['target'])
    malformed = [text[:-1],text+'x',text.replace('"op":"le"','"op":"le","op":"eq"')]
    assert all(not score(candidate,row)['strict_decision_validity'] for candidate in malformed)
    write('DECODER-SCORER-QUALIFICATION.json',dict(mechanism_controls_passed=True,
        adversarial_controls=read(OUT/'ADVERSARIAL-VERIFICATION.json')['counts'],contrast_controls=contrasts,
        compact_decoder_controls='COMPACT-DECODER-CONTROLS.json',evaluation_gold=gold,evaluation_languages=decoder,
        malformed_budget_suffix_controls=3,answer_filter=False,live_model_generation='NOT_RUN',
        reserved_evaluation_ready=False,reserved_gold_accepted=0,reserved_denominator=24,
        calibration_gold_accepted=6,calibration_denominator=6,budget='64 includes terminal EOS; incomplete output rejects without repair.'))
    runtime = load('r674_resource_audit','experiments/contrastive_preflight_r6_74/runtime.py')
    resource = callable(getattr(runtime.c,'rss',None))
    assert not resource
    worker = load('r674_static_worker','experiments/contrastive_preflight_r6_74/worker.py')
    source = (OUT/'EFFECTIVE-WORKER.py.txt').read_text(encoding='utf-8')
    assert source==worker.effective_source()
    compile(source,'r674-worker','exec')
    for p in HERE.glob('*.py'):
        ast.parse(p.read_text(encoding='utf-8'))
    write('EXECUTABLE-INTEGRATION-AUDIT.json',dict(compile_pass=True,runtime_import_pass=True,
        required_resource_provider_pass=False,
        defect='runtime.c and dispatch.c bind R6.18 composition, which has no rss callable. Both inherited worker memory() and launcher require c.rss; frozen RSS enforcement is unavailable.',
        defects_not_repaired=True,model_loads=0,optimizer_instances=0,scheduler_instances=0))
    native = []
    for row in evaluation['records']:
        try:
            assembly.check_before(row['scope'])
            native.append(dict(id=row['id'],passed=True))
        except c.Diagnostic as exc:
            native.append(dict(id=row['id'],passed=False,diagnostic=exc.data))
    write('EVALUATION-READINESS.json',dict(ready=False,expectations_frozen=True,independent=False,
        reserved_cases=24,underlying_requirements=12,exposed_calibration_cases=6,
        reserved_gold_acceptance=0,calibration_gold_acceptance=6,native_scope_checks=native,
        blocker='Reserved scope names contain hyphens (R674E01-boundary-negation1R1 etc.), violating unchanged semantic reference-name grammar.',
        functional_reserved='NOT_REACHED; scopes reject before reconstruction/VM execution',
        no_training_leakage='Training dataset and exact source ledger frozen before evaluation realization; no E-family row in training.',
        withholding='Coordinator-only exploratory reservation, not independently withheld.'))
    sampling = read(OUT/'SAMPLING.json')
    assert [p['episode_id'] for p in sampling['sequence']] == sampling['cycle']*4
    for i,p in enumerate(sampling['sequence']):
        assert p['presentation']==i+1 and p['epoch']==i//54+1 and p['optimizer_step']==i//4+1 and p['microbatch_in_step']==i%4+1
    schedule = read(OUT/'SCHEDULER-SIMULATION.json')['sequence']
    for i,row in enumerate(schedule,1):
        assert row['lr_used_by_update']==1e-4*factor(i-1,num_warmup_steps=6,num_training_steps=54)
        assert row['lr_after_scheduler_step']==1e-4*factor(i,num_warmup_steps=6,num_training_steps=54)
    assert len(sampling['sequence'])==216 and len(schedule)==54
    assert not ARTIFACTS.exists() and not (OUT/'execution').exists() and not torch.cuda.is_initialized()
    write('CPU-QUALIFICATION.json',dict(passed=False,classification='R6_74_CONFIGURATION_GAP',
        preserved_halting_gates=['HALT-qualify.json','HALT-remaining-controls.json'],frozen_sources_repaired=False,
        remaining_independent_controls_completed=True,packages=versions,python=sys.version,interpreter=sys.executable,
        cpu_only=True,cuda_initialized=False,eligible_records=54,direct=18,corrective=36,
        sampling_presentations=216,optimizer_schedule_entries=54,sampling_identity=identity(sampling),
        loss_normalization_identity=identity(read(OUT/'LOSS-POLICY.json')),configuration_identity=identity(cfg),
        evaluation_cases=24,exposed_calibration_cases=6,model_loads=0,participant_inference=0,training=0,
        backward_calls=0,optimizer_instances=0,scheduler_instances=0,optimizer_updates=0,scheduler_updates=0,
        output_paths_absent=True,limits=cfg['limits'],historical_rescoring=0,p6_a04_acceptance=0,p6_a05_access=False))
    write('TRAINING-READINESS.json',dict(ready=False,classification='R6_74_CONFIGURATION_GAP',
        qualified_direct=18,qualified_corrective=36,sampling_identity=identity(sampling),
        loss_normalization_identity=identity(read(OUT/'LOSS-POLICY.json')),
        configuration_identity=identity(cfg),evaluation_ready=False,gpu_attempt_justified=False,
        blockers=['Frozen loss-normalization negative control uses four equal-length targets and fails.',
                  'Frozen reserved evaluation scope names violate unchanged reference-name grammar (24/24 reject).',
                  'Execution context lacks required c.rss resource-monitor callable.'],
        recommended_next_step='Separately authorize additive successor CPU integration qualification for these three mechanical defects; retain all R6.74 freezes/halts. No GPU dispatch.',
        model_learning='NOT_MEASURED',kernel_constructs=26,stopped=True))
    print('PASS independent audit completion: CONFIGURATION_GAP; no frozen repair or GPU dispatch')


if __name__ == '__main__':
    main()
