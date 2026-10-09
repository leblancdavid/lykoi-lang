# R6.33 decisions and tradeoffs

Fix one available capable route before results, freeze a bounded composition and
selective caller migration requirement, and require explicit action JSON through
unchanged lifecycle machinery. No outcome-informed model switching or semantic
repair. The [protocol](../experiments/ai_lifecycle_r6_33/PROTOCOL.md) requires a
transport failure to halt; observed exhausted provider credits therefore terminate
this pilot as R6_33_PROTOCOL_HALT. This preserves experimental accounting rather
than silently substituting a new model or coordinator-written definitions.

Keep production impact diagnostic separate from the frozen symbolic dependency
map. Preserve raw failure semantics while redacting response credentials. Record
missing telemetry and unexecuted deliverables explicitly. Further funded-provider
work needs fresh explicit authorization and a linked post-halt record.
