"""Single bounded inference-only comparison, frozen before dispatch."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'experiments/incremental_training_r6_66'))
spec = importlib.util.spec_from_file_location('r668_frozen', ROOT / 'experiments/incremental_training_r6_66/run.py')
f = importlib.util.module_from_spec(spec)
spec.loader.exec_module(f)
OUT = ROOT / 'benchmark/results/phase6/r6_68'


def write(name, value):
    path = OUT / name
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n', encoding='utf-8', newline='\n')


def audit():
    result = dict(publications={name:f.publication(name) for name in ('r6_65','r6_66','r6_67')}, baseline=f.baseline())
    adapter = f.read(ROOT/'benchmark/results/phase6/r6_67/ADAPTER-IDENTITIES.json')
    assert f.file_manifest(Path(adapter['directory'])) == adapter['files']
    assert adapter['content_identity'] == '7fa3e7bfd5f99dd54caf700d53537c165a1193752d9820b3283423dfc9aef921'
    result['adapter'] = adapter
    result['r6_67_original_acceptance'] = dict(base=0, adapter=0, denominator=13, historical_rescoring=False)
    return result


def records():
    state, fixture = f.data.state, f.data.fixture
    def action(op, args, typ):
        return dict(id='selected',type=typ,deps=sorted({x['ref'] for x in args if 'ref' in x}),node=dict(op='value',expr={op:args}))
    def ref(name): return {'ref':name}
    def const(value): return {'const':value}
    prefix = [dict(id='raised',type='Int64',deps=['seed'],node=dict(op='value',expr={'add':[ref('seed'),const(4)]})),
              dict(id='twice',type='Int64',deps=['raised'],node=dict(op='value',expr={'add':[ref('raised'),ref('raised')]}))]
    tasks = [
        ('N01',state('FreshLiteralSum',[('flag','Bool'),('unused','Int64')],[7,-11],'Int64'),
         'Compute seven plus negative eleven, with seven first. Ignore both stored inputs.',action('add',[const(7),const(-11)],'Int64'),
         [fixture(dict(flag=False,unused=9),-4),fixture(dict(flag=True,unused=-100),-4)]),
        ('N02',state('FreshOffset',[('amount','Int64'),('offset','Int64'),('ready','Bool')],[6],'Int64'),
         'Add literal six on the left to amount on the right. The offset and ready fields are distractors.',action('add',[const(6),ref('amount')],'Int64'),
         [fixture(dict(amount=-8,offset=20,ready=True),-2),fixture(dict(amount=12,offset=-3,ready=False),18)]),
        ('N03',state('FreshChain',[('seed','Int64'),('noise','Int64')],[4,3],'Int64',prefix),
         'Add three to the previously constructed twice value: twice is the left operand. Use the end of the chain, not raised or seed.',action('add',[ref('twice'),const(3)],'Int64'),
         [fixture(dict(seed=1,noise=30),13),fixture(dict(seed=-5,noise=0),1)]),
        ('N04',state('FreshReverseBound',[('low','Int64'),('high','Int64'),('flag','Bool')],[],'Bool'),
         'Test whether high is no greater than low. high must be the left operand; low must be the right.',action('le',[ref('high'),ref('low')],'Bool'),
         [fixture(dict(low=2,high=9,flag=True),False),fixture(dict(low=9,high=2,flag=False),True),fixture(dict(low=3,high=3,flag=False),True)]),
        ('N05',state('FreshLiteralBound',[('reading','Int64'),('decoy','Int64')],[-2],'Bool'),
         'Return whether negative two is less than or equal to reading. Put the literal first, and do not use decoy.',action('le',[const(-2),ref('reading')],'Bool'),
         [fixture(dict(reading=-3,decoy=80),False),fixture(dict(reading=0,decoy=-80),True),fixture(dict(reading=-2,decoy=0),True)]),
        ('N06',state('FreshChainBound',[('seed','Int64'),('noise','Int64')],[4],'Bool',prefix),
         'Test whether raised is no greater than twice, using those two previous results in that order. Dependencies must be direct, not seed.',action('le',[ref('raised'),ref('twice')],'Bool'),
         [fixture(dict(seed=1,noise=30),True),fixture(dict(seed=-5,noise=0),False),fixture(dict(seed=-4,noise=2),True)]),
        ('N07',state('FreshBooleanEquality',[('enabled','Bool'),('count','Int64'),('other','Bool')],[True],'Bool'),
         'Compare enabled on the left with literal true on the right for equality. Do not compare count or other.',action('eq',[ref('enabled'),const(True)],'Bool'),
         [fixture(dict(enabled=True,count=1,other=False),True),fixture(dict(enabled=False,count=1,other=True),False)]),
        ('N08',state('FreshIntegerEquality',[('code','Int64'),('flag','Bool')],[0,False],'Bool'),
         'Compare literal integer zero on the left with code on the right for equality. Integer zero is not Boolean false; ignore flag.',action('eq',[const(0),ref('code')],'Bool'),
         [fixture(dict(code=0,flag=False),True),fixture(dict(code=1,flag=False),False),fixture(dict(code=-1,flag=True),False)]),
        ('N09',state('FreshSingleDependency',[('source','Bool'),('decoy','Bool'),('n','Int64')],[],'Bool',
                      [dict(id='saved',type='Bool',deps=['source'],node=dict(op='value',expr=ref('source')))]),
         'Check equality of saved with itself. Both ordered operands must name saved; list its one distinct direct dependency once. Ignore source and decoy.',action('eq',[ref('saved'),ref('saved')],'Bool'),
         [fixture(dict(source=False,decoy=True,n=8),True),fixture(dict(source=True,decoy=False,n=-8),True)]),
    ]
    return [f.old.make_record(eid,'fresh_diagnostic',before,req,gold,cases) for eid,before,req,gold,cases in tasks]


def freeze():
    assert not (OUT/'SOURCE-FREEZE.json').exists() and not (OUT/'DISPATCH-CLAIM.json').exists()
    baseline = audit()
    OUT.mkdir(exist_ok=True)
    write('PREFLIGHT.json',baseline)
    rows = records()
    training = f.read(ROOT/'benchmark/results/phase6/r6_66/DATASET.json')['records']
    assert all(row['prompt'] != old['prompt'] and row['before'] != old['before'] for row in rows for old in training)
    gold = [f.score(row['completion'][0]['content'], row) for row in rows]
    assert all(x['accepted'] for x in gold)
    write('DIAGNOSTICS.json',dict(records=rows,identities=[f.identity(r) for r in rows],independent=False,
          provenance='Coordinator-authored prospective variation after reading R6.67 findings and R6.64 task construction; no model-output selection',
          exact_training_records_reused=False,reserved_unit_shared_diamond_family=False,training_dataset_expansion=0))
    write('GOLD-QUALIFICATION.json',dict(records=gold,scorer_sha256=f.sha(ROOT/'experiments/incremental_scorer_r6_65/scorer.py')))
    from transformers import AutoTokenizer
    import transformers, regex
    from decoder import StructuralMask
    tokenizer=AutoTokenizer.from_pretrained(f.STORE/'checkpoint',local_files_only=True,trust_remote_code=False)
    def validate(text): f.successor.validate_action(f.successor.c.load(text))
    mask=StructuralMask(tokenizer,0,validate)
    controls=[]
    for op in ('add','le','eq'):
        for typ in ('Int64','Bool'):
            for operands in ([{'ref':'arbitrary_name'},{'const':True}],[{'const':-8},{'const':None}]):
                candidate=dict(id='selected',type=typ,deps=['not_in_any_scope'],node=dict(op='value',expr={op:operands}))
                text=json.dumps(candidate,separators=(',',':'))
                assert mask.accepts(text)==(True,True)
                assert all(mask.accepts(text[:i])[0] for i in range(len(text)+1))
                ids=tokenizer(text,add_special_tokens=False)['input_ids']
                pieces=dict(mask.pieces)
                assert ''.join(pieces[i] for i in ids)==tokenizer.decode(ids,skip_special_tokens=False)==text
                controls.append(dict(action=candidate,pass_all_prefixes=True,ascii_token_concatenation=True))
    negatives=['```json\n{}\n```','{}','{"id":"other"}',
               '{"id":"selected","type":"Unit","deps":[],"node":{"op":"value","expr":{"sub":[{"const":1},{"const":2}]}}}']
    assert all(not mask.accepts(x)[0] for x in negatives)
    probes={name:importlib.util.find_spec(name) is not None for name in ('outlines','lmformatenforcer','xgrammar','guidance','jsonschema')}
    write('GENERATION-INTERFACE.json',dict(transformers=transformers.__version__,regex=regex.__version__,packages=probes,
          standard_generation=True,explicit_instruction=True,native_grammar_api=False,native_json_schema_api=False,
          experiment_local_grammar='Transformers LogitsProcessor + regex partial fullmatch; terminal R6.65 structural checker',
          constraints='ASCII compact JSON, fixed envelope key order id/type/deps/node and op/expr, selected/value constants, Int64|Bool, add|le|eq, two ref|const operands, max two unique dependency strings, Int64|Bool|null literals. JSON strings permit escapes. No scope membership, operation/type correspondence, dependency correctness, or task answer enforcement.',
          limitations='Structural subset excludes alternative object key ordering, whitespace and raw non-ASCII; escaped Unicode permitted. Integer range and decoded dependency uniqueness checked at completed actions. No guarantee against budget exhaustion or prefix dead ends.',
          controls=controls,negative_controls=negatives,setup_seconds=mask.setup_seconds,model_calls=0,new_dependencies=0))
    config=f.read(ROOT/'benchmark/results/phase6/r6_66/DIAGNOSTIC-PROTOCOL.json')
    prompts={}
    for condition in 'ABC':
        prompts[condition]=[]
        for row in rows:
            prompt=copy.deepcopy(row['prompt'])
            if condition=='B':
                prompt[-1]['content']+='\nOutput only the raw JSON action. Do not use Markdown fences, commentary, explanations, or text before or after the JSON object.'
            # C uses identical prompts to A. The mask never sees the requirement, scope or gold.
            ids=tokenizer.apply_chat_template(prompt,tokenize=True,add_generation_prompt=True)
            assert len(ids)+128<=2048
            prompts[condition].append(dict(episode_id=row['episode_id'],messages=prompt,identity=f.identity(prompt),input_tokens=len(ids)))
    write('GENERATION-CONFIGURATIONS.json',dict(inherited=config,conditions=dict(A='unchanged R6.67 prompts/procedure, new tasks',B='A plus raw-JSON instruction',C='A plus structural token mask'),prompts=prompts,
          ordering='base A/B/C then adapter A/B/C; N01 through N09 per condition',replications=1,calls=54,
          limits=dict(per_generation_seconds=120,process_seconds=3600,max_reserved_bytes=8589934592,minimum_free_bytes=1610612736),
          raw_handling='Decode all generated IDs verbatim; strip only terminal EOS exactly as R6.67. No repair or normalization.',
          classification_rule='Adapter accepted-count advantage over base in any matched condition -> semantic-action learning observed; otherwise a B/C structural advantage -> structured generation only; otherwise no observed advantage. Unavailable C -> interface gap; integrity/runtime protocol blocker -> halt. Small exploratory set only.'))
    write('SOURCE-FREEZE.json',dict(files={p.relative_to(ROOT).as_posix():f.sha(p) for p in list(HERE.glob('*.py'))+[ROOT/'benchmark/results/phase6/R6_68-PROTOCOL.md']},
          inputs={p.name:f.sha(p) for p in OUT.glob('*.json')}))
    print('PASS freeze: nine fresh tasks, 54 calls; grammar qualification has zero model calls')


def check_freeze():
    frozen=f.read(OUT/'SOURCE-FREEZE.json')
    for path,digest in frozen['files'].items(): assert f.sha(ROOT/path)==digest,path
    for name,digest in frozen['inputs'].items(): assert f.sha(OUT/name)==digest,name


def worker(track):
    check_freeze()
    import torch
    from transformers import AutoTokenizer,GenerationConfig,LogitsProcessorList,StoppingCriteria,StoppingCriteriaList
    from decoder import StructuralMask
    precision=f.read(ROOT/'benchmark/results/phase6/r6_66/TRAINING-CONFIGURATION.json')['configuration']['precision_runtime']
    torch.backends.cuda.matmul.allow_tf32=precision['allow_tf32_matmul']
    torch.backends.cudnn.allow_tf32=precision['allow_tf32_cudnn']
    torch.set_float32_matmul_precision(precision['float32_matmul_precision'])
    torch.use_deterministic_algorithms(precision['deterministic_algorithms'])
    f.q52.seed()
    from peft import prepare_model_for_kbit_training,PeftModel
    started=time.perf_counter()
    model,quant=f.q52.load_base()
    model=prepare_model_for_kbit_training(model,use_gradient_checkpointing=True,gradient_checkpointing_kwargs={'use_reentrant':False})
    if track=='adapter': model=PeftModel.from_pretrained(model,f.ARTIFACTS/'step20/adapter',is_trainable=False,local_files_only=True)
    model.eval()
    for parameter in model.parameters(): parameter.requires_grad_(False)
    load_seconds=time.perf_counter()-started
    # Read-only manifests before/after prove no inference-side tensor update.
    source=(ROOT/'benchmark/results/phase6/r6_66/EFFECTIVE-WORKER.py.txt').read_text(encoding='utf-8')
    import ast
    nodes=[n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name in ('tensor_record','base_manifest','adapter_manifest')]
    ns={}
    exec(compile(ast.Module(body=nodes,type_ignores=[]),'frozen-readonly-manifest','exec'),ns)
    before=ns['base_manifest'](model)
    adapter_before=ns['adapter_manifest'](model)
    assert before==f.read(ROOT/'benchmark/results/phase6/r6_67/INITIAL-PARAMETERS.json')['base']
    if track=='adapter': assert adapter_before==f.read(ROOT/'benchmark/results/phase6/r6_67/TRAINING-RESULT.json')['trained_adapter_tensors']
    tokenizer=AutoTokenizer.from_pretrained(f.STORE/'checkpoint',local_files_only=True,trust_remote_code=False)
    configuration=f.read(OUT/'GENERATION-CONFIGURATIONS.json')
    generation=GenerationConfig.from_dict(configuration['inherited']['resolved_generation_configuration'])
    rows=f.read(OUT/'DIAGNOSTICS.json')['records']
    entries=[]
    class Limit(StoppingCriteria):
        def __init__(self,start): self.start=start
        def __call__(self,input_ids,scores,**kwargs):
            free,_=torch.cuda.mem_get_info()
            assert time.perf_counter()-self.start<=120,'GENERATION_TIMEOUT'
            assert torch.cuda.max_memory_reserved()<=8589934592 and free>=1610612736,'VRAM_LIMIT'
            return False
    for condition in 'ABC':
        for row,prompt in zip(rows,configuration['prompts'][condition]):
            x=tokenizer(tokenizer.apply_chat_template(prompt['messages'],tokenize=False,add_generation_prompt=True),add_special_tokens=False,return_tensors='pt').to('cuda')
            assert x.input_ids.shape[1]==prompt['input_tokens']
            mask=StructuralMask(tokenizer,x.input_ids.shape[1],lambda text:f.successor.validate_action(f.successor.c.load(text))) if condition=='C' else None
            torch.cuda.empty_cache()
            torch.cuda.reset_peak_memory_stats()
            torch.cuda.synchronize()
            begin=time.perf_counter()
            forward=[0.0,0]
            def pre(module,args):
                torch.cuda.synchronize()
                forward[1]=time.perf_counter()
            def post(module,args,output):
                torch.cuda.synchronize()
                forward[0]+=time.perf_counter()-forward[1]
            h1=model.register_forward_pre_hook(pre)
            h2=model.register_forward_hook(post)
            try:
                with torch.inference_mode():
                    generated=model.generate(**x,generation_config=generation,use_cache=False,
                        logits_processor=LogitsProcessorList([mask] if mask else []),
                        stopping_criteria=StoppingCriteriaList([Limit(begin)]))
                torch.cuda.synchronize()
                seconds=time.perf_counter()-begin
                ids=generated[0,x.input_ids.shape[1]:].cpu().tolist()
                eos=bool(ids and ids[-1] in generation.eos_token_id)
                text=tokenizer.decode(ids[:-1] if eos else ids,skip_special_tokens=False)
                if mask: assert mask.accepts(text)[0]
                scoring_begin=time.perf_counter()
                scores=f.score(text,row)
                scoring_seconds=time.perf_counter()-scoring_begin
                entry=dict(track=track,condition=condition,episode_id=row['episode_id'],prompt_identity=prompt['identity'],
                    output=text,output_token_ids=ids,output_tokens=len(ids),eos_terminated=eos,truncated=not eos and len(ids)==128,
                    inference_seconds=seconds,model_forward_seconds=forward[0],
                    constraint_seconds=mask.seconds if mask else 0,decoder_setup_seconds=mask.setup_seconds if mask else 0,
                    generation_other_seconds=seconds-forward[0]-(mask.seconds if mask else 0),
                    constraint_calls=mask.calls if mask else 0,allowed_counts=mask.allowed_counts if mask else [],
                    peak_allocated_bytes=torch.cuda.max_memory_allocated(),peak_reserved_bytes=torch.cuda.max_memory_reserved(),
                    scores=scores,scoring_seconds=scoring_seconds,runtime_error=None)
                if scores['schema_valid']:
                    a=f.successor.c.load(text)
                    t=time.perf_counter()
                    try:
                        f.successor.validate_action(a)
                        entry['validation_seconds']=time.perf_counter()-t
                        t=time.perf_counter()
                        f.successor.assembly.apply(row['before'],a)
                        entry['assembly_seconds']=time.perf_counter()-t
                    except Exception as exc:
                        entry['assembly_seconds']=time.perf_counter()-t
                        entry['timing_diagnostic']=str(exc)
                entries.append(entry)
                write(f'{track.upper()}-{condition}-{row["episode_id"]}.json',entry)
                print(track,condition,row['episode_id'],scores['schema_valid'],scores['accepted'],flush=True)
                del generated
            finally:
                h1.remove(); h2.remove()
                del x
    assert ns['base_manifest'](model)==before
    assert ns['adapter_manifest'](model)==adapter_before
    write(track.upper()+'-RESULTS.json',dict(status='PASS',records=entries,model_load_seconds=load_seconds,quantization=quant,
          base_tensor_identity=f.identity(before),adapter_tensor_identity=f.identity(adapter_before),parameters_unchanged=True))


def execute():
    check_freeze()
    with (OUT/'DISPATCH-CLAIM.json').open('x',encoding='utf-8') as stream:
        json.dump(dict(attempts=1,training=False,calls=54),stream)
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',HF_HUB_OFFLINE='1',HF_HUB_DISABLE_TELEMETRY='1',TOKENIZERS_PARALLELISM='false',HF_HOME=str(f.STORE/'hf-cache'))
    env.pop('CUDA_VISIBLE_DEVICES',None)
    try:
        for track in ('base','adapter'):
            args=[str(f.PYTHON),'-B',str(Path(__file__).resolve()),'worker',track]
            start=time.perf_counter()
            proc=subprocess.run(args,cwd=ROOT,env=env,capture_output=True,text=True,timeout=3600)
            write(track.upper()+'-PROCESS.json',dict(argv=args,returncode=proc.returncode,stdout=proc.stdout,stderr=proc.stderr,seconds=time.perf_counter()-start))
            print(proc.stdout,flush=True)
            assert proc.returncode==0,proc.stderr
    except BaseException as exc:
        write('HALT.json',dict(error=str(exc),traceback=traceback.format_exc(),retry=False))
        raise


if __name__=='__main__':
    if sys.argv[1]=='freeze': freeze()
    elif sys.argv[1]=='execute': execute()
    elif sys.argv[1]=='worker': worker(sys.argv[2])
    else: raise ValueError(sys.argv[1])
