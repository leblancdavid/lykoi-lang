"""Additive launch attribution repair; v2 configuration and failure remain frozen."""
import successor2
import context75 as x
import runtime75

x.OUT = successor2.ORIGINAL_OUT/'qualification_3'
runtime75.OUT = x.OUT/'execution'
v2_write = x.write


def write(name, value):
    if name == 'TRAINING-CONFIGURATION.json':
        # Invoke the v2 configuration wrapper first, then write final v3 bindings.
        cfg = value['configuration']
        cfg['execution_binding']['worker'] = (x.HERE/'worker_v3.py').relative_to(x.ROOT).as_posix()
        cfg['execution_binding']['launcher'] = (x.HERE/'dispatch_v3.py').relative_to(x.ROOT).as_posix()
        value['canonical_sha256'] = x.identity(cfg)
        successor2.original_write(name,value)
    else:
        v2_write(name,value)


x.write = write
