# R5.103 — Fresh typed corpus rebaseline and bounded existing-semantic closure

**Final classification: `R5_103_FRESH_TYPED_CORPUS_REBASELINED`.**

All twenty exposed cases have fresh current-system source interpretations and
normal reconciliation/coverage evaluation. **B01, B04 and B05 reach actual
behavioral success.** The new baseline is **3 successes / 14 structural blockers /
1 BDI blocker / 2 clarification blockers**. Every unexecuted downstream stage is
explicitly `NOT_REACHED`. This is requirement-local development/regression
evidence, **not held-out generalization or cumulative Phase 5C achievement**.

## Evidence and reproducibility

1. Twenty exact producer captures and FRCs: `R5_103-B01-CANDIDATE.json` through
   `R5_103-B20-CANDIDATE.json` in this directory. Each includes the exact source
   bundle, source-file SHA-256s, typed relations, contextual model authority and
   unresolved questions. [Fresh capture source](R5_103-corpus.py) imports no old
   evaluation/capture generator.
2. [Initial pre-repair evidence](R5_103-INITIAL-EVIDENCE.json) and
   [final current evidence](R5_103-FINAL-EVIDENCE.json) include native formalization,
   source-only inventory, reconciliation, full controller audits, structural
   projections/coverage, all reached downstream artifacts, preauthor source-side
   plans, compilation and external process observations.
3. [Fresh matrix](R5_103-CAPABILITY-MATRIX.md),
   [three-round progression](R5_103-PROGRESSION.md) and
   [machine-readable summary](R5_103-SUMMARY.json) are derived from those records.
4. [Existing-semantic inventory](R5_103-EXISTING-SEMANTIC-INVENTORY.md) and
   [versioned composition rules](../../../docs/existing-semantic-composition-v1.md)
   explain executable origins and qualified interactions.
5. [Synthetic closure evidence](R5_103-SYNTHETIC-EVIDENCE.json) publishes four
   additional source-bound normal chains, **78 external invocations**.
6. [Final verification](R5_103-FINAL-VERIFICATION.json) records **328/328 tests**,
   canonical validation and safety, all commands exit 0. Earlier
   `R5_103-VERIFICATION.json` is the intermediate 327-test implementation check.
   The [final audit](R5_103-FINAL-AUDIT.json) binds preservation, candidates and
   whitespace/change scope.

With PowerShell from the repository root, `PYTHONPATH='src;.'` is needed when
executing these evidence scripts by pathname (the workspace root supplies the
`benchmark` package). The evaluator uses exclusive output creation; to repeat a
published run, use a disposable checkout/output location rather than overwrite
evidence. Ordinary verification can be repeated with a fresh result label:

```powershell
$env:PYTHONPATH='src;.'
python benchmark/results/phase5c/R5_103-verify.py RECHECK
```

## Fresh formalization and authority

The active `openai/gpt-6.1-sol` agent inspected all twenty frozen requirement
sources, the baseline and common requirement authority. Prior requirement text is
explicit context for precursor demands, not a fabricated achieved precursor model.
Attempts remain local against the canonical baseline, as in the historical current
matrices; source requirements are cumulative, but these results do not establish
their cumulative achievement.

Each source bundle is freshly interpreted at the ModelAdapter producer boundary.
No middle FRC/projection/receipt is injected. The normal Workspace validates
producer output, commits a candidate-blind source-side inventory, reconciles
domains and material obligations, and requires exact synthetic owner approval
before the pipeline's WHAT seal. Blocking questions prevent that approval.
The inventory uses explicit whole-source spans for inherited context; candidate
quotes identify the local requirement or whole baseline/restated authority.

Supported meanings use current typed scalar, CollectionQuery and existing-model
amendment facets. Unsupported behavior uses structured
`required_capability/specification` objects in the existing FRC envelope. Those
objects are inspectable source-side demands **without executable semantics**;
coverage refuses them. They are not prose captures, accepted program operators,
or a new semantic family disguised as metadata.

**Evidence limits:** source extraction, inventory and literal oracles share this
agent; ModelAdapter replays its newly captured outputs. Producer-role separation
is not independent cognition. Owners/reviewers use synthetic credentials, not
actual human semantic approval. The implementation/external processes execute
normally; the round does not measure general English formalization accuracy.

### Ambiguity

- **B17 remains clarification-blocked:** role on creation defaults USER, and
  system is ADMIN, but the source does not determine migration of an existing
  non-system user. No migration value was borrowed from an implementation/oracle.
- **B20 remains clarification-blocked:** the nonexistent member-user application
  error and applicability of the task-named common missing-ID rule need explicit
  authority. No error was inferred to make a benchmark pass.

The native reconciliation outcome is `DISPUTED` with retained blocking questions
and unresolved ambiguity issues; the first-blocker category is formalization/
clarification. Neither reaches structure. No newly identified material source
ambiguity is silently resolved. B01 uses the baseline's explicit creation and
legacy-migration rules; it does not authorize arbitrary current-schema repairs.
CRITICAL's placement follows the declared enum ordering, while task lists retain
baseline created_at/id ordering; no new priority-sorting operation is claimed.

## Separating stale-capture effects from repairs

The **complete pre-repair fresh run already succeeds on B01/B04/B05** using the
unchanged R5.102 implementation. Relative to R5.102, **one case, B01**, changes
first result solely because fresh typed enum/default/evolution facts replace
stale prose-shaped relations. This is existing-support reachability, not a new
semantic operator or an R5.103 repair success. B04's equivalent improvement was
already recorded in R5.102; B05 was already successful in R5.101.

Generic repairs then pass separate source-authorized synthetic challenges.
**Zero additional corpus first-blocker changes are attributable to those repairs.**
They close useful seams but do not remove the corpus's missing prerequisites.
B12/B13 final captures re-emit clock/guard portions through the newly integrated
typed amendment route; source meaning is retained, and their first results remain
structural. Both now expose the actual missing `archived` binding, with other
material demands still present. Initial and final records are separately retained.

| First-blocker category | R5.101 | R5.102 | R5.103 |
| --- | ---: | ---: | ---: |
| Formalization/clarification | 2 | 2 | **2** |
| Structural | 16 | 15 | **14** |
| BDI | 1 | 1 | **1** |
| Success | 1 | 2 | **3** |

**B01 alone newly reaches BDI, adequacy, V1, authoring, compilation, runtime and
external verification relative to R5.101/R5.102 current matrices.** B18 already
reached BDI; B04/B05 already reached all later stages in R5.102.

## Existing seams additionally closed

- **Guard amendments:** typed equality guards on existing lookup updates/deletes,
  preserving existence-first order, prior lifecycle-state guards/errors and
  unchanged rejected state. Contradictory guards refuse. The standalone
  `existing-model-1` route preserves prior model authority without demanding
  unrelated scalar restatement.
- **Guarded additive inputs:** source-declared nonblank guards/errors on new
  required scalar inputs and existing timestamp-input guards bind through model
  evolution. Presence-aware optional nonblank semantics remain unsupported.
- **Clock-relative reads:** existing `field_before_clock`, timestamp null exclusion,
  `field_equals` and existing conjunction lower normally with exact clock/resource
  authority, whole-record results, identity-tied order and no writes. Exact
  past/equal/future/null/terminal-state boundaries are externally challenged with
  the existing public `clock` API. This does not add a temporal predicate family.
- **Creation providers:** normal generated API binds UUID/UTC callables by declared
  capability ID. Deterministic ID/time, collision rejection, unauthorized/invalid
  provider refusal, unchanged storage and binding reset/default behavior are
  tested in separate processes. No resource kind or injection CLI is added.
- **Mixed profiles:** complete scalar facets plus read-only query groups bind one
  actual derived model-state under `existing-composed-1`. Type/identity/namespace/
  effect checks precede coverage; existing query-policy BDI decisions are retained.
- **Independent lifecycle composition:** the normal lowerer now uses existing
  literal-assignment guarantees for multiple initialized lifecycle fields. Two
  independent single-transition fields coexist and preserve one another.

No compiler validator/runtime-template/schema primitive was extended. No canonical
model, generated historical application, requirement, oracle or historical result
was modified. New executable targets are normal compiler output in temporary
directories. The normal product dispatcher and typed integration modules contain
no B01–B20 IDs, source-word dispatch or benchmark-specific operation.

## Behavioral verification

| Successful local case | External invocations | Observed behavior |
| --- | ---: | --- |
| B01 | **18** | CRITICAL acceptance/persistence, exact HIGH partition, unchanged LOW/NORMAL/HIGH migration, omitted creation/legacy priority NORMAL, list/reload, missing/invalid storage and baseline rejection preservation |
| B04 | **21** | Verbatim/omitted/explicit-empty source, reload, whole-record list/high/overdue, complete/delete preservation, explicit migration/idempotence, invalid input and missing-ID rejection |
| B05 | **8** | Exact pending/completed partitions, whole-record normal/tie order, empty/no-match/missing/invalid-store paths and unchanged bytes/absence |
| **Corpus total** | **47** | All three actually author/lower, compile, run and pass sealed external plans |

Four separately published synthetic closure chains add **78** observations, for
**125 published external CLI invocations** total. Supplemental deterministic API,
guard/evolution/two-lifecycle tests and the current regressions are additional
checks, not added to that published invocation denominator.

The R5.102 isolated Unicode stdout failure after successful persistence is
preserved. No R5.103 actual corpus execution hits that issue: the behavioral
inputs are ASCII/whitespace. It is neither repaired globally nor counted as a
semantic success. No environment encoding or runtime portability changes occurred.

## New first-blocker distribution

| Category | Count |
| --- | ---: |
| Formalization/clarification | **2** |
| Structural | **14** |
| BDI | **1** |
| Adequacy | **0** |
| Representation / V1 | **0** |
| Lykoi semantics (separate reached-stage failure) | **0** |
| Authoring | **0** |
| Compilation | **0** |
| Runtime | **0** |
| Behavioral verification | **0** |
| Success | **3** |

No author-plan/tooling blocker remains. Zero in a downstream column is **not**
evidence that its unsupported cases would succeed; those stages are `NOT_REACHED`.

## Recomputed capability clusters

Primary classes are mutually exclusive counts; underlying demands overlap.
They are recomputed from fresh sources/native evidence, not inherited labels.

| Primary class | Cases | Count |
| --- | --- | ---: |
| Missing semantic family/composition | B02, B06, B07, B09, B10, B11, B12, B14, B15, B16, B19 | **11** |
| Backend/store prerequisite gap | B03, B08, B13 | **3** |
| BDI gap | B18 | **1** |
| Ambiguity | B17, B20 | **2** |
| Existing-semantic integration gap (primary remaining blocker) | None in this corpus | **0** |
| Representation gap (first reached blocker) | None | **0** |
| Success | B01, B04, B05 | **3** |

Backend/store labels are not proof of an orphaned executable write capability:
tags/notes require a missing writable array algebra; archived requires a missing
writable boolean algebra. B03's membership semantics and B13's simple guard
semantics already work generically, but their actual store prerequisites do not.
Full-profile closure outside these qualified interactions is not established.

Remaining missing-family structural demands are: mutable values/transforms
(B02/B06/B07/B10); temporal ranges/compound predicates (B09/B11/B12); relationships,
graph and quantified related-record guards (B14/B15/B16); and nullable integer/
calendar arithmetic/atomic successor effects (B19). B18 reaches native BDI refusal
for the external-effect channel before its further durable-event/atomic-effect
demands can be evaluated downstream. Its structural pass is explicitly bounded,
not full understanding of audit semantics.

### R5.104 recommendation — one family, not implementation

Recommend **typed mutable values and transformations** as the single primary next
family. The tightly evidenced direct demand set is **B02, B03, B06, B07, B10**:
ordered persisted string values, repeated input, explicit write normalization,
presence/validation, stable deduplication and append would expose existing query
semantics and mixed normal-path authoring. This is five directly affected local
requests, **not a promise of five successes**. B14/B15 have dependency-value
prerequisites that this family could expose, but still need relationship semantics.
Writable boolean/numeric types are neighboring write-algebra gaps; they should be
scoped explicitly rather than automatically bundled into the recommendation.

This family is preferable now to:

- **Predicate composition:** directly important to B09/B11/B12, but archive
  storage remains absent, and two require temporal/in-set machinery beyond OR.
  Closing only predicates would leave substantial write prerequisites untouched.
- **Relationships:** important to B14/B15/B16 and downstream ambiguous B17/B20,
  but depends on writable identity values and introduces multi-entity/graph/
  quantification interactions. The smaller value/transform base is a useful
  architectural prerequisite and broadly useful outside this corpus.
- **Atomic effects:** B18/B19 are valuable, but add durable events, event-decision
  discovery and multi-state successor/arithmetic dependencies. They reach fewer
  direct local requests and sit on more missing foundations.

Typed mutable values are useful for labels, notes, histories and identifier
collections across software domains, and remove concrete blockers in front of
already-executable query/guard/profile machinery. No new held-out generality claim
follows from that diagnostic prioritization. **R5.104 is not begun.**

## Completion answers

1. **Fresh representation alone changed one result: B01.**
2. **Closed seams:** existing equality/lookup guards, newly added required-input
   guards, before-clock/equality-conjunction read projection, deterministic declared
   creation-resource binding, bounded scalar/query and independent-lifecycle composition.
3. **Three behavioral successes: B01/B04/B05.**
4. **Distribution:** 2 clarification, 14 structural, 1 BDI, 3 success; all other
   requested first-blocker categories zero.
5. **First-time BDI:** B01 relative to both previous current matrices.
6. **First-time adequacy/V1/authoring:** B01; it also compiles/runs/verifies.
7. **Genuinely missing structural families:** the eleven cases listed above;
   several also have missing store prerequisites.
8. **Remaining backend prerequisites:** B03/B08/B13. No primary remaining
   existing-semantic integration-only blocker is measured in this corpus.
9. **B17/B20 remain ambiguous and unanswered.**
10. **Existing profiles compose within qualified one-state read/write boundaries,**
    with explicit compatibility checks, conflict refusal and unsupported-interaction
    refusal. Arbitrary profile union is not supported.
11. **Recommend typed mutable values and transformations for R5.104.**
12. **Why:** five directly affected cases, useful general value operations,
    architectural prerequisites and meaningful already-supported downstream stages.
13. **No major new semantic family introduced.** No append/dedup/set mutation,
    OR/NOT/ranges, relationship/effect/arithmetic/successor behavior was implemented.
14. **Infrastructure work avoided.** No OpenCode/model/transport/runtime
    qualification, portability, research freezes or benchmark-firewall work.

Historical Phase 5, R5.97 B03 first result, R5.101 and R5.102 remain unchanged.
Stop after this fresh baseline and next-family recommendation.
