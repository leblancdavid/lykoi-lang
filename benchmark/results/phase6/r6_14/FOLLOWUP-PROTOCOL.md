# R6.14 experiment 2 — consuming projection repair

Prospective record after experiment 1, before successor construction. Original fixed
six-attempt budget is exhausted; all original plans, freezes and observations are
preserved. This is an explicitly recorded budget change/new experiment under owner's
section 8 allowance, not an unrecorded extension or reclassification of first success.
No language/VM extension or new relation. Stop after this one successor attempt.

Observation motivating change: original 57-node XOR8 rejects `nonconsuming repeat`;
its shared rule's constant-length Take is conservatively zero progress, as documented
in the unchanged contract. ADDMOD8 and PARITY8 completed three exhaustive passes.

Only permitted repair: shared byte projection replaces constant-length Take with
existing UInt8 Atom. Atom consumes one byte and establishes static progress; its
result remains unused. Byte bits, selection, Horner expression and output unchanged.
At most ONE new plan, builder process <=120 seconds, acceptance process <=180 seconds,
follow-up dispatch session <=240 seconds. No retry/replacement or further budget change.
All original acceptance expectations, traversal/time/memory procedures and determinism
requirements remain exactly PROTOCOL.md. Freeze successor before execution. Preserve
both rejected first plan and successor; report paired structural/validation differences.
