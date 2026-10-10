# R6.58 — controlled cache release supports one accumulation window

**Final classification: `R6_58_CACHE_RELEASE_SUPPORTED`.**

**Recommended next action: A. Adopt controlled cache release**, prospectively and
only with separate authorization. The cache-release condition completed E01–E04
forward/backward, cleanup and four cache releases within the unchanged8GiB
allocator ceiling. All112 LoRA gradients were finite and correctly additive;
cache release preserved their exact bytes. The actual parameter-equality assertion
passed. No optimizer or scheduler updates occurred. The baseline stopped during
E04 forward on the device-free floor. No training workflow change or retry occurred.

The cache process subsequently exited1 on a **diagnostic scheduler-state assertion**,
not a memory, numerical or parameter-equality failure. That original failure remains
published. Its implications and offline explanation are detailed below; process
success and a complete terminal integrity receipt are not claimed.

## 1. Baseline and preservation

Initial git status was clean. [Baseline verification](r6_58/BASELINE.json) rechecks
R6.52–R6.56 publications, all5,387 inherited protected identities, all47 installed
package trees, private executables/lock, checkpoint/tokenizer/untrained adapter,
and matches R6.57's baseline. Both R6.56 and R6.57 publication manifests are
reconstructed and match their published identities before dispatch and after.
The R6.58 verification also requires zero tracked-file differences from HEAD.

The pinned model remains Qwen2.5-Coder-1.5B-Instruct revision
`2e1fd397ee46e1388853d2af2c993145b0f1098a`. Python3.12.11, torch2.7.1+cu128,
Transformers4.55.4, PEFT0.17.1 and BNB0.47.0 remain unchanged. R6.54 scheduler,
R6.55 AdamW (including weight_decay=0), R6.56 sampling and equal-record /4 loss,
and E01–E06 identities remain bound by the unchanged frozen configuration
`2b0fa8ee329e4cfa9e3d46c53151c2d266dd213fd7f62f8959d25a2ac3e0918b`.
Historical normalization controls remain preserved and verified; this round does
not repeat GPU training or the historical baseline inference diagnostics.

The [protocol](r6_58/PROTOCOL.md) and [preflight](r6_58/PREFLIGHT.json) freeze the
two conditions. The [worker](../../../experiments/memory_attribution_r6_58/worker.py)
applies explicit single-match instrumentation transformations to the read-only
R6.57 no-update worker and uses exact R6.56 model/manifest helpers. Effective-source
identities and the [offline line map](r6_58/EFFECTIVE-SOURCE-LINE-MAP.json) make the
executed source reproducible. No historical worker is modified.

## 2. Device-wide accounting

The RTX4070 has **12,878,086,144 bytes** of CUDA-reported total memory
(nvidia-smi12,282MiB); driver617.42, WDDM, display active. Each worker records a
pre-context census, post-context census, every synchronized boundary census and
postprocess census. [Initial inventory](r6_58/DEVICE-PREFLIGHT.json) and condition
directories preserve all raw GPU and process reports.

Before baseline context creation nvidia-smi reports2776MiB used/9235MiB free;
afterward it reports2888MiB used/9123MiB free. This **112MiB observed delta**
is context-associated, not pure context attribution: external allocations can
change between queries. CUDA mem_get_info after initialization reports
11,645,485,056 free bytes, while PyTorch allocated/reserved are both0. The CUDA
and WDDM/nvidia-smi views differ materially. They are retained separately;
neither is silently converted into the other's accounting domain.

| Category | Measurement and attribution boundary |
| --- | --- |
| A. Live PyTorch tensors | allocated and active bytes plus segment block states; cleanup allocated1,647,003,136 bytes in both conditions. |
| B. Allocator reservations | reserved bytes, fully inactive segments, inactive split blocks and release events; controlled release directly measures reclaimable reservations. |
| C. Context/libraries | observed112MiB census change at initialization; no isolated library breakdown or exclusive context measurement. |
| D. Other GPU processes | PID/name/type census identifies Windows desktop services, browsers, Spotify, Godot, OpenCode, ChatGPT and other existing applications. Every per-process memory field is **N/A under WDDM**; no individual byte attribution. No unrelated process terminated. |
| E. Unattributed/device-accounting residual | CUDA total-free-reserved at synchronized boundaries; includes own nonallocator allocations, other processes and accounting differences. Not equivalent to external-process memory. |

Baseline outside-allocator residual is1,282,932,736 bytes after E01/E02,
then3,288,367,104 after E03 cleanup: increase2,005,434,368 bytes. The associated
nvidia-smi census reports10,263MiB used/1748MiB free after E03 backward.
No offender or exact cause of that additional pressure is established. Cache-release
boundary residual remains1,282,932,736 bytes after each cleanup/release.

The baseline watchdog reads are unsynchronized and non-atomic. At the stop,
allocator reclamation was in progress: current reserved3,567,255,552 bytes,
peak8,178,892,800 and cumulative freed reservation5,131,730,944. Consequently
its7,900,004,352-byte computed residual is **not a coherent process-attribution
measurement**. Do not interpret that value as a sudden external allocation.

## 3. Allocator statistics and snapshots

[Analysis](r6_58/ANALYSIS.json) summarizes full memory_stats at every boundary,
including active/inactive split, allocation/free counts, cumulative peaks, retries
and OOMs. JSON snapshots retain segments, blocks, stack metadata and a bounded
12,000-event history after loading, each completed cleanup and the cache window.
Event history is a rolling tail, not a complete allocation log; cumulative stats
provide totals. PyTorch emits a retained warning that C++ context unwinding is
unsupported on this platform. Stack provenance is therefore limited.

Baseline cleanup snapshots show:

| Completed record | Reserved bytes | Fully inactive segment bytes | Inactive split bytes | Live allocated bytes |
| --- | ---: | ---: | ---: | ---: |
| E01 | 3,812,622,336 | 1,285,554,176 | 880,065,024 | 1,647,003,136 |
| E02 | 5,643,436,032 | 3,116,367,872 | 880,065,024 | 1,647,003,136 |
| E03 | 7,656,701,952 | 5,129,633,792 | 880,065,024 | 1,647,003,136 |

Thus measured reservation growth is **fully inactive segment growth**, with
stable live allocations and stable split fragmentation. It is not growing live
graphs or gradients. Increasing sequence lengths accompany larger temporary
activation peaks; exact allocator block-fit/operator causality is not established.
Fragmentation exists but its measured split growth does not explain the trajectory.

Controlled empty_cache releases exactly the snapshot's fully inactive segment
bytes after each cleanup:1,285,554,176;1,832,910,848;2,017,460,224;2,086,666,240.
Every release returns reserved memory to **2,527,068,160 bytes**, with live
allocation unchanged and880,065,024 inactive split bytes remaining. Free device
memory returns to9,068,085,248 bytes at recorded release boundaries. This establishes
reclaimable cache as a mechanism of improvement. It does not identify the exact
cause of the outside-allocator baseline pressure or prove optimal cache reuse.

## 4. Sequence-padding inspection

[Padding inspection](r6_58/PADDING-INSPECTION.json) and in-worker before-forward
records establish actual input/label/mask shapes[1,702], [1,752], [1,827], [1,855].
Attention masks are all ones with sums702/752/827/855. Supervised completion+EOS
counts329/370/425/461 retain causal shifted alignment and ignored prompt/newline
labels. Batch size1 needs no within-batch padding;2048 is a cap, not tensor width.
**Dynamic-padding condition SKIPPED:** no unnecessary static padding exists.
Tokenization, masking, sequence lengths and frozen implementation are unchanged.

## 5. Condition comparison and safety

Both conditions enforce reserved8GiB, RSS16GiB,1800s timeout and device-free
1.5GiB, with the same preflight2GiB headroom rule. No R6.57 higher diagnostic
ceiling is inherited; no limit is raised. Resolved RESOURCE-SAFETY.json files
precede model loading. Each condition has one exclusive dispatch/worker claim.

| Measurement | Baseline | Cache release |
| --- | ---: | ---: |
| Completed backward/cleanup calls | 3/4 | 4/4 |
| Peak allocated bytes | 3,808,492,544 (3.547GiB) | 3,880,693,248 (3.614GiB) |
| Peak reserved bytes | 8,178,892,800 (7.617GiB) | 4,613,734,400 (4.297GiB) |
| Minimum retained boundary/stop free bytes | 1,410,826,240 (1.314GiB) | 6,981,419,008 (6.502GiB) |
| Whole-process wall seconds | 74.276665 | 84.840259 |
| Process exit | 71, device-free floor | 1, post-window guard-state assertion |

Baseline cleanup device-free trajectory:7,782,531,072→5,951,717,376→
1,933,017,088 bytes, then E04 stop. Cache cleanup reserved trajectory:
3,812,622,336→4,359,979,008→4,544,528,384→4,613,734,400, followed each time
by2,527,068,160 reserved after release. No cache-condition memory safety stop.

Peak reservations are cumulative, reset once before loading. Baseline cap triggered
allocator reclamation during E04; the50ms device-free watchdog stopped first from
the available trace. That is not a CUDA OOM completion measurement. The floor is a
sampled stop threshold, not guaranteed atomic protection; cache's retained minimum
is a boundary minimum, not a continuously recorded global minimum. RSS is measured
inside the actual worker. No exclusive device isolation is claimed.

Census subprocesses, JSON snapshots, synchronization, Python collection and detached
CPU gradient copies add substantial overhead. Wall times include baseline checking,
model loading and instrumentation; they are not training throughput comparisons.

## 6. Gradient and parameter integrity

Both conditions have all112 intended LoRA gradients finite after each completed
backward, frozen-base gradients absent, and constant4,358,144-byte persistent
gradient storage. Detached CPU leaf-hook sum versus accumulated gradients has
maximum absolute error **0** through E01–E03 baseline and E01–E04 cache. This
verifies additive accumulation under the frozen per-record mean /4 rule, not an
independent derivative implementation. Initial trainable selection is112 tensors,
1,089,536 parameters, all LoRA, with exact R6.52 initialization identities.

Cross-condition E01–E03 losses are exactly1.8160520792007446,
1.7120777368545532 and1.517041563987732, and all accumulated-gradient SHA256
identities match exactly, stronger than declared tolerances. E04 cache loss is
1.4645479917526245; baseline E04 comparison is **NOT_REACHED**. Each cache release
preserves all current gradient bytes exactly; no accumulated gradients are reset.

For the cache process, the frozen actual assertion
`assert initial == adapter_after and base_before == base_after` **passed** after
computing final manifests. Execution then reached the subsequent scheduler-state
assertion at effective line205. This establishes measured adapter/base parameter,
buffer and quant-state equality by actual in-worker comparison. Final manifests
were not separately persisted because the terminal receipt follows line205.
Baseline final equality is **NOT_REACHED** due to the hard stop.

The scheduler assertion compares a dictionary captured before assigning
`scheduler.step = forbidden` with one afterward. Installed scheduler state_dict
includes instance attributes other than optimizer; the added **step callable**
makes that comparison fail without a schedule tick. The
[CPU-only guard control](r6_58/SCHEDULER-GUARD-CONTROL.json) reproduces the failure
and shows all state excluding that added callable exactly unchanged, epoch0/LR0,
empty optimizer state and zero updates. Actual failed worker state dictionaries
were not persisted; explanation rests on the exact source and installed API plus
the reproduced control. No GPU retry or frozen-worker repair occurred.

Both executed paths contain no optimizer/scheduler step after construction; hard
guards forbid them. Scheduler constructor's initial epoch0/LR0 setup is inherited,
not a training scheduler update. No clipping, optimizer moments, parameter write or
adapter save. The original exit1/FAILURE.json and conservative worker RESULT.json
remain unchanged: their `four_record_completed=false` conflates terminal integrity
failure with execution completion. The separately versioned analysis distinguishes
the four retained backward records from terminal process failure.

The first offline analysis-control invocation failed a JSON-key lookup before
constructing its CPU optimizer. That publication helper lookup was corrected to
the frozen training configuration's nested kwargs; no model was loaded and no
experiment source or outcome was repaired.

## 7. Exactly one next action and remaining limits

**A. Adopt controlled cache release after completed microbatch cleanup**, retaining
gradients and every existing sampling/loss/model/resource setting. It is the smallest
measured adjustment: it reclaims fully inactive segments, completes this window,
preserves shared-prefix derivatives and passes actual parameter equality. No production
training implementation adopts it in R6.58. A separately authorized20-step attempt
is **justified as a bounded feasibility test**, not already qualified to succeed.

Remaining limits: external-process bytes and context/library components are
unattributed under WDDM; exact outside-allocator pressure cause and allocator-fit
mechanism unresolved; watchdog observations non-atomic; incomplete baseline E04
derivative comparison; final equality hashes not separately retained; post-window
guard-state assertion defect preserved; no AdamW moment/update/checkpoint memory
qualification; E05/E06 and subsequent windows untested. No full20-step fit, model
learning, generalization, efficiency benefit or trained-model result is claimed.

## 8. Publication and stop

[Publication identities](r6_58/PUBLICATION-IDENTITIES.json) bind all sources,
protocol, inventories, raw snapshots/stats/gradients/failures, analysis and docs.
[Verification](r6_58/VERIFICATION.json) rechecks historical/protected/environment
identities, frozen source bindings, additive paths, JSON/Python/links/whitespace,
credential patterns and git diff --check. The terminal failure is preserved rather
than turned into a clean process-success claim.

The first publication seal failed its link check because VERIFICATION.json had
not yet been created. The publication-only helper now creates an explicitly
unpassed placeholder before checking, then replaces it only after all checks pass.
No diagnostic or frozen source changed; no model process was dispatched.

Production kernel26, compiler/lowerer/runtime and experimental semantics unchanged.
New execution primitives0; optimizer/scheduler updates0; trained adapter creation0;
dataset expansion0; Python comparison adapter0; additional diagnostic conditions0;
P6-A04 acceptance executions0; P6-A05 access false. AI-independent deterministic
execution preserved. **Stopped after bounded diagnostics and publication. Await
explicit authorization before training.**
