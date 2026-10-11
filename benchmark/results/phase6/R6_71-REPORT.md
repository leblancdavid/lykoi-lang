# R6.71 — Structured generation and semantic learning comparison

**Final classification: `R6_71_STRUCTURED_GENERATION_ONLY`.** All **54/54** frozen
generations completed, with **0 runtime failures**. Constrained decoding improved
structural validity. The R6.67 adapter completed more constrained JSON actions,
but did **not** improve correct semantic construction. Base accepted1/27;
adapter accepted0/27. This is a bounded diagnostic observation, not independent
generalization or language superiority.

## Baseline and preservation

[Baseline verification](r6_71/BASELINE-IDENTITY-VERIFICATION.json) passed before
dispatch and was repeated at publication. It checks the R6.70 publication and
ready=true receipt; unchanged R6.69 namespace-aware verifier; R6.67 trained adapter;
R6.52 checkpoint/tokenizer and executable identities; R6.65 scorer; nine frozen
R6.68 diagnostic identities and all A/B/C prompts/configurations. Original R6.68
and R6.69 protocol halts remain unchanged. Initial git status was clean.

- Base: Qwen2.5-Coder-1.5B-Instruct revision
  `2e1fd397ee46e1388853d2af2c993145b0f1098a`.
- Adapter file content identity:
  `7fa3e7bfd5f99dd54caf700d53537c165a1193752d9820b3283423dfc9aef921`.
- Trained loaded adapter tensor-manifest identity:
  `57c1281624acd0fe6249e78fdbea8755c3d81f24c35d203df0be5779b1f6db03`.
- Unchanged qualified decoder SHA256:
  `f93b261933487a9a95f8fc07339cfb9e902374a5421e4037f009ccf06cc9a01f`.

Live base and adapter unwrapped mappings each verify535/535 historical entries;
wrapped adapter base verifies535/535 and matches same-process unwrapped content.
Adapter verifies112/112 exact shape/dtype/raw-byte fingerprints. All parameters
are frozen; eval and inference mode apply. Before/after manifests match for both
workers. These are cryptographic fingerprint checks, not an independent numerical
elementwise comparison with historical arrays.

Production kernel remains26 under preserved accounting; production compiler,
lowerer, runtime and experimental semantics are unchanged. The inherited audit
protects historical identities; this publication has zero tracked modifications.
Training/optimizer/scheduler updates, dataset expansion, installations, Python
comparison adapter, historical rescoring and P6-A04 acceptance are0; P6-A05 access
is false. Deterministic assembly and execution remain AI-independent.

## Frozen execution

[Protocol](R6_71-PROTOCOL.md), [execution manifest](r6_71/EXECUTION-MANIFEST.json),
[source freeze](r6_71/SOURCE-FREEZE.json) and
[effective worker](r6_71/EFFECTIVE-WORKER.py.txt) document the fresh successor.
The worker retains the R6.68 generation/scoring loop and uses the qualified R6.69
loading/verifier path, adding attempt/raw-failure persistence and initialization
evidence. It does not change model settings, scorer, grammar or task semantics.
Protocol prose was published after inference; the execution manifest and source
freeze precede dispatch.

[Diagnostics](r6_71/DIAGNOSTICS.json) and
[conditions](r6_71/GENERATION-CONFIGURATIONS.json) are byte-identical copies of
R6.68 inputs. Base A/B/C then adapter A/B/C, N01–N09 each, one generation per cell.
A is unconstrained decoding (its existing system prompt already asks for raw JSON);
B adds the frozen stronger raw-JSON instruction; C uses A's identical prompts and
the unchanged structural token mask. Greedy, one beam, max128 tokens, penalty1.1,
cache off, seed651 and inherited precision; identical limits and scorer for both.
Each worker dispatched once, no retries or repairs.

## Structural validity and semantic acceptance

Every table cell below has nine diagnostic generations.

| Condition | Base strict JSON | Adapter strict JSON | Base schema | Adapter schema | Base full semantic acceptance | Adapter full semantic acceptance |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| A — unconstrained |0/9|0/9|0/9|0/9|0/9|0/9|
| B — explicit raw JSON |0/9|0/9|0/9|0/9|0/9|0/9|
| C — grammar constrained |6/9|9/9|6/9|9/9|1/9|0/9|

[Unchanged scorer outputs](r6_71/STRUCTURAL-SEMANTIC-SCORING.json) preserve all
eight dimensions and native first-failure diagnostics. Structurally valid but
semantically wrong actions remain failures. A/B semantic dimensions are
NOT_REACHED after serialization failure, not individually observed wrong choices.

| C dimension | Base /9 | Adapter /9 | Base among schema-valid /6 | Adapter among schema-valid /9 |
| --- | ---: | ---: | ---: | ---: |
| Correct operation |4|4|4|4|
| Correct ordered operands/literals |2|1|2|1|
| Correct result type |6|9|6|9|
| Exact dependencies |2|1|2|1|
| Deterministic assembly |1|0|1|0|
| Functional acceptance |1|0|1|0|
| All dimensions accepted |1|0|1|0|

On the **six matched cases where both models have valid schemas**, operation
selection is4/6 versus4/6; operands2/6 versus1/6; dependencies2/6 versus1/6;
correct type6/6 each; full acceptance1/6 versus0/6. Thus the adapter's extra three
complete actions do not hide a semantic advantage. No matched semantic dimension
improves. [Paired comparison](r6_71/BASE-VERSUS-ADAPTER.json) retains case-level scores.

## Error analysis and first-failure evidence

[Raw base](r6_71/RAW-BASE-OUTPUTS.json), [raw adapter](r6_71/RAW-ADAPTER-OUTPUTS.json)
and per-cell RAW/ATTEMPT files preserve verbatim outputs, IDs and dispatch evidence.
[Failure analysis](r6_71/FAILURE-ANALYSIS.json) preserves native scorer stages/errors
and separately labels observable failures, without repairing or parsing fenced bodies.

- All36 A/B outputs contain Markdown fences and fail strict serialization.
  B does not improve formatting for either model. Base budget exhaustion falls
  from3/9 in A to2/9 in B; adapter has0/9 in each, but still fails raw serialization.
- Base C truncates N04/N05/N07 at128 tokens while generating state-hash strings
  as dependencies/references. Each remains a viable prefix, not complete JSON.
- Both C models encode N01 numeric literals as reference strings `7` and `-11`.
- Both reverse the specified N02 operand order and include the distractor offset
  dependency. Both N03 actions have correct operands but include indirect seed.
- Base C N06 is the only accepted action: ordered `le(raised,twice)` with exact
  sorted direct dependencies, deterministic assembly and all three fixtures pass.
  Adapter reverses operands and dependencies and rejects at assembly.
- Adapter's newly complete N04/N05/N07 actions select add for comparison/equality
  requirements, with wrong operand/dependency bindings. Completion is structural.
- Both choose add instead of eq in N08/N09; N09 names the one correct dependency,
  yet remains a wrong operation/operand choice.

Across54 calls, nonexclusive observed labels are Markdown36, invalid raw JSON39,
wrong operation7, wrong operands12, wrong dependencies12, assembly rejection14,
and truncation/termination8. Schema mismatch0, wrong result type0 among schema-valid
actions, functional mismatch0 among reached executions, runtime failure0.
The14 assembly rejections are not14 behavioral executions: their functional
acceptance is NOT_REACHED. Serialization-invalid bodies are not rescored for
latent semantic correctness. The one reached behavior case passes.

## Decoder and inference measurements

[Measurements](r6_71/DECODER-INFERENCE-MEASUREMENTS.json) retain per-call token counts,
wall time, mask/setup time, scoring/validation/assembly time and VRAM peaks.

| Track/condition | Generated tokens incl. EOS | Inference wall seconds | Mask enforcement seconds | Decoder setup seconds |
| --- | ---: | ---: | ---: | ---: |
| Base A |879|152.300|0|0|
| Base B |826|145.929|0|0|
| Base C |612|395.299|290.016|12.981|
| Adapter A |592|103.948|0|0|
| Adapter B |520|93.206|0|0|
| Adapter C |340|112.186|53.650|13.189|

Mask enforcement is73.37% of base C generation wall time and47.82% of adapter C.
Setup is outside generation wall time. Combined enforcement343.665s plus
setup26.169s; this is measured decoder cost, not a causal comparison with the
same unrestricted output trajectory. Base truncation/long dependency strings
substantially increase its cost. Faster/shorter adapter outputs are not more correct.

All scorer calls total0.009575s, separate from model generation. Additional
structural-validation diagnostics total0.000239s and assembly attempts0.004489s,
including rejection attempts; successful repeated assembly/functional execution
also occur inside scorer time. Inference wall time does not include scoring.
Maximum allocated VRAM1,932,464,128 bytes and reserved2,527,068,160 bytes across
generation-level peaks, below the frozen8GiB reserved limit. Per-step stopping
criteria enforce120s and1.5GiB minimum free memory; all calls complete without
resource assertion failure. Peaks reset per call and exclude a continuous
whole-worker load/verification peak; no numeric minimum-free series was retained.

**Timing limitation:** the inherited outer-model forward hook is bypassed by PEFT
generation. Adapter `model_forward_seconds=0` means unmeasured, not free inference;
its `generation_other_seconds` includes real forward work. Reliable totals are
generation wall time and mask/setup timers. Do not compare the recorded base and
adapter forward-only columns or call the adapter remainder pure overhead. No
instrumentation repair or repeat generation occurred.

## Interpretation, validity limitations and next experiment

1. Raw-JSON instructions yield no strict formatting gain in this frozen setting.
2. Model-time constraints improve structural validity; three base prefixes still
   exhaust budget. The decoder guarantees admitted prefixes and structural checks
   at completion, not completion within128 tokens.
3. Adapter correct operation count remains4; no learned operation-selection gain.
4. Operand/dependency counts decline2→1 under C; no binding-selection gain.
5. Schema-conditional and matched-schema acceptance show no adapter semantic gain.
6. No semantic improvement transfers across these varied diagnostics. One base
   prior-result chain comparison demonstrates a usable incremental action;
   the trained adapter demonstrates none in this comparison.

The decoder admits all add/le/eq alternatives, both result labels, arbitrary refs,
literal choices and dependency strings; it sees no gold, expected fixtures or
application scope. It enforces compact ASCII fixed key order, selected/value
envelopes, scalar domains and dependency uniqueness, not task-correct operation,
operand order, scope or direct/sorted dependency identities. Type validity here
means the chosen label matches the requirement, not that the operation is well typed.
Adapter C structural completion improved, but this is not evidence of learned
semantic correctness beyond enforcement.

Nine coordinator-designed variations, exposed historical design context, one
greedy sample each, and a small fine-tuning history constrain inference. No
statistical population claim, independently sourced holdout, broad generalization,
causal training attribution or language-superiority claim is warranted.

**Recommended separately authorized next experiment:** a freshly frozen,
inference-only semantic-binding diagnostic with independent task/fixture curation,
operation-balanced literal/reference distractors, ordered comparisons and exact
direct-dependency controls; retain structurally matched comparisons and correct
the PEFT forward timer before its freeze. Predeclare sample size and paired
analysis. This is a proposal, not permission to generate tasks or execute it.
Further training is not established as beneficial by this result.

## Publication integrity and stop

[Publication identities](r6_71/PUBLICATION-IDENTITIES.json) and
[verification](r6_71/VERIFICATION.json) bind runner, effective worker, raw evidence,
analysis, report and supplement. Fresh-process verification checks hashes/sizes,
baseline equality, JSON/Python syntax, local links, whitespace, credential patterns,
additive-only scope and `git diff --check`. R6.3–R6.70 evidence remains preserved.

**Stopped after the authorized bounded comparison and publication. Await explicit
authorization before further work.**
