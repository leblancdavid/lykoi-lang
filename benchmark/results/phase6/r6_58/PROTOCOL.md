# R6.58 — bounded CUDA attribution protocol

Authorized by the owner's R6.58 request. One baseline and one cache-release
fresh process, E01→E02→E03→E04, no optimizer/scheduler updates or adapter saves.
Read-only instrumentation transforms the pinned R6.57 diagnostic, reusing the
unchanged R6.56 model/manifest helpers. Hashes bind transform and effective source.
All47 package trees, historical publications, protected identities, checkpoint,
tokenizer, dataset, optimizer, scheduler and normalization remain checked.

Original R6.56 limits remain: reserved8GiB, worker RSS16GiB,1800s timeout,
device-free1.5GiB. Preflight requires8GiB ceiling with2GiB available headroom;
ceiling=min(8GiB, reserved+free-2GiB). No limit increase.50ms in-worker watchdog
retains the R6.57 hard-stop behavior; sampled floor is not an atomic reservation.
No process termination except the diagnostic's own safety stop.

Record device census before CUDA context and afterward and at each synchronized
boundary: nvidia-smi total/free/process reports (including N/A WDDM limitations),
full allocator stats, allocated/reserved/active/inactive-split peaks and cumulative
allocation/release counts. Enable bounded allocator event history (12,000 events)
and JSON snapshots after loading, completed cleanup and completed window.
Hard stops may preempt snapshots, final hashes and census. Device-used minus
PyTorch-reserved is an outside-allocator residual, not an attributed process total.
Context census deltas are concurrency-confounded; no unsupported causal attribution.

Baseline retains cache. Cache condition adds only empty_cache after each completed
cleanup, preserves gradients, and compares their exact bytes before/after release.
Both conditions use mean completion+EOS loss /4 and frozen seed/model/selection.
Cross-condition loss tolerance rtol1e-6/atol1e-7; gradient rtol1e-5/atol1e-7;
exact SHA256 equality is a stricter cross-condition gradient check. If unequal,
do not assert tolerance qualification from hashes. Per-backward CPU leaf-hook sum
checks accumulation; frozen normalization control binds the /4 rule.
Final adapter/base/buffer/quant-state equality and finite112 LoRA-only gradients
are necessary for full-window integrity. Constructor scheduler initialization
is inherited; subsequent step methods hard-raise. No clipping or parameter writes.

Source inspection establishes actual batch1 lengths702/752/827/855 and ones masks,
with2048 only an upper bound. Conditional dynamic-padding diagnostic is skipped.
Record actual shapes/mask sums in-worker. No combined modifications or reruns.

Publish partial failures and exactly one A–E recommendation; supported adjustment
requires safe four-record completion and unchanged intended gradients/parameters.
One window cannot qualify20 updates or AdamW state materialization. Preserve all
R6.3–R6.57 history/production/kernel26; no P6-A04 execution/P6-A05 access. Stop
after publication and wait for explicit authorization before training.
