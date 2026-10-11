# One prospective fresh-adapter experiment — not authorized for execution

## Question and inputs

Does one fresh adapter improve direct compact semantic binding over the unchanged
base on a small exploratory structurally different diagnostic, with complete failure
accounting? Improvement is falsifiable, not predicted or established by R6.73.

Use original Qwen/Qwen2.5-Coder-1.5B-Instruct revision
`2e1fd397ee46e1388853d2af2c993145b0f1098a`, pinned R6.52 weights/tokenizer.
Start a **fresh** adapter, never R6.67 or R6.59 weights. Bind the R6.66 manifest,
R6.69 live identity verifier and R6.73 publication identities prospectively. Existing
training infrastructure is reusable, but its historical worker expects full actions;
a separately qualified experiment-local record/scorer integration is required.

Training input: 18 direct correct compact records in
[SFT-POSITIVES](qualification_2/SFT-POSITIVES.json), plus36 correction records in
[CONTRASTIVE-SFT-POSITIVES](qualification_2/CONTRASTIVE-SFT-POSITIVES.json).
Negative candidates occur only as explicitly labeled user input; assistant completions
are always the requirement-derived correct decision. Reasons remain outside prompts.
All54 records derive from18 positives/36 negatives, not54 independent requirements.
No positive loss on incorrect decisions, fabricated rationale, evaluation-family rows,
R6.72 raw response or participant-generated repair enters training.

## Proposed fixed bounded budget

Retain qualified NF4/double-quantization/BF16 compute and UInt8 quantized storage;
rank8 q_proj/v_proj LoRA, alpha16, dropout0.05, bias none, adapter FP32; seed651;
base frozen. Original base fingerprint is checked before the first update.
Retain R6.55 adapter-only AdamW LR1e-4, weight_decay0, betas0.9/0.999, eps1e-8;
R6.54 linear scheduler; per-record completion+EOS mean loss; microbatch1,
accumulation4; clipping1 and finite checks; non-reentrant checkpointing; cache off;
R6.58 ordered release checks. No packing, target truncation or silent drops.

Propose **54 maximum optimizer updates**,216 record presentations: all54 eligible
records repeated four times. Canonical order: each requirement's direct record then
its two corrections, ordered by frozen positive ID, cycling four times. No shuffle.
Set warmup6, linear total54, one final selected checkpoint at54; intermediate27 is
retained only for recovery/provenance, never selected using evaluation outcomes.
This gives four full passes of a larger compact curriculum instead of mechanically
reusing20 updates. It is a feasibility budget, **not an optimality claim** or permission
to tune against evaluation. Loss convergence may justify a future separately authorized
budget study, never automatic continuation. Qualified normalization and scheduler
arithmetic must be rechecked for54 updates before dispatch.

2048-token cap; observed training sequences304–444 tokens. Preserve R6.66 precision
flags and resource safeguards: reserved8GiB ceiling, free1.5GiB floor, RSS16GiB,
training/diagnostic1800s, generation120s, reload120s. Save accounting at every completed
update. One-shot execution; any error preserves first halt/raw logs, no automatic retry.
Fresh output directories and exclusive claims must not reuse historical training paths.

## Freeze diagnostics before training

Realize the three reserved evaluation structures into **four requirements per family**,
with two scope-order/distractor renderings per requirement:24 correlated diagnostic
cases,12 underlying requirements. Publish provenance and overlap accounting; do not
call the renderings independent families. Scope types must not by themselves distinguish
le from eq. Include opposite ordered bounds, equal/unequal values, literal/reference
alternatives, wrong-type distractors, repeated refs and exact direct versus transitive
dependencies. Freeze requirements, scopes, expected choices and distinguishing behavioral
fixtures before any base/adapter generation. Obtain independent review/withholding if
available; otherwise retain exploratory classification. Do not materialize solutions
in training-data preparation. No R6.73 reserved solution is published here.

Run a frozen base diagnostic **before** training, seal its raw outputs and failure
results, then train without changing records/hyperparameters from those outcomes.
Evaluate final fresh adapter on exactly the same pinned prompts/settings/fixtures.
Also report six training-example calibration cases separately as memorization controls,
never evaluation/generalization evidence. No checkpoint selection by diagnostic results.

## Identical evaluation and metrics

Use direct requirement prompts with no incorrect-candidate hints. Both models get the
same compact scope-bounded syntax mask, greedy one beam, max64 new tokens, repetition
penalty1.0 and cache off, seed651; EOS only after terminal. This differs prospectively
from the historical128/1.1 configuration and must be frozen/CPU-qualified and neutrally
qualified before scored inference. The compact grammar's measured maximum41–42 tokens
on current scopes motivates64, but future reserved scopes must fit64 without truncation.
No expected decisions, result-type filter or fixtures enter token masks. Full decoded
prefix transitions are audited. Enforce completion budget and preserve incomplete output;
no semantic normalization, silent repairs, retries or fallback inference.

Parse compact decisions strictly; apply the unchanged R6.73 renderer/authoritative
R6.63 assembler/VM and unchanged R6.65 functional scorer for reconstructed actions.
Derive result types but keep deps explicit. Record per-case:

1. Operation selection.
2. Exact operand identity/tagged literal and unordered operand multiset.
3. Ordered slotwise match; commutative swaps remain structural mismatches.
4. Literal/reference choice, separately from ordering.
5. Exact explicit direct dependencies, including repeated/shared references.
6. Compact serialization/schema, reconstruction validity and rejection stage.
7. Functional acceptance after successful reconstruction; strict full semantic acceptance
   additionally requires exact frozen operation/ordered choices/dependencies.

Give end-to-end denominators for all24 cases and conditional denominators after parse
and reconstruction. Distinguish schema failure, semantic rejection, valid-but-wrong
decision, functional mismatch and budget halt. Behavioral agreement does not prove
correct operation, especially on equivalent shared prefixes. Report paired counts
and raw case outcomes;12 underlying requirements is too small for broad conclusions.
Measure token lengths, wall/forward/mask/assembly/behavior costs separately; training
cost is reported in full. Halted stages remain NOT_REACHED. Do not infer generalization
from related training examples or attribute failures to unobserved model reasoning.

## Authorization gate and smallest next step

R6.73 justifies this bounded experiment as a proposal because data, reconstruction
and syntax paths are qualified. It does not establish training-worker integration,
GPU feasibility with the new objective, live compact decoding or model learning.
The smallest next step is separately authorized **CPU-only integration preflight**:
load the54 eligible records into the R6.66 masked-completion path, qualify sampling,
loss labels and54-step schedule, freeze new worker/configuration, and realize/review
the reserved diagnostic without exposing its solutions to training preparation.
Only a later explicit authorization may permit neutral inference or fresh QLoRA.
