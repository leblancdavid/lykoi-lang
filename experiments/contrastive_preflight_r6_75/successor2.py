"""Explicit additive amendment after preserved first successor name-length failure."""
import re
import context75 as x
import runtime75

ORIGINAL_OUT = x.OUT
x.OUT = ORIGINAL_OUT/'qualification_2'
runtime75.OUT = x.OUT/'execution'
original_corrected = x.corrected
original_write = x.write


def corrected(row):
    result = original_corrected(row)
    if row['partition'] == 'training_calibration':
        return result
    match = re.fullmatch(r'(E[0-9]{2})-.*-([1-4])-(R[12])', row['id'])
    assert match, 'AMBIGUOUS_IDENTIFIER_MAPPING'
    scope = result['scope']
    scope['name'] = 'R675' + match[1] + 'N' + match[2] + match[3]
    assert re.fullmatch(r'[A-Za-z][A-Za-z0-9_]{0,31}',scope['name'])
    scope.pop('identity')
    scope['identity'] = x.identity(scope)
    result['scope_identity'] = scope['identity']
    result['prompt'][1]['content'] = x.serialize(dict(requirement=result['requirement'],scope=scope))
    return result


def write(name, value):
    if name == 'TRAINING-CONFIGURATION.json':
        cfg = value['configuration']
        cfg['execution_binding']['worker'] = (x.HERE/'worker_v2.py').relative_to(x.ROOT).as_posix()
        cfg['execution_binding']['launcher'] = (x.HERE/'dispatch_v2.py').relative_to(x.ROOT).as_posix()
        value['canonical_sha256'] = x.identity(cfg)
    if name == 'EVALUATION-IDENTITIES.json':
        value['mapping'] = 'Reserved scope name -> R675 + family E01/E02/E03 + N + requirement index + R1/R2; grammar-valid <=32 characters'
    original_write(name,value)


x.corrected = corrected
x.write = write
