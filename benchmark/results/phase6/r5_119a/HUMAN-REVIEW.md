# P6-A03 — Revised Research Approval Review

**Original request:** Add SELECT permission to both Redis @read and @write ACL
categories, avoiding the reporter's GET/SET-working-but-SELECT-denied problem and
allowing explicit selection of the intended database.

**Inherited ACL behavior established:** Redis project's public documentation,
pinned before this issue at revision `7277deb0a858a6384d8a069fc654c61fcda32b34`
(2022-01-02), says rules apply **left-to-right**. Command rules add/remove individual
commands; category rules add/remove all their member commands from the same allowed
list. Thus a later category removal can revoke an earlier explicit grant, and a
later category grant can restore an earlier explicit denial. No permanent special
priority is assigned to explicit grants or denials. This is documentation-grounded
behavior, not a runtime/version-matrix finding.

**Q1 resolution or remaining uncertainty:** Q1 is resolved for this bounded,
documented simple-rule scope. After SELECT joins both categories:

| ACL suffix after -@all | SELECT outcome |
| --- | --- |
| `+select +@read -@write` | **Deny** |
| `+@read -@write +select` | **Allow** |
| `-select +@read` | **Allow** |
| `+@read -select` | **Deny** |
| `+@read -@write` / `-@write +@read` | **Deny / Allow** |
| `+@write -@read` / `-@read +@write` | **Deny / Allow** |

No new permission-precedence policy is needed. The evidence resolves the reporter's
uncertainty about order; it does not assert a maintainer decision to adopt the change.

**Proposed research interpretation:** Add SELECT to exactly the requested two
categories while preserving inherited ACL rule-processing semantics and other
memberships. Valid surviving grants permit explicit SELECT and real selection of
the requested database. Do not introduce a SELECT exception to keep the first mixed
configuration allowed. Preserving processing does **not** preserve every old SELECT
allowance after membership changes.

**Acceptance expectations:** Isolated @read and @write, the full reporter
configuration, and explicit DB0/nonzero selection must succeed when other preconditions
hold. Twelve mixed-rule cases have fixed allow/deny and selected-database expectations.
Four direct-command controls sample unchanged processing for SELECT and GET; category
inspection checks SELECT belongs to both requested categories. Denied SELECT must
not execute selection. Exact wire error text is not specified. **Zero tests executed.**

**Assumptions and limitations:** Fresh valid ACL users and authenticated connections;
ordinary command/category lists on a non-cluster environment with an available
nonzero database. Reporter server version is unknown; no runtime probes or all-release
equivalence established. Selectors, modules, first-argument/subcommand restrictions,
persistence/reload/migration and rollout are outside scope. Same-agent/same-model
candidate/review; expectations fixed independently of any generated implementation,
not independent cognition. No Redis maintainer endorsement or production authority.
Later evaluator/verifier credentials and native pipeline bindings are not supplied here.

**Exact source/FRC/acceptance identities:** SHA-256; JSON candidate identities are
existing FRC canonical hashes, not controller approvals.
- Original source: `redis/redis#13736`, exact R5.116A capture
  `90132320ad5aa7e7c3996ed97096a798a9ecceea76927a9f9c1948bda58d9970`.
- Inherited evidence candidate:
  `bd0487a9c2e90f7cfa31124c3071ffe98c630099382c99e692190d5dcfd6c348`.
- Attributed composite source (unchanged issue body plus pinned documentary excerpts):
  `61f939652d67777081306ee0c9d3caeca47872f49af155bab9f2723838f3819a`.
- FRC: `R5.119/P6-A03/candidate`, revision **2**:
  `69d32178bb065e1fa80ac6bb319a1147e3ac7c699a99bb0f56a6db52129ce0f8`.
- Acceptance: `R5.119A/P6-A03/acceptance-candidate/2`:
  `6d0551086fffacc52ce9c35f1d87b127ec181c06120f67b177eefe5f6a1406b3`.

**Recommendation: approve** this bounded research interpretation and fixed behavioral
expectations in an explicit subsequent human decision. **This is a recommendation,
not approval.** All native semantic/authoring/verification gates remain. No grant,
seal, implementation or evaluation issued; stop after review.
