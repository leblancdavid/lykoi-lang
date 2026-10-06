# R5.104 — Typed mutable values and write transformations

**Final classification: `R5_104_TYPED_MUTABLE_VALUES_IMPLEMENTED`.**

The bounded generic family traverses the normal human-source → captured typed
FRC → source-only inventory/reconciliation → synthetic owner seal → structural
coverage → BDI/adequacy → faithful normal V1 → restricted author → normal compiler
→ external behavior path on four synthetic domains. **340/340 current tests pass**;
the published generic corpus passes **96 external CLI invocations**. The frozen
exposed transfer has **6 successes / 11 structural / 1 BDI / 2 clarification**,
with **121 external CLI invocations** across its six successful local cases.

This is bounded implementation and exposed development/regression evidence,
**not held-out generalization, cumulative Phase 5C achievement, live natural-language
formalization accuracy or full normal-profile closure**. R5.103 remains the preserved
pre-R5.104 current-system baseline. R5.97's immutable B03 first result is unchanged.

## Deliverables and reproducibility

| Deliverable | Implementation/evidence |
| --- | --- |
| Versioned types, collection policy, presence, pipeline and storage semantics | [Typed mutable values 1](../../../docs/typed-mutable-values-v1.md) |
| Closed typed producer/FRC relations | `src/lykoi_workspace/mutable_schema.py` and normal adapter schema/guidance |
| Source reconciliation, complete structural facets, BDI/adequacy, faithful normal V1 | `src/lykoi_pipeline/mutable_profile.py`, normal workspace/contracts integration |
| Deterministic semantic validation/IR composition | `src/air_compiler/mutable_values.py` |
| Normal backend, atomic writes, migration/reload and same-state queries | `src/air_compiler/profiles.py`, `mutable_runtime.py`, bounded query dispatcher |
| Source-first article/contact/product/profile captures and literal external plans | `src/lykoi_workspace/mutable_corpus.py` |
| Semantic, FRC/reconciliation, coverage, BDI/adequacy, V1, backend, migration/failure and composition challenges | `tests/test_mutable_values.py` (12 tests, with multiple material corruptions/observations per test) |
| Full synthetic source/inventory/controller/native/external audits | [Synthetic evidence](R5_104-SYNTHETIC-EVIDENCE.json) |
| Passing pre-transfer checks | [Final generic verification](R5_104-GENERIC-FINAL-VERIFICATION.json), 340 tests; initial [339-test check](R5_104-GENERIC-VERIFICATION.json) retained |
| Generic implementation/spec/test/history content lock | [Generic lock](R5_104-GENERIC-LOCK.json) |
| Twenty exact source-bound captures and preauthor plans | `R5_104-B01-CANDIDATE.json` through `R5_104-B20-CANDIDATE.json` |
| All captures/plans fixed before the first transfer outcome | [Corpus lock](R5_104-CORPUS-LOCK.json) |
| Full twenty-case native transfer evidence | [Transfer evidence](R5_104-TRANSFER-EVIDENCE.json) |
| Before/after blockers, all stages, next native blockers | [Matrix](R5_104-CAPABILITY-MATRIX.md), [machine comparison](R5_104-COMPARISON.json) |
| Preservation, final whitespace/scope/content audit | `R5_104-FINAL-AUDIT.json` |

Evidence scripts use exclusive output creation and refuse overwriting published
records. With PowerShell, `PYTHONPATH='src;.'` supplies both normal code and the
existing benchmark semantic-analysis package. Ordinary checks can be repeated
under a new result label:

```powershell
$env:PYTHONPATH='src;.'
python benchmark/results/phase5c/R5_104-verify.py RECHECK
```

`R5_104-generic.py` publishes the synthetic audit and implementation lock only
after the passing final generic check. `R5_104-transfer.py` compares that lock
before and after the twenty attempts, fixes every capture/plan first, then
publishes the complete transfer/matrix. Repeat publication requires a disposable
output location. No implementation, test or semantic-spec repair followed any
individual transfer outcome.

## General composable semantics

- **Typed values:** existing writable string/identifier/enum/timestamp values;
  collections of nonnullable supported scalars with explicit enum domains.
  Existing timestamp nullability remains the only nullable value support.
- **Independent policies:** insertion order, allow/unique duplicates and exact
  case-sensitive scalar equality are distinct typed relations. Empty arrays are
  valid; persistence is ordered JSON arrays. Timestamp equality compares exact
  representations, not normalized instants.
- **Distinct writes:** scalar/collection `replace`, occurrence-preserving
  `append` on duplicate-permitted fields, and `add_unique` on a declared typed
  collection. Unique policy validates; it never supplies implicit dedup authority.
- **Transformations:** explicit verbatim/trim/stable-first-dedup steps and bounded
  element-pipeline mapping. Stable dedup preserves relative order and case
  distinction. Scalar transforms are composable inside an element pipeline.
- **Stage semantics:** ordered transform/validate steps, raw-shape checks, exact
  error identities and final typed-value validation. Trim→nonempty differs
  externally from nonempty→trim on raw whitespace.
- **Presence:** mapping membership distinguishes omitted from supplied empty,
  empty collection and permitted explicit timestamp null. Updates declare
  unchanged/reject omission and separate missing/invalid/stage errors.
- **Atomicity:** prepare all field changes privately, validate the staged store,
  atomically replace one persisted store and return only after success. Validation
  or supported persistence failure exposes no partially transformed record.
- **Evolution/composition:** separate explicit historical defaults, additive
  migration/idempotence and preserved prior scalar authority; one actual model
  state can feed unchanged CollectionQuery membership/equality behavior and
  independent lifecycle operations.

The typed extended model is an additive normal compiler IR, **not** an assertion
that the historical v0.3 validator accepts `value_collection` nodes. The compiler
validates its scalar component and recomputes the typed extension before emitting
the self-contained runtime. This keeps the historical serialized language, runtime
template, generator, canonical model and generated application intact. New product
modules contain no benchmark IDs, task-field primitives or source-word dispatch.

## Authority and fail-closed behavior

All normal FRC envelopes retain exact source quotes and obligation IDs. Closed
typed relations can reconcile distinct display descriptions only when their
semantic values agree. Source-side domain/authority disagreement, invented trim
or duplicate policies, missing material facets and extra unsupported obligations
refuse automatic progress. Tests directly dispute invented transformation/duplicate
facts against the unchanged source-side interpretation.

Structural facets preserve value/collection mutation, presence, pipelines,
validation stages and atomic effects. Coverage recomputes the entire typed model
and projection, so omission/tampering cannot make an incomplete operation complete.
Prospective BDI decisions cover duplicate/order/equality choices, operation,
omission, pipeline/stage sequence and rejection atomicity, retaining all applicable
existing scalar/query decisions. Removing determined authority for duplicates,
ordering, presence, pipeline or atomicity makes existing adequacy
`IMPLEMENTATION_UNDERSPECIFIED`. Missing policy declarations fail structure rather
than being guessed. Faithful V1 recovery detects changes to every material family.

**Evidence limits:** active-agent captures, inventories, analytical source reviews
and literal oracles share one agent; ModelAdapter replays those outputs. Synthetic
owners/reviewers approve these fixtures. Separate compiler/verifier subprocesses
provide external execution evidence, not independent cognition or real-owner
approval. Correlated source-extraction errors remain possible, as in prior rounds.

## Behavioral evidence and interactions

| Synthetic domain | Published external invocations | Material observations |
| --- | ---: | --- |
| Article labels | 27 | Add-unique, exact case distinction/order, repeated creation input, per-element trim/validation then stable dedup, invalid transformed-input rejection |
| Contact aliases | 25 | Append preserves repeated occurrences and insertion order, verbatim values |
| Product keywords | 22 | Whole-collection replacement after stable-first dedup |
| Profile interests/nickname/description | 22 | Whole-collection replacement with duplicates, optional supplied/omitted description, trim/stage distinction, simultaneous scalar updates |
| **Total** | **96** | All four traverse the full normal pipeline and external verifier |

Each domain independently reloads newly written values, uses exact existing
membership selection, preserves query bytes, transitions its lifecycle field and
then mutates an unrelated value successfully. Supplemental external-process tests
cover empty/already-unique/duplicate/case-distinct dedup inputs, invalid arrays/null,
explicit collection migration and idempotent reload/query, supported write/replace
failure with unchanged destination/temp cleanup, nullable timestamp omission versus
explicit null, trimmed enum replacement and a later-field validation failure after
an earlier candidate change. These checks are part of the 340-test verification;
they are not added to the published 96-CLI denominator.

## Fixed exposed transfer and baseline comparison

| First blocker | Preserved R5.103 | R5.104 |
| --- | ---: | ---: |
| Behavioral success | 3 | **6** |
| Structural | 14 | **11** |
| BDI | 1 | **1** |
| Formalization/clarification | 2 | **2** |

Successful local cases: **B01/B02/B03/B04/B05/B10**. B02/B03/B10 newly reach
BDI, adequacy, faithful representation, authoring, compilation, runtime and external
verification. They add 74 external invocations to the 47 baseline-case invocations,
for **121** exposed transfer invocations. No downstream stage is credited merely
for being compilable or structurally representable. Unexecuted stages remain
`NOT_REACHED`, with full per-case details in the matrix/comparison.

### Five prioritization cases

| Case | Result and diagnostic change |
| --- | --- |
| B02 | **Success.** Repeated supplied values are trimmed/validated per element and stable-deduplicated; creation omission and explicit older-record migration use empty arrays; whole-record/lifecycle/persistence composition passes. |
| B03 | **Success.** Actual writable typed tags store now feeds unchanged exact membership/query validation, including completed records, no-match/order/case/whitespace and read-only preservation. This is exposed regression only. |
| B06 | **Structural remains.** Scalar storage, trim, migration and query facts now map; source's raw-empty-sensitive validation does not. Explicit raw empty must succeed while nonempty whitespace trims to invalid. A flat pipeline cannot silently collapse those cases. No later stage or behavioral success claimed. |
| B07 | **Structural remains.** Generic append/trim/atomic semantics work on public contacts, but this source requires literal-empty collection creation, with no authorized creation input. The frozen profile exposes collection creation via a declared supplied input/default; inventing `create --notes` would violate literal initialization. Required `--text` CLI refusal also cannot be replaced with a guessed application missing-input error. Keep the original source demand and specific literal-binding gap; no later stage claimed. |
| B10 | **Success.** Omitted owner defaults empty only at creation; supplied owner trims then must remain nonempty; empty/whitespace reject unchanged. Explicit migration, exact owner query including empty, baseline/lifecycle/delete/persistence composition pass. |

B06's blocker is narrowed to a bounded raw-value/stage-sensitive validation seam;
B07 exposes collection-creation/required-input binding seams. **No new major
predicate/relationship/event family was reached downstream in a newly successful
case.** Existing boolean-store, compound/range/in-set predicate, relationship,
graph, durable event and successor/arithmetic gaps remain visible on their other
cases. B18 remains native `UNSUPPORTED_BDI_SCOPE` for the external-effect channel.

**B17/B20 remain unresolved:** no old-user migration role or nonexistent-member
error is supplied. Their native source reconciliation is `DISPUTED`; structure and
all downstream stages remain `NOT_REACHED`.

Five directly affected cases received new typed source reexpression after generic
development. The other fifteen reloaded exact frozen source bundles and retained
R5.103's still-current typed representation/unsupported demand shapes, rather than
inventing unrelated capabilities. This is not a new general English understanding
measurement. Historical sources, matrices, first results and frozen oracles retain
their original content and classifications.

## Next recommendation and stop

Recommend **R5.105: bounded typed-value normal-profile closure**: literal collection
creation bindings and source-authorized raw-stage/presence-sensitive validation,
plus faithful required-CLI-input error binding. Reuse the general mutation algebra;
do not infer B06's conditional behavior or B07's input/error authority. These are
prospective integration targets, not changes in this locked round. Broader
predicate/relationship/effect work remains outside R5.104.

Stop after generic implementation, the fixed exposed transfer and documentation.
No benchmark-specific primitive, infrastructure qualification/portability/OpenCode/
transport/model/firewall work, distributed transaction, unrelated major semantic
family, canonical model change or hand-edited generated Python was introduced.

## Completion answers

1. Typed scalar replacement, ordered scalar-element collections, append,
   add-unique, replace, element mapping, stable dedup and ordered write pipelines.
2. Order/duplicate/equality are independent explicit typed field policies.
3. Yes: input membership separates omitted/supplied empty/permitted timestamp null.
4. Yes: transformation and validation steps have explicit deterministic order.
5. Yes: rejected supported single-record mutations preserve prior state/storage;
   supported persistence failure returns no partial record.
6. Yes: scalar/collection write, reload, explicit migration and idempotence pass.
7. Yes: persisted values feed unchanged CollectionQuery membership/equality.
8. Yes within the bounded capture architecture: material omissions/refused
   policies, disputed invented facts and missing adequacy clauses are detected.
9. Yes: the full normal V1/Lykoi/compiler/external path executes the public corpus.
10. **Six** exposed local cases are behaviorally verified.
11. **B02/B03/B10** newly succeed; B06 narrows its residual blocker; B07 remains
    blocked. Only those first three newly reach later stages.
12. Raw-empty-sensitive validation, literal collection creation and required CLI
    binding seams; no newly reached unrelated major-family downstream blocker.
13. Yes: B17/B20 remain ambiguous and unapproved.
14. Bounded remaining typed-value profile closure, as recommended above.
15. No benchmark-specific primitive.
16. Infrastructure work avoided; stop after R5.104.
