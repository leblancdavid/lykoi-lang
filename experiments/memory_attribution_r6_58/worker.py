"""Explicit instrumentation transform of pinned R6.57 no-update worker."""
import hashlib
import sys
import time
import run

condition = sys.argv[1]
assert condition in ('baseline', 'cache_release')
root_out = run.OUT
freeze = run.c.read(root_out / 'PREFLIGHT.json')
assert run.c.sha(run.HERE / 'worker.py') == freeze['worker_sha256']
assert run.baseline() == run.c.read(root_out / 'BASELINE.json')
run.OUT = root_out / condition
run.write('PREFLIGHT.json', freeze)
run.write('BASELINE.json', run.c.read(root_out / 'BASELINE.json'))
source_path = run.ROOT / 'experiments/memory_diagnostic_r6_57/worker.py'
source = source_path.read_text(encoding='utf-8')


def replace(old, new):
    global source
    assert source.count(old) == 1, old
    source = source.replace(old, new)


replace("    free, total = torch.cuda.mem_get_info()", """    write('PRE-CONTEXT-CENSUS.json', census())
    started_context = time.perf_counter()
    torch.cuda.init()
    free, total = torch.cuda.mem_get_info()
    write('POST-CONTEXT-CENSUS.json', {'census': census(), 'device_free_bytes': free,
          'device_total_bytes': total, 'allocated_bytes': torch.cuda.memory_allocated(),
          'reserved_bytes': torch.cuda.memory_reserved(), 'initialization_seconds': time.perf_counter()-started_context,
          'limitation': 'before/after device delta includes concurrent external changes; not pure context attribution'})""")
# Retain original R6.56 limits; never raise the8GiB allocator ceiling.
replace('ceiling = min(10 * GiB, initial_reserved + free - 2 * GiB)', 'ceiling = min(8 * GiB, initial_reserved + free - 2 * GiB)')
replace("    assert ceiling > 8 * GiB, 'NO_SAFE_DIAGNOSTIC_HEADROOM'", "    assert ceiling == 8 * GiB, 'NO_SAFE_DIAGNOSTIC_HEADROOM'")
replace("'ceiling_formula': 'min(10GiB, initial_reserved+verified_free-2GiB)'", "'ceiling_formula': 'min(8GiB, initial_reserved+verified_free-2GiB)'")
replace('    torch.cuda.reset_peak_memory_stats()', "    torch.cuda.reset_peak_memory_stats()\n    torch.cuda.memory._record_memory_history(max_entries=12000)")
replace("'allocator_stats': {k: stats.get(k) for k in ('active_bytes.all.current', 'inactive_split_bytes.all.current',\n                    'inactive_split_bytes.all.peak', 'allocation.all.current', 'num_alloc_retries', 'num_ooms')}", "'allocator_stats': dict(stats), 'outside_allocator_residual_bytes': total_now-free_now-torch.cuda.memory_reserved()")
replace('        check(v)\n        return v', """        check(v)
        write('CENSUS-' + str(micro) + '-' + boundary + '.json', census())
        if boundary in ('after_model_loading', 'after_cleanup', 'after_four_accumulation_steps'):
            write('SNAPSHOT-' + str(micro) + '-' + boundary + '.json', torch.cuda.memory._snapshot())
        return v""")
replace("{'episode_id': eid, 'sequence_tokens': len(ids)}", "{'episode_id': eid, 'sequence_tokens': len(ids), 'input_shape': list(x.shape), 'labels_shape': list(y.shape), 'attention_mask_shape': list(x.shape), 'attention_mask_sum': int(x.numel()), 'supervised_tokens': sum(v != -100 for v in labels)}")
replace("            write('GRADIENTS.json',", """            write('GRADIENT-IDENTITIES-' + str(micro) + '.json', {
                n: hashlib.sha256(p.grad.detach().cpu().numpy().tobytes()).hexdigest() for n,p in named.items()})
            write('GRADIENTS.json',""")
replace("            measure('after_cleanup', micro, {'temporary_weakrefs_dead': released})", """            measure('after_cleanup', micro, {'temporary_weakrefs_dead': released})
            if condition == 'cache_release':
                before_flush = {n: hashlib.sha256(p.grad.detach().cpu().numpy().tobytes()).hexdigest() for n,p in named.items()}
                torch.cuda.empty_cache()
                measure('after_cache_release', micro)
                after_flush = {n: hashlib.sha256(p.grad.detach().cpu().numpy().tobytes()).hexdigest() for n,p in named.items()}
                assert before_flush == after_flush
                write('CACHE-GRADIENT-INTEGRITY-' + str(micro) + '.json', {'exact_gradient_bytes_unchanged': True})""")
# No extra post-window condition is applied to either trajectory.
replace('        torch.cuda.empty_cache()\n        measure(\'after_postwindow_empty_cache\')', "        measure('after_window_no_additional_flush')")
replace("if __name__ == '__main__':\n    diagnostic()", 'diagnostic()')
source = source.replace("'R6.57'", "'R6.58'")
run.write('EFFECTIVE-SOURCE-IDENTITY.json', {'historical_worker_sha256': run.c.sha(source_path),
    'effective_source_sha256': hashlib.sha256(source.encode()).hexdigest(), 'condition': condition,
    'method': 'read-only explicit single-match source instrumentation; frozen files unchanged'})
exec(compile(source, str(source_path) + ':r6_58_instrumented', 'exec'),
     {'__name__': '__main__', 'census': run.census, 'condition': condition, 'hashlib': hashlib})
