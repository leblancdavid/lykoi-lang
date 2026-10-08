# P6-A03 source-only behavioral interpretation and materiality review

Initial review, pass **1 of at most 3** under R5.118A. SAME_AGENT/SAME_MODEL;
no correction review registered, no independent cognition claimed. Candidate and
acceptance plan are prepared without generated implementation, inspection of fixes,
or external behavioral execution. This is a human-review preparation, not a native
review receipt, controller registration or pipeline first result.

## What the request changes

The reporter says read/write ACL configurations may allow GET/SET but deny SELECT,
so activity incorrectly remains on DB0. They propose including SELECT permission
implicitly in **each** of `@read` and `@write`, avoiding a separate `+select`.
The contract's unopposed-grant cases require a valid explicit SELECT to be allowed
and actually select the requested database. It is not enough to emit success while
continuing on DB0. No automatic SELECT executed by GET/SET is requested.

Inputs are authorized category-based ACL configuration, authenticated user/connection,
and explicit valid SELECT database index. Outputs are permission success/denial and
selected-database observations through already permitted operations. Material state
is ACL command permission and connection selection. Fixture keys demonstrate selection;
they are not a new requirement for SELECT to mutate keys.

The source supplies no exact success/error strings, general validation policy,
invalid-index range, persistence/restart semantics or migration/rollout requirement.
Tests use valid inputs and established prerequisites. Absence of those details is
not a material clarification question for this bounded preparation. Nothing invents
new authentication, unrestricted key access, FLUSHDB grants or durability guarantees.

## Source inventory and bidirectional reconciliation

| Source fragment | Status and disposition | Candidate/check coverage |
| --- | --- | --- |
| `The @read and @write ... do not currently include select` (with source backticks) | Reporter diagnosis, not independently verified implementation fact | E1/E2 motivation, T1/T2 |
| Full `ACL SETUSER cacheUser ...` example | Exact source input witness, including `+@read`, preserved as data | T3; context |
| `GET, SET etc worked, but the SELECT did not` (with source backticks) | Reported observation grounds database-specific probes, not universal preservation | I2; T3 |
| `I propose that this should be implicit in @read / @write` (with source backticks) | Two stated category obligations | E1/E2; T1/T2/T3 |
| `Obviously a workaround here is to add +select` (with source backticks) | Necessary implication: separate grant should not be necessary | I1; T1/T2/T3 |
| `specifying the correct database is a fundamental requirement` | Necessary implication: explicit permitted SELECT enables intended selection | I2; T1/T2/T3/T4 |
| `select is in @keyspace` / `flushdb` caution / `del` overlapping categories | Context only; no request to remove @keyspace membership or broaden grants | FRC unspecified, plan preservation limitations |
| Linked client ticket | Uninspected, no imported obligation | Excluded context |
| `+select +@read -@write` and order uncertainty | Material source-raised compatibility decision, not an algorithm choice | Q1; T5/T6 conditional, unresolved |

Every E/I obligation has a literal quote from the preserved body and explicit check
bindings. Necessary implications derive only from E1/E2/I1, never from Lykoi
capabilities. No obligation is inferred from an upstream fix, current label or test
result. The inventory treats the final paragraph as a question, not an instruction
to preserve all ACLs or a definitive ordering rule.

## Explicit obligations versus implications and assumptions

- **Stated:** A03-E1 grants SELECT through @read; A03-E2 grants it through @write.
- **Necessary implications:** A03-I1 eliminates the separate +select requirement in
  unopposed valid grants; A03-I2 makes the resulting explicit valid SELECT operational
  for selecting the desired database. Neither decides conflict precedence.
- **Assumptions/prerequisites:** valid administrator setup, authenticated connection,
  available nonzero database, permissible observation keys/GET/SET. These enable
  probes, not new product obligations. Database 1 and marker values are replaceable
  fixture witnesses, not source-mandated numeric/value constants.
- **Text interpretation:** the full source configuration says `+@read`; prose says
  `@read` without `+`. The candidate preserves both source spellings and uses the
  complete configuration as the valid example. It does not require missing-plus
  syntax to be accepted. No question about internal tokenization is needed.
- **Preservation:** the source's described GET/SET operation is the limited context
  for T3 probes. There is no explicit universal unchanged-behavior promise. Existing
  command policies outside the requested SELECT permission delta remain unspecified,
  with no new authority to redefine them. The source-raised ACL compatibility issue
  remains open rather than being silently treated as preservation.

## Material clarification — A03-Q1 (blocking)

**Unresolved decision:** What observable grant/revoke rule applies after SELECT
belongs to both categories, particularly for `+select +@read -@write`?

**Why it matters:** The exact same otherwise-valid SELECT can succeed and select
the desired database, or fail permission checking. Existing user configurations can
lose access under one interpretation and retain it under another. That affects the
meaning of the feature, not just how it is implemented.

**Exact source evidence:**

> One potential gotcha; I do not know the order in which ACLs are applied; if it is left-to-right, then pre-existing setups like `+select +@read -@write` would presumably (if `select` was included in `@read` and `@write`) lead to not having `select`. Not sure if this is considered a problem.

The preserved body has a trailing space after this paragraph; the quote above
omits only that display whitespace. The FRC retains the exact body bytes.

**Available interpretations:**

1. Later category revocation can remove SELECT, even if explicitly or through
   @read granted earlier; the named configuration therefore denies SELECT.
2. A source-authorized compatibility/grant-preservation rule retains SELECT when
   independently or explicitly granted; the named configuration allows SELECT.
3. Another legitimately clarified behavioral rule determines those outcomes.

These are candidate interpretations, not claims about Redis's current semantics.
**Source-supported default:** none. The reporter presents left-to-right removal
as hypothetical and expressly questions whether it is a problem.

**Human question:** For this experiment, should `+select +@read -@write` allow or
deny SELECT? Please provide/confirm the observable rule that also determines
`+@read -@write` versus `-@write +@read` and explicit `-select` before/after a
category grant. No internal algorithm, storage layout or implementation choice is
requested. A research-only preference is not proof of upstream intent; any supplied
interpretation must be transparently recorded as legitimate clarification with its
authority and limitation. New clarified artifacts need new identities and review.

## Acceptance coverage and readiness

T1/T2 isolate the categories; T3 reproduces the source configuration; T4 checks
explicit DB0/nonzero selection. All are source-grounded logical checks, not executed
Redis commands. T5/T6 identify negative/order boundary witnesses but intentionally
have no selected expectation pending Q1. No guessed errors or universal policies.
Finite coverage cannot establish all ACL combinations, version/platform behavior,
restart/persistence or security correctness.

**Recommendation: needs clarification.** Candidate artifacts are ready for human
review, not approval/evaluation. Appointed owner approval is available as a role,
but has not been given for these artifacts; it cannot waive material ambiguity.
Acceptance needs the clarified order outcomes and a legitimately registered
different verifier principal before later native use. No native plan has been
projected and no stage gate has run.
