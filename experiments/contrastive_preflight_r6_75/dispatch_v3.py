"""Actual worker handshake accounts for Windows venv redirector process."""
import os
import subprocess
import sys
import time
import traceback
import uuid
import successor3
import context75 as x
import resources75 as resource
from runtime75 import validate_configuration


def validate_handshake(value, nonce, mode, launcher_pid):
    assert value['nonce'] == nonce and value['mode'] == mode, 'STALE_OR_WRONG_HANDSHAKE'
    assert value['interpreter'] == str(x.PYTHON), 'WRONG_WORKER_INTERPRETER'
    assert type(value['worker_pid']) is int and value['worker_pid'] > 0
    assert value['worker_pid'] == launcher_pid or value['parent_pid'] == launcher_pid, 'INCORRECT_PROCESS_ATTRIBUTION'
    return value['worker_pid']


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
    x.write(folder.name+'/DISPATCH-CLAIM.json',dict(dry_run=dry,pid=os.getpid(),one_shot=True,automatic_retry=False))
    env = dict(x.ENV) if dry else dict(os.environ,HF_HUB_OFFLINE='1',HF_HUB_DISABLE_TELEMETRY='1',PYTHONDONTWRITEBYTECODE='1',TOKENIZERS_PARALLELISM='false')
    if dry:
        env['LYKOI_R6_75_DRY_RUN'] = '1'
    else:
        env.pop('CUDA_VISIBLE_DEVICES',None)
    phases = []
    try:
        for mode in cfg['execution_binding']['launch_modes']:
            nonce = uuid.uuid4().hex
            env['LYKOI_R6_75_PHASE_NONCE'] = nonce
            command = [str(x.PYTHON),str(x.ROOT/cfg['execution_binding']['worker']),mode]+(['--dry-run'] if dry else [])
            samples, startup = [], []
            handshake = None
            worker_pid = None
            with (folder/f'{mode}-stdout.txt').open('x',encoding='utf-8') as stdout, (folder/f'{mode}-stderr.txt').open('x',encoding='utf-8') as stderr:
                process = subprocess.Popen(command,cwd=x.ROOT,env=env,stdout=stdout,stderr=stderr)
                started = time.perf_counter()
                try:
                    while process.poll() is None:
                        handshake_path = folder/f'WORKER-{mode}.json'
                        if handshake is None and handshake_path.exists():
                            # The exclusive small JSON can be observed mid-write; wait for closure.
                            try:
                                handshake = x.read(handshake_path)
                            except __import__('json').JSONDecodeError:
                                handshake = None
                            if handshake is not None:
                                worker_pid = validate_handshake(handshake,nonce,mode,process.pid)
                        measured_pid = worker_pid or process.pid
                        value = resource.measure(measured_pid)
                        if not value['available'] and process.poll() is not None:
                            break
                        resource.validate(value,measured_pid,cfg['limits']['process_rss_bytes'])
                        (samples if worker_pid else startup).append(value)
                        assert time.perf_counter()-started <= cfg['training_process_timeout_seconds'], 'PROCESS_WALL_LIMIT'
                        time.sleep(cfg['external_rss_poll_seconds'])
                    assert process.returncode == 0,(mode,process.returncode)
                finally:
                    if process.poll() is None:
                        # Kill the actual worker as well as a Windows redirector on a limit halt.
                        if worker_pid is not None and worker_pid != process.pid:
                            if sys.platform == 'win32':
                                subprocess.run(['taskkill','/PID',str(worker_pid),'/T','/F'],capture_output=True,timeout=30)
                            else:
                                os.kill(worker_pid,9)
                        process.kill()
                        process.wait(timeout=30)
            assert handshake is not None and samples, 'WORKER_ATTRIBUTION_NOT_QUALIFIED'
            phase = dict(mode=mode,pid=worker_pid,launcher_pid=process.pid,worker_handshake=handshake,command=command,
                returncode=process.returncode,seconds=time.perf_counter()-started,resource_samples=samples,
                startup_launcher_samples=startup)
            phases.append(phase)
            x.write(folder.name+'/PHASE-'+mode+'.json',phase)
        x.write(folder.name+'/RESULT.json',dict(passed=True,dry_run=dry,phases=phases,
            configuration_identity=x.identity(cfg),training_outputs_claimed=not dry))
    except BaseException as exc:
        x.write(folder.name+'/HALT.json',dict(error=str(exc),traceback=traceback.format_exc(),automatic_retry=False))
        raise


if __name__ == '__main__':
    main()
