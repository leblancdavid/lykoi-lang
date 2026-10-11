"""Fresh bounded successor; inherited model, grammar, scorer and inputs stay frozen."""
import ast
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
OUT = ROOT / 'benchmark/results/phase6/r6_71'
sys.path.insert(0, str(ROOT / 'experiments/inference_qualification_r6_69'))
sys.path.insert(0, str(ROOT / 'experiments/structured_generation_r6_68'))
spec = importlib.util.spec_from_file_location('r671_qualified', ROOT / 'experiments/inference_qualification_r6_70/qualify.py')
qualified = importlib.util.module_from_spec(spec)
spec.loader.exec_module(qualified)
q, h, f = qualified.q, qualified.h, qualified.f


def write(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n', encoding='utf-8', newline='\n')


def baseline():
    qualified.check_freeze()
    result = qualified.baseline()
    result['r6_70_publication'] = f.publication('r6_70')
    receipt = f.read(qualified.OUT / 'INFERENCE-READINESS.json')
    assert receipt['ready'] and receipt['classification'] == 'R6_70_INFERENCE_COMPARISON_READY'
    result['readiness_sha256'] = f.sha(qualified.OUT / 'INFERENCE-READINESS.json')
    return result


def effective_worker():
    source = inspect.getsource(h.worker)
    start = source.index('    started=time.perf_counter()')
    end = source.index('    tokenizer=AutoTokenizer', start)
    inherited = inspect.getsource(q.worker)
    block = inherited[inherited.index("    source=(ROOT/"):inherited.index('    tokenizer=AutoTokenizer')]
    source = source[:start] + '    started=time.perf_counter()\n' + block + '    load_seconds=time.perf_counter()-started\n' + source[end:]
    source = source.replace("    before=ns['base_manifest'](model)\n", "    before=ns['base_manifest'](model)\n    write(track.upper()+'-INITIALIZATION.json',dict(inference_only=True,all_parameters_frozen=all(not p.requires_grad for p in model.parameters()),base_identity=f.identity(before),adapter_identity=f.identity(adapter_before)))\n")
    # Persist a dispatched call and its last observed prefix even if generation raises.
    source = source.replace('             return False', '             return False')
    source = source.replace('            return False', "            progress['token_ids']=input_ids[0,progress['prompt_length']:].cpu().tolist()\n            return False")
    source = source.replace("            try:\n                with torch.inference_mode():", "            progress=dict(token_ids=[],prompt_length=x.input_ids.shape[1])\n            write(f'{track.upper()}-{condition}-{row[\"episode_id\"]}-ATTEMPT.json',dict(track=track,condition=condition,episode_id=row['episode_id'],prompt_identity=prompt['identity'],attempt=1))\n            try:\n                with torch.inference_mode():")
    source = source.replace("                if mask: assert mask.accepts(text)[0]", "                write(f'{track.upper()}-{condition}-{row[\"episode_id\"]}-RAW.json',dict(output=text,output_token_ids=ids,eos_terminated=eos))\n                if mask: assert mask.accepts(text)[0]")
    source = source.replace('            finally:\n                h1.remove()', "            except BaseException as exc:\n                write(f'{track.upper()}-{condition}-{row[\"episode_id\"]}-FAILURE.json',dict(runtime_error=str(exc),traceback=traceback.format_exc(),partial_token_ids=progress['token_ids'],partial_output=tokenizer.decode(progress['token_ids'],skip_special_tokens=False),retry=False))\n                raise\n            finally:\n                h1.remove()")
    ast.parse(source)
    return source


def freeze():
    assert not OUT.exists()
    receipt = baseline()
    OUT.mkdir()
    write('BASELINE-IDENTITY-VERIFICATION.json', receipt)
    for name in ('DIAGNOSTICS.json', 'GENERATION-CONFIGURATIONS.json'):
        (OUT / name).write_bytes((h.OUT / name).read_bytes())
    (OUT / 'EFFECTIVE-WORKER.py.txt').write_text(effective_worker(), encoding='utf-8', newline='\n')
    write('EXECUTION-MANIFEST.json', dict(round='R6.71',calls=54,ordering='base A/B/C then adapter A/B/C; N01 through N09 per condition',replications=1,training=False,raw_repair=False,scorer=str(ROOT/'experiments/incremental_scorer_r6_65/scorer.py'),conditions_sha256=f.sha(OUT/'GENERATION-CONFIGURATIONS.json'),diagnostics_sha256=f.sha(OUT/'DIAGNOSTICS.json')))
    write('SOURCE-FREEZE.json', dict(files={p.relative_to(ROOT).as_posix():f.sha(p) for p in HERE.glob('*.py')},inputs={p.name:f.sha(p) for p in OUT.iterdir()}))
    print('PASS baseline identities; fresh 54-call successor frozen', flush=True)


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
    namespace = dict(q.__dict__, OUT=OUT, write=write, check_freeze=check_freeze)
    exec(compile(source, str(OUT / 'EFFECTIVE-WORKER.py.txt'), 'exec'), namespace)
    namespace['worker'](track)


def execute():
    check_freeze()
    assert baseline() == f.read(OUT / 'BASELINE-IDENTITY-VERIFICATION.json')
    with (OUT / 'DISPATCH-CLAIM.json').open('x', encoding='utf-8') as stream:
        json.dump(dict(attempts=1,calls=54,training=False), stream)
    env = dict(os.environ,PYTHONDONTWRITEBYTECODE='1',HF_HUB_OFFLINE='1',HF_HUB_DISABLE_TELEMETRY='1',TOKENIZERS_PARALLELISM='false',HF_HOME=str(f.STORE/'hf-cache'))
    env.pop('CUDA_VISIBLE_DEVICES', None)
    try:
        for track in ('base','adapter'):
            args = [str(f.PYTHON), '-B', str(Path(__file__).resolve()), 'worker', track]
            start = time.perf_counter()
            try:
                proc = subprocess.run(args,cwd=ROOT,env=env,capture_output=True,text=True,timeout=3600)
            except subprocess.TimeoutExpired as exc:
                write(track.upper()+'-PROCESS.json',dict(timeout=True,seconds=time.perf_counter()-start,stdout=str(exc.stdout),stderr=str(exc.stderr)))
                raise
            write(track.upper()+'-PROCESS.json',dict(argv=args,returncode=proc.returncode,stdout=proc.stdout,stderr=proc.stderr,seconds=time.perf_counter()-start))
            print(proc.stdout,flush=True)
            assert proc.returncode == 0, proc.stderr
    except BaseException as exc:
        write('HALT.json',dict(error=str(exc),traceback=traceback.format_exc(),retry=False))
        raise


if __name__ == '__main__':
    {'freeze':freeze,'execute':execute,'worker':lambda:worker(sys.argv[2])}[sys.argv[1]]()
