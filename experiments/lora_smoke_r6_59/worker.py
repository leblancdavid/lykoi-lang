"""Execute the pinned R6.56 worker with explicit, single-match R6.59 amendments."""
import run
import sys


def effective_source():
    source = (run.ROOT / 'experiments/lora_smoke_r6_56/worker.py').read_text(encoding='utf-8')
    def replace(old, new):
        nonlocal source
        assert source.count(old) == 1, old
        source = source.replace(old, new)
    replace('from common import ARTIFACTS, OUT, ROOT, STORE, canonical, file_manifest, frozen_check, identity, q52, read, rows, score, sha, write',
            'from run import ARTIFACTS, OUT, ROOT, STORE, canonical, file_manifest, frozen_check, identity, q52, read, rows, score, sha, write')
    replace("'round': 'R6.56', 'run_number'", "'round': 'R6.59', 'run_number'")
    replace("    limits = read(OUT / 'TRAINING-CONFIGURATION.json')['configuration']['limits']",
            "    limits = read(OUT / 'TRAINING-CONFIGURATION.json')['configuration']['limits']\n"
            "    write('MEMORY-LATEST.json', values)\n"
            "    if values['peak_reserved_bytes'] > limits['cuda_reserved_bytes'] or free < limits['minimum_device_free_bytes']:\n"
            "        write('MEMORY-LIMIT.json', values)\n"
            "    worker_rss = __import__('run').c.rss(os.getpid())\n"
            "    assert worker_rss is not None and worker_rss <= 17179869184, 'WORKER_RSS_LIMIT'")
    replace('    steps = []\n', '    steps = []\n    optimizer_calls = 0\n    scheduler_calls = 0\n')
    replace("'presentations': len(records_seen)})\n                os._exit(71)",
            "'presentations': len(records_seen), 'optimizer_calls': optimizer_calls, 'scheduler_calls': scheduler_calls,\n"
            "                    'values': read(OUT / 'MEMORY-LATEST.json'), 'training_wall_seconds': time.perf_counter() - training_started})\n"
            "                os._exit(71)")
    replace('                raw_loss = loss.item()\n                (loss / 4).backward()',
            '                (loss / 4).backward()\n                raw_loss = loss.item()')
    replace('                del output, loss, x, y\n                torch.cuda.synchronize()\n                values = memory()',
            "                write('MICROSTEPS.json', {'completed_presentations': len(records_seen), 'records': micro_losses})\n"
            "                del output, loss, x, y\n"
            "                torch.cuda.synchronize()\n"
            "                before_release = memory()\n"
            "                gradients = {}\n"
            "                for name, param in model.named_parameters():\n"
            "                    if param.requires_grad:\n"
            "                        assert param.grad is not None and torch.isfinite(param.grad).all().item(), 'INVALID_GRADIENT:' + name\n"
            "                        gradients[name] = tensor_record(param.grad)\n"
            "                    else:\n"
            "                        assert param.grad is None, 'UNEXPECTED_BASE_GRADIENT:' + name\n"
            "                torch.cuda.empty_cache()\n"
            "                values = memory()\n"
            "                assert gradients == {n: tensor_record(p.grad) for n, p in model.named_parameters() if p.requires_grad}\n"
            "                micro_losses[-1].update(before_cache_release=before_release, after_cache_release=values,\n"
            "                    accumulated_gradient_identity=identity(gradients), cache_preserved_gradients=True)\n")
    replace('            optimizer.step()\n',
            "            optimizer.step()\n            optimizer_calls += 1\n"
            "            write('UPDATE-ACCOUNTING.json', {'optimizer_calls': optimizer_calls, 'scheduler_calls': scheduler_calls, 'boundary': 'optimizer_returned'})\n")
    replace('            scheduler.step()\n',
            "            scheduler.step()\n            scheduler_calls += 1\n"
            "            assert optimizer_calls == scheduler_calls == step\n"
            "            assert 'step' not in scheduler.state_dict()\n"
            "            write('UPDATE-ACCOUNTING.json', {'optimizer_calls': optimizer_calls, 'scheduler_calls': scheduler_calls,\n"
            "                'scheduler_state': scheduler.state_dict(), 'optimizer_state_steps': [int(s['step'].item()) for s in optimizer.state.values()],\n"
            "                'optimizer_defaults': optimizer.defaults, 'lr': optimizer.param_groups[0]['lr']})\n")
    replace("'unrecorded_boundary_update_possible': True, 'restart_permitted': False}",
            "'optimizer_calls': optimizer_calls, 'scheduler_calls': scheduler_calls,\n"
            "              'training_wall_seconds': time.perf_counter() - training_started,\n"
            "              'memory': read(OUT / 'MEMORY-LATEST.json'), 'restart_permitted': False}")
    return source


if __name__ == '__main__':
    exec(compile(effective_source(), str(run.HERE / 'EFFECTIVE-WORKER.py'), 'exec'), globals())
