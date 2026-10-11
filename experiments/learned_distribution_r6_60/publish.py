"""Publication checks including live index bindings and mathematical consistency."""
import math
import sys
import diagnose as d

INDEX = ['docs/research-log.md', 'docs/decisions.md', 'docs/project-overview.md', 'docs/research-log-r6.60.md']


def verify_math():
    a, b = [d.c.read(d.OUT / f'{track}-LOSS.json') for track in ('BASE', 'ADAPTER')]
    for data in (a, b):
        assert data['model_parameters_unchanged'] and not data['gradient_computation']
        assert not data['numerical_failures'] and data['optimizer_updates'] == data['generated_tokens'] == 0
        assert len(data['records']) == 6
        assert sum(r['supervised_tokens'] for r in data['records']) == 2326
        for record in data['records']:
            tokens = record['tokens']
            assert len(tokens) == record['supervised_tokens']
            assert record['sum_nll_nats'] == sum(t['nll_nats'] for t in tokens)
            assert record['mean_nll_nats'] == record['sum_nll_nats']/len(tokens)
            for t in tokens:
                assert math.isfinite(t['nll_nats']) and 0 <= t['probability'] <= 1
                assert t['probability'] == math.exp(-t['nll_nats'])
                assert t['logit_index'] == t['sequence_index']-1
        assert data['equal_record_mean_nll_nats'] == sum(r['mean_nll_nats'] for r in data['records'])/6
        assert data['pooled_token_mean_nll_nats'] == sum(r['sum_nll_nats'] for r in data['records'])/2326
    for ra, rb in zip(a['records'], b['records']):
        assert ra['ids_sha256'] == rb['ids_sha256'] and ra['labels_sha256'] == rb['labels_sha256']
        assert rb['mean_nll_nats'] < ra['mean_nll_nats']
    inventory = d.c.read(d.OUT / 'FIRST-DIVERGENCE.json')['records']
    assert len(inventory) == 12
    assert all(r['first_violation_character_index'] == 0 and r['first_token_id'] == 73594 and not r['repair_or_rescore'] for r in inventory)
    assert d.c.read(d.OUT / 'RESULT.json')['classification'] == 'R6_60_TARGET_LIKELIHOOD_IMPROVED'


if __name__ == '__main__':
    mode = sys.argv[1]
    verify_math()
    values = {name: d.c.sha(d.ROOT / name) for name in INDEX}
    for name in INDEX:
        text = (d.ROOT / name).read_text(encoding='utf-8')
        assert all(line == line.rstrip() for line in text.splitlines())
    if mode == 'seal':
        d.write('INDEX-IDENTITIES.json', values)
        d.write('VERIFICATION.json', {'passed': False, 'status': 'verification pending'})
    assert values == d.c.read(d.OUT / 'INDEX-IDENTITIES.json')
    d.publication(mode == 'seal')
