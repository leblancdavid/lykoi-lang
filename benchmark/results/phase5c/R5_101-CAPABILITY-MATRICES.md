# R5.101 — twenty-case current capability matrix

Requirement-local current pipeline results; **not cumulative Phase 5C achievement**. See the report for evidence limits and dependencies.

| Case | Requirement family | First blocker | Native classification | Missing capability/integration (primary class) | Furthest stage | Current result |
| --- | --- | --- | --- | --- | --- | --- |
| B01 | enum evolution | STRUCTURAL | `STRUCTURAL_COVERAGE_FAILURE` | Closed structural bridge cannot carry enum extension, rank/list and migration-preservation relations; legacy enum/default/filter semantics already exist (STRUCTURAL_INTEGRATION_GAP) | STRUCTURAL | Blocked; later stages NOT_REACHED |
| B02 | ordered normalized values | STRUCTURAL | `STRUCTURAL_COVERAGE_FAILURE` | Persisted ordered string values, repeated input, trim/validate/map and stable deduplication; query read-only strings do not provide mutation semantics (MISSING_GENERAL_SEMANTIC_CAPABILITY) | STRUCTURAL | Blocked; later stages NOT_REACHED |
| B03 | runtime membership query | STRUCTURAL | `STRUCTURAL_COVERAGE_FAILURE` | Typed membership query is supported; model-state binding refuses missing tags field. Underlying persisted-list prerequisite remains missing (BACKEND_INTEGRATION_GAP) | STRUCTURAL | Blocked; later stages NOT_REACHED |
| B04 | verbatim optional field | STRUCTURAL | `STRUCTURAL_COVERAGE_FAILURE` | No normal field-addition/migration/result-preservation bridge despite legacy input_default and literal migration support (STRUCTURAL_INTEGRATION_GAP) | STRUCTURAL | Blocked; later stages NOT_REACHED |
| B05 | runtime equality query | SUCCESS | `BEHAVIORALLY_VERIFIED` | Runtime equality query works against current model; pending/completed domain only, not cumulative B01-B04 achievement (no blocker) | BEHAVIORAL_VERIFICATION | Behaviorally verified (local) |
| B06 | normalized field and equality query | STRUCTURAL | `STRUCTURAL_COVERAGE_FAILURE` | Create-time optional/explicit-empty distinction plus trim/validation assignment; exact query exists but category state is missing and mixed mutation/query mappings refuse (MISSING_GENERAL_SEMANTIC_CAPABILITY) | STRUCTURAL | Blocked; later stages NOT_REACHED |
| B07 | append mutation | STRUCTURAL | `STRUCTURAL_COVERAGE_FAILURE` | Ordered persisted value arrays and append transformation; trim-before-write; legacy assignments cannot append (MISSING_GENERAL_SEMANTIC_CAPABILITY) | STRUCTURAL | Blocked; later stages NOT_REACHED |
| B08 | orthogonal lifecycle and query inclusion | STRUCTURAL | `STRUCTURAL_COVERAGE_FAILURE` | Boolean typed query values/inclusion exist, but legacy application fields/store cannot persist booleans; orthogonal archive mutation and coordinated query integration absent (BACKEND_INTEGRATION_GAP) | STRUCTURAL | Blocked; later stages NOT_REACHED |
| B09 | nullable temporal range query | STRUCTURAL | `STRUCTURAL_COVERAGE_FAILURE` | Two typed temporal operands, inclusive range, cross-input comparison and null exclusion; archive store binding also absent (MISSING_GENERAL_SEMANTIC_CAPABILITY) | STRUCTURAL | Blocked; later stages NOT_REACHED |
| B10 | optional identity field and equality query | STRUCTURAL | `STRUCTURAL_COVERAGE_FAILURE` | Optional owner create-time trim/validation with omission distinguished; query equality supported but owner state and normal mutation bridge absent (MISSING_GENERAL_SEMANTIC_CAPABILITY) | STRUCTURAL | Blocked; later stages NOT_REACHED |
| B11 | conditional deletion guard | STRUCTURAL | `STRUCTURAL_COVERAGE_FAILURE` | Composed conditional rejection/permission predicate: pending OR archived; conjunction-only equality guards are insufficient; boolean prerequisite absent (MISSING_GENERAL_SEMANTIC_CAPABILITY) | STRUCTURAL | Blocked; later stages NOT_REACHED |
| B12 | clock-relative compound query | STRUCTURAL | `STRUCTURAL_COVERAGE_FAILURE` | Compose clock/null/pending/archive predicate with scalar priority in a constant set. Legacy before-clock exists; query profile has no clock/nullable predicate or scalar-in-set composition (MISSING_GENERAL_SEMANTIC_CAPABILITY) | STRUCTURAL | Blocked; later stages NOT_REACHED |
| B13 | cross-operation terminal guard | STRUCTURAL | `STRUCTURAL_COVERAGE_FAILURE` | Cross-operation equality/transition guards exist in legacy semantics but normal invariant mapping is absent; boolean/archive and notes prerequisites remain missing (STRUCTURAL_INTEGRATION_GAP) | STRUCTURAL | Blocked; later stages NOT_REACHED |
| B14 | identity graph invariants | STRUCTURAL | `STRUCTURAL_COVERAGE_FAILURE` | Persisted identity edges, append, relation lookup, acyclicity/reachability and inverse-reference deletion guard (MISSING_GENERAL_SEMANTIC_CAPABILITY) | STRUCTURAL | Blocked; later stages NOT_REACHED |
| B15 | quantified relationship guard | STRUCTURAL | `STRUCTURAL_COVERAGE_FAILURE` | Quantified related-record state guard (all dependencies complete), with existing transition composition (MISSING_GENERAL_SEMANTIC_CAPABILITY) | STRUCTURAL | Blocked; later stages NOT_REACHED |
| B16 | multi-entity referential integrity | STRUCTURAL | `STRUCTURAL_COVERAGE_FAILURE` | Multiple persistent entity states, dynamic cross-entity existence/uniqueness and relation-aware migration (MISSING_GENERAL_SEMANTIC_CAPABILITY) | STRUCTURAL | Blocked; later stages NOT_REACHED |
| B17 | data-dependent authorization | FORMALIZATION | `NEEDS_CLARIFICATION` | Existing non-system users need a migration role; creation default USER alone does not authorize that migration. Authorization/state integration is a separate downstream demand (AMBIGUOUS_REQUIREMENT) | FORMALIZATION | Blocked; later stages NOT_REACHED |
| B18 | atomic ordered event effects | BDI | `UNSUPPORTED_BDI_SCOPE` | Effects are accepted as external_effect channels but no supported event decision discovery carries their meaning: rule_for:external_effect. Durable event/transaction semantics also absent downstream (STRUCTURAL_INTEGRATION_GAP) | BDI | Blocked; later stages NOT_REACHED |
| B19 | conditional atomic successor creation | STRUCTURAL | `STRUCTURAL_COVERAGE_FAILURE` | Nullable positive integer, temporal arithmetic, conditional record copy/create, fresh resources and multi-effect atomicity (MISSING_GENERAL_SEMANTIC_CAPABILITY) | STRUCTURAL | Blocked; later stages NOT_REACHED |
| B20 | relationships and composed permission predicates | FORMALIZATION | `NEEDS_CLARIFICATION` | Unknown member-user rejection error has no explicit authority; persistent project/membership relationships and composed permissions remain downstream demands (AMBIGUOUS_REQUIREMENT) | FORMALIZATION | Blocked; later stages NOT_REACHED |

## Explicit stage accounting

P = pass; C = source-bound analytical candidate accepted by native reconciliation; B = blocked; — = NOT_REACHED. No downstream failure is inferred.

| Case | Formalization | Structural | BDI | Adequacy | V1/profile | Authoring | Compilation | Runtime | External behavior |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B01 | C | B | — | — | — | — | — | — | — |
| B02 | C | B | — | — | — | — | — | — | — |
| B03 | C | B | — | — | — | — | — | — | — |
| B04 | C | B | — | — | — | — | — | — | — |
| B05 | C | P | P | P | P | P | P | P | P |
| B06 | C | B | — | — | — | — | — | — | — |
| B07 | C | B | — | — | — | — | — | — | — |
| B08 | C | B | — | — | — | — | — | — | — |
| B09 | C | B | — | — | — | — | — | — | — |
| B10 | C | B | — | — | — | — | — | — | — |
| B11 | C | B | — | — | — | — | — | — | — |
| B12 | C | B | — | — | — | — | — | — | — |
| B13 | C | B | — | — | — | — | — | — | — |
| B14 | C | B | — | — | — | — | — | — | — |
| B15 | C | B | — | — | — | — | — | — | — |
| B16 | C | B | — | — | — | — | — | — | — |
| B17 | B | — | — | — | — | — | — | — | — |
| B18 | C | P* | B | — | — | — | — | — | — |
| B19 | C | B | — | — | — | — | — | — | — |
| B20 | B | — | — | — | — | — | — | — | — |

P* for B18 is native bounded structural acceptance of effects channels, not proof that full event semantics were structurally understood.

## Historical results (preserved, not current classifications)

Conventional historically achieved B01–B16; B17–B20 were not evaluated. Lykoi results below come from the R2/R3/R4/B16 checkpoint reports referenced in the R5.101 report.

| Case | Historical Lykoi result | R5.101 current local result |
| --- | --- | --- |
| B01 | SUCCESS | `STRUCTURAL_COVERAGE_FAILURE` |
| B02 | AXIOM_CAPABILITY_GAP | `STRUCTURAL_COVERAGE_FAILURE` |
| B03 | BLOCKED_BY_GAP -> B02; R5.97 DECISION_DISCOVERY_UNSUPPORTED / STRUCTURAL_COVERAGE_FAILURE; R5.98 transfer STRUCTURAL_COVERAGE_FAILURE | `STRUCTURAL_COVERAGE_FAILURE` |
| B04 | SUCCESS | `STRUCTURAL_COVERAGE_FAILURE` |
| B05 | AXIOM_CAPABILITY_GAP (runtime input-dependent filter) | `BEHAVIORALLY_VERIFIED` |
| B06 | AXIOM_CAPABILITY_GAP | `STRUCTURAL_COVERAGE_FAILURE` |
| B07 | AXIOM_CAPABILITY_GAP | `STRUCTURAL_COVERAGE_FAILURE` |
| B08 | AXIOM_CAPABILITY_GAP (boolean) | `STRUCTURAL_COVERAGE_FAILURE` |
| B09 | BLOCKED_BY_GAP -> B08 | `STRUCTURAL_COVERAGE_FAILURE` |
| B10 | AXIOM_CAPABILITY_GAP | `STRUCTURAL_COVERAGE_FAILURE` |
| B11 | BLOCKED_BY_GAP -> B08 | `STRUCTURAL_COVERAGE_FAILURE` |
| B12 | BLOCKED_BY_GAP -> B08 | `STRUCTURAL_COVERAGE_FAILURE` |
| B13 | BLOCKED_BY_GAP -> B08,B07 | `STRUCTURAL_COVERAGE_FAILURE` |
| B14 | LYKOI_CAPABILITY_GAP | `STRUCTURAL_COVERAGE_FAILURE` |
| B15 | BLOCKED_BY_GAP -> B14,B08 | `STRUCTURAL_COVERAGE_FAILURE` |
| B16 | AXIOM_CAPABILITY_GAP | `STRUCTURAL_COVERAGE_FAILURE` |
| B17 | NOT_EVALUATED (prospective analysis only) | `NEEDS_CLARIFICATION` |
| B18 | NOT_EVALUATED | `UNSUPPORTED_BDI_SCOPE` |
| B19 | NOT_EVALUATED | `STRUCTURAL_COVERAGE_FAILURE` |
| B20 | NOT_EVALUATED | `NEEDS_CLARIFICATION` |

## Capability-by-case matrix

**S** = required/supported concept in an existing profile; **I** = required concept exists but integration is missing; **M** = required semantic composition missing; **U** = uncertain authority; **—** = not required by the local change.

S is never shorthand for whole-case success. E.g. query normalization does not implement mutation-time trimming, and a read-only `strings` view does not implement persistent append. I may coexist with a deeper M prerequisite, detailed in the report. Rows describe local demands; cumulative inherited demands are explicit dependency edges instead of twenty repeated supersets.

| Capability | B01 | B02 | B03 | B04 | B05 | B06 | B07 | B08 | B09 | B10 | B11 | B12 | B13 | B14 | B15 | B16 | B17 | B18 | B19 | B20 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Enum evolution / verbatim optional scalar fields | I | — | — | I | — | I | — | — | — | I | — | — | — | — | — | I | I | — | — | I |
| Runtime string equality predicate | — | — | — | — | S | S | — | — | — | S | — | — | — | — | — | — | — | — | — | S |
| Runtime string-list membership predicate | — | — | S | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| Explicit exact/case-sensitive comparison | — | S | S | — | S | S | — | — | — | S | — | — | — | S | — | S | S | — | — | S |
| Create-time trim / optional presence / validation composition | — | M | — | — | — | M | M | — | — | M | — | — | — | — | — | — | — | — | — | — |
| Nonblank rejection and declared errors | — | S | S | — | — | — | S | — | — | S | — | — | — | — | — | S | — | — | — | S |
| Deterministic key ordering and unique tie break | S | — | S | S | S | S | — | S | S | S | — | S | — | — | — | S | — | S | — | S |
| Ordered scalar collections in persisted records | — | I | — | — | — | — | I | — | — | — | — | — | — | I | — | — | — | — | I | I |
| Stable first-occurrence dedup / append / set update | — | M | — | — | — | — | M | — | — | — | — | — | — | M | — | — | — | — | — | M |
| Input/insertion-occurrence ordering (not key sorting) | — | M | — | — | — | — | M | — | — | — | — | — | — | M | — | — | — | — | — | — |
| Boolean task fields / inclusion store integration | — | — | — | — | — | — | — | I | I | — | I | I | I | — | — | — | — | — | — | I |
| Positive integer input / nullable integer state | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | M | — |
| Nullable timestamp storage / legacy clock exclusion | — | — | — | — | — | — | — | — | S | — | — | S | — | — | — | — | — | — | S | — |
| Temporal range / null-aware runtime predicates / date arithmetic | — | — | — | — | — | — | — | — | M | — | — | I | — | — | — | — | — | — | M | — |
| Compound AND/OR/NOT or scalar-in-set predicates | — | — | — | — | — | — | — | I | M | — | M | M | I | — | M | — | M | — | — | M |
| Create/update/delete and lifecycle, simple guards | S | S | — | S | — | S | S | S | — | S | S | — | S | S | S | S | S | S | S | S |
| Read-only effect and whole-record/empty-list results | S | — | S | S | S | S | — | S | S | S | — | S | S | — | — | S | — | S | — | S |
| Normal query/model-state field binding | — | — | I | — | S | I | — | I | I | I | — | I | — | — | — | — | — | — | — | I |
| Identity references / dynamic existence / quantified relationships | — | — | — | — | — | — | — | — | — | — | — | — | — | M | M | M | M | — | — | M |
| Graph reachability / acyclicity / inverse-use guard | — | — | — | — | — | — | — | — | — | — | — | — | — | M | — | — | — | — | — | — |
| Multiple durable entity states | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | M | M | M | M | M |
| Data-dependent actor/owner/role authorization | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | M | — | — | M |
| Durable ordered events and transaction composition | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | M | M | — |
| Conditional copy/map/create with fresh resources | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | M | — |
| Literal field migration / single-store atomic persistence | S | I | — | S | — | S | I | I | — | S | — | — | — | I | — | S | S | S | I | S |
| Relation-aware conditional migration | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | M | U | — | — | — |
| Unresolved behavioral authority | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | U | — | — | U |

Generic aggregation, pagination, regex/prefix search and stable occurrence sorting of returned *records* are not required by this corpus's local clauses. Tag deduplication and note/dependency insertion order do require occurrence semantics for *values*.

First-result counts: {'STRUCTURAL': 16, 'SUCCESS': 1, 'FORMALIZATION': 2, 'BDI': 1}. Primary root classifications (nineteen blocked cases): {'STRUCTURAL_INTEGRATION_GAP': 4, 'MISSING_GENERAL_SEMANTIC_CAPABILITY': 11, 'BACKEND_INTEGRATION_GAP': 2, 'AMBIGUOUS_REQUIREMENT': 2}.
