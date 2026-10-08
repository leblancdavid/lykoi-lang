# R5.118A — Research-only evaluation authority

**`R5_118A_RESEARCH_EVALUATION_AUTHORITY_READY`**

An explicitly provisioned synthetic research approver issued an exact source/FRC/
acceptance-bound approval, consumed by its designated evaluator and recognized by
the existing native pipeline without product WHAT approval. Research implementation
retained every native gate and external verification. This establishes bounded
**methodology/interface readiness**, not approval or success of an external source.

## Deliverables and integration

1. [Research-only approval specification](../../../docs/research-evaluation-approval-v1.md).
2. `src/lykoi_controller/research.py`: role-checked issuance/start/research sealing;
   existing Controller typed wrappers, journal, identities and stale rejection reused.
3. Minimal Workspace exact-credential approval/start methods and PipelineController
   research-seal recognition/native-plan equality/research grant labeling. Product
   WHAT decisions retain their existing role/events. No controller rebuild.
4. `tests/test_research_authority.py`: **22 focused synthetic controls**.
5. [Synthetic walkthrough](r5_118a/SYNTHETIC-WALKTHROUGH.md) and
   [exact extracted receipt](r5_118a/WALKTHROUGH-RECEIPT.json).
6. [Prospective Phase 6 protocol 2](../../../docs/phase6-generalization-protocol-r5.118a.md).
7. Minimal project, agent/workflow, decision, research-log and README pointers.

## Authority and review finding

Source authority supplies attributable behavioral obligations. Research authority
supplies permission to test a declared interpretation. Product authority supplies
product decisions/release permission. Research approval does not certify original
maintainer intent. A sufficiently determined bounded source delta can be evaluated
without restating unrelated application behavior or requiring upstream approval.

Approval binds source, FRC, review, acceptance plan, assumptions, nonblocking unknowns,
purpose and evaluator. Source quotes, check/obligation coverage, current review,
clarification state and exact native plan are checked. Source-only substantive
completeness/entailment remains a finite disclosed reviewer/approver judgment, not
a mechanically proven property of these binding checks.

Review budget: initial pass plus at most two corrections per exact FRC. Same-agent/
same-model review must be disclosed; no independent-cognition claim from a second
pass. This session used same-agent review and known-answer test roles. No separate
review context or independently authorized real research approver was available.
Unavailable cognition separation is not an automatic infrastructure blocker.

**No real external research approver has been appointed in this round.** The user
authorized methodology/synthetic work, not AI self-appointment or approval of an
external candidate. Test-owned role provisioning is simulation of legitimate
appointment, not an appointment for P6-A01–P6-A05. Without a real appointed approver,
a later external attempt must record `RESEARCH_APPROVER_UNAVAILABLE`; no fabricated
approval or assertion of upstream consent.

## Demonstration and negative controls

The retained walkthrough at `2026-10-08T15:00:11.780985+00:00` uses public synthetic
R5.80 calibration with a fixed source-side store acceptance check. Research approval
revision 9 → evaluator consumption 11 → research seal 13 → native stage checks →
plan seal 35 → research grant 39 → author reservation 41 → external verification 49.
Plan sealing precedes authoring, and its payload is identical to the preapproved
research plan. Product `APPROVAL_GRANTED` events: **zero**.

The deliberately unrelated existing task CLI compiles, but exits 2 on required
`store`, returns empty stdout and produces no measurement file. One retained
walkthrough acceptance case / one subprocess invocation gives native
**`BEHAVIORAL_VERIFICATION_FAILURE`**, not success. This demonstrates legitimate
experimental permission and refusal of generated self-certification; it does not
demonstrate satisfying that synthetic contract or external generalization.

| Control | Observed |
| --- | --- |
| Research token or research grant used for deployment/release | Refused; no product WHAT seal/approval acquired |
| Source A approval with source B | `RESEARCH_IDENTITY_MISMATCH` |
| FRC A approval with changed FRC B | `RESEARCH_IDENTITY_MISMATCH` |
| Changed acceptance-plan identity or native payload | Identity/binding refusal |
| Material ambiguity, contradiction, blocking clarification | `NEEDS_CLARIFICATION` |
| Structural, BDI, adequacy fault | Original native stage refusal, no grant |
| Unsupported V1 | `UNREPRESENTABLE_SOURCE`, no authoring |
| Wrong but compilable generated target | External behavioral failure |
| Author binds verification | `SELF_VERIFICATION` |
| Unapproved candidate status/approval strings | Inert; reserved approval registration and producer approval refused |
| Wrong approver role / candidate self-approval | `ROLE_DENIED` / `RESEARCH_SELF_APPROVAL` |
| Wrong evaluator/project, replay, revoked dependency, newer review | Refused; old artifacts remain inspectable |

Source quote presence cannot prove faithful interpretation. Deliberately corrupted
synthetic relation mappings test that later native gates still halt even if a
fallible source review accepted them. They are fault injections, not legitimate
external behavioral obligations or evidence that ambiguous sources were approved.

## Verification

From repository root, `$env:PYTHONPATH='src'`:

| Command | Passed tests |
| --- | ---: |
| `python -m unittest discover -s tests -p test_research_authority.py -v` | 22 |
| `python -m unittest discover -s tests -p test_authority_controller.py -v` | 34 |
| `python -m unittest discover -s tests -p test_requirements_workspace.py -v` | 26 |
| `python -m unittest discover -s tests -p test_sealed_pipeline.py -v` | 30 |
| `python -m unittest discover -s tests -p test_compiler.py -v` | 22 |
| `python -m unittest discover -s tests -p test_application.py -v` | 9 |
| `python -m unittest discover -s benchmark/harness -p test_baseline.py -v` | 3 |
| **Total distinct focused/relevant tests** | **146** |

Model validation and safety passed: zero capability violations and invalid
transitions. Existing code paths/regressions, not external requirement evaluations,
were exercised. The initial focused-test fixture had a missing Workspace formalizer
credential; corrected before the final passing run. Later focused reruns verified
new native-path and defensive-input controls; they are development testing, not
rewritten benchmark first attempts.

Scope/preservation: `git diff --check` plus whitespace checks for each new file;
Git metadata comparisons against verification HEAD
`8f412f056fca7542f5f35ca37a71410c0a67f136` for R5.116A/R5.117/R5.118 and all
other tracked historical evidence, language
specifications, compiler/backend, profiles/mappings, schemas, model and generated
files. Curation integrity checked without opening source/acceptance content. New
research result files are additive. No commit, runtime freeze, qualification service,
isolation service, telemetry or protected-source infrastructure added. Existing
native component-manifest checks are reused, not new runtime eligibility gates.

`git diff --exit-code HEAD -- benchmark/results src/air_compiler src/lykoi_query
schema air generated benchmark/evaluation benchmark/semantic` returned no diff.
Tracked code diff contains only controller/workspace interface edits; the new
research mixin and focused test are additive. JSON receipt parsing passed. Initial
working tree was clean; no user work was overwritten or staging/commit performed.

## Historical boundary and stop

P6-A01 first result remains `NEEDS_CLARIFICATION` for material ambiguity; P6-A02
remains `NEEDS_CLARIFICATION` for unavailable required FRC approval. Their records,
classifications and stage ledgers are immutable. No rerun, repair, reinterpretation
of those first results or R5.116A curation modification. P6-A03–P6-A05 source/acceptance
content not accessed/evaluated. No external requirement evaluation in this round.

The R5.114 implementation/kernel remains **26**, with zero additions/removals/
reclassifications. Only bounded research authority/interfaces and documentation
changed; no semantic producer, compiler or backend behavior changed.

**Stop after methodology/interface verification.** P6-A03 is next in the preserved
batch and the methodology can support a separately authorized first attempt. Its
source-specific readiness/ambiguity/acceptance cannot be asserted without access;
no actual approver, FRC approval or evaluation grant for it exists here.

## Completion answers

1. **Without maintainer approval?** Yes for legitimate research-only experiments,
   with appointed research approval and source-grounded fixed expectations.
2. **Distinct research/product authority?** Yes; different roles, events, purposes.
3. **AI producers manufacture approval?** No; recommendations/candidate assertions
   are inert and self-approval is refused.
4. **Material ambiguity blocking?** Yes, `NEEDS_CLARIFICATION`.
5. **Criteria fixed before authoring?** Yes, exact pre-author plan/native payload.
6. **Exact source/FRC binding?** Yes, typed content identities and dependency checks.
7. **Production protected?** Yes; no product WHAT approval or deployment permission.
8. **P6-A01/P6-A02 preserved?** Yes, no rerun or first-result edits.
9. **P6-A03–P6-A05 unexposed here?** Yes; no content access/evaluation.
10. **P6-A03 ready?** Methodology-ready for separate authorization, not source-specifically
    reviewed/approved or authorized to execute yet.
11. **Kernel unchanged?** Yes, 26.
12. **Infrastructure expansion avoided?** Yes; existing authority/artifact mechanisms
    reused with the requested minimal scoped distinction.
