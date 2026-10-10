# Hardware, licensing and effort assessment — R6.50

Planning input: [verified R6.47 inventory](../r6_47/MODEL-FEASIBILITY.md), RTX4070
12,282 MiB VRAM (~12 GB marketed), Ryzen7700X, nominal32 GiB RAM (31.11 GiB visible).
R6.47 observed 8,872 MiB free VRAM and ~1.57 TiB free D: storage; these fluctuate
and are **not new live measurements**. Training packages were absent in that
inventory; no new install/import/weight inspection is performed here. The existing
Ollama GGUF inference artifacts are not qualified trainable checkpoints.

## Candidate sizes and feasibility

Illustrative sizes only; no final model family/revision selected. Raw BF16 weights
use about 2P bytes, ideal 4-bit about 0.5P. Planning ranges below inherit R6.47's
unmeasured batch1, rank8–16, sequence512–2048, activation-checkpointing assumptions.

| Size | BF16 weight-only | Ideal 4-bit | BF16 LoRA estimated total | QLoRA estimated total | Judgment |
| --- | --- | --- | --- | --- | --- |
| 1.5B | 2.8 GiB | 0.70 GiB | 4–8 GiB | 3–6 GiB | Most conservative local qualification candidate |
| 3B | 5.6 GiB | 1.4 GiB | 8–14 GiB | 5–9 GiB | QLoRA plausible; LoRA/context fit uncertain |
| 4B | 7.5 GiB | 1.9 GiB | 8–14+ GiB | 5–9+ GiB | QLoRA plausible but architecture/vocabulary sensitive |

Quantization metadata, optimizer/gradients, high-precision modules, attention/logits,
KV/cache and CUDA workspace add overhead. Preserve 1–2 GiB display/background
headroom; historical free VRAM is smaller than total VRAM. Gradient accumulation
does not fix an overlength microbatch. Windows/Python3.14 and training-kernel package
compatibility require a separately authorized pinned environment qualification;
do not assume inference support establishes training support. 32 GiB RAM is plausible
for streamed small-checkpoint processing; avoid full-optimizer offload assumptions.

## Effort and cost scenarios (estimates, not quotes)

- Human commissioning/review/custody setup for a two-episode family: budget 2–5
  person-days plus wait time for actual independent humans. Four new training
  contracts/two conventional pairs per component: roughly 3–10 engineer/reviewer-days,
  highly dependent on ambiguity and state/authority obligations. Meter actual effort.
- A future smoke test might cap **0.1M processed tokens per adapter**, one pass,
  short context. Assumed 10–100 tokens/s yields 0.28–2.8 GPU-hours per adapter,
  0.56–5.6 for both; allow 2–12 total GPU-hours for loading/checks. This is not
  measured throughput and the existing ten episodes are not assumed to supply it.
- A later 0.1–1M tokens/epoch, 1–3 epoch study at that throughput spans roughly
  0.28–83 GPU-hours **per adapter**, plus tuning/seeds/evaluation. Comparable budgets
  may be token-limited and compute-capped; report both rather than extrapolate gains.
- Local electricity: `measured wall kW * hours * local price/kWh`; illustration
  0.3 kW * 12 h = 3.6 kWh before CPU preparation. No measured power or tariff here.
  Rental illustration at assumed $0.50–$2/GPU-hour: 2–12 hours costs $1–$24 before
  storage/egress/setup; actual current quotes and compatible GPU must be obtained.
- Evaluation illustration: 12 tasks * 4 cells * 3 seeds = 144 trials; at assumed
  2–10 min/trial, 4.8–24 participant-hours plus deterministic scoring/repairs.
  These are budget examples, not an authorized evaluation size or time measurement.
- Reserve 10–30 GiB for one 1.5–4B checkpoint/tokenizer/cache plus two modest adapters
  and optimizer receipts; broad rank/module targeting increases adapter storage.
  Reserve 0.1–5 GiB bounded-pilot raw evidence, and estimate later storage as
  `unique episodes * measured bundle bytes + replay/trajectory bytes + backups`.
  Do not multiply correlated rows into an apparent semantic dataset scale.

Local compute minimizes external custody exposure and is plausible for short-context
small adapters. Rental may offer more memory and compatible Linux tooling, but costs,
data-export rights, custodian access and deletion/log-retention controls must qualify.
Neither route solves missing independent evaluation or paired data.

## Licensing and authorization gate

For each candidate pin exact model revision, base/instruct status, tokenizer/template,
tensor format, license and derivative/distribution restrictions. R6.47's illustrative
Qwen2.5-Coder sizes have differing license terms; open weights do not guarantee
unrestricted training or distribution. Recheck the exact card/license later; no
current license adjudication or final checkpoint selection is claimed. Confirm dataset
source/target rights and owner permission separately from model rights. R6.50 authorizes
design only, not training, downloads, dependencies or redistribution.
