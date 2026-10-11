# R6.77 — Durable orchestration and linked contrastive attempt

**Final classification: `R6_77_PROTOCOL_HALT`.** All required identities pass,
and four R6.76 observations qualify for linked reuse. Synthetic durable-launcher
controls pass. Baseline continuation stops because the fifth historical generation
has no recoverable raw output or completion record: avoiding duplicate generation
cannot be established. No new model generation or training attempt was dispatched.
R6.76's original `R6_76_PROTOCOL_HALT` is preserved.

## Identities and preserved observations

[Identity preflight](r6_77/IDENTITY-PREFLIGHT.json) reverifies R6.76 publication,
terminal classification and original preflight, R6.75 training readiness/freezes,
R6.73 training records/compact decoder, successor evaluation fixtures, pinned local
Qwen2.5-Coder-1.5B-Instruct checkpoint/tokenizer, R6.65 scorer and inherited
preservation receipts. Original configuration identity remains:

`a2b3d148a5e966d856864a1ad6b4e43550ce699e8c94b21493667abbf6d55189`.

Production kernel remains **26**, based on preserved accounting/implementation
identities, not a new construct recount. The existing checkpoint destination is
still empty. Historical adapters were not loaded or overwritten. Initial status
contained only untracked R6.76 publication/implementation/supplement files; their
publication identities are verified and preserved.

[Recovery audit](r6_77/RECOVERY-AUDIT.json) and four per-case reuse receipts verify
fixture ordering and identities, prompt identities, unique case IDs, raw text against
token decoding, terminal EOS, token budget, every recorded prefix/allowed-set hash,
selected-token membership and exact frozen scoring. This is deterministic evidence
reverification, **not fresh model inference** or score repair. All four complete
records qualify; their original raw outputs/scores remain unchanged.

## Timeout and durable launcher

[Timeout diagnosis](r6_77/TIMEOUT-DIAGNOSIS.md): the original 600-second interruption
was reported by the outer shell-tool command runner. The exact enforcing process/PID
is unavailable. The available tool supports a millisecond `timeout` argument and
accepted 1800000 ms for the short synthetic qualification. No long-duration survival
test was performed. The experiment's 1800-second ceiling applies **per worker**.

The four observed cases average 88.1155 seconds. Extrapolated baseline duration
exceeds 1800 seconds; increasing the outer timeout alone does not establish that the
unchanged monolithic evaluation worker can finish within its own safety limit.

[Implementation](../../../experiments/contrastive_learning_r6_77/durable77.py)
provides exclusive ordered case starts, hash-bound raw/completion commitments,
verified recovery, refusal to regenerate ambiguous work, corruption detection,
tracked foreground child processes, actual-worker identity handshakes, flushed RSS
samples, wall time and exit receipts. [Qualification](r6_77/LAUNCHER-QUALIFICATION.json)
passes **14 synthetic controls**, including real process completion and deliberate
timeout/termination. This is synthetic orchestration qualification, not live-model
or training qualification. Frozen memory/generation/worker ceilings were not raised.

One initial test expectation incorrectly called the invalid-PID measurement outside
its rejection wrapper. [Failure](r6_77/QUALIFICATION-FAILURE-1.json) and original
controls are retained; corrected controls use a separate `controls_2` directory.
The existing resource implementation correctly rejected that invalid PID and was
not changed. No participant settings or training retries were involved.
An initial publication link check also rejected the report-relative pending manifest
link before the manifest existed. Its [failure record](r6_77/PUBLICATION-CHECK-FAILURE-1.json)
is retained; the corrected check resolves only the two prospective publication files
in the exact R6.77 directory. No participant evidence was changed.

## Recovery blocker and baseline

The frozen historical worker appends a result only **after** generation and scoring
finish. Its stderr has five generation-warning lines, but its partial result has only
four records. There is no fifth raw output/token journal/start claim, complete base
seal or closed base-worker exit/resource receipt. Warning count is corroborating
evidence, not an exact model-call meter. The fifth case may have started or completed
generation before interruption; its precise state is unavailable.

The linked baseline therefore contains **4/30 completed observations**, all from the
24 structurally varied renderings, and **0/6 exposed calibrations**. Twenty-five later
cases were not reached under the sequential commitment order. The next case is
ambiguous; the 26 missing observations cannot all be described as never generated.
No case was silently rerun or scored from missing evidence.

| Dimension | Correct / completed diagnostic observations |
|---|---:|
| Strict decision validity | 4/4 |
| Operation correctness | 4/4 |
| Operand identities | 0/4 |
| Operand order | 0/4 |
| Dependencies | 1/4 |
| Deterministic reconstruction | 0/4 |
| Functional acceptance | 0 accepted; 4 NOT_REACHED |
| Full acceptance | 0/4 |

These are the original four observations, totaling **168 generated tokens** and
**352.462 seconds** combined inference/decoder time. The frozen diagnostic worker
did not measure decoder enforcement separately; that split remains unavailable.
No new baseline aggregate or adapter comparison is implied by partial evidence.

## Training, adapter and post-training stages

All are **NOT_REACHED**. Baseline completion and unresolved-protocol gates fail
before GPU preflight or training dispatch. Optimizer updates **0**, scheduler updates
**0**, presentations **0**, new model calls **0**. There is no new training loss,
GPU-memory measurement, training/inference wall-time observation, adapter artifact,
changed-parameter verification, fresh adapter reload or reference initialization.
These unavailable measurements are null, not fabricated zeros.

The authorized NF4 rank8 q/v QLoRA, 54 qualified records, four fixed passes,
216 presentations, at most54 updates, frozen AdamW/warmup6/linear54 schedule,
equal-record completion-only normalization and controlled cache release remain
unchanged and unexecuted in R6.77. Base-versus-adapter semantic results, operand-order
and dependency comparison, functional improvement, regressions and learning
classification are **NOT_ESTABLISHED**. Structural validity alone is not learning.

## Telemetry, limitations and next step

[Terminal telemetry](r6_77/TERMINAL-RESULT.json) distinguishes four reusable completed
observations from unknown historical total model calls, zero new model calls,
synthetic worker exits/resources, retained interruption and missing measurements.
The qualification records real current RSS, not guaranteed peaks between samples.
Only the synthetic interruption control is new; it is not another participant attempt.

Twenty-four renderings represent twelve synthetic requirements, and six calibrations
are exposed. Coordinator exposure and null Unit values remain limitations. No
independent generalization, model-learning or no-advantage conclusion is justified.

**Recommended next step:** explicitly decide whether the interrupted fifth generation
may be re-attempted as a labeled linked observation with unknown historical call cost,
or provide its original complete raw evidence. If authorized, separately qualify
bounded foreground evaluation batches under unchanged per-worker/resource limits
before one still-gated training attempt. R6.77 does not authorize either action.

## Publication and stop

[Publication identities](r6_77/PUBLICATION-IDENTITIES.json) and
[verification](r6_77/VERIFICATION.json) bind the additive report, implementation,
controls, identity/recovery receipts, telemetry and versioned documentation.
Production compiler/lowerer/runtime, experimental semantics and R6.3–R6.76 history
remain unchanged; kernel26, P6-A04 acceptance0 and P6-A05 access false. No dataset
expansion, comparison adapter, hyperparameter search, new training attempt or
credentials. **Stopped after this bounded linked attempt and publication. Await
explicit authorization.**
