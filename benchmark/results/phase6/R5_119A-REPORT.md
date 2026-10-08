# R5.119A — Redis ACL clarification and research contract revision

**`R5_119A_REDIS_RESEARCH_CONTRACT_READY_FOR_APPROVAL`**

**Yes:** pre-issue public Redis documentation supplies the established simple ACL
rule processor, so adding SELECT to @read/@write does not need a newly invented
permission-precedence policy. Q1 is resolved within that documented-rule scope.
This is contract/expectation readiness for human research approval, not a grant,
native execution-readiness receipt, feature implementation or evaluation result.

## Deliverables

1. [Inherited Redis ACL evidence](r5_119a/INHERITED-EVIDENCE.json): exact pinned
   sources/revision, raw SHA-256/Git blob/size, retrieval chronology, 15 literal
   extracts, documentary findings and version limitations.
2. [Q1 analysis](r5_119a/Q1-ANALYSIS.md): all four requested cases, reversed-category
   and explicit-denial counterparts; original-membership versus requested-membership
   deductions; preservation scope and authority limits.
3. [Revised typed candidate FRC](r5_119a/FRC-CANDIDATE-R2.json): same contract ID,
   revision 2, original E1/E2 and I1/I2 retained with declared meaning-change lineage;
   documented inherited H1/H2 and narrow-preservation I3 added. No unresolved material
   issue in this scope, separate same-agent human review, no FRC approval/seal.
4. [Revised acceptance candidate](r5_119a/ACCEPTANCE-PLAN-R2.json): exact source,
   inherited evidence, prior-plan and new-FRC binding; seven check groups with all
   expectations fixed before authoring, zero executed.
5. [Human research approval review](r5_119a/HUMAN-REVIEW.md): recommendation **approve**
   the bounded research interpretation in a subsequent human decision; no automatic
   approval, credentials, research authorization or fabricated maintainer decision.
6. This report; [identities](r5_119a/IDENTITIES.json) and
   [read-only revision verifier](r5_119a/verify_revision.py).

## Start, provenance and source boundary

Initial `git status --short` empty. HEAD
`b2240550d3a5f2e8bdc1c717f2310cd1f715785c`; root tree
`0d8a1efa7a895b636329bbdf3b0a709ea47acb95`.
Metadata observation UTC `2026-10-08T16:01:33.383450+00:00` occurred after
documentary retrieval began and before R5.119A edits; it is not represented as a
fresh pre-exposure evaluation snapshot. This is an authorized clarification round,
not an evaluation. Model/provider OpenAI `openai/gpt-6.1-sol` via OpenCode.

Compiler subtree `87f3c8c1c8b1af394235aa835d39342b770b6c49`; kernel accounting blob
`cb0f5c566149fae770e270bdbe71d456a03fe8b9`, **26 concepts unchanged**. FRC
`FormalRequirementContract-0.1`, compiler/backend `0.3.0`, normal dispatcher
`LykoiProgram-1`, representation `LykoiContractV1`, sealed pipeline and all profiles
unchanged. Historical R5.118A 146-test and R5.114 397-test evidence remains historical;
no test suite that could author/project/compile/behaviorally verify was run here.

Only exact preserved P6-A03 issue/capture/provenance and R5.119 records reopened.
Public inherited evidence was identified from the Redis project's documentation
repository independently of issue-linked material. A documentation-history query
with a pre-issue cutoff found a 2022 path restructure; its named parent provides
the old ACL topic. Pinned raw topic, ACL SETUSER and SELECT command documentation
were read. Documentation commit metadata, not implementation diffs, supplied date/
revision identity. No fixing PR, Redis implementation commit, solution patch,
post-resolution explanation, comments or linked client ticket accessed. No
P6-A04/P6-A05 source or acceptance content accessed.

The raw documentation was byte-hashed in memory; source versions and exact relevant
extracts are preserved locally, not an unversioned paraphrase of today's website.
Raw full text is reproducible from pinned URLs, blobs, sizes and SHA-256. These are
public documentation claims, not empirical baseline-server observations. No Redis
runtime was installed, started, altered or probed; baseline probes **zero**.

## Findings and Q1 resolution

Documentation explicitly establishes left-to-right processing and add/remove effects
on allowed commands, including all members of a category. The overlapping-category
example confirms that a later category removal removes commands granted earlier.
Explicit grant and denial operations have no documented permanent priority over
later category operations on the same commands.

Consequently, after adding SELECT to both categories:

- `+select +@read -@write` **denies** SELECT.
- `+@read -@write +select` **allows** SELECT.
- `-select +@read` **allows** SELECT.
- `+@read -select` **denies** SELECT.
- `+@read -@write` versus `-@write +@read` yields **deny versus allow**.
- The mirrored @write/@read and explicit-denial cases follow the same rule.

These are documentary deductions combining original E1/E2 with inherited semantics,
not observations of a modified Redis or a desired-outcome-derived policy. The old
membership column uses the issue's reported absence of SELECT from those categories;
no complete old command table or all-version behavior was measured.

The source asks for category membership and warns conditionally about ordered
removal. It does not request a new processor or guarantee preserving each existing
mixed configuration. The user explicitly prefers the ordinary-processor-preserving
interpretation when supported. Independent pre-issue documentation now supports it.
No maintainer decision is fabricated; the owner will decide whether to authorize
this disclosed experimental interpretation. A SELECT-specific preservation exception
would be an additional unsupported policy and is excluded.

## Source inventory, lineage and evidence binding

| Material item | Revision 2 treatment | Acceptance bindings |
| --- | --- | --- |
| Source proposal for both categories | E1/E2 retained as membership obligations | T1/T2/T3/T5/T7 |
| Separate +select workaround | I1, surviving category grant supplies permission | T1/T2/T3/T5 |
| Intended database rather than incorrect DB0 | I2, documented connection-selection context | T1/T2/T3/T4/T5 |
| Reporter full configuration and prose typo | Full input retained, missing-plus prose not made new syntax | T3, context |
| Reporter Q1 order/compatibility question | Resolved through independently attributable D1/D2 context | H1/H2, T5/T6 |
| Existing @keyspace/multiple-category discussion | Context and narrow unchanged-other-membership frame, no FLUSHDB grant | I3, limitations |
| Narrow requested delta | Preserve ordinary processor and other memberships, no special priority | I3, T5/T6/T7 |

Original body is retained byte-for-byte, including CRLF and trailing space. To bind
new documentary obligations legitimately under the existing single-source FRC
envelope, revision 2 uses a **new explicitly attributed composite source identity**:
the unchanged original issue body followed by pinned documentary excerpts identified
as not issue-author text. It does not claim those additions are a newer Redis issue
revision. Context binds both original capture/body/provenance and exact inherited
evidence canonical identity. Each obligation quotes its appropriate issue or documentary
part, and provenance identifies their distinct authority.

Revision 1 and its identities/ambiguity stay unchanged. Existing `check_revision`
accepts the revision-2 lineage: E1/E2/I1/I2 explicitly declared changed, new H1/H2/I3,
no retired IDs. No `resolved: true` mutation is made in the frozen prior FRC; the
new context explains why Q1 no longer supplies a material issue in this new scope.

## Acceptance and review limitations

Seven groups cover isolated read/write grants, reporter configuration, nonzero/DB0
selection, twelve mixed-order rows, four direct-command order controls, and category
membership introspection. Every one of seven obligations has check bindings. All
allow/deny expectations are fixed without generated implementation or test execution.
Permission-denied SELECT cannot execute selection; valid allowed SELECT must change
the connection target. Exact wire strings remain unspecified.

The scope is simple base-command/category lists for fresh users. The reporter's
server version is unknown. The 2022 tutorial describes Redis 6-era ACLs and mentions
6.2/7.0 differences elsewhere; no empirical later-release matrix, alternate selectors,
modules, first-argument/subcommand restrictions, cluster behavior or rollout semantics
is established. These are nonblocking scope limitations, not blanket compatibility
claims. Conflicting evidence or scope expansion would require another review.

Initial review of this exact revised candidate: **SAME_AGENT/SAME_MODEL**, pass 1
of at most 3; no registered research review. Independent public source provenance
and independence from generated implementation do not imply independent cognition.
No verifier/evaluator principal or credential provisioned. Native executable plan/
V1 payload not generated; approval recommendation concerns exact declared WHAT and
fixed acceptance expectations, not a readiness receipt for downstream native execution.
All existing structural, BDI, adequacy, V1, authoring and verification gates remain.

## Verification and preservation

- Three pinned raw documentation files matched SHA-256, byte size and calculated
  Git blob SHA-1; all **15** stored extracts matched literal source bytes. Public
  documentation metadata predates the issue. No implementation provenance used.
- Read-only existing FRC `validate` and `check_revision` pass. Canonical FRC:
  `69d32178bb065e1fa80ac6bb319a1147e3ac7c699a99bb0f56a6db52129ce0f8`.
  These check envelope/provenance/lineage, not natural-language entailment.
- From root, `$env:PYTHONPATH='src'` then
  `python -m benchmark.results.phase6.r5_119a.verify_revision` passes exact original
  source/historical hashes, attributed composite reconstruction, evidence/FRC/plan
  commitments, declared lineage, complete bindings, fixed expectation matrix and
  publication identities. It contains no ACL processor, stage execution or oracle.
- `git diff --check`, whitespace/JSON checks for new artifacts, and protected-scope
  `git diff --exit-code HEAD` pass. Changes limited to additive R5.119A evidence and
  four overview/README/research-log/decision pointers. Compiler/semantics/backend,
  structural/BDI/adequacy/V1, tests and authoring prompts unchanged. R5.116A/R5.119
  and all tracked historical benchmark evidence unchanged. No staging or commit.

## Stop ledger

| Activity | Status |
| --- | --- |
| Public inherited evidence / Q1 analysis | COMPLETE, documented-rule scope |
| Revised FRC / fixed candidate acceptance / human review | PREPARED, ready for human approval |
| Research approval | NOT_GIVEN |
| Research authorization / seal | NOT_ISSUED / NOT_SEALED |
| Baseline Redis probes | NOT_RUN; not necessary given documentation |
| Structural coverage / BDI / adequacy / V1 | NOT_REACHED |
| Lykoi authoring / compilation | NOT_REACHED |
| P6-A03 acceptance / external behavioral verification | NOT_REACHED; zero executions |

**Stop after the revised human review.** There is no P6-A03 first evaluation result,
implementation success or new authority receipt. A subsequent explicit human decision
bound to these exact identities is required; this AI issues no approval.
