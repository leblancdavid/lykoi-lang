# R5.66 — Sealed authority verification and deferred materialization qualification

## Result

**`R5_66_SEALED_AUTHORITY_QUALIFIED`** within the prospective authority/infrastructure
boundary. **B02 remains unopened, 0/0/0/0; core semantics remain 30; Phase 5C paused.**

The generic adapter qualifies ordinary members by current reads and sealed members
by trusted historical commitments and immutable-object mapping. Canonical evidence
distinguishes the modes. Deferred workspaces copy ordinary inputs and provide opaque
references for sealed inputs. Synthetic-only opening and CertificateV2 adapters pass
focused qualification. No full production authority, production workspace, production
certificate, batch, receipt or observation is qualified or issued here.

## Inherited gap and historical preservation

R5.65 remains permanently **`R5_65_QUALIFIED_AUTHORITY_GAP`**. Its fresh 178-stage
plan and qualification identity completed freeze/seal/persistence/schema validation/
canonical reload, then stopped before invoking QualifiedAuthority or materialization.
Both mandatory read sets contained 11 sealed B02 resources, including two frozen pins.
Its downstream production qualification remains NOT_RUN. Its plan is not resumed,
and its old authority call is not retrospectively invoked.

This round preserves **2,103 pre-existing unsealed result files by physical bytes**
and **four protected result files by size/mtime metadata only**. Frozen compiler,
runtime, schema, requirements, oracle, historical mechanisms and old classifications
are preserved. Changes introduce separately versioned adapters and evidence.
See [historical preservation](R5_66-evidence/historical-preservation.json) and
[independent audit](R5_66-evidence/independent-audit.json).

## Safe sealed-resource inventory

The complete [canonical inventory](R5_66-evidence/sealed-inventory.json) contains
all 11 original authority members, with their already-permitted path linkage, opaque
ID, sealed class, authority role, SHA-256 commitment, Git object identity, provenance,
frozen status and safely inherited representation kind. Inventory construction reads
safe manifests and qualification records, not protected files or Git blob contents.

| Opaque resource identity | Sealed authority role | Frozen pin |
| --- | --- | --- |
| `frozen-request` | Authority | Yes |
| `frozen-profile` | Contract | Yes |
| `frozen-capabilities` | Contract | No |
| `semantic-fixture-r537` | Fixture | No |
| `semantic-fixture-r540` | Fixture | No |
| `profile-fixture-r540` | Fixture | No |
| `obligation-fixture-r540` | Contract | No |
| `sealed-test-module-0` | Contract | No |
| `sealed-test-module-1` | Contract | No |
| `sealed-test-module-2` | Contract | No |
| `sealed-test-module-3` | Contract | No |

Protected module bytecode designations remain protected by R5.61/R5.62. They are not
additional members of the historical 1,083-member authority, and no caches are copied.

## Trusted commitments and provenance

Externally inherited trust roots:

```text
R5.55 authorization: 31d4b3632cfcdbf1e928ddf3cbeaf2b88fad97e50ba502b78cf1434d09a114b8
R5.53 successor:     5dd2e7e645c1736f23a80bff755d347da5688cc9e8b7f7df515bd7110d1534ea
```

The pinned authorization binds the manifest, historical qualification and independent
audit. The manifest's canonical identity, qualification identity, audit baseline/PASS
and member-integrity/ancestry/reproduction flags are checked. Each sealed member's
SHA-256 and Git object identity come from that **pre-existing qualified manifest**.
No first commitment is created from protected bytes during R5.66.

Chain: historical frozen/member authority → previously qualified manifest commitment
and object identity → pinned successor qualification and audit → current opaque member.
Historical and current committed tree entries must agree on path, regular-file mode
and object identity. `git cat-file --batch-check` checks object existence/type without
extracting content. The two frozen SHA-256 pins additionally match the independent
authorization's frozen-authority mapping.

The sealed source is the **historically qualified immutable Git object**, not the
current protected worktree file. This establishes commitment/provenance continuity,
not fresh byte verification of either the object payload or worktree. Object-store
integrity is the existing cooperative content-addressed research-infrastructure trust
boundary; opened bytes must still pass the SHA-256 commitment before acceptance.
Current protected worktree bytes are neither attested nor used as fallback sources.
This does not claim hostile-host or arbitrary object-store-corruption resistance
without reading contents. Missing/substituted object mappings reject; synthetic
mismatched payloads reject at opening.

Git remains research infrastructure. Ordinary Lykoi program execution gains no Git
dependency. The existing continuity adapter handles safe ordinary metadata; no new
LF/CRLF methodology is introduced. Sealed checkout observation is explicitly
`DEFERRED_UNTIL_OPEN`.

## QualifiedAuthority and explicit evidence

[`sealed_authority_r5_66.Authority`](../../evaluation/sealed_authority_r5_66.py)
is a prospective versioned QualifiedAuthority adapter accepting arbitrary ordinary
and sealed members under an externally pinned policy. It is not a path exception for
the 11 B02 members. Policies bind resource IDs, classes, commitments, provenance,
membership and independent frozen pins; policy mutation invalidates qualification.

- Ordinary: approved ordinary reader → commitment/representation verification →
  `BYTE_VERIFIED_FROM_CURRENT_READ`, with physical checkout digest.
- Sealed: reviewed metadata observer → immutable mapping/commitment/provenance
  verification → `SEALED_COMMITMENT_VERIFIED`, `seal=CLOSED`,
  `current_content_read=false`, checkout deferred.

The ordinary reader rejects a sealed member **before** any content API. Downgrading
its class without matching the externally pinned policy also rejects before reading.
Sealed members are included in the authority identity; none is silently omitted or
reported as byte-verified. Frozen pins remain explicitly visible.

[Real sealed-authority evidence](R5_66-evidence/sealed-authority.json) freshly checks
**all 11 sealed members only**. It does not claim a complete fresh 1,083-member
production qualification. The derived policy records its historical trust root and
scope in [derived-sealed-policy.json](R5_66-evidence/derived-sealed-policy.json).

## No-read enforcement and tamper qualification

Fresh synthetic tests cover correct, missing, replaced and wrongly mapped resources,
altered commitments, broken provenance, frozen pins and post-issuance mutation.
Read spies prove the sealed path never reaches `Path.read_bytes`; direct ordinary
routing rejects with the reader instrumented to fail on any invocation. A metadata
inventory test additionally instruments protected-path reads and Git blob extraction.

The qualification and independent-audit processes install a separate audit hook
denying actual repository protected-path opens. Any such attempt requires
`R5_66_PROTOCOL_HALT` and quarantine. There are **zero actual protected-path attempts,
zero actual content reads and no quarantine event**. Denial witnesses target synthetic
resources. Mediated subprocesses retain R5.62's child/descendant registry and guard.

## Deferred cooperative workspace and placeholder format

The prospective materializer consumes a pinned declared input inventory. It verifies
authority before and after copying, copies ordinary bytes, verifies ordinary drift,
and leaves every protected original path absent. Opaque references live under
`.sealed/<opaque-ID-digest>.json`. **No `.git` database, shared-object alternate,
protected content file or bytecode is copied**, so the workspace offers no Git-based
resolution bypass. Safe metadata examples exist for all 11 real resources; actual
workspace materialization is exercised only with synthetic inputs.

Closed placeholder allowlist:

```json
{"protocol":"lykoi-sealed-reference-v1","resource":"synthetic:alpha","commitment":"<SHA-256>","seal":"CLOSED","qualified_authority":"<identity>"}
```

No contract text, fixture bytes, decoded behavioral information, source path, storage
locator or automatic resolver appears in the placeholder. Its identity/commitment
metadata is already permitted; metadata does not supply an opening capability.

`worker_resolve` uses the R5.61 authoritative resource registry/read boundary.
Ordinary-worker resolution rejects before content and records denial/quarantine
evidence. A fresh real mediated-child witness independently tries synthetic source
resolution and produces `SECURITY_FAILURE`/INCOMPLETE with quarantine. Reading safe
placeholder metadata is not resolving its protected source.

## Synthetic seal-open lifecycle and future binding

`SEALED_RESOURCE_OPEN` is separate from generic qualification capabilities. R5.61
generic authorization rejects it. **No real-resource opener or B02 grant exists in
this adapter.** The executable opening prototype accepts only `SyntheticStore`
fixtures and externally pinned `SYNTHETIC_ONLY` grants.

Grant binding includes exact qualified authority, resource, precommitment, one-time
status and the durable ledger identity. Before reading, mapping and grant must match;
an exclusive, flushed/fsynced reservation permanently consumes the opening. Opened
synthetic bytes are accepted/returned only after commitment and unchanged-authority
checks. A failed payload comparison consumes the reservation and records REJECTED.
Second opening and alternate-ledger replay reject before another content read.

The final [synthetic lifecycle](R5_66-evidence/synthetic-lifecycle-final-mechanism.json)
qualifies sealed authority without reading, materializes a placeholder, binds a
separate synthetic grant, opens **exactly once**, verifies the precommitment and rejects
the second opening. Fresh tests separately prove ordinary-worker/unauthorized-open
denial and A→B substitution rejection before acceptance (and before reading when the
mapping differs). No opened fixture bytes are published.

Future design, **not executed or authorized here**: a separately authorized protected
opening must select the exact precommitted immutable resource, bind authority and
one durable observation ledger, verify opened bytes before exposing them to the
observation consumer, and feed exactly one locked observation. It must not fall back
to a worktree substitute. Opening and locked observation authorization must be explicit;
ordinary authority/certificate capabilities cannot imply either.

## ProductionCertificateV2 compatibility

[`certificate_r5_66`](../../evaluation/certificate_r5_66.py) retains CertificateV2's
required stage/receipt/capsule/semantics/contamination/workspace linkage checks while
binding the prospective authority interface and its full verification-mode evidence.
It freshly requalifies authority at assembly/validation, rejecting commitment,
provenance or mapping mutation after issuance. Both ordinary and sealed evidence
remain visible in canonical certificate data.

Issuance is explicitly synthetic-only. The
[synthetic certificate record](R5_66-evidence/synthetic-certificate-v2-final-mechanism.json)
uses a focused synthetic capsule and receipts; it is **not a production certificate
or a complete production regression receipt set**. Historical v1 authority and v2
certificate implementations remain unchanged; future production must select and
pin the prospective adapters in its wholly fresh authorization and plan.

## Fresh focused verification

| Focused suite | Final applicable result |
| --- | ---: |
| New sealed authority, workspace, opening, CertificateV2 and no-read tests | 31/31 |
| Protected-resource guard / synthetic authority and certificate linkage | 30/30 |
| Mediated child execution / safe worker selection | 47/47 |
| Qualified ordinary continuity | 8/8 |
| Publication separation | 9/9 |
| Context-aware publication | 19/19 |
| Security | 22/22 |
| AI independence | 5/5 |
| Generic optional-support/schema foundation | 14/14 |
| **Applicable focused total** | **185/185** |

The 31-test changed-mechanism suite was rerun after the ledger-binding correction;
the other 154 checks had freshly passed in this round and their unchanged results
remain applicable. Schema/structure, **99-leaf traceability**, contamination, validation,
safety, semantic count 30, independent evidence reconciliation and whitespace pass.
Full production qualification and broad harness discovery are not run. Historical
certificate fixture setup that would read/materialize B02 is not invoked.

Publication accepts the safe commitments, provenance, placeholders, evidence and
new sources through existing guards. Credential detection and synthetic-security
fixture nonpublication remain unchanged; a fresh rejection witness confirms that
adding credential material is still denied. See publication-integrity evidence.

AI provider/model/credential state is unrelated to sealed authority. Fresh offline
AI-independence checks pass 5/5. Lykoi remains a language, not an AI runtime.

## Development history and accounting

Preserved [development observations](R5_66-evidence/development-observations.json)
record two initial metadata-loader errors, an exclusive-persistence collision with
the already-published identical inventory, the early 28-test check, and the preliminary
183-test run. Review then bound the durable ledger into the grant and added two
adversarial tests. No initial error exposed protected content or began production.
Preliminary evidence is retained; **`summary-final-mechanism.json` is the final
applicable mechanism evidence**.

The first final source-publication scan rejected an inline synthetic `api_key`
assignment in the new rejection test. The test retains that credential field and
now consumes the already-content-pinned synthetic security fixture instead of
publishing a credential-shaped source assignment. Its focused rejection witness
passes again with the precise `SecretRejected` expectation. No credential guard,
schema, fixture designation or policy is weakened; the rejected scan is recorded
in development observations. Final publication checks then pass.

There are **two independent canonical synthetic fixture demonstrations across
development and final verification**, each with one opening and a second-open
rejection. The final mechanism demonstration has exactly one opening. Independent
unit-test fixtures also open synthetic bytes; those are not benchmark reservations,
dispatches or completions. No fixture lifecycle is promoted to B02 or production.

| Final accounting | Result |
| --- | --- |
| Actual protected B02 read attempts / reads | 0 / 0 |
| B02 exposure / reservation / dispatch / completion | 0 / 0 / 0 / 0 |
| Real seal-open grants | 0 |
| Production batches / receipts / certificates | 0 / 0 / 0 |
| Final canonical synthetic demonstration openings | 1 |
| Protected paths materialized into a real cooperative workspace | 0 |
| Full production qualification | NOT_RUN |
| R5.65 retry / resume / retrospective authority call | None |
| Core semantics | 30 |
| Phase 5C | Paused |

Commands executed for this round include metadata-only inventory, the prospective
qualification driver, changed-mechanism verification, independent audit and final
publication checks. The driver records validation/safety/diff commands and individual
suite results beside evidence. No B02 contract/fixture inspection, CheckedPlan,
readiness/audit/admission, reservation/dispatch, generation/execution or acceptance
is performed.

## Recommendation and stop

Separately authorize a **wholly fresh production qualification** with a newly pinned
complete ordinary/sealed input policy, prospective authority/certificate adapters,
deferred workspace adapter, mediated workers and all required fresh production gates.
Keep R5.65 permanently stopped. That later qualification must establish complete
authority/capsule/workspace linkage and production readiness before any separately
authorized locked B02 observation. No production qualification begins here.

**STOP: `R5_66_SEALED_AUTHORITY_QUALIFIED`.**
