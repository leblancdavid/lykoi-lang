# Deterministic context contract

`generate(registry, requirement_identity, objective_text, caller_bindings,
constraints_text)` reads authoritative R6.32 state and retrieves every transitive
dependency of both required callers by exact pin and generation token. Each complete
definition retains parameters, result type, dependency map, steps, ordered checks,
result expression and immutable identity. Separate signature/dependency indexes
are redundant lookup aids, not substituted meanings. CallerA/CallerB keys are a
bounded experiment contract, not a new registry or language operation.

Requirement identity, objective and constraints are host-supplied exact frozen task
data: the registry does not itself store requirements. The runner binds requirement
to its canonical JSON SHA256 and copies all behavioral constraints verbatim. It
does not infer semantics or choose which constraints to discard. Current root
validation is recomputed deterministically by unchanged expansion; this is not a
new persisted historical validation event. Lifecycle successors and migrations
are copied verbatim. Definitions outside active closure have exact retrieval pins.
No timestamps, timing counters, model output or LLM summary enter the snapshot.

Identity is SHA256 of unchanged R6.18 canonical JSON of the entire snapshot body.
`verify` checks the identity and regenerates the expected whole snapshot against
authoritative registry state and separately supplied frozen facts. Re-sealing an
omission does not bypass equality. Stale generation, missing caller/dependency,
altered objective/constraint, modified pins or absent validation fields reject.
Fresh-session continuation verification occurs before sending snapshot context.

`lykoi_detail` is the same read-only facade for both tracks. One exact pin and one
enumerated kind return definition closure, dependency graph, deterministic current
validation, lifecycle history, or exact identity/generation. It uses existing
R6.32 retrieval/probe/dependents and R6.18 expansion. Parameterized validation uses
the existing admission probe and is not executable-root acceptance. Scope is at
most the bounded task registry (five admitted definitions); no arbitrary file,
network, tool-log or other-track read. Retrieval writes ordinary telemetry only,
never symbolic state. Full MCP results and local response estimates are preserved.

Snapshot tests use R6.37 saved artifacts only as unscored infrastructure fixtures;
scored R6.38 definitions are newly authored. Supplemental post-authoring controls
verify migration records, predecessor retrieval, read-only state, restart and every
actual pre-modification snapshot. These supplements do not change scored oracles.
