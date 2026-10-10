"""R6.52 tokenizer/NF4 mechanics only: deliberately no optimizer implementation."""
import importlib
import importlib.metadata
import json
import platform
import random
import sys
import time
from pathlib import Path
from setup import ROOT, OUT, STORE, sha, write

REPO = 'Qwen/Qwen2.5-Coder-1.5B-Instruct'
REVISION = '2e1fd397ee46e1388853d2af2c993145b0f1098a'
MODEL = STORE / 'checkpoint'
ADAPTER = STORE / 'untrained-adapter'
SEED = 651


def inventory():
    import torch
    packages = ['torch', 'transformers', 'peft', 'trl', 'accelerate', 'bitsandbytes',
                'datasets', 'tokenizers', 'safetensors']
    versions = {}
    for name in packages:
        importlib.import_module(name)
        versions[name] = importlib.metadata.version(name)
    assert torch.cuda.is_available()
    assert '4070' in torch.cuda.get_device_name(0)
    x = torch.ones(16, device='cuda', requires_grad=True)
    x.square().sum().backward()
    torch.cuda.synchronize()
    assert torch.isfinite(x.grad).all().item()
    write('ENVIRONMENT.json', {'os': platform.platform(), 'python': sys.version,
          'executable': sys.executable, 'packages': versions, 'cuda_available': True,
          'torch_cuda_runtime': torch.version.cuda, 'gpu': torch.cuda.get_device_name(0),
          'compute_capability': list(torch.cuda.get_device_capability(0)),
          'bf16_supported': torch.cuda.is_bf16_supported(), 'cuda_tensor_backward': 'PASS',
          'storage': str(STORE), 'global_python_3_14_modified': False})


def assets():
    from huggingface_hub import HfApi, hf_hub_download
    info = HfApi().model_info(REPO, revision=REVISION, files_metadata=True, token=False)
    assert info.sha == REVISION
    required = {'config.json', 'generation_config.json', 'tokenizer.json', 'tokenizer_config.json',
                'vocab.json', 'merges.txt', 'LICENSE', 'README.md', 'special_tokens_map.json',
                'model.safetensors.index.json'}
    selected = [s for s in info.siblings if s.rfilename in required or
                (s.rfilename.startswith('model') and s.rfilename.endswith('.safetensors'))]
    assert any(s.rfilename.endswith('.safetensors') for s in selected)
    files = {}
    for s in selected:
        p = Path(hf_hub_download(REPO, s.rfilename, revision=REVISION, local_dir=MODEL, token=False))
        digest = sha(p)
        lfs_hash = s.lfs.sha256 if s.lfs else None
        if lfs_hash:
            assert digest == lfs_hash
        files[s.rfilename] = {'sha256': digest, 'bytes': p.stat().st_size,
                              'remote_blob_id': s.blob_id, 'remote_lfs_sha256': lfs_hash}
    assert {'config.json', 'tokenizer.json', 'tokenizer_config.json'}.issubset(files)
    write('CHECKPOINT.json', {'repo': REPO, 'revision': REVISION, 'resolved_revision': info.sha,
          'files': files, 'asset_bytes': sum(f['bytes'] for f in files.values()),
          'license': info.card_data.get('license'), 'configuration': json.loads((MODEL / 'config.json').read_text()),
          'license_source': 'LICENSE' if 'LICENSE' in files else 'README.md model card',
          'local_directory': str(MODEL), 'trust_remote_code': False})


def encoded(record, tokenizer):
    prompt = tokenizer.apply_chat_template(record['prompt'], tokenize=False, add_generation_prompt=True)
    full = tokenizer.apply_chat_template(record['prompt'] + record['completion'], tokenize=False,
                                         add_generation_prompt=False)
    assert full.startswith(prompt)
    expected = record['completion'][0]['content'] + '<|im_end|>\n'
    assert full[len(prompt):] == expected
    pids = tokenizer(prompt, add_special_tokens=False)['input_ids']
    ids = tokenizer(full, add_special_tokens=False)['input_ids']
    assert ids[:len(pids)] == pids, 'template/token boundary mismatch'
    eos = tokenizer.convert_tokens_to_ids('<|im_end|>')
    end = len(ids) - 1 - ids[::-1].index(eos)
    assert end >= len(pids)
    assert tokenizer.decode(ids[len(pids):end], skip_special_tokens=False) == record['completion'][0]['content']
    labels = [-100] * len(ids)
    labels[len(pids):end + 1] = ids[len(pids):end + 1]
    assert all(v == -100 for v in labels[:len(pids)])
    assert labels[len(pids):end + 1] == ids[len(pids):end + 1]
    assert all(v == -100 for v in labels[end + 1:])
    return ids, labels, {'episode_id': record['episode_id'], 'prompt_tokens': len(pids),
            'target_content_tokens': end - len(pids), 'supervised_tokens_including_eos': end + 1 - len(pids),
            'sequence_tokens': len(ids), 'post_eos_masked_tokens': len(ids) - end - 1,
            'exceeds_2048': len(ids) > 2048, 'exceeds_4096': len(ids) > 4096,
            'prompt_loss_excluded': True, 'target_fully_trainable': True, 'truncated': False}


def tokenize():
    from transformers import AutoTokenizer
    t = AutoTokenizer.from_pretrained(MODEL, local_files_only=True, trust_remote_code=False)
    rows = [json.loads(s) for s in (ROOT / 'benchmark/results/phase6/r6_51/DIRECT.jsonl').read_text().splitlines()]
    measurements = []
    for row in rows:
        ids, labels, data = encoded(row, t)
        # Padding and overflow are independently checked without altering any target.
        padded_labels = labels + [-100] * 7
        assert all(v == -100 for v in padded_labels[len(ids):])
        assert len(ids) > len(ids) - 1  # a candidate length cap of N-1 must reject this row
        measurements.append(data)
    write('TOKENIZATION.json', {'repo': REPO, 'revision': REVISION,
          'dataset_sha256': sha(ROOT / 'benchmark/results/phase6/r6_51/DIRECT.jsonl'),
          'chat_template_sha256': __import__('hashlib').sha256(t.chat_template.encode()).hexdigest(),
          'eos_token': t.eos_token, 'eos_token_id': t.eos_token_id,
          'pad_token': t.pad_token, 'pad_token_id': t.pad_token_id, 'records': measurements,
          'truncation': False, 'mask_rule': 'exact prompt prefix and post-EOS newline/padding -100; target plus im_end supervised',
          'chat_prefix_and_target_roundtrip_checks': 10, 'padding_controls': 10,
          'requires_4096': any(r['exceeds_2048'] for r in measurements)})


def tensor_manifest(model):
    import hashlib
    result = {}
    for name, param in model.named_parameters():
        if param.requires_grad:
            data = param.detach().cpu().contiguous()
            result[name] = {'shape': list(data.shape), 'dtype': str(data.dtype),
                            'sha256': hashlib.sha256(data.view(__import__('torch').uint8).numpy().tobytes()).hexdigest()}
    assert result and all('lora_' in n and ('.q_proj.' in n or '.v_proj.' in n) for n in result)
    return result


def load_base():
    import torch
    from transformers import AutoModelForCausalLM, BitsAndBytesConfig
    config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type='nf4',
                               bnb_4bit_use_double_quant=True, bnb_4bit_compute_dtype=torch.bfloat16)
    model = AutoModelForCausalLM.from_pretrained(MODEL, local_files_only=True,
            trust_remote_code=False, quantization_config=config, device_map={'': 0},
            torch_dtype=torch.bfloat16, attn_implementation='sdpa')
    assert model.is_loaded_in_4bit
    model.config.use_cache = False
    return model, config.to_dict()


def seed():
    import torch
    random.seed(SEED)
    torch.manual_seed(SEED)
    torch.cuda.manual_seed_all(SEED)


def reference(model):
    import torch
    model.eval()
    with torch.no_grad():
        logits = model(input_ids=torch.tensor([[1, 2, 3, 4]], device='cuda')).logits.float().cpu()
    assert torch.isfinite(logits).all().item()
    return logits


def backward():
    import torch
    import bitsandbytes as bnb
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
    from transformers import AutoTokenizer
    seed()
    torch.cuda.reset_peak_memory_stats()
    total_start = time.perf_counter()
    base, quant = load_base()
    nf4_layers = [n for n, m in base.named_modules() if isinstance(m, bnb.nn.Linear4bit)]
    assert nf4_layers
    base = prepare_model_for_kbit_training(base, use_gradient_checkpointing=True,
            gradient_checkpointing_kwargs={'use_reentrant': False})
    lora = LoraConfig(r=8, lora_alpha=16, lora_dropout=0.05, target_modules=['q_proj', 'v_proj'],
                      bias='none', task_type='CAUSAL_LM', base_model_name_or_path=REPO, revision=REVISION)
    model = get_peft_model(base, lora)
    # PEFT derives this field from the local load path; bind the public base identity.
    model.peft_config['default'].base_model_name_or_path = REPO
    model.peft_config['default'].revision = REVISION
    before = tensor_manifest(model)
    assert len(before) == 112
    ADAPTER.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(ADAPTER, safe_serialization=True)
    tokenizer = AutoTokenizer.from_pretrained(MODEL, local_files_only=True)
    rows = [json.loads(s) for s in (ROOT / 'benchmark/results/phase6/r6_51/DIRECT.jsonl').read_text().splitlines()]
    six = [r for r in rows if r['episode_id'].endswith(tuple('E%02d' % i for i in range(1, 7)))]
    assert len(six) == 6
    samples = [(r, *encoded(r, tokenizer)) for r in six]
    row, ids, labels, measure = max(samples, key=lambda s: len(s[1]))
    assert len(ids) <= 2048
    tests = []
    for name, input_ids, targets in [('longest_smoke_record', ids, labels),
            ('synthetic_full_2048', [100] * 2047 + [tokenizer.eos_token_id], [-100] * 1024 + [100] * 1023 + [tokenizer.eos_token_id])]:
        model.train()
        model.zero_grad(set_to_none=True)
        torch.cuda.reset_peak_memory_stats()
        torch.cuda.synchronize()
        start = time.perf_counter()
        x = torch.tensor([input_ids], device='cuda')
        y = torch.tensor([targets], device='cuda')
        loss = model(input_ids=x, attention_mask=torch.ones_like(x), labels=y).loss
        assert torch.isfinite(loss).item()
        loss.backward()
        torch.cuda.synchronize()
        gradient_records = []
        for n, p in model.named_parameters():
            if p.requires_grad:
                assert p.grad is not None and torch.isfinite(p.grad).all().item(), n
                gradient_records.append({'name': n, 'nonzero': bool(torch.count_nonzero(p.grad).item())})
            else:
                assert p.grad is None, n
        assert any(g['nonzero'] for g in gradient_records)
        assert tensor_manifest(model) == before
        free, total = torch.cuda.mem_get_info()
        tests.append({'name': name, 'episode_id': row['episode_id'] if name == 'longest_smoke_record' else None,
              'sequence_tokens': len(input_ids), 'supervised_tokens': sum(v != -100 for v in targets),
              'loss': loss.item(), 'finite_gradients': True, 'gradient_tensors': gradient_records,
              'seconds': time.perf_counter() - start, 'peak_allocated_bytes': torch.cuda.max_memory_allocated(),
              'peak_reserved_bytes': torch.cuda.max_memory_reserved(), 'device_free_bytes_after': free,
              'device_total_bytes': total, 'adapter_parameters_unchanged': True, 'base_gradients_absent': True})
        del loss, x, y
    model.zero_grad(set_to_none=True)
    torch.save(reference(model), STORE / 'reference-logits.pt')
    saved = {p.name: {'sha256': sha(p), 'bytes': p.stat().st_size} for p in ADAPTER.iterdir() if p.is_file()}
    config = json.loads((ADAPTER / 'adapter_config.json').read_text())
    assert config['r'] == 8 and set(config['target_modules']) == {'q_proj', 'v_proj'}
    write('BACKWARD.json', {'seed': SEED, 'quantization': quant, 'nf4_linear_layers': len(nf4_layers),
          'adapter_config': config, 'trainable_parameters': sum(p.numel() for p in model.parameters() if p.requires_grad),
          'adapter_tensor_manifest': before, 'saved_adapter_files': saved, 'tests': tests,
          'optimizer_instances': 0, 'optimizer_steps': 0, 'parameter_updates': 0,
          'total_seconds_including_loading': time.perf_counter() - total_start, 'status': 'PASS'})


def reload():
    import torch
    from peft import PeftModel, prepare_model_for_kbit_training
    from safetensors import safe_open
    seed()
    base, quant = load_base()
    base = prepare_model_for_kbit_training(base, use_gradient_checkpointing=True,
                gradient_checkpointing_kwargs={'use_reentrant': False})
    model = PeftModel.from_pretrained(base, ADAPTER, is_trainable=True)
    old = json.loads((OUT / 'BACKWARD.json').read_text())
    assert tensor_manifest(model) == old['adapter_tensor_manifest']
    cfg = json.loads((ADAPTER / 'adapter_config.json').read_text())
    assert cfg == old['adapter_config']
    assert cfg['base_model_name_or_path'] == REPO and cfg['revision'] == REVISION
    for name, record in old['saved_adapter_files'].items():
        assert sha(ADAPTER / name) == record['sha256']
    with safe_open(ADAPTER / 'adapter_model.safetensors', framework='pt') as f:
        shapes = {k: list(f.get_tensor(k).shape) for k in f.keys()}
    current = reference(model)
    previous = torch.load(STORE / 'reference-logits.pt', weights_only=True)
    delta = (current - previous).abs().max().item()
    assert torch.equal(current, previous)
    write('ADAPTER-RELOAD.json', {'status': 'PASS', 'fresh_process': True, 'seed': SEED,
          'repo': REPO, 'revision': REVISION, 'configuration_identical': True, 'parameters_exactly_preserved': True,
          'tensor_shapes': shapes, 'tensor_count': len(shapes), 'logits_exactly_equal': True,
          'maximum_logit_difference': delta, 'inference_initialization': 'finite short forward logits',
          'optimizer_steps': 0, 'untrained': True, 'peak_allocated_bytes': torch.cuda.max_memory_allocated(),
          'peak_reserved_bytes': torch.cuda.max_memory_reserved()})


if __name__ == '__main__':
    {'inventory': inventory, 'assets': assets, 'tokenize': tokenize, 'backward': backward, 'reload': reload}[sys.argv[1]]()
