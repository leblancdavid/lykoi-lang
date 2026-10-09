# R6.38 architectural decision record

Keep state-based continuation experiment-local. Preserve full required definition
closure and exact frozen constraints instead of using an LLM summary or estimating
which ordered checks can be omitted. Tradeoff: redundant signatures/dependencies
and provenance increase snapshot size, but deterministic regeneration rejects stale
or re-sealed incomplete context. Read-only detail retrieval is identical for both
tracks and delegates existing semantics; telemetry changes are not semantic writes.

Use `R6_38_COMPARISON_INCONCLUSIVE` despite the observed participant input-volume
reduction: fully accounted effort is unknown and ordinary summary efficacy was not
measured. An offline generic latest-state extraction is smaller than the registry
snapshot. The demonstrated registry contribution is identity/closure verification,
not an isolated productivity advantage. Recommend separately authorized matched-state
three-way comparison after safe exact request/tokenizer qualification. Stop now.
