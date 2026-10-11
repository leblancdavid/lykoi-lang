"""Additive qualification using frozen R6.69 verification and R6.68 grammar."""
import ast
import copy
import hashlib
import importlib.util
import inspect
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = ROOT / 'benchmark/results/phase6/r6_70'
sys.path.insert(0, str(ROOT / 'experiments/inference_qualification_r6_69'))
spec = importlib.util.spec_from_file_location('r670_inherited', ROOT / 'experiments/inference_qualification_r6_69/qualify.py')
q = importlib.util.module_from_spec(spec)
spec.loader.exec_module(q)
f, h = q.f, q.h


def write(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n', encoding='utf-8', newline='\n')


def ordered_action(action):
    """Reorder only the two fixed envelopes; never select or alter their values."""
    assert set(action) == {'id', 'type', 'deps', 'node'}
    assert set(action['node']) == {'op', 'expr'}
    result = dict(id=action['id'], type=action['type'], deps=action['deps'],
                  node=dict(op=action['node']['op'], expr=action['node']['expr']))
    assert result == action
    return result


def baseline():
    q.check_freeze()
    result = q.baseline()
    result['r6_69_publication'] = f.publication('r6_69')
    assert f.read(q.OUT / 'INFERENCE-READINESS.json')['classification'] == 'R6_69_PROTOCOL_HALT'
    result['r6_69_failure_sha256'] = f.sha(q.OUT / 'HALT.json')
    result['r6_69_verifier_sha256'] = f.sha(ROOT / 'experiments/inference_qualification_r6_69/verifier.py')
    return result


def cpu_controls(config):
    from transformers import AutoTokenizer
    spec = importlib.util.spec_from_file_location('r670_decoder_cpu', ROOT / 'experiments/structured_generation_r6_68/decoder.py')
    decoder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(decoder)
    tokenizer = AutoTokenizer.from_pretrained(f.STORE / 'checkpoint', local_files_only=True, trust_remote_code=False)
    mask = decoder.StructuralMask(tokenizer, 0, lambda text: f.successor.validate_action(f.successor.c.load(text)))
    original = config['neutral_action']
    ordered = ordered_action(original)
    dumps = lambda action: json.dumps(action, separators=(',', ':'), ensure_ascii=True, allow_nan=False)
    text = dumps(ordered)
    assert mask.accepts(text) == (True, True)
    assert not mask.accepts(dumps(original))[0]
    repeats = [dumps(ordered_action(json.loads(json.dumps(original, sort_keys=True)))).encode('ascii') for _ in range(100)]
    assert all(value == text.encode('ascii') for value in repeats)
    assert json.loads(text) == original
    alternatives = []
    for operation in ('add', 'le', 'eq'):
        for typ in ('Int64', 'Bool'):
            action = copy.deepcopy(ordered)
            action['type'] = typ
            action['node']['expr'] = {operation: [{'const': True}, {'ref': 'arbitrary_out_of_scope'}]}
            candidate = dumps(action)
            assert mask.accepts(candidate) == (True, True)
            assert all(mask.accepts(candidate[:i])[0] for i in range(len(candidate) + 1))
            alternatives.append(dict(operation=operation, type=typ, text=candidate, all_prefixes_viable=True))
    negatives = []
    mutations = [
        ('outer_order', lambda a: dict(sorted(a.items()))),
        ('nested_order', lambda a: dict(a, node=dict(expr=a['node']['expr'], op=a['node']['op']))),
        ('missing_field', lambda a: {k: v for k, v in a.items() if k != 'deps'}),
        ('extra_field', lambda a: dict(a, extra=0)),
        ('extra_nested_field', lambda a: dict(a, node=dict(a['node'], extra=0))),
        ('invalid_type', lambda a: dict(a, type=1)),
        ('invalid_deps_type', lambda a: dict(a, deps=False)),
        ('invalid_operation', lambda a: dict(a, node=dict(op='value', expr={'sub': [{'const': 1}, {'const': 2}]}))),
        ('invalid_node_operation', lambda a: dict(a, node=dict(a['node'], op='other'))),
        ('invalid_operand_type', lambda a: dict(a, node=dict(op='value', expr={'eq': [{'ref': 1}, {'const': True}]}))),
    ]
    for label, mutate in mutations:
        candidate = dumps(mutate(copy.deepcopy(ordered)))
        assert not mask.accepts(candidate)[0], label
        negatives.append(dict(name=label, raw_text=candidate, rejected=True))
    write('CPU-SERIALIZATION-CONTROLS.json', dict(passed=True, cpu_only=True, model_loads=0,
          original_text=dumps(original), corrected_text=text, same_semantic_content=True,
          outer_order=list(ordered), nested_order=list(ordered['node']), repeat_count=100,
          serialization_sha256=hashlib.sha256(text.encode('ascii')).hexdigest(), identical_bytes=True,
          alternatives=alternatives, invalid_controls=negatives, grammar_sha256=f.sha(ROOT / 'experiments/structured_generation_r6_68/decoder.py')))


def effective_worker():
    """Bounded exact edits to a pinned historical worker, archived before dispatch."""
    source = inspect.getsource(q.worker)
    edits = [
        ("    config=f.read(OUT/'QUALIFICATION-CONFIGURATION.json')", "    config=f.read(OUT/'QUALIFICATION-CONFIGURATION.json')\n    config['neutral_action']=ordered_action(config['neutral_action'])"),
        ("    before=ns['base_manifest'](model)", "    before=ns['base_manifest'](model)\n    write(track.upper()+'-INITIALIZATION.json',dict(passed=True,inference_only=True,all_parameters_frozen=all(not p.requires_grad for p in model.parameters()),base_identity=f.identity(before)))"),
        ("('complete_action_eos',neutral,1)", "('neutral_suffix_repeat',neutral[:-1],4),('complete_action_eos',neutral,1)"),
        ("                applied.append(dict(allowed=", "                prefix=self.tokenizer.decode(input_ids[0,self.prompt_length:].tolist(),skip_special_tokens=False)\n                allowed_ids=finite.nonzero().flatten().cpu().tolist()\n                applied.append(dict(prefix=prefix,selected_text=self.tokenizer.decode([selected],skip_special_tokens=False),allowed_ids_sha256=f.identity(allowed_ids),allowed="),
        ("        if name=='neutral_suffix_continuation': assert complete and eos", "        # Persist raw outputs/resources before any post-generation assertion."),
        ("        if name=='complete_action_eos': assert new==[tokenizer.eos_token_id] and complete", "        # EOS assertion follows persistence."),
        ("        if name=='one_token_budget': assert len(new)==1 and not eos and not complete", "        # Budget assertion follows persistence."),
        ("        print(track,name,len(new),complete,eos,flush=True)", "        assert [decision['selected'] for decision in applied]==new,'SELECTED_TOKEN_CORRESPONDENCE'\n        if name in ('neutral_suffix_continuation','neutral_suffix_repeat'): assert complete and eos\n        if name=='neutral_suffix_repeat': assert new==probes[-2]['new_token_ids'],'DETERMINISTIC_REPEAT'\n        if name=='complete_action_eos': assert new==[tokenizer.eos_token_id] and complete\n        if name=='one_token_budget': assert len(new)==1 and not eos and not complete\n        print(track,name,len(new),complete,eos,flush=True)"),
    ]
    for old, new in edits:
        assert source.count(old) == 1, old
        source = source.replace(old, new)
    ast.parse(source)
    return source


def freeze():
    assert not OUT.exists()
    preflight = baseline()
    OUT.mkdir()
    write('PREFLIGHT.json', preflight)
    config = copy.deepcopy(f.read(q.OUT / 'QUALIFICATION-CONFIGURATION.json'))
    config.update(round='R6.70', max_generation_calls=10)
    config['probes'].insert(2, 'neutral_suffix_repeat')
    write('QUALIFICATION-CONFIGURATION.json', config)
    # Test the actual sorted on-disk round trip before loading any model.
    cpu_controls(f.read(OUT / 'QUALIFICATION-CONFIGURATION.json'))
    (OUT / 'EFFECTIVE-WORKER.py.txt').write_text(effective_worker(), encoding='utf-8', newline='\n')
    write('SOURCE-FREEZE.json', dict(files={p.relative_to(ROOT).as_posix(): f.sha(p) for p in list(HERE.glob('*.py')) + [ROOT / 'benchmark/results/phase6/R6_70-PROTOCOL.md']},
          inputs={p.name: f.sha(p) for p in OUT.iterdir()}))
    print('PASS baseline, CPU serialization controls and R6.70 source freeze')


def check_freeze():
    seal = f.read(OUT / 'SOURCE-FREEZE.json')
    for path, digest in seal['files'].items():
        assert f.sha(ROOT / path) == digest, path
    for name, digest in seal['inputs'].items():
        assert f.sha(OUT / name) == digest, name


def worker(track):
    check_freeze()
    source = (OUT / 'EFFECTIVE-WORKER.py.txt').read_text(encoding='utf-8')
    assert source == effective_worker()
    namespace = dict(q.__dict__, OUT=OUT, write=write, check_freeze=check_freeze, ordered_action=ordered_action)
    exec(compile(source, str(OUT / 'EFFECTIVE-WORKER.py.txt'), 'exec'), namespace)
    try:
        namespace['worker'](track)
    finally:
        import torch
        write(track.upper() + '-WORKER-RESOURCES.json', dict(peak_allocated_bytes=torch.cuda.max_memory_allocated(),
              peak_reserved_bytes=torch.cuda.max_memory_reserved(), end_free_bytes=torch.cuda.mem_get_info()[0]))


def execute():
    check_freeze()
    assert baseline() == f.read(OUT / 'PREFLIGHT.json')
    with (OUT / 'DISPATCH-CLAIM.json').open('x', encoding='utf-8') as stream:
        json.dump(dict(attempts=1, neutral_calls_max=10), stream)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', HF_HUB_OFFLINE='1', HF_HUB_DISABLE_TELEMETRY='1',
               TOKENIZERS_PARALLELISM='false', HF_HOME=str(f.STORE / 'hf-cache'))
    env.pop('CUDA_VISIBLE_DEVICES', None)
    try:
        for track in ('base', 'adapter'):
            args = [str(f.PYTHON), '-B', str(Path(__file__).resolve()), 'worker', track]
            start = time.perf_counter()
            try:
                proc = subprocess.run(args, cwd=ROOT, env=env, capture_output=True, text=True, timeout=1800)
            except subprocess.TimeoutExpired as exc:
                write(track.upper() + '-PROCESS.json', dict(timeout=True, seconds=time.perf_counter()-start,
                      stdout=str(exc.stdout), stderr=str(exc.stderr)))
                raise
            write(track.upper() + '-PROCESS.json', dict(argv=args, returncode=proc.returncode, stdout=proc.stdout,
                  stderr=proc.stderr, seconds=time.perf_counter()-start))
            print(proc.stdout, flush=True)
            assert proc.returncode == 0, proc.stderr
    except BaseException as exc:
        write('HALT.json', dict(error=str(exc), traceback=traceback.format_exc(), retry=False))
        raise


if __name__ == '__main__':
    {'freeze': freeze, 'execute': execute, 'worker': lambda: worker(sys.argv[2])}[sys.argv[1]]()
