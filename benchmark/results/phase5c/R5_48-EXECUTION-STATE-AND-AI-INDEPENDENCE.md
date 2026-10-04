# R5.48 — Execution-state identity and AI independence

## Disposition

**`R5_48_PROTOCOL_HALT`**. The fresh 74-stage investigation stopped at its
dependency-inventory gate: **71 receipts**, **70 PASS before quarantine**, one
failed inventory receipt. **Every receipt is quarantined and non-reusable.**
The frozen run was not repaired or resumed. No production certificate, qualified
execution identity or production TOCTOU guarantee follows.

The failure is an inventory implementation defect: a direct AST import-root screen
treated seven repository-owned standalone deployment runtimes/helpers as third-party
dependencies. Six correspond to repository source files; `transport_helpers_r5_41`
is an explicit deployment alias of `transport_runtime_r5_35.py` in
`benchmark/semantic/application_boundary_r5_41.py:96`. This is not evidence of an
AI-provider dependency or a language capability gap. The independently versioned
[stopped adjudication](R5_48-evidence/inventory-failure-adjudication.json) records
resolved source hashes and preserves the failed receipt. Any inventory correction
belongs to a separately authorized successor investigation.

The request ended at an empty “Halt / Failure Classifications” heading. The
prospective protocol used the explicit halt/quarantine outcome for verification
failure as well as material drift/exposure; it did not invent a qualified outcome.
The earlier planned descriptive identity-gap disposition was **not issued**.

## Baseline and historical preservation

The R5.47 security-corrected successor remains exactly:

- Manifest: `R5_47-infrastructure-lock-v2.json`.
- Members: **1,065**.
- Identity: `31339cb73996c9ee728656558477436d9a5ba1cfbd0272c771720e6a1f6bf084`.
- Canonical digest independently reconstructed and every member independently hashed
  by the new test module; successor verification passes before and after the run.

Historical lock **678/678**, prospective lock **695/695**; R5.43 historical identity
unchanged, **730/731** live matches with only its already reconciled `.gitignore`
difference. R5.46 remains permanently halted; all 16 prior receipts remain
quarantined and their recorded hashes are unchanged. The R5.46 prototype was not
imported, executed or promoted. Frozen authority hashes and core semantic count
remain unchanged. Rotation is still `ROTATION_STATUS_EXTERNAL_OR_UNVERIFIED`;
unavailable remote history is not attested.

## Implemented fresh infrastructure

- `benchmark/evaluation/execution_identity_r5_48.py`: new protocol
  **`lykoi-execution-state-identity-v2-r5.48`**, dependency-domain/environment
  classification, physical/scoped committed/index repository capture, exact
  observed interpreter/module/tool hashes, canonical sealing, cross-stage equality,
  fail-closed R5.45 certificate bridge and synthetic final authorization.
- `benchmark/evaluation/ai_independence_r5_48.py`: direct-import inspection and
  isolated offline core probe with network/external-process-denying audit hook.
- `benchmark/evaluation/test_execution_identity_r5_48.py`: **52 independent tests**.
- `r5_48_qualification.py`: separately bounded, restricted stages, secret-safe
  exclusive evidence publication and permanent halt/quarantine.
- [AI-independence policy](../../../docs/ai-independence-r5.48.md): language versus
  authoring domains, semantic authority, fixed-source cross-model principle,
  optional future application integrations and behavioral-equivalence boundary.

The observed, incomplete coordinator identity was:

`eb9693648f46bfbeab710b7548a02bfc93171e7456bf79ac94ce3a375cf7725d`

It is a **partial observed-host identity**, not a production capsule. Source state
remained identical through the recorded batches and stopped accounting. Stage
mechanisms and receipts bind this partial identity explicitly; they cannot substitute
for complete state certification and now remain quarantined.

## Investigations A–W

| Investigation | Finding and boundary |
| --- | --- |
| A — domains | Source/rules are LANGUAGE_CORE; Python/current host implementations BUILD_EXECUTION; model/input/store/clock/ID capabilities PROGRAM_DECLARED. Authoring providers/tools are DEVELOPMENT_AUTHORING; evaluation tools are optional relative to language correctness but material to evaluation. Unrelated installed packages/machine labels are excluded. Native/import/context closure remains UNKNOWN. |
| B — providers | Repository reference inventory publishes locations/categories only. No provider references were found in core source/model/generated paths. Direct core imports are stdlib/internal only; semantic helper roots are local deployment modules, misclassified by the failed gate. External agent configuration was not attested or made a dependency. |
| C — credentials | No real AI credential values were inspected. AI credentials, including presence and fingerprints, are absent from v2 core environment identity. Synthetic credential changes produce identical identity and core-operation outputs. |
| D — negative tests | Credential absent/changed, development model/editor metadata/author-only OpenCode config changed, no OpenCode and site-disabled execution all pass the independent probes/fixtures. |
| E — offline core | Valid/invalid semantic validation, deterministic generation and an existing generated program's read-only execution work with network/process operations denied. Static direct imports supplement dynamic observations. Audit hooks are bounded evidence, not a native sandbox or universal proof. |
| F — authority | Validator independently rejects an invalid language version; model/compiler rules, declared contracts and inputs determine meaning, not author interpretation. |
| G — inventory | Exact observed interpreter/stdlib/native-extension file and Git executable hashes are recorded. Complete native/descendant closure, actual context ownership and strict minimality are unqualified. |
| H — repository | Physical relevant-directory bytes and membership, scoped committed/index objects/modes, unstaged and ignored/untracked inputs are bound. Synthetic staged-only, unstaged, committed, untracked and membership mutations invalidate identity. Symlink/submodule/unmerged inputs reject. Root-level import shadows/external Git config remain closure gaps. |
| I — runtime | Actual CPython 3.14.3 executable/version/flags/xoptions/platform/filesystem encoding recorded; AI-agent runtime is excluded. Hashing on-disk frozen-module `__file__` values is observation, not independently proven resolved-code authority; executable/native closure remains necessary. |
| J — dependencies | Implementation bytes, not declared ranges or unrelated distribution inventories, are measured. Same-version resolved-file mutation is detected. The failed standalone import-root classifier is preserved as a defect. |
| K — environment | Host names receive domain classifications without values. Children are sanitized; only three qualified public Python controls enter the effective environment component. Preserved path/temp/system context is categorical and unresolved, rather than falsely bound by raw or unkeyed secret fingerprints. |
| L — tools | Actual resolved Git executable is material to qualification, not core compilation. Editors/agents are excluded. Tool mutation detection is qualified only on the closed fixture. |
| M — v2 | Fresh versioned composition is implemented and canonically round-trips; production qualification fails closed. R5.46 identity is not promoted. |
| N — minimality | Authoring state, unrelated packages, username/hostname/serial are excluded. Conservative repository/import observations are not a proven minimal production slice. |
| O — mutations | Source/index/unstaged/untracked/runtime/dependency/public-environment/tool/context mutations invalidate closed-fixture identity. Real production dependency closure has not been established. |
| P — authoring mutations | Credential presence/value, development model, editor metadata and non-material OpenCode config/index changes preserve fixture identity; real core outputs independently remain equal. No difference was merely accepted after a failed comparison. |
| Q — cross-model | Fixed-source semantics are author-independent; equal source production across different models is not required. |
| R — equivalence | Frozen observable behavior/invariants remain the benchmark target, not identical code, control flow, storage or architecture. |
| S — cross-batch | 70 stage PASS receipts had matching before/after partial observed identity; the failed gate quarantines all 71 receipts. No reusable production evidence is issued. |
| T — TOCTOU | Bounded synthetic recapture rejects post-certificate material changes before reservation; authoring-only changes preserve identity. ABA/exclusive ownership/atomic production check-and-dispatch remain unqualified. |
| U — certificate | R5.45 bridge binds v2/repository state, R5.47 baseline, receipts, recorder/canonical protocol, authority, count, contamination and required locks in synthetic assembly. Mixed/stale/unsafe/incomplete assembly rejects. **Valid actual production-certificate assembly was not achieved**; it cannot be relabeled synthetic success. |
| V — provider outage | Within the inspected/tested core scope, validation, generation, deterministic lowering and read-only execution continue: **YES**, with ordinary declared non-AI dependencies. Synthetic unreachable provider endpoints leave outputs identical. |
| W — future integrations | Explicit optional AI program/library dependencies are permitted in principle and separately identified, not core semantics. No integration was implemented. |

## Verification and evidence

| Verification observed before quarantine | Result |
| --- | --- |
| Restricted harness, split by module | 429 discovered / **393 passes / 36 preserved skips** |
| Application/compiler | **31 passed** |
| R5.41 focused | **14 passed** |
| R5.43 recorder | **29 passed** |
| R5.45 synthetic certificate | **33 passed** |
| R5.47 security | **22 passed** |
| Prior environment publication | **2 passed** |
| Fresh R5.48 execution/AI independence | **52 passed** |
| Independent matrix/coherence | **16 profiles / 84 rows**, deterministic and saved canonical equality |
| Structural profile schema / traceability / contamination | Valid / **99 leaves** / clean |
| Locks, frozen authority and semantic count | Passed; core **30** |
| Dependency inventory gate | **FAIL**, local standalone-module classifier defect |

`validate`, `safety` and `diff` did not run as the final three qualification stages.
Separate read-only stopped-state diagnostics then passed model validation, safety
and `git diff --check`. These are explicitly **not** missing-stage replacements,
qualification continuation or reusable PASS evidence. Full 74-stage qualification
did not pass.

Pre-freeze construction encountered two publication rejections: credential-named
domain-map keys and the stdlib module identifier `token`. Neither created unsafe
output or began a stage. Typed name/domain and implementation rows fixed the producer
shape without relaxing R5.47's guard. Both construction dispositions are retained.

Evidence:

- [Frozen partial state](R5_48-evidence/state.json) and
  [stage definitions](R5_48-evidence/definitions.json).
- [Host environment domains](R5_48-evidence/host-environment-domains.json), values omitted.
- [Failed inventory worker](R5_48-evidence/inventory-worker.json), immutable.
- [Permanent quarantine](R5_48-evidence/quarantine.json), hashing every existing receipt.
- [Stopped summary](R5_48-evidence/stopped-summary.json).
- [Independent stopped diagnostics](R5_48-evidence/post-halt-diagnostics.json).
- [Stopped reporting integrity](R5_48-evidence/stopped-final-integrity.json).

## Remaining production gaps and next boundary

Complete native Python/Git/OS dependency closure; actual descendant import/search/
startup/bytecode closure; material external Git configuration/helpers/attributes;
effective filesystem/context identity; strict per-computation minimality; and
immutable/exclusive ownership across the final check and dispatch remain unresolved.
Provider credentials are **not** a remedy or a required part of this closure.

Next requires a separately authorized, prospectively versioned inventory resolver
and execution-capsule/ownership qualification. Preserve R5.48's failed gate and all
quarantined receipts. AI independence is architectural policy with positive bounded
observations, not a production identity qualification.

**Zero B02 exposure**: reservations, dispatches, CheckedPlans, readiness, audit,
admission, static support, generation, execution and frozen acceptance all zero.
Core **30**, B03 prospectively untouched, B17 unexposed/unclassified, Phase 5C paused.
