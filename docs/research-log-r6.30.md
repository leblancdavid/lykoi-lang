# R6.30 research observations

[Bounded comparison](../benchmark/results/phase6/R6_30-REPORT.md) is inconclusive.
Identical explicit ordered arithmetic/Boolean/error contracts yield first-candidate
success in A/B/C,each56 base cases and27 additive-extension cases. No observed
semantic-validation advantage beyond lean intent. Zero regressions partly derive
from immutable original endpoint deployment,not in-place editing safety.

The independent scripted VM-stage correction preserves historical R6.29 score19/23
while its separate unchanged-artifact successor passes23/23. Pre-author native
qualification verifies all83 new expectations. C artifact/call reconstruction and
AI-free replay83/83 succeed; transport/wrapper/VM107 methods pass.

Observed process defects: enclosing terminal120s timeout interrupts T2/B; submitted
candidate and native SDK export are recovered without rerun. Unknown process wall
remains null,completed usage is a lower bound. Four C run_case calls precede sealing
and fail. A lineage audit first assumes error states expose output; failed audit
is retained and the collector reads native error feedback. No scored repairs,
acceptance changes or semantic changes follow these outcomes.

A author stages use26,424 SDK tokens/134.667s; C71,409/162.533s. B≥29,920 tokens
and138.481s known four-stage subset,with one missing wall/partial usage stage.
API billing,coordinator usage and pure inference remain unavailable. Exploratory
synthetic evidence; no significance,generalization or fully costed winner claim.
