# R5.107 — Normal predicate/value interface closure

**Final classification: `R5_107_PREDICATE_VALUE_INTERFACE_CLOSED`.**

All four bounded interfaces traverse captured requirements → typed FRC → source
inventory/reconciliation → synthetic owner seal → structural coverage → BDI →
adequacy → faithful normal V1 → restricted semantic authoring → deterministic
normal compiler/backend → externally observed behavior. Existing semantic families
compose without a benchmark-specific operation or another major family.

**361/361 tests**, canonical model validation and safety pass. Four synthetic
domains publish **84 external CLI invocations**; the new generic tests additionally
verify an injected declared clock in a separate process. The twenty-case frozen
exposed transfer has **13 behavioral successes, B01–B13**, and **358 external
invocations**. R5.106 remains the historical baseline with eight successes.

**Whitespace audit is not clean:** `git diff --check` reports one trailing space
at `src/lykoi_pipeline/mutable_profile.py:259`, in a formalizer-guidance string
continuation. It has no behavioral effect and is retained in the exact generic
lock rather than changing implementation bytes after outcomes. This is a failed
formatting check, not a hidden passing check. Semantic closure and frozen-content
integrity are separately established.

## Deliverables and evidence

| Deliverable | Location |
| --- | --- |
| Versioned interface contract | `docs/predicate-value-interfaces-v1.md` |
| Literal replacement validation/execution | `mutable_values.py`, `mutable_runtime.py`, `input_values.py` |
| Existing listing normalization and exact binding | `src/air_compiler/query_interfaces.py`, `profiles.py` |
| Query amendment, precondition, parameter-error and clock validation | `predicate_integration.py`, `collection_query.py` |
| Deterministic pure query evaluation and normal dispatch | `collection_query_runtime.py`, `profile_runtime.py`, existing provider adapter |
| Closed typed FRC producer schemas | `src/lykoi_workspace/mutable_schema.py`, `query_schema.py` |
| Reconciliation, recomputed coverage, BDI/adequacy and V1 | Existing normal query/mutable profiles and `src/lykoi_query/contracts.py` |
| Multi-domain source captures and pre-author literal plans | `src/lykoi_workspace/interface_corpus.py` |
| Composition, authority-loss, round-trip and injected-clock tests | `tests/test_query_interfaces.py` |
| Final generic verification | `R5_107-GENERIC-FINAL-VERIFICATION-2.json` |
| Four-domain final external evidence | `R5_107-SYNTHETIC-FINAL-EVIDENCE-2.json` |
| Authoritative final pre-transfer implementation lock | `R5_107-GENERIC-LOCK-3.json` |
| Twenty fresh fixed source captures/plans | `R5_107-B01-CANDIDATE.json` through `R5_107-B20-CANDIDATE.json` |
| Pre-outcome corpus lock | `R5_107-CORPUS-LOCK.json` |
| Individual terminal receipts | `R5_107-B01-RESULT.json` through `R5_107-B20-RESULT.json` |
| Complete exposed transfer and blocker comparison | `R5_107-TRANSFER-EVIDENCE.json`, `R5_107-COMPARISON.json`, [matrix](R5_107-CAPABILITY-MATRIX.md) |
| Historical/content/corpus/scope/whitespace audit | `R5_107-FINAL-AUDIT.json` |

## Four closed interfaces

### Literal assignment

An existing ValueMutation replacement can supply an exact typed literal instead
of a runtime input. Strings, enums, actual booleans, supported UTC timestamps and
existing ordered scalar collections use existing value validation and atomic
single-record persistence. The exact target/type/value is represented and source
reconciled; no pipeline transformation, omission or default trigger is attached.
Identity and lifecycle fields retain their separate write-authority boundaries.
External cases verify preservation of other fields, persisted reload, independent
lifecycle composition, and boolean terminal-state writes without invented inputs.

### Existing selection amendment

CollectionQuery gains an explicit amendment facet with a complete base query,
source-determined `and`, `or` or `replace`, and a typed predicate. The resulting
selection tree must match that composition. Other facets remain exact, including
ordering, result shape, inclusion, read-only effect and validation. Existing
clock/error/precondition interfaces in a base query remain preserved too.

Normal model binding independently normalizes supported existing list behavior,
including field equality, conjunctions and declared before-clock filters. An
unfiltered list uses an ordinary typed true-equality tree. Existing command
collision without the exact preserved base refuses. Normal query amendments also
compose with membership. No command-name special case occurs in product code.

### Preconditions and declared errors

Parameter presence/type checks, existing parameter validation, operation
preconditions and record selection are distinct. A query precondition binds
parameters/resources, has a declared error and before-selection stage, and rejects
without a write. Normal dispatch evaluates it before state read and selection.
Parameter type/missing errors retain their own declared identity. Required CLI
rejection reuses the existing input-binding concept without fabricating an
unspecified application missing-input error.

Document cases distinguish missing owner, invalid owner type, nonblank parameter
validation, an empty-owner precondition, and a successful empty result. Transfer
B09 separately verifies invalid/non-UTC timestamp errors, reversed-window rejection,
inclusive and equal-endpoint selection, and unchanged storage.

### Declared clocks

Resource operands bind an explicitly authorized existing UTC capability with exact
timestamp type and once-per-query sampling. Default execution delegates to the
existing declared-capability adapter; it does not insert ambient backend time.
Host/test providers bind capability IDs and are type/authority checked. Multiple
aliases sample one capability once. Nullable timestamp field comparison against
nonnullable clock values retains exact binding types and atomic-null-false behavior.

The injected-clock external process loads persisted records through the generated
target, checks strict boundary/null behavior, observes the single sample count and
unchanged file bytes. Combined owner/clock/selection queries retain ordering.

## Source authority and representation challenges

Normal schemas carry complete literal sources, amendment base/mode/tree,
precondition error/stage/rejection, declared parameter errors and clock bindings.
Reconciliation disputes changed literal values, amendment mode, errors and clock
identity. Inconsistent resulting amendment trees refuse even before reconciliation.
Coverage recomputes the full facts/IR/facets and rejects material interface losses;
faithful V1 recovery detects altered literal facts and removed query interfaces.
BDI makes exact literal and query-interface decisions visible; removed determined
authority yields `IMPLEMENTATION_UNDERSPECIFIED` through existing adequacy.
Unknown amendment composition and missing typed resource binding refuse rather
than being guessed.

These are same-agent analytical source captures/inventories/oracles with synthetic
owners, not independent cognition or measured live English interpretation accuracy.
External plans exercise finite selected behavior; their facet-level coverage labels
are not proof of exhaustive semantic-leaf coverage. Existing compiler/persistence/
pipeline regressions supplement the new plans.

## Synthetic evidence

| Public domain | Final published invocations | Result |
| --- | ---: | --- |
| Accounts | 21 | Normal path externally verified |
| Products | 21 | Normal path externally verified |
| Documents | 21 | Normal path externally verified |
| Sessions | 21 | Normal path externally verified |
| **Total** | **84** | All four interfaces composed |

Each exercises literal writes, atomic replacement/reload, preservation, lifecycle,
existing listing selection and ordering, membership selection amendments, query
validation/preconditions, application and CLI-only rejection, nullable timestamp
clock selection and existing clock-listing amendment. Their common reusable record
vocabulary has domain-specific collection policies; this is a bounded composability
challenge, not a held-out multi-domain generalization study.

## Generic development and locking chronology

Initial development caught nullable-clock comparison typing and a deliberately
changed amendment mode whose resulting tree also needed to change before testing
source reconciliation. Both were repaired before a passing generic lock.

1. First passing 361-test verification and four-domain 72-invocation audit produced
   `R5_107-GENERIC-LOCK.json`.
2. A pre-transfer composition audit added normalization for existing clock listings.
   A second passing 361-test check and 76-invocation audit produced lock 2.
3. Source review before any transfer outcome identified that declared query type
   errors must compose with existing required-CLI rejection without an invented
   missing application error. A synthetic owner-CLI case qualified that composition.
   Final 361-test verification and 84-invocation audit produced **lock 3**.

All three locks and their original evidence are preserved. Only lock 3 governed
R5.107 transfer; it precedes every fixed R5.107 candidate and terminal result and
remains byte-intact. No implementation, specification or test modification followed
any R5.107 transfer outcome. The ordinary regression suite run before locks is
separate from this fixed twenty-case R5.107 transfer.

One verification shell call and a final generic audit shell call exceeded tool
timeouts; neither published its final record/lock. Complete reruns succeeded.
Their unpersisted partial stdout is session evidence only, not an extra invocation
denominator. An initial script invocation with `PYTHONPATH=src` failed to import
the repository benchmark package; `PYTHONPATH=src;.` ran the existing environment.
No environment/tool/runtime infrastructure was changed.

## Frozen exposed transfer

| First blocker | R5.106 | R5.107 |
| --- | ---: | ---: |
| Behavioral success | 8 | **13** |
| Structural coverage | 8 | **4** |
| Invalid typed clock candidate at formalization | 1 | **0** |
| Source clarification/dispute | 2 | **2** |
| BDI external-effect discovery | 1 | **1** |

**B01–B07/B10 preserve their eight successes.** Newly successful cases:

* **B08:** exact literal archive write, repeat rejection/status preservation,
  additive migration and all six source-named listing exclusions/archived listing.
* **B09:** declared UTC-input error plus start≤end precondition, inclusive/equal
  boundaries, exclusion rules and read-only behavior.
* **B11:** pending OR (completed AND archived) delete permission now traverses the
  full path once archive/listing precursors are represented.
* **B12:** declared-clock urgent membership selection verifies; ordinary overdue
  listing preserves every priority while excluding archived records.
* **B13:** terminal archive guards compose with append-note, completion, B11
  deletion and archived visibility.

B08/B09/B11/B13 newly reach BDI through external behavior. B12 newly reaches
structure and every later stage, correcting the earlier *prospective* normal clock
binding seam without rewriting its preserved R5.106 first blocker.

No newly progressed case exposes another downstream failure. The remaining
boundaries are clearer: B14 persistent references/cycles/delete integrity;
B15 quantified related-state guards; B16 multiple entities/existence; B19 atomic
successor creation and temporal arithmetic. B17 old-user migration role and B20
unknown-member error remain unresolved `DISPUTED`. B18 remains
`UNSUPPORTED_BDI_SCOPE`, with missing `rule_for:external_effect`, not a predicate
problem. The exact before/after matrix retains all `NOT_REACHED` stages.

All sources are freshly read frozen bundles. Unchanged supported facts are reviewed
through current typed producers; saved FRC captures are not replayed. Targeted
requirement-local realizations use a disposable additive schema 4 against the
canonical schema 3, with explicit source-authorized defaults for listing/store
precursors. They do not claim cumulative historical B01–B13 achievement or recreate
every intervening schema version. B01–B20 are exposed development/regression data;
new generalization requires a new development-unexposed source.

## Completion answers and stop

1. **Yes:** existing mutation replacement assigns exact typed literals.
2. **Yes:** existing model/normal queries gain authorized selection with preserved
   unrelated facets and explicit composition.
3. **Yes:** query preconditions, parameter validation and selection remain distinct.
4. **Yes:** failed preconditions emit declared application errors before selection.
5. **Yes:** declared typed clocks are deterministic under controlled providers.
6. **Yes:** exact literal/base/mode/error/resource facts are source-reconciled.
7. **Yes:** normal coverage, BDI, adequacy and faithful V1 retain the interfaces.
8. **Yes:** normal compiler/backend executes them using existing mechanisms.
9. **13 of 20** behaviorally succeed: **B01–B13**.
10. **B08/B09/B11/B12/B13** newly reach external behavior.
11. No new downstream failures in progressed cases; remaining major-family blockers
    are persistent/multiple-entity references, quantified guards and atomic
    successor/effect/arithmetic demands.
12. **Yes:** B17/B20 remain disputed; missing authority was not invented.
13. **Yes:** B18 remains an event/external-effect discovery issue.
14. Recommend **persistent relationships and cross-entity reference integrity** as
    the next major family, with multi-entity foundations explicitly scoped. This
    is a recommendation, not work started here.
15. **No** benchmark-specific primitive or product benchmark-ID dispatch.
16. **Yes** infrastructure work was avoided.

**Stop after R5.107 generic closure and exposed transfer.** No relationships,
events, arithmetic or another round has begun. Whitespace cleanup remains a
separately recorded follow-up because the evaluated implementation is frozen.
