# R6.42 prospective provenance qualification

**Completed once; `R6_42_PROVENANCE_PARTIAL`.**
[Report](../../benchmark/results/phase6/R6_42-REPORT.md) and
[prospective contract](CONTRACT-1.md).

`prepare.py` generated the immutable pre-execution freeze; `run.py` performed the
one authorized attempt. **Do not rerun either or repair frozen oracle.py.**
`audit.py` only analyzed the first evidence and losslessly archived its original
bytes. `verify_regressions.py` recorded unchanged R6.18/R6.32 regressions.
`publication.py` verifies preservation and publication without executing plans.

Compact/exact full execution agrees, and flat functional behavior agrees within
the finite domain. The oracle incorrectly retained byte-origin tuples on numeric
UInt8 Cells, failing intermediate trace expectations. All first discrepancies are
preserved. No production or existing experimental semantic implementation changed.

Evidence lives in `benchmark/results/phase6/r6_42/`. Raw differential/adversarial
JSON is published as `.json.gz`, with original/compressed hashes in RAW-ARCHIVES.json.
Local uncompressed originals remain intact and are Git-ignored. Decompression
recovers exact original bytes. Wait for explicit authorization for further work.
