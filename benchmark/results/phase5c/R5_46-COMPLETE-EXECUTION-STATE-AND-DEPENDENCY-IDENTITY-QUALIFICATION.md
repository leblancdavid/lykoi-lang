# R5.46 — Complete Execution-State and Dependency-Identity Qualification

Primary classification: **`R5_46_PROTOCOL_HALT`**.

**The round is permanently stopped and its verification receipts are quarantined.**
A concurrent repository/security correction changed a protected R5.43 infrastructure
member during staged verification. The before/after check rejected the stage even
though its worker exited successfully. No production execution-state identity,
certificate, evidence reuse or locked authorization was qualified. B02 remains
completely sealed.

## Inherited boundary and scope

R5.45 ended `R5_45_STATE_IDENTITY_GAP`: 72 bounded checks, 33 synthetic certificate
tests, restricted harness 393 passes / 36 preserved skips, compiler/application
31, R5.41 focused 14 and recorder 29; matrix/coherence, validation, safety, structural
schema, traceability and contamination passed. Its reported historical/prospective/
infrastructure locks were 678/678, 695/695 and 731/731. R5.43 timing estimated
123.923 seconds of suite work for the former R5.44 monolith. R5.44's interruption
position remains unknown; incomplete results were never promoted to PASS.

Initial status contained the R5.45 prospective files/evidence and changes to the
three research documents. They were treated as inherited work. This round added
only infrastructure prototypes, tests, observation orchestration and reporting.
It did not edit semantic/profile/application/compiler/recorder implementations,
the frozen authority, historical results or generated artifacts. Concurrent owner
work committed and corrected R5.45 during this session; it was not performed by
this round and was not reverted.

## Observed halt and quarantine

The planned observational run comprised 74 stages: the inherited 72 plus execution
identity tests and a dependency inventory. Snapshot identity:
`4c03799dcc95d8361fd019db779cd19789ca65932f172a24a04b20ed3c79fec9`.
It was explicitly a repository observation snapshot, not a complete execution
identity or production certificate.

Fifteen completion receipts recorded PASS. The sixteenth,
`harness-test_coverage_gate_r5_3`, recorded **FAIL** for mid-stage repository
mutation. Its independent worker ran one test successfully, but that success did
not become a reusable stage PASS. Inspection found concurrent changes to
`.gitignore` and `r5_45_qualification.py`, plus a new environment-publication helper
and R5.45 security-correction record. Subsequent stopped-run accounting also saw
the R5.45 snapshot redaction, its new helper test and new bytecode files.

The protected-lock diagnostic established:

| Lock | Current byte matches | Status |
| --- | ---: | --- |
| Historical | 678/678 | PASS; identity and ancestry valid |
| Prospective | 695/695 | PASS; identity and ancestry valid |
| R5.43 infrastructure | **730/731** | **FAIL: `.gitignore`**; original lock identity remains valid |

This is an infrastructure integrity failure, not a semantic change or B02
capability result. The owner correction has its own
[security record](R5_45-SECURITY-REDACTION.md). That record says the redacted
R5.45 snapshot intentionally fails its old seal; no R5.45 snapshot resealing or
historical qualification replay was attempted here. A security correction is not
implicit permission to replace the R5.43 lock or continue an already changed-state
qualification.

The owner subsequently confirmed that a push warning identified an API-key
exposure and that separate work rewrote the offending commit and added the
`.gitignore` change. This explains the concurrent drift. It does not undo the
stage failure or restore the pinned infrastructure lock, and is not authorization
to restart this stopped experiment.

`R5_46-evidence/quarantine.json` seals the stopped receipts' hashes, the detected
drift and the permanent no-reuse disposition. `summary.json` and
`classification.json` preserve stopped-round accounting. The orchestrator refuses
batch/worker execution when quarantine exists. No new baseline or second
verification attempt was created. The halt classification takes precedence over
the independently identified unresolved dependency closure.

## A–C. Execution dependency inventory and relevance

Classification is relative to the actual inherited pipeline, including evidence
production and integrity gates. MATERIAL means an input can change computation
or authorization evidence; UNKNOWN means its effective closure/equivalence has
not been established. The following is an investigation inventory, **not a claim
that every material input is already captured**.

| Candidate | Classification | Rationale / binding obligation |
| --- | --- | --- |
| Physical executed source/model/test/profile/authority bytes and membership | MATERIAL | Imports, discovery and hash gates consume them; bind physical bytes including relevant ignored/untracked files. |
| HEAD and effective ancestry, replacements, graft/shallow behavior | MATERIAL | `historical_lock` calls `rev-parse` and `merge-base --is-ancestor`; commit label alone is insufficient. |
| Index/staged content and file modes | MATERIAL | Distinguish staged-only states and bind Git state required by the protocol; modes can change execution. |
| Unstaged changes | MATERIAL | Current physical bytes, not committed bytes, are executed. |
| Git attributes, ignore and conversion policy | MATERIAL | Membership selection, lock construction and diff checks can depend on them. Physical content hashing alone does not bind external attributes/ignore inputs. |
| Exact relevant Git configuration/helper closure | UNKNOWN | Broad configuration hashing is possible but not minimal; conditional includes, external attribute/ignore files and config-selected helpers need resolved dependency slicing. |
| Submodules | MATERIAL if present | Their commits and actual worktrees need recursive identity; fixture prototype fails closed on gitlinks rather than pretending to support them. |
| Python implementation, exact build/version, executable bytes | MATERIAL | Parser, runtime and subprocess behavior differ by implementation/build; version alone cannot bind patched executable bytes. |
| Python DLL, extension and stdlib implementations | MATERIAL | JSON/canonicalization, hashing, validation, imports, subprocesses and filesystem behavior run external library code. |
| Complete transitive/late-loaded native library and OS service closure | UNKNOWN | Selected DLL hashes and an OS build label do not establish every implementation actually used by Python and Git descendants. |
| Interpreter flags, `-X` options and effective startup configuration | MATERIAL | Optimization, encoding, import behavior, integer conversion limits and other runtime controls can change results. |
| Existing readable bytecode / interpreter caches | MATERIAL | `-B` suppresses writes, **not reads**. Excluding caches requires a separately qualified cache-free mechanism. |
| Declared dependency ranges | IRRELEVANT as implementation proof | They are insufficient to identify the implementation which ran. Relevant declaration bytes are still repository inputs. |
| Resolved required Python dependencies | MATERIAL | Bind actual version **and implementation bytes**, with an exact declared relevant set and missing/unexpected policy. |
| Unrelated installed distributions | IRRELEVANT only after isolation proof | Do not hash all installed software merely because it exists. Current user-site/import startup behavior leaves interference exclusion UNKNOWN. |
| User/site startup hooks, `.pth` execution, import paths/shadowing | MATERIAL; closure UNKNOWN | User site is enabled and workers are not isolated. The current observation found no `.pth` files in inspected site directories; absence does not prove descendant import closure. |
| Python executable and Git binary/tool behavior | MATERIAL | Python subprocesses and Git are directly invoked by verification; Git version/executable hash do not bind its companion executables/libraries. |
| PowerShell/tool supervisor | MATERIAL for launch/completion evidence | It supplies environment, cwd and the execution envelope. No independent shell logic is required inside the proposed certificate comparator; upstream supervision still needs qualification. |
| `PYTHON*`, `PYTHONPATH`, `PYTHONHOME`, search and startup controls | MATERIAL when effective | Bind resolved worker behavior, not merely the parent environment. Child `-E` use differs from ordinary children. |
| `PATH`, `PATHEXT`, loader/system-root settings, `GIT_*` | MATERIAL when effective | Resolve actual tools/configuration/libraries; do not substitute a requested tool name for actual resolution. |
| Locale, encoding, timezone, hashing/determinism controls | MATERIAL when consumed | Text subprocess decoding, case/path behavior and random hash iteration may affect evidence. UTC-aware application values do not justify globally ignoring all locale/time controls. |
| `LYKOI_R5_22_CAPS`, trace/invocation and benchmark settings | MATERIAL when consumed | Current/legacy runtime adapters read capability or trace configuration and propagate environment to descendants. Bind declared worker overrides and consumer semantics. |
| Effective relevant environment subset for all descendants | UNKNOWN | An allowlist publication helper is not a proof of noninterference or complete execution identity. |
| Cwd / relative path resolution | MATERIAL | Model, module, durable and evidence resolution consume execution context. Role equivalence requires proving behavior before discarding absolute location. |
| Case sensitivity, filesystem/reparse/link semantics, temp behavior, permissions | MATERIAL when effective | File creation, locks, exclusive reservations and generated subprocess runs consume these behaviors. Symlinks/nonregular files fail closed in the fixture. |
| Physical line endings | MATERIAL | Byte locks and generated comparison consume actual bytes. No blanket LF/CRLF normalization is authorized. |
| Current clocks, random IDs/temp names and timeout scheduling | MATERIAL or observation nondeterminism | Not timestamps to insert into semantic identity. Controlled provider/temp policy and bounded execution assumptions must be qualified; same environment does not promise identical timing. |
| Dirty/status summaries | DERIVED | Determined by physical/index/HEAD/configuration inputs; not an independent freshness guarantee. |
| Dependency declaration summary / canonical hash / certificate state reference | DERIVED | Resolved bytes or canonical components determine these; do not independently fingerprint redundant metadata. |
| Hostname, serial numbers, terminal appearance, unrelated hardware/software | IRRELEVANT to identified direct consumers | No direct consumer was identified; exclude them from the fixture identity. Startup/native noninterference remains a production obligation. |
| Username and home path as human identifiers | IRRELEVANT as identifiers | Bind effective site/config/import inputs where necessary, not the identity of their owner. |
| Secret-bearing configuration | MATERIAL if consumed | Use domain-separated keyed identity, never raw values; relevance and key custody need explicit policy. |

The inventory observation records **CPython 3.14.3, MSC v.1944 AMD64**, Windows
build `10.0.26300`, **Git 2.52.0.windows.1**, and actual executable hashes. Python
executable hash is `cce21c0e8710e304273e98ac4b2b0f5aceb639acbcd2343cbaa5c4e81619c45b`.
Git executable hash is `3cbd024d9d11ef08bd6a0cb5a973613c50825b4952bc6006f3f4222f436091e5`.
Four runtime-root DLLs were found: `python3.dll`, `python314.dll`,
`vcruntime140.dll`, `vcruntime140_1.dll`; their hashes and selected resolved
stdlib/extension hashes are in the stopped summary.

The repository declares no third-party dependencies. The observed interpreter
nevertheless has **67 installed distributions**, whose resolved names/versions
are recorded, not their credential/configuration contents. This is diagnostic
inventory, not a 67-package execution lock and not evidence that they all affect
evaluation. Actual descendant import origins and startup exclusion have not been
qualified. Merely hashing those version labels would still omit implementation
bytes and native dependencies.

## D–H. Prototype identities and canonical composition

Unqualified implementation: `benchmark/evaluation/execution_identity_r5_46.py`.
Protocol: `lykoi-execution-identity-r5.46-synthetic`.

- Repository component: physical file bytes/membership; HEAD; effective parent
  traversal hash; index records; keyed effective Git configuration identity;
  declared exclusions. Submodules fail closed. The all-config hash is deliberately
  a **broad fixture primitive**, not proven minimal production relevance.
- Runtime descriptor: implementation/build, executable hash, flags, options,
  platform behavior labels and filesystem encoding/error policy. It explicitly
  does not claim native/stdlib closure. Reflective flag metadata is redundant;
  minimal flag slicing was not qualified.
- Dependency component: exact caller-declared resolved names, versions and file
  hashes; missing/unexpected relevant names and unavailable/linked files reject.
  This is a closed fixture manifest, not discovery of arbitrary imports.
- Environment component: explicit material names; absent, empty and nonempty remain
  distinct. Sensitive values use domain-separated HMAC-SHA256. Undeclared fixture
  terminal-color metadata is omitted because no fixture consumer reads it.
- Tools/context: explicit synthetic tool implementation/version and cwd/filesystem
  behavior descriptors. These descriptors do not attest actual external tools or
  physical filesystem behavior.
- Composition: repository + runtime + dependencies + effective environment +
  tools + context + unknown obligations, canonicalized by the unchanged R5.43
  protocol and sealed with SHA-256. UNKNOWN obligations reject certificate assembly.

Sealing copies canonical content; changing a recorded dictionary invalidates its
integrity seal. Exclusive R5.43 persistence supplies immutable artifact creation.
No wall-clock timestamp appears in semantic state identity. Capture time may be
telemetry, not freshness. Cryptographic integrity here has the inherited trusted
local producer boundary, not hostile attestation.

## I–K. Adversarial tests, secrets and determinism

`test_execution_identity_r5_46.py` contains **49 proposed tests**, including all
30 requested categories, actual disposable Git staged/unstaged/untracked probes,
runtime/dependency/environment/tool/context mutation, round trips, repeated
process capture, secret identity, mixed-state assembly, UNKNOWN/production
rejection and exactly-one synthetic authorization.

The initial direct run executed **46 tests in 10.624 seconds; all 46 errored in
setup** because the new collector used `config.hex()` instead of
`config.stdout.hex()`. The error was corrected and three tests added **before**
the observational snapshot. The post-fix execution-identity test stage was not
reached before halt. **There is no passing R5.46 synthetic qualification result.**

| Requested mutation family | Implemented probe | Qualified result |
| --- | --- | --- |
| Source, staged-only, unstaged, relevant untracked/ignored inputs | Real disposable Git repository and physical-byte mutation | NOT ESTABLISHED |
| Runtime version/flags; dependency version and same-version implementation bytes | Independent fixture component/file mutations | NOT ESTABLISHED |
| Missing/unexpected relevant dependency | Exact resolved manifest rejection | NOT ESTABLISHED |
| Relevant environment change; absent/present/empty transitions | Material `MODE` / synthetic `TOKEN` cases | NOT ESTABLISHED |
| Irrelevant environment mutation | No consumer for fixture terminal color | NOT ESTABLISHED; irrelevance is fixture-scoped |
| Tool version; cwd role/filesystem case policy; Git config | Independent component mutations and actual Git config | NOT ESTABLISHED |
| Secret-safe identity, weak-key rejection and key rotation | HMAC, no plaintext fixture secret in state | NOT ESTABLISHED |
| Canonical bytes/reload, repeated process and cross-batch identity | Serialization and subprocess probes | NOT ESTABLISHED |
| Material/irrelevant post-certificate mutation and one-pass lifecycle | R5.45 bridge and unchanged R5.43 recorder | NOT ESTABLISHED |

The new production environment observation persists **variable names only**, never
values, and stores no real HMAC key or real credential. Candidate names included
Python/Git/Lykoi controls, path/temp/system and user-profile context. Synthetic
credential strings and a fixed test key are explicitly fixture data; that key is
not secure production key material. A production HMAC mechanism needs a strong
externally provisioned stable key, protected custody, key identity/rotation policy
and separately qualified subprocess propagation. A public salt or ordinary hash
of a low-entropy secret is insufficient. Current relevant-secret policy remains
unqualified. No real environment was dumped into R5.46 artifacts.

## L–O. Cross-batch evidence, TOCTOU, certificates and reuse

The prospective stage primitive requires before/after canonical execution-state
equality. The **actual observational runner** required before/after repository
snapshot equality and demonstrated rejection of a successful worker when that
snapshot changed. This is one real non-reusable mutation rejection, not proof of
complete external-state equality across batches. All sixteen receipts are now
quarantined, including the fifteen earlier PASS receipts.

The fixture bridge places the entire canonical execution identity inside a
versioned R5.45 state envelope. Stage hashes bind that envelope; existing R5.45
assembly retains policy, stage mechanisms, recorder, canonical protocol, frozen
authority, count, lock/contamination and regression evidence. The new assembly
entry **rejects production purpose**. The old R5.45 production-input closure is
not upgraded by merely adding this wrapper.

The prospective authorization entry takes a capture callback and freshly compares
current state immediately before the unchanged synthetic-only recorder gate.
Expected stale material state: REJECT before reservation. Expected justified
irrelevant fixture mutation: equivalent identity. Expected exactly-one callback:
second dispatch prevented. These post-fix lifecycle expectations are **unverified**
in R5.46, rather than inherited passes attributed to the new code.

Endpoint equality cannot detect change-and-restore (ABA) during a stage, nor prevent
change after final capture and before use. A proposed test explicitly documents
that limitation. Exclusive ownership is an R5.43/R5.45 assumption; actual external
Python/Git libraries are not sealed by repository ownership. Production TOCTOU
protection needs a qualified immutable execution capsule or equivalent protected
dependency/worker mechanism, not just a cheaper comparison function.

Proposed reuse requires unchanged relevant repository, external execution and
protocol/version dependencies, valid evidence integrity, completed guarantees and
fresh structural identity equality. No time-to-live, same machine or same commit
rule suffices. No narrower dependency reuse is qualified. This stopped round
authorizes **no evidence reuse**.

## P. Bounded costs and incomplete regression verification

The sixteen supervised subprocesses total **39.083625 seconds**; largest stage
was boundary closure at **11.235579 seconds**. The rejected stage cost **3.028073
seconds**. These are verification worker timings, **not complete execution-state
capture/final-validation timings**. Capture, canonicalization, validation and
comparison measurement stages were not reached. No production cost bound is
established; no synthetic capture measurement is promoted to a production bound.

| Required regression | R5.46 observation |
| --- | --- |
| Full restricted harness | Incomplete: 15 earlier stage receipts cover 114 discovered / 79 passes / 35 preserved skips; all quarantined |
| Sixteenth harness worker | One test passes locally; stage FAIL due repository mutation; not added to accepted totals |
| Application/compiler | Not reached; inherited 31/31 remains historical |
| R5.41 focused | Not reached; inherited 14/14 remains historical |
| R5.43 recorder | Its harness module passes 29/29; separate focused stage not reached; receipt quarantined |
| R5.45 certificate | Not reached; inherited 33/33 remains historical |
| R5.46 execution identity | Initial 46 setup errors; corrected/expanded 49-test suite not reached |
| Independent matrix/coherence | Not reached |
| Validation, safety, structural schema, traceability | Not reached |
| Contamination | Stopped-run existing nine-file and new two-file implementation scans clean; full profile stage not reached |
| Frozen authority | Stopped-run hashing verifies unchanged members; oracle not executed |
| Historical/prospective locks | Stopped-run 678/678 and 695/695, identity/ancestry valid |
| Qualified infrastructure lock | **FAIL: 730/731; `.gitignore` mismatch**; no successor issued |
| `git diff --check` | PASS in stopped-run accounting; final report check recorded separately |

Evidence under `R5_46-evidence/` includes snapshot, initial inherited-file hashes,
separate INCOMPLETE attempts, worker outcomes, completion receipts, quarantine,
summary and classification. New prototype hashes are recorded as **unqualified**,
not a qualified infrastructure successor. Documentation/accounting changes after
snapshot do not refresh or reseal stage evidence.

## Final boundary and next gate

**Zero B02 reservations, dispatches, static support evaluations, CheckedPlans,
readiness evaluations, audits, admissions, generation, execution or frozen
acceptance.** No benchmark exposure or synthetic callback occurred in this round.
The restricted runner preserved prohibited historical-test skips. Core semantics
begin and end at **30**, with no semantic/profile/application repair. B03 is
prospectively untouched; B17 unexposed/unclassified; Phase 5C paused. R5.42/R5.44
historical halts remain unchanged.

Primary classification: **`R5_46_PROTOCOL_HALT`**. Qualification fails before its
success criteria can be established. Repository mutation rejection is evidenced;
complete minimal external identity, safe production certificate integration,
cross-batch reuse, final TOCTOU protection and bounded capture remain unqualified.

Next gate: separately authorize reconciliation of the owner's security correction
with a **versioned infrastructure successor**, then re-establish an exclusively
owned starting state and qualify resolved execution-capsule dependency closure,
effective worker/environment identity and TOCTOU ownership. Do not restore exposed
credentials to satisfy an old hash. Preserve this halted run; do not resume or
relabel it. A new B02 static support-transfer experiment is **not** the next gate.
