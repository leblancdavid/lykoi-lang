# T5 base — current production capability assessment

Terminal: `PRODUCTION_RANKED_ROUND_BINDING_PROFILE_GAP` (static assessment).
No semantic candidate, compilation or acceptance execution; zero repairs.

## Obligations and available subsets

- Clauses 1–2: candidates and ranks fit insertion-ordered, unique enum scalar
  collections. Strict integer weights, bounds and exact member checks are
  available (`mutable_values.py:22–40`; `predicates.py:19–34,68–94`). A list of
  exact ballot record **parameters**, and full request shape validation before
  duplicate-candidate/unknown-rank phases, has no normal request schema interface.
  Stored entity row validation is real but is not that request-phase contract
  (`reference_runtime.py:28–44`; `references.py:192–200`).
- Clause 3: nominal candidate records, an active flag/state, original ballot
  scalar collections, and exact membership predicates are available. However,
  scalar collection operands do not expose rank-index/first-selected-element
  bindings. Query `execute_predicate_query` returns filtered and ordered copies
  of existing records, without computed field projection
  (`collection_query_runtime.py:149–168`).
- Clause 3: flattening ranks to explicit rows with original position is a plausible
  exact decoded-data projection, rather than an arithmetic/ballot processor.
  It still needs a production correlated rank→active-candidate binding and
  first-active selection for each ballot. `references.validate_condition` permits
  an extent over a fresh related alias, but its selection predicate is an atom
  tree with no recursive extent/query nesting (`references.py:62–115`).
  Computation cardinality has the same nonrecursive predicate restriction
  (`computation.py:29–46`). No full ranked assignment interface was found.
- Clauses 3–4: **weighted sum and majority are not alone decisive gaps**.
  For weights 1–9, after assignment is bound, sum(weight) can be nine counts of
  weight≥k plus eight checked additions (a 16-node graph can use the first count
  directly as an add operand). Majority is `2*votes > nonexhausted`, expressible
  by add(votes,votes) and gt; no division is required. Minimum totals with largest
  ID tie can use numeric ASC then ID DESC ordering if actual totals are fields.
  See `computation.py:14–58`, `predicate_integration.py:55–110`, and
  `collection_query.py:74–85`. These are analytical subsets, not executions.
- Clauses 4–5: elimination changes the domain, reassigns original ballots and
  appends exact nested totals/exhausted/eliminated snapshots up to six rounds.
  Atomic history creation is supported for complete ordinary rows, using a
  primary before/after image, explicit inputs and bounded graphs
  (`atomic_state.py:29–114`; `docs/prewrite-conditional-composition-v1.md:86–140`).
  It does not add grouped ranked query projection or a normal in-memory iterative
  nested-round result binding. Scalar collections do not store lists of round
  records (`predicates.py:19–34`).
- Clause 6: a Python loop computing assignments, totals, winner or elimination
  would implement central decoded-data behavior. A transport may invoke ordinary
  APIs and serialize actual observations, but cannot create these missing facts.

## Classification

Bounded enumeration, threshold-count arithmetic, state predicates and history
composition were considered. The missing current interfaces are ranked-element
binding/correlated selection and integrated grouped round results, alongside the
request-record profile. This is a static current semantic/profile limit, not
kernel impossibility, an author failure or an executed acceptance failure.
All 15 base cases remain unexecuted. Task-specific reads followed START.json;
GAP.json records actual elapsed time.
