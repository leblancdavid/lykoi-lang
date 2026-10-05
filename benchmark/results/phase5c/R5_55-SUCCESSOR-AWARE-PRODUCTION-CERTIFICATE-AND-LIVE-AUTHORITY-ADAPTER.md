# R5.55 — Successor-aware production certificate and live-authority adapter

## Outcome and scope

**Successor-aware certificate mechanics independently qualify.** QualifiedAuthority
v1 and ProductionCertificateV2 consume the existing qualified R5.53 authority via
an externally pinned experiment authorization. Fresh synthetic assembly, canonical
reload/validation, deterministic reproduction and live mutation rejection pass.

R5.55 stops at certificate qualification. Full production Tier-2 qualification is
not performed. There are **zero production reservations, dispatches or completions**.
B02 reservation, dispatch, CheckedPlans, readiness, audit, admission, static
evaluation, generation, execution and frozen acceptance remain completely sealed.
Core semantics remain **30**; Phase 5C remains **paused**.

Initial `git status --short` was clean. Changes are prospective certificate/authority
integration, independent tests, evidence drivers and documentation. No semantics,
compiler, profile, behavioral contract, R5.53 manifest, historical lock or R5.50
methodology is changed. No new authority successor is created.

## Inherited failure and exact cause

R5.54 remains `R5_54_PRODUCTION_CERTIFICATE_GAP`: authority 1,083 members,
representation 56 exact / 1,027 LF/CRLF, deterministic capsule and dedicated copy
passed; certificate admission failed and 24 downstream entries remain INCOMPLETE.
The R5.51 production certificate at `tier2_r5_51.py:210-240` fixes infrastructure
identity to R5.47's `31339cb73996c9ee728656558477436d9a5ba1cfbd0272c771720e6a1f6bf084`.
It also requires exactly historical/prospective/infrastructure physical locks,
with infrastructure equal to that pin. R5.54 preserves both rejection diagnostics.

V1 retains its historical meaning. The prospective V2 consumes qualified authority
instead of declaring historical physical locks PASS. The generic V2 implementation
contains neither an R5.47-only nor an R5.53-only identity admission branch.

## Authority design, current binding and compatibility adapter

See [the versioned interface](../../../docs/qualified-authority-certificate-r5.55.md).
`qualified_authority_r5_55.py` defines `lykoi-qualified-authority-v1`; its
authorization policy is `lykoi-qualified-authority-authorization-v1`. Selection
belongs to independently pinned experiment policy, not certificate schema or
newest-manifest discovery. Current selection:

- Manifest: `R5_53-authority-successor-v1.json`.
- Authority: `5dd2e7e645c1736f23a80bff755d347da5688cc9e8b7f7df515bd7110d1534ea`.
- Authorization policy: `31d4b3632cfcdbf1e928ddf3cbeaf2b88fad97e50ba502b78cf1434d09a114b8`.
- Qualified interface: `202d16698a5d67e0ad7adf86c98c1d1d2805bf6abc0a42614518dd403757df6c`.
- Synthetic V2 certificate: `2997363f0bc4f2e4c873b94ea9d17a57fd6362c784ea65cf81a82793c437bfbe`.

The interface binds authority schema/identity, raw manifest identity, member
integrity, qualification and independent audit, independently frozen pins,
provenance/decision, predecessors, historical evidence, checkout policy/receipt,
effective attributes/EOL controls and qualification status. It interprets the
R5.53 protocol structurally without content-path exceptions. Compatible genuinely
qualified future successors need a new explicit authorization policy, not a
certificate schema redesign. Unsupported authority protocols fail closed.

The owner must provide the policy digest from trusted authorization, not compute
an expected digest from untrusted input. R5.55 constructs its policy from the
explicit user-authorized current selection and preserved evidence, then pins it
before qualification. Canonical shape, a self-seal, qualification status or a
newer Git commit alone is insufficient. Certificate assembly itself freshly
qualifies supplied authority; validation repeats qualification and current-state
comparison. An arbitrary fabricated interface cannot bypass the adapter.

## Historical preservation, frozen authority and ancestry

Original historical physical-lock FAILs retain their original recorded counts:
R5.40 **145/678**, R5.41 **145/695**, R5.47 **145/1,065**. The R5.47 predecessor
relationship remains exact manifest evidence plus legitimate ancestry. R5.51 failed
qualification, R5.52 reconciliation and R5.53 successor provenance remain pinned.
Historical outcome/reconciliation bytes are explicit authorization inputs; their
erasure or mutation rejects. No old result is converted to a current PASS.

Qualification verifies predecessor raw hashes/status, predecessor HEAD ancestry
to successor HEAD, successor ancestry to experiment HEAD, reconciliation/decision
identity and every Git/change-record/decision provenance link. Current members
must match scoped repository content/blob/mode and authorized additions. An
unrelated manifest, broken predecessor link, missing/altered provenance or
unqualified newer manifest rejects. Predecessor member physical bytes are not
required to equal current checkout bytes.

The four frozen behavioral pins are bound independently of ordinary infrastructure
selection and preserved unchanged in interface/certificate. A policy with changed
frozen pins rejects even when its own policy digest is explicitly recomputed;
physical frozen member mutation also rejects. Frozen B02 bytes are hashed only,
never parsed or evaluated as a benchmark subject. Infrastructure succession does
not authorize behavioral-contract succession.

## Checkout representation and experiment snapshot

Fresh authority qualification verifies all **1,083** members against exact
repository authority and separately recorded representation. Original relationships
remain **56 EXACT / 1,027 LF_CRLF_REPRESENTATION**. Only declared UTF-8 LF text may
use proven CRLF-pair expansion; binary/material inputs require exact bytes. Bare
CR, encoding/filter transformations and unexplained mutations reject. Effective
attributes and EOL controls are recorded. Physical capsule bytes remain exact.

Fresh qualification uses a **2,031-file** dedicated cooperative snapshot at
`C:\Users\lblan\AppData\Local\Temp\opencode\r555-qualified-certificate-workspace`.
Authoring inputs/caches are excluded and copying preserves physical bytes/index
provenance. Evidence stays outside its consumed roots. New report/overview prose
does not rewrite the authority baseline: the governed snapshot remains pinned.
Changed pinned members in another checkout must fail, not receive an implicit
documentation exception. R5.56 must explicitly instantiate its governed inputs.

## Certificate schema and synthetic qualification

`certificate_r5_55.py` defines `lykoi-production-certificate-v2`, explicit version
**2**. It binds QualifiedAuthority identity and policy, independent frozen pins,
Tier-2 capsule identity, every required receipt, recorder/canonical protocol,
semantic count, contamination and observation state. The minimum synthetic
receipts establish actual identity/core count, freshly qualified authority, scoped
contamination and dedicated workspace. More required stages can be specified;
all must be present, successful, and match experiment/capsule/stage/mechanism.

The recorded independent synthetic sequence in `R5_55-qualified-evidence/`:

1. Pin explicit authority authorization before verification.
2. Freshly verify qualified R5.53 authority and separate representation.
3. Capture a fresh bounded Tier-2 capsule repeatedly; obtain same-state focused
   identity/authority/contamination/workspace receipts.
4. Assemble and guarded-publish the V2 certificate, capsule, policy and receipts.
5. Canonically reload and validate against freshly requalified live authority.
6. Reassemble deterministically and compare exact canonical identities.
7. Mutate a disposable authority member; validation rejects.
8. Restore synthetic state; recapture equality and fresh validation pass.
9. Independently audit raw content/canonical identities/receipt linkage and final
   preservation without using the certificate constructor or authority verifier.

`synthetic-qualification.json` records PASS. This certificate establishes the
specified minimum synthetic evidence, not completion of the full production
regression/observation protocol. Neither new module dispatches an observation.
V1 StaticGate remains version-specific; no full V2 live gate is claimed here.

## Independent adversarial tests

`test_certificate_r5_55.py` freshly passes **33/33**:

- Canonical interface identity and qualified current R5.53 acceptance.
- Superseded R5.47-as-current and arbitrary manifest rejection.
- Member and identity mutation rejection, including resealed manifest mutations.
- Independently changed frozen pins and physical frozen member rejection.
- Broken predecessor link, missing/altered provenance, wrong checkout policy.
- Historical-evidence mutation/erasure and unqualified newer successor rejection.
- Deterministic V2 assembly and canonical round trip; valid authority/capsule.
- Wrong authority, stale capsule, mixed receipts and semantic-count mismatch.
- Contamination, incomplete and missing receipt rejection.
- Authority mutation after certificate; zero-state enforcement.
- AI authoring independence, authoring metadata and untrusted policy rejection.
- Secret-safe publication and no file creation for rejected credential fields.
- Exact binary/material treatment and permitted LF/CRLF relationship.

The fixture explicitly reconstructs only evolving research prose for a governed
baseline fixture; it does not normalize historical physical evidence. Fresh live
snapshot qualification is separate from those independent fixture tests.

## Fresh regression results

All results are newly persisted `*-worker.json` records, not reused historical
PASS receipts. Commands use the existing CPython **3.12.10** image with `-B`;
suite workers withhold raw test diagnostics and preserve test IDs/status/counts.

| Check | Fresh result |
| --- | ---: |
| Successor-aware authority/certificate tests | 33/33 PASS |
| R5.53 authority focused mechanisms | 18/18 PASS |
| R5.41 independent support mechanisms | 14/14 PASS |
| R5.51 Tier-2 capsule/certificate mechanisms | 43/43 PASS |
| R5.45 staged certificate mechanisms | 33/33 PASS |
| R5.43 recorder/canonical evidence | 29/29 PASS |
| R5.47 full security | 20 PASS / 2 preserved historical FAIL |
| R5.50 methodology | 18/18 PASS |
| AI independence, including Git-independent core probe | 5/5 PASS |
| Application/compiler | 31/31 PASS |
| Generic schema / traceability / coherence | PASS: 99 leaves, 16 profiles / 84 rows |
| Scoped contamination / core count | PASS: clean / 30 |
| Model validation / safety / diff check | PASS |
| Fresh successor snapshot / synthetic V2 / independent final audit | PASS |

Final focused suite aggregate: **246 discovered / 244 pass / 2 historical failures**.
The preserved security failures are `test_historical_lock_unchanged` and
`test_ignore_effective_behavior`, the previously diagnosed physical-representation
and negated-ignore-rule assertions. They are not relabeled PASS. All 20 current
publication/security witnesses pass. Full restricted harness observations remain
inherited (active 338/36/55; LF 393/36/0); no new full harness claim is made.

## Development diagnostics, independence and security

Before the recorded fresh snapshot, a development authority assembly rejected
the field name `authorization` under the existing secret-field guard. A read-only
diagnostic identified that boundary. The public digest field is now `policy_binding`;
the security guard is unchanged. An initial independent-test setup also failed
because it restored historical physical evidence to repository text. The fixture
was corrected to restore only evolving research prose; 30 tests passed before
three additional witnesses yielded the final 33/33. Earlier evidence/workspace is
preserved and never reused to claim successful qualification. These are mechanism
development corrections before fresh independent qualification, not resumption
of R5.54 or a production observation. `development-disposition.json` records them.
The independent auditor's first launch also rejected an external policy pin by
mistaking it for a self-sealed envelope. Its typed interpretation was corrected
before the final audit; the final audit records that development correction.

Lykoi remains a language, not an AI runtime. No credential/model/OpenCode state or
prompt history enters authority/certificate metadata. Independent changes outside
consumed authoring roots preserve capsule and certificate validation. Git is used
for content provenance/ancestry only; a commit alone cannot qualify authority,
and core language operations remain Git-independent.

All structured publication uses the unchanged R5.47 guard, including capsule,
interface, certificate, receipts, regression records and final audit. Raw credential
fields reject before file creation; no raw worker logs, ambient dumps or credential
identities are published. Trust remains cooperative/local, not signature-backed
hostile-host or malicious ABA attestation. R5.50 methodology is unchanged.

## Final integrity, accounting and next round

`final-integrity.json` and `independent-final-audit.json` preserve **1,728**
pre-existing benchmark-result files, including R5.51/R5.52/R5.53/R5.54 evidence and
the development initialization records. The auditor independently hashes all 1,083
authority members and current captured physical files, frozen pins, predecessor
manifests/ancestry, qualification/audit and historical evidence, canonical interface/
capsule/certificate/receipts and final prose identities. `git diff --check` passes.

Production accounting: **0 reservations / 0 dispatches / 0 completions**. Synthetic
unit-test lifecycle observations remain fixture-only mechanism tests; no production
or B02 observation follows. B02 exposure **zero**; core semantics **30**; Phase 5C
**paused**. Historical failures and inherited harness observations are preserved.

Recommend separately authorized **R5.56 fresh complete production Tier-2
qualification** against the qualified current authority, with its full explicit
receipt policy, fresh dedicated inputs and separately verified live observation
integration. R5.55 stops here; the stopped R5.54 candidate is not repaired/resumed.
No B02 authorization follows from this certificate-mechanism qualification.

Final primary classification:

**`R5_55_SUCCESSOR_AWARE_CERTIFICATE_QUALIFIED`**
