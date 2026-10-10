# R6.46 — Scoped persistence contract closure

**Final classification: `R6_46_PERSISTENCE_CONTRACT_CLOSED`.**

The complete declared nonmigrating version1 JSON-list contract passes **18/18
rows,25/25 observations**. Matching version1 envelopes are rejected as well as
empty/stale/future objects and scalar values. Valid lists keep their original
decoder, record validation and operation behavior. The exposed kiln persistence
defect is fully closed within this declaration and its authoritative `handle`
interface. No production semantic kernel change is required.

## 1. Authorization, preservation and freeze

The owner authorized a bounded successor of R6.45 covering list-format closure,
not merely error remapping. Initial git status was clean. The
[baseline](r6_46/BASELINE.json) verifies **5,192 protected SHA256 identities**:
5,059 inherited identities,116 R6.44 publication files and its two manifest/receipt
files,13 R6.45 publication files and its two manifest/receipt files. Both receipt
bindings pass.20 R6.44 frozen-input identities and9 R6.16 task identities also pass.
Preservation is repeated after execution and at publication.

R6.44 remains `R6_44_COMPARISON_INCONCLUSIVE`; R6.45 remains
`R6_45_INTEGRATION_DEFECT`. Their requirements, expectations, original sources,
blank-label baseline correction, rejected attempts, raw diagnostics, scoring
corrections and all R6.3–R6.45 protected history remain intact. This round does
not rescore R6.44. Kernel remains **26**, verified through unchanged R5.114
accounting and protected production implementation, not an independent recount.

[Contract](../../../experiments/scoped_persistence_r6_46/CONTRACT.md),
[source-based expectation check](r6_46/EXPECTATION-CHECK.json), concrete
[fixtures](r6_46/MATRIX.json) and their [freeze](r6_46/FREEZE.json) precede
implementation. Expectations independently follow original COMMON:3–21 and
R6.44 CONTRACT:6–14,23,33–58, not candidate output. This is candidate-output-
independent same-agent checking, not independent human review or blinded research.

## 2. Exact correction and implementation identities

The new [adapter](../../../experiments/scoped_persistence_r6_46/adapter.py) and
[explicit declaration](../../../experiments/scoped_persistence_r6_46/profile.json)
are application integration changes. Installation requires the named existing
state, integer schema_version1, JSON-list format, forbidden migrations and
invalid_state error. A conflicting state version or any model migration refuses
installation; absent declaration leaves the original decoder exactly unchanged.
No kiln-specific application name, field, command or benchmark value selects it.

At the existing decode boundary, the closure invokes the unchanged shared decoder
once. Only decoder-origin migration_required becomes invalid_state. All other
failures propagate unchanged. Independently, the original parsed payload must be
a list, so an otherwise decoder-accepted version1 envelope also fails invalid_state.
Valid lists pass to existing whole-store/invariant validation. The adapter does
no IO, second read, migration, normalization, defaults or mutation. Operation-level
migration_required remains unchanged.

The [successor generator](../../../experiments/scoped_persistence_r6_46/build.py)
regenerates the preserved R6.44 final intent through the unchanged production
generator, then appends profile installation for the exposed imported `handle`
interface. No generated behavior is hand-edited. The full lowered IR and original
generated prefix match exactly. [Implementation receipt](r6_46/IMPLEMENTATION.json):

| Artifact | SHA256 |
|---|---|
| Historical accepted starting executable | `ed48e8bdbba8503fcf6d2f51ef34f96b22845b2542712721b8fbec292e4602b7` |
| Immediate predecessor R6.44 final executable | `3ee6332840e9c433d91cd3c1fb4509e0c8aedeed35577b1d3294af28c7677dc4` |
| Unchanged final intent | `dc3b03a815c49c23e53c660a23b9e75e6564c2c7f54e9c7e21899dc217819726` |
| Corrected executable | `2e13cf43117032670c73e7fa0f39f3c78e28c1d1725d3b3f9570dd57b4299712` |
| Unchanged lowered IR | `05ed6e4bc15c058254e2026a54276eb1a9cfd95e95e512f38611a90e7b0fbc84` |

Detailed [contract-to-runtime mapping](r6_46/CONTRACT-TO-RUNTIME.md) locates the
profile boundary, precedence, validation, byte preservation and noninterference.

## 3. Frozen list-format acceptance

[Raw results](r6_46/MATRIX-RESULTS.json) retain request, expected/observed output,
return code, stdout/stderr, decoded state and exact before/after bytes.18 semantic
rows expand to25 observations because K01/K11/K12 and K06 have multiple operations.
All requests use a fresh subprocess and the unchanged JSON transport.

| Rows | Coverage | Observations | Result |
|---|---|---:|---|
| K01 | Empty object: list/ignite/set_gate with omitted value |3|PASS|
| K02–K03 | Missing label; empty record |2|PASS|
| K04–K05 | Empty list; valid ordinary open record |2|PASS|
| K06 | Old same-schema emergency firing record: list then cool |2|PASS|
| K07 | Malformed same-schema old record/invariant |1|PASS|
| K08–K10 | Unsupported version; missing envelope member; matching version1 envelope |3|PASS|
| K11 | label=0,phase=null,vent=[] |3|PASS|
| K12 | Top-level null,number,string |3|PASS|
| K13 | Missing store; empty result and absence preserved |1|PASS|
| K14–K15 | Invalid store wins over lookup/input/transition defects |2|PASS|
| K16–K18 | Valid store: missing ID,ordinary gate lock,emergency invalid input |3|PASS|

Every error/read preserves exact existing fixture bytes or absence. K06's cool
changes only phase and persists the expected valid list through the original
atomic writer. No distinct legacy kiln schema or migration was invented.

## 4. Regression protection and retained attempts

[Prospective kiln regression](r6_46/KILN-REGRESSION.json) passes **188/188** frozen
R6.44 modified observations. Output,error,return-code,persisted-state and exact
before/after-byte projections match the already published accepted predecessor
results. This is new successor regression execution, not historical rescoring.
It covers existing transitions, guards, whole-store invariants, create/list,
identity/field preservation, sorting, invalid unrelated records and error order.

**53 completed test methods pass**:

| Complete checks | Methods | Coverage |
|---|---:|---|
| Scoped adapter |6|Explicit selection,no-op,no migration scope,36 other-state differential comparisons,decoder-only remapping,one-call valid-list identity |
| Existing compiler |22|Validation,capability/effect authority,lifecycle,migrations,generation provenance |
| Existing application |9|Actual explicit legacy/version2 migrations,load invariants,lifecycle,persistence |
| Existing mutable values |12|Collection migration,unrelated profiles,typed mutation,persistence rollback |
| Existing baseline oracle |3|Lifecycle,migration,corruption,clock behavior |
| Direct existing runtime |1|Six authorization/atomic failure cases on an existing versioned application |

[Complete and partial command logs](r6_46/REGRESSION.json),
[direct-runtime log](r6_46/regression/direct-runtime-controls-v2.json) and
[adapter controls](../../../experiments/scoped_persistence_r6_46/test_adapter.py)
are preserved. Runtime cases reject forged actor,wrong context source,wrong role,
wrong owner and failed atomic replacement with exact bytes unchanged; the valid
authorized case succeeds and preserves expected history composition. No-declaration
installation retains its decoder and deterministic source exactly.

The first enclosing verification tool timed out after240s; completed matrix/replay
and four test logs were retained in [attempt1](r6_46/EXECUTION-ATTEMPT-1.json).
Resuming unfinished tests retained three180s timeouts in additional full workflow
suites (`test_predicates`, `test_historical_state`, `test_authorization_composition`).
Their partial logs contain completed positive tests and incomplete workflow work;
these suites are **not claimed as passes**. No assertion failure was observed in
those timeout logs. Direct scoped runtime preservation completes the relevant
authorization check without the unrelated end-to-end reconciliation workflow.

A separate [runtime-control launch](r6_46/regression/direct-runtime-controls.json)
failed before tests because the repository root was absent from PYTHONPATH.
The corrected invocation includes root+src and passes. Initial
[RESULT](r6_46/RESULT.json) and [RESULT-v2](r6_46/RESULT-v2.json) retain the provisional
regression-gap outcomes. [RESULT-v3](r6_46/RESULT-v3.json) is the final bounded
classification after completed scoped controls. No candidate,expectation or
production implementation changed during these verification adjustments.

## 5. AI-independent replay

[Matrix replay](r6_46/MATRIX-REPLAY.json) repeats **25/25**, and
[kiln replay](r6_46/KILN-REPLAY.json) repeats **188/188**. The
[replay receipt](r6_46/REPLAY.json) compares deterministic outputs,errors,return
codes,stdout/stderr,decoded persisted state,exact before/after bytes and executable
identity. Both projection hashes match exactly, excluding elapsed timing only.
Every operation is a fresh Python process; sequential K06 and regression sequences
share only their local store. AI calls during all execution/replay: **0**.
This qualifies deterministic local cooperating execution, not crash/concurrency or
distributed persistence. The correcting agent's authorship is not itself AI-free.

## 6. Remaining limits and next architecture proposal

The complete declared list-format defect is closed for the exposed application's
required interface. The adapter is explicitly attached in this successor; it is
not integrated into all production profiles or a proof of universal contract fidelity.
Shared decoder behavior and general migration_required meaning remain unchanged.
Full additional end-to-end workflow suites remain incomplete due to their logged
timeouts; the completed scoped controls and unchanged production identities support
the bounded nonregression claim. No broad full-suite qualification is claimed.

[Migration ambiguities](r6_46/MIGRATION-AMBIGUITIES.md) keep R6.45 V01–V04 unscored.
In particular, malformed old-schema normal-read precedence and unsupported/future
envelope recognition require separate source clarification. They do not weaken the
determined kiln list-format expectation or authorize global error remapping.

Recommended next architectural step: source-authoritative persistence shape,
version recognition,migration permission and decode-error precedence as explicit
validated integration facts carried through deterministic lowering. Resolve
migration-enabled ambiguity before implementing that broader representation.
No new semantic primitive or automatic next experiment is justified here.

## 7. Publication and stop

[Publication identities](r6_46/PUBLICATION-IDENTITIES.json) and
[verification receipt](r6_46/VERIFICATION.json) bind this report,implementation,
fixtures,raw matrix/regression/replay evidence and versioned
[boundary](../../../docs/project-overview-r6.46.md),
[observations](../../../docs/research-log-r6.46.md) and
[decision](../../../docs/decisions-r6.46.md). They verify all protected identities,
freeze and implementation bindings,unchanged production/kernel,deterministic
replays,source/JSON/link integrity,credential patterns,implementation scope and
`git diff --check`. All new-file whitespace is checked as well.

No production primitives,P6-A04 acceptance checks,P6-A05 content access,training,
historical rescoring or credentials are introduced. **Stopped after the bounded
correction and publication.** Further work requires explicit owner authorization.
