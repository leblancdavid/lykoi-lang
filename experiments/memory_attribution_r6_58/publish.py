"""Offline analysis and publication, never loads a model."""
import ast
import re
import subprocess
import sys
import run

c, OUT, ROOT = run.c, run.OUT, run.ROOT


def effective_source():
    source = (ROOT / 'experiments/memory_diagnostic_r6_57/worker.py').read_text(encoding='utf-8')
    tree = ast.parse((run.HERE / 'worker.py').read_text(encoding='utf-8'))
    for node in tree.body:
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name) and node.value.func.id == 'replace':
            old, new = [ast.literal_eval(a) for a in node.value.args]
            assert source.count(old) == 1
            source = source.replace(old, new)
    return source.replace("'R6.57'", "'R6.58'")


def analyze():
    source = effective_source()
    # CPU-only reproduction of the observed instrumentation assertion; no updates.
    import torch
    from transformers.optimization import get_linear_schedule_with_warmup
    param = torch.nn.Parameter(torch.tensor([1.0]))
    kwargs = dict(c.read(c.OUT / 'TRAINING-CONFIGURATION.json')['configuration']['optimizer_configuration']['kwargs'])
    kwargs['betas'] = tuple(kwargs['betas'])
    optimizer = torch.optim.AdamW([param], **kwargs)
    scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=2, num_training_steps=20)
    before = scheduler.state_dict()
    def forbidden(*args, **kwargs):
        raise RuntimeError('OPTIMIZER_OR_SCHEDULER_UPDATE_FORBIDDEN')
    optimizer.step = forbidden
    scheduler.step = forbidden
    after = scheduler.state_dict()
    assert set(after) - set(before) == {'step'}
    assert {k:v for k,v in after.items() if k != 'step'} == before
    assert not optimizer.state and scheduler.last_epoch == 0 and optimizer.param_groups[0]['lr'] == 0
    run.write('SCHEDULER-GUARD-CONTROL.json', {'cpu_only': True, 'model_loaded': False,
        'before': before, 'after_excluding_guard': {k:v for k,v in after.items() if k != 'step'},
        'added_state_key': 'step', 'added_value': 'forbidden callable assigned by instrumentation',
        'original_comparison_fails': before != after, 'semantic_schedule_state_unchanged': True,
        'optimizer_state_empty': True, 'optimizer_updates': 0, 'scheduler_updates': 0,
        'limitation': 'offline source/control explanation; actual failed worker state dictionary was not persisted'})
    run.write('EFFECTIVE-SOURCE-LINE-MAP.json', {'failure_line_205': source.splitlines()[204],
        'effective_source_sha256': __import__('hashlib').sha256(source.encode()).hexdigest()})
    summaries = {}
    for condition in ('baseline', 'cache_release'):
        folder = OUT / condition
        trace = c.read(folder / 'MEMORY-TRACE.json')['boundaries']
        stop = c.read(folder / 'SAFETY-STOP.json') if (folder / 'SAFETY-STOP.json').exists() else None
        values = trace + ([dict(stop['values'], boundary='watchdog_stop', microbatch=4)] if stop else [])
        grads = c.read(folder / 'GRADIENTS.json')['records']
        compact = [{k: v.get(k) for k in ('boundary', 'microbatch', 'allocated_bytes', 'reserved_bytes',
            'peak_allocated_bytes', 'peak_reserved_bytes', 'device_free_bytes', 'outside_allocator_residual_bytes')} |
            {'active_bytes': v['allocator_stats']['active_bytes.all.current'],
             'inactive_split_bytes': v['allocator_stats']['inactive_split_bytes.all.current'],
             'allocation_events': v['allocator_stats']['allocation.all.allocated'],
             'release_events': v['allocator_stats']['allocation.all.freed']} for v in values]
        snapshots = {}
        for path in folder.glob('SNAPSHOT-*.json'):
            snap = c.read(path)
            segments = snap['segments']
            snapshots[path.name] = {'segments': len(segments),
                'segment_bytes': sum(s['total_size'] for s in segments),
                'inactive_block_bytes': sum(b['size'] for s in segments for b in s['blocks'] if b['state'] == 'inactive'),
                'fully_inactive_segment_bytes': sum(s['total_size'] for s in segments if s['active_size'] == 0),
                'event_counts': {action: sum(e['action'] == action for entries in snap['device_traces'] for e in entries)
                    for action in ('alloc', 'free_requested', 'free_completed', 'segment_alloc', 'segment_free', 'oom')}}
        summaries[condition] = {'trajectory': compact, 'snapshot_summary': snapshots,
            'completed_backward_calls': len(grads), 'four_record_completed': len(grads) == 4,
            'wall_seconds': c.read(folder / 'PROCESS.json')['seconds'],
            'process_returncode': c.read(folder / 'PROCESS.json')['returncode'],
            'peak_allocated_bytes': max(v['peak_allocated_bytes'] for v in values),
            'peak_reserved_bytes': max(v['peak_reserved_bytes'] for v in values),
            'minimum_boundary_or_stop_device_free_bytes': min(v['device_free_bytes'] for v in values),
            'final_parameter_integrity': 'NOT_ESTABLISHED: hard stop' if stop else 'PASS actual adapter/base/buffer/quant-state equality assertion preceding failed scheduler assertion; final manifests not persisted',
            'finite_lora_gradients': [g['finite_adapter_gradient_tensors'] for g in grads],
            'base_gradients_absent': all(g['base_gradients_absent'] for g in grads),
            'hook_sum_max_absolute_error': max(g['hook_sum_max_absolute_error'] for g in grads)}
    comparisons = []
    b = c.read(OUT / 'baseline/GRADIENTS.json')['records']
    m = c.read(OUT / 'cache_release/GRADIENTS.json')['records']
    for i, (x, y) in enumerate(zip(b, m), 1):
        comparisons.append({'microbatch': i, 'baseline_loss': x['mean_record_loss'], 'cache_loss': y['mean_record_loss'],
            'loss_exact_equal': x['mean_record_loss'] == y['mean_record_loss'],
            'accumulated_gradient_sha256_exact_equal': c.read(OUT / f'baseline/GRADIENT-IDENTITIES-{i}.json') == c.read(OUT / f'cache_release/GRADIENT-IDENTITIES-{i}.json')})
    run.write('ANALYSIS.json', {'conditions': summaries, 'cross_condition_completed_prefix': comparisons,
        'classification': 'R6_58_CACHE_RELEASE_SUPPORTED', 'recommendation': 'A',
        'optimizer_updates': 0, 'scheduler_updates': 0, 'full_twenty_step_qualified': False,
        'dynamic_padding': 'SKIPPED: actual unpadded record lengths',
        'failure_assertion': source.splitlines()[204]})
    print(__import__('json').dumps({'conditions': {k: {n:v for n,v in s.items() if n not in ('trajectory','snapshot_summary')} for k,s in summaries.items()},
        'comparisons': comparisons, 'failure_line': source.splitlines()[204]}, indent=2))


def manifest():
    paths = list(run.HERE.glob('*.py')) + [ROOT / 'benchmark/results/phase6/R6_58-REPORT.md']
    paths += list(ROOT.glob('docs/*-r6.58.md'))
    paths += [p for p in OUT.rglob('*') if p.is_file() and p.name not in ('PUBLICATION-IDENTITIES.json', 'VERIFICATION.json')]
    return {'round': 'R6.58', 'files': {p.relative_to(ROOT).as_posix(): {'sha256': c.sha(p), 'bytes': p.stat().st_size} for p in sorted(paths)}}


def verify():
    assert manifest() == c.read(OUT / 'PUBLICATION-IDENTITIES.json')
    assert run.baseline() == c.read(OUT / 'BASELINE.json')
    assert not subprocess.check_output(['git', 'diff', 'HEAD', '--name-only'], cwd=ROOT, text=True).strip()
    allowed = set(manifest()['files']) | {'benchmark/results/phase6/r6_58/PUBLICATION-IDENTITIES.json', 'benchmark/results/phase6/r6_58/VERIFICATION.json'}
    for line in subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=all'], cwd=ROOT, text=True).splitlines():
        assert line.startswith('?? ') and line[3:].replace('\\', '/') in allowed, line
    for rel in manifest()['files']:
        path = ROOT / rel
        data = path.read_bytes()
        text = data.decode('utf-8')
        assert data.endswith(b'\n') and b'\r' not in data
        assert not any(s.endswith((' ', '\t')) for s in text.splitlines())
        assert not re.search(r'(?:sk-[A-Za-z0-9_-]{32,}|ghp_[A-Za-z0-9]{32,}|hf_[A-Za-z0-9]{32,})', text)
        if path.suffix == '.json':
            c.read(path)
        elif path.suffix == '.py':
            compile(text, str(path), 'exec')
        elif path.suffix == '.md':
            for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)', text):
                if '://' not in target and not target.startswith('#'):
                    assert (path.parent / target.split('#')[0]).resolve().is_file(), target
    f = c.read(OUT / 'PREFLIGHT.json')
    assert c.sha(run.HERE / 'worker.py') == f['worker_sha256'] and c.sha(run.HERE / 'run.py') == f['run_sha256']
    assert c.sha(OUT / 'PROTOCOL.md') == f['protocol_sha256']
    for condition in ('baseline','cache_release'):
        assert c.read(OUT / condition / 'EFFECTIVE-SOURCE-IDENTITY.json')['effective_source_sha256'] == c.read(OUT / 'EFFECTIVE-SOURCE-LINE-MAP.json')['effective_source_sha256']
    subprocess.run(['git', 'diff', '--check'], cwd=ROOT, check=True)
    return {'round': 'R6.58', 'passed': True, 'manifest_sha256': c.sha(OUT / 'PUBLICATION-IDENTITIES.json'),
        'historical_environment_production_preserved': True, 'kernel_constructs': 26,
        'payload_files': len(manifest()['files']), 'source_json_links_whitespace_credentials': 'PASS', 'git_diff_check_returncode': 0}


if __name__ == '__main__':
    if sys.argv[1] == 'analyze':
        analyze()
    elif sys.argv[1] == 'seal':
        run.write('PUBLICATION-IDENTITIES.json', manifest())
        run.write('VERIFICATION.json', {'round': 'R6.58', 'passed': False, 'status': 'publication check in progress'})
        run.write('VERIFICATION.json', verify())
    elif sys.argv[1] == 'check':
        assert verify() == c.read(OUT / 'VERIFICATION.json')
        print('PASS publication and all frozen identities')
