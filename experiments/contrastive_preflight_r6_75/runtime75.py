"""Successor runtime binding; CPU dry gate precedes every model boundary."""
import json
import os
import time
import context75 as integration
import resources75 as c
from context75 import ROOT, STORE, ARTIFACTS, canonical, file_manifest, frozen_check, identity, q52, rows, score, sha

OUT = integration.OUT/'execution'


def read(path):
    if not path.exists() and path.parent == OUT:
        path = integration.OUT/path.name
    return integration.read(path)


def write(name, value):
    path = OUT/name
    temporary = path.with_suffix(path.suffix+'.pending')
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False)+'\n', encoding='utf-8', newline='\n')
    temporary.replace(path)


def validate_configuration(cfg):
    baseline = integration.read(integration.OLD/'TRAINING-CONFIGURATION.json')['configuration']
    mutable = {'round', 'checkpoint_output_root', 'checkpoint_output_paths', 'logging',
               'evaluation_manifest', 'status', 'execution_binding'}
    assert set(cfg) == set(baseline) | {'execution_binding'}, 'INCOMPLETE_CONFIGURATION'
    for key in set(baseline)-mutable:
        assert cfg[key] == baseline[key], 'TRAINING_CONFIGURATION_DRIFT:' + key
    assert cfg['round'] == 'R6.75'
    assert cfg['checkpoint_output_root'] == str(ARTIFACTS)
    assert cfg['checkpoint_output_paths'] == [str(ARTIFACTS/f'step{s}') for s in (27,54)]
    assert cfg['logging'] == dict(baseline['logging'], directory=str(OUT))
    binding = cfg['execution_binding']
    required = {'worker', 'launcher', 'runtime', 'resource', 'evaluation', 'normalization',
                'worker_source_sha256', 'runtime_source_sha256', 'dataset', 'sampling',
                'loss_policy', 'schedule', 'interpreter', 'launch_modes', 'dry_boundary'}
    assert set(binding) == required, 'INCOMPLETE_EXECUTION_BINDING'
    for key in ('worker','launcher','runtime','resource','evaluation','normalization','dataset','sampling','loss_policy','schedule'):
        assert (ROOT/binding[key]).is_file(), key
    assert binding['interpreter'] == str(integration.PYTHON)
    assert binding['launch_modes'] == ['base','train','adapter']
    assert binding['worker_source_sha256'] == sha(integration.OUT/'EFFECTIVE-WORKER.py.txt')
    assert binding['runtime_source_sha256'] == sha(integration.OUT/'EFFECTIVE-DIAGNOSTIC.py.txt')
    assert cfg['evaluation_manifest'] == binding['evaluation']
    assert cfg['status'] == 'FROZEN_CPU_PREFLIGHT'
    assert binding['dry_boundary'] == 'Before model load, CUDA operations and optimizer/scheduler construction'


def launch_check(mode):
    integration.guard()
    frozen_check()
    cfg = read(OUT/'TRAINING-CONFIGURATION.json')['configuration']
    validate_configuration(cfg)
    assert mode in cfg['execution_binding']['launch_modes']
    sample = c.measure()
    c.validate(sample, os.getpid(), cfg['limits']['process_rss_bytes'])
    assert callable(q52.load_base) and callable(q52.encoded) and callable(score)
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(STORE/'checkpoint', local_files_only=True, trust_remote_code=False)
    if mode == 'train':
        assert len(rows()) == 54
        for row in rows():
            ids, labels, measurement = q52.encoded(row, tokenizer)
            assert len(ids) <= cfg['max_sequence_length'] and not measurement['truncated']
            assert sum(v != -100 for v in labels[1:]) == measurement['supervised_tokens_including_eos']
    else:
        for row in read(OUT/'EVALUATION.json')['records']:
            prompt = tokenizer.apply_chat_template(row['prompt'], tokenize=True, add_generation_prompt=True)
            assert len(prompt)+64 <= 2048
            assert integration.serialize(row['target']) in integration.CompletionLanguage(row['scope']).terminals
    import torch
    assert not torch.cuda.is_initialized()
    return dict(mode=mode, pid=os.getpid(), interpreter=__import__('sys').executable,
                resource=sample, configuration_identity=identity(cfg), dry_boundary_reached=True,
                model_loads=0, inference_calls=0, backward_calls=0, optimizer_instances=0,
                scheduler_instances=0, optimizer_updates=0, scheduler_updates=0, cuda_initialized=False)


def diagnostic_source():
    source = (integration.OLD.parent.parent.parent.parent/'experiments/contrastive_preflight_r6_74/runtime.py').read_text(encoding='utf-8')
    source = source[source.index('def diagnostic(track):'):]
    source = source.replace('def diagnostic(track):\n', "def diagnostic(track):\n    if os.environ.get('LYKOI_R6_75_DRY_RUN') == '1':\n        return launch_check(track)\n", 1)
    source = source.replace('from integration import CompletionLanguage, serialize', 'from context75 import CompletionLanguage, serialize')
    return source


exec(compile(diagnostic_source(), 'r675-diagnostic-definitions', 'exec'))
