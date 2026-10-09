# Attempt 3 — replay-label collision

All 148 stateful observations matched the frozen behavioral expectations, and impact
output was written. The replay aggregator then confused two different `create`
requests in each sequence (valid label versus blank label) because their case IDs
were identical. Raw observations and exact inputs remain in `attempt-3/telemetry/`;
no `FUNCTIONAL.json` success summary or recovery-stage completion is claimed there.

Attempt 4 adds the sequence ordinal to case IDs and normalizes only the repeat
component. It does not change fixture semantics, functional expectations or
production execution. The prior failed aggregator attempt remains preserved.
