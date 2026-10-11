"""CPU-only, exclusive staged preflight. No optimizer/scheduler/model instances."""
import copy
import importlib
import importlib.metadata
import inspect
import json
import os
from pathlib import Path
import random
import subprocess
import sys
import time
import traceback
from integration import *

ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', CUDA_VISIBLE_DEVICES='',
           HF_HUB_OFFLINE='1', HF_HUB_DISABLE_TELEMETRY='1', TOKENIZERS_PARALLELISM='false')


def guard():
    assert Path(sys.executable).resolve() == PYTHON.resolve()
    assert sys.version_info[:3] == (3,12,11)
    assert os.environ.get('CUDA_VISIBLE_DEVICES') == ''
    assert os.environ.get('HF_HUB_OFFLINE') == '1'


def encode(row, tokenizer):
    assert len(row['completion']) == 1 and row['completion'][0]['role'] == 'assistant'
    assert all(set(m) == {'role','content'} and '<|im_' not in m['content'] for m in row['prompt']+row['completion'])
    ids, labels, measurement = q52.encoded(row, tokenizer)
    prompt = tokenizer.apply_chat_template(row['prompt'], tokenize=True, add_generation_prompt=True)
    start = len(prompt)
    end = start + measurement['supervised_tokens_including_eos']
    assert ids[:start] == prompt and labels[:start] == [-100]*start
    assert labels[start:end] == ids[start:end] and ids[end-1] == tokenizer.eos_token_id
    assert labels[end:] == [-100]*(len(ids)-end)
    assert tokenizer.decode(ids[start:end-1], skip_special_tokens=False) == row['completion'][0]['content']
    assert sum(v != -100 for v in labels[1:]) == end-start
    assert len(ids) <= 2048 and start+64 <= 2048 and not measurement['truncated']
    padded = labels + [-100]*(2048-len(ids))
    assert all(v == -100 for v in padded[len(ids):])
    return dict(measurement, input_ids=ids, labels=labels, attention_mask=[1]*len(ids),
        target_start=start, target_end=end, causal_logit_positions=list(range(start-1,end-1)),
        padded_labels_identity=identity(padded), padding_mask_pass=True, prompt_mask_pass=True,
        post_eos_mask_pass=True, causal_alignment_pass=True)


def prepare():
    guard()
    assert not (OUT/'SOURCE-FREEZE.json').exists() and not ARTIFACTS.exists() and ARTIFACTS.parent.is_dir()
    assert {p.name for p in OUT.iterdir()} == {'PREPARATION-FAILURE-1.json','PREPARATION-FAILURE-2.json'}
    write('SOURCE-FREEZE.json', dict(stage='BEFORE_PREFLIGHT', files={p.relative_to(ROOT).as_posix():sha(p) for p in sorted(HERE.glob('*')) if p.is_file()}))
    # Preserved identity audit, never historical publication routines or response scoring.
    publisher.checks()
    baseline = q.freeze.baseline()
    assert baseline == read(ROOT/'benchmark/results/phase6/r6_73/BASELINE.json')
    write('BASELINE.json', dict(inherited=baseline, r6_73=f.publication('r6_73'),
        preserved_publications={name:f.publication(name) for name in ('r6_52','r6_54','r6_55','r6_58','r6_59','r6_66','r6_67')},
        kernel_constructs=26, kernel_basis='Preserved accounting/production identities, not a new recount.'))
    dataset = read(PRIOR/'SFT-READY.json')
    assert dataset == publisher.ready_records()
    source = read(PRIOR/'TRAINING-RECORDS.json')['records']
    positives = {identity(r):r for r in source if r['label']=='positive'}
    negatives = {identity(r):r for r in source if r['label']=='negative'}
    assert len(positives) == 18 and len(negatives) == 36
    direct = sorted((r for r in dataset['records'] if r['label']=='positive'), key=lambda r:r['episode_id'])
    cycle = []
    provenance = []
    duplicate_inputs = set()
    for row in direct:
        parent = positives[row['positive_ledger_identity']]
        corrections = sorted((r for r in dataset['records'] if r['input_negative_ledger_identity'] in negatives and
            r['positive_ledger_identity'] == row['positive_ledger_identity']), key=lambda r:r['episode_id'])
        assert len(corrections) == 2
        cycle.extend([row]+corrections)
        for item in [row]+corrections:
            assert item['partition'] == 'training' and item['assistant_target_label'] == 'positive'
            assert item['contrast_family_identity'].startswith('F')
            assert item['completion'] == row['completion']
            assert item['completion'][0]['content'] == serialize(parent['correct_compact_decision'])
            prompt_source = json.loads(item['prompt'][1]['content'])
            assert prompt_source['requirement'] == parent['requirement']
            assert identity(prompt_source['requirement']) == item['requirement_identity']
            assert canonical(prompt_source['scope']) == canonical(parent['typed_scope'])
            assert prompt_source['scope']['identity'] == item['typed_scope_identity']
            key = identity(item['prompt'])
            assert key not in duplicate_inputs, 'Duplicate or contradictory supervision'
            duplicate_inputs.add(key)
            if item['label'] != 'positive':
                negative = negatives[item['input_negative_ledger_identity']]
                hint = json.loads(item['prompt'][-1]['content'])
                assert hint['candidate_decision'] == negative['compact_target_decision']
                assert item['input_candidate_label'] == 'negative' and 'does not satisfy' in hint['instruction']
            action, _, _ = reconstruct(item['completion'][0]['content'], parent['typed_scope'])
            assert identity(action) == item['reconstructed_action_identity']
            provenance.append(dict(episode_id=item['episode_id'], record_identity=identity(item),
                source_file_sha256=sha(PRIOR/'SFT-READY.json'), positive_ledger_identity=item['positive_ledger_identity'],
                input_negative_ledger_identity=item['input_negative_ledger_identity'], action_identity=identity(action)))
    assert len(cycle) == 54 and len({r['episode_id'] for r in cycle}) == 54
    write('DATASET.json', dict(records=cycle, source='R6.73 SFT-READY.json', direct=18, corrective=36, expansion=0))
    write('DATASET-QUALIFICATION.json', dict(passed=True, direct=18, corrective=36, eligible=54,
        underlying_positive_records=18, distinct_requirement_identities=17, independent_requirements=False,
        duplicates=0, contradictions=0, evaluation_family_rows=0, all_targets_correct=True,
        exact_source=provenance, dataset_identity=identity(read(OUT/'DATASET.json'))))
    sequence = [dict(presentation=i+1, episode_id=cycle[i%54]['episode_id'],
        epoch=i//54+1, optimizer_step=i//4+1, microbatch_in_step=i%4+1) for i in range(216)]
    sampling = dict(cycle=[r['episode_id'] for r in cycle], sequence=sequence, presentations=216,
        counts={r['episode_id']:4 for r in cycle}, microbatch_size=1, gradient_accumulation=4,
        maximum_optimizer_updates=54, epoch_end_presentations=[54,108,162,216],
        accumulation_across_epoch_boundaries=True, shuffle=False, reshuffling_permitted=False,
        seed=651, sampling_rng_draws=0, rng='Sampling consumes no RNG. Python/torch CPU/CUDA seed651 for adapter/dropout; no NumPy transforms.',
        order='Frozen positive ID ascending, direct followed by its N1/N2 corrections; repeat four times.')
    write('SAMPLING.json', sampling)
    cfg = copy.deepcopy(read(ROOT/'benchmark/results/phase6/r6_66/TRAINING-CONFIGURATION.json')['configuration'])
    # No historical dataset/diagnostic/worker identities masquerade as current integration.
    for key in ('dataset_file_sha256','dataset_identities_sha256','diagnostic_manifest_sha256','diagnostic_protocol_identity',
                'loss_mask_evidence_sha256','loss_normalization_evidence_sha256','tokenization_sha256','worker_sha256',
                'scheduler_manifest_sha256','scorer_sha256'):
        cfg.pop(key, None)
    cfg.update(round='R6.74', planned_optimizer_steps=54, warmup_steps=6,
        checkpoint_output_root=str(ARTIFACTS), checkpoint_steps=[27,54],
        checkpoint_output_paths=[str(ARTIFACTS/f'step{s}') for s in (27,54)],
        initialization='Original pinned base, fresh seed651 adapter; never R6.59/R6.67 adapter.',
        dataset_identity=identity(read(OUT/'DATASET.json')), sampling_identity=identity(sampling),
        training_episodes=sampling['cycle'], training_record_sampling_order=sampling['order'],
        scheduler_post_warmup_behavior='Peak at index6, decay to zero at index54; update1 uses zero LR.',
        decoding_settings=dict(do_sample=False,num_beams=1,max_new_tokens=64,repetition_penalty=1.0,
            use_cache=False,eos_token_id=151645,pad_token_id=151643,seed=651,per_generation_timeout_seconds=120),
        evaluation_manifest='EVALUATION.json; separate realization after dataset freeze',
        fresh_output_claim=True, final_checkpoint_selection=54,
        intermediate_checkpoint='27 recovery/provenance only; no outcome selection',
        model_loss='Installed ForCausalLMLoss; per-record completion+EOS mean; divide each by4 before backward.',
        executable_training_configuration_frozen=True, status='PREPARED_CPU_ONLY')
    cfg['logging']['directory'] = str(OUT/'execution')
    write('TRAINING-CONFIGURATION.json', dict(configuration=cfg, canonical_sha256=identity(cfg)))
    from transformers.optimization import _get_linear_schedule_with_warmup_lr_lambda as factor
    schedule = [dict(step=s, lr_used_by_update=1e-4*factor(s-1,num_warmup_steps=6,num_training_steps=54),
        lr_after_scheduler_step=1e-4*factor(s,num_warmup_steps=6,num_training_steps=54)) for s in range(1,55)]
    assert schedule[0]['lr_used_by_update'] == 0 and schedule[6]['lr_used_by_update'] == 1e-4
    assert schedule[-1]['lr_after_scheduler_step'] == 0
    write('SCHEDULER-SIMULATION.json', dict(sequence=schedule, initial_index=0, scheduler_instances=0,
        optimizer_instances=0, scheduler_updates=0, semantics='Optimizer then scheduler, only completed/unskipped update; failures halt.',
        skipped_update_control='No optimizer completion -> index unchanged; halt, no continuation.'))
    write('LOSS-POLICY.json', dict(normalization='Equal-record mean completion+EOS CE divided by4 for each microbatch; not pooled-token.',
        mask='Prompt, padding and post-EOS newline -100; assistant content plus turn EOS supervised.',
        causal_shift='Labels[t] predicted by logits[t-1]; installed ForCausalLMLoss handles shift once.',
        corrective='Incorrect labeled input stays in prompt; only correct assistant completion receives loss.',
        packing=False,truncation=False,gradient_accumulation=4))
    # Freeze train conversion before evaluation solution realization, in a separate process.
    write('TRAINING-DATA-FREEZE.json', dict(stage='BEFORE_EVALUATION_REALIZATION', files={
        (OUT/n).relative_to(ROOT).as_posix():sha(OUT/n) for n in ('DATASET.json','DATASET-QUALIFICATION.json','SAMPLING.json','LOSS-POLICY.json')}))
    proc = subprocess.run([str(PYTHON),str(HERE/'evaluation.py')],env=ENV,cwd=ROOT,capture_output=True,text=True,timeout=120)
    write('EVALUATION-PREPARATION-PROCESS.json', dict(returncode=proc.returncode,stdout=proc.stdout,stderr=proc.stderr))
    assert proc.returncode == 0, proc.stderr
    worker = load('r674_frozen_worker', 'experiments/contrastive_preflight_r6_74/worker.py')
    source = worker.effective_source()
    compile(source, 'r674-frozen-worker', 'exec')
    (OUT/'EFFECTIVE-WORKER.py.txt').write_text(source,encoding='utf-8',newline='\n')
    write('OUTPUT-PATHS.json', dict(artifacts=str(ARTIFACTS), execution=str(OUT/'execution'),
        checkpoints=[27,54],fresh=True,exists=False,overwrite=False,automatic_resume=False,
        dispatch_claim=str(OUT/'execution/DISPATCH-CLAIM.json'),one_shot=True))
    write('CONFIGURATION-FREEZE.json', dict(stage='BEFORE_CPU_CONTROLS_AND_ALL_MODEL_INFERENCE',files={
        p.relative_to(ROOT).as_posix():sha(p) for p in sorted(OUT.iterdir()) if p.is_file()}))


def qualify():
    guard()
    frozen_check()
    started = time.perf_counter()
    versions = {}
    for name in ('torch','transformers','peft','trl','accelerate','bitsandbytes','datasets','tokenizers','safetensors'):
        importlib.import_module(name)
        versions[name] = importlib.metadata.version(name)
    installed = read(ROOT/'benchmark/results/phase6/r6_52/ENVIRONMENT.json')['packages']
    assert versions == installed
    import torch
    torch.set_num_threads(1)
    from transformers import AutoTokenizer, GenerationConfig, BitsAndBytesConfig
    from peft import LoraConfig
    from transformers.loss.loss_utils import ForCausalLMLoss
    cfg = read(OUT/'TRAINING-CONFIGURATION.json')['configuration']
    assert cfg['optimizer_configuration'] == read(ROOT/'benchmark/results/phase6/r6_66/TRAINING-CONFIGURATION.json')['configuration']['optimizer_configuration']
    assert cfg['optimizer_configuration']['torch_version'] == torch.__version__
    inspect.signature(torch.optim.AdamW).bind([],**cfg['optimizer_configuration']['kwargs'])
    lora = LoraConfig(**cfg['adapter_configuration'])
    assert lora.r == 8 and not lora.inference_mode and lora.target_modules == {'q_proj','v_proj'}
    quant = BitsAndBytesConfig(load_in_4bit=True,bnb_4bit_quant_type='nf4',bnb_4bit_use_double_quant=True,bnb_4bit_compute_dtype=torch.bfloat16)
    assert quant.to_dict() == cfg['quantization_configuration']
    assert inspect.getsource(ForCausalLMLoss) == read(ROOT/'benchmark/results/phase6/r6_56/LOSS-NORMALIZATION.json')['loss_helper_source']
    tokenizer = AutoTokenizer.from_pretrained(STORE/'checkpoint',local_files_only=True,trust_remote_code=False)
    tokens = [encode(r,tokenizer) for r in rows()]
    losses, counts, checks = [], [], []
    for i, item in enumerate(tokens):
        labels = torch.tensor([[-100 if v == -100 else 0 for v in item['labels']]],dtype=torch.long)
        logits = torch.zeros((1,len(item['input_ids']),2),dtype=torch.float32)
        logits[:,:,1] = (i+1)/10
        loss = ForCausalLMLoss(logits,labels,vocab_size=2)
        shifted = torch.nn.functional.pad(labels,(0,1),value=-100)[:,1:]
        manual = torch.nn.functional.cross_entropy(logits.reshape(-1,2),shifted.reshape(-1),ignore_index=-100)
        padded = ForCausalLMLoss(torch.nn.functional.pad(logits,(0,0,0,7)),torch.nn.functional.pad(labels,(0,7),value=-100),vocab_size=2)
        assert torch.equal(loss,manual) and torch.equal(loss,padded)
        count = int((shifted != -100).sum())
        assert count == item['supervised_tokens_including_eos']
        checks.append(dict(episode_id=item['episode_id'],causal_shift=True,padding_invariance=True,count=count,synthetic_loss=float(loss)))
        losses.append(float(loss)); counts.append(count)
    equal = sum(losses[:4])/4
    pooled = sum(v*n for v,n in zip(losses[:4],counts[:4]))/sum(counts[:4])
    assert abs(equal-pooled)>1e-6
    # Sampling must consume no RNG, including across non-update-aligned epoch ends.
    rng = random.Random(651)
    before = rng.getstate()
    sampling = read(OUT/'SAMPLING.json')
    for i,p in enumerate(sampling['sequence']):
        assert p['episode_id'] == sampling['cycle'][i%54] and p['optimizer_step'] == i//4+1
        assert p['microbatch_in_step'] == i%4+1 and p['epoch'] == i//54+1
    assert rng.getstate() == before
    assert all(sampling['sequence'][s*4]['optimizer_step'] == s+1 for s in range(54))
    # Recheck qualified linear arithmetic without scheduler construction or stepping.
    from transformers.optimization import _get_linear_schedule_with_warmup_lr_lambda as factor
    for s,row in enumerate(read(OUT/'SCHEDULER-SIMULATION.json')['sequence'],1):
        assert row['lr_used_by_update'] == 1e-4*factor(s-1,num_warmup_steps=6,num_training_steps=54)
        assert row['lr_after_scheduler_step'] == 1e-4*factor(s,num_warmup_steps=6,num_training_steps=54)
    q.write = write
    q.adversarial(q.rows())
    q.compact_controls(q.rows(),tokenizer)
    evaluation = read(OUT/'EVALUATION.json')
    evaluation_scores = []
    decoder_cases = []
    seen = set()
    generation = GenerationConfig(**{k:v for k,v in cfg['decoding_settings'].items() if k not in ('seed','per_generation_timeout_seconds')})
    assert generation.max_new_tokens == 64 and not generation.do_sample and not generation.use_cache
    for row in evaluation['records']:
        for path,digest in read(OUT/'EVALUATION-FREEZE.json')['files'].items():
            assert sha(ROOT/path) == digest
        result = score(serialize(row['target']),row)
        assert result['accepted'], (row['id'],result)
        evaluation_scores.append(dict(id=row['id'],scores=result))
        key = identity(dict(names=sorted(p['name'] for p in row['scope']['params'])+sorted(s['id'] for s in row['scope']['steps']),literals=row['scope']['literals']))
        if key not in seen:
            seen.add(key)
            language = CompletionLanguage(row['scope'])
            maximum = 0
            for text in language.texts:
                ids = tokenizer.encode(text,add_special_tokens=False)
                maximum = max(maximum,len(ids)+1)
                assert tokenizer.decode(ids,skip_special_tokens=False) == text
                for at in range(len(ids)+1):
                    assert language.accepts(tokenizer.decode(ids[:at],skip_special_tokens=False))[0]
                assert language.allowed(tokenizer,ids,[]) == [tokenizer.eos_token_id]
            assert maximum <= 64
            decoder_cases.append(dict(language_identity=identity(language.texts),decisions=len(language.texts),maximum_tokens_including_eos=maximum))
        assert serialize(row['target']) in CompletionLanguage(row['scope']).terminals
    controls = []
    for original in q.rows():
        row = dict(scope=original['scope'],target=original['target'],cases=original['cases'])
        for negative in original['negatives']:
            actual = score(serialize(negative['decision']),row)
            assert not actual['accepted']
            controls.append(dict(id=original['id'],input=negative['decision'],scores=actual))
    # Duplicate-key, incomplete/budget-cut and terminal suffix rejection use exact parser.
    row = evaluation['records'][0]
    text = serialize(row['target'])
    for malformed in (text[:-1],text+'x',text.replace('"op":"le"','"op":"le","op":"eq"')):
        assert not score(malformed,row)['strict_decision_validity']
    write('TOKENIZATION.json', dict(records=tokens,tokenizer_sha256=sha(STORE/'checkpoint/tokenizer.json'),truncated=0))
    write('LOSS-MASK-VERIFICATION.json', dict(passed=True,records=checks,normalization=read(OUT/'LOSS-POLICY.json'),
        equal_record_control=equal,pooled_token_control=pooled,backward_calls=0))
    write('DECODER-SCORER-QUALIFICATION.json', dict(passed=True,compact_controls='COMPACT-DECODER-CONTROLS.json',
        adversarial_controls=26,semantic_contrast_controls=controls,evaluation_gold=evaluation_scores,
        evaluation_languages=decoder_cases,malformed_budget_suffix_controls=3,
        budget='64 includes final EOS; incomplete output never repaired; EOS permitted only at terminal.',
        answer_filter=False,live_model_generation='NOT_RUN; later neutral qualification required.'))
    assert not torch.cuda.is_initialized() and not ARTIFACTS.exists()
    source = (OUT/'EFFECTIVE-WORKER.py.txt').read_text(encoding='utf-8')
    worker = load('r674_checked_worker', 'experiments/contrastive_preflight_r6_74/worker.py')
    assert source == worker.effective_source()
    compile(source,'r674-worker','exec')
    assert '(loss / 4).backward()' in source and 'range(1, 55)' in source
    assert 'num_warmup_steps=6, num_training_steps=54' in source
    assert 'step20' not in source and "read(OUT / 'SCHEDULER-SIMULATION.json')['sequence']" in source
    write('CPU-QUALIFICATION.json',dict(passed=True,interpreter=sys.executable,python=sys.version,packages=versions,
        cpu_only=True,cuda_initialized=False,model_loads=0,inference_calls=0,training=0,backward_calls=0,
        optimizer_instances=0,scheduler_instances=0,optimizer_updates=0,scheduler_updates=0,
        sampling_presentations=216,optimizer_schedule_entries=54,eligible_records=54,direct=18,corrective=36,
        evaluation_cases=24,calibration_cases=6,configuration_identity=identity(cfg),sampling_identity=identity(sampling),
        loss_normalization_identity=identity(read(OUT/'LOSS-POLICY.json')),elapsed_seconds=time.perf_counter()-started,
        worker_compile=True,output_paths_absent=True,limits=cfg['limits'],gpu_feasibility='Inherited only; no new GPU execution.'))


if __name__ == '__main__':
    try:
        {'prepare':prepare,'qualify':qualify}[sys.argv[1]]()
        print('PASS R6.74 '+sys.argv[1])
    except BaseException as exc:
        if OUT.exists():
            write('HALT-'+sys.argv[1]+'.json',dict(error=str(exc),traceback=traceback.format_exc(),automatic_retry=False))
        raise
