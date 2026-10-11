"""Prospective hash-serialization assertion correction; frozen original retained."""
import hashlib
import json
import sys
import diagnose as d


def effective():
    source = (d.HERE / 'diagnose.py').read_text(encoding='utf-8')
    changes = {
        "assert c.identity(labels) == e['labels_sha256']":
            "assert hashlib.sha256(json.dumps(labels).encode()).hexdigest() == e['labels_sha256']; assert hashlib.sha256(json.dumps(ids).encode()).hexdigest() == e['tokens_sha256']",
        "f'{track.upper()}-CLAIM.json'": "f'{track.upper()}-QUALIFIED-CLAIM.json'",
        "f'{track.upper()}-PROCESS.json'": "f'{track.upper()}-QUALIFIED-PROCESS.json'",
    }
    for old, new in changes.items():
        assert source.count(old) == 1
        source = source.replace(old, new)
    return source


if __name__ == '__main__':
    if sys.argv[1] == 'freeze':
        d.check()
        from transformers import AutoTokenizer
        t = AutoTokenizer.from_pretrained(d.c.STORE / 'checkpoint', local_files_only=True)
        expected = {r['episode_id']: r for r in d.c.read(d.c.OUT / 'SOURCE-DATASET-IDENTITIES.json')['records']}
        matches = []
        for row in d.c.rows():
            ids, labels, measure = d.c.q52.encoded(row, t)
            e = expected[row['episode_id']]
            assert hashlib.sha256(json.dumps(labels).encode()).hexdigest() == e['labels_sha256']
            assert hashlib.sha256(json.dumps(ids).encode()).hexdigest() == e['tokens_sha256']
            assert measure == e['tokenization']
            matches.append(row['episode_id'])
        assert not (d.OUT / 'BASE-LOSS.json').exists()
        assert not (d.OUT / 'CORRECTION.json').exists()
        d.write('CORRECTION.json', {'status': 'PASS', 'matched_original_token_and_mask_records': matches,
            'original_process_sha256': d.c.sha(d.OUT / 'BASE-PROCESS.json'), 'evaluated_target_tokens_before_correction': 0,
            'reason': 'historical labels/tokens use default json.dumps spacing, not compact canonical serialization',
            'qualified_source_sha256': d.c.sha(d.HERE / 'qualified.py'),
            'effective_source_sha256': hashlib.sha256(effective().encode()).hexdigest(),
            'model_prompt_mask_loss_settings_changed': False})
        print('PASS original-convention mask identities; prospective assertion correction frozen')
    else:
        receipt = d.c.read(d.OUT / 'CORRECTION.json')
        assert d.c.sha(d.HERE / 'qualified.py') == receipt['qualified_source_sha256']
        source = effective()
        assert hashlib.sha256(source.encode()).hexdigest() == receipt['effective_source_sha256']
        # Child dispatch must use this same qualified entry point.
        source = source.replace("str(HERE / 'diagnose.py'), 'evaluate'", "str(HERE / 'qualified.py'), 'evaluate'")
        exec(compile(source, 'R6.60-qualified-source', 'exec'), {'__name__': '__main__', '__file__': str(d.HERE / 'diagnose.py')})
