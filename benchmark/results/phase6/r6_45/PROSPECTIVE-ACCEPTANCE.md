# Prospective successor acceptance matrix — NOT RUN

This is a documentary freeze of requirement-supported expected behavior, not an
execution-ready new benchmark or a change to R6.44. Expected values derive from
[authority](REQUIREMENT-AUTHORITY.md). All rows are NOT_RUN. No candidate is submitted
or scored. Clarification rows have no frozen error or success expectation.

## Exact fixture notation

`R` is exactly:

```json
{"id":"00000000-0000-4000-8000-000000000001","created_at":"2040-01-01T00:00:00Z","label":" kiln ","phase":"cold","vent":"closed","load":"emergency"}
```

`R-open` differs only in vent=open, load=ordinary. `R-firing` differs from R only
in phase=firing. `R-bad` differs from R-firing only in load=ordinary, violating the
persisted invariant. `missing` denotes file absence, never JSON null. Set expressions
below define exact JSON values; no unspecified field defaults are permitted.
Concrete serialization/fixture byte hashes must be bound before a later execution;
this round freezes semantic expectations, not a runner or byte serialization.

For every error, preserve the input's exact file bytes; for every list, preserve
bytes/absence and return sorted whole records. Each operation must use a fresh
process in a future authorized verification. No success/rejection may migrate or
normalize the kiln store.

| ID | Category / exact value or request | Frozen expected behavior | Authority |
|---|---|---|---|
| K01 | Empty persisted object `{}`; list, ignite(id=R.id), set_gate(id=R.id, value omitted) | invalid_state for each; unchanged bytes | COMMON:3–13; CONTRACT:23,44 |
| K02 | Missing record field: `[R minus label]`; list | invalid_state | COMMON:5–12 |
| K03 | Empty record `[{}]`; list | invalid_state | Exact required fields, COMMON:5–12 |
| K04 | Valid current empty list `[]`; list | `{"ok":[]}`; no rewrite | COMMON:3–13 |
| K05 | Valid current `[R-open]`; list | `{"ok":[R-open]}` | COMMON:11–13; CONTRACT:7–13 |
| K06 | Valid old **same-schema** kiln `[R-firing]`; list, then cool(id=R.id) | List returns `[R-firing]` unchanged; cool returns R and stores `[R]` | Stage 2:6–10; CONTRACT:51–58, cool rule |
| K07 | Malformed old **same-schema** kiln `[R-bad]`; list | invalid_state; no historical repair | Stage 2:9–10; CONTRACT:53–55 |
| K08 | Unsupported-version object `{"schema_version":99,"records":[R]}`; list | invalid_state: object is outside kiln's list format; not migration_required | COMMON:3,12–13; CONTRACT:23 |
| K09 | Envelope missing required member `{"schema_version":1}`; list | invalid_state | JSON-list format; COMMON:3,12 |
| K10 | Matching-version envelope `{"schema_version":1,"records":[R]}`; list | invalid_state: tests list-only shape independently of version equality | COMMON:3,12–13 |
| K11 | Invalid field types: independently `[R with label=0]`, `[R with phase=null]`, `[R with vent=[]]`; list | invalid_state for each | COMMON:5–12; kiln enum domains |
| K12 | Invalid top-level values: independently `null`, `0`, `"store"`; list | invalid_state for each | COMMON:3,12 |
| K13 | Missing store; list | `{"ok":[]}`; absence preserved | COMMON:3–4; CONTRACT:6 |
| K14 | Multiple defects: `[R-bad]`; set_gate(id="missing",value="bogus") | invalid_state before not_found or invalid_input | CONTRACT:44–49 |
| K15 | Multiple defects: `[R-bad]`; ignite(id=R.id) | invalid_state before firing-state invalid_transition | CONTRACT:23,44 |
| K16 | Valid `[R-firing]`; set_gate(id="missing", value="bogus") | not_found before guards/input | CONTRACT:22,46 |
| K17 | Valid `[R-open with phase=firing]`; set_gate(id=R.id,value="closed") | gate_locked | CONTRACT:36–49; ordinary lock remains |
| K18 | Valid `[R-firing]`; set_gate(id=R.id,value="bogus") | invalid_input (emergency lock not applicable) | CONTRACT:36–49 |

K06/K07 cover predecessor-compatible stored data without claiming a historical
schema migration. The phrase “valid legacy state” must not silently create a new
kiln schema or migration endpoint. Rows below keep that distinction explicit.

## Versioned-migration controls requiring separate scope/clarification

| ID | Requested category | Authority-supported part | Unfrozen part / clarification |
|---|---|---|---|
| V01 | Genuinely valid legacy-schema state for kiln | Kiln authorizes no distinct legacy schema or migration. | NOT_APPLICABLE_TO_KILN; require owner-supplied old schema, version chain, historical values, operations and errors before constructing a fixture. |
| V02 | A separate declared version-2 application with a valid version-1 list | v0.2:79–85 supports normal-read migration_required and explicit migration using model-declared defaults/validation. | CONDITIONAL_ONLY; select and pin that application's model/fixtures independently. No new model or whole result frozen here. |
| V03 | Malformed recognized old schema plus stale version under normal read | Historical-state profile:43–46 supports malformed historical record rejection during explicit migration. | CLARIFICATION_REQUIRED: invalid_state versus migration_required normal-read precedence; do not infer it from migration-time checks. |
| V04 | Unsupported/future version plus invalid field types in a migration-enabled application | No cited clause authorizes converting a future version or inventing old values. | CLARIFICATION_REQUIRED: recognized-envelope rules and public unsupported-version/shape/type precedence. |

Any later successor verification should execute supported K rows and retain raw
outputs and before/after bytes. V rows must not be scored until their scope and
expectations are authorized. A focused migration-regression control can reuse an
existing exposed, explicitly versioned fixture under separate authorization; never
use P6-A04/P6-A05 as a qualification source.
