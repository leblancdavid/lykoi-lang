# R6.75 successor CPU-only preflight

Authorization: one additive qualification of R6.74's three mechanical defects.
No weights, inference, gradients, optimizer/scheduler instances or updates. The
54 training records, equal-record completion+EOS mean /4 rule, 216 presentations,
AdamW settings and warmup6/linear54 arithmetic stay exact. Kernel26, production,
experimental semantics and R6.3–R6.74 evidence stay unchanged. No P6-A04 acceptance,
P6-A05 access, dataset expansion, comparison adapter or historical rescoring.

Stages: baseline identity verification; freeze inputs/expected results and complete
prospective worker configuration; CPU numerical/semantic/resource qualification;
fresh-process base/train/adapter launch-path dry run; publication and stop.
Every output is exclusive; failures retain tracebacks and require additive attempts.

Normalization control is separate synthetic data, never a training row. Counts
2/4/6/8 include a final EOS surrogate. Two-class logits [0,0], [0,1], [0,2],
[0,3] predict class0 at completion positions only. Prompt, post-EOS and padding
are -100. Nonprediction logits are poison [0,9] to detect incorrect shifting.
Expected CE per record is log(1+exp(i)); each backward contribution is CE/4;
accumulated contribution is sum(CE)/4, differing from sum(count*CE)/20.
Float32 installed CE must exactly match manual shifted CE and its /4 contribution;
analytic frozen expectations have 2e-6 absolute tolerance. No backward is called.
Equal-length inputs and nondiscriminating losses must reject as invalid controls.

Only reserved scope name hyphens map to underscores, preserving every other scope
field, target, requirement, case and operand/dependency obligation. Rehash scope
identity and its prompt envelope only. Six exposed calibrations stay byte-equivalent
as JSON values. Any other change rejects rather than modifying expectations. All
diagnostics remain coordinator-authored exploratory evidence, not independently
withheld evaluation.

RSS uses stdlib Windows working-set query with handle-derived PID; Linux uses
/proc current VmRSS; other platforms return explicit null/unavailable. Missing or
misattributed readings fail closed for budget enforcement, never become zero.
Only the experiment-local resource binding changes in the inherited worker.

The prospective launcher uses a separate explicit execution authorization variable.
Dry mode preserves hidden CUDA, spawns the same worker entry point for all three
phases, resolves/compiles real functions and configuration, validates actual CPU
resource checks and returns before model loading. No simulated inference or updates
count as qualification. Actual GPU/model/generation behavior remains untested here.
