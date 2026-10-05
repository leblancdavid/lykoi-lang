# Behavioral Decision Inventory 0.1 — R5.82 experiment

## Boundary and relevance

Pipeline: Human Requirement → Formalization → Reviewed FRC → **Decision
Discovery** → Implementation Adequacy → V1 projection when applicable → Lykoi
authoring → deterministic validation/lowering → verification of software.
These are separate questions and approvals. Discovery supplies choices, not
authority, projection, expressiveness, correctness or an implementation grant.

A behaviorally relevant decision is a choice an implementation potentially has to
make for an admitted operation/input/state, with two materially different outcomes
through a declared contractual observation channel. Analyze candidate alternatives
before applying behavioral authority: even determined selection/normalization and
explicitly delegated ordering belong. Authority may eliminate incorrect choices
or delegate them later. Discovery is not defect detection. Unreachable alternatives
and changes solely to private algorithms are excluded. Loop/recursion, containers,
helpers, names and unobservable caches are not inventory entries.

This experiment supports sequential abstract interfaces, reviewed structural facts
and two small exhaustive finite-domain analyses. It does **not** parse arbitrary
FRC prose or certify that an entire product's decisions have been found. Synthetic
contracts are source/interface capsules, not new independently approved FRC receipts.
The interface is a prospective sidecar; FRC-0.1, V1 and Lykoi are unchanged.

## Executable representation

`BehavioralDecisionInventory-0.1` contains `contract_commitment`,
`interface_commitment`, `decisions`, `exclusions`, `unknown`, and bounded `coverage`.
`benchmark/evaluation/behavioral_discovery_r5_82.py` defines the executable shape.
Each decision records:

| Field | Evidence purpose |
| --- | --- |
| `id`, `family`, `operation` | Stable `operation:family` identity; contract/interface changes change commitments, not these semantic identities. |
| `origins`, `facts`, `trigger`, `rule` | Named obligation/interface/domain provenance and the exact conjunction that fired. |
| `alternatives`, `consequence`, `channel` | Distinguishing behavioral probes and where consumers can distinguish them. |
| `observation_scope` | Meaningful, delegated or excluded observation treatment. |
| `evidence`, `reachability`, `witnesses` | Structural declaration versus finite mechanically derived implication; concrete finite witnesses when available. |
| `authority` | Optional separately encoded R5.81 clause; null denotes no supplied authority, not proof the source lacks authority. |
| `dependency` | Retry depends on transition; not a general coupled-decision solver. |

Finite alternatives are **probe labels**, not automatically an exhaustive behavior
domain. Separate local adequacy review must establish that a complete finite domain
and authority interpretation are valid before adapting. Generic discoveries must
not automatically be granted `coverage_reviewed=True`. Default adapter value is false.

Input operations have stable IDs, `facts`, `channels`, optional `authority` and
optional `finite_domain`. Facts carry `value`, nonempty `origin` and `evidence`.
Origins may name FRC obligations, declared interface facts, or an admitted domain;
synthetic capsules name their interface declarations rather than pretend to have
independently approved obligation IDs. Evidence provenance is attestational: the
checker does not prove that a quoted sentence entails the encoded value.

## Observation-scope model

Physical observation and authorized consumer distinction are separate. Supported
rule channels are `return` (value/membership/multiplicity), `order` (returned sequence),
`error`, and `later` (persisted state or subsequent operation result). The model can
also declare serialization, effects, timing, identity and events, but no discovery
rules for them are qualified here. Merely adding a channel does not add a rule.

* `MEANINGFUL`: consumer distinctions matter; silence about authority is unresolved.
* `DELEGATED`: visible choices exist and remain discovered; adequate delegation is
  checked downstream. Consumer exact-order dependence is not authorized.
* `EXCLUDED`: explicitly private or outside the declared contract observation scope;
  reject its candidate and record the exclusion. This is not a synonym for delegated.
* Missing channel: record UNKNOWN when an otherwise applicable candidate requires it.

DELEGATED requires source-supported freedom and a consumer restriction, not an
implementer's preference. EXCLUDED requires scope authority; physically visible public
order must not be excluded merely because the source is silent. Fixed return value
does not make private iteration order a returned-order observation. Timing only
matters when declared contractual; physical timing alone is insufficient.

## Discovery methodology and bounded implications

1. Bind exact FRC/source and declared operation/input/state/observation scope.
2. Review their structural annotation. Unknowns stay unknown; no invented invariant.
3. Apply relevant fact conjunctions. Keep traceable candidate, exclusion or unknown.
4. Challenge reachability with supported preconditions/invariants and, where available,
   exhaustive finite domains. Record distinguishing witnesses separately from authority.
5. Compare against an expected inventory written without invoking the candidate engine.
   Preserve disagreements and unsupported decisions. Expected inventory author identity
   and lack of isolation must be reported.
6. Probe alternative plans, mutate source/interface semantics, then feed reviewed
   inventories to R5.81. Never replace coverage review with a green metric.

| Family | Required interaction | Supported exclusion |
| --- | --- | --- |
| ordering | collection can return at least two distinguishable elements + order can vary + returned order channel | singleton/identical-elements bound/private channel |
| selection/cardinality | selection; exactly-one adds cardinality | not a selection operation |
| tie | selection + exactly one + multiple eligible matches | proved unique match/maximizer |
| optional | omitted input admitted + result observation | omitted input not admitted |
| nullable predicate | nullable field + predicate | non-null call precondition |
| default trigger domain | creation default + absent historical field + later observation | all admitted historical fields present |
| normalization/collision | transformation; uniqueness + colliding inputs adds collision | identity transform excludes normalization; injectivity excludes collision |
| invalid input | invalid values admitted at validation boundary | values outside implementation scope |
| duplicates | collection + duplicate inputs admitted | no admitted duplicate inputs |
| persistence/transition | durable write or state transition + later observation | later observation outside scope |
| retry | transition + repeated invocation + admitted poststate | authorized single-invocation precondition |
| failure atomicity | persistence + failure possible after write | all failures before write |

The rule table is relevance-sensitive, not an every-operation checklist. These
conjunctions are **bounded structural heuristics** when their facts are reviewer
supplied. In particular `failure_after_write`, `poststate_admitted` and historical
absence still require justified structural annotation.

Two implication checks are mechanical on **declared exhaustive finite domains**:

* Enumerate nonempty eligible score states. A repeated maximum establishes a reachable
  tie witness; absence of repeated maxima in every enumerated state proves unique
  maximizers **only for that finite domain**. This does not prove unique scores globally.
* Enumerate admitted strings under the exact `lower` transformation. Distinct values
  with equal transformed values establish a collision; no such pair establishes
  injectivity **only on that enumerated domain**. This is not general normalization.

Nonexhaustive domains and contradictions with structural declarations reject.
Numeric NaN/Infinity reject through canonical commitment. No general logical
entailment, symbolic invariant induction, concurrent reachability, environmental
failure modeling, arbitrary trace reasoning or free-text implication is supported.
Reviewer judgments and unsupported general reasoning must not be labeled mechanical.

## Coverage and adequacy integration

`r5_82/expected.json` is separate manual source/interface analysis. Compare exact
operation/family identity; no semantic-equivalence remapping was needed. Report TP,
FP, FN and enumerated irrelevant rejections; these are not universal precision/recall.
One post-result correction removes normalization for an already lowercase domain:
raw/normalized observations coincide. Original 30-entry expectations and 26 TP
measurement are preserved in the correction record and results; revised expected
total is 29. The corresponding identity-transform exclusion is now implemented.
Four expected decisions deliberately
remain missed, documenting timing/identity/event gaps. The corpus and rules share
one coordinating author/context, so measurements are development evidence.

The adapter binds the same contract and uses unchanged R5.81 authority checking.
An exactly-two-record local ordering probe returns adequate for explicitly free
order, underspecified for no order authority, and outside scope when coverage is
unreviewed. This does not qualify arbitrary discovered probe domains as complete.
B01 conditional discovery carries its unresolved issue to NEEDS_CLARIFICATION;
no authoring authority is issued. Full B01 inventory and admitted legacy-state
reachability remain unqualified.

**Status: experimental partial qualification.** Mechanically generating supported
inventories reduces implementer elicitation work once structural scope is supplied.
It does not remove upstream annotation, reachability, observation or completeness
judgment. No language/V1 change or protected held-out experiment is authorized.
