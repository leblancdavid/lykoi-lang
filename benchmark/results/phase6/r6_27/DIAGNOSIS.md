# Failure-stage diagnosis

## Established by actual controlled probes

OpenCode 1.18.32 initializes the stdio MCP server, receives `tools/list`, then
fails to publish the tool catalog when an `inputSchema` lacks root
`type: "object"`. This occurs before provider invocation. Synthetic object-only
`oneOf` fails; the same schema plus that single annotation connects. Exact frozen
Lykoi publication fails; the same four tools with only the annotation on
`apply_operation` connect. [Raw matrix](SCHEMA-MATRIX.json), `ORIGINAL/MCP.jsonl`,
`ORIGINAL/STATUS.txt`, `ANNOTATED/MCP.jsonl` and `ANNOTATED/STATUS.txt` preserve
the controlled exchanges. No semantic dispatcher is entered.

The defect is **missing MCP-required object-root metadata**, not a prohibition
on root `oneOf`: annotated root unions are both discovered and invoked live.
Required/optional fields, nested schemas and tool-name prefixes do not explain
the original discovery failure. No upstream provider SDK/model is invoked by
these model-free discovery commands, so this first failure is not attributed to
provider JSON Schema validation.

## Exception visibility and source evidence

[Public matching-version source identities](SOURCE/IDENTITIES.json) pin OpenCode
MCP `index.ts`, `catalog.ts`, package metadata and SDK1.29.0 types. The catalog's
`defs()` catches the list error and returns void; `create()` substitutes
`Failed to get tools`. The captured CLI stderr does not contain the original
exception. **The original R6.26/bundled OpenCode exception is not recovered.**

SDK1.29.0 `ToolSchema.inputSchema` requires `type: z.literal('object')` and
passes through other keys. Its `ListToolsResultSchema` validates every tool.
An already installed SDK1.27.1 reproduces the validation against the actual
captured responses: `ZodError`, issue `invalid_value`, path
`tools[1].inputSchema.type`, message `Invalid input: expected "object"` for
the exact Lykoi list; annotated list passes. [SDK reproduction](SDK-VALIDATION.json)
is explicitly a separate SDK version, not an intercepted bundled exception.
Public-tag source is supporting explanation; installed-binary/source build
equivalence is not independently attested. The controlled runtime delta establishes
the compatibility cause without assuming that equivalence.

The matching-version source also contains an AI-SDK conversion helper that sets
root properties/additionalProperties. We do not assume every provider route uses
that helper: the actual selected model successfully sends both root-union variants
without further schema adaptation. Exact upstream HTTP schemas are unavailable.
No unused helper is treated as evidence of a live provider failure.

## Registration, names, configuration and subsequent stages

The bridge advertises `tools` capability and complete ordered definitions. MCP
requests use original function names; OpenCode model events use `lykoi_` prefixes,
then the bridge receives the original names. All existing names are already safe
under OpenCode's alphanumeric/underscore/hyphen normalization; no collision or
renaming repair is needed. Matching raw requests, events and echoes establish this
for all four names, not every possible future name.

Configuration enables the local server and permits `lykoi_*`; inherited MCP
servers are explicitly disabled. Config paths/overrides are captured without
credential values. Fresh processes load experiment-local configuration; installed
user/project configuration is not edited. R6.25 normalization remains authoritative
and metadata is not forwarded into semantic arguments.

Separate neutral preparation defects were observed: Windows positional prompt
truncation/escaping and model refusals caused by original effect descriptions on
an inert server. [Preparation history](PREPARATION-NOTES.md) retains all attempts.
UTF-8 stdin plus exported-text comparison qualifies exact prompt delivery. An
honest inert-only prefix, with the complete original description retained, qualifies
neutral invocation. This prefix is publication metadata, not an argument or
semantic modification. Unannotated effect descriptions were discovered but not
invoked in the two neutral refusal sessions.
