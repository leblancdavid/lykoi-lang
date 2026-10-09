# R6.29 failure attribution

**First terminal classification remains `R6_29_CONSTRUCTION_PARTIAL`.**

The frozen evaluator passes19/23 observations. Four false-guard cases disagree
only on the expected error stage: frozen `structure`, native `validation`. The
model-authored check returns the correct GuardDenied code at the correct guard
site and offset0; the trace enters no arithmetic. The frozen manifest is unchanged.
This is a **coordinator acceptance-expectation defect**, not incorrect model
reasoning, semantic insufficiency or a guard/ordering error. The initial failed
verification assertion is [retained](FAILED-VERIFICATION.json). The separately
labeled [precedence audit](PRECEDENCE-AUDIT.json) explains native behavior without
replacing the first result or rescoring acceptance.

| Failure category | Observation |
| --- | --- |
| Existing semantic capability gap | None demonstrated; scripted gate passed |
| Tool-interface capability gap | None observed; four truthful tools exposed |
| Invalid model tool arguments | 0/7 |
| Incorrect semantic construction | None observed; exact dependencies/expressions verified |
| Guard/ordering error | None observed; three real competing-overflow conflicts stop at check |
| Functional acceptance failure | 4/23 frozen stage-label mismatches, coordinator defect |
| Provider/runtime failure | No unexpected errors; expected guard/overflow/encode rejections retained |
| Budget exhaustion | None;7/16 calls,0/4 correction turns |
| Offline verification failure | Original full-acceptance assertion fails; preserved |

No model-authored decision, artifact, backend or frozen expectation is repaired.
Post-result integrity checks can pass while full functional acceptance remains
false. Consequently this round does not receive a supported classification.
