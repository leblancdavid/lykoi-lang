# R5.119 — P6-A03 research contract preparation

**`R5_119_P6_A03_RESEARCH_REVIEW_PREPARED`**

Candidate contract and acceptance plan are ready for human review. **Recommendation:
NEEDS_CLARIFICATION**, specifically the source's unresolved ACL grant/revoke
compatibility question. Preparation completion is not approval readiness, a semantic
blocker classification or a first evaluation result.

## Deliverables

1. [Fresh pre-access snapshot](r5_119/SNAPSHOT.md): clean HEAD
   `aaa1121915b7b3786d430460043556e87a7fae8e`, UTC, tree/kernel/version/model/test
   provenance. Kernel remains 26. Relevant tests recorded as historical; no fresh
   tests invoking prohibited stages.
2. [Exact preserved-source verification](r5_119/SOURCE-VERIFICATION.md): only
   R5.116A P6-A03 capture/provenance-named records; no newer source substituted.
3. [Typed FRC candidate](r5_119/FRC-CANDIDATE.json): existing
   `FormalRequirementContract-0.1`, revision 1, stable A03-E1/E2/I1/I2, quoted source
   relations, assumptions, behavioral freedoms and unresolved A03-Q1. Review null;
   no approval, seal or controller registration.
4. [Acceptance-plan candidate](r5_119/ACCEPTANCE-PLAN-CANDIDATE.json): exact
   source/FRC binding, inputs, expected observations, state/error effects and coverage
   limitations; four source-determined checks and two conditional order checks.
   No selected expected outcomes for Q1; no executable native payload or plan seal.
5. [Behavioral interpretation and clarification](r5_119/FORMALIZATION-AND-QUESTIONS.md):
   source-only inventory, bidirectional reconciliation and one material question.
6. [Human approval review](r5_119/HUMAN-REVIEW.md): concise owner-facing summary.
7. This report; [identities](r5_119/IDENTITIES.json) and read-only
   [publication verifier](r5_119/verify_preparation.py) support inspectable binding.

## Central behavioral decision

The owner would be authorizing an attempt to make **either @read or @write grant
SELECT permission without a separate +select**, so a valid explicit SELECT actually
chooses the requested database for permitted operations. This is not an automatic
selection feature or a complete Redis reimplementation.

The reporter expressly questions what happens for `+select +@read -@write`. Their
left-to-right removal hypothesis is not a source-established rule. Allowing SELECT
versus denying it changes observable access for existing configurations. Q1 asks for
that rule, not an internal algorithm; it also covers reversed order and explicit
command denial boundaries. Research approval cannot waive the material question.
Unspecified error spelling, invalid indices, internal representation and persistence
outside this delta are not additional human questions.

## Authority and review disclosure

- Source authority: attributable contributor/reporter proposal by mgravell,
  exact R5.116A retrieved title/body. Redis maintainer approval NOT_ESTABLISHED.
- Research approver: project owner, explicitly appointed in the R5.119 user request
  for research experimentation only. Appointment evidence is that instruction;
  no personal identity, credential provisioning or artifact decision invented.
- Research approval: NOT_GIVEN. Evaluator: NOT_DESIGNATED. Evaluation grant/seal:
  NOT_ISSUED. Product WHAT approval: NOT_ESTABLISHED; production_authorized: false.
- Review: one initial source-only preparation pass, SAME_AGENT/SAME_MODEL. No
  independent-cognition claim or differently named synthetic verifier principal.
  Acceptance is independent of implementation because none is authored/accessed.
  Later registered plan producer must differ from candidate/author principal under
  the unchanged controller. This preparation creates no authoritative wrappers/events.
- Exact artifact digests are preparation identities, not `authority-1` lifecycle
  receipts. Any source-grounded clarification changes material expectations and needs
  linked, freshly identified candidate/plan/review records and a subsequent explicit
  human approval bound to them, including a designated evaluator.

## Verification performed

1. Git clean-state/commit/tree/kernel metadata before source access; snapshot persisted
   first. Source hashes and saved API title/body, issue and author identity checked.
2. Existing `formal_requirements_r5_80.validate` checks candidate envelope, literal
   quote bindings, derivation references and source commitment. It returns canonical
   FRC SHA-256 `69fe6dd3816c184be9af73ad1b8863a6881f579543cd4c99d80cca402b7bc5ab`.
   No `review_gate`, projection, structural or behavioral method invoked. Envelope
   validity proves bookkeeping, not faithful interpretation or completeness.
3. Read-only preparation verifier, from root with `$env:PYTHONPATH='src'`:
   `python -m benchmark.results.phase6.r5_119.verify_preparation` checks selected-source
   hashes/identity/timestamps/repository, exact source equality, candidate commitment,
   six check bindings, literal evidence, unresolved expectations and identity manifest.
   An initial direct script-path invocation failed to import `benchmark`; module
   invocation fixes import context without semantic/tooling changes. Final run passes.
4. Publication JSON/hash/scope and `git diff --check` checks. Source/evidence read
   scope restricted to P6-A03; historical evidence protected by unchanged Git paths.
   Report/helper checks are preparation bookkeeping, not external tests.

## Stage ledger and preservation

| Activity | R5.119 status |
| --- | --- |
| Snapshot, exact source verification | COMPLETE |
| Typed candidate / source inventory / candidate acceptance / human review | PREPARED |
| Research approval / evaluation grant / contract seal | NOT_GIVEN / NOT_ISSUED / NOT_SEALED |
| Structural coverage | NOT_REACHED |
| BDI | NOT_REACHED |
| Adequacy | NOT_REACHED |
| V1 projection | NOT_REACHED |
| Lykoi authoring | NOT_REACHED |
| Compilation | NOT_REACHED |
| External behavioral verification | NOT_REACHED; zero tests/invocations |

This is not a pipeline evaluation and creates no P6_A03_FIRST_RESULT record. R5.117
and R5.118 immutable first results, R5.116/R5.116A curation and R5.118A evidence
remain unchanged. No Lykoi semantics, compiler, backend, structural representation,
BDI, adequacy, V1 or authoring prompts modified. New evidence is additive; overview,
README, research log and decision pointers describe the new preparation boundary.
No staging, commit or source refetch. No fixing PRs, commits, implementation,
comments, linked ticket, P6-A04 or P6-A05 content accessed.

**Stop after this review.** Owner clarification and a subsequent exact-artifact
approval are required before any separately authorized later evaluation. Appointment
and preparation alone supply neither permission to author nor evidence of success.
