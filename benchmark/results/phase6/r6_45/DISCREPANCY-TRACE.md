# Malformed-store discrepancy trace

## Input and preserved observations

The persisted file contains exactly UTF-8 `{}`, hex `7b7d`; it exists. It is not an
empty list, absent storage, invalid JSON syntax or an empty record inside a list.

[R6.44 A diagnostic](../r6_44/DIAGNOSTIC-A.json) and
[B diagnostic](../r6_44/DIAGNOSTIC-B.json) each retain six observations: list,
set_gate and ignite, each on baseline and modified executables. A returns
`invalid_state` in all six; B returns `migration_required` in all six. Every before/
after hex equals `7b7d`; bytes are unchanged. These are existing unscored R6.44 runs.
R6.45 performs zero application runs and does not enlarge historical denominators.

## Production-backed path (static reconstruction)

1. [R6.16 generator](../../../../experiments/value_added_r6_16/generate.py):29–55
   lowers storage with `version=1` and `evolution=[]`, then composes typed mutations
   and invariants. :75–83 uses production `generate_mutable`, appending C_WRAPPER.
2. [Scalar lowering](../../../../src/lykoi_pipeline/scalar_profile.py):171–185
   declares migration_required only for versions above 1; :179–180 still attaches
   `schema_version:1` to the kiln state.
3. Generated [baseline B](../r6_44/build/baseline-accepted/B/application.py):
   734–746 dispatches list to execute and mutations to execute_mutation. Both reach
   the shared `read_state` (production execute at runtime_template:204–207;
   mutable_runtime:95–103). There are no actor-context requirements in this kiln IR.
4. [Production runtime template](../../../../src/air_compiler/runtime_template.py):
   103–117 opens the file, successfully parses JSON and calls decode_state. Parsing
   produces an empty Python dict; decoding, not JSON parsing, is the rejection site.
5. `decode_state`:91–100 has this ordering:

   ```python
   if "schema_version" not in state:
       return payload
   if state["schema_version"] == 1 and isinstance(payload, list):
       return payload
   if not isinstance(payload, dict) or payload.get("schema_version") != state["schema_version"]:
       raise Failure("migration_required")
   if set(payload) != {"schema_version", "records"}:
       raise Failure("invalid_state")
   return payload.get("records")
   ```

   `{}` is not a list; `.get('schema_version')` is None, which differs from 1.
   The version-mismatch branch raises migration_required **before** checking the
   envelope's keys or validating the record list. No migration is selected, no
   eligibility/chain is consulted, and migrate is never called.
6. Failure's constructor (generated :20–22) maps declared error IDs if present,
   otherwise retains the supplied code. This raw code is not declared in the
   version-1 scalar behaviors. read_state catches JSON/Unicode/OSError, not Failure;
   its valid_state call at :118 is unreachable for this input.
7. C_WRAPPER `except Failure` emits `{'error': e.code}` without translation.
   Transport serializes that returned object. It does not invent migration_required.
   Lookup, policy guards, record invariants and writing are never reached.

**Origin:** shared production backend decoding/version discrimination. **Exposure:**
the nonmigrating application integration passes through the generic code despite its
list-only invalid-state contract. This is not a migration-selection result, record
validator result, or transport-generated error.

## Predecessor/successor identity

Static AST fingerprints were computed with Python standard-library ast parsing,
`ast.dump(function, include_attributes=False)` and SHA256 of UTF-8 dump. This does
not import, compile to executable bytecode or run any target code.

| Function | Production template / accepted baseline B / submitted final B |
|---|---|
| decode_state | `a3cf3c6afcb50c1964f300135af500c68d56fc4028621ed389cf37ec49a98078` in all three |
| read_state | `0e5a4289a3f1e323badae52eeed45e79ea0472138fedee94901083474453b72d` in all three |

Generated baseline and successor function sites are :94–119. Their loader has not
changed; the R6.44 two-guard modification cannot account for this discrepancy.
Original historical intent identity is recorded in STARTING-APPLICATION as
`d1ffeef91ed6c70148ebe029b70d73c56b89cd3530ebcba47e519aaa3b01e0a5`.

## Python path

[Accepted baseline A](../r6_44/build/baseline-accepted/A/application.py):57–77
parses the same file, then rejects a non-list at :72–73 with ValueError. handle
:96–101 maps that to invalid_state before dispatch or lookup. Its R6.44 baseline
blank-label correction occurs later, unrelated to reload. Existing diagnostics
confirm the same result in predecessor and successor. Python is corroborating
evidence; the textual contract supplies authority.

## Broader static implications (not new behavioral observations)

The same branch predicts migration_required for null, scalars and objects with
missing/wrong version tags. Conversely a well-shaped version-1 envelope can pass
decode_state even though kiln's contract says a JSON list. A matching version tag
with missing records reaches invalid_state. Thus a blanket code remap fixes the
reported error but does not by itself enforce the complete list-only format.
These predictions have not been executed in R6.45; they motivate prospective
controls, not additional demonstrated failures or historical scoring changes.
