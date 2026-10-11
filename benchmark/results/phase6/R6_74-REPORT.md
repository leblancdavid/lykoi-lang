# R6.74 — Contrastive training integration preflight

**Final classification: `R6_74_CONFIGURATION_GAP`.** The bounded CPU-only
nonproduction preflight qualifies the 54-row training conversion and freezes the
prospective settings, but mandatory loss-control, evaluation-scope and resource
integration checks fail. **Training is not ready; a GPU attempt is not justified.**
These are preflight construction defects, not demonstrated model-learning failures
or new Lykoi semantic gaps. No model weights were loaded, no participant inference
or training occurred, and no optimizer or scheduler was instantiated or updated.

## Preservation and environment

Initial `git status --short` was clean. [Baseline](r6_74/BASELINE.json) checks R6.73
publication/dataset/decoder identities and the inherited preservation chain, including
R6.52 assets, R6.54 scheduler, R6.55 AdamW, R6.58 cache release and R6.59/R6.67
training infrastructure. R6.73's original base revision remains
`2e1fd397ee46e1388853d2af2c993145b0f1098a`; tokenizer.json remains
`c0382117ea329cdf097041132f6d735924b697924d6f6fc3945713e96ce87539`.
File hashing is identity verification, not loading model tensors.

[CPU evidence](r6_74/CPU-QUALIFICATION.json) uses the exact pinned interpreter
`C:\Users\lblan\AppData\Local\Temp\opencode\lykoi-r6-52\venv\Scripts\python.exe`,
Python **3.12.11**, with CUDA hidden and offline local assets. All nine required
package imports match R6.52, including torch2.7.1+cu128, transformers4.55.4,
peft0.17.1 and bitsandbytes0.47.0. The CPU bitsandbytes import reports its unavailable
8-bit optimizer; this experiment retains ordinary torch AdamW and instantiates none.
CUDA remains uninitialized. Production/compiler/lowerer/runtime, experimental
execution meanings and R6.3–R6.73 historical evidence remain unchanged. Kernel26
is preserved accounting/implementation, not a new recount. P6-A04 acceptance0;
P6-A05 access false. Historical model outputs are not rescored.

## Dataset qualification

[Dataset](r6_74/DATASET.json) and [qualification](r6_74/DATASET-QUALIFICATION.json):

- **54 eligible rows:18 direct and36 corrective**, derived from18 positive and36
  negative source records; no expansion.
- Every assistant target is the requirement-derived correct compact decision.
  Incorrect candidates appear only in explicitly labeled corrective user inputs.
- Requirement, typed scope, positive/negative ledger, action and acceptance identities
  reproduce the R6.73 SFT-ready conversion exactly; reconstruction action hashes match.
- Zero duplicate prompt identities, contradictions or evaluation-family training rows.
  There are17 distinct requirement identities and18 underlying positive records;
  these are correlated synthetic development examples, not54 independent requirements.
- Training conversion/provenance and loss/sampling are frozen **before** separate
  [evaluation realization](../../../experiments/contrastive_preflight_r6_74/evaluation.py).
  Training conversion never imports that evaluation module.

## Sampling and normalization freezes

[Sampling](r6_74/SAMPLING.json) specifies the exact216-presentation order: ascending
frozen positive ID, each direct record followed by its two corrections, repeated four
times. Each row is presented four times. Microbatch1, accumulation4, maximum54
optimizer updates, epoch boundaries54/108/162/216, no shuffle or reshuffle, seed651.
Accumulation crosses epoch boundaries54 and162; it is not reset at epoch end.
Sampling consumes no RNG. Adapter/dropout initialization retains Python and torch
CPU/CUDA seed651; checkpoint RNG preservation is inherited, with no NumPy transforms.

Sampling identity:
`21e5ed5d399f5c3083b7f50e60a549f16f9182a5d4756be4baea1048e2d1fd17`.

[Loss policy](r6_74/LOSS-POLICY.json): completion+turn-EOS-only mean CE per record,
each divided by4 before its backward call; equal-record weighting, not pooled-token.
Prompts, padding and post-EOS newline are masked. Causal shifting is performed once
by installed ForCausalLMLoss. Corrective inputs receive no desired-output loss.
No packing, truncation or silent drops.

Loss-normalization identity:
`4459c87b994cdeef59e144dfcaa6ff4134d4ef613cf384c094ba0ac7a31d9055`.

[Mask controls](r6_74/LOSS-MASK-VERIFICATION.json) pass54/54 synthetic CPU
causal-shift/manual-CE/padding-invariance checks. However, the frozen discriminating
normalization control fails: its first four targets each supervise24 tokens, making
equal-record and pooled-token means both0.8274765014648438. This fixture cannot
distinguish the policies. The assertion is a preflight-control defect; the policy
is not silently changed or declared fully qualified.

## Optimizer, scheduler and executable configuration

[Configuration](r6_74/TRAINING-CONFIGURATION.json) retains qualified settings:
adapter-only torch AdamW, LR1e-4, weight_decay0, betas0.9/0.999, eps1e-8,
amsgrad/maximize/capturable/differentiable false, foreach/fused null. Rank8 q/v LoRA,
alpha16, dropout0.05, bias none, FP32 adapter; frozen original base with NF4/double
quantization, BF16 compute, UInt8 storage, no autocast/scaler. Non-reentrant
checkpointing, cache off, clipping L2 max1 with nonfinite rejection, retained precision
flags and seed651. Fresh adapter only; neither historical trained adapter is reused.

R6.73 prospectively specifies warmup6/total54. The complete
[54-update LR sequence](r6_74/SCHEDULER-SIMULATION.json) is frozen and independently
checked against installed R6.54 linear arithmetic. Index0 starts at zero; update1
uses zero LR; index6 is peak; index54 reaches zero. Optimizer completion precedes
exactly one scheduler tick. Failed/skipped updates do not advance and must halt.
This is scalar simulation, not scheduler stepping.

Configuration identity:
`5636627affea3cceaf2e17e15421284feb8c67b3546c1d325991d81c8b4a4356`.

[Frozen executable worker](r6_74/EFFECTIVE-WORKER.py.txt),
[launcher](../../../experiments/contrastive_preflight_r6_74/dispatch.py) and
[runtime integration](../../../experiments/contrastive_preflight_r6_74/runtime.py)
are prepared and compile/import checked, but **not dispatch-qualified**. The inherited
R6.58 backward/telemetry/delete/synchronize/finite-gradient-hash/empty_cache/exact-hash
sequence is retained. Fresh artifact paths, exclusive claims, checkpoints27/54,
final-only selection54 and no automatic retry/resume are explicit in
[output paths](r6_74/OUTPUT-PATHS.json). Budgets retain8GiB reserved GPU ceiling,
1.5GiB free floor,16GiB RSS,1800s processes and120s generation.

[Integration audit](r6_74/EXECUTABLE-INTEGRATION-AUDIT.json) finds a required-interface
defect: runtime/launcher `c` binds the unchanged composition module, which has no
`rss` callable. The worker memory monitor and launcher therefore cannot enforce the
frozen RSS contract. Compilation alone is insufficient. No post-freeze repair is made.

## Compact decoder, scorer and evaluation

[Decoder controls](r6_74/COMPACT-DECODER-CONTROLS.json) reproduce five bounded
languages with1,734 decisions,47,517 token-prefix observations and three exhaustive
vocabulary masks. Canonical compact wire serialization round-trips, duplicate deps
are excluded, and terminal states allow EOS only. Syntax masks admit wrong operations,
operands and dependencies; requirement answers and result-type filtering do not enter
the decoder. This remains CPU mechanism evidence, not live-generation qualification.

[Adversarial controls](r6_74/ADVERSARIAL-VERIFICATION.json) pass26/26:16 schema
rejections,7 semantic rejections,1 valid-but-wrong order rejection and2 legal controls.
[Integrated scorer controls](r6_74/DECODER-SCORER-QUALIFICATION.json) reject all36
contrast negatives from full semantic acceptance, including functionally agreeing but
wrong-relation examples; three malformed/incomplete/trailing/duplicate-key controls
reject. Operation, operand multiset, ordered operands, dependencies, reconstruction
and functional acceptance are separately recorded. Reconstruction never repairs choices.
All enumerated evaluation-language token paths fit the64-token budget including EOS;
this syntax result does not cure invalid scope envelopes.

[Frozen evaluation](r6_74/EVALUATION.json) contains24 coordinator-reserved structurally
varied diagnostics: four requirements in each of three families, two correlated
scope-order renderings per requirement (12 underlying requirements), plus six separately
labeled exposed training calibration cases. It includes opposite bounds/equal and
unequal values, literal/reference alternatives, typed distractors, repeated refs and
direct/transitive dependency distinctions. Bool result obligations do not select le
versus eq. Unit values are all null; Unit identity/order distinctions are structural,
not behaviorally discriminated. Independent review/withholding is unavailable.

**Evaluation is not ready.** [Native scope checks](r6_74/EVALUATION-READINESS.json)
reject24/24 reserved scopes at `$/name`, code `REFERENCE`: generated names contain
hyphens and violate unchanged case-sensitive ASCII identifier rules. Their gold
decisions parse and match frozen fields, but reconstruction and functional acceptance
are NOT_REACHED. Six exposed calibration gold cases pass6/6; they are mechanism/
memorization controls, not participant outcomes or generalization evidence. Frozen
requirements, scopes, expectations and fixtures are retained without correction.

## Failed preparation, halts and publication

Two import-preparation failures preceded source/data freeze:
[generic helper shadowing](r6_74/PREPARATION-FAILURE-1.json) and
[incomplete rename application](r6_74/PREPARATION-FAILURE-2.json).
The new helper was renamed before freezing, without changing historical sources.
The frozen [normalization halt](r6_74/HALT-qualify.json) and later
[evaluation control halt](r6_74/HALT-remaining-controls.json) retain tracebacks.
Independent remaining checks then recorded actual outcomes and resource defects;
they did not repair or rerun the frozen failed entry points. Repeated CPU checks are
not additional independent examples. [Source freeze](r6_74/SOURCE-FREEZE.json),
[configuration freeze](r6_74/CONFIGURATION-FREEZE.json),
[evaluation freeze](r6_74/EVALUATION-FREEZE.json) and additive audit freezes retain order.

[Publication identities](r6_74/PUBLICATION-IDENTITIES.json) and
[verification](r6_74/VERIFICATION.json) bind all deliverables, confirm historical
preservation and additive scope, check syntax/links/whitespace/credential patterns,
and run `git diff --check`. Publication integrity does not imply training readiness.

## Stop and recommendation

[Readiness receipt](r6_74/TRAINING-READINESS.json): **not ready**, three blockers:
invalid normalization negative-control fixture, invalid reserved scope names and missing
RSS-monitor interface. Recommended next step is a **separately authorized additive
successor CPU qualification** of those mechanical defects, preserving every R6.74
freeze/halt. Only after full mandatory qualification should neutral compact inference
and a single bounded GPU training attempt be considered under explicit authorization.

**Stopped after bounded CPU preflight and publication. Await explicit authorization.**
