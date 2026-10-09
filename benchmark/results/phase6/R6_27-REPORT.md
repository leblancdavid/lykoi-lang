# R6.27 — Native tool exposure compatibility qualification

**Final classification: `R6_27_TOOL_EXPOSURE_QUALIFIED`.**

OpenCode1.18.32 discovers the existing four Lykoi construction-tool schemas when
the object-only `apply_operation` union receives root `type: "object"`. Selected
`openai/gpt-6.1-sol` invokes all four names with neutral arguments and receives
their structured inert echoes. Qualification is scoped to this route/model and
echo-only endpoint; no symbolic program, semantic construction or scored task
execution occurred.

## Authorization and preservation

The owner authorized a bounded infrastructure compatibility investigation and
experiment-local repair. Initial Git status was clean. [Baseline](r6_27/BASELINE.json)
verifies **1,362 protected identities**, both complete R6.25/R6.26 publication
manifests and receipts, original schemas, transport, failure evidence and frozen
task/acceptance identities. Those identities remain exact at publication.

Production kernel remains **26 constructs**. Production implementation, R6.10 VM,
R6.18 wrapper, R6.23 adapter, R6.24/R6.25 semantic tool definitions and R6.25
provider-neutral transport are read-only and unchanged. R6.26 remains
`R6_26_PROVIDER_COMPATIBILITY_GAP`; this successor does not revise its first result.
R6.26 scored tasks are not read for participant prompts, exposed or executed.
No P6-A04 acceptance, P6-A05 access, model download, training or fine-tuning occurs.
No credentials are collected/published and no dependency is installed. Public
matching-version source text is captured for diagnosis, not installed as runtime.

Changes are confined to `r6_27/`, this report and additive associated documentation.
The [protocol](r6_27/PROTOCOL.md), successive pre-inference freezes and
[preparation notes](r6_27/PREPARATION-NOTES.md) distinguish neutral repair attempts.
The coordinator knows historical findings and selects the same explicit model
identity as itself; no independent replication or unbiased provider selection claim.

## Exact failure stage and cause

[Diagnosis](r6_27/DIAGNOSIS.md) separates controlled runtime observations from
source explanation and exception reproduction:

1. Original server registration and initialization succeed, and a complete
   `tools/list` response is recorded. Discovery fails before any provider call.
2. Synthetic object-only root `oneOf` without root type reproduces `Failed to get tools`.
3. Adding only `type: object` makes that same synthetic schema connect. The exact
   four Lykoi tools show the same original/annotated controlled result.
4. Matching-version OpenCode source catches list errors and substitutes the generic
   diagnostic. Its pinned MCP SDK1.29.0 requires root `type: object` in inputSchema.
5. Separate already installed SDK1.27.1 validates the captured original list with
   `ZodError`, `tools[1].inputSchema.type`, `Invalid input: expected "object"`.
   The annotated list passes. This is reproduction, **not recovery of the original
   bundled R6.26 exception**, which remains inaccessible.

The established compatibility cause is the missing MCP-required object-root
annotation, **not root `oneOf` itself**. No tool-name, argument-defaulting,
configuration or upstream provider SDK cause is inferred from the generic message.
The root union is successfully invoked after annotation.

## Supported schema forms

The [matrix](r6_27/SCHEMA-MATRIX.md) and [raw summary](r6_27/SCHEMA-MATRIX.json)
cover simple/nested objects, required/optional fields, enumerations, root/nested
`oneOf` and a const-tag union with discriminator annotation. Eight object-root
forms connect; the one root union without type fails. Actual synthetic model
calls accept all eight successful forms, including both root-union alternatives
and both optional-field presence states. Discriminator-specific provider behavior
is unproven; `oneOf`/`const` and the bridge enforce validity.

Server publication is not client acceptance. Client discovery is not upstream
provider enforcement. One live deliberately missing required field reaches the
bridge and rejects; no provider-side rejection guarantee is claimed.

## Smallest compatibility adapter and preserved contracts

[Adapter](r6_27/adapter.py) deep-copies publication schemas. Object-root schemas
are unchanged. A root union is annotated only if its sole key is nonempty `oneOf`
and every branch explicitly has `type: object`; all other conversions reject.
No flattening or invented arguments are introduced.

**Acceptance-set argument:** every instance satisfying any original branch is
already an object. Conjoining root object type therefore removes no original
accepted instance and admits none. Every original branch, required field,
additional-property restriction, bound and nested expression remains intact.
Original frozen schemas remain the authoritative per-call validator.

[Schema publication](r6_27/SCHEMA-PUBLICATION.json) records original, annotated and
neutral-exposure definitions. Names and order are unchanged. Provider metadata
stays in unchanged R6.25 normalization; it never becomes semantic arguments.
An honest inert-only description prefix is used in the final neutral session,
with full original description retained after it. This explains actual echo-only
sandbox behavior and does not change a semantic contract or frozen definition.

## End-to-end neutral and exact-schema results

| Qualified stage | Result |
| --- | --- |
| Synthetic OpenCode discovery | All eight object-root forms connected |
| Authoritative synthetic model session | 10/10 positive calls; 1/1 deliberately malformed call rejected |
| Arguments delivered to bridge | Exact request objects and ordered MCP calls recorded |
| Responses delivered back to model | Exact echoed values and rejection summarized in model response |
| Exact Lykoi schema discovery | All four tools connected with single root annotation |
| Exact-schema inert model invocation | 4/4 tools in original order, correct neutral arguments |
| Actual stdio bridge controls | 6/6 valid, 36/36 invalid expectations matched |
| Neutral unit suite | 6/6 methods pass |
| Frozen provider-neutral transport regression | 17/17 methods pass, no inference |
| Semantic construction / programs / scored executions | 0 / 0 / 0 |

The exact-schema live session tests one `value` operation. Direct stdio controls
also test `check` and `compose`, missing fields, unauthorized names, extra provider
metadata, mixed variants, unknown operation tags and duplicate dependencies. Those
two operation branches are not claimed to have been model-authored live.
Schema validation does not test semantic reference/dependency meaning; unchanged
transport regression preserves existing semantic rejection/rollback evidence.

Raw evidence: `SYNTHETIC-LIVE-3/` and `EXACT-LIVE-3/` retain requests, complete MCP
exchange, OpenCode events, stderr, status and exact exported-user-text checks.
StructuredContent and JSON text content match. OpenCode exposes names with the
`lykoi_` prefix and sends original names to MCP; no identity collision occurs.
The [bridge controls](r6_27/BRIDGE-CONTROLS/RESULT.json) preserve separate actual
stdio positive/negative exchanges. No semantic Session is instantiated by the bridge.

## Retained preparation failures and telemetry

All **six** neutral model sessions are retained, including the first truncated
multiline CLI prompt, a successful synthetic run with argv escaping, the verified
stdin synthetic run, two exact-description model refusals and final inert-description
success. The refused calls are not relabeled as schema failures or successful
invocations. A local exact-delivery assertion also halted one planned invocation
before inference. Final qualification uses verified UTF-8 stdin delivery and
honest endpoint descriptions. No further model attempt follows final qualification.

[Measurements](r6_27/MEASUREMENTS.json) retain every session's SDK tokens, cost and
client wall. Final synthetic session: **12 completion steps**, 10,854 input,
602 output, 0 reasoning, cached-read1,152, wall45.413s. Final exact-schema session:
**5 completion steps**, 4,154 input, 262 output, 0 reasoning, cached-read1,024,
wall22.823s. SDK input counters are retained separately from cache and total fields.
SDK cost0 is not an API billing receipt. Hidden retries, raw upstream HTTP, effective
reasoning attestation and hidden-context exclusion remain unavailable. Wall includes
process initialization; no model speed/authoring-efficiency comparison is made.

## Publication, remaining limits and next step

[Publication identities](r6_27/PUBLICATION-IDENTITIES.json) and
[verification receipt](r6_27/VERIFICATION.json) bind report, evidence, implementation
and additive documentation; verify protected identities, final pre-inference freeze,
JSON/links/whitespace, tests, original argument validation and `git diff --check`.
Publication issues no model requests. The installed configuration is unchanged;
each qualification process loads an experiment-local override.

The tested neutral exposure route is qualified. Broader provider certification,
unprompted schema usability, genuine semantic authoring, actual dispatcher effects
through this endpoint and scored construction remain **unmeasured**. Two unchanged
effect-description neutral sessions refused invocation; the qualified echo-only
session uses explicit inert-description metadata. That distinction must accompany
any claim that the model can invoke Lykoi tools. The original bundled exception and
exact upstream provider schemas remain unavailable.

**Recommended next experiment, requiring explicit authorization:** freeze a new
tiny unscored semantic construction attempt through this object-root annotation
and stdin-qualified transport, with actual frozen dispatcher and truthful semantic
effect descriptions, then verify one complete candidate and malformed semantic
rejection. Do not resume/relabel R6.26 or expose its scored tasks as a consequence
of this qualification. A second provider can later be qualified with the same
neutral controls before any provider-neutral certification claim.

**Stopped after neutral qualification and publication. Await explicit authorization.**
