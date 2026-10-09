# R6.33 — single AI symbolic lifecycle pilot

Owner authorization is the R6.33 request in the coordinator conversation.
One fresh synthetic, capability-tailored development requirement; exploratory
feasibility only. No independent sourcing, unbiased discovery, H1/H2 comparison,
efficiency benefit or generality claim. Coordinator designs the requirement and
oracle; a separate OpenCode primary session authors all executable definitions.
No production or experimental execution foundation changes are authorized.

## Frozen requirement (exposed first)

Create a reusable family `BoundedScore` with ordered parameters
`x:Int64, y:Int64, limit:Int64, bias:Int64 -> Int64`. It consumes no bytes.
Check x nonnegative first (`X_NEGATIVE`, site x), then y nonnegative
(`Y_NEGATIVE`, site y). Compute x+y using checked existing addition, reject if
that sum exceeds limit (`SUM_LIMIT`, site x), then return sum+bias using checked
addition. No extra input refinements, effects or new meanings.

Create two **independently constructed closed Int64 caller definitions**:

- `CallerA`: read x then y as UInt8; call the admitted exact BoundedScore pin
  with limit300/bias7; then require end of input; return the call result.
- `CallerB`: read x as UInt8; call that same pin with y11/limit200/bias3;
  then require end of input; return the call result.

The reusable logic must exist only in the shared definition, with explicit compose
references in the callers. Neither expanded-copy reuse nor name-only binding counts.
All reads, checks, expressions and end checks preserve declared order. Rejected
compositions absorb before a caller's trailing-input check.

## Separately frozen modification (withheld until original reuse passes)

Create a new immutable BoundedScore with the same exact family/signature. After
the original ordered checks, compute sum+bias and then add a surcharge of2 using
existing checked addition. Preserve the predecessor. Explicitly admit a CallerA
successor changing only its dependency/call pins. CallerB retains its old exact
pin. Explicit total migration decisions must update old CallerA and retain
CallerB. No implicit reference redirection. Both old and new CallerA remain saved.

## Frozen acceptance and dependency/impact expectation map

Before exposure freeze scorer source and all contracts in FREEZE.json. Original
A returns x+y+7 for x+y<=300, otherwise SUM_LIMIT. Original/retained B returns
x+14 for x<=189, otherwise SUM_LIMIT. Modified A returns x+y+9 for x+y<=300.
Test all64 pairs from {0,1,11,127,189,200,254,255} and all256 B byte values.
At each phase also test EOF, extra bytes, and limit-reject plus trailing bytes.
Direct signed-parameter probes check x/y precedence, negative limit, sum overflow,
bias overflow, valid boundary, and encode-range rejection. Observations include
exact typed values/output bytes, raw errors, ordering and logical work.
Repeat saved execution3 times in a fresh AI-free process; compare full observations.
Exercise every work cutoff for representative successful/rejected A/B inputs.

Before modification, direct users of BoundedScore(old) are exactly A(old),B(old).
After selective migration selected roots are A(new)->BoundedScore(new) and
B(old)->BoundedScore(old). Old A and all predecessor definitions remain identical.
The successor edge map contains BoundedScore(new)->old and A(new)->old. Migration
decisions are exactly {A(old):A(new),B(old):null}. This map is requirement-derived
and independently specified from registry output, not independently reviewed.
Production impact output is recorded as diagnostic evidence only; this symbolic
package is outside its production-model API domain. No repair of that API.

## Authoring and mechanical broker

Fix OpenCode1.18.32, provider openai/model gpt-6.1-sol, variant high before results.
Use an experiment-local primary JSON author agent with all permissions denied,
external plugins/skills disabled. No callable author tools; host broker dispatches
explicit JSON action requests through unchanged R6.32 Registry and Journal.
Record injected configuration, advertised model metadata/context limits, requested
reasoning, every prompt/raw CLI event/export and actual usage. Provider hidden
context/effective tool schema/reasoning attestation and billing may be unavailable;
never infer missing telemetry. Shared coordinator/provider platform is disclosed.

Five stages: predecessor admission, caller batch admission, successor admission,
CallerA successor admission, explicit migration. At most3 proposals per stage,
15 model invocations total,600s timeout each. One fixed model/session; no model
selection/tuning after outcomes. Transport failure halts. JSON/schema/functional
failure may get only native diagnostics or failed acceptance rows, at most2
correction turns. Preserve every failure; never manually repair semantic content.

Author returns exact R6.18 definition objects **without identity**. The broker
only calls unchanged `c.seal` to compute hashes, preserving all authored semantic
fields. This mechanical operation is frozen in advance. Dependencies/call pins
must be actual retrieved hashes supplied in subsequent feedback; no placeholder
replacement, synthesized body, automatic caller repinning or semantic repair.
Admission must be requested explicitly, including predecessor for successors.
Migration is a separate author request after retrieval of the new caller hash.
Registry/validation/retrieval/expansion/execution timings and events are preserved.

Terminate CLI authoring before replay; write AUTHORING-CLOSED.json and export
the session. Replay command has no model invocation path. Saved raw/canonical
artifacts and expansion maps are verified by hashes. Trace observation uses a
temporary Machine.run observer restored after each execution, changing no
execution decisions or source. Trace/ordinary execution must agree.

## Publication and stop

Classify supported only if all five AI stages, original reuse, selective migration,
functional acceptance and exact AI-free replay pass. Otherwise classify the first
observed authoring/infrastructure/protocol gap or partial completed lifecycle.
Preserve R6.3–R6.32, production/kernel26, R6.10/R6.18/R6.23/R6.25 and existing
registry/admission/telemetry. No training, P6-A04 acceptance or P6-A05 access.
Publish additive report/evidence/measurements/integrity receipts, git diff --check,
then stop awaiting explicit authorization. No automatic follow-up experiment.
