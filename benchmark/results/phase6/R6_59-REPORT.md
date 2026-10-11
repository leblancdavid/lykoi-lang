# R6.59 — First completed Lykoi QLoRA smoke with controlled cache release

**Final classification: `R6_59_LORA_SMOKE_SUPPORTED`.**

The single authorized attempt completed **20/20 optimizer updates**,20 scheduler
ticks and80 microbatches. All112 LoRA tensors changed; frozen base tensors,
buffers and quantization state remained exact. Step20 adapter save and fresh-process
reload passed, including bitwise-equal finite reference logits. Controlled cache
release preserved accumulated gradient bytes across all80 releases. There was no
CUDA, numerical, resource, optimizer or serialization failure and no retry.

This supports bounded training/save/reload mechanics. Repeated-record supervised
loss decreased, but **strict output and functional diagnostic acceptance remain
0/6 for both base and trained adapter**. No generalization benefit is established.

## 1. Authorization, preservation and complete freeze

Initial git status was clean. Before adding R6.59 files, the existing R6.58 publication
verifier passed. [Baseline](r6_59/BASELINE.json) rechecks R6.52–R6.58 publication
payloads, all5,387 inherited protected identities, all47 installed package trees,
checkpoint/tokenizer and prior untrained adapter. Publication verification repeats
the checks after training and diagnostics. R6.53–R6.58 halts, raw failures and the
R6.58 diagnostic scheduler-assertion failure remain unchanged.

The [executable identity supplement](r6_59/EXECUTABLE-IDENTITY-SUPPLEMENT.json)
additionally confirms exact R6.52 private Python executable/DLL, venv launcher,
uv executable and lock hashes. These specific binary hashes were freshly measured
at publication, not before dispatch: the inherited pre-dispatch verifier covered
installed package trees/checkpoint but omitted fresh executable hashes. No binary
change occurred in this round; an independently recorded pre-dispatch binary-hash
observation is not claimed.

The [protocol](r6_59/PROTOCOL.md), [preflight](r6_59/PREFLIGHT.json) and
[configuration](r6_59/TRAINING-CONFIGURATION.json) bind:

- `Qwen/Qwen2.5-Coder-1.5B-Instruct`, revision
  `2e1fd397ee46e1388853d2af2c993145b0f1098a`.
- Existing Python3.12.11/torch2.7.1+cu128/Transformers4.55.4/PEFT0.17.1/BNB0.47.0;
  offline local-only loads, no dependency, checkpoint or tokenizer changes.
- NF4/double quantization/BF16; rank8/alpha16/dropout0.05 q/v attention adapters,
  FP32 adapter parameters; seed651, exact R6.52 initial112 tensors.
- Sequence cap2048, microbatch1, gradient accumulation4, unchanged checkpointing/
  SDPA/cache-off preparation, no packing/truncation/offload/precision fallback.
- Fixed E01–E06 cyclic sampling,80 presentations, equal per-record completion+EOS
  mean loss/4, unchanged causal-shift/ignored-label normalization.
- R6.55 AdamW: lr1e-4, betas(0.9,0.999), eps1e-8, **weight_decay0**,
  amsgrad/maximize/capturable/differentiable false, foreach/fused None.
- R6.54 linear20-step schedule with2 warmup steps; unchanged norm2/max1 clipping,
  checkpoints10/20 and two-checkpoint retention.
- Reserved8GiB, device-free1.5GiB, actual worker RSS16GiB,1800s process timeout.

The inherited configuration bytes and historical round fields remain exact;
R6.59's amendment is separately bound by the protocol and effective worker source.
Complete R6.56 configuration canonical identity:
`2b0fa8ee329e4cfa9e3d46c53151c2d266dd213fd7f62f8959d25a2ac3e0918b`.
Sampling identity:
`07e8775fe3c438467b42e659a429c89c00d3b834ed3571a8ddcc3c192cf8faf0`.
AdamW identity:
`22b189e27a4a592366864fdf247fa2c446b9eca4c802802b9817153f08a26be1`.

## 2. Controlled cache release and instrumentation qualification

The [worker](../../../experiments/lora_smoke_r6_59/worker.py) applies explicit
single-match transformations to the unchanged R6.56 worker. The complete
[effective source](r6_59/EFFECTIVE-WORKER.py.txt) is saved and frozen before dispatch;
publication reconstructs it exactly. The model, optimizer, scheduler, scoring,
save/reload helpers and semantic foundations remain inherited.

Every microbatch completes backward **before** retaining its scalar loss. The worker
records loss, deletes output/loss/input/label references, synchronizes, records memory
and checks finite LoRA gradients/frozen-base gradient absence. It hashes all current
accumulated gradients, calls `torch.cuda.empty_cache()`, records allocated/reserved/
device-free memory, then requires exact gradient hashes. No gradient clearing occurs
between microbatches.80/80 checks pass; the only gradient clears are inherited
initial/window-boundary and terminal behavior. The
[qualification receipt](r6_59/CACHE-RELEASE-QUALIFICATION.json) binds the preserved
R6.58 no-update evidence; no extra GPU qualification or training run occurred.

No optimizer or scheduler method is reassigned by R6.59 instrumentation. Counters
increment externally after native calls return; state_dict/defaults/parameter-group
values are inspected read-only. A [CPU-only synthetic twin control](r6_59/ACCOUNTING-QUALIFICATION.json)
shows exact parameter, AdamW-moment and scheduler-state equality across20 updates
with/without read-only inspection. This verifies this instrumentation path, not an
independent optimizer implementation. It adds no trained-model updates.

The [final accounting](r6_59/UPDATE-ACCOUNTING.json) contains optimizer_calls20,
scheduler_calls20, all112 AdamW state steps20, scheduler last_epoch20 and final LR0.
Scheduler `_step_count=21` includes the inherited constructor's initial tick; there
are20 post-optimizer ticks, not21 training updates. No added `step` callable appears
in serialized scheduler state. The R6.58 failing assertion is preserved as history.

## 3. Actual losses, rates, gradients and memory

[Training steps](r6_59/TRAINING-STEPS.json) retain all20 mean losses, four record
losses per update, LR used/after tick, preclip norm, tokens, timings, memory and exact
base-identity assertions. [Microsteps](r6_59/MICROSTEPS.json) retain all80 losses,
episode presentations, supervised counts, release-boundary memory and gradient
identities. E01/E02 appear14 times each; E03–E06 appear13 times each.

| Record | First presentation loss | Last presentation loss | Relative decrease |
| --- | ---: | ---: | ---: |
| E01 | 1.816052 | 1.664219 | 8.36% |
| E02 | 1.712078 | 1.555900 | 9.12% |
| E03 | 1.517042 | 1.387161 | 8.56% |
| E04 | 1.464548 | 1.345058 | 8.16% |
| E05 | 1.870430 | 1.704717 | 8.86% |
| E06 | 1.501986 | 1.381912 | 7.99% |

Step1 mean loss1.627430 and step20 mean1.576687 use different four-record groups;
they are not a clean paired endpoint comparison. Same cyclic-group endpoints are
step1→19:1.627430→1.488823; step2→20:1.725136→1.576687;
step3→18:1.583618→1.458731. These are train-mode teacher-forced observations
with frozen dropout0.05 and changing parameters, not a dropout-off evaluation.

All per-update preclip norms are finite, range0.410838–0.493869, below clipping
threshold1. All trainable gradients/parameters pass finite checks and frozen-base
gradients remain absent. Base parameters/buffers/quantization state match after
every update. The first successful AdamW update uses LR0, as frozen: it advances
moments/counters without a learning-rate-driven parameter change. Later rates
are5e-5,1e-4, then linear decay to5.5555555556e-6 at update20; the final scheduler
tick installs0. Every observed rate matches the original schedule exactly.

| Measurement | Actual result |
| --- | ---: |
| Optimizer / scheduler updates | 20 /20 |
| Completed presentations / cache releases | 80 /80 |
| Peak allocated VRAM | 3,889,410,048 bytes (3.622GiB) |
| Peak reserved VRAM | 4,620,025,856 bytes (4.303GiB) |
| Minimum retained sampled/boundary device-free memory | 6,975,127,552 bytes (6.496GiB) |
| Training-loop wall time, including checkpoint/integrity overhead | 57.550900s |
| Whole training subprocess, including initialization/reference/exit | 71.669301s |
| CUDA / numerical / resource failures | 0 /0 /0 |

Peaks are cumulative actual PyTorch allocator values, reset once before model load.
The device-free minimum includes the100ms watchdog aggregate and retained release
boundaries; it is not a continuously measured global minimum. Reservations stay below
8GiB and all retained free observations above1.5GiB. Actual worker RSS is checked
in-process using its own PID; numeric RSS peaks are not retained. No exclusive GPU
isolation or per-process WDDM byte attribution is claimed. Synchronization, CPU hash
copies, telemetry and base verification contribute overhead; this is not throughput
or efficiency qualification.

## 4. Adapter artifacts and fresh-process reload

Checkpoints10 and20 saved successfully, with adapter-only safetensors, tokenizer,
optimizer/scheduler/RNG state and provenance. No merge or full-model save occurs.
[Checkpoint20 identities](r6_59/CHECKPOINT-20.json) and
[all external artifacts](r6_59/EXTERNAL-ARTIFACTS.json) bind exact file bytes.

Final adapter directory:
`C:\Users\lblan\AppData\Local\Temp\opencode\lykoi-r6-52\r6-59\step20\adapter`.
This remains temporary storage; published hashes identify it but do not make it durable.

- `adapter_model.safetensors`:4,372,840 bytes, SHA256
  `79843df8ce1f3e9bf87c81e0e23073c37a702695df6e52ac384b0a33f77fb7d1`.
- `adapter_config.json` SHA256:
  `642b816c81121fb0bf251550885b1ae30ca89c2cb824f4b4a2cd2c1caf657050`.
- Canonical adapter-directory manifest identity:
  `d8bbe876eca1e5929a0bd570e44fb661d4eb1cdb5ebf8e857c3ee659923ab58a`.
- All112 adapter tensors differ from initial R6.52 values;1,089,536 parameters.

[Fresh-process reload](r6_59/ADAPTER-RELOAD.json) passes exact trained tensor/file
identity, frozen base/buffer/quantization equality, finite four-token reference
logits and bitwise comparison to the trained process (max difference0).
Reload process exits0 in10.710873s. Saved optimizer/scheduler state is hash-bound;
resuming training or testing resumability is not authorized or performed.

The inherited PEFT local-path normalization warning and offline save vocabulary
warning are retained in [training process output](r6_59/TRAINING-PROCESS.json).
Public model/revision bindings are restored before save by the unchanged helper;
reload proves the actual exact base identity. Saved tokenizer serialization files
differ bytewise from downloaded files; inference still uses the unchanged pinned
checkpoint tokenizer, as frozen. No tokenizer modification for learning occurred.

## 5. Frozen base-versus-adapter comparison

[Baseline reuse](r6_59/BASELINE-REUSE.json) validates exact R6.56 diagnostic results,
prompts, scorer, schema, acceptance fixtures and checkpoint/generation settings.
No base inference rerun was performed. Offline publication rescoring of preserved
raw base and new adapter outputs reproduces their original scores exactly.

All six adapter calls use fresh processes and the same greedy decoding,
max_new_tokens1400/context cap2048, cache off, repetition_penalty1.1, EOS-only
termination and120s process limit. Inactive sampling flags produce retained
framework warnings. No markdown stripping, repair, semantic sealing or prompt change.
[Comparison](r6_59/DIAGNOSTIC-COMPARISON.json) retains every score and token/time pair.

| Metric | Frozen base | Step20 adapter |
| --- | ---: | ---: |
| Completed calls | 6/6 | 6/6 |
| Strict output validity | 0/6 | 0/6 |
| Schema validity | 0/6 | 0/6 |
| Type correctness | NOT_REACHED on6 | NOT_REACHED on6 |
| Semantic acceptance | 0/6 | 0/6 |
| Full functional acceptance | 0/6 | 0/6 |
| Executable functional cases | NOT_REACHED | NOT_REACHED |
| Exact / normalized target reproduction | 0/6 /0/6 | 0/6 /0/6 |
| Generated tokens including EOS | 244 | 217 |
| Sum generation wall time | 16.217444s | 16.727540s |

Every base and trained response is markdown-fenced; all hit native serialization
failure before type checking or execution. Consequently0 accepted is not evidence
of incorrect runtime semantics for a valid generated program. E02 output changes;
the other five outputs remain exact. No strict/schema/semantic/functional metric
improves. Different output lengths, historical baseline timing and uncontrolled
device load preclude an inference-efficiency conclusion.

## 6. Learning, memorization, limits and recommended next experiment

Parameter change and consistently lower repeated-record teacher-forced losses are
evidence of fitting the exposed training targets. They do not establish learning
of reusable semantics or successful free generation. Neither exact nor normalized
target reproduction is observed; that does not rule out partial memorization.
Six related records,13–14 repeated presentations and same-record diagnostics cannot
separate task learning from memorization or establish broad generalization.

Remaining limitations include the raw-output serialization blocker, train-mode
dropout confounding a precise fixed-input loss comparison, no independent unseen
evaluation, sampled resource accounting, no exclusive GPU containment, temporary
adapter storage, and no training-resume qualification. The supported classification
means20 updates, verified adapter changes and fresh reload; it does not require or
imply improved generalization. `NO_OBSERVED_LEARNING` would obscure the actual
parameter change and training-loss fit, so it is not the selected classification.

**Recommended next experiment:** separately authorize a read-only, fixed-input
paired teacher-forced evaluation of the unchanged base and saved step20 adapter
on these same six records with dropout off. Freeze scoring/masks before dispatch,
retain per-record loss and timings, and preserve the current free-generation failure.
This would quantify repeatable target fitting; it would still be exposed
resubstitution evidence. No additional training, dataset expansion or hyperparameter
search is recommended as an automatic continuation.

## 7. Publication and stop

[Publication identities](r6_59/PUBLICATION-IDENTITIES.json) bind source, protocol,
freeze, raw process results, loss/memory/accounting, checkpoint/reload/comparison,
analysis and versioned documentation. [Verification](r6_59/VERIFICATION.json)
rechecks protected history/environment, frozen effective source, all external
artifacts, JSON/Python, links, whitespace/credential patterns and `git diff --check`.

Production kernel remains26; production compiler/lowerer/runtime and experimental
semantics unchanged. New execution primitives0; dataset expansion0; Python comparison
adapter0; training attempts1; retries0; base diagnostic reruns0; P6-A04 acceptance
executions0; P6-A05 access false. AI-independent deterministic execution preserved.

**Stopped after the single attempt, authorized verification and publication.
Await explicit authorization before further work.**
