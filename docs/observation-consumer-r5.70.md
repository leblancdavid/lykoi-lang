# CertificateV3 observation-consumer contract — R5.70 v1

This is prospective research infrastructure, implemented in
`benchmark/evaluation/observation_consumer_r5_70.py`. The R5.51 module and frozen
R5.69 candidate retain their historical meanings. No language semantic is added.

## Production contract

`StaticGate.prepare()` accepts only the explicit pair
`lykoi-production-certificate-v3` / integer version `3`, in `PRODUCTION_SEALED`
mode. There is no latest-version lookup or fallback. V1, V2 and future versions
reject. Validation delegates to R5.68's qualified `require_operation`, with
`PRODUCTION_GATE_QUALIFIED`, not to the R5.51 certificate assembler.

Required inputs are the exact certificate, QualifiedAuthority, Tier-2 capsule,
complete receipt set and policy, current capture, R5.66 Authority adapter,
producer-schema declaration, externally trusted declaration digest and
qualification identity. Deterministic V3 validation rechecks authorization,
authority/resource policy, capsule, successful receipt identities, contamination,
semantic count 30, zero certificate observation state and the closed/no-open
policy. Fresh contamination and ownership checks also run. Unknown versions fail
before staging or reservation. Mutations cannot be accepted by merely resealing.

Historical interpretation uses the historical validators explicitly. New production
preparation never promotes a historical certificate into current authority and
never reconstructs an R5.51 certificate from V3.

`prepare_synthetic()` is a separately named entry point requiring the explicit
synthetic mode and synthetic immutable sealed-resource designations. A synthetic
certificate, even with a synthetic-mode consumer configured, cannot enter
production `prepare()`.

## Sealed resources and execution

The already-qualified R5.66 authority adapter distinguishes ordinary current byte
verification from `SEALED_COMMITMENT_VERIFIED`. Sealed evidence remains CLOSED,
with deferred checkout and no current content read. Preparation calls qualification
through that interface and has no opening operation. Existing R5.66 deferred
materialization remains the workspace adapter; no old all-content materializer is
introduced by the new consumer.

Every sealed authority member must have the same identity and resolved member path
in the protected-resource boundary. A content-pinned R5.62 `Child` is mandatory;
ordinary callbacks are not observation workers. Child capabilities must be
same-or-narrower than the parent. The execution parent binds the certificate,
qualification, authority, resource policy, guard implementation and full child
descriptor. R5.62 rechecks registry/runtime/worker source, exclusion index,
interpreter, minimal environment and linked execution integrity. Child startup
installs the guard and safe exclusion before worker import. No Git or AI-provider
requirement is added.

## Separate opening authority: synthetic implementation only

The only observation entry point is `observe_synthetic`. Actual B02 observation,
authorization issuance and opening APIs are absent. A production-sealed certificate
is necessary for future production preparation but cannot grant opening by itself.
Future actual B02 opening still requires a separately authorized one-time declaration
and separately qualified actual opening path; R5.70 creates neither.

The synthetic two-object consumer requires an externally pinned declaration binding:

- consumer protocol and exact synthetic observation operation;
- exact CertificateV3 identity and qualification;
- an R5.66 synthetic opening grant binding QualifiedAuthority, resource, commitment,
  one-time scope and one durable ledger;
- the bound worker's exact opening-evidence path and expected commitment.

Both objects are validated before reservation or content access. Recorder reservation
precedes durable dispatch; dispatch binds the observation declaration, reservation,
execution and ledger. R5.66 reserves the ledger exclusively before opening and
verifies returned content against its commitment. A mediated worker receives only
opening evidence, not the sealed content. Completion links dispatch and the recorder
observation receipt. Immediate independent capture, authority/contamination,
workspace, worker, integrity and bounded post-checks precede final stop. Replay and
alternate-ledger substitution reject; accounting is neither reset nor bypassed.

The cooperative Tier-2 trust boundary remains reviewed local adapters, externally
supplied owner pins and ordinary Python/OS infrastructure, not a hostile-host sandbox.

## Generic publication reconciliation

`publication_r5_70.check_python_source` accepts source bytes, an externally trusted
content digest, and an immutable producer-owned publication schema and schema pin.
It has no filename argument or exemption registry. Only AST-recognized literal
dictionary fields explicitly classified public receive context. Each actual value
is inspected before a narrowly bounded assignment span is masked for the legacy
text scan; comments, ordinary assignments and undeclared fields retain that scan.
Credentials, short HTTP authorization material, marked structures and immutable
fixture values reject. Unicode offsets and LF/CRLF source identity are supported.

`safe_object` / `persist_object` apply the same schema to declared object fields and
the existing guard to every remaining field. The canonical output retains the
original protocol field names and values without a context-discarding serialized
rescan. The reviewed summary context classifies the production declaration status
as public protocol metadata. Pins belong to the producer/control plane, not to an
untrusted payload. Existing untyped writers continue to reject the historical
R5.69 source and summary; the prospective check never changes those old FAIL records.
