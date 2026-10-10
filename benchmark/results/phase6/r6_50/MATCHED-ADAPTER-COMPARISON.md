# Future matched-adapter study — R6.50 design

No checkpoint selected, adapters built or study run. Require all readiness gates
in [matrix](READINESS-GATES.md), independent frozen evaluation and separate owner
authorization. Pre-register hypotheses about functional construction and fully
costed effort; successful specialized construction does not prove language superiority.

## Minimum four cells

| Cell | Weights | Target |
| --- | --- | --- |
| Base-L | One unchanged shared open-weight checkpoint | Lykoi semantic representation |
| Base-P | Exactly the same unchanged checkpoint | Conventional Python |
| Adapter-L | Shared checkpoint + Lykoi LoRA | Lykoi semantic representation |
| Adapter-P | Shared checkpoint + Python LoRA | Conventional Python |

If QLoRA is used, quantize/freeze the same base identically for both training arms.
Pin source revision, tensor/tokenizer hashes, license, prompts, precision and inference
runtime. Keep untouched base controls on the same inference quantization. No specialist
base for one arm. Each paired requirement supplies two approved language targets;
underlying family distribution, positive/negative behavior and task difficulty match.

## Budget matching and residual differences

Match rank, target-module policy, optimizer, learning-rate schedule, seed list,
sequence policy, effective batch, maximum optimizer updates and compute cap.
Measure actual GPU seconds/peak memory and **non-padding processed tokens**, with
prompt/completion/loss-bearing counts separately. Match total training-token budgets
within a predeclared tolerance (proposed 5%); also report a paired-episode-balanced
sensitivity analysis, because different representation lengths prevent simultaneous
exact token and episode weighting. No hidden duplication of short Lykoi targets.
Fix packing/truncation rules; reject rather than silently truncate obligations.
Tune both adapters on development-validation components only with equal search
budgets, and freeze selection before evaluation release. Seeds reuse paired sampling.

Use equivalent requirement/FRC prompts and the same functional acceptance. Language
documentation differs only by target interface, is pinned and equally accessible;
include its tokens, retrieval and validation costs. Primary comparison can be direct
target authoring; tool-assisted authoring is a separately registered symmetric arm.
Do not pool production and experimental Lykoi targets without foundation-stratified
results or claim runtime limits are identical language capabilities.

## Inference, repair and scoring

Fix context, temperature/seed, output-token cap, wall/compute cap, validation calls,
feedback policy and number of repairs (proposed first attempt + at most two repairs)
identically. Same requirement sequence and provider assumptions; arm order randomized.
The custodian scores frozen submitted artifacts. Participant access excludes hidden
tests/oracle and sibling solutions. Retain first-result failures, static rejections,
behavioral failures, capability gaps, timeouts and NOT_REACHED separately.

Report whole-contract acceptance first-pass and after repairs; successor regression;
family/component-level paired differences; cost/tokens/wall time and all setup/data/
review effort. Use paired component bootstrap intervals or exact paired analysis
where sample size allows; tiny cohorts are descriptive, not significance claims.
Pre-register stopping/sample-size criteria after an independent pilot and before
test release. Report task and construct strata and excluded-contract counts to avoid
language-capability filtering after outcomes. Base-to-adapter gains in both languages
and their paired difference are required; tuned Lykoi versus untuned Python alone
cannot support a language superiority claim.
