"""Offline analysis with historical message-hash convention; no model dispatch."""
import diagnose as d


if __name__ == '__main__':
    source = (d.HERE / 'diagnose.py').read_text(encoding='utf-8')
    old = "assert pa == d['prompt_sha256']"
    assert source.count(old) == 1
    source = source.replace(old, "assert c.identity(row['prompt']) == d['prompt_sha256']")
    scope = {'__name__': 'r60_offline_analysis', '__file__': str(d.HERE / 'diagnose.py')}
    exec(compile(source, 'R6.60-offline-analysis', 'exec'), scope)
    d.write('AUDIT-ASSERTION-CORRECTION.json', {'initial_analysis_failure': 'prompt hash assertion before prompt audit/output inventory publication',
        'reason': 'historical prompt_sha256 hashes canonical message list, not rendered chat text',
        'changes_to_prompts_or_models': False, 'model_reruns': 0, 'rendered_hash_retained_separately': True})
    scope['analyze']()
