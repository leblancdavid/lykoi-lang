# Open-weight model and hardware feasibility

## Current read-only observations — 2026-10-10

| Item | Observed |
|---|---|
| CPU | AMD Ryzen7 7700X,8 cores/16 logical processors |
| System memory | 33,408,004,096 bytes visible (31.11 GiB; nominal32 GiB machine) |
| GPU | NVIDIA GeForce RTX4070 |
| VRAM |12,282 MiB total;8,872 MiB free at inspection |
| Driver |617.42 |
| D: storage |4,000,475,770,880 bytes total;1,724,772,339,712 free (about1.57 TiB) |
| Python in active shell |3.14.3 |
| Training packages discoverable without import |torch/transformers/peft/bitsandbytes/accelerate/trl: all false |
| Installed inference runtime |Ollama0.35.0 |
| Relevant installed inference models |qwen2.5-coder:1.5b-base (~986 MB), qwen3:8b (~5.2 GB); larger quantized models also present |

Commands were CIM metadata queries, `nvidia-smi --query-gpu`, `ollama list/version`
and Python `find_spec`, not weight loading/inference. Free VRAM/storage fluctuate.
No credential stores, model-weight bytes or training packages were inspected/imported.
An installed GGUF Q4 model is an inference artifact, **not** a qualified Transformers
training checkpoint. Its original trainable tensors/tokenizer and compatible stack
are not established by Ollama listing. No download or installation occurred.

## Candidate sizes and memory planning

Qwen2.5-Coder is an illustrative existing open-weight coding family, not a model
selected for an experiment. Public cards list0.5/1.5/3/7/14/32B sizes. The3B instruct
card reports3.09B parameters/32K context and `qwen-research` license;7B reports7.61B,
Apache2.0, with default32K context and optional larger-context configuration. Open
weights do not mean identical licensing across sizes. Exact model revision, license,
tokenizer, chat/tool template and capability calibration must be pinned later.

Raw weights: BF16 is approximately2P bytes; ideal4-bit is0.5P bytes. Real QLoRA
adds quantization metadata, higher-precision modules, LoRA gradients/optimizer state,
activations, attention, logits and CUDA workspace. Standard mixed-precision Adam
full tuning can require roughly12–20P bytes **before activations**, depending on
master/optimizer implementation. It is not the appropriate7B/12GiB plan.

The following are **unmeasured planning ranges**, batch1, sequence512–2048,
checkpointed activations, modest LoRA rank8–16 and memory-efficient kernels. They
are not vendor benchmarks or a guarantee that every Windows configuration fits.

| Size | BF16 weight-only | 4-bit weight-only, ideal | LoRA on BF16, estimated total | QLoRA estimated total | Local assessment |
|---|---:|---:|---:|---:|---|
|1–1.5B|1.9–2.8 GiB|0.47–0.70 GiB|4–8 GiB|3–6 GiB|Most conservative small experiment |
|3–4B|5.6–7.5 GiB|1.4–1.9 GiB|8–14 GiB|5–9 GiB|QLoRA plausible; BF16 LoRA context-sensitive |
|7–8B|13–15 GiB|3.3–3.7 GiB|18–28 GiB|8–13 GiB|Borderline; short sequences/batch1 needed, measured fit required |
|14B|26 GiB|6.5 GiB|30+ GiB|13–22 GiB|Not recommended on12GiB; offload is not an established solution |

Large vocab logits and long tool histories can exceed these ranges. Current free
VRAM is only8.66 GiB; a future7B fit must account for display/background use and leave
about1–2 GiB headroom. Microbatch1 with accumulation changes effective batch without
holding all examples at once. Accumulation does not fix an overlength sample.
Freeze base parameters; train adapters only. NF4/double quantization/checkpointing
are plausible PEFT approaches; neither changes symbolic semantics.

## Time, storage and preparation ranges

For a future pilot of0.1–1 million **non-padding processed tokens per epoch**,1–3
epochs, assumed observed training throughput10–100 tokens/s gives:
`tokens × epochs / throughput` = approximately0.28–83 hours. Budget **1–96 hours**
including loading/checkpoints/evaluation for a small1–4B experiment;7–8B or offload
could be materially slower. Throughput has not been measured here.12 data episodes
are not presumed to contain0.1M tokens or enough signal for useful fine-tuning.

- Dataset joining/review: roughly3–10 engineer-days for the12-episode process pilot
  with a genuinely available curator/reviewer; broader production/authority data can
  take weeks. Labor independence and requirement clarification are bottlenecks.
- Storage: reserve10–30 GiB for1–4B checkpoint/cache/tokenizer/adapters and multiple
  receipts,20–50 GiB for7–8B; actual checkpoint precision/sharding/revisions matter.
  LoRA adapters typically tens to hundreds of MiB, potentially near1 GiB for broad
  high-rank targeting; optimizer checkpoints add overhead. Raw evidence might use
  0.1–5 GiB for a bounded pilot; existing raw traces dwarf symbolic target bytes.
- RAM32GiB: reasonable for small-checkpoint loading and streaming dataset processing;
  7–8B loads/offload copies can exceed it without careful sharding. Full-parameter
  optimizer offload is not recommended as the small baseline.
- Inference:1.5–4B quantized weights plus KV cache plausibly fit;7–8B short-context
  quantized inference has historical local evidence. Training checkpoints/adapter
  export and native tool-format compatibility still need qualification. Model-card
  maximum context is not affordable training context on this machine.
- Evaluation:12 episodes ×4 tracks ×3 seeds =144 authoring trials before format
  ablations; at2–10 minutes/trial about4.8–24 hours of participant wall, plus
  deterministic scoring, preparation and replay. Direct/tool crossing may double it.
  Historical arithmetic checks take subsecond-to-seconds; stateful subprocess suites
  take longer and R6.46 records workflow timeouts. No billing advantage is inferred.

**Hardware is plausibly sufficient for a small1.5–4B PEFT experiment after separately
authorized setup and measured memory qualification. The current tooling is not
training-ready.** Recommend starting with1.5B or about3B short-context adapters,
not assuming the installed8B GGUF can simply be fine-tuned. Training authorization
and data readiness are separate from physical feasibility.

## Public references read, not software installed

Accessed2026-10-10:

- [3B coding-model card](https://huggingface.co/Qwen/Qwen2.5-Coder-3B-Instruct).
- [7B coding-model card](https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct).
- [Transformers bitsandbytes documentation](https://huggingface.co/docs/transformers/quantization/bitsandbytes):
  NF4/QLoRA, extra-parameter-only quantized training, current Windows/NVIDIA support,
  and inference-only status of automatic device maps.

These pages support architecture/technique feasibility, not the memory/time ranges
above. No claim that these models are the newest or superior for Lykoi is made.
