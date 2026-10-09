# R6.25 — Tool integration repair and model-agnostic qualification

**Final classification: `R6_25_MODEL_AUTHORING_GAP`.**

The metadata-aware transport repair works for the tested Ollama envelopes, including
live multiple ordered calls. The one bounded Qwen construction attempt did not
produce an executable symbolic program. It exhausted three correction turns after
a malformed operation request; functional acceptance and executable replay remain
**NOT_REACHED**. This is an observed authoring gap in this model/interface/configuration,
not proof that the model cannot construct programs or a semantic expressiveness gap.

## Authorization, preservation and prospective selection

The owner authorized experiment-owned transport normalization, qualification and
one fresh construction attempt. Initial Git status was clean. Before implementation,
[baseline verification](r6_25/BASELINE.json) checked **1,266 protected identities**,
R6.24's publication manifest and receipt, its original raw envelope and its frozen
dispatcher's `TOOL_SYNTAX` rejection. R6.24 remains `R6_24_PROTOCOL_HALT`; nothing
was resumed, repaired or relabeled in that historical attempt.

The production ledger remains **26 constructs**. These frozen implementations match:

| Implementation | SHA256 |
| --- | --- |
| R6.10 VM | `bf5dbfb96d6d50124d109c35804c81e5a27bf4038b7f65b1a909ad4f0cc13fa3` |
| R6.18 wrapper | `e5e57901d4df32bcb2eed3b5bbd7ce6f19ee3145bbf71303d96e15b4e3d67fab` |
| R6.23 adapter | `1cc2efe486298a94d7119eed6c4a4d3a7eba7ddd99fd4f32b33892c07d963cc2` |

R6.24's semantic dispatcher is also imported read-only. New implementation and
evidence are confined to `r6_25/` and additive associated documentation. No production
compiler/lowerer/runtime, semantic operation, full MCP server, training or download
was introduced. No P6-A04 acceptance checks ran and P6-A05 was not accessed.

The coordinator read prior reports and designed the synthetic requirement. No
independent replication, unbiased task/model selection, held-out generalization,
comparative benefit or broad provider certification is claimed.

## Provider and model configuration

[Baseline inventory](r6_25/BASELINE.json) records other installed local models and
credential-presence booleans only. Existing **qwen3:8b** was selected prospectively
for its previously verified native-tool support and small pinned local footprint.
Other models exist; this is not a claim that Qwen was the only available model.
No other participant model was attempted and no outcome-driven switching occurred.

[Configuration](r6_25/MODEL-CONFIG.json) and [live inventory](r6_25/INVENTORY.json):

| Setting | Value |
| --- | --- |
| Provider/runtime | Local Ollama **0.35.0** |
| Model | **qwen3:8b**, 8,190,735,360 parameters, GGUF/Q4_K_M |
| Manifest digest | `500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41` |
| Weight SHA256 | `a3de86cd1c132c822487ededd47a324c50491393e6565cd14bafa40d0b8e686f` |
| Reasoning | `think:false` requested; returned fields/logs retained, stronger attestation unavailable |
| Sampling | temperature0, seed625, top_k20, top_p0.95, repeat_penalty1 |
| Tool interface | Native streaming `/api/chat`, no forced JSON format |
| Context | Requested/effective8,192; per-request runtime delivery checks pass |
| Local server | Owned loopback11435, cloud disabled, parallel1, one loaded model |

All six requests completed normally with HTTP200 and intact recorded delivery.
The owned server process tree was [terminated](r6_25/CLEANUP.json). Model/provider
configuration is isolated from the Lykoi core. No credentials are published.

## Transport boundary and qualification

[Tool envelope 1](r6_25/ENVELOPE-1.md) specifies provider/model/call identities,
function name, unchanged semantic arguments, quarantined provider metadata and
explicit turn/position ordering. [Normalization](r6_25/transport.py) accepts optional
Ollama `id` and `function.index`. It never forwards metadata to semantic construction
arguments, fills missing arguments, sorts invocations or repairs semantic choices.

Unknown finite JSON metadata is preserved inertly. Malformed known fields,
ambiguous envelope fields, duplicate identities, contradictory indices and
unauthorized tools reject. Semantic schemas, reference/type/dependency checks and
transactional rollback stay in the unchanged dispatcher and frozen adapter/wrapper.
Feedback retains the matching provider tool_call_id and tool_name.

[Tests](r6_25/test_transport.py) pass **17/17 methods**, including multiple assertions
per method: exact historical native shape; metadata and no-metadata positives;
ordered calls; unknown extensions; invalid names/types/missing/extra arguments;
duplicate identities within/across turns; malformed/ambiguous envelopes; invalid
indices; unauthorized requests; duplicate JSON keys; and unchanged semantic
dependency/type/reference rejection with rollback. A distinct synthetic
OpenAI-compatible profile qualifies JSON-string arguments and required id/type.
There was no live remote-provider call; unsupported profiles reject explicitly.

[Qualification](r6_25/QUALIFICATION.json) preceded the final freeze. A pre-exposure
code review found that applying integer-only JSON decoding globally would reject
legitimate inventory and timing floats. [Preparation note](r6_25/PREPARATION-NOTE.json)
and [earlier preparation freeze](r6_25/PREPARATION-FREEZE.json) preserve that finding.
Before any inference, decoding was scoped to preserve finite provider numbers while
still rejecting duplicate keys and enforcing strict semantic schemas. This was a
pre-exposure harness correction, not model or outcome repair. The final
[freeze](r6_25/FREEZE.json) is unchanged after exposure.

The [current live envelope](r6_25/CURRENT-ENVELOPE.json) contains
`id=call_viw7m2ew` and `function.index=0`; inert echo selection is correct and
normalizes successfully. In the task, **10/10 calls** normalized, with batch
sizes4,2,2,2 and indices consistent with invocation order.

## Frozen requirement and actual authoring

[Requirement and seven acceptance observations](r6_25/REQUIREMENT.json),
[prompt](r6_25/PROMPT.json), [tool schemas](r6_25/TOOLS.json) and
[protocol](r6_25/PROTOCOL.md) were frozen before model exposure.

The fresh task was `OffsetTotal(a:Int64,b:Int64)`: materialize their subtotal, then
increase that stored value by3 in a second value step, returning the second value.
It requires two typed inputs, multiple semantic operations and an explicit
stored-value dependency. Acceptance covers ordinary output9, zero output,
UInt16BE maximum65535, positive/negative encode-range failure, signed64 addition
overflow and rejection of Bool in an Int64 input. No completed solution or
acceptance fixture was supplied to the model.

Budget: at most16 model calls,24 semantic calls,384 output tokens/call,
4,096 cumulative output tokens,60,000 cumulative prompt tokens,180s task wall,
and **three corrective turns**. Four native tools expose declaration, operation
append, result finalization and candidate validation. No manual semantic repairs.

[Raw calls](r6_25/calls/) and [full interaction](r6_25/INTERACTION.json) retain:

1. First response declares the correct two-input definition successfully.
2. Its `apply_operation` arguments contain only dependencies and an operation
   array. They omit definition, alias, declared type and expression, and use an
   array where the operation selector must be the literal `value`. Strict argument
   validation rejects this call as `ARGUMENT_SCHEMA`.
3. Premature `define_result` references literal placeholder `$prior_alias` and
   attempts a result before any operation exists. The first deterministic blocker
   is `SHAPE`: at least one operation required. No alias repair occurs.
4. `validate_candidate` rejects the unfinalized definition as `INCOMPLETE`.
5. All three correction turns repeat only result/validation calls. No value step
   is authored. The run stops at `REPAIR_BUDGET`.

There are **9/10 schema-valid semantic argument objects**, but only **1/10 successful
construction mutations**. Schema validity does not establish valid references,
state preconditions or complete programming. The only accepted mutation is the
input declaration. [Partial representation inventory](r6_25/MODEL-REPRESENTATIONS.json)
preserves the unfinalized packet. Its result0 is the dispatcher's documented
internal temporary type-check sentinel, not a model-authored completed program.

The supplied operation schema uses `oneOf`; the evidence does not attest how fully
the provider's native tool renderer communicates that schema to this model. The
observed gap therefore belongs to the tested authoring interface/configuration,
not a causal attribution solely to model capacity. Transport acceptance alone
does not qualify schema usability or authoring competence.

## Functional execution and replay

**No executable symbolic artifact was constructed.** Final symbolic validation,
R6.18 expansion, R6.10 VM execution and all seven participant acceptance observations
are [NOT_REACHED](r6_25/FUNCTIONAL-RESULTS.json), with executed-case denominator0.
Program provenance/work and validation/expansion/execution times are unavailable.

[Executable replay status](r6_25/REPLAY-STATUS.json) is **NOT_REACHED** because its
successful-construction prerequisite was absent. No executable replay or further
model connection was attempted. The frozen harness contains a three-pass model-free
replay path for a successfully produced packet/artifact; that path was not invoked.

Publication separately replays the ten recorded construction-tool requests without
inference and verifies identical diagnostics, normalization, rollback and partial
packet after excluding wall timings. This is rejection/transcript determinism,
not executable-program success or functional acceptance.

## Measurements

[Measurements](r6_25/MEASUREMENTS.json) use actual terminal API counters and measured
client/tool durations. Cached inputs are a subset of input tokens.

| Dimension | Result |
| --- | ---: |
| Task transport acceptance |10/10 |
| Task authorized tool/name syntax |10/10 |
| Task argument-schema validity |9/10 |
| Task successful semantic construction calls |1/10 |
| Model calls |6 total:2 neutral +4 task |
| Tool calls |1 neutral +10 construction |
| Correction turns/manual repairs |3 /0 |
| Task input/output tokens |4,955 /313 |
| All submitted input/output tokens |5,120 /336 |
| Task/all cached input subset |3,458 /3,459 |
| Task/all inference client wall |5.142441s /7.713524s |
| Construction interval |14.386513s, includes final owned-server cleanup |
| Tool dispatch wall total |0.002917s, includes partial/schema validation |
| Whole bounded run |24.659719s |
| Provider/runtime failures |0 |
| Completed programs/executed acceptance observations |0 /0 |

Per-call input/output, cached tokens and runtime load/prompt/generation durations are
retained. Isolated semantic validation time, final expansion/execution timing, billing,
energy, peak resources and stronger reasoning attestation are unavailable, not inferred.
Publication costs are outside the run and issued no inference/tokenizer requests.

## Remaining blocker, next experiment and stop

The original Ollama metadata compatibility defect is repaired in the successor and
qualified against the observed native envelope. The remaining blocker is operation
schema use and recovery from the first rejected semantic call. No production change
or new execution meaning is warranted by these observations.

**Recommended next experiment, requiring separate authorization:** a neutral,
unscored schema-visibility/control qualification using a flat single-operation tool
schema instead of a `oneOf` wrapper, verifying all required keys and structured
diagnostic delivery with the same prospectively selected model. Only after that,
freeze a new tiny requirement for one new construction attempt. Preserve this run;
do not repair its packet, rerun this task or switch models to improve its outcome.

[Verification receipt](r6_25/VERIFICATION.json) and
[publication manifest](r6_25/PUBLICATION-IDENTITIES.json) check protected identities,
final freeze, regression requalification, exact request hashes, raw-stream
reassembly, intact delivery, matching feedback ids, offline transcript determinism,
JSON, relative links, whitespace and `git diff --check`. Associated evidence is
summarized in the additive [overview](../../../docs/project-overview-r6.25.md),
[research log](../../../docs/research-log-r6.25.md) and
[decision](../../../docs/decisions-r6.25.md).

**Stopped after transport qualification, one bounded construction attempt and
publication. Await explicit owner authorization before further work.**
