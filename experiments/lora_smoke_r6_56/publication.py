"""Read-only postmortem and additive R6.56 publication; never dispatches a model."""
import json
import importlib.util
from pathlib import Path
import re
import subprocess
import sys
from common import ARTIFACTS, OUT, ROOT, file_manifest, frozen_check, identity, read, rows, sha, write
spec = importlib.util.spec_from_file_location('r56_run', Path(__file__).parent / 'run.py')
r56_run = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r56_run)
inherited = r56_run.inherited


def gather():
    freeze = frozen_check()
    assert read(OUT / 'RESOURCE-ABORT.json') == {'completed_steps': 0, 'error': 'CUDA_RESERVED_LIMIT', 'presentations': 3}
    process = read(OUT / 'TRAINING-PROCESS.json')
    assert process['returncode'] == 71
    assert not (OUT / 'TRAINING-STEPS.json').exists()
    assert not (ARTIFACTS / 'step10').exists() and not (ARTIFACTS / 'step20').exists()
    micros = read(OUT / 'MICROSTEPS.json')
    assert micros['completed_presentations'] == 3
    initial = read(OUT / 'INITIAL-PARAMETERS.json')
    assert initial['adapter'] == read(ROOT / 'benchmark/results/phase6/r6_52/BACKWARD.json')['adapter_tensor_manifest']
    base = read(OUT / 'DIAGNOSTIC-BASE-SUMMARY.json')
    assert base['completed_calls'] == 6
    write('RESULT.json', {'round': 'R6.56', 'classification': 'R6_56_RESOURCE_OR_STACK_GAP',
          'first_blocker': 'CUDA_RESERVED_LIMIT', 'training_configuration_preflight': 'PASS',
          'training_configuration_identity': freeze['training_configuration_identity'],
          'training_runs': 1, 'optimizer_instantiated': True, 'scheduler_instantiated': True,
          'successful_optimizer_steps': 0, 'successful_scheduler_updates': 0,
          'planned_optimizer_steps': 20, 'planned_presentations': 80,
          'completed_logged_presentations': 3, 'possibly_inflight_presentation': 'R6.48/E04',
          'unlogged_inflight_processing_quantified': False,
          'completed_logged_supervised_tokens': sum(r['supervised_tokens'] for r in micros['records']),
          'completed_logged_sequence_tokens': 702 + 752 + 827,
          'model_inference_calls': 6, 'trained_adapter_identity': None,
          'restart_or_fallback': False, 'kernel_constructs': 26,
          'P6_A04_acceptance_executions': 0, 'P6_A05_content_access': False})
    write('TRAINING-MEASUREMENTS.json', {
        'status': 'RESOURCE_LIMIT_ABORT_BEFORE_FIRST_UPDATE', 'per_optimizer_step_losses': [],
        'completed_microbatch_losses': micros['records'], 'lr_used_by_optimizer_updates': [], 'gradient_norms': [],
        'initial_scheduler_lr': 0, 'optimizer_updates': 0, 'scheduler_updates': 0,
        'worker_process_wall_seconds_including_load': process['seconds'], 'training_loop_wall_seconds': None,
        'peak_training_allocated_bytes': None, 'peak_training_reserved_bytes': None,
        'peak_training_reserved_bytes_strict_lower_bound': 8589934592,
        'exact_peak_measurement_missing': 'memory() asserted on peak_reserved >8GiB before returning measurements; monitor abort packet retained reason/counts only',
        'minimum_sampled_device_free_bytes': None,
        'external_reported_peak_working_set_bytes': process['peak_sampled_rss_bytes'],
        'external_working_set_is_qualified_training_worker_rss': False,
        'rss_limitation': 'Polling the launched Windows venv process yielded only~4.7MiB; worker process-tree/launcher coverage is not attested. Do not report this as model-process RSS or successful enforcement of16GiB.',
        'cuda_oom_observed': False, 'numerical_error_observed': False,
        'all_model_gradients_finite_qualified': False, 'resource_abort_exit_code': 71,
        'partial_window_loss_is_not_optimizer_step_loss': True})
    write('EVALUATION-AND-ADAPTER-STATUS.json', {
        'baseline': base['metrics'], 'base_inference_seconds': base['inference_seconds'],
        'base_output_tokens': base['output_tokens'], 'base_completed_calls': 6,
        'trained_adapter_save': 'NOT_REACHED', 'trained_adapter_identity': None,
        'adapter_parameter_change': 'NOT_REACHED;0 updates', 'fresh_process_trained_reload': 'NOT_REACHED',
        'trained_inference_initialization': 'NOT_REACHED', 'post_training_diagnostics': 'NOT_REACHED',
        'base_vs_trained_comparison': 'NOT_REACHED', 'learning_or_memorization': 'NOT_MEASURED; no optimizer update',
        'initial_adapter_matches_R6_52': True,
        'in_memory_base_post_update_check': 'NOT_REACHED; no update',
        'checkpoint_external_hashes': 'verified again at publication', 'generalization_claim': False,
        'actual_training_steps': 0, 'partial_or_trained_checkpoint_artifacts': []})
    write('EXTERNAL-ARTIFACTS.json', {'directory': str(ARTIFACTS), 'files': file_manifest(ARTIFACTS),
          'content': 'process stdout/stderr only; no trained or merged model',
          'trained_adapter_present': False})
    print('Recorded single resource-limit abort; no rerun, adapter save/reload or post-training inference')


def inventory():
    paths = sorted(p for p in Path(__file__).parent.iterdir() if p.is_file())
    paths += [ROOT / 'benchmark/results/phase6/R6_56-REPORT.md']
    paths += [ROOT / f'docs/{n}-r6.56.md' for n in ('project-overview', 'research-log', 'decisions')]
    paths += [p for p in OUT.iterdir() if p.is_file() and p.name not in ('PUBLICATION-IDENTITIES.json', 'VERIFICATION.json')]
    return sorted(paths)


def manifest():
    return {'round': 'R6.56', 'files': {p.relative_to(ROOT).as_posix():
            {'sha256': sha(p), 'bytes': p.stat().st_size} for p in inventory()},
            'excluded': ['PUBLICATION-IDENTITIES.json', 'VERIFICATION.json']}


def verify():
    assert read(OUT / 'PUBLICATION-IDENTITIES.json') == manifest()
    freeze = frozen_check()
    r55 = inherited()
    previous = {str(n): r55.r53.identities(ROOT / f'benchmark/results/phase6/r6_{n}') for n in (52, 53, 54, 55)}
    assert previous == freeze['previous_publications']
    baseline = r55.r53.prior.baseline()
    assert baseline == read(OUT / 'SOURCE-PREFLIGHT.json')['baseline']
    assert r55.r53.prior.external() == read(OUT / 'SOURCE-PREFLIGHT.json')['external_assets']
    assert r55.r53.prior.package_identity() == read(ROOT / 'benchmark/results/phase6/r6_52/ENVIRONMENT-IDENTITIES.json')['packages']
    sampler = read(OUT / 'SAMPLING.json')
    sampler_id = sampler.pop('canonical_sha256')
    assert identity(sampler) == sampler_id == freeze['sampling_identity']
    assert [s['episode_id'] for s in sampler['sequence']] == [f'R6.48/E{i % 6 + 1:02d}' for i in range(80)]
    protocol = read(OUT / 'DIAGNOSTIC-PROTOCOL.json')
    protocol_id = protocol.pop('canonical_sha256')
    assert identity(protocol) == protocol_id
    assert identity(read(OUT / 'OPTIMIZER-CONFIGURATION.json')['configuration']) == freeze['optimizer_identity']
    initial = read(OUT / 'PREFLIGHT-INITIAL.json')
    assert sha(OUT / 'WORKER-INITIAL.py.txt') == initial['frozen_payloads']['experiments/lora_smoke_r6_56/worker.py']
    correction = read(OUT / 'PREUPDATE-ASSERTION-CORRECTION.json')
    assert correction['initial_preflight_sha256'] == sha(OUT / 'PREFLIGHT-INITIAL.json')
    assert correction['corrected_worker_sha256'] == sha(Path(__file__).parent / 'worker.py')
    assert correction['training_configuration_identity_unchanged'] == freeze['training_configuration_identity']
    assert sha(OUT / 'PREUPDATE-ASSERTION-CORRECTION.json') == freeze['preupdate_assertion_correction_sha256']
    result = read(OUT / 'RESULT.json')
    assert result['training_runs'] == 1 and result['successful_optimizer_steps'] == 0
    assert result['classification'] == 'R6_56_RESOURCE_OR_STACK_GAP'
    assert file_manifest(ARTIFACTS) == read(OUT / 'EXTERNAL-ARTIFACTS.json')['files']
    assert not (ARTIFACTS / 'step10').exists() and not (ARTIFACTS / 'step20').exists()
    for item in protocol['items']:
        assert sha(ROOT / item['acceptance_path']) == item['acceptance_sha256']
    base = read(OUT / 'DIAGNOSTIC-BASE-SUMMARY.json')
    for index, record in enumerate(base['results'], 1):
        assert record == read(OUT / f'DIAGNOSTIC-BASE-E{index:02d}.json')
        assert record['prompt_sha256'] == protocol['items'][index - 1]['prompt_identity']
        assert read(OUT / f'DIAGNOSTIC-BASE-E{index:02d}-PROCESS.json')['returncode'] == 0
    assert not subprocess.check_output(['git', 'diff', 'HEAD', '--name-only'], cwd=ROOT, text=True).strip()
    # R6.55 was already untracked at entry; preserve and allow its exact published files.
    allowed = set(manifest()['files']) | set(read(ROOT / 'benchmark/results/phase6/r6_55/PUBLICATION-IDENTITIES.json')['files'])
    allowed |= {f'benchmark/results/phase6/r6_{n}/{name}' for n in (55, 56)
                for name in ('PUBLICATION-IDENTITIES.json', 'VERIFICATION.json')}
    for line in subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=all'], cwd=ROOT, text=True).splitlines():
        assert line.startswith('?? ') and line[3:].replace('\\', '/') in allowed, line
    for path in inventory():
        data = path.read_bytes()
        text = data.decode('utf-8')
        assert data.endswith(b'\n'), str(path)
        if path.name == 'TRAINING-RUN-CLAIM.json':
            # Preserve the exclusive worker's original Windows text-mode receipt bytes.
            assert b'\r' not in data.replace(b'\r\n', b'\n'), str(path)
        else:
            assert b'\r' not in data, str(path)
        assert not any(line.endswith((' ', '\t')) for line in text.splitlines()), str(path)
        assert not re.search(r'(?:sk-[A-Za-z0-9_-]{32,}|ghp_[A-Za-z0-9]{32,}|hf_[A-Za-z0-9]{32,})', text)
        if path.suffix == '.json':
            read(path)
        if path.suffix == '.py' or path.name == 'WORKER-INITIAL.py.txt':
            compile(text, str(path), 'exec')
        if path.suffix == '.md':
            for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)', text):
                if '://' not in target and not target.startswith('#'):
                    assert (path.parent / target.split('#')[0]).resolve().is_file(), target
    subprocess.run(['git', 'diff', '--check'], cwd=ROOT, check=True)
    return {'round': 'R6.56', 'passed': True, 'manifest_sha256': sha(OUT / 'PUBLICATION-IDENTITIES.json'),
            'payload_files': len(inventory()), 'previous_publications': previous, 'baseline': baseline,
            'installed_package_trees_verified': 47, 'frozen_preflight_payloads': 'PASS',
            'base_checkpoint_and_historical_untrained_adapter_external_hashes': 'PASS',
            'initial_assertion_and_prospective_correction_preserved': True, 'tracked_diff_empty': True,
            'git_diff_check_returncode': 0, 'publication_json_source_links_whitespace': 'PASS',
            'credential_pattern_scan': 'PASS', 'preservation_failures': [],
            'raw_worker_claim_native_crlf_preserved': True,
            'training_runs': 1, 'successful_optimizer_steps': 0, 'post_training_calls': 0}


if __name__ == '__main__':
    if sys.argv[1] == 'gather':
        gather()
    elif sys.argv[1] == 'seal':
        write('PUBLICATION-IDENTITIES.json', manifest())
        write('VERIFICATION.json', verify())
    elif sys.argv[1] == 'check':
        result = verify()
        assert result == read(OUT / 'VERIFICATION.json')
        print(json.dumps(result, sort_keys=True))
    else:
        raise ValueError('unknown mode')
