# R5.68 — Production sealed-certificate promotion qualification

## Result

**`R5_68_PRODUCTION_SEALED_CERTIFICATE_QUALIFIED`**.

The explicitly authorized production-sealed certificate mechanism binds a real,
fresh qualification identity and actual sealed authority without opening protected
B02 resources. **213/213 fresh focused tests pass**, with a separate-process
structural/linkage audit. Actual B02 read attempts/content reads remain **0/0**;
exposure/reservation/dispatch/completion remain **0/0/0/0**. Core semantics remain **30**.

This qualifies certificate promotion mechanics. The bounded candidate uses four
non-B02 receipts and a narrow actual capsule, not a complete production regression
qualification. The complete production environment and B02 observation gate remain
unqualified. Phase 5C remains paused. Stop after R5.68.

## Inherited gap and historical preservation

R5.67 remains permanently **`R5_67_PRODUCTION_CERTIFICATE_GAP`**. Its 186-stage
plan is not resumed and no R5.67 certificate is issued retrospectively. Its exact
R5.66 prefix rejection and `SYNTHETIC_ONLY` scope retain their original meaning.

The unchanged R5.66 synthetic adapter and all its evidence remain historical.
R5.68 adds `certificate_r5_68.py` as an explicitly versioned **CertificateV3**
successor rather than silently altering CertificateV2. [Historical preservation](R5_68-evidence/historical-preservation.json)
verifies **2,154 pre-existing unsealed result files by physical bytes** and **four
protected result files by size/mtime metadata only**, including all R5.67 evidence.
The [independent audit](R5_68-evidence/independent-audit.json) confirms the stopped
classification and absent retrospective certificate.

## Mode model and explicit authorization

The versioned [contract](../../../docs/certificate-modes-r5.68.md) defines:

| Mode | Meaning | Certificate operation |
| --- | --- | --- |
| `SYNTHETIC_QUALIFICATION` | Synthetic qualification, preserving historical scope | `SYNTHETIC_GATE_QUALIFIED` |
| `PRODUCTION_SEALED` | Declared production gate qualified while benchmark remains sealed | `PRODUCTION_GATE_QUALIFIED` |

Synthetic opening remains possible only through the separate unchanged R5.66
synthetic grant and one-time ledger. Production-sealed issuance grants neither
synthetic nor actual B02 opening authority. No mode is inferred from names.

The [production declaration](R5_68-evidence/production-declaration.json) is canonical,
content-pinned and validated by a [producer-owned immutable schema](R5_68-evidence/declaration-schema.json).
It binds experiment, qualification, mode, scope, authority, QualifiedAuthority,
sealed-resource policy, capsule, complete certificate policy, allowed operation,
zero observation state and an explicit opening prohibition. The declaration digest
is separately fixed in the reviewed qualification control plane before issuance.
It is not read from a self-appointed payload identity. Mutation of any field
invalidates eligibility; even repinning cannot relax the fixed no-open policy.

```text
Experiment:        R5.68-production-sealed-certificate-promotion-v1
Qualification:     3dfdc5c477cddde7a8b39c1398d3e2f5b8a893b0775563d5e4115b13d96bb2ff
Declaration pin:   1e3a26664e6d9082ee9c8f7766dd86df2354c986928bdd30c48dcbe84b3e75e2
Schema pin:        f3648f3ce5bb2e8ff4f105dd0af82db096b77de33ad2e78d5586ff02fd10ea17
QualifiedAuthority:664b33dfb8a61e1fa5e3f6d4e7b71a7dca3145c34621043630f052a415e8ba82
Resource policy:   956b52da83032ec1ef82d6a0077034c4f01d2f82e72be2cc3c1e29915ea5ba22
Tier-2 capsule:    79badd0e73ab8874af7d89afad819708b6745f6f183ed6eca0d2745f444e66a2
```

## Actual commitments and frozen pins

Fresh [inventory](R5_68-evidence/sealed-inventory.json), [policy](R5_68-evidence/sealed-policy.json)
and [QualifiedAuthority](R5_68-evidence/sealed-authority.json) use the unchanged
R5.66 no-read path. All **11 actual sealed resources** bind prior R5.53/R5.55
commitments/provenance and historical/current immutable Git mappings. The **two
frozen pins** match the independently inherited commitments.

Only Git tree/object metadata is requested. No Git blob content extraction or
protected worktree read occurs. Every sealed row records `SEALED_COMMITMENT_VERIFIED`,
`CLOSED`, `DEFERRED_UNTIL_OPEN`, and `current_content_read = false`. This attests the
historically qualified immutable source; it does not attest present protected
worktree bytes. The candidate's authority is explicitly the 11-member sealed subset,
not the complete 1,083-member production authority.

## Candidate and reproduction

The [certificate candidate](R5_68-evidence/certificate-candidate.json) uses protocol
`lykoi-production-certificate-v3`, version 3 and `mode = PRODUCTION_SEALED`.
It binds the canonical owner declaration and schema, fresh qualification, actual
QualifiedAuthority, all sealed verification rows, two frozen pins, [Tier-2 capsule](R5_68-evidence/capsule.json),
[certificate policy](R5_68-evidence/certificate-policy.json) and [four fresh non-B02 receipts](R5_68-evidence/non-b02-receipts.json).

The actual capsule captures explicit safe subject/compiler/schema/profile and
evaluator inputs plus the sealed authority metadata. It uses ordinary declared
Python/OS infrastructure and excludes AI authoring state. It is intentionally
narrow for mechanism qualification. The [dedicated cooperative workspace](R5_68-evidence/workspace.json)
contains exactly 11 opaque closed references, no protected paths/materialization
and no Git database. Its identity is linked through the workspace receipt.

Canonical serialization, canonical reload, unchanged fresh capsule, deterministic
reassembly, receipt linkage, authority linkage, sealed commitments, capsule linkage,
mode and authorization all pass. The independent audit separately checks each
binding, every closed sealed row and workspace membership, then revalidates the
candidate. No historical receipt is promoted into the candidate.

## Mode-confusion and prefix-independence tests

The new [mode suite](R5_68-evidence/test_certificate_modes_r5_68.json) passes **28/28**:

- synthetic mode preserved; explicit production-sealed mode eligible;
- arbitrary production-looking identity and absent authorization rejected;
- every declaration field mutation rejected under its original pin;
- sealed mode and authorization mutations rejected, including after rehashing;
- synthetic certificate presented as production rejected;
- production certificate presented as synthetic qualification/opening rejected;
- production certificate passed as synthetic opening grant rejected before read/reservation;
- actual B02 opening operation rejected at the certificate operation boundary,
  without invoking an actual opener or protected-resource access;
- actual 11 commitments and two frozen pins verified through no-read metadata;
- canonical round trip and deterministic reproduction;
- authority, capsule and receipt mutation rejection;
- production identity containing `synthetic:` accepted only with an explicit
  production declaration; synthetic identity without that prefix accepted only
  with explicit synthetic authorization;
- misleading production/B02/opening names confer no additional operation authority;
- cross-mode declaration use rejected in both directions;
- issuance preserves the absent ledger and zero observation accounting;
- credential/fixture publication rejected; public declaration schema passes;
- historical V2 synthetic interpretation preserved and not promoted into V3;
- payload-chosen pin, altered schema and repinned opening permission rejected.

All denied actual-B02 tests concern the certificate operation class. They do not
test by attempting a protected file open. Synthetic tests use isolated disposable
fixtures. The R5.66 suite additionally preserves its historical synthetic-only
opening/replay behavior; those unit fixture openings are not B02 or production
observations.

## Future boundary and one-time ledger

Definition only:

```text
fresh ProductionCertificateV3(PRODUCTION_SEALED)
  + separately authorized one-time B02 observation declaration
  -> eligible for a future B02 seal-open reservation gate
```

Neither object alone is sufficient. The future separately qualified gate must bind
the exact certificate, qualification, authority, resource commitment, operation and
durable one-time ledger, with fresh state and reserve-before-read. R5.68 creates no
actual observation authorization and implements no actual B02 opener or reservation.

`PRODUCTION_GATE_QUALIFIED` is separate from `B02_SEAL_OPEN_AUTHORIZED`.
The candidate explicitly says `seal_open_authorized = false` and
`b02_observation_authorized = false`. Issuance has no ledger or observation API.
Opening reservations/consumptions remain **0/0**, actual seal openings **0**,
and B02 observation count **0**. The separate R5.66 ledger is unchanged.

## Focused verification

| Suite | Pass / run |
| --- | --- |
| Certificate modes R5.68 | 28 / 28 |
| Sealed authority / QualifiedAuthority linkage / no-read CertificateV2 R5.66 | 31 / 31 |
| Protected-resource guard R5.61 | 30 / 30 |
| Mediated child linkage R5.62 | 47 / 47 |
| Continuity R5.59 | 8 / 8 |
| Publication R5.59 | 9 / 9 |
| Protocol authorization publication R5.64 | 19 / 19 |
| Security/publication R5.47 | 22 / 22 |
| AI independence R5.49 | 5 / 5 |
| Generic optional support/schema R5.41 | 14 / 14 |
| **Total** | **213 / 213** |

The historical `test_certificate_r5_55` fixture materializes/reads the complete
authority including protected resources, so CertificateV2/QualifiedAuthority
verification uses R5.66's safe explicit linkage witnesses. No broad harness
discovery or full production plan runs.

[Schema/traceability/contamination](R5_68-evidence/schema-traceability-contamination.json)
passes with **99 traced leaves**, valid structure and empty contamination findings.
Model validation, safety and `git diff --check` pass in [command evidence](R5_68-evidence/commands.json).
AI/provider/model identity remains outside certificate mode and core semantics.

Commands executed from the repository root:

```powershell
python -B -m unittest benchmark.evaluation.test_certificate_modes_r5_68 -v
python -B benchmark/results/phase5c/r5_68_qualification.py prepare
python -B benchmark/results/phase5c/r5_68_qualification.py qualify
python -B benchmark/results/phase5c/r5_68_independent_audit.py
python -B benchmark/results/phase5c/r5_68_qualification.py final
```

The first command is the separate 28-test development check. The qualification
invocation freshly executes the 213-test focused selection; no test result is reused
as a production stage. Prepare freezes the public declaration before its digest is
independently selected in the control plane and consumed by qualify.

## Security, publication and accounting

The first final publication scan rejected a literal credential-field assignment
in a negative test's source. The [development rejection](R5_68-evidence/publication-development-failure.json)
is retained with redacted diagnostics. The test now obtains the already content-pinned
synthetic-security fixture dynamically, as the existing R5.66 test does; no publication
guard is relaxed. The entire corrected mode suite freshly passes **28/28** under the
protected-read hook in [final mode-source verification](R5_68-evidence/final-mode-source-verification.json).
The candidate/evaluator bindings are unchanged. This additional focused rerun is
separate from the 213-test qualification denominator.

[Publication integrity](R5_68-evidence/publication-integrity.json): **PASS**. Existing
guards scan all new source/evidence and updated prose; JSON evidence is canonical;
new-file whitespace and tracked `git diff --check` pass. No raw credentials,
protected B02 content or opened synthetic fixture content is published. Protocol
authorization metadata remains public/schema-bound and rejection diagnostics are
redacted. The qualification and audit processes install protected-file open hooks;
actual metadata verification uses no content APIs.

| Boundary | Final state |
| --- | --- |
| Actual B02 read attempts / content reads | **0 / 0** |
| B02 exposure / reservation / dispatch / completion | **0 / 0 / 0 / 0** |
| Actual B02 opening grants / openings | **0 / 0** |
| Opening-ledger reservations / consumptions by issuance | **0 / 0** |
| Production-sealed mechanism certificate candidates | **1** |
| Candidate non-B02 receipts | **4** |
| Complete production batches / receipts / certificates | **0 / 0 / 0** |
| Synthetic production observation reservation / dispatch / completion | **0 / 0 / 0** |
| Actual future observation authorizations created | **0** |
| Historical R5.67 resume / retrospective certificate | **No / none** |
| Core semantics | **30** |
| Phase 5C | **Paused** |

## Recommendation and stop

Recommend a **wholly fresh, separately authorized complete production qualification**
that pins CertificateV3, its explicit production declaration/schema, sealed authority,
safe materialization and all required fresh production regressions/receipts. Its full
authority/capsule/workspace and observation-control integration must be qualified
before any separately authorized B02 experiment. R5.68 does not begin that run or
authorize B02 readiness, audit, admission, reservation, dispatch, generation,
execution or acceptance.

**STOP: `R5_68_PRODUCTION_SEALED_CERTIFICATE_QUALIFIED`.**
