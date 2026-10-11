# R6.72 — Semantic binding diagnostic and curriculum design

**Final classification: `R6_72_PROTOCOL_HALT`.** Neutral timing qualification passed,
but base S11 reached `GRAMMAR_DEAD_END`. Ten base generations completed; S12 and all
twelve adapter diagnostic generations were **NOT_REACHED**. No retry or repair.
Partial base evidence shows binding and operation errors, including a deterministically
assembled reversed comparison that fails behavior. A paired adapter conclusion is
unavailable. Training was not performed.

## Baseline and frozen diagnostic

[Baseline verification](r6_72/BASELINE-IDENTITY-VERIFICATION.json) verifies R6.71
publication/raw identities and inherited R6.70 decoder, R6.65 scorer, R6.63 expert
demonstrations, R6.66 configuration, R6.67 trained adapter and base checkpoint.
Repeated publication verification checks equality. Initial git status was clean.

- Base Qwen2.5-Coder-1.5B-Instruct revision
  `2e1fd397ee46e1388853d2af2c993145b0f1098a`.
- R6.67 adapter file identity:
  `7fa3e7bfd5f99dd54caf700d53537c165a1193752d9820b3283423dfc9aef921`.
- Adapter tensor manifest identity:
  `57c1281624acd0fe6249e78fdbea8755c3d81f24c35d203df0be5779b1f6db03`.
- Unchanged decoder SHA256:
  `f93b261933487a9a95f8fc07339cfb9e902374a5421e4037f009ccf06cc9a01f`.

[Protocol](R6_72-PROTOCOL.md), [requirements](r6_72/REQUIREMENTS.json),
[expectations](r6_72/SEMANTIC-EXPECTATIONS.json), [source freeze](r6_72/SOURCE-FREEZE.json)
and [generation configuration](r6_72/GENERATION-CONFIGURATIONS.json) precede all
model calls. Four cases per add/le/eq; literal/ref mixtures, reordered typed scopes,
distractors, repeated refs, prior dependencies, false-versus-zero, comparison reversal
and negated greater-than wording. Two equivalent-wording/scope-order pairs are
correlated controls. No exact R6.63 training records are reused.

[Expectation review](r6_72/EXPECTATION-REVIEW.md): a distinct same-platform nonblind
reviewer derived operations/operands/order/types/dependencies and manually checked
all28 fixtures, finding no material ambiguities. Isolation and independence are
unattested: **coordinator-reviewed**, not independently qualified. Coordinator
executed all12 gold actions through unchanged scorer/assembler/semantics;28/28
fixtures pass. [Eight negative binding controls](r6_72/BINDING-REJECTION-CONTROLS.json)
reject invalid types/scope/literals/result/dependencies. The single-action interface
has no rejection response, so unsupported strict inequality or mixed-type requirements
are excluded from model diagnostics and do not become forced add/le/eq golds.

The seven decisions remain distinct: relation selection, operand identity, ordering,
literal/ref tags, type, exact direct dependencies, incompatible-binding rejection.
Valid JSON establishes none of the latter choices. Result type is supplied in scope;
type-label agreement is consistency, not unaided type inference. Commutative add/eq
order and alias identities require exact structural scoring beyond behavior.

## Timing correction and controls

R6.71's outer PEFT hook did not observe actual generation forwards. Its zero-valued
historical measurements remain unchanged. R6.72's [timer](../../../experiments/semantic_binding_r6_72/timing.py)
temporarily wraps the underlying Qwen2ForCausalLM forward callable, forwarding all
arguments and returning the exact output; it restores the callable and adds no hooks.
Synchronized perf_counter intervals measure actual elapsed forward work. The existing
decoder measures enforcement/setup independently; generation wall includes both.

CPU delayed-call/return-identity/restoration control passes. Neutral untimed/timed
generation produces identical token IDs `[3925,151645]` for both tracks. Before/after
base/adapter tensors match for both neutral workers; all parameters frozen.

|Neutral timed control|Forward calls|Forward seconds|Generation wall seconds|
|---|---:|---:|---:|
|Base|2|0.112024|0.114663|
|Adapter|2|0.126958|0.129291|

[Base controls](r6_72/BASE-TIMING-CONTROLS.json) and
[adapter controls](r6_72/ADAPTER-TIMING-CONTROLS.json) demonstrate positive PEFT
measurement and token preservation. Untimed first calls include warm-up and must
not be used to estimate timer overhead. Neutral equality is bounded evidence,
not proof over every generation. Per-forward synchronization adds measurement
overhead; these are instrumented elapsed times, not pristine latency estimates.

For the ten completed base diagnostic calls: **316.428s generation wall**, **95.004s
forward/562 calls**, **220.469s enforcement**, **14.285s decoder setup outside wall**,
and **0.955s remaining generation overhead**. Scoring totals0.005018s. Forward and
enforcement are measured separate intervals; no subtraction-based forward estimate.
The failed S11 interval was not persisted as a completed timing record. Adapter
diagnostic timing is NOT_REACHED, not zero cost. No paired performance comparison.

## Raw inference and authoritative semantic scoring

Both tracks were configured identically: unchanged prompts/mask, greedy one beam,
max128 tokens, penalty1.1, cache off, seed651, inherited precision and resource
budgets. The decoder admits semantically wrong operation/type/bindings; it receives
no expectations/fixtures/task-specific grammar. [Decoder controls](r6_72/DECODER-CONTROLS.json)
verify arbitrary out-of-scope alternatives and every viable prefix for their probes.

[Analysis](r6_72/SEMANTIC-ANALYSIS.json) preserves unchanged R6.65 scorer results,
raw outputs and read-only supplemental binding diagnostics. No normalization/repair.

|Dimension|Base completed /10|Base schema-valid /8|Adapter|
|---|---:|---:|---|
|Strict serialization|8|8|NOT_REACHED|
|Structural schema|8|8|NOT_REACHED|
|Correct operation|5|5|NOT_REACHED|
|Correct operand multiset, including tags/types|2|2|NOT_REACHED|
|Correct ordered operands (authoritative)|0|0|NOT_REACHED|
|Correct slotwise literal/ref kinds|1|1|NOT_REACHED|
|Correct supplied result-type label|8|8|NOT_REACHED|
|Exact sorted direct dependencies|3|3|NOT_REACHED|
|Deterministic assembly|1|1|NOT_REACHED|
|Functional acceptance|0|0|NOT_REACHED|
|Full acceptance|0|0|NOT_REACHED|

Operation selection among schema-valid cases: **add4/4, le1/4, eq NOT_REACHED (0
schema-valid cases)**. Both completed eq calls exhaust128 tokens and fail serialization;
do not infer a scored wrong equality decision from their prefixes. Among all ten
completed calls operation5/10, exact operands0/10 and deps3/10 are end-to-end counts;
the conditional semantic accuracies are **62.5%,0%,37.5%** among the eight schema-valid
actions. Only S07 reaches execution: two fixtures both fail. Functional0/1 reached
candidate differs from0/10 end-to-end. Seven assembly rejections are not executions.

## Observed failure patterns

- S01 uses stored backup instead of the two fixed literals and includes unrelated ok
  in dependencies. S02 adds Boolean ready to integer eight, rejecting type checks.
- S03 uses adjusted plus literal-3 instead of adjusted twice and adds shadow to deps.
- S04 chooses the correct two operands but reverses the required order and lists
  literal string `8` as a dependency. Its equivalent S02 wording/scope-order partner
  chooses a different binding; no robust pair consistency is observed.
- S05/S06/S08 choose add for inclusive comparisons. S05/S08 have the correct expected
  dependency list despite wrong expressions; dependency agreement alone is not closure
  correctness of the generated expression. S05/S08 invent unavailable literals.
- **S07 selects le and the correct operand identities/dependencies, but reverses echo
  and adjusted.** Assembly is deterministic; execution returns true in both fixtures
  whose required answer is false. This is a valid semantic error observation beyond
  schema compliance.
- S09/S10 emit long state-hash reference strings and truncate. Their semantic fields
  are NOT_REACHED. No fenced-body parsing or latent semantic rescoring.
- S11's saved incomplete prefix repeats snapshot in its dependency array. The unchanged
  terminal checker rejects decoded dependency duplicates, leaving no legal completion
  and raising GRAMMAR_DEAD_END. This supports a serialization/completion failure, not
  a completed scored eq action. S12 and adapter diagnostics remain NOT_REACHED.

Nonexclusive completed-output labels: wrong operation3, wrong ordered bindings8,
operand-selection errors6, order-only errors2, wrong dependencies5, slotwise kind
errors7, irrelevant-scope operands3, type-stage errors2, assembly rejection7,
functional mismatch1, truncation2. Type-stage labels include operation/result mismatch;
they do not all imply a wrong operand type. Slotwise kind mismatch may follow a pure
reversal (S04), so it is not seven independent kind-selection mistakes.
These are observed outputs, not inferred hidden reasoning or causal mechanisms.

[Halt](r6_72/DIAGNOSTIC-HALT.json), [failed prefix](r6_72/BASE-C-S11-FAILURE.json)
and per-cell ATTEMPT/RAW files preserve the first failure. The effective-source
traceback's synthetic filename can resolve an unrelated inherited linecache excerpt;
the frozen effective worker and original process traceback are authoritative for
code location. No repair or later cells were dispatched. There is no base-versus-
adapter diagnostic difference estimate; both only share qualified neutral timing.

## Training coverage, alternatives and next experiment

[Curriculum assessment](r6_72/CURRICULUM-ASSESSMENT.md) reviews all ten unchanged
demonstrations. They teach positive basic add/le/eq mechanics, both le literal
orientations, same-type distractors, repeated refs and one prior result. They lack
matched same-scope operation contrasts, swapped-order negative choices, scope-order
twins, false/zero action contrasts, and labeled invalid type/dependency alternatives.
Existing runtime-negative fixtures are not assistant training targets. Coverage
gaps are documented, but no causal attribution or adapter failure is established here.

A complete-action curriculum retains native supervision but carries boilerplate;
B compact selection requires a lossless deterministic renderer; C contrastive
choices require verified negatives/feedback and control of label/mutation shortcuts.
Recommend **C with explicit B-style semantic choices and deterministic reconstruction**,
retaining two ordered tagged operands and explicit dependency choices. Shorter
targets are not presumed better. Rendering must reject invalid choices, never silently
choose correct identities or dependencies.

[One successor design](r6_72/SUCCESSOR-DESIGN.md): same pinned base, one fresh q/v
LoRA, proposed36 verified positives/72 contrastive negatives, frozen20-step inherited
training settings,18 fresh evaluation-only family cases, matched base, no evaluation-
family leakage, qualified compact schema/renderer, unchanged authoritative functional
acceptance. No data expansion/training executed here. A focused training test is
justified as a falsifiable proposal; separately authorize neutral completion
qualification and data review before it. The halt prevents any immediate paired
semantic-learning conclusion.

## Preservation, verification and stop

[Publication identities](r6_72/PUBLICATION-IDENTITIES.json) and
[verification](r6_72/VERIFICATION.json) bind all new evidence/source/report/design.
Baseline preservation is repeated in a fresh process. JSON/Python syntax, local
links, whitespace, credential-pattern checks, additive scope and git diff --check
pass. A pre-freeze exception-handler naming error was corrected before inference,
with its [preparation failure](r6_72/PREPARATION-FAILURE-1.json) retained.

Production kernel remains26 by preserved accounting; compiler/lowerer/runtime and
experimental meanings remain byte-preserved. No optimizer/scheduler/backward/training,
new primitives, dataset expansion, Python comparison adapter, historical rescoring,
P6-A04 acceptance or P6-A05 access. Model parameters are frozen and inference mode
applies. Neutral before/after tensor fingerprints match; the diagnostic worker halted
before its post-run live-tensor check, which is NOT_REACHED. On-disk base/adapter and
all historical publication identities remain verified. Do not claim an unperformed
post-diagnostic live check. AI-independent deterministic execution is retained.

**Stopped after bounded diagnostic attempt and publication. Await explicit owner
authorization before any retry, decoder work, dataset creation or focused training.**
