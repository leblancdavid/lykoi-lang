# Attempt 1 — serialization failure

`qualify.py attempt-1` completed registry controls and the twelve VM executions,
then failed serializing the raw VM `output` bytes into `REGISTRY.json`.
The partial JSON, immutable registry snapshots, exact proposals, validation events
and `FAILED.json` are retained under `attempt-1/`. Stateful/recovery stages were
not reached. This is an evidence serialization defect, not a semantic repair.

Successor runner serializes output bytes losslessly as `output_hex`, and prepares
JSON fully before opening an evidence destination. Attempt 2 is a separately
identified rerun of qualification infrastructure, not replacement of attempt 1.
