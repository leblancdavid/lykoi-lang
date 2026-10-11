"""Independent remaining CPU controls after preserved frozen qualification halt.

Does not repair/reexecute the frozen qualify entry point or permit dispatch.
"""
import ast
import importlib
import importlib.metadata
import inspect
import json
import os
from pathlib import Path
import sys
import traceback
from integration import *


def main():
    assert Path(sys.executable).resolve() == PYTHON.resolve() and sys.version_info[:3] == (3,12,11)
    assert os.environ.get('CUDA_VISIBLE_DEVICES') == ''
    frozen_check()
    assert read(OUT/'HALT-qualify.json')['error'] == ''
    write('REMAINING-CONTROLS-FREEZE.json',dict(stage='AFTER_PRESERVED_HALT_BEFORE_REMAINING_CONTROLS',
        source_sha256=sha(Path(__file__)),original_source_freeze_sha256=sha(OUT/'SOURCE-FREEZE.json'),
        classification_cannot_be_ready=True,frozen_configuration_modified=False))
    from transformers import AutoTokenizer, GenerationConfig
    import torch
    torch.set_num_threads(1)
    from transformers.loss.loss_utils import ForCausalLMLoss
    preflight = load('r674_inert_encoding','experiments/contrastive_preflight_r6_74/preflight.py')
    tokenizer = AutoTokenizer.from_pretrained(STORE/'checkpoint',local_files_only=True,trust_remote_code=False)
    cfg = read(OUT/'TRAINING-CONFIGURATION.json')['configuration']
    versions = {}
    for name in ('torch','transformers','peft','trl','accelerate','bitsandbytes','datasets','tokenizers','safetensors'):
        importlib.import_module(name)
        versions[name] = importlib.metadata.version(name)
    assert versions == read(ROOT/'benchmark/results/phase6/r6_52/ENVIRONMENT.json')['packages']
    tokens = [preflight.encode(row,tokenizer) for row in rows()]
    checks, losses, counts = [], [], []
    for i,item in enumerate(tokens):
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
    assert len(set(counts[:4])) == 1 and abs(equal-pooled)<=1e-6
    write('TOKENIZATION.json',dict(records=tokens,tokenizer_sha256=sha(STORE/'checkpoint/tokenizer.json'),truncated=0))
    write('LOSS-MASK-VERIFICATION.json',dict(per_record_checks_passed=True,records=checks,
        normalization=read(OUT/'LOSS-POLICY.json'),normalization_identity=identity(read(OUT/'LOSS-POLICY.json')),
        negative_control_passed=False,equal_record_control=equal,pooled_token_control=pooled,
        first_four_supervised_counts=counts[:4],cause='Equal lengths make both weighting formulas identical; frozen discriminating-control assertion is invalid.',
        policy_not_modified=True,backward_calls=0))
    q.write = write
    q.adversarial(q.rows())
    q.compact_controls(q.rows(),tokenizer)
    evaluation = read(OUT/'EVALUATION.json')
    gold, decoder = [], []
    seen = set()
    generation = GenerationConfig(**{k:v for k,v in cfg['decoding_settings'].items() if k not in ('seed','per_generation_timeout_seconds')})
    assert generation.max_new_tokens == 64 and not generation.do_sample and not generation.use_cache
    for path,digest in read(OUT/'EVALUATION-FREEZE.json')['files'].items():
        assert sha(ROOT/path) == digest
    # ASCII single-character extension witnesses exist on the pinned tokenizer.
    char_ids = {}
    for token in range(len(tokenizer)):
        if token not in tokenizer.all_special_ids:
            text = tokenizer.decode([token],skip_special_tokens=False)
            if len(text)==1 and text.isascii():
                char_ids.setdefault(text,token)
    for row in evaluation['records']:
        result = score(serialize(row['target']),row)
        assert result['accepted'], (row['id'],result)
        gold.append(dict(id=row['id'],scores=result))
        language = CompletionLanguage(row['scope'])
        assert serialize(row['target']) in language.terminals
        key = identity(language.texts)
        if key not in seen:
            seen.add(key)
            maximum, observations, witnesses = 0, 0, {}
            for text in language.texts:
                ids = tokenizer.encode(text,add_special_tokens=False)
                maximum = max(maximum,len(ids)+1)
                assert tokenizer.decode(ids,skip_special_tokens=False) == text
                for at in range(len(ids)+1):
                    assert language.accepts(tokenizer.decode(ids[:at],skip_special_tokens=False))[0]
                    observations += 1
                for i in range(len(text)):
                    witnesses.setdefault(text[:i],text[i])
                assert language.allowed(tokenizer,ids,[]) == [tokenizer.eos_token_id]
            assert maximum <= 64 and set(witnesses) == language.prefixes-language.terminals
            for prefix,next_char in witnesses.items():
                ids = tokenizer.encode(prefix,add_special_tokens=False)
                following = tokenizer.decode(ids+[char_ids[next_char]],skip_special_tokens=False)
                assert following == prefix+next_char and language.accepts(following)[0]
            assert {json.loads(text)['op'] for text in language.texts} == {'add','le','eq'}
            decoder.append(dict(language_identity=key,decisions=len(language.texts),prefix_observations=observations,
                nonterminal_extension_witnesses=len(witnesses),maximum_tokens_including_eos=maximum,terminal_eos_only=True))
    contrasts = []
    for row in q.rows():
        for negative in row['negatives']:
            actual = score(serialize(negative['decision']),row)
            assert not actual['accepted']
            contrasts.append(dict(id=row['id'],input=negative['decision'],scores=actual))
    row = evaluation['records'][0]
    text = serialize(row['target'])
    malformed = [text[:-1],text+'x',text.replace('"op":"le"','"op":"le","op":"eq"')]
    assert all(not score(candidate,row)['strict_decision_validity'] for candidate in malformed)
    write('DECODER-SCORER-QUALIFICATION.json',dict(passed=True,adversarial_controls=26,contrast_controls=contrasts,
        evaluation_gold=gold,evaluation_languages=decoder,malformed_budget_suffix_controls=3,
        answer_filter=False,live_model_generation='NOT_RUN',budget='64 including terminal EOS; incomplete outputs reject without repair.'))
    worker = load('r674_source_audit','experiments/contrastive_preflight_r6_74/worker.py')
    source = (OUT/'EFFECTIVE-WORKER.py.txt').read_text(encoding='utf-8')
    assert source == worker.effective_source()
    compile(source,'r674-frozen-worker','exec')
    for path in HERE.glob('*.py'):
        ast.parse(path.read_text(encoding='utf-8'))
    runtime = load('r674_runtime_import_only','experiments/contrastive_preflight_r6_74/runtime.py')
    # Required resource interface must exist; never exercise model/GPU machinery.
    resource_callable = callable(getattr(runtime.c,'rss',None))
    assert not resource_callable
    write('EXECUTABLE-INTEGRATION-AUDIT.json',dict(compile_pass=True,runtime_import_pass=True,
        required_resource_provider_pass=False,
        defect='runtime.c and dispatch.c bind R6.18 composition, which has no rss callable. Inherited worker memory() and launcher invoke c.rss; dispatch cannot enforce the frozen RSS limit.',
        defects_not_repaired=True,model_loads=0,optimizer_instances=0,scheduler_instances=0))
    schedule = read(OUT/'SCHEDULER-SIMULATION.json')['sequence']
    from transformers.optimization import _get_linear_schedule_with_warmup_lr_lambda as factor
    for i, entry in enumerate(schedule,1):
        assert entry['lr_used_by_update'] == 1e-4*factor(i-1,num_warmup_steps=6,num_training_steps=54)
        assert entry['lr_after_scheduler_step'] == 1e-4*factor(i,num_warmup_steps=6,num_training_steps=54)
    sampling = read(OUT/'SAMPLING.json')
    assert [p['episode_id'] for p in sampling['sequence']] == sampling['cycle']*4
    assert len(sampling['sequence']) == 216 and len(schedule)==54
    assert not ARTIFACTS.exists() and not (OUT/'execution').exists() and not torch.cuda.is_initialized()
    write('CPU-QUALIFICATION.json',dict(passed=False,classification='R6_74_CONFIGURATION_GAP',
        original_gate='HALT-qualify.json; not repaired/reexecuted',remaining_controls_passed=True,
        packages=versions,interpreter=sys.executable,python=sys.version,cpu_only=True,cuda_initialized=False,
        eligible_records=54,direct=18,corrective=36,sampling_presentations=216,optimizer_schedule_entries=54,
        sampling_identity=identity(sampling),loss_normalization_identity=identity(read(OUT/'LOSS-POLICY.json')),
        configuration_identity=identity(cfg),evaluation_cases=24,exposed_calibration_cases=6,
        model_loads=0,participant_inference=0,training=0,backward_calls=0,optimizer_instances=0,scheduler_instances=0,
        optimizer_updates=0,scheduler_updates=0,output_paths_absent=True,limits=cfg['limits'],
        historical_rescoring=0,p6_a04_acceptance=0,p6_a05_access=False))
    print('PASS remaining CPU controls; frozen qualification/resource integration gaps retained; NOT READY')


if __name__ == '__main__':
    try:
        main()
    except BaseException as exc:
        write('HALT-remaining-controls.json',dict(error=str(exc),traceback=traceback.format_exc(),automatic_retry=False))
        raise
