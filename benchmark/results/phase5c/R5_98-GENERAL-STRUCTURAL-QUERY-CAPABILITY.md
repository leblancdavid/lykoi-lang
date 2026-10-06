# R5.98 — general structural query capability

**`R5_98_GENERAL_STRUCTURAL_QUERY_CAPABILITY_IMPLEMENTED_BOUNDED_PROFILE`**

**`B03_POST_EXPOSURE_TRANSFER = STRUCTURAL_COVERAGE_FAILURE`**

**`B03_FIRST_RESULT = DECISION_DISCOVERY_UNSUPPORTED`** remains immutable.
The new generic path works through typed FRC → complete structural projection →
BDI → existing adequacy → prospective query V1 → deterministic Lykoi lowering →
external synthetic behavior. It is a **separate bounded prospective profile**,
not complete integration into the historical v0.3 task CLI, its store, historical
V1 consumers, or its prose-shaped FRC adapter. The exposed candidate still fails
that transfer boundary. No implementation changes followed the transfer.

## Scope, provenance and review

R5.98 only; clean tree at initial `git status --short`. Current available
`openai/gpt-6.1-sol` and compatible CPython are used; exact interpreter and UTC
times are recorded in [verification](R5_98-VERIFICATION.json). No infrastructure
qualification, transport work, activation or model-registry work occurred.

The [fresh obligation sanity review](R5_98-B03-OBLIGATION-REVIEW.md) checked the
exposed source and shared context before Lykoi edits. **9 confirmed, 0 disputed,
0 missing local behavioral obligations, 0 invented behavioral obligations.**
Membership versus scalar equality is material. Byte/file-absence preservation is
an operational refinement of the no-storage-change frame; Unicode whitespace and
canonical-equivalence algorithms are not fully specified by B03. This is an
independent analytical recheck, not a blind separate-context/model review. No new
formalization qualification or owner approval is claimed.

Only B03 was used for that initial review. Development requirements use products,
users, owners/documents and labels, with no task/tag command wording. After the
synthetic freeze, already-exposed B02 was read: it concerns trimmed creation-time
tags, not a query, so no claimed query transfer was manufactured from it. Public
R5.80/R5.82 corpus material was inspected; R5.82 price/limit filtering is the
recorded public negative transfer. No hidden oracle, conventional B03 solution,
B04 or later unexposed requirement was accessed.

## General abstraction and implementation

Normative [CollectionQuery-0.1 specification](../../../docs/collection-query-v0.1.md).

- `src/air_compiler/collection_query.py`: closed typed validation and deterministic
  generation. Adjacent runtime template is the standalone read-only JSON backend.
- `src/lykoi_query/contracts.py`: exact semantic FRC-facet adapter, reprojection
  coverage, query BDI extension, unchanged adequacy integration and faithful
  `CollectionQueryDocumentV1` round-trip.
- `src/lykoi_query/compiler.py`: recovery → native FRC validation → coverage → BDI
  → adequacy → lowering. `python -m lykoi_query` exposes validation/compilation.
- `src/lykoi_query/corpus.py`: six new composed synthetic requirements/models.
- `tests/test_collection_query.py` and `test_collection_query_behavior.py`:
  structural, decision, adequacy, document/compiler and external process evidence.

The facets are source/typed record schema, named runtime parameters, field/operator/
operand predicate, independent comparison policy, ordered key sequence, input
validation/errors, inclusion criteria, effect/state frame and result/no-match shape.
Equality and collection membership are supported. Parameter operands are distinct
from constants. Case-sensitive exact comparison, explicit Unicode casefold,
no normalization and explicit Unicode whitespace stripping are distinct policies.
Ordering supports multiple keys, precedence and ASC/DESC independently of selection.
Record-validation and query-input validation are not filters.

No generic code contains B03, the exposed command name, or tag-specific dispatch.
The corpus includes **non-task collection membership** to justify membership as a
general primitive. A source facet's logical collection selects the supplied store;
this backend does not route multiple collections through one database.

Coverage refuses missing/duplicate facets, unrepresented extra obligations,
unsupported semantics, stale identities and changed projected values. Omission can
be **represented explicitly** as a null policy and then remain underspecified;
silently omitting an entire facet is a coverage failure. Explicit finite freedom
is adequate authority but is not automatically resolved by the compiler.

### Decision and adequacy integration

Existing BDI handles selection. The extension distinguishes runtime binding,
comparison policy, key sequence, validation, inclusion, effect frame and no-match
result. It reuses the unchanged BDI sidecar and unchanged adequacy analyzer.
The corpus yields **8 decisions per explicit query**, all bound to facet origins.
All six policies are challenged by omission versus explicit freedom. Removing
read-only authority remains underspecified; contradictory effect authority remains
conflicting. A mutating contract can be analyzed but cannot lower in the read-only
backend. This is finite/profile-bounded discovery, not a completeness proof.

### V1 and language boundary

The old V1 document envelope can contain opaque dictionaries; that is not a
faithful supported executable mapping. The historical faithful mapper rejects
the new queries. `CollectionQueryDocumentV1` is an explicit prospective semantic
profile extension, with exact contract commitment, full facet values and origins;
recovery rejects semantic loss. Historical V1 consumers are not claimed to accept
it. The v0.3 canonical task model/schema/compiler and generated task application
are unchanged. The added compiler module is a bounded Lykoi query backend rather
than a hand-authored task-manager implementation.

## Synthetic evidence, freeze and regressions

[Captured corpus](R5_98-SYNTHETIC-CORPUS.json) contains exact FRCs, projections,
BDI/adequacy results, query documents and generated target digests. Models include:

1. Products by exact category, SKU ASC, discontinued included, significant spaces.
2. Users by exact department, last-name ASC then ID DESC, inactive included.
3. Documents by owner, creation ASC then ID ASC, archived included.
4. Explicit casefold products contrast, still whitespace-significant.
5. Explicit stripping products contrast, still case-sensitive.
6. Documents by runtime label membership, creation DESC then ID ASC, archives
   included, repeated matching members do not duplicate records.

The tests also compose all **54 facet obligations in one six-query FRC** and
compile all six targets. Twelve near-miss variants distinguish constants/runtime,
case/normalization, one/multiple keys, precedence/direction, mutation, empty/error/
null, validation policies and included/excluded alternate-state records. Loss of
each of nine facets and unsupported-feature corruptions fail closed. Results are
detached and in-memory records are preserved.

External verification uses **42 fresh isolated generated-target subprocess
invocations** across ten tests. Literal expected record identities and complete
record equality test matches/nonmatches, case and whitespace contrasts, ordering,
inclusion, invalid inputs, no match, state errors and original persisted bytes or
file absence. These finite cases are independent processes, not independent
cognitive oracle authorship; the active agent authored requirements/models/tests.

[Verification log](R5_98-VERIFICATION.json), produced by `R5_98-verify.py`:

| Suite/check | Result |
| --- | ---: |
| New structural/query/document/compiler and external behavioral tests | 21 pass |
| Existing compiler/application | 22 / 9 pass |
| Controller/workspace/pipeline/public rehearsal | 34 / 26 / 30 / 33 pass |
| Existing BDI/adequacy/FRC | 16 / 18 / 18 pass |
| Historical V1 | 33 pass |
| External baseline | 3 pass |
| Canonical model validation and safety | exit 0 / exit 0 |

**263/263 tests pass; 14/14 commands exit 0.** No regression criteria were weakened.
Earlier development runs are not hidden: the first 18-test run had 25 subtest
failures because existing BDI's tie rule required a `multiple_matches` annotation
before checking the false exactly-one condition. The explicit zero-or-more source
fact corrected that interface omission; the next 18-test run passed. Three further
composition/effect/memory tests and the document-to-compiler handoff were added
before final verification. No such changes occurred after freeze/transfer.

[Synthetic freeze](R5_98-SYNTHETIC-FREEZE.json) binds implementation, versioned
specification, corpus and tests **after passing final verification and before
transfer execution**. This is ordinary research provenance/test freezing, not
infrastructure qualification. The transfer checks all frozen content before/after.

## Public and B03 post-exposure transfer

[Transfer evidence](R5_98-TRANSFER.json), produced by `R5_98-transfer.py`:

- **Historical public transfer:** R5.82 `nullable` price-less-than-limit example
  remains **UNSUPPORTED_RANGE_AND_NULLABILITY**. The operator-class refusal was
  executed; a whole price application was not authored. Numeric parameters,
  nullable fields and less-than semantics remain gaps. R5.80 stable-name ties and
  numeric-prefix examples also fall outside this profile; no full transfer success
  is claimed for them. Earlier public filtering gap closure is **not established**
  by this round. Historical results are unchanged.
- **`B03_POST_EXPOSURE_TRANSFER = STRUCTURAL_COVERAGE_FAILURE`.** Declared target:
  the **unmodified R5.97 candidate FRC** through the new generic structural adapter.
  Its nine legacy prose relations lack typed facet mappings; **0/9 represented**.
  BDI, adequacy, V1, authoring, compilation and B03 behavioral verification are
  **NOT_RUN** after that halt. No rewritten candidate, guessed store/CLI adapter or
  fragment-level success is substituted for this result.
- The first-result bytes and all **10** hash-bound R5.97 evidence artifacts were
  verified unchanged. **No generic implementation changes after transfer.**

This negative transfer means the new generic path requires typed semantic
formalization and has not closed the legacy candidate/application integration gap.
It does not negate the synthetic executable capability, and it is not held-out
generalization evidence. No remediation follows within R5.98.

## Required final answers

1. **Nine obligations confirmed?** Yes, analytically rechecked; the stated review
   independence and Unicode/operational-refinement caveats apply.
2. **Abstractions added?** Compositional typed CollectionQuery facets listed above.
3. **B03 dependence?** No benchmark identity or task/tag wording in generic code.
4. **Runtime predicates?** Yes, string equality and string-collection membership.
5. **Comparison/order independent?** Yes, explicit case/normalization axes and
   ordered multi-key ASC/DESC sequences.
6. **Validation/read-only preserved?** Yes, declared errors and authoritative state/
   persistence frames; bytes/absence and memory checked.
7. **BDI?** Yes in the prospective profile, reusing selection and adding bounded
   general query policy decisions.
8. **Adequacy?** Yes with the existing analyzer; omission, freedom and conflict stay
   distinct. No production authority/seal is claimed.
9. **V1?** Existing faithful mapping insufficient; the prospective query V1 extension
   round-trips faithfully. Legacy V1 executable integration remains unsupported.
10. **Lykoi execute?** Yes through the added standalone deterministic query backend;
    not through the unchanged historical task CLI.
11. **Synthetic/public behavior?** Synthetic external behavior passes (42 cases).
    Public range/nullable behavior is unsupported, not a behavioral pass.
12. **Earlier public gaps improve?** No complete earlier filtering gap closure is
    demonstrated; exact/membership capability is established on the new corpus.
13. **B03?** Post-exposure structural halt on the unchanged candidate, before BDI.
14. **Unsupported?** Prose-to-typed semantic extraction, legacy CLI/store/V1 adapters,
    ranges/numeric/nullable predicates, joins/aggregates/pagination, stable input
    ties without unique keys, arbitrary expressions, mutating lowering and automatic
    freedom resolution. General completeness/independent formalization unproven.
15. **Next unexposed benchmark?** B04 and later unexposed requirements untouched.

The ordinary concept is now an executable general **bounded** Lykoi query profile
across several domains. It is not a benchmark-specific patch, nor a claim that the
unchanged exposed candidate now traverses the old full application pipeline.
Stop after R5.98, with the two transfer limits recorded and no repair.
