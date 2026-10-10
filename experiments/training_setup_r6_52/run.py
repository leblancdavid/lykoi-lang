"""Launch separate qualification processes and retain failure diagnostics."""
import os
import subprocess
import sys
from setup import PYTHON, ROOT, OUT, STORE, run, write


if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'host':
        for name, args in [('WSL-LIST', ['wsl', '--list', '--verbose']),
                           ('WSL-STATUS', ['wsl', '--status']), ('PY-LIST', ['py', '--list-paths']),
                           ('GPU', ['nvidia-smi', '-q']),
                           ('OS', ['pwsh', '-NoProfile', '-Command', 'Get-CimInstance Win32_OperatingSystem | Format-List Caption,Version,TotalVisibleMemorySize,FreePhysicalMemory'])]:
            p = subprocess.run(args, cwd=ROOT, capture_output=True)
            encoding = 'utf-16-le' if name.startswith('WSL') else 'utf-8'
            write(name + '.json', {'argv': args, 'returncode': p.returncode,
                  'stdout': p.stdout.decode(encoding, errors='replace'), 'stderr': p.stderr.decode(encoding, errors='replace')})
    else:
        os.environ['HF_HUB_DISABLE_TELEMETRY'] = '1'
        os.environ['HF_HOME'] = str(STORE / 'hf-cache')
        if mode == 'mask-controls':
            args = [PYTHON, ROOT / 'experiments/training_setup_r6_52/mask_controls.py']
        else:
            args = [PYTHON, ROOT / 'experiments/training_setup_r6_52/qualify.py', mode]
        run(mode.upper() + '-PROCESS', args, timeout=1800)
