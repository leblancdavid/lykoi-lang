"""Actual worker self-attribution before any model-bound execution."""
import os
import sys
import successor3
import context75 as x
import worker75

if __name__ == '__main__':
    x.frozen_check()
    dry = '--dry-run' in sys.argv
    if dry:
        x.guard()
    else:
        assert os.environ.get('LYKOI_R6_75_EXECUTION_AUTHORIZED') == '1'
    folder = 'dry-launch' if dry else 'execution'
    x.write(folder+'/WORKER-'+sys.argv[1]+'.json',dict(worker_pid=os.getpid(),parent_pid=os.getppid(),
        nonce=os.environ['LYKOI_R6_75_PHASE_NONCE'],mode=sys.argv[1],interpreter=sys.executable))
    worker75.main()
