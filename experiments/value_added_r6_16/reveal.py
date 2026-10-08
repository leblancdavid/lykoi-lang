"""Chronological stage release; cannot enforce hidden-context/file withholding."""
import sys
from evidence import OUT, load, now, save, verify

stage = int(sys.argv[1])
assert stage in (1, 2)
verify(load(OUT / f'SUBMISSION-FREEZE-{stage - 1}.json')['files'])
verify(load(OUT / 'MODIFICATION-SEAL.json')['files'])
save(OUT / f'REVEAL-{stage}.json', dict(utc=now(), stage=stage,
    previous_submissions_frozen=True, acceptance_feedback_to_authors=False,
    disclosure='CONTAMINATED_UNENFORCED',
    released=[f'sealed/{d}-s{stage}.md' for d in ('kiln', 'custody')]))
print('Released stage', stage, 'after previous handoff; no acceptance feedback')
