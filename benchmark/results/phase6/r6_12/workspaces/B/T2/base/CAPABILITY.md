# T2 base — current production capability assessment

Terminal: `PRODUCTION_SCHEDULE_SYNTHESIS_PROFILE_GAP` (static assessment).
No semantic candidate, compilation or acceptance execution; zero repairs.

## Obligation mapping

| Contract | Assessment and current references |
| --- | --- |
| 1–2: exact typed job/dependency input and phased validation | Decoded jobs can be ordinary related records with numeric fields and nominal dependency collections. Scalar type validation distinguishes bool/int (`mutable_values.py:22–40`); equality, numeric bounds, member and boolean guards are available (`predicates.py:68–94`). Request-level list-of-record parameters are absent (`predicates.py:19–34`; `references.py:192–200`). Stored unique-key validation (`reference_runtime.py:28–44`) alone does not implement all-shapes-first request precedence. |
| 2: known dependencies and cycles | Existing finite entity selection/extent and nominal required-existence checks can express useful subsets. Finite **nonempty** reachability includes self-loops; see `references.py:62–115,141–177` and `reference_runtime.py:74–127`. A missing named topological-sort primitive is not itself the reason for a gap. |
| 3: permutation synthesis, dependency ordering, inclusive deadlines | No normal operation derives permutations of a supplied entity sequence and binds successive cumulative completions. Query selection orders already-existing records (`collection_query.py:36–133`), not synthesized schedules. `computation.py:14–58` admits 1–16 local pure scalar/cardinality nodes, not a sequence accumulator or variable record projection. |
| 3–4: weighted-cost sum and minimum/lexical tie choice | Checked add and integer comparisons are available. No current computed query projection, grouped prefix/sum or schedule-valued argmin interface combines these into the required derived schedule. Ordering existing records by declared fields cannot create their runtime completion/cost values. |
| 4–5: exact parallel arrays/cost; empty result; pure deterministic execution | Exact projection of an actual compiled observation would be transport. Constructing the schedules, completion arrays or optimal choice in Python would be central task behavior. No such transport was authored. |

## Composition diligence

The contract has at most seven jobs; it does not demand unbounded search.
Multiplication by weights 0–9 might be expanded using additions and finite
selection/conditional cases, and candidate permutations might be predeclared.
Therefore absence of an unrestricted multiplication/search primitive is **not**
an impossibility argument. The current normal profile still lacks bindings to
instantiate those candidate sequence records from arbitrary runtime job rows,
compute their prefix values, and return the minimum derived sequence. Cardinality
is a count over an existing finite entity, not a sum of its numeric fields
(`computation.py:29–51`; `docs/typed-computation-v1.md:63–99,114–137`).
Conditional coupled effects create 1–8 rows from explicit primary images/parameters;
they do not introduce a permutation iterator or query aggregate (`atomic_state.py:29–114`).

This is a current production semantic/profile-interface limit, not an authoring
or compiler failure and not a theorem about kernel 26. Acceptance was not run;
the 17 frozen base cases are not counted as executed failures. Own contract and
acceptance were read only after recorder start. See GAP.json for elapsed time.
