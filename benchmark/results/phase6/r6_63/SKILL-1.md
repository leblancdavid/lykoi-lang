# Frozen construction skill 1

Input: human-style requirement, immutable typed definition prefix, available scalar
literals, mechanical output id `selected`, required result type, foundation identity.
Choose exactly one existing binary `add`, `le` or `eq`; bind two operands, each a
direct immutable ref or declared literal. Output one native R6.18 value-step object
with id/type/deps/node. Dependencies enumerate exactly the distinct direct refs;
lexically sorted serialization is required by this experiment (no execution change).
No nested selected expressions, new operations or inferred repair are admitted.

Existing meanings: R6.18 expression typing admits add/le on Int64 and eq on two
operands of the same Int64/Bool/Unit type. Int64 is signed 64-bit; Bool is not Int64.
R6.10 add rejects overflow; le is inclusive and ordered; eq preserves exact types.
The selected subset includes Int64 add/le/eq and Bool eq. Unit equality is reserved.

State includes version/foundation, name, typed params, frozen native prior value
steps and order, available literals, mechanical output id/type, and SHA256 of its
canonical body. After-state contains parent pin, action pin, complete sealed package
and its canonical body identity. Prefix byte-equivalence and parameter identities
are checked. Rejects produce no after-state and leave input identities unchanged.

A emits the complete package, including identities and the mechanical HostEntry
which calls the selected definition with type-correct zero/false/null defaults and
returns Int64 zero. B emits only the selected step. Both have one new semantic
relation selection, two ordered operand bindings, result type and exact dependency
declaration; copying prior steps/ids is additional A structure, not extra task choice.
HostEntry is validation scaffolding, never behavioral acceptance of the requirement.

For each behavioral fixture: check supplied scalar argument types with unchanged
expression typing; instantiate HostEntry with those constants, expand unchanged,
extract the generated task seq into the existing VM decode slot and call execute
with assemble=False. This observes the actual Int64/Bool task result and runtime
rejections without the unrelated UInt16 output restriction. No new evaluator is
implemented. Positive records refer to separately frozen literal expected outcomes.

Bounds: ten expert demonstrations, at most four params and two prefix steps,
one selected step, two deterministic acceptance passes, finite mutation controls.
Only locally synthesized training-candidate preparation is authorized.
