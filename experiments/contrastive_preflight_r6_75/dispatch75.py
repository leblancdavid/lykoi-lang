"""Bounded launcher; dry mode never claims training outputs or exposes CUDA."""
import os
import subprocess
import sys
import time
import traceback
import context75 as x
import resources75 as resource
from runtime75 import validate_configuration


def main():
    dry = sys.argv[1:] == ['--dry-run']
    assert dry or os.environ.get('LYKOI_R6_75_EXECUTION_AUTHORIZED') == '1'
    if dry:
        x.guard()
    assert __import__('pathlib').Path(sys.executable).resolve() == x.PYTHON.resolve()
    x.frozen_check()
    cfg = x.read(x.OUT/'TRAINING-CONFIGURATION.json')['configuration']
    validate_configuration(cfg)
    assert not x.ARTIFACTS.exists() and not (x.OUT/'execution').exists()
    assert x.ARTIFACTS.parent.is_dir()
    folder = x.OUT/('dry-launch' if dry else 'execution')
    folder.mkdir()
    if not dry:
        x.ARTIFACTS.mkdir()
    x.write(folder.name+'/DISPATCH-CLAIM.json', dict(dry_run=dry, pid=os.getpid(), one_shot=True, automatic_retry=False))
    env = dict(x.ENV) if dry else dict(os.environ, HF_HUB_OFFLINE='1', HF_HUB_DISABLE_TELEMETRY='1', PYTHONDONTWRITEBYTECODE='1', TOKENIZERS_PARALLELISM='false')
    if dry:
        env['LYKOI_R6_75_DRY_RUN'] = '1'
    else:
        env.pop('CUDA_VISIBLE_DEVICES', None)
    phases = []
    try:
        for mode in cfg['execution_binding']['launch_modes']:
            command = [str(x.PYTHON), str(x.HERE/'worker75.py'), mode] + (['--dry-run'] if dry else [])
            samples = []
            with (folder/f'{mode}-stdout.txt').open('x', encoding='utf-8') as stdout, (folder/f'{mode}-stderr.txt').open('x', encoding='utf-8') as stderr:
                process = subprocess.Popen(command, cwd=x.ROOT, env=env, stdout=stdout, stderr=stderr)
                started = time.perf_counter()
                try:
                    while process.poll() is None:
                        value = resource.measure(process.pid)
                        if not value['available'] and process.poll() is not None:
                            break  # exited between poll and measurement; never record a zero
                        resource.validate(value, process.pid, cfg['limits']['process_rss_bytes'])
                        samples.append(value)
                        assert time.perf_counter()-started <= cfg['training_process_timeout_seconds'], 'PROCESS_WALL_LIMIT'
                        time.sleep(cfg['external_rss_poll_seconds'])
                    assert process.returncode == 0, (mode, process.returncode)
                finally:
                    if process.poll() is None:
                        process.kill()
                        process.wait(timeout=30)
            assert samples
            phases.append(dict(mode=mode, pid=process.pid, command=command, returncode=process.returncode,
                               seconds=time.perf_counter()-started, resource_samples=samples))
            x.write(folder.name+'/PHASE-'+mode+'.json', phases[-1])
        x.write(folder.name+'/RESULT.json', dict(passed=True, dry_run=dry, phases=phases,
                  configuration_identity=x.identity(cfg), training_outputs_claimed=not dry))
    except BaseException as exc:
        x.write(folder.name+'/HALT.json', dict(error=str(exc), traceback=traceback.format_exc(), automatic_retry=False))
        raise


if __name__ == '__main__':
    main()
