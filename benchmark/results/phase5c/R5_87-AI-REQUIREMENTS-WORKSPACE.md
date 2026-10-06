# R5.87 — AI Requirements Workspace Implementation

## Result and scope

**R5_87_REQUIREMENTS_WORKSPACE_IMPLEMENTED** in public synthetic engineering scope.
The executable service completes human intent → candidate formalization → meaningful
clarification → adopted policy application → source-only inventory commitment →
deterministic reconciliation → exact human approval → controller-sealed FRC.

Delivered code: [`src/lykoi_workspace/`](../../../src/lykoi_workspace/).
[Interface and limitations](../../../docs/requirements-workspace-r5.87.md),
[26 workspace challenges](../../../tests/test_requirements_workspace.py),
[verification summary](r5_87/verification.json),
[public example evidence](r5_87/example-evidence.json) and
[wizard transcript](r5_87/WIZARD-TRANSCRIPT.md) accompany this report.
The unchanged R5.86 controller is the sole authority mechanism. No concrete controller
correctness defect requiring redesign was encountered.

## Delivered engineering

- Cohesive session abstraction managing exact source versions, obligations, issues,
  questions/answers, policies, candidate contracts, committed inventories,
  reconciliation, approvals and controller identities. Journal-derived restart state.
- Exact text ingestion and source supersession; immutable R5.80 nested FRC records,
  conservative stable logical IDs, revision/retirement checks and separate identity/
  authority/provenance ledgers. Clarification never mutates a previous FRC.
- Bounded question priorities; required product decisions use controller-authorized
  human answers. Explicit answer replacement retains other decisions and invalidates
  affected historical approval/seal authority through controller dependency closure.
- Minimal scoped Project Policy Contract adoption, exact evidence identity, DEFAULT /
  FEATURE_EXCEPTION precedence, visible non-waivable conflicts and policy invalidation.
- Formalizer/reviewer structured-output adapters with distinct session identities and
  recorded provider/model provenance; future model callbacks require no network here.
- Fresh deterministic producer subprocesses, fixed stdin input allowlist, empty
  environment and no controller object/credential input. Reviewer's normal interface
  cannot receive candidate data. Reconciliation access requires exact committed SOI
  and controller REVIEW_STARTED binding. Isolation class is
  PROCESS_SEPARATED_FIXTURE_NO_OS_SANDBOX, not model/provider independence.
- R5.84 SOI concepts, exact quote/offset text accountability, meaningful item-level
  inventory, separate per-item interpretations/authority and independent context.
- Deterministic bidirectional reconciliation: matched, missing source obligation,
  unsupported FRC invention/authority, divergent interpretation, ambiguity, unsupported
  scope and unresolved mapping. A broad umbrella cannot supply item mappings.
- Material disagreement receives DISPUTED controller review and a concise human
  question. One initial review plus one bounded correction re-review per lineage;
  exhaustion persists across restart and halts visibly. No AI adjudicator recursion.
- Human commitment summary and exact-version approval, followed by the real controller
  WHAT seal. The normal-user transcript hides hashes; audit evidence retains them.
- Requirements-recovery provenance extension point, without implementing recovery
  or converting observed behavior into automatically authorized intent.

## Verification evidence

| Verification | Actual result |
| --- | --- |
| Workspace/lifecycle/policy/blindness/reconciliation/adversarial/controller-integration/sealing/restart | **26/26 PASS**, 33.504 s. |
| Existing unchanged R5.86 controller suite | **34/34 PASS**, 38.550 s. |
| Compiler/application | **31/31 PASS**, 4.909 s. |
| Selected historical R5.80–82/R5.84/V1 | **104 PASS / 2 FAIL** out of 106, 3.577 s. |
| Model validation/safety | PASS; zero capability violations / invalid transitions. |
| Public example and read-only LF diagnostics | PASS; exact source/FRC/SOI/approval/seal bindings published. |
| Whitespace/change-scope | Scoped checks PASS; only new workspace/tests/R5.87 records and current project documentation. |

Workspace suite is an explicitly named root test file. Historical selections are
`benchmark.evaluation.test_formal_requirements_r5_80`,
`test_implementation_adequacy_r5_81`, `test_behavioral_discovery_r5_82`,
`test_source_coverage_r5_84`, and `test_benchmark_documents_v1`.
These are the existing public/synthetic guarded suites, not broad benchmark discovery.
Existing public synthetic R5.83 regression helpers do not activate its candidate.

The two historical physical-byte failures are the known Windows CRLF pin issue:

1. R5.80 `test_reproducible_results_and_exact_coverage_locators`: public B01 bytes
   differ from its historical pin; six CRLF sequences normalized read-only to LF
   match `b7b2d714db5cee566e9e55982dd4c4d95d3d57f0c341e04ba1e15c24e9a8e94d`.
2. R5.84 `test_independent_disagreement_and_public_b01_calibration`: independent SOI
   bytes differ; 120 CRLF sequences normalized read-only to LF match
   `ff124b66301901a9e945338ccad1a354f8e393d8fe9175f06d1fbf3068d29d44`.

[Evidence](r5_87/example-evidence.json) records physical and LF hashes separately.
**The original tests remain failed in this checkout.** No pin, historical file or
normalization bypass was changed. Logical/LF diagnostic matches are not reported as
passing physical-byte tests.

Verification uses the previously installed official CPython 3.12.10 embeddable amd64
interpreter under the approved temporary directory, with explicit repository/src
`sys.path` bootstrapping. `python` is absent from PATH and the available `py` is 3.9.
No third-party dependency or repository runtime configuration was introduced.

Initial workspace verification exposed a fixture revision defect: the deliberately
omitted obligation still had a meaning-change lineage reference. The test was corrected
to omit the obligation from its first candidate, retain the human question, and later
introduce the previously absent logical ID. The failure was in new engineering/test
setup, not a controller defect or a rewritten historical result.

## Decisive challenges

**Omission:** source contains title creation, optional priority and important-task
listing. Formalizer omits listing; independently configured source reviewer identifies
all three. Reconciliation detects SOURCE_OBLIGATION_MISSING. Owner approval and seal
deny. The human confirms listing, revised formalization restores it, bounded re-review
succeeds and the exact revised FRC seals.

**Invention:** formalizer adds plausible alphabetical ordering with a real source
quote and real source authority identity. Independent inventory contains no such
obligation. Reverse reconciliation identifies FRC_OBLIGATION_LACKING_AUTHORITY and
denies approval/sealing. A separate test rejects invented input-domain restrictions
and invented freedoms as material context divergence.

**Disagreement:** source reviewer says one highest-priority task while the formalizer
says all matching tasks. Reconciliation is disputed; product question asks one versus
all. Human resolution creates a new source root; bounded corrected review/seal proceeds.

**Policy:** elected unconstrained-order policy supplies exact default authority.
Feature-specific newest-first source overrides a waivable policy with explicit
FEATURE_EXCEPTION evidence. Non-waivable conflict remains visible and cannot approve.
Policy supersession makes retained downstream approval/seal ineligible for new use.

**Clarification version:** initial draft → priority question → NORMAL answer → revised
contract → exact approval/seal. Replacing NORMAL with LOW produces a new answer, root,
FRC and seal; old approval/seal cannot authorize the changed graph and are stale.

**Correlated agreement:** both fixtures wrongly treat the listing clause as context,
not behavior. They agree, and an approving synthetic human can seal the incomplete
summary. The externally declared expected inventory still identifies the lost listing.
This negative control deliberately demonstrates that agreement is not universal
semantic truth; the architecture does not mathematically eliminate shared error.

**Persistence/finite review:** actual separate-process restart reproduces sealed
workspace status. Two disputed review commitments exhaust the lineage's budget;
restart cannot reset it or silently launch a third review.

## Public example and authoring boundary

The executable public task wizard asks what omitted priority means and what “important”
means. The synthetic human chooses NORMAL and HIGH; an adopted synthetic policy leaves
list ordering unconstrained. Independent source inventory identifies all commitments,
reconciliation succeeds, the human approves the exact displayed behavior, and the
controller seals the FRC. Run `python -m lykoi_workspace.example` with `PYTHONPATH=src`;
`--audit` displays exact artifact bindings. No actual Lykoi implementation follows.

The seal binds a requirements-only structural disposition marked UNSUPPORTED for
authoring projection, using R5.86's existing WHAT-only facility. No faithful structural
projection, supported discovery, adequacy, V1 projection, independent sealed
verification plan or implementation grant is claimed. Explicit unsupported required
scope/proposed structure in the candidate instead halts reconciliation.

Before authoring: independently reviewed complete structural projection and qualified
coverage; supported bounded BDI and authority-complete adequate decisions; faithful
complete unchanged-V1 mapping; independent verification plan sealed before dispatch;
exact executable freeze and controller implementation grant; restricted author/build
and independent verifier execution closure. Production use additionally needs real
scoped human authentication, qualified semantic producers and stronger enforced blind
worker containment. Those remain subsequent separately authorized work.

## Protection and stop

**B03_PRISTINE / B03_NOT_EVALUATED /
B03_NOT_EXPOSED_TO_LYKOI_DEVELOPMENT** remain true by inherited status and scoped
public-only activity. All B03 access, content-revealing metadata, inference,
formalization, review, authorization, packaging, observation and execution/activity
counters remain **zero**. No protected source/metadata/ledger inspection occurred.
**R5.83-CANDIDATE-1 remains unactivated**. Controller, compiler, runtime/schema,
generated files, Lykoi semantics, V1 and R5.82 families retain their content. Core
**30** inherited; Phase 5C paused. **Stop after R5.87.**

## Final answers

1. **Can the wizard create behavioral authority without the human/controller?** No;
   candidate output cannot manufacture any authority event.
2. **Can an independently committed inventory catch an omission?** Yes, demonstrated
   with three material source obligations and one omitted candidate obligation.
3. **Can invented behavior be prevented from sealing?** Yes, when independent inventory
   challenges it; invention/unsupported authority blocks. Correlated semantic error
   remains a documented limitation, not a universal prevention proof.
4. **Do changed clarification/policy dependencies invalidate affected authority?** Yes,
   using exact controller supersession/invalidation and normative dependency closure.
5. **Can material disagreement return to the human?** Yes; DISPUTED evidence routes
   to product-level clarification, followed by bounded fresh review or visible halt.
6. **Can the complete public example reach a controller-sealed FRC?** Yes; exact
   source/inventory/approval/seal identities and transcript are published.
7. **What remains before safe Lykoi authoring?** Reviewed structure, qualified coverage,
   supported discovery/adequacy, faithful V1, sealed independent verification planning,
   executable freeze and controller grant, plus restricted author/build/verifier closure.
   Production AI formalization is not qualified by this engineering round.
