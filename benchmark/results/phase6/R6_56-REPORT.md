# R6.56 — Complete training freeze; first run stops on reserved-VRAM limit

**Final classification: `R6_56_RESOURCE_OR_STACK_GAP`.**

Preflight passes with the complete authorized sampling, loss, optimizer and scheduler
configuration. All six unchanged-base diagnostic calls complete. The **one training
attempt** stops during its first accumulation window when the CUDA monitor detects
peak reserved memory **above8GiB**. Three completed microbatches are logged;
**0/20 optimizer updates and0 scheduler updates** occur. No trained adapter exists.
No restart, fallback, hyperparameter change or additional training run is performed.

## Authorization, preflight and preservation

R6.56 explicitly fixes deterministic E01-E06 cycling and equal-record accumulation
loss, conditional on complete preflight. The pre-existing untracked R6.55 publication
files are preserved. R6.53-R6.55 remain their original protocol halts; no historical
classification is changed.

[Preflight](r6_56/PREFLIGHT.json), [source identities](r6_56/SOURCE-PREFLIGHT.json)
and [six-record manifest](r6_56/SOURCE-DATASET-IDENTITIES.json) verify:

- All5,387 inherited protected identities; production32, VM21, wrapper27,
  R6.23 adapter79, tool contracts48 and registry11. Kernel remains **26**.
- R6.52-R6.55 publication payload hashes and receipt/manifest bindings; inherited
  R6.49-R6.51 publications and admission provenance.
- All47 installed distribution trees/RECORD identities, private Python executable/DLL,
  venv executable, uv and full package lock. Python3.12.11, torch2.7.1+cu128,
  Transformers4.55.4, PEFT0.17.1 and BitsAndBytes0.47.0 remain pinned.
- All9 base checkpoint/tokenizer assets and3 prior untrained-adapter files.
  `Qwen/Qwen2.5-Coder-1.5B-Instruct`, revision
  `2e1fd397ee46e1388853d2af2c993145b0f1098a`; no alternate model or download.
- Native chat template and exact E01-E06 conversion/provenance/token/label identities.
  Completion+turn EOS only; prompt, post-EOS newline and padding labels=-100.
  All records fit2048; overflow rejects and no truncation/packing occurs.
- Installed AdamW signature/module identity, exact R6.54 schedule source and all20
  planned update/post-update rates, complete80-presentation order, numerical
  accumulation control and prospective scorer controls.

No additional genuinely missing training parameter is identified. Model loading
for training occurs only after the configuration gate and baseline diagnostics.
Publication verification rechecks protected/external/package identities after the abort.

## Frozen sampling, normalization and configuration identities

[Sampling manifest](r6_56/SAMPLING.json) records each presentation's episode,
optimizer step and microbatch index. It starts E01, cycles E01/E02/E03/E04/E05/E06
without shuffle, and contains exactly80 planned presentations grouped four per step.
Planned counts: E01/E02 each14; E03-E06 each13. These are **planned**, not actual
exposure counts after the resource abort.

Sampling canonical SHA256:
`07e8775fe3c438467b42e659a429c89c00d3b834ed3571a8ddcc3c192cf8faf0`.

[Normalization specification/control](r6_56/LOSS-NORMALIZATION.json) applies installed
causal shifted token loss with ignore_index=-100 and no num_items_in_batch. Each
record's mean completion+EOS loss is divided by4 before backward. Four such calls
would precede one clipped update. No pooled-token weighting is substituted.

The CPU numerical control uses supervised counts1/2/3/4:

| Check | Observed value |
| --- | --- |
| Accumulated equal-record mean | 0.7600901946425438 |
| Independently calculated equal-record mean | 0.7600901268588703 |
| Pooled-token mean negative control | 0.8340901268588704 |
| Accumulated gradient | 0.35399167984724045 |
| Independent gradient | 0.35399171247704597 |

Loss/gradient differences are below1e-6; pooled weighting differs. This is a
deterministic synthetic numerical control, not trained-model learning evidence.

[Complete training configuration](r6_56/TRAINING-CONFIGURATION.json) canonical SHA256:
`2b0fa8ee329e4cfa9e3d46c53151c2d266dd213fd7f62f8959d25a2ac3e0918b`.

It retains NF4/double-quant/BF16; r8/alpha16/dropout0.05 q/v, bias none;
FP32 adapter parameters; seed651 and exact R6.52 adapter initialization required;
length cap2048, microbatch1, accumulation4; non-reentrant gradient checkpointing,
SDPA/cache off, no CPU offload/compile/packing/truncation; clipping norm2/max1;
adapter-only updates; checkpoints10/20 with at most two retained; timeout1800s,
RSS16GiB, reserved CUDA8GiB and minimum device-free1.5GiB. The embedded R6.52
adapter configuration is its saved initialization configuration; training activates
trainable LoRA tensors and train mode, as in the qualified R6.52 construction.

[AdamW configuration](r6_56/OPTIMIZER-CONFIGURATION.json) is the exact R6.55 freeze:

```text
lr=1e-4; betas=(0.9,0.999); eps=1e-8; weight_decay=0;
amsgrad=False; maximize=False; foreach=None; capturable=False;
differentiable=False; fused=None
```

Optimizer canonical identity:
`22b189e27a4a592366864fdf247fa2c446b9eca4c802802b9817153f08a26be1`.
R6.54 schedule file identity:
`9dfccd8545d1d3e30324b803185c3ce995ec0964f3e9363ceb0fe0653b083711`.
The constructor installs LR0; successful update s would use LR(s-1), followed by
one scheduler tick installing LR(s). No actual update uses any LR in this attempt.

### Preserved pre-update assertion correction

The original worker compared optimizer.defaults to only the public AdamW arguments.
Installed AdamW inherits Adam and additionally inserts the invariant internal field
decoupled_weight_decay=True. Inspection caught that assertion mismatch **before any
training dispatch**. Only the assertion was corrected to include that implementation
field; optimizer arguments, full configuration identity, prompts and decoding were unchanged.

[Correction receipt](r6_56/PREUPDATE-ASSERTION-CORRECTION.json) binds original/corrected
worker source and [original preflight](r6_56/PREFLIGHT-INITIAL.json). Original worker
bytes remain in `WORKER-INITIAL.py.txt`; the prospective preflight binds corrected
bytes. This is not a new optimizer setting or outcome-informed training retry.

## Frozen unchanged-base diagnostics

[Diagnostic protocol](r6_56/DIAGNOSTIC-PROTOCOL.json) freezes the existing six exact
converter prompts and admission-bound acceptance fixtures before model output.
These are **resubstitution / exposed training-development** records, not unseen data.
No new panel, independent withheld source or extra training record is introduced.

Both proposed tracks use the same NF4 base and k-bit preparation, native template,
eval mode, one greedy sequence, max_new_tokens1400 and total context<=2048,
EOS-only termination, cache off, no repair/seal tool calls,120s hard process limit
per item. The limit includes model loading and is stricter than generation-only120s.
All other pinned checkpoint generation settings remain recorded, including
repetition_penalty1.1. The retained temperature/top_p/top_k fields are inactive
with do_sample=false; the framework's corresponding warnings are preserved.

[Scorer controls](r6_56/SCORER-CONTROLS.json) qualify the pinned schema's used keywords,
native type/semantic validation and deterministic literal acceptance against all six
admitted targets; bad-type and duplicate-key controls reject. This prospective scorer
qualification leaves historical acceptance scores untouched. Scoring never changes
generated seals or strips markdown. Raw responses and token IDs are retained.

[Base summary](r6_56/DIAGNOSTIC-BASE-SUMMARY.json):

| Diagnostic | Base result | Trained adapter |
| --- | --- | --- |
| Completed calls | 6/6 | NOT_REACHED |
| Strict JSON/output validity | 0/6 | NOT_REACHED |
| Schema validity | 0/6 | NOT_REACHED |
| Native type correctness | NOT_REACHED on all6 | NOT_REACHED |
| Semantic validation | 0/6 accepted | NOT_REACHED |
| Full diagnostic functional acceptance | 0/6 accepted; executable cases NOT_REACHED | NOT_REACHED |
| Exact / normalized training target reproduction | 0/6 /0/6 | NOT_REACHED |
| Generated tokens, including EOS | 244 | NOT_REACHED |
| Sum of generation wall times | 16.2174442s | NOT_REACHED |

All six responses are markdown-fenced snippets rather than the required complete
raw JSON package; native serialization is the first blocker. This establishes failure
of the frozen raw-output interface, not a measured execution/type verdict on a repaired
representation. No markdown extraction, repair or target seal assistance is performed.
Each call is fresh-process; load/process timings and per-call inference GPU peaks are
retained separately. **Base inference** peak reserved2,520,776,704 bytes (~2.35GiB)
is not reused as the missing training VRAM peak.

## Single training attempt and actual resource halt

[Exclusive run claim](r6_56/TRAINING-RUN-CLAIM.json) and
[process receipt](r6_56/TRAINING-PROCESS.json) document one dispatch. Model initialization
matches all112 historical adapter tensor identities (1,089,536 trainable parameters).
[Initial parameters](r6_56/INITIAL-PARAMETERS.json) bind adapter tensors and frozen
base parameters/buffers/quantization state before the first microbatch.

The loop begins at E01 and accumulates each mean loss divided by4. Completed logged
microbatches in [partial measurements](r6_56/MICROSTEPS.json):

| Presentation | Record | Mean record loss | Supervised tokens |
| --- | --- | ---: | ---: |
| 1 | E01 | 1.8160520792007446 | 329 |
| 2 | E02 | 1.7120777368545532 | 370 |
| 3 | E03 | 1.517041563987732 | 425 |

These are three **different records before any update**, not a loss-learning curve.
Logged totals:3 presentations,1,124 supervised tokens and2,281 full-sequence tokens.
The fourth E04 presentation may have been in flight; its progress/loss/token exposure
was not atomically retained and is not added to those completed/logged totals.

The100ms CUDA monitor calls memory() and detects peak reserved bytes>8,589,934,592.
[Abort packet](r6_56/RESOURCE-ABORT.json) records CUDA_RESERVED_LIMIT, completed_steps0,
presentations3; process exits71. **0 optimizer updates,0 scheduler ticks**, no gradient
norm measurement and no full accumulation-window/optimizer-step loss are recorded.
The parent does not restart the process. No silent allocator, length, batch, precision,
model or optimizer fallback is introduced.

[Training measurements](r6_56/TRAINING-MEASUREMENTS.json) explicitly retain limitations:

- Whole worker process wall time **13.589081s**, including model loading and abort.
  Training-loop-only time was not retained and is null.
- Exact allocated/reserved training peaks are **unavailable**. The limit assertion
  occurs before memory() returns its values, and the abort packet records the reason
  but not numeric peaks. Only the strict lower bound **reserved>8GiB** is supported.
  This is an explicit telemetry defect, not permission to reconstruct a peak from
  R6.52 probes or base inference.
- External WorkingSetSize polling reports4,939,776 bytes (~4.7MiB), inconsistent with
  full model-process residency. Windows venv launcher/worker process-tree coverage
  was not attested. This value is retained as a raw observation, **not qualified
  worker RSS or successful enforcement of the16GiB worker limit**.
- No CUDA OOM or numerical error is reported; the reserved-memory threshold abort
  occurs first. The all-gradient finite check, clipping and per-update frozen-base
  hash comparisons are not reached. Their unexecuted success is not claimed.

R6.52's two no-update probes did not qualify the actual four-record accumulation
window or memory telemetry. This round demonstrates that the implemented loop stops
on its reserved-memory bound; it does not establish accumulation/optimizer feasibility
under the unchanged bounds. The cause of the higher reservation is not diagnosed here.

## Adapter, comparison and memorization outcomes

[Deliverable status](r6_56/EVALUATION-AND-ADAPTER-STATUS.json) and
[terminal result](r6_56/RESULT.json) distinguish missing outcomes:

- No step10/20 checkpoint, trained adapter, adapter content identity or parameter-change
  verification. No adapter merge or full-model save.
- Fresh-process trained reload and trained inference initialization NOT_REACHED.
- Base-versus-trained comparison, trained schema/type/semantic/functional scores and
  trained target reproduction NOT_REACHED.
- Learning/memorization effects **not measured**; no optimizer update occurred. Neither
  no-learning classification nor a supported LoRA smoke is justified.
- External base checkpoint/tokenizer and prior untrained adapter hashes match after the
  attempt. No in-memory post-update base check is claimed because no update occurred.

Only process stdout/stderr are present under the temporary artifact directory
`C:\Users\lblan\AppData\Local\Temp\opencode\lykoi-r6-52\r6-56`;
[external artifact identities](r6_56/EXTERNAL-ARTIFACTS.json) bind them. The repository
retains their contents in process receipts. This directory contains no trained adapter.

## Remaining limitations and smallest next step

Complete configuration and baseline diagnostics are now available. First training
feasibility under8GiB reserved memory is **not** established. Exact abort-peak retention
and Windows actual-worker RSS coverage are additional instrumentation gaps. Six related
records and same-record diagnostics would remain insufficient for broad generalization,
even if a later separately authorized run succeeded.

Smallest recommendation: separately authorize a **no-optimizer-update resource and
telemetry diagnosis** of the fixed four-record accumulation window, preserving this
failed attempt. Capture numeric peaks before abort and identify the actual Python/CUDA
worker in the external RSS monitor. Diagnose reservation behavior before proposing
any prospective change. A new training attempt would need explicit separate authorization;
no retry or resource/hyperparameter amendment is authorized or performed here.

## Publication integrity and preservation boundaries

[Publication manifest](r6_56/PUBLICATION-IDENTITIES.json) binds frozen configuration,
original/corrected assertion evidence, raw diagnostics, failure artifacts, source,
report and versioned companion documents. Verification rechecks canonical identities,
protected history/external assets/all47 package trees, additive path scope, source/JSON,
links/whitespace/credential patterns and `git diff --check`.

The first publication gather command encountered a module-name collision with the
historical run.py after its import path was added. The publication-only helper was
corrected to use an explicit file-qualified import; the corrected gather passed.
Frozen model worker, hyperparameters, diagnostics, training attempt and history
were unaffected. No model process was dispatched by publication work.

The initial seal also rejected the worker's native Windows CRLF run-claim receipt.
Publication verification now permits CRLF only for that exact raw receipt, preserving
its original bytes; other publication text remains LF-only. No experiment payload was
normalized or rewritten to satisfy the check.

Production compiler/lowerer/runtime and experimental semantics remain unchanged;
kernel26; new execution primitives0; dataset expansion0; Python comparison adapters0;
training attempts1, retries0; P6-A04 acceptance executions0; P6-A05 access false.
AI-independent deterministic execution is preserved.

**Stopped after the single bounded attempt, available evaluation and publication.
Await explicit authorization before further work.**
