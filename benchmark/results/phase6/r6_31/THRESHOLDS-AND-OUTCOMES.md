# R6.31 — Practical effect thresholds and falsifiable outcomes

These rules are prospective and frozen with protocol1. H1 and H2 get separate
verdicts; design readiness is not any of the empirical outcomes below.

## Metrics, practical bands and guardrails

| Metric | Material improvement | No-meaningful-difference band |
| --- | --- | --- |
| First/final fully accepted task or modification rate | At least10 percentage points absolute | ±5 percentage points |
| End-to-end metered author tokens or wall, on matched accepted tasks and all-run totals | At least20% reduction; creation/setup/maintenance included where claimed | Ratio0.90–1.10 |
| H2 passing-to-failing retained-observation regression rate | At least5 percentage points absolute reduction, with at least2 distinct application/change branches benefiting | ±2 percentage points |
| H2 impact F1 | At least0.10 increase, no recall decrease | ±0.05 |

Each metric is reported rather than a weighted composite. Primary correctness is
first and final **strict checkpoint acceptance**, not many correlated easy cases.
Effort improvement qualifies only with acceptance no more than5pp worse, no new
critical state/invariant/rejection-atomicity failure, and complete metering of that
dimension. Reliability support uses acceptance and regression metrics; impact-only
or representation-only gain is a secondary tooling observation, not H2 support.
Repairs/calls/tool time have descriptive totals and ratios; no arbitrarily added
significance threshold. If tokens improve but wall/cost materially worsens, label
the tradeoff and do not declare unqualified development-efficiency superiority.

For H1 adaptive support require at least2 sealed admitted abstractions each reused
successfully on at least2 distinct evaluation requirements, with witnesses spanning
at least2 evaluation strata overall. L1 must materially improve correctness **or**
fully costed effort against **both L0 and capacity-matched LH**. Against A/B report
whether this is a practical overall advantage or only an intra-symbolic advantage.
No advantage over LH means ordinary macro reuse remains a sufficient explanation.
LX identifies compact-reference effects; it need not be worse for discovery
selection to matter, but compactness-specific superiority needs a material L1–LX
effort contrast. Empty library or no transfer falsifies adaptive support in this run.

For H2 symbolic support require a material acceptance/regression or guarded-effort
gain versus **both A and B**, benefiting at least2 applications from2 skeletons.
Track-local improvements and gaps still report separately. A C-only semantic-check
claim additionally requires saved defect lineage, actual earlier check rejection
and absent equivalent B prevention; validation pass alone is not a witness.

## Uncertainty before evaluation

Report all paired per-task/per-application deltas, first/final denominators,
median/range, discordant counts, paired effort ratios and direction consistency.
For main H1, calculate descriptive95% cluster-bootstrap intervals (10,000 draws,
seed631, resample12 task clusters; all replicates/conditions move together).
For H2 use4 application clusters, retaining branches/replicates together, and show
leave-one-application-out sensitivity; four clusters provide weak precision.
Within each bootstrap average replicates per task/branch, then equally weight
tasks/applications; compute cost ratio from paired sums. Do not bootstrap cases
or model messages as independent requirements. Paired complete-success ratios
must show excluded failures and all-run cost alongside them.

Intervals are descriptive and assumption-sensitive; report exact raw counts and
small-sample limitations. No p-values/statistical-significance or population-wide
superiority claims from this study/pilot. Practical threshold crossing with wide
intervals is an exploratory signal, not confident evidence. A supported bounded
main-study advantage requires the point estimate to meet the material threshold,
the paired interval exclude zero gain (or ratio1 for cost), guardrails hold and
required completeness/validity controls pass. This is a predeclared decision rule,
not a claim of statistical significance.

No-meaningful-difference requires intervals wholly within the relevant equivalence
bands for acceptance and selected complete effort dimensions; failure to find a
winner or all point estimates equal is insufficient. With small samples, this may
remain inconclusive. Report negative transfer and rare critical defects regardless
of favorable average. Multiple contrasts remain visible; do not choose the winning
metric/seed/task subset after scoring.

## Empirical outcome rules (hypothesis-specific)

| Outcome | Required interpretation |
| --- | --- |
| Adaptive Lykoi advantage (H1) | Admission and transfer witnesses plus L1–L0 and L1–LH material gain, full cost guardrails and valid unseen boundary; report A/B/LX contrasts explicitly |
| Fixed symbolic vocabulary sufficiency (H1 or H2) | Fixed L0/LH or H2-C achieves at least90% final checkpoints, while complete adaptive comparisons show no material added gain; report primitive versus human-macro sufficiency separately. Sufficiency alone is not superiority. |
| Structured-intent advantage | B materially improves guarded correctness/effort versus A and relevant symbolic comparator; credit equivalent checks, not C attribution. If B≈C and both outperform A, report shared structured-workflow benefit. |
| Direct conventional advantage | A materially improves guarded correctness/effort versus B and symbolic conditions, including failed-symbol cost; scope limited to admitted tasks |
| No meaningful difference | Predefined interval-equivalence rules hold on primary correctness and complete selected effort dimensions; no unique critical failure |
| Inconclusive evidence | Incomplete comparisons, unmatched LH, unqualified oracle/machinery, wide intervals, unattested relevant isolation, missing total cost or opposing material metrics prevent the requested claim |

Outcomes may coexist on different dimensions: e.g. fixed symbols suffice while
Python costs less. Report a vector, not a forced universal winner. If H1 fails but
H2 succeeds, say modification support without adaptive discovery. If H1 succeeds
and H2 fails, say bounded transfer without modification reliability. Exploratory
grade attaches to all substantive signals when containment/independence is missing.

## Publication classification versus future empirical verdict

`R6_31_EXPERIMENT_DESIGN_READY`: both protocols, controls, measurement/scoring rules,
prerequisite boundaries and falsifiable decisions specified for separate authorization.
`R6_31_DESIGN_PARTIAL`: a necessary design decision remains unspecified.
`R6_31_CAPABILITY_PREREQUISITE_GAP`: no credible bounded implementation path using
existing meanings can answer a hypothesis. `R6_31_PROTOCOL_HALT`: this authorized
design violates its boundary or preservation cannot be established. Known small
plumbing/fixture qualification needs do not imply that the design itself is partial
or that implementations already pass. This round selects **DESIGN_READY** only.
