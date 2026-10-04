# R5.38 — Nullable domain and whole-contract coherence review

**Result: `R5_38_NULLABLE_COHERENCE_PARTIAL`.** Required nullable
values now refine under scoped non-null semantic facts in the authoritative
current pipeline. Presence remains a separate fact. The revised static
whole-contract pass correctly predicts the independent supported application and
rejects an unsupported safe composition before generation. Frozen B02's saved
operation family is **semantic-static READY / whole-contract NOT_READY**; no
retry is recommended. A post-lock independent audit finds a redundant-guard
ordering regression: the old optional analyzer accepts equivalent duplicate
presence guards, while the new checked ordering dependencies fail internal scope
consistency. Duplicate nullable guards fail similarly. This prevents validation
of nullable composition and optional-regression preservation as a whole.

The demonstrated bounded type/pipeline integration and revised readiness
methodology remain useful evidence, but the phase is incomplete. It is not
complete B02 readiness, a format freeze, or universal
implementation correctness. Candidate core constructs remain **30**, new core
constructs **0**. No B02 generation, B02 execution or frozen B02 acceptance ran.

## 1. R5.37 failure reconstruction

R5.37 ended `R5_37_B02_INTEGRATION_GAP`, with no implementation repair. Its locked
`benchmark.semantic.current_pipeline` rejected the complete submitted operation
family before emission:

```text
ValueError: before requires two typed instants; optional operand needs in-scope presence
```

The affected operand was **required `nullable<instant>`**, not optional. The
source already supplied `not(equals(reference, typed-null))`. R5.23 explicitly
identified nullable composition; this was an old requirement exposed by a
readiness-methodology error. R5.37's diagnostic, source, lock and result remain
unchanged. The present review changes two prospective implementation components,
not the historical locked compiler or frozen artifacts.

## 2. Optional versus nullable taxonomy

Authority: recursive semantic shape declarations and `typed_lowering_r5_12._type`,
consumed by current analysis/runtime/verification. The required record-field set
excludes only outer optional declarations.

| Domain | Membership | Value if present |
| --- | --- | --- |
| `T` | required | `T` |
| `optional<T>` | absent or present | `T` |
| `nullable<T>` | required | `null ∪ T` |
| `optional<nullable<T>>` | absent or present | `null ∪ T` |

`nullable<optional<T>>` is recursively accepted but does not permit record-field
absence: outer nullable still requires membership. Inner optional value checking
has no standalone absent sentinel. Arbitrary nested wrapper/parent-record
refinement closure is not claimed. Full definitions and scope limits are in
[the versioned interface](../../../docs/nullable-readiness-r5.38.md).

## 3. Presence versus non-null analysis

Membership witnesses remove **optional**, not nullable. Non-null witnesses remove
**nullable**, not optional. Required nullable fields already exist by declaration.
An optional nullable reference cannot safely evaluate its value without presence;
its non-null expression does not create a missing field. No dictionary convention
or Python `None` shortcut changes these semantic distinctions.

## 4. Semantic expressibility decision

**`EXISTING_SEMANTIC_CONDITION_SUFFICIENT`** and
**`EXISTING_TYPE_SYSTEM_GENERALIZATION`**. Existing negation and typed equality
to null express the condition, with either equality operand order. The internal
fact name `non_null` is checked machinery, not a new semantic relation or human
syntax. Neither `CONSTRUCT_31_REVIEW_REQUIRED` nor
`NULLABLE_MODEL_RETHINK_REQUIRED` is supported by the evidence.

## 5. Non-null refinement rule

Given `x : nullable<T>` and a same-scope semantic condition establishing
`x != null`, the effective operand type is `T`. The analyzer recognizes the
existing negated typed-null equality, records its producer/scope, and checks the
equality premise in the original nullable domain. The conclusion cannot justify
its own premise. Optional membership, if needed, is retained for that evaluation.
The unwrapping function has no scalar-specific or application-specific branches.

## 6. Scope and order independence

Fact identity consists of reference slot/path, fact kind and source-bound scope.
Checked facts additionally carry stable contract/document paths; Python object
handles remain private source-bound consumer keys under a seal. Selection creates
its own item binding. Facts do not escape to sibling selections, unrelated
conjunctions, alternative operations/branches, other records/fields or post-state.

Conjunction analysis collects same-scope facts before typing consumers. Checked
scheduling evaluates presence before null guards before dependent comparisons.
All six serializations of the combined three-condition selection generate and
conform identically. This is relation-set scheduling, not left-to-right semantics.
Population witnesses currently propagate to **direct** selection ordering only.

## 7. Optional plus nullable interaction

`optional<nullable<instant>>` is represented and exercised with absent, present-null
and present-instant rows. Only presence **and** non-nullness license instant use.
Either fact alone rejects. Both ordering dependencies are retained in CheckedPlan.
An optional non-null instant still needs only presence. No optional semantics
were changed or collapsed into nullable semantics.

## 8. Independent domain

The publication application contains required nullable `embargo` and `released`
instants, nullable `caption` string and `rating` integer, optional `reviewed`
instant, optional-nullable `window`, identity/edition and two independent writable
string fields. Its six-record population includes null, two tied earlier values,
equal cutoff, later value, and another present-null/absent witness.

Source, transport, state and launch declarations:
[independent contract](R5_38-independent-contract.json). This is a non-task
application; no task, due-date or benchmark-specific compiler behavior was added.

## 9. Nullable instant plus before

`earlier` selects exactly records with non-null embargo strictly before the typed
cutoff. Results are `b,a`; equal/later/null records are excluded. It follows semantic
source → authoritative analyzer → sealed CheckedPlan → current_pipeline → actual
generated subprocess → independent durable/public challenge → semantic verifier.
No prototype-only generator substitutes for that entry.

## 10. Nullable instant plus ordering

`ordered` selects non-null embargo values then orders by embargo and code:
`a,b,equal,later`. Chronological ties resolve by the explicit secondary key. Null
is excluded before ordering. Changing the secondary key to edition yields
`b,a,equal,later`. Fully tied keys retain existing unconstrained-tie semantics;
no semantic null-first/null-last rule was introduced.

## 11. Nullable-refined write

`replace` and `remove` use a non-null/before-selected publication row and existing
sole/project/equality relations to establish target eligibility, then existing
keyed replacement/removal. Replacement changes only `a.label`; removal removes
only `a`. Independent pre/post file bytes and verifier framing preserve unrelated
rows/fields. The nullable machinery is shared with reads, not a read-only path.

## 12. Cross-type generality

`caption` combines the same refinement with `nonblank`; `rating` combines it with
integer equality. Both return `b,a,equal,later`, excluding null. The type rule
unwraps nullable generically; instant, string and integer do not have separate
refinement implementations. The matrix additionally exercises all three bases.

## 13. Unsafe and wrong-target negatives

Authoritative analysis rejects unguarded nullable `before`, unfiltered nullable
ordering, a guard on another field, a guard on another record slot, a guard inside
a negated conjunction, absent same-scope evidence and pre/post fact substitution.
Operation payloads cannot borrow unrelated branch/operation facts. The scoped
analyzer is the same authority used to form a CheckedPlan before generation.

## 14. Optional/nullable confusion regression

Permanent test `test_presence_and_non_null_are_separate_permanent_regression`:
required-nullable fields cannot use an optional-membership witness; combined
optional-nullable fields reject either prerequisite alone; optional non-null
instant membership still licenses before. A non-null expression never establishes
that an optional field exists. Six ordering permutations also exercise actual
absence and present-null rather than merely checking declared types.

## 15. CheckedPlan integration

Sealed facts distinguish declared type, declared presence/nullability domains,
established presence/non-null facts, effective type, producer dependency and scope.
Stable producer/scope document identities survive deserialization; they do not
authorize source substitution. Ordering facts retain all dependencies. Source or
fact mutation fails the seal. Existing internal node handles remain compatible;
there is no second type authority.

## 16. Generator integration

The emitter's only prospective change consumes the **checked producer order**.
It does not recognize `!= null`, infer a nullable unwrap, or change scalar runtime
semantics. Instant key emission uses authoritative effective key types. Poisoned
alternate typers and disabled downstream analysis still permit checked generation.

## 17. Verifier integration

The independent semantic interpreter uses the same authoritative checked facts,
but evaluates original semantic relations over observed values. It never reads
generated algorithms to decide what should happen. Grounded disposable null
acceptance, omitted selection and ordered-null faults all fail conformance.

## 18. Semantic mutations

Five semantic-only changes regenerate and conform: cutoff, nullable field,
secondary ordering key, write field, and the direction of the guarded before
relation. No compiler edits accompany them. Outcomes change as predicted:
three selected before-later rows; empty released-before-cutoff; edition tie order;
replacement of note rather than label; and later-only selection respectively.

## 19. Grounding

[Nullable evidence](R5_38-nullable-evidence.json) records **8 normal calls,
5 source mutations, 3 grounded nonconformant faults**. Reads preserve durable
bytes; writes have independent pre/post readback and semantic framing checks.
[Whole-contract public execution](R5_38-whole-contract-execution.json) records
**7 standalone public calls** through checked launch/transport/binding, including
read-after-write and remove on a shared durable store. Every applicable layered
verdict passes. The matrix adds **128 grounded conformant typed calls**.
These populations and calls are finite evidence, not universal proof.

## 20. Fault matrix

| Fault | Injection/challenge | Result |
| --- | --- | --- |
| A: null accepted by guarded before | Disposable generated predicate accepts null without evaluating its instant | Grounding PASS; semantic conformance FAIL |
| B: non-null record omitted | Disposable exact selection omits `a` | Grounding PASS; semantic conformance FAIL |
| C: null in ordered population | Disposable selection includes null; injected sentinel only permits faulty execution | Grounding PASS; semantic conformance FAIL |
| D: wrong-field refinement | Guard released; compare embargo | Authoritative compile-time rejection |
| E: escaped refinement | Negated/unrelated scope or other record/post binding | Authoritative compile-time rejection |

Fault artifacts are disposable and honestly resealed to isolate semantic errors
from provenance errors. The Fault C sentinel is deliberately wrong generated
behavior, not a proposed nullable ordering rule.

## 21. Existing optional regression

All **37** R5.25–R5.31 optional/current-authority tests pass in full discovery:
R5.25 4; R5.26 6; R5.27 4; R5.28 6; R5.29 5; R5.30 4; R5.31 8. The focused
R5.25–R5.29 run also passes 25/25. Presence witnesses, omitted constructors,
instant keys, typed writes, source-only changes and downstream authority poisoning
retain their previous results.

**Additional audit failure:** [redundant-guard evidence](R5_38-redundant-guard-audit.json)
constructs a non-task optional-instant selected ordering with two equivalent
presence conditions. The historical analyzer loaded directly from the pinned
HEAD accepts its CheckedPlan; the current analyzer rejects with
`compiler internal consistency failure: ordering refinement`. Required-nullable
ordering with two equivalent non-null guards has the same failure. Scope producer
maps keep one producer per fact, but ordering dependencies retain both source
producers, so the redundant producer fails the scope invariant. This is an
implementation regression/incomplete idempotent-conjunction composition, not a
change to the intended optional domain or a reason for #31. No post-static
implementation repair or B02 reanalysis was performed; the 625-file lock remains
valid. Passing the previous 37 tests is insufficient to select the validated gate.

## 22. R5.36 methodology audit

R5.36's matrix used broad rows such as ordering, optional refinement and general
lowering. It marked optional refinement independently resolved and recorded no
benchmark-critical blocker, while its limits said only “scoped presence witnesses.”
The method had no operand-domain obligation linking R5.23's nullable comparison
to a distinct nullable elimination witness. Successful neighboring capability
evidence substituted for an unproved composition. Matrix validation then checked
record consistency, not closure of the actual complete contract.

This is a **coverage abstraction and evidence-substitution error**, not merely a
missed test or a new frozen requirement. R5.23 had already asked for shared-domain
compositions; that requirement was lost during coarse readiness aggregation.

## 23. Revised readiness model

Readiness is keyed by relation, declared/effective operand domain, refinement
prerequisites, scope/dependency, state shape, read/write composition, binding
domain and pipeline stage. Optional-present instant before and nullable-non-null
instant before are distinct cells. `SUPPORTED_STATIC` is implementation support,
not execution or proof. Missing profiles and unrepresented external obligations
fail closed. Semantic-static READY is explicitly insufficient for retry.

## 24. Domain/refinement closure matrix

[Machine-readable matrix](R5_38-domain-refinement-matrix.json): **84 combinations**
of string/integer/instant × required/optional/nullable/optional-nullable × equality,
before, ordering, selection predicates, fallback, projection, write targeting.
Each includes required facts, effective result, state shape, context and stage.

[Pipeline evidence](R5_38-domain-pipeline-evidence.json): **64 accepted combinations
generate, ground and conform**; **20 unsupported combinations reject before
generation**. Populations exercise present values, null and absence as applicable.
Fallback is omission elimination, not null elimination. Projection preserves
nullable but cannot require optional fields. Before is restricted to instant.
Typed nullable invocation does not establish public nullable decoder support.

## 25. Whole-contract readiness pass

`readiness_r5_38.inspect` walks the entire document, not one operation frontier.
It checks every operation through authoritative analysis and sealed planning,
records operand facts/ordering dependencies/state bindings, and traverses failed
operation expressions under real scopes to enumerate later independent failures.
Consumer boundaries are checked without invoking generated_unit, render, generate
or execution. Relation-set overlap/framing planning is analysis, not emission.

## 26. Composition readiness

The pass includes conjunctions, selected ordering, branch read/write use, relation
sets, registered pre/post shape evolution, scalar/sequence decoder domains,
transport route/output/persistence validation and launch validation. Route checks
are independent so a bad route does not mask later ones. Known public-state
alternatives/content constraints are explicit generic boundary obligations;
unknown obligation kinds reject. Natural-language requirements omitted by a source
must be supplied as coverage obligations; the pass cannot magically infer them.

## 27. Independent whole-contract prediction

[Independent readiness](R5_38-independent-readiness.json) is READY for all eight
operations and complete profiles. Generation is disabled during the static test;
then unchanged current_pipeline under checked standalone launch generates and
runs seven public calls. Static prediction agrees with actual generation and all
observed semantic/binding/persistence/transport/launch verdicts.

## 28. Negative readiness fixture

[Negative fixture](R5_38-negative-readiness.json) adds a second always-true
selection around the non-null selected population before nullable ordering.
Semantically every ordered member remains non-null. Current architecture cannot
propagate population facts through that nested composition and rejects it
statically as non-orderable. This is a valid safe application-semantic composition
outside the supported implementation boundary, detected before generation.
Nested closure is a documented general limitation, not a B02-specific repair.

## 29. Historical correction

**R5.36 readiness conclusion was too coarse with respect to nullable refinement.**
`R5_36_READY_FOR_COMPREHENSIVE_B02_RETRY` remains the historical result produced
by that methodology; its gate/matrix/artifacts are not rewritten. R5.23's prior
nullable finding and R5.37's unsuccessful integration remain historical evidence.
The correction is recorded prospectively in decisions and research log.

## 30. Frozen B02 descriptive static result

After implementation/evidence/verification, the recorder locked **625 files**:
identity `46d380be742eb11f6081b2ba548ed80d62a37c13789734f6b819234d06640e5c`.
HEAD remains `428a3409ea4d47a57a9fc9e5a94af2595d98ec43`. Byte lock verification
passes immediately before and after the **single** descriptive static pass.

[B02 static report](R5_38-B02-static-readiness.json) reads the unchanged saved
R5.37 document, augmented with explicit generic boundary obligations from its
existing reconstruction. Both current_pipeline.generate and generated_unit are
disabled. All **15/15 operation-family CheckedPlans** form; nullable before and
optional-nullable fallback now type coherently. This is not a complete checked
public B02 application. Overall status **NOT_READY**, generated/executed **false**.

## 31. Complete remaining-gap set for the supplied contract

The one pass records six findings together:

| Finding | Exact combination/stage | Classification |
| --- | --- | --- |
| Nullable public input | optional nullable instant → scalar public decoder | Unsupported binding domain |
| Public state alternatives | one public list/HIGH/overdue/migrate route → bare legacy/envelope/current operations | Unsupported transport composition |
| Durable content constraints | structural row codec + population uniqueness/nonblank identity/title/status/priority domains | Unsupported state-validity boundary |
| Transport profile | complete public mapping absent from saved operation-family document | Missing contract/profile coverage |
| State profile | checked durable declaration absent from saved document | Missing contract/profile coverage |
| Launch profile | checked standalone configuration absent from saved document | Missing contract/profile coverage |

There are **three capability gaps and three missing-profile obligations**, not
six measured execution failures. No further analyzer/CheckedPlan domain rejection
was found among those 15 operations. This is exhaustive for the supplied static
document/explicit boundary obligations, not proof that every possible encoding
or unrepresented natural-language requirement has been explored. Nested-selection
ordering remains a general matrix/fixture limitation but is not used by this B02
operation family and is not inflated into a benchmark-critical gap.

The later independent audit adds **redundant equivalent optional/nullable guards
plus ordering** to the general implementation completion set. It does not occur
in the saved B02 predicates and is not a second B02 static finding or frozen
failure. It must nevertheless be independently repaired and regressed before
claiming the requested nullable/optional integration is complete.

## 32. Retry decision

**Do not retry B02.** Complete the whole known benchmark-critical set independently
and supply complete checked profiles. A future descriptive whole-contract pass
must report READY for semantic/type/refinement/state/binding/transport/launch and
explicit boundary obligations before recommending comprehensive evaluation.
No “fix first gap, retry, discover next” recommendation follows.

## 33. Construct #31 decision

No #31. Nullable refinement composes existing null equality, negation, selection,
ordering and state relations. The demonstrated integration does not require a
missing application-semantic concept. Future boundary reviews must independently
justify any genuine semantic extension; this result does not preauthorize one.

## 34. Capability/readiness and verification matrix

| Class/check | Result |
| --- | --- |
| Nullable before / chronological order / refined writes | Integrated; generated, grounded, conformant |
| Nullable string/integer refinement | Same general machinery; conformant |
| Optional plus nullable | Both facts required; six orders conform |
| Unsafe, wrong target, leaked scope | Authoritative rejection |
| CheckedPlan / generator / verifier authority | Sealed facts and downstream poisoning tests pass |
| Whole independent contract/profiles | Static READY predicts successful generation/public calls |
| Safe nested selection ordering | Static NOT_READY; known population-fact boundary |
| Frozen B02 saved operation family | 15 CheckedPlans; overall NOT_READY; no generation/execution |
| Full restriction-aware benchmark harness | 360 discovered; 324 pass; 36 explicit restriction skips; 0 failures/errors |
| Application/compiler | 31/31 pass |
| New R5.38 tests | 13/13 pass within full discovery |
| R5.10–R5.36 permitted focused families | Covered in full harness; module denominators recorded |
| R5.37 evidence integrity | 5 pass; 1 historical live-tree lock assertion intentionally skipped |
| Post-lock independent redundant-guard audit | FAIL: optional baseline accepts, current rejects; nullable duplicate guard also rejects |
| Model validation / safety | Pass; 0 capability violations, 0 invalid transitions, 6 invariants |
| Domain/refinement matrix / pipeline closure | 84 rows; 64 supported; 20 rejected; 128 grounded calls |
| Lock verification before/after B02 static pass | 625 protected files; no mismatch; HEAD unchanged |
| Evidence integrity audit | Pass for recorded hashes/verdicts/denominators; records partial gate and real regression |
| git diff --check | Pass |

The harness discovers its complete suite but explicitly skips all 35 tests in
historical B02 retry/integration modules (including rendering-only probes) plus
the one nested frozen-B02 acceptance replay. Historical files are untouched.
R5.37's one skipped live-working-tree lock assertion expects the old architecture
bytes; its immutable source/result/seal checks pass. Architecture/grounding/
semantic/binding/evolution/transport/launch suites run within full discovery.
No skip is reported as a pass. Exact identities and output are in
[verification](R5_38-verification.json) and [summary](R5_38-summary.json).

Environment: Windows `10.0.26300-SP0`, AMD64, Python **3.14.3**, PowerShell 7,
standard library only, PYTHONPATH=src for verification. `core.autocrlf=true`.
git emits LF→CRLF future-checkout warnings for the two prospective edited files;
these do not fail diff checking or semantics. One initial PowerShell command
failed to parse an environment assignment after `&&` and was corrected before
verification ran. One initial disposable fault-injection test found an emitter
binding-name mismatch (`_element_0` versus `_element_1`); the evidence fixture was
corrected before the final suites and lock. Neither is a B02 behavior failure.

Reproduction:

```powershell
python benchmark/results/phase5c/r5_38_review.py evidence
$env:PYTHONPATH='src'
python benchmark/results/phase5c/r5_38_review.py verify
python benchmark/results/phase5c/r5_38_review.py lock-check
python benchmark/results/phase5c/r5_38_redundant_guard_audit.py
python benchmark/results/phase5c/r5_38_integrity.py
git diff --check
```

The recorded B02 static result is consumed as evidence; ordinary verification
does not repeat it. Lock/static recorder modes document collection provenance,
not permission for a subsequent frozen evaluation.

## 35. Construct/system accounting

Candidate core **30**; new core **0**; #31 **not added**. Nullable facts belong to
**TYPE SYSTEM**; sealed identities/dependencies to **CHECKED PLAN**; exact-domain
consumer/profile enumeration to **READINESS ANALYSIS**; independent fixtures,
faults, matrices and observations to **TESTING/EVIDENCE**. No task-specific
semantics or replacement type authority was introduced.

Phase 5C remains paused. B03 is prospectively untouched. B17 is unexposed and
unclassified. Semantic-first format remains globally UNFROZEN. R5.2.2 remains
historical benchmark authority. Universal implementation correctness: **NO**.

## 36. Exact recommendation for R5.39

**R5.39 = Independent Refinement Dependency and Whole-Contract Boundary Closure
Review.** First repair canonical producer/dependency consistency for redundant
equivalent optional/nullable guards and prove preservation against the historical
optional analyzer. Review and independently complete the entire known set on
non-task applications: omitted versus present-null versus
present-instant public decoding; one public operation over declared state-shape
alternatives; population/content constraints with malformed-state no-write
boundary outcomes; and complete checked state/transport/launch profile coverage.
Use current authority, exact domain/refinement readiness, independent grounding,
semantic-only changes and fault evidence. Review semantic concepts before any
implementation requiring an extension. Do not retry B02, resume B03, expose B17
or add #31 automatically. Only complete static whole-contract READY can recommend
a later separately authorized comprehensive B02 evaluation.

R5_38_NULLABLE_COHERENCE_PARTIAL
