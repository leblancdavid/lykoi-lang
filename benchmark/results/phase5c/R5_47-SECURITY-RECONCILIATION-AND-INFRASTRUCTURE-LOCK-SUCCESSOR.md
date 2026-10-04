# R5.47 — Security Reconciliation and Infrastructure-Lock Successor

Primary classification: **`R5_47_SECURITY_RECONCILIATION_QUALIFIED`**.

Security correction preserved; a separately versioned **1,065-member** physical
infrastructure successor is qualified. This is security/infrastructure reconciliation
only. No execution-state identity, production certificate, receipt reuse or benchmark
exposure is qualified. R5.48 has not begun.

## Inherited state and investigation A: change inventory

R5.46 remains permanently **`R5_46_PROTOCOL_HALT`**. Its 15 earlier PASS receipts
and failed sixteenth receipt remain quarantined. Historical 678/678 and prospective
695/695 byte locks pass; the immutable R5.43 infrastructure manifest retains a
730/731 live match, with `.gitignore` differing. Its original identity still verifies.
R5.47 began at clean HEAD `122bdb4a5435fee40d6e617df78abd22e2108955`.

Incident category: **raw authentication material in generated environment evidence**.
Human references to affected values are `[REDACTED]`. No value was recovered,
used, printed, fingerprinted or stored by this investigation.

| Area | Incident-related change / observation |
| --- | --- |
| `.gitignore` | Added `.env`, `.env.*`, with `.env.example`/`.env.sample` exceptions; retained exactly as committed. |
| Environment capture / infrastructure | `environment_snapshot.py` added public allowlist/default redaction; `r5_45_qualification.py` imports and uses it instead of publishing the raw parent environment. |
| Generated evidence | `R5_45-evidence/state.json` redacted `OPENAI_API_KEY` and `OPENCODE_SERVER_PASSWORD`; original identity and dependent receipts retained. Its old seal still rejects. |
| Reports | `R5_45-SECURITY-REDACTION.md` records the exception/rewrite requirement; R5.46 report and stopped-run accounting explain drift/quarantine. Three research summaries describe the boundary. |
| Logs / receipts | R5.46 quarantine records snapshot drift and all 16 receipt identities; no incident correction resealed receipts or promoted them. No additional raw-credential report/log/test artifact was detected in sharing scope. |
| Fixtures / tests | `test_environment_snapshot.py` added synthetic redaction tests. Synthetic R5.46 credential fixtures are research material, not leaked real credentials. |
| Configuration | Ignore/publication policy changed; no semantic/runtime/application configuration or committed replacement credential was introduced. |
| Local untracked/ignored state | Initial `git status` clean. No `.env*` files found. Scanner inspected 191 ignored local files, including bytecode; no unresolved credential finding. R5.46 records four remediation-associated added bytecode files, which are not sharing candidates. |
| Git history | Owner's recorded unpushed R5.45 rewrite is reflected in current history. Reflog metadata still lists a replaced commit; its contents were not recovered. All reachable local/remote-tracking refs scanned clean after exact non-authentication adjudication. |

R5.46 quarantine lists changed `.gitignore`, R5.45 collector/snapshot and its own
qualification runner, plus the new publication helper/test/security record and four
bytecode files. The R5.46 runner/accounting change is stopped-investigation work,
not a secret-remediation semantic change. Its report supplies that distinction.
Original credential-bearing historical objects are not restored to compare bytes.

## B–C, I: exposure/history scope and rotation

| Scope | Categorical finding |
| --- | --- |
| Working tree only | Incident was **not confined to working tree**. Corrected sharing candidates have no unresolved raw-credential finding. |
| Ignored/untracked file | Not the recorded incident carrier; no actual credential detected in inspected ignored local content. |
| Tracked/generated evidence | **YES**, the historical R5.45 environment snapshot was the carrier; current snapshot is redacted. |
| Local commit / earlier local history | **YES**, owner record identifies the original unpushed R5.45 commit; reachable corrected history is clean under the bounded scan. |
| Remote history | Original exposure was recorded as unpushed/rejected by a push warning. Locally available `origin/main`/`origin/HEAD` and `main` are scanned; `origin/main...HEAD` is 0/0. No credential detected there. Unfetched/server-side refs are not attested. |
| Reports/logs/test artifacts | No additional actual credential carrier detected. Exact fake fixture literals are separately adjudicated. |
| Reflog/unreachable objects | Replaced-commit metadata remains locally; excluded from intended sharing/push history. Do not publish/recover it. No Git history/reflog rewrite was performed by R5.47. |

Rotation/revocation remains required externally:
**`ROTATION_STATUS_EXTERNAL_OR_UNVERIFIED`**. Repository removal does not establish
that an exposed credential is safe. No replacement credential is stored.

`R5_47-repository-scan.json` seals the qualification scan of tracked working-tree
and new commit candidates, the complete index, **all three locally available refs**,
and ignored local files. Archive members are inspected in memory without extraction
or execution. Index scope includes 1,650 content checks and reachable-history scope
1,498 checks, including archive members. Working-tree check count grows as R5.47
outputs are added; final counts are in `R5_47-final-integrity.json`.

The scan found lexical CLI `token` fields, administrative `authorization` prose,
a CLI schema field and explicitly synthetic fixture literals. Adjudication substitutes
**only exact reviewed non-authentication literals in an in-memory scan copy**, never
whole files and never the publication guard. Unresolved findings: **zero**. This is
a bounded contextual/recognizable-pattern scan, not proof against every possible
opaque/encoded secret or attestation of unavailable remote history.

## D–H: ignore policy, publication invariant, identity and diagnostics

Policy: [secret-safe evidence R5.47](../../../docs/security-evidence-r5.47.md).
Implementation: `benchmark/evaluation/security_r5_47.py`.

**Raw credentials must never be persisted in benchmark/canonical evidence, reports,
logs, fixtures, committed configuration or generated project artifacts.** This covers
API keys, access/refresh tokens, passwords, private keys, secret connection strings
and equivalent authentication material. `.gitignore` is defense in depth.

The existing ignore correction is appropriately scoped to local dotenv files;
example/sample files remain visible and must contain placeholders only. Effective
Git tests verify `.env`, `.env.local`, nested `.env.production` and local environment
contents are ignored, while examples, source, canonical model and R5.47 evidence are
not hidden. No additional broad source/evidence exclusions were added.

Prospective `persist`, `report` and `PublicationRecorder` reject credential-named
fields, explicitly secret/sensitive structures, assignment text, selected recognizable
token shapes, bearer/basic auth, private-key headers and credential-bearing URLs
**before output-file creation**. Ordinary digests are not classified by entropy alone.
Diagnostics expose category and safe identifier-shaped field name only; arbitrary
keys, matched values and callback exception details are withheld. R5.47 regression
evidence publishes counts/test IDs instead of arbitrary worker output/tracebacks.

Environment publication now has a narrower prospective public enum/control policy
and presence metadata for everything else. Unknown values are never automatically
published. Material secret identity, when explicitly justified, uses domain-separated
HMAC-SHA256 with an external key of at least 32 bytes and safe key identifier. Exact
values and key bytes never enter evidence. Irrelevant secrets have no fingerprint;
plain hashes/public salts are not accepted for low-entropy secrets. Synthetic tests
establish representation and key separation. Production entropy/custody/rotation,
effective descendants and complete material relevance remain future qualification
obligations; no production identity guarantee is claimed here.

Historical raw writers remain frozen historical implementations and are **not
approved publication entry points for new work**. R5.48 must integrate the prospective
guard into its newly qualified mechanisms. The contextual detector cannot identify
every arbitrary opaque value; producers must not dump raw environment/configuration,
stdout/stderr or exception text. The invariant and constrained publication APIs are
the primary protection, with detection and ignore rules supplying defense in depth.

## J–M: semantic non-interference and successor audit

Core semantics remain **30**. All inherited tracked bytes match current HEAD,
except the three permitted research summaries edited for this report. No compiler,
semantic interpretation/vocabulary, public decoder, durable-domain/readiness/profile,
application, generated artifact, frozen requirement or oracle was changed by R5.47.
Protected historical/prospective byte locks and frozen-authority identities verify
before and after; restricted regressions challenge established behavior separately.

Predecessor `R5_43-infrastructure-lock.json` identity:

`5ded5ebc2a9412883a9796026fec8cd7d9477fa163e05012ac6a3a10a2254242`

Qualified successor **`R5_47-infrastructure-lock-v2.json`**, protocol
`lykoi-infrastructure-lock-r5.47-v2`, identity:

`31339cb73996c9ee728656558477436d9a5ba1cfbd0272c771720e6a1f6bf084`

Members: **1,065**. Predecessor members: **731 retained, zero removed**; **730 byte
identical**, sole changed member `.gitignore`. Additions: **334**, each classified
in `authorized_differences` in the successor. Categories are security remediation,
new R5.47 publication/lock/test/policy machinery, preserved predecessor qualification
evidence, preserved R5.44/R5.45/R5.46 stopped/gap evidence/orchestration, and retained
unqualified research. The audit rejects unknown additions or inherited byte changes.
The full physical snapshot includes preserved historical evidence and research;
membership does not promote their qualification status.

New machinery: `security_r5_47.py`, `infrastructure_lock_r5_47.py`,
`test_security_r5_47.py`, `r5_47_qualification.py`, `docs/security-evidence-r5.47.md`.
Only the three research summary documents and separately named `R5_47-*` output
artifacts are outside the lock. Future code changes require explicit succession,
not use of the output exemption to evade infrastructure locking.

The initial construction manifest `R5_47-infrastructure-lock.json` is retained as
an **unqualified draft**, not replaced or confused with the final `-v2` successor.
It preceded completion of exact synthetic-fixture scan adjudication. Its disposition
and the initial 19-test versus final 22-test suite are explicit in
`R5_47-draft-disposition.json`; no draft authority or receipt reuse follows.

Historical classifications remain byte-preserved:
R5.42 `R5_42_PROTOCOL_HALT`; R5.44 `R5_44_PROTOCOL_HALT`;
R5.45 `R5_45_STATE_IDENTITY_GAP`; R5.46 `R5_46_PROTOCOL_HALT`.
The redacted R5.45 snapshot still fails its original seal. All R5.46 receipts remain
quarantined. R5.43's manifest is not edited or made falsely current-compliant.

## N–P: deterministic qualification and security regressions

The final successor was generated, exclusively persisted, reloaded and all 1,065
members verified. Reproduction with current membership/metadata matches canonical
bytes; an independent hash comprehension also reproduces its identity. Disposable
copies of `.gitignore` and the security implementation are separately mutated;
both reject, then restored fixture bytes verify. The real historical/current files
are never mutated by these probes. Final real successor state verifies clean.

**22/22 independent security tests pass**, including all requested categories:
API key/token/password rejection; explicitly marked secrets; safe environment;
absent/empty/present metadata; keyed representation/no raw canonical value; weak
key rejection; redacted diagnostics; safe generated report; generic bearer/URL,
private-key and token detection; quoted/unquoted assignment rejection; no entropy-only
rejection; public-variable injection; malformed fingerprint rejection; recorder
write bypass prevention; callback exception redaction; `.gitignore` and security-code
mutation rejection/restoration; unchanged historical lock; effective Git ignore rules.
Only synthetic credentials and fixture keys are used.

## Required established regressions

| Check | R5.47 result |
| --- | --- |
| Restricted harness | **429 discovered; 393 passed; 36 preserved skips** |
| Application/compiler | **31/31 PASS** |
| R5.41 focused | **14/14 PASS** |
| R5.43 recorder qualification | **29/29 PASS** |
| R5.45 staged/certificate synthetic | **33/33 PASS** |
| Existing environment publication | **2/2 PASS** |
| R5.47 security/successor tests | **22/22 PASS** |
| Independent matrix/coherence | **16 profiles / 84 rows**, deterministic canonical match |
| Structural schema / traceability | PASS; **99 fields**, authority-linked |
| Profile/implementation contamination | PASS; no findings, existing nine-file implementation scan |
| Validation / safety | PASS / PASS |
| Historical / prospective locks | **678/678 / 695/695 PASS**, identity and ancestry valid |
| Historical R5.43 infrastructure | Immutable identity valid; **730/731** live match retained and explained |
| New R5.47 successor | **1,065/1,065 PASS**, independent reproduction and mutation rejection |
| Frozen authority | Byte hashes verified; oracle not executed |
| `git diff --check` | PASS; final documentation/accounting recheck recorded separately |

Evidence: `R5_47-starting-boundary.json`, `R5_47-regression-*.json`,
`R5_47-repository-scan.json`, `R5_47-infrastructure-lock-v2.json`,
`R5_47-qualification.json`, `R5_47-final-integrity.json` and draft disposition.
Full restricted harness took 128.448 seconds; it used a 240-second supervisory
limit. No interruption or timeout receipt was treated as PASS.

## Q: prototype treatment and final boundary

R5.46's execution-state implementation/tests are retained as **explicitly unqualified
research material**, locked for preservation. Its qualification runner was not resumed;
its 49 identity tests were not run in R5.47. Byte inclusion is not production promotion.
No prototype reversion, receipt reuse or production certificate was issued.

**Zero B02 reservations, dispatches, static evaluations, CheckedPlans, readiness,
audits, admissions, generation, execution or frozen acceptance.** All prohibitions
and restricted-harness skips remain active. Core semantics **30**; B03 prospectively
untouched; B17 unexposed/unclassified; Phase 5C paused.

Primary classification: **`R5_47_SECURITY_RECONCILIATION_QUALIFIED`**.
Recommend separately authorized **R5.48 fresh execution-state and dependency-identity
qualification** against the new successor, including secret-safe publication,
material-secret key custody, resolved runtime/native/import/Git/tool closure,
effective descendant environment and immutable-capsule/TOCTOU ownership. Preserve
all historical halts. R5.48 and any B02 exposure have not begun.
