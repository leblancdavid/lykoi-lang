# R5.110 — Atomic effect composition and durable audit history

**Final classification: `R5_110_ATOMIC_DURABLE_HISTORY_IMPLEMENTED_BY_COMPOSITION`.**

The bounded family executes as ordinary typed durable record creation coupled to
an existing primary mutation under one existing local atomic commit. No Event,
AuditEvent, Log, Sequence, Transaction or Effect core primitive was added.
The exact inherited **23-concept proposed kernel remains 23**.

This classification applies to explicitly authorized typed records, local coupled
writes and ordered history. **Numeric sequence generation is not implemented.**
B18's complete numeric/actor contract does not pass merely because ordered history
now works. Fresh exposed transfer retains **16/20 successes, B01–B16**, with no
newly reached downstream request stages. B18 now halts at **structural coverage**
on numeric-history state and inherited primary actor binding, replacing the old
external-effect BDI diagnosis prospectively. B17/B20 remain disputed; B19 remains
structural. All earlier results, including B03's first result, are preserved.

## Deliverables and evidence

| Deliverable | Location |
| --- | --- |
| Semantic specification, exact pre-round 23, sequence/ordering/immutability analysis | `docs/atomic-durable-history-v1.md` |
| Typed record model and coupled-creation validation | `src/air_compiler/atomic_state.py` |
| Closed FRC producer relations | `src/lykoi_workspace/atomic_state_schema.py`, `mutable_schema.py` |
| FRC/structural coverage, BDI/adequacy, faithful normal V1 | `src/lykoi_pipeline/mutable_profile.py` |
| Normal compiler dispatcher/lowering | `src/air_compiler/profiles.py` |
| Private candidate, shared declared resources, persistence/rollback and migration | `src/air_compiler/atomic_state_runtime.py` |
| Existing CollectionQuery occurrence-order interface | `collection_query.py`, `predicate_integration.py` |
| Five-domain typed source corpus and literal external plans | `src/lykoi_workspace/atomic_state_corpus.py` |
| Generic, adversarial, authority and external rollback/clock tests | `tests/test_atomic_state.py` |
| Existing and new regression receipts | `R5_110-GENERIC-VERIFICATION.json`, `R5_110-CHECK-*.json` |
| Published external normal-pipeline behavior | `R5_110-SYNTHETIC-EVIDENCE.json` |
| Kernel pressure/accounting | `R5_110-KERNEL-ACCOUNTING.json` |
| Pre-transfer generic content lock | `R5_110-GENERIC-LOCK.json` |
| Fresh twenty-case source captures and fixed plans | `R5_110-Bxx-CANDIDATE.json`, `R5_110-CORPUS-LOCK.json` |
| Stage/native outcomes and comparison | `R5_110-Bxx-RESULT.json`, `R5_110-COMPARISON.json`, `R5_110-TRANSFER-EVIDENCE.json` |
| Transfer matrix | [R5.110 capability matrix](R5_110-CAPABILITY-MATRIX.md) |
| Final pins, kernel, whitespace and scope checks | `R5_110-FINAL-AUDIT.json` |
| Direction, observations and tradeoffs | Overview, decisions, research log, workflow, README and AGENTS |

## Semantic findings

### History is state

History rows are ordinary related record entities with nominal identity and an
ordinary durable ordered collection. Their schemas have only source-authorized
typed fields. Payload sources are literal, existing primary input, before/after
field, or declared capability. There is no untyped JSON payload or logging adapter.
Record creation reuses the existing identity/type/uniqueness constraints. Historical
subject identities can survive deletion only under an explicit unchecked/permit
reference authority; no hidden target deletion rule is invented.

The generic operation contract names an existing primary write and one to eight
secondary creations. The primary implementation builds its usual candidate. Before
the existing commit publishes it, the composition resolves the declared resource
observations and complete typed secondary records in a private candidate. The
ordinary reference backend validates the complete combined state and performs one
atomic file replacement. No intermediate primary-only/history-only state is exposed.

The frame covers primary creation, guarded transition, typed mutation, related
creation/update and deletion interfaces; generic fixtures exercise existing primary
creation/transition/deletion plus related primary updates. It is not an arbitrary
program of multiple updates or a distributed transaction.

### Failure and observation

Input/lookup/guard failures create no secondary records. Primary rejection, secondary
typed rejection, duplicate identity (including a later secondary creation), reference
validation and supported replacement failure leave persisted bytes unchanged.
Controlled failure probes execute generated code in separate processes and inspect
the store from the test process. Reload queries verify both primary and history state.
The existing exclusive reservation surrounds cooperating CLI read/check/write.
Direct host API tests run without competing writers; no concurrent host API guarantee,
crash recovery or hostile/out-of-band writer isolation is claimed.

History creation occurrence order is explicit, stored and observable on reads.
Internal primary/secondary evaluation is not independently observable before commit.
One declaration's finite creation sequence can append multiple records; duplicate
identity errors reject all of them and the primary candidate. Append-only history
uses a closed exposed operation interface: standalone create/update/delete on the
declared history entities is refused; only coupled creation and reads are available.
It does not protect files against out-of-band modification.

### Ordering is distinct from sequence values

Occurrence-order queries reuse stable selection over the durable finite sequence.
The selected composition permits explicit `ordering:[]`; other normal profiles
retain their existing deterministic key requirements. Timestamp/ID ordering reuses
parsed timestamp ordering and unique tie-break keys. Controlled reversed-time records
distinguish occurrence order from key order after reload.

A numeric monotonic value is an additional observable requirement. No backend
`max+1` or counter increment was introduced. Cardinality of an append-only candidate
prefix can conceptually supply an ordinal without arithmetic, if source authority
permits that policy. But the current normal durable-value profile does not provide
integer fields or cardinality as a typed value source. Exact successor of an arbitrary
counter/max would require computation absent from the current kernel. Thus the
finding is **not “all numeric sequencing inherently requires arithmetic”**; it is
that this round implements neither the missing normal value binding nor an invented
successor rule. B18 says monotonic sequence, not `max+1`, and remains unsupported.

### Clock and identity authority

Every clock/identity observation binds an existing declared capability. Sampling is
once per capability per operation, shared with primary creation. A controlled primary
creation probe observes the clock exactly once and verifies identical primary and
history timestamps. Multiple secondary records share one clock observation. Resource
provider output is checked before persistence; no ambient clock is implicitly bound.
Supplied record and actor identities remain typed values; generated IDs use only
declared UUID capabilities. An actor's identity does not itself prove authorization.

### Normal requirements path

The FRC facet separates primary command/entity/input authority, secondary record
bindings, success-only cardinality, resource sampling, occurrence ordering, queries,
append-only restriction and atomic frame. Complete structural recomputation checks
each selected facet. Existing reconciliation compares source-side typed relations;
material omission, duplication, wrong subject/action/clock/payload, failure-only
creation, removed atomicity and changed ordering are rejected or disputed.
Normal V1 retains source contract and recomputed facts; recovery detects removed
secondary creations, changed payload/frame/resource/query order.

BDI exposes finite general choices for operation creation content/cardinality,
success/failure trigger, sampling/order/resources, coupled commit, query selection
and write restriction. Existing adequacy rejects removed determined decision
authority. No historical BDI engine or `external_effect` rule is rewritten. Missing
required record fields, error/source bindings or sequence authority are not supplied
by conventional audit-log practice.

## Verification and chronology

**379/379 tests pass**, plus canonical validation and safety. Existing reference,
predicate/interface/value, query, compiler/application, workspace/controller/pipeline,
formal-requirement, BDI/adequacy, V1, coverage and external baseline suites are included.
Per-command receipts bind the exact source/test tree; partial earlier runs are not
added to the denominator.

| Domain | Public external invocations | Primary effect / history order |
| --- | ---: | --- |
| Inventory | 21 | Named stock-band label change; occurrence order |
| Account | 21 | Status label change; timestamp + ID |
| Document | 21 | Ownership label change; occurrence order |
| Deployment | 21 | Deployment-state label change; timestamp + ID |
| Synthetic ledger | 21 | Status label change; occurrence order |
| **Total** | **105** | All five full normal pipelines verify |

These fixtures deliberately use bounded typed state, not numeric stock/balance
calculation or full domain authorization. Additional tests externally verify
controlled clocks, two compiled secondary creations, later-effect duplicate rollback,
injected persistence failure, invalid secondary values, rejected primary lookups,
history-query bytes, unavailable history edit/delete commands and explicit empty
history migration. Primary create/advance/delete are exercised in all five domains.

The first focused run found a synthetic delete binding to a command the scalar
fixture did not expose. The fixture was corrected to ordinary reference deletion
before verification/lock. A 200-second focused-test timeout was rerun with a larger
ordinary test timeout and passed. The first evidence launch lacked repo root in
PYTHONPATH; it produced no evidence, and the compatible `src;.` environment succeeded.
No product change occurred after generic verification, lock or transfer outcomes.

The generic lock pins source, tests, canonical model, specification and evidence
runners, as well as historical results/requirements/generated artifacts. It was
published after verification, five-domain behavior and kernel accounting and before
all fixed transfer captures/outcomes. All twenty transfer captures/oracles were
locked before the first terminal result. No product, saved candidate or oracle repair
followed an outcome.

Same-agent source captures, inventories, literal plans and synthetic owner approvals
remain evidence limits. External subprocess observations verify generated behavior,
not independent cognition or general English formalization accuracy. Repeated exposed
corpus success is regression evidence, not held-out generalization or cumulative
historical benchmark achievement.

## Frozen exposed transfer

| Outcome | R5.109 | R5.110 |
| --- | ---: | ---: |
| Behavioral success | 16 | **16** |
| Structural halt | 1 | **2** |
| BDI halt | 1 | **0** |
| Clarification/dispute | 2 | **2** |

There are **447 external transfer invocations** for B01–B16. B18's fresh source
capture retains the required actor and integer sequence, success-only cardinality,
atomic coupling, migration initialization, operation/task/time content and sequence
query order. It no longer classifies this internal durable state as an external
effect. Coverage rejects exactly `B18/numeric_history_state` and
`B18/primary_actor_binding`. No B18 BDI/adequacy/authoring/external behavior is reached;
this is a more precise prospective blocker diagnosis, **not stage progress or success**.
Generic related-operation actor inputs do not close inherited B17 actor parameters
on existing primary commands. B17's existing non-system migration role remains
unanswered; B20's unknown-member error remains unanswered. B19 arithmetic/temporal
successor construction stays unimplemented and structurally unsupported.

## Kernel pressure and final answers

Existing K01–06/K21 model typed history; K03 models creation occurrence order;
K10/K16 model queries/key ordering; K04/K15/K20 bind resources; K14/K17/K22 couple
writes; K17 restricts exposed history mutation. The FRC/profile interfaces compose
these meanings. Private candidates/cache/envelope are backend implementation details.
No irreducible event, ordered-effect or transaction meaning is established in the
bounded family. The proposed architectural count remains **23**, not a minimality proof.

1. **Yes:** history is ordinary typed durable state.
2. **Yes:** a primary mutation and bounded secondary creations share one local atomic frame.
3. **Yes:** finite occurrence order and existing timestamp/ID key policies suffice.
4. **Policy-dependent:** cardinality-derived ordinals may compose existing concepts; arbitrary counter/max successor needs arithmetic. Numeric generation is not implemented here.
5. **Yes:** declared clock capabilities supply one shared operation observation.
6. **Yes:** existing CollectionQuery reads/filtering/order operate on the history collection.
7. **Yes:** append-only behavior follows closed mutation authority plus coupled creation contracts.
8. **Decisions:** required content/cardinality, success trigger, coupling/failure, ordering, resource binding/sampling, payload sources, selection and mutation restriction.
9. **No new core primitive admitted.**
10. **23** after R5.110, preserving R5.109 exactly.
11. **Yes:** the bounded typed family compiles/executes through the normal pipeline.
12. **16/20**, B01–B16, requirement-local exposed behavioral success.
13. **B18 does not succeed or reach a new downstream stage:** its diagnosis changes from external-effect BDI to precise residual structural demands.
14. **Residual boundaries:** normal integer/cardinality-value binding and inherited primary actor-parameter/authorization composition; arbitrary numeric successor remains computationally unsupported.
15. **Yes:** B17/B20 ambiguity is preserved.
16. **Yes:** B19 is outside implemented scope.
17. Recommend R5.111 investigate source-authorized **typed numeric/cardinality-value composition and its arithmetic boundary**, with primary actor binding/authorization closure tracked explicitly. Do not assume temporal successor work is authorized by this recommendation.
18. **No benchmark-specific primitive.** Product dispatch depends only on declared typed profiles.
19. **Infrastructure work avoided.**

**Stop after R5.110.** No R5.111, arithmetic/B19, external network, event sourcing,
unrestricted aggregates, distributed transaction or infrastructure implementation began.
