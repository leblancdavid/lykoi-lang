# Schema compatibility matrix

Route: OpenCode1.18.32, stdio MCP2025-11-25, `openai/gpt-6.1-sol`, high reasoning.
All server rows below were published in complete `tools/list` responses. Publishing
a response does not attest MCP conformance; the untyped root row is nonconforming
to the SDK tool-envelope requirement despite being a valid JSON Schema.

| Synthetic schema form | OpenCode MCP discovery | Actual selected-model invocation |
| --- | --- | --- |
| Simple object | Connected | Accepted; exact echo |
| Nested object | Connected | Accepted; exact echo |
| Required field | Connected | Valid accepted; missing field reaches bridge and rejects |
| Optional field | Connected | Both omitted and supplied accepted, no inserted default |
| Enumeration | Connected | Accepted; invalid member rejects in neutral controls |
| Root `oneOf`, no root type | Failed to get tools | NOT_REACHED |
| Root `oneOf` + `type: object` | Connected | Both alpha/beta branches accepted |
| Nested `oneOf` | Connected | Accepted; malformed branch rejects in controls |
| `oneOf` + const tag + discriminator annotation | Connected | Accepted; disjointness enforced by original oneOf/const |

The `discriminator` extension is not proven to have provider-side enforcement or
optimization. It is passed as an annotation; branch validation uses `oneOf` and
`const`. No general JSON Schema dialect certification is claimed.

Successful authoritative synthetic qualification:
`SYNTHETIC-LIVE-3` has 10 positive calls and 1 deliberately malformed call,
with byte-exact delivered prompt. The model receives and summarizes the rejection.
Earlier `SYNTHETIC-LIVE-2` also has 10/1 but its prompt contains argv escaping;
`SYNTHETIC-LIVE` has no calls and truncated delivery. All are preserved.

Client discovery structural validation, model/SDK invocation acceptance and bridge
argument validity are separate stages. Missing required arguments are demonstrably
not prevented by this live client/provider route; authoritative bridge validation
is essential. Upstream provider schema rendering/validation is not independently
visible. Machine-readable summary: [SCHEMA-MATRIX.json](SCHEMA-MATRIX.json).
