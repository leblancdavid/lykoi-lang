# R6.31 — Comparable AI conditions, telemetry and cost accounting

## Model and session contract

Use the same capable model/provider route/version and requested reasoning settings
across all conditions, pinned before task exposure after neutral calibration.
Historical `openai/gpt-6.1-sol` / OpenCode1.18.32 is a feasible candidate, not a new
selection or availability certification in R6.31. Local inference is optional.
If a route becomes unavailable, preserve the halt; model replacement needs a new
pre-exposure freeze and cannot splice selected winning observations into a comparison.

Record exact requested and returned model/provider, route, runtime executable hash,
temperature/top_p/seed where supported, context/output caps, reasoning variant,
tool choice, concurrency/cache policy, startup settings and all exported effective
configuration. Requested high or reported zero reasoning tokens does not attest
effective reasoning. Unknown effective settings get null plus explanation; claims
are restricted to requested/exported comparability. No training/fine-tuning.

Same requirements, budgets, resource class, selftest opportunity and supervisor;
track tools must reflect actual architecture. Meter differences in batching,
schema size, retrieval and tool choice rather than claiming equal tool names remove
workflow effects. Prefer the smallest truthful facade; keep R6.25 argument contracts
unchanged and do not infer/repair author decisions. Pin all facade implementations.

## Durable event plan

Before dispatch append session ID, hypothesis/condition/task/application/change/
replicate, prompt/package hashes, base/library/foundation IDs, monotonic start and
UTC time. Flush request, tool arguments, feedback, artifact and termination events
as they occur. Supervisor owns each process/session and waits within that stage's
budget; outer terminal timeout cannot silently discard completed native events.
Retain interrupted event tails, errors, stderr, completed exported messages and
missing-usage status. No replay inference just to recover metrics.

Per model call: exact supplied context and token size if observable; input/output/
reasoning/cache-read/cache-write/SDK-total tokens with source and counting semantics;
started/completed status, attempts/retries if visible, cost field as returned,
actual billing receipt/price schedule if available, wall elapsed and load/prompt/
generation durations if exported. Retain reported counts without silently summing
overlapping output/reasoning/cache categories. Missing telemetry is **null**, not0;
incomplete cumulative counts are lower bounds. SDK cost0 is not a bill.

Per deterministic tool: ID/name, request/response hashes, success/error, wall/CPU,
bytes, serialization/schema/lookup/admission/type-check/expansion/lowering/compilation/
execution spans, artifact lineage. Nested spans show inclusive/exclusive values;
never add validation twice when expansion invokes validation internally. Per stage:
process startup/end-to-end wall, active author/human minutes, tools, calls, failures,
first/final seals and budget status. Assistant-message elapsed is not pure inference.

Count coordinator setup, human macro design, library docs/indexing, retrieval misses,
failed proposals/attempts, acceptance preparation, fixtures, transport qualification,
metering, maintenance and publication separately. Common setup is allocated equally
to planned conditions; condition-specific new setup is charged to benefiting
conditions. Publish both full and amortized allocation and a sensitivity table,
not a favorable allocation only. Inherited production/VM development effort is
explicitly unavailable or historical; a measured incremental advantage is not a
fully known lifetime-cost claim.

## H1 complexity and amortization

Record per entry and full library: proposed/accepted/rejected counts, semantic
body steps, parameter signatures, transitive closure depth, canonical/raw bytes,
index/docs bytes and actual exposure tokens; expanded task bytes/node count,
representation size including libraries, runtime work and validation cost.
Discovery cost per accepted abstraction equals **all** proposal/admission/rejection/
documentation expenditure divided by accepted entries; also report individual
lineages. With0 accepted entries the ratio is undefined and total wasted effort
remains visible. Allocate shared discovery across accepted entries equally as an
accounting convention and retain unallocated raw totals.

Reuse: direct/static calls, dynamic entered calls, successful distinct task contexts,
transitive calls, retrieval misses and wrong-use failures. One task calling an entry
100 times is not100 transferred requirements. Registry closure fetched once versus
repeated per session is metered under the pinned cache policy; cache savings are
observed, never assumed.

For each comparable resource dimension d (tokens, billed currency where known,
active human time, author wall, tool CPU) compute:

`Total_X(N,d) = Setup_X(d) + Development_X(d) + Maintenance_X(N,d)
               + sum(Evaluation_X(task,d), task=1..N)`

Publish incremental workflow totals and totals including new experiment setup.
Do not combine seconds/tokens/dollars into a weighted "efficiency" without a
predeclared conversion. If labor pricing is desired, publish sensitivity at fixed
rates chosen before evaluation; unpriced human time remains its own dimension.

For a comparator Q and discovered track L1:

`ExtraFixed_d = Fixed_L1(d) - Fixed_Q(d)`

`NetSavingPerReuse_d = Variable_Q(d) - Variable_L1(d) - MaintenancePerReuse_d`

When savings>0 and correctness is no worse, estimated break-even reuse count is
`max(0, ceil(ExtraFixed_d / NetSavingPerReuse_d))`; if savings<=0 there is no finite
break-even under that scenario. Label marginal-reuse stationarity as an assumption.
Use observed tasks first: cumulative total-cost curves at N=1,4,8,12, with rejected
and unused abstraction costs included. Report comparison against A, L0 and LH,
uncertainty ranges and maintenance sensitivity (0%,25%,100% of discovery expenditure
per12 tasks). Actual maintenance during sealed evaluation is0 only if none occurred;
it is not a forecast that future maintenance is free. Projected break-even outside
observed tasks is not demonstrated benefit.

## H2 effort and completeness

Separate accepted-base fixture preparation, modifier authoring, impact prediction,
diff/snapshot processing, validation/generation, selftests, repairs, offline scoring
and publication. Report tokens/calls/wall/total tooling for both first and final
candidate, per change/application and all planned runs. Include failed branches.
Fully costed ranking requires complete comparable selected resource dimensions;
unknown billing blocks a billed-cost claim, unknown coordinator usage blocks a
full-token workflow claim. Other complete dimensions may still yield bounded
descriptive conclusions. Durable telemetry qualification must include interrupted
calls, missing usage and nested spans before main authoring.
