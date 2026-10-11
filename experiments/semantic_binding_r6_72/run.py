"""R6.72 inference-only diagnostic through unchanged qualified interfaces."""
import ast
import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import traceback
from tasks import specifications
from timing import forward_timer, neutral_cpu_control

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = ROOT / 'benchmark/results/phase6/r6_72'
spec = importlib.util.spec_from_file_location('r672_prior', ROOT/'experiments/semantic_learning_r6_71/run.py')
prior = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prior)
f, q = prior.f, prior.q


def write(name, value):
    (OUT/name).write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False)+'\n', encoding='utf-8', newline='\n')


def baseline():
    prior.check_freeze()
    return dict(inherited=prior.baseline(), r6_71=f.publication('r6_71'))


def effective_worker():
    source = (prior.OUT/'EFFECTIVE-WORKER.py.txt').read_text(encoding='utf-8')
    start = source.index('            forward=[0.0,0]')
    end = source.index('            progress=dict', start)
    source = source[:start] + "            timer=forward_timer(model,torch.cuda.synchronize)\n            forward=timer.__enter__()\n" + source[end:]
    source = source.replace("for condition in 'ABC':", "for condition in 'C':")
    source = source.replace("model_forward_seconds=forward[0]", "model_forward_seconds=forward['seconds'],model_forward_calls=forward['calls'],forward_timer_target=forward['target']")
    source = source.replace("seconds-forward[0]", "seconds-forward['seconds']")
    source = source.replace('h1.remove(); h2.remove()', 'timer.__exit__(None,None,None)')
    source = source.replace('    entries=[]', "    if QUALIFY:\n        neutral_gpu_controls(model,tokenizer,generation,track)\n        assert ns['base_manifest'](model)==before\n        assert ns['adapter_manifest'](model)==adapter_before\n        return\n    entries=[]")
    ast.parse(source)
    return source


def neutral_gpu_controls(model, tokenizer, generation, track):
    import torch
    from transformers import GenerationConfig
    config = copy.deepcopy(generation)
    config.max_new_tokens = 4
    prompt = tokenizer.apply_chat_template([dict(role='user',content='Reply with the word OK.')],tokenize=False,add_generation_prompt=True)
    x = tokenizer(prompt,add_special_tokens=False,return_tensors='pt').to('cuda')
    calls = []
    for timed in (False, True):
        f.q52.seed()
        torch.cuda.synchronize()
        begin = time.perf_counter()
        timer = forward_timer(model,torch.cuda.synchronize) if timed else None
        measure = timer.__enter__() if timer else None
        try:
            with torch.inference_mode():
                generated = model.generate(**x,generation_config=config,use_cache=False)
            torch.cuda.synchronize()
            elapsed = time.perf_counter()-begin
            ids = generated[0,x.input_ids.shape[1]:].cpu().tolist()
            calls.append(dict(timed=timed,ids=ids,wall_seconds=elapsed,forward=measure))
        finally:
            if timer: timer.__exit__(None,None,None)
    write(track.upper()+'-TIMING-CONTROLS.json',dict(calls=calls,outputs_identical=calls[0]['ids']==calls[1]['ids'],hooks_added=0,parameters_frozen=True))
    assert calls[0]['ids']==calls[1]['ids'], 'TIMER_OUTPUT_DRIFT'
    assert 0 < measure['seconds'] <= calls[1]['wall_seconds'] and measure['calls']==len(ids)
    assert 'forward' not in (model.get_base_model() if hasattr(model,'get_base_model') else model).__dict__


def freeze():
    assert not (OUT/'SOURCE-FREEZE.json').exists()
    receipt = baseline()
    write('BASELINE-IDENTITY-VERIFICATION.json',receipt)
    write('CPU-TIMING-CONTROL.json',neutral_cpu_control())
    tasks = specifications(f)
    rows = [f.old.make_record(eid,'semantic_binding_diagnostic',before,requirement,gold,cases) for eid,before,requirement,gold,cases in tasks]
    training = f.read(ROOT/'benchmark/results/phase6/r6_66/DATASET.json')['records']
    assert all(row['prompt']!=old['prompt'] and row['before']!=old['before'] for row in rows for old in training)
    scores = [f.score(row['completion'][0]['content'],row) for row in rows]
    assert all(s['accepted'] for s in scores)
    rejections = []
    for label,index,change in [
        ('Bool_as_Int64',1,lambda a:a['node']['expr']['add'].__setitem__(1,{'ref':'ready'})),
        ('mixed_eq_types',9,lambda a:a['node']['expr']['eq'].__setitem__(0,{'const':False})),
        ('unknown_reference',0,lambda a:a['node']['expr']['add'].__setitem__(0,{'ref':'missing'})),
        ('unavailable_literal',0,lambda a:a['node']['expr']['add'].__setitem__(0,{'const':99})),
        ('indirect_dependency',2,lambda a:a['deps'].append('raw')),
        ('missing_dependency',6,lambda a:a.__setitem__('deps',['adjusted'])),
        ('duplicate_dependency',10,lambda a:a['deps'].append('snapshot')),
        ('wrong_result_type',4,lambda a:a.__setitem__('type','Int64'))]:
        action=copy.deepcopy(tasks[index][3])
        change(action)
        try:
            f.successor.assembly.apply(tasks[index][1],action)
        except f.successor.c.Diagnostic as exc:
            rejections.append(dict(name=label,action=action,error=exc.data,rejected=True))
        else:
            raise AssertionError(label)
    write('BINDING-REJECTION-CONTROLS.json',dict(passed=True,records=rejections,semantics_unchanged=True))
    # Expectations and behavior fixtures never enter the model prompt or decoder.
    write('REQUIREMENTS.json',dict(records=[dict(episode_id=eid,before=before,requirement=req) for eid,before,req,_,_ in tasks],counts=dict(add=4,le=4,eq=4),exact_training_reuse=False))
    write('SEMANTIC-EXPECTATIONS.json',dict(records=[dict(episode_id=eid,action=gold,cases=cases) for eid,_,_,gold,cases in tasks],review='coordinator-reviewed; distinct same-platform nonblind consistency review, independence unattested',gold_scores=scores,fixture_observations=sum(len(s['observations']) for s in scores)))
    write('DIAGNOSTICS.json',dict(records=rows,independent=False,training_dataset_expansion=0))
    from transformers import AutoTokenizer
    from decoder import StructuralMask
    tokenizer = AutoTokenizer.from_pretrained(f.STORE/'checkpoint',local_files_only=True,trust_remote_code=False)
    mask = StructuralMask(tokenizer,0,lambda text:f.successor.validate_action(f.successor.c.load(text)))
    controls = []
    for op in ('add','le','eq'):
        for typ in ('Int64','Bool'):
            action = dict(id='selected',type=typ,deps=['arbitrary_unknown'],node=dict(op='value',expr={op:[{'ref':'arbitrary_unknown'},{'const':True}]}))
            text = json.dumps(action,separators=(',',':'))
            assert mask.accepts(text)==(True,True)
            assert all(mask.accepts(text[:i])[0] for i in range(len(text)+1))
            controls.append(dict(action=action,admitted=True))
    write('DECODER-CONTROLS.json',dict(passed=True,grammar_sha256=f.sha(ROOT/'experiments/structured_generation_r6_68/decoder.py'),arbitrary_semantically_invalid_alternatives=controls,task_answers_in_grammar=False))
    configuration = copy.deepcopy(f.read(prior.OUT/'GENERATION-CONFIGURATIONS.json'))
    prompts = []
    for row in rows:
        ids = tokenizer.apply_chat_template(row['prompt'],tokenize=True,add_generation_prompt=True)
        assert len(ids)+128<=2048
        prompts.append(dict(episode_id=row['episode_id'],messages=row['prompt'],identity=f.identity(row['prompt']),input_tokens=len(ids)))
    configuration.update(prompts=dict(C=prompts),conditions=dict(C='unchanged qualified structural mask'),calls=24,ordering='base S01-S12 then adapter S01-S12',replications=1)
    write('GENERATION-CONFIGURATIONS.json',configuration)
    (OUT/'EFFECTIVE-WORKER.py.txt').write_text(effective_worker(),encoding='utf-8',newline='\n')
    write('SOURCE-FREEZE.json',dict(files={p.relative_to(ROOT).as_posix():f.sha(p) for p in list(HERE.glob('*.py'))+[ROOT/'benchmark/results/phase6/R6_72-PROTOCOL.md']},inputs={p.name:f.sha(p) for p in OUT.iterdir() if p.name!='SOURCE-FREEZE.json'}))
    print('PASS baseline, 12 balanced gold actions/28 fixtures, CPU timing and decoder controls; frozen before inference')


def check_freeze():
    seal = f.read(OUT/'SOURCE-FREEZE.json')
    for path,digest in seal['files'].items(): assert f.sha(ROOT/path)==digest,path
    for name,digest in seal['inputs'].items(): assert f.sha(OUT/name)==digest,name


def worker(track, qualify):
    check_freeze()
    namespace = dict(q.__dict__,OUT=OUT,write=write,check_freeze=check_freeze,forward_timer=forward_timer,neutral_gpu_controls=neutral_gpu_controls,QUALIFY=qualify)
    exec(compile((OUT/'EFFECTIVE-WORKER.py.txt').read_text(encoding='utf-8'),'r672-frozen-worker','exec'),namespace)
    namespace['worker'](track)


def dispatch(qualify):
    check_freeze()
    assert baseline()==f.read(OUT/'BASELINE-IDENTITY-VERIFICATION.json')
    label = 'QUALIFICATION' if qualify else 'DIAGNOSTIC'
    if not qualify:
        for track in ('BASE','ADAPTER'):
            assert f.read(OUT/(track+'-TIMING-CONTROLS.json'))['outputs_identical']
            assert f.read(OUT/(track+'-QUALIFICATION-PROCESS.json'))['returncode']==0
    with (OUT/(label+'-DISPATCH.json')).open('x',encoding='utf-8') as stream:
        json.dump(dict(attempts=1,calls=4 if qualify else 24,training=False),stream)
    env = dict(os.environ,PYTHONDONTWRITEBYTECODE='1',HF_HUB_OFFLINE='1',HF_HUB_DISABLE_TELEMETRY='1',TOKENIZERS_PARALLELISM='false',HF_HOME=str(f.STORE/'hf-cache'))
    env.pop('CUDA_VISIBLE_DEVICES',None)
    try:
        for track in ('base','adapter'):
            args = [str(f.PYTHON),'-B',str(Path(__file__).resolve()),'worker',track,'qualify' if qualify else 'diagnostic']
            start = time.perf_counter()
            proc = subprocess.run(args,cwd=ROOT,env=env,capture_output=True,text=True,timeout=3600)
            write(track.upper()+'-'+label+'-PROCESS.json',dict(returncode=proc.returncode,stdout=proc.stdout,stderr=proc.stderr,seconds=time.perf_counter()-start))
            print(proc.stdout,flush=True)
            assert proc.returncode==0,proc.stderr
    except BaseException as exc:
        write(label+'-HALT.json',dict(error=str(exc),traceback=traceback.format_exc(),retry=False))
        raise


if __name__=='__main__':
    {'freeze':freeze,'qualify':lambda:dispatch(True),'execute':lambda:dispatch(False),'worker':lambda:worker(sys.argv[2],sys.argv[3]=='qualify')}[sys.argv[1]]()
