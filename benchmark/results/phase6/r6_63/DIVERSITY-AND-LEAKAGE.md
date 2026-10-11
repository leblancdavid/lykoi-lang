# Diversity and leakage audit

Ten demonstrations, three selected operations (add4/le3/eq3), one broad ancestry
component `R663_FIXED_TYPED_STEP`. Ten nominal source family labels are **not ten
independently sourced semantic families**. None are counted for variable renaming,
changed constants alone, duplicate execution, A/B/C representation or fixture count.

| Episode | Structural distinction | Selected direct dependencies |
| --- | --- | --- |
| D01 | add two distinct Int64 refs; unused Bool param | arrivals, reserve |
| D02 | add literal on left, ref on right; unused Int64 ref/literal | count |
| D03 | add same reference twice; deduplicated dependency | batch |
| D04 | add prior subtotal and param; prior subtotal has two parents; unused mirror | adjustment, subtotal |
| D05 | inclusive upper bound, ref ≤ literal | load |
| D06 | inclusive lower bound, literal ≤ ref | stock |
| D07 | ordered reference-to-reference limit; unequal/equal/extreme inputs | available, requested |
| D08 | exact Int64 agreement rather than inclusive ordering | recorded, reference |
| D09 | Bool agreement, all four truth pairs; Int64 distractor | first, second |
| D10 | Bool reference equals available literal; opposite Bool distractor | enabled |

D05/D06 are an orientation contrast within one broad literal-bound pattern, not
independent family ancestry. D01/D08/D09 share two-ref shape with different relation
or type obligations. Every example includes unused references; D04 includes a prior
unused value. Zero-, one- and two-distinct-ref effects are distinguished in the
dependency machinery, but the positive selected records cover **one/two**, not zero
refs. No literal-only positive demo is claimed. Prefix dependency depth is at most
two; no long graph, scheduler, ordered effect, storage or application coverage.

Six overflow fixtures cover both signed ends, repeated-reference overflow and prior
subtotal versus selected-step overflow. Four argument-shape/type failures include
Bool/Int64 distinction. Twelve static mutation controls cover mixed types, Boolean
ordering, incompatible equality, result type, dependencies, refs, literal vocabulary,
new operation and state tampering. Six well-typed wrong choices fail frozen behavior.
One commutative operand swap preserves behavior but fails exact source binding; this
prevents acceptance from treating finite output equivalence as identity fidelity.
Five further test methods challenge rehashed prefix validity/order, capture, local
bounds and strict native serialization. Negative controls are not positive examples.

## Source, acceptance and provenance

All sources/FRCs/explicit fixture expectations and exact binding expectations were
sealed before expert actions. Expected values are literal fixture data; execution
does not compute expected outputs. Source/oracle and candidate implementation are
separate artifacts, but authored and reviewed by the same capability-aware
coordinator. Human-style prose is synthetic, not human-authored. This is expert
construction supervision, not observed AI semantic tool decisions or invented
reasoning. Existing R6.18/R6.23/R6.62 contracts and historical findings were available.

All examples and derivatives remain training_development. The rights basis is the
owner's bounded research data-qualification authorization. `training_allowed` in
the inherited schema marks candidate partition eligibility; it does not authorize
training now. Each admission receipt applies all R6.49 Tier T gates. Tier E is zero.

## Reserved family and custody limitation

[Partition record](PARTITIONS.json) reserves Unit equality over two prior Unit-valued
aliases sharing a Unit input (a diamond dependency shape) for future evaluation.
No completed solution, expert action, acceptance suite or evaluation target was
created for it, and none appears in producer records. The reservation is prospective
scope only. Same-coordinator/repository access cannot enforce exclusion from future
training-data producers; provider hidden context and future access are unattested.
No independent evaluation qualification, pristine held-out family or clean custody
is claimed. A future independent custodian must commission/freeze its own task and
acceptance privately before exposure; this description is already exposed planning.

No known completed evaluation solution is included in this bounded candidate pool.
That Tier T statement is not a claim of hidden-context cleanliness or universal
semantic deduplication. Publicly exposed historical examples remain historical.
