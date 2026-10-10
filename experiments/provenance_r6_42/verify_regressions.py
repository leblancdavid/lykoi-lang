"""Run unchanged requested regression suites, retain actual stdout/stderr and status."""
import os
import subprocess
import sys
from common import ROOT, OUT, save, verify_files, read, verify_freeze


def verify():
    verify_files(read(OUT / 'BASELINE.json')['protected_files'])
    verify_freeze()
    results = []
    for directory, pattern in [('experiments/typed_composition_r6_18', 'test_composition.py'),
                               ('experiments/lifecycle_r6_32', 'test_lifecycle.py')]:
        env = dict(os.environ)
        env['PYTHONPATH'] = os.pathsep.join([str(ROOT / directory), str(ROOT / 'src')])
        command = [sys.executable, '-m', 'unittest', 'discover', '-s', directory, '-p', pattern, '-v']
        process = subprocess.run(command, cwd=ROOT, env=env, text=True, capture_output=True)
        row = {'command': command, 'returncode': process.returncode, 'stdout': process.stdout, 'stderr': process.stderr}
        results.append(row)
        print(directory, 'returncode:', process.returncode)
        print(process.stderr)
    verify_files(read(OUT / 'BASELINE.json')['protected_files'])
    verify_freeze()
    save(OUT / 'REGRESSIONS.json', {'results': results, 'all_passed': all(r['returncode'] == 0 for r in results),
         'protected_files_preserved': True, 'frozen_R6_42_files_preserved': True})


if __name__ == '__main__':
    verify()
