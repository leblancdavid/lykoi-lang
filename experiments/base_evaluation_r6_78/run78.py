"""Bounded base-only successor using frozen diagnostics and the R6.77 launcher."""
import json
import os
from pathlib import Path
import sys
import time
import traceback
import types
import uuid

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'experiments/contrastive_learning_r6_77'))
import audit77
import qualify77
from durable77 import Journal, atomic, digest, launch, load
old = audit77.old
x = old.x
OUT = ROOT/'benchmark/results/phase6/r6_78'


def binding():
    return dict(attempt='R6.78-base-successor-1', configuration_identity=old.CONFIG_ID,
                evaluation_sha256=digest(x.OUT/'EVALUATION.json'),
                case_ids=[r['id'] for r in x.read(x.OUT/'EVALUATION.json')['records'][4:]])


def prepare():
    assert not (OUT/'IDENTITY-PREFLIGHT.json').exists(), 'ONE_SHOT_PREPARATION'
    for round_name in ('r6_76', 'r6_77'):
        root = OUT.parent/round_name
        for name, entry in load(root/'PUBLICATION-IDENTITIES.json')['files'].items():
            assert digest(ROOT/name) == entry['sha256'], name
        assert load(root/'TERMINAL-RESULT.json')['classification'] == round_name.upper()+'_PROTOCOL_HALT'
    audit77.OUT = OUT
    audit77.main()
    atomic(OUT/'HISTORICAL-RECONCILIATION.json', dict(
        historical_qualified_observations=4, historical_total_model_calls=None,
        fifth_case=load(OUT/'RECOVERY-AUDIT.json')['next_case'],
        fifth_historical_generation=dict(invocation_status='potentially started',
            completion_status='unknown', raw_output=None, token_usage=None,
            wall_time_seconds=None, billing=None),
        historical_warning_lines=5, warning_is_not_completion_evidence=True,
        original_generation_counts_unchanged=True,
        replacement_attempt='R6.78-base-successor-1:000', recovery_of_historical_generation=False))
    qualify77.OUT = OUT
    qualify77.main()
    atomic(OUT/'EXECUTION-FREEZE.json', dict(binding=binding(),
        files={p.relative_to(ROOT).as_posix(): digest(p) for p in
               [Path(__file__), OUT/'PROTOCOL.md', OUT/'HISTORICAL-RECONCILIATION.json']},
        batch_size=1, worker_wall_seconds=1800, per_generation_seconds=120,
        training_authorized=False))


def worker(index, destination, nonce):
    destination = Path(destination)
    atomic(destination/'HANDSHAKE.json', dict(worker_pid=os.getpid(), parent_pid=os.getppid(),
        interpreter=sys.executable, nonce=nonce))
    assert Path(sys.executable).resolve() == x.PYTHON.resolve()
    freeze = load(OUT/'EXECUTION-FREEZE.json')
    for name, sha in freeze['files'].items():
        assert digest(ROOT/name) == sha
    x.frozen_check()
    row = x.read(x.OUT/'EVALUATION.json')['records'][index+4]
    journal = Journal(OUT/'cases', binding())
    assert len(journal.recover()) == index
    decoder_seconds = 0.0
    transitions = []
    prompt_tokens = None
    generated_tokens = None
    inference_seconds = None
    dispatch_index = None
    tokenizer_holder = {}

    class Language(x.CompletionLanguage):
        def allowed(self, tokenizer, ids, vocabulary):
            nonlocal decoder_seconds
            began = time.perf_counter()
            allowed = super().allowed(tokenizer, ids, vocabulary)
            transitions.append(dict(ids=list(ids), allowed_count=len(allowed),
                allowed_identity=x.identity(allowed)))
            atomic(destination/'TOKEN-PROGRESS.json', dict(transitions=transitions,
                selected_prefix_ids=list(ids), completed=False))
            tokenizer_holder['tokenizer'] = tokenizer
            decoder_seconds += time.perf_counter()-began
            return allowed

    def load_base():
        model, quant = x.q52.load_base()
        generate = model.generate

        def tracked_generate(*args, **kwargs):
            nonlocal dispatch_index, prompt_tokens, generated_tokens, inference_seconds
            dispatch_index = journal.begin(row['id'])
            assert dispatch_index == index
            prompt_tokens = kwargs['input_ids'].shape[1]
            atomic(destination/'PRE-DISPATCH.json', dict(attempt=binding()['attempt'],
                index=index, case_id=row['id'], replacement=index == 0,
                fixture_identity=x.identity(row), prompt_identity=x.identity(row['prompt']),
                prompt_tokens=prompt_tokens, decoder_settings=kwargs.keys().__str__(),
                configuration_identity=old.CONFIG_ID, pid=os.getpid(), time_ns=time.time_ns()))
            began = time.perf_counter()
            output = generate(*args, **kwargs)
            inference_seconds = time.perf_counter()-began
            ids = output[0, prompt_tokens:].tolist()
            generated_tokens = len(ids)
            tokenizer = tokenizer_holder['tokenizer']
            eos = bool(ids and ids[-1] == tokenizer.eos_token_id)
            atomic(destination/'POST-DISPATCH.json', dict(case_id=row['id'],
                generated_ids=ids, raw=tokenizer.decode(ids[:-1] if eos else ids,
                skip_special_tokens=False), eos=eos, prompt_tokens=prompt_tokens,
                generated_tokens_including_eos=generated_tokens,
                inference_decoder_seconds=inference_seconds,
                allowed_set_and_progress_persistence_seconds=decoder_seconds,
                billing=None, completed=True))
            return output

        model.generate = tracked_generate
        return model, quant

    def read(path):
        if path.name == 'EVALUATION.json':
            return dict(records=[row])
        return old.runtime.read(path)

    def write(name, value):
        atomic(destination/name, value)
        if name == 'BASE-DIAGNOSTIC-PARTIAL.json':
            record = value['records'][0]
            record.update(attempt_identity=f"{binding()['attempt']}:{index:03d}",
                replacement_attempt=index == 0, prompt_tokens=prompt_tokens,
                generated_tokens_including_eos=generated_tokens,
                allowed_set_and_progress_persistence_seconds=decoder_seconds,
                inference_decoder_seconds=inference_seconds, full_mask_seconds=None, billing=None)
            journal.commit(dispatch_index, record)

    namespace = dict(old.runtime.__dict__)
    namespace.update(read=read, write=write, q52=types.SimpleNamespace(seed=x.q52.seed, load_base=load_base))
    # Only substitute the instrumented subclass at the imported decoder binding.
    source = old.runtime.diagnostic_source().replace(
        'from context75 import CompletionLanguage, serialize', 'CompletionLanguage = instrumented_language')
    namespace['instrumented_language'] = Language
    exec(compile(source, 'r678-frozen-diagnostic-instrumented', 'exec'), namespace)
    namespace['diagnostic']('base')
    records = journal.recover()
    record = records[index]
    assert record['eos'] and len(record['generated_ids']) <= 64
    assert record['transitions'] == transitions
    assert 0 < record['seconds'] <= 120, 'GENERATION_TIMEOUT'
    atomic(destination/'COMPLETION.json', dict(passed=True, case_id=row['id'],
        raw_sha256=digest(journal.root/f'{index:03d}.raw.json'),
        attempt_identity=record['attempt_identity'], inference_calls=1))


def dispatch(index):
    assert load(OUT/'LAUNCHER-QUALIFICATION.json')['passed']
    if index:
        assert load(OUT/'LIVE-QUALIFICATION.json')['passed']
    destination = OUT/f'worker-{index:03d}'
    nonce = uuid.uuid4().hex
    os.environ.update(HF_HUB_OFFLINE='1', HF_HUB_DISABLE_TELEMETRY='1',
        PYTHONDONTWRITEBYTECODE='1', TOKENIZERS_PARALLELISM='false')
    os.environ.pop('CUDA_VISIBLE_DEVICES', None)
    result = launch([str(x.PYTHON), str(Path(__file__)), 'worker', str(index), str(destination), nonce],
        destination, old.resource, 17179869184, 1800, x.PYTHON, nonce)
    assert result['returncode'] == 0 and result['failure'] is None, result
    assert result['worker_pid'] and load(destination/'COMPLETION.json')['passed']
    record = Journal(OUT/'cases', binding()).recover()[index]
    if index == 0:
        checks = dict(process_identity=True, dispatch_commitment=True, durable_raw_output=True,
            completion_receipt=True, duplicate_dispatch_refused=False, corruption_detection=False,
            interruption_handling=load(OUT/'LAUNCHER-QUALIFICATION.json')['checks']['tracked_timeout_child_terminated'],
            timeout_enforcement=load(OUT/'LAUNCHER-QUALIFICATION.json')['checks']['tracked_timeout_child_terminated'])
        try:
            Journal(OUT/'cases', binding()).begin(record['id'])
        except AssertionError:
            checks['duplicate_dispatch_refused'] = True
        control = Journal(OUT/'live-corruption-control', dict(case_ids=[record['id']], control=True))
        control.commit(control.begin(record['id']), record)
        atomic(control.root/'000.raw.json', dict(record, raw=record['raw']+'corruption'))
        try:
            control.recover()
        except AssertionError:
            checks['corruption_detection'] = True
        assert all(checks.values())
        atomic(OUT/'LIVE-QUALIFICATION.json', dict(passed=True, checks=checks,
            live_completed_generations=1, live_case=record['id'], replacement_attempt=True,
            interruption_and_timeout_scope='Real pinned-worker synthetic controls; no extra interrupted model generation.',
            batch_size=1, worker_ceiling_seconds=1800, phase=result))
    print(json.dumps(dict(index=index, id=record['id'], qualified=True,
        accepted=record['scores']['accepted'], tokens=len(record['generated_ids']))))


if __name__ == '__main__':
    try:
        if sys.argv[1] == 'prepare':
            prepare()
        elif sys.argv[1] == 'dispatch':
            dispatch(int(sys.argv[2]))
        else:
            worker(int(sys.argv[2]), sys.argv[3], sys.argv[4])
    except BaseException as exc:
        destination = Path(sys.argv[3]) if sys.argv[1] == 'worker' else OUT
        atomic(destination/f'HALT-{sys.argv[1]}.json', dict(error=str(exc),
            traceback=traceback.format_exc(), automatic_retry=False))
        raise
