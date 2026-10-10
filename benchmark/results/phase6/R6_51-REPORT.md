# R6.51 — Small-model training infrastructure qualification

**Final classification: `R6_51_HARDWARE_OR_STACK_GAP`.**

The hardware is a plausible small-model LoRA/QLoRA host, but the active environment
is **not a qualified training stack**. All core training libraries are absent;
selected training weights/tokenizer are absent; GPU training allocation and adapter
save/reload have not been tested. Dataset preparation succeeds: **10 direct-format
records; 0 genuine semantic-tool decision records**. No training benefit or
generalization is inferred from this qualification.

## 1. Authorization and preserved baseline

The owner authorized bounded nonproduction infrastructure/dataset investigation,
including a local converter, while explicitly excluding dependency installation,
weight downloads, model training and semantic changes. Initial `git status --short`
was clean. Before editing, the read-only R6.50 verifier passed:

`python benchmark/results/phase6/r6_50/verify_publication.py check`

It verified 5,387 inherited protected files, 5,441 including R6.49 publication,
18 R6.50 payload files / 70,051 bytes, R6.48 zero original admissions, R6.49
successor **10 Tier T / 0 Tier E**, kernel26, manifest/receipt and `git diff --check`.
R6.50 manifest SHA256:
`21f8f81ade3e195c7209cae506e5918469add3962866a9dc7768e5c5930f9945`.

The round-local checker rechecks the full inherited protected chain and R6.49/
R6.50 publication identities. [Receipt](r6_51/VERIFICATION.json) gives preservation
group counts for production, R6.10 VM, R6.18 wrapper, R6.23 adapter, R6.25 tool
contracts and R6.32 registry. Kernel26 is verified against unchanged accounting,
not freshly inferred from a benchmark. Production compiler/lowerer/runtime and all
experimental semantic implementations are byte-identical. R6.49 admission status
and source provenance are preserved; R6.48's zero-admission history is not rewritten.
Historical evidence R6.3–R6.50 is preserved by the inherited identity chain.

Work is confined to `experiments/training_infrastructure_r6_51/`, `r6_51/`, the
report and additive versioned documentation. No execution primitive, source evidence
edit, historical acceptance rescore, P6-A04 acceptance execution or P6-A05 content
access occurred. There were zero model inference/training calls, dependency installs
and weight downloads. Web retrieval was limited to public textual model metadata/
licenses and training documentation. No tokenizer assets were downloaded either.

## 2. Current hardware/software inventory

[Raw scoped inventory](r6_51/INVENTORY.json) retains command arguments, return codes,
stdout/stderr, library detection and scope limitations. Current measurements:

| Item | Verified observation |
| --- | --- |
| CPU / architecture | AMD Ryzen7 7700X, x86-64 / AMD64, 8 cores /16 threads |
| System RAM | 33,408,004,096 bytes (~31.11 GiB usable physical); ~10.49 GiB free at final recorded snapshot |
| GPU / dedicated VRAM | NVIDIA RTX4070, 12,282 MiB dedicated; 9,078 MiB free at inventory (9,314 MiB in earlier probe) |
| NVIDIA driver | 617.42, WDDM; driver CUDA UMD13.4 reported |
| CUDA toolkit | nvcc13.1.115 present; framework CUDA allocation **NOT_RUN**, torch absent |
| OS | Windows11 Home, version10.0.26300, 64-bit |
| Python | 3.14.3, active global interpreter; py launcher lists only3.14 |
| Storage | C: ~42.8 GiB free of ~930.5 GiB; D: ~1.57 TiB free of ~3.64 TiB |
| WSL | Default version2; no installed Linux distributions; Linux training unavailable now |
| Core ML training libraries | torch/transformers/peft/trl/accelerate/bitsandbytes/datasets/tokenizers/safetensors absent in active interpreter |
| Dataset validation | jsonschema4.26.0 installed and used; standard-library JSON/JSONL conversion tested |
| Existing model serving | Ollama0.35.0; local catalog includes qwen2.5-coder1.5b-base Q4_K_M and larger quantized models |

The existing 986MB coder base is verified by `ollama show` as Q4_K_M, context32768,
completion/insert. It is not the selected instruction checkpoint or qualified HF
training tensors. Conventional HF cache has speech-model directories, no selected
LLM directory. Search scope does not exclude every possible external virtualenv or
custom model directory. The hardware verification is current, not a reused historical
4070 claim. Free RAM/VRAM/storage vary; no process was stopped to create headroom.

## 3. Checkpoint and stack assessment

[Comparison and compatibility assessment](r6_51/CHECKPOINTS-AND-STACK.md) evaluates
Qwen2.5-Coder1.5B-Instruct, Qwen2.5-Coder3B-Instruct and Qwen3-4B. **Recommend the
1.5B instruction checkpoint** at revision
`2e1fd397ee46e1388853d2af2c993145b0f1098a`: Apache-2.0, established Transformers/
PEFT support, tool-aware chat template and smallest footprint. The 3B coder has a
noncommercial Qwen Research license, not Apache-2.0. The 4B alternative is Apache-2.0
and agent-capable but consumes more training memory. Selection used size/license/
tooling evidence only; no exposed-example inference score was measured.

Native Windows HF/PEFT training is plausible. Current BitsAndBytes documentation
lists official Windows CUDA support, so Windows is not categorically excluded.
Native Windows is the smallest setup route here; WSL2 adds an uninstalled distro/
Linux environment. Both remain unqualified. Installed CUDA tooling does not establish
PyTorch CUDA compatibility. Checkpoint saving/loading and adapter inference are
documented upstream, not locally tested. Full support distinctions and primary
source URLs are retained in the comparison.

## 4. Dataset conversion results

[Formats and qualification](r6_51/DATA-FORMATS.md),
[schema](r6_51/training-record-1.schema.json),
[converter](../../../experiments/training_infrastructure_r6_51/convert.py) and
[assessment/exclusions](r6_51/CONVERSION-ASSESSMENT.json) specify fail-closed reads,
source/admission checks, exact endpoint JSON, family/component grouping and provenance.

- **A: 10 usable direct preparation records**, eight typed-composition packages and
  two production-backed intent targets. Five nominal families /two connected scaffolds.
  Direct endpoint supervision does not require AI-authored edit trajectories.
- **B: 0 usable genuine semantic-tool records.** Eight scripted traces are excluded;
  two genuine AI file-edit captures are preserved but have no observed semantic-tool
  selection/current-state/typed-argument trajectory. No missing decisions were invented.
  Tool-decision format is a schema/design with fail-closed capture gates, not a
  qualified positive-data pipeline. `TOOL.jsonl` is deliberately empty.
- All ten remain training-development. No evaluation export or row-level split;
  connected family/scaffold ancestry must stay together. No independent evaluation
  family is available. Metadata sidecars must not become training prompt text.

Eight test methods pass: full outer record Draft2020-12 validation, exact cohort,
strict JSON, gate/reference/tamper/path rejection, family/component partition
controls and trajectory substitution rejection. Eight stateless targets pass
unchanged wrapper validation and two stateful intents pass unchanged schema.
Original production validation/acceptance evidence remains bound; no functional
acceptance was re-executed. Converter regeneration matches all published records.
This supports serialization/preparation, not broad target fidelity or generalization.

## 5. Sequence lengths, memory and proposed objective

[Sequence/memory plan](r6_51/MEMORY-AND-SEQUENCES.md) records actual text bytes and
explicitly estimated tokens. Full direct sequences span 2,441–5,736 bytes,
approximately **611–2,868 tokens plus template overhead**, not real tokenization.
E01–E06 fit the planning range for2,048 tokens; longer composition/stateful rows may
need4,096. Real tokenizer checks must reject overflow without target truncation.
Tool trajectory lengths are hypothetical because no semantic capture exists.

1.5B NF4 rank8 attention-only QLoRA at microbatch1/2,048 tokens is estimated at
**4–7 GiB process GPU memory**; BF16 LoRA at **6–9 GiB**. 3B/4B short-context QLoRA
is plausible but increasingly constrained (~6–9 /7–11 GiB). These are engineering
estimates, **not measured allocation feasibility**. Reserve display/headroom; actual
free GPU/RAM is less than nominal capacity.

[Future smoke and evaluation design](r6_51/SMOKE-AND-EVALUATION.md) freezes a proposal:
1.5B NF4/BF16-compute QLoRA, r8/alpha16/dropout0.05 q/v adapters, completion-only
cross-entropy on six short direct records, sequence2048, batch1/accumulation4,
20 optimizer steps, fixed seeds, local step logs and adapter checkpoints10/20,
30-minute timeout/RSS16GiB/reserved-GPU8GiB limits. Exact tokenization, masking,
allocation and adapter reload are pre-run gates. No training is executed here.

## 6. Evaluation and fair-comparison roadmap

Compare unchanged quantized base versus the same base + final adapter using identical
prompts, vocabulary, tools, token/time/repair budgets and runtime. Preserve initial
and repaired outputs; measure strict/schema/type/identity correctness, applicable
tool success, functional acceptance, repairs, loss, memorization indicators, actual
tokens and inference/tool/validation time. The smoke panel is explicitly **exposed,
non-independent resubstitution**, with any future related paraphrase/behavior-change
diagnostics labeled likewise. Falling loss or copied seals alone proves no generalization.

Retain same-base, training-budget/capacity-matched Lykoi and Python adapters with
independently withheld connected evaluation families and equivalent requirements.
No Python adapter starts in this round. R6.50 independent human commissioning/review
and enforceable custody remain gaps; ten narrow endpoints are not ten independent
paired Python/Lykoi tasks or adequate generalization data.

## 7. Blockers, installation requirements and stop

Training readiness is **NO**. Missing compatible isolated stack, selected safetensors/
tokenizer, exact lengths/loss mask, framework CUDA/NF4 backward/peak allocation,
adapter serialization/reload and explicit training authorization. B additionally lacks
genuine semantic decision captures. Generalization/comparative evaluation lacks
independent commissioning/custody/diverse families. These gaps are kept separate.

Future setup needs isolated Python (recommend3.12), CUDA-enabled torch plus HF/PEFT/
TRL/Accelerate/BitsAndBytes/datasets/tokenizers/safetensors, locked versions/wheels,
and exact checkpoint/config/tokenizer/license assets (~3.1GB weights; reserve
15–25GB total environment/cache/logs on D:). No installation or download occurred.

**Smallest recommended next step:** separately authorize isolated stack setup and
exact tokenizer/allocation/adapter save-load qualification, without training first.
If it passes, separately authorize the20-step exposed direct-format mechanics smoke
test. Independent custody remains necessary for later comparative/generalization claims.

[Publication manifest](r6_51/PUBLICATION-IDENTITIES.json) binds all payload bytes;
[verification receipt](r6_51/VERIFICATION.json) binds its hash, preserved identities,
conversion regeneration, tests, links, whitespace/credential-pattern inspection and
`git diff --check`. Manifests exclude themselves/receipt to avoid circular hashes.
Additive [overview](../../../docs/project-overview-r6.51.md),
[research log](../../../docs/research-log-r6.51.md) and
[decisions](../../../docs/decisions-r6.51.md) retain the pinned primary-document history.

**Stopped after infrastructure and dataset-format publication. Await explicit
authorization for setup, capture expansion, training or any further experiment.**
