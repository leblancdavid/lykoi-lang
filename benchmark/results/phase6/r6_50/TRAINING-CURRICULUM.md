# Staged training curriculum — R6.50

Curriculum design only; no training runs, training export or coverage promotion.
Coverage labels below refer to the ten R6.49 candidates, not an independently
qualified paired corpus. Advance after deterministic acceptance and development-
validation checks in disjoint connected components; do not tune stages on evaluation.

| Stage | Behaviors and qualification targets | Semantic foundation / existing data gap |
| --- | --- | --- |
| 1. Basic typed expressions | Types, literals, dependency binding, checked addition, overflow/type rejection | Production bounded computation exists; byte arithmetic candidate evidence is experimental wrapper/VM, not a full production arithmetic curriculum |
| 2. Boolean constraints and ordered checks | AND/NOT, compound rejection, first-error order and no effect | Production typed predicates/staged guards exist; existing experimental ordering and two stateful guard examples are narrow |
| 3. Composition and references | Acyclic dependencies, shared subexpressions, binding/type errors | Production bounded computed graphs exist; pinned reusable definitions/hygienic DAG composition in current corpus are experimental-only |
| 4. Stateful transitions | Allowed/forbidden edges, terminal behavior, histories, multi-record independence | Two production-backed LOCAL_RELEASE episodes; shared scaffold is not broad lifecycle coverage |
| 5. Invariants and effects | Prewrite versus staged checks, rejected-byte preservation, atomic related effects | Production local invariant/atomic profiles exist; candidate coverage only narrow single-record invariant; related effects/authority gap |
| 6. Persistence and restart | Normal fresh-process continuity, deterministic ordering, migrations with explicit history | Production durable state exists; two candidate restarts, no admitted migration/multi-record-order evidence; concurrency/power-loss not qualified |
| 7. Reusable abstractions | Pinned composition, reuse without hidden callbacks, identity/dependency rejection | Experimental R6.18/R6.32 machinery; do not claim production abstraction registry integration |
| 8. Successor modifications | Changed requirement, old/new cases, no unintended regression, parent ancestry | Prospective pairs needed; historical modifications are exposed and must stay with predecessors |
| 9. Invalid input / error precedence | Missing, null, malformed, type/overflow/boundary, multiple invalid conditions | Existing finite cases provide a start; new stateful/history cross-products and independent expected error review missing |
| 10. Cross-feature combinations | References + guards + local atomic effects; time + nullable values + history | Existing production profiles bounded; admitted coverage of relations, authority, migration and dimensioned time absent |

Stages 2–6 and 9 are revisited throughout with negative/boundary examples, not
postponed until a model has learned only success. Distinguish rejecting invalid
semantic representations from runtime domain errors. Invalid targets must never
be ordinary positive completions; error-diagnosis/repair examples use explicit
task labels with preserved rejected input and approved corrected target.

## Complete 26-construct accounting plan

Bind coverage to preserved [R5.114 accounting](../../phase5c/R5_114-KERNEL-ACCOUNTING.json).
Require one source obligation, target site, positive and applicable negative/boundary
observation for each claimed construct; count interactions separately. Current
occurrences alone do not satisfy this matrix. Planned stage assignments:

- K01–K05 record schema, field, finite sequence, var, literal: stages 1, 3, 4, 6.
- K06–K09 equals, and, not, contains: stages 2, 5, 9.
- K10–K13 selection, trim, map(trim), stable_unique: stages 2, 3, 6, 9.
- K14 transition: stages 4, 8, 10.
- K15–K17 instant, before, operation contract: stages 2, 4, 5, 10.
- K18–K20 cardinality, input presence, typed resource/capability authority:
  stages 1, 3, 5, 9, 10.
- K21–K23 durable state, atomic commit, finite nonempty-path reachability:
  stages 4–6, 10.
- K24–K26 checked integer addition, fixed-duration instant displacement,
  checked elapsed-day duration conversion: stages 1, 8–10.

This is a curriculum mapping of all 26 preserved meanings, **not** a demonstrated
coverage result. Authority requires verifier-owned controlled-host contexts; CLI
actor strings do not authenticate. Reachability is finite/bounded; atomicity is one
local store. Arbitrary recursion, distributed transactions, physical effects and
general parsing remain outside this curriculum's qualified production scope.
Mixing experimental byte composition and production stateful targets requires
explicit task/foundation labels and separate metrics; no common executable union
is assumed. Decide later whether to use two tracks or a production-only first adapter.
