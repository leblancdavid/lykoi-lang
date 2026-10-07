# R5.111 — Typed numeric/cardinality computation and arithmetic boundary

**Final classification: `R5_111_TYPED_COMPUTATION_IMPLEMENTED_KERNEL_EXTENDED`.**

The bounded normal profile implements signed-64 integers, cardinality value
bindings, checked addition and separately typed fixed-second UTC displacement.
Explicit acyclic graphs feed ordinary mutations, predicates and related creations;
dependent effects share the existing local atomic commit. Increment, history and
successor construction compose. No unrestricted expression language was introduced.

Composition analysis finds two genuinely new operation meanings: **K24 checked
integer addition** and **K25 fixed-duration instant displacement (`offset`)**.
Finite pointwise map does not define either transformation. Exact R5.110 baseline
**23 → 25 proposed concepts**; types, graph/binding structures and application
patterns do not add further concepts. This is not a minimum-kernel proof.

Fresh frozen exposed transfer remains **16/20 successes B01–B16**, with **447
external invocations**. B18/B19 remain structural, with no newly reached downstream
stages. B17/B20 remain disputed. Generic content and prior evidence are unchanged
through transfer; earlier first results, including B03, are preserved.

## Deliverables

| Deliverable | Location |
| --- | --- |
| Exact baseline, types, operators, cardinality, binding/dependency and offset semantics | `docs/typed-computation-v1.md` |
| Closed graph validation, exact operand/result/dependency/domain/failure policies | `src/air_compiler/computation.py` |
| Lykoi-defined signed-64 value validation and integer predicates | `mutable_values.py`, `mutable_runtime.py`, `predicates.py`, `collection_query_runtime.py` |
| Deterministic checked evaluation and temporal lowering | `src/air_compiler/computation_runtime.py`, `profiles.py` |
| Mutation/computed guard/creation and coupled history integration | `references.py`, `reference_runtime.py`, `atomic_state.py`, `atomic_state_runtime.py` |
| Typed FRC/producer relations | `src/lykoi_workspace/computation_schema.py`, `reference_schema.py`, `atomic_state_schema.py`, `predicate_schema.py` |
| Structural recomputation, generic BDI decisions, adequacy and faithful V1 | `src/lykoi_pipeline/mutable_profile.py` |
| Five-domain normative synthetic authority and fixed literal external plans | `src/lykoi_workspace/computation_corpus.py` |
| Semantic, adversarial, normal-path, rollback and backend-independence tests | `tests/test_computation.py`; updated prospective integer expectation in `test_predicates.py` |
| Verification receipts | `R5_111-GENERIC-VERIFICATION.json`, `R5_111-CHECK-*.json` |
| Published synthetic external behavior | `R5_111-SYNTHETIC-EVIDENCE.json` |
| Kernel pressure and original-candidate reassessment | `R5_111-KERNEL-ACCOUNTING.json` |
| Pre-transfer generic lock | `R5_111-GENERIC-LOCK.json` |
| Twenty fixed fresh source captures/plans | `R5_111-Bxx-CANDIDATE.json`, `R5_111-CORPUS-LOCK.json` |
| Transfer comparison, native stages and behavior | `R5_111-COMPARISON.json`, `R5_111-TRANSFER-EVIDENCE.json`, `R5_111-Bxx-RESULT.json` |
| Transfer matrix | [R5.111 capability matrix](R5_111-CAPABILITY-MATRIX.md) |
| Content identity, kernel and scope audit | `R5_111-FINAL-AUDIT-2.json` (final documentation pins); prior audit retained |

## Semantic findings

### Integers and cardinality

Integer meaning is mathematical signed-64, including negatives, with JSON integer
serialization and reject-on-overflow. Python booleans, strings, integral-valued
floats and arbitrary-precision values are not admitted integers. Integer literals,
related fields, explicit JSON runtime parameters, reload and existing equality/order
predicates are supported through normal authoring/lowering. The historical primary
scalar field-introduction and nullable integer migration interface is not extended.

Cardinality is the existing K18 operation over a declared finite K10 selection.
`value(cardinality(selection))` explicitly binds its integer result; no duplicate
count primitive. It can feed addition, predicate, mutation and creation. Counts are
of selected occurrences, not distinct identities, and use the operation-before
domain. Missing domain/predicate/type/snapshot authority cannot be silently inferred.

Synthetic append-only history starts empty, creates one row per success, and uses
`cardinality(entire history)+1`. Exclusive cooperating one-store reservation makes
this bounded policy sufficient for strictly increasing ordinals. It is not a
distributed sequence guarantee or a rule for imported/deleted history. Multiple
same-snapshot creations need separate explicit ordinal constants/policy; nothing
silently increments between nodes or appends. Numeric history needs no Event core.

### Addition, binding and dependency

Checked addition has independent inventory/retry/ordinal uses. Signed adjustments
cover the synthetic negative-change contracts; a distinct subtraction operator is
not justified merely by symmetry. This does not prove arbitrary variable subtraction
is expressible without additional meaning. `x+1` is ordinary addition plus a literal,
not Increment/Counter. No multiplication/division/float/library operators were added.

Graphs contain 1..16 closed nodes with explicit names, types, sources, exact
dependencies and failures. Every computed dependency precedes its consumer; cycles,
forward references and shadowing reject. No nested arbitrary operator expression
trees, functions, dynamic dispatch, loops or recursion. Computed predicate sources
remain distinct from supplied input parameters. FRC/V1 preserve every relation;
structural coverage rejects incomplete graphs; material changed source-side graph
facts dispute reconciliation. Generic BDI graph/policy decisions retain source
authority; removed authority fails adequacy.

### Offset, clock and calendar boundary

`shift_utc_seconds(timestamp,duration)` is distinct from integer addition. Duration
has explicit type and unit `seconds`, signed-64 magnitude and JSON integer storage.
Plain timestamp+integer is ill-typed. The result is a canonical UTC Gregorian instant,
year 0001..9999, microsecond precision, excluding leap seconds; range errors reject.
Temporal vectors fix leap-year behavior, negative displacement, fractional preservation,
UTC spelling and boundary errors independently of incidental Python acceptance.

Original `offset` is admitted as **K25 fixed-duration displacement**; broader calendar
offsets remain unresolved. Local tomorrow, DST, months and years are not implemented.
The clock observes time; no implicit clock reading or arithmetic inside a clock.
UTC calendar days agree with 86400 elapsed seconds in this specified model, but
runtime N-day-to-second conversion is absent. The duration-unit closed schema and
exact types reject alternate units; sampled temporal-policy mutations change the
operator, rather than separately sampling a `duration.unit` field mutation.

Original `for_each` stays finite pointwise-map composition. Cardinality scope is
explicit finite-domain policy over existing sequence/selection concepts. No unrelated
original-candidate statuses are changed.

### Atomicity and successor composition

Related mutation computation observes the current operation-before store. Atomic
secondary graphs receive that before store plus explicitly declared primary images
and once-observed resources. No secondary-prefix or compile-time stale observation.
All dependent records are built privately; failures discard the full candidate.
The inherited one-store atomic replacement commits the primary mutation, one numeric
history row and ordinary successor together. Duplicate successor after history
construction, overflow, invalid inputs, predicate rejection and injected persistence
failure preserve bytes. Cooperating CLI reservation is inherited; direct host API
callers must cooperate for concurrency. No crash recovery/hostile writer/distributed
isolation claim.

Successor construction in the synthetic family is ordinary **related** entity
creation from computed after fields plus atomic coupled effects. The legacy primary
same-entity successor creation/resource/actor interface remains a separate integration
boundary. No benchmark-specific successor or recurring-task primitive was introduced.

## Verification and chronology

**386 passing tests**, canonical model validation and safety. Seven new computation
tests cover five full source-to-behavior pipelines, adversarial graphs, reconciliation,
coverage, BDI/adequacy, V1 recovery, integer boundaries, independent temporal vectors,
reload, current-state observation and rollback. Existing reference/history/value/
predicate/query/compiler/application/workspace/controller/pipeline/FRC/V1/coverage
and external baseline regressions pass.

| Synthetic domain | Published external invocations |
| --- | ---: |
| Inventory | 15 |
| Retry | 15 |
| Session | 15 |
| Subscription | 15 |
| Ledger | 15 |
| **Total** | **75** |

Additional controlled subprocess/vector invocations belong to tests and are not
added to the published 75. Domains share a bounded generic shape; this demonstrates
cross-domain reuse, not independently sampled domain generality.

Pre-lock diagnostics first found missing typed integer recognition in history-query
runtime; this was repaired before generic verification. Regression testing then found
the current predicate suite's obsolete "integer always unsupported" assertion.
It was updated prospectively; historical reports/captures were not altered. The
verification runner proves all other source/test bytes identical to the already-passed
tree by reconstructing the prior test bytes/hash, reuses those exact passed receipts,
and reruns the affected predicate suite. Its final 386 denominator counts each suite
once, excluding the obsolete assertion failure and diagnostic repeats. The first
whole verification command timed out; its completed receipts were preserved, and
the remaining public rehearsal suite and affected predicate suite passed on resume.

Published five-domain evidence and exact kernel accounting precede the generic lock.
All twenty fresh frozen-source captures/plans were then fixed before the first
transfer outcome. The first transfer driver timed out after B13; exact fixed bytes
were resumed through B20. No product/spec/tests/candidates/oracles were repaired
after lock or outcomes. Content checks confirm prior records/requirements/generated
artifacts unchanged. Same-agent captures/inventories/plans and synthetic approval
remain evidence limits; external subprocess behavior is not independent cognition
or held-out generalization.

## Frozen exposed transfer

| Outcome | R5.110 | R5.111 |
| --- | ---: | ---: |
| Behavioral success | 16 | **16** |
| Structural halt | 2 | **2** |
| Clarification/dispute | 2 | **2** |

**447 external invocations** freshly verify B01–B16. B18 now represents an ordinary
integer-valued audit schema, empty initial history and sequence-order read. Its native
unsupported obligations are **`B18/primary_history_integration`** and
**`B18/primary_actor_binding`**. Numeric/cardinality arithmetic is no longer a generic
capability gap, but complete success-only history coupling over inherited primary
commands cannot bind the required actor. No B18 BDI/adequacy/authoring/external stage
is reached and no partial B18 success is claimed.

B19 remains structurally unsupported: nullable recurrence-days in existing primary
creation/migration, positive runtime N-day conversion, primary same-entity cloning
with preserved/new/reset fields, and ordered actor-attributed dual history are not
closed. Fixed-duration related successors reduce the generic arithmetic diagnosis,
but establish no newly reached B19 stage or behavioral success.

B17's existing non-system migration role and B20's unknown-member error remain
unanswered. No inferred answers or system actor workaround.

## Completion answers

1. **Yes**, admitted typed integers are explicitly Lykoi-defined signed-64 values.
2. **Yes**, finite selection cardinality binds as an integer value.
3. **Checked integer addition**; subtraction not independently justified. Fixed-second
   displacement is a separate temporal operator, not overloaded addition.
4. **Yes**, increment and bounded successor patterns compose; no special primitive.
5. **Yes**, fixed elapsed-second UTC displacement with a typed duration; broad calendar
   arithmetic and runtime day conversion are absent.
6. **`offset` → K25**, fixed-duration core meaning; calendar-relative offset unresolved.
7. **Yes**, related mutations, computed guards and ordinary/coupled creation fields.
8. **Yes**, within the cooperating bounded one-store atomic frame.
9. **Yes**, generic related successor creation composes; full legacy primary interface
   remains unclosed.
10. **Yes**, cardinality-derived numeric history works without Event.
11. **B18 primary actor binding and complete inherited primary-history integration.**
12. **B19 does not advance stages or succeed**; residual interfaces identified above.
13. **Two core meanings**, checked integer addition and fixed-duration displacement.
14. **25**, from exact preserved 23.
15. **16/20**, B01–B16 exposed requirement-local successes.
16. **Yes**, B17/B20 remain ambiguous/disputed.
17. **Remaining leaks/limits:** broad legacy timestamp parsers, old standalone untyped
    query unbounded integer acceptance, Python string/JSON compatibility behavior,
    one-backend evidence only. New typed integers and displacement reject those
    incidental numeric/time behaviors in their declared boundary.
18. **Recommend R5.112 target source-authorized primary value/actor/interface closure**:
    actor parameters and prewrite authority, nullable numeric primary inputs/migration,
    typed UTC-day conversion and same-primary coupled creation. Require explicit
    treatment of unresolved authority; no new round started.
19. **No benchmark-specific primitive.**
20. **Infrastructure work avoided.**

**Stop after R5.111.** Useful computation is possible without a conventional expression
language, but its irreducible operation meanings must be counted rather than hidden
inside an existing map or backend policy.
