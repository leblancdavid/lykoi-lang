### P6-A03 — Research Approval Review

**Original request:** Redis issue `redis/redis#13736` proposes including `SELECT`
permission in both `@read` and `@write` ACL categories. The reporter describes
GET/SET working while SELECT fails, causing activity on DB0 instead of the intended
database.

**Proposed behavior:** In otherwise-valid category grants without conflicting
revocations, either category permits an explicit valid `SELECT` without adding
`+select`. SELECT must actually select the requested database for subsequent
permitted operations. Grant/revoke compatibility remains unresolved.

**Explicit obligations:** A03-E1: `@read` includes SELECT permission. A03-E2:
`@write` includes SELECT permission. Avoiding a separate `+select` and enabling the
intended explicit database selection are necessary implications (A03-I1/I2).

**Assumptions:** Valid authorized setup, authenticated user, available nonzero
database and permitted observation keys/commands are fixture prerequisites. Use
the full configuration's `+@read`; preserve the prose's missing-plus spelling as
source text, without making it a required syntax. No ACL precedence is assumed.

**Material questions:** A03-Q1: should `+select +@read -@write` **allow or deny
SELECT**? Clarify the observable grant/revoke rule, including reversed category
order and explicit `-select` before/after a category grant. The reporter expressly
raises this compatibility issue and supplies **no definitive default**.

**Acceptance tests:** Four source-determined candidate checks isolate @read and
@write, reproduce the supplied configuration, and observe explicit selection of
DB0/nonzero DB through read/write probes. Two additional checks cover the reported
compatibility case and grant/revoke boundaries; their expected permission outcomes
remain unselected pending Q1. **Zero tests executed.**

**Scope limitations:** Bounded permission/connection-selection experiment, not a
complete Redis specification, restart/persistence/migration assessment, universal
ACL/security proof, Redis maintainer endorsement or production authorization.
Same-agent/same-model source-only preparation; expectations are independent of
generated implementation, not independently authored cognition. Owner appointment
does not approve these artifacts; no grant, seal or authoring has occurred.

**Exact identities:** SHA-256 below; JSON candidates use existing FRC canonical
JSON hashing, not controller approval identities.
- Source identity: `redis/redis#13736`, R5.116A `candidate-06-source.json`, retrieved
  `2026-10-08T13:55:07.762848+00:00`; capture
  `90132320ad5aa7e7c3996ed97096a798a9ecceea76927a9f9c1948bda58d9970`;
  body `568764f7390f21f06b50682fc385168116f572b764615dada8b0893963ef3952`.
- Candidate FRC identity: `R5.119/P6-A03/candidate`, revision 1;
  `69fe6dd3816c184be9af73ad1b8863a6881f579543cd4c99d80cca402b7bc5ab`.
- Acceptance-plan identity: `R5.119/P6-A03/acceptance-candidate/1`;
  `c50f461fa53046fe8da3fe75307061b9a345818f6bbe21453e6e58a3292ae0b0`.

**Recommendation:** **Needs clarification.** Ready for human review, not approval
or evaluation. Resolve Q1, then prepare newly identified linked candidates/review
for an explicit subsequent owner decision; the current artifacts cannot be approved
as a waiver of that ambiguity.
