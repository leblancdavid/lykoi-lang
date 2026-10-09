# R6.38 observations

[Report and evidence](../benchmark/results/phase6/R6_38-REPORT.md) preserve a three-task,
six-run actual-MCP comparison on GPT-6.1 Sol. Deterministic snapshots support3/3
fresh modification continuations, all acceptance passes, and exact AI-free replay.
Snapshot verification uses authoritative registry closure plus verbatim frozen facts.
Four prospective and two supplemental snapshot/retrieval test methods pass.

B shows26.7% lower reported processed input including cached input, with higher
noncached input and one additional completion. Retrieval calls20 versus19 and
retrieval response volume increases. Aggregate authoring time is3.2% lower but the
per-task pattern is inconsistent. Exact provider request boundaries/tokenizer,
billing/coordinator usage and scored ordinary-summary control are absent. Thus
`R6_38_COMPARISON_INCONCLUSIVE`; no quantitative causal attribution or general
superiority. Historical identities protected3,374; production remains26. Stopped.
