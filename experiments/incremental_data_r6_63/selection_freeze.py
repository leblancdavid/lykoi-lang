"""Seal exact source-selection expectations before expert-action construction."""
from freeze import OUT, ROOT, read, sha, write

frozen = read(OUT / 'SOURCE-FREEZE.json')
assert all(sha(ROOT / p) == h for p, h in frozen['files'].items())
assert not list((OUT / 'episodes').glob('*/ACTION.json'))
write(OUT / 'SELECTION-FREEZE.json', {
    'source_freeze_sha256': sha(OUT / 'SOURCE-FREEZE.json'),
    'selection_acceptance_sha256': sha(OUT / 'SELECTION-ACCEPTANCE.json'),
    'expert_actions_exist': False, 'candidate_execution': 0})
print('PASS exact operation/binding/type/dependency acceptance frozen before actions')
