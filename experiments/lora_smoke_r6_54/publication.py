"""Prospective scheduler qualification and publication. No LLM optimizer updates."""
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
OUT = ROOT / 'benchmark/results/phase6/r6_54'
spec = importlib.util.spec_from_file_location('r6_53_publication', ROOT / 'experiments/lora_smoke_r6_53/publication.py')
r53 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r53)


def write(name, value):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n',
                            encoding='utf-8', newline='\n')


def qualify():
    preserved = r53.identities(ROOT / 'benchmark/results/phase6/r6_53')
    assert r53.read(ROOT / 'benchmark/results/phase6/r6_53/RESULT.json')['classification'] == 'R6_53_PROTOCOL_HALT'
    # Reuse read-only checks, redirecting all new evidence into this round.
    r53.write = lambda name, value: write('SOURCE-' + name, value)
    r53.preflight()
    import torch
    import transformers
    from transformers.optimization import get_linear_schedule_with_warmup
    from fractions import Fraction
    # An inert CPU scalar/SGD is sufficient to exercise LambdaLR semantics.
    # It is not the selected AdamW training optimizer and has no model/data/gradients.
    scalar = torch.nn.Parameter(torch.tensor(1.0))
    optimizer = torch.optim.SGD([scalar], lr=1e-4)
    scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=2, num_training_steps=20)
    assert scheduler.last_epoch == 0 and optimizer.param_groups[0]['lr'] == 0
    sequence = []
    microsteps = 0
    skipped_controls = 0
    for step in range(1, 21):
        used = optimizer.param_groups[0]['lr']
        epoch = scheduler.last_epoch
        for _ in range(4):
            microsteps += 1
            assert scheduler.last_epoch == epoch and optimizer.param_groups[0]['lr'] == used
        # Failed/skipped update branch deliberately calls neither step method.
        before = scheduler.state_dict()
        assert scheduler.state_dict() == before and scheduler.last_epoch == epoch
        skipped_controls += 1
        assert scalar.grad is None
        optimizer.step()
        scheduler.step()
        assert scheduler.last_epoch == step
        factor = Fraction(step, 2) if step < 2 else Fraction(20 - step, 18)
        expected = 1e-4 * float(factor)
        actual = optimizer.param_groups[0]['lr']
        assert actual == expected
        used_factor = Fraction(step - 1, 2) if step - 1 < 2 else Fraction(21 - step, 18)
        assert used == 1e-4 * float(used_factor)
        sequence.append({'optimizer_step': step, 'completed_microsteps': microsteps,
                         'lr_used_by_update': used, 'lr_after_scheduler_step': actual,
                         'used_peak_lr_multiplier': str(used_factor),
                         'post_step_peak_lr_multiplier': str(factor)})
    assert scalar.item() == 1.0 and scalar.grad is None
    assert sequence[1]['lr_after_scheduler_step'] == 1e-4
    assert sequence[-1]['lr_after_scheduler_step'] == 0
    source = inspect.getsource(get_linear_schedule_with_warmup)
    helper = inspect.getsource(transformers.optimization._get_linear_schedule_with_warmup_lr_lambda)
    write('LEARNING-RATE-SCHEDULE.json', {
        'round': 'R6.54', 'status': 'PASS', 'framework': 'transformers', 'version': transformers.__version__,
        'torch_version': torch.__version__, 'scheduler': 'get_linear_schedule_with_warmup / torch LambdaLR',
        'scheduler_constructor_source': source, 'scheduler_lambda_source': helper,
        'scheduler_module_sha256': r53.sha(Path(inspect.getfile(get_linear_schedule_with_warmup))),
        'peak_learning_rate': 1e-4, 'warmup_steps': 2, 'total_optimizer_steps': 20,
        'initial_scheduler_index': 0, 'initial_learning_rate': 0,
        'factor_definition': 'f(k)=k/2 for 0<=k<2; f(k)=max(0,(20-k)/18) for k>=2',
        'update_order': 'optimizer.step() then scheduler.step() once on successful update only',
        'update_lr_definition': 'update s uses 1e-4*f(s-1); after update s scheduler installs 1e-4*f(s)',
        'sequence': sequence, 'final_learning_rate': 0,
        'qualification_only_inert_cpu_sgd_step_calls': 20, 'qualification_microstep_controls': microsteps,
        'qualification_skipped_update_controls': skipped_controls, 'scalar_parameter_unchanged': True,
        'model_optimizer_steps': 0, 'training_data_processed': 0,
        'limitations': 'Controls qualify scheduler semantics and intended guard/accounting only; no training loop or failure-detection path is qualified.'})
    config = r53.read(ROOT / 'benchmark/results/phase6/r6_53/TRAINING-CONFIGURATION.json')
    config.update(round='R6.54', scheduler='linear warmup then linear decay',
                  scheduler_post_warmup_behavior='peak at index2; linear decay to zero at index20',
                  scheduler_step_order='optimizer.step then scheduler.step only on completed, unskipped update',
                  blocking_gap='AdamW beta coefficients and epsilon not previously fixed or explicitly authorized as framework defaults',
                  status='INCOMPLETE_OPTIMIZER_CONFIGURATION', executable_training_configuration_frozen=False)
    write('TRAINING-CONFIGURATION.json', config)
    write('CONFIGURATION-QUALIFICATION.json', {
        'round': 'R6.54', 'status': 'HALT', 'r6_53_publication': preserved,
        'source_preflight': 'PASS', 'completion_only_masking': 'PASS', 'scheduler_semantics': 'PASS',
        'gradient_accumulation_accounting_controls': 'PASS: 4 microsteps per schedule tick; 80 for20',
        'limits_match_published_proposal': config['limits'], 'limits_exercised_in_training': False,
        'first_blocker': 'REQUIRED_ADAMW_BETAS_AND_EPSILON_NOT_PREVIOUSLY_FIXED',
        'published_optimizer_fields': {'optimizer': config['optimizer'], 'learning_rate': config['learning_rate'],
                                       'weight_decay': config['weight_decay'], 'max_grad_norm': config['max_grad_norm']},
        'missing_required_optimizer_fields': ['betas', 'eps'],
        'qualified_framework_adamw_signature_for_inspection_only': str(inspect.signature(torch.optim.AdamW)),
        'framework_defaults_adopted': False, 'adamw_instantiated': False,
        'inert_scheduler_control_optimizer': 'CPU SGD, no gradients; not model training',
        'model_loaded': False, 'actual_training_optimizer_steps': 0})
    print('PASS identities and exact linear schedule; HALT: AdamW betas/eps not previously fixed')


def inventory():
    paths = [Path(__file__).resolve(), ROOT / 'benchmark/results/phase6/R6_54-REPORT.md']
    paths += [ROOT / f'docs/{name}-r6.54.md' for name in ('project-overview', 'research-log', 'decisions')]
    paths += [p for p in OUT.iterdir() if p.is_file() and p.name not in ('PUBLICATION-IDENTITIES.json', 'VERIFICATION.json')]
    return sorted(paths)


def manifest():
    return {'round': 'R6.54', 'files': {p.relative_to(ROOT).as_posix():
            {'sha256': r53.sha(p), 'bytes': p.stat().st_size} for p in inventory()},
            'excluded': ['PUBLICATION-IDENTITIES.json', 'VERIFICATION.json']}


def verify():
    assert r53.read(OUT / 'PUBLICATION-IDENTITIES.json') == manifest()
    preserved = r53.identities(ROOT / 'benchmark/results/phase6/r6_53')
    r53.identities(ROOT / 'benchmark/results/phase6/r6_52')
    baseline = r53.prior.baseline()
    assert baseline == r53.read(OUT / 'SOURCE-PREFLIGHT.json')['baseline']
    assert r53.prior.external() == r53.read(OUT / 'SOURCE-PREFLIGHT.json')['external_assets']
    assert preserved == r53.read(OUT / 'CONFIGURATION-QUALIFICATION.json')['r6_53_publication']
    historical = set(r53.read(ROOT / 'benchmark/results/phase6/r6_53/PUBLICATION-IDENTITIES.json')['files'])
    historical |= {'benchmark/results/phase6/r6_53/' + n for n in ('PUBLICATION-IDENTITIES.json', 'VERIFICATION.json')}
    allowed = set(manifest()['files']) | historical | {'benchmark/results/phase6/r6_54/' + n
              for n in ('PUBLICATION-IDENTITIES.json', 'VERIFICATION.json')}
    assert not subprocess.check_output(['git', 'diff', '--name-only'], cwd=ROOT, text=True).strip()
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
                    resolved = (p.parent / target.split('#')[0]).resolve()
                    assert resolved.is_file() or resolved == OUT / 'VERIFICATION.json', target
    subprocess.run(['git', 'diff', '--check'], cwd=ROOT, check=True)
    result = r53.read(OUT / 'RESULT.json')
    assert result['classification'] == 'R6_54_PROTOCOL_HALT' and result['actual_optimizer_steps'] == 0
    return {'round': 'R6.54', 'passed': True, 'manifest_sha256': r53.sha(OUT / 'PUBLICATION-IDENTITIES.json'),
            'payload_files': len(inventory()), 'baseline': baseline, 'r6_53_preserved': preserved,
            'tracked_diff_empty': True, 'git_diff_check_returncode': 0, 'preservation_failures': [],
            'publication_whitespace_links_json_source_checks': 'PASS', 'credential_pattern_scan': 'PASS',
            'training_optimizer_steps': 0, 'scheduler_control_steps': 20}


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
