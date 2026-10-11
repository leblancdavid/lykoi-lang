"""One bounded B-only experiment; immutable historical helpers and offline assets."""
import ast
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = ROOT / 'benchmark/results/phase6/r6_64'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


old = load('r664_old', 'experiments/lora_smoke_r6_59/run.py')
c = old.c
STORE, PYTHON, q52 = old.STORE, old.PYTHON, old.q52
ARTIFACTS = STORE / 'r6-64'
canonical, file_manifest, identity, read, sha = old.canonical, old.file_manifest, old.identity, old.read, old.sha
sys.path.insert(0, str(ROOT / 'experiments/incremental_data_r6_63'))
import freeze as data
import assembly
LOCK = threading.RLock()


def write(name, value):
    with LOCK:
        OUT.mkdir(parents=True, exist_ok=True)
        p = OUT / name
        temp = p.with_suffix(p.suffix + '.pending')
        temp.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n', encoding='utf-8', newline='\n')
        temp.replace(p)


def baseline():
    inherited = data.baseline()
    assert inherited == read(data.OUT / 'BASELINE.json')
    manifest = read(data.OUT / 'PUBLICATION-IDENTITIES.json')
    for name, entry in manifest['files'].items():
        assert sha(ROOT / name) == entry['sha256'], name
    assert sha(data.OUT / 'PUBLICATION-IDENTITIES.json') == read(data.OUT / 'VERIFICATION.json')['manifest_sha256']
    executable = read(old.OUT / 'EXECUTABLE-IDENTITY-SUPPLEMENT.json')
    home = STORE / 'python/cpython-3.12.11-windows-x86_64-none'
    paths = dict(python_executable_sha256=home/'python.exe', python_dll_sha256=home/'python312.dll',
                 venv_executable_sha256=PYTHON, uv_executable_sha256=STORE/'uv/uv.exe',
                 requirements_lock_sha256=ROOT/'benchmark/results/phase6/r6_52/requirements-lock.txt')
    assert {key:sha(path) for key,path in paths.items()} == executable['identities']
    return dict(inherited=inherited, r6_63_publication_sha256=sha(data.OUT / 'PUBLICATION-IDENTITIES.json'),
                r6_63_files=len(manifest['files']), executable_supplement=executable, kernel_constructs=26)


def rows():
    return read(OUT / 'DATASET.json')['records']


def score(text, row):
    result = dict(strict_serialization=False, schema_valid=False, operation_correct=False,
                  operands_correct=False, result_type_correct=False, dependencies_correct=False,
                  deterministic_assembly=False, behavioral_acceptance=False, exact_target_reproduction=False,
                  repair_count=0, observations=[])
    try:
        action = data.c.load(text)
        result['strict_serialization'] = type(action) is dict
        if not result['strict_serialization']:
            return result
        import jsonschema
        jsonschema.validate(action, read(data.OUT / 'step-1.schema.json'))
        result['schema_valid'] = True
        gold = data.c.load(row['completion'][0]['content'])
        expr, expected = action['node']['expr'], gold['node']['expr']
        result.update(operation_correct=list(expr) == list(expected),
                      operands_correct=canonical(next(iter(expr.values()))) == canonical(next(iter(expected.values()))),
                      result_type_correct=action['type'] == gold['type'],
                      dependencies_correct=action['deps'] == gold['deps'],
                      exact_target_reproduction=canonical(action) == canonical(gold))
        after, validation = assembly.apply(row['before'], action)
        again, again_validation = assembly.apply(data.c.load(data.c.canonical(row['before'])), data.c.load(text))
        result['deterministic_assembly'] = after == again and validation == again_validation
        for fixture in row['cases']:
            actual = assembly.behavior(after, fixture['arguments'])
            result['observations'].append(dict(actual=actual, expected=fixture['expected'],
                                               passed=assembly.agrees(actual, fixture['expected'])))
        result['behavioral_acceptance'] = all(x['passed'] for x in result['observations'])
    except Exception as exc:
        result['error'] = str(exc)
    return result


def make_record(eid, group, before, requirement, action, cases):
    skill = (data.OUT / 'SKILL-1.md').read_text(encoding='utf-8')
    schema = (data.OUT / 'step-1.schema.json').read_text(encoding='utf-8')
    system = ('Return exactly one B incremental action as a JSON object, without markdown or explanation. '
              'Use the following fixed skill and schema. Only the selected step is requested.\n' + skill + '\n' + schema)
    user = canonical(dict(requirement=requirement, before_state=before,
                          instruction='Select one add/le/eq value step with two ordered direct references or available literals, correct type and exact sorted distinct direct dependencies.')).decode()
    return dict(episode_id=eid, group=group, before=before, cases=cases,
                prompt=[dict(role='system', content=system), dict(role='user', content=user)],
                completion=[dict(role='assistant', content=canonical(action).decode())])


def freeze():
    assert not OUT.exists() and not ARTIFACTS.exists()
    b = baseline()
    write('BASELINE.json', b)
    records, entries = [], []
    for i in range(1, 11):
        folder = data.OUT / 'episodes' / f'D{i:02d}'
        envelope = read(folder / 'B-RECORD-2.json')
        action = read(folder / 'ACTION.json')
        assert canonical(action).decode() == envelope['target']['text']
        records.append(make_record(f'R6.63/D{i:02d}', 'training_record', read(folder / 'BEFORE.json'),
                                  read(folder / 'SOURCE.json')['requirement'], action, read(folder / 'ACCEPTANCE.json')['cases']))
        entries.append(dict(episode=f'D{i:02d}', provenance=envelope['provenance']['class'],
                            files={p.relative_to(ROOT).as_posix(): dict(sha256=sha(p), bytes=p.stat().st_size)
                                   for p in sorted(folder.glob('*.json'))}))
    write('DATASET-IDENTITIES.json', dict(records=entries, operations=dict(add=4, le=3, eq=3),
                                        training_examples=10, variants=0, objective='B'))
    write('DATASET.json', dict(records=records, targets='exact R6.63 ACTION bytes in canonical serialization',
                               context_convention='full pinned skill/schema plus requirement and immutable before state'))
    # Diagnostics are coordinator-authored, exposed, never sampled for training.
    def action(op, args, typ, deps):
        return dict(id='selected', type=typ, deps=deps, node=dict(op='value', expr={op: args}))
    varied = [
        make_record('V01', 'structurally_varied', data.state('FixedSum', [('unused','Bool')], [2,-3], 'Int64'),
                    'Add literal two to literal negative three, in that order. The stored flag is irrelevant.',
                    action('add', [{'const':2},{'const':-3}], 'Int64', []),
                    [data.fixture(dict(unused=False),-1),data.fixture(dict(unused=True),-1)]),
        make_record('V02', 'structurally_varied', data.state('SelfLimit', [('quantity','Int64'),('decoy','Int64')], [], 'Bool'),
                    'Report whether quantity is no greater than itself. Use quantity in both operand positions; ignore decoy.',
                    action('le', [{'ref':'quantity'},{'ref':'quantity'}], 'Bool', ['quantity']),
                    [data.fixture(dict(quantity=-9,decoy=20),True),data.fixture(dict(quantity=9223372036854775807,decoy=-1),True)]),
        make_record('V03', 'structurally_varied', data.state('PriorFlag', [('flag','Bool'),('noise','Int64')], [False], 'Bool',
                    [dict(id='cached',type='Bool',deps=['flag'],node=dict(op='value',expr={'ref':'flag'}))]),
                    'Compare literal false on the left with the previously constructed cached Boolean on the right. Use cached rather than the original flag.',
                    action('eq', [{'const':False},{'ref':'cached'}], 'Bool', ['cached']),
                    [data.fixture(dict(flag=False,noise=0),True),data.fixture(dict(flag=True,noise=1),False)])]
    diagnostics = records + varied
    for row in diagnostics:
        scores = score(row['completion'][0]['content'], row)
        assert all(scores[k] for k in ('strict_serialization','schema_valid','operation_correct','operands_correct',
                                      'result_type_correct','dependencies_correct','deterministic_assembly','behavioral_acceptance'))
    write('DIAGNOSTICS.json', dict(records=diagnostics, independent=False, reserved_family_used=False,
                                   expected='all eight scoring dimensions pass for each gold action; improvements measured separately by group'))
    from transformers import AutoTokenizer, GenerationConfig
    tokenizer = AutoTokenizer.from_pretrained(STORE / 'checkpoint', local_files_only=True, trust_remote_code=False)
    tokens = []
    for row in diagnostics:
        ids, labels, measurement = q52.encoded(row, tokenizer)
        assert len(ids) <= 2048 and measurement['prompt_tokens'] + 128 <= 2048
        tokens.append(dict(measurement, input_identity=identity(ids), labels_identity=identity(labels)))
    write('TOKENIZATION.json', dict(records=tokens, mask='prompt/post-EOS newline/padding ignored; completion plus one EOS; causal mean per record /4'))
    config = copy.deepcopy(read(old.OUT / 'TRAINING-CONFIGURATION.json')['configuration'])
    config.update(round='R6.64', training_episodes=[r['episode_id'] for r in records],
                  training_record_sampling_order='D01-D10 cyclic, eight complete cycles, no shuffle',
                  diagnostic_protocol_identity=None, sampling_identity=None)
    sequence = [dict(episode_id=records[i % 10]['episode_id'], presentation=i+1,
                     optimizer_step=i//4+1, microbatch_in_step=i%4+1) for i in range(80)]
    sampling = dict(sequence=sequence, cycle=[r['episode_id'] for r in records], presentations=80,
                    counts={r['episode_id']:8 for r in records}, shuffle=False)
    write('SAMPLING.json', sampling)
    generation = GenerationConfig(do_sample=False, num_beams=1, max_new_tokens=128, repetition_penalty=1.1,
                                  eos_token_id=[tokenizer.eos_token_id], pad_token_id=tokenizer.pad_token_id,
                                  bos_token_id=tokenizer.bos_token_id, use_cache=False)
    protocol = dict(resolved_generation_configuration=generation.to_dict(), process_timeout_seconds=1800,
                    per_generation_timeout_seconds=120, raw_output_repair=False, eos_only=True,
                    teacher_forced_evaluation='dropout off, identical completion+EOS labels, mean per record')
    write('DIAGNOSTIC-PROTOCOL.json', protocol)
    config.update(sampling_identity=identity(sampling), diagnostic_protocol_identity=identity(protocol))
    write('TRAINING-CONFIGURATION.json', dict(configuration=config, canonical_sha256=identity(config)))
    for name in ('LOSS-NORMALIZATION.json','OPTIMIZER-CONFIGURATION.json','CACHE-RELEASE-QUALIFICATION.json'):
        write(name, dict(inherited_from=f'r6_59/{name}', sha256=sha(old.OUT/name), evidence=read(old.OUT/name)))
    write('LEARNING-RATE-SCHEDULE.json', read(ROOT/'benchmark/results/phase6/r6_54/LEARNING-RATE-SCHEDULE.json'))
    worker = load('r664_worker_source', 'experiments/incremental_training_r6_64/worker.py')
    source = worker.effective_source()
    compile(source, 'R6.64-effective-worker', 'exec')
    (OUT/'EFFECTIVE-WORKER.py.txt').write_text(source, encoding='utf-8', newline='\n')
    paths = list(OUT.glob('*')) + list(HERE.glob('*.py')) + [ROOT/'benchmark/results/phase6/R6_64-PROTOCOL.md']
    write('PREFLIGHT.json', dict(status='PASS', training_configuration_identity=identity(config),
          frozen_payloads={p.relative_to(ROOT).as_posix():sha(p) for p in sorted(paths)},
          optimizer_updates_planned=20, initialization='original base plus seed651 fresh rank8 adapter; require exact R6.52 initial tensors',
          unresolved_training_critical_settings=[], attempts_authorized=1))
    print('PASS baseline, ten exact B targets, three exposed structural diagnostics, masks and configuration frozen')


def frozen_check():
    freeze = read(OUT/'PREFLIGHT.json')
    for path, digest in freeze['frozen_payloads'].items():
        assert sha(ROOT/path) == digest, path
    return freeze


def dispatch(mode):
    frozen_check()
    assert baseline() == read(OUT/'BASELINE.json')
    if mode == 'train':
        assert read(OUT/'DIAGNOSTIC-BASE.json')['status'] == 'PASS'
    if mode in ('reload','adapter'):
        assert read(OUT/'TRAINING-RESULT.json')['status'] == 'PASS'
    if mode == 'adapter':
        assert read(OUT/'ADAPTER-RELOAD.json')['status'] == 'PASS'
    with (OUT/f'{mode.upper()}-DISPATCH-CLAIM.json').open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(dict(mode=mode, attempts=1))+'\n')
    ARTIFACTS.mkdir(exist_ok=True)
    args=[str(PYTHON),str(HERE/'worker.py'),mode]
    start=time.perf_counter()
    env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1', HF_HUB_OFFLINE='1', HF_HUB_DISABLE_TELEMETRY='1', HF_HOME=str(STORE/'hf-cache'))
    try:
        proc=subprocess.run(args,cwd=ROOT,env=env,capture_output=True,text=True,timeout=1800 if mode!='reload' else 120)
        packet=dict(argv=args,returncode=proc.returncode,stdout=proc.stdout,stderr=proc.stderr)
    except subprocess.TimeoutExpired as exc:
        packet=dict(argv=args,returncode=None,stdout=str(exc.stdout),stderr=str(exc.stderr),error='PROCESS_TIMEOUT')
    write(mode.upper()+'-PROCESS.json',dict(packet,seconds=time.perf_counter()-start))
    print(json.dumps(packet,indent=2))
    assert packet['returncode']==0, 'single dispatch halted; no retry'


if __name__=='__main__':
    if sys.argv[1]=='freeze': freeze()
    else: dispatch(sys.argv[1])
