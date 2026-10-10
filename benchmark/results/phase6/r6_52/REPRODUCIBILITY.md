# R6.52 — Reproducibility instructions

The original installation and qualification are complete. These are instructions
for a separately authorized reproduction, not permission to rerun or train.
Do not overwrite original sealed evidence. No script implements optimizer steps.

## Verify existing publication and environment

From the repository root in PowerShell, with the preserved temporary store:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
& 'C:\Users\lblan\AppData\Local\Temp\opencode\lykoi-r6-52\venv\Scripts\python.exe' experiments/training_setup_r6_52/publication.py check
git diff --check
```

The checker rehashes inherited protected publications, all pinned model assets,
untrained adapter files,47 installed distribution file trees/RECORD hashes and
new publication bytes. This performs no model forward/backward or acceptance
execution. Model/adapter assets are external and must still exist. The checker
expects the original clean tracked baseline and only the additive R6.52 files;
future repository changes need their own prospective checker, not amendment of
this historical seal. It also binds the original HEAD identity.

## Isolated reproduction

Use a separately authorized clean checkout with the sealed R6.51 data and R6.52
source/lock, native Windows AMD64, compatible NVIDIA driver and sufficient disk,
RAM and RTX4070 GPU headroom. No WSL installation is necessary. Before creating
reproduction paths, confirm the chosen parent directory exists and is correct.

```powershell
Test-Path -LiteralPath 'C:\Users\lblan\AppData\Local\Temp\opencode'
$env:LYKOI_R6_52_STORE='C:\Users\lblan\AppData\Local\Temp\opencode\lykoi-r6-52-reproduction'
$env:LYKOI_R6_52_OUT='C:\Users\lblan\AppData\Local\Temp\opencode\lykoi-r6-52-reproduction-evidence'
$env:PYTHONDONTWRITEBYTECODE='1'
python experiments/training_setup_r6_52/setup.py
python experiments/training_setup_r6_52/run.py host
python experiments/training_setup_r6_52/run.py inventory
python experiments/training_setup_r6_52/run.py assets
python experiments/training_setup_r6_52/run.py tokenize
python experiments/training_setup_r6_52/run.py mask-controls
python experiments/training_setup_r6_52/run.py backward
python experiments/training_setup_r6_52/run.py reload
```

Run each command sequentially and stop on any nonzero exit; preserve its diagnostics.
Do not execute later qualification stages after a CUDA/NF4 failure. No silent BF16,
CPU, alternate model/revision or smaller-context fallback. Scripts use telemetry-off
settings and capture stdout/stderr/elapsed time/exit codes. Model loads after download
are local-only, remote code disabled. Do not run `seal` over the original evidence
after reproduction. Compare new measurements/hashes against the historical publication
and publish any new result in its own round.

Setup downloads uv0.8.22, installs private CPython3.12.11 and creates a private venv.
Torch2.7.1+cu128 comes from `https://download.pytorch.org/whl/cu128`; remaining exact
packages come from PyPI using the sealed [requirements lock](requirements-lock.txt).
Initial installation logs record the one-time transitive resolution. Subsequent setup
uses all47 pinned versions; installations do not target system Python3.14. uv may
create user-bin Python integration as described by its retained install warning;
no PATH edits or elevated Windows changes are needed. Before accepting a reproduced
installation, compare Python and distribution file identities, not just version strings.

Only the exact revision `2e1fd397ee46e1388853d2af2c993145b0f1098a` is allowed for
`Qwen/Qwen2.5-Coder-1.5B-Instruct`. `assets` checks resolved commit and LFS weight
SHA256 and downloads the selected config/tokenizer/safetensors/license/model-card
files. Compare all SHA256s with [CHECKPOINT.json](CHECKPOINT.json). No Hub uploads.

Tokenization uses the sealed DIRECT.jsonl only. `checked_record` in mask_controls.py
rejects overflow; it never truncates. Prompt template and full token prefix alignment
must match; target decoding must reproduce the entire target. Labels are-100 through
the prompt, after final EOS and for padding. Supervise target plus EOS151645. All10
rows fit2048; a new oversized target must halt rather than silently change context.

Backward uses seed651; load NF4/double-quant/BF16, single CUDA device, SDPA,
cache off, non-reentrant gradient checkpointing, rank8/alpha16/dropout0.05 q/v LoRA.
Save the adapter before backward, verify112 trainable tensors/1,089,536 parameters,
finite loss/gradients, absent frozen-base gradients and unchanged tensor identities.
Run E04/855 tokens and ephemeral synthetic2048; clear gradients between probes.
No optimizer, scheduler, clipping, parameter update or model checkpoint training.
Fresh reload repeats base/k-bit preparation and verifies exact adapter config/tensors,
public base revision and bitwise-identical finite short-forward logits.

## Future training boundary

The20-step smoke remains a separate authorization. Retain R6.51 E01–E06 subset,
batch1/accumulation4/max2048, completion-only labels, adapter-only AdamW and fixed
limits; monitor actual optimizer/accumulation/RSS/VRAM use then. Setup measured
allocator peaks, not optimizer-step peaks. A temporary-directory asset loss or changed
driver/stack/model identity invalidates reliance on this exact qualified environment.
No independent/generalization claim follows from reproduction or a future smoke.
