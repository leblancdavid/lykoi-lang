# Research log supplement — R6.20

Local diagnosis used the same pinned participant, baseline inference options and
existing runtime as R6.19. All tasks, schemas and prompt templates were frozen
before49 loopback requests. Raw requests/responses, first validation failures,
runtime log spans,126037 input/28146 output tokens and416 resource samples are
preserved in [R6.20 evidence](../benchmark/results/phase6/r6_20/MEASUREMENTS.json).

Observed: all requests HTTP200; neutral short/list/nested/sequential/tool conditions
passed apart from three intentionally insufficient output caps. Historical500
cause remains undetermined; no OOM evidence. New symbolic instructions were about
9900 tokens and runtime truncated each to4098. Eight individual features and four
paired objectives produced no accepted composition. A consumed16384 output tokens
over16 calls; B consumed666 over4 calls and stopped at stage1. The cost difference
measures failure paths and supports no efficiency claim.

The coordinator's oversized repeated schemas violated intended compact prompt
delivery. Preserve that failure; do not retrofit a favorable comparison or blame
isolated semantic features that validation never reached. No prompt tuning or
inference rerun followed results. Host controls are not model successes.

Final `R6_20_PROTOCOL_HALT`; discovery gate not passed. See
[report](../benchmark/results/phase6/R6_20-REPORT.md). This additive entry preserves
the exact R6.19-pinned historical log. Stop pending explicit authorization.
