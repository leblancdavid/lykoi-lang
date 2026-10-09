# R6.28 — First capable-model semantic construction

**Final classification: `R6_28_SEMANTIC_CONSTRUCTION_SUPPORTED`.**

GPT-6.1 Sol constructed a complete executable symbolic program through the real
Lykoi semantic tools. **11/11 frozen acceptance observations passed**, and **33/33
observations across three AI-independent replay passes matched exactly**. This is
one bounded, unscored feasibility result, not a competitive or generalization result.

## Authorization and baseline

The owner authorized this single R6.28 attempt. Initial Git status was clean.
[Baseline](r6_28/BASELINE.json) verifies **1,495 protected identities**, the complete
R6.27 publication manifest and receipt, its `R6_27_TOOL_EXPOSURE_QUALIFIED` result,
and the identical qualified OpenCode executable. Production kernel remains **26**.
Production compiler/lowerer/runtime, R6.10 VM, R6.18 wrapper, R6.23 adapter,
R6.24 semantic dispatcher and R6.25 contracts/transport remain unchanged.

Historical classifications and evidence are preserved. No new execution semantics,
training/fine-tuning, P6-A04 acceptance or P6-A05 access occurred. Changes are confined
to this round's evidence/report and additive associated documentation. Credentials
were neither collected nor published; installed OpenCode configuration is unchanged.

## Frozen requirement and exposure

[Protocol](r6_28/PROTOCOL.md), [requirement](r6_28/REQUIREMENT.json),
[acceptance manifest](r6_28/ACCEPTANCE.json), [prompt](r6_28/PROMPT.json) and
[pre-inference freeze](r6_28/FREEZE.json) precede participant inference.

Target `TwiceRight(left:Int64,right:Int64)` stores `left + right`, then adds
`right` to that stored sum and returns the second value. Exactly two dependent,
ordered value operations; no guards or other operations. Existing signed64 overflow
and fixed UInt16BE encoding errors remain native. This is a fresh coordinator-authored,
capability-tailored synthetic requirement; no earlier completed solution was supplied
or reused. The requirement deliberately specifies the operations and intermediate
value, so this demonstrates strongly scaffolded construction rather than autonomous
algorithm selection.

[Exposure](r6_28/TOOL-EXPOSURE.json) retains the four original truthful semantic
descriptions and names: `declare_input`, `apply_operation`, `define_result`,
`validate_candidate`. Only the R6.27-qualified root `type: object` annotation is
added to the object-only `apply_operation` union. Original schemas remain the
argument validators, with no defaulting or semantic argument transformation.
OpenCode publishes the `lykoi_` prefix and delivers original tool names to MCP.

This endpoint instantiates the real unchanged `Session` and dispatches through
R6.25 normalization → R6.24 construction → R6.23 adapter → R6.18 validation/
expansion → R6.10 VM. It is not an echo endpoint. A [pre-inference backend control](r6_28/BACKEND-CONTROL.json)
observes a neutral declaration mutate actual construction state without constructing
the requirement solution. The actual live session confirms all four tool names,
real construction state, sealing and expansion to five VM nodes.

## Model authoring and artifact

The exact observed provider/model is **`openai/gpt-6.1-sol`**, OpenCode **1.18.32**,
requested `high` variant, maximum output4,096 per completion, maximum17 completion
steps. Effective reasoning is **unattested**; returned SDK reasoning tokens are0.
[Configuration](r6_28/OPENCODE-CONFIG.json) is experiment-local, loaded by a new
process, with non-Lykoi tools denied. UTF-8 stdin prompt delivery is verified by
the exact [exported user text](r6_28/LIVE/DELIVERY.json). Hidden context exclusion,
provider retries and upstream HTTP are unavailable.

The model used **5/12 semantic calls**, **0/4 correction turns**:

1. Declare `TwiceRight` with two Int64 inputs.
2. Append `sum = add($left,$right)`, dependencies `left,right`.
3. Append `result = add($sum,$right)`, dependencies `sum,right`.
4. Finalize result `$result:Int64`.
5. Validate `TwiceRight`; unchanged backend returns completed, expanded nodes5.

All5 argument objects are valid and all5 dispatches succeed. No coordinator repaired
semantic decisions. Exact model requests, feedback, session export, ordered MCP
exchange and diagnostics are in [LIVE](r6_28/LIVE/).

The [compact packet](r6_28/LIVE/SYMBOLIC-PACKET.json) and
[sealed artifact](r6_28/LIVE/ARTIFACT.json) are preserved:

| Identity | SHA256/content identity |
| --- | --- |
| Artifact file | `762d32c8d98883c9d82139e453484a8d3a00136f84c98da023134ace4aa0d322` |
| Canonical artifact | `7c1dcb2fca91abea048577f32232ca8a334cd9d0f7abe029c8e96ab0a2d386f6` |
| Typed definition | `8fb37edc2225819adbdac606deeea1eff8e4059669db6a89d240a675bda1678b` |

## Functional acceptance

[Functional evidence](r6_28/FUNCTIONAL.json) includes complete typed packages,
expanded plans, mapping, identities, result/error envelopes, provenance, logical
work and ordered entry traces. All11 expected observations pass:

| Inputs `(left,right)` | Frozen expectation | Result |
| --- | --- | --- |
| `(7,11)` | Int64 29, output `001d` | PASS |
| `(0,0)` | Int64 0, output `0000` | PASS |
| `(65535,0)` | Int64 65535, output `ffff` | PASS |
| `(1,32767)` | Int64 65535, output `ffff` | PASS |
| `(-2,1)` | Int64 0, output `0000` | PASS |
| `(0,32768)` | `ENCODE_RANGE`, encode stage | PASS |
| `(-1,0)` | `ENCODE_RANGE`, encode stage | PASS |
| `(Int64_MAX,1)` | `OVERFLOW`, structure stage, first addition | PASS |
| `(Int64_MAX-1,1)` | `OVERFLOW`, structure stage, second addition | PASS |
| `(true,1)` | Wrapper `TYPE` rejection | PASS |
| Missing `right` | Wrapper `SHAPE` rejection | PASS |

Every successful execution consumes0 bytes and uses16 VM logical work. Invalid typed
host arguments are rejected by the wrapper before VM execution, not represented as
VM runtime failures. Native error stage/node/path/offset/work are preserved in the
complete observations. Functional acceptance checks values, output bytes, consumption,
errors and required structure, rather than relying on schema validity.

## AI-independent replay

The author process terminated before offline evaluation. [Replay](r6_28/REPLAY.json)
reloads only the saved artifact for each of three passes; no model request occurs.
All33 records match the initial11 exactly: typed results, full error behavior,
provenance, logical work, ordered node-entry/cursor/work/depth traces, packages,
expanded plans and repeated-run identities. Timing is recorded separately and is
excluded from deterministic identities. Trace instrumentation delegates unchanged
VM behavior and checks equality with the uninstrumented public executor.

An additional [offline verification](r6_28/OFFLINE-CHECKS.json) independently checks
frozen expectations, all33 replay records and transcript lineage. Deterministic
reconstruction from the raw model tool arguments exactly matches the saved packet
and artifact; this lineage control is separate from saved-artifact execution replay.
The unchanged R6.25 transport suite passes **17/17 methods**, without inference.

## Measurements and authoring effort

[Measurements](r6_28/MEASUREMENTS.json) and [summary](r6_28/SUMMARY.json) retain exact
counters, message metadata and timing samples:

| Measurement | Observed |
| --- | --- |
| Authoring sessions | 1 |
| Model completion calls/steps | 6: five tool-call completions plus final stop |
| Semantic tool calls / valid arguments / successful dispatches | 5 / 5 / 5 |
| Construction failures / correction turns | 0 / 0 |
| SDK input / output / reasoning tokens | 5,789 / 215 / 0 |
| Cached-read tokens | 0 |
| Session wall, including startup/tool work | 19.001s |
| Summed assistant-message elapsed, not pure inference | 17.020s |
| Total deterministic tool dispatch time | 3.074ms |
| Final adapter construction / typed validation | 0.103ms / 0.158ms |
| Acceptance typed validation total, nine VM-eligible cases | 1.224ms |
| Acceptance expansion total, including wrapper validation | 1.392ms |
| Acceptance VM execution total, including VM validation | 0.303ms |
| Two invalid-input wrapper rejections total | 0.120ms |
| Runtime/provider/construction errors | 0 unexpected; four expected VM rejections |

SDK cost0 is not a billing receipt. Pure inference time, API billing, effective
reasoning configuration, hidden retries and raw provider requests are explicitly
unavailable. Timing is descriptive on one tiny run, not a speed comparison.

## Failure analysis, preservation and next experiment

[Failure analysis](r6_28/FAILURE-ANALYSIS.md): no authoring, integration or unexpected
execution failure was observed. Correction ability was not exercised. The selected
arithmetic branch works through actual native tool exposure; live `check`/`compose`,
larger programs, discovery, reuse, generalization and comparative efficiency remain
unmeasured. Requested high reasoning with reported0 reasoning tokens is not proof
of effective provider reasoning. Coordinator-selected synthetic scaffolding and
unattested hidden context limit inference to this bounded feasibility observation.

[Publication identities](r6_28/PUBLICATION-IDENTITIES.json) and
[verification receipt](r6_28/VERIFICATION.json) bind the full deliverables, verify all
protected identities and pre-inference freeze, check JSON/links/whitespace and
credentials, and pass `git diff --check`. Untracked new files also receive an explicit
whitespace check. Publication makes zero inference calls.

**Recommended next experiment, requiring separate authorization:** one newly frozen,
unscored program combining a Bool input, ordered check and a dependent arithmetic
result through this same real backend. Include false-guard/overflow conflict cases
to test model-authored ordering and native first-failure behavior, then saved-artifact
AI-free replay. Do not infer permission for that attempt or a competitive benchmark.

**Stopped after this single construction attempt and publication. Await explicit authorization.**
