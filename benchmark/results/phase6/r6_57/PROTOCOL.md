# R6.57 — frozen no-update memory diagnosis

Owner authorization: one bounded nonproduction investigation of R6.56's memory
halt, using its pinned environment/checkpoint/tokenizer/configuration and first
four presentations E01 → E02 → E03 → E04. No optimizer/scheduler updates,
parameter changes, adapter save, configuration search or semantic changes.

## Baseline and dispatch

Before any model load, verify R6.52–R6.56 publication manifests and receipts,
5,387 inherited protected identities/kernel26, all47 installed distribution
trees, executables/lock/checkpoint/tokenizer/untrained adapter and six source,
token and label identities. Recheck exact installed AdamW, schedule and causal
loss source identities; repeat the frozen CPU normalization control. Freeze
worker/orchestrator hashes in PREFLIGHT.json. One exclusive dispatch claim and
one exclusive actual-worker claim; no automatic retry.

The initial historical verifier was inadvertently invoked with system Python
and failed its installed-package equality assertion. Reinvocation with the
pinned private Python passed the full original R6.56 verifier before edits.
This was a read-only verification invocation; no model was dispatched and no
environment installation or repair was made.

## Instrumented actual worker

Reuse the historical worker's exact model construction and manifest functions.
Seed651, NF4/double quant/BF16, non-reentrant checkpointing, SDPA/cache off,
r8/alpha16/dropout0.05 q/v LoRA with FP32 trainable tensors; no precision/batch/
length changes. Construct the exact optimizer/scheduler, then replace both
step methods with hard-raising guards. Scheduler construction's initial tick
sets epoch0/LR0 as in R6.56; no later scheduler tick is permitted.

Execute exactly four frozen model forwards and `(loss / 4).backward()` calls.
Preserve adapter gradients; scalar loss history only. Detached CPU leaf-hook
copies permit comparison of persistent gradients against the independent sum
of each backward's contributions, with rtol1e-5/atol1e-7. This checks accumulation
mechanics, not an independent full-model derivative calculation. The unchanged
CPU normalization control separately checks equal-record weighting versus pooled
token weighting. No clipping, optimizer state materialization or parameter write.

Synchronize and durably record allocated/reserved/peak allocated/peak reserved,
device free/total, selected allocator statistics and actual-worker RSS after
model load; before/after each forward; after backward; after temporary cleanup;
after four calls; after integrity checks. Reset peaks **once before loading**.
Weakrefs cover each output/logits/loss/input/label object. Delete the frozen loop's
temporaries, collect Python garbage and retain cumulative gradients. Additional
measurement/CPU-copy/collection work is disclosed; it may affect timing and
asynchronous lifetime compared with the historical worker.

After the complete window and parameter checks only, `empty_cache()` is an
isolated allocator observation with gradients preserved, not a change to the
training window. No microbatch-level cache flushing or allocator tuning.

## Prospective safety rule

8GiB remains the original training diagnostic reference. Before loading, verify
current device free/total and set the diagnostic-only allocator ceiling to
`min(10GiB, initial_reserved + verified_free - 2GiB)`. The2GiB reserve comprises
the frozen1.5GiB minimum free plus0.5GiB extra preflight margin. If the resulting
ceiling is not above8GiB, stop before loading; no unsafe continuation.

Record the resolved ceiling before loading. Enforce it through PyTorch's hard
per-process allocator fraction; a50ms in-worker watchdog stops on device free
below1.5GiB, reservations above the diagnostic ceiling, or actual-worker RSS
above16GiB. Persist numeric safety evidence before hard exit. Parent timeout1800s.
Non-PyTorch allocations and other GPU processes are outside the allocator cap;
the free-memory watchdog is sampled, not atomic isolation or an exhaustion proof.
Any stop publishes a partial trace; no retry or lowered-resource substitution.

## Publication and stopping

Complete four-record trace plus exact adapter/base/buffer/quant-state equality,
finite adapter-only graph-free gradients, correct accumulation and unchanged
empty optimizer state/scheduler state are required for qualification. Analyze
allocated versus reserved, cleanup baselines, peaks and inactive split bytes.
No full20-update fit claim. Exactly one recommendation A/B/C/D; do not implement
it. Preserve R6.56's gap/abort and R6.3–R6.56 bytes; no P6-A04 acceptance/P6-A05
access. Verify publication/source/links/credential patterns and git diff --check.
Stop after publication.
