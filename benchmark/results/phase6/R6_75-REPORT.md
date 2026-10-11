# R6.75 — Contrastive training preflight repair

**Final classification: `R6_75_CONTRASTIVE_TRAINING_READY`.** All three R6.74
mechanical blockers are corrected in a separately frozen additive successor. The
complete CPU-only preflight and actual-worker launch path pass. A single bounded
fresh-adapter **54-update / 216-presentation** attempt is justified as a prospective
experiment, subject to explicit authorization. It is not authorized by this receipt.
No learning, GPU-training success or independent generalization is established.

Final evidence is in [qualification_3](r6_75/qualification_3/TRAINING-READINESS.json).
The original R6.74 classification remains **`R6_74_CONFIGURATION_GAP`**. All original
and intermediate freezes, failures and measurements are retained.

## Baseline and preservation

Initial `git status --short` was clean. [Baseline](r6_75/qualification_3/BASELINE.json)
verifies R6.74 publication and original failures, R6.73 dataset/decoder/publication,
the pinned R6.52 environment/assets, and inherited preservation boundaries including
AdamW, scheduler, cache-release and training infrastructure. Original R6.74 equal
counts24/24/24/24, invalid scopes, missing composition-module rss and both control
halts remain unchanged. Historical publication audits are identity checks, not
historical model-output rescoring or acceptance execution.

Production kernel26, compiler/lowerer/runtime, experimental meanings and
R6.3–R6.74 evidence are preserved. Historical entry-point documents are pinned;
current direction is recorded in additive versioned supplements. No new execution
primitive, comparison adapter, dataset expansion, dependency or credentials.
P6-A04 acceptance0; P6-A05 access false; AI-independent execution retained.

## Normalization repair

[Control inputs and analytic expectations](r6_75/qualification_3/NORMALIZATION-CONTROL.json)
were frozen before execution in [the preflight freeze](r6_75/qualification_3/PREFLIGHT-FREEZE.json).
They are synthetic numerical controls, not training examples. Supervised counts
**2/4/6/8** include final EOS surrogates; distinguishable token losses use two-class
logits `[0,0]`, `[0,1]`, `[0,2]`, `[0,3]`. Masked-position logits are deliberately
different so incorrect shifting is detectable.

[Results](r6_75/qualification_3/NORMALIZATION-VERIFICATION.json):

|Quantity|Observed value|
|---|---:|
|Per-record mean CE|0.6931471825; 1.3132616282; 2.1269280910; 3.0485875607|
|Accumulated sum of four record losses /4, equal-record mean|1.795481115579605|
|Equal-record mean divided by four|0.4488702788949013|
|Pooled-token mean|2.189480495452881|
|Absolute weighting disagreement|0.39399937987327593|

Installed `ForCausalLMLoss` agrees **exactly** with manual once-shifted CE and each
CE/4 contribution. Sum of the four contributions exactly equals equal-record mean;
their mean exactly equals equal-record mean/4. Analytic precommitted expectations
agree within2e-6. Prompt/post-EOS/padding masking, masked-logit poison invariance,
padding invariance and rejection of an unshifted calculation pass. No backward call.
Equal-count fixtures and unequal-count/equal-loss fixtures reject as nondiscriminating.
The frozen training loss rule and all54 training records are unchanged.

## Evaluation identifier repair

[Successor fixtures](r6_75/qualification_3/EVALUATION.json) and
[exact fixture/expectation identities](r6_75/qualification_3/EVALUATION-IDENTITIES.json)
use short grammar-valid scope names such as `R675E01N1R1`: fixed round prefix,
unchanged family/index/rendering. All24 names are distinct and satisfy unchanged
`[A-Za-z][A-Za-z0-9_]{0,31}` grammar.

Only definition-name metadata, its canonical scope identity and its prompt envelope
change. Names are not operand references. Requirement text, params, prior steps,
operation, operands/order, deps/direct-versus-transitive obligations, result type,
literal choices and behavioral expectations are exact. Original and successor
expectation identities agree. Arbitrary remapping or changed expectations reject.
Six exposed calibration records are unchanged JSON values.

[Acceptance](r6_75/qualification_3/EVALUATION-VERIFICATION.json): **24/24 reserved
diagnostic scopes validate, reconstruct deterministically and pass full semantic plus
functional acceptance**, covering80 fixture observations. **6/6 unchanged exposed
calibrations pass.** These24 renderings represent12 underlying synthetic requirements;
repetitions are not independent evidence. Unit values remain all null, so Unit identity/
order/literal distinctions are structural rather than functionally discriminated.
Coordinator-authored reservations remain exploratory, without independent withholding.

The unchanged R6.73 compact decoder and scorer are requalified in
[decoder/scorer evidence](r6_75/qualification_3/DECODER-SCORER-VERIFICATION.json),
[compact controls](r6_75/qualification_3/COMPACT-DECODER-CONTROLS.json) and
[26 adversarial controls](r6_75/qualification_3/ADVERSARIAL-VERIFICATION.json).
All36 contrast negatives reject full acceptance. Enumerated evaluation-language
paths fit64 tokens including terminal EOS; malformed/truncated/trailing/duplicate-key
outputs reject. This is CPU syntax/scoring qualification, not live generation.

## Resource mechanism and actual process identity

The missing callable came from binding worker and launcher resource checks to the
unchanged R6.18 composition module. The successor binds an experiment-local
[stdlib resource module](../../../experiments/contrastive_preflight_r6_75/resources75.py),
without modifying composition or training semantics.

Windows measures current resident working set using `GetProcessMemoryInfo` with
pointer-sized counters, explicit ctypes signatures, and handle-derived `GetProcessId`.
Linux `/proc/PID/status` support is implemented but not executed on this Windows host.
Other platforms or failed queries return explicit null/unavailable with reason; zero
is never a missing-value fallback. Budget enforcement fails closed on unavailable,
nonpositive, wrong-PID or over-ceiling readings.

[Resource qualification](r6_75/qualification_3/RESOURCE-VERIFICATION.json) measures
683,347,968 resident bytes for the qualification worker (PID17624). Invalid PID and
unsupported-platform controls return nulls. Fresh pinned Python3.12.11 workers pass.

The Windows venv executable is a redirector, so `Popen.pid` differs from the actual
Python worker. The final [launcher](../../../experiments/contrastive_preflight_r6_75/dispatch_v3.py)
uses an exclusive nonce/mode/interpreter/parent-bound self-PID handshake, measures
the actual worker, and labels startup redirector samples separately. Worker self-RSS
and external samples agree on attribution in all three phases. Wrong nonce, mode,
interpreter and parent controls reject12/12. RSS remains sampled current residency,
not hard OS containment or a guarantee about peaks between0.1s polls.

## Complete preflight and executable identity

[CPU qualification](r6_75/qualification_3/CPU-QUALIFICATION.json) uses exactly
`C:\Users\lblan\AppData\Local\Temp\opencode\lykoi-r6-52\venv\Scripts\python.exe`,
Python3.12.11. All nine package versions match the pinned environment, including
torch2.7.1+cu128, transformers4.55.4, peft0.17.1 and bitsandbytes0.47.0. The CPU
bitsandbytes unavailable-8-bit-optimizer message is retained; ordinary torch AdamW
is signature-qualified and no optimizer instance is constructed.

- [Dataset/masks](r6_75/qualification_3/DATASET-MASK-VERIFICATION.json): all54 rows
  and R6.73 source/action identities match; original tokenization is exact; all54
  completion/EOS, prompt/post-EOS/padding and shifted-CE checks pass.18 direct+36
  corrective; no expansion or silent truncation.
- [Sampling/schedule](r6_75/qualification_3/SAMPLING-SCHEDULE-VERIFICATION.json):
  exact216 frozen presentations, microbatch1/accumulation4,54 scalar LR entries,
  accumulation across epoch boundaries, unchanged seed651/order/no shuffle.
  Frozen AdamW and warmup6/linear54 choices are unchanged; no scheduler instance/tick.
- [Executable configuration](r6_75/qualification_3/TRAINING-CONFIGURATION.json)
  resolves worker/launcher/runtime/resource, decoder/scorer context, dataset, sampling,
  loss policy, schedule, fixtures and interpreter. Rank8 q/v LoRA, alpha16,
  dropout0.05, FP32 adapter/NF4 base/BF16 compute, checkpoint27/54/final54,
  precision/cache-release/clipping/recovery choices stay exact.
- [Worker definitions](r6_75/qualification_3/EFFECTIVE-WORKER.py.txt),
  [diagnostic definitions](r6_75/qualification_3/EFFECTIVE-DIAGNOSTIC.py.txt),
  [launch audit](r6_75/qualification_3/LAUNCH-INTEGRATION-AUDIT.json) and
  [dry launch](r6_75/qualification_3/dry-launch/RESULT.json) pass for fresh base,
  train and adapter worker processes. Real entry points/imports/configuration/tokenizer/
  dataset/diagnostic preparation and CPU resource monitoring execute; the explicit
  dry boundary returns before weights, CUDA work, inference or optimizer/scheduler
  construction. No mock model or fake updates count as qualification.
- [Output paths/ceilings](r6_75/qualification_3/OUTPUT-PATHS.json): fresh external
  `r6-75` checkpoint root and qualification_3/execution path remain absent;
  exclusive dispatch/run/checkpoint claims, no resume/retry.8GiB GPU-reserved ceiling,
  1.5GiB free floor,16GiB RSS,1800s process ceiling and120s generation ceiling are
  resolved. GPU enforcement is inherited/static here, not newly GPU-exercised.

**Complete configuration identity:**
`a2b3d148a5e966d856864a1ad6b4e43550ce699e8c94b21493667abbf6d55189`.
**Unresolved configuration dependencies: none.** Model loading, real compact
generation, GPU resources and numerical training behavior remain unexecuted empirical
qualifications; CPU readiness does not substitute for them.

## Adversarial integrity and failed attempts

[Nine preflight rejection controls](r6_75/qualification_3/ADVERSARIAL-PREFLIGHT.json)
cover equal-length/equal-loss nondiscrimination, incorrect identifier remapping,
changed expectations, zero-as-missing RSS, wrong PID, incomplete execution bindings,
missing optimizer configuration and unavailable RSS budget enforcement.12 additional
handshake controls,26 inherited decision controls and36 contrast negatives pass.

Preserved attempts:

1. [Preparation timeout](../../../experiments/contrastive_preflight_r6_75/PREPARATION-TIMEOUT-1.json):
   initial read-only identity audit exceeded120s; no output/freeze/control reached.
   A600s tool budget allowed the same identity audit to complete without source repair.
2. [First frozen qualification halt](r6_75/HALT-qualify.json): underscore replacement
   still violated the32-character name bound. Passing normalization/mask evidence and
   the complete first freeze remain. [Amendment2](../../../experiments/contrastive_preflight_r6_75/AMENDMENT-2.md)
   precommits short, unambiguous identifiers in separate qualification_2 outputs.
3. [Version2 finish halt](r6_75/qualification_2/HALT-finish.json): final audit caught
   redirector/worker PID mismatch after all three CPU phases exited successfully.
   Version2 measurements correctly measure the redirector but cannot qualify worker
   attribution. [Amendment3](../../../experiments/contrastive_preflight_r6_75/AMENDMENT-3.md)
   freezes actual-worker handshake instrumentation and separate qualification_3 outputs.

No failed evidence is replaced. Repeated mechanical controls are not additional
independent examples. [Publication identities](r6_75/PUBLICATION-IDENTITIES.json) and
[verification](r6_75/VERIFICATION.json) bind every version, report and supplement,
reverify all freezes/preservation, syntax/links/whitespace/credential-pattern checks,
additive-only scope and `git diff --check`.

## Receipt and stop

[Training-readiness receipt](r6_75/qualification_3/TRAINING-READINESS.json): ready,
all three defects corrected, complete executable configuration, no unresolved
configuration dependencies. **Weights loaded0; inference0; backward0;
optimizer/scheduler instances0; optimizer/scheduler updates0; CUDA initialized false.**

Recommended next step: explicitly authorize neutral compact inference and at most
one bounded fresh-adapter54-update/216-presentation experiment, with frozen paired
exploratory diagnostics and halt/no automatic retry on any failure. No model-learning,
generalization or efficiency claim follows from this CPU preflight.

**Stopped after CPU-only qualification and publication. Await explicit authorization.**
