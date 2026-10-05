# R5.70 — CertificateV3 observation-consumer migration and publication reconciliation

## Result

**`R5_70_V3_OBSERVATION_CONSUMER_QUALIFIED`**, within prospective consumer and
publication-mechanism scope. **The full production B02 gate remains unqualified.**
B02 stays sealed. Phase 5C stays paused; core semantics stay **30**.

The new production `StaticGate.prepare` consumes qualified CertificateV3 through
its existing R5.68 interface. The frozen R5.69 publication rejection independently
reproduces and is classified **`PROTOCOL_METADATA_FALSE_POSITIVE`**. Generic pinned
typed source/object publication reconciles it prospectively without changing the
historical artifact, renaming its rejected field, or adding a filename exemption.

Final selected focused verification: **288/288 tests pass**. The separately recorded
final synthetic demonstration performs exactly one reservation/dispatch/completion
and one seal opening, then rejects replay. Actual B02 attempts/reads are **0/0**;
exposure/reservation/dispatch/completion **0/0/0/0**; opening ledger **0/0**.

## Inherited gap and historical boundary

R5.69 permanently remains **`R5_69_OBSERVATION_CONTROL_GAP`**. Its 193 regression
stages, eight prerequisites and 15 checkpoints are not resumed. Its identity
successfully sealed/persisted/schema-revalidated/reloaded before the starting
consumer failed. The later publication rejection remains secondary, with its
original FAIL evidence and frozen orchestration retained.

All implementation changes are new R5.70 modules. No R5.51/R5.55/R5.66/R5.68
producer, validator, runtime, schema, old orchestration or candidate is modified.
CertificateV3 production and Phase 5 methodology are not redesigned.

## Exact legacy consumer trace

| Layer | Actual legacy dependency |
| --- | --- |
| `tier2_r5_51.StaticGate.prepare`, lines 342–350 | Workspace verification, local `validate`, staging, R5.43 recorder freeze |
| `tier2_r5_51.validate`, lines 243–247 | Current capsule must equal original; reconstructs the local certificate |
| `tier2_r5_51.certificate`, lines 210–240 | R5.51 protocol/policy/receipts, hard-coded infrastructure identity and physical-lock evidence |
| Legacy receipt checks | Required `identity`, `locks`, `contamination`, `workspace`; successful sealed Tier-2 receipts matching capsule/experiment/stage/mechanism |
| Legacy authority | `policy.authority` must equal capsule authority-role digest; no QualifiedAuthority/declaration/qualification linkage |
| Legacy physical locks | Exactly historical/prospective/infrastructure lock state, with the fixed R5.51 infrastructure pin |
| `live_checks`, lines 352–361 | Reads legacy `required_locks` and `authority` fields rather than current sealed QualifiedAuthority evidence |
| `observe_synthetic`, lines 363–406 | Synthetic-name restriction, arbitrary callback, old validator before/after, legacy live checks and recorder lifecycle |

The R5.51 certificate has no explicit certificate version or V3 mode. Its protocol
is the capsule protocol, not the V3 certificate protocol. Its validator does not
interpret V3's mode declaration, authorization schema, QualifiedAuthority,
verification modes or explicit zero observation state. It does retain contamination,
semantic identity, dedicated workspace and capsule/receipt checks. Synthetic-only
dispatch is a separate old assumption; the fixed physical locks are certificate
assumptions. The concrete V3 policy lacks the demanded `infrastructure` and legacy
lock/authority layout. No intervening adapter resolves that mismatch.

The R5.68 producer already supports successor/sealed authority and explicit modes.
Its `require_operation` validates the complete V3 contract; R5.69 failed because the
consumer never called that interface. The R5.66 synthetic opener separately binds
authority/resource/commitment/ledger, but lacks the outer certificate/qualification
binding supplied by the new synthetic two-object consumer.

## Prospective contract and migration

Implementation: `benchmark/evaluation/observation_consumer_r5_70.py`.
Versioned contract: [R5.70 consumer contract](../../../docs/observation-consumer-r5.70.md).

Production `prepare()` requires exact protocol `lykoi-production-certificate-v3`,
integer version **3**, and **`PRODUCTION_SEALED`**. Unknown versions/protocols, legacy
R5.51 certificates and synthetic V2 reject. Even deliberately configuring the
consumer for synthetic mode does not make production `prepare()` accept it.
`prepare_synthetic()` is explicit and limited to synthetic immutable sealed resources.

Validation invokes the qualified R5.68 `require_operation` with the expected mode's
gate operation and all current inputs: exact QualifiedAuthority, capsule, receipt
set/policy, current capture, R5.66 Authority adapter, producer declaration and
external declaration/qualification pins. It revalidates authorization/schema,
authority/resource-policy/commitment linkage, capsule/receipts, clean contamination,
zero observation state and sealed no-opening policy. There is no legacy certificate
reconstruction or latest-version selection. Historical validators continue to
interpret historical V1/V2 explicitly; fresh tests demonstrate both preservation
and prospective rejection.

## Sealed evidence and separate observation authorization

`SEALED_COMMITMENT_VERIFIED` is accepted through the qualified R5.66 authority
interface. No current byte-read verification is demanded for sealed members.
Preparation stages evidence and verifies ownership without opening resources.
Every sealed member must match both identity and resolved path in the guard.

Certificate alone rejects before any reservation or opening. The implemented
synthetic declaration separately binds consumer protocol/operation, exact certificate
and qualification, and the qualified R5.66 opening grant's authority/resource/
commitment/one-time ledger. External pins are required. Wrong operation, certificate,
qualification, pin, worker inputs or alternate ledger reject. No actual B02
authorization issuer, actual opener or B02 observation API exists in this migration.
Future actual opening continues to require production-sealed certification **plus**
a separately authorized one-time actual observation declaration.

## Mediated execution and accounting

Only a content-pinned R5.62 `Child` is accepted as worker. Its capabilities are
same-or-narrower than the parent; execution binds certificate/qualification,
QualifiedAuthority, guard/resource policy and full reviewed worker descriptor.
R5.62 revalidates source/runtime/registry/exclusion/interpreter/environment integrity;
safe exclusion and protected-resource enforcement precede worker import. Ordinary
callbacks, escalation, missing/wrong guard paths, protected access, source/binding
mutation and unaudited child paths reject. Minimal environment and redacted errors
remain active. No AI-provider state or new Git requirement is introduced.

The R5.43 recorder remains responsible for exclusive observation reservation and
completion, immutable evidence, replay discipline and stopped-run behavior. R5.70
adds explicitly linked durable dispatch/completion evidence around mediated
observation; R5.66 retains exclusive reserve-before-read opening ledgers. Preparation
cannot reset an existing evidence directory. Failed/mismatched opening remains
consumed rather than retried.

## Synthetic end-to-end evidence

Final demonstration artifacts have the `-final` suffix under [R5_70-evidence](R5_70-evidence/).

1. Fresh synthetic ordinary/sealed authority and V3 production-sealed inputs are
   created with qualified interfaces and dedicated synthetic owner pins.
2. Production preparation succeeds; synthetic protected-store content reads remain zero.
3. Certificate-alone observation rejects with no opening ledger.
4. Separate synthetic one-time authorization is supplied.
5. Recorder reserves once; dispatch durably binds reservation, authorization,
   execution and opening ledger; R5.66 reserves then opens once.
6. A real R5.62-mediated synthetic worker validates opening evidence without
   receiving protected content. Recorder completion and linked completion evidence
   persist; immediate state/authority/contamination/integrity checks pass.
7. Final counts are one reservation and one completed observation; the durable
   dispatch and opening result establish one dispatch and one opening.
8. Replay rejects and content-read count stays one. Alternate-ledger rejection is
   separately challenged by focused tests.

See [final synthetic flow](R5_70-evidence/synthetic-flow-final.json),
[dispatch](R5_70-evidence/synthetic-synthetic-dispatch-final.json),
[completion](R5_70-evidence/synthetic-synthetic-completion-final.json), and
[opening result](R5_70-evidence/synthetic-opening-result-final.json).
Unit tests use separate temporary fixtures, not this demonstration's ledger or B02.

## Publication adjudication and correction

[Independent reproduction](R5_70-evidence/publication-adjudication.json) reads only
the unsealed frozen R5.69 orchestration, checks its physical digest against the
frozen qualification identity, and invokes the unchanged publication guard.

The sole sensitive-assignment match is source **line 236**, field
`production_authorization`, with the fixed status value `REQUIRED_NOT_ISSUED`.
This denotes an explicitly required but unissued protocol declaration; it is not
a credential, secret reference, security fixture, or grant to open B02. The summary
writer supplies no producer schema for that field, and source-text scanning has no
typed context. Both failures are the same context loss. Classification:
**`PROTOCOL_METADATA_FALSE_POSITIVE`**.

The source is frozen as the stopped R5.69 candidate's orchestration, not a new
current behavioral authority requiring modification. It is not edited. The old
guard still rejects it; R5.69's source/summary FAILs remain authoritative history.

Prospective `publication_r5_70.py` generalizes R5.59/R5.64 principles: immutable
producer schemas, externally pinned source identity, AST-recognized literal
dictionary context, typed value inspection, normally guarded unclassified remainder,
and fixture nonpublication. Its API has no filename argument or filename exemption.
The source context is content-bound, not a whitelist of the orchestration path.
An identical contextual literal works under arbitrary source identities/paths;
ordinary assignments and undeclared credential fields still reject.

The corrected source check passes without altering the frozen bytes. A new
[prospective summary publication](R5_70-evidence/prospective-summary-publication.json)
retains the original field and value and persists through the typed object path.
Recognizable credential values, short opaque HTTP authorization, undeclared opaque
credentials, marked secret structures, fixture leaks, source/schema mutation and
uncontextualized assignments all reject. Diagnostics withhold values. No synthetic
fixture designation or filename exemption is added.

## Focused verification

| Suite | Final selected result |
| --- | ---: |
| New V3 observation consumer / StaticGate / separate authorization | 32/32 |
| New publication reproduction / reconciliation / security adversaries | 16/16 |
| Historical synthetic Tier-2 / StaticGate preservation | 43/43 |
| CertificateV3 modes | 28/28 |
| Sealed authority / opening ledgers | 31/31 |
| Capability/resource guard | 30/30 |
| Mediated execution / safe exclusion | 47/47 |
| Continuity | 8/8 |
| R5.59 publication | 9/9 |
| R5.64 context-aware publication | 19/19 |
| Applicable publication/security subset | 20/20 |
| AI independence | 5/5 |
| **Total** | **288/288** |

The two previously diagnosed historical security-suite host assertions (physical
checkout lock and Git-ignore behavior) are explicitly excluded, recorded by ID,
and not relabeled PASS. The historical all-member V2 fixture suite is not run
because its setup reads sealed subjects; no-read V2/linkage witnesses are selected.
No full harness or production regression plan runs.

Generic schema structure, **99-leaf traceability**, contamination, validation,
safety, publication, historical preservation and `git diff --check` pass.
Verification installs a protected-path audit hook in each qualification process;
R5.62 children install their own qualified resource enforcement. Protected-path
denials remain zero in every recorded focused result.

Commands actually used:

```powershell
python -B benchmark/results/phase5c/r5_70_qualification.py baseline
python -B benchmark/results/phase5c/r5_70_qualification.py adjudicate
python -B benchmark/results/phase5c/r5_70_qualification.py consumer
python -B benchmark/results/phase5c/r5_70_qualification.py consumer corrected
python -B benchmark/results/phase5c/r5_70_qualification.py synthetic
python -B benchmark/results/phase5c/r5_70_qualification.py synthetic-report
python -B benchmark/results/phase5c/r5_70_qualification.py certificate
python -B benchmark/results/phase5c/r5_70_qualification.py execution
python -B benchmark/results/phase5c/r5_70_qualification.py security
python -B benchmark/results/phase5c/r5_70_qualification.py checks
python -B benchmark/results/phase5c/r5_70_qualification.py consumer accounting
python -B benchmark/results/phase5c/r5_70_qualification.py synthetic final
python -B benchmark/results/phase5c/r5_70_qualification.py consumer final
python -B benchmark/results/phase5c/r5_70_qualification.py publication-development
python -B benchmark/results/phase5c/r5_70_qualification.py consumer final-publication
python -B benchmark/results/phase5c/r5_70_qualification.py final
python -B benchmark/results/phase5c/r5_70_qualification.py consumer final-safety
python -B benchmark/results/phase5c/r5_70_qualification.py final completed
python -B benchmark/results/phase5c/r5_70_qualification.py preservation
```

### Development observations retained

An initial 37-test direct development run passed. The first recorded expanded
consumer run then found a new authorization-evidence filename colliding with the
recorder's `observation-*` namespace: **29/30**, with the error ID preserved.
Prospective evidence uses a separate namespace; corrected and final tests pass.

A preliminary synthetic development demonstration completed one opening and
rejected replay, then its report writer rejected an unclassified Boolean field
ending in the reserved authorization name. Its successful ledger/recorder artifacts
and publication failure remain preserved. `synthetic-report` publishes a validation
outcome from those already-existing artifacts without reopening that fixture.
The final separately versioned demonstration additionally retains linked durable
dispatch/completion evidence. Each demonstration opens its own synthetic resource
once; these are not repeated B02 observations or a resumed production candidate.

The first final source scan also correctly rejected a direct nonfunctional credential
assignment in a new adversarial test. Its failure is recorded separately. That
prospective test constructs the challenge value at runtime; the guard and fixture
designation registry remain unchanged. Final source/evidence publication passes.

Final review additionally requires a public root classification in the source
context schema; a secret/fixture root cannot grant a public child-field exemption.
The new adversarial test passes. The completed 288-test summary and publication
inventory carry the `-completed` suffix; earlier R5.70 development results remain
preserved independently. Separate-process final audit verifies those completed pins.

## Historical preservation and final accounting

The new baseline and independent verification preserve **2,215 unsealed historical
result files by physical bytes** and **four protected result files by size/mtime
metadata only**. This includes all R5.69 files and frozen source/report/rejection.
No protected historical content is inspected. Old infrastructure modules, frozen
requirements/oracles, model/compiler/runtime and old classifications are unchanged.

| Boundary | Final value |
| --- | --- |
| Actual B02 read attempts / content reads | **0 / 0** |
| Actual B02 exposure / reservation / dispatch / completion | **0 / 0 / 0 / 0** |
| Actual opening reservations / consumptions | **0 / 0** |
| Actual observation authorizations created / B02 openings | **0 / 0** |
| Final synthetic demonstration reservation / dispatch / completion | **1 / 1 / 1** |
| Final synthetic opening / replay content reads | **1 / 0 additional** |
| Full production batches / receipts / certificates | **0 / 0 / 0** |
| R5.69 repair / retry / resume | **None** |
| Core semantics | **30** |
| Phase 5C | **Paused** |

## Recommendation and stop

Recommend a **separately authorized, wholly fresh full production qualification**
that explicitly pins the R5.70 consumer/publication infrastructure, qualified
worker closures and R5.68 production declaration, creates all fresh required
authority/capsule/receipt/workspace evidence, and exercises the complete production
chain while B02 stays sealed. Historical receipts are not fresh qualification evidence.
Actual B02 opening would still require separate one-time authorization and further
explicit permission. That qualification does not begin here.

**STOP after R5.70: `R5_70_V3_OBSERVATION_CONSUMER_QUALIFIED`.**
