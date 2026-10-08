# R6.16 — Lykoi value-added architecture experiment

**Final classification: `R6_16_ARCHITECTURAL_COMPARISON_INCONCLUSIVE`.**

Both structured tracks meet every frozen application and modification expectation.
Direct Python produces executable persistent applications, but both retain one
incorrect error code. **No scored correctness or modification-safety advantage of
Lykoi over ordinary structured-intent generation was observed.** Production Lykoi
does supply additional pre-execution type/binding/effect checks; these are genuine,
but did not improve the authored applications' results and added integration burden.
This bounded exploratory slice supports a lean structured-intent option, not a
general conclusion that any architecture is superior or Lykoi should be removed.

## 1. Baseline, protocol and preservation

Owner authorization is the R6.16 value-added architecture request. The
[protocol](../../../experiments/value_added_r6_16/PROTOCOL.md) preceded infrastructure
implementation. [Baseline](r6_16/BASELINE.json) verifies **26** in production kernel
accounting and **775 protected/history identities**, with R6.15 transitive R6.3–R6.14
preservation, original R6.15 publication and supplement. Production model validation
passes; safety reports zero capability violations/invalid transitions, six invariants
(five runtime-enforced and one structurally guaranteed). A count and accepted model
are not a proof of construct minimality or general correctness.

The initial working tree contained six modified guidance files and untracked R6.15
publication. These are preserved; R6.16 guidance additions do not rewrite historical
results. Compiler/lowerer/runtime, canonical application, schema, generated production
artifacts and the R6.10 VM remain byte-identical. VM experiments are not Track C here.
No P6-A04 acceptance executed and no P6-A05 accessed.

[Capability inventory](r6_16/CAPABILITY-INVENTORY.md) separates production scalar,
mutable/predicate, authority/effect, invariant and impact APIs from new experimental
schema/generators/transport/oracle. Existing full source/FRC approval workflow was
not measured. Track C calls low-level production semantic APIs through a research
adapter; no claim of owner-approved normal-contract/FRC provenance is made.

Python/platform/head/model and initial status are captured. All recovered author
calls identify **openai/gpt-6.1-sol**. Harness-default reasoning is common by
instruction but unattested; filesystem/inherited guidance shared. Scripts use the
standard library and no provider SDK or credentials. Optional sanitized usage export
is OpenCode-specific instrumentation, not a provider dependency of the applications.

## 2. Freeze, task selection and pipeline fidelity

Two coordinator-authored synthetic applications:

* **Kiln firing permits:** cold/firing phase, open/closed vent, ordinary/emergency load.
* **Evidence custody seals:** unsealed/sealed phase, present/absent witness,
  routine/fragile material.

Both have immutable identity/time/category/label, verbatim nonblank labels, persistent
unique records, atomic rejection, guarded transitions and interacting state/gate
invariants. Stage 1 adds a guarded return transition. Stage 2 adds an explicit
category-conditioned exception, broadens the persisted invariant and retains ordinary
start's gate requirement and active gate locking. No frozen old case is superseded.

[Selection](r6_16/SELECTION.json), [requirements](r6_16/tasks/), [task freeze](r6_16/TASK-FREEZE.json)
and [separate modification seal](r6_16/MODIFICATION-SEAL.json) precede all application
authoring. Acceptance observations are explicit, prepared separately from author
submissions. No prior scored application implementation is reused. Selection is
implementation-aware, nonrandom, nonindependent and favors production record-local
semantics. The two domains **share the same structural skeleton**; they are two
applications, not independent demonstrations of broad semantic diversity.

The original frozen schema has a missing brace. The first unscored infrastructure
test failed on import. Original bytes and task seal remain preserved; the
[pre-author amendment](../../../experiments/value_added_r6_16/PREAUTHOR-AMENDMENT.md)
and corrected [shared schema](../../../experiments/value_added_r6_16/intent-2.schema.json)
were supplied equally to B/C. [Infrastructure freeze](r6_16/INFRASTRUCTURE-FREEZE.json)
binds the tested code before dispatch. No schema/generator/scorer changes follow
application acceptance. Setup failure is not an application repair.

| Track | Actual implementation |
| --- | --- |
| A | Independently AI-authored Python `handle`; conventional persistent JSON and guards. |
| B | Independently AI-authored shared intent; Lykoi-independent schema checker and ordinary Python generator/runtime. |
| C | Same intent grammar; existing `scalar_profile.lower`, production `mutable_values.compose`/typed predicates, then `profiles.generate_mutable`; production-generated guards/invariants/storage execute. |

C is a genuine semantic pipeline: no identity validator, callbacks implementing the
application or host validation substituting for Lykoi. Adapter only translates
declarative nodes/binds named API inputs/providers and projects success/errors.
**Transitions are guarded enum writes in existing typed mutation semantics**, not
production declared state-machine nodes; no static lifecycle-completeness or
invariant-preservation proof is claimed. All required behaviors were representable;
no unavailable final C application or task-specific construct was introduced.

## 3. Authorship, budgets and functional results

Six fresh task-level contexts, one application/track; stages resume only their own
context. Initial dispatch order A/kiln, B/custody, C/kiln, A/custody, B/kiln, C/custody;
calls dispatched in parallel. No other-track source or scored feedback was delivered.
[Stage 1](r6_16/REVEAL-1.json) and [stage 2](r6_16/REVEAL-2.json) reveal after all prior
handoffs. Cooperative restrictions cannot enforce hidden context/file withholding:
**EXPLORATORY**, staged results **CONTAMINATED_UNENFORCED**. Exported tool-argument
marker scans find no forbidden markers; this does not establish containment.

Per context/stage: 300-second cooperative budget, 12 tool calls, first candidate
plus at most one repair, at most two author-selected selftest batches capped 30s.
Recovered leaf-tool counts meet 12 and first→last-tool durations meet 300s. Parallel
wrapper/self-reported counts can differ; exported leaf counts are retained. Test
opportunities equal, consumption differs: B chose no selftests, A tested behavior,
C used generation checks and some behavioral tests. No acceptance-feedback repair.

Every first candidate is sealed before selftests. A/B first=final. Both C base
first candidates failed production scalar validation because input binding `value`
contained a field name rather than null. One repair/application corrects that redundant
metadata; finals pass. C/kiln's attempted second snapshot refused overwrite, preventing
its author retry; coordinator final scoring subsequently generated the unchanged
handed-off repaired intent successfully. First failures remain **0/26, UNAVAILABLE**,
not erased by final success. All modification first=final; no modification repairs.

Common external subprocess oracle restarts the application for every operation;
provider injection fixes UUID/UTC values using existing C provider authority. Exact
type/field/order comparison, persisted reload and rejected byte preservation are
scored. Per application: 13 base scenarios/26 observations, stage1 adds 8, stage2 adds13.
Coverage is finite directed cases, not exhaustive state space or fault-injection testing.

| Scope, both applications | A direct Python | B intent + Python | C intent + Lykoi + Python |
| --- | ---: | ---: | ---: |
| Base final observations | 50/52 | 52/52 | 52/52 |
| Fully accepted base applications | **0/2** | **2/2** | **2/2** |
| Base first-attempt observations | 50/52 | 52/52 | **0/52 (validation refused)** |
| Stage1 retained base / new | 50/52;16/16 | 52/52;16/16 | 52/52;16/16 |
| Stage2 retained base+stage1 / new | 66/68;26/26 | 68/68;26/26 | 68/68;26/26 |
| Cumulative full stage checkpoints | 0/4 | 4/4 | 4/4 |
| New modification requirements met | 4/4 | 4/4 | 4/4 |
| Passing→failing regressions | 0 | 0 | 0 |
| AI candidate repairs, all stages | 0 | 0 | 2 (base only) |

A's sole error per application is blank-label creation returning `invalid_input`
instead of required `invalid_label`; storage is preserved. Both persistent applications
otherwise execute the tested state/transition behavior. Reporting executable A programs
as fully accepted would be wrong. Zero regressions does not repair their inherited
failure. Raw stdout/stderr and per-operation timing are in [results](r6_16/results/);
summaries [base](r6_16/RESULTS-0.json), [stage1](r6_16/RESULTS-1.json),
[stage2](r6_16/RESULTS-2.json), with [submission seals](r6_16/SUBMISSION-FREEZE-0.json).
First/final and cumulative sources/intent/author records are under [submissions](r6_16/submissions/).

## 4. What Lykoi specifically added

[Semantic evidence](r6_16/SEMANTIC-EVIDENCE.json), [seeded runtime evidence](r6_16/CONTROL-RUNTIME.json)
and [impact output](r6_16/IMPACT.json) distinguish attribution:

* **Actual pre-execution author catches: 2** input-binding integration errors, each
  requiring one C repair. B accepts/ignores this unused metadata and still meets the
  contract. These are additional representational rejections/burden, not prevented
  observable defects. No false rejection of a valid canonical production IR observed;
  this is not evidence of zero possible false positives.
* Seeded wrong predicate operand type and unbound field pass the shared schema/B
  generation but fail **production typed predicate validation** before execution.
  B executes wrong-type redundant metadata normally; unbound field rejects a valid
  transition at runtime. This demonstrates earlier diagnostics, not a scored AI benefit.
* Seeded out-of-domain literal fails C composition before execution. B rejects it at
  runtime before commit with unchanged bytes. Additional timing of detection is real;
  persisted invariant safety is also available through ordinary B validation.
* Production capability/effect controls reject missing write authority and changed
  rejection policy. These are internal C consistency checks; B exposes no tunable
  capability/effect declarations and fixes atomic/unchanged behavior by generation.
  Do not credit C alone for the same observable guarantee.
* **Defect missed:** a well-typed `ignite` target of `cold` is accepted by both
  generators. Seeded execution confirms the wrong returned phase in both. Lykoi
  validates declared semantics, not agreement with the human transition requirement.
* Persisted invalid domains/duplicate IDs/blank labels/behavioral invariant violations,
  invalid/repeated transitions and category exceptions are rejected as required by
  **all three** final tracks, with unchanged rejected bytes. C runtime checks are
  genuine, but B/A provide equivalent observable protection in the frozen cases.
* Native legacy `impact(field:phase)` produces real dependency paths on the scalar
  base. It omits the extension mutations and predicate invariant users; **no complete
  modification-impact benefit was demonstrated**. Ordinary traversal over shared
  intent could expose those dependencies; no author-effort saving measured.

**Uniquely prevented scored behavioral defects: 0.** Stronger static checks are
real existing Lykoi capabilities; equivalent type/reference checks could also be
ordinary B validation. The comparison did not test that alternate B configuration.

## 5. Actual development efficiency and architectural overhead

Actual per-call exports: [base](r6_16/TELEMETRY-0.json), [stage1](r6_16/TELEMETRY-1.json),
[stage2](r6_16/TELEMETRY-2.json). Resumed-session stages exclude previously recorded
message IDs, preventing double counting. Original author null records remain intact.
Reported cost0 is metadata, **not API billing**; actual API cost is null throughout.

Totals across two applications and three phases (author sessions only):

| Track | Input | Output | Reasoning | Cache read | Model calls | Author wall s | Tool elapsed sum s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A | 132,926 | 22,733 | 1,368 | 2,714,496 | 54 | 600.681 | 8.789 |
| B | 129,054 | 16,866 | 348 | 2,099,968 | 42 | 441.720 | 7.153 |
| C | 138,683 | 22,218 | 1,104 | 2,790,272 | 53 | 579.771 | 10.633 |

Cache writes explicitly0. Input/cache/reasoning are separate exported fields; not
inferred billing units. Durations first-assistant-created→final-completed include
reads/prompts/schema/generation/selftests/logging; sums across parallel sessions are
**effort sums, not elapsed experiment wall time**. Tool sums may overlap. Comparable
matched accepted scope B/C: C has about **31% more author wall**, **32% more output**
and two extra repairs. Different chosen selftesting, same-model stochastic behavior,
shared context and synthetic selection prevent causal or cost-efficiency conclusions.
A is not a fully accepted matched-efficiency comparator; all its effort is retained.

Shared pre-author setup is **48,214 bytes/921 lines**, including protocol, both schema
versions, adapters/runtime, preparation/scoring/transport and qualification utilities.
Baseline→infrastructure freeze spans about **308 seconds**; that includes preparation
and orchestration, not isolated B/C infrastructure development. Coordinator setup,
analysis/publication model usage is **unavailable/unallocated**, not zero. Post-author
measurement/publication tooling is additional overhead, separately visible in the
experimental directory. This is not an end-to-end cost break-even measurement.

| Representation, kiln/custody | Base authored bytes | Stage2 authored bytes | Stage2 executable Python bytes |
| --- | --- | --- | --- |
| A | 5,564 /4,641 | 6,129 /5,215 | 6,129 /5,215 |
| B | 3,143 /3,231 | 5,397 /5,522 | 7,932 /8,057 |
| C | 3,136 /3,217 | 5,390 /5,666 | 55,195 /55,700 |

C also carries lowered IR, production module dependencies, multiple semantic versions
and wrapper/provider integration; B requires its schema/runtime/generator; A requires
neither IR nor generator. Generated template bytes are not hand-maintained complexity
or tokens. C generation/validation timings differ substantially by cold/warm imports
(base roughly44ms kiln versus3ms custody); no stable runtime-speed claim follows from
one-host process startup dominated observations. [Comparison](r6_16/COMPARISON.json)
retains full sizes, actual per-operation times, generation times and selftest records.

## 6. Attribution, recommendation and limitations

**Structured requirements:** identical for all tracks, so not a C-specific advantage.
**Structured authoring/deterministic generation:** B/C consistently emit the declared
error code; A's direct implementations miss it. This is a local correlation, not
proof the IR caused the improvement. **Semantic validation:** C has earlier typed
diagnostics, not better scored behavior. **Expressiveness:** sufficient for this narrow
record-local slice; unrestricted/general support is not tested. **AI interface/maturity:**
redundant binding metadata costs C two repairs; extension impact coverage is incomplete.

For these contracts, **ordinary structured intent is sufficient in observed behavior**
and locally cheaper to author than C. The broader architecture comparison remains
inconclusive: two isomorphic synthetic applications, correlated coordinator-authored
oracles, six single authors, varying test consumption, unenforced withholding, default
reasoning/routing unattested, missing setup usage/billing, no independent task sourcing,
no exhaustive coverage or long-term maintenance study. These limits preclude claiming
general B sufficiency, A superiority or demonstrated incremental Lykoi value.

**Recommended direction:** prioritize the lean B-shaped intent/generation path for this
bounded application class; retain Lykoi as an optional semantic analysis/research layer
where typed authority/effects could matter. Do not make it a mandatory layer on the
basis of this experiment. Keep direct Python as the simplicity baseline. A future
decision to retain/remove/integrate Lykoi needs separately authorized, more diverse,
controlled comparisons with complete setup cost and fair equivalent static checks.
No architectural/production changes are automatically made from this recommendation.

Publication checks cover experimental scoring integrity, deterministic generation,
normal compiler/application/baseline regression, hash preservation, scope and whitespace.
[Publication checks](r6_16/PUBLICATION-CHECKS.json) and
[identities](r6_16/PUBLICATION-IDENTITIES.json) retain actual commands/results.

**Stopped after bounded experiment and publication. Further experiments or Lykoi
changes require explicit owner authorization.**
