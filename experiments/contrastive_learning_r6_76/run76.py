"""Additive one-shot orchestration of the exact R6.75 configuration."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'experiments/contrastive_preflight_r6_75'))
import successor3
import context75 as x
import runtime75 as runtime
import resources75 as resource

OUT = ROOT/'benchmark/results/phase6/r6_76'
CONFIG_ID = 'a2b3d148a5e966d856864a1ad6b4e43550ce699e8c94b21493667abbf6d55189'


def write(name, value):
    path = OUT/name
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix+'.pending')
    temp.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False)+'\n', encoding='utf-8', newline='\n')
    temp.replace(path)


def verify():
    import preflight75
    publication = x.prior.f.publication('r6_75')
    baseline = preflight75.baseline()
    assert baseline == x.read(x.OUT/'BASELINE.json')
    assert x.frozen_check()['training_configuration_identity'] == CONFIG_ID
    cfg = x.read(x.OUT/'TRAINING-CONFIGURATION.json')['configuration']
    runtime.validate_configuration(cfg)
    for name, record in cfg['model_identities'].items():
        assert x.sha(x.STORE/'checkpoint'/name) == record['sha256'], name
    assert x.prior.f.publication('r6_73')
    return dict(passed=True, publication=publication, baseline=baseline,
                configuration_identity=CONFIG_ID, kernel_constructs=26,
                model_tokenizer_files=cfg['model_identities'], historical_rescoring=0)


def neutral():
    import torch
    from transformers import AutoTokenizer, LogitsProcessor
    cfg = x.read(x.OUT/'TRAINING-CONFIGURATION.json')['configuration']
    precision = cfg['precision_runtime']
    torch.backends.cuda.matmul.allow_tf32 = precision['allow_tf32_matmul']
    torch.backends.cudnn.allow_tf32 = precision['allow_tf32_cudnn']
    torch.set_float32_matmul_precision(precision['float32_matmul_precision'])
    torch.use_deterministic_algorithms(precision['deterministic_algorithms'])
    x.q52.seed()
    model, quant = x.q52.load_base()
    tokenizer = AutoTokenizer.from_pretrained(x.STORE/'checkpoint', local_files_only=True, trust_remote_code=False)
    model.eval()
    controls = x.read(OUT/'NEUTRAL-CONTROLS.json')['controls']
    results = []
    for control in controls:
        language = x.CompletionLanguage(control['scope'])
        prompt = tokenizer.apply_chat_template(control['prompt'], tokenize=True, add_generation_prompt=True)
        transitions = []
        started = time.perf_counter()
        enforcement = 0.0

        class Mask(LogitsProcessor):
            def __call__(self, input_ids, scores):
                nonlocal enforcement
                before = time.perf_counter()
                assert before-started <= 120, 'GENERATION_TIMEOUT'
                free, _ = torch.cuda.mem_get_info()
                assert free >= cfg['limits']['minimum_device_free_bytes'], 'DEVICE_FREE_LIMIT'
                assert torch.cuda.max_memory_reserved() <= cfg['limits']['cuda_reserved_bytes'], 'CUDA_RESERVED_LIMIT'
                ids = input_ids[0,len(prompt):].tolist()
                prefix = tokenizer.decode(ids, skip_special_tokens=False)
                assert len(ids) < 64, 'GENERATION_BUDGET'
                allowed = language.allowed(tokenizer, ids, range(len(tokenizer)))
                transition = dict(ids=ids, prefix=prefix, terminal=prefix in language.terminals,
                                  allowed_ids=allowed, allowed_identity=x.identity(allowed))
                transitions.append(transition)
                write('NEUTRAL-TOKENS.json', dict(control=control['id'], transitions=transitions))
                assert allowed, 'COMPACT_DEAD_END'
                if transition['terminal']:
                    assert allowed == [tokenizer.eos_token_id]
                filtered = torch.full_like(scores, float('-inf'))
                filtered[:,allowed] = scores[:,allowed]
                assert torch.isneginf(filtered).sum().item() == scores.numel()-len(allowed)
                enforcement += time.perf_counter()-before
                assert time.perf_counter()-started <= 120, 'GENERATION_TIMEOUT'
                return filtered

        inputs = torch.tensor([prompt], device='cuda')
        with torch.no_grad():
            output = model.generate(input_ids=inputs, attention_mask=torch.ones_like(inputs), logits_processor=[Mask()],
                **{k:v for k,v in cfg['decoding_settings'].items() if k not in ('seed','per_generation_timeout_seconds')})
        ids = output[0,len(prompt):].tolist()
        raw = tokenizer.decode(ids[:-1], skip_special_tokens=False)
        result = dict(id=control['id'], generated_ids=ids, raw=raw, transitions=transitions,
                      seconds=time.perf_counter()-started, decoder_seconds=enforcement)
        results.append(result)
        write('NEUTRAL-PARTIAL.json', dict(records=results))
        assert ids[-1] == tokenizer.eos_token_id, 'EOS_OR_OUTPUT_BUDGET_FAILURE'
        assert len(ids) <= 64 and len(ids) == len(transitions)
        assert all(token in transition['allowed_ids'] for token, transition in zip(ids, transitions))
        assert raw in language.terminals
        x.prior.parse(raw)
        # A deliberately short budget is a neutral truncation control, never scored.
        short_ids = ids[:1]
        assert tokenizer.decode(short_ids, skip_special_tokens=False) not in language.terminals
    write('NEUTRAL-QUALIFICATION.json', dict(passed=True, records=results, quantization=quant,
        syntax_only=True, semantic_answer_inputs=False, output_budget=64,
        short_budget_truncation_rejected=True))


def worker(mode):
    write('WORKER-'+mode+'.json', dict(worker_pid=os.getpid(), parent_pid=os.getppid(),
        interpreter=sys.executable, mode=mode, nonce=os.environ['LYKOI_R6_76_NONCE']))
    x.frozen_check()
    runtime.OUT = OUT
    # Evidence destination only: configuration, checkpoint paths and executable
    # training definitions remain byte-identical to the qualified publication.
    if mode == 'neutral':
        neutral()
    else:
        assert x.read(OUT/'NEUTRAL-QUALIFICATION.json')['passed']
        namespace = {}
        exec(compile((x.OUT/'EFFECTIVE-WORKER.py.txt').read_text(encoding='utf-8'), 'r675-worker', 'exec'), namespace)
        if mode == 'train':
            namespace['train']()
        else:
            runtime.diagnostic(mode)


def dispatch():
    import uuid
    assert not OUT.exists(), 'ONE_SHOT_OUTPUT_EXISTS'
    receipt = verify()
    assert not x.ARTIFACTS.exists()
    write('IDENTITY-PREFLIGHT.json', receipt)
    write('NEUTRAL-CONTROLS.json', dict(controls=[dict(id='N1',
        scope=dict(params=[dict(name='a',type='Int64'),dict(name='b',type='Int64')],steps=[],literals=[]),
        prompt=[dict(role='system',content='Return one compact JSON decision with deps, left, op, right. Choose any available operation and operands; this is a syntax-only neutral control.'),
                dict(role='user',content='Available references: a, b. Operations: add, le, eq. Dependencies: zero to two of a, b. Return compact JSON only.')])]))
    write('EXECUTION-RECEIPT.json', dict(round='R6.76', configuration_identity=CONFIG_ID,
        owner_authorized=True, max_optimizer_updates=54, retries=False,
        evidence_destination=str(OUT), checkpoint_destination=str(x.ARTIFACTS),
        frozen_training_source=x.sha(x.OUT/'EFFECTIVE-WORKER.py.txt'),
        diagnostics='6 exposed calibration + 24 coordinator-reviewed successor renderings; exploratory'))
    files = [Path(__file__), OUT/'NEUTRAL-CONTROLS.json', OUT/'EXECUTION-RECEIPT.json']
    write('EXECUTION-FREEZE.json', dict(files={p.relative_to(ROOT).as_posix():x.sha(p) for p in files}))
    phases = []
    for mode in ('neutral','base','train','adapter'):
        nonce = uuid.uuid4().hex
        env = dict(os.environ, HF_HUB_OFFLINE='1', HF_HUB_DISABLE_TELEMETRY='1',
                   PYTHONDONTWRITEBYTECODE='1', TOKENIZERS_PARALLELISM='false', LYKOI_R6_76_NONCE=nonce)
        env.pop('CUDA_VISIBLE_DEVICES', None)
        started = time.perf_counter()
        samples = []
        pid = None
        with (OUT/(mode+'-stdout.txt')).open('x',encoding='utf-8') as stdout, (OUT/(mode+'-stderr.txt')).open('x',encoding='utf-8') as stderr:
            process = subprocess.Popen([str(x.PYTHON),str(Path(__file__)), 'worker', mode],cwd=ROOT,env=env,stdout=stdout,stderr=stderr)
            try:
                while process.poll() is None:
                    handshake = OUT/('WORKER-'+mode+'.json')
                    if pid is None and handshake.exists():
                        try:
                            value = x.read(handshake)
                        except json.JSONDecodeError:
                            value = None
                        if value:
                            from dispatch_v3 import validate_handshake
                            pid = validate_handshake(value, nonce, mode, process.pid)
                    value = resource.measure(pid or process.pid)
                    if not value['available'] and process.poll() is not None:
                        break
                    resource.validate(value, pid or process.pid, 17179869184)
                    samples.append(value)
                    assert time.perf_counter()-started <= 1800, 'PROCESS_WALL_LIMIT'
                    time.sleep(0.1)
            finally:
                if process.poll() is None:
                    subprocess.run(['taskkill','/PID',str(pid or process.pid),'/T','/F'],capture_output=True,timeout=30)
                    process.kill()
                    process.wait(timeout=30)
        phase = dict(mode=mode, worker_pid=pid, returncode=process.returncode,
                     seconds=time.perf_counter()-started, resource_samples=samples)
        phases.append(phase)
        write('PHASE-'+mode+'.json',phase)
        assert process.returncode == 0, ('PHASE_FAILED',mode,process.returncode)
        if mode == 'neutral':
            assert x.read(OUT/'NEUTRAL-QUALIFICATION.json')['passed']
            x.ARTIFACTS.mkdir()
    write('EXECUTION-RESULT.json', dict(passed=True,phases=phases))


if __name__ == '__main__':
    try:
        if sys.argv[1] == 'dispatch':
            dispatch()
        else:
            worker(sys.argv[2])
    except BaseException as exc:
        write('HALT-'+sys.argv[1]+'.json',dict(error=str(exc),traceback=traceback.format_exc(),
            automatic_retry=False,phase=sys.argv[2] if len(sys.argv)>2 else 'dispatch'))
        raise
