"""Prospective one-shot bounded launcher. No execution authorized by R6.74."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from integration import ROOT, HERE, OUT, STORE, PYTHON, ARTIFACTS, c, read, frozen_check


def main():
    assert os.environ.get('LYKOI_R6_74_EXECUTION_AUTHORIZED') == '1', 'Requires separate explicit owner authorization'
    assert Path(sys.executable).resolve() == PYTHON.resolve()
    frozen_check()
    assert not ARTIFACTS.exists() and not (OUT/'execution').exists()
    assert ARTIFACTS.parent.is_dir()
    (OUT/'execution').mkdir()
    ARTIFACTS.mkdir()
    (OUT/'execution/DISPATCH-CLAIM.json').write_text(json.dumps(dict(one_shot=True,automatic_retry=False))+'\n',encoding='utf-8')
    env = dict(os.environ,HF_HUB_OFFLINE='1',HF_HUB_DISABLE_TELEMETRY='1',PYTHONDONTWRITEBYTECODE='1',TOKENIZERS_PARALLELISM='false')
    env.pop('CUDA_VISIBLE_DEVICES',None)
    cfg = read(OUT/'TRAINING-CONFIGURATION.json')['configuration']
    try:
        for mode in ('base','train','adapter'):
            with (OUT/'execution'/f'{mode}-stdout.txt').open('x',encoding='utf-8') as stdout, (OUT/'execution'/f'{mode}-stderr.txt').open('x',encoding='utf-8') as stderr:
                process = subprocess.Popen([str(PYTHON),str(HERE/'worker.py'),mode],cwd=ROOT,env=env,stdout=stdout,stderr=stderr)
                started = time.perf_counter()
                try:
                    while process.poll() is None:
                        rss = c.rss(process.pid)
                        assert rss is not None and rss <= cfg['limits']['process_rss_bytes'], 'RSS_LIMIT'
                        assert time.perf_counter()-started <= 1800, 'PROCESS_WALL_LIMIT'
                        time.sleep(0.1)
                    assert process.returncode == 0, (mode,process.returncode)
                finally:
                    if process.poll() is None:
                        process.kill()
                        process.wait(timeout=30)
    except BaseException as exc:
        (OUT/'execution/DISPATCH-HALT.json').write_text(json.dumps(dict(error=str(exc),automatic_retry=False))+'\n',encoding='utf-8')
        raise


if __name__ == '__main__':
    main()
