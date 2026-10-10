# R6.52 — Lykoi training environment setup and qualification

**Final classification: `R6_52_TRAINING_ENVIRONMENT_QUALIFIED`.**

Native Windows Python3.12.11 / CUDA-enabled PyTorch2.7.1+cu128 successfully loads
the exact pinned Qwen checkpoint in NF4, constructs completion-only labels for
all ten admitted records, executes two finite forward/backward probes without
updates, and reloads an exactly preserved untrained rank8 adapter in a fresh
process. The proposed20-step smoke test is **technically ready, not executed or
authorized by this qualification**. This is mechanics evidence, not trained-model
capability, generalization or a comparative benefit.

## Authorization, baseline and preservation

The owner explicitly authorized isolated dependency installation, the specified
model download, exact tokenization, CUDA/NF4 backward without optimizer updates,
and untrained adapter save/reload. Initial `git status --short` was clean. Before
editing, `python experiments/training_infrastructure_r6_51/publication.py check`
passed and all8 R6.51 converter tests passed; the final captured8-test rerun also
passes in [R6_51-CONVERTER-TESTS.json](r6_52/R6_51-CONVERTER-TESTS.json).

[Baseline](r6_52/BASELINE.json) verifies the inherited5,387 protected identities,
R6.49/R6.50 publications and all20 R6.51 payload identities. R6.51 manifest SHA256:
`b867961a4d0af5f4201e7f4d4baa45692294a4c30622d0c68aa0b12e78b61ef3`.
R6.49 admission index SHA256:
`305cfe4a1671cbb2a92747f20bece390e0de67cc90596333e160dd7a2ccb959c`.
The ledger remains10 Tier T /0 Tier E; R6.48's original zero admissions remain
unchanged. Kernel26 accounting and protected production32 /VM21 /wrapper27 /
R6.23 adapter79 /tool contracts48 /registry11 identities match. No tracked
historical or implementation bytes changed. R6.3–R6.51 classifications are preserved.

Work is additive under `experiments/training_setup_r6_52/`, `r6_52/`, this report
and versioned companion docs. No semantics, compiler/lowerer/runtime, dataset,
execution primitives, historical acceptance scores or AI-independent execution
changed. P6-A04 acceptance executions0; P6-A05 content access false. Optimizer
instances0, optimizer steps0, fine-tuning runs0, parameter updates0. The backward
probes consume one authorized existing row and one ephemeral synthetic sequence;
no synthetic record was added to the dataset.

## Environment and installation changes

[Host diagnostics](r6_52/GPU.json), [WSL inventory](r6_52/WSL-LIST.json),
[environment](r6_52/ENVIRONMENT.json), [full47-package lock](r6_52/requirements-lock.txt)
and [installed file identities](r6_52/ENVIRONMENT-IDENTITIES.json) retain exact details.

- Windows11 Home10.0.26300, AMD64; RTX4070,12,282MiB dedicated VRAM, driver617.42,
  compute capability8.9. Driver-reported maximum CUDA support and installed toolkit
  are distinct from the tested **PyTorch runtime CUDA12.8**.
- WSL default2 has no installed distribution. Used the authorized native Windows
  fallback. No distribution, Windows feature, administrator action or driver/toolkit
  installation occurred.
- Bootstrap uv0.8.22 downloaded from its exact GitHub release; archive/executable
  hashes retained. uv installed private CPython3.12.11 and created a private venv.
  Its installation log includes the user-bin/PATH warning; user-level Python launcher
  integration is not claimed absent. No PATH edit or installation into system3.14
  occurred. Exact installation commands/stdout/stderr are retained.
- Private environment/model/cache/adapter root:
  `C:\Users\lblan\AppData\Local\Temp\opencode\lykoi-r6-52`.
  Training assets are outside protected production directories. This is a temporary
  directory; preserve it against cleanup before subsequent use, or separately
  reproduce it at an owner-selected durable location with hash verification.
- First installation pinned the nine core libraries and resolved transitives once;
  all47 resulting versions were then frozen. Reproduction setup uses that complete
  lock. Installed RECORD hashes are checked and per-distribution actual-file tree
  digests, metadata hashes, Python executable/DLL and uv hashes are published.

| Package | Installed version |
| --- | --- |
| Python | 3.12.11 |
| PyTorch | 2.7.1+cu128 |
| Transformers | 4.55.4 |
| PEFT | 0.17.1 |
| TRL | 0.21.0 |
| Accelerate | 1.10.1 |
| BitsAndBytes | 0.47.0 |
| Datasets | 4.0.0 |
| Tokenizers | 0.21.4 |
| Safetensors | 0.6.2 |

All nine imports pass, `uv pip check` passes, torch identifies the4070, BF16 support
is true, and a CUDA tensor backward produces finite gradients. The subsequent
actual NF4 model backward establishes framework/quantization support beyond
toolkit presence. TRL imports, but its Trainer is not exercised; future smoke uses
explicit completion-only labels and the proposed ordinary torch AdamW path.

[Storage](r6_52/STORAGE.json): selected checkpoint assets3,098,972,269 bytes;
private venv logical6,279,359,911 bytes; uv cache logical6,314,388,197 bytes;
untrained adapter directory4,379,064 bytes. Hardlinks share venv/cache contents:
deduplicated directory file lengths total9,545,429,322 bytes (~8.89GiB), excluding
loose root files. These are file lengths, not allocated filesystem clusters.
Recorded free storage on the store volume43,747,856,384 bytes. No unrelated process
was terminated to obtain memory headroom.

## Exact checkpoint and tokenizer identities

[Checkpoint manifest](r6_52/CHECKPOINT.json) includes every asset's byte length,
local SHA256, remote Git blob identity and LFS SHA256 where available, plus full
model config. Both requested and resolved revisions are:

`Qwen/Qwen2.5-Coder-1.5B-Instruct`
`2e1fd397ee46e1388853d2af2c993145b0f1098a`.

- `model.safetensors`:3,087,467,144 bytes;
  SHA256 `c1b9b30e907950516ba3c646bdf570d8084c25a6410a0cdca80cf04b11bc13a8`,
  equal to the pinned remote LFS identity.
- `tokenizer.json` SHA256:
  `c0382117ea329cdf097041132f6d735924b697924d6f6fc3945713e96ce87539`.
- `tokenizer_config.json` SHA256:
  `959e7f1d9a1b7641a6d6ce05ca97b75c7894fcb66cbe5a040406458fb1128ee4`.
- Native template SHA256:
  `cd8e9439f0570856fd70470bf8889ebd8b5d1107207f67a5efb46e342330527f`.
- Qwen2 causal LM,28 layers, hidden1536,12 attention heads/2 KV heads,
  vocab151936, tied embeddings, declared BF16, max positions32768.
- Apache-2.0: downloaded pinned LICENSE and model-card README with hashes.
  Other downloaded assets are config, generation config, tokenizer JSON/config,
  vocab and merges. No alternate checkpoint, original pickle weights or remote
  model code. No Hub upload or credentials published.

After download all model/tokenizer loads use `local_files_only=True`; model
`trust_remote_code=False`. HF transport emitted an informational HTTP fallback
because hf_xet is absent; pinned revision/hash checks still passed. This changes
download transport only. No training-method fallback occurred.

## Exact tokenization and completion-only loss

[Tokenization](r6_52/TOKENIZATION.json) uses the unchanged sealed DIRECT.jsonl
(SHA256 `6b0eafab8f397e1001877c1e9119c350f36433544eeb9ef723425d959fad5f55`).
Metadata sidecars are excluded from prompt text. All10 native chat strings have
exact generation-prompt prefixes, token-aligned boundaries and exact decoded
target roundtrips. Labels supervise target content and `<|im_end|>` only; prompt,
final template newline and padding labels are-100. EOS151645; pad151643.

| Episode | Prompt | Target content | Supervised incl. EOS | Full sequence |
| --- | ---: | ---: | ---: | ---: |
| E01 | 372 | 328 | 329 | 702 |
| E02 | 381 | 369 | 370 | 752 |
| E03 | 401 | 424 | 425 | 827 |
| E04 | 393 | 460 | 461 | 855 |
| E05 | 384 | 330 | 331 | 716 |
| E06 | 380 | 409 | 410 | 791 |
| E07 | 396 | 1018 | 1019 | 1416 |
| E08 | 398 | 1058 | 1059 | 1458 |
| S01 | 587 | 470 | 471 | 1059 |
| S02 | 604 | 662 | 663 | 1268 |

**0/10 exceed2048;0/10 exceed4096;0 truncated.** No context change to4096 is needed.
The actual lengths replace R6.51's estimates prospectively without editing them.
The proposed smoke subset remainsE01–E06; fitting longer rows does not expand it.

[Independent loss-mask controls](r6_52/LOSS-MASK.json) additionally check every
row's causal label shift, explicit N-1 cap rejection, masked padding, equality of
masked cross-entropy with independently selected-token loss, zero logit gradients
at ignored positions and nonzero gradients at every supervised position. These
CPU tests use tiny synthetic logits with the exact real token/mask positions;
they are not model capability scores. The last prompt logit correctly predicts
the first target token; prompt labels themselves contribute no loss.

## CUDA/NF4 and adapter qualification

[Backward evidence](r6_52/BACKWARD.json) / [clean process log](r6_52/BACKWARD-PROCESS.json):
NF4 double quantization, BF16 compute, single CUDA device, no CPU offload, SDPA,
cache disabled, non-reentrant gradient checkpointing.196 actual Linear4bit modules
are present. Seed651 for Python/torch/CUDA. LoRA r8/alpha16/dropout0.05 q_proj/v_proj,
bias none, CAUSAL_LM;112 adapter tensors /1,089,536 trainable parameters.

| Probe | Tokens | Supervised | Loss | Backward wall seconds | Peak allocated | Peak reserved |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| E04, longest E01–E06 | 855 | 461 | 1.464548 | 1.0423 | 3,347,648,512 B (3.12GiB) | 4,089,446,400 B (3.81GiB) |
| Full-length synthetic | 2048 | 1024 | 13.489070 | 1.3271 | 5,747,075,584 B (5.35GiB) | 7,826,571,264 B (7.29GiB) |

Both losses and all112 adapter gradients are finite; at least one gradient is
nonzero (initial LoRA A gradients may be zero because B starts zero). Frozen base
gradients are absent. Exact adapter tensor hashes/shapes/dtypes before and after
each backward match; no optimizer is instantiated. Each probe clears gradients;
no optimizer, clipping, scheduler, checkpoint merge or model update is implemented.

After the2048 probe device free memory is1,902,489,600 bytes (~1.77GiB), total
12,878,086,144 bytes. CUDA peaks are actual torch process allocations/reservations,
not total-board peaks or a sampled per-process nvidia-smi estimate under WDDM.
Display/other allocations are reflected in device-free observations. Probe timing
includes forward, backward, gradient checks and tensor identity checks; excludes
model load. Internal load+qualification7.9873s; whole process16.4637s. Exit code0.
Allocator cache from the first probe is retained for the second, conservatively
included in reserved-memory measurements. No full accumulation/optimizer-step
memory claim is made; those operations are excluded by authorization.

Adapter saved **before backward**, with safetensors and exact config; all subsequent
hash checks show it remains untrained. PEFT warns that a local base load path initially
overrides its name; before save the config is explicitly bound to the public repo
and pinned revision. This is identity normalization, not a different model.

[Fresh reload](r6_52/ADAPTER-RELOAD.json) / [process log](r6_52/RELOAD-PROCESS.json):
fresh NF4 base, identical k-bit preparation, adapter loading, all112 tensor identities
and shapes exact, config identical, saved file hashes exact and compatible public
base/revision. Finite four-token forward logits are bitwise equal to the original
untrained model, maximum difference0. Whole reload process11.1412s, exit0.
Inference initialization succeeded; no free-form task generation or trained
capability evaluation was performed.

## Reproducibility, blockers and recommendation

[Reproduction instructions](r6_52/REPRODUCIBILITY.md) specify the isolated paths,
commands, full lock, seed, pinned assets, no-update probes and separate evidence
directory. [Publication manifest](r6_52/PUBLICATION-IDENTITIES.json) binds payload
bytes; [verification receipt](r6_52/VERIFICATION.json) records inherited preservation,
external model/adapter hashes, actual installed-package file identities, process
results, links, credential-pattern/whitespace inspection and `git diff --check`.

No environment/model/mask/NF4/adapter technical gate remains open for the small
smoke configuration. Remaining requirements/limits:

1. Explicit training authorization is still required;20 optimizer steps were not run.
2. Peak reserved7.29GiB and free1.77GiB satisfy the proposed8GiB/1.5GiB gates at
   qualification, with modest headroom. Future AdamW state for1,089,536 FP32 adapter
   parameters is estimated~8.3MiB for two moments, not measured. Monitor accumulation,
   optimizer, process RSS and total-device free memory during a future actual run;
   stop on the frozen limits rather than silently change methods or context.
3. The temporary store must remain available and hash-identical. Other GPU process
   use may alter headroom; recheck it before an authorized smoke test.
4. Genuine semantic-tool decision records remain0; independent evaluation families,
   commissioning/custody and paired Python training data remain unavailable. Successful
   setup does not remedy these R6.50/R6.51 research limitations.

Recommend the unchanged R6.51 mechanics configuration: pinned1.5B NF4/BF16,
r8/alpha16/dropout0.05 q/v, completion-only EOS labels, E01–E06, max2048 without
truncation/packing, batch1/accumulation4, gradient checkpointing, SDPA/cache off,
ordinary adapter-only AdamW lr1e-4, fixed seed651,20 steps with checkpoints10/20,
30-minute timeout/RSS16GiB/reserved8GiB/free1.5GiB limits. The environment is
technically ready for separate authorization of that exposed mechanics smoke;
passing it would still not establish generalization.

**Smallest recommended next step:** explicitly authorize the bounded20-step smoke
with the preserved identities and limits. **Stopped after qualification and publication.**
