# R5.49 — Dependency provenance and complete execution-capsule qualification

## Disposition

**`R5_49_DEPENDENCY_CLOSURE_GAP`**.

The first blocking qualification gate is **DEPENDENCY_CLOSURE_INCOMPLETE**.
Resolved repository/deployment provenance is generically corrected and fresh
diagnostics pass, but material native descendants are not transitively bound.
Effective production context/Git closure and exclusive ownership also remain
unqualified. A fresh synthetic ABA counterexample positively demonstrates the
existing check-then-observe bridge's ownership limitation.

**No qualified ExecutionCapsuleV2, production certificate, or exposure authority
was issued.** The complete production lifecycle was not reached. The 78 fresh
bounded receipts are diagnostic-only and **not reusable for production**. A PASS
for a counterexample means the gap was reproduced, not that ownership succeeded.
This is a stopped gap investigation, not a repaired R5.48 run.

## Inherited boundary and preservation

R5.48 remains permanently `R5_48_PROTOCOL_HALT`: 71 of 74 planned receipts,
70 PASS before quarantine, one failed inventory; all remain quarantined and
non-reusable. No R5.48 receipt satisfied any R5.49 stage. Historical diagnostic
code was independently rerun where identified below; historical receipt contents
were used only for preservation checks. R5.46 evidence is also unchanged.

The authoritative R5.47 infrastructure successor remains **1,065/1,065 members**:

`31339cb73996c9ee728656558477436d9a5ba1cfbd0272c771720e6a1f6bf084`

Historical 678/678 and prospective 695/695 locks pass. R5.43's preserved historical
manifest has the known 730/731 live matches, with only the reconciled `.gitignore`
difference. No new infrastructure lock was issued. Frozen-authority hashes pass;
the frozen oracle was not executed. Core semantic count stays **30**.

## R5.48 failure class and generic correction — A–D

The failed direct-import screen subtracted stdlib and two recognized package names
from an AST import-root set. Standalone deployment names were therefore counted
as external without resolving their implementations. Deployment copying can rename
a file, so even a filename search is insufficient.

New `benchmark/evaluation/dependency_provenance_r5_49.py` resolves module
specifications/loaders and implementation locations against an explicit
content-bound repository-member set. It does not exempt the seven historical names.
For deployment copies, the fresh acoustic fixture maps copied artifact bytes back
to bound source members and checks the actual imported module's resolved location.
Changed copy bytes reject attribution. Merely being under the repository directory
does not make an unbound file repository-owned.

### Provenance model

| Category | Definition |
| --- | --- |
| REPOSITORY_OWNED | Resolved implementation is an explicitly content-bound repository member, or a verified byte-identical deployment copy of one. |
| LANGUAGE_RUNTIME | Repository-owned implementation designated as Lykoi validation/lowering/runtime infrastructure. This is a role refinement, not a claim that all repository files are language runtime. |
| STANDARD_RUNTIME | Resolved implementation belongs to this interpreter's standard-runtime locations, excluding package-installation sites; built-in/frozen code requires its actual built-in/frozen loader. |
| THIRD_PARTY | External implementation attributed to distribution metadata by matching its installed-file location and current bytes. External editable sources need explicit source attribution; a `.dist-info` pointer alone does not establish their ownership. |
| NATIVE_EXTERNAL | Resolved external executable/library with separate implementation bytes. Its descendants still need closure. |
| DECLARED_PROGRAM_DEPENDENCY | Explicit program input or capability; a usage role orthogonal to where its implementation comes from. |
| DEVELOPMENT_AUTHORING | Author/provider/editor state unused by the bounded operation. Exclusion follows the operation boundary, not the mere name of a variable. |
| OPTIONAL_TOOLING | Tool unused by core semantics; it can nevertheless be material to an evaluator that invokes it. |
| UNKNOWN | Implementation resolution or safe attribution is unavailable. Material UNKNOWN fails closed. |

Provenance, materiality, and dependency role are distinct axes. An AI library
explicitly invoked by a future program would be a declared program dependency
with its own implementation provenance, rather than an authoring exclusion.

Fresh tests cover package paths, nested helpers, standalone deployment helpers,
generated repository modules, namespace membership, arbitrary import names,
verified renamed copies, genuine installed-file attribution using discoverable
distribution metadata, external editable source, installed-site exclusion,
unbound files inside a repository, custom loaders, and external executable bytes.
An unattributed editable source is UNKNOWN and rejected, rather than relabeled
local. The installed-package fixture is independently constructed with normal
`.dist-info`/RECORD metadata; no third-party package was added to Lykoi.

The fresh non-B02 deployment resolves **eight actual imported helpers**:

| Imported implementation | Bound repository source |
| --- | --- |
| input_binding_r5_32 | benchmark/semantic/input_binding_r5_32.py |
| launch_runtime_r5_36 | benchmark/semantic/launch_runtime_r5_36.py |
| optional_support_r5_41 | benchmark/semantic/optional_support_r5_41.py |
| refined_runtime_r5_28 | benchmark/semantic/refined_runtime_r5_28.py |
| state_runtime_r5_39 | benchmark/semantic/state_runtime_r5_41.py |
| transport_helpers_r5_41 | benchmark/semantic/transport_runtime_r5_35.py |
| transport_runtime_r5_34 | benchmark/semantic/transport_runtime_r5_34.py |
| transport_runtime_r5_35 | benchmark/semantic/transport_runtime_r5_41.py |

The mapping is reproduced from artifact/source content, not encoded as exceptions
in the resolver. Generated artifacts are constructed only in disposable fixtures;
the repository's `generated/` files were not edited.

## Dependency graph, native descendants and standard boundary — E–G

The implemented graph checker walks supplied transitive edges, supports cycles,
requires nodes and edge declarations for every reached component, and rejects
UNKNOWN, missing descendants, and unresolved native/dynamic descendants. It does
**not** infer complete edges from a successful direct-import inventory.

The fresh process observation has no UNKNOWN among its resolved module rows, but
its reachability list is explicitly **not an exhaustive dependency graph**:

```text
validate / deterministic lower / read-only list probe
  -> Lykoi parser, validator, generator and semantic rules
  -> resolved Python standard and built-in/frozen implementations
  -> material interpreter image and hashing implementation
     -> python314.dll / VCRUNTIME140.dll / Windows runtime services
     -> _hashlib -> libcrypto-3.dll -> unresolved descendants
qualification inventory / recorder
  -> its own resolved Python implementations and native images
qualification Git inspections
  -> Git executable -> not-yet-qualified native/helper/config closure
```

Fresh PE inspection records direct native import names without executing the
images. Observed extension images include `_bz2`, `_hashlib`, `_lzma`, `_uuid`,
and `_zstd`, plus the Python executable. Their import tables include
`python314.dll`, `VCRUNTIME140.dll`, `KERNEL32.dll`, CRT API-set names,
`RPCRT4.dll`, and, for `_hashlib`, **`libcrypto-3.dll`**. These are direct import
names, not proof of the loader's selected descendant implementation bytes.
Hashing the executable and `.pyd` files leaves this material state unbound.

API-set resolution, forwarded exports, transitive loader search, runtime-loaded
libraries, OS service dependencies and state ownership are not established by
this inspector. No arbitrary all-OS-library fingerprint was substituted for that
missing per-computation argument. Imports used only by inventory infrastructure
are not automatically declared material to every Lykoi program.

Built-in/frozen implementation identity is **DERIVED from a complete interpreter
image identity**, including its implementing DLLs, not merely `python.exe` or a
version string. Ordinary stdlib implementation files can vary independently of
that executable and are separately observed here. Frozen `__file__` paths are
not treated as executed source authority. Namespace locations require separately
bound executed descendants. Source-loader origin establishes provenance, but
does not alone prove which cached code was executed; cache/startup/late-import
closure remains open. There is no claim of a stronger qualified runtime identity
that would justify dropping these separate observations.

## AI independence and provider references — H–J, M

The R5.48 AI Independence Principle remains in force: **Lykoi is an AI-native
programming language, not an AI runtime**. Its meaning, validation, lowering,
compilation and execution do not gain AI-provider dependencies from the authoring
worker. Provider/model/OpenCode state is outside the tested core input boundary.

Fresh R5.49 subprocess tests independently reproduce:

1. Valid source validation and invalid language-version rejection without credentials.
2. Deterministic lowering without credentials.
3. Applicable generated read-only execution without credentials.
4. Site-disabled operation with an empty executable PATH; no OpenCode invocation.
5. Core operation with Python network/process audit events denied.
6. Equal core result with an unreachable provider endpoint.
7. Equal core result with changed synthetic AI credentials.
8. Equal core result with changed development-model selection.
9. Exclusion of credential values/presence/fingerprints from effective core controls.
10. Equal results under changed author/editor/OpenCode/unrelated environment state.

The separately fresh 52-test historical-prototype replay also checks full
closed-fixture identity stability under credential/model/editor/OpenCode mutation.
These are bounded independent observations, not reusable R5.48 receipts or proof
of a complete production capsule. Audit hooks are not a native network sandbox.
The direct core-import inspection finds no required provider-inference library.
Documentation, authoring configuration, and optional evaluation tooling are not
automatically core execution coupling; no required core AI inference was found
in the inspected/tested paths. No universal all-program claim is made.

No actual AI credential values were read or published. Child environments are
sanitized; mutations use explicitly synthetic values. Capsule/inventory evidence
contains neither raw environment dumps nor AI credential fingerprints. Every
JSON evidence publication uses the unchanged R5.47 secret-safe guard and exclusive
writer. Subprocess output is withheld from persisted diagnostics. Secret and
publication regressions pass; external credential rotation remains
`ROTATION_STATUS_EXTERNAL_OR_UNVERIFIED`.

## Git and effective context — K–L

The fresh diagnostic state binds HEAD, index digest, physical selected source/model/
schema/test/evaluator and pinned JSON evidence bytes, runtime observation and
R5.46/R5.48 preservation hashes. Captures agree before/after all recorded stages.
Its identity is:

`cf0db7b38b51b463027b5a63cfb7fee6162e3cccf0b540499e22f4895b87a39c`

This is deliberately **an incomplete diagnostic identity**, not a minimal core
execution identity. Its broad HEAD/index treatment can change for development-only
staged changes; the narrower historical synthetic fixture's authoring exclusions
must not be claimed for this diagnostic identity. Physical input and index/committed
state mutation tests were freshly rerun, but production effective Git attributes,
configuration, helpers, mode behavior, submodules and external context are not
qualified. Unsupported links/submodules/unmerged fixture inputs fail closed.

| Context property | Current treatment |
| --- | --- |
| cwd, selected operation/argv, model/store location | MATERIAL; bounded probe specifies them, production launch-wide identity not qualified. |
| Python module search/startup/cache paths | MATERIAL; `-S`, explicit source root and observed origins bound diagnostically; exhaustive descendant/cache closure UNKNOWN. |
| Executable search | MATERIAL for evaluator tools; core probe uses absolute Python and empty PATH. Evaluator PATH/tool descendant closure UNKNOWN. |
| Python hash seed, UTF-8 mode, bytecode-write policy | MATERIAL; explicitly controlled public enums in the child. |
| Interpreter/platform/filesystem encoding | MATERIAL; observed runtime fields. Complete runtime image/service identity UNKNOWN. |
| Locale, encoding aliases, timezone | Computation-relative; not assumed irrelevant for arbitrary operations. Production materiality/identity UNKNOWN. |
| Temp/system roots, filesystem semantics and ownership | MATERIAL where used; production ownership/context UNKNOWN. |
| AI credential, model, editor/OpenCode metadata | IRRELEVANT to the tested fixed core operation; excluded from its semantic inputs. |
| Built-in/frozen code | DERIVED only from a stronger complete interpreter image, not the partial executable observation. |
| Unrelated environment variable | IRRELEVANT to the bounded core probes as independently tested; no general name-based exclusion for arbitrary programs. |

These UNKNOWNs prevent production qualification; they are not silently normalized.

## ExecutionCapsuleV2 design, determinism and mutation evidence — N–Q

The intended production candidate must compose relevant effective repository/Git
state, complete runtime identity, material dependency graph and native descendants,
material public/secret-safe controls, resolved tools, effective context, and the
R5.47 infrastructure identity. Non-material development-authoring state is excluded.
No timestamp participates in semantic identity; suite elapsed time is separate
diagnostic receipt telemetry.

**Construction of a complete production candidate stopped at native closure.**
The diagnostic state is not renamed ExecutionCapsuleV2. The R5.48 observed-host
composition and closed-fixture certificate bridge remain unqualified for production.
This design is a requirement/proposal, not implemented production behavior.

Freshly replayed fixture tests demonstrate deterministic capture, canonical round
trip, source/staged/unstaged/untracked and ignored-input mutations, runtime,
dependency, public-environment, tool and context mutation rejection. New provenance
tests separately detect repository/copy/native-external byte mutations and reject
unattributed/missing/native-descendant closure. Credential/model/editor/OpenCode
and unrelated-environment changes preserve bounded core outputs and the applicable
closed-fixture identity. Real production descendant mutations and full production
context minimality were **not qualified**.

## Ownership, certificate and lifecycle — R–V

The fresh synthetic attack changes a relevant input **after final capture**, reads
the changed input during observation, then restores it before final integrity.
The existing synthetic bridge records one observation while the final capture
equals the certified fixture. This is direct evidence that endpoint recapture
does not establish exclusive ownership or ABA-resistant check-and-use.

Proposed ownership mechanism: a content-addressed immutable materialization of
the complete input/runtime/tool closure, with child access restricted to that
materialization and separately controlled output paths. An isolated worktree or
read-only attribute alone is not sufficient; the actual evaluator must execute
only the certified immutable state. No such production mechanism was installed
or qualified here. Post-seal prevention therefore has no positive qualification.

Fresh certificate regressions preserve capsule/state linkage, stage mechanisms,
R5.47 infrastructure, recorder/canonical protocol, authority, semantic count,
contamination and lock-state checks in **synthetic** assembly. Mixed-capsule,
missing receipt, stale certificate, material pre-authorization mutation, unsafe
publication and second-observation tests reject as expected. One synthetic
observation and final fixture integrity pass. This does not supply the missing
complete production capsule or ownership guarantee.

The requested lifecycle cannot advance from observed provenance to **qualified
complete closure**, so production certificate assembly, sealing/owning production
state, final production authorization and its observation remain **not reached**.
There is no production-shaped synthetic success relabeled as production success.

## Bounded fresh verification

The new R5.49 runner records **78/78 diagnostic PASS receipts** in four bounded
batches (23, 25, 20, 10 completions). Each stage has a persisted INCOMPLETE attempt,
its own child process, a maximum 65-second worker bound, a matching mechanism
digest and the same before/after diagnostic state. Incomplete/failed/mixed/drifting
stages fail closed; abandoned attempts cannot be retried. Batches have an 85-second
work budget, avoiding the monolithic R5.44 timeout pattern.

| Fresh verification | Result |
| --- | --- |
| Restricted harness, split by module | 429 discovered / **393 passed / 36 preserved prohibited skips** |
| Application/compiler | **31 passed** |
| R5.41 focused | **14 passed** |
| R5.43 recorder | **29 passed** |
| R5.45 certificate | **33 passed**, synthetic scope |
| R5.47 security | **22 passed** |
| Environment publication | **2 passed** |
| Historical identity implementation freshly replayed | **52 passed**, historical prototype scope |
| New provenance suite | **24 passed** |
| New AI-independence suite | **5 passed** |
| New ownership counterexample | **1 passed**, confirms gap |
| Actual core/deployment inventory | PASS observed provenance; closure explicitly incomplete |
| Independent matrix/coherence | **16 profiles / 84 rows**, canonical equality and determinism |
| Structural profile schema / traceability / contamination | Valid / **99 leaves** / clean |
| Historical / prospective / R5.47 successor locks | **678 / 695 / 1,065**, valid |
| Validation / safety / staged diff check | PASS |

### Required test accounting

| Required areas | Fresh evidence and qualification limit |
| --- | --- |
| 1–3 repository/nested/generated provenance | New layout tests and actual copied-deployment imports pass. |
| 4 standard runtime | Resolved source, built-in and frozen-loader tests pass; complete image closure is not qualified. |
| 5 genuine third party | Discoverable installed-file metadata fixture passes; no third-party dependency was introduced into core. |
| 6 editable/local installation | Attributed external-source fixture remains third-party; unattributed external source rejects as UNKNOWN. |
| 7 external executable | Actual Python executable provenance and disposable native-byte mutation tests pass. |
| 8 dependency closure | Supplied transitive/cyclic graph traversal and missing-node rejection pass; actual complete closure is not established. |
| 9 native descendants | Actual direct PE evidence and fail-closed closure test; **gap**, not successful closure. |
| 10 unknown rejection | New material UNKNOWN/custom-loader tests reject. |
| 11–13 repository determinism/dirty Git/context | Fresh synthetic-fixture replay passes; effective production Git/context remains unqualified. |
| 14–15 capsule deterministic capture/round trip | Diagnostic/closed-fixture tests pass; complete production ExecutionCapsuleV2 **not reached**. |
| 16–18 dependency/native/environment mutation | Fresh implementation/copy/native-byte tests and synthetic environment mutation tests pass; real complete native-capsule mutation not qualified. |
| 19 irrelevant environment | Fresh bounded core output stability passes; no arbitrary-program exclusion claim. |
| 20–24 credentials/model/OpenCode/offline/no inference | Fresh subprocess/identity/direct-import evidence passes within tested scope. |
| 25 secret safety | Fresh R5.47 guard/publication regressions pass; real credentials were not used. |
| 26–27 ownership/post-seal prevention | Fresh ABA counterexample confirms **gap**; no production seal or prevention success. |
| 28 mixed-capsule receipts | Fresh historical synthetic bridge replay rejects mixed state. |
| 29 production certificate assembly | Production-shaped synthetic assembly passes and production promotion rejects; actual production assembly **not reached**. |
| 30–31 stale certificate/bounded final validation | Fresh synthetic replay passes; production final validation not reached. |
| 32–33 one observation/second prevention | Fresh synthetic replay passes; full owned production-capsule lifecycle not reached. |

Passing regression denominators do not yield capsule qualification.

Evidence: [stage definitions](R5_49-evidence/definitions.json),
[diagnostic state](R5_49-evidence/state.json),
[core/native inventory](R5_49-evidence/core-inventory-worker.json),
[deployment inventory](R5_49-evidence/deployment-inventory-worker.json),
[AI tests](R5_49-evidence/ai-independence-worker.json),
[ownership counterexample](R5_49-evidence/ownership-counterexample-worker.json),
[locks](R5_49-evidence/locks-worker.json), and
[stopped summary with receipt digests](R5_49-evidence/summary.json).

## Final boundary

After report/overview/research/decision publication, a separate final verification
recomputes the diagnostic state, checks every stopped-summary receipt digest, and
confirms the included historical-evidence hashes are unchanged. It passes.
The final `git diff --check` passes; Git's existing LF/CRLF notices are not
whitespace-check failures. Markdown reporting is outside this incomplete diagnostic
execution slice and does not change its identity.

The generic R5.48 provenance failure class is reproduced and corrected without
name exceptions. Complete material native/descendant closure is not established,
so qualification stops at that first gate. Actual effective Git/context and
exclusive ownership remain additional evidenced/unqualified obligations.

The benchmark target remains semantic and externally observable behavioral
equivalence, not conventional/generated source layout, functions, classes,
storage representation or architecture.

**Zero B02 exposure**: no reservations, dispatch, CheckedPlans, readiness, audit,
admission, static evaluation, generation, execution or frozen acceptance. Restricted
harness skips remain active. Core **30**, no semantic #31. B03 prospectively
untouched, B17 unexposed/unclassified, Phase 5C paused. Any subsequent qualification
requires a separately versioned fresh run after closure and ownership are implemented;
these incomplete diagnostic receipts cannot satisfy production requirements.
