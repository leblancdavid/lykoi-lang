# R5.39 — Refinement dependency and whole-contract boundary closure review

**Result: `R5_39_WHOLE_CONTRACT_BOUNDARY_PARTIAL`.** The redundant-guard defect
is repaired, and the known capability classes are independently integrated through
the existing current pipeline. A versioned seed bank forms one checked aggregate
boundary and executes a real public lifecycle. The saved frozen B02 contract is
still **NOT_READY**: concrete profiles and coverage declarations are absent.
Independent capability support does not supply those declarations.

**No comprehensive B02 evaluation is recommended.** Candidate core **30**, new
core **0**, no #31. No B02 generation, execution or frozen acceptance. No post-static
implementation repair. Phase 5C remains paused; B03 prospectively unchanged;
B17 unexposed. Historical R5.38 evidence is preserved.

## 1. R5.38 defect reconstruction

[Minimal reconstruction](R5_39-refinement-reconstruction.json) loads the immutable
R5.38 analyzer at `4dc980f`. Nine contracts exercise optional, nullable and combined
instant domains, each under three placements of equivalent guards and a dependent
`before` predicate, embedded in selected chronological ordering. All nine historical
CheckedPlans reject with `compiler internal consistency failure: ordering refinement`;
all nine current plans form. The pre-R5.38 optional analyzer at `428a340` accepts
the three optional-only examples.

The minimal patterns are `G,G,P`, `G,P,G`, `P,G,G`, with `G = present(x)` or
existing negated equality to correctly typed null. The conjunction itself types;
selected ordering exposes the checked dependency/scope invariant failure.

## 2. Refinement dependency analysis

Conjunction scope collection overwrote equivalent providers in a one-provider
dictionary, while ordering retained all source providers. The overwritten relation
then failed scope ownership. This is provider-multiplicity bookkeeping inconsistency,
not a new ordering relation, contradictory semantic fact or change to optional/
nullable meaning.

## 3. Canonical refinement facts

`CheckedPlan.refinement_facts` records one fact per value/kind/positive scope,
declared/effective types and every stable source justification. Optional presence
and nullable non-nullness remain independent. Singleton selection guards use the
same representation. Sealing and invariants check fact/provider correspondence.

## 4. Provider multiplicity

Source relations are preserved. Active operand dependencies retain the complete
justification set; ordering dependencies now agree with scope ownership. Checked
scheduling evaluates membership before non-nullness before consumers. No procedural
"first guard wins" rule; stable document paths preserve provenance.

## 5. Conflict handling

Only correctly typed membership or existing negated typed-null equality establishes
refinement. Wrong fields, bindings, state sides, negative scopes and other predicates
are not equivalent. Positive non-nullness plus the opposite typed-null equality
consumer rejects as an equality-domain mismatch. General satisfiability checking
is not claimed: `present(x) AND NOT present(x)` may safely denote false, rather
than a reachable contradictory value.

## 6. Serialization independence

Permanent regression generates the three guard placements with actual absent/null
populations and independent semantic grounding. Optional and nullable `G,G,P`
conjunctions validate equivalently; serialized order does not determine safety.

## 7. Mixed optional/nullable refinement

For `optional<nullable<instant>>`, duplicate presence only, duplicate non-nullness
only and duplicate both are each exercised in three placements. Including the
optional-only/nullable-only cases, this regression produces **15 grounded conformant
calls**. Both independent facts remain necessary; duplicating one cannot supply
the other.

## 8. Refinement regression and faults

Missing, wrong-field, escaped-scope and opposite typed-null assumptions reject
unsafe consumers. Duplicate providers remain valid. Altered justification facts
break the seal. Existing optional/current-authority regressions, including the
37 R5.25–R5.31 tests, pass. Neither emitter nor semantic verifier adds a duplicate
special case: both consume corrected authoritative dependencies.

## 9. Nullable public input model

| Raw observation | Required nullable | Optional nullable |
| --- | --- | --- |
| Omitted key | `missing_required` | Omitted slot/absent typed field |
| Explicit JSON null | Supplied typed null | Supplied typed null |
| Valid non-null raw T | Existing decoder → T | Existing decoder → T |
| Malformed non-null raw T | Binding failure | Binding failure |

JSON token `null` is the declared null representation. Nullable CLI arguments
require JSON representation; string values are quoted JSON. Omission is never null.

## 10. Nullable decoder composition

The R5.32 decoder composes nullable with its existing scalar decoder. Non-null
values must pass the base decoder, preserving integer conversion and instant/
string/Boolean validity. The independent public oracle does not call production
binding. No invalid T is created or silently converted to null.

## 11. Optional-nullable and collection binding

Required/optional nullable string, integer and instant probes distinguish all four
states. Existing R5.35 per-element collection binding accepts nullable scalar
elements: `[null,"3"]` becomes `[null,3]`; malformed elements fail with an index
and no typed invocation. Optional element sentinels/nested collections are not
added. Whole-boundary subprocesses exercise optional nullable harvest instants and
query integers with omission, null, valid value and malformed value.

## 12. Nullable binding evidence and faults A–D

[Disposable public fault evidence](R5_39-boundary-fault-evidence.json): A reports
null as omitted; B reports malformed integer as null; C reports valid integer as
null; D accepts null as a non-nullable string. Independent input binding fails
conformance in each case. D declares JSON representation for the non-nullable
argument so the observed raw input really is null; generated typed invocation
also rejects. Honest artifact resealing does not make incorrect binding conformant.

## 13. State-alternative dispatch model

Profiles link registered state names, exact codecs, content predicates and initial
values. Complete persistence decoding produces exactly one alternative name;
zero/ambiguous matches reject. Transport consumes that checked name to select a
route, without application-specific JSON version logic. This is infrastructure
metadata over existing state types, not a core union.

## 14. Operation applicability

Each public route declares available alternatives. Each mapping must match its
CheckedPlan pre-state codec and registered post-state alternatives. Every plan
needs public input/output coverage. An unavailable alternative rejects before
semantic invocation. Generated semantic `requires` remains separate: an available
route can still receive an invocation rejection, not an invented typed outcome.

## 15. Independent versioned application dispatch

The seed-bank V1/V2 envelopes differ in required seed storage. Public `create`,
`query`, `early` use version-specific plans; `migrate` is V1→V2 only. Migration
uses existing defaults, target equality and cardinality. V1 create/query, migration,
V2 query/create and refined chronological ordering execute through generic
infrastructure. Repeating migrate in V2 rejects with no semantic event.

## 16. Dispatch faults E–H

E dispatches V2 using V1; F makes V1 available in V2; G substitutes a query for
migration; H substitutes the V2 codec under V1. Static profile validation rejects
incompatible codec/contract combinations. Disposable resealed substitutions are
also rejected by independent aggregate reconstruction before trusted semantic
conformance. Resealing a changed declaration does not make it authoritative.

## 17. Durable validation model

Bytes → parse → complete recursive codec → declared content constraints → unique
typed alternative → dispatch → generated invocation. Supported declarations are
existing typed discriminator equality and population checks for declared string
identity uniqueness, nonblank fields and finite typed domains. New constraint
kinds reject for separate review. No inferred application invariant is invented.

## 18. Population/content validation

Valid empty/populated states execute. Seven invalid fixtures cover wrong element
shape, wrong field type, V2 envelope/V1 content, incompatible row type, blank
content, outside-domain storage and duplicate identity. All reject as
`persistence_invalid_state`. Permanent tests also exercise invalid JSON and
required-store absence.

## 19. Persistence failure behavior and faults I–L

All seven invalid populations preserve durable bytes and produce no semantic
event. Binding is not reached because typed state selection precedes
alternative-specific binding. I accepts an invalid element; J accepts mismatched
version/content; K drops an invalid element; L supplies a missing field by rewriting
durable content. Independent persistence/grounding/output checks fail. K/L's physical
mutations are separately observed; semantic success cannot hide normalization.

Validation on **load** does not prove universal write preservation of arbitrary
profile predicates. Independent post-observation persistence/semantic checks remain
necessary. Existing direct writes have no established crash/concurrency guarantee.

## 20. Complete profile composition

R5.38 had absent saved-contract profiles as well as missing composition capabilities.
R5.39 independently implements nullable binding compatibility, typed alternative
dispatch, declared content validation and aggregation, supplying complete profiles
for the independent application. That does not populate B02's absent declarations
or prove its frozen public-format equivalence.

## 21. Aggregate boundary profile

One aggregate links application identity, CheckedPlan digests, artifact manifest,
transport, binding, state/persistence, launch, provider and trace/provenance.
[Schema](R5_39-aggregate-profile-schema.json) semantic identity:
`ada9895144e40390617357583cf17f2270e8327d172551fe4abdcf9b8b598fa3`.
The sole compiler remains `benchmark.semantic.current_pipeline`. Existing
same-shape profiles retain readiness-v2 support. The aggregate is not semantic source.

## 22. Cross-profile validation and faults M–P

Checks reject stale application/plan identity, missing input/output routes,
incompatible state codec, wrong launch transport/persistence reference, incompatible
capability provider and trace/artifact provenance. Permanent faults M–P cover
foreign transport revision, incompatible launch state reference, omitted V2 and
trace provenance mismatch. Runtime rejects altered aggregate links before trusted
execution. Hash consistency is revision integrity, not hostile-writer attestation.

## 23. Complete standalone application and lifecycle

[Evidence](R5_39-whole-boundary-evidence.json) records **14 public lifecycle calls**
plus **7 invalid populations** on one shared store. Sequence: missing-store query
without materialization; nullable V1 create/query; explicit integer; dated seed;
refined ordering; migration; V2 query/create; post-migration ordering; unavailable
migration; malformed nullable input; unknown route; invalid durable attempts;
final restored valid query. Eleven lifecycle calls reach semantics; three stop
at public boundaries. All reached normal/rejection layers conform.

[Source-only mutation](R5_39-semantic-mutation.json) changes migration storage
`dry`→`cold`, regenerates without compiler edits and conforms through the same
aggregate.

## 24. Layered grounding

Separate verdicts: `APPLICATION_PROFILE`, `LAUNCH`, `TRANSPORT`, `INPUT_BINDING`,
`STATE/PERSISTENCE`, `SEMANTIC_EXECUTION`, `OUTPUT`. Independent command/cwd/PID,
public output, evidence-file and pre/post byte observations challenge internal
reports. Persistence expectations do not call the production decoder. Semantic
verification uses original source/authoritative facts, not emitted algorithms.
Null verdicts mean unreached layers, never passing semantic execution.

## 25. Exact matrix and redundancy dimension

The **84-cell** model remains **64 supported / 20 rejected**. The **336 static
rows** preserve each original base/domain/relation cell under single-provider,
equivalent-duplicate, independent-required and conflicting dimensions. Applicability
is explicit: required non-null operands have no guard; both independent facts apply
to combined domains; opposite typed-null premises apply to nullable consumers.

[Transfer evidence](R5_39-domain-pipeline-evidence.json): baseline 64 accepted
cells/128 grounded conformant calls; duplicate-provider 64 accepted cells/128
grounded conformant calls. Each rejects 20 before generation. No claim that all
336 static rows or all attached boundary dimensions executed. Separate boundary
evidence is linked, not substituted for exact-cell execution.

## 26. Whole-contract readiness v2 and prediction

V2 preserves v1's complete source/domain scan, updates decoder domains, records
canonical provider facts and checks per-operation input, state codec, persistence,
transport/output, launch/provider and aggregate compatibility. Typed content
obligations require matching declarations; absent metadata rejects.

[Complete independent prediction](R5_39-independent-readiness.json): READY with
emission/rendering disabled, then successful public generation/execution.
[Deliberate incomplete fixture](R5_39-negative-readiness.json): NOT_READY, collecting
**seven findings** across binding, state, transport, launch and aggregate stages.
Only the READY application is generated/executed.

**Additional independent admission audit:** removing the optional `filter` mapping
from the V2 query is accepted by aggregate **compatibility** validation, while
readiness v2 correctly reports NOT_READY for incomplete input coverage. This
static non-task audit performs no generation or B02 analysis. Thus the aggregate
constructor is not itself a whole-contract completeness gate; callers must use
readiness v2. That remaining admission distinction warrants independent review
before claiming unconditional aggregate-boundary closure. It was observed after
lock/static comparison and is preserved without implementation repair.

## 27. Implementation lock

After implementation, independent evidence, verification and audit, **658 files**
are locked, including historical frozen evidence, implementation, tests/recorder,
matrix/schema and interface documentation. Repository state/hashes are recorded in
[the lock](R5_39-implementation-lock.json).

- HEAD: `4dc980f2365c3d546574d12db06321f0ee139c4f`.
- Lock: `b41816d614186319ba02564f2b3dcaec0f76a258c1913e33c643f89052f41fc4`.
- Matrix SHA-256: `b4f8dbfbab8d1fa5e89e29e2e71ee3e3dab58f5fdaa111368ed90d79a16d3f06`.
- Aggregate schema identity: `ada9895144e40390617357583cf17f2270e8327d172551fe4abdcf9b8b598fa3`.

Changes remain uncommitted. Final result/current-boundary prose is outside the byte
lock; implementation and evidence are not repaired after static comparison.

## 28. Single frozen B02 static pass

[Static result](R5_39-B02-static-readiness.json) reads R5.37's unchanged saved
document once after verified lock. Generation and unit rendering are disabled.
**15/15 CheckedPlans form; semantic-static READY; whole-contract NOT_READY.**
Before/after/final lock checks pass. Generated/executed false; acceptance absent.
The recorder refuses another static pass or replacement lock after this result.

## 29. Entire remaining B02 coverage set

| Finding | Stage | Concrete remaining obligation |
| --- | --- | --- |
| Complete transport specification missing | TRANSPORT | Public routes, binding/output mappings |
| Durable declaration missing | STATE/PERSISTENCE | Alternative codecs, constraints, initial policy |
| Launch configuration missing | LAUNCH | Compatible standalone profile |
| Aggregate boundary cannot form | APPLICATION_PROFILE | Complete linked profiles |
| Public state-alternative coverage missing | TRANSPORT | Required routing across alternatives |
| Population/content coverage missing | STATE/PERSISTENCE | Declared constraints/typed coverage references |

The nullable decoder capability finding is removed. Dispatch/content validation
are independently implemented capabilities, but concrete saved-contract coverage
is absent. These six records include dependent completeness findings: they are
not six distinct new core gaps or measured execution failures. No B02-specific
mapping is inferred from neighboring evidence; no later inspection/repair follows.

## 30. Retry decision and methodology assessment

**Do not recommend comprehensive B02 evaluation.** Every benchmark-critical
operation and boundary must be READY. Next bounded work should complete authored
boundary/typed-obligation coverage independently, before another separately locked,
authorized static comparison. Fixing one capability cannot authorize frozen execution.
The next independent review should also align aggregate admission with the
readiness completeness requirement for optional input mappings, rather than rely
on callers to perform the extra gate.

R5.36 coarse aggregation substituted optional evidence for nullable readiness.
R5.38 v1 introduced exact domains and the full known backlog, but missed provider
multiplicity and lacked boundary composition. R5.39 v2 retains exact domains,
challenges redundant providers, collects simultaneous incompatible profiles and
fails absent complete metadata. **Yes: independent gaps are now detected before
frozen generation.** This is methodological progress, not universal readiness.
Unrepresented natural-language obligations remain a limitation.

## 31. Construct/system accounting

| Category | Prospective change/count |
| --- | --- |
| Core semantics | 30 candidates; 0 new; no #31 |
| Type/refinement | 2 existing fact kinds; provider multiplicity generalized |
| CheckedPlan | 1 new sealed canonical fact field |
| Binding | 1 nullable composition over 4 scalar domains; existing per-element binding |
| State profiles | 1 profile version; 2 independent state alternatives |
| Persistence | 1 decoder module; 2 descriptor kinds: equality and population |
| Transport | 1 alternative-route composition; 0 application-specific algorithms |
| Launch | 1 aggregate-link preflight; 0 new launch/provider modes |
| Aggregate profiles | 1 schema linking 9 boundary components |
| Readiness | 1 v2 inspector; 84 preserved cells, 336 dimensional rows |
| Verification/evidence | 1 independent boundary verifier, 7 layers, 12 new tests, 12 public faults |

Six existing implementation modules edited; six prospective semantic-package
modules added (including study/fault utilities); one test module; one recorder.
These infrastructure counts are not new core constructs.

## 32. Verification and evidence integrity

[Verification](R5_39-verification.json): **372 harness discovered, 336 passed,
36 explicit restriction skips, zero failures/errors**; **31/31 application/compiler**;
**5/6 R5.37 integrity checks**, with its historical live-tree lock assertion skipped.
All **12 new tests** pass. Validation/safety pass (zero capability violations or
invalid transitions), diff check passes. The 36 skips preserve B02 rendering/retry
and nested frozen acceptance restrictions; no skipped acceptance is counted as a pass.

[Audit](R5_39-evidence-audit.json) validates reconstruction, matrix denominators,
byte preservation, fault detection, mutation, prediction and evidence hashes.
Recorder totals: **21 public lifecycle/invalid-population calls**, **12 public
fault calls**, **1 source-only mutation**, **256 grounded matrix calls**.
Regression/additional policy-test calls are separately counted test evidence.

Windows/Python 3.14.3/PowerShell 7; standard library only. An initial combined
evidence/verification command hit the 120-second tool timeout; the final complete
run used sufficient timeout and passed. LF→CRLF warnings do not fail diff checking.
No implementation/evidence repairs followed the static pass.

Ordinary reproduction:

```powershell
python -m unittest discover -s benchmark/harness -p test_boundary_closure_r5_39.py -v
python benchmark/results/phase5c/r5_39_review.py lock-check
git diff --check
```

Recorder collection modes document provenance; regenerating evidence changes the
lock. Ordinary checks must not repeat frozen static analysis. Interface:
[boundary-closure-r5.39.md](../../../docs/boundary-closure-r5.39.md).

Universal correctness NO; format globally UNFROZEN; R5.2.2 historical authority;
Phase 5C paused; B03 prospectively untouched; B17 unexposed/unclassified.

R5_39_WHOLE_CONTRACT_BOUNDARY_PARTIAL
