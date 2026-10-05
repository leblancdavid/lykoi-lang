# Implementation Adequacy v0.1 — R5.81 experiment

## Boundary and authorization

Pipeline: Human Requirement → Requirement Formalization → Reviewed FRC →
Implementation-Adequacy Gate → Lykoi authoring → validation/lowering → software.
Fidelity approval says that the FRC preserves its source. It does not say that
the source supplied sufficient behavioral authority. Neither approval nor V1
representability alone authorizes authoring. This prospective experiment grants
no actual benchmark authoring authority.

An adequate contract determines or explicitly delegates every required,
contractually meaningful behavioral decision within a reviewed scope. Multiple
implementations are welcome: differences must fall within authorized freedom.
Literal consistency with an incomplete contract is insufficient authority.

## Bounded relevance and observable-decision analysis

1. Freeze source, FRC, interface, admitted inputs/initial states, environmental
   preconditions, temporal horizon and consumer observation contract.
2. Trace each operation from admissible input through result, errors, effects and
   later observations. Identify decisions needed to execute each reachable branch.
3. For each proposed relevant decision give a reachable distinguishing witness:
   two choices change a required observation or an observation whose freedom has
   not been authorized. Link it to source/context; distinguish obligation from
   interface-imposed choice. An ordered result interface can require an ordering
   choice even when the source is silent about which order.
4. Ask whether authority determines the choice, delegates a nonempty allowed set,
   expressly excludes the observation, or accidentally omits a decision. A source
   quote or reviewed necessary implication is required for delegated freedom.
5. Check cross-decision constraints, frame/temporal requirements and conflicts.
   If these cannot be analyzed, return OUTSIDE_ANALYSIS_SCOPE. Do not pretend
   independent finite choice domains model concurrency or coupled constraints.
6. A reviewer signs off the inventory's coverage and exclusions. Mechanical
   checking cannot discover an omitted inventory entry from natural language.

Ordering, ties, defaulting, invalid input, duplication, normalization, effects,
persistence, atomicity, repetition, cardinality and boundaries are elicitation
prompts, not universal obligations. Pure arithmetic needs no storage policy.
Impossible states under authorized preconditions need no decision. Preconditions
may not be invented to exclude a difficult case. Exclusions must match the
requested implementation scope: an abstract integer interface approval does not
authorize a production CLI with unspecified parsing or error behavior.

## Freedom, omission and observation

Internal algorithms, containers and temporary variables are free when they cannot
change contractually relevant observations. Memory limits, timing or durable bytes
make these relevant only if the declared architecture/contract requires them.

Explicitly unconstrained in-domain behavior can authorize implementation if the
source deliberately delegates it, the range and temporal scope are defined, it
does not contradict another obligation, and consumers are told what they may
rely on. For example, any ordering with stable ties is a bounded delegation;
any permutation with callers forbidden to rely on order is an explicit freedom.
Physical serialization order remains visible, but exact sequence equality is
not a valid consumer demand under that observation contract. Membership and
multiplicity remain binding. Stability is not implied by freedom over order.

Silence does not create either delegation. An FRC-0.1 `unspecified` entry is not
automatically authority: distinguish source-declared freedom, out-of-domain
behavior, and a formalizer's report of missing authority. R5.80's open-world
literal trace semantics is preserved; a literal trace may be allowed while the
separate implementation-authority gate still blocks choosing it.

Explicit freedom cannot waive another actual requirement, safety invariant,
frame or downstream consumer obligation. Unresolved scope, stakeholder conflict,
or unsupported freedom semantics blocks the gate.

## Experimental machine-readable model

`ImplementationAdequacy-0.1` is a sidecar, not a Lykoi or FRC/V1 extension.
The executable shape is illustrated by `r5_81/corpus.json`. Each analysis contains
`scope`, `coverage_reviewed`, `supported`, `issues`, and `decisions`. A decision
has a stable `id`, `relevance` (REQUIRED, INTERNAL, EXCLUDED), a `reason`, finite
`options`, and zero or more `clauses`. Clauses contain `authority` (DETERMINED,
DELEGATED, UNCONSTRAINED), `allowed`, and exact `source_quote`. All clauses on a
required decision apply simultaneously; their intersection must be nonempty.
Unconstrained means the entire declared domain. Internal/excluded decisions do
not require clauses but do require reviewed relevance rationales.

This finite independent-decision profile checks absence of authority and empty
intersections, not whether an arbitrary choice is executable or textually faithful.
Inventories, domains, witness reachability, quotes' semantic relevance, consumer
obligations and independence of decisions remain reviewer judgments. Unsupported
or unreviewed analysis fails closed. A false reviewer attestation cannot be
detected by hashes. No general completeness solver or signed trust system exists.

| Status | Meaning |
| --- | --- |
| IMPLEMENTATION_ADEQUATE | Every reviewed relevant decision has consistent authority within this bounded profile. |
| IMPLEMENTATION_UNDERSPECIFIED | At least one required decision has no authority. |
| NEEDS_CLARIFICATION | An unresolved interpretation/authority question blocks the analysis. |
| CONFLICTING_REQUIREMENT | Simultaneous finite obligations have empty intersection, or a reviewed conflict is recorded. |
| OUTSIDE_ANALYSIS_SCOPE | Unsupported, malformed, stale or unreviewed evidence; no positive conclusion. |

Underspecification returns `next_action: NEEDS_CLARIFICATION`; ambiguity directly
returns NEEDS_CLARIFICATION. This separates diagnosed absence from unresolved
interpretation without pretending they are mutually exclusive research concepts.
Conflict precedes ambiguity, then unsupported analysis, then missing authority.
All blockers are retained in findings. Authorization additionally requires a
separate APPROVED fidelity receipt bound to the exact FRC and an adequate sidecar
bound to that same FRC. Receipts are cooperative experimental bookkeeping.

## V1 and qualification limits

Adequacy is independent of V1 mapping. All four adequacy/representability
combinations are conceptually valid. A syntactically valid V1 document can omit
behavioral authority; syntax is not faithful complete projection. Adequate
abstract arithmetic can lack the prototype's qualified mapping. R5.80's 1/9
projection result remains unchanged. Existing component calibration is not
automatically adequate: complete decision coverage must still be reviewed.

This version qualifies bounded analysis only. General completeness, transport
refinement, coupled choices and production authoring enforcement remain gaps.
