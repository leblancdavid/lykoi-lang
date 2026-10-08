# R6.15 — bounded AI authoring comparison, protocol 1

Owner authorization: R6.15 AI Authoring Efficiency Challenge. Tracks A (standard
library Python) and C (explicit plans on unchanged R6.10 VM); production unscored.
No implementation, operation, historical artifact or external acceptance changes.

## Baseline and design

Verify kernel26, R6.10 publication, R6.14 preservation/publication before selecting
tasks. Record identifier-only provider inventory and targeted sanitized export
metadata probe. Provider listing does not authenticate routing or credentials.
Use the harness general-agent fresh contexts, same inherited model/default reasoning;
actual identities verified afterward. No configurable reasoning attestation available.
Shared filesystem/inherited repository guidance means exploratory classification.
Never disclose the other track's implementations in authoring prompts. Access rules
are cooperative, not OS isolation. Record actual accesses from tool metadata.

Select four new synthetic tasks after baseline: no historical scored implementations
or format examples supplied. Coordinator knows VM and earlier findings; selection is
implementation-aware, nonrandom and nonindependent. Freeze contracts and explicit
normal/boundary/adversarial observations before dispatch. Both tracks receive identical
contracts. Transport accepts bytes and projects only value/output or code/offset;
it computes no task relation. No callbacks or host algorithms in C execution.

## Fixed budgets (before task selection)

Two tasks per fresh authoring session, 600 seconds cooperative wall deadline per
session, 20 tool calls, at most one initial submission and one repair per task.
Every submitted candidate is frozen before acceptance; at most two development
test batches per task (author-chosen tests), each direct subprocess <=30 seconds.
No coordinator acceptance feedback or post-submission scored repair. Self-test
corrections count as repairs. Calls/tokens recorded afterward; no token limit claimed.
Exceeding deadline stops authoring; retain partial files and classify budget failure.
Model reasoning/dispatch cannot be forcibly interrupted by task tool: disclose this.
First attempt means first executable candidate before self-testing, not final handoff.

Counterbalance: wave1 A(T1,T3), C(T2,T4); wave2 C(T1,T3), A(T2,T4).
Separate fresh contexts for modifications A(T1,T2), C(T1,T2), C dispatched first.
Modification budget 600 seconds/20 tools/one candidate plus one repair per task,
same test opportunities. Original files immutable; revisions separate. Modification
contracts/observations separately hash-sealed before base authoring; reveal only after
all original submissions are frozen. Withholding is instruction-based; any premature
read or inherited content marks comparison contaminated. Coordinator's prior knowledge
is disclosed, distinct from authoring-context disclosure. Reserved-version additions
must not supersede frozen original observations.

## Scoring and measurements

One scored subprocess per task/phase/track <=30 seconds. All frozen observations
count; three executions each test determinism, repeats not extra unique coverage.
Exact recursive type-sensitive equality including fields, byte output and offsets.
No source-matching criterion. Classify invalid plan, authoring failure, missing
capability (only with supported analysis), interpreter error, conventional error,
and infrastructure failure separately. Retain raw observations and stderr on failure.
No scored artifact edits after handoff/deadline. Missing artifacts remain denominator.

Measure exported per-call input/output/reasoning/cache tokens and model/provider,
model calls, timestamps, development wall duration, tool elapsed times, self-test
repairs and first/final acceptance. Zero reported cost is metadata, not proved billing;
actual API cost unavailable without billing evidence. Never estimate usage from bytes.
Incomplete telemetry => partial/exploratory, never completed instrumented comparison.
Keep task-group effort separate from task-specific results; do not allocate tokens by
source size. VM structural nodes, canonical/published bytes, standalone validation
time and actual traversal visits (profiled separately), runtime work and public execute
time are separate metrics. Python bytes/AST branch-loop-function counts and execution
time are not interchangeable with VM metrics. Timing is finite host observation.

## Publication and stop

Publish protocol/frozen manifests, sessions/metadata, source/plans, original and new
acceptance results, failed attempts, comparison/limitations and recommended next step.
Verify historical hashes, kernel26, publication identities, relevant harness checks
and git diff --check (plus untracked-file whitespace). Stop after publication;
no automatic semantic development or P6-A04 acceptance/P6-A05 access.
