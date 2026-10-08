# T2 BASE — static capability assessment

Outcome: CAPABILITY_GAP / BOUNDED_PERMUTATION_OPTIMIZATION_UNAVAILABLE.
Acceptance not executed; no interpreter runtime failure claimed.

Contract 3–4 requires constructing permutations of runtime jobs, checking cumulative
completion/dependencies/deadlines, minimizing sum(weight * completion), and breaking
ties by runtime ID sequence. This is required for all 0–7-job inputs, not just the
published observations.

API references: CONTRACT-1.md 11–18, 49–60, 64–72, 117–122;
interpreter.py 32–59, 85–113, 266–316, 464–480, 489–513, 540–541.
`repeat` constructs lists by consuming the byte cursor, not by enumerating a state
space. `map`/`each` only traverse an already supplied list; `select` preserves order.
There is no permutation/cartesian-product generator, runtime-index list projection,
list concatenation/update, fold over computed results, or argmin/sort. Rules are
acyclic and argument-free. Source-item prefixes are not computed schedule prefixes.

Bounds considered: seven jobs fit the eight-occurrence ceiling; bounded dependency
comparisons can use nested select/length/eq checks, and some fixed path checks can
be unrolled. Weight 0–9 multiplication could in isolation be expanded by finite
dispatch and repeated add; lack of a multiplication opcode alone is not decisive.
Completion and cost fit the integer domain. However these subsets do not generate
and compare arbitrary feasible orders or bind running totals from prior mapped
results. Up to 5040 permutations cannot be supplied by the transport, and collecting
them for map/select exceeds the eight-item ceiling. Explicit exhaustive branches
for arbitrary job data/permutations do not fit 64 nodes and 2048 expression visits;
calls cannot parameterize/recurse over subsets. No claim of unbounded computational
impossibility is made. This is the current frozen API/plan-bound coverage gap.
