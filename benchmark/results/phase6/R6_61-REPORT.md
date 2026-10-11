# R6.61 — First-token decoding and minimal-prefix continuation diagnosis

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
at `<|im_start|>assistant\n`; no extra roles, instructions or keys supplied.

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
| base | E01 | 1.0 | 13.775663 | 0.081761 | 3 | 15.373813 | 0.404216 | 1 | -0.322455 |
| base | E01 | 1.1 | 12.523330 | 0.026076 | 5 | 15.373813 | 0.451015 | 1 | -0.424939 |
| base | E02 | 1.0 | 13.792407 | 0.069467 | 3 | 15.587447 | 0.418175 | 1 | -0.348707 |
| base | E02 | 1.1 | 12.538551 | 0.022374 | 5 | 15.587447 | 0.471918 | 1 | -0.449543 |
| base | E03 | 1.0 | 13.184737 | 0.048409 | 3 | 15.338840 | 0.417296 | 1 | -0.368886 |
| base | E03 | 1.1 | 11.986124 | 0.015697 | 6 | 15.338840 | 0.448636 | 1 | -0.432939 |
| base | E04 | 1.0 | 13.488997 | 0.065089 | 3 | 15.384401 | 0.433184 | 1 | -0.368095 |
| base | E04 | 1.1 | 12.262724 | 0.021046 | 5 | 15.384401 | 0.477409 | 1 | -0.456364 |
| base | E05 | 1.0 | 13.841341 | 0.060236 | 3 | 15.827394 | 0.438926 | 1 | -0.378690 |
| base | E05 | 1.1 | 12.583036 | 0.018667 | 5 | 15.827394 | 0.478712 | 1 | -0.460045 |
| base | E06 | 1.0 | 14.053001 | 0.079000 | 3 | 15.715037 | 0.416335 | 1 | -0.337334 |
| base | E06 | 1.1 | 12.775455 | 0.024584 | 5 | 15.715037 | 0.464831 | 1 | -0.440247 |
| adapter | E01 | 1.0 | 13.839259 | 0.090996 | 3 | 15.352062 | 0.413070 | 1 | -0.322074 |
| adapter | E01 | 1.1 | 12.581144 | 0.029024 | 5 | 15.352062 | 0.463608 | 1 | -0.434584 |
| adapter | E02 | 1.0 | 13.837284 | 0.078080 | 3 | 15.502565 | 0.412822 | 1 | -0.334742 |
| adapter | E02 | 1.1 | 12.579349 | 0.025358 | 5 | 15.502565 | 0.471687 | 1 | -0.446329 |
| adapter | E03 | 1.0 | 13.292693 | 0.055313 | 3 | 15.334090 | 0.425988 | 1 | -0.370674 |
| adapter | E03 | 1.1 | 12.084266 | 0.017915 | 5 | 15.334090 | 0.461950 | 1 | -0.444035 |
| adapter | E04 | 1.0 | 13.541807 | 0.072017 | 3 | 15.350579 | 0.439514 | 1 | -0.367497 |
| adapter | E04 | 1.1 | 12.310734 | 0.023360 | 4 | 15.350579 | 0.488264 | 1 | -0.464904 |
| adapter | E05 | 1.0 | 13.892895 | 0.068117 | 3 | 15.773207 | 0.446544 | 1 | -0.378427 |
| adapter | E05 | 1.1 | 12.629904 | 0.021144 | 5 | 15.773207 | 0.490125 | 1 | -0.468981 |
| adapter | E06 | 1.0 | 14.106735 | 0.092077 | 3 | 15.598452 | 0.409256 | 1 | -0.317179 |
| adapter | E06 | 1.1 | 12.824305 | 0.028955 | 4 | 15.598452 | 0.464005 | 1 | -0.435050 |

### Rank summary (penalty1.0 /1.1)

| Record | Base opening rank | Adapter opening rank |
| --- | ---: | ---: |
| E01 | 3 / 5 | 3 / 5 |
| E02 | 3 / 5 | 3 / 5 |
| E03 | 3 / 6 | 3 / 5 |
| E04 | 3 / 5 | 3 / 4 |
| E05 | 3 / 5 | 3 / 5 |
| E06 | 3 / 5 | 3 / 4 |

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
does not imply raw *package* format:22 outputs immediately choose a top-level key
outside the exact required envelope; both E05/1.0 outputs use an invalid version
value and omit the remaining required envelope. Raw continuation `.txt` and complete token
IDs/text/configuration/scores in matching `CONTINUATION-*.json` are preserved.
Text scoring removes only the final EOS; no normalization, fence stripping or seal.

| Model | Penalty | Ordinary JSON parses | Native bounded output_valid | Schema passes | Type /semantic stages | Functional reached /passes |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| Base | 1.0 | 6/6 | 1/6 | 0/6 | NOT_REACHED6 | 0/6 /0/6 |
| Base | 1.1 | 6/6 | 6/6 | 0/6 | NOT_REACHED6 | 0/6 /0/6 |
| Adapter | 1.0 | 6/6 | 1/6 | 0/6 | NOT_REACHED6 | 0/6 /0/6 |
| Adapter | 1.1 | 6/6 | 6/6 | 0/6 | NOT_REACHED6 | 0/6 /0/6 |

[Validation results](r6_61/VALIDATION-RESULTS.json) retain native failures and
unchanged scorer observations. Its boolean semantic_valid=false is failure to
achieve validation, not evidence of a reached semantic runtime test. Independent
deterministic schema/native validation and E01–E06 fixture execution were frozen
before generation; execution remains unreachable for all24. No historical rescoring.

All24 completed texts parse as ordinary JSON objects. At1.0 E01–E04/E06 echo the
user prompt's required_output/requirement/vocabulary object; the unchanged native
loader rejects their long strings as RESOURCE/string bound before package shape
validation. E05 emits `{"version":7,"count":0}`. At1.1 every output is a small answer
snippet, not the definitions/foundation/program/version package. Example E01,
both models: `{"result":137,"result_type":"Int64"}`. Adapter E05 differs:
`{"result":true,"message":"The provided input meets the specified requirements."}`.
All other base/adapter pairs are byte- and token-identical: **11/12 pairs**,
including all six at1.0. Neither changed E05 output is accepted.

## 5. First divergence: formatting versus construction

Historical unprefilled generation first diverged at token0/character0 (fence73594)
on all12 calls; original [R6.60 inventory](r6_60/FIRST-DIVERGENCE.json) is preserved.
This round's distributions measure that preference without rerunning those outputs.

Twenty-two supplied-prefix continuations diverge from the package envelope at
completed-text character2, continuation token0: first key required_output or result
is outside the admitted package keys. E05/1.0 on both models instead diverges at
character11, continuation token2, version value7 rather than the required string
typed-composition-1. This field-level observation is separate from native rejection
at$ for missing/extra fields. [Supplement](r6_61/STRUCTURAL-DIVERGENCE-SUPPLEMENT.json)
retains initial first-key observations; [native inventory](r6_61/FIRST-DIVERGENCE.json)
records native paths, missing keys, EOS and repetition flags; the
[parse-stage audit](r6_61/PARSE-STAGE-AUDIT.json) clarifies ordinary syntax versus
bounded serialization; [version-value supplement](r6_61/VERSION-VALUE-DIVERGENCE.json)
records the remaining two earliest structural divergences.

| Record | Base tokens1.0 /1.1 | Adapter tokens1.0 /1.1 | Base native blocker1.0 /1.1 |
| --- | ---: | ---: | --- |
| E01 | 345 / 14 | 345 / 14 | RESOURCE / SHAPE |
| E02 | 354 / 19 | 354 / 19 | RESOURCE / SHAPE |
| E03 | 374 / 9 | 374 / 9 | RESOURCE / SHAPE |
| E04 | 366 / 14 | 366 / 14 | RESOURCE / SHAPE |
| E05 | 9 / 6 | 9 / 16 | SHAPE / SHAPE |
| E06 | 353 / 6 | 353 / 6 | RESOURCE / SHAPE |

Twenty-two objects lack all four required envelope keys. Both E05/1.0 outputs
contain version but omit definitions/foundation/program and add count; version7
fails the pinned schema constant. Lexical and structural keys are retained separately.
No ordinary JSON parse failure occurred. Typed labels
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
| base | 0.790666 | 134.557133 | 1869 | 2087705088 | 2522873856 | 202.506913 |
| adapter | 0.909336 | 144.451834 | 1879 | 2087705088 | 2527068160 | 357.054818 |

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

The initial descriptive draft conflated native bounded output_valid with ordinary
JSON parsing and guessed extra-brace failures. An offline audit also first matched
the new pair-comparison summary in its continuation glob and failed with KeyError.
[Correction](r6_61/OFFLINE-AUDIT-CORRECTION.json) preserves both analysis defects;
the separately published parse-stage audit and corrected report resolve them without
inference reruns, output repairs or scorer/semantic changes. Initial analysis artifacts
are retained; ordinary_json_object_parses in the audit is authoritative for syntax,
whereas output_valid in frozen scores retains the native bounded-loader meaning.
The first publication seal also stopped on a report self-link before its manifest
existed. [Ordering correction](r6_61/PUBLICATION-ORDER-CORRECTION.json) preserves
that failure; the [qualified publication entry point](../../../experiments/first_token_r6_61/qualified_publish.py)
replaces only exact pending placeholders for these new publication self-links.
This dispatches no model and changes no measurements or historical artifacts.
That first wrapper then collided with an inherited unqualified `publication`
module import; [import correction](r6_61/PUBLICATION-IMPORT-CORRECTION.json) retains
the failure. [Final offline entry point](../../../experiments/first_token_r6_61/qualified_publish_v2.py)
uses a unique module name. Both failed sources and receipts remain preserved.

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
