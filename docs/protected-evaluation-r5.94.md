# R5.94 — Generic protected evaluation admission

Prospective **protected-evaluation-r5.94-1**, with provenance
`PROTECTED_EVALUATION`, activation scope `PROTECTED_HELD_OUT_EVALUATION`, and
`FormalRequirementContract-protected-0.1`. The provenance means arbitrary source
material admitted under restricted held-out evaluation rules. It selects no target.

## Exact admission and visibility

The trusted service instantiates `ProtectedController` against a verified candidate.
An owner activates that exact candidate for one project. Owner authorization binds
the activation, opaque source identity, run, exact role-policy digest and clarification
authority. No content hash or source path is needed at authorization. A dedicated
admission principal (roles `admission` and `owner`) durably reserves one opening before
the trusted custodian callback is invoked. The returned UTF-8 text receives immutable
message/source identities and is bound to the opaque identity and authorization.
An incomplete callback consumes the attempt; no automatic reopen is permitted.
A returned read is separately recorded before admission, so rejected admission cannot
erase a completed source read or restore pristine status.

Workers get mediated input values, never controller/database capabilities. Source-side
formalizer and reviewer handoffs record recipient principal, role, session, artifact,
representation and journal ordering **before** producer invocation, including when
the producer later fails. The reviewer cannot request a candidate before SOI commitment.
The author gets only the native grant/reservation-bound `author_input`, with unchanged
V1, toolchain and seed fields. Raw sources/transcripts/inventories/candidates are denied.
Verifier handoffs allow formal WHAT, sealed plans and targets; formal WHAT removes
source prose/quotes. Original protected prose is never sent to the author or verifier.

The immutable dependency graph retains protected origin through seals, projections,
plans, grants, builds and verification. Native semantic payloads are unchanged; no
public/synthetic relabeling satisfies a protected validation check. Protected records
and their digests belong in a restricted controller store, not public result publication.
Only synthetic fixture contents may be published by this engineering round.

## Auditable state and counters

`ledger(opaque_identity)` reconstructs append-only receipts: `PRISTINE`,
`AUTHORIZED_NOT_ACCESSED`, reservation, `SOURCE_ADMITTED`, `FORMALIZATION_EXPOSED`,
`REVIEW_EXPOSED`, `AUTHOR_EXPOSED`, verification exposure and first terminal outcome.
These are observed milestones, not a linear ordinal that invents missing exposures.
Authorization leaves custody pristine. Author delivery records derived development
knowledge as `AUTHORIZED_DERIVED_EXPOSURE`; separate `DEVELOPMENT_EXPOSED` is forbidden
by this policy and its counter remains zero. No reset can erase admissions/exposures.

Counters distinguish authorization, open attempts, completed source opens/reads/admissions,
each role's deliveries and denied operations. A failed callback has an open-attempt
receipt and an `INCOMPLETE` result; it does not claim a successful source read. The
trusted custodian must report partial external reads honestly: controller receipts
cannot independently observe bytes read outside its API. Denials record no source text.

## Clarification

An authorization selects `HUMAN_AVAILABLE`, `UNAVAILABLE_TERMINATE`, or
`PREAUTHORIZED_AUTHORITY`, with an exact scoped owner/delegate principal for available
modes. Answers retain the existing authenticated clarification/revision/review rules.
Unavailable material clarification terminates the evaluation; no answer is manufactured.
Changing authority needs a separately authorized evaluation, never repair of a frozen
first terminal result. Supported meaning, mappings, BDI, adequacy, V1 and verification
remain exactly the existing bounded engines.

## Historical preservation and compatibility mechanism

Historical controller/workspace/pipeline/FRC modules are byte-preserved. A small private
module-view recipe compiles their source into separate namespaces; only enumerated
FRC provenance/version and workspace provenance/context anchors are substituted. Each
anchor must occur exactly once or import fails. Private dependency rebinding selects
the prospective validator; it never patches historical globals or `sys.modules`.
The frozen recipe and its complete original import closure identify this machinery.
This avoids a second maintained copy of semantic implementations. Public comparison
uses the same prospective validator/version and identical neutral workspace context.
Existing public workers' source-only commitments get a prospective adapter correcting
only the classification field used in that commitment. Prompts/configurations are pinned.

## Boundary and limits

This is trusted-local engineering calibration, not held-out evidence, hostile-code OS
isolation, a live protected model run or a claim of semantic completeness. Trusted
service APIs `artifact()`, `inputs()` and SQLite are deliberately unavailable to workers;
an operator or arbitrary Python code in that process can bypass them. Receipt counts
measure delivered inputs, not human/model cognition. Existing process/tool/API controls,
provider retention/build uncertainty, correlated errors and finite verification remain.
The generic candidate is frozen **inactive**, without any target authorization. A later
round must explicitly activate it and authorize a source. R5.94 stops at that freeze.
