# Learning-failure analysis

Evidence is the preserved [R6.59](../R6_59-REPORT.md),
[R6.60](../R6_60-REPORT.md) and [R6.61](../R6_61-REPORT.md) observations.
No new inference or historical rescoring occurred.

The complete-package objective improved exposed target likelihood but did not
establish construction. R6.59 completed20 updates/80 presentations of six records
(13–14 each), updating all112 adapter tensors. R6.60 dropout-off equal-record NLL
fell1.647022447→1.504800672, pooled1.627590528→1.487384112. Operation names,
references and types as well as formatting improved under exact gold prefixes.
R6.59 raw generation remained0/6 versus0/6 strict and functional acceptance;
semantic/runtime stages were NOT_REACHED, not measured wrong semantics.

R6.61 measured fence73594 as first-token rank1 on all six prompts for both models
at penalties1.0/1.1. Repetition penalty suppresses prompt-present opening4913;
the fence already wins at1.0. Supplying only `{"` led to0/24 schema-valid packages.
All24 parse as ordinary JSON objects; native bounded loader validity is a separate
stage. Twenty-two immediately choose an inadmissible envelope key; two E05/1.0
outputs choose version7 and omit the remaining envelope. At1.0 five tasks echo
prompt content; at1.1 outputs are short snippets. All terminate at EOS without
token/time truncation. This contradicts a first-token-only sufficient explanation.

| Candidate cause | Evidence | Status and discriminating future control |
| --- | --- | --- |
| Insufficient exposure | Only20 updates, first usesLR0, six targets13–14 times; fitting observed | Plausible, not proven. A frozen exposure-dose comparison with same data would be needed; do not prescribe more steps from current losses. |
| Insufficient diversity | Six correlated short stateless targets; whole cohort10 endpoints/5 nominal families/2 scaffold components, Tier E0 | Measured coverage limitation; causal responsibility unresolved. Compare structurally diverse, matched-budget training after qualification. |
| Output-format complexity | Fencing, omitted envelope, invalid version; raw opening correction insufficient | Observed package-structure gap. Smaller-unit structure learning is a hypothesis, not evidence B/C wins. |
| Long-range dependency construction | Targets have local depth2–4, nested compositions absent from trained six | Untested generated dependency correctness: no candidate reaches type/semantic validation. No demonstrated dependency failure in a valid package. |
| Typed operation selection | Teacher-forced op/type/reference likelihood improves; no generated program | Useful distribution fitting, not free semantic choice. Measure add/le/eq selection with typed state and withheld contrasts. |
| Prompt/target alignment | R6.60 exact messages/native template/prefix/masks match; no training-only scaffold | No observed role/template mismatch. Requirement→answer-snippet interpretation remains a possible task-alignment issue, not a proven hidden cause. |
| Autoregressive error propagation | Gold-prefix fitting differs from own-prefix greedy decoding; early fence/key divergence | Conditioning difference established; downstream causal contribution not isolated. Validated incremental rollout may limit local damage but introduces policy/state exposure shift. |
| Capacity limitations | One1.5B checkpoint, rank8 q/v adapter, tiny fixed run | No capacity ablation or sufficient-data plateau; cannot conclude model too small. Also cannot claim it will learn with more data. |

The architecture does not lack meaning merely because generated packages fail.
Ground-truth targets execute under the admitted finite fixtures. Existing mechanics
are qualified; observed failure is generation in this checkpoint/data/objective/
decoding configuration. No single cause is identified. Format constraints, longer
training, new prompts or tool use would be interventions requiring separate freezes,
not retrospective repairs. Improved likelihood on repeated targets may include
memorized fragments; exact reproduction0/6 does not disprove memorization.
