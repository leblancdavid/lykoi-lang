"""Authors seal the first candidate before any self-test; no overwrites."""
import sys
from pathlib import Path
from evidence import now, save, sha

path = Path(sys.argv[1]).resolve()
first = path.with_name('first' + path.suffix)
with first.open('xb') as f:
    f.write(path.read_bytes())
save(path.with_name('FIRST-SEAL.json'), dict(utc=now(), first_sha256=sha(first), candidate_sha256=sha(path)))
print('First candidate sealed:', sha(first))
