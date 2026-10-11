"""Publication-only subprocess capture; does not alter the frozen training payload."""
import json
import subprocess
import sys
import time
import run


if __name__ == '__main__':
    assert run.Path(sys.executable).resolve() == run.PYTHON.resolve()
    assert not (run.OUT/'CPU-REPLAY-PROCESS.json').exists()
    args = [str(run.PYTHON), str(run.HERE/'qualify.py')]
    start = time.perf_counter()
    proc = subprocess.run(args, cwd=run.ROOT, env=run.ENV, capture_output=True, text=True, timeout=180)
    run.write('CPU-REPLAY-PROCESS.json', dict(argv=args, returncode=proc.returncode, stdout=proc.stdout,
              stderr=proc.stderr, seconds=time.perf_counter()-start,
              capture_source_sha256=run.sha(run.HERE/'capture.py')))
    assert proc.returncode == 0, proc.stdout + proc.stderr
    result = json.loads(proc.stdout)
    assert result['passed']
    run.write('CPU-REPLAY.json', result)
    print(json.dumps(result, indent=2))
