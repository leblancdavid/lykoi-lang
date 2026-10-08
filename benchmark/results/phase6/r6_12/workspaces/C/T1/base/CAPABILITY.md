# T1 BASE — static capability assessment

Outcome: CAPABILITY_GAP / ORDERED_STATE_FOLD_AND_SORT_UNAVAILABLE.
No candidate or acceptance execution; no executed interpreter failure claimed.

Contract obligations 4–5 require each operation to observe the updated free/held/
shipped quantities and active/ever-used hold sets, then sort stock and holds by
runtime ASCII keys. For example reserve/release/reserve must preserve the used-ID
set while changing available units and active holds.

Frozen API evidence: CONTRACT-1.md lines 11–18, 47–60, 64–72 and 117–122;
interpreter.py FIELDS/EXPRS (32–59), seq (443–455), map/each (489–498),
select (505–513), call (540–541), and execute (551–575).
`seq` adds fresh bindings without reassignment; `map` provides an inclusive prefix
of original items, not prior computed results. `select` retains original order;
`unique` rejects duplicates rather than building/updating a keyed state. `call`
has an empty environment and no parameters. The closed expressions have addition,
equality and <=, but no fold, dynamic indexing, list update/concatenation, sorting,
or dynamic negation/subtraction. execute accepts bytes, not initial typed state.

Considered composition: a byte grammar can parse stock and operations; unique can
check duplicate SKUs; pointwise predicates/dispatch can check local conditions and
select subsets. Eight stock items fit the occurrence ceiling. Sixteen operations
could be split into bounded parse groups or explicit stages, so the eight-item
ceiling alone is not the gap. A prefix inspection does not accumulate reservation
quantities or resolve active holds, and select cannot turn a singleton list into
a bound scalar for updating a stock quantity. Unrolling 16 stages still supplies
no general state/list update or runtime order permutation. Enumerating all legal
requests is not a viable frozen plan: 64 structural nodes, 2048 expression visits,
acyclic argument-free rules and 4096-byte input/output limits are enforced.
Sorting cannot be supplied by the JSON transport. No host task algorithm or
acceptance-case table was authored. This is a whole-task implemented-API coverage
assessment, not a proof about an unrestricted future language.
