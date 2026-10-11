# R6.67 — Additive boundary, research and decision supplement

Current authorized boundary: **R6_67_TRAINING_MECHANICS_ONLY**.
See the [report](../benchmark/results/phase6/R6_67-REPORT.md) and
[protocol](../benchmark/results/phase6/R6_67-PROTOCOL.md).

Observation: one exact R6.66 QLoRA attempt completes20 updates/80 presentations;
112 adapter tensors change, frozen base tensors remain unchanged, and fresh reload
reproduces deterministic reference logits bitwise. Peak reserved5.389GiB; training
104.288s. All13 target losses improve, but strict output validity and acceptance
stay0/13. All generated actions halt at serialization; semantic correctness cannot
be inferred from downstream false score flags.

Decision/tradeoff: retain the byte-identical worker and frozen external checkpoint
paths, routing only telemetry additively into R6.67. Preserve R6.66 publication and
the R6.59 adapter. Target likelihood is a fitting measurement, not usable semantic
construction. Exposed10 and coordinator-authored varied3 are not independent
generalization; memorization remains a compatible explanation, not a proven cause.

Proposal: separately authorize a prospectively frozen serialization-focused
generation experiment with fresh diagnostics. No further inference, tuning or
training is authorized here. Kernel26/production/experimental semantics/history
remain preserved; P6-A04 acceptance0 and P6-A05 access false.

Stopped after publication; await explicit authorization.
