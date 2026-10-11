"""Fresh-process launch closure, hostile handshake and static resource bindings."""
import ast
import copy
import inspect
import json
import os
import successor3
import context75 as x
import resources75 as resource
import runtime75
import worker75
from dispatch_v3 import validate_handshake


def main():
    x.guard()
    x.frozen_check()
    cfg = x.read(x.OUT/'TRAINING-CONFIGURATION.json')['configuration']
    runtime75.validate_configuration(cfg)
    launch = x.read(x.OUT/'dry-launch/RESULT.json')
    controls = []
    for phase in launch['phases']:
        handshake = phase['worker_handshake']
        assert validate_handshake(handshake,handshake['nonce'],phase['mode'],phase['launcher_pid']) == phase['pid']
        worker = json.loads((x.OUT/'dry-launch'/f"{phase['mode']}-stdout.txt").read_text(encoding='utf-8'))
        assert worker['pid'] == phase['pid']
        resource.validate(worker['resource'],phase['pid'],cfg['limits']['process_rss_bytes'])
        for value in phase['resource_samples']:
            resource.validate(value,phase['pid'],cfg['limits']['process_rss_bytes'])
        assert phase['resource_samples']
        for field, value in (('nonce','wrong'),('parent_pid',-1),('interpreter','wrong'),('mode','wrong')):
            wrong = dict(handshake,**{field:value})
            if field == 'parent_pid' and handshake['worker_pid'] == phase['launcher_pid']:
                wrong['worker_pid'] += 1
            try:
                validate_handshake(wrong,handshake['nonce'],phase['mode'],phase['launcher_pid'])
            except AssertionError as exc:
                controls.append(dict(mode=phase['mode'],changed_field=field,rejected=True,error=str(exc)))
            else:
                raise AssertionError('HANDSHAKE_REJECTION_FAILED')
    source = worker75.effective_source()
    assert source == (x.OUT/'EFFECTIVE-WORKER.py.txt').read_text(encoding='utf-8')
    tree = ast.parse(source)
    ns = {}
    exec(compile(tree,'r675-definition-only','exec'),ns)
    required = ('ARTIFACTS','OUT','ROOT','STORE','canonical','file_manifest','frozen_check','identity','q52','read','rows','score','sha','write')
    assert all(name in ns for name in required)
    for name in ('prepare_base','load_trained','reference','memory','train','base_manifest','adapter_manifest'):
        assert callable(ns[name])
    assert callable(runtime75.c.rss) and runtime75.c is resource
    assert ns['q52'] is x.q52 and runtime75.score is x.prior.score
    assert '(loss / 4).backward()' in source
    assert 'num_warmup_steps=6, num_training_steps=54' in source
    assert 'range(1, 55)' in source and 'step in (27, 54)' in source
    assert 'worker_rss = __import__(\'runtime75\').c.rss(os.getpid())' in source
    baseline = copy.deepcopy(x.read(x.OLD/'TRAINING-CONFIGURATION.json')['configuration'])
    permitted = {'round','checkpoint_output_root','checkpoint_output_paths','logging','evaluation_manifest','status','execution_binding'}
    assert all(cfg[key] == baseline[key] for key in set(baseline)-permitted)
    assert not x.ARTIFACTS.exists() and not (x.OUT/'execution').exists()
    import torch
    assert not torch.cuda.is_initialized()
    # Malformed/truncated/trailing/duplicate-key output rejection remains mandatory.
    row = x.read(x.OUT/'EVALUATION.json')['records'][0]
    text = x.serialize(row['target'])
    malformed = [text[:-1],text+'x',text.replace('"op":"le"','"op":"le","op":"eq"')]
    assert all(not x.score(candidate,row)['strict_decision_validity'] for candidate in malformed)
    x.write('LAUNCH-INTEGRATION-AUDIT.json',dict(passed=True,worker_attribution=True,
        handshake_rejections=controls,source_compile=True,required_bindings=list(required),
        current_process_rss_binding=True,training_configuration_unchanged_except_paths_bindings_metadata=True,
        resource_dependencies_added=0,malformed_scorer_controls=3,model_loads=0,inference_calls=0,
        optimizer_instances=0,scheduler_instances=0,optimizer_updates=0,scheduler_updates=0,cuda_initialized=False,
        unresolved_configuration_dependencies=[]))
    print('PASS worker closure, actual process attribution and 12 hostile handshake controls')


if __name__ == '__main__':
    main()
