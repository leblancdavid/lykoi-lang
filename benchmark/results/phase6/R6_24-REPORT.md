# R6.24 — Local AI typed-tool construction experiment

**Final classification: `R6_24_PROTOCOL_HALT`.**

The bounded run halted at its neutral native-tool interface control, before any
construction task was exposed to Qwen. The model selected the correct tool and
argument, but the frozen harness incorrectly rejected Ollama's native transport
metadata. **No model-authored program, functional result or comparative authoring
benefit was measured.** The failed harness, raw calls and task freeze are preserved.

## 1. Authorization and baseline

The owner authorized a bounded nonproduction local construction experiment, using
the existing Qwen3 8B model, unchanged R6.18 semantics and R6.23 adapter. Initial Git
status was clean. [Baseline](r6_24/BASELINE.json), recorded before tool implementation,
verifies **1,228 protected identities**: production and preserved history, including
R6.18–R6.23 artifacts, publication manifests and verification receipts. R6.18's seven
shared-guidance supersessions were already recorded by R6.23; those historical
manifest bytes and the later current guidance bytes remain preserved.

The production ledger remains **26 constructs**. Frozen implementation identities:

| Implementation | SHA256 |
| --- | --- |
| R6.10 VM | `bf5dbfb96d6d50124d109c35804c81e5a27bf4038b7f65b1a909ad4f0cc13fa3` |
| R6.18 wrapper | `e5e57901d4df32bcb2eed3b5bbd7ce6f19ee3145bbf71303d96e15b4e3d67fab` |
| R6.23 adapter | `1cc2efe486298a94d7119eed6c4a4d3a7eba7ddd99fd4f32b33892c07d963cc2` |

The coordinator read R6.18–R6.23 reports before task design. Tasks are synthetic,
feature-targeted and coordinator-authored; this is not independent replication,
unbiased sampling or held-out generalization. No earlier participant solution or
scored symbolic-discovery task was supplied to the local model.

## 2. Exact local inference identity and limits

[Inventory](r6_24/INVENTORY.json) retains API version, selected model, capabilities,
full model metadata, template, parameters and experiment-owned environment.
Baseline retains CLI version and freshly hashed local weight bytes.

| Setting | Value |
| --- | --- |
| Ollama | Existing **0.35.0**, CLI/API checked |
| Model | Existing **qwen3:8b**, Qwen3 8,190,735,360 parameters, GGUF/Q4_K_M |
| Model manifest digest | `500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41` |
| GGUF SHA256 | `a3de86cd1c132c822487ededd47a324c50491393e6565cd14bafa40d0b8e686f` |
| GGUF size | 5,225,374,496 bytes |
| Context | Metadata40,960; requested/effective **8,192**, confirmed by loaded model and slot logs |
| Sampling | temperature0, seed624, top_k20, top_p0.95, repeat_penalty1 |
| Interface | Native streaming `/api/chat`, `think:false`, no forced JSON format |
| Locality | Dedicated loopback11435, owned offline backend, cloud disabled, parallel1/one model |
| T budget |24 model calls and24 tool calls/task;384 output tokens/call;4,096 cumulative output/task |
| A/B budget | One4,096-output-token request each/task, zero repairs |
| Input | <=6,144 actual prompt tokens; cumulative<=60,000/task/track; input+cap+256<=8,192 |
| Time/calls |180s/task,60s socket/client call deadline,1,200s global,132 model calls maximum |
| Construction | T:3 definitions,4 inputs,8 steps/definition, one binary expression layer; unchanged expansion nesting4/64 nodes/64KiB |

Preflight tokenizes serialized messages/tools with a1,024-token template reserve;
this is a conservative proxy, not exact native-template tokenization. The submitted
controls' actual prompt counters match runtime log counts and show no truncation.
No task history approached a context limit because task interaction was never reached.
Bounds are client/cooperative controls rather than hard OS resource containment.

The frozen rule stops a task on a runtime abort and stops the run after a second
runtime abort; transport/identity/harness failures halt immediately. No budgets,
runtime guards, model weights or frozen code were changed after inference.
Prior R6.21 and R6.23 token-repeat abort evidence is hash-bound in the baseline and
failure analysis; zero current aborts do not clear those earlier failures.

## 3. Typed interface and scripted qualification

[Interface specification](r6_24/INTERFACE.md), [implementation](r6_24/tools.py),
[native tool schemas](r6_24/TOOLS.json) and [protocol](r6_24/PROTOCOL.md) were
[frozen](r6_24/FREEZE.json) before participant inference. The four tools are:

- `declare_input`: explicitly declare a named definition and typed signature.
- `apply_operation`: append a value/check/compose operation with exact dependencies.
- `define_result`: explicitly finalize the definition's result expression/type.
- `validate_candidate`: call the frozen adapter, wrapper validation and expansion.

Partial append checks use frozen adapter machinery; rejected mutations roll back.
No operation selection, dependency, order, type or result is silently repaired.
Final candidates use unchanged construction/sealing, R6.18 hygienic expansion and
R6.10 execution. Internal temporary result sentinels cannot complete a candidate.
There are no new execution meanings, arbitrary callbacks or host-language execution.

[Scripted qualification](r6_24/SCRIPTED-QUALIFICATION.json) passed before freeze:

- Four scripted calls construct a valid control program.
- Four frozen input cases execute successfully via the unchanged wrapper/VM.
- Six negative controls reject malformed envelope, unknown tool, malformed arguments,
  unknown reference, missing dependency and wrong type; rollback is checked.
- A schema-valid/executable but wrong program is distinguished from correctness.

This qualifies **the stripped-envelope dispatcher**, not native API integration or
model programming. The controls omitted the native `id` and `function.index` fields,
which proved decisive. The [preparation note](r6_24/PREPARATION-NOTE.md) preserves a
pre-freeze controls-import failure and its exact-path import correction; no model
inference preceded that correction and no historical file changed.

## 4. Frozen tasks and controls

[Task/acceptance manifest](r6_24/TASKS.json) freezes five objectives and26 cases per
track. [Exact prompts](r6_24/PROMPTS.json) contain compact requirements and shared
existing semantic rules. T/A/B order rotates by task; each uses its own context,
with T retaining only its own interaction history.

| Task | Requirement | Cases |
| --- | --- | ---: |
| U1 TwiceSum | Materialize x+y, then double that subtotal |6 |
| U2 Match | Store equality Bool then check it |4 |
| U3 Priority | Two ordered checks with EARLY/LATE failure precedence |5 |
| U4 Double/Combine | Same authored Double abstraction called twice; add results |4 |
| U5 Leaf/Middle/Shell | Nested authored composition and ordered outer/inner guards |7 |

Cases include negative/edge scalar inputs, invalid argument types, signed overflow,
UInt16BE range failure and competing failures. Acceptance requires exact requested
signatures, operation sequences and symbolic edges as well as functional envelopes.
Model-functional expectations are separate from tool feedback. These expectations
remain frozen but **unexecuted against participant programs**.

A generates complete definitions using the unchanged R6.23 complete schema and
mechanical sealing. B generates construct-1 compact packets. T uses incremental
native tools. The same total4,096-token output allowance does not equalize feedback
or inference-call opportunities: T has bounded model retries, A/B have none. T also
has narrower representation limits than the old A/B adapter schemas. These are
explicit interface-policy differences, not a controlled single-variable causal study.
Cache effects, fixed seed and synthetic task selection would further limit any
comparison even if task execution had occurred.

## 5. Actual interaction and terminal defect

Two neutral requests were submitted. Warmup returned `ready`; the tool control
returned HTTP200/normal stop with this **raw native tool call**:

```json
{"id":"call_ttew5ij6","function":{"index":0,"name":"echo","arguments":{"text":"local24"}}}
```

The selected name and arguments are correct. The frozen runner compared the full
tool object to a stripped `{"function":{"name":...,"arguments":...}}` object,
so metadata made its equality assertion fail. [Halt](r6_24/HALT.json) records
`AssertionError('native tool calibration failed')` at the pre-task control.

[Failure analysis](r6_24/FAILURE-ANALYSIS.json) binds the exact request and raw output.
A separate posthoc host-only shape control retains the actual native metadata while
using legal construction arguments: the frozen dispatcher also rejects that envelope
as `TOOL_SYNTAX`. Thus merely weakening the runner assertion would not qualify the
end-to-end interface. No metadata normalization, tool argument repair or inference
rerun was applied to this frozen attempt.

| Dimension | Observation |
| --- | --- |
| Neutral semantic tool selection | Correct name/argument **1/1** |
| Native runtime completion | **2/2** requests, HTTP200, normal stop |
| Frozen host envelope compatibility | Fails before dispatch; native metadata was omitted from controls |
| Task tool-call/argument validity | **NOT_REACHED**, denominator0 |
| Model semantic operation selection | **NOT_REACHED** |
| Complete model executable candidates | **0**, no task prompts submitted |
| Functional acceptance | **NOT_REACHED**, zero participant execution observations |
| Model runtime aborts | **0** in two neutral calls; prior aborts preserved |

[Raw requests, NDJSON streams and responses](r6_24/calls/),
[interaction summary](r6_24/INTERACTION-RESULTS.json),
[functional stage results](r6_24/FUNCTIONAL-RESULTS.json) and
[empty model representation inventory](r6_24/MODEL-REPRESENTATIONS.json) explicitly
retain the halted boundary. All15 scheduled task/track runs are NOT_REACHED.
There are no incomplete task candidates because construction never began.
Scripted success and neutral tool selection are not model-authored program success.

## 6. Tokens, timing and repair accounting

[Measurements](r6_24/MEASUREMENTS.json) derive counters from terminal Ollama responses.
Both submitted requests have complete token telemetry:

| Request | Input | Cached input subset | Output |
| --- | ---: | ---: | ---: |
| Neutral warmup |22 |0 |2 |
| Inert native-tool selection |146 |1 |21 |
| **Total submitted inference** | **168** | **1** | **23** |

Inference call wall time totals **2.616365s**; measured prompt evaluation0.186130s
and generation0.300207s are separate runtime counters. Scripted positive tool calls
took0.001827s in their original pre-freeze qualification, not model authoring time.
Whole bounded run took **14.374713s**, including local startup, inventory, endpoint
verification, token accounting and cleanup. Per-call inference wall and runtime
prompt/generation/load durations are retained in measurements. Actual task model
calls/tool calls, repair attempts and runtime aborts are all0. Task construction,
validation, expansion and execution timing are **null/NOT_REACHED**, not invented
zero costs. Scripted tool timings are separately labeled host costs. Tokenizer and
endpoint overhead is included in whole-run time but not separately metered here.
Billing, energy and peak resource usage were not measured. Publication costs are
outside the bounded run; publication issues no inference or tokenizer requests.

## 7. Analysis and recommended next experiment

This experiment does **not** establish a local model tool-use gap or a new runtime
reliability failure. Its first blocker is the host's incompatible tool envelope.
Ollama correctly completed the small native selection control. Whether the model
can select symbolic operations, manage exact dependencies, finalize reusable/nested
definitions or improve on complete/compact authoring remains untested here.

**Recommended smallest successor, requiring explicit authorization:** qualify a
metadata-aware native transport boundary that accepts/validates Ollama `id` and
`function.index`, preserves raw messages and arguments, and returns matching tool
identifiers in feedback. Use the same native envelope in scripted positive and
malformed-metadata controls, then a tiny declaration/value/result/validation loop
under a fresh freeze. Only after end-to-end qualification should a separately frozen
authoring comparison be commissioned. Do not resume/relabel these unexecuted tasks
as successfully tested or repair/re-evaluate the preserved R6.23 candidates.

## 8. Publication and stop

[Verification](r6_24/VERIFICATION.json) and
[publication identities](r6_24/PUBLICATION-IDENTITIES.json) check protected baselines,
frozen artifacts, requalified scripted controls, exact requests, raw stream
reassembly, intact native delivery, JSON, relative links, whitespace and
`git diff --check`. Only the experiment-owned server process tree was
[terminated](r6_24/CLEANUP.json).
The [publication note](r6_24/PUBLICATION-NOTE.md) preserves two posthoc verification
failures (byte serialization comparison and anticipated-output links); their fixes
changed no frozen experiment, inference or historical bytes.

Production compiler/lowerer/runtime, kernel26, R6.10 VM, R6.18 wrapper and R6.23
adapter remain unchanged. No full MCP server, new execution semantics, training,
fine-tuning, remote participant inference or downloads occurred. No P6-A04
acceptance check was run and P6-A05 was not accessed. Additive guidance is in the
[overview](../../../docs/project-overview-r6.24.md),
[research log](../../../docs/research-log-r6.24.md) and
[decision](../../../docs/decisions-r6.24.md).

**Stopped after R6.24 publication. Await explicit owner authorization.**
