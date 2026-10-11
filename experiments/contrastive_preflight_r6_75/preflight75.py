"""Exclusive CPU stages: freeze before numerical/semantic controls and dry launch."""
import copy
import importlib
import importlib.metadata
import inspect
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import traceback
import context75 as x
import resources75 as resource
import runtime75
import worker75


def baseline():
    old_publisher = x.prior.load('r675_preserved_audit', 'experiments/contrastive_preflight_r6_74/publish.py')
    checks = old_publisher.checks()
    publication = x.prior.f.publication('r6_74')
    assert not checks['ready'] and checks['classifier'] == 'R6_74_CONFIGURATION_GAP'
    assert not callable(getattr(x.prior.c, 'rss', None))
    assert x.read(x.OLD/'LOSS-MASK-VERIFICATION.json')['first_four_supervised_counts'] == [24]*4
    return dict(r6_74=publication, checks=checks, inherited=x.read(x.OLD/'BASELINE.json'),
                original_failures={n:x.sha(x.OLD/n) for n in ('HALT-qualify.json','HALT-remaining-controls.json',
                'PREPARATION-FAILURE-1.json','PREPARATION-FAILURE-2.json','EVALUATION-READINESS.json',
                'EXECUTABLE-INTEGRATION-AUDIT.json','TRAINING-READINESS.json')}, kernel_constructs=26)


def prepare():
    x.guard()
    assert not x.OUT.exists()
    x.write('BASELINE.json', baseline())
    old = x.read(x.OLD/'EVALUATION.json')
    successor = copy.deepcopy(old)
    successor['records'] = [x.corrected(row) for row in old['records']]
    x.check_remapping(old, successor)
    x.write('EVALUATION.json', successor)
    identities = []
    for old_row, new in zip(old['records'], successor['records']):
        identities.append(dict(id=new['id'], partition=new['partition'], original_name=old_row['scope']['name'],
            successor_name=new['scope']['name'], original_scope_identity=old_row['scope_identity'],
            successor_scope_identity=new['scope_identity'], fixture_identity=x.identity(new),
            expectation_identity=x.identity(dict(requirement=new['requirement'], target=new['target'], cases=new['cases'])),
            original_expectation_identity=x.identity(dict(requirement=old_row['requirement'],target=old_row['target'],cases=old_row['cases'])),
            calibration_unchanged=new == old_row))
    x.write('EVALUATION-IDENTITIES.json', dict(original_file_sha256=x.sha(x.OLD/'EVALUATION.json'),
        successor_file_sha256=x.sha(x.OUT/'EVALUATION.json'), mapping='Scope name hyphen -> underscore only', records=identities))
    examples = []
    for i, count in enumerate((2,4,6,8)):
        labels = [-100]*3 + [0]*count + [-100]*3
        logits = [[0,9] for _ in labels]
        for at in range(2,2+count):
            logits[at] = [0,i]
        examples.append(dict(count=count, content_tokens=count-1, eos_position=3+count-1,
            labels=labels, logits=logits, expected_mean_ce=math.log1p(math.exp(i)),
            expected_contribution=math.log1p(math.exp(i))/4))
    losses = [row['expected_mean_ce'] for row in examples]
    x.write('NORMALIZATION-CONTROL.json', dict(examples=examples, synthetic_only=True, training_records_changed=0,
        expected_accumulated_equal_record=sum(losses)/4, expected_equal_record_mean_divided_by_four=sum(losses)/16,
        expected_pooled_token=sum(v*n for v,n in zip(losses,(2,4,6,8)))/20,
        analytic_absolute_tolerance=2e-6, accumulation=4, backward_calls=0))
    source = worker75.effective_source()
    diagnostic = runtime75.diagnostic_source()
    for name, value in (('EFFECTIVE-WORKER.py.txt',source),('EFFECTIVE-DIAGNOSTIC.py.txt',diagnostic)):
        compile(value,name,'exec')
        with (x.OUT/name).open('x',encoding='utf-8',newline='\n') as stream:
            stream.write(value)
    cfg = copy.deepcopy(x.read(x.OLD/'TRAINING-CONFIGURATION.json')['configuration'])
    cfg.update(round='R6.75',checkpoint_output_root=str(x.ARTIFACTS),
        checkpoint_output_paths=[str(x.ARTIFACTS/f'step{s}') for s in (27,54)],
        logging=dict(cfg['logging'],directory=str(x.OUT/'execution')),status='FROZEN_CPU_PREFLIGHT',
        evaluation_manifest=(x.OUT/'EVALUATION.json').relative_to(x.ROOT).as_posix())
    rel = lambda p:p.relative_to(x.ROOT).as_posix()
    cfg['execution_binding'] = dict(worker=rel(x.HERE/'worker75.py'),launcher=rel(x.HERE/'dispatch75.py'),
        runtime=rel(x.HERE/'runtime75.py'),resource=rel(x.HERE/'resources75.py'),evaluation=cfg['evaluation_manifest'],
        normalization=rel(x.OUT/'NORMALIZATION-CONTROL.json'),worker_source_sha256=x.sha(x.OUT/'EFFECTIVE-WORKER.py.txt'),
        runtime_source_sha256=x.sha(x.OUT/'EFFECTIVE-DIAGNOSTIC.py.txt'), dataset=rel(x.OLD/'DATASET.json'),
        sampling=rel(x.OLD/'SAMPLING.json'),loss_policy=rel(x.OLD/'LOSS-POLICY.json'),schedule=rel(x.OLD/'SCHEDULER-SIMULATION.json'),
        interpreter=str(x.PYTHON),launch_modes=['base','train','adapter'],
        dry_boundary='Before model load, CUDA operations and optimizer/scheduler construction')
    runtime75.validate_configuration(cfg)
    x.write('TRAINING-CONFIGURATION.json',dict(configuration=cfg,canonical_sha256=x.identity(cfg)))
    assert not x.ARTIFACTS.exists() and not (x.OUT/'execution').exists() and x.ARTIFACTS.parent.is_dir()
    x.write('OUTPUT-PATHS.json',dict(artifacts=str(x.ARTIFACTS),execution=str(x.OUT/'execution'),
        dry_launch=str(x.OUT/'dry-launch'),fresh=True,automatic_retry=False,resume=False,
        checkpoints=[27,54],selected_checkpoint=54,limits=cfg['limits'],process_timeout=1800,generation_timeout=120))
    files = [p for p in x.HERE.iterdir() if p.is_file()] + [p for p in x.OUT.iterdir() if p.is_file()]
    x.write('PREFLIGHT-FREEZE.json', dict(stage='Before successor numerical, scope acceptance and launch execution',
        files={rel(p):x.sha(p) for p in sorted(files)}))
    print('PASS R6.75 baseline and pre-execution freeze')


def reject(name, fn, controls):
    try:
        fn()
    except (AssertionError, ValueError, RuntimeError) as exc:
        controls.append(dict(name=name,rejected=True,error=str(exc)))
    else:
        raise AssertionError('CONTROL_NOT_REJECTED:' + name)


def discriminating(counts, losses):
    assert len(set(counts)) > 1, 'EQUAL_LENGTH_NONDISCRIMINATING'
    assert abs(sum(losses)/4-sum(n*v for n,v in zip(counts,losses))/sum(counts)) > 1e-6, 'INDISTINGUISHABLE_WEIGHTING'


def qualify():
    x.guard()
    x.frozen_check()
    import torch
    torch.set_num_threads(1)
    from transformers import AutoTokenizer, GenerationConfig, BitsAndBytesConfig
    from transformers.loss.loss_utils import ForCausalLMLoss
    from transformers.optimization import _get_linear_schedule_with_warmup_lr_lambda as factor
    from peft import LoraConfig
    versions = {}
    for name in ('torch','transformers','peft','trl','accelerate','bitsandbytes','datasets','tokenizers','safetensors'):
        importlib.import_module(name)
        versions[name] = importlib.metadata.version(name)
    assert versions == x.read(x.ROOT/'benchmark/results/phase6/r6_52/ENVIRONMENT.json')['packages']
    cfg = x.read(x.OUT/'TRAINING-CONFIGURATION.json')['configuration']
    runtime75.validate_configuration(cfg)
    inspect.signature(torch.optim.AdamW).bind([],**cfg['optimizer_configuration']['kwargs'])
    assert LoraConfig(**cfg['adapter_configuration']).target_modules == {'q_proj','v_proj'}
    quant = BitsAndBytesConfig(load_in_4bit=True,bnb_4bit_quant_type='nf4',bnb_4bit_use_double_quant=True,bnb_4bit_compute_dtype=torch.bfloat16)
    assert quant.to_dict() == cfg['quantization_configuration']
    assert inspect.getsource(ForCausalLMLoss) == x.read(x.ROOT/'benchmark/results/phase6/r6_56/LOSS-NORMALIZATION.json')['loss_helper_source']
    gen = GenerationConfig(**{k:v for k,v in cfg['decoding_settings'].items() if k not in ('seed','per_generation_timeout_seconds')})
    assert gen.max_new_tokens == 64 and not gen.do_sample and not gen.use_cache
    tokenizer = AutoTokenizer.from_pretrained(x.STORE/'checkpoint',local_files_only=True,trust_remote_code=False)
    encoder = x.prior.load('r675_inherited_encode', 'experiments/contrastive_preflight_r6_74/preflight.py').encode
    tokens = [encoder(row,tokenizer) for row in x.rows()]
    assert tokens == x.read(x.OLD/'TOKENIZATION.json')['records']
    assert {x.identity(r) for r in x.rows()} == {x.identity(r) for r in x.prior.publisher.ready_records()['records']}
    mask_checks = []
    for i, item in enumerate(tokens):
        labels = torch.tensor([[-100 if v == -100 else 0 for v in item['labels']]],dtype=torch.long)
        logits = torch.zeros((1,len(item['input_ids']),2),dtype=torch.float32)
        logits[:,:,1] = (i+1)/10
        actual = ForCausalLMLoss(logits,labels,vocab_size=2)
        shifted = torch.nn.functional.pad(labels,(0,1),value=-100)[:,1:]
        manual = torch.nn.functional.cross_entropy(logits.reshape(-1,2),shifted.reshape(-1),ignore_index=-100)
        padded = ForCausalLMLoss(torch.nn.functional.pad(logits,(0,0,0,7)),torch.nn.functional.pad(labels,(0,7),value=-100),vocab_size=2)
        assert torch.equal(actual,manual) and torch.equal(actual,padded)
        mask_checks.append(dict(episode_id=item['episode_id'],count=int((shifted != -100).sum()),passed=True))
    x.write('DATASET-MASK-VERIFICATION.json',dict(passed=True,records=mask_checks,source_records=54,
        original_dataset_sha256=x.sha(x.OLD/'DATASET.json'),source_qualification_sha256=x.sha(x.OLD/'DATASET-QUALIFICATION.json'),
        tokenization_exact=True,training_records_changed=0))
    fixture = x.read(x.OUT/'NORMALIZATION-CONTROL.json')
    losses, contributions, numerical = [], [], []
    for row in fixture['examples']:
        labels = torch.tensor([row['labels']],dtype=torch.long)
        logits = torch.tensor([row['logits']],dtype=torch.float32)
        shifted = torch.nn.functional.pad(labels,(0,1),value=-100)[:,1:]
        actual = ForCausalLMLoss(logits,labels,vocab_size=2)
        manual = torch.nn.functional.cross_entropy(logits.reshape(-1,2),shifted.reshape(-1),ignore_index=-100)
        assert torch.equal(actual,manual) and torch.equal(actual/4,manual/4)
        assert int((shifted != -100).sum()) == row['count']
        assert labels[0,row['eos_position']] == 0 and (labels[0,row['eos_position']+1:] == -100).all()
        assert abs(float(actual)-row['expected_mean_ce']) < fixture['analytic_absolute_tolerance']
        poison = logits.clone()
        poison[shifted == -100] = torch.tensor([100.,-100.])
        assert torch.equal(actual,ForCausalLMLoss(poison,labels,vocab_size=2))
        padded = ForCausalLMLoss(torch.nn.functional.pad(logits,(0,0,0,7)),torch.nn.functional.pad(labels,(0,7),value=-100),vocab_size=2)
        assert torch.equal(actual,padded)
        unshifted = torch.nn.functional.cross_entropy(logits.reshape(-1,2),labels.reshape(-1),ignore_index=-100)
        assert not torch.equal(actual,unshifted)
        losses.append(float(actual)); contributions.append(float(actual/4))
        numerical.append(dict(count=row['count'],mean_ce=float(actual),divided_by_four=float(actual/4),
            exact_manual_agreement=True,poison_mask_invariance=True,padding_invariance=True,unshifted_rejected=True))
    counts = [r['count'] for r in fixture['examples']]
    discriminating(counts,losses)
    accumulated = sum(contributions)
    equal_mean = sum(losses)/4
    pooled = sum(n*v for n,v in zip(counts,losses))/sum(counts)
    assert accumulated == equal_mean
    assert sum(contributions)/4 == equal_mean/4
    assert abs(accumulated-fixture['expected_accumulated_equal_record']) < 2e-6
    assert abs(pooled-fixture['expected_pooled_token']) < 2e-6
    x.write('NORMALIZATION-VERIFICATION.json',dict(passed=True,records=numerical,counts=counts,
        accumulated_equal_record=accumulated,equal_record_mean_divided_by_four=equal_mean/4,
        pooled_token=pooled,absolute_disagreement=abs(equal_mean-pooled),exact_equal_record_agreement=True,backward_calls=0))
    sampling = x.read(x.OLD/'SAMPLING.json')
    assert [p['episode_id'] for p in sampling['sequence']] == sampling['cycle']*4
    for i,p in enumerate(sampling['sequence']):
        assert p == dict(presentation=i+1,episode_id=sampling['cycle'][i%54],epoch=i//54+1,optimizer_step=i//4+1,microbatch_in_step=i%4+1)
    schedule = x.read(x.OLD/'SCHEDULER-SIMULATION.json')['sequence']
    assert len(schedule)==54 and len(sampling['sequence'])==216
    for i,row in enumerate(schedule,1):
        assert row['lr_used_by_update']==1e-4*factor(i-1,num_warmup_steps=6,num_training_steps=54)
        assert row['lr_after_scheduler_step']==1e-4*factor(i,num_warmup_steps=6,num_training_steps=54)
    x.write('SAMPLING-SCHEDULE-VERIFICATION.json',dict(passed=True,presentations=216,schedule_entries=54,
        sampling_identity=x.identity(sampling),loss_policy_identity=x.identity(x.read(x.OLD/'LOSS-POLICY.json')),
        optimizer_configuration_identity=x.identity(cfg['optimizer_configuration']),optimizer_instances=0,scheduler_instances=0))
    evaluation = x.read(x.OUT/'EVALUATION.json')
    x.check_remapping(x.read(x.OLD/'EVALUATION.json'),evaluation)
    scores = []
    for row in evaluation['records']:
        x.prior.assembly.check_before(row['scope'])
        result = x.score(x.serialize(row['target']),row)
        assert result['accepted'], (row['id'],result)
        assert result == x.score(x.serialize(row['target']),row)
        scores.append(dict(id=row['id'],partition=row['partition'],scope_valid=True,scores=result))
    x.write('EVALUATION-VERIFICATION.json',dict(passed=True,reserved_accepted=24,calibration_accepted=6,
        observations=sum(len(s['scores']['observations']) for s in scores[:24]),deterministic_reconstruction=True,
        independent_withholding=False,records=scores))
    # Repeat unchanged R6.73 syntax and adversarial mechanism controls into successor output.
    q = x.prior.q
    original_write = q.write
    try:
        q.write = x.write
        q.adversarial(q.rows())
        q.compact_controls(q.rows(),tokenizer)
    finally:
        q.write = original_write
    languages, seen = [], set()
    for row in evaluation['records']:
        language = x.CompletionLanguage(row['scope'])
        key = x.identity(language.texts)
        if key in seen:
            continue
        seen.add(key)
        maximum = 0
        for text in language.texts:
            ids = tokenizer.encode(text,add_special_tokens=False)
            maximum = max(maximum,len(ids)+1)
            assert tokenizer.decode(ids,skip_special_tokens=False)==text
            for at in range(len(ids)+1):
                assert language.accepts(tokenizer.decode(ids[:at],skip_special_tokens=False))[0]
            assert language.allowed(tokenizer,ids,[]) == [tokenizer.eos_token_id]
        assert maximum <= 64
        languages.append(dict(identity=key,decisions=len(language.texts),max_tokens_including_eos=maximum))
    contrasts = []
    for row in q.rows():
        for negative in row['negatives']:
            result = x.score(x.serialize(negative['decision']),row)
            assert not result['accepted']
            contrasts.append(result)
    x.write('DECODER-SCORER-VERIFICATION.json',dict(passed=True,languages=languages,contrast_rejections=contrasts,
        unchanged_decoder=True,unchanged_scorer=True,live_generation='NOT_RUN'))
    controls = []
    reject('equal_length_control',lambda:discriminating([24]*4,losses),controls)
    reject('equal_losses_control',lambda:discriminating(counts,[1.]*4),controls)
    mutated = copy.deepcopy(evaluation)
    mutated['records'][0]['scope']['name'] += 'X'
    reject('incorrect_identifier_remapping',lambda:x.check_remapping(x.read(x.OLD/'EVALUATION.json'),mutated),controls)
    changed = copy.deepcopy(evaluation)
    changed['records'][0]['cases'][0]['expected']['value'] = False
    reject('changed_semantic_expectation',lambda:x.check_remapping(x.read(x.OLD/'EVALUATION.json'),changed),controls)
    missing = dict(requested_pid=os.getpid(),measured_pid=None,observer_pid=os.getpid(),resident_bytes=0,available=False,method=None,reason='unsupported')
    reject('missing_rss_as_zero',lambda:resource.validate(missing,os.getpid()),controls)
    measured = resource.measure()
    resource.validate(measured,os.getpid(),cfg['limits']['process_rss_bytes'])
    wrong = dict(measured,measured_pid=os.getpid()+1)
    reject('incorrect_process_attribution',lambda:resource.validate(wrong,os.getpid()),controls)
    incomplete = copy.deepcopy(cfg)
    del incomplete['execution_binding']['resource']
    reject('incomplete_worker_binding',lambda:runtime75.validate_configuration(incomplete),controls)
    incomplete2 = copy.deepcopy(cfg)
    del incomplete2['optimizer_configuration']
    reject('incomplete_training_configuration',lambda:runtime75.validate_configuration(incomplete2),controls)
    # Genuine unavailable PID and unsupported platform paths must be explicit nulls.
    missing_pid = resource.measure(2147483647)
    assert not missing_pid['available'] and resource.validate(missing_pid,2147483647) is None
    reject('unavailable_rss_budget_enforcement',lambda:resource.validate(missing_pid,2147483647,17179869184),controls)
    platform = resource.sys.platform
    try:
        resource.sys.platform = 'qualification-unsupported'
        unsupported = resource.measure()
        assert not unsupported['available'] and resource.validate(unsupported,os.getpid()) is None
    finally:
        resource.sys.platform = platform
    x.write('RESOURCE-VERIFICATION.json',dict(passed=True,current_worker=measured,invalid_pid=missing_pid,
        unsupported_platform_control=unsupported,dependencies_added=0,fresh_process_python=sys.version))
    x.write('ADVERSARIAL-PREFLIGHT.json',dict(passed=True,controls=controls,count=len(controls)))
    assert not torch.cuda.is_initialized() and not x.ARTIFACTS.exists()
    x.write('CPU-QUALIFICATION.json',dict(passed=True,interpreter=sys.executable,python=sys.version,packages=versions,
        eligible_records=54,presentations=216,reserved_diagnostics=24,exposed_calibrations=6,
        configuration_identity=x.identity(cfg),model_loads=0,inference_calls=0,backward_calls=0,
        optimizer_instances=0,scheduler_instances=0,optimizer_updates=0,scheduler_updates=0,cuda_initialized=False))
    print('PASS R6.75 numerical, dataset, evaluation, decoder, schedule, resource and adversarial controls')


def finish():
    x.guard()
    x.frozen_check()
    assert baseline() == x.read(x.OUT/'BASELINE.json')
    assert x.read(x.OUT/'CPU-QUALIFICATION.json')['passed']
    launch = x.read(x.OUT/'dry-launch/RESULT.json')
    assert launch['passed'] and launch['dry_run'] and not launch['training_outputs_claimed']
    for phase in launch['phases']:
        worker = json.loads((x.OUT/'dry-launch'/f"{phase['mode']}-stdout.txt").read_text(encoding='utf-8'))
        assert worker['pid'] == phase['pid'] and worker['dry_boundary_reached']
        resource.validate(worker['resource'],phase['pid'],17179869184)
        assert worker['configuration_identity'] == launch['configuration_identity']
        assert all(worker[k] == 0 for k in ('model_loads','inference_calls','backward_calls','optimizer_instances','scheduler_instances','optimizer_updates','scheduler_updates'))
    assert not x.ARTIFACTS.exists() and not (x.OUT/'execution').exists()
    x.write('TRAINING-READINESS.json',dict(ready=True,classification='R6_75_CONTRASTIVE_TRAINING_READY',
        all_three_defects_corrected=True,configuration_identity=launch['configuration_identity'],
        unresolved_configuration_dependencies=[],single_bounded_54_update_attempt_justified=True,
        execution_authorized=False,neutral_inference_qualified=False,model_learning='NOT_MEASURED',
        limitations=['CPU launch gate stops before actual model loading and CUDA execution.',
                    'GPU budgets and real training numerical behavior remain inherited, not newly exercised.',
                    'Compact live generation remains unqualified; exploratory diagnostics are not independently withheld.',
                    'RSS is sampled current resident memory, not hard OS containment or a peak between polls.',
                    'Unit identity/order obligations are structurally discriminated, not functionally separated.'],
        recommended_next_step='Separately authorize neutral compact inference and at most one fresh-adapter 54-update/216-presentation attempt; halt on any failure, no automatic retry.',
        kernel_constructs=26,production_unchanged=True,experimental_semantics_unchanged=True,
        historical_rescoring=0,p6_a04_acceptance=0,p6_a05_access=False,stopped=True))
    print('PASS R6.75 launch readiness receipt; stopped, execution not authorized')


if __name__ == '__main__':
    stage = sys.argv[1]
    try:
        {'prepare':prepare,'qualify':qualify,'finish':finish}[stage]()
    except BaseException as exc:
        if x.OUT.exists():
            x.write('HALT-'+stage+'.json',dict(error=str(exc),traceback=traceback.format_exc(),automatic_retry=False))
        raise
