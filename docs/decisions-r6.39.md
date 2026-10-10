# R6.39 architectural decision record

**Recommendation only:** retain the existing nonproduction immutable registry and
identity machinery. Treat a mechanically generated ordinary summary plus exact
retrieval as a viable context policy; symbolic snapshots remain optional. No
production default or execution semantics are changed.

[Evidence](../benchmark/results/phase6/R6_39-REPORT.md): A/B/C each accept all three
modifications, no regressions. C's lower aggregate measured input/time is accompanied
by more completions and rejected migration calls; full accounting and uniqueness
are unresolved. B's retrieval of history and snapshots means this is not a pure
summary-only test. Shared typed checks are available in B, so success does not
measure eliminating the symbolic-state layer, and no unique C benefit is proven.

Decision status: `R6_39_COMPARISON_INCONCLUSIVE`. Further ablation/repetitions or
architectural changes require explicit authorization. Stop after publication.
