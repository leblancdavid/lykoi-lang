# R5.81 — Formal contract completeness and implementation adequacy

## Result and central answer

**`R5_81_IMPLEMENTATION_ADEQUACY_PARTIAL`**.

An approved FRC may authorize implementation only after a **separate scoped
adequacy determination** establishes that every relevant reachable behavioral
decision is determined or deliberately delegated by authority. A decision whose
choice changes contractual behavior and lacks authority must halt authoring for
upstream clarification. Reviewer uncertainty and unsupported analysis also halt.

R5.81 demonstrates this distinction for reviewed finite strategy domains. It
does not establish general completeness from arbitrary FRC text. Decision
discovery, necessary implication, coverage, consumer scope and several mutation
interpretations remain judgment-based. Actual authoring authorization is **zero**.
Stop after R5.81; Phase 5C remains paused.

## Deliverables and evidence

| Deliverable | Artifact |
| --- | --- |
| Versioned definition, relevance/observation methodology, classifications | [Implementation Adequacy 0.1](../../../docs/implementation-adequacy-v0.1.md) |
| Finite authority/intersection checks and separate authorization rule | [implementation_adequacy_r5_81.py](../../evaluation/implementation_adequacy_r5_81.py) |
| Synthetic complete/incomplete pairs and explicit freedom | [corpus.json](r5_81/corpus.json) |
| Fixed obligations, exclusions, witnesses, mutation judgments | [coverage.json](r5_81/coverage.json) |
| Mutations, residual implementation plans, public FRC checks | [experiment.py](r5_81/experiment.py) |
| Recorded results, validation, B03 activity accounting | [results.json](r5_81/results.json) |
| Independent review and preserved disagreements | [review.json](r5_81/review.json) |
| Mechanical tests | [test_implementation_adequacy_r5_81.py](../../evaluation/test_implementation_adequacy_r5_81.py) |
| Reproduction and scope | [README](r5_81/README.md) |

## Separate statuses and bounded authority policy

The pipeline now includes the implementation-adequacy gate between reviewed FRC
and authoring. R5.80 fidelity approval is preserved. The new sidecar does not
reinterpret approval, change the historical FRC format, or require all possible
conditions to be specified.

Relevance comes from admitted interface, reachable states/inputs, required results,
effects and temporal observations. A distinguishing witness supports relevance;
it does not establish that a source failed to delegate a choice. Internal
decomposition is irrelevant unless required observations such as time/resource
limits or public representation make it relevant. Preconditions and exclusions
need authority; they cannot be invented to obtain an adequate result.

The prospective authoring policy blocks material silence. This is an explicit
authority discipline, not a theorem that every refinement of a partial classical
specification is incorrect. Source-approved necessary implications may determine
choices without a separate prose clause. Distinguishing omission from implication
or delegation is therefore a real judgment boundary, exposed by independent review.

Five machine outcomes are retained: IMPLEMENTATION_ADEQUATE,
IMPLEMENTATION_UNDERSPECIFIED, NEEDS_CLARIFICATION, CONFLICTING_REQUIREMENT and
OUTSIDE_ANALYSIS_SCOPE. Diagnosed missing authority also returns clarification
as its next action. Uncertainty never becomes adequate.

## Synthetic corpus and observable decisions

Sixteen cases produce **10 profile-local adequate / 3 underspecified / 1
clarification / 1 conflict / 1 outside scope**. These are not 10 independently
qualified production contracts. Fixed obligations are inventoried textually;
only finite residual authority and conflict are checked mechanically.

| Pair/category | Missing/resolved decision | Result |
| --- | --- | --- |
| A | Ordered list, exact membership but no ordering authority / creation ordering | Underspecified / adequate |
| B | Missing-priority treatment explicitly awaits requester / missing means zero | Underspecified / adequate |
| C | Required tie policy explicitly awaits requester / earliest creation among ties | Underspecified / adequate |
| D stable | Ascending or descending priority authorized, creation-order ties | Adequate; direction may vary per call |
| D unconstrained | Caller must ignore order, including repeated-call ordering | Adequate within declared domain |
| E internal | Exact sum/no effects; no algorithm needed | Adequate before and after internal clause removal |
| F | Simultaneous opposite ordering on distinct tasks | Conflict |
| G | Undefined best | Clarification |
| H | Concurrent linearizability | Outside sequential finite profile |
| M | Rejection, transition condition, cardinality, normalization | Adequate local calibration clauses |

B/C synthetic incomplete sources were revised after independent review to make
the reservation of authority explicit. The original equality/maximum wording
could entail exclusion or implicitly delegate any maximizer. Correcting synthetic
sources establishes clearer test inputs; it does not resolve those original
interpretations or any public requirement.

Physically visible order can be contractually non-semantic when deliberate
source freedom and consumer restrictions say so. Membership, multiplicity and
frames remain binding. This cannot cancel an existing consumer obligation or
actual required ordering. Explicit unconstrained order differs mechanically from
an absent authority clause. Internal freedom needs no new source permission.

## Mutation experiment

Seven complete cases have the significant source quote and encoded authority
removed: ordering, defaulting, ties, rejection, transition condition, cardinality,
normalization. **7/7 mechanically report the newly unbound encoded decision.**
One internal-information removal remains adequate (**1/1**).

This is model-local removal sensitivity, **not seven independently validated
semantic omissions**. Inventories are retained rather than independently
re-derived from the altered prose. Review disputes defaulting (equality might
entail exclusion), ties (one maximizer might delegate selection), normalization
(lowercasing might entail unchanged spaces), and cardinality's ordinary refinement
interpretation. The transition mutation removes the complete accepted/rejected
clause; the original draft left a surviving instruction and was corrected.
No universal behavioral-completeness rate is claimed.

## Multiple-implementation evidence

Executable creation sorting and insertion sorting agree on **5/5 selected input
samples**, including reversed input, empty input, a singleton and sparse creation
numbers. Their internal algorithms differ. This is finite evidence, not universal
equivalence proof or complete filtering implementations.

Executable residual plans distinguish literal behaviors:

- Order omitted: `[z,a]` versus `[a,z]`.
- Reserved missing-priority treatment at query zero: `[missing]` versus `[]`.
- Reserved tie policy: `[z]` versus `[a]` at equal maximal priorities.
- Explicit unconstrained order: `[z,a]` versus `[a,z]` remains authorized because
  consumers compare membership/multiplicity rather than sequence order.

The last case is important: two implementations with different visible bytes are
not inherently inadequate. Unauthorized contractual difference is the issue.
The plans are residual-choice witnesses, not whole-contract applications.

## Public R5.80 reuse and B01

Five exact public candidate/receipt pairs are reused; all **5/5 fidelity bindings
match**. S01 is adequate only for abstract mathematical-integer sum and explicit
no-effects scope. S02, S10 and P01 retain APPROVED fidelity but return
OUTSIDE_ANALYSIS_SCOPE because this round has no qualified complete decision
inventory for their full stated scope. P01's known projection does not substitute
for adequacy review. These findings neither revoke R5.80 review nor establish
that these sources are inherently incapable of adequate implementation.

**B01 remains NEEDS_CLARIFICATION and unauthorized.** Exact reason:

> B01.O08 / B01.I1 states NORMAL as the default value but does not determine
> the trigger domain: omitted creation argument only, or creation omission plus
> an absent historical stored field. An implementation covering creation and
> migration would have to choose observable persisted/returned priority or
> failure behavior on the unresolved branch without authority.

“Still” requires upstream permitted baseline/source-owner authority that the
requirement-local FRC does not supply. No conventional implementation, oracle,
downstream consumer or support result is consulted to settle it. Conditional
legacy-state examples distinguish interpretations; they do not establish which
legacy states were historically valid. Full schema, transport, migration protocol
and other local omissions also prevent a complete adequacy inventory. The
specific default-domain blocker is sufficient to deny authority. Historical B01
acceptance is preserved; no public requirement is revised.

## Independent review and limitations

One separate same-family context performed two review passes. Mandatory governance
was available/read; **zero strict-isolation-qualified reviews** and **zero
independent test reruns**. The reviewer inspected exact new public files, no
protected sources, consumers or R5.80 candidates. B01 has coordinating analysis
and inherited R5.80 review evidence, not a new independent B01 adequacy review.

The first review identified semantic alternatives, an ambiguous transition,
insufficient mutation re-elicitation and a dense-sequence implementation defect.
The second accepted corrected reserved-authority pairs and transition but kept
the mutation and coverage disagreements. Both supported PARTIAL.

Final local fixes use the common authorization rule for public results, reject
scope mismatch/empty supported inventories and fail closed on noncanonical JSON.
They have coordinating tests, not a third independent review. Coverage flags and
quote semantics remain review attestations; hashes do not establish truthful
review. The text inventory is not bound to an independently approved coverage
receipt. Independent finite decisions do not model coupled constraints,
concurrency, arbitrary persistence protocols or arbitrary trace languages.

## Adequacy versus V1

| Conceptual combination | Interpretation |
| --- | --- |
| Adequate + representable | A completely reviewed decision inventory may have a separate complete V1 mapping. No new general joint qualification demonstrated here. |
| Adequate + unrepresentable | Public S01 has local adequacy; R5.80 lacks a qualified complete V1 mapping for it. |
| Inadequate + representable syntax | A V1 envelope can be syntactically valid while omitting source-required authority; syntax does not approve a faithful projection. |
| Inadequate + unrepresentable | Missing authority and missing mapping can coexist; B01 also has unresolved fidelity before approved projection. |

These axes remain separate. No additional projection is attempted; R5.80's
**1/9** result and V1 remain unchanged. A prototype mapping gap is not proof of
fundamental V1 impossibility or a Lykoi semantic gap.

## Verification, protection and stop

Commands and reproduction are in the evidence README. New mechanical tests
**18/18 PASS**; unchanged R5.80 checks **18/18 PASS**; unchanged guarded V1 checks
**33/33 PASS**, protected read attempts **0**. Initial new suite **16/16 PASS**;
two robustness tests added after review also pass. The experiment emitted
structured results without writing old records. No failed qualification command.
Final compact reproduction confirms all recorded classifications after robustness
fixes; `git diff --check` passes. Review-driven changes are prospective experiment fixes.

**B03_PRISTINE / B03_NOT_EVALUATED /
B03_NOT_EXPOSED_TO_LYKOI_DEVELOPMENT**. Every access/activity counter is **zero**,
including source/metadata access, adequacy evaluation, authorization, packaging,
opening, consumer observation, generation, execution, acceptance and repair.
This is scoped session accounting with inherited pristine status, not a protected
ledger or content inspection. No other protected held-out requirement is accessed.

Lykoi semantics/compiler/runtime/schema, V1, runner, frozen requirements/oracles
and historical evidence are preserved; core **30**, B02 exposed/indeterminate
history retained. The only new code is prospective public adequacy infrastructure.

**Final: R5_81_IMPLEMENTATION_ADEQUACY_PARTIAL. Stop after R5.81.**
