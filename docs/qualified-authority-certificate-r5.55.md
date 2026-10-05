# QualifiedAuthority v1 and ProductionCertificateV2 — R5.55

These are prospective experiment-infrastructure interfaces. They introduce no
Lykoi semantic construct. Lykoi is a language, not an AI runtime.

## Trust and authority selection

The experiment owner supplies a **separately pinned authorization policy**, not
a directory search for the newest manifest. The policy schema is
`lykoi-qualified-authority-authorization-v1`. Its canonical SHA-256 is supplied
externally to `qualify`; deriving an expected pin from untrusted incoming policy
would defeat the trust boundary. A policy is an authorization input, not proof
of qualification. Git commit age, ancestry or manifest shape cannot qualify it.

The R5.55 authorized selection is the existing R5.53 successor, identity
`5dd2e7e645c1736f23a80bff755d347da5688cc9e8b7f7df515bd7110d1534ea`.
The experiment policy digest is
`31d4b3632cfcdbf1e928ddf3cbeaf2b88fad97e50ba502b78cf1434d09a114b8`.
See `benchmark/results/phase5c/R5_55-qualified-evidence/authorization.json`.

The policy enumerates manifest path/raw identity/canonical authority identity,
qualification and independent audit paths/raw identities, decision/adjudication
locations, predecessor-evidence root, independently frozen behavioral pins,
historical-evidence pins, checkout policy and qualification status. There is no
credential, development model, editor state or prompt history field. Closed
policy keys reject attempts to add authoring identity.

## QualifiedAuthority v1

`benchmark/evaluation/qualified_authority_r5_55.py` interprets the versioned
`lykoi-authority-successor-r5.53-v1` structure. Unsupported structures reject.
Its generic verifier has no R5.53 identity constant or content-path exception.
The current selection is experiment policy, outside certificate implementation.
Future genuinely qualified successors of this authority protocol can be selected
by a separately authorized policy without changing the certificate schema.
A new authority protocol requires a structural interpreter, not an automatic PASS.

Verification requires canonical externally pinned identity, raw manifest identity,
qualification/audit integrity and successful qualification fields; exact scoped
repository content/blob/mode membership and authorized additions; frozen pins
independent of the infrastructure manifest; actual provenance links and decision;
nonempty predecessors with exact historical manifest evidence and Git ancestry;
unchanged historical outcome/reconciliation records; valid checkout policy and
supported effective attributes. Qualifying status alone cannot substitute for
these checks. Errors are fail-closed and redact untrusted diagnostics.

The deterministic sealed `lykoi-qualified-authority-v1` value binds authority
schema, canonical authority ID, manifest ID, authorization-policy binding,
qualification/audit IDs, member integrity, frozen pins, provenance/decision,
predecessors, historical evidence, checkout policy, actual representation receipt,
attributes/effective EOL settings and `QUALIFIED` status. Representation changes
can preserve repository authority while changing the qualified representation
receipt and physical capsule; those prior experiment certificates become stale.

LF/CRLF equivalence is limited to declared UTF-8 LF repository text and exact
CRLF-pair expansion. Binary/material content remains exact. Historical physical
locks retain FAIL: predecessor bytes are evidence, not current physical-input
requirements. No historical mismatch is normalized into a historical PASS.

## ProductionCertificateV2

`benchmark/evaluation/certificate_r5_55.py` uses protocol
`lykoi-production-certificate-v2`, explicit version **2**. The old R5.51 schema,
implementation, physical-lock requirements and evidence retain their meaning.

Assembly freshly requalifies supplied authority using the externally pinned
authorization. A self-sealed object of the right shape is insufficient. Validation
also freshly requalifies and compares current capsule, authority and deterministic
certificate assembly. No fixed infrastructure-generation constant is consulted.

The certificate binds QualifiedAuthority ID and policy binding, independent frozen
pins, Tier-2 capsule ID, exact required receipt IDs, complete experiment policy,
canonical/recorder protocol, core count **30**, clean contamination and explicitly
zero reservation/dispatch/completion state. Required minimum receipts are identity,
authority, contamination and dedicated workspace; an experiment may require more.
Every specified receipt must be successful and have matching capsule, experiment,
stage and mechanism. Authority results must bind the qualified-interface ID.
Missing/stale/mixed/incomplete evidence fails closed.

An eligible certificate means the **specified** required evidence passed against
the selected qualified authority. The four synthetic receipts in R5.55 do not
assert completion of the full R5.54 production regression/observation protocol.
There is no dispatcher in either new module. R5.56 must separately supply its
complete required policy, fresh evidence and separately qualified observation
integration. V1 StaticGate is not silently made V2-compatible by this round.

## Boundaries

All publication retains the R5.47 guard. The trust model remains cooperative
local content/provenance evidence, not signed hostile-host attestation. Git supports
content and ancestry; a commit ID cannot replace those checks, and core semantics
do not depend on Git. AI authoring changes outside consumed roots do not change
authority/capsule identity; authoring data inside a consumed root is not exempt.

The governed experiment uses its dedicated authority snapshot. New development
prose is separate prospective infrastructure; it does not rewrite the pinned
baseline. A checkout with changed pinned members must reject until an explicitly
governed snapshot/relationship is established. No implicit documentation exception
weakens member integrity. R5.56 must instantiate its experiment inputs explicitly.

R5.55 independently qualifies certificate mechanics only and stops. No full
production observation or B02 activity follows. Core remains **30**, Phase 5C paused.
