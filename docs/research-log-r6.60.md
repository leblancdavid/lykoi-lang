# R6.60 research observation supplement

The historical shared research log, decisions and project overview are protected
by inherited publication identities. Their original bytes remain unchanged;
this additive supplement records the new observations and decisions.

## Observations

[Report](../benchmark/results/phase6/R6_60-REPORT.md):
`R6_60_TARGET_LIKELIHOOD_IMPROVED`. Exact checkpoint/adapter/environment pass.
All six frozen completion+EOS losses improve with dropout disabled:
equal-record1.647022→1.504801 and pooled2,326-token1.627591→1.487384 nats/token.
Symbolic operations, references and output-definition likelihoods improve along
with formatting. No prompt/template mismatch was observed. All12 preserved
responses start with fence73594 and omit required package-envelope keys.
Original0/6 scores remain unchanged. Initial hash-assertion mistakes are retained
and corrected using historical serialization conventions; no parameters change.

## Decision and current boundary

Separate exposed gold-prefix fitting from free-running acceptance. Do not replace
historical scores with repaired outputs or claim generalization from six exposed
records. Do not attribute fencing to an unobserved template mismatch. The
conditioning/ranking difference is plausible but not a demonstrated causal result.
Publish without optional generation probes. Kernel26 and semantic implementations
remain exact. Stop after publication; separately authorized first-position logits/
ranks and repetition-penalty inspection are the smallest recommended follow-up.
