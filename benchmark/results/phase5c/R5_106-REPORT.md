# R5.106 — Typed predicate and guard composition

**Final classification: `R5_106_TYPED_PREDICATE_GUARD_COMPOSITION_IMPLEMENTED`.**

The bounded family traverses captured source requirements → typed FRC → source
inventory/reconciliation → synthetic owner seal → complete structural coverage →
BDI/adequacy → faithful normal V1 → normal restricted author/compiler → external
application behavior. **Queries, mutation/lifecycle guards and staged conditional
validation share a pure typed boolean interpreter.** Four public synthetic domains
pass **124 external invocations**. Final generic verification passes **355/355
tests**, canonical model validation and safety. The classification is bounded
implementation, not complete closure of all normal predicate-related interfaces.

**Exposed B01–B20 behavioral successes remain eight: B01–B07 and B10.** No case
newly reaches a downstream stage. Native first blockers are **8 success / 8
structural / 1 BDI / 3 formalization**, where formalization separates **B17/B20
clarification** from **B12 invalid typed candidate/resource binding**. This is
not the R5.105 distribution relabeled: B12 actually refuses earlier with
`INVALID_TYPED_PREDICATE`. The completed transfer has **178 external invocations**.

R5.105 remains the pre-R5.106 baseline. All twenty cases are exposed development,
transfer and regression data; no held-out generalization, cumulative Phase 5C
achievement or independent cognition is claimed. Historical first results,
including B03's immutable first result, are preserved.

## Deliverables

| Deliverable | Location |
| --- | --- |
| Versioned typed algebra, operands, null/range/membership and effect boundaries | [Specification](../../../docs/typed-predicates-v1.md) |
| Closed pure expression validation, bounded equivalence and node decisions | `src/air_compiler/predicates.py` |
| Shared deterministic self-contained evaluation | `src/air_compiler/predicate_runtime.py` |
| Boolean model/migration and typed query/guard validation | `src/air_compiler/predicate_integration.py` |
| Atomic boolean replacement, guard rejection, staged condition activation | `mutable_values.py`, `mutable_runtime.py`, `input_values.py` |
| Common query selection and compatibility equality/CONTAINS normalization | `collection_query.py`, `collection_query_runtime.py`, `profile_runtime.py`, normal dispatcher |
| Closed typed FRC trees and normal formalizer guidance | `src/lykoi_workspace/predicate_schema.py`, query/mutable schemas, mutable profile guidance |
| Reconciliation equivalence, complete coverage, BDI/adequacy and faithful V1 | `src/lykoi_pipeline/query_profile.py`, `mutable_profile.py`, `src/lykoi_query/contracts.py` |
| Public products/users/sessions/documents source captures and literal external plans | `src/lykoi_workspace/predicate_corpus.py` |
| Typed/tree/authority/V1/boolean migration/external/adversarial verification | `tests/test_predicates.py`, existing 348 regression tests |
| Passing final checks and 124-invocation audit | `R5_106-GENERIC-FINAL-VERIFICATION-2.json`, `R5_106-SYNTHETIC-FINAL-EVIDENCE.json` |
| Pre-transfer generic content lock | `R5_106-GENERIC-LOCK.json` |
| Fixed fresh source captures and plans | `R5_106-B01-CANDIDATE.json` through `R5_106-B20-CANDIDATE.json`, `R5_106-CORPUS-LOCK.json` |
| Complete exposed transfer and before/after stages | `R5_106-TRANSFER-EVIDENCE.json`, `R5_106-COMPARISON.json`, [matrix](R5_106-CAPABILITY-MATRIX.md) |
| Preserved transfer interruptions and exact-JSON completion | `R5_106-TRANSFER-INTERRUPTION*.json`, resume/completion scripts and locks |
| Final implementation/history/corpus/whitespace/scope audit | `R5_106-FINAL-AUDIT.json` |

## Implemented semantics

Atomic comparison eq/lt/le/gt/ge, AND, OR, NOT, IS NULL, presence and scalar IN
collection all have a declared boolean result. Trees carry grouping structurally;
there is no arbitrary expression source or implicit truthiness. Inequality is
only NOT eq, IS NOT NULL is NOT is_null, and a range is a conjunction of ordinary
ordered comparisons. Every atomic comparison explicitly declares case,
normalization and `nulls: false`.

Operands declare types and reference bound fields/parameters, typed literals or
the local RAW/TRANSFORMED/PERSISTED pipeline value. Strings/enums/identifiers use
explicit sensitive/casefold and none/strip policies. Boolean equality uses exact
booleans, never 0/1. Timestamp equality/order uses parsed UTC instants, including
equivalent fractional-second spellings. Only existing timestamp nullability is
included. Comparisons with null/omitted optional input return false; NOT complements
that result, making explicit null inclusion/exclusion important.

Scalar-IN-set and existing collection-CONTAINS coexist through the same canonical
membership direction. Compatibility CollectionQuery equality, membership and
inclusion facts normalize into the common interpreter without reparsing prose.
New tree queries require node-local policy and put all selection in the tree;
existing order/result/effect rules remain bounded and distinct.

Boolean fields have typed literal creation, explicit additive migration and generic
input replacement through the atomic mutable-store path. Creation, update, reload,
query, guard use and invalid integer-for-boolean store rejection are externally
checked. Boolean creation from input and literal-assignment mutation commands are
not included. The historical v0.3 schema/runtime/generated application is preserved.

Guard trees evaluate against the original record and declared operation inputs,
before preparation/mutation. Lifecycle/delete preconditions declare command,
error and unchanged rejection. Missing-record authority keeps precedence. Staged
validation activates from the same algebra while keeping R5.105's private RAW,
pipeline-point TRANSFORMED and final-candidate PERSISTED observations. Omitted
optional writes still skip pipelines. Record-local invariants reuse trees with
the existing invalid_state rejection at read/write boundaries.

Integer comparison was investigated and refused at the normal writable-profile
type boundary; integer storage, arithmetic and comparison are separate concerns.
No range arithmetic, successor semantics or cross-type comparison was fabricated.
Declared resource operands are supported by the algebra with an explicit typed
environment, but normal predicate queries lack resource binding/sampling in this
round. Timestamp bounds are executable declared runtime parameters.

## Authority and adversarial challenges

FRC relations retain source-quoted complete trees, including operands/type,
operator, grouping, policy, stage, null semantics, membership direction and guard
rejection behavior. Reconciliation recognizes only bounded mechanical equivalence:
associative/commutative/idempotent same-operator AND/OR and double NOT. Exact tree
serialization still survives V1, even where meaning is equivalent for reconciliation.

Adversarial source candidates dispute AND↔OR, removed/extra operands, NOT,
inclusive↔exclusive bounds, null inversion, membership direction, case policy and
grouping. Ill-typed direction/type changes refuse; structurally well-typed material
differences dispute source inventory. Coverage recomputes complete IR/facets and
fails closed on missing operands. V1 corruption detects all material changes.

BDI publishes complete material node/subnode decisions, including policies,
operands, grouping and guard errors. Removing node authority yields
IMPLEMENTATION_UNDERSPECIFIED. Formalizer guidance requires clarification for
undefined recent boundaries, inclusivity/null participation and ambiguous grouping.
These captures do not demonstrate an autonomous English ambiguity detector:
source-side interpretations, inventories and oracles share the active agent and
owners are synthetic. Mechanical agreement does not establish authority truth.

## Synthetic external evidence

| Public domain | External invocations | Outcome |
| --- | ---: | --- |
| Products | 31 | Complete normal path, verified |
| Users | 31 | Complete normal path, verified |
| Sessions | 31 | Complete normal path, verified |
| Documents | 31 | Complete normal path, verified |
| **Total** | **124** | All four pass |

Each domain exercises equality+boolean AND, parameter equality OR, explicit null
exclusion with strict UTC cutoff, inclusive timestamp range/boundary cases,
scalar-IN-runtime-set, distinct nested groupings, boolean persistence/reload,
rejected lifecycle/mutation guard byte preservation, conditional RAW activation
with TRANSFORMED validation, transformed persisted strings and persisted collection
membership combined with lifecycle state. Additional tests exercise additive
boolean migration, record-local invariant composition and malformed stored booleans.
Those supplemental invocations belong to tests, not the 124 published-plan count.

### Generic development chronology

Focused development caught a nullable timestamp literal unsupported by the legacy
component (changed to the existing nullable-input omission default), and an old
query BDI assumption requiring a parameter even for constant-only predicates.
Both fixes preceded full verification. The first passing 354-test check was followed
by a boolean migration/invariant test and direct typed-query validation correction;
355 tests then passed.

The first four-domain audit preserved three successes and one sessions oracle
failure: its replacement pipeline explicitly deduplicated but the oracle expected
a duplicate. The expected array was corrected before any lock or corpus outcome.
Final 355-test verification passed. A chained verification/audit shell call timed
out after two audit domains, publishing no lock; the standalone audit completed
all four and published the sole generic lock. Initial verification/audit records
remain preserved. **No product/spec/test edit followed any transfer outcome.**

## Fresh fixed exposed transfer

| First-blocker category | Preserved R5.105 | R5.106 |
| --- | ---: | ---: |
| Behavioral success | 8 | **8** |
| Structural | 9 | **8** |
| BDI/event discovery | 1 | **1** |
| Source clarification | 2 | **2** |
| Invalid typed candidate / missing normal resource binding | 0 | **1** |

Every bundle freshly reads frozen sources. Unchanged supported facts retain their
current typed interpretation rather than replaying saved FRC results. New captured
tree/boolean/guard components are added where authorized; excluded demands remain
explicit. This is same-agent current-system capture evaluation, not a fresh live
language-model English-parsing study.

* **B01–B07/B10:** all eight preserved local successes pass 178 final transfer
  invocations. No behaviorally successful case regresses.
* **B08:** boolean creation/migration and list-archived predicate are represented.
  Remaining unsupported obligation is literal boolean mutation plus amendments
  to existing listing selection. No unrequested --archived input is invented.
* **B09:** inclusive/null-excluding compound selection is represented. Remaining
  gaps are the archive interface precursor and source-specific declared timestamp
  errors / start≤end query precondition. Pure comparison support alone cannot
  authorize the required query rejection behavior.
* **B11:** deletion's pending OR (completed AND archived) guard is represented.
  Coverage still refuses the explicit unclosed archive interface precursor.
* **B12:** the full tree retains the source-authorized UTC clock, membership and
  state/null conditions. Native producer validation refuses the unbound resource
  before sealing: FORMALIZATION / INVALID_TYPED_PREDICATE, not clarification and
  not a newly reached stage. The normal clock-to-common-query binding is a seam.
* **B13:** common complete/append-note guards and notes write semantics are
  represented; coverage still refuses the inherited archive interface demand.
* **B14/B15/B16/B19:** relationships, quantified guards, multiple-entity existence
  and atomic successor/effect/arithmetic families remain structural gaps.
* **B17/B20:** DISPUTED clarification remains; no migration role/member error guessed.
* **B18:** UNSUPPORTED_BDI_SCOPE remains its event/effect discovery issue.

Thus B08/B09/B11/B13 advance **component representation**, not request-level
stages or behavioral success. B12's earlier producer refusal is an integration/
candidate limitation, not an improvement and not evidence of source ambiguity.

### Transfer interruptions and preservation

The initial driver completed B01–B07 but stopped before B08's formalization on an
in-memory Python tuple in a retained unsupported-demand specification. All twenty
candidate JSON files were already fixed; JSON serialization faithfully represented
those tuples as canonical arrays. A new evidence driver read the **exact original
locked bytes**, changing neither candidates nor product.

That driver reached B12 and exposed the native unsupported resource-reference
failure which the historical evaluator did not catch. A separately pinned
prospective evidence wrapper records that producer failure at its actual stage
and completes the same twenty locked candidates. Both interruptions/stdout results
and their receipt limitations are preserved. The complete published audit is the
reported twenty-case denominator; interrupted repetitions are not added to its
178 invocation count. Neither problem triggered an implementation or candidate repair.

## Recommendation and stop

**R5.107 should target bounded normal predicate/value interface closure**, before
relationships: source-authorized literal-assignment mutation, existing-listing
selection amendments, query preconditions/declared typed-input errors and normal
clock/resource binding to common trees. This is a recommendation only. It should
use multiple synthetic domains and a new generic lock before exposed transfer.

No benchmark-specific primitive or benchmark-ID dispatch was introduced into
product code. Benchmark identifiers occur only in exposed capture/evidence tooling.
No model/tool/runtime/firewall infrastructure work or excluded semantic family was
started. **Stop after R5.106 generic implementation and exposed transfer.**

## Completion answers

1. eq/lt/le/gt/ge, AND/OR/NOT, presence, IS NULL and scalar-IN-collection.
2. Yes, typed/bound operands and source-quoted complete relations; same-agent authority evidence boundary.
3. Yes, exact structural grouping survives round-trip and deterministic execution.
4. Existing nullable timestamps; explicit atomic-null-false semantics, parsed UTC ordering and composed inclusive/exclusive ranges. No integer write/range profile.
5. Yes, IN and compatibility CONTAINS normalize into one membership direction.
6. Yes, normal tree queries and compatibility selection share the interpreter.
7. Yes, mutation and lifecycle/delete guards reuse it with separate rejection effects.
8. Yes, bounded local staged validation conditions preserve RAW/TRANSFORMED/PERSISTED.
9. Yes, material changes dispute; limited mechanically established equivalences reconcile.
10. BDI/adequacy refuse missing material typed authority; undefined English conditions require source-side clarification rather than guessed trees.
11. Yes, four synthetic normal V1/Lykoi/compiler/external paths verify the bounded family.
12. **Eight**, B01–B07/B10.
13. No new request-level stages; B08/B09/B11/B13 gain represented components. B12 refuses earlier.
14. Literal writes/listing amendments, query input error/precondition effects and common-query clock binding.
15. Yes, B17/B20 remain ambiguous.
16. Yes, B18 remains a separate event/discovery issue.
17. Bounded normal predicate/value interface closure, as detailed above.
18. No benchmark-specific product primitive.
19. Infrastructure work was avoided.
