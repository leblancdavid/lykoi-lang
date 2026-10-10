"""R6.56 preflight freeze and externally bounded one-shot worker dispatch."""
import copy
import importlib.util
import inspect
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from common import ARTIFACTS, OUT, PYTHON, ROOT, STORE, canonical, frozen_check, identity, read, rows, rss, score, sha, write


def inherited():
    spec = importlib.util.spec_from_file_location('r55', ROOT / 'experiments/lora_smoke_r6_55/publication.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def numerical_control():
    import torch
    from transformers.loss.loss_utils import ForCausalLMLoss
    w = torch.tensor(0.37, dtype=torch.float64, requires_grad=True)
    losses = []
    for count, target in zip((1, 2, 3, 4), (0, 1, 0, 1)):
        logits = torch.stack((w, -w)).view(1, 1, 2).repeat(1, count + 2, 1)
        labels = torch.tensor([[-100] + [target] * count + [-100]])
        loss = ForCausalLMLoss(logits, labels, vocab_size=2)
        losses.append(float(loss))
        (loss / 4).backward()
    accumulated = float(w.grad)
    v = torch.tensor(0.37, dtype=torch.float64, requires_grad=True)
    # Independent selected-token expression, without the installed causal-loss helper.
    log_probs = torch.log_softmax(torch.stack((v, -v)), dim=0)
    record_losses = [-log_probs[t] for t in (0, 1, 0, 1)]
    equal = sum(record_losses) / 4
    equal.backward()
    independent = float(v.grad)
    pooled = sum(float(l) * n for l, n in zip(record_losses, (1, 2, 3, 4))) / 10
    assert abs(sum(losses) / 4 - float(equal)) < 1e-6
    assert abs(accumulated - independent) < 1e-6
    assert abs(pooled - float(equal)) > 0.01
    return {'status': 'PASS', 'record_supervised_counts': [1, 2, 3, 4], 'record_mean_losses': losses,
            'accumulated_equal_record_mean': sum(losses) / 4, 'independent_equal_record_mean': float(equal),
            'pooled_token_mean_negative_control': pooled, 'accumulated_gradient': accumulated,
            'independent_gradient': independent, 'gradient_tolerance': 1e-6,
            'loss_helper_source': inspect.getsource(ForCausalLMLoss),
            'loss_helper_module_sha256': sha(Path(inspect.getfile(ForCausalLMLoss))),
            'specification': 'Per record causal-shifted completion+EOS cross-entropy mean, ignored labels -100; backward loss/4; no num_items_in_batch; four backward calls per clipped optimizer update.',
            'model_optimizer_steps': 0}


def freeze():
    assert not (OUT / 'PREFLIGHT.json').exists(), 'already frozen; do not overwrite'
    assert ARTIFACTS.parent.is_dir() and not ARTIFACTS.exists()
    r55 = inherited()
    previous = {str(n): r55.r53.identities(ROOT / f'benchmark/results/phase6/r6_{n}') for n in (52, 53, 54, 55)}
    r55.r53.write = lambda name, value: write('SOURCE-' + name, value)
    r55.r53.preflight()
    import torch
    from transformers import GenerationConfig
    from transformers.optimization import get_linear_schedule_with_warmup
    optimizer = read(ROOT / 'benchmark/results/phase6/r6_55/OPTIMIZER-CONFIGURATION.json')
    assert identity(optimizer['configuration']) == optimizer['canonical_sha256']
    assert str(inspect.signature(torch.optim.AdamW)) == optimizer['installed_signature']
    assert sha(Path(inspect.getfile(torch.optim.AdamW))) == optimizer['implementation_file_sha256']
    write('OPTIMIZER-CONFIGURATION.json', optimizer)
    schedule = read(ROOT / 'benchmark/results/phase6/r6_54/LEARNING-RATE-SCHEDULE.json')
    assert sha(Path(inspect.getfile(get_linear_schedule_with_warmup))) == schedule['scheduler_module_sha256']
    assert inspect.getsource(get_linear_schedule_with_warmup) == schedule['scheduler_constructor_source']
    from fractions import Fraction
    for step, entry in enumerate(schedule['sequence'], 1):
        before = Fraction(step - 1, 2) if step < 3 else Fraction(21 - step, 18)
        after = Fraction(step, 2) if step < 2 else Fraction(20 - step, 18)
        assert entry['lr_used_by_update'] == 1e-4 * float(before)
        assert entry['lr_after_scheduler_step'] == 1e-4 * float(after)
    sequence = [{'presentation': i + 1, 'optimizer_step': i // 4 + 1, 'microbatch_in_step': i % 4 + 1,
                 'episode_id': f'R6.48/E{i % 6 + 1:02d}'} for i in range(80)]
    sampling = {'sequence': sequence, 'shuffle': False, 'start': 'E01', 'cycle': ['E01', 'E02', 'E03', 'E04', 'E05', 'E06'],
                'optimizer_steps': 20, 'microbatches_per_step': 4, 'presentation_count': 80}
    write('SAMPLING.json', dict(sampling, canonical_sha256=identity(sampling)))
    write('LOSS-NORMALIZATION.json', numerical_control())
    selected = rows()
    schema = read(ROOT / 'experiments/typed_composition_r6_18/typed-composition-1.schema.json')
    controls = []
    for row in selected:
        result = score(row['completion'][0]['content'], row)
        assert result['schema_valid'] and result['type_valid'] is True and result['semantic_valid'] and result['functional_acceptance']
        bad = copy.deepcopy(json.loads(row['completion'][0]['content']))
        bad['program']['result_type'] = 'wrong'
        rejected = score(json.dumps(bad), row)
        assert not rejected['schema_valid'] and not rejected['semantic_valid']
        duplicate = score('{"version":1,"version":2}', row)
        assert not duplicate['output_valid']
        controls.append({'episode_id': row['episode_id'], 'target_schema_type_semantics_acceptance': 'PASS',
                         'functional_cases': len(result['functional_cases']), 'bad_type_and_duplicate_rejected': True})
    write('SCORER-CONTROLS.json', {'status': 'PASS', 'records': controls,
          'scope': 'prospective scorer qualification on six admitted targets; historical scores unchanged'})
    generation = GenerationConfig.from_pretrained(STORE / 'checkpoint', local_files_only=True)
    generation.do_sample = False
    generation.max_new_tokens = 1400
    generation.num_return_sequences = 1
    # Retain all other pinned checkpoint generation settings, including repetition_penalty1.1.
    # Cache-off matches the existing load path; no custom stop/repair/seal assistance.
    protocol = {'round': 'R6.56', 'items': [{'episode_id': r['episode_id'], 'prompt': r['prompt'],
                    'prompt_identity': identity(r['prompt']), 'target_identity': identity(r['completion']),
                    'acceptance_path': r['provenance']['source_refs']['ACCEPTANCE.json']['path'],
                    'acceptance_sha256': r['provenance']['source_refs']['ACCEPTANCE.json']['sha256']} for r in selected],
                'source_protocol_sha256': sha(ROOT / 'benchmark/results/phase6/r6_51/SMOKE-AND-EVALUATION.md'),
                'resolved_generation_configuration': generation.to_dict(), 'max_total_tokens': 2048,
                'per_call_timeout_seconds': 120, 'timeout_includes_process_load': True, 'use_cache': False,
                'repair_calls': 0, 'seal_tool_calls': 0, 'raw_output_only': True,
                'type_reporting': 'True on native validation pass or final identity-content mismatch after all closed-program type checks; False on TYPE; otherwise NOT_REACHED',
                'schema_path': 'experiments/typed_composition_r6_18/typed-composition-1.schema.json',
                'schema_sha256': sha(ROOT / 'experiments/typed_composition_r6_18/typed-composition-1.schema.json'),
                'independent_or_unseen': False, 'classification': 'training-record resubstitution',
                'comparison_checkpoint': 'final step20 only; no selection on diagnostic results'}
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(STORE / 'checkpoint', local_files_only=True, trust_remote_code=False)
    for r in selected:
        prompt = tokenizer.apply_chat_template(r['prompt'], tokenize=False, add_generation_prompt=True)
        assert len(tokenizer(prompt, add_special_tokens=False).input_ids) + 1400 <= 2048
    write('DIAGNOSTIC-PROTOCOL.json', dict(protocol, canonical_sha256=identity(protocol)))
    config = read(ROOT / 'benchmark/results/phase6/r6_55/TRAINING-CONFIGURATION.json')['configuration']
    config.pop('blocking_fields')
    config.update(round='R6.56', status='COMPLETE', executable_training_configuration_frozen=True,
                  training_record_sampling_order='fixed E01-E06 cycle starting E01, no shuffle,80 presentations',
                  sampling_identity=identity(sampling),
                  gradient_accumulation_loss_normalization='per-record mean completion+EOS loss /4, four backward calls',
                  initialization='seed651; exact R6.52 initial adapter tensors required before first update',
                  initial_adapter_manifest_sha256=sha(ROOT / 'benchmark/results/phase6/r6_52/BACKWARD.json'),
                  adapter_configuration=read(ROOT / 'benchmark/results/phase6/r6_52/BACKWARD.json')['adapter_config'],
                  adapter_parameter_dtype='float32', model_forward_autocast=False, gradient_scaler=False,
                  model_loss='installed ForCausalLMLoss; no num_items_in_batch; verified causal shift/masked mean',
                  loss_normalization_evidence_sha256=sha(OUT / 'LOSS-NORMALIZATION.json'),
                  gradient_clip={'max_norm': 1, 'norm_type': 2, 'error_if_nonfinite': True, 'foreach': None},
                  zero_grad_set_to_none=True, checkpoint_steps=[10, 20], checkpoint_retention=2,
                  training_process_timeout_seconds=1800, external_rss_poll_seconds=0.1, cuda_memory_poll_seconds=0.1,
                  diagnostic_protocol_identity=identity(protocol), adapter_merge=False,
                  precision_runtime={'allow_tf32_matmul': torch.backends.cuda.matmul.allow_tf32,
                                     'allow_tf32_cudnn': torch.backends.cudnn.allow_tf32,
                                     'float32_matmul_precision': torch.get_float32_matmul_precision(),
                                     'deterministic_algorithms': torch.are_deterministic_algorithms_enabled()})
    write('TRAINING-CONFIGURATION.json', {'configuration': config, 'canonical_sha256': identity(config)})
    # Readiness check uses device capability/free-memory query only, no model allocation.
    assert torch.cuda.is_available() and torch.cuda.is_bf16_supported()
    free, total = torch.cuda.mem_get_info()
    assert free >= config['limits']['minimum_device_free_bytes']
    paths = list(Path(__file__).parent.glob('*.py')) + list(OUT.glob('*.json'))
    write('PREFLIGHT.json', {'round': 'R6.56', 'status': 'PASS', 'previous_publications': previous,
          'training_configuration_identity': identity(config), 'sampling_identity': identity(sampling),
          'optimizer_identity': optimizer['canonical_sha256'], 'scheduler_identity': config['scheduler_manifest_sha256'],
          'frozen_payloads': {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted(paths)},
          'completion_only_masks': 'PASS; six regenerated records and inherited numerical mask qualification',
          'normalization': 'PASS', 'scorer_controls': 'PASS', 'genuinely_missing_training_parameters': [],
          'model_loaded': False, 'model_optimizer_steps': 0, 'device_free_bytes': free, 'device_total_bytes': total,
          'kernel_constructs': 26, 'P6_A04_acceptance_executions': 0, 'P6_A05_content_access': False})
    print('PASS complete configuration,80-presentation cycle, equal-record normalization, identities and diagnostic controls', flush=True)


def dispatch(name, args, timeout):
    frozen_check()
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    start = time.perf_counter()
    stdout_path = ARTIFACTS / (name + '.stdout')
    stderr_path = ARTIFACTS / (name + '.stderr')
    assert not stdout_path.exists() and not stderr_path.exists(), 'dispatch already attempted'
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', HF_HUB_OFFLINE='1', HF_HUB_DISABLE_TELEMETRY='1',
               HF_HOME=str(STORE / 'hf-cache'))
    argv = [str(PYTHON), str(Path(__file__).parent / 'worker.py'), *args]
    aborted = None
    peak_rss = 0
    samples = 0
    missing_samples = 0
    with stdout_path.open('w', encoding='utf-8') as stdout, stderr_path.open('w', encoding='utf-8') as stderr:
        process = subprocess.Popen(argv, cwd=ROOT, env=env, stdout=stdout, stderr=stderr)
        while process.poll() is None:
            current_rss = rss(process.pid)
            samples += 1
            if current_rss is None:
                missing_samples += 1
            else:
                peak_rss = max(peak_rss, current_rss)
            if time.perf_counter() - start > timeout:
                aborted = 'PROCESS_WALL_TIMEOUT'
            elif peak_rss > 17179869184:
                aborted = 'PROCESS_RSS_LIMIT'
            if aborted:
                process.kill()
                break
            time.sleep(0.1)
        returncode = process.wait()
    packet = {'argv': argv, 'returncode': returncode, 'seconds': time.perf_counter() - start,
              'stdout': stdout_path.read_text(encoding='utf-8'), 'stderr': stderr_path.read_text(encoding='utf-8'),
              'external_abort': aborted, 'peak_sampled_rss_bytes': peak_rss, 'rss_samples': samples,
              'rss_query_missing_samples': missing_samples, 'timeout_seconds': timeout}
    write(name + '-PROCESS.json', packet)
    print(name, returncode, packet['stdout'], packet['stderr'], flush=True)
    return packet


def diagnostics(track):
    if track == 'adapter':
        assert read(OUT / 'ADAPTER-RELOAD.json')['status'] == 'PASS'
    results = []
    for i in range(6):
        name = f'DIAGNOSTIC-{track.upper()}-E{i+1:02d}'
        packet = dispatch(name, ['diagnostic', track, str(i)], 120)
        if packet['returncode'] or not (OUT / (name + '.json')).exists():
            write(name + '.json', {'status': 'FAILED_OR_TIMEOUT', 'episode_id': f'R6.48/E{i+1:02d}', 'track': track,
                  'returncode': packet['returncode'], 'reason': packet['external_abort'], 'scores': None,
                  'output_tokens': None, 'inference_seconds': None})
        results.append(read(OUT / (name + '.json')))
    scored = [r for r in results if r['scores'] is not None]
    metrics = ('output_valid', 'schema_valid', 'type_valid', 'semantic_valid', 'functional_acceptance',
               'exact_target_match', 'normalized_target_match')
    summary = {metric: {'passed': sum(r['scores'][metric] is True for r in scored), 'requests': 6,
                       'observed': sum(type(r['scores'][metric]) is bool for r in scored)} for metric in metrics}
    write(f'DIAGNOSTIC-{track.upper()}-SUMMARY.json', {'track': track, 'results': results, 'metrics': summary,
          'completed_calls': len(scored), 'attempted_calls': 6,
          'output_tokens': sum(r['output_tokens'] for r in scored),
          'inference_seconds': sum(r['inference_seconds'] for r in scored),
          'independent_generalization': False, 'repair_calls': 0, 'seal_tool_calls': 0})


if __name__ == '__main__':
    os.environ['HF_HUB_OFFLINE'] = '1'
    os.environ['HF_HUB_DISABLE_TELEMETRY'] = '1'
    mode = sys.argv[1]
    if mode == 'freeze':
        freeze()
    elif mode == 'baseline':
        diagnostics('base')
    elif mode == 'train':
        assert read(OUT / 'DIAGNOSTIC-BASE-SUMMARY.json')['attempted_calls'] == 6
        packet = dispatch('TRAINING', ['train'], 1800)
        if packet['returncode']:
            raise RuntimeError('single training attempt halted; do not restart')
    elif mode == 'reload':
        assert read(OUT / 'TRAINING-RESULT.json')['status'] == 'PASS'
        packet = dispatch('RELOAD', ['reload'], 120)
        assert packet['returncode'] == 0
    elif mode == 'post':
        diagnostics('adapter')
    else:
        raise ValueError('unknown mode')
