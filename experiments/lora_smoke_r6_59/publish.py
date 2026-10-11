"""Read-only result analysis and additive publication integrity; no model dispatch."""
import ast
from collections import Counter
import re
import subprocess
import sys
import run

c, ROOT, OUT, HERE = run.c, run.ROOT, run.OUT, run.HERE


def executable_identities():
    env = c.read(ROOT / 'benchmark/results/phase6/r6_52/ENVIRONMENT-IDENTITIES.json')
    home = run.STORE / 'python/cpython-3.12.11-windows-x86_64-none'
    paths = {'python_executable_sha256': home / 'python.exe', 'python_dll_sha256': home / 'python312.dll',
             'venv_executable_sha256': run.PYTHON, 'uv_executable_sha256': run.STORE / 'uv/uv.exe',
             'requirements_lock_sha256': ROOT / 'benchmark/results/phase6/r6_52/requirements-lock.txt'}
    result = {key: c.sha(path) for key, path in paths.items()}
    assert all(result[key] == env[key] for key in result)
    return result


def gather():
    run.frozen_check()
    assert run.baseline() == c.read(OUT / 'BASELINE.json')
    run.write('EXECUTABLE-IDENTITY-SUPPLEMENT.json', {'status': 'PASS', 'identities': executable_identities(),
        'measurement_stage': 'post-training publication; pre-dispatch inherited verifier rechecked package trees and checkpoint but did not freshly hash these executables',
        'matches_original_r6_52': True})
    training = c.read(OUT / 'TRAINING-RESULT.json')
    micros = c.read(OUT / 'MICROSTEPS.json')['records']
    steps = c.read(OUT / 'TRAINING-STEPS.json')['steps']
    accounting = c.read(OUT / 'UPDATE-ACCOUNTING.json')
    reload = c.read(OUT / 'ADAPTER-RELOAD.json')
    sequence = c.read(OUT / 'SAMPLING.json')['sequence']
    assert training['successful_optimizer_steps'] == training['scheduler_updates'] == len(steps) == 20
    assert len(micros) == 80 and [m['episode_id'] for m in micros] == [s['episode_id'] for s in sequence]
    assert all(m['cache_preserved_gradients'] for m in micros)
    assert accounting['optimizer_calls'] == accounting['scheduler_calls'] == 20
    assert accounting['optimizer_state_steps'] == [20] * 112
    assert accounting['scheduler_state']['last_epoch'] == 20 and 'step' not in accounting['scheduler_state']
    schedule = c.read(ROOT / 'benchmark/results/phase6/r6_54/LEARNING-RATE-SCHEDULE.json')['sequence']
    for step, expected in zip(steps, schedule):
        assert step['lr_used'] == expected['lr_used_by_update']
        assert step['lr_after_scheduler'] == expected['lr_after_scheduler_step']
        assert step['mean_record_loss'] == sum(step['record_losses']) / 4
        assert step['base_tensor_identity_unchanged']
    assert training['base_unchanged'] and training['changed_tensor_count'] == 112
    assert reload['status'] == 'PASS' and reload['reference_logits_bitwise_equal'] and reload['base_tensors_match']
    base = c.read(OUT / 'DIAGNOSTIC-BASE-SUMMARY.json')
    adapter = c.read(OUT / 'DIAGNOSTIC-ADAPTER-SUMMARY.json')
    assert base['completed_calls'] == adapter['completed_calls'] == 6
    comparisons = []
    for before, after in zip(base['results'], adapter['results']):
        assert before['episode_id'] == after['episode_id'] and before['prompt_sha256'] == after['prompt_sha256']
        assert before['input_tokens'] == after['input_tokens'] and before['quantization'] == after['quantization']
        row = next(r for r in c.rows() if r['episode_id'] == after['episode_id'])
        assert c.score(before['output'], row) == before['scores']
        assert c.score(after['output'], row) == after['scores']
        comparisons.append({'episode_id': before['episode_id'], 'base_scores': before['scores'], 'adapter_scores': after['scores'],
            'output_changed': before['output'] != after['output'], 'base_tokens': before['output_tokens'], 'adapter_tokens': after['output_tokens'],
            'base_inference_seconds': before['inference_seconds'], 'adapter_inference_seconds': after['inference_seconds']})
    run.write('DIAGNOSTIC-COMPARISON.json', {'base_metrics': base['metrics'], 'adapter_metrics': adapter['metrics'], 'records': comparisons,
        'base_output_tokens': base['output_tokens'], 'adapter_output_tokens': adapter['output_tokens'],
        'base_inference_seconds': base['inference_seconds'], 'adapter_inference_seconds': adapter['inference_seconds'],
        'baseline_reused': True, 'configuration_differences': [], 'unseen_generalization': False})
    losses = []
    for eid in training['record_counts']:
        observations = [m for m in micros if m['episode_id'] == eid]
        losses.append({'episode_id': eid, 'presentations': len(observations),
                      'first_loss': observations[0]['mean_record_loss'], 'last_loss': observations[-1]['mean_record_loss'],
                      'relative_decrease': 1 - observations[-1]['mean_record_loss'] / observations[0]['mean_record_loss']})
    memories = [m[boundary] for m in micros for boundary in ('before_cache_release', 'after_cache_release')]
    minimum = min(training['minimum_sampled_device_free_bytes'], *(m['device_free_bytes'] for m in memories))
    result = {'classification': 'R6_59_LORA_SMOKE_SUPPORTED', 'successful_optimizer_steps': 20, 'scheduler_updates': 20,
        'presentations': 80, 'record_counts': dict(Counter(m['episode_id'] for m in micros)), 'loss_by_record_first_last': losses,
        'step_losses': [s['mean_record_loss'] for s in steps], 'gradient_norms_preclip': [s['preclip_gradient_norm'] for s in steps],
        'lr_used': [s['lr_used'] for s in steps], 'peak_allocated_bytes': training['peak_allocated_bytes'],
        'peak_reserved_bytes': training['peak_reserved_bytes'], 'minimum_retained_device_free_bytes': minimum,
        'training_wall_seconds': training['training_wall_seconds'], 'whole_training_process_seconds': c.read(OUT / 'TRAINING-PROCESS.json')['seconds'],
        'cache_releases': 80, 'exact_gradient_preservation_checks': 80, 'adapter_content_identity': training['adapter_content_identity'],
        'changed_adapter_tensors': 112, 'fresh_reload': 'PASS', 'kernel_constructs': 26, 'cuda_errors': [], 'numerical_errors': [],
        'training_attempts': 1, 'retries': 0, 'base_diagnostic_reruns': 0,
        'P6_A04_acceptance_executions': 0, 'P6_A05_access': False,
        'learning_assessment': 'changed adapter parameters and falling repeated-record teacher-forced loss; no strict or functional acceptance improvement',
        'memorization_assessment': 'exact/normalized target reproduction 0/6; six exposed repeated records cannot distinguish task learning from partial memorization',
        'recommendation': 'separately authorize a read-only fixed-input paired base/trained teacher-forced loss evaluation with dropout off; no further training or dataset expansion'}
    run.write('RESULT.json', result)
    run.write('EXTERNAL-ARTIFACTS.json', {'directory': str(run.ARTIFACTS), 'files': c.file_manifest(run.ARTIFACTS)})
    print(__import__('json').dumps(result, indent=2))


def manifest():
    paths = list(HERE.glob('*.py')) + [ROOT / 'benchmark/results/phase6/R6_59-REPORT.md']
    paths += list(ROOT.glob('docs/*-r6.59.md'))
    paths += [p for p in OUT.rglob('*') if p.is_file() and p.name not in ('PUBLICATION-IDENTITIES.json', 'VERIFICATION.json')]
    return {'round': 'R6.59', 'files': {p.relative_to(ROOT).as_posix(): {'sha256': c.sha(p), 'bytes': p.stat().st_size} for p in sorted(paths)},
            'excluded': ['PUBLICATION-IDENTITIES.json', 'VERIFICATION.json']}


def verify():
    saved = c.read(OUT / 'PUBLICATION-IDENTITIES.json')
    assert manifest() == saved
    assert run.baseline() == c.read(OUT / 'BASELINE.json')
    assert executable_identities() == c.read(OUT / 'EXECUTABLE-IDENTITY-SUPPLEMENT.json')['identities']
    run.frozen_check()
    worker = run.load('r59_verified_worker', 'experiments/lora_smoke_r6_59/worker.py')
    source = worker.effective_source()
    assert source == (OUT / 'EFFECTIVE-WORKER.py.txt').read_text(encoding='utf-8')
    assert not re.search(r'(?:optimizer|scheduler)\.step\s*=', source)
    assert c.file_manifest(run.ARTIFACTS) == c.read(OUT / 'EXTERNAL-ARTIFACTS.json')['files']
    for step in (10, 20):
        assert c.file_manifest(run.ARTIFACTS / f'step{step}') == c.read(OUT / f'CHECKPOINT-{step}.json')['files']
    assert not subprocess.check_output(['git', 'diff', 'HEAD', '--name-only'], cwd=ROOT, text=True).strip()
    allowed = set(saved['files']) | {'benchmark/results/phase6/r6_59/PUBLICATION-IDENTITIES.json', 'benchmark/results/phase6/r6_59/VERIFICATION.json'}
    for path in subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard'], cwd=ROOT, text=True).splitlines():
        assert path in allowed, path
    for name in saved['files']:
        path = ROOT / name
        data = path.read_bytes()
        text = data.decode('utf-8')
        if path.suffix == '.json':
            __import__('json').loads(text)
        if path.suffix == '.py':
            ast.parse(text)
        # Preserve the native Windows raw worker claim exactly as emitted.
        if path.name != 'TRAINING-RUN-CLAIM.json':
            assert b'\r' not in data, name
        assert all(line == line.rstrip() for line in text.splitlines()), name
        assert not re.search(r'(?:hf_[A-Za-z0-9]{25,}|sk-[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})', text), name
        if path.suffix == '.md':
            for target in re.findall(r'\]\(([^)]+)\)', text):
                if '://' not in target and not target.startswith('#'):
                    assert (path.parent / target.split('#')[0]).exists(), (name, target)
    p = subprocess.run(['git', 'diff', '--check'], cwd=ROOT, capture_output=True, text=True)
    assert p.returncode == 0, p.stdout + p.stderr
    run.write('VERIFICATION.json', {'round': 'R6.59', 'passed': True, 'manifest_sha256': c.sha(OUT / 'PUBLICATION-IDENTITIES.json'),
        'payload_files': len(saved['files']), 'historical_environment_production_preserved': True, 'external_artifacts_verified': True,
        'effective_source_exact': True, 'source_json_links_whitespace_credentials': 'PASS', 'git_diff_check_returncode': p.returncode,
        'kernel_constructs': 26})
    print('PASS publication payload, external adapter/checkpoints, historical/environment identities, source, links and git diff --check')


if __name__ == '__main__':
    if sys.argv[1] == 'gather':
        gather()
    elif sys.argv[1] == 'seal':
        run.write('VERIFICATION.json', {'passed': False, 'status': 'verification pending'})
        run.write('PUBLICATION-IDENTITIES.json', manifest())
        verify()
    elif sys.argv[1] == 'verify':
        verify()
    else:
        raise ValueError(sys.argv[1])
