# Alternative provenance contracts

The proposals below are prospective; historical R6.40 acceptance and R6.18 semantics
remain unchanged. “Authoring location” must be typed explicitly: symbolic step ID,
expression occurrence, text coordinate and input-byte origin are different domains.

## A — Expanded-operation source locations authoritative

- **Determinism:** exact plan node and declared site Cell start, with unchanged
  ordered VM execution/charges; existing contract supplies a deterministic rule.
- **Compatibility:** strongest with R6.18; preserve nested seq regions, substitutions,
  raw IDs and limits. Flat expressions are not exact expansions.
- **Reporting/debugging:** accurately identifies the executing operation and region
  span; offset2 may be less informative as causal-byte blame. Existing map adds
  symbolic context without changing the error.
- **Equivalence:** compact versus its exact lowered plan must match full envelopes.
  Arbitrary flattened plans need separate equivalence rules; values do not suffice.
- **Complexity:** minimal for existing mechanics; no new runtime operation. Tooling
  needs to expose/label the map and distinguish input offset from node identity.
- **Fairness:** appropriate for a representation-only ablation retaining boundaries;
  unfair to call flattened X semantically identical when span/work change. Does not
  by itself settle whether a user requires original-input blame.

## B — Compact authoring locations authoritative

- **Determinism:** requires a fully specified canonical authored coordinate/blame
  rule. Choice among caller/definition/expression and duplicate occurrence cannot
  be left to rendering or model judgment.
- **Compatibility:** definition/local coordinates already exist as metadata, but
  replacing raw VM error locations violates current wrapper's no-rebase rule.
  Input-origin-preserving return spans are a further semantic change, not an authored
  coordinate automatically supplied by existing maps.
- **Reporting/debugging:** useful for compact editing and locating reused definitions;
  insufficient to identify the exact expanded occurrence without a call path.
- **Equivalence:** expanded representations require an independently supplied source
  map or canonical authoring surrogate; otherwise this privileges one representation.
- **Complexity:** moderate for node-level display, substantial and presently unspecified
  for text/expression-level maps or rewritten runtime input blame.
- **Fairness:** acceptable only if both representations retain the same independently
  specified authoring identities and metadata costs are counted. Selecting it because
  offset0/1 would make E3/E4 pass is circular and unsupported.

## C — Preserve origins separately

- **Determinism:** retain raw operation/node/site offset/work; add separately labeled
  definition/local/occurrence path from exact map/package. Specify missing origins
  as absent, never guess a byte/line.
- **Compatibility:** existing node-level sidecars support this without changing
  execution semantics. Complete value-producer/operand lineage and text coordinates
  are not currently present; making them runtime fields needs separate work.
- **Reporting/debugging:** shows both the active primitive and the compact caller/
  definition. Distinguishes consumer failure path from producer region-span path.
- **Equivalence:** permits exact runtime comparison plus metadata correspondence;
  raw offset disagreement remains visible. Does not make flattened span/work equal.
- **Complexity:** low for retained node/map/package analysis; higher for generalized
  expression-level/causal lineage. Sidecar generation/storage/validation costs count.
- **Fairness:** most informative when expectations say which fields are semantic
  requirements and which are tooling metadata. Cannot waive required original-input
  blame by placing an alternative coordinate beside an incorrect one.

## D — Representation-relative locations with correspondence rules

- **Determinism:** requires pre-frozen typed coordinate domains, a total mapping on
  compared sites, occurrence disambiguation and declared equivalence predicates.
  Undefined/unmapped/multiple matches must reject qualification, not be normalized.
- **Compatibility:** can compare existing envelopes externally without runtime changes;
  the correspondence itself is not specified by R6.18 or R6.40. Mapping node IDs is
  easier than claiming seq start2 corresponds to an original byte0/1.
- **Reporting/debugging:** keeps each representation's truthful native location and
  shows its paired site. Needs careful labeling to avoid conflating byte and node.
- **Equivalence:** separates functional, error-precedence, location correspondence
  and work/limit judgments. A broad equivalence theorem is not currently supplied.
- **Complexity:** bounded node-level relations feasible; general transformed-expression
  matching and proof of provenance equivalence are substantial missing interfaces.
- **Fairness:** useful for independently authored forms if justified by requirements
  before results. Post-hoc mapping any failure to the desired byte is unacceptable.

## Recommendation and selection discipline

Recommend **C at node/map sidecar level, with A's raw runtime semantics preserved**.
Use D only for independently frozen representation-aware node correspondence;
keep numeric input offsets exact when the requirement makes them observable.
This retains information, respects established semantics and enables debugging
without altering primitives. It is deliberately not a promise that the existing
compact tasks pass an input-origin contract.

Selection reasons are determinism, compatibility and explicitness. A's raw behavior
is source-supported today; C/D are a prospective reporting/comparison recommendation.
Human clarification must choose the task's provenance authority before adopting a
benchmark contract. If original-input attribution is required, qualify its actual
support or record a gap; do not downgrade it to cosmetic metadata for parity.
