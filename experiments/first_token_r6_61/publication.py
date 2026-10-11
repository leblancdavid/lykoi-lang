"""Post-inference descriptive analysis and additive publication; never loads a model."""
import importlib.util
import json
from pathlib import Path
import re
import sys

spec = importlib.util.spec_from_file_location('r61_driver', Path(__file__).with_name('diagnose.py'))
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)


def summarize():
    # Initial descriptive draft retained for provenance. PARSE-STAGE-AUDIT,
    # VERSION-VALUE-DIVERGENCE and corrected report are authoritative corrections.
    d.check()
    matrix = d.c.read(d.OUT / 'FIRST-TOKEN-MATRIX.json')['records']
    continuations = [d.c.read(p) for p in sorted(d.OUT.glob('CONTINUATION-*.json'))]
    assert len(matrix) == len(continuations) == 24
    rows, effects, pairs, structural = [], [], [], []
    for track in ('base', 'adapter'):
        for eid in range(1, 7):
            episode = f'R6.48/E{eid:02d}'
            a, b = [next(r for r in matrix if r['track'] == track and r['episode_id'] == episode and r['penalty'] == p)
                    for p in (1.0, 1.1)]
            effects.append({'track': track, 'episode_id': episode,
                'opening_rank_1_0': a['processed']['raw_opening']['rank'], 'opening_rank_1_1': b['processed']['raw_opening']['rank'],
                'fence_rank_1_0': a['processed']['fence']['rank'], 'fence_rank_1_1': b['processed']['fence']['rank'],
                'top_changed': a['processed']['top']['id'] != b['processed']['top']['id'],
                'probability_margin_delta_1_1_minus_1_0': b['processed']['probability_margin_opening_minus_fence'] - a['processed']['probability_margin_opening_minus_fence'],
                'logit_margin_delta_1_1_minus_1_0': b['processed']['logit_margin_opening_minus_fence'] - a['processed']['logit_margin_opening_minus_fence']})
            for r in (a, b):
                v = r['processed']
                rows.append(f"| {track} | E{eid:02d} | {r['penalty']:.1f} | {v['raw_opening']['logit']:.6f} | {v['raw_opening']['probability']:.6f} | {v['raw_opening']['rank']} | {v['fence']['logit']:.6f} | {v['fence']['probability']:.6f} | {v['fence']['rank']} | {v['probability_margin_opening_minus_fence']:.6f} |")
    for eid in range(1, 7):
        for p in (1.0, 1.1):
            a, b = [next(r for r in continuations if r['track'] == track and r['episode_id'] == f'R6.48/E{eid:02d}' and r['penalty'] == p)
                    for track in ('base', 'adapter')]
            pairs.append({'episode_id': a['episode_id'], 'penalty': p,
                'byte_identical': a['continuation'] == b['continuation'], 'token_ids_identical': a['output_token_ids'] == b['output_token_ids'],
                'base_tokens': a['output_tokens_including_eos'], 'adapter_tokens': b['output_tokens_including_eos']})
    for r in continuations:
        text = r['completed_text']
        first = re.match(r'\{"([^"\\]*)"\s*:', text)
        key = first.group(1) if first else None
        forbidden = key not in ('definitions', 'foundation', 'program', 'version') if key else None
        structural.append({'track': r['track'], 'episode_id': r['episode_id'], 'penalty': r['penalty'],
            'first_top_level_key': key, 'first_package_structure_divergence_character': 2 if forbidden else None,
            'first_package_structure_divergence_generated_token': 0 if forbidden else None,
            'reason': 'first top-level key is outside required closed package envelope' if forbidden else 'see native diagnostic',
            'prompt_content_echo': key == 'required_output', 'contains_fence': '```' in text,
            'parse_valid': r['scores']['output_valid'], 'schema_valid': r['scores']['schema_valid'],
            'semantic_validation_stage': 'NOT_REACHED', 'functional_stage': 'NOT_REACHED'})
    d.write('REPETITION-PENALTY-COMPARISON.json', {'records': effects,
        'all_top_tokens_73594': all(r['processed']['top']['id'] == 73594 for r in matrix),
        'all_opening_ranks_worse_at_1_1': all(r['opening_rank_1_1'] > r['opening_rank_1_0'] for r in effects),
        'interpretation': 'penalty suppresses prompt-present opening and widens fence advantage, but is not necessary for fence selection'})
    d.write('CONTINUATION-PAIR-COMPARISON.json', {'records': pairs, 'byte_identical_pairs': sum(r['byte_identical'] for r in pairs),
        'accepted_adapter_advantage': False, 'all_fail_schema': True})
    d.write('STRUCTURAL-DIVERGENCE-SUPPLEMENT.json', {'records': structural,
        'note': 'earliest package-envelope divergence differs from later parser failure offset; no repaired evaluation'})
    resources = []
    for track in ('base', 'adapter'):
        data = d.c.read(d.OUT / f'{track.upper()}-MEASUREMENTS.json')
        process = d.c.read(d.OUT / f'{track.upper()}-PROCESS.json')
        calls = [r for r in continuations if r['track'] == track]
        resources.append({'track': track, 'first_position_forward_seconds': sum(r['forward_seconds'] for r in data['records']),
            'generation_seconds': sum(r['generation_seconds'] for r in calls),
            'generated_tokens_including_eos': sum(r['output_tokens_including_eos'] for r in calls),
            'worker_seconds': data['whole_worker_seconds'], 'subprocess_seconds': process['seconds'],
            'peak_allocated_bytes': data['peak_allocated_bytes'], 'peak_reserved_bytes': data['peak_reserved_bytes'],
            'minimum_retained_device_free_bytes': min([data['device_free_bytes']] + [r['device_free_bytes'] for r in calls]),
            'external_observed_pid': 'venv launcher; not claimed as model-worker RSS',
            'external_peak_launcher_rss_bytes': process['peak_sampled_rss_bytes'],
            'actual_worker_rss_checks': 'own PID <=16GiB at each generation step and measurement boundaries; numeric peak not retained',
            'returncode': process['returncode'], 'external_abort': process['external_abort'],
            'runtime_error': None, 'warnings': 'inactive temperature/top_p/top_k under greedy decoding'})
    d.write('RESOURCE-MEASUREMENTS.json', {'records': resources, 'no_exclusive_gpu_isolation': True,
        'no_continuous_global_device_free_minimum': True, 'optimizer_updates': 0, 'scheduler_updates': 0})
    d.write('INTERPRETATION.json', {'A': 'first-token fence preference measured; primary/decisive-only blocker not supported',
        'B': 'interference supported as probability/rank suppression; not necessary or sufficient explanation of formatting failure',
        'C': 'broader package construction gap supported: all24 omit required envelope even after opening supplied',
        'D': 'not supported: no adapter schema/type/semantic/functional advantage',
        'E': 'no measurable accepted-generation adapter advantage; raw opening probability improves on6/6',
        'F': 'semantic runtime correctness and unseen generalization remain untested; types/operations blocked before evaluation'})
    # Read-only check for no decode normalization and deterministic recomputation of new scores only.
    t = d.tokenizer()
    for r in continuations:
        ids = r['output_token_ids'][:-1] if r['eos_terminated'] else r['output_token_ids']
        assert t.decode(ids, skip_special_tokens=False) == r['continuation']
        row = next(v for v in d.c.rows() if v['episode_id'] == r['episode_id'])
        assert d.c.score(r['completed_text'], row) == r['scores']
    rank_rows = []
    for eid in range(1, 7):
        v = [next(r for r in matrix if r['track'] == track and r['episode_id'] == f'R6.48/E{eid:02d}' and r['penalty'] == p)['processed']['raw_opening']['rank']
             for track in ('base', 'adapter') for p in (1.0, 1.1)]
        rank_rows.append(f'| E{eid:02d} | {v[0]} / {v[1]} | {v[2]} / {v[3]} |')
    inventory_rows = []
    for eid in range(1, 7):
        values = [next(r for r in continuations if r['track'] == track and r['episode_id'] == f'R6.48/E{eid:02d}' and r['penalty'] == p)
                  for track in ('base', 'adapter') for p in (1.0, 1.1)]
        a, b, cc, dd = values
        inventory_rows.append(f"| E{eid:02d} | {a['output_tokens_including_eos']} / {b['output_tokens_including_eos']} | {cc['output_tokens_including_eos']} / {dd['output_tokens_including_eos']} | {a['scores']['native_diagnostic']['code']} / {b['scores']['native_diagnostic']['code']} |")
    resource_rows = []
    for r in resources:
        resource_rows.append(f"| {r['track']} | {r['first_position_forward_seconds']:.6f} | {r['generation_seconds']:.6f} | {r['generated_tokens_including_eos']} | {r['peak_allocated_bytes']} | {r['peak_reserved_bytes']} | {r['subprocess_seconds']:.6f} |")
    report = '''# R6.61 — First-token decoding and minimal-prefix continuation diagnosis

**Final classification: `R6_61_BROADER_GENERATION_GAP`.**

The markdown fence is the highest-ranked first token on **6/6 prompts in both
models at both penalties**. Penalty1.1 measurably suppresses the raw opening already
present in the prompt, but fence selection persists at1.0. Supplying exactly the
raw opening does not yield a symbolic package: **0/24 schema-valid or functionally
accepted continuations**. The first token is an observed formatting failure, not
the decisive complete-construction blocker. No accepted-generation adapter advantage.

## 1. Baseline, identities and preservation

Initial git status clean. Before edits, R6.60 publication verifier passed, including
R6.59 publication/external artifacts and inherited R6.52 environment/checkpoint/
tokenizer/package/protected-history chain. [Baseline](r6_61/BASELINE.json) repeats
these checks before freeze, each dispatch, analysis and publication. All47 installed
distribution trees, exact private Python executable/DLL/launcher/uv/lock,5,387 inherited
protected identities, E01–E06 canonical sources/token masks/provenance and original
base/adapter diagnostic file hashes remain exact. Publications R6.59/R6.60 and
original classifications are preserved. R6.59 strict/functional scores stay0/6 vs0/6.

- Model: `Qwen/Qwen2.5-Coder-1.5B-Instruct`, revision
  `2e1fd397ee46e1388853d2af2c993145b0f1098a` (the historical Instruct checkpoint,
  “base” here denotes its unchanged no-adapter condition).
- Weight SHA256 `c1b9b30e907950516ba3c646bdf570d8084c25a6410a0cdca80cf04b11bc13a8`.
- Tokenizer JSON SHA256 `c0382117ea329cdf097041132f6d735924b697924d6f6fc3945713e96ce87539`.
- Step20 adapter weights SHA256
  `79843df8ce1f3e9bf87c81e0e23073c37a702695df6e52ac384b0a33f77fb7d1`;
  config `642b816c81121fb0bf251550885b1ae30ca89c2cb824f4b4a2cd2c1caf657050`;
  directory `d8bbe876eca1e5929a0bd570e44fb661d4eb1cdb5ebf8e857c3ee659923ab58a`.
- Python3.12.11/torch2.7.1+cu128/Transformers4.55.4/PEFT0.17.1/BNB0.47.0,
  offline local-only NF4/double-quantization/BF16, SDPA and cache off unchanged.

Loaded112 adapter tensors match R6.59. Each model's parameter/buffer/quantization
and adapter tensor manifests match before/after inference; all gradients absent.
Production compiler/lowerer/runtime and experimental semantics unchanged; kernel26.

## 2. Freeze, tokenizer and decoding procedure

[Protocol](r6_61/PROTOCOL.md), [executable](../../../experiments/first_token_r6_61/diagnose.py),
[freeze](r6_61/FREEZE.json) and [prefix specification](r6_61/PREFIX-SPECIFICATION.json)
were written before model execution. Exact frozen messages/native chat template end
at `<|im_start|>assistant\\n`; no extra roles, instructions or keys supplied.

Pinned tokenizer verifies4913 decodes **`{"`**, object plus key-string opening,
and73594 decodes three backticks. Neither token is a complete JSON document; the
fence token alone supplies no language identifier or closing fence. The supplied
prefix is precisely UTF-8 hex7b22, IDs[4913], no newline. It is a syntactically valid
partial JSON prefix, verified by a CPU-only valid completion and by being the
first two bytes of all six targets. No target key/value, operation, graph, identity
or implementation is supplied. Full prompt+prefix tokenization equals original
prompt IDs followed by4913 in every record; boundary merging does not change prompts.

Two fresh processes (base then adapter), one unprefilled forward per frozen prompt
and one continuation per prompt/penalty:12 forwards,24 continuations. Every module
eval, parameters nontrainable, inference_mode; no backward/optimizer/scheduler.
Greedy/one beam, inherited max_new_tokens1400/context2048, EOS151645/151643,
pad151643, actual use_cache false. Stored config use_cache true is overridden.
Temperature/top_p/top_k fields are inactive; framework warnings preserved.

Raw last-position FP32 logits retained across the entire vocabulary in12 `.f32`
files (little-endian). Installed RepetitionPenaltyLogitsProcessor receives all
prompt IDs, separately at1.0/1.1. No sampling transformations apply. Softmax is
over the full vocabulary, rank=1+strictly greater logits; ties retained. Highest
token ID73594 in every condition, unique top. Probability and logit margins use
opening minus fence. CPU publication reconstruction independently verifies each
processor transformation, top choice, ranks and probabilities from saved logits.

## 3. First-token probability/rank matrix

Penalty1.0 is the identity transform and is exactly the raw-model distribution.
Penalty1.1 is shown separately. All target logits and margins, ties, full raw logits
and model/prompt identities are retained in [matrix](r6_61/FIRST-TOKEN-MATRIX.json).

| Model | Record | Penalty | Opening logit | Opening probability | Opening rank | Fence logit | Fence probability | Fence rank | Probability margin |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
''' + '\n'.join(rows) + '''

### Rank summary (penalty1.0 /1.1)

| Record | Base opening rank | Adapter opening rank |
| --- | ---: | ---: |
''' + '\n'.join(rank_rows) + '''

Fence rank1 throughout. Opening4913 is present in every prompt; fence73594 is
absent from every prompt. All opening logits are positive:1.1 divides them by1.1,
while leaving fence logits unchanged. Softmax redistribution increases fence
probability and lowers opening probability; rank worsens on all12 prompt/model
pairs. [Penalty comparison](r6_61/REPETITION-PENALTY-COMPARISON.json) retains exact
rank changes and logit/probability-margin deltas. This is measured interference,
but **not the cause necessary for fence selection**: fence already wins on raw
logits. Neutralizing the penalty alone does not select the opening.

Adapter increases raw opening probability on all six paired prompts, but does not
change the winning token. Minor numerical differences from R6.60's gold-completion
full-sequence likelihood are not treated as identity mismatches or replay failure:
this probe runs prompt-only forwards, with different sequence shape and kernel
arithmetic; exact historical R6.60 observations remain preserved.

## 4. Raw continuation and validation results

All24 calls finish at native EOS151645; no token cap/time cap/resource error.
The supplied opening is preserved; no backticks occur in completed texts. This
does not imply raw *package* format: all outputs immediately choose a top-level key
outside the exact required envelope. Raw continuation `.txt` and complete token
IDs/text/configuration/scores in matching `CONTINUATION-*.json` are preserved.
Text scoring removes only the final EOS; no normalization, fence stripping or seal.

| Model | Penalty | JSON object parses | Schema passes | Type passes | Semantic passes | Functional reached /passes |
| --- | ---: | ---: | ---: | --- | --- | --- |
| Base | 1.0 | 1/6 | 0/6 | NOT_REACHED6 | NOT_REACHED6 | 0/6 /0/6 |
| Base | 1.1 | 6/6 | 0/6 | NOT_REACHED6 | NOT_REACHED6 | 0/6 /0/6 |
| Adapter | 1.0 | 1/6 | 0/6 | NOT_REACHED6 | NOT_REACHED6 | 0/6 /0/6 |
| Adapter | 1.1 | 6/6 | 0/6 | NOT_REACHED6 | NOT_REACHED6 | 0/6 /0/6 |

[Validation results](r6_61/VALIDATION-RESULTS.json) retain native failures and
unchanged scorer observations. Its boolean semantic_valid=false is failure to
achieve validation, not evidence of a reached semantic runtime test. Independent
deterministic schema/native validation and E01–E06 fixture execution were frozen
before generation; execution remains unreachable for all24. No historical rescoring.

At1.0 E01–E04/E06 echo the user prompt's required_output/requirement/vocabulary
object then append an extra closing brace; parser reports Extra data. E05 emits
a parseable VERSION/COUNT answer object. At1.1 every output is a small answer
snippet, not the definitions/foundation/program/version package. Example E01,
both models: `{"result":137,"result_type":"Int64"}`. Adapter E05 differs:
`{"result":true,"message":"The provided input meets the specified requirements."}`.
All other base/adapter pairs are byte- and token-identical: **11/12 pairs**,
including all six at1.0. Neither changed E05 output is accepted.

## 5. First divergence: formatting versus construction

Historical unprefilled generation first diverged at token0/character0 (fence73594)
on all12 calls; original [R6.60 inventory](r6_60/FIRST-DIVERGENCE.json) is preserved.
This round's distributions measure that preference without rerunning those outputs.

Every supplied-prefix continuation diverges from the required package envelope at
completed-text character2, first continuation token0: first key is required_output,
VERSION, result, or low instead of an admitted top-level package key. This early
structural divergence is distinct from the later parser failure offset on malformed
echoes. [Supplement](r6_61/STRUCTURAL-DIVERGENCE-SUPPLEMENT.json) records earliest
envelope divergence; [native inventory](r6_61/FIRST-DIVERGENCE.json) records exact
parser offsets/native paths, missing keys, EOS and repetition flags.

| Record | Base tokens1.0 /1.1 | Adapter tokens1.0 /1.1 | Base native blocker1.0 /1.1 |
| --- | ---: | ---: | --- |
''' + '\n'.join(inventory_rows) + '''

All24 lack lexical key occurrences for every required package envelope key;
every parseable object structurally lacks all four. Structural key presence for
malformed texts is unestablished, separately from lexical absence. Typed labels
are descriptive snippet observations only; no typed arguments or generated program
operations reach validation. **Wrong-operation or runtime behavior verdicts are
NOT_REACHED**, not silently treated as passes or diagnosed from target mismatch.
All EOS terminations are premature relative to a complete package. No adjacent
identical8-token blocks, no token/time truncation; copying prompt content at1.0 is
retained separately from the narrow repetition detector. The neutral control
improves opening probability but produces prompt echo on five tasks; penalty1.1
produces short parseable snippets. Neither constructs a package.

## 6. Resource controls, timings and limitations

[Measurements](r6_61/RESOURCE-MEASUREMENTS.json), base/adapter full-vocabulary
measurements and raw process receipts retain warnings, token counts and identities.

| Model | First-position forwards seconds | Continuation seconds | Tokens incl.EOS | Peak allocated bytes | Peak reserved bytes | Whole subprocess seconds |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
''' + '\n'.join(resource_rows) + '''

Bounds:120s/generation,1800s/model process, reserved8GiB/free1.5GiB/actual worker
RSS16GiB. Per-step stopping criteria check GPU bounds and own-PID RSS; no timeout,
CUDA/numerical/provider error or failed invocation occurred. GPU peaks include load
and all model operations, reset once per process. Device-free minima are retained
samples, not continuous board minima. No exclusive GPU isolation/efficiency claim.

External100ms RSS watchdog sampled the **venv launcher PID**, with only about5MB
observed. It is not a valid model-worker peak RSS estimate. Actual worker enforces
its own PID limit during generation and measurement boundaries; numeric worker peak
RSS was not retained. This instrumentation limitation is disclosed, not repaired
by rerunning inference. Baseline hashing/load/tensor-integrity checks contribute
subprocess overhead; base and adapter times are not controlled performance evidence.

## 7. Interpretation and smallest next experiment

- **A:** measured first-token formatting preference, but decisive-only/primary
  blocker classification not supported because fixing it still fails construction.
- **B:** measured penalty interference with prompt-present opening; not necessary
  for fence choice, and neutral control does not solve subsequent construction.
- **C:** broader package-structure generation gap supported in all24 continuations.
- **D:** no improved accepted adapter continuation under supplied opening.
- **E:** no measurable adapter schema/type/semantic/functional generation advantage;
  raw opening probabilities improve, which is a narrower distribution observation.
- **F:** unseen transfer, internal semantic understanding and runtime correctness
  of valid generated programs remain unresolved because these are exposed records
  and no generated program reaches execution.

Supported likelihood fitting from R6.60 remains true; this diagnosis does not
replace it. No first-token correction claim solves symbolic construction. No
independent authoring, unseen generalization or semantic-understanding claim.

**Recommended smallest next experiment:** separately authorize one inference-only
paired next-key ranking probe immediately after this same minimal opening, on the
same six exposed prompts. Predeclare admitted top-level package key starts versus
observed required_output/result/VERSION/low competitors, retain raw/processed
distributions at1.0/1.1, supply no additional key/value/graph. This isolates the
next structural decision without training or a complete-package scaffold. It is
not authorized or executed here; further scaffolding cannot establish independent
construction. No training or dataset expansion is recommended automatically.

## 8. Publication integrity and stop

[Publication identities](r6_61/PUBLICATION-IDENTITIES.json) bind protocol/freeze,
baseline, full-vocabulary binaries, all24 raw outputs, scores, processor comparisons,
divergence/resource/interpretation/results, report and additive research supplement.
[Verification](r6_61/VERIFICATION.json) verifies original preservation chain,
numerical CPU reconstruction, JSON/Python/links/credential patterns and
`git diff --check`; the offline publication wrapper additionally rechecks exact
decoding and recomputes only these new scores. Shared historical documentation
remains pinned; [new log supplement](../../../docs/research-log-r6.61.md) records
current observation/decision/boundary without altering historical indexed bytes.

Kernel26; new primitives0; optimizer/scheduler updates0; training0; expansion0;
Python comparison adapter0; historical rescoring0; P6-A04 acceptance0; P6-A05 access
false. AI-independent execution preserved. **Stopped after bounded inference and
publication; await explicit authorization before further work.**
'''
    report_path = d.ROOT / 'benchmark/results/phase6/R6_61-REPORT.md'
    assert not report_path.exists()
    report_path.write_text(report, encoding='utf-8', newline='\n')
    print('\n'.join(rank_rows))
    print(json.dumps(resources, indent=2))


def publish(seal):
    verify_observations()
    supplement = d.c.read(d.OUT / 'OFFLINE-SOURCE-IDENTITIES.json') if not seal else {
        'files': {Path(__file__).relative_to(d.ROOT).as_posix(): d.c.sha(Path(__file__))},
        'verification': 'offline only: exact raw decoding, all24 new scores,24 processor observations, preserved historical baseline'}
    if seal:
        d.write('OFFLINE-SOURCE-IDENTITIES.json', supplement)
    for name, digest in supplement['files'].items():
        assert d.c.sha(d.ROOT / name) == digest
    d.publish(seal)


def verify_observations():
    import ast
    ast.parse(Path(__file__).read_text(encoding='utf-8'))
    t = d.tokenizer()
    audit_rows = d.c.read(d.OUT / 'PARSE-STAGE-AUDIT.json')['records']
    assert len(audit_rows) == 24
    schema = d.c.read(d.ROOT / 'experiments/typed_composition_r6_18/typed-composition-1.schema.json')
    for r in audit_rows:
        eid = r['episode_id'].split('/')[-1]
        raw = d.c.read(d.OUT / f'CONTINUATION-{r["track"].upper()}-{eid}-P{r["penalty"]:.1f}.json')
        ids = raw['output_token_ids']
        assert ids[-1] == 151645 and raw['eos_terminated']
        assert t.decode(ids[:-1], skip_special_tokens=False) == raw['continuation']
        assert raw['completed_text'] == d.PREFIX + raw['continuation']
        value = json.loads(raw['completed_text'])
        assert isinstance(value, dict) and r['ordinary_json_object_parses']
        assert list(value) == r['top_level_keys']
        assert not d.c.schema_valid(value, schema, schema)
        row = next(v for v in d.c.rows() if v['episode_id'] == raw['episode_id'])
        assert d.c.score(raw['completed_text'], row) == raw['scores']
        assert raw['scores']['type_valid'] == 'NOT_REACHED' and not raw['scores']['functional_cases']
        assert not raw['time_limit_reached'] and not raw['token_limit_reached']
        if eid == 'E05' and r['penalty'] == 1.0:
            assert value == {'version': 7, 'count': 0}
            assert raw['completed_text'][11] == '7' and ids[2] == 22
        else:
            assert not set(value) & {'definitions', 'foundation', 'program', 'version'}
    matrix = d.c.read(d.OUT / 'FIRST-TOKEN-MATRIX.json')['records']
    for eid in range(1, 7):
        a, b = [next(r for r in matrix if r['track'] == track and r['episode_id'] == f'R6.48/E{eid:02d}' and r['penalty'] == 1.0)
                for track in ('base', 'adapter')]
        assert b['raw']['raw_opening']['probability'] > a['raw']['raw_opening']['probability']
    assert all(r['processed']['top']['id'] == 73594 for r in matrix)


def audit():
    """Separate ordinary JSON parsing from native bounded serialization acceptance."""
    records = []
    for p in sorted(d.OUT.glob('CONTINUATION-*.json')):
        r = d.c.read(p)
        if 'completed_text' not in r:
            continue
        text = r['completed_text']
        try:
            value = json.loads(text)
            parsed = isinstance(value, dict)
            keys = list(value) if parsed else []
            error = None
        except json.JSONDecodeError as exc:
            parsed, keys = False, []
            error = {'offset': exc.pos, 'detail': exc.msg}
        records.append({'track': r['track'], 'episode_id': r['episode_id'], 'penalty': r['penalty'],
            'ordinary_json_object_parses': parsed, 'ordinary_parser_error': error, 'top_level_keys': keys,
            'missing_keys': sorted(set(['definitions', 'foundation', 'program', 'version']) - set(keys)),
            'native_output_valid': r['scores']['output_valid'], 'native_diagnostic': r['scores'].get('native_diagnostic'),
            'terminal_token_id': r['output_token_ids'][-1]})
    assert all(r['ordinary_json_object_parses'] for r in records)
    assert all(r['terminal_token_id'] == 151645 for r in records)
    d.write('PARSE-STAGE-AUDIT.json', {'records': records, 'ordinary_json_parses': sum(r['ordinary_json_object_parses'] for r in records),
        'correction': 'initial descriptive draft conflated output_valid (native bounded loader) with json.loads; raw results and all original analysis artifacts retained',
        'note': 'native string-bound rejection precedes package shape; ordinary syntax is not admitted serialization'})
    for r in records:
        print(r['track'], r['episode_id'], r['penalty'], r['top_level_keys'], r['native_diagnostic'])


if __name__ == '__main__':
    if sys.argv[1] == 'summarize':
        summarize()
    elif sys.argv[1] == 'audit':
        audit()
    elif sys.argv[1] in ('seal', 'verify'):
        publish(sys.argv[1] == 'seal')
    else:
        raise ValueError(sys.argv[1])
