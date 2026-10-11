"""Offline publication with unambiguous module name and pending-only self-link seal."""
import importlib.util
import json
from pathlib import Path
import sys

spec = importlib.util.spec_from_file_location('r61_offline_publication', Path(__file__).with_name('publication.py'))
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)
d = p.d
original_write = d.write


def qualified_write(name, value):
    path = d.OUT / name
    if path.exists():
        old = d.c.read(path)
        if name == 'OFFLINE-SOURCE-IDENTITIES.json':
            assert old == value
            return
        assert name in ('PUBLICATION-IDENTITIES.json', 'VERIFICATION.json')
        assert old == {'status': 'PENDING_SELF_LINK_PLACEHOLDER'}
        path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n', encoding='utf-8', newline='\n')
    else:
        original_write(name, value)


if __name__ == '__main__':
    seal = sys.argv[1] == 'seal'
    if seal:
        original_write('PUBLICATION-IMPORT-CORRECTION.json', {
            'initial_failure': "AttributeError: module publication has no attribute baseline: wrapper module name collided with inherited unqualified publication import",
            'model_rerun': False, 'historical_changes': False,
            'qualified_source_sha256': d.c.sha(Path(__file__)),
            'correction': 'Use unique spec module name; retain first qualified source and existing pending self-link placeholders.'})
        d.write = qualified_write
    assert d.c.sha(Path(__file__)) == d.c.read(d.OUT / 'PUBLICATION-IMPORT-CORRECTION.json')['qualified_source_sha256']
    assert d.c.sha(Path(__file__).with_name('qualified_publish.py')) == d.c.read(d.OUT / 'PUBLICATION-ORDER-CORRECTION.json')['qualified_publication_source_sha256']
    p.publish(seal)
