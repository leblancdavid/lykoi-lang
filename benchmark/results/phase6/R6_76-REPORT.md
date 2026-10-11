# R6.76 — Contrastive semantic learning experiment

**Final classification: `R6_76_PROTOCOL_HALT`.** Neutral live compact-decoder
qualification passed. The unchanged-base diagnostic stage was interrupted by the
outer command harness at600 seconds; training, adapter save/reload and post-training
evaluation were **NOT_REACHED**. No learning or paired advantage is established.

## Identity and preflight

Initial git status was clean. [Identity receipt](r6_76/IDENTITY-PREFLIGHT.json)
reverifies R6.75 publication, all qualified freezes, original R6.74 halts and the
inherited R6.73 supervision, R6.52 checkpoint/tokenizer, R6.59/R6.67 infrastructure,
R6.58 cache-release and R6.65 scorer preservation checks. Local checkpoint/tokenizer
file hashes match. Production kernel remains26. Exact configuration identity:

`a2b3d148a5e966d856864a1ad6b4e43550ce699e8c94b21493667abbf6d55189`

[Execution receipt](r6_76/EXECUTION-RECEIPT.json) and
[prospective freeze](r6_76/EXECUTION-FREEZE.json) bind the additive orchestration.
The qualified training and diagnostic source definitions were executed unchanged;
only the runtime evidence destination was rebound to r6_76. The frozen external
r6-75 checkpoint destination was retained, claimed after neutral success, and remains
empty. No historical adapter was loaded. No hyperparameter, dataset, expectation,
decoder, scorer or execution meaning was changed.

## Neutral live decoder qualification

[Qualification](r6_76/NEUTRAL-QUALIFICATION.json): one small neutral scope with two
references and no literals, no expected operation/operand/dependency answer. All three
operations and both reference choices remained grammar-available. Actual pinned NF4
model/tokenizer generated **25 tokens including EOS**,
in **47.042s**, with **42.869s**
instrumented mask/enforcement overhead (including token-evidence writes).

Every selected token belongs to the recorded allowed set; disallowed logits were
negative infinity. Each prefix stays in the frozen language, terminals allow only
EOS, final EOS is observed and compact parsing passes. No dead end occurred on this
control. The64-token live budget was respected. A one-token prefix of this live
output is nonterminal: this is a truncation consistency check, not a separate
short-budget live generation. [Raw token decisions](r6_76/NEUTRAL-TOKENS.json),
full transitions and stdout/stderr are retained. This is a small neutral control,
not exhaustive live qualification of every diagnostic scope or model behavior.
Decoder validity is structural enforcement, not model learning.

## Frozen base-model evaluation: interrupted

The frozen fixture order starts with24 diagnostics, then6 exposed calibrations.
**4/30** completed outputs were atomically preserved; all are diagnostic
renderings. No exposed calibration was reached. Remaining and in-flight cases are
unexecuted/unavailable, not failures or zero-score observations.

|Dimension|Completed diagnostic correct / completed|Calibration|
|---|---:|---:|
|strict_decision_validity|4/4|0/0 (unexecuted)|
|correct_operation|4/4|0/0 (unexecuted)|
|correct_operand_identities|0/4|0/0 (unexecuted)|
|correct_operand_order|0/4|0/0 (unexecuted)|
|correct_dependencies|1/4|0/0 (unexecuted)|
|reconstruction_success|0/4|0/0 (unexecuted)|
|functional_acceptance|0/4|0/0 (unexecuted)|
|accepted|0/4|0/0 (unexecuted)|

Completed diagnostic outputs total **168 tokens**
and **352.462s** combined inference/decoder time.
The unchanged qualified diagnostic worker does not separately measure decoder time;
that split is unavailable and must not be inferred from neutral timing. Raw text,
generated IDs, allowed-set identities, exact semantic dimensions and reconstruction
errors are in [partial base results](r6_76/BASE-DIAGNOSTIC-PARTIAL.json).
Outputs were neither repaired nor rescored into successes. Structural JSON validity
did not ensure correct operand binding, exact dependency coherence or reconstruction.
Functional acceptance marked NOT_REACHED remains distinct from false.

## Halt and resource accounting

[Harness interruption](r6_76/HARNESS-INTERRUPTION.json): the tool terminated the
dispatch command after600000ms during base inference. A subsequent process check
found no Python worker. This outer budget was too short for the complete four-phase
orchestration; it is an orchestration failure, not a demonstrated frozen CUDA/RSS or
1800s per-worker violation. No restart or second inference attempt was made.
The interrupted base process has no closed PHASE-base receipt; its external samples
were still in launcher memory and are unavailable. Neutral actual-worker RSS samples
are retained in [neutral phase](r6_76/PHASE-neutral.json). Generation-library ignored
flag warnings remain in stderr. No conclusion about the unobserved in-flight output
or absence of errors during termination is justified.

## Training, adapter and paired assessment

**Optimizer updates0; scheduler updates0; presentations0.** No training initialization,
optimizer construction, loss/backward measurement or trained adapter was reached.
Training loss, allocated/reserved VRAM, minimum device-free memory and wall time are
unavailable, not zero-valued measurements. Adapter tensor changes, frozen-base
tensor verification after training, save/reload reference-logit verification,
post-training30-case scoring and base-versus-adapter comparisons are NOT_REACHED.
The configured54-update ceiling was never exercised. Historical adapters remain separate.

Assessment A–F: mechanics, likelihood, calibration improvement, diagnostic binding
improvement, functional improvement, and no-advantage/regression are all **not
established**. Incomplete base-only results cannot demonstrate advantage, no advantage,
memorization or semantic learning. No broad generalization or Python superiority claim.

## Contamination, limitations and recommendation

The coordinator reviewed fixtures and historical qualification findings. The24
diagnostic renderings cover12 underlying synthetic requirements; repeated renderings
are not independent observations. Six calibrations are exposed. Unit values are null,
so some distinctions are structural rather than behaviorally discriminated. These
remain exploratory, not independently qualified generalization evidence.

Recommended next step: separately authorize a new linked attempt with an outer
execution budget that accommodates all frozen per-process ceilings and durable
launcher resource telemetry. Preserve this interrupted first result; do not resume
or infer authorization from the prior readiness receipt. No new training settings
or outcome-informed diagnostic/decoder changes are recommended from this evidence.

## Publication and stop

[Terminal result](r6_76/TERMINAL-RESULT.json), [stage status](r6_76/STAGE-STATUS.json),
[publication identities](r6_76/PUBLICATION-IDENTITIES.json) and
[verification](r6_76/VERIFICATION.json) bind the evidence and additive supplements.
Production compiler/lowerer/runtime, experimental semantics, kernel26 and R6.3–R6.75
history are unchanged; P6-A04 acceptance0, P6-A05 access false. No credentials,
dataset expansion, comparison adapter, new primitive or model merge. Execution remains
AI-independent. **Stopped after terminal publication. Await explicit authorization.**
