"""R6.61 frozen read-only logits and minimal-prefix continuations."""
import ast
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = ROOT / 'benchmark/results/phase6/r6_61'
sys.path.insert(0, str(ROOT / 'experiments/learned_distribution_r6_60'))
import diagnose as previous
c = previous.c
PREFIX = '{"'


def write(name, value):
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    assert not path.exists(), name
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n', encoding='utf-8', newline='\n')


def baseline():
    receipt = previous.baseline()
    for name, entry in c.read(previous.OUT / 'PUBLICATION-IDENTITIES.json')['files'].items():
        assert c.sha(ROOT / name) == entry['sha256'], name
    for name, digest in c.read(previous.OUT / 'INDEX-IDENTITIES.json').items():
        assert c.sha(ROOT / name) == digest, name
    assert c.read(previous.OUT / 'VERIFICATION.json')['passed']
    return dict(receipt, r6_60_publication_sha256=c.sha(previous.OUT / 'PUBLICATION-IDENTITIES.json'),
                original_generation_results={p.relative_to(ROOT).as_posix(): c.sha(p)
                    for folder, track in ((c.OUT, 'BASE'), (previous.prior.OUT, 'ADAPTER'))
                    for p in sorted(folder.glob(f'DIAGNOSTIC-{track}-E*.json'))})


def tokenizer():
    from transformers import AutoTokenizer
    return AutoTokenizer.from_pretrained(c.STORE / 'checkpoint', local_files_only=True, trust_remote_code=False)


def freeze():
    write('BASELINE.json', baseline())
    t = tokenizer()
    assert t.decode([4913]) == PREFIX and t.encode(PREFIX, add_special_tokens=False) == [4913]
    assert t.decode([73594]) == '```' and t.encode('```', add_special_tokens=False) == [73594]
    assert json.loads(PREFIX + 'definitions":[]}') == {'definitions': []}
    records = []
    expected = {r['episode_id']: r for r in c.read(c.OUT / 'SOURCE-DATASET-IDENTITIES.json')['records']}
    for row in c.rows():
        assert c.identity(row) == expected[row['episode_id']]['canonical_record_sha256']
        ids, labels, measure = c.q52.encoded(row, t)
        e = expected[row['episode_id']]
        assert hashlib.sha256(json.dumps(ids).encode()).hexdigest() == e['tokens_sha256']
        assert hashlib.sha256(json.dumps(labels).encode()).hexdigest() == e['labels_sha256']
        assert measure == e['tokenization']
        prompt = t.apply_chat_template(row['prompt'], tokenize=False, add_generation_prompt=True)
        pid = t.encode(prompt, add_special_tokens=False)
        prefixed = t.encode(prompt + PREFIX, add_special_tokens=False)
        assert prefixed == pid + [4913] and len(prefixed) + 1400 <= 2048
        assert prompt.endswith('<|im_start|>assistant\n')
        assert row['completion'][0]['content'].startswith(PREFIX)
        for folder, track in ((c.OUT, 'BASE'), (previous.prior.OUT, 'ADAPTER')):
            old = c.read(folder / f'DIAGNOSTIC-{track}-{row["episode_id"].split("/")[-1]}.json')
            assert old['prompt_sha256'] == c.identity(row['prompt'])
        records.append({'episode_id': row['episode_id'], 'messages': row['prompt'],
            'message_identity': c.identity(row['prompt']), 'rendered_prompt': prompt,
            'rendered_prompt_sha256': hashlib.sha256(prompt.encode()).hexdigest(),
            'input_ids': pid, 'prefixed_input_ids': prefixed, 'target_identity': c.identity(row['completion'])})
    write('PREFIX-SPECIFICATION.json', {'prefix': PREFIX, 'utf8_hex': PREFIX.encode().hex(), 'token_ids': [4913],
        'complete_document': False, 'syntactically_valid_partial_prefix': True, 'task_specific_content': False,
        'tokens': {str(i): {'decoded': t.decode([i]), 'vocabulary_text': t.convert_ids_to_tokens(i)} for i in (4913, 73594)},
        'chat_template': t.chat_template, 'chat_template_sha256': hashlib.sha256(t.chat_template.encode()).hexdigest(),
        'records': records, 'generation': c.read(c.OUT / 'DIAGNOSTIC-PROTOCOL.json'),
        'penalties': [1.0, 1.1], 'max_continuation_calls': 24,
        'evaluation': 'unchanged native scorer; prefix+continuation; no repairs or sealing; later blocked stages NOT_REACHED'})
    write('FREEZE.json', {'source_sha256': c.sha(HERE / 'diagnose.py'), 'protocol_sha256': c.sha(OUT / 'PROTOCOL.md'),
        'prefix_specification_sha256': c.sha(OUT / 'PREFIX-SPECIFICATION.json'),
        'baseline_sha256': c.sha(OUT / 'BASELINE.json'), 'optimizer_updates': 0})
    print('PASS baseline and pre-execution prefix/settings/evaluation freeze')


def check():
    f = c.read(OUT / 'FREEZE.json')
    for path, key in ((HERE / 'diagnose.py', 'source_sha256'), (OUT / 'PROTOCOL.md', 'protocol_sha256'),
                      (OUT / 'PREFIX-SPECIFICATION.json', 'prefix_specification_sha256'), (OUT / 'BASELINE.json', 'baseline_sha256')):
        assert c.sha(path) == f[key], str(path)
    assert baseline() == c.read(OUT / 'BASELINE.json')


def evaluate(track):
    check()
    write(f'{track.upper()}-CLAIM.json', {'track': track, 'pid': os.getpid()})
    import torch
    from transformers import GenerationConfig, RepetitionPenaltyLogitsProcessor, StoppingCriteria, StoppingCriteriaList
    from peft import PeftModel, prepare_model_for_kbit_training
    spec = importlib.util.spec_from_file_location('r61_helpers', ROOT / 'experiments/lora_smoke_r6_56/worker.py')
    helpers = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helpers)
    c.q52.seed()
    started = time.perf_counter()
    torch.cuda.reset_peak_memory_stats()
    model, quant = c.q52.load_base()
    model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=True,
                                            gradient_checkpointing_kwargs={'use_reentrant': False})
    if track == 'adapter':
        model = PeftModel.from_pretrained(model, previous.prior.ARTIFACTS / 'step20/adapter', is_trainable=False, local_files_only=True)
        assert helpers.adapter_manifest(model) == c.read(previous.prior.OUT / 'TRAINING-RESULT.json')['trained_adapter_tensors']
    model.eval()
    model.requires_grad_(False)
    assert not any(m.training for m in model.modules())
    before, adapter_before = helpers.base_manifest(model), helpers.adapter_manifest(model)
    t = tokenizer()
    frozen = c.read(OUT / 'PREFIX-SPECIFICATION.json')

    def bounds():
        free = torch.cuda.mem_get_info()[0]
        assert torch.cuda.max_memory_reserved() <= 8 * 1024**3 and free >= 1.5 * 1024**3
        assert c.rss(os.getpid()) <= 16 * 1024**3
        return free

    class Limit(StoppingCriteria):
        def __init__(self):
            self.start = time.perf_counter()
            self.timed_out = False

        def __call__(self, input_ids, scores, **kwargs):
            bounds()
            self.timed_out = time.perf_counter() - self.start >= 120
            return self.timed_out

    def distribution(logits):
        assert torch.isfinite(logits).all().item()
        probs = torch.softmax(logits, dim=-1)
        top = int(torch.argmax(logits).item())
        def token(i):
            return {'id': i, 'text': t.decode([i]), 'logit': float(logits[i]), 'probability': float(probs[i]),
                    'rank': 1 + int((logits > logits[i]).sum().item()), 'tied_tokens': int((logits == logits[i]).sum().item())}
        return {'raw_opening': token(4913), 'fence': token(73594), 'top': token(top),
                'logit_margin_opening_minus_fence': float(logits[4913] - logits[73594]),
                'probability_margin_opening_minus_fence': float(probs[4913] - probs[73594])}

    measurements = []
    for record, row in zip(frozen['records'], c.rows()):
        eid = record['episode_id'].split('/')[-1]
        x = torch.tensor([record['input_ids']], device='cuda')
        torch.cuda.synchronize()
        start = time.perf_counter()
        with torch.inference_mode():
            output = model(input_ids=x, attention_mask=torch.ones_like(x), use_cache=False)
            raw = output.logits[:, -1, :].float().clone()
            raw_data = distribution(raw[0])
            matrix = []
            for penalty in (1.0, 1.1):
                processed = RepetitionPenaltyLogitsProcessor(penalty)(x, raw.clone())
                matrix.append({'penalty': penalty, 'processed': distribution(processed[0]),
                    'target_in_prompt': {str(i): i in record['input_ids'] for i in (4913, 73594)}})
        torch.cuda.synchronize()
        elapsed = time.perf_counter() - start
        raw_path = OUT / f'{track.upper()}-{eid}-RAW-LOGITS.f32'
        assert not raw_path.exists()
        raw.cpu().numpy().astype('<f4').tofile(raw_path)
        measurements.append({'episode_id': record['episode_id'], 'raw': raw_data, 'conditions': matrix,
            'forward_seconds': elapsed, 'vocabulary_size': raw.shape[-1], 'raw_logits_sha256': c.sha(raw_path),
            'raw_logits_file': raw_path.relative_to(ROOT).as_posix(), 'raw_dtype': 'little-endian float32',
            'input_identity': c.identity(record['input_ids'])})
        del output, raw, processed, x
        torch.cuda.empty_cache()
        bounds()
        for penalty in (1.0, 1.1):
            generation = GenerationConfig.from_dict(frozen['generation']['resolved_generation_configuration'])
            generation.repetition_penalty = penalty
            x = torch.tensor([record['prefixed_input_ids']], device='cuda')
            limit = Limit()
            torch.cuda.synchronize()
            start = time.perf_counter()
            with torch.inference_mode():
                generated = model.generate(input_ids=x, attention_mask=torch.ones_like(x), generation_config=generation,
                    use_cache=False, stopping_criteria=StoppingCriteriaList([limit]))
            torch.cuda.synchronize()
            elapsed = time.perf_counter() - start
            ids = generated[0, x.shape[1]:].cpu().tolist()
            eos = bool(ids and ids[-1] in generation.eos_token_id)
            content = ids[:-1] if eos else ids
            continuation = t.decode(content, skip_special_tokens=False)
            text = PREFIX + continuation
            name = f'CONTINUATION-{track.upper()}-{eid}-P{penalty:.1f}'
            write(name + '.json', {'track': track, 'episode_id': record['episode_id'], 'penalty': penalty,
                'prefix': PREFIX, 'continuation': continuation, 'completed_text': text, 'output_token_ids': ids,
                'output_tokens_including_eos': len(ids), 'eos_terminated': eos, 'time_limit_reached': limit.timed_out,
                'token_limit_reached': len(ids) == generation.max_new_tokens and not eos,
                'input_tokens': x.shape[1], 'generation_seconds': elapsed, 'scores': c.score(text, row),
                'peak_allocated_bytes': torch.cuda.max_memory_allocated(), 'peak_reserved_bytes': torch.cuda.max_memory_reserved(),
                'device_free_bytes': bounds(), 'generation_configuration': generation.to_dict()})
            (OUT / (name + '.txt')).write_text(continuation, encoding='utf-8', newline='\n')
            print(track, eid, penalty, len(ids), elapsed, flush=True)
            del generated, x
            torch.cuda.empty_cache()
            assert not limit.timed_out, 'generation timeout preserved; stop'
    assert helpers.base_manifest(model) == before
    assert helpers.adapter_manifest(model) == adapter_before
    assert all(p.grad is None for p in model.parameters())
    write(f'{track.upper()}-MEASUREMENTS.json', {'track': track, 'records': measurements, 'quantization': quant,
        'whole_worker_seconds': time.perf_counter() - started, 'peak_allocated_bytes': torch.cuda.max_memory_allocated(),
        'peak_reserved_bytes': torch.cuda.max_memory_reserved(), 'device_free_bytes': bounds(),
        'base_tensor_identity': c.identity(before), 'adapter_tensor_identity': c.identity(adapter_before),
        'parameters_buffers_quantization_unchanged': True, 'dropout_disabled': True, 'gradients': False, 'optimizer_updates': 0})


def dispatch():
    check()
    for track in ('base', 'adapter'):
        assert not (OUT / f'{track.upper()}-PROCESS.json').exists()
        start = time.perf_counter()
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', HF_HUB_OFFLINE='1', HF_HUB_DISABLE_TELEMETRY='1')
        p = subprocess.Popen([str(c.PYTHON), '-B', str(HERE / 'diagnose.py'), 'evaluate', track], cwd=ROOT,
                             env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        # communicate with short timeouts drains pipes without unbounded buffering in child.
        peak, samples, abort = 0, 0, None
        while True:
            rss = c.rss(p.pid)
            peak = max(peak, rss or 0)
            samples += 1
            if peak > 16 * 1024**3 or time.perf_counter() - start > 1800:
                abort = 'RSS_OR_PROCESS_TIME_LIMIT'
                p.kill()
            try:
                stdout, stderr = p.communicate(timeout=0.1)
                break
            except subprocess.TimeoutExpired:
                continue
        write(f'{track.upper()}-PROCESS.json', {'returncode': p.returncode, 'stdout': stdout, 'stderr': stderr,
            'seconds': time.perf_counter() - start, 'peak_sampled_rss_bytes': peak, 'samples': samples,
            'external_abort': abort, 'timeout_seconds': 1800})
        assert p.returncode == 0 and abort is None, stderr
    print('PASS bounded paired diagnosis')


def analyze():
    check()
    matrix, inventory = [], []
    for track in ('BASE', 'ADAPTER'):
        data = c.read(OUT / f'{track}-MEASUREMENTS.json')
        for r in data['records']:
            for condition in r['conditions']:
                matrix.append({'track': track.lower(), 'episode_id': r['episode_id'], 'raw': r['raw'], **condition})
    for path in sorted(OUT.glob('CONTINUATION-*.json')):
        r = c.read(path)
        text, scores = r['completed_text'], r['scores']
        keys = ['definitions', 'foundation', 'program', 'version']
        try:
            parsed = json.loads(text)
            missing = sorted(set(keys) - set(parsed)) if isinstance(parsed, dict) else keys
            parse_error = None
        except json.JSONDecodeError as exc:
            parsed = None
            missing = None
            parse_error = {'character_index': exc.pos, 'line': exc.lineno, 'column': exc.colno, 'detail': exc.msg}
        ids = r['output_token_ids']
        repeat = [i for i in range(8, len(ids) - 7) if ids[i-8:i] == ids[i:i+8]]
        diagnostic = scores.get('native_diagnostic')
        inventory.append({'file': path.relative_to(ROOT).as_posix(), 'track': r['track'], 'episode_id': r['episode_id'],
            'penalty': r['penalty'], 'parse_error': parse_error, 'native_diagnostic': diagnostic,
            'first_divergence': parse_error or diagnostic or next((v for v in scores['functional_cases'] if v['differences']), None),
            'raw_opening_preserved': text.startswith(PREFIX), 'fence_occurs': '```' in text,
            'missing_structural_keys': missing, 'keys_without_lexical_occurrence': [k for k in keys if not re.search('"' + k + '"\\s*:', text)],
            'visible_non_wrapper_type_labels': re.findall(r'"(?:type|result_type)"\s*:\s*"(?!Int64"|Bool"|Unit")([^"]+)"', text),
            'invalid_typed_arguments': diagnostic if diagnostic and diagnostic.get('code') == 'TYPE' else 'NOT_REACHED_OR_NOT_REPORTED',
            'incorrect_semantic_operations': 'NOT_REACHED' if not scores['semantic_valid'] else
                ('functional differences' if not scores['functional_acceptance'] else 'none in tested cases'),
            'premature_eos_incomplete_package': r['eos_terminated'] and not scores['schema_valid'],
            'repeated_adjacent_8token_blocks': repeat, 'token_limit_reached': r['token_limit_reached'],
            'time_limit_reached': r['time_limit_reached'], 'scores': scores})
    write('FIRST-TOKEN-MATRIX.json', {'rank_policy': '1 + strictly greater logits; ties explicit', 'records': matrix})
    write('FIRST-DIVERGENCE.json', {'records': inventory, 'historical_outputs': 'unchanged R6.60 FIRST-DIVERGENCE.json; original first token73594 on12/12'})
    summary = []
    for track in ('base', 'adapter'):
        for penalty in (1.0, 1.1):
            rows = [r for r in inventory if r['track'] == track and r['penalty'] == penalty]
            assert len(rows) == 6
            summary.append({'track': track, 'penalty': penalty, 'calls': len(rows),
                **{k: sum(r['scores'][k] is True for r in rows) for k in ('output_valid', 'schema_valid', 'type_valid', 'semantic_valid', 'functional_acceptance')},
                'type_not_reached': sum(r['scores']['type_valid'] == 'NOT_REACHED' for r in rows),
                'functional_reached': sum(bool(r['scores']['functional_cases']) for r in rows)})
    accepted = sum(r['functional_acceptance'] for r in summary)
    classification = 'R6_61_PREFIX_CONTINUATION_SUPPORTED' if accepted else 'R6_61_BROADER_GENERATION_GAP'
    write('VALIDATION-RESULTS.json', {'summary': summary, 'records': inventory})
    write('RESULT.json', {'classification': classification, 'continuation_summary': summary,
        'first_token_observations': len(matrix), 'continuation_calls': len(inventory), 'kernel_constructs': 26,
        'optimizer_updates': 0, 'scheduler_updates': 0, 'dataset_expansion': 0, 'historical_rescoring': False,
        'P6_A04_acceptance_executions': 0, 'P6_A05_access': False, 'independent_authoring': False, 'generalization': False})
    print(json.dumps(c.read(OUT / 'RESULT.json'), indent=2))


def publish(seal):
    check()
    paths = sorted([HERE / 'diagnose.py', ROOT / 'benchmark/results/phase6/R6_61-REPORT.md',
                    ROOT / 'docs/research-log-r6.61.md'] + [p for p in OUT.iterdir() if p.is_file()
                    and p.name not in ('PUBLICATION-IDENTITIES.json', 'VERIFICATION.json')])
    for path in paths:
        if path.suffix == '.f32':
            continue
        text = path.read_text(encoding='utf-8')
        assert not re.search(r'(?:hf_[A-Za-z0-9]{25,}|sk-[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})', text)
        if path.suffix == '.json':
            json.loads(text)
        if path.suffix == '.py':
            ast.parse(text)
        if path.suffix == '.md':
            assert all(line == line.rstrip() for line in text.splitlines())
            for target in re.findall(r'\]\(([^)]+)\)', text):
                if '://' not in target and not target.startswith('#'):
                    assert (path.parent / target.split('#')[0]).exists(), target
    # Independent CPU reconstruction of ranks/probabilities and penalty transformation.
    import numpy as np
    frozen = c.read(OUT / 'PREFIX-SPECIFICATION.json')
    for track in ('BASE', 'ADAPTER'):
        data = c.read(OUT / f'{track}-MEASUREMENTS.json')
        assert data['parameters_buffers_quantization_unchanged'] and data['dropout_disabled'] and not data['gradients']
        for r, record in zip(data['records'], frozen['records']):
            path = ROOT / r['raw_logits_file']
            assert c.sha(path) == r['raw_logits_sha256']
            logits = np.fromfile(path, dtype='<f4')
            assert len(logits) == r['vocabulary_size'] and np.isfinite(logits).all()
            for condition in r['conditions']:
                v = logits.copy()
                for i in set(record['input_ids']):
                    v[i] = v[i] * condition['penalty'] if v[i] < 0 else v[i] / condition['penalty']
                probs = np.exp(v.astype(np.float64) - float(np.max(v)))
                probs /= probs.sum()
                observed = condition['processed']
                assert int(np.argmax(v)) == observed['top']['id']
                for name in ('raw_opening', 'fence', 'top'):
                    token = observed[name]
                    i = token['id']
                    assert 1 + int(np.sum(v > v[i])) == token['rank']
                    assert abs(float(v[i]) - token['logit']) < 1e-5
                    assert abs(float(probs[i]) - token['probability']) < 1e-6
    diff = subprocess.run(['git', 'diff', '--check'], cwd=ROOT, capture_output=True, text=True)
    assert diff.returncode == 0, diff.stdout + diff.stderr
    manifest = {'round': 'R6.61', 'files': {p.relative_to(ROOT).as_posix(): {'sha256': c.sha(p), 'bytes': p.stat().st_size} for p in paths}}
    if seal:
        write('PUBLICATION-IDENTITIES.json', manifest)
        write('VERIFICATION.json', {'passed': True, 'manifest_sha256': c.sha(OUT / 'PUBLICATION-IDENTITIES.json'),
            'baseline_and_history_preserved': True, 'kernel_constructs': 26, 'git_diff_check_returncode': 0,
            'independent_cpu_logits_rank_probability_check': 'PASS', 'json_python_links_credentials': 'PASS'})
    assert manifest == c.read(OUT / 'PUBLICATION-IDENTITIES.json')
    assert c.read(OUT / 'VERIFICATION.json')['manifest_sha256'] == c.sha(OUT / 'PUBLICATION-IDENTITIES.json')
    print('PASS R6.61 publication, independent numerical reconstruction and preservation')


if __name__ == '__main__':
    os.environ['HF_HUB_OFFLINE'] = '1'
    os.environ['HF_HUB_DISABLE_TELEMETRY'] = '1'
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
        publish(mode == 'seal')
    else:
        raise ValueError(mode)
