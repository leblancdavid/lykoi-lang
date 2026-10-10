"""Read-only analysis of the single stopped diagnostic; never loads a model."""
from run import OUT, baseline, c, write


def analyze():
    assert baseline() == c.read(OUT / 'BASELINE.json')
    trace = c.read(OUT / 'MEMORY-TRACE.json')['boundaries']
    stop = c.read(OUT / 'SAFETY-STOP.json')
    assert stop['error'] == 'DEVICE_FREE_LIMIT'
    assert c.read(OUT / 'PROCESS.json')['returncode'] == 71
    grads = c.read(OUT / 'GRADIENTS.json')['records']
    assert len(grads) == 3
    assert not (OUT / 'INTEGRITY.json').exists()
    safety = c.read(OUT / 'RESOURCE-SAFETY.json')
    samples = trace + [stop['values']]
    peak_a = max(v['peak_allocated_bytes'] for v in samples)
    peak_r = max(v['peak_reserved_bytes'] for v in samples)
    loaded = next(v for v in trace if v['boundary'] == 'after_model_loading')
    clean = [v for v in trace if v['boundary'] == 'after_cleanup']
    assert len(clean) == 3 and len({v['allocated_bytes'] for v in clean}) == 1
    assert all(all(v['temporary_weakrefs_dead'].values()) for v in clean)
    assert all(g['hook_sum_max_absolute_error'] == 0 and g['finite_adapter_gradient_tensors'] == 112 for g in grads)
    summary = []
    for micro in range(1, 5):
        subset = [v for v in trace if v['microbatch'] == micro]
        summary.append({'microbatch': micro, 'episode_id': f'R6.48/E{micro:02d}',
                        'boundaries': {v['boundary']: {k: v[k] for k in ('allocated_bytes', 'reserved_bytes',
                            'peak_allocated_bytes', 'peak_reserved_bytes', 'device_free_bytes')} for v in subset}})
    analysis = {'status': 'PARTIAL_SAFETY_STOP', 'completed_backwards_and_cleanups': 3,
                'four_record_completed': False, 'peak_allocated_bytes': peak_a, 'peak_reserved_bytes': peak_r,
                'peak_allocated_gib': peak_a / 1024**3, 'peak_reserved_gib': peak_r / 1024**3,
                'minimum_observed_free_bytes': min(v['device_free_bytes'] for v in samples),
                'microbatch_summary': summary,
                'allocated_cleanup_bytes': [v['allocated_bytes'] for v in clean],
                'reserved_cleanup_bytes': [v['reserved_bytes'] for v in clean],
                'allocated_cleanup_increase_from_loaded_bytes': clean[0]['allocated_bytes'] - loaded['allocated_bytes'],
                'persistent_gradient_bytes': grads[0]['gradient_storage_bytes'],
                'inactive_split_cleanup_bytes': [v['allocator_stats']['inactive_split_bytes.all.current'] for v in clean],
                'reserved_minus_allocated_cleanup_bytes': [v['reserved_bytes'] - v['allocated_bytes'] for v in clean],
                'outside_allocator_accounting_residual_bytes': [
                    {'boundary': v.get('boundary', 'unsynchronized_safety_stop'), 'microbatch': v.get('microbatch'),
                     'total_minus_free_minus_reserved': v['device_total_bytes'] - v['device_free_bytes'] - v['reserved_bytes']}
                    for v in [loaded] + clean + [stop['values']]],
                'outside_allocator_residual_is_not_process_attribution': True,
                'unnecessary_retention_demonstrated': False,
                'eight_gib_is_sufficient_for_observed_path': False,
                'causal_scope': 'Reservation growth persists despite stable live allocated cleanup baseline. Cache/non-live reservations measured; exact allocation provenance and device-wide pressure unresolved.',
                'parameter_hash_comparison_after_diagnostic': 'NOT_REACHED',
                'full_four_record_gradient_qualification': 'NOT_REACHED',
                'postwindow_empty_cache_control': 'NOT_REACHED',
                'recommendation': 'D. Investigate unresolved memory behavior further.',
                'original_R6_56_classification_preserved': 'R6_56_RESOURCE_OR_STACK_GAP'}
    write('MEMORY-ANALYSIS.json', analysis)
    write('PARAMETER-INTEGRITY-STATUS.json', {
          'initial_adapter_exact_R6_52_match': True, 'initial_base_manifest_recorded': True,
          'finite_adapter_only_graph_free_gradients_verified_microbatches': [1, 2, 3],
          'independent_hook_sum_max_absolute_error': 0.0,
          'all_four_gradients_verified': False, 'postdiagnostic_parameter_equality': 'NOT_REACHED',
          'optimizer_updates': 0, 'scheduler_updates': 0,
          'update_absence_evidence': 'exact frozen four-call worker has no update call; both step methods hard-raise after construction; hard exit during E04 forward before any completion/update path',
          'scheduler_initialization_epoch': 0, 'scheduler_updates_exclude_constructor_initialization': True,
          'no_update_is_not_substitute_for_postdiagnostic_hashes': True,
          'trained_adapter_created': False, 'adapter_save_calls': 0})
    write('RESULT.json', {'round': 'R6.57', 'classification': 'R6_57_MEMORY_DIAGNOSIS_PARTIAL',
          'four_record_completed': False, 'completed_microbatches': 3, 'fourth_microbatch': 'forward in flight at hard stop',
          'peak_allocated_bytes': peak_a, 'peak_reserved_bytes': peak_r,
          'original_eight_gib_exceeded_by_bytes': peak_r - safety['original_reference_bytes'],
          'first_blocker': stop['error'], 'optimizer_updates': 0, 'scheduler_updates': 0,
          'unnecessary_retention_demonstrated': False, 'final_parameter_equality': 'NOT_REACHED',
          'recommendation': 'D', 'full_twenty_step_fit_established': False,
          'kernel_constructs': 26, 'P6_A04_acceptance_executions': 0, 'P6_A05_content_access': False})
    print(c.canonical(analysis).decode())


if __name__ == '__main__':
    analyze()
