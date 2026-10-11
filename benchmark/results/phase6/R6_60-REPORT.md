# R6.60 — Learned distribution and output-format diagnosis

**Final classification: `R6_60_TARGET_LIKELIHOOD_IMPROVED`.**

On the exact six exposed records, dropout-off teacher-forced completion likelihood
improves for every record. Equal-record NLL decreases **1.647022447 → 1.504800672
nats/token** (delta **−0.142221775**, approximately8.64%). Pooled-token NLL decreases
**1.627590528 → 1.487384112** (delta **−0.140206416**, approximately8.61%).
This measures target fitting, not valid generation, unseen transfer or semantic
understanding. R6.59's original strict/functional scores remain **0/6 versus0/6**.

## 1. Baseline identities and authorization

Initial git status was clean. Before edits, a read-only verification passed R6.59
publication payloads, inherited protected history, installed package trees,
checkpoint/tokenizer, executable/DLL/lock and all external artifact identities.
[Baseline verification](r6_60/BASELINE.json) repeats these checks before dispatch
and publication, using the inherited R6.52–R6.59 chain and5,387 protected identities.
R6.56 frozen configuration, records/provenance, native template, token IDs/masks,
prompts/raw outputs and R6.59 checkpoint files match their original bindings.

- Model: `Qwen/Qwen2.5-Coder-1.5B-Instruct`, revision
  `2e1fd397ee46e1388853d2af2c993145b0f1098a`.
- Checkpoint weights SHA256:
  `c1b9b30e907950516ba3c646bdf570d8084c25a6410a0cdca80cf04b11bc13a8`.
- Tokenizer JSON SHA256:
  `c0382117ea329cdf097041132f6d735924b697924d6f6fc3945713e96ce87539`.
- Step20 adapter weights SHA256:
  `79843df8ce1f3e9bf87c81e0e23073c37a702695df6e52ac384b0a33f77fb7d1`.
- Adapter config SHA256:
  `642b816c81121fb0bf251550885b1ae30ca89c2cb824f4b4a2cd2c1caf657050`.
- Adapter directory canonical identity:
  `d8bbe876eca1e5929a0bd570e44fb661d4eb1cdb5ebf8e857c3ee659923ab58a`.
- Existing private Python3.12.11, torch2.7.1+cu128, Transformers4.55.4,
  PEFT0.17.1, BNB0.47.0 and all47 installed distribution trees remain pinned.

No checkpoint or adapter identity mismatch occurred. Exact loaded112 adapter
tensors match R6.59. No model download, optimizer/scheduler construction, training,
parameter update, adapter save/merge, dataset addition or semantic implementation
change occurred. Production kernel26 and AI-independent execution are preserved.

### Preserved instrumentation failures

The initial frozen worker loaded the base, then stopped **before any target forward
evaluation**: its mask assertion incorrectly compared a compact-canonical JSON hash
to the historical default-spacing `json.dumps` hash. The original source,
[freeze](r6_60/FREEZE.json), claim and [failed process](r6_60/BASE-PROCESS.json)
remain unchanged. CPU tokenization then verified **all six exact token-ID and label
hashes using the original convention**, recorded in [correction](r6_60/CORRECTION.json).
The separately frozen [qualified entry point](../../../experiments/learned_distribution_r6_60/qualified.py)
corrects only that assertion and gives later claims/process receipts distinct names.
Loss, masks, model, prompting and evaluation settings were unchanged. There was
one successful evaluation pass per model, with no loss-outcome-informed rerun.

Offline analysis also initially assumed historical `prompt_sha256` hashed rendered
chat text. The frozen worker actually hashes the canonical message list. The
[offline correction](r6_60/AUDIT-ASSERTION-CORRECTION.json) records this assertion
failure; the [audit entry point](../../../experiments/learned_distribution_r6_60/audit.py)
checks the correct historical convention and separately retains rendered hashes.
This dispatched no model and changed no prompts or historical evidence.

## 2. Paired teacher-forced measurements

[Protocol](r6_60/PROTOCOL.md) and source were frozen before dispatch. A and B use
the same exact checkpoint, inherited NF4/double quantization/BF16 computation,
SDPA, cache off and k-bit preparation. This is the established quantized inference
interface, not a new full-precision comparison. Two fresh processes run base then
adapter. Both set every module to eval, all parameters nontrainable, and use
`torch.no_grad()`. Dropout is disabled; no backward/optimizer/scheduler calls occur.
Parameter/buffer/quantization and adapter hashes are unchanged before/after.

The exact E01–E06 completion masks supervise target content plus `<|im_end|>`.
Prompt, post-turn newline and padding are excluded; no truncation or packing.
At supervised sequence index i, logit i−1 predicts the exact token. FP32
cross-entropy over the complete vocabulary yields NLL in nats; host FP64 sums
aggregate the observed FP32 per-token losses. Probability is exp(−NLL).

| Record | Supervised tokens incl. EOS | Base NLL | Adapter NLL | Adapter − base |
| --- | ---: | ---: | ---: | ---: |
| E01 | 329 | 1.816051889 | 1.662560441 | −0.153491448 |
| E02 | 370 | 1.712077551 | 1.554743066 | −0.157334485 |
| E03 | 425 | 1.517041733 | 1.385327859 | −0.131713874 |
| E04 | 461 | 1.464548160 | 1.342530458 | −0.122017702 |
| E05 | 331 | 1.870429486 | 1.703114711 | −0.167314776 |
| E06 | 410 | 1.501985864 | 1.380527498 | −0.121458366 |
| Equal-record mean | six equal weights | 1.647022447 | 1.504800672 | −0.142221775 |
| Pooled-token mean | 2,326 equal token weights | 1.627590528 | 1.487384112 | −0.140206416 |

Equal-record mean is sum of six within-record token means divided by6. Pooled
mean is total NLL divided by2,326. They are deliberately distinct. Each track
evaluates2,326 supervised tokens once:4,652 paired-track token observations.
[Base raw loss](r6_60/BASE-LOSS.json) and [adapter raw loss](r6_60/ADAPTER-LOSS.json)
retain every token probability, NLL, ID, causal index and exact character span.

## 3. Token-level learning

[Token analysis](r6_60/TOKEN-ANALYSIS.json) retains every matched token pair and
category aggregation. Exact full-string fast-tokenizer offset mappings match the
frozen IDs; categories tag intersecting lexical spans without splitting tokens.
Categories **overlap**: e.g. token4913 is `{"`, covering both opening delimiter
and the first key's quote. Category counts cannot be summed into a partition,
and overlapping gains cannot establish independent causal contributions.

| Category | Tokens | Base mean NLL | Adapter mean NLL | Mean probability increase |
| --- | ---: | ---: | ---: | ---: |
| Package delimiters | 385 | 0.731688 | 0.620643 | 0.031220 |
| Structural keys | 1,105 | 0.782715 | 0.583168 | 0.028540 |
| Typed values | 200 | 0.283288 | 0.244888 | 0.014329 |
| Semantic operation names | 375 | 0.672743 | 0.503095 | 0.024283 |
| Dependency references | 337 | 0.488867 | 0.412108 | 0.021476 |
| Output definitions | 84 | 1.026187 | 0.836106 | 0.057485 |
| Closing delimiters | 216 | 0.555780 | 0.442337 | 0.040176 |
| End of turn | 6 | 0.028925 | 0.001949 | 0.026449 |

Operation names cover op/codec values and ref/const/add/le/eq keys. Dependency
references cover explicit ref values and deps arrays. Output definitions cover
result/result_type field spans, not runtime output bytes. Typed values include
Int64/Bool/Unit names and literal number/boolean/null spans. All lexical categories
have lower mean NLL; individual tokens can worsen. Structural keys and output
definitions have larger mean NLL reductions than typed literals/references.
Operation-name improvement is also larger than delimiter-only improvement.
The observed fitting is **not confined to formatting**; it includes symbolic
content under gold prefixes. It does not demonstrate correct free-running programs.

At the first target token4913 (`{"`), probability increases on all six records:

| Record | Base | Adapter |
| --- | ---: | ---: |
| E01 | 0.080347 | 0.090301 |
| E02 | 0.069558 | 0.079148 |
| E03 | 0.048384 | 0.054277 |
| E04 | 0.064698 | 0.069402 |
| E05 | 0.061530 | 0.072648 |
| E06 | 0.079517 | 0.089631 |

These remain approximately5–9% for the trained adapter. Increased probability
does not imply the token wins greedy decoding. Fence-token probability/rank was
not retained by this target-token evaluation; no precise competitor margin is claimed.

## 4. Prompt/template audit and plausible explanation

[Full audit](r6_60/PROMPT-AUDIT.json) contains exact system/user messages, rendered
training/evaluation strings, target, native template and decoding configuration.
The system instruction is “Construct the declared Lykoi research representation
using only the supplied vocabulary.” The user JSON requires
`SYMBOLIC.json: one complete JSON object; no markdown or Python`. Developer messages
are absent in both model inputs. Coordinator/harness guidance is not forwarded as
an extra model role. Historical message-list hashes match all12 calls; identical
frozen source/template establishes the rendered-prefix reconstruction.

- Training and evaluation use the same native template and exact prompt messages.
- Both end at `<|im_start|>assistant\n`; there is no training-only package prefill.
- Targets are complete minified raw JSON packages, without markdown fences.
- Training supervises target and `<|im_end|>`151645; final newline is masked.
- Diagnostic EOS set is[151645,151643], pad151643; no extra textual stop string.
- Frozen decoding: greedy/do_sample false, one beam/sequence, max_new_tokens1400,
  context cap2048, repetition_penalty1.1, cache explicitly overridden false,
  fresh process120s. Temperature0.7/top_p0.8/top_k20 are inactive sampling fields.

**No training/evaluation prompt, role, template or assistant-prefix mismatch is
found.** The stored generation configuration says use_cache true, but the actual
frozen call overrides it false; this is not a base/adapter discrepancy. The
diagnostic EOS set includes an additional checkpoint special token; preserved
responses terminate at151645, so no observed termination mismatch explains fencing.

There is a **conditioning/decoding difference**: supervised likelihood uses the
gold package prefix at every step and unpenalized logits; greedy generation uses
its own prior tokens and repetition penalty1.1 (including tokens already in the
prompt). Both models choose a fence before any package content and then produce
short answer snippets. A modest increase in raw-package target probability can
coexist with that choice; subsequent gold-prefix likelihood says nothing about
continuations after the generated fence. This is a plausible distribution/ranking
explanation, not a demonstrated causal effect of the penalty or a proven learned
markdown prior. No hidden reasoning or internal representations are inferred.

## 5. First-divergence inventory

[Inventory](r6_60/FIRST-DIVERGENCE.json) preserves all12 raw responses and token IDs.
Every response violates raw-package format at **character0**, the first backtick,
and **generated token0**, ID73594 (` ``` `). Fencing precedes any package content.
Every response lacks even a lexical key occurrence for the required
`definitions`, `foundation`, `program`, `version` package envelope.

| Record | Base snippet observation | Adapter observation | Tokens base / adapter incl. EOS |
| --- | --- | --- | ---: |
| E01 | result/type Int64/value0 | identical | 30 /30 |
| E02 | route_quote/charge object, string descriptions | result/type UInt16BE/value0 | 58 /31 |
| E03 | result UInt16BE/value0, FLAG_A/FLAG_B list | identical | 76 /76 |
| E04 | result UInt16BE/value0 | identical | 31 /31 |
| E05 | VERSION7/COUNT2 object | identical | 21 /21 |
| E06 | low0/high0/reading0 object | identical | 28 /28 |

Five response pairs are byte-identical; E02 changes but still omits the package.
UInt16BE is a snippet label, not an admitted wrapper Int64/Bool/Unit type, and no
observable program/dependencies/steps are provided. These are raw-text structural
observations, not repaired type/semantic scores. Native first blocker remains
SERIALIZATION/JSONDecodeError at$. No fences were stripped, no repaired package
was evaluated, and historical acceptance remains0/6 for both tracks. Historical
generated tokens244/217 and inference16.217444s/16.727540s remain separate from
this round's teacher-forced evaluations.

## 6. Resources, failures and optional probes

| Measurement | Base | Adapter |
| --- | ---: | ---: |
| Six forwards, synchronized evaluation seconds | 1.522911 | 1.283487 |
| Worker time after baseline gate, load through final hashes | 9.938573s | 6.510540s |
| Whole qualified subprocess incl. baseline verification/startup | 80.088299s | 77.682423s |
| Peak allocated VRAM bytes | 2,920,335,872 | 2,924,694,016 |
| Peak reserved VRAM bytes | 3,042,967,552 | 3,047,161,856 |
| Final sampled device-free bytes | 9,086,959,616 | 9,084,862,464 |
| Generated tokens this round | 0 | 0 |
| Numerical/CUDA failures in qualified passes | 0 | 0 |

Whole process includes costly baseline/package/checkpoint integrity checks; timings
are not a controlled efficiency comparison. Allocator peaks reset before load.
Reserved8GiB/free1.5GiB/actual-worker-RSS16GiB bounds pass at retained record
boundaries; no continuous minimum or numeric peak RSS is retained. No exclusive
GPU isolation or WDDM per-process board-memory attribution is claimed.
Raw process receipts retain the initial assertion failure and successful qualified
processes; the offline assertion failure is also disclosed above.

**Optional probes: NOT_RUN.** Exact training-style prompting already produced the
preserved failures; the matched audit and target likelihood are sufficient for this
bounded diagnosis. No new free-generation calls, prompt search or constraints were used.

## 7. Learning, memorization and smallest next experiment

- **A supported:** improved training-target likelihood without valid generation.
- **B not demonstrated:** no structural-generation acceptance improvement.
- **C not observed:** no training/evaluation formatting-template mismatch.
- **D unresolved:** fitting six repeatedly presented exposed targets is compatible
  with partial memorization; it does not establish task-general semantic learning.
  Historical exact/normalized reproduction remains0/6, which does not rule out
  memorized fragments or reusable statistical patterns.
- **E contradicted for these frozen tokens:** all six paired losses improve.
- **F applies to transfer, usefulness in execution and causal format diagnosis.**

The adapter learned a more favorable distribution over useful target structure
**when conditioned on exact training prefixes**. It has not demonstrated useful
complete-package generation. The failure has a plausible gold-prefix versus
free-running ranking explanation, and substantial package omission remains even
beyond the first fence. Six exposed records cannot establish broad generalization,
semantic understanding or independence from memorization. One paired pass per
model supplies no repeated-run variance estimate.

**Recommended smallest next experiment:** separately authorize an inference-only
first-position competitor/ranking probe on these same six frozen prompts, for base
and unchanged adapter. Freeze before execution: retain raw logits/probability/rank
for target4913 and fence73594, and deterministically inspect the frozen1.1 repetition
penalty versus identity penalty1.0 on those logits. No training or prompt/data
expansion. This tests the immediate fence-choice explanation without changing or
replacing historical scores. It is a recommendation, not an executed continuation.

## 8. Publication and stop

[Publication identities](r6_60/PUBLICATION-IDENTITIES.json) bind protocol, original
and qualified sources, corrections, raw loss/process/token evidence, audit,
inventory, result, report and versioned documentation. [Verification](r6_60/VERIFICATION.json)
rechecks baseline/external identities, paired counts/means/probabilities, unchanged
parameters, source/JSON/links/whitespace/credential patterns and `git diff --check`.

The initial seal caught attempted new entries in inherited protected shared
documentation. Those exact additions were removed, restoring original bytes;
[publication correction](r6_60/PUBLICATION-CORRECTION.json) records the failure.
Observations/decisions/current boundary are in an additive
[research-log supplement](../../../docs/research-log-r6.60.md), bound by
[index identities](r6_60/INDEX-IDENTITIES.json). No model rerun followed publication work.

Production compiler/lowerer/runtime and experimental semantics unchanged; kernel26;
optimizer updates0; training0; expansion0; Python comparison adapter0; historical
rescoring0; P6-A04 acceptance0; P6-A05 access false. Stop after bounded diagnosis
and publication. **Await explicit authorization before further work.**
