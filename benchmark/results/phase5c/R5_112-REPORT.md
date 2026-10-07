# R5.112 — Primary value, actor and successor integration

**Final classification: `R5_112_PRIMARY_INTERFACE_COMPOSITION_PARTIAL`.**

The existing **25-concept kernel** expresses primary signed-64/nullable numeric
state, explicitly supplied primary actor context, cardinality-derived history and
unconditional same-primary successors by composition. These admitted interfaces
traverse normal typed FRC → reconciliation → structural → BDI → adequacy → faithful
V1 → compiler → external behavior. Full targeted closure is not established:
prewrite role/owner authorization, nullable input refinement, runtime N-day duration
conversion, conditional effect membership and secondary-created-image bindings remain.

Fresh exposed transfer retains **16/20 successes B01–B16**, **447 external
invocations**. B18/B19 remain structural; no new downstream stage or partial
benchmark success is claimed. B17/B20 remain disputed. R5.111 evidence/accounting,
prior first results, frozen requirements and generated artifacts remain preserved.

## Deliverables and evidence

| Deliverable | Location |
| --- | --- |
| Primary numeric, nullable presence, creation and historical authority | `docs/primary-value-interfaces-v1.md` |
| UTC-day representation and runtime interval conversion analysis | Same specification, UTC-day section |
| Primary field/context integration | `src/air_compiler/primary_interfaces.py`, `mutable_values.py`, `input_values.py` |
| Explicit actor transport, numeric validation and persistence | `mutable_runtime.py`, `reference_runtime.py` |
| Same-primary coupled creation/history composition | `atomic_state.py`, `atomic_state_runtime.py` |
| Closed FRC/producer shapes and generic BDI authority | `src/lykoi_workspace/primary_schema.py`, `mutable_schema.py`, `reference_schema.py`; `src/lykoi_pipeline/mutable_profile.py` |
| Five-domain full normal-path synthetic authority/plans | `src/lykoi_workspace/primary_corpus.py` |
| Adversarial/reconciliation/V1/rollback/reload verification | `tests/test_primary_interfaces.py` |
| Verification receipts | `R5_112-GENERIC-VERIFICATION.json`, `R5_112-CHECK-*.json` |
| Published synthetic external pipelines | `R5_112-SYNTHETIC-EVIDENCE.json` |
| Exact kernel reconciliation | `R5_112-KERNEL-ACCOUNTING.json` |
| Pre-transfer content lock | `R5_112-GENERIC-LOCK.json` |
| All twenty fixed fresh source captures/plans | `R5_112-Bxx-CANDIDATE.json`, `R5_112-CORPUS-LOCK.json` |
| Native stages, before/after blockers and external behavior | `R5_112-Bxx-RESULT.json`, `R5_112-TRANSFER-EVIDENCE.json`, `R5_112-COMPARISON.json` |
| Updated transfer matrix | [R5.112 capability matrix](R5_112-CAPABILITY-MATRIX.md) |
| History/content/scope/whitespace audit | `R5_112-FINAL-AUDIT.json` |

## Implemented behavior

### Primary numeric state

Normal primary integer fields use the same signed-64 domain as R5.111 related
fields. Primary literal/runtime creation, presence-aware replacement, computed
reference-operation mutation, checked addition, migration, persistence/reload and
typed null selection execute. Bounds reject bool-as-int, integral floats, strings
and arbitrary host integers; checked arithmetic rejects overflow atomically.

Nullable inputs distinguish omission, null and supplied integer. Synthetic quantity
creates at 0 but migrates at 10; nullable limit creates at 7 on omission but migrates
at null. Explicit creation null remains null. Mutation null clears; omission preserves
and performs no write/history append. Creation defaults never authorize migration.
No implicit null-as-zero refinement or arbitrary computed legacy creation was added.

### UTC-day conversion

The exact admitted conversion is an absolute Gregorian UTC date, strict ASCII
`YYYY-MM-DD`, to its start-of-day instant `YYYY-MM-DDT00:00:00Z`. The typed parameter
adapter requires source/target, UTC timezone, midnight boundary, second precision
and reject policy. Invalid dates and datetime/offset spellings reject before effects.
This is an explicit K15 instant representation/profile integration, not K25 displacement
or a new calendar operation. Leap-date/rejection vectors and external reload verify it.

**B19's N-day interval is different.** Runtime integer-to-dimensioned-duration scaling
is not defined by K24 addition or by finite map alone. A bounded graph with literal
86400 cannot express arbitrary runtime scaling merely by repeated addition. The
specification records the exact dimensional pressure; no multiplication primitive or
hidden backend coercion is admitted. A dimensioned representation/refinement deserves
composition-first investigation before any new core candidate is proposed.

### Actor and history

An explicit supplied actor is a nominal typed primary operation-context parameter.
Normal legacy primary creation, transition and mutable-value operations inherit it
into coupled history. Missing or malformed actors reject; separately declared history
reference integrity rejects unknown actors without committing primary changes.
No owner, related entity, system user or authenticated identity is substituted.

This is parameter binding, not authentication/authorization. Commit-time history
integrity does not implement required prewrite error precedence or role/owner checks,
especially on primary creation. Authenticated/request-context adapters and historical
non-system role assignment are not inferred. These limitations keep B18 structural.

History remains ordinary typed append-only durable state. `cardinality` of the explicit
entire operation-before history binds a value; K24 adds the explicit offset one.
Primary mutation and actor-bound numeric history commit together. Cardinality does not
observe earlier creations in the private candidate. Imported/deleted arbitrary history,
max+1 and distributed sequence allocation are not silently substituted.

### Same-primary successor

The existing atomic creation frame now admits the primary entity as a creation target.
Complete typed bindings explicitly copy primary after fields, bind nominal source-record
identities, supply successor identity, and observe declared clock resources. No implicit
clone, field defaults, lifecycle reset, ambient IDs or repeated resource sampling.
Primary validation and reference integrity apply to the final candidate. Duplicate
successor, overflow, invalid input and injected persistence failure preserve store bytes.

The synthetic operation unconditionally creates one same-type successor. It does not
prove conditional recurrence membership or provide a named secondary-created image
to another effect. Those interfaces are distinct B19 residuals. Ordinary creation,
resource/binding authority and existing atomic commit remain sufficient core meanings
for the implemented successor family; no RecurringTask or Event concept is added.

## Verification and chronology

**389 passing tests**, canonical model validation and safety. All R5.111 regression
commands rerun on the final source/test tree; three new tests include five complete
synthetic pipelines, source-inventory reconciliation, structural/V1 loss, missing BDI
authority, failed persistence and corrupted primary reload. Numeric/null/migration,
actor source, ordinal domain, successor provenance and effect membership mutations
are rejected. Existing compiler/application/reference/history/computation/query/value/
workspace/controller/FRC/BDI/adequacy/V1/external-baseline suites remain passing.

| Synthetic domain | Published external invocations |
| --- | ---: |
| Inventory | 23 |
| Document | 23 |
| Account | 23 |
| Session | 23 |
| Renewal | 23 |
| **Total** | **115** |

Each includes migrated/reloaded primary integers, null/default distinctions, missing
actor, unknown actor rollback, bad integer/overflow, duplicate successor rollback,
primary-context transition/history, absolute UTC-day decoding and typed null query.
Controlled host subprocess corruption/persistence probes are additional test evidence,
not added to the published 115. Domains share a generic schema shape; names alone do
not establish independent domain generality. Captures, source inventories and literal
plans use the same agent and synthetic approval; they are not held-out evaluation.

Pre-lock diagnostics found a missing explicit query identity tie-breaker in the new
synthetic plan; it was fixed before verification. Two focused test commands exceeded
their tool timeout; final cached-fixture tests completed. The full verification driver
also timed out; exact source-bound completed receipts were resumed, with every suite
counted once. Generic publication first required the repository root in `PYTHONPATH`;
the invocation was corrected before publication/lock, without product changes.

Published generic evidence and exact accounting preceded the content lock. Twenty fresh
source captures/plans were then fixed before the first transfer outcome. Transfer timed
out after B13 and resumed exact locked bytes. No product, spec, tests, candidates or
oracles were repaired after outcomes. Final checks bind historical records, generic
implementation, verification, synthetic evidence, accounting and corpus candidates.

## Before/after blockers

| Case | R5.111 first blocker | R5.112 first blocker | Change inside structural boundary |
| --- | --- | --- | --- |
| B01–B16 | Success | Success | All 16 freshly externally verified |
| B17 | Disputed formalization | Disputed formalization | Non-system historical role unanswered |
| B18 | Structural primary-history/actor interfaces | Structural primary actor authorization | Six numeric-history operations and actor parameters now represented; one unsupported authorization demand remains |
| B19 | Structural primary numeric/day/successor/actor interfaces | Structural authorization and recurring successor effect integration | Nullable recurrence field/migration now represented; conditional duration/refinement/effect/image interfaces remain |
| B20 | Disputed formalization | Disputed formalization | Unknown-member error unanswered |

B18's native unsupported obligation is `B18/primary_actor_authorization`.
B19's are `B19/primary_actor_authorization` and
`B19/recurring_successor_effect_integration`. Their projections have no generic
profile validation failure (`reason:null`): these are explicit unrepresented source
demands, not malformed candidate repairs. Neither reaches BDI, adequacy, V1, authoring,
compilation or behavioral verification. Structural diagnostic progress is not downstream
stage progress, and the **16/20** denominator is exposed requirement-local evidence.

## Kernel accounting

Exact preserved R5.111 baseline is **25**: its 23 baseline concepts plus K24 checked
addition and K25 fixed-duration displacement. **Zero new core candidates admitted.**
Primary numeric/null/context and UTC-day lexical representation are profile/interface
integration; history ordinals and same-type successor effects are existing-core
composition; host validation/private candidates are backend implementation. Runtime
duration scaling is documented unsupported pressure, not a silently counted adapter.
No unrestricted expression language, benchmark-specific dispatch/primitives or new
benchmark infrastructure was implemented.

## Completion answers

1. **Yes for admitted primary integer/nullable paths:** literal/runtime creation,
   replacement, computed primary mutation, persistence, migration and query. Nullable
   arithmetic refinement and computed legacy creation remain explicit limits.
2. **Yes for absolute UTC-day → midnight instant**, exact policy declared. Runtime
   N-day interval conversion remains unsupported and is separately analyzed.
3. **Yes for an explicitly supplied primary actor parameter.** Authentication and
   prewrite role/owner authorization are separate, unclosed authorities.
4. **Yes:** declared pre-operation history cardinality plus offset, coupled atomically
   in the supported cooperating one-store append-only frame.
5. **Yes for complete unconditional same-primary successor creation by composition.**
   Conditional effects and secondary-created-image consumers remain unclosed.
6. **B18 improves structural representation, but neither advances stages nor succeeds.**
7. **B19 improves structural representation, but neither advances stages nor succeeds.**
8. **16/20**, B01–B16; 447 fresh exposed external invocations.
9. **Yes, 25.** Existing K24/K25 meanings preserved; no new core candidate admitted.
10. **Remaining gaps:** primary prewrite actor existence/role/owner authorization,
    historical role authority, nullable numeric input refinement, runtime duration
    conversion, conditional atomic membership, secondary-created-image references,
    computed legacy primary creation; inherited broad timestamp and standalone untyped
    query integer compatibility leaks and cooperating one-store limits remain.
11. **Yes, B17/B20 remain disputed.**
12. **Recommend R5.113 target source-authorized prewrite context/permission composition
    and conditional typed effect/image bindings, with a separate dimensioned-duration
    conversion investigation.** Resolve migration/error authority explicitly; lock
    synthetic generic evidence before transfer and account for any actual new meaning.
13. **Yes:** benchmark-specific primitives and infrastructure work were avoided.

**Stop after R5.112.** The central question has a bounded positive answer for primary
numeric state, actor-attributed history and unconditional same-entity successors in
the 25-concept kernel. The complete targeted primary interface family remains partial;
`R5_112_PRIMARY_INTERFACE_COMPOSITION_CLOSED` is not justified.
