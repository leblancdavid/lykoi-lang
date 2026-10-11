# R6.67 — Incremental Lykoi QLoRA training and evaluation

**Final classification: `R6_67_TRAINING_MECHANICS_ONLY`.** The single authorized
attempt completed20 optimizer and20 scheduler updates with80 presentations. The
saved adapter reloads in a fresh process with unchanged base tensors and bitwise
identical reference logits. Teacher-forced target loss improves in all13 cases,
but strict valid action generation and functional acceptance remain **0/13 → 0/13**.
There is no demonstrated improvement in usable incremental construction.

## Frozen baseline and execution provenance

Initial git status was clean. [Preflight](r6_67/PREFLIGHT.json) verifies the R6.66
publication, all frozen payloads, readiness components, all13 diagnostic prompt
identities/gold acceptances and inherited full baseline audit before inference.
R6.65 scorer, R6.52 checkpoint/tokenizer, R6.59 infrastructure, R6.58 release
qualification and preserved kernel26 accounting pass. The same full preservation
audit passes at publication. Kernel26 is preserved accounting, not a new recount.

| Canonical identity | SHA256 |
| --- | --- |
| Dataset |`75b78ccf27a6043af05cb197fc4c36d73aebbfd244b6fcbc55087d635746daf9`|
| Sampling |`554dc5e8d15b2371088c10ed0c211fd570a58e1f586c1a58795dfb144015a38f`|
| Configuration |`b7f02ba671c78baf243148a4ed49b8e143775538bb5cbd82369ee2294d096ca5`|
| Exact effective worker bytes |`b648490af821996ddbb80a9362bce1c471ed036fe0cf17e5bf4612c8e3e63a89`|

The [additive runner](../../../experiments/incremental_training_r6_67/run.py)
executes the byte-identical R6.66 worker and reads immutable inputs directly from
R6.66. Only telemetry destinations are routed into r6_67; the frozen external
r6-66 checkpoint paths remain exact. Embedded R6.66 labels identify worker
provenance, not a second R6.66 experiment. No historical publication is rewritten.
Exclusive dispatch/run claims and captured process results retain the single
base/train/reload/adapter invocation sequence. All four processes return0.

Initialization uses the original pinned Qwen2.5-Coder-1.5B-Instruct checkpoint,
revision `2e1fd397ee46e1388853d2af2c993145b0f1098a`, never the R6.59 adapter.
NF4 double quantization/BF16 and fresh FP32 rank8 q/v LoRA, alpha16/dropout0.05,
seed651 and tokenizer are unchanged. All112 initial adapter tensor identities match
R6.52 before training. No base architecture change or adapter merge occurs.

## Training and resource measurements

[Training result](r6_67/TRAINING-RESULT.json), [updates](r6_67/TRAINING-STEPS.json),
[microbatches](r6_67/MICROSTEPS.json) and [accounting](r6_67/UPDATE-ACCOUNTING.json)
retain losses, learning rates, gradient norms, tokens, presentations and resources.

- Completed optimizer/scheduler updates: **20/20**, maximum20.
- Presentations: **80**, D01–D10 cyclic eight times, four records/update.
- Sequence tokens100,912; supervised completion+EOS tokens2,912.
- Equal per-record masked mean loss divided by4; no token pooling.
- Frozen ordinary AdamW, weight decay0; linear warmup2/total20.
- Update1 uses LR0, update3 uses1e-4, final post-scheduler LR0.
- Training-loop wall time **104.288s**; worker load/save/reference-inclusive **109.506s**.
- Peak allocated VRAM **5,135,322,624 bytes (4.783GiB)**.
- Peak reserved VRAM **5,786,042,368 bytes (5.389GiB)**, below8GiB.
- Minimum sampled device-free memory **5,809,111,040 bytes (5.410GiB)**, above1.5GiB.
- Resource sampling0.1s; sampled minimum is not a continuous-time guarantee.
- CUDA/numerical errors: none recorded. No safety halt or retry.

Per-update mean losses, in order:
`0.516329, 0.714259, 0.641632, 0.589311, 0.592084, 0.413464, 0.552656,
0.474432, 0.438974, 0.440381, 0.298534, 0.419765, 0.358311, 0.345248,
0.346763, 0.236371, 0.350306, 0.299894, 0.300886, 0.310509`.
Record groups vary across updates and dropout is active; this is not a monotone
matched-example curve. Preclip gradient norms range0.801031–1.398907; frozen norm1
clipping applies. Each microbatch verifies finite accumulated gradients and exact
gradient hashes across controlled cache release; every completed update verifies
unchanged base tensors. Checkpoints step10 and step20 are saved separately.

## Adapter save and fresh-process reload

[Adapter identities](r6_67/ADAPTER-IDENTITIES.json) bind the exact final files and
content identity `7fa3e7bfd5f99dd54caf700d53537c165a1193752d9820b3283423dfc9aef921`.
The adapter resides at the frozen external `lykoi-r6-52/r6-66/step20/adapter` path;
it is not embedded in this repository. External temporary storage is not durable
archival storage. Step10/20 receipts also bind tokenizer, training state and provenance.

[Reload](r6_67/ADAPTER-RELOAD.json) in fresh PID16040 verifies all112 adapter tensors
changed from initialization and exactly match saved trained tensors; base tensors
and quantization state match initialization. Reference logits are finite and
bitwise equal, maximum difference0. Adapter file hashes match. The original base
checkpoint and R6.59 adapter remain separately preserved by the full audit.

## Paired frozen diagnostics

[Base results](r6_67/DIAGNOSTIC-BASE.json),
[adapter results](r6_67/DIAGNOSTIC-ADAPTER.json) and
[per-case comparison](r6_67/COMPARISON.json) retain raw outputs/token IDs, prompt
identities, teacher-forced losses, timings and all eight unchanged scorer dimensions.
Individual raw-output receipts exist for every case on both tracks. Greedy128-token
decoding, repetition penalty1.1, cache off and terminal-EOS-only stripping are exact.
No malformed response is repaired, code fence removed or permissive fallback scored.

| Group | Accepted base → adapter | Mean target loss base → adapter | Tokens base → adapter | Generation seconds base → adapter |
| --- | --- | --- | --- | --- |
| Exposed training10 |0/10 → 0/10|0.642406 → 0.287226|927 → 720|168.877 → 130.184|
| Structurally varied3 |0/3 → 0/3|0.643708 → 0.334274|255 → 217|47.073 → 39.627|
| Combined13 |0/13 → 0/13|0.642706 → 0.298083|1,182 → 937|215.950 → 169.811|

All13 cases on both tracks fail strict serialization with JSONDecodeError.
Strict serialization, schema, correct operation, ordered operands, result type,
dependencies, deterministic assembly and functional acceptance each have **zero
demonstrated passes**: 0/10 exposed and0/3 varied on both tracks. Downstream false
flags are the frozen scorer's serialization-halt convention; semantic checking,
assembly and behavioral fixtures are **NOT_REACHED**, not independently observed
semantic-decision failures. Exact target reproduction is also0/13 on both tracks.
For example, trained D09 emits a fenced JSON-like response with bare-reference
operands and missing action fields; its untouched text is retained, not rescored.

Generated-token counts include terminal EOS when present. Aggregate generation time
excludes loading and teacher-forced evaluation. Shorter invalid outputs explain part
of the time decrease; this is not a successful-construction efficiency advantage.
There is one paired run and no statistical replication.

## Learning and memorization assessment

[Assessment](r6_67/ASSESSMENT.json) distinguishes:

- **A — Training mechanics supported:** bounded updates, safeguards, save/reload pass.
- **B — Target likelihood improved:** all13 paired teacher-forced losses decrease;
  exact greedy reproduction does not improve.
- **C — Valid incremental generation:** no observable improvement,0/13 both.
- **D — Correct semantic decisions:** no demonstrated improvement; strict parsing
  blocks operation/operand/dependency evaluation on all generated actions.
- **E — Exposed fitting limit:** ten trained records and three coordinator-authored
  variants permit fitting/memorization-compatible evidence only. They do not prove
  memorization as a causal mechanism or qualify independent generalization.
- **F — No observable usable-generation improvement:** supported for this diagnostic
  run, despite genuine measured likelihood changes.

Lower loss alone does not establish construction skill. Therefore the terminal
classification is TRAINING_MECHANICS_ONLY rather than incremental learning supported.

## Publication, next recommendation and stop

The [publication manifest](r6_67/PUBLICATION-IDENTITIES.json) and
[verification receipt](r6_67/VERIFICATION.json) bind report/protocol, additive source,
raw measurements and derived evidence. Fresh-process integrity/preservation checks,
JSON/Python/link/whitespace/credential checks, additive scope and git diff --check pass.
The first publication-only check rejected the report's prospective manifest link
before sealing created that file. Its [failure receipt](r6_67/PUBLICATION-FIRST-FAILURE.json)
is preserved; the publication checker now permits its two seal outputs during initial
sealing only. Fresh-process checking requires both files. No model execution was repeated.
The second publication check detected one newly created, untracked memory telemetry
file under r6_66: the concurrent monitor wrote during the wrapper's temporary
frozen-input identity check. No historical tracked bytes changed. The
[scope failure](r6_67/PUBLICATION-SECOND-FAILURE.json) and
[unaltered measurement](r6_67/MEMORY-ROUTING-RACE.json) are retained in r6_67.
Telemetry routing was not fully race-free; the executed wrapper was not repaired
or rerun. Final aggregates, per-microbatch data and all frozen identities remain valid.
The [boundary supplement](../../../docs/research-log-r6.67.md) records research and
decision limits without rewriting pinned overview/history.

Recommended next experiment: a separately authorized serialization-focused study
with prospectively frozen generation protocol and fresh diagnostics, measuring whether
raw schema-valid actions can be produced before claiming semantic learning. Retain
this adapter and all failures; no repair, rerun or hyperparameter change in R6.67.

Production compiler/lowerer/runtime, experimental semantics and R6.3–R6.66 artifacts
remain unchanged; kernel26, new primitives0, dataset expansion0, Python comparison
adapter0, installations0, P6-A04 acceptance0, P6-A05 access false. Execution remains
AI-independent and deterministic after validation. One authorized attempt only.

**Stopped after evaluation and publication. Await explicit authorization for further work.**
