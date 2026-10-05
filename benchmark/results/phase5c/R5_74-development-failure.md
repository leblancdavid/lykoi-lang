# R5.74 development health failure — preserved

Before any fake ExperimentFreeze, authorization or observation, the first
development candidate prepared `R5_74-evidence/` and passed seven health stages.
Its isolated runner health command failed with `generic health worker failed;
output withheld`. No health-runner PASS artifact exists for that candidate.

A separate PATH-empty diagnostic ran all 74 runner tests: 73 passed, one errored.
The B02 metadata-only eligibility test could not launch `git ls-tree`:
`FileNotFoundError: [WinError 2]`. This happened before any protected-content access.
The ordinary environment's runner suite passed 74/74.

Cause: the stripped worker environment omitted the Git metadata tool required by
the newly added eligibility test. Prospectively declare its resolved location in
CurrentState and expose only its parent directory in the worker PATH. All other
authoring context remains stripped.

Preserve `R5_74-evidence/` unchanged as incomplete development evidence. It is not
qualified health evidence and contains no freeze, grant or observation. A wholly
fresh candidate uses `R5_74-qualified-evidence/`. R5.73 is not retried, and no B02
authorization, reservation, opening, read, observation or repair occurred.
