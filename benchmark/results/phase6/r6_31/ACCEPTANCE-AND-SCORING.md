# R6.31 — Acceptance and scoring methodology

Freeze exact executable expectations later, before participant exposure, using
these rules. No acceptance execution occurs in this design publication.

## Common requirements and oracle qualification

All tracks receive identical functional requirements, types, observable errors,
precedence and storage/transport boundaries. Track-specific documentation describes
tools, not a suggested solution. Do not prewrite a detailed operation sequence if
the question requires algorithm/abstraction choice; state only externally required
order where errors/effects make it observable. Count supplied scaffolding tokens.

Derive oracle behavior mathematically or with a separate requirement-level state
model, outside candidate implementations/generators/lowerers. Cross-check neutral
native scripted witnesses before freezing. Do not make the C runtime its own
behavioral oracle. Explicitly specify exact scalar types (Bool not Int64), signed
bounds, ordered first failure, absence of partial output and agreed wire projection.
R6.10 check errors are `validation`; overflow is `structure`; encoding failures
remain native. Internal IDs/work are conformance measurements, not arbitrary Python
functional obligations. A projection may normalize incidental identifiers only,
never rewrite behavior to pass.

Separate negative scorer controls: correct, valid-but-wrong, malformed, duplicate
keys, missing/extra output, wrong exact type, precedence inversion, nondeterminism,
timeout, state corruption and rejected-write mutation. For H2 also include a no-op
edit, changed-one-caller-only and new-endpoint-only candidate; all must fail relevant
changed-behavior cases. Qualification failure blocks primary scoring.

## H1 observations

At least24 unique directed observations/task: ordinary cases, boundary values,
type/signature rejection, competing failures, overflow/encoding and unsuitable-reuse
conditions where applicable. Declare category counts and case-to-obligation map in
the frozen task manifest. Exhaust small tractable domains in addition; enumerate
coverage and repetitions separately. Program validity, semantic conformance, desired
behavior and discovery-transfer witness are distinct outcomes.

Primary unit: **fully accepted task session**, first submission and final submission
reported separately. Acceptance requires all required external observations and
reproducible model-free execution. Report per-task results aggregated across three
replicates, not72 or216 independent requirement samples. Secondary metrics: case
pass rate, schema/type/dependency failures, wrong behavior, repair count, transfer
identity uses, negative transfer, compact/expanded bytes and cost.

## H2 original versus modified observations

For each application freeze at least32 base observations spanning every operation,
each invariant, multiple-operation sequences, restart, rejection atomicity and both
shared consumers. Each change has at least16 unique new or intentionally changed
observations plus16 retained observations, covering both consumers and untouched
operations. More observations are required if needed to cover all obligations;
numeric minima cannot substitute for coverage. Fixed injected clock/ID resources,
fresh scenario storage and process restart avoid incidental nondeterminism.

Before reveal record base output/state bytes and exact expected old behavior. Frozen
supersession map identifies which old obligations change and why; each old case is
retained, superseded or genuinely inapplicable with requirement citation. No
post-performance deletion of cases. Modified scoring reports:

- New/changed expectation pass counts and strict full modified checkpoint acceptance.
- **Passing-to-failing regression:** a previously passing retained observation now
  fails under unchanged expectation. Denominator is passing retained base observations.
- **Unintended behavior change:** a differing observed output/error/order/state on
  a retained requirement, including interactions outside the edited operation.
  Distinguish newly failing expectations from additional differences detected by
  sequence/differential probes; no duplicate counting in a defect total.
- Superseded-old results separately; an intended change is not a regression. Testing
  the modified artifact against old superseded behavior is a diagnostic, not a score.
- Refactor-only branches preserve all old expectations and must meet the shared-use
  structural requirement; no-op source copying cannot pass that requirement.
- Persisted state reload, rejection byte preservation and invariant consistency.
  Keep any historical migration requirement explicit; no implicit data repair.

Primary unit is a **fully accepted modification branch/session** including retained
behavior, reported first/final. Aggregate by application and change class; four
branches on one base and three replicates are correlated, not12 independent apps.

## Change-impact accuracy

Before edits, author predicts affected existing operations/consumers, invariants,
state fields and declared error/ordering obligations. Retain raw automatic-tool
output separately from model-enriched prediction and post-edit explanation.
Independent acceptance author freezes required semantic-change set R from the
requirement and consumer/dependency inventory before modifier authoring. Map A/B/C
representation-local names to the same semantic IDs; do not score line counts.

For predicted set P report precision=|P∩R|/|P|, recall=|P∩R|/|R| and F1, plus false
positives/negatives per category. Empty P with nonempty R has precision convention0,
recall0 and F1=0; if both empty mark not applicable. Refactor R contains the required
shared-definition/caller structural effects, although external behavior is unchanged.
Also measure predicted **behaviorally affected** consumers against independently
frozen witness obligations; keep structural and behavioral impact separate.
Overpredicting every node cannot earn perfect precision. Ground-truth disagreements
are unresolved measurement cells, not tuned to favor C. Legacy C omissions remain
in automatic impact recall; optional manual tracing is counted as author effort.

## Failure and repair accounting

Seal first submitted complete candidate before any tool feedback from its selftests;
capture earlier invalid construction attempts separately. Repair iteration means
each subsequent submitted candidate/revision after a failure; correction turns,
tool sequencing errors, setup fixes and resubmissions without failures are separate.
No manual repair to scored author artifacts. Report testing choices and test volume
even with identical opportunity limits.

All planned cells stay in accounting. Native categories: unsupported semantics,
argument/schema/type/pin/closure rejection, incorrect behavior, regression, budget
exhaustion, provider failure, harness/oracle failure, missing telemetry, contamination.
Author failures are unsuccessful planned sessions. Harness/provider interruptions
are incomplete comparison cells with first artifacts retained; do not turn them
into language failures or success. Downstream NOT_REACHED is not invented failure
execution. Complete-case successful-pair efficiency analysis is secondary and may
not erase failure cost. Record censored wall/token bounds instead of zero.

Scoring gives no acceptance answers to authors. After all seals, perform offline
acceptance and two model-free reload/replay passes; repeats check determinism, not
increase sample size. Runtime conformance and raw envelopes supplement acceptance.
Outcome-informed oracle corrections require an independently justified successor
record and authorization; original expectations/results/classifications persist.
