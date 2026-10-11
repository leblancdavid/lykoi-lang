"""Compact offline publication tables; no model inference."""
import diagnose as d

if __name__ == '__main__':
    a, b = [d.c.read(d.OUT / f'{t}-LOSS.json') for t in ('BASE', 'ADAPTER')]
    analysis = d.c.read(d.OUT / 'TOKEN-ANALYSIS.json')
    inventory = d.c.read(d.OUT / 'FIRST-DIVERGENCE.json')
    d.write('SUMMARY.json', {'loss_records': [{k: r[k] for k in ('episode_id', 'tokens', 'base_mean_nll', 'adapter_mean_nll', 'delta')} for r in analysis['records']],
        'resources': {t: {k: r[k] for k in ('evaluation_seconds', 'whole_worker_seconds', 'peak_allocated_bytes', 'peak_reserved_bytes', 'final_device_free_bytes', 'numerical_failures', 'model_parameters_unchanged')} for t, r in [('base', a), ('adapter', b)]},
        'first_target_probabilities': [{'episode_id': ra['episode_id'], 'token_id': ra['tokens'][0]['token_id'],
            'text': ra['tokens'][0]['text'], 'base': ra['tokens'][0]['probability'], 'adapter': rb['tokens'][0]['probability']} for ra, rb in zip(a['records'], b['records'])],
        'divergence': [{k: r[k] for k in ('episode_id', 'track', 'first_violation_character_index', 'first_token_id', 'first_token_text', 'output', 'output_tokens_including_eos', 'expected_package_keys_without_lexical_occurrence')} for r in inventory['records']],
        'historical_generation_configuration': d.c.read(d.c.OUT / 'DIAGNOSTIC-PROTOCOL.json')['resolved_generation_configuration']})
