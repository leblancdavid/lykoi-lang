# T1 MODIFICATION — static capability assessment

Terminal outcome: CAPABILITY_GAP / ORDERED_STATE_FOLD_AND_RESIZE_UNAVAILABLE.

The base records remain authoritative: ORDERED_STATE_FOLD_AND_SORT_UNAVAILABLE,
no implementation and no acceptance execution. Base contract clauses 4–5 still
require sequential keyed-state updates, persistent used IDs, and ASCII-sorted
stock/active holds. The new contract explicitly retains these obligations; it
does not supply a missing VM operation or relax the original requirements.

Modification clauses 1–2 add shape validation of resize, active-hold lookup,
runtime d=n-old_n, availability validation, and coordinated free/held/hold.n
updates. Decrease and equality must work, without changing shipped or used IDs.
This adds dynamic difference and replacement requirements to the inherited
state-fold blocker. Closed expressions provide checked addition but no dynamic
subtraction/negation; adding a negative constant does not negate a runtime old_n.

Frozen evidence inspected in this session: CONTRACT-1.md 39–72 and 117–122;
interpreter.py 32–59, 443–455, 489–523, 540–575. seq provides local bindings;
map/each use original-item prefixes rather than an evolving computed state;
select preserves order; unique rejects duplicate keys; call has an empty
environment. No fold, keyed lookup/update, sort or dynamic subtraction is in the
closed API. Unrolling bounded operations still lacks those data operations;
bounded parsing/dispatch alone cannot perform the required state transition.

The assigned contracts and both frozen suites were read after START.json was
recorded. Original cases: 15 NOT_REACHED; new cases: 8 NOT_REACHED. Candidate
attempts, repairs, and acceptance subprocess invocations: 0. This is a static
whole-task coverage assessment, not an executed VM failure or impossibility
proof. No behavioral regression observations exist; regression rate is
unavailable because the base never succeeded. No host task algorithm, VM change,
historical plan or other-track solution was used.
