# Research evaluation approval 1 — R5.118A

Prospective authority/interface policy; no language, compiler or backend extension.
Use with [Phase 6 protocol 2](phase6-generalization-protocol-r5.118a.md).

## Three distinct authorities

| Authority | Supplies | Does not supply |
| --- | --- | --- |
| Source behavioral authority | Preserved externally authored request, exact revision/bytes, attributable obligations and legitimate clarification/context | Automatic upstream endorsement or permission to invent omitted behavior |
| Research evaluation approval | Permission from an explicitly appointed research role/human to experiment against an exact declared interpretation and fixed acceptance plan | Original maintainer intent certification, product WHAT approval, production release/deployment |
| Product WHAT / production authority | Existing owner decisions and applicable release/deployment authorization | A substitute for external behavioral verification |

`RESEARCH_EVALUATION_APPROVED` means **approved for an experiment**, not approved
by the source project's maintainer. Reporter-level source attribution can ground a
research experiment without acquiring upstream product-owner authority. This round's
human instruction authorizes methodology and synthetic testing; it does not appoint
this AI as a research approver or approve any curated external candidate.

## Exact content binding

Reuse `authority-1` wrappers, CJ-1/SHA-256 identity, typed dependency edges,
authenticated project-scoped principals, compare-and-append events and the existing
SQLite artifact/journal store. No new authority database, qualification or service.

1. Preserve the source as a `message` with exact text, origin/revision and capture
   identity/provenance; a `source` depends on it. For an external source include its
   exact external locator/revision and original capture SHA-256 in preserved content.
   Changing text, origin, revision or a dependency changes the identity.
2. The candidate `frc` depends on that source. Full FRC source text must match the
   preserved message. Source attribution alone is not `HUMAN_AUTHORIZED` by an
   upstream maintainer; research binding deliberately does not require that event.
3. A verifier produces `research_plan`, depending on **exact source + FRC**:
   purpose `research-evaluation-only`, `fixed_before_authoring: true`, expectation
   basis `preserved-source`, observable checks with IDs, obligation IDs and expected
   observations, and a coverage-limitations list. Every candidate obligation needs
   an explicit check binding. The verifier must not be the candidate producer or
   an author-role principal. Coverage review must explain finite limitations rather
   than claim universal proof.
4. A reviewer produces `research_review`, depending on **exact source + FRC + plan**:
   obligation-to-source quote traceability, explicit assumptions, nonblocking
   uncertainties, material questions, contradictions, scope determination, review
   context and limitations. Trace quotes must occur in preserved source text.
5. `approve_research` requires an externally provisioned `research_approver` role.
   It binds those four exact identities plus authorized `research_evaluator`,
   purpose, assumptions/uncertainties, review disclosure and authority-event evidence
   in an internal `research_approval`. Candidate producers cannot approve their own
   candidates even if improperly given both roles. Registering a purported approval
   artifact or setting `approved: true` in AI output confers no authority.
6. `begin_research_evaluation` requires the exact designated evaluator credential,
   exact identities and purpose. It rechecks current review/ambiguity and freshness,
   and issues an internal `research_evaluation` once. It grants neither authoring
   nor verification success. Replay requires a separately authorized linked attempt.

The immutable principal registry is provisioned by the embedding authority's
administrator/human, outside producer APIs. Production adoption and owner approval
do not automatically confer the new research role. An unavailable approver is
`NEEDS_CLARIFICATION / RESEARCH_APPROVER_UNAVAILABLE`, not fabricated approval.
Test principals are explicitly synthetic role simulation, never real batch approval.

## Finite, inspectable review

Before authoring, conduct one source-only inventory/materiality/acceptance review,
with at most two correction passes (three registered `research_review` artifacts
per exact FRC; controller refuses a fourth). Each pass must:

- account for every material source obligation and reconcile bidirectionally with
  FRC/checks, identifying source fragments and inherited authoritative context;
- distinguish missing material decisions from irrelevant unspecified behavior;
- state scope, source contradictions, assumptions and genuinely nonblocking unknowns;
- check that expectations came from source/context before generated implementation;
- disclose actual producer/reviewer relationship and access, then recommend or refuse
  approval. The authorized approver makes the explicit content-bound decision.

Prefer a separate context where available. `SEPARATE_CONTEXT` is a disclosure,
not an independent-cognition certificate. `SAME_AGENT` and `SAME_MODEL` are allowed
with explicit limitations; a second pass never becomes independent merely by name.
Unavailable independent cognition is not a research infrastructure blocker. Source-
grounded pre-author expectations and external observations remain mandatory.

The latest review is binding: a newer review makes old-review approval inapplicable;
new material questions/contradictions halt `NEEDS_CLARIFICATION`. Existing FRC
clarification state, blocking/important questions, contract issues and disputed
review evidence also halt. Corrections to material interpretation require legitimate
source-grounded resolution and a new linked candidate/attempt, preserving first results.

Mechanical checks establish identity/role/shape/coverage bindings, **not natural-
language entailment or completeness**. A false source-only attestation can still be
wrong. The reviewer/approver must inspect its substantive meaning; correlated
synthetic fixtures prove interface behavior, not independent source correctness.

## Bounded interpretation

A sufficiently determined source-derived delta may be evaluated without respecifying
the surrounding application. Every material obligation must have source authority;
assumptions are explicit and cannot fill material gaps. No source contradiction or
unresolved material decision can be waived by research approval. Unspecified unrelated
implementation detail remains unspecified. Upstream intent is never certified.

## Existing native pipeline integration

`seal_research_frc` uses the existing `frc_seal` edge with purpose
`research-evaluation-only`, referencing the exact approval and consumed evaluation.
It emits `RESEARCH_FRC_SEALED`, **not** product `APPROVAL_GRANTED` or `ARTIFACT_SEALED`.
Workspace exposes explicit-credential approval/start methods; service credentials
are not silently used as approver credentials. Ordinary workspace product methods
and historical envelope identities remain compatible.

`PipelineController.what` recognizes this research-specific seal and rechecks its
binding. For native execution the approved research plan must include `native_plan`,
the exact source-side acceptance payload. That payload must equal the existing
`expected_plan` supplied by the source-side verifier before authoring. Changing
expectations requires new plan/review/approval; no post-failure oracle adjustment.

All existing structural coverage, BDI, adequacy, faithful V1, plan coverage/review,
plan sealing, author reservation, compiler and external verification checks execute
unchanged. Research approval does not provide any of their receipts or successful
outcomes. The native path labels its eventual author grant `research-implementation`;
grant action remains bounded `author`, and release/deploy actions are refused.
The base non-native controller refuses a research author grant. Product WHAT sealing
still requires product-owner approval and cannot consume a research approval event.

There is no new deployment mechanism. No existing release/deployment authorizer is
made to accept research approvals or research grants. A future production integration
must require its own product/release authority, not just generic implementation state.

Generated output and producer success strings cannot certify success. The existing
external verifier owns observations and classifies them against the fixed plan;
author self-verification remains refused. Finite checked executions are not universal
proof. Revocation/supersession of any bound source/FRC/plan/review/approval dependency
rejects new use while preserving its immutable history.

## Scope and readiness

The [synthetic walkthrough](../benchmark/results/phase6/r5_118a/SYNTHETIC-WALKTHROUGH.md)
demonstrates issuance, consumption, native execution and an externally detected
behavioral failure without product approval. It is public known-answer development
evidence. No actual research approver is appointed for P6-A01–P6-A05 here, and no
external candidate is approved. Subsequent source access/evaluation needs separate
authorization, fresh snapshot, legitimate exact approval and pre-author acceptance.
