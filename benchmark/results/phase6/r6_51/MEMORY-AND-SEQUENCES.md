# R6.51 — Sequence and memory planning (not allocation measurements)

[Per-episode estimates](CONVERSION-ASSESSMENT.json) measure actual UTF8 lengths of
converted text and use **bytes/4 to bytes/2** as a deliberately approximate planning
range. This is not a tokenizer measurement or upper bound; hash strings, numbers,
punctuation and escaped JSON can tokenize very differently. No selected model
tokenizer is installed. Add approximately 32–128 tokens of chat-template/EOS overhead
as another estimate; exact tokenization and supervision masks are prerequisites.
Provenance metadata is excluded from model text.

| Text | Measured bytes | Estimated tokens |
| --- | --- | --- |
| E01–E08 compact requirement | 264–415 | 66–208 |
| S01/S02 stateful requirement | 1,532–1,611 | 383–806 |
| Stateless complete symbolic target | 863–2,388 | 216–1,194 |
| Stateful intent target | 1,926–2,714 | 482–1,357 |
| Full prompt + target, all ten | 2,441–5,736 | 611–2,868, plus chat overhead |
| Existing validation feedback | 450–658 | 113–329 (not included in initial SFT) |

E01–E06 full records estimate 611–1,477 tokens before template overhead. E07/E08
estimate 1,012–2,059 and may overflow 2,048; stateful records estimate 1,218–2,868.
Use **2,048** initial maximum for a short-context smoke subset, only after actual
tokenization verifies complete target + EOS fit. Reject oversized rows; never
truncate symbolic targets. Use 4,096 only for a separately allocated/frozen later
cohort including long stateful/composition rows.

Tool trajectories have **no measured semantic examples** here. A planning scenario
of 2–8 turns with 200–800 token state/call/feedback per turn adds roughly 400–6,400
tokens plus requirement/tool schema; this is hypothetical, not an observed trajectory
distribution. Validation feedback above is artifact evidence, not observed AI repair
history. Tools/state schemas can dominate context; qualify real captures later.

## Memory model

For frozen BF16 weights: 2 bytes × parameter count. For ideal quantized weights:
0.5 bytes × parameters, then add nonquantized layers/metadata. LoRA trainable count
for a linear layer is r × (input_dim + output_dim). With rank8 attention q/v only,
the 1.5B GQA architecture yields on the order of 1–2 million adapter parameters
(exact matched module dimensions must be measured). BF16/FP32 trainables, gradients,
FP32 Adam moments/master tensors require roughly 12–20 bytes per trainable
parameter, tens of MB here, but activations/logits dominate more than adapter size.
The ~152k token vocabulary makes a 2,048×vocab FP32 logits tensor ~1.25 GB before
additional loss work; actual fused/chunked loss behavior matters. Full-model Adam
training needs multiple model-sized gradients/states and is not the plan.

| Configuration: microbatch1, checkpointed, SDPA | Planning peak VRAM, including training buffers but excluding other apps |
| --- | --- |
| 1.5B NF4 QLoRA, rank8 q/v, 2,048 | **4–7 GiB** |
| 1.5B BF16 LoRA, same short sequence | **6–9 GiB** |
| 3B NF4 QLoRA, 2,048 | **6–9 GiB** |
| 4B NF4 QLoRA, 2,048 | **7–11 GiB** |
| 1.5B QLoRA, 4,096 | **6–10 GiB**, especially uncertain logits/activation overhead |

These are broad engineering estimates, **not measured fit** and not guarantees.
No tensor was allocated. Current dedicated total is 12,282 MiB, but inventory free
is only 9,078 MiB (earlier probe 9,314); GUI/display usage fluctuates. Do not budget
all nominal VRAM. Reserve at least 1.5 GiB free, abort on OOM without outcome-tuned
retry. Require a representative actual allocation/backward test in the later setup.

RAM is 33,408,004,096 bytes (~31.11 GiB), with ~10.49 GiB free at final inventory snapshot.
Use low-memory loading and avoid duplicated CPU tensors. Plan 8–16 GiB process RAM
for the 1.5B stack/load, unmeasured; 32GiB-class total supports planning, while current
free RAM may need headroom. Proposed cap is 16 GiB process RSS. Disk free snapshots:
C: ~42.8 GiB, D: ~1.57 TiB; reserve 15–25 GB on D: for 1.5B environment/cache/output.
Larger checkpoints cost more; no storage was allocated for models.

Batch plan: per-device batch1, accumulation4, effective batch4; accumulation reduces
simultaneous examples but does not eliminate one-sequence activation/logit peaks.
Use no packing, no eval-logit retention and dataloader workers0. Increasing sequence
length raises memory strongly; model maximum context is not a feasible training
length on this host by default.
