"""Freeze tested setup before authors; retain real pre-author qualification log."""
import subprocess
import sys
from evidence import HERE, OUT, ROOT, now, save, sha

p = subprocess.run([sys.executable, '-B', '-m', 'unittest', 'discover', '-s', str(HERE),
                    '-p', 'test_infrastructure.py', '-v'], cwd=ROOT, capture_output=True, text=True, timeout=120)
save(OUT / 'INFRASTRUCTURE-QUALIFICATION.json', dict(utc=now(), returncode=p.returncode,
    stdout=p.stdout, stderr=p.stderr, initial_setup_failure='original schema missing closing brace; retained; corrected pre-author'))
if p.returncode:
    raise RuntimeError(p.stderr)
save(OUT / 'INFRASTRUCTURE-FREEZE.json', dict(utc=now(), files={p.relative_to(ROOT).as_posix(): sha(p)
    for p in HERE.glob('*') if p.is_file()}, setup='shared new experimental infrastructure, not production changes'))
print('Infrastructure frozen before first author dispatch')
