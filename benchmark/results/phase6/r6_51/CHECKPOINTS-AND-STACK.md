# R6.51 — Checkpoints and training stack

Assessment date: 2026-10-10. Only public metadata, cards, license text and package
documentation were retrieved. No tokenizer or model weight was downloaded, and no
candidate was run against Lykoi examples. Model-card capabilities are upstream
claims, not locally measured symbolic competence.

## Candidate comparison

| Checkpoint | License / fine-tuning | Context | Structured outputs / tools | Planning choice |
| --- | --- | --- | --- | --- |
| Qwen/Qwen2.5-Coder-1.5B-Instruct (1.54B) | Apache-2.0; modifications/fine-tuning allowed, retain required notices/license on redistribution | 32,768 native | Instruction/code model; repository chat template explicitly supports tool schemas and JSON name/arguments calls; no guaranteed JSON/type correctness | **Initial recommendation**: smallest memory footprint, mature Qwen2 support, uncomplicated permissive license |
| Qwen/Qwen2.5-Coder-3B-Instruct (3.09B) | **Qwen Research**, not Apache-2.0; noncommercial research/evaluation derivatives allowed; commercial use requires separate license; attribution/redistribution conditions apply | 32,768 native | Same model family and established Transformers integration; prompt-based JSON remains validation-dependent | Feasible research alternative, less headroom and more restrictive rights |
| Qwen/Qwen3-4B (4.0B) | Apache-2.0; modifications/fine-tuning allowed subject to notices/license | 32,768 native; upstream describes 131,072 with YaRN | Upstream agent/tool support and non-thinking switch; use enable_thinking=false in a future output-only test | Later QLoRA alternative; larger activation/logit footprint and newer stack |

Metadata identifies stable, publicly available revisions:

- 1.5B: `2e1fd397ee46e1388853d2af2c993145b0f1098a`;
  metadata lists BF16 safetensors, tokenizer.json, vocab.json, merges.txt,
  tokenizer_config.json, config.json, generation_config.json and LICENSE.
- 3B: `488639f1ff808d1d3d0ba301aef8c11461451ec5`.
- 4B: `1cfa9a7208912126459214e8b04321603b3df60c`.

These are metadata observations, not local tensor checksums. A future download must
use an exact revision and bind actual downloaded bytes before a run. The recommendation
is based on architecture/size/license/tool support, not exposed-example performance.
All three are dense causal Transformers and support PEFT LoRA on attention/MLP linear
layers. BitsAndBytes NF4 + PEFT is the established QLoRA path; actual imports,
quantized forward/backward and save/reload remain untested here. AWQ/GPTQ/GGUF
inference availability is not interchangeable with this training path.

Approximate resident **weight-only** decimal GB: BF16 3.09/6.18/8.0; ideal packed
4-bit 0.77/1.55/2.0. Actual QLoRA is larger: nonquantized embeddings/norms, packing
metadata, trainable adapters, gradients, optimizer, activations, logits and allocator
workspace. Training needs much more memory than weight-only inference. See
[memory plan](MEMORY-AND-SEQUENCES.md). BF16 inference at 1.5B is plausible; 3B/4B
quantized inference is plausible. No inference fit or training fit was measured.

## Installed versus available

[Inventory](INVENTORY.json) probes the active interpreter, Windows host, NVIDIA tools,
WSL configuration, Ollama catalog and conventional HF cache. It does not prove no
other custom environment exists elsewhere on disk.

| Component | Installed / tested in active environment | Available support and qualification needed |
| --- | --- | --- |
| Python | 3.14.3 AMD64, active global environment; py launcher lists only this interpreter; repository venv search found none | Prefer an isolated Python 3.12 environment for mature wheel availability; resolve exact compatible stable versions rather than assuming 3.14 is unsupported |
| PyTorch | Absent; CUDA tensor test NOT_RUN | CUDA-enabled Windows/Linux builds exist; verify wheel ABI/runtime, imports, cuda.is_available, device capability, BF16 and allocation |
| CUDA | NVIDIA driver 617.42; nvidia-smi advertises driver CUDA UMD 13.4; nvcc toolkit 13.1.115 exists | Driver capacity, installed toolkit and PyTorch bundled CUDA runtime are distinct; a toolkit alone is no training stack qualification |
| Transformers | Absent | Qwen2 card needs >=4.37; Qwen3 >=4.51. Choose stable versions compatible with PEFT/TRL, not only these minima |
| PEFT | Absent | LoRA, prepare_model_for_kbit_training, adapter save_pretrained and PeftModel loading documented; test base freeze and adapter-only gradients |
| TRL | Absent | Conversational prompt/completion SFT, completion-only loss, tool-call data and PEFT integration documented; qualify EOS/mask behavior for the pinned template |
| Accelerate | Absent | Trainer/device support available; use single GPU, no automatic CPU/offload placement during training |
| BitsAndBytes | Absent | Current docs list official Windows x86-64 CUDA wheels and sm89 (Ada) support, including 11.8–12.6, 12.8 and 13.0–13.2 builds; verify exact chosen release/wheel and NF4 backward |
| datasets / tokenizers / safetensors | All absent | JSONL loading/tokenization and adapter checkpoint serialization available, untested; standard-library JSONL round-trip is tested now |
| jsonschema | 4.26.0 installed | Draft2020-12 used successfully for generated record validation; this is dataset tooling, not training qualification |

No model checkpoint save, adapter loading or model inference was tested. Dataset
conversion and identity/schema controls are tested. A BF16 LoRA alternative on 1.5B
avoids BitsAndBytes but has higher weight memory; it needs a separately frozen
configuration/allocation check. HQQ and torchao have documented PEFT paths but are
not installed or qualified here; they add another compatibility surface and are not
the initial recommendation. CPU LoRA is theoretically possible, practically slower;
no timing/feasibility claim is made.

## Native Windows versus WSL2

Native Windows is a technically plausible initial single-GPU HF/PEFT/NF4 route;
do **not** repeat the obsolete blanket claim that BitsAndBytes has no Windows support.
Use PyTorch SDPA, dataloader workers=0, no FlashAttention/Triton/torch.compile
requirement and no distributed NCCL dependency. Windows wheel availability and
subprocess/spawn behavior still require actual qualification. WDDM/display processes
consume VRAM and hard wall-time supervision belongs outside Trainer.

WSL default version is 2, but **no distribution is installed**. Linux training is
therefore not currently usable. A future WSL2 glibc distribution can use the Windows
NVIDIA GPU driver through WSL; Microsoft documents CUDA ML support. Verify kernel,
GPU exposure and Linux wheel/runtime, use a Linux filesystem for training I/O, and
budget WSL RAM/disk usage. Do not install a second Linux display driver. WSL2 may
offer broader Linux tooling compatibility but needs more setup here; neither route
was changed or qualified. Native Windows is the smallest first setup candidate.

## Future installation/download requirements (not executed)

1. Isolated Python 3.12 interpreter/environment; explicit owner authorization for
   setup and candidate assets. Keep the production/research interpreter intact.
2. Resolve and lock stable CUDA-enabled torch, transformers, peft, trl, accelerate,
   bitsandbytes, datasets, tokenizers, safetensors and their transitive dependencies.
   Record wheel hashes and package versions. The installed global CUDA toolkit does
   not force the selected torch wheel to use CUDA 13.1. No new toolkit/driver is
   presumed necessary unless actual wheel qualification shows a gap.
3. Exact 1.5B revision: BF16 safetensors plus config, tokenizer assets, chat template,
   generation config and license. About 3.1 GB weights plus small tokenizer/config;
   reserve 15–25 GB for environment, cache, temporary load copies and adapter/logs.
   Place cache/output on D: (ample free capacity), not the relatively tight C: drive.
4. Import/device/NF4 forward-backward, frozen-base gradient, finite-loss, adapter
   save/reload/equivalence, loss-mask and exact-tokenization checks; capture measured
   peak VRAM and RAM. Perform only in a separately authorized setup round.
5. Only after those pass, separately authorize the bounded smoke training run.

Existing Ollama `qwen2.5-coder:1.5b-base` is Q4_K_M, completion/insert, 986 MB;
it is neither the recommended instruction checkpoint nor verified HF training tensors.
Ollama0.35.0 also lists 8B/20B/30B quantized models; names/aliases may share blobs.
HF cache inventory contains speech-model directories, no selected LLM checkpoint.
No missing assets were fetched.

## Primary sources read

- [1.5B card](https://huggingface.co/Qwen/Qwen2.5-Coder-1.5B-Instruct/raw/main/README.md),
  [metadata](https://huggingface.co/api/models/Qwen/Qwen2.5-Coder-1.5B-Instruct),
  [pinned Apache license](https://huggingface.co/Qwen/Qwen2.5-Coder-1.5B-Instruct/raw/2e1fd397ee46e1388853d2af2c993145b0f1098a/LICENSE).
- [3B card](https://huggingface.co/Qwen/Qwen2.5-Coder-3B-Instruct/raw/main/README.md),
  [research license](https://huggingface.co/Qwen/Qwen2.5-Coder-3B-Instruct/raw/main/LICENSE).
- [4B card](https://huggingface.co/Qwen/Qwen3-4B/raw/main/README.md).
- [BitsAndBytes installation](https://huggingface.co/docs/bitsandbytes/main/en/installation),
  [PEFT quantization](https://huggingface.co/docs/peft/main/en/developer_guides/quantization),
  [TRL SFT](https://huggingface.co/docs/trl/main/en/sft_trainer).
- [PyTorch local setup](https://pytorch.org/get-started/locally/) (retrieval succeeded;
  rendered response truncated, not used as proof of an exact version matrix),
  [Microsoft CUDA on WSL2](https://learn.microsoft.com/en-us/windows/ai/directml/gpu-cuda-in-wsl).

Documentation at main URLs is mutable. This assessment preserves the observed
claims and revisions in prose; it is not a frozen wheel compatibility certification.
