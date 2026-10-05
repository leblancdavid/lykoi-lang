# R5.59 — Prospective continuity and synthetic-input boundaries

This applies the qualified R5.50–R5.53 repository-content/checkout distinction
and R5.47's synthetic-security-test allowance. It does not amend historical
physical locks, Tier-2 methodology, authority or certificate semantics.

## Continuity

`benchmark.evaluation.continuity_r5_59.verify` takes independently qualified
repository bytes, their trusted SHA-256, the reviewed file classification and
an exact-byte protocol override. The repository pin is checked before comparing
the checkout. Only `utf8-lf-text` with valid UTF-8, no NUL and no repository CR
is eligible. Replace actual CRLF pairs only; bare CR and every other mutation
fail. Continuity identity is the unchanged repository digest. Checkout physical
digest, newline counts and representation relationship are separate metadata.

Binary, unclassified, encoding/filter-transformed, materially byte-sensitive and
explicitly physical-byte frozen artifacts require exact physical equality.
Callers must carry the strongest applicable protocol as `exact_bytes=True`;
eligibility cannot be inferred solely from a filename or successful decoding.
Frozen authority semantics remain unchanged. This adapter does not reconstruct
historical bytes or turn historical physical-hash failures into passes.

The R5.59 read-only witness explicitly reviews evaluator Python implementation
source as non-byte-sensitive UTF-8 LF text, checks its HEAD repository bytes
against the qualified R5.55 snapshot pin, and records current checkout form.
Its enumerated witnesses come from the preserved failure record; the adapter
contains no filename-specific behavior.

## Synthetic security inputs versus publication

`SYNTHETIC_SECURITY_FIXTURE` is an input disposition, never a publication
permission. `PUBLISHABLE_SOURCE_OR_EVIDENCE` remains subject to R5.47 scanning.
New probes place deliberately fake, nonfunctional credential assignments in
separately reviewed fixtures. The reviewed designation table is fixed in
`benchmark.evaluation.publication_r5_59`, read-only and content-pinned. It has
no registration API, environment/config override or caller-supplied policy.
Adding a designation requires a reviewed mechanism/policy change and fresh
qualification; a comment or runtime label cannot add one.

Only sensitive quoted assignment values beginning with the explicit fake
`synthetic-` marker can be consumed from an approved fixture. Recognizable
provider/token/private-key patterns remain forbidden even there. The detector
redacts those input assignments in memory and scans all remaining content with
R5.47. Unquoted assignments, unapproved sources, changed fixture content and
unavailable designated inputs fail closed. LF/CRLF is separately permissible
for these designated text fixtures; substantive edits invalidate designation.
Never place real credentials into fixtures; the marker is a producer obligation,
not proof that an arbitrary opaque value is nonfunctional.

The prospective `safe_bytes`, `persist`, `report` and `PublicationRecorder`
entry points retain R5.47 protections and additionally reject designated fake
values anywhere in publication text, including ordinary noncredential fields.
Evidence, certificates, capsules, receipts, reports, publication output and
publication-intended logs must use this boundary. Fixture input scanning never
replaces the output check. Output creation follows validation, and diagnostics
contain fixed categories rather than rejected values.

The historical R5.58 stopped-audit filename and its embedded assignment are
**not** whitelisted or designated. Its old scan continues to fail. Prospective
audits consume separately designated input and publish only structured safe
results, not fixture content or worker logs. No historical evidence is rewritten.

This retains R5.47's bounded detector limitations and cooperative local trust
boundary. It does not claim hostile Python-process immutability, recognize all
possible encoded secrets, change reproducibility requirements, or authorize B02.
