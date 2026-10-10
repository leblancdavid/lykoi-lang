"""R6.55 prospective optimizer resolution, read-only preflight and halt seal."""
import hashlib
import importlib.util
import inspect
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'benchmark/results/phase6/r6_55'
spec = importlib.util.spec_from_file_location('r54', ROOT / 'experiments/lora_smoke_r6_54/publication.py')
r54 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r54)
r53 = r54.r53


def write(name, value):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n',
                            encoding='utf-8', newline='\n')


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')


def identity(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def qualify():
    previous = {str(n): r53.identities(ROOT / f'benchmark/results/phase6/r6_{n}') for n in (52, 53, 54)}
    r53.write = lambda name, value: write('SOURCE-' + name, value)
    r53.preflight()
    import torch
    assert torch.__version__ == '2.7.1+cu128'
    signature = inspect.signature(torch.optim.AdamW)
    defaults = {name: param.default for name, param in signature.parameters.items() if name != 'params'}
    assert defaults == dict(lr=0.001, betas=(0.9, 0.999), eps=1e-8, weight_decay=0.01,
                            amsgrad=False, maximize=False, foreach=None, capturable=False,
                            differentiable=False, fused=None)
    resolved = dict(defaults, lr=1e-4, weight_decay=0)
    optimizer = {'implementation': 'torch.optim.AdamW', 'torch_version': torch.__version__,
                 'parameter_selection': 'only trainable q_proj/v_proj LoRA parameters',
                 'kwargs': resolved}
    write('OPTIMIZER-CONFIGURATION.json', {
        'round': 'R6.55', 'status': 'COMPLETE', 'configuration': optimizer,
        'canonical_sha256': identity(optimizer),
        'canonical_encoding': 'UTF-8 JSON, sorted keys, separators comma/colon, no trailing newline; tuples as arrays',
        'installed_signature': str(signature), 'installed_defaults': defaults,
        'installed_docstring': inspect.getdoc(torch.optim.AdamW),
        'implementation_file_sha256': r53.sha(Path(inspect.getfile(torch.optim.AdamW))),
        'default_adoption_authorized': True,
        'overrides': {'lr': {'value': 1e-4, 'source': 'R6.51 and R6.55'},
                      'weight_decay': {'value': 0, 'installed_default': 0.01,
                                       'source': 'R6.51 lines25-26; R6.55 preserve frozen overrides'}},
        'optimizer_instantiated': False})
    source_paths = [ROOT / name for name in (
        'benchmark/results/phase6/r6_51/SMOKE-AND-EVALUATION.md',
        'benchmark/results/phase6/R6_52-REPORT.md',
        'benchmark/results/phase6/r6_52/REPRODUCIBILITY.md',
        'benchmark/results/phase6/r6_53/TRAINING-CONFIGURATION.json',
        'benchmark/results/phase6/r6_54/TRAINING-CONFIGURATION.json',
        'experiments/training_setup_r6_52/qualify.py')]
    source_paths += sorted(ROOT.glob('docs/*-r6.5[1234].md'))
    gaps = [
        {'field': 'training_record_sampling_order',
         'published': 'cycling six examples; seed/data_seed651; workers0',
         'missing': 'fixed E01-E06 cycling versus seeded reshuffle, permutation algorithm and epoch boundary behavior',
         'why_critical': 'Different four-record update groups and record counts across80 presentations change gradients; a seed does not choose a sampler.'},
        {'field': 'gradient_accumulation_loss_normalization',
         'published': 'completion token cross-entropy; microbatch1; accumulation4',
         'missing': 'equal mean per-record loss divided by4 versus pooled supervised-token mean over the four microbatches',
         'why_critical': 'Supervised token lengths329,370,425,461,331,410 differ; these reductions weight the records differently. R6.52 only probes single-record backward.'}]
    write('CONFIGURATION-AUDIT.json', {
        'round': 'R6.55', 'status': 'HALT', 'sources': {p.relative_to(ROOT).as_posix(): r53.sha(p) for p in source_paths},
        'unresolved_training_critical_fields': gaps,
        'optimizer_defaults_do_not_resolve_these_fields': True,
        'scope': 'configuration audit; no new sampler, reduction or training loop chosen',
        'diagnostic_protocol': 'R6.51 six resubstitution prompts and decoding proposal; concrete scoring/prompt manifest not qualified or executed after configuration halt'})
    config = r53.read(ROOT / 'benchmark/results/phase6/r6_54/TRAINING-CONFIGURATION.json')
    for key in ('blocking_gap', 'additional_explicitness_gap', 'adamw_betas_explicitly_published',
                'adamw_epsilon_explicitly_published'):
        config.pop(key)
    config.update(round='R6.55', optimizer_configuration=optimizer, optimizer_canonical_sha256=identity(optimizer),
                  training_record_sampling_order=None, gradient_accumulation_loss_normalization=None,
                  status='INCOMPLETE_TRAINING_CRITICAL_CONFIGURATION', executable_training_configuration_frozen=False,
                  blocking_fields=[g['field'] for g in gaps],
                  scheduler_manifest_sha256=r53.sha(ROOT / 'benchmark/results/phase6/r6_54/LEARNING-RATE-SCHEDULE.json'))
    write('TRAINING-CONFIGURATION.json', {'configuration': config, 'canonical_sha256': identity(config),
          'identity_is_inventory_not_executable_training_freeze': True})
    write('PREFLIGHT.json', {'round': 'R6.55', 'identity_checks': 'PASS', 'complete_training_configuration': 'HALT',
          'previous_publications': previous, 'source_preflight_sha256': r53.sha(OUT / 'SOURCE-PREFLIGHT.json'),
          'source_dataset_sha256': r53.sha(OUT / 'SOURCE-DATASET-IDENTITIES.json'),
          'optimizer_canonical_sha256': identity(optimizer), 'scheduler_preserved': True,
          'environment_package_trees_verified': 47, 'model_loaded': False, 'cuda_allocated_for_training': False})
    write('RESULT.json', {'round': 'R6.55', 'classification': 'R6_55_PROTOCOL_HALT',
          'first_blocker': 'TRAINING_RECORD_SAMPLING_ORDER_NOT_FROZEN', 'blocking_fields': [g['field'] for g in gaps],
          'training_runs': 0, 'actual_optimizer_steps': 0, 'actual_scheduler_updates': 0,
          'record_exposures': 0, 'training_tokens': 0, 'optimizer_instantiated': False,
          'model_loaded': False, 'model_inference_calls': 0, 'kernel_constructs': 26,
          'historical_acceptance_executions': 0, 'P6_A04_acceptance_executions': 0, 'P6_A05_content_access': False})
    write('EVALUATION-AND-ADAPTER-STATUS.json', {
        'base_diagnostic': 'NOT_REACHED', 'training_losses': [], 'learning_rates_used': [], 'gradient_norms': [],
        'peak_gpu_allocated_bytes': None, 'peak_gpu_reserved_bytes': None, 'training_wall_seconds': None,
        'cuda_or_numerical_training_errors': 'NOT_REACHED', 'trained_adapter_identity': None,
        'adapter_parameter_changes': 'NOT_REACHED', 'fresh_process_trained_reload': 'NOT_REACHED',
        'base_vs_adapter_comparison': 'NOT_REACHED', 'training_target_reproduction': 'NOT_REACHED',
        'memorization_assessment': 'NOT_REACHED', 'diagnostic_scores': None,
        'inference_time_seconds': None, 'inference_output_tokens': 0,
        'external_checkpoint_and_untrained_adapter_identity': 'PASS; see SOURCE-PREFLIGHT.json',
        'in_memory_base_weight_preservation_after_update': 'NOT_REACHED; no update or model load'})
    print('PASS inherited identities and complete AdamW resolution; HALT sampling order/loss normalization; model updates0')


def inventory():
    paths = [Path(__file__).resolve(), ROOT / 'benchmark/results/phase6/R6_55-REPORT.md']
    paths += [ROOT / f'docs/{name}-r6.55.md' for name in ('project-overview', 'research-log', 'decisions')]
    paths += [p for p in OUT.iterdir() if p.is_file() and p.name not in ('PUBLICATION-IDENTITIES.json', 'VERIFICATION.json')]
    return sorted(paths)


def manifest():
    return {'round': 'R6.55', 'files': {p.relative_to(ROOT).as_posix():
            {'sha256': r53.sha(p), 'bytes': p.stat().st_size} for p in inventory()},
            'excluded': ['PUBLICATION-IDENTITIES.json', 'VERIFICATION.json']}


def verify():
    assert r53.read(OUT / 'PUBLICATION-IDENTITIES.json') == manifest()
    previous = {str(n): r53.identities(ROOT / f'benchmark/results/phase6/r6_{n}') for n in (52, 53, 54)}
    assert previous == r53.read(OUT / 'PREFLIGHT.json')['previous_publications']
    baseline = r53.prior.baseline()
    assert baseline == r53.read(OUT / 'SOURCE-PREFLIGHT.json')['baseline']
    assert r53.prior.external() == r53.read(OUT / 'SOURCE-PREFLIGHT.json')['external_assets']
    for name in ('OPTIMIZER-CONFIGURATION.json', 'TRAINING-CONFIGURATION.json'):
        record = r53.read(OUT / name)
        assert identity(record['configuration']) == record['canonical_sha256']
    for name, digest in r53.read(OUT / 'CONFIGURATION-AUDIT.json')['sources'].items():
        assert r53.sha(ROOT / name) == digest
    assert not subprocess.check_output(['git', 'diff', 'HEAD', '--name-only'], cwd=ROOT, text=True).strip()
    allowed = set(manifest()['files']) | {'benchmark/results/phase6/r6_55/' + n
              for n in ('PUBLICATION-IDENTITIES.json', 'VERIFICATION.json')}
    for line in subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=all'], cwd=ROOT, text=True).splitlines():
        assert line.startswith('?? ') and line[3:].replace('\\', '/') in allowed, line
    for p in inventory():
        data = p.read_bytes()
        text = data.decode('utf-8')
        assert data.endswith(b'\n') and b'\r' not in data
        assert not any(s.endswith((' ', '\t')) for s in text.splitlines())
        assert not re.search(r'(?:sk-[A-Za-z0-9_-]{32,}|ghp_[A-Za-z0-9]{32,}|hf_[A-Za-z0-9]{32,})', text)
        if p.suffix == '.json':
            r53.read(p)
        if p.suffix == '.py':
            compile(text, str(p), 'exec')
        if p.suffix == '.md':
            for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)', text):
                if '://' not in target and not target.startswith('#'):
                    assert (p.parent / target.split('#')[0]).resolve().is_file(), target
    subprocess.run(['git', 'diff', '--check'], cwd=ROOT, check=True)
    return {'round': 'R6.55', 'passed': True, 'manifest_sha256': r53.sha(OUT / 'PUBLICATION-IDENTITIES.json'),
            'payload_files': len(inventory()), 'baseline': baseline, 'previous_publications': previous,
            'tracked_diff_empty': True, 'git_diff_check_returncode': 0,
            'publication_json_source_links_whitespace_checks': 'PASS', 'credential_pattern_scan': 'PASS',
            'preservation_failures': [], 'model_optimizer_steps': 0}


if __name__ == '__main__':
    os.environ['HF_HUB_OFFLINE'] = '1'
    os.environ['HF_HUB_DISABLE_TELEMETRY'] = '1'
    if sys.argv[1] == 'qualify':
        qualify()
    elif sys.argv[1] == 'seal':
        write('PUBLICATION-IDENTITIES.json', manifest())
        write('VERIFICATION.json', verify())
    elif sys.argv[1] == 'check':
        result = verify()
        assert result == r53.read(OUT / 'VERIFICATION.json')
        print(json.dumps(result, sort_keys=True))
    else:
        raise ValueError('unknown mode')
