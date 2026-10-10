# Lykoi research observation — R6.56

The complete configuration passes with sampling80, no shuffle, record mean loss/4,
R6.55 AdamW and R6.54 schedule. Independent normalization loss/gradients match within
1e-6 and differ from pooled weighting. All5,387 protected identities and47 installed
package trees match. Initial adapter tensors match R6.52 exactly.

Base6/6 calls complete: strict JSON/schema/semantic/full-task acceptance0/6; native
types and executable cases are NOT_REACHED. Generated244 tokens in16.2174442s.
One training attempt logs E01/E02/E03 losses1.816052/1.712078/1.517042 before any
update, then exits71 for reserved VRAM>8GiB. Updates0; no trained adapter or comparison.
Different-record losses are not evidence of learning. Exact training peaks and loop-only
time were not retained; launcher RSS polling is not qualified as actual-worker RSS.

Original assertion and a pre-update internal AdamW-default assertion correction are
preserved without changing configuration or diagnostics. Publication-only import repair
does not alter frozen experiment source. See the [report](../benchmark/results/phase6/R6_56-REPORT.md).
