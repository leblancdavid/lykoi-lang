"""Independent fresh-process replay of the frozen CPU-only preflight."""
import copy
import inspect
import json
import os
from pathlib import Path
import sys
import run


def evaluate():
    r = run
    assert Path(sys.executable).resolve() == r.PYTHON.resolve()
    assert os.environ.get('CUDA_VISIBLE_DEVICES') == ''
    r.frozen_check()
    config = r.read(r.OUT/'TRAINING-CONFIGURATION.json')['configuration']
    dataset = r.read(r.OUT/'DATASET.json')
    sampling = r.read(r.OUT/'SAMPLING.json')
    assert r.identity(dataset) == config['dataset_identity']
    assert r.identity(sampling) == config['sampling_identity']
    assert len(dataset['records']) == 10
    assert dataset['records'] == r.read(r.old.OUT/'DATASET.json')['records']
    cycle = [f'R6.63/D{i:02d}' for i in range(1,11)]
    assert sampling['cycle'] == cycle and sampling['shuffle'] is False
    assert [p['episode_id'] for p in sampling['sequence']] == cycle*8
    assert sampling['canonical_record_identities'] == [r.identity(row) for row in dataset['records']]
    for position, entry in enumerate(sampling['sequence']):
        assert entry == dict(episode_id=cycle[position % 10], presentation=position+1,
                             optimizer_step=position//4+1, microbatch_in_step=position%4+1)
    diagnostics = r.read(r.OUT/'DIAGNOSTICS.json')
    assert diagnostics['records'] == dataset['records'] + r.varied_records()
    assert len(diagnostics['records']) == len(diagnostics['expectations']) == 13
    from transformers import AutoTokenizer, GenerationConfig
    tokenizer = AutoTokenizer.from_pretrained(r.STORE/'checkpoint', local_files_only=True, trust_remote_code=False)
    tokens = [r.encode(row, tokenizer) for row in diagnostics['records']]
    assert tokens == r.read(r.OUT/'TOKENIZATION.json')['records']
    protocol = r.read(r.OUT/'DIAGNOSTIC-PROTOCOL.json')
    generation = GenerationConfig.from_dict(protocol['resolved_generation_configuration'])
    assert generation.to_dict() == protocol['resolved_generation_configuration']
    assert generation.max_new_tokens == 128 and not generation.do_sample and not generation.use_cache
    assert generation.num_beams == 1 and generation.repetition_penalty == 1.1
    assert generation.eos_token_id == [tokenizer.eos_token_id]
    assert all(t['target_content_tokens']+1 <= generation.max_new_tokens for t in tokens)
    gold = []
    for row, expected in zip(diagnostics['records'], diagnostics['expectations'], strict=True):
        action = r.successor.c.load(row['completion'][0]['content'])
        assert expected['prompt_identity'] == r.identity(row['prompt'])
        assert expected['operation'] == next(iter(action['node']['expr']))
        assert expected['operands'] == next(iter(action['node']['expr'].values()))
        assert expected['dependencies'] == action['deps'] and expected['result_type'] == action['type']
        assert expected['functional_acceptance'] == row['cases']
        after, validation = r.successor.assembly.apply(row['before'], action)
        assert expected['assembled_after_identity'] == r.identity(after)
        assert expected['native_validation_identity'] == r.identity(validation)
        gold.append(dict(episode_id=row['episode_id'], scores=r.score(row['completion'][0]['content'], row)))
    assert gold == r.read(r.OUT/'SCORER-GOLD.json')['records']
    integration = r.read(r.OUT/'SCORER-INTEGRATION.json')
    mapping = {row['episode_id']:row for row in dataset['records']}
    for control in integration['negative_controls']:
        assert r.score(control['input'], mapping[control['episode_id']]) == control['integrated_scores']
    assert r.score is r.successor.score and 'jsonschema' not in sys.modules
    assert r.importlib.util.find_spec('jsonschema') is None
    from transformers.optimization import _get_linear_schedule_with_warmup_lr_lambda as factor
    historical = r.read(r.ROOT/'benchmark/results/phase6/r6_54/LEARNING-RATE-SCHEDULE.json')
    for step in range(1,21):
        assert 1e-4*factor(step-1, num_warmup_steps=2, num_training_steps=20) == historical['sequence'][step-1]['lr_used_by_update']
        assert 1e-4*factor(step, num_warmup_steps=2, num_training_steps=20) == historical['sequence'][step-1]['lr_after_scheduler_step']
    # Installed loss helper on synthetic CPU tensors; no model, backward or optimizer.
    import torch
    from transformers.loss.loss_utils import ForCausalLMLoss
    source = inspect.getsource(ForCausalLMLoss)
    inherited = r.read(r.ROOT/'benchmark/results/phase6/r6_56/LOSS-NORMALIZATION.json')
    assert source == inherited['loss_helper_source']
    record_losses = []
    counts = []
    cpu_shift_checks = []
    for index, item in enumerate(tokens):
        labels = torch.tensor([[-100 if v == -100 else 0 for v in item['labels']]], dtype=torch.long)
        logits = torch.zeros((1,len(item['input_ids']),2), dtype=torch.float32)
        logits[:,:,1] = (index+1)/10
        loss = ForCausalLMLoss(logits, labels, vocab_size=2)
        shifted = torch.nn.functional.pad(labels, (0,1), value=-100)[:,1:]
        manual = torch.nn.functional.cross_entropy(logits.reshape(-1,2), shifted.reshape(-1), ignore_index=-100)
        assert torch.equal(loss, manual)
        count = int((shifted != -100).sum())
        assert count == item['supervised_tokens_including_eos']
        padded = torch.nn.functional.pad(labels, (0,7), value=-100)
        padded_logits = torch.nn.functional.pad(logits, (0,0,0,7))
        padded_loss = ForCausalLMLoss(padded_logits, padded, vocab_size=2)
        assert torch.equal(loss,padded_loss)
        counts.append(count)
        record_losses.append(float(loss))
        cpu_shift_checks.append(dict(episode_id=item['episode_id'], synthetic_loss=float(loss), supervised_count=count,
                                     installed_helper_matches_manual=True, padding_invariance=True))
    equal = sum(record_losses[:4])/4
    pooled = sum(loss*n for loss,n in zip(record_losses[:4],counts[:4]))/sum(counts[:4])
    assert abs(equal-pooled) > 1e-6
    inherited_config = r.read(r.ROOT/'benchmark/results/phase6/r6_59/TRAINING-CONFIGURATION.json')['configuration']
    for key in ('optimizer_configuration','limits','precision_runtime','compute_dtype','adapter_parameter_dtype',
                'gradient_clip','gradient_checkpointing','lora_rank','lora_dropout','lora_alpha','max_sequence_length',
                'microbatch_size','gradient_accumulation','warmup_steps','planned_optimizer_steps','use_cache'):
        assert config[key] == inherited_config[key], key
    assert config['seed'] == 651 and config['adapter_configuration']['inference_mode'] is False
    assert config['adapter_configuration']['r'] == 8
    assert config['adapter_configuration']['target_modules'] == ['q_proj','v_proj']
    assert config['unresolved_training_critical_settings'] == []
    assert config['cache_release'] == r.read(r.ROOT/'benchmark/results/phase6/r6_59/CACHE-RELEASE-QUALIFICATION.json')
    from peft import LoraConfig
    lora = LoraConfig(**config['adapter_configuration'])
    assert not lora.inference_mode and lora.r == 8 and lora.target_modules == {'q_proj','v_proj'}
    from transformers import BitsAndBytesConfig
    quant = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type='nf4',
                              bnb_4bit_use_double_quant=True, bnb_4bit_compute_dtype=torch.bfloat16)
    assert quant.to_dict() == config['quantization_configuration']
    worker = r.load('r666_replay_worker', 'experiments/incremental_training_r6_66/worker.py')
    source = worker.effective_source()
    assert source == (r.OUT/'EFFECTIVE-WORKER.py.txt').read_text(encoding='utf-8')
    compile(source, 'qualified-effective-worker', 'exec')
    assert '(loss / 4).backward()' in source and "read(OUT / 'SAMPLING.json')['sequence']" in source
    assert 'num_warmup_steps=2, num_training_steps=20' in source
    assert 'torch.cuda.empty_cache()' in source and 'cache_preserved_gradients=True' in source
    assert not r.ARTIFACTS.exists() and not list(r.OUT.glob('*DISPATCH-CLAIM.json'))
    assert not torch.cuda.is_initialized()
    return dict(passed=True, interpreter=sys.executable, cpu_only=True, model_loads=0, inference_calls=0,
                backward_calls=0, optimizer_instances=0, scheduler_instances=0, optimizer_updates=0, scheduler_updates=0,
                exact_tokenization_replay=13, diagnostic_gold=13, diagnostic_fixtures=sum(len(row['cases']) for row in diagnostics['records']),
                negative_controls=len(integration['negative_controls']), direct_checker_controls=6,
                sampling_presentations=80, sequence_identity=r.identity(sampling), configuration_identity=r.identity(config),
                cpu_loss_checks=cpu_shift_checks, equal_record_mean=equal, pooled_token_negative_control=pooled,
                installed_loss_helper_sha256=r.sha(Path(inspect.getfile(ForCausalLMLoss))), cuda_initialized=False,
                gpu_model_execution='NOT_RUN; only tokenizer and synthetic CPU loss helper')


if __name__ == '__main__':
    print(json.dumps(evaluate(), sort_keys=True, allow_nan=False))
