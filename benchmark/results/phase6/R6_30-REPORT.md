# R6.30 — Three-track AI software development comparison

**Final classification: `R6_30_COMPARISON_INCONCLUSIVE`.**

GPT-6.1 Sol completed all three base tasks and both additive modifications in
each track. All first submitted candidates pass their finite acceptance suites:
**A/B/C each56/56 base observations and27/27 extension observations**. Original
behavior rechecks each pass37/37, with zero regressions. Experimental Lykoi C
does not demonstrate functional or modification value beyond structured intent B.
Measured author-session overhead favors A over C; incomplete B telemetry and
unmetered coordinator effort prevent a complete workflow-cost ranking.

## R6.29 prerequisite: separately corrected, history preserved

[Correction1](r6_30/R6_29-CORRECTION-1.md) independently establishes that failed
VM checks use `validation`, not `structure`. A distinct scripted Bool guard and
increment control passes seven stage/type/signature/overflow observations before
the R6.29 model artifact is loaded for successor replay. The authoritative unchanged
VM explicitly chooses `validation` in its check branch. This justification is not
derived from the model-authored artifact's observed success or desired score.

Exactly four guard-stage expectations change in a
[successor manifest](r6_30/R6_29-ACCEPTANCE-SUCCESSOR-1.json). The unchanged artifact
passes **23/23** in [successor replay](r6_30/R6_29-SUCCESSOR-REPLAY.json), with zero
model calls. Original **19/23**, `R6_29_CONSTRUCTION_PARTIAL`, manifest, failed
verification and publication identities remain exact. No historical reclassification.

## Baseline and preservation

Initial Git status was clean. [Baseline](r6_30/BASELINE.json) verifies **1,569**
protected/history identities, the R6.29 publication manifest and receipt, inherited
R6.28/R6.27 qualification, and the installed qualified OpenCode executable.
Its explicit implementation identities and kernel ledger retain **26 constructs**.
Production compiler/lowerer/runtime, R6.10 VM, R6.18 wrapper, R6.23 adapter,
R6.24 dispatcher and R6.25 semantic contracts/transport are unchanged. All
inherited R6.3–R6.29 evidence remains exact. R6.27's qualified object-root schema
annotation is retained when exposing the original construction schemas.

C executes **experimental Lykoi**, through existing four-tool Session construction,
typed validation, deterministic expansion and the experimental VM. This is not
production Lykoi execution. Central behavior consists only of fixed symbolic
add/le/eq/check operations; no opaque Python performs that behavior.

## Frozen requirements and independent acceptance

[Protocol](r6_30/PROTOCOL.md), [tasks](r6_30/TASKS.json),
[acceptance](r6_30/ACCEPTANCE.json), [tooling documentation](r6_30/AUTHORING-DOCS.json),
coordinator/runtime/scorer and baseline are bound in the
[pre-author freeze](r6_30/FREEZE.json). No task is replaced after model performance.

| Task | Required ordered computation | Base cases |
| --- | --- | ---: |
| T1 CapacityFee | load+reserve; capacity guard; add fixed fee3 | 18 |
| T2 ConfirmedIncrement | Bool-enabled guard; a+b; equality confirmation; add1 | 19 |
| T3 FloorThenCeiling | seed+delta; lower-bound guard; add delta; upper-bound guard | 19 |

Exact signature precedes host-representation checks, then exact scalar typing,
ordered arithmetic/guards, then UInt16BE encoding. Bool is not Int64. Signature
errors are SHAPE, invalid representable scalar types TYPE, floats SHAPE, addition
overflow OVERFLOW/structure, guards validation, out-of-output-domain values
ENCODE_RANGE/encode. Cases cover normal/boundary values, underflow/overflow,
competing errors, negative/high output, missing/extra arguments and invalid types.
Output bytes, integer type, consumed0, code, stage and conceptual failing step
are checked. Auxiliary stored Bool values are excluded from conceptual step numbering.

The frozen explicit mathematical oracle is outside candidate implementations.
[Pre-author qualification](r6_30/PREAUTHOR-QUALIFICATION.json) compares **all83**
base/extension expectations with separately scripted native symbolic programs,
before any author inference. Scripts are not supplied to authors. Common host
plumbing is shared with A/B and is independently cross-checked by these native
observations; this is not an independently staffed oracle review.

Tasks are fresh coordinator-authored, synthetic and capability-tailored, differing
from R6.28/R6.29 in signatures, predicates, constants and ordering. Coordinator
knowledge of those examples is disclosed. They test small bounded software
endpoints, not broad application construction or development-unexposed sourcing.

## Three complete author workflows

- **A:** model authors Python `compute(v)`, with conventional checked-add and guard
  helpers, shared host validation and output encoding. Standard-library use is allowed.
- **B:** model authors input bindings and ordered assignment/check expressions.
  A lean deterministic generator emits Python. It only performs basic shape/identifier
  handling and Python compilation; no Lykoi typing, symbolic lowering or semantic checks.
  The existing R6.16 generator handles persistent records and cannot express these
  arithmetic endpoints. The new generator is experiment-local and does not extend Lykoi.
- **C:** model calls unchanged declare_input/apply_operation/define_result/
  validate_candidate tools, then may test the sealed artifact with run_case. Values
  are immutable and explicit dependencies/order pass actual semantic validation.

Every stage uses a fresh process/session, pinned `openai/gpt-6.1-sol`, requested
`high` variant,4096 output tokens/response,33 completion steps,32 development tool
calls, four complete attempts and240s process-wall budget. The unchanged C Session
also retains its internal24-call limit per attempt. Explicit requirements are
identical across tracks, with track-specific tooling docs. No acceptance cases or
other-track source are provided. Explicit tool access is restricted to the stage's
MCP bridge; hidden-context and OS-level exclusion remain unattested.

Counterbalanced base order is T1 A/B/C, T2 B/C/A, T3 C/A/B. Modification order is
T1 C/B/A, T2 A/C/B. [Measurements](r6_30/MEASUREMENTS.json) retain all15 session IDs,
model identity, prompt delivery, call counts and failures. Raw prompts/configs,
MCP arguments/feedback, SDK exports, attempts and artifacts are in the corresponding
`r6_30/T*-*/` directories. [Offline audit](r6_30/OFFLINE-AUDIT.json) verifies all15
argument/feedback lineages and reconstructs every C artifact from its actual calls.

### Orchestration interruption and collector successor

The enclosing terminal command's120s timeout interrupted T2/B after a candidate
was compiled and seven development tool calls completed. The original native
session contains three completed model messages and a fourth started/incomplete
message. Candidate/MCP records and the native session export were recovered;
**the author was not rerun** and no acceptance outcome drove continuation.
[Interruption](r6_30/ORCHESTRATION-INTERRUPTION.json) preserves unavailable process
wall time and lost raw stdout/stderr. Remaining stages follow the original order.

The frozen collector assumed numeric wall time and raw events for every stage.
A [separate collector successor](r6_30/COLLECTOR-SUCCESSOR-1.json) reads authentic
SDK messages for T2/B and retains missing time as null. Completed token usage is
a lower bound; no usage is inferred for the interrupted message. Frozen acceptance,
scoring functions, candidates, budgets and semantic code are unchanged. This is
an orchestration/telemetry failure, not a B capability or behavioral failure.

## Functional and modification results

[Functional evidence](r6_30/FUNCTIONAL.json) retains expected/actual results for
first and final candidates and original-behavior regression checks.

| Track | First-attempt base tasks | Final base | Extensions | Original rechecks | Regressions |
| --- | ---: | ---: | ---: | ---: | ---: |
| A Direct Python | 3/3 | 56/56 | 27/27,2/2 tasks | 37/37 | 0 |
| B Structured intent | 3/3 | 56/56 | 27/27,2/2 tasks | 37/37 | 0 |
| C Experimental Lykoi | 3/3 | 56/56 | 27/27,2/2 tasks | 37/37 | 0 |

There are **249** final base/extension acceptance observations across tracks and
**111** original-behavior rechecks. First/final copies are repeat evaluations, not
additional independent cases. Zero incorrect outputs, wrong error behavior,
candidate compilation failures, semantic validation failures or capability gaps
are observed. Each track submits five successful candidates with zero candidate
resubmissions or semantic repairs. C has **four development-tool sequencing failures**:
run_case requests execute before validation seals the artifact. These are genuine
retained workflow failures, not C type errors or scored behavioral failures.

Successful self-selected development test calls: **A36, B55, C0**. C's four test
requests fail before sealing; actual validate_candidate calls still succeed.
Model testing choices differ, despite comparable tools/budgets. C's first submitted
artifact acceptance therefore does not demonstrate superior debugging or repairs.

T1 modification adds an audited endpoint with an additional Bool guard after the
existing arithmetic; T2 adds a premium endpoint with dependent increment and cap.
Modifications and27 cases are frozen before base authoring, disclosed only after
all base processes terminate. Explicit base prompts omit modifications, and
disclosure timestamps are audited. Hidden-context withholding cannot be attested:
**modification results are `CONTAMINATED_UNENFORCED`**.

Original endpoints remain byte-for-byte deployed beside the new endpoints.
Consequently zero regressions partly follow from additive deployment preservation;
this is **not evidence of safe in-place refactoring, schema migration or edits to
existing behavior**. No claim of language-specific modification safety is supported.

## Actual effort, time and cost

Totals below cover three base and two extension author stages per track, including
prompt/schema/tool feedback overhead in reported SDK usage. Cached tokens are
reported separately; SDK total is used as reported, not reconstructed billing.

| Measurement | A | B | C |
| --- | ---: | ---: | ---: |
| Started model messages/calls | 23 | 24,including1 incomplete | 45 |
| Development tool calls | 41 | 60 | 40 |
| Development tool failures | 0 | 0 | 4 |
| Complete submitted candidates | 5 | 5 | 5 |
| Candidate repairs | 0 | 0 | 0 |
| Input tokens | 19,896 | ≥23,824 | 32,869 |
| Output tokens | 2,276 | ≥3,302 | 2,333 |
| Reasoning tokens reported | 668 | ≥490 | 111 |
| Cached-read tokens | 3,584 | ≥2,304 | 36,096 |
| SDK total tokens | 26,424 | ≥29,920 | 71,409 |
| Total author process wall | 134.667s | unavailable;138.481s known four-stage subset | 162.533s |
| Assistant-message elapsed,not pure inference | 125.310s | ≥147.573s completed subset | 154.032s |
| Deterministic development dispatch | 7.890ms | 10.286ms | 36.630ms |
| Python compilation only | 0.639ms | 0.757ms | not applicable |
| API billing | unavailable | unavailable | unavailable |

[Effort breakdown](r6_30/EFFORT-BREAKDOWN.json) separates actual generation/submission
work from validation and runtime. A/B complete submission/generation/compilation
dispatch totals6.194/8.084ms; C validate_candidate dispatch totals15.642ms, including
schema handling, adapter construction, wrapper validation and expansion. C final
acceptance separately uses9.419ms typed validation,12.946ms expansion including
validation,2.233ms public VM execution including VM validation, and1.854ms invalid
host rejection. These runtime/acceptance timings are not development wall times.

Baseline-to-freeze preparation elapsed **519.222s**, including the R6.29 correction,
task/oracle construction and tooling. Baseline-to-evaluation elapsed **1,213.599s**;
evaluation collector wall **0.584s**. These intervals include coordinator work and
orchestration gaps, are not per-track inference, and do not include subsequent
publication. Coordinator model tokens/cost, API billing, pure inference time and
hidden upstream retries are unavailable. SDK cost0 is not a billing receipt.
Effective reasoning remains unattested despite requested/exported high variant.

Thus fully costed total development superiority is **not established**. A's lower
measured calls/tokens/session wall than C is a bounded descriptive observation;
B's incomplete stage prevents a complete A/B/C wall-time or total-token comparison.

## Architectural value and threats to validity

**Structured requirements:** all tracks receive unusually explicit ordered,
typed/error-precedence contracts. This scaffolding plausibly contributes to the
uniform success, but there is no unstructured-requirement ablation.

**Deterministic generation:** B successfully constructs all endpoints using a tiny
generator and supplied conventional error helpers. This demonstrates local lean
sufficiency, not that arbitrary structured intent replaces semantic validation.

**Lykoi semantic validation:** C genuinely validates types, dependencies, closure
and expansion through fixed meanings. No model candidate violates those checks,
and no scored error uniquely prevented by C occurs. A/B helpers already encode
checked arithmetic and shared host/error behavior. No unique C advantage is measured.

**Symbolic composition:** C expresses dependent ordered symbolic operations. No
author invokes reusable `compose`; reusable-symbol discovery/retrieval/generalization
is not tested. All endpoints execute without an LLM after construction.

**Tool assistance/model behavior:** C's stepwise calls increase measured model
messages and context usage; four premature test calls fail. A/B batch submissions
and numerous self-selected tests differ from C's sealed-session interaction.
This compares the supplied workflows, not a pure isolated language effect.

Other limits: only three tiny synthetic capability-tailored tasks; one model and
one run per stage; shared coordinator/oracle development; inherited historical
knowledge; unattested session/OS/hidden-reasoning isolation; an interrupted B
process and incomplete cost telemetry; mechanically preserved additive originals;
in-process external observation wrappers rather than independently hosted sandboxes;
no blind independent review, capacity-matched ablation or statistical significance.
Finite passing tests do not establish universal correctness or broad superiority.

## Verification and recommended direction

[Offline audit](r6_30/OFFLINE-AUDIT.json) reconstructs C artifacts, verifies all15
native call/feedback lineages and repeats **83/83** saved C observations with zero
model calls. Frozen transport17, wrapper8 and VM82 methods pass (**107** total).
An initial audit assumed all native tool states expose `output`; genuine error
states use `error`. [Failed audit](r6_30/AUDIT-ATTEMPT-1.json) is retained and its
read-only lineage collector corrected; no behavior or expectation is repaired.
The frozen first-publication link checker also expects its own not-yet-created
manifest/receipt. [Failed publication](r6_30/PUBLICATION-ATTEMPT-1.json) is preserved;
a publication-only successor defers those exact two links and verifies them after
creation. These coordinator failures are additional preparation/publication effort,
not authoring repairs or semantic defects.

[Publication manifest](r6_30/PUBLICATION-IDENTITIES.json) and
[receipt](r6_30/VERIFICATION.json) bind report, contracts, artifacts, telemetry and
additive documentation; verify freeze,1,569 protected identities, JSON/links/
whitespace and `git diff --check`. No credentials, training, semantic operations,
P6-A04 acceptance or P6-A05 access are published/performed.

**Recommended next priority, requiring new authorization:** improve the experimental
orchestrator's per-stage process ownership, telemetry durability and explicit
validate-before-test sequencing. Then evaluate tasks with actual unscripted design
choices and in-place modifications, using complete comparable metering and a lean
B control. Keep typed symbolic validation available as an experimental option;
this evidence does not justify making it the mandatory authoring architecture or
changing production semantics. A lean direct-Python/intent path is locally sufficient.

**Stopped after bounded evaluation and publication. Await explicit authorization
before any further experiment or architectural change.**
