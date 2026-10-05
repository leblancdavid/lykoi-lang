# R5.82 — Behavioral decision discovery and coverage qualification

## Result and central answer

**`R5_82_BEHAVIORAL_DECISION_DISCOVERY_PARTIAL`**.

Systematic discovery is useful **within reviewed structural interface scope**:
15 bounded rule families find 25/25 expected supported-family decisions without
the downstream implementer composing the inventory. Two finite-domain interaction
analyses derive tie and normalization-collision reachability mechanically. The
experiment does not yet discover a complete BDI from arbitrary reviewed FRC text:
annotation, consumer scope, temporal reachability and inventory completeness remain
reviewer dependent. Four expected timing/identity/event decisions are missed.
No isolated review or independently produced plan evidence is established.

Discovery is a separate stage between reviewed FRC and R5.81 adequacy. Finding a
choice neither alleges a defect nor supplies authority. Projection, Lykoi capability
and implementation verification retain their own gates. Stop after R5.82.

## Deliverables

| Deliverable | Artifact |
| --- | --- |
| Versioned BDI, relevance, observations, implication scope and methodology | [Behavioral Decision Inventory 0.1](../../../docs/behavioral-decision-inventory-v0.1.md) |
| Pure structural rules, finite implications, R5.81 adapter | [behavioral_discovery_r5_82.py](../../evaluation/behavioral_discovery_r5_82.py) |
| Public synthetic sources/interfaces | [corpus.json](r5_82/corpus.json) |
| Separate manual expectations, witnesses, irrelevant choices, correction history | [expected.json](r5_82/expected.json) |
| Per-case BDIs, coverage, hidden cases, mutations, plans, adequacy and B01 reproduction | [experiment.py](r5_82/experiment.py), emits full JSON to stdout |
| Compact observed evidence and protection accounting | [results.json](r5_82/results.json) |
| Independent-review status and coordinating review findings | [review.json](r5_82/review.json) |
| Mechanical qualification tests | [test_behavioral_discovery_r5_82.py](../../evaluation/test_behavioral_discovery_r5_82.py) |
| Commands and evidence limits | [README](r5_82/README.md) |

## Discovery representation and supported scope

BDI identities are stable `operation:family` pairs, with contract/interface
commitments, originating obligations/interface declarations, rule conjunction,
alternative probes, consequence, channel, reachability/evidence and optional
separate authority. Exclusions and missing facts/channels are retained. Algorithm
notes never become decisions merely because code strategies can differ.

Supported families: **ordering, selection, cardinality, ties, optional inputs,
nullable predicates, default trigger domain, normalization, normalization collisions,
invalid inputs, duplicates, persistence, transitions, retries and failure atomicity**.
These are experimental discovery categories, not language or V1 semantics.

The synthetic capsules are public source/interface abstractions, not new approved
FRC-0.1 receipts. Their structural facts are supplied by coordinating manual analysis.
The engine combines facts mechanically; it does not infer all facts from prose.
Origins distinguish interface declarations from actual obligation IDs. This limitation
is central: rule prerequisites such as poststate admission, failure after writing
and historical absence still require upstream structural justification.

### Necessary implication and reachability

Structural conjunctions expose interactions without prescribing solutions. Exactly
one selection plus multiple eligible matches raises ties; creation default plus
admitted historical absence raises default trigger scope; transition plus admitted
poststate and repeated invocation raises retry; failure after durable write raises
failure atomicity visible through subsequent reads.

These are **bounded structural heuristics** until reachability is justified. Two
finite mechanisms additionally derive facts from declared exhaustive domains:

1. Enumerated eligible score states detect repeated maxima or prove their absence
   over exactly that domain. Positive witness `[7,7]`; unique-max domain excludes ties.
2. Enumerated strings under exact lowercase transformation detect distinct-input
   collisions or prove injectivity on that domain. Positive witness `A/a`; already
   lowercase domain has neither collisions nor a distinguishable normalization choice.

Four finite probes match their expected inventories, two positive interaction
discoveries and two negative domain checks. Exhaustiveness is an assertion about
the admitted finite interface, not inferred from human prose. Contradictory facts,
nonexhaustive finite domains and noncanonical numeric evidence reject. There is no
general logical completeness, SMT reachability, invariant induction, concurrency
or arbitrary trace solver.

Evidence classification: all **25** main-corpus discoveries are mechanically fired
rules over **reviewer-supplied structural facts** (`BOUNDED_STRUCTURAL`); **2**
additional finite interaction entries are `MECHANICALLY_DERIVED_FINITE`. The **4**
unsupported expected entries are reviewer-derived, not mechanical discoveries.
No general logical implication is qualified.

Supported structural inhibitors reject unique-max ties, non-null predicate branches,
historical missing fields under complete-history scope, injective collisions,
single-invocation retries and post-write failures under before-write-only failure
scope. No undeclared invariant is assumed. For general temporal history these are
attestations, not mechanically proved reachable-state sets.

### Consumer observation scope

Meaningful return values/membership, sequence order, errors and later state/results
are supported rule channels. Declared timing, identity and event channels are
recognized as unsupported, producing unknown coverage rather than an adequate result.
Other channels can be declared but are not discovery-qualified.

`DELEGATED` physically visible ordering remains in the BDI. `EXCLUDED` private
iteration order is rejected with provenance. Missing channel semantics remain unknown.
Singleton and identical-element collections do not produce ordering decisions.
Private algorithm/cache variation is rejected. Explicit freedom cannot be inferred
from silence and does not erase a decision or an unrelated membership requirement.

## Corpus, coverage and correction disclosure

26 public synthetic cases cover the requested scalar, collection, optional/null,
history, input, state, retry, failure, invariant, freedom and internal-choice classes.
Manual expected inventories live separately from the engine and were initially
written before invoking it. They share the coordinating author/context, not an
independent reviewer. Their exact family identities require no equivalence remapping.

| Measure | Final observed result |
| --- | --- |
| Expected decisions, revision 2 | 29 |
| True positives | 25 |
| False positives | 0 |
| False negatives | 4 |
| Expected supported-family coverage | 25/25 |
| Enumerated irrelevant choices correctly rejected | 12/12 |
| Unresolved independent-review disagreements | No independent reviewer; questions unadjudicated |

Missed entries are deadline boundary, identity stability, event order and event
multiplicity. These remain in expectations rather than disappearing to improve
coverage. Unsupported channels are flagged but their decisions are not discovered;
an unknown warning is not counted as a true positive.

**One post-result expected correction is disclosed.** Revision 1 wrongly expected
normalization for already lowercase inputs, where raw and normalized observations
coincide. The initial measurement was **26 TP / 0 FP / 4 FN, 30 expected, 11 irrelevant
rejections**. Revision 2 removes that entry, adds it to irrelevant choices, and the
engine now excludes identity transforms. This is a coordinating semantic correction,
not independent review; original numbers and original expected entry are preserved
in the records. An `order_varies` prerequisite also prevents blindly treating every
multi-element collection as a variable ordering decision. Metrics remain development
evidence, not a general completeness rate.

## Hidden-decision challenge

| Interaction | Discovered target | Scope/witness |
| --- | --- | --- |
| Selection + exactly one + repeated maximum | tie | a/b both score 7 |
| Creation default + historical missing field | default_trigger_domain | stored sensor reading lacks unit |
| Lowercase + uniqueness + admitted case variants | collision | A/a normalize to a |
| Transition + repeat + admitted poststate | retry | close already-closed record |
| Nullable field + predicate | nullable_predicate | null price changes selected membership |
| Persistence + later failure + subsequent read | failure_atomicity | notification fails after storing v=2 |

All **6/6 target interactions** are found. Five additional selection/cardinality,
normalization, transition and persistence entries are also found. No target policy
is resolved by discovery. Negative invariant/private-scope variants resist the
corresponding false positives.

## Mutation qualification

Eight semantic mutations and three negative hint/metadata mutations behave as
expected (**11/11**, zero unexpected added or missing decision deltas):

* Removing the selection declaration removes selection/cardinality/tie candidates.
* Weakening unique-match invariant adds tie.
* Broadening omission admission adds optional-input handling.
* Removing non-null precondition exposes nullable predicate behavior.
* Permitting duplicate inputs adds multiplicity handling.
* Changing exactly-one cardinality removes its cardinality/tie candidates.
* Exposing formerly private order adds ordering.
* Removing explicit freedom keeps the ordering decision but removes authority.
* Loop/recursion hint, container hint and nonsemantic metadata leave inventory unchanged.

These mutate structural capsules and annotate prospective source changes; they are
not independent fresh formalizations of mutated natural language. Mutation success
does not prove English extraction or hidden-decision completeness. Detailed deltas
are reproducible in `experiment.py`.

## Differential plans and independence

Six separately described residual strategy pairs predict five observable divergences:
first/last maximizer, default/reject historical absence, reject/merge collision,
idempotent/reject retry, rollback/retain write on failure. **5/5 corresponding decisions
are in the BDI.** Direct addition versus sequence sum predicts internal agreement.

These are same-context declarative plans and output predictions, not executed complete
implementations and **not independently produced plans**. Their agreement is not proof
of completeness; their differences illustrate already-inventoried choices. The
independent-plan requirement remains unqualified rather than being simulated with
different author labels.

Ordinary coordinating discovery attempts **1**; ordinary mechanical reruns separately
recorded; context-isolated **0**; provider/model-isolated **0**; strict-isolation-qualified
evidence **0**. No external reviewer run or controlled isolated environment was
established. The independent-review record explicitly says **NOT_PERFORMED**. Shared
context expectations and rules, prior B01 knowledge, and declaration trust prevent
strong independent qualification.

## R5.81 integration and B01 calibration

The unchanged R5.81 analyzer consumes adapted discovered entries:

| Local probe | R5.81 result |
| --- | --- |
| Exactly two fixed records; any permutation explicitly authorized | IMPLEMENTATION_ADEQUATE |
| Same order choice; no supplied order authority | IMPLEMENTATION_UNDERSPECIFIED |
| Delegated order; coverage not reviewed | OUTSIDE_ANALYSIS_SCOPE |

The positive finite domain is exactly forward/reverse for two distinct fixed records,
not all collection permutations or an entire application. The adapter defaults to
unreviewed coverage; probe labels are not automatic exhaustive adequacy domains.
No actual fidelity approval or implementation grant is issued.

Only exact already-public R5.80 B01 candidate information is loaded. The generic
default/history rule also exercised by sensor-reading examples finds
`priority-lifecycle:default_trigger_domain`, with **B01.O07/O08/I1** provenance.
It records creation-only versus historical-absence trigger alternatives, without
choosing either. R5.81 integration retains **NEEDS_CLARIFICATION / unauthorized**.

This is **conditional discovery, not independent elicitation**: the coordinator knew
the earlier finding and the annotation references B01.I1. Historical missing-field
admission is unresolved, not a newly established baseline invariant or state.
The successful claim is that a general rule reproduces the conditional decision;
the requested independent rediscovery criterion is not qualified. Full B01 interface
inventory and source fidelity remain unqualified; no baseline/oracle/implementation
or consumer is consulted to resolve the default.

## Verification, boundaries and stop

New discovery checks **16/16 PASS**; unchanged R5.81 **18/18 PASS**; unchanged R5.80
**18/18 PASS**; guarded V1 **33/33 PASS**; ordinary compiler/application **31/31 PASS**.
The initial new suite passed 12/12; the intermediate finite-domain suite passed
14/14 plus 18/18 unchanged adequacy checks. Final compact reproduction confirms
25 TP / 0 FP / 4 FN, 12 irrelevant rejections, 11 mutation passes, four finite-domain
matches and the stated adequacy/B01 outcomes. `git diff --check` passes. Commands
are in the README.

Lykoi model/compiler/runtime/schema, generated artifacts, V1, frozen requirements,
oracles, runner and prior evidence are preserved. No additional projection, support
classification, held-out experiment or semantic extension follows; inherited core
**30**, B02 exposed/indeterminate history and paused Phase 5C remain.

**B03_PRISTINE / B03_NOT_EVALUATED /
B03_NOT_EXPOSED_TO_LYKOI_DEVELOPMENT**. B03 source attempts/reads, content-revealing
metadata, discovery, adequacy, authorization, packaging, opening, consumer observation,
generation, execution, acceptance and repair counters are **all zero**. This is
scoped session accounting with inherited pristine status, not an inspection of any
protected ledger or content. No other held-out requirement is accessed.

**Final: R5_82_BEHAVIORAL_DECISION_DISCOVERY_PARTIAL. Stop after R5.82.**
