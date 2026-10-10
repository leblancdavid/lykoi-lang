# R6.51 — Future bounded smoke test and evaluation protocol

**Proposal only. Training/inference/model allocation were not executed.** The
smallest test is completion-only supervised fine-tuning, format A. Tool-selection
SFT (B) has zero qualified targets. DPO/RL/reward-model or discovery training adds
unsupported labels/infrastructure and is not the initial objective.

## Frozen run proposal

- Base: `Qwen/Qwen2.5-Coder-1.5B-Instruct`, revision
  `2e1fd397ee46e1388853d2af2c993145b0f1098a`.
- Subset: R6.48/E01–E06, all family/scaffold members retain training-development
  identity; six short endpoint records, F1/F2/F3, one broad scaffold. E07/E08 and
  S01/S02 excluded from this **smoke subset** for context/profile simplicity, not
  relabeled held-out evaluation. All ten remain usable full conversion records.
- Base frozen; NF4 4-bit, double quantization, BF16 compute if tested; PEFT
  prepare_model_for_kbit_training; single CUDA device, no auto CPU offload.
- LoRA r=8, alpha=16, dropout=0.05, q_proj/v_proj only, bias=none,
  task_type=CAUSAL_LM. Verify actual module match and base gradients are absent.
- Supervision: token cross-entropy on completion + final turn EOS only; prompt and
  padding labels=-100. Native pinned chat template, EOS `<|im_end|>`, explicit mask
  test; do not assume assistant_only_loss works on an unqualified template.
- max_length=2048, microbatch1, accumulation4, no packing/truncation, gradient
  checkpointing enabled, use_cache=false, SDPA, workers0, torch_compile=false.
- AdamW on adapters (ordinary torch optimizer), lr=1e-4, max_grad_norm=1,
  weight_decay=0, warmup2 steps, fixed seed/data seed651. **20 optimizer steps**,
  max80 example presentations (cycling six examples, deliberately overfit mechanics).
  No hyperparameter search or best-on-diagnostic checkpoint selection.
- Log every optimizer step: loss, target-token count, cumulative tokens/steps,
  learning rate, gradient norm, elapsed time, peak allocated/reserved GPU memory,
  process RSS and failures. Local JSONL, no telemetry service or Hub upload.
- Save adapters/config + tokenizer/template + provenance at steps10 and20; save
  optimizer/scheduler/RNG for these checkpoints, cap retained count2. Do not save a
  merged/full model. Bind base/dataset/stack hashes. Save final or partial failure
  evidence; unexpected stop must not be relabeled success.
- Limits: 30-minute total training-process wall timeout, process RSS16GiB,
  reserved CUDA memory8GiB and at least1.5GiB device free. Poll limits externally;
  retain stdout/stderr/partial artifacts on abort. No silent microbatch/context/model
  fallback. Representative allocation/backward must first pass in authorized setup.

20 steps tests tokenizer→masked loss→adapter gradient→save→reload, not adequate
generalization data or a meaningful learning curve. Falling training loss alone is
not proficiency improvement. Setup and this execution require separate explicit
authorization; data preparation permission is not training permission.

## Paired diagnostic inference

Pre-register prompts/budgets and byte identities before training. A is the unchanged
base checkpoint with the **same NF4 quantization/runtime**; B is the exact same base
plus final step20 Lykoi adapter. Do not compare BF16 base to NF4 tuned model. Never
merge adapters into base. Freshly load base for each phase or use PEFT disable_adapter
after proving equivalence. Qualify save/reload with matching adapter outputs.

Use the converter's exact prompt/vocabulary and native template, no reference target
or acceptance answers in context, identical inference budgets/tools/decoding:
one sequence per request, max_input+output2048, max_new_tokens1400 (actual token
preflight must leave enough room), do_sample=false, eval mode, no added stop rules
except EOS, 120-second per-call timeout. Record initial generation separately. Then
at most **one repair** per item, with identical unchanged validator diagnostics and
the same token/time limits and permitted semantic seal tool (if made available, it
must be available identically in both tracks and its calls counted). Initial strict
raw validity always reported before any tool assistance.

Initial diagnostic set: same six training endpoints with original frozen contracts,
explicitly **resubstitution / non-independent**. It measures training mechanics and
memorization-sensitive Lykoi reproduction. After a separately authorized prospective
freeze, add a small public diagnostic panel of two wording paraphrases and two
behavior-changing boundary/order variants derived from these families. These are
still related/exposed, never independent evaluation. Author/check expected behavior
before either model output; no new examples or acceptance execution in R6.51.
Do not use E07/E08/S01/S02 as independent held-out data: shared scaffolds/history.

For each item/track report:

1. Strict JSON/output-envelope/schema pass counts with denominator; no duplicate keys.
2. Type/reference/order/identity validation independently, native diagnostic stage.
3. Tool syntax, argument typing and successful responses if any; B training objective
   unavailable now, so tool-choice learning metrics NOT_APPLICABLE for direct-only run.
4. Functional acceptance over the same deterministic frozen requirements/oracle,
   including success/failure/error precedence and applicable state/restart observations.
   Execute only future authorized diagnostics, never historic rescoring in this round.
5. Initial versus repaired results, repair count, validation/tool/lowering costs,
   retained invalid candidates and failures. No best-of-many cherry-picking.
6. Exact/normalized target match, novel requirement mutation fidelity, copied stale
   literals/error order/hashes, near-duplicate target similarity; flag memorization.
7. Training loss versus step and optional teacher-forced same-item diagnostic NLL
   (not held-out loss), finite gradients, adapter save/reload success.
8. Actual tokenizer input/output/repair token counts, wall time/TTFT if instrumented,
   peak memory and total inference/tool/validation time; warm-up separately recorded.

Same-item functional gains would support only improvement on this exposed diagnostic
panel. Hash memorization, template repetition and overfit loss are alternatives to
generalized symbolic construction. Base pretraining contamination is unknown; no
language superiority, causal architecture superiority or broad generalization claim.

## Longer-term fair comparison retained

Carry forward [R6.50 matched-adapter design](../r6_50/MATCHED-ADAPTER-COMPARISON.md):
same base/revision, Lykoi-specialized and Python-specialized adapters, matched
trainable capacity/token/optimizer/compute budgets, language-appropriate equivalent
requirements and independent functional scoring. Include unchanged-base controls
for both languages and episode-balanced/token-balanced sensitivity analysis.
Freeze independent families and all connected ancestry under real custodian exclusion
before training; current R6.50 independent commissioning/custody gap remains unresolved.
Report retrieval/tooling/repair costs and failures, not just final pass rate or loss.
No Python adapter or paired training dataset is started here.

## Smallest next recommendation

Separately authorize **isolated training-stack setup and tokenizer/allocation/save-load
qualification only**, preferably native Windows first on this host, using the pinned
1.5B checkpoint. This next step necessarily needs dependency installations and weight/
tokenizer downloads, explicitly excluded now. If that passes, separately authorize
the 20-step direct-format mechanics test. Independent family commissioning/custody
must precede any later generalization/comparative claim; it is not manufactured by
the tiny diagnostic smoke test.
