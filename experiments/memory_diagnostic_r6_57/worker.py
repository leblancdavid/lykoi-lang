"""Same frozen four-microbatch training path, instrumented; updates forbidden."""
import gc
import os
import threading
import time
import traceback
import weakref
from run import HERE, OUT, ROOT, baseline, c, write
import importlib.util

spec = importlib.util.spec_from_file_location('frozen_r56_worker', ROOT / 'experiments/lora_smoke_r6_56/worker.py')
frozen_worker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(frozen_worker)

os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['HF_HUB_DISABLE_TELEMETRY'] = '1'


def diagnostic():
    import torch
    from peft import LoraConfig, get_peft_model
    from transformers import AutoTokenizer
    from transformers.optimization import get_linear_schedule_with_warmup
    freeze = c.read(OUT / 'PREFLIGHT.json')
    assert c.sha(HERE / 'worker.py') == freeze['worker_sha256']
    assert baseline() == c.read(OUT / 'BASELINE.json')
    with (OUT / 'WORKER-CLAIM.json').open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(c.canonical({'pid': os.getpid(), 'executable': __import__('sys').executable}).decode() + '\n')
    GiB = 1024 ** 3
    free, total = torch.cuda.mem_get_info()
    initial_reserved = torch.cuda.memory_reserved()
    # Verified current availability minus frozen1.5GiB free floor and extra0.5GiB margin.
    ceiling = min(10 * GiB, initial_reserved + free - 2 * GiB)
    assert ceiling > 8 * GiB, 'NO_SAFE_DIAGNOSTIC_HEADROOM'
    safety = {'device_name': torch.cuda.get_device_name(), 'device_total_bytes': total,
              'initial_device_free_bytes': free, 'initial_reserved_bytes': initial_reserved,
              'original_reference_bytes': 8 * GiB, 'diagnostic_allocator_ceiling_bytes': ceiling,
              'minimum_device_free_bytes': int(1.5 * GiB), 'extra_preflight_margin_bytes': int(0.5 * GiB),
              'ceiling_formula': 'min(10GiB, initial_reserved+verified_free-2GiB)',
              'allocator_hard_cap': 'torch.cuda.set_per_process_memory_fraction(ceiling/total)',
              'free_memory_watchdog_seconds': 0.05, 'rss_limit_bytes': 16 * GiB,
              'limitation': 'allocator cap excludes non-PyTorch allocations; free-memory watchdog is sampled, not device reservation isolation'}
    write('RESOURCE-SAFETY.json', safety)
    torch.cuda.set_per_process_memory_fraction(ceiling / total)
    # One reset before model loading; all peaks are cumulative through the whole worker.
    torch.cuda.reset_peak_memory_stats()
    boundaries = []
    gradients = []
    stop = threading.Event()

    def values(sync=False):
        if sync:
            torch.cuda.synchronize()
        free_now, total_now = torch.cuda.mem_get_info()
        stats = torch.cuda.memory_stats()
        return {'allocated_bytes': torch.cuda.memory_allocated(), 'reserved_bytes': torch.cuda.memory_reserved(),
                'peak_allocated_bytes': torch.cuda.max_memory_allocated(), 'peak_reserved_bytes': torch.cuda.max_memory_reserved(),
                'device_free_bytes': free_now, 'device_total_bytes': total_now,
                'worker_rss_bytes': c.rss(os.getpid()),
                'allocator_stats': {k: stats.get(k) for k in ('active_bytes.all.current', 'inactive_split_bytes.all.current',
                    'inactive_split_bytes.all.peak', 'allocation.all.current', 'num_alloc_retries', 'num_ooms')}}

    def check(v):
        assert v['reserved_bytes'] <= ceiling, 'DIAGNOSTIC_CEILING'
        assert v['device_free_bytes'] >= int(1.5 * GiB), 'DEVICE_FREE_LIMIT'
        assert v['worker_rss_bytes'] is not None and v['worker_rss_bytes'] <= 16 * GiB, 'WORKER_RSS_LIMIT'

    def measure(boundary, micro=0, extra=None):
        v = values(True)
        boundaries.append(dict(v, boundary=boundary, microbatch=micro, **(extra or {})))
        write('MEMORY-TRACE.json', {'peak_reset': 'once before model loading; no per-microbatch resets', 'boundaries': boundaries})
        check(v)
        return v

    def watchdog():
        while not stop.wait(0.05):
            try:
                v = values()
                check(v)
            except BaseException as exc:
                write('SAFETY-STOP.json', {'error': str(exc), 'values': v, 'pid': os.getpid()})
                os._exit(71)

    monitor = threading.Thread(target=watchdog, daemon=True)
    monitor.start()
    try:
        c.q52.seed()
        base, quant = frozen_worker.prepare_base()
        lora = LoraConfig(r=8, lora_alpha=16, lora_dropout=0.05, target_modules=['q_proj', 'v_proj'],
                         bias='none', task_type='CAUSAL_LM', base_model_name_or_path=c.q52.REPO, revision=c.q52.REVISION)
        model = get_peft_model(base, lora)
        model.peft_config['default'].base_model_name_or_path = c.q52.REPO
        model.peft_config['default'].revision = c.q52.REVISION
        measure('after_model_loading')
        initial = frozen_worker.adapter_manifest(model)
        assert initial == c.read(ROOT / 'benchmark/results/phase6/r6_52/BACKWARD.json')['adapter_tensor_manifest']
        base_before = frozen_worker.base_manifest(model)
        write('INITIAL-PARAMETERS.json', {'adapter': initial, 'base': base_before})
        named = {n: p for n, p in model.named_parameters() if p.requires_grad}
        assert len(named) == 112 and sum(p.numel() for p in named.values()) == 1089536
        assert all('lora_' in n for n in named)
        config = c.read(c.OUT / 'TRAINING-CONFIGURATION.json')['configuration']
        kwargs = dict(config['optimizer_configuration']['kwargs'])
        kwargs['betas'] = tuple(kwargs['betas'])
        optimizer = torch.optim.AdamW(list(named.values()), **kwargs)
        scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=2, num_training_steps=20)
        assert not optimizer.state and scheduler.last_epoch == 0 and optimizer.param_groups[0]['lr'] == 0
        scheduler_before = scheduler.state_dict()
        def forbidden(*args, **kwargs):
            raise RuntimeError('OPTIMIZER_OR_SCHEDULER_UPDATE_FORBIDDEN')
        optimizer.step = forbidden
        scheduler.step = forbidden
        tokenizer = AutoTokenizer.from_pretrained(c.STORE / 'checkpoint', local_files_only=True, trust_remote_code=False)
        samples = {r['episode_id']: (r, *c.q52.encoded(r, tokenizer)) for r in c.rows()}
        expected_records = c.read(c.OUT / 'SOURCE-DATASET-IDENTITIES.json')['records']
        import hashlib
        for eid, (_, ids, labels, measurement) in samples.items():
            record = next(r for r in expected_records if r['episode_id'] == eid)
            assert hashlib.sha256(__import__('json').dumps(ids).encode()).hexdigest() == record['tokens_sha256']
            assert hashlib.sha256(__import__('json').dumps(labels).encode()).hexdigest() == record['labels_sha256']
            assert measurement == record['tokenization']
        # Detached CPU hook copies are independent evidence of additive leaf accumulation.
        contributions = {}
        summed = {}
        def hook(name):
            def capture(g):
                assert name not in contributions, 'MULTIPLE_LEAF_HOOK_CALLS'
                contributions[name] = g.detach().cpu().clone()
            return capture
        handles = [p.register_hook(hook(n)) for n, p in named.items()]
        model.train()
        optimizer.zero_grad(set_to_none=True)
        measure('before_accumulation')
        for micro, entry in enumerate(freeze['sequence'], 1):
            eid = entry['episode_id']
            row, ids, labels, token_measure = samples[eid]
            assert len(ids) <= 2048
            contributions.clear()
            x = torch.tensor([ids], device='cuda')
            y = torch.tensor([labels], device='cuda')
            measure('before_forward', micro, {'episode_id': eid, 'sequence_tokens': len(ids)})
            output = model(input_ids=x, attention_mask=torch.ones_like(x), labels=y, use_cache=False)
            loss = output.loss
            assert torch.isfinite(loss).item()
            raw_loss = loss.item()
            refs = {'output': weakref.ref(output), 'logits': weakref.ref(output.logits),
                    'loss': weakref.ref(loss), 'input': weakref.ref(x), 'labels': weakref.ref(y)}
            measure('after_forward', micro, {'mean_record_loss': raw_loss, 'backward_multiplier': 0.25})
            (loss / 4).backward()
            measure('after_backward', micro)
            assert set(contributions) == set(named)
            worst = 0.0
            grad_bytes = 0
            for name, param in model.named_parameters():
                if not param.requires_grad:
                    assert param.grad is None, name
                    continue
                assert param.grad is not None and torch.isfinite(param.grad).all().item(), name
                assert param.grad.grad_fn is None and not param.grad.requires_grad
                current = param.grad.detach().cpu()
                if name not in summed:
                    summed[name] = torch.zeros_like(current)
                summed[name].add_(contributions[name])
                error = float((current - summed[name]).abs().max())
                worst = max(worst, error)
                assert torch.allclose(current, summed[name], rtol=1e-5, atol=1e-7), name
                grad_bytes += param.grad.numel() * param.grad.element_size()
            del current
            gradients.append({'microbatch': micro, 'episode_id': eid, 'finite_adapter_gradient_tensors': len(named),
                              'base_gradients_absent': True, 'gradient_storage_bytes': grad_bytes,
                              'hook_sum_max_absolute_error': worst, 'gradient_graphs_absent': True,
                              'mean_record_loss': raw_loss, 'supervised_tokens': token_measure['supervised_tokens_including_eos']})
            write('GRADIENTS.json', {'records': gradients, 'comparison': 'CPU sum of detached per-backward leaf hook gradients vs persistent accumulated gradients',
                  'rtol': 1e-5, 'atol': 1e-7, 'loss_normalization': 'unchanged model per-record completion mean /4'})
            del output, loss, x, y
            gc.collect()
            released = {name: ref() is None for name, ref in refs.items()}
            assert all(released.values()), released
            measure('after_cleanup', micro, {'temporary_weakrefs_dead': released})
        measure('after_four_accumulation_steps')
        for handle in handles:
            handle.remove()
        adapter_after = frozen_worker.adapter_manifest(model)
        base_after = frozen_worker.base_manifest(model)
        assert initial == adapter_after and base_before == base_after
        assert not optimizer.state and scheduler.state_dict() == scheduler_before
        write('INTEGRITY.json', {'adapter_unchanged': True, 'base_unchanged': True,
              'adapter_before': initial, 'adapter_after': adapter_after,
              'base_before_identity': c.identity(base_before), 'base_after_identity': c.identity(base_after),
              'optimizer_state_empty': True, 'scheduler_before': scheduler_before, 'scheduler_after': scheduler.state_dict(),
              'optimizer_updates': 0, 'scheduler_updates': 0, 'all_four_backward_calls_completed': True})
        measure('after_integrity_checks')
        # After the frozen window only: release unused allocator cache, keep every gradient.
        torch.cuda.empty_cache()
        measure('after_postwindow_empty_cache')
        assert all(torch.equal(p.grad.detach().cpu(), summed[n]) for n, p in named.items())
        peak_a = max(v['peak_allocated_bytes'] for v in boundaries)
        peak_r = max(v['peak_reserved_bytes'] for v in boundaries)
        write('RESULT.json', {'round': 'R6.57', 'four_record_completed': True,
              'classification': 'R6_57_RESOURCE_LIMIT_TOO_LOW' if peak_r > 8 * GiB else 'R6_57_MEMORY_BEHAVIOR_QUALIFIED',
              'optimizer_updates': 0, 'scheduler_updates': 0, 'peak_allocated_bytes': peak_a, 'peak_reserved_bytes': peak_r,
              'eight_gib_reference_exceeded': peak_r > 8 * GiB, 'unnecessary_retention_demonstrated': False,
              'adapter_unchanged': True, 'base_unchanged': True, 'quantization': quant,
              'full_twenty_step_fit_established': False})
        print('PASS four frozen backward calls; gradients finite/additive; all parameters unchanged; no updates')
    except BaseException as exc:
        write('FAILURE.json', {'error': str(exc), 'traceback': traceback.format_exc(), 'completed_microbatches': len(gradients)})
        write('RESULT.json', {'round': 'R6.57', 'classification': 'R6_57_MEMORY_DIAGNOSIS_PARTIAL',
              'four_record_completed': False, 'optimizer_updates': 0, 'scheduler_updates': 0,
              'error': str(exc), 'completed_microbatches': len(gradients)})
        raise
    finally:
        stop.set()
        monitor.join(timeout=2)


if __name__ == '__main__':
    diagnostic()
