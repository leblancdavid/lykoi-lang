"""Run focused tests once and preserve real output/timing in a new receipt."""
import subprocess
import sys
import time
from baseline import OUT, ROOT, save, sha
from pathlib import Path

command = [sys.executable, '-B', '-m', 'unittest', 'discover', '-s',
           'experiments/lifecycle_r6_32', '-p', 'test_lifecycle.py', '-v']
start = time.perf_counter()
child = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=120)
save(OUT / sys.argv[1], dict(command=command, returncode=child.returncode, stdout=child.stdout,
    stderr=child.stderr, wall_seconds=time.perf_counter() - start,
    inputs={p.relative_to(ROOT).as_posix(): sha(p) for p in Path(__file__).parent.glob('*.py')}))
print(child.stdout + child.stderr)
raise SystemExit(child.returncode)
