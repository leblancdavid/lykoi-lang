# R6.29 successor correction 1

The original **19/23**, `R6_29_CONSTRUCTION_PARTIAL`, frozen acceptance manifest,
artifact and publication remain immutable. This is a separately versioned successor.

Before reading the model artifact for replay, a deterministic scripted client
constructed `StageControl(permit:Bool,n:Int64)` with a direct Bool guard and one
increment. The unchanged VM's `Machine.run` check branch explicitly selects
`validation`; checked addition uses the default `structure` stage and encoding
selects `encode`. [Independent controls](CORRECTION-CONTROL.json) pass seven
success, guard/overflow-conflict, arithmetic, encoding, type and signature checks.
This justification does not depend on the model-authored GuardedLeft artifact.

Only the stage of `guard`, `guard_first_overflow`, `guard_second_overflow`, and
`guard_underflow` changes from `structure` to `validation`. All other expectations
are exact copies. [Correction record](R6_29-CORRECTION-1.json) binds the original,
successor and control identities. The correction was saved before successor replay.

[Unchanged-artifact replay](R6_29-SUCCESSOR-REPLAY.json) passes **23/23** against
[successor expectations](R6_29-ACCEPTANCE-SUCCESSOR-1.json), with zero model calls.
This does not relabel the original round or establish a comparative advantage.
