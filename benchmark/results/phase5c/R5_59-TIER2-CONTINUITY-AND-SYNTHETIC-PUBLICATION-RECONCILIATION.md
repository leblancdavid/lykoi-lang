# R5.59 — Tier-2 continuity and synthetic-publication reconciliation

## Outcome

**`R5_59_CONTINUITY_PUBLICATION_RECONCILED`** — both corrections are
independently qualified prospectively. Focused qualification: **267/267 pass**.
This is mechanism qualification, not production Tier-2 qualification.

Inherited **`R5_58_PROTOCOL_HALT`** remains permanent. Its failed continuity,
failed independent publication audit, zero qualification batches and zero
production receipts retain their original meaning and bytes.

**B02 exposure: zero. Core semantics: 30. Phase 5C: paused.**

## Scope and starting state

Initial `git status --short` was clean. The only implementation additions are
prospective continuity and publication adapters, a synthetic security input,
independent focused tests and a focused evidence driver. Versioned policy:
[continuity-publication-r5.59.md](../../../docs/continuity-publication-r5.59.md).

Core semantics, compiler behavior, profiles, behavioral contracts, B02 authority,
QualifiedAuthority, ProductionCertificateV2, Tier-2 methodology, observation
controls and bounded-driver policy retain their existing definitions. Historical
R5.58 orchestration is preserved. No full R5.58 production qualification is run.

## LF/CRLF cause and generic correction

R5.58 compared physical checkout hashes against the R5.55 LF snapshot before
governed materialization. Four mechanisms were CRLF checkouts; their actual LF
repository bytes reproduce the snapshot hashes exactly. That mismatch is checkout
representation, not implementation mutation under the qualified R5.50–R5.53 rule.

`continuity_r5_59.verify` first verifies independently pinned repository bytes,
then compares eligible qualified UTF-8 LF text against a checkout with actual
CRLF pairs mapped to LF. Repository digest is deterministic continuity identity;
physical digest, newline counts and representation remain separately recorded.
It neither normalizes the repository pin nor changes any historical physical lock.
No filename is special-cased. The fresh read-only witness enumerates the four
original failures from historical evidence and explicitly reviews their evaluator
source-text eligibility. All four return `LF_CRLF_ONLY` prospectively.

Exact-byte exclusions: binary, unclassified, materially byte-sensitive, unsupported
encoding/filter transformations, repository CR and frozen artifacts whose protocol
requires physical bytes. The exact-byte override takes precedence over text
classification. Bare CR and actual textual/binary mutations reject.

Evidence: [checks.json](R5_59-evidence/checks.json),
[continuity.json](R5_59-evidence/continuity.json).

## Synthetic-fixture and publication correction

The explicit dispositions are `SYNTHETIC_SECURITY_FIXTURE` and
`PUBLISHABLE_SOURCE_OR_EVIDENCE`. A fixed read-only designation table binds an
explicitly reviewed security input to its repository-content SHA-256. Neither
caller labels, comments, environment configuration nor runtime registration can
add a designation. Changing substantive fixture bytes rejects the designation.

Only obviously fake, nonfunctional, explicitly synthetic sensitive assignments
are consumed as input. The fixture scanner redacts just those values in memory
and applies R5.47 to all remaining content. Token-shaped material and non-synthetic
credential assignments still reject. No real credential is used in tests.

Prospective output entry points retain all R5.47 checks and reject designated
synthetic values anywhere in output, including ordinary fields. The same input
value rejects in evidence, certificates, capsules, receipts, reports, publication
and publication-intended logs, before output-file creation. Recorder and prose
report paths are covered. Diagnostics remain redacted.

The failing R5.58 filename and credential string have no whitelist. Its embedded
assignment remains rejected as unapproved source. New audits must consume the
separate designated input and publish only safe structured results. Fixture input
acceptance never authorizes publishing the source fixture itself as evidence.

Evidence: [publication-qualified.json](R5_59-evidence/publication-qualified.json).
The earlier eight-test development pass is separately preserved in
[publication.json](R5_59-evidence/publication.json); it predates removal of the
temporary historical-audit designation and the added recorder witness. It is
not the final publication qualification. The intermediate nine-test pass in
`publication-final.json` also precedes the final source-safe test construction.

## Independent focused tests

Each suite runs through a fresh invocation of the focused driver. Worker logs
and exception details are withheld; evidence records counts and test IDs only.
CertificateV2/linkage methods run in five separate groups of 8/8/8/8/2 against
the already-qualified prospective synthetic fixture. No production stage plan,
authority instance, capsule, certificate or receipt is issued by R5.59.

| Suite | Discovered / passed |
| --- | ---: |
| New generic continuity | 8 / 8 |
| Final synthetic/publication boundary | 9 / 9 |
| Existing checkout representation | 22 / 22 |
| Existing successor authority | 18 / 18 |
| Existing CertificateV2/linkage | 34 / 34 |
| Existing legacy certificate | 33 / 33 |
| Existing security | 22 / 22 |
| Existing reproducibility boundary | 18 / 18 |
| Existing Tier-2 mechanisms | 43 / 43 |
| Existing canonical recorder/publication linkage | 29 / 29 |
| Compiler/application regression | 31 / 31 |
| **Total final focused qualification** | **267 / 267** |

Continuity witnesses cover LF→CRLF, CRLF→LF, genuine mutation, binary mutation,
exact-byte authority, unclassified/bare-CR rejection, wrong repository pin and
deterministic identity. Publication witnesses cover designated input, all output
contexts, unapproved assignment, opaque raw-secret stand-in rejection, redaction,
immutable designation, recognizable-token rejection, safe source, preserved
historical source rejection and recorder bypass prevention.

Fresh closed schema/structure and **99-leaf** traceability pass on the independent
public profile; implementation/profile contamination is clean and core count is
30. Validation and safety pass. `git diff --check` passes. Current full security
tests pass 22/22; earlier historical failures remain preserved as earlier evidence.
See [commands.json](R5_59-evidence/commands.json) and
[summary.json](R5_59-evidence/summary.json).

Commands use `python -B -S benchmark/results/phase5c/r5_59_qualification.py`
with `suite <label>`, `suite certificate <0..4>`, `checks`, `commands`, `summary`
and `final`. The separate commands mode runs model validation, safety and diff
checks without publishing captured output.

## Development observations and historical preservation

An initial read-only continuity witness assumed all R5.55 mechanisms belonged
to the older R5.53 manifest and failed on missing membership. The corrected
witness uses HEAD repository blobs proven against the R5.55 snapshot, with
explicit reviewed text classification. An intermediate PowerShell command
failed parsing before execution; its corrected invocation completed. Neither
failure was a mechanism-test failure or a production-stage attempt. Both are
recorded in [development-observations.json](R5_59-evidence/development-observations.json).

The first final publication scan rejected an assignment pattern in the new test
source. No integrity PASS was issued. Rejection inputs are now constructed in
memory with JSON quoting; source receives no designation or exception. The affected
nine-test suite and final integrity are freshly rerun. Its earlier pre-publication
summary and suite counts are retained separately, not promoted as final integrity.

The preservation baseline binds all **1,962** pre-existing tracked `benchmark/results`
file by physical SHA-256, including R5.58's failed evidence and scripts. Final
publication integrity rehashes that complete set, checks new canonical evidence,
scans current changed/new source under the explicit input/output dispositions,
and records evidence and current source digests. New-file whitespace checks and
`git diff --check` pass. The historical R5.58 rejection is also independently
tested without rewriting or resuming its candidate.

Evidence: [preservation-baseline.json](R5_59-evidence/preservation-baseline.json),
[publication-integrity.json](R5_59-evidence/publication-integrity.json).

## Accounting, final classification and stop

B02 exposure, reservation, dispatch, CheckedPlans, readiness, audit, admission,
generation, execution and frozen acceptance: **all zero** in R5.59. The focused
driver has no B02 subject or production observation entry point. Synthetic
certificate/recorder tests remain isolated test fixtures. Production qualification
batches, production receipts and production observations: **zero**.

Final classification: **`R5_59_CONTINUITY_PUBLICATION_RECONCILED`**.

Recommend a separately authorized **wholly fresh production qualification**,
binding these prospective adapters and requiring all fresh production regression
and lifecycle gates. R5.58 supplies no reusable production evidence. R5.59 stops
after focused qualification and publication integrity; it does not begin that
fresh qualification or authorize B02.
