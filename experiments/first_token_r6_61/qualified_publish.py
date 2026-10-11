"""Publication-only self-link ordering correction; frozen inference untouched."""
import json
from pathlib import Path
import sys
import publication as p

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
        original_write('PUBLICATION-ORDER-CORRECTION.json', {
            'initial_failure': 'AssertionError: r6_61/PUBLICATION-IDENTITIES.json: report self-link checked before manifest existed',
            'model_rerun': False, 'historical_changes': False,
            'qualified_publication_source_sha256': d.c.sha(Path(__file__)),
            'correction': 'Pending placeholders satisfy self-links; replace only exact pending new-publication placeholders with final seal. Existing offline source receipt must match, never rewritten.'})
        for name in ('PUBLICATION-IDENTITIES.json', 'VERIFICATION.json'):
            original_write(name, {'status': 'PENDING_SELF_LINK_PLACEHOLDER'})
        d.write = qualified_write
    else:
        assert d.c.sha(Path(__file__)) == d.c.read(d.OUT / 'PUBLICATION-ORDER-CORRECTION.json')['qualified_publication_source_sha256']
    p.publish(seal)
