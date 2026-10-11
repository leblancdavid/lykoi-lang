"""Prospective R6.66 integration. CPU preflight is the only authorized operation."""
import ast
import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = ROOT / 'benchmark/results/phase6/r6_66'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


old = load('r666_historical_helpers', 'experiments/incremental_training_r6_64/run.py')
successor = load('r666_successor', 'experiments/incremental_scorer_r6_65/scorer.py')
score = successor.score
c, q52, data = old.c, old.q52, old.data
STORE, PYTHON = old.STORE, old.PYTHON
ARTIFACTS = STORE / 'r6-66'
canonical, file_manifest, identity, read, sha = old.canonical, old.file_manifest, old.identity, old.read, old.sha
ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', CUDA_VISIBLE_DEVICES='',
           HF_HUB_OFFLINE='1', HF_HUB_DISABLE_TELEMETRY='1', TOKENIZERS_PARALLELISM='false')
LOCK = threading.RLock()


def write(name, value):
    with LOCK:
        OUT.mkdir(parents=True, exist_ok=True)
        path = OUT / name
        temporary = path.with_suffix(path.suffix + '.pending')
        temporary.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n',
                             encoding='utf-8', newline='\n')
        temporary.replace(path)


def rows():
    return read(OUT / 'DATASET.json')['records']


def publication(name):
    directory = ROOT / 'benchmark/results/phase6' / name
    manifest = read(directory / 'PUBLICATION-IDENTITIES.json')
    for path, entry in manifest['files'].items():
        assert sha(ROOT / path) == entry['sha256'], path
        assert (ROOT / path).stat().st_size == entry['bytes'], path
    assert sha(directory / 'PUBLICATION-IDENTITIES.json') == read(directory / 'VERIFICATION.json')['manifest_sha256']
    return dict(manifest_sha256=sha(directory / 'PUBLICATION-IDENTITIES.json'), files=len(manifest['files']))


def baseline():
    assert Path(sys.executable).resolve() == PYTHON.resolve()
    args = [str(PYTHON), str(ROOT / 'experiments/incremental_data_r6_63/publish.py'), 'baseline-check']
    proc = subprocess.run(args, cwd=ROOT, env=ENV, capture_output=True, text=True, timeout=600)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    rounds = {name: publication(name) for name in ('r6_59', 'r6_63', 'r6_64', 'r6_65')}
    supplement = read(ROOT / 'benchmark/results/phase6/r6_59/EXECUTABLE-IDENTITY-SUPPLEMENT.json')
    home = STORE / 'python/cpython-3.12.11-windows-x86_64-none'
    binaries = dict(python_executable_sha256=home/'python.exe', python_dll_sha256=home/'python312.dll',
                    venv_executable_sha256=PYTHON, uv_executable_sha256=STORE/'uv/uv.exe',
                    requirements_lock_sha256=ROOT/'benchmark/results/phase6/r6_52/requirements-lock.txt')
    assert {k: sha(p) for k, p in binaries.items()} == supplement['identities']
    assert not (old.OUT / 'PREFLIGHT.json').exists() and not old.ARTIFACTS.exists()
    return dict(rounds=rounds, executable_identities=supplement['identities'],
                inherited_audit=dict(argv=args, returncode=proc.returncode, stdout=proc.stdout, stderr=proc.stderr),
                kernel_constructs=26, kernel_basis='preserved accounting and implementation; not a new recount',
                historical_halt_preserved=True)


def varied_records():
    # Exact three prospective R6.64 cases, extracted without executing its freeze/scorer.
    text = (ROOT / 'experiments/incremental_training_r6_64/run.py').read_text(encoding='utf-8')
    tree = ast.parse(text)
    freeze = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'freeze')
    action = next(n for n in freeze.body if isinstance(n, ast.FunctionDef) and n.name == 'action')
    varied = next(n for n in freeze.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'varied' for t in n.targets))
    namespace = dict(data=data, make_record=old.make_record)
    module = ast.Module(body=[action, varied], type_ignores=[])
    exec(compile(module, 'unchanged-R6.64-prospective-diagnostics', 'exec'), namespace)
    return namespace['varied']


def encode(row, tokenizer):
    assert set(row) == {'episode_id', 'group', 'before', 'cases', 'prompt', 'completion'}
    assert [m['role'] for m in row['prompt']] == ['system', 'user']
    assert len(row['completion']) == 1 and row['completion'][0]['role'] == 'assistant'
    for message in row['prompt'] + row['completion']:
        assert set(message) == {'role', 'content'} and type(message['content']) is str and message['content']
        assert '<|im_start|>' not in message['content'] and '<|im_end|>' not in message['content']
    assert row['cases'] and score(row['completion'][0]['content'], row)['accepted']
    ids, labels, measurement = q52.encoded(row, tokenizer)
    assert len(ids) <= 2048
    prompt = tokenizer.apply_chat_template(row['prompt'], tokenize=False, add_generation_prompt=True)
    assert prompt.endswith('<|im_start|>assistant\n')
    pids = tokenizer(prompt, add_special_tokens=False)['input_ids']
    assert len(pids) + 128 <= 2048
    start = len(pids)
    end = start + measurement['supervised_tokens_including_eos']
    assert start > 0 and labels[start:end] == ids[start:end]
    assert ids[end-1] == tokenizer.eos_token_id
    assert sum(v != -100 for v in labels[1:]) == end-start
    # Unpadded microbatch1 is executable; independently qualify right-padding.
    attention = [1] * len(ids)
    padded_labels = labels + [-100] * (2048-len(ids))
    padded_ids = ids + [tokenizer.pad_token_id] * (2048-len(ids))
    padded_attention = attention + [0] * (2048-len(ids))
    assert len(padded_labels) == len(padded_ids) == len(padded_attention) == 2048
    assert all(label == -100 for label, mask in zip(padded_labels, padded_attention) if not mask)
    assert padded_attention[:len(ids)] == attention and sum(padded_attention) == len(ids)
    return dict(measurement, input_ids=ids, labels=labels, attention_mask=attention,
                input_identity=identity(ids), labels_identity=identity(labels),
                attention_identity=identity(attention), padded_labels_identity=identity(padded_labels),
                padded_input_identity=identity(padded_ids), padded_attention_identity=identity(padded_attention),
                target_start_inclusive=start, target_end_exclusive=end,
                causal_logit_positions=list(range(start-1, end-1)),
                generation_headroom=2048-start, assistant_generation_prefix='<|im_start|>assistant\n',
                effective_prompt_sha256=__import__('hashlib').sha256(prompt.encode()).hexdigest(),
                prompt_identity=identity(row['prompt']), padding_mask_pass=True, causal_alignment_pass=True)


def preflight():
    assert Path(sys.executable).resolve() == PYTHON.resolve()
    assert os.environ.get('CUDA_VISIBLE_DEVICES') == ''
    assert not OUT.exists() and not ARTIFACTS.exists() and ARTIFACTS.parent.is_dir()
    write('SOURCE-FREEZE.json', dict(files={p.relative_to(ROOT).as_posix(): sha(p) for p in sorted(HERE.glob('*.py'))},
                                   scope='CPU-only; no model/optimizer/scheduler dispatch'))
    try:
        write('BASELINE.json', baseline())
        records = []
        entries = []
        for index in range(1, 11):
            folder = data.OUT / 'episodes' / f'D{index:02d}'
            envelope = read(folder / 'B-RECORD-2.json')
            action = read(folder / 'ACTION.json')
            assert canonical(action).decode() == envelope['target']['text']
            assert envelope['provenance']['class'] == 'deterministic_expert_demonstration'
            row = old.make_record(f'R6.63/D{index:02d}', 'training_record', read(folder/'BEFORE.json'),
                                  read(folder/'SOURCE.json')['requirement'], action, read(folder/'ACCEPTANCE.json')['cases'])
            records.append(row)
            entries.append(dict(episode_id=row['episode_id'], canonical_record_identity=identity(row),
                                immutable_files={p.relative_to(ROOT).as_posix():dict(sha256=sha(p), bytes=p.stat().st_size)
                                                 for p in sorted(folder.glob('*.json'))}))
        assert records == read(old.OUT / 'DATASET.json')['records']
        dataset = dict(records=records, expansion=0, provenance='ten immutable R6.63 expert demonstrations')
        write('DATASET.json', dataset)
        write('DATASET-IDENTITIES.json', dict(records=entries, canonical_order=[r['episode_id'] for r in records],
              order_rule='immutable episode identity ascending D01 through D10', dataset_identity=identity(dataset),
              dataset_file_sha256=sha(OUT/'DATASET.json'), historical_conversion_sha256=sha(old.OUT/'DATASET.json')))
        sequence = [dict(episode_id=records[i % 10]['episode_id'], presentation=i+1,
                         optimizer_step=i//4+1, microbatch_in_step=i%4+1) for i in range(80)]
        sampling = dict(sequence=sequence, cycle=[r['episode_id'] for r in records], presentations=80,
                        counts={r['episode_id']:8 for r in records}, shuffle=False,
                        canonical_record_identities=[identity(r) for r in records], dataset_identity=identity(dataset))
        assert all(len([p for p in sequence if p['optimizer_step'] == s]) == 4 for s in range(1,21))
        assert [p['episode_id'] for p in sequence] == sampling['cycle'] * 8
        write('SAMPLING.json', sampling)
        diagnostics = records + varied_records()
        gold = []
        expected = []
        for row in diagnostics:
            result = score(row['completion'][0]['content'], row)
            assert result['accepted'], (row['episode_id'], result)
            action = successor.c.load(row['completion'][0]['content'])
            after, validation = successor.assembly.apply(row['before'], action)
            if row['group'] == 'training_record':
                folder = data.OUT/'episodes'/row['episode_id'].split('/')[-1]
                assert after == read(folder/'AFTER.json')
                assert validation == read(folder/'VALIDATION.json')['native']
            expected.append(dict(episode_id=row['episode_id'], group=row['group'], prompt_identity=identity(row['prompt']),
                                 operation=next(iter(action['node']['expr'])), operands=next(iter(action['node']['expr'].values())),
                                 dependencies=action['deps'], result_type=action['type'], action_identity=identity(action),
                                 assembled_after_identity=identity(after), native_validation_identity=identity(validation),
                                 functional_acceptance=row['cases'], assembly_behavior='unchanged R6.63 assembly.apply; exact pinned after and native validation',
                                 decoding_protocol='DIAGNOSTIC-PROTOCOL.json', output_limit_tokens=128,
                                 acceptance_dimensions=list(successor.DIMENSIONS)))
            gold.append(dict(episode_id=row['episode_id'], scores=result))
        write('DIAGNOSTICS.json', dict(records=diagnostics, expectations=expected, independent=False,
                                      reserved_family_used=False, training_diagnostics=10, varied_diagnostics=3))
        write('SCORER-GOLD.json', dict(records=gold, accepted=len(gold), fixtures=sum(len(r['scores']['observations']) for r in gold)))
        negatives = read(ROOT/'benchmark/results/phase6/r6_65/NEGATIVE-CONTROLS.json')
        controls = []
        mapping = {r['episode_id']:r for r in records}
        for control in negatives['records']:
            actual = score(control['input'], mapping[control['episode_id']])
            assert actual == control['scores'] and not actual['accepted']
            controls.append(dict(control, integrated_scores=actual))
        for control in negatives['direct_checker']:
            action = successor.c.load(records[1]['completion'][0]['content'])
            action['node']['expr']['add'][0]['const'] = control['literal']
            try:
                successor.validate_action(action)
            except successor.c.Diagnostic as exc:
                assert exc.data == control['error']
            else:
                raise AssertionError(control)
        assert importlib.util.find_spec('jsonschema') is None
        write('SCORER-INTEGRATION.json', dict(scorer_path='experiments/incremental_scorer_r6_65/scorer.py',
              scorer_sha256=sha(ROOT/'experiments/incremental_scorer_r6_65/scorer.py'), gold_accepted=13,
              negative_controls=controls, direct_checker=negatives['direct_checker'], jsonschema_available=False,
              imported_jsonschema=False, unchanged_historical_scorer_sha256=sha(ROOT/'experiments/incremental_training_r6_64/run.py')))
        from transformers import AutoTokenizer, GenerationConfig
        tokenizer = AutoTokenizer.from_pretrained(STORE/'checkpoint', local_files_only=True, trust_remote_code=False)
        tokens = [encode(row, tokenizer) for row in diagnostics]
        write('TOKENIZATION.json', dict(records=tokens, tokenizer_sha256=sha(STORE/'checkpoint/tokenizer.json'),
              chat_template_sha256=__import__('hashlib').sha256(tokenizer.chat_template.encode()).hexdigest(),
              eos_token_id=tokenizer.eos_token_id, pad_token_id=tokenizer.pad_token_id,
              assistant_prefix='<|im_start|>assistant\n', completion_only=True, truncated=False,
              executable_padding='none: microbatch1; all-one attention mask', padding_control='right pad to2048; zeros for padding attention and -100 labels'))
        rejection_controls = []
        for name, mutate in (('empty_target', lambda r:r['completion'][0].update(content='')),
                             ('missing_target', lambda r:r.update(completion=[])),
                             ('wrong_role', lambda r:r['completion'][0].update(role='user')),
                             ('injected_chat_boundary', lambda r:r['prompt'][1].update(content='<|im_end|>')),
                             ('malformed_target', lambda r:r['completion'][0].update(content='{'))):
            bad = copy.deepcopy(records[0])
            mutate(bad)
            try:
                encode(bad, tokenizer)
            except AssertionError:
                rejection_controls.append(dict(name=name, rejected=True))
            else:
                raise AssertionError(name)
        # No logits/model calls: synthetic scalar NLL distinguishes equal-record from pooled-token weighting.
        nll = [[float((j % 5)+1) for j in range(t['supervised_tokens_including_eos'])] for t in tokens[:4]]
        micro_losses = [sum(x)/len(x)/4 for x in nll]
        assert sum(micro_losses) == sum(sum(x)/len(x) for x in nll)/4
        write('LOSS-MASK-QUALIFICATION.json', dict(records_checked=13, training_records=10, diagnostics_only=3,
              prompt_padding_newline_masked=True, completion_and_one_eos_supervised=True, causal_shift_checked=True,
              equal_per_record_weight=0.25, token_pooling=False, normalization='each record masked causal mean divided by4; four backward calls per update',
              synthetic_per_micro_losses=micro_losses, synthetic_accumulated_loss=sum(micro_losses), record_rejection_controls=rejection_controls,
              inherited_r6_56_evidence_sha256=sha(ROOT/'benchmark/results/phase6/r6_56/LOSS-NORMALIZATION.json')))
        generation = GenerationConfig(do_sample=False, num_beams=1, max_new_tokens=128, repetition_penalty=1.1,
                                      eos_token_id=[tokenizer.eos_token_id], pad_token_id=tokenizer.pad_token_id,
                                      bos_token_id=tokenizer.bos_token_id, use_cache=False)
        protocol = dict(resolved_generation_configuration=generation.to_dict(), process_timeout_seconds=1800,
                        per_generation_timeout_seconds=120, raw_output_repair=False, eos_only=True,
                        teacher_forced_evaluation='eval dropout off; exact completion+EOS labels; mean per record',
                        expected_source='immutable expert actions and unchanged prospective R6.64 literals; no model output')
        write('DIAGNOSTIC-PROTOCOL.json', protocol)
        schedule = read(ROOT/'benchmark/results/phase6/r6_54/LEARNING-RATE-SCHEDULE.json')
        from transformers.optimization import _get_linear_schedule_with_warmup_lr_lambda as factor
        simulation = []
        for s in range(1,21):
            used = 1e-4 * factor(s-1, num_warmup_steps=2, num_training_steps=20)
            after = 1e-4 * factor(s, num_warmup_steps=2, num_training_steps=20)
            assert used == schedule['sequence'][s-1]['lr_used_by_update']
            assert after == schedule['sequence'][s-1]['lr_after_scheduler_step']
            simulation.append(dict(step=s, used=used, after=after, presentations=4*s))
        write('SCHEDULER-SIMULATION.json', dict(sequence=simulation, passed=True, optimizer_instances=0,
              scheduler_instances=0, optimizer_step_calls=0, scheduler_step_calls=0, inherited_sha256=sha(ROOT/'benchmark/results/phase6/r6_54/LEARNING-RATE-SCHEDULE.json')))
        worker = load('r666_worker_builder', 'experiments/incremental_training_r6_66/worker.py')
        source = worker.effective_source()
        compile(source, 'R6.66-effective-worker', 'exec')
        (OUT/'EFFECTIVE-WORKER.py.txt').write_text(source, encoding='utf-8', newline='\n')
        config = copy.deepcopy(read(ROOT/'benchmark/results/phase6/r6_59/TRAINING-CONFIGURATION.json')['configuration'])
        config['adapter_configuration']['inference_mode'] = False
        config.update(round='R6.66', initialization='original R6.52 base; seed651 fresh q/v LoRA; never R6.59 adapter',
                      training_episodes=[r['episode_id'] for r in records],
                      training_record_sampling_order='immutable D01-D10 order; eight cyclic passes; no shuffle',
                      dataset_identity=identity(dataset), dataset_file_sha256=sha(OUT/'DATASET.json'),
                      dataset_identities_sha256=sha(OUT/'DATASET-IDENTITIES.json'), sampling_identity=identity(sampling),
                      diagnostic_manifest_sha256=sha(OUT/'DIAGNOSTICS.json'), diagnostic_protocol_identity=identity(protocol),
                      decoding_settings=protocol, scorer_sha256=sha(ROOT/'experiments/incremental_scorer_r6_65/scorer.py'),
                      tokenizer_identities=read(ROOT/'benchmark/results/phase6/r6_52/CHECKPOINT.json')['files'],
                      model_identities=read(ROOT/'benchmark/results/phase6/r6_52/CHECKPOINT.json')['files'],
                      quantization_configuration=read(ROOT/'benchmark/results/phase6/r6_52/BACKWARD.json')['quantization'],
                      model_local_directory=str(STORE/'checkpoint'), training_interpreter=str(PYTHON),
                      executable_identities=read(OUT/'BASELINE.json')['executable_identities'],
                      loss_mask_evidence_sha256=sha(OUT/'LOSS-MASK-QUALIFICATION.json'), tokenization_sha256=sha(OUT/'TOKENIZATION.json'),
                      cache_release=read(ROOT/'benchmark/results/phase6/r6_59/CACHE-RELEASE-QUALIFICATION.json'),
                      cache_release_evidence_sha256=sha(ROOT/'benchmark/results/phase6/r6_59/CACHE-RELEASE-QUALIFICATION.json'),
                      worker_sha256=sha(OUT/'EFFECTIVE-WORKER.py.txt'), checkpoint_output_root=str(ARTIFACTS),
                      checkpoint_output_paths=[str(ARTIFACTS/f'step{s}') for s in (10,20)],
                      logging=dict(directory=str(OUT), per_presentation=True, per_update=True, raw_diagnostics=True,
                                   memory_poll_seconds=0.1, overwrite_policy='atomic telemetry replacement; exclusive dispatch/run/checkpoint claims'),
                      recovery=dict(automatic_resume=False, retry=False, failure='retain raw traceback/accounting; halt; require new authorization',
                                    checkpoint_state='optimizer/scheduler/Python+torch CPU+CUDA RNG; diagnostic paired reference'),
                      resolved_choices=dict(adapter_inference_mode='false for fresh training; saved inference mode is not training mode',
                                            padding_side='right for mask controls; executable unpadded microbatch1',
                                            additional_rng='Python and torch seed651; no numpy/random data transformations',
                                            diagnostic_output='strict raw JSON; strip terminal EOS only; no output repair'),
                      unresolved_training_critical_settings=[])
        assert config['weight_decay'] == config['optimizer_configuration']['kwargs']['weight_decay'] == 0
        assert config['planned_optimizer_steps'] == 20 and config['gradient_accumulation'] == 4
        write('TRAINING-CONFIGURATION.json', dict(configuration=config, canonical_sha256=identity(config)))
        probe = ARTIFACTS.parent / 'r6-66-output-path-probe.tmp'
        assert not probe.exists()
        with probe.open('x', encoding='utf-8') as stream:
            stream.write('R6.66 CPU-only output path qualification\n')
        assert probe.read_text(encoding='utf-8') == 'R6.66 CPU-only output path qualification\n'
        probe.unlink()
        write('OUTPUT-PATHS.json', dict(parent=str(ARTIFACTS.parent), parent_exists=True, root=str(ARTIFACTS), root_absent=True,
              historical_roots_distinct=all(ARTIFACTS != STORE/name for name in ('r6-59','r6-64','untrained-adapter','checkpoint')),
              output_paths=config['checkpoint_output_paths'], write_probe='exclusive file create/read/delete in intended output parent passed; model output directory not created',
              checkpoint_claim='mkdir exist_ok=False', recovery=config['recovery']))
        files = list(OUT.glob('*')) + list(HERE.glob('*.py'))
        freeze = dict(status='PASS', training_configuration_identity=identity(config),
                      frozen_payloads={p.relative_to(ROOT).as_posix():sha(p) for p in sorted(files)},
                      optimizer_updates_planned=20, unresolved_training_critical_settings=[], attempts_authorized=0)
        write('PREFLIGHT.json', freeze)
        frozen_check()
        mandatory = ('baseline', 'dataset_conversion', 'sampling', 'tokenization', 'loss_masks', 'scheduler_simulation',
                     'scorer_integration', 'scorer_gold', 'scorer_negative', 'diagnostics', 'configuration', 'output_paths', 'effective_worker')
        write('CPU-QUALIFICATION.json', dict(components={k:'QUALIFIED' for k in mandatory}, pinned_interpreter=sys.executable,
              python_version=sys.version, cuda_visible_devices=os.environ['CUDA_VISIBLE_DEVICES'],
              model_loads=0, model_inference=0, optimizer_updates=0, scheduler_updates=0, fine_tuning=0,
              dataset_expansion=0, diagnostic_cases=13, diagnostic_fixtures=sum(len(r['cases']) for r in diagnostics),
              training_presentations=80, per_record_presentations=8, negative_controls=len(controls), direct_checker_controls=6,
              training_lengths=[t['sequence_tokens'] for t in tokens[:10]], training_supervised_tokens=[t['supervised_tokens_including_eos'] for t in tokens[:10]],
              minimum_diagnostic_headroom=min(t['generation_headroom'] for t in tokens), gpu_runtime='inherited qualification; not retested', passed=True))
        write('TRAINING-READINESS.json', dict(classification='R6_66_INCREMENTAL_TRAINING_READY', ready=True,
              components={k:'QUALIFIED' for k in mandatory}, training_configuration_identity=identity(config),
              dataset_identity=identity(dataset), sampling_identity=identity(sampling), scorer_integrated=True,
              diagnostic_manifest_sha256=sha(OUT/'DIAGNOSTICS.json'), blockers=[], fresh_20_step_attempt_justified=True,
              dispatch_authorized=False, scope='CPU preflight readiness only; no GPU training success or model learning claim'))
        print(json.dumps(read(OUT/'CPU-QUALIFICATION.json'), indent=2))
    except BaseException as exc:
        write('PREFLIGHT-FAILURE.json', dict(error=str(exc), traceback=__import__('traceback').format_exc(),
                                          classification='R6_66_PROTOCOL_HALT', model_calls=0, optimizer_updates=0, scheduler_updates=0))
        raise


def frozen_check():
    freeze = read(OUT/'PREFLIGHT.json')
    for path, digest in freeze['frozen_payloads'].items():
        assert sha(ROOT/path) == digest, path
    config = read(OUT/'TRAINING-CONFIGURATION.json')
    assert identity(config['configuration']) == config['canonical_sha256'] == freeze['training_configuration_identity']
    for name in ('r6_59', 'r6_63', 'r6_64', 'r6_65'):
        publication(name)
    return freeze


def dispatch(mode, authorization):
    # Implemented for the next explicitly authorized experiment; never used by preflight.
    assert authorization == '--explicit-owner-authorization', 'separate owner authorization required'
    assert Path(sys.executable).resolve() == PYTHON.resolve()
    frozen_check()
    assert read(OUT/'TRAINING-READINESS.json')['ready']
    baseline()
    if mode == 'train':
        assert read(OUT/'DIAGNOSTIC-BASE.json')['status'] == 'PASS'
    if mode in ('reload', 'adapter'):
        assert read(OUT/'TRAINING-RESULT.json')['status'] == 'PASS'
    if mode == 'adapter':
        assert read(OUT/'ADAPTER-RELOAD.json')['status'] == 'PASS'
    with (OUT/f'{mode.upper()}-DISPATCH-CLAIM.json').open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(dict(mode=mode, attempts=1))+'\n')
    ARTIFACTS.mkdir(exist_ok=mode != 'base')
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', HF_HUB_OFFLINE='1', HF_HUB_DISABLE_TELEMETRY='1',
               HF_HOME=str(STORE/'hf-cache'), TOKENIZERS_PARALLELISM='false', LYKOI_R6_66_AUTHORIZED='1')
    env.pop('CUDA_VISIBLE_DEVICES', None)
    args = [str(PYTHON), str(HERE/'worker.py'), mode]
    start = time.perf_counter()
    try:
        proc = subprocess.run(args, cwd=ROOT, env=env, capture_output=True, text=True,
                              timeout=120 if mode == 'reload' else 1800)
        packet = dict(argv=args, returncode=proc.returncode, stdout=proc.stdout, stderr=proc.stderr)
    except subprocess.TimeoutExpired as exc:
        packet = dict(argv=args, returncode=None, stdout=str(exc.stdout), stderr=str(exc.stderr), error='PROCESS_TIMEOUT')
    write(mode.upper()+'-PROCESS.json', dict(packet, seconds=time.perf_counter()-start))
    assert packet['returncode'] == 0, 'single dispatch halted; no retry'


if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'preflight':
        preflight()
    elif mode == 'check':
        frozen_check()
        print('PASS R6.66 frozen configuration and payload identities')
    elif mode in ('base', 'train', 'reload', 'adapter'):
        dispatch(mode, sys.argv[2] if len(sys.argv) > 2 else '')
    else:
        raise ValueError(mode)
