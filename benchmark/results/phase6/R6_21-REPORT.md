# R6.21 — Compact prompt and local authoring qualification

**Final classification: `R6_21_PROTOCOL_HALT`.**

The compact interface eliminated observed input truncation for the two evaluated
authoring calls. One model-authored parameterized definition passed unchanged
R6.18 validation and deterministic execution on three input cases. The third
authoring request returned **HTTP500: `prediction aborted, token repeat limit
reached`**. The frozen stop rule terminated inference immediately. Remaining
calibrations and both paired authoring interfaces are **NOT_REACHED**.

Local symbolic discovery is **not ready for another attempt**: intact compact
delivery and one executable composition are supported, but bounded runtime
completion reliability failed. This is neither a universal model-authoring gap
nor a representation impossibility result.

## Authorization, baseline and preservation

Owner authorized bounded nonproduction R6.21 interface correction. The coordinator
knew R6.19/R6.20 outcomes and authored synthetic feature-tailored neutral tasks;
this is outcome-informed qualification, not independent replication, unbiased
task selection or generalization. Only the pinned local model generated candidate
definitions. No manual semantic repairs or participant retries occurred.

[Baseline](r6_21/BASELINE.json) verifies **972 protected identities**, including
R6.19/R6.20 baseline/publication manifests, receipts and all published bytes.
R6.19's nine rejected proposals, empty vocabulary and halted request are preserved;
R6.20's truncated prompts, failed outputs and halt remain preserved. All shared
guidance pinned by historical publications remains byte-identical. Current guidance
is added through separate supplements rather than editing pinned prose.

Production kernel remains **26 constructs**. Production compiler/lowerer/runtime,
R6.10 VM and R6.18 wrapper/schema/semantics are unchanged. Exact VM SHA256:
`bf5dbfb96d6d50124d109c35804c81e5a27bf4038b7f65b1a909ad4f0cc13fa3`.
Wrapper SHA256:
`e5e57901d4df32bcb2eed3b5bbd7ce6f19ee3145bbf71303d96e15b4e3d67fab`.
No new operations, MCP infrastructure, training, remote participant provider,
installation/download, P6-A04 acceptance execution or P6-A05 access occurred.

[Protocol](r6_21/PROTOCOL.md), [contract](r6_21/CONTRACT-1.txt),
[tasks](r6_21/TASKS.json), [schema checks](r6_21/SCHEMAS.json),
[fixed library](r6_21/LIBRARY.json), runner and seven host controls were
[frozen](r6_21/FREEZE.json) before participant inference. The runner/contract/tasks
were not changed after outcomes. A separate posthoc publisher performs accounting
and integrity checks without inference or tokenization.

## Exact local configuration

[Inventory](r6_21/INVENTORY.json), [server log](r6_21/SERVER.log),
[local process evidence](r6_21/LOCALITY.json) and raw calls retain settings.

| Setting | Recorded observation |
| --- | --- |
| Runtime | Existing Ollama **0.35.0**, version endpoint verified |
| Model | Existing **qwen3:8b**, Qwen3, 8,190,735,360 parameters, GGUF/Q4_K_M |
| Manifest digest | `500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41` |
| Verified GGUF SHA256 | `a3de86cd1c132c822487ededd47a324c50491393e6565cd14bafa40d0b8e686f` |
| GGUF size | 5,225,374,496 bytes |
| Hardware | Existing RTX4070/32GiB host; GPU inventory retained |
| Model metadata context | 40,960; not treated as effective delivered budget |
| Effective loaded context | **8,192**, confirmed by runner slot logs and per-call `/api/ps` |
| Conservative accepted input | **<=3,584 runtime-tokenized tokens**, below R6.20's observed4,098 cutoff |
| Capacity rule | Input + requested output +256 margin <=8,192; authoring output reserve2,048 |
| Sampling | temperature0, seed621, top_k20, top_p0.95, repeat_penalty1 |
| Output caps | Calibration/A2,048; B512/stage, four stages, total2,048/objective |
| Structured output | Generic `format:"json"`; full schema checks performed after generation |
| Prompt transport | `raw:true`, `/api/generate`, exact explicit ChatML including closed empty thinking prefix |
| Concurrency/locality | One sequential caller, one loaded model, parallel1, loopback127.0.0.1:11435, cloud disabled, backend `--offline` |
| Baseline symbolic subset | Unchanged seq/UInt8 atom/value/check/end/UInt16BE emit; ref/const/add/le/eq; Int64/Bool/Unit |
| Authoring subset | Task-filtered value/check/compose nodes and applicable expression grammar; no reads/end/new semantics |

The seed and raw serialization are declared prospective changes from R6.20,
fixed before results. `/tokenize` is the existing bundled local backend endpoint,
not new infrastructure. Runtime templates and default parameters are retained in
inventory; the raw path avoids opaque chat-template expansion. Locality is
configuration/process evidence, not continuous OS network isolation. The
experiment-owned parent/descendants were terminated; the desktop service was not
targeted ([cleanup](r6_21/CLEANUP.json)).

## Compact contract and intact prompt delivery

The versioned contract defines shapes once using a short machine-readable grammar.
Required rules are explicitly separated from optional short-ID/compact-JSON
guidance. It includes immutable typing/references, exact deps and order, template
argument substitution, direct identity pins, hygienic scope, absorbing failures,
seq provenance/work, fixed output encoding and wrapper/VM resource limits. No
task-specific solution examples are embedded. Fixed Echo/Relay identity templates
are supplied only for objectives that call them; these are host-authored library
definitions, not discoveries. The original executable schema remains external to
the authoring prompt. Task-specific grammar filters remove unused node/expression
alternatives; shared semantic prose and type rules remain for completeness.

R6.20 repeated entire schemas approximately9,900 tokens in a shared instruction.
R6.21's two evaluated complete serialized authoring prompts measured **961 and953
tokens**, roughly an order of magnitude smaller. This comparison uses R6.20's
published approximate original-input size and R6.21's actual runtime measurements;
no precise percentage is inferred. A fully exercised nested/incremental prompt
size is not available because those objectives were not reached.

[Tokenizations](r6_21/TOKENIZATIONS.json) preserve the exact local tokenizer token
IDs and count for every checked prompt. Raw calls preserve exact serialized prompt
and request bytes plus their SHA256 identities. Before sending each substantive
request, the harness measures input, rejects unsafe counts and reserves its output
cap/margin. Before evaluating any output it requires:

1. Expected tokenizer count = API `prompt_eval_count` = logged `task.n_tokens`.
2. Logged runner slot and loaded-model context both8,192.
3. No logged input truncation.

[Delivery controls](r6_21/DELIVERY-CONTROLS.json) passed **3/3** first/last sentinel
extractions at **50,1,651,2,851 input tokens**, all counts matching exactly.
Warmup's34 reported tokens also matched post-load tokenization; its initial
ungated output was not used as authoring evidence. An intentionally oversized
prompt was tokenized and rejected **without generation**
([guard](r6_21/OVERSIZED-GUARD.json)). This proves the guard branch, not handling
of a full8,192-token input. No safe-bound maximum or long-session claim is made.

[Prompt delivery](r6_21/PROMPT-DELIVERY.json) confirms intact delivery for **both
evaluated symbolic requests**. F3 preflight and backend log both report969 tokens,
with no truncation and release `truncated=0`; HTTP500 has no final API usage fields,
so the full success-response delivery criterion is unavailable. Its output was
never evaluated. No truncated request was silently accepted.

## Neutral calibration: separate validity layers

[Complete neutral results](r6_21/NEUTRAL-RESULTS.json) distinguish all six planned
objectives; [raw calibration](r6_21/CALIBRATION.json) preserves actual evaluations.

| Objective | JSON / strict / schema | Full type / semantic validation | Executable correctness |
| --- | --- | --- | --- |
| F1: operations and typed literals | All pass | First failure DEPENDENCY; complete type pass not established | NOT_REACHED |
| F2: typed n:Int64 input and immutable copy | All pass | Both pass;4 expanded nodes including adapter/encode | **3/3 cases pass**, full envelopes repeat |
| F3: local reference/add dependency | Runtime HTTP500; no candidate returned | NOT_REACHED | NOT_REACHED |
| F4: ordered checks | NOT_REACHED | NOT_REACHED | NOT_REACHED |
| F5: nested fixed reuse | NOT_REACHED | NOT_REACHED | NOT_REACHED |
| F6: deterministic addition/output | NOT_REACHED | NOT_REACHED | NOT_REACHED |

F1 selected value operations and exact declaration fields, but emitted self refs
instead of requested literals, with empty deps. The unchanged wrapper rejected
the first step's dependency mismatch; it did not reach later cycle diagnostics.
The failed original output remains intact and was not repaired.

F2 authored one typed reusable definition: parameter `n:Int64`, one Int64 value
step referencing n with exact deps, ordered execution and returning that step.
The host only seals the definition and instantiates the frozen one-call adapter.
For inputs **0,17,65,535**, unchanged VM returns matching values, UInt16BE bytes
`0000`,`0011`,`ffff`, consumed0 and work10. Each entire envelope is identical on
two executions: **three unique cases, six execution observations**. This is one
valid model-authored composition, not three independently authored compositions.
It demonstrates typed identity transfer and deterministic output; it does not
establish computed arithmetic, ordered failure or model-authored nested reuse.

Totals: **6 planned,3 attempted,2 outputs evaluated,1 completed objective,1 valid
composition,1 semantic rejection,1 runtime failure,3 not reached**. The success
rate is1/2 among returned/evaluated candidates,1/3 among attempted objectives;
the remaining three are not counted as failures. Seven pre-inference
[host controls](r6_21/HOST-CONTROLS.json) distinguish JSON, duplicate-key,
schema, type, dependency and valid-but-wrong/execution-encoding cases. Host controls
are not participant successes. Wrapper diagnostic precedence blocks whole-type
claims when a prior semantic diagnostic is returned.

## Complete-plan versus incremental comparison

[Comparison](r6_21/COMPARISON.json), [complete-plan record](r6_21/COMPLETE-PLAN.json)
and [incremental record](r6_21/INCREMENTAL.json) publish the frozen four-objective
paired schedule and explicit **NOT_REACHED** status.

A was designed for one complete-definition call with cap2,048. B was designed for
four cap512 decisions: operations/header/typed signatures; node bodies/deps;
order; result. Deterministic assembly copies fields by submitted IDs and validates
the final definition with unchanged R6.18. Both receive the identical compact
semantic text, objective, library and output-format descriptions. Static hashes
verify shared semantic information for each paired objective; actual delivered
parity and incremental execution remain unqualified. No B candidate was assembled.

**Neither paired interface began: actual A calls0, B calls0; completion, validity,
validation/assembly times are NOT_REACHED.** Calibration used complete-definition
generation but is not substituted for the distinct paired A objectives. There is
no observed ranking, incremental advantage or efficiency advantage from early
termination. Per-turn caps, deterministic assembly and prefix-cache history would
remain intrinsic comparison limitations even had the schedule completed.

## Token and timing measurements

[Measurements](r6_21/MEASUREMENTS.json) distinguish reported sums from missing data.

| Group | Calls | Reported input | Cached input (separate) | Reported output | Call wall(s) | Validation(s) |
| --- | --- | --- | --- | --- | --- | --- |
| Warmup + delivery |4 |4,586 |1,651 |47 |3.531346 | Authoring validation not applicable |
| Neutral authoring |3 |1,914* |919* |203* |5.491429 |0.005283 |
| All inference requests |7 |6,500* |2,570* |250* |9.022775 |0.005283 |

\*F3 has no final input/output/cached usage fields. These totals are **known sums
from six completed responses**, not complete seven-call token expenditure. F3's
969 preflight/logged input tokens are recorded separately, not substituted for
absent final API telemetry. The log's released slot total1,159 is not converted
into invented output-token usage. Aborted generated content is unavailable.

Six completed responses report6.306336s total runtime duration, including2.121924s
load,1.045357s prompt processing and3.059280s generation. Failed F3's2.698651s
measured call wall time is included in wall totals; its runtime durations are
missing. Whole bounded run29.547258s includes weight verification, server setup,
tokenization and cleanup. Eight tokenizer calls have separate measured times.
Publication elapsed time is separately recorded in the verification receipt.

F1/F2 input utilization is11.73%/11.63% of effective8,192 context; with2,048 output
reserve it is36.73%/36.63%. Delivery controls qualify at most34.80% input utilization.
No output hit its cap among completed calls. Validation time combines strict load,
schema, wrapper, expansion and case execution; separate phase times were not
instrumented and cannot be inferred. Final inventory/process memory snapshots do
not provide resource peaks; energy/billing are unavailable. Actual token counts
come only from local runtime/tokenizer evidence, never text-length estimates.

## Failure analysis and reliability gate

[Failure analysis](r6_21/FAILURE-ANALYSIS.json) binds the exact F3 request/body/log:

- Request SHA256 `13436f1a540d6659c32cc4ba898537a9e4699ac5b90f0375ba07c838e5d43616`.
- HTTP500 body: `{"error":"prediction aborted, token repeat limit reached"}`.
- SERVER.log line496: slot8,192 and task969 tokens; line499 names repeat-limit
  abort; line505 releases the slot with `truncated=0`.
- Loaded-model GET still responds after failure. No restart, retry, model/output
  repair, prompt adjustment or additional inference followed.

This identifies **the current runtime's repeat-guard abort mechanism**, while the
underlying generated repetition is unavailable. No evidence establishes OOM,
context exhaustion or a backend crash. It must not be asserted as the cause of
R6.19's historical500, whose original error body remains unavailable. Both historical
evidence sets remain unchanged.

[Reliability gate](r6_21/RELIABILITY.json):

| Requirement | Result |
| --- | --- |
| Demonstrably intact compact delivery | Pass for evaluated calls and three neutral delivery controls |
| Bounded requests complete reliably | **Fail:**6/7 current requests complete, F3 aborts |
| >=1 model-authored validated executable composition | Pass:1 definition,3 cases |
| Failed attempts/resource usage preserved | Pass within recorded coverage; failed final usage explicitly missing |

The conjunctive gate fails. A small successful subset cannot establish general
reliability, clear the original500 or justify a discovery restart.

## Recommended next experiment and stop

**Recommend a separately authorized, bounded neutral token-repeat abort diagnosis**,
with raw streaming output/chunk capture, timestamps, exact generated-token usage
where returned, backend process/exit evidence and fixed controls around JSON and
the explicit raw thinking prefix. Predeclare any varied format/sampling/budget
conditions; preserve all failures and use a stop rule. Do not silently disable a
guard or tune this frozen attempt from its outcomes. No download, installation,
training or semantic change is justified by these observations.

Only after bounded completion reliability is established should a separately
authorized intact-prompt A/B comparison be attempted; ordered composition and
nested reuse still need actual participant evidence. A new discovery pilot awaits
the reliability gate and separate owner authorization. This report commissions
none of these follow-ups.

## Publication integrity

[Publication identities](r6_21/PUBLICATION-IDENTITIES.json) and
[verification receipt](r6_21/VERIFICATION.json) verify protected/frozen/publication
bytes, request/prompt hashes, all JSON, new-text whitespace, relative links and
`git diff --check`. Deterministic F1/F2 validation and F2 exact execution envelopes
are rechecked without participant inference. The
[first posthoc accounting failure](r6_21/PUBLICATION-FAILURE-1.md) was a publisher
syntax error before execution; its correction did not modify the frozen runner or
inference evidence. No tracked files were modified.

Additive guidance: [overview](../../../docs/project-overview-r6.21.md),
[research log](../../../docs/research-log-r6.21.md),
[decision](../../../docs/decisions-r6.21.md).

**Stopped after R6.21 publication. Await owner authorization.**
