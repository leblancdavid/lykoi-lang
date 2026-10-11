"""Bounded read-only R6.60 evaluation; no training or historical rescoring."""
import ast
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = ROOT / 'benchmark/results/phase6/r6_60'
sys.path.insert(0, str(ROOT / 'experiments/lora_smoke_r6_59'))
import run as prior
c = prior.c


def write(name, value):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n', encoding='utf-8', newline='\n')


def baseline():
    assert prior.baseline() == c.read(prior.OUT / 'BASELINE.json')
    prior.frozen_check()
    manifest = c.read(prior.OUT / 'PUBLICATION-IDENTITIES.json')
    for name, entry in manifest['files'].items():
        assert c.sha(ROOT / name) == entry['sha256'], name
    assert c.file_manifest(prior.ARTIFACTS) == c.read(prior.OUT / 'EXTERNAL-ARTIFACTS.json')['files']
    env = c.read(ROOT / 'benchmark/results/phase6/r6_52/ENVIRONMENT-IDENTITIES.json')
    home = c.STORE / 'python/cpython-3.12.11-windows-x86_64-none'
    paths = {'python_executable_sha256': home / 'python.exe', 'python_dll_sha256': home / 'python312.dll',
             'venv_executable_sha256': c.PYTHON, 'uv_executable_sha256': c.STORE / 'uv/uv.exe',
             'requirements_lock_sha256': ROOT / 'benchmark/results/phase6/r6_52/requirements-lock.txt'}
    assert all(c.sha(p) == env[k] for k, p in paths.items())
    return {'status': 'PASS', 'r6_59_publication_sha256': c.sha(prior.OUT / 'PUBLICATION-IDENTITIES.json'),
            'inherited_baseline': prior.baseline(), 'executable_identities': {k: c.sha(p) for k, p in paths.items()},
            'checkpoint': c.read(ROOT / 'benchmark/results/phase6/r6_52/CHECKPOINT.json'),
            'adapter_files': c.file_manifest(prior.ARTIFACTS / 'step20/adapter'),
            'source_manifest_sha256': c.sha(c.OUT / 'SOURCE-DATASET-IDENTITIES.json'),
            'kernel_constructs': 26, 'historical_scores_preserved': True}


def freeze():
    assert not (OUT / 'FREEZE.json').exists()
    write('BASELINE.json', baseline())
    write('FREEZE.json', {'source_sha256': c.sha(HERE / 'diagnose.py'), 'protocol_sha256': c.sha(OUT / 'PROTOCOL.md'),
        'evaluation': 'one base and one adapter pass over exact E01-E06; eval/no_grad; same NF4 preparation',
        'weighting': 'equal-record mean and pooled-token mean; target plus im_end only',
        'token_analysis': 'all supervised tokens; exact full-string fast-tokenizer offsets; overlapping lexical category tags',
        'optional_probes': 'not planned: preserved outputs and exact-template audit suffice',
        'optimizer_updates': 0, 'timeout_seconds_per_process': 180, 'max_sequence': 2048})


def check():
    f = c.read(OUT / 'FREEZE.json')
    assert c.sha(HERE / 'diagnose.py') == f['source_sha256']
    assert c.sha(OUT / 'PROTOCOL.md') == f['protocol_sha256']
    assert baseline() == c.read(OUT / 'BASELINE.json')


def tags(text, start, end):
    result = set()
    for m in re.finditer(r'"(?:[^"\\]|\\.)*"|true|false|null|-?\d+|[{}\[\],:]', text):
        if m.end() <= start or m.start() >= end:
            continue
        value = m.group()
        if value in '{}[]':
            result.add('package_delimiters')
            if value in '}]':
                result.add('closing_delimiters')
        elif value in ',:':
            result.add('punctuation')
        elif value.startswith('"'):
            is_key = text[m.end():].lstrip().startswith(':')
            if is_key:
                result.add('structural_keys')
                if value in ('"add"', '"le"', '"eq"', '"ref"', '"const"'):
                    result.add('semantic_operation_names')
            else:
                prefix = text[:m.start()]
                if re.search(r'"(?:op|codec)"\s*:\s*$', prefix):
                    result.add('semantic_operation_names')
                elif re.search(r'"ref"\s*:\s*$', prefix):
                    result.add('dependency_references')
                elif value in ('"Int64"', '"Bool"', '"Unit"'):
                    result.add('typed_values')
                else:
                    result.add('other_values')
        else:
            result.add('typed_values')
    # Output definitions are the exact result/result_type field spans, not emitted bytes.
    for m in re.finditer(r'"result"\s*:\s*\{[^{}]*\}|"result_type"\s*:\s*"[^"]*"', text):
        if m.end() > start and m.start() < end:
            result.add('output_definitions')
    # Dependencies include exact deps arrays and explicit ref values.
    for m in re.finditer(r'"deps"\s*:\s*\[[^\[\]]*\]', text):
        if m.end() > start and m.start() < end:
            result.add('dependency_references')
    return sorted(result)


def evaluate(track):
    check()
    with (OUT / f'{track.upper()}-CLAIM.json').open('x', encoding='utf-8') as stream:
        stream.write(json.dumps({'track': track, 'pid': os.getpid()}) + '\n')
    import torch
    from transformers import AutoTokenizer
    from peft import PeftModel, prepare_model_for_kbit_training
    spec = importlib.util.spec_from_file_location('r60_tensor_helpers', ROOT / 'experiments/lora_smoke_r6_56/worker.py')
    helpers = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helpers)
    c.q52.seed()
    started = time.perf_counter()
    torch.cuda.reset_peak_memory_stats()
    model, quant = c.q52.load_base()
    model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=True,
                                           gradient_checkpointing_kwargs={'use_reentrant': False})
    if track == 'adapter':
        model = PeftModel.from_pretrained(model, prior.ARTIFACTS / 'step20/adapter', is_trainable=False, local_files_only=True)
        assert helpers.adapter_manifest(model) == c.read(prior.OUT / 'TRAINING-RESULT.json')['trained_adapter_tensors']
    model.eval()
    model.requires_grad_(False)
    assert not any(m.training for m in model.modules())
    before = helpers.base_manifest(model)
    adapter_before = helpers.adapter_manifest(model)
    tokenizer = AutoTokenizer.from_pretrained(c.STORE / 'checkpoint', local_files_only=True, trust_remote_code=False)
    expected = {r['episode_id']: r for r in c.read(c.OUT / 'SOURCE-DATASET-IDENTITIES.json')['records']}
    records = []
    for row in c.rows():
        ids, labels, measure = c.q52.encoded(row, tokenizer)
        e = expected[row['episode_id']]
        assert c.identity(row) == e['canonical_record_sha256']
        assert c.identity(labels) == e['labels_sha256']
        assert measure == e['tokenization']
        assert len(ids) <= 2048
        full = tokenizer.apply_chat_template(row['prompt'] + row['completion'], tokenize=False, add_generation_prompt=False)
        prompt = tokenizer.apply_chat_template(row['prompt'], tokenize=False, add_generation_prompt=True)
        offsets = tokenizer(full, add_special_tokens=False, return_offsets_mapping=True)
        assert offsets['input_ids'] == ids
        x = torch.tensor([ids], device='cuda')
        torch.cuda.synchronize()
        t0 = time.perf_counter()
        with torch.no_grad():
            output = model(input_ids=x, attention_mask=torch.ones_like(x), use_cache=False)
            positions = [i for i, v in enumerate(labels) if v != -100]
            logits = output.logits[0, [i - 1 for i in positions], :].float()
            assert torch.isfinite(logits).all().item()
            targets = torch.tensor([ids[i] for i in positions], device='cuda')
            nll = torch.nn.functional.cross_entropy(logits, targets, reduction='none')
            assert torch.isfinite(nll).all().item()
            losses = nll.double().cpu().tolist()
        torch.cuda.synchronize()
        elapsed = time.perf_counter() - t0
        tokens = []
        for i, loss in zip(positions, losses):
            a, b = offsets['offset_mapping'][i]
            category = ['end_of_turn'] if ids[i] == tokenizer.eos_token_id else tags(row['completion'][0]['content'], a-len(prompt), b-len(prompt))
            tokens.append({'sequence_index': i, 'logit_index': i-1, 'token_id': ids[i],
                'token': tokenizer.convert_ids_to_tokens(ids[i]), 'full_character_span': [a, b],
                'target_character_span': [a-len(prompt), b-len(prompt)], 'text': full[a:b], 'categories': category,
                'nll_nats': loss, 'probability': math.exp(-loss)})
        records.append({'episode_id': row['episode_id'], 'measurement': measure,
            'ids_sha256': c.identity(ids), 'labels_sha256': c.identity(labels), 'prompt_sha256': hashlib.sha256(prompt.encode()).hexdigest(),
            'supervised_tokens': len(losses), 'sum_nll_nats': sum(losses), 'mean_nll_nats': sum(losses)/len(losses),
            'evaluation_seconds': elapsed, 'tokens': tokens})
        del output, logits, targets, nll, x
        torch.cuda.empty_cache()
        free, total = torch.cuda.mem_get_info()
        assert torch.cuda.max_memory_reserved() <= 8 * 1024**3 and free >= 1.5 * 1024**3
        assert c.rss(os.getpid()) <= 16 * 1024**3
    assert helpers.base_manifest(model) == before
    assert helpers.adapter_manifest(model) == adapter_before
    assert all(p.grad is None for p in model.parameters())
    write(f'{track.upper()}-LOSS.json', {'track': track, 'records': records, 'quantization': quant,
        'equal_record_mean_nll_nats': sum(r['mean_nll_nats'] for r in records)/6,
        'pooled_token_mean_nll_nats': sum(r['sum_nll_nats'] for r in records)/sum(r['supervised_tokens'] for r in records),
        'supervised_tokens': sum(r['supervised_tokens'] for r in records), 'whole_worker_seconds': time.perf_counter()-started,
        'evaluation_seconds': sum(r['evaluation_seconds'] for r in records),
        'peak_allocated_bytes': torch.cuda.max_memory_allocated(), 'peak_reserved_bytes': torch.cuda.max_memory_reserved(),
        'final_device_free_bytes': torch.cuda.mem_get_info()[0], 'model_parameters_unchanged': True,
        'base_tensor_identity': c.identity(before), 'adapter_tensor_identity': c.identity(adapter_before),
        'numerical_failures': [], 'gradient_computation': False, 'optimizer_updates': 0, 'generated_tokens': 0})


def dispatch():
    check()
    for track in ('base', 'adapter'):
        start = time.perf_counter()
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', HF_HUB_OFFLINE='1', HF_HUB_DISABLE_TELEMETRY='1')
        p = subprocess.run([str(c.PYTHON), '-B', str(HERE / 'diagnose.py'), 'evaluate', track],
                           cwd=ROOT, env=env, capture_output=True, text=True, timeout=180)
        write(f'{track.upper()}-PROCESS.json', {'returncode': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr,
              'seconds': time.perf_counter()-start, 'timeout_seconds': 180})
        assert p.returncode == 0, p.stderr
    print('PASS two read-only likelihood passes')


def analyze():
    from transformers import AutoTokenizer
    check()
    tokenizer = AutoTokenizer.from_pretrained(c.STORE / 'checkpoint', local_files_only=True)
    a, b = [c.read(OUT / f'{track}-LOSS.json') for track in ('BASE', 'ADAPTER')]
    comparisons, groups = [], {}
    for ra, rb in zip(a['records'], b['records']):
        assert ra['ids_sha256'] == rb['ids_sha256'] and ra['labels_sha256'] == rb['labels_sha256']
        pairs = []
        for ta, tb in zip(ra['tokens'], rb['tokens']):
            assert {k: v for k, v in ta.items() if k not in ('nll_nats', 'probability')} == {k: v for k, v in tb.items() if k not in ('nll_nats', 'probability')}
            pair = dict(ta, base_nll_nats=ta['nll_nats'], adapter_nll_nats=tb['nll_nats'],
                nll_delta=tb['nll_nats']-ta['nll_nats'], probability_delta=tb['probability']-ta['probability'], adapter_probability=tb['probability'])
            pairs.append(pair)
            for category in ta['categories']:
                groups.setdefault(category, []).append(pair)
        comparisons.append({'episode_id': ra['episode_id'], 'tokens': ra['supervised_tokens'],
            'base_mean_nll': ra['mean_nll_nats'], 'adapter_mean_nll': rb['mean_nll_nats'],
            'delta': rb['mean_nll_nats']-ra['mean_nll_nats'], 'token_pairs': pairs})
    write('TOKEN-ANALYSIS.json', {'categories_overlap': True, 'boundary_policy': 'tag entire tokenizer token on any lexical-span overlap; do not split token probabilities',
        'categories': {k: {'tokens': len(v), 'base_mean_nll': sum(t['base_nll_nats'] for t in v)/len(v),
            'adapter_mean_nll': sum(t['adapter_nll_nats'] for t in v)/len(v),
            'mean_nll_delta': sum(t['nll_delta'] for t in v)/len(v),
            'mean_probability_delta': sum(t['probability_delta'] for t in v)/len(v),
            'improved_tokens': sum(t['nll_delta'] < 0 for t in v)} for k, v in groups.items()}, 'records': comparisons})
    audits, divergence = [], []
    for row in c.rows():
        eid = row['episode_id'].split('/')[-1]
        prompt = tokenizer.apply_chat_template(row['prompt'], tokenize=False, add_generation_prompt=True)
        pa = hashlib.sha256(prompt.encode()).hexdigest()
        target = row['completion'][0]['content']
        outputs = []
        for track, folder in [('base', c.OUT), ('adapter', prior.OUT)]:
            d = c.read(folder / f'DIAGNOSTIC-{track.upper()}-{eid}.json')
            assert pa == d['prompt_sha256']
            assert tokenizer.decode(d['output_token_ids'], skip_special_tokens=True) == d['output']
            raw = d['output']
            first = len(raw)-len(raw.lstrip())
            outputs.append(raw)
            divergence.append({'episode_id': eid, 'track': track, 'output': raw, 'output_token_ids': d['output_token_ids'],
                'output_tokens_including_eos': d['output_tokens'], 'historical_inference_seconds': d['inference_seconds'],
                'first_violation_character_index': first, 'first_violation_character': raw[first],
                'first_token_id': d['output_token_ids'][0], 'first_token_text': tokenizer.decode(d['output_token_ids'][:1]),
                'fence_before_package_content': raw.startswith('```'),
                'expected_package_keys_without_lexical_occurrence': [k for k in json.loads(target) if not re.search(r'"'+re.escape(k)+r'"\s*:', raw)],
                'classification': 'RAW_FORMAT_FENCE_BEFORE_CONTENT; incomplete package lexical coverage',
                'historical_native_diagnostic': d['scores']['native_diagnostic'], 'repair_or_rescore': False})
        audits.append({'episode_id': eid, 'messages': row['prompt'], 'developer_messages': [], 'rendered_training_prompt': prompt,
            'rendered_evaluation_prompt': prompt, 'prompt_sha256': pa, 'prompts_exactly_match_historical_calls': True,
            'target': target, 'target_raw_json_no_fences': target.startswith('{'), 'assistant_generation_prefix': '<|im_start|>assistant\n',
            'training_suffix': '<|im_end|>\n', 'eos_supervised': True, 'post_eos_newline_supervised': False,
            'base_adapter_output_identical': outputs[0] == outputs[1]})
    write('PROMPT-AUDIT.json', {'records': audits, 'chat_template': tokenizer.chat_template,
        'chat_template_sha256': hashlib.sha256(tokenizer.chat_template.encode()).hexdigest(),
        'diagnostic_protocol': c.read(c.OUT / 'DIAGNOSTIC-PROTOCOL.json'),
        'mismatches': [], 'observed_distribution_gap': 'teacher-forced gold package prefixes versus free-running fenced answer snippets',
        'decoding_note': 'greedy repetition_penalty 1.1 alters logits during generation; loss measures unpenalized gold-prefix likelihood'})
    write('FIRST-DIVERGENCE.json', {'records': divergence, 'historical_acceptance_preserved': '0/6 base and 0/6 adapter', 'rescoring': False})
    write('RESULT.json', {'classification': 'R6_60_TARGET_LIKELIHOOD_IMPROVED' if b['pooled_token_mean_nll_nats'] < a['pooled_token_mean_nll_nats'] and b['equal_record_mean_nll_nats'] < a['equal_record_mean_nll_nats'] else 'R6_60_NO_MEASURABLE_LEARNING',
        'base_equal_record_nll': a['equal_record_mean_nll_nats'], 'adapter_equal_record_nll': b['equal_record_mean_nll_nats'],
        'equal_record_delta': b['equal_record_mean_nll_nats']-a['equal_record_mean_nll_nats'],
        'base_pooled_nll': a['pooled_token_mean_nll_nats'], 'adapter_pooled_nll': b['pooled_token_mean_nll_nats'],
        'pooled_delta': b['pooled_token_mean_nll_nats']-a['pooled_token_mean_nll_nats'], 'supervised_tokens': a['supervised_tokens'],
        'optional_probes': 'NOT_RUN: exact matched prompts already produced preserved failures', 'kernel_constructs': 26,
        'optimizer_updates': 0, 'dataset_expansion': 0, 'historical_rescoring': False, 'P6_A04_acceptance_executions': 0, 'P6_A05_access': False})
    print(json.dumps(c.read(OUT / 'RESULT.json'), indent=2))


def publication(seal=False):
    check()
    paths = list(HERE.glob('*.py')) + [ROOT / 'benchmark/results/phase6/R6_60-REPORT.md', ROOT / 'docs/learned-distribution-r6.60.md']
    paths += [p for p in OUT.iterdir() if p.is_file() and p.name not in ('PUBLICATION-IDENTITIES.json', 'VERIFICATION.json')]
    manifest = {'round': 'R6.60', 'files': {p.relative_to(ROOT).as_posix(): {'sha256': c.sha(p), 'bytes': p.stat().st_size} for p in sorted(paths)}}
    if seal:
        write('PUBLICATION-IDENTITIES.json', manifest)
    assert manifest == c.read(OUT / 'PUBLICATION-IDENTITIES.json')
    for p in paths:
        text = p.read_text(encoding='utf-8')
        assert all(line == line.rstrip() for line in text.splitlines()), str(p)
        assert not re.search(r'(?:hf_[A-Za-z0-9]{25,}|sk-[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})', text)
        if p.suffix == '.json':
            json.loads(text)
        if p.suffix == '.py':
            ast.parse(text)
        if p.suffix == '.md':
            for target in re.findall(r'\]\(([^)]+)\)', text):
                if '://' not in target and not target.startswith('#'):
                    assert (p.parent / target.split('#')[0]).exists(), target
    diff = subprocess.run(['git', 'diff', '--check'], cwd=ROOT, capture_output=True, text=True)
    assert diff.returncode == 0, diff.stdout + diff.stderr
    if seal:
        write('VERIFICATION.json', {'passed': True, 'manifest_sha256': c.sha(OUT / 'PUBLICATION-IDENTITIES.json'),
            'baseline_reverified': True, 'historical_scores_preserved': True, 'kernel_constructs': 26,
            'git_diff_check_returncode': 0, 'source_json_links_whitespace_credentials': 'PASS'})
    else:
        assert c.read(OUT / 'VERIFICATION.json')['manifest_sha256'] == c.sha(OUT / 'PUBLICATION-IDENTITIES.json')
    print('PASS R6.60 publication and preserved baseline')


if __name__ == '__main__':
    os.environ['HF_HUB_OFFLINE'] = '1'
    mode = sys.argv[1]
    if mode == 'freeze':
        freeze()
    elif mode == 'evaluate':
        evaluate(sys.argv[2])
    elif mode == 'dispatch':
        dispatch()
    elif mode == 'analyze':
        analyze()
    elif mode in ('seal', 'verify'):
        publication(mode == 'seal')
    else:
        raise ValueError(mode)
