# R5.64 — Context-aware credential publication reconciliation

## Outcome

**`R5_64_CONTEXT_AWARE_PUBLICATION_QUALIFIED`**.

This prospectively qualifies a narrow publication/security correction using
synthetic non-B02 metadata. **124/124 focused tests pass.** A synthetic qualification
identity is constructed, sealed through the previously failing publication path,
persisted and canonically reloaded. No production qualification starts.

| Boundary | Result |
| --- | --- |
| Inherited R5.63 | Permanently `R5_63_PROTOCOL_HALT` |
| Production batches / receipts | **0 / 0** |
| Production certificate | Not issued |
| Production qualification identity | Not issued |
| Synthetic observation reservation / dispatch / completion | **0 / 0 / 0** |
| B02 exposure / reservation / dispatch / completion | **0 / 0 / 0 / 0** |
| Core semantics | **30** |
| Phase 5C | Paused |

## Inherited halt and false-positive class

R5.63's first and only freeze invocation stopped before starting-state verification
or production qualification. Its 173-stage plan and worker registry persisted;
its attempted identity did not. The retained diagnostic is:

```text
SECRET_VALUE_REJECTED: credential field field authorization
```

The false-positive class is **protocol/experiment authorization identity metadata
interpreted as authentication material solely by its field name**. R5.63 described
the intended value as a public authority-policy digest; no evidence established
that it was a credential. Its halt remains correct under its then-qualified guard
and no historical outcome is reclassified. Its source, candidate, plan, quarantine
and missing identity remain unchanged. Nothing resumes its 173-stage plan.

## Schema classification and security behavior

The [prospective policy](../../../docs/context-aware-publication-r5.64.md) defines
PUBLIC_METADATA, PROTOCOL_IDENTITY, PROTOCOL_AUTHORIZATION, CONTENT_IDENTITY,
SECRET_REFERENCE, SECRET_VALUE, CREDENTIAL_HEADER and SYNTHETIC_SECURITY_FIXTURE.
The generic mechanism stores immutable canonical schema bytes and requires a
trusted content pin on every typed publication. Exact field membership, types,
nesting and classifications are checked. Schema mutation invalidates the original
pin. Declarations are owned by reviewed producer code, never worker payloads.

Protocol authorization describes permitted experiment/process actions, public
authorization IDs, stage classes or policy versions. It is publishable only without
embedded secrets. QualificationIdentity explicitly declares its unchanged
`authorization` field PROTOCOL_AUTHORIZATION. A second independent nested process
schema demonstrates the same behavior without qualification-specific exceptions.

Credential authorization includes authentication headers, opaque credential objects,
bearer/basic values, API keys, passwords, cookies and unsafe signed credential
material. Credential classes reject raw values regardless of field spelling.
Existing safe presence/redacted/reference representations remain available.

Every public/protocol string and key still receives value inspection. Recognizable
tokens, credential assignments, private keys and credential URLs remain prohibited;
explicit marked-secret structures cannot be overridden by a public declaration.
R5.59 fixture values remain prohibited everywhere in output. Only the redundant
untyped assignment scan of *typed JSON serialization* is omitted: schema traversal
already inspected each actual key/value. Free-text assignments still reject.

Typed metadata additionally rejects HTTP authentication values (bearer/basic) even with
short opaque payloads; schema context cannot bypass protection by token length.
Unknown context retains the existing conservative fallback: a raw unclassified
authorization field rejects; an existing safe representation is allowed. Ordinary
unrelated unknown fields undergo value/marked-structure inspection. Missing/wrong
pins, extra fields and self-declared payload metadata do not establish schema trust.

The detector retains its bounded scope: it is not an entropy oracle and cannot
identify every opaque credential without declared context or a recognizable value
indicator. Producers remain responsible for reviewed classifications and must not
publish raw environment/configuration/worker dumps. No filename or value whitelist
is introduced. Rejected values never appear in diagnostics.

## Adversarial and focused verification

| Suite | Passed / discovered |
| --- | ---: |
| New R5.64 publication tests | **19 / 19** |
| R5.47 security | **22 / 22** |
| R5.59 publication and immutable fixture rules | **9 / 9** |
| R5.59 continuity | **8 / 8** |
| AI independence | **5 / 5** |
| Generic schema/support | **14 / 14** |
| R5.62 mediated child, safe workers and minimal environment | **47 / 47** |
| Total | **124 / 124** |

The new tests cover ordinary protocol authorization, a second nested protocol
schema, bearer injection, HTTP Authorization, credential objects, explicitly
classified public authorization metadata, API keys and password assignments under
innocent names, unknown-context fallback, immutable fixture input/nonpublication,
redacted diagnostics (including unsafe keys), identity publication/reload, schema
mutation, credential rename, multiple value-level bypass attempts, marked secrets,
missing pins/extra fields and fixture-class rejection.

Initial development run: **57/58 pass, one assertion failure**. The reload assertion
expected canonical bytes without the persistence format's required newline. The
assertion was corrected; production code was not changed to satisfy it. This failed
development check is retained in `R5_64-evidence/development-check.json`.
New source publication scans additionally caught literal assignment syntax in schema
and test source; values are constructed without embedding credential assignments.
Runtime field names, classes and test values are unchanged; source scans were not
exempted or weakened. The initial final new-suite rerun is **19/19**. After adding
short opaque bearer/basic adversaries, the final combined new-publication/R5.47/
R5.59 security-publication verification is **50/50**. A subsequent prose scan
conservatively flagged adjacent authentication terminology as credential-shaped
text; wording was clarified and the unchanged guard rerun. The stopped scan and
successful final scan are separately recorded.

Fresh structural schema validation, **99-leaf traceability**, the established
contamination scan (**nine files; no findings**), model validation, model safety,
and `git diff --check` pass. New-file whitespace/source and evidence publication
checks are recorded in `R5_64-evidence/publication-integrity-checked.json`.

## Exact identity freeze publication dry run

The synthetic body uses the same QualificationIdentity field structure as the
failed freeze, with independently synthetic protocol/policy strings and digests.
No R5.63 identity is reconstructed and no production policy is qualified.

```text
tier.seal(body, schema, schema_identity)
  -> security.safe_bytes (schema classification plus value inspection)
  -> unchanged envelope seal
publication.persist(identity, schema, schema_identity)
  -> guarded canonical persistence
canonical loads -> schema revalidation -> unchanged envelope unseal
```

All five required witnesses pass: constructed identity, correct authorization
classification, acceptance of safe metadata, persistence and canonical reload.
The retained `synthetic-qualification-identity.json` and `identity-dry-run.json`
provide the identity and schema pins. No batch, driver, authority qualification,
capsule, certificate or observation is initialized by the dry run.

## Security and historical preservation

R5.47 credential patterns, assignment scans, marked structures, safe references
and redacted diagnostics are preserved. R5.59's fixed content-pinned fixture
designation and publication prohibition remain intact. R5.62 minimal child
environment and mediated execution are unchanged and freshly tested.

**2,066 prior unsealed result files** remain byte-preserved; **four protected files**
remain unopened and metadata-preserved. This is not a new content-hash attestation
of protected files. R5.63 still has no qualification identity and its tracked
candidate/source/evidence have no diff. Its halt is permanent.

No B02 authority, contract, fixture, static evaluation, CheckedPlan, readiness,
audit, admission, reservation, dispatch, generation, execution or acceptance is
accessed. Resource registry/index metadata is used solely to exclude protected
contents from preservation and publication scans. All B02 accounting remains zero.

Core/compiler/profile/benchmark-authority/QualifiedAuthority/CertificateV2,
capability enforcement, mediated execution, observation controls and Tier-2
methodology remain unchanged. The only Tier-2 edit forwards optional publication
schema context through `seal`; envelope and qualification semantics do not change.

## Commands and recommendation

```text
python -B -S benchmark/results/phase5c/r5_64_publication_reconciliation.py
python -B -S benchmark/results/phase5c/r5_64_publication_reconciliation.py final
python -B -S benchmark/results/phase5c/r5_64_publication_reconciliation.py final-verified
python -B -S benchmark/results/phase5c/r5_64_publication_reconciliation.py final-checked
```

The focused runner records suite denominators, schema/traceability/contamination,
validation/safety/diff commands, synthetic identity evidence and historical
preservation. It has no production qualification entry point.

**Recommendation:** separately authorize a **wholly fresh production qualification**
that explicitly binds the corrected publication schema and implementation, uses
fresh metadata/evidence, and resolves the previously noted sealed-resource
compatibility prerequisite before any protected-content API. Neither this correction
nor its synthetic identity qualifies the complete production gate or authorizes
B02 exposure. Do not resume R5.63. **Stop after R5.64.**
