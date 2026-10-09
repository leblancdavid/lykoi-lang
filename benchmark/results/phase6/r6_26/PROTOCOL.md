# R6.26 — prospectively bounded model capability comparison

Owner authorization: the R6.26 request in the coordinating session. Initial Git
status clean. Coordinator knows R6.25 failures and creates these synthetic tasks;
no independent task sourcing, blinded selection or independent replication claim.

## Tracks and order

A is the immutable R6.25 Qwen3 8B record, historical calibration only, never a
paired fresh-task score. B is prospectively selected `openai/gpt-6.1-sol`, high
reasoning, through existing OpenCode 1.18.32 credentials/configuration. The catalog
advertises native tool calls, programming/reasoning capability, context1,050,000,
input922,000, output128,000. These are catalog limits, not measured effective
delivery. No optional C: another authenticated capable provider has not been
established and a second track is unnecessary for this bounded feasibility run.
No outcome-driven model switching or new dependencies/services.

Run neutral compatibility before calibration or fresh task exposure. Then exposed
OffsetTotal calibration, then N1–N4 in order, each a fresh OpenCode session/process
and fresh construction state. Identical semantic tools in every session:
declare_input, apply_operation (value/check/compose), define_result,
validate_candidate, from frozen R6.24 definitions and R6.25 normalization. The
calibration allows value only, matching R6.25. No supplied solution or acceptance
oracle in participant prompts. Same fixed prompt for all fresh tasks/models.

## Transport boundary

An experiment-owned standard-library stdio MCP bridge exposes exact existing
function descriptions and argument schemas as inputSchema; it must not add a
root type, flatten oneOf, fill arguments or repair semantic decisions. MCP
tools/call name/arguments and JSON-RPC request identity are mapped mechanically
to the existing R6.25 openai-compatible envelope. This is SDK/MCP-boundary
qualification, not capture of unobservable upstream HTTP envelopes. Preserve
the underlying OpenCode events and MCP requests/responses. Unsupported native
provider or MCP schemas make B unavailable; no scored tasks are exposed if the
neutral compatibility prerequisite fails. Minimal envelope changes, if needed,
must be separately recorded and neutrally qualified before a final freeze.

Neutral control exposes the same unchanged schemas but handles calls inertly.
Ask for one declare_input and one schema-correct value apply_operation with no
program execution. Require exact arguments and ordered matching feedback.
Schema visibility/startup failure is compatibility failure, not model incapability.

## Budgets and stopping

Per construction: at most16 model steps (OpenCode steps setting),24 dispatched
semantic calls (unchanged dispatcher), three correction turns after a rejected
call,180s wall. Native OpenCode step events count model completions; no provider
retry/tokenizer requests are inferred from them. Request output cap4096 per
response; catalog/effective distinction retained. Cumulative input/output caps
60,000/16,384 are checked at visible completed-step boundaries; requests already
in flight can overshoot, which is recorded and stops the session. Correction
turns use completed model-step grouping, not count of errors in a tool batch.
Stop immediately at validate_candidate success or exhaustion. No host repair,
semantic prompt tuning, cross-model sharing or outcome-informed retries.

Requirements, cases, prompts, tools, scripts and model config are hash-frozen
before scored exposure. Acceptance uses unchanged R6.24 evaluator, R6.23 adapter,
R6.18 expansion and R6.10 execution, plus structural clauses stated in tasks.
Expected invalid inputs/overflow/check failures are successful observations when
they match; absent executable stages are NOT_REACHED, not failed cases.

## Reporting and preservation

Report denominators for authorized tool selection, schema validity, successful
construction, completed artifacts and acceptance. Record SDK tokens/time/cost
when returned; missing is null, catalog/SDK zero cost is not proved zero billing.
Raw HTTP provider payloads, stronger reasoning attestation and hard OS isolation
may be unavailable. Fresh session is not proof of hidden-context exclusion.

Preserve production kernel26, compiler/lowerer/runtime, R6.10 VM, R6.18 wrapper,
R6.23 adapter, all semantic schemas and R6.3–R6.25 evidence. No P6-A04 acceptance
or P6-A05 access. Execution remains LLM-free. Publish one terminal classification,
integrity manifest/receipt and recommended separately authorized next experiment;
then stop. No automatic resume after incompatibility or publication.
