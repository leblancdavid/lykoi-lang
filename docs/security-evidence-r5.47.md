# R5.47 secret-safe evidence and infrastructure succession

## Publication invariant

Raw credentials must never be persisted in benchmark/canonical evidence,
reports, logs, fixtures, committed configuration or generated project artifacts.
This covers API keys, access/refresh tokens, passwords, private keys, secret
connection strings and equivalent authentication material. Human references use
`[REDACTED]`. Only explicitly synthetic credentials belong in security tests.
`.gitignore` is defense in depth, never the publication gate.

New publication must use `benchmark.evaluation.security_r5_47.persist`, `report`
or `PublicationRecorder`, **not** the historical raw persistence entry points.
Historical R5.43/R5.45/R5.46 implementations and their evidence stay immutable;
their byte inclusion in a successor is preservation, not authorization to use
their unrestricted writers for new evidence. R5.48 must integrate and bind this
boundary into any newly qualified execution/certificate mechanism.

The versioned guard checks before output-file creation: credential-named fields,
explicit `secret`/`sensitive` structures, assignment text, bearer/basic auth,
credential-bearing URLs, private-key headers and selected recognizable provider
and JWT token shapes. It rejects ambiguous credential fields conservatively.
It does not treat ordinary digests/high entropy as secrets by themselves.
Diagnostics report fixed categories and identifier-shaped field names only;
arbitrary keys and exception details are withheld. Recorder callback exceptions
are sanitized both in persisted HALT and exceptions delivered to callers.

This bounded detector cannot recognize every opaque string, encoding or unknown
credential format. Producers must not submit raw environment/configuration or
arbitrary stdout/stderr/tracebacks. R5.47 publishes structured regression counts
and test identifiers, not captured worker text. Adding a producer or format needs
explicit publication review; passing a pattern scanner alone is insufficient.
Fail closed on a suspected value; diagnose without displaying it. Do not relax
the guard with an entire-file exemption. Scan-only adjudications must identify
exact reviewed non-authentication literals, separately from runtime protection.

## Environment and secret identity

`publication_environment` permits a narrow set of public enum/control values;
everything else records only presence. It never changes the actual worker
environment. Names are metadata; unsafe names themselves reject publication.
Absent, empty and nonempty are distinct where material identity requires it;
presence-only metadata intentionally does not establish empty/value equivalence.

Do not fingerprint an irrelevant secret. For explicitly material secret values,
the prospective helper uses domain-separated HMAC-SHA256 over protocol, name and
value, with an external key of at least 32 bytes and a non-secret key identifier.
No raw secret or key bytes enter evidence. Plain hashes/public salts are not
approved for low-entropy secrets. Key material must be generated with adequate
entropy, held outside the repository/evidence, access controlled, and rotated
under an explicit identity policy. Length alone cannot prove entropy. Synthetic
tests establish representation and key-dependent separation only; production
key custody, descendant propagation and complete material relevance remain
**unqualified**, for separately authorized R5.48 work. No real key is provisioned
or stored by R5.47. Fingerprint envelopes are representations, not attestations
of trustworthy origin or production execution identity.

## Infrastructure successor boundary

R5.43 remains a historical qualified baseline. Its immutable lock must retain
the `.gitignore` mismatch. R5.46 remains permanently halted, all 16 receipts
quarantined. R5.47 may qualify physical security-corrected infrastructure bytes
only, with predecessor identity, a complete per-file difference inventory and
deterministic reproduction. Lock membership includes preserved historical and
unqualified research material without promoting its qualification status.
The successor does not attest external Python/Git/OS closure, runtime identity,
freshness/TOCTOU, certificates or evidence reuse.

Every inherited file must match current HEAD, except explicitly declared new
R5.47 code/docs/evidence and the three research summaries. Each predecessor
member is preserved except the already committed `.gitignore` security correction.
Added post-R5.43 history is classified separately as historical stopped/gap
evidence, security remediation, or retained unqualified prototype. No unexplained
semantic/profile/compiler/application difference is authorized.

Scan tracked physical bytes, the full index, all locally reachable Git refs,
new commit candidates and ignored local files. Record only categorical findings.
Local remote-tracking refs do not attest unfetched/server-side history. Preserve
the owner's recorded unpushed-history rewrite; do not recover or publish old
credential-bearing reflog/unreachable objects. If a credential remains reachable
in sharing history, halt until separately authorized remediation. External
revocation/rotation remains `ROTATION_STATUS_EXTERNAL_OR_UNVERIFIED`.

All B02 prohibitions remain active. Restricted historical harness skips are
mandatory. No R5.46 identity tests or qualification runner is resumed here.
