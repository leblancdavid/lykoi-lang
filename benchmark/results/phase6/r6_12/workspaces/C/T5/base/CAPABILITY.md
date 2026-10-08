# T5 BASE — static capability assessment

Outcome: CAPABILITY_GAP / RANKED_ROUND_AGGREGATION_AND_ORDER_UNAVAILABLE.
Acceptance not executed; no candidate/runtime failure is claimed.

Contract 3–5 requires first-active-rank selection, weighted aggregation by candidate,
sorted totals, majority/elimination choice with ASCII tie-breaking, and rebuilding
the active set for successive rounds while retaining every round observation.

Evidence: CONTRACT-1.md 11–18, 47–60, 64–72, 117–122;
interpreter.py 55–59, 85–113, 266–316, 443–455, 489–513, 533–541.
Map bodies see original items/prefixes, not previous outputs; no fold or mutable
accumulator is available. Select yields a list in supplied order and no expression
extracts its first element. Static dotted ref is record-key projection, not runtime
list indexing. There is no sort/argmin or list append/concatenation operation.
Rules have no parameters/captured environment and recursion is rejected.

Composition considered: six candidates/ranks and six rounds fit the eight-item
limit. Twelve ballots could be split into groups; this is not by itself a terminal
gap. Membership can in principle be tested with select+nonempty and nested eq;
uniqueness can validate parsed record wrappers. Strict majority can be expressed
without division as nonexhausted < votes+votes using <=/eq with Boolean dispatch.
Weights 1–9 could theoretically be summed by nine weight buckets, cardinalities
and repeated addition rather than a sum primitive. These subsets do not provide a
scalar first-surviving-rank binding, sorted candidate output, generic round state
update, or construction of the runtime round list. Six rounds can theoretically
be unrolled, but parameter-free calls cannot reuse environment-dependent tally/
elimination bodies; full repeated construction must also fit 64 nodes/2048
expression visits. Finite candidate subsets/ballot rankings are not permission to
enumerate acceptance outputs, and exhaustive legal inputs do not fit the frozen
plan bounds. No within-bound whole-task plan was identified; no host ranking,
tally, sorting, or iteration fallback is supplied. This is a frozen implemented
API assessment, not a minimality or unrestricted-language impossibility claim.
