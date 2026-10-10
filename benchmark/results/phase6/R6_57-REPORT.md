# R6.57 — QLoRA memory diagnosis stops on device-free safety floor

**Final classification: `R6_57_MEMORY_DIAGNOSIS_PARTIAL`.**

The single authorized no-update diagnostic completed E01/E02/E03 backward and
cleanup, then stopped during **E04 forward** on device-free memory below1.5GiB.
It reproduced reservations above R6.56's8GiB reference: **8,698,986,496 bytes
(8.1015625GiB) peak reserved**, with **3,808,492,544 bytes (3.546935GiB) peak
allocated**. Four-record accumulation and final in-memory parameter equality
were **NOT_REACHED**. Zero optimizer updates, zero scheduler updates and zero
adapter saves. No retry or prospective training change was made.

## 1. Authorization and preservation

The owner authorized a bounded nonproduction diagnosis using the existing
checkpoint, environment, dataset and frozen four-record loss accumulation, with
no updates or hyperparameter/semantic changes. Initial git status was clean.
The original R6.56 worker and its `R6_56_RESOURCE_OR_STACK_GAP` classification,
raw failure, original assertion correction and all historical publication bytes
are preserved. The frozen [protocol](r6_57/PROTOCOL.md) records the dispatch,
measurement boundaries, safety formula and no-update guards.

The original R6.56 read-only verifier initially failed when invoked using system
Python because it inspected that interpreter's installed distributions. The same
verifier **passed under the pinned private Python before edits**. No environment
repair occurred. The R6.57 preflight and post-run checks also use that interpreter.

[Baseline verification](r6_57/BASELINE.json), [source preflight](r6_57/SOURCE-PREFLIGHT.json)
and [six-record identities](r6_57/SOURCE-DATASET-IDENTITIES.json) verify:

- R6.52–R6.56 publication payload hashes and manifest/verification bindings.
  R6.56 publication manifest SHA256:
  `8db4bf13dc941a4f1baad6c44963e5c5d74e356cdc831429ba37e08fbcaae71f`.
- All5,387 inherited protected identities; production32, VM21, wrapper27,
  adapter79, tool contracts48, registry11. Production kernel remains **26**.
- All47 installed package trees, RECORD identities, executable/DLL/uv and lock;
  Python3.12.11, torch2.7.1+cu128, Transformers4.55.4, PEFT0.17.1, BNB0.47.0.
- All9 checkpoint/tokenizer assets and3 existing untrained-adapter files:
  Qwen2.5-Coder-1.5B-Instruct revision
  `2e1fd397ee46e1388853d2af2c993145b0f1098a`.
- E01–E06 conversion/provenance/token/label identities exactly match R6.56.
  Native chat template; completion+turn EOS only, ignored prompt/newline/padding;
  no packing, truncation or dataset expansion.
- Exact R6.55 AdamW installed signature/source/configuration, R6.54 scheduler
  source/manifest, R6.56 sampling and loss/configuration identities.
  Training configuration remains
  `2b0fa8ee329e4cfa9e3d46c53151c2d266dd213fd7f62f8959d25a2ac3e0918b`.
- The repeated [CPU normalization control](r6_57/NORMALIZATION-CONTROL.json)
  is exactly equal to R6.56's frozen evidence, including its pooled-token
  negative control. Each record's mean loss is divided by4 before backward.

[Preflight](r6_57/PREFLIGHT.json) binds the diagnostic worker/orchestrator before
execution. The exclusive [dispatch](r6_57/DISPATCH-CLAIM.json) and actual-worker
[claim](r6_57/WORKER-CLAIM.json) establish one dispatch, actual PID62624 and pinned
executable. [Process receipt](r6_57/PROCESS.json): exit71,44.4387412s including
worker baseline checking/model loading/instrumentation; no loop-only timing claim.

## 2. Accumulation-loop inspection and instrumentation

[Inspection](r6_57/ACCUMULATION-INSPECTION.md) finds scalar loss-history lists,
default backward graph release, no retain_graph=True, no gradient reset within
the window and deletion of output/loss/input/labels after each backward. No
likely retention defect is established by source review, and no repair is made.

The experiment-local [worker](../../../experiments/memory_diagnostic_r6_57/worker.py)
reuses historical exact model-construction/manifest functions and the same
seed651/NF4/double-quant/BF16/r8/alpha16/dropout0.05/q-v/FP32-adapter setup,
non-reentrant gradient checkpointing, SDPA/cache off, batch1/accumulation4,
max2048. Its only presentations are E01→E02→E03→E04, lengths702/752/827/855.
The optimizer/scheduler are constructed with frozen settings; both step methods
then hard-raise. Scheduler constructor initialization to epoch0/LR0 is preserved;
there is no subsequent scheduler step. No clipping or checkpoint/adapter save.

In-worker synchronization precedes every recorded load/forward/backward/cleanup
boundary. Peaks reset **once before model loading**, never between records.
Telemetry includes allocated/reserved/cumulative peaks/free/total, inactive split
bytes, active allocations, allocator retries/OOMs and actual-worker RSS. Trace
records are persisted before boundary assertions. The50ms safety watchdog uses
unsynchronized readings and persists numeric evidence before hard exit.

Detached CPU leaf-hook copies verify gradient accumulation; weakrefs verify
output/logits/loss/input/label lifetime. Python garbage collection, extra CPU
copies and additional synchronization are disclosed instrumentation and may
affect timing/lifetimes. No saved-tensor hook changes autograd behavior. No cache
flush occurs within the window. The planned post-window empty_cache observation
and final hashes were not reached. The frozen diagnostic worker is preserved
unchanged after this attempt.

## 3. Memory trace and original-threshold reproduction

[Complete available boundary trace](r6_57/MEMORY-TRACE.json) and
[numeric safety packet](r6_57/SAFETY-STOP.json) retain the observations.
All values below are **bytes**, with cumulative worker peaks.

| Boundary | Allocated | Reserved | Peak allocated | Peak reserved | Device free |
| --- | ---: | ---: | ---: | ---: | ---: |
| Model loaded | 1,625,605,632 | 2,518,679,552 | 2,087,705,088 | 2,518,679,552 | 9,101,639,680 |
| E01 after forward | 2,613,222,912 | 2,952,790,016 | 2,617,541,632 | 2,952,790,016 | 8,650,752,000 |
| E01 after backward | 2,073,651,200 | 3,812,622,336 | 3,466,490,368 | 3,812,622,336 | 7,782,531,072 |
| E01 after cleanup | 1,647,003,136 | 3,812,622,336 | 3,466,490,368 | 3,812,622,336 | 7,782,531,072 |
| E02 after forward | 2,696,345,088 | 4,729,077,760 | 3,466,490,368 | 4,729,077,760 | 6,866,075,648 |
| E02 after backward | 2,104,195,072 | 5,643,436,032 | 3,610,697,728 | 5,643,436,032 | 5,951,717,376 |
| E02 after cleanup | 1,647,003,136 | 5,643,436,032 | 3,610,697,728 | 5,643,436,032 | 5,951,717,376 |
| E03 after forward | 2,801,865,728 | 6,650,068,992 | 3,610,697,728 | 6,650,068,992 | 4,945,084,416 |
| E03 after backward | 2,150,333,440 | 7,656,701,952 | 3,808,492,544 | 7,656,701,952 | 1,820,291,072 |
| E03 after cleanup | 1,647,003,136 | 7,656,701,952 | 3,808,492,544 | 7,656,701,952 | 1,819,963,392 |
| E04 before forward | 1,647,017,472 | 7,656,701,952 | 3,808,492,544 | 7,656,701,952 | 1,819,963,392 |
| E04 in-flight watchdog stop | 2,840,513,024 | 8,698,986,496 | 3,808,492,544 | 8,698,986,496 | 778,858,496 |

Before-forward measurements for all four records are retained in the raw trace.
E04 after-forward/backward/cleanup and after-four-steps are **NOT_REACHED**.
The watchdog sample is not a synchronized E04 forward-completion measurement.

R6.56's reserved>8GiB condition is **reproduced**, exceeding the reference by
109,051,904 bytes. Its exact original numeric peak remains unavailable; this
round does not reconstruct it. E01/E02/E03 mean losses exactly match the original
1.8160520792/1.7120777369/1.5170415640, supporting path/seed consistency.

## 4. Gradient, retention and parameter-integrity evidence

[Gradient evidence](r6_57/GRADIENTS.json) establishes for each completed record:

- All112 intended LoRA tensors have finite gradients; all frozen-base gradients
  are absent. LoRA gradients have no grad_fn and do not require gradients.
- The stored gradient equals the CPU sum of detached per-backward leaf-hook
  contributions, **maximum absolute difference0** for E01, E02 and E03.
  This verifies actual additive accumulation through three calls. The separate
  frozen numerical control verifies equal-record /4 loss weighting; no independent
  full-model derivative or complete four-record qualification is claimed.
- Persistent gradient storage is **4,358,144 bytes**, constant across these
  records. Persistent gradients are intended and do not constitute graph retention.
- All five tracked temporary weakrefs are dead after every completed cleanup.
  The live allocated baseline is **exactly1,647,003,136 bytes** after each cleanup,
  with no inter-microbatch live allocation growth.

[Initial parameters](r6_57/INITIAL-PARAMETERS.json) match all112 historical
adapter tensor identities and record frozen-base/buffer/quant-state hashes.
[Integrity status](r6_57/PARAMETER-INTEGRITY-STATUS.json) explicitly records
postdiagnostic adapter/base equality as **NOT_REACHED** because the hard stop
preempted final hashing. No update call exists in the diagnostic path and both
step methods are guarded; zero optimizer/scheduler updates is established by
source/control-flow evidence. That does **not** substitute for missing final
tensor hashes. No full absence-of-parameter-change qualification is claimed.

## 5. Allocated versus reserved analysis

[Machine-readable analysis](r6_57/MEMORY-ANALYSIS.json) distinguishes observations
from unresolved mechanisms:

| Factor | Evidence and supported conclusion |
| --- | --- |
| Persistent gradients | 4,358,144 bytes constant; cannot explain GiB-scale reservation growth. |
| Other persistent live allocations | Cleanup is21,397,504 bytes above loaded baseline, including gradients and other persistent framework allocations; remaining17,039,360 bytes not specifically attributed. No continuing live baseline growth after E01. |
| Temporary forward/backward tensors | Forward/live and cumulative allocated peaks rise with longer records; backward frees substantial allocation, cleanup returns to the identical baseline. Supports temporary peaks. Exact operator allocation provenance not collected. |
| Allocator cache/non-live reservations | Cleanup reserved-minus-allocated rises2,165,619,200→3,996,432,896→6,009,698,816 bytes while live allocation is stable. Reservation retention rather than retained live graphs accounts for the measured divergence. Specific cache/segment reuse cause remains unresolved. |
| Fragmentation | Cleanup inactive split bytes are880,065,024 for all three records, not increasing; peak inactive split1,080,947,712. Split fragmentation exists but its recorded growth does not explain the increasing total reservation. No fragmentation-optimality claim. |
| Retained computation graphs | No source retention construct; graph-free gradients, dead tracked temporaries and identical cleanup allocation baseline provide evidence against unnecessary retention in E01–E03. No blanket E04/future-window absence proof. |
| Optimizer allocations | Constructed AdamW without any update; no moment-state initialization path is called. Final empty-state inspection was not reached. GiB growth is not evidenced as AdamW moment storage. |
| Other device-wide pressure | total-free-reserved residual rises from~1.19GiB after E01/E02 to~3.17GiB after E03. This is outside measured PyTorch reservations, but is not process attribution; other processes, CUDA/library allocations or accounting effects remain unresolved. |

The ~2.1GB increase in outside-allocator residual prevents a defensible claim
that only raising the PyTorch reserved ceiling is safe. No device process census,
allocation stack snapshot or post-window cache-release result is available.
We do not identify an offending process or claim a specific allocator bug.

## 6. Resource safety assessment

[Resolved safety configuration](r6_57/RESOURCE-SAFETY.json) was recorded before
model load: RTX4070 total12,878,086,144 bytes; verified initial free11,645,485,056
bytes. The precommitted formula established a **9,498,001,408-byte diagnostic-only
allocator ceiling**, leaving2GiB of verified preflight headroom: preserved1.5GiB
floor plus0.5GiB extra margin. PyTorch per-process allocator cap enforced that
ceiling. This did not amend the original8GiB training reference.

The50ms in-worker watchdog stopped on **DEVICE_FREE_LIMIT** at778,858,496 free
bytes (~0.725GiB), before an observed CUDA OOM. Sampled free memory can drop below
the floor between samples: it is a stop threshold, not a guaranteed reservation.
No allocator OOM/retry is reported; hard allocator ceiling was not reached.
Actual-worker RSS at stop2,528,104,448 bytes, below16GiB; this corrects the launcher-
only polling problem for the available diagnostic samples. Device safety includes
uncontrolled non-PyTorch and other-process allocations; their growth was not
prevented by the allocator cap. Safe continuation was not established, so the
process stopped and was **not restarted**.

The original8GiB reserved reference is insufficient for the observed path.
That fact alone does not qualify a higher safe training ceiling or establish
that all four microbatches, optimizer allocation or20 updates fit.

## 7. Exactly one prospective recommendation

**D. Investigate unresolved memory behavior further.**

The smallest justified next action is a separately authorized no-update diagnosis
that attributes allocator reservation/segment reuse and device-wide pressure,
while preserving this partial trace and re-establishing current safe headroom.
Evidence supports cache/non-live reservation growth and rejects three-record
live-graph growth, but the simultaneous free-memory collapse makes a ceiling
increase alone unjustified. No corrective/configuration action is implemented
in this round. No full20-step training fit or trained-model benefit is claimed.

## 8. Publication verification and stop

[Publication manifest](r6_57/PUBLICATION-IDENTITIES.json) binds diagnostic source,
protocol/preflight, raw trace/stop/process, analysis/integrity status, report and
versioned companion docs. [Verification](r6_57/VERIFICATION.json) rechecks all
historical publication/protected/environment/external identities, additive paths,
source/JSON/link/whitespace/credential checks and `git diff --check`. No frozen
implementation/source or publication file was repaired from the outcome.

Production compiler/lowerer/runtime and experimental semantics unchanged;
kernel26; new execution primitives0; optimizer/scheduler updates0; trained adapter
creation0; dataset expansion0; Python comparison adapter0; hyperparameter search0;
P6-A04 acceptance executions0; P6-A05 access false. AI-independent deterministic
execution is preserved. **Stopped after the bounded diagnosis and publication;
await explicit authorization before further work.**
