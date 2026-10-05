# R5.80 — Requirement formalization qualification

## Result

**`R5_80_REQUIREMENT_FORMALIZATION_PARTIAL`**.

Structured candidates, separate source-fidelity review, issue preservation,
content-bound approval bookkeeping and conservative projection work on a small
declared public calibration. The evidence does **not** qualify trustworthy future
benchmark input production from arbitrary human requirements. Production approval,
cross-provider reliability and general faithful V1 conversion remain unestablished.
Stop after R5.80; Phase 5C remains paused.

| Dimension | Observed result |
| --- | --- |
| Formalization quality | 14 source candidates: 12 synthetic human-style requirements, public B01, one additional explicitly selected public-component calibration. Independent source-WHAT review approves 9, blocks 4 for clarification and 1 for conflict. |
| Independent-formalizer agreement | Same-family isolated A/B attempts on 7 sources: comparison judges 6 equivalent within declared candidate scope and B01 materially divergent. Strict two-file-isolation-qualified agreement: **0/7**, because B exceeded that read scope. |
| Review negatives | 3 deliberately defective drafts: 2 rejected (implementation leakage/invented invalid-input policy), 1 incomplete (missing required obligation). |
| V1 projection coverage | Of 9 approved FRC candidates, 1/9 has a complete calibrated projection; 8/9 explicitly fail `UNREPRESENTABLE_SOURCE`. |
| Preservation | P01 complete component context and both supplemental clauses/IDs mechanically preserved; separate projection review approves fidelity. No arbitrary prose round-trip proof. |
| Mechanical verification | New FRC tests **18/18 PASS**; unchanged guarded V1 regression tests **33/33 PASS**, actual protected read attempts **0**. |
| B01 | Every identified local obligation retained, with default-scope ambiguity explicit. **NEEDS_CLARIFICATION**, no approved B01 projection or benchmark-authority change. |
| B03 | **B03_PRISTINE / B03_NOT_EVALUATED / B03_NOT_EXPOSED_TO_LYKOI_DEVELOPMENT**. Every R5.80 B03 access/activity counter remains zero. |

## Architecture and deliverables

Retain R5.79's separation:

`Human Requirement → Requirement Formalization → Formal Requirement Contract
→ Lykoi authoring → deterministic validation/lowering → software`.

| Deliverable | Artifact |
| --- | --- |
| Versioned experimental vocabulary, methodology, equivalence/review rules | [FRC-0.1 specification](../../../docs/formal-requirement-contract-v0.1.md) |
| Machine-readable structural schema | [FRC-0.1 schema](../../../schema/formal-requirement-contract-v0.1.schema.json) |
| Small diverse public corpus | [corpus.json](r5_80/corpus.json) |
| Manually authored formalizations, including public B01 | [candidates.json](r5_80/candidates.json), [reproducible fixture authoring](r5_80/fixtures.py) |
| Independent attempts | [attempt A](r5_80/independent-a.json), [attempt B](r5_80/independent-b.json) |
| Semantic obligation alignment/disagreements | [comparison.json](r5_80/comparison.json) |
| Independent source-WHAT approvals and coverage judgments | [reviews.json](r5_80/reviews.json) |
| Exact source locators | [coverage.json](r5_80/coverage.json) |
| Projection results, positive V1 document/normalized contract/map and provenance | [qualification.json](r5_80/qualification.json) |
| Separate projection-fidelity approval | [projection-review.json](r5_80/projection-review.json) |
| Pure bounded infrastructure | [formal_requirements_r5_80.py](../../evaluation/formal_requirements_r5_80.py) |
| Executable mechanical checks | [test_formal_requirements_r5_80.py](../../evaluation/test_formal_requirements_r5_80.py) |
| Evidence reproduction | [qualify.py](r5_80/qualify.py), [inventory and instructions](r5_80/README.md) |

The fixture authoring code is a serialization of manually authored interpretations;
it is **not** an automatic natural-language formalizer. The independent A/B attempts
use their own notation so their output cannot be mistaken for a shared-template
reproduction. Comparison aligns obligations one-to-many rather than renumbering
them to resemble each other.

## Vocabulary and methodology qualification

FRC-0.1 records source identity/text commitment, explicit context/domain/assumptions,
stable obligation IDs, direct versus necessary-implication basis, exact source
quotes, derivation parents, reviewed relation parameters and normative statements.
It separately records ambiguities, conflicts, questions, open behavior,
implementation freedoms and revision lineage. Approval is a **separate receipt**;
a draft has `review: null`.

Twenty relation labels cover arithmetic, entity behavior, selection/ordering,
normalization, transitions, invariants, persistence, optional/null branches,
cardinality, effects and the public priority example's observations. These are
review profiles, not Lykoi primitives. The `priority_*` labels expose domain/rank,
creation, inclusion and selection facts; they are not evidence that domain-specific
labels are a minimal general vocabulary. FRC-0.1's generic parameter objects and
textual normative clauses deliberately do not pretend to have a complete,
implementation-independent executable predicate calculus. This remains an
important **formal-contract precision/generality gap**.

The bounded procedure freezes admitted source/context, enumerates material
clauses, labels directly stated behavior and separately justified implications,
retains material alternatives/conflict witnesses, records what remains unspecified,
and submits the candidate to a fresh reviewer before projection. It never resolves
intent by querying support. An explicit successful-domain requirement can be
approved without inventing invalid-input behavior; a missing definition of the
successful selection criterion cannot.

Additional review concepts—quantification, occurrence identity/multiplicity,
frame conditions, temporal horizon, concurrent observation and partial-domain
freedoms—are necessary to distinguish superficially similar behaviors. They are
included only when source authority requires them; concurrency/transactions,
timeouts, coercion and storage mechanisms are not implicit requirements.

The coverage ledger supplies exact code-point offsets/quotes and mapped IDs. Its
mechanical quote overlap does **not** establish that every proposition in a
fragment is covered. The independent reviewer supplies that judgment. The richer
prospective evidence-inventory and resolution protocol in the specification is
not fully mechanically implemented; no interactive source-owner resolution or
complete lineage history was qualified here.

## Corpus and review results

| Source | Distinct concern | Independent source review | Projection |
| --- | --- | --- | --- |
| S01 | Exact integer sum; explicit purity | APPROVED | UNREPRESENTABLE_SOURCE |
| S02 | CRUD with key-domain/frame/open-invalid cases | APPROVED | UNREPRESENTABLE_SOURCE |
| S03 | Exact selection, Unicode ordering, stable ties | NEEDS_CLARIFICATION: active predicate/type | NOT_APPROVED |
| S04 | ASCII transformation composition | APPROVED | UNREPRESENTABLE_SOURCE |
| S05 | Initial state, conditional close, error/frame/invariant | APPROVED | UNREPRESENTABLE_SOURCE |
| S06 | Last-successful storage across restart; failure preservation | APPROVED | UNREPRESENTABLE_SOURCE |
| S07 | Omitted/null/integer/invalid; purity | APPROVED on abstract typed domain | UNREPRESENTABLE_SOURCE |
| S08 | Undefined best | NEEDS_CLARIFICATION | NOT_APPROVED |
| S09 | Universal insertion and alphabetical orders | CONFLICTING_REQUIREMENT | NOT_APPROVED |
| S10 | Positive-integer success only | APPROVED with invalid/effect behavior open | UNREPRESENTABLE_SOURCE |
| S11 | Earliest qualifying prefix, limit, zero and frame | APPROVED | UNREPRESENTABLE_SOURCE |
| S12 | Reservation pre/postcondition, invariant and effect counts | NEEDS_CLARIFICATION: acceptance sufficiency/otherwise | NOT_APPROVED |
| B01 | Public local priority change with interacting commands/migration/default | NEEDS_CLARIFICATION | NOT_APPROVED |
| P01 | Explicit selection of complete existing public components; two supplemental boundary obligations | APPROVED | Complete projected calibration; separate APPROVED_PROJECTION |

The twelve synthetic texts are AI-authored human-style requirements, not
independently collected human-written requests. B01 supplies the public
human-written source. This authorship limitation directly limits qualification
against the requested human-input objective; it is not hidden by calling the
corpus a real-user study. P01 is an additional non-held-out **component calibration**,
intentionally designed to exercise existing mechanical preservation, not unseen
formalizer reliability. Diverse examples prevent a one-task demonstration, but
small hand-selected coverage is not generality evidence.

### Negative results

* **Undefined best:** all attempts keep the predicate unresolved. No priority,
  recency, top-k count or ordering is silently selected. Approval is blocked.
* **Contradictory ordering:** both order obligations and the `[z,a]` witness remain.
  A bounded executable enumeration finds no one output permutation satisfying
  both orderings; this is not a general consistency solver.
* **Missing invalid-input commitment:** S10 receives no invented rejection/purity
  rule and remains approved only on its positive-integer domain. The separate
  INVENTED draft adds INVALID and is independently rejected.
* **Implementation leakage:** LEAK adds a specific loop/storage engine absent
  from S10; independent review rejects it. Structural validity alone permits it,
  demonstrating why semantic review is necessary.
* **Missing success obligation:** MISSING has no increment obligation and is
  independently classified INCOMPLETE_FORMALIZATION.
* **Approval misuse:** executable tests reject stale/self-review/incomplete-check
  receipts; active ambiguities and conflicts defeat an adversarial APPROVED label.
  Identity inequality alone cannot establish honest institutional independence.

No adversarial draft is revised into authority merely to produce a passing count.

## Public B01 source → candidate contract

The unchanged complete source is retained in the candidate and both independent
records. Its physical and contract-text commitments are independently computed
by the evidence driver and match on this checkout:
`b7b2d714db5cee566e9e55982dd4c4d95d3d57f0c341e04ba1e15c24e9a8e94d`.
No source simplification, imported acceptance test or protected request is used.

| B01 meaning | Coordinating candidate obligation(s) |
| --- | --- |
| Add accepted CRITICAL, retaining existing vocabulary | B01.O01 |
| CRITICAL above HIGH as a rank, without invented list sorting | B01.O02 |
| Explicit CRITICAL creation accepts/persists/returns that value | B01.O03 |
| list includes CRITICAL task/value | B01.O04 |
| list-high still exactly HIGH | B01.O05 |
| CRITICAL/LOW/NORMAL excluded by that priority criterion | B01.O06, separately labeled necessary implication of O05 |
| Each existing LOW/NORMAL/HIGH task preserves its priority through migration | B01.O07 |
| Missing priority still defaults to NORMAL | B01.O08 plus unresolved B01.I1 |

Independent review judges **coverage of every identified local obligation**, but
does not approve a complete contract: missing priority could describe omitted
creation input or an absent historical stored field. “Still” references context
not imported in this requirement-local study. A source owner/permitted baseline
authority must resolve that scope; R5.80 neither changes B01 nor chooses a convenient
interpretation. Rank observability and full transport/state configuration also
remain locally unspecified. This does not retroactively invalidate historical
B01 acceptance; it is a prospective formalization finding under declared local scope.

B01's current result is **NOT_APPROVED**, before a complete projection attempt.
Its preserved relation kinds/configuration absence would also encounter this
prototype's `NO_QUALIFIED_COMPLETE_MAPPING`, but that conditional observation is
not a separately approved B01 projection result. R5.78's historical public-source
packaging rejection is preserved; no frozen V1 expansion forces B01 to fit.

## Independent attempts and equivalence findings

A and B receive the same public sources, no other's output and no developer
solution. Separate contexts are genuine procedural attempts; same model family,
preloaded guidance and shared concern annotations constrain independence.
No cross-provider or blind elicitation study occurred.

Comparison judgments:

* **6/7 candidate-scope equivalents:** S03, S07, S08, S09, S10 and S12. This
  includes equivalent preserved *issues*, not six approved contracts.
* **1/7 materially divergent:** B01 A limits defaulting to omitted creation
  input, while B retains an unresolved potentially broader defaulting point.
  Matching issue lists do not erase this difference. This is not a mutually
  unsatisfiable pair; it is a material domain discrepancy requiring clarification.
* S03 returned-content preservation is entailed by exact membership of input
  occurrences, not merely input nonmutation. Differing clause decomposition is
  explicitly aligned in the comparison record.
* S07's encoding issues are labeled ambiguity by A versus unspecified by B.
  The comparator preserves this disposition difference; the independent reviewer
  approves only abstract typed meaning, leaving executable encodings open.
* Stated/implication partitioning and redundant derived consequences differ;
  no byte/ID identity is required for a behavioral alignment.

B's additional required project-guidance reads violate the requested two-file
input restriction, although it disclosed no other formalization or protected
request read. Strict input-isolated agreement therefore has **zero qualifying
pairs**, not a 6/7 clean-isolation success. The comparison reviewer also discloses
extra governance reads. The records remain informative, limitation-bearing
observations, not production independence certificates.

## V1 projection and round-trip preservation

The complete projection question is asked only after content-bound source review.
The new rule supports exactly **explicitly source-selected complete public
application/configuration context**, plus the two supplemental kinds already
defined by V1. A missing complete mapping returns one structured failure and no
document bytes; partially mappable obligations are not packaged alone.

**Eight failures** are `UNREPRESENTABLE_SOURCE /
NO_QUALIFIED_COMPLETE_MAPPING`. Each record lists all unmapped obligation IDs
and the missing component-authority condition. These are **prototype mapping /
evaluation-source representation gaps**, not proofs that no expression in frozen
V1 could ever represent those requirements and not Lykoi capability findings.
No support-driven assumptions or unqualified opaque obligation kind is used to
claim successful translation.

**P01 positive calibration** selects the already-public optional-measurement
fixture's entire application/configuration via a source commitment. Its public
constructor performs existing checked-plan construction; this is disclosed
calibration context, not support feedback supplied to independent prose formalizers.
Both supplemental requirements use existing meanings unchanged. The V1 document,
normalized contract and complete ID map are retained in `qualification.json`.
Separate projection review binds source/FRC, document, coverage and behavioral
identity; `production_authority` is false.

Mechanically demonstrated for P01:

1. Every application/configuration JSON value equals its authoritative input.
2. Both FRC IDs survive as their exact supplemental V1 IDs; requirements are
   transferred unchanged, including optional/null durable-domain constraints.
3. Canonical document encode/parse/assemble preserves normalized V1 identity.
4. Recovery interprets the two known V1 kinds and exact full context, yielding
   the original reviewed relation clauses and retained provenance.
5. Added/dropped IDs, changed context, weakened constraints and stale coverage /
   document review bindings are detected by tests/comparison.

Recovery retains original normative statements for review; it does **not** infer
human intent from V1 or prove those statements from arbitrary parameter JSON.
Fidelity of selected component authority and recognized clauses has independent
review support. No universal trace equality, software correctness, actual
execution or acceptance result follows. The other sources have no complete
round-trip, rather than a silently weakened recovered contract.

## Verification and failures retained

Command observations and initial development failures are recorded in
[validation.json](r5_80/validation.json).

Executed from the repository root:

```powershell
Test-Path -LiteralPath "benchmark/results/phase5c/r5_80"
python -B -S -m benchmark.results.phase5c.r5_80.fixtures
python -B -S -m benchmark.results.phase5c.r5_80.qualify
python -B -S -m benchmark.evaluation.test_formal_requirements_r5_80
python -B -S -m benchmark.evaluation.test_benchmark_documents_v1
git diff --check
```

Final FRC suite **18/18 PASS**, unchanged guarded V1 suite **33/33 PASS**, zero
actual protected read attempts in that guard. The V1 suite's fake protected
resources live in temporary directories; its public/fake static lifecycles are
regression evidence, not an actual held-out observation. No broad harness discovery
or protected suite runs. Test-only schema evaluation covers the experimental
schema's keyword subset; no general JSON Schema engine is claimed.

The first new-prototype test run discovered **15 tests: 11 pass, 1 failure and
3 errors**. Strict JSON serialization rejected the comparator's own internal tuple,
and an exception wrapper obscured the intended non-JSON rejection code. Both
were repaired in the new module. A subsequent 15/15 run passed; after adding
separate projection-review, bounded witness and evidence-reproduction tests,
18/18 passed. These are qualification infrastructure development fixes, not a
pre-existing Lykoi defect, semantic expansion or repaired held-out run.

### Reading-scope deviation

One coordinating file-targeted content-search call unexpectedly searched the
containing semantic directory and returned unrelated historical draft snippets
outside the admitted design inventory. The output was discarded as design /
qualification input; no returned obligation was copied into the vocabulary,
corpus or test expectations. No B03 content was returned or opened. Subsequent
reads used exact paths; qualification fixture reads are explicitly allowlisted
before access in a focused test. This is a **READ_SCOPE_DEVIATION**, not a claim
of successfully enforced repository-wide public-only containment. No further
investigation of those drafts or protected request source was performed.

The additional agent-governance reads and this tool deviation reinforce the
PARTIAL containment conclusion. Session disclosures and a focused path guard
cannot establish a trusted, isolated production formalization environment.

## Protected boundary and semantic accounting

| B03 activity during R5.80 | Count/status |
| --- | --- |
| Protected development/source read attempts and reads | **0 / 0** |
| Formalization / packaging attempts | **0 / 0** |
| Authorizations / reservations / openings | **0 / 0 / 0** |
| Observations / static-consumer calls | **0 / 0** |
| Generation / execution / acceptance / repair | **0 / 0 / 0 / 0** |
| B03 FRC / V1 package / package commitment | **Not created** |
| B03 eligibility | **Not claimed** |

These are scoped activity accounting and inherited pristine status, corroborated
by the declared reads and V1 test guard, **not** a protected-file hash/content
inspection or read of a protected ledger. No protected metadata that reveals
request content is inspected. B02 exposed/indeterminate history is retained and
its contents are not design feedback. Existing frozen semantics, compiler/runtime,
V1 adapter/runner, requirements, oracles and historical evidence are preserved.
Core semantics remain **30**; the new module is prospective requirement-process
infrastructure. No Lykoi semantic capability or program generation is added.

## Interpretation and stop

The central question receives a bounded **partially positive** answer: independent
candidate production/review can retain meaningful obligations and correctly block
several adversarial failures; a narrowly authoritative public component contract
can project without loss. The evidence also exposes substantive missing precision,
independence/containment and mapping qualifications. Conceptual relation labels
and reviewer judgments cannot be represented as universal executable proof.

Before future input-production authority could be considered, separate public-only
work would need independently authored human examples, cleaner enforced input
isolation, stronger provider-independent relation definitions, source-owner issue
resolution, richer evidence/lineage checking and independently authored full V1
projections beyond component pass-through. These are limitations/proposals, not
activities authorized or started after this round.

**Final: `R5_80_REQUIREMENT_FORMALIZATION_PARTIAL`. R5.80 stops. B03 remains
pristine, not evaluated and not exposed to Lykoi development.**
