# R5.120A — Lightweight local research execution

**`R5_120A_LOCAL_RESEARCH_EXECUTION_READY`**

Exact human-approved research artifacts can be consumed locally through existing
semantic stages without acquiring production authority. Qualification is synthetic
only. Production authentication/approval/seals/grants/journal behavior is unchanged.

## Deliverables and evidence

1. [Local execution specification](../../../docs/local-research-execution-v1.md).
2. Minimal receipt/runner: `src/lykoi_research/local.py`; callable entry point `execute`.
3. Isolation/exact-binding/stage/external-behavior tests: `tests/test_local_research.py`.
4. [Synthetic receipts and observations](r5_120a/SYNTHETIC-EVIDENCE.json),
   [qualification/checks/preservation](r5_120a/QUALIFICATION.md).
5. [Prospective Phase 6 protocol 3](../../../docs/phase6-generalization-protocol-r5.120a.md).
6. Additive current-boundary/project/decision/research-log guidance.

## Findings

The local runner has no production database/credential/registry/role interface and
constructs no controller. It reuses the existing FRC, structural coverage, BDI,
adequacy, faithful V1, acceptance coverage, restricted author subprocess, compiler
dispatcher and external execution/classification functions. No semantic implementation,
backend behavior or expected result is changed. Exact human approval is a retained
trust input, not a new authority service or cryptographically authenticated principal.

The public synthetic library contract passes every semantic/author/compiler/verifier
stage: **5 cases / 17 external process steps**. The public P01 wrong-but-compilable task
CLI fails its fixed store expectation with exit 2 and missing measurement file:
**BEHAVIORAL_VERIFICATION_FAILURE**. Native unsupported-stage controls retain structural,
BDI, adequacy and V1 first blockers and downstream `NOT_REACHED`. Missing executable
acceptance payload is an explicit blocker, never a generated replacement oracle.

Production rejects local receipts as credentials or approval/grant artifacts, refuses
reserved-type imitation and refuses a receipt inside a registered context as a grant.
An actual local run leaves test production database bytes/revision/events unchanged.
Production denial auditing remains intact. Tests disclose synthetic role simulation;
no real production authority is provisioned. The interface does not claim hostile
OS containment, independent cognition, upstream endorsement or universal correctness.

**146 distinct relevant tests pass**, including 13 new local controls and existing
authenticated research/production/pipeline/compiler/application/scalar/harness regressions.
Model validation/safety pass; whitespace/scope/preservation checks pass.

## Completion questions

1. **Can exact human-approved research artifacts be consumed locally?** Yes. The
   separately retained human statement/provenance, evaluator and source/FRC/plan
   hashes must match the receipt; no production administrator credentials required.
2. **Is production authority unchanged?** Yes. No existing controller/security file
   or rule changed; local execution creates no production approvals, seals or grants.
3. **Can research receipts be rejected by production authorization?** Yes. Observed
   authentication, reserved-type, grant-subject and applicability refusals demonstrate it.
4. **Are source/FRC/acceptance identities enforced?** Yes. Full canonical content
   hashes, FRC-source equality, exact human statement/provenance and snapshot are checked.
   Changed expectations are rejected before authoring; no artifact substitution.
5. **Are semantic stage gates preserved?** Yes. Existing semantic functions execute
   in sequence, with native outcome checks and first-blocker halt. This does not
   manufacture controller-authenticated review/seal receipts.
6. **Does independent behavioral verification remain authoritative?** Yes. Fixed
   source-side expectations and the unchanged external subprocess verifier classify
   behavior. Same-agent source interpretation is separately disclosed.
7. **Can a wrong implementation fail?** Yes. Wrong but compilable public target
   fails external store verification; compilation is not success.
8. **Is the 26-concept kernel unchanged?** Yes, including FRC/BDI/adequacy/V1/compiler/
   lowering/backend and R5.114 accounting. Only the research interface and supporting
   tests/documentation/evidence are added.
9. **Were historical first results preserved?** Yes. R5.117/R5.118/R5.118A/R5.119/
   R5.119A/R5.120 unchanged; P6-A03 remains `NEEDS_CLARIFICATION /
   RESEARCH_APPROVER_UNAVAILABLE` under its original approval workflow.
10. **Is P6-A03 ready for a separately authorized post-first-result evaluation?** The
    local interface is ready to support such an attempt without production credentials.
    **P6-A03-specific executable acceptance/backend integration is not established.**
    R5.120 already records the approved plan's null native payload; this round neither
    replaces it nor tests Redis. Separate authorization, explicit prior-result linkage,
    exact approval/evaluator binding and a fixed approved executable acceptance
    representation are still required. Unsupported integration must halt honestly;
    no simplified simulation may be called full Redis success.
11. **Was infrastructure expansion kept minimal?** Yes. One small local runner and
    one test module; no auth service, research controller, runtime/model/OpenCode
    qualification, protected-source machinery or deployment infrastructure.

## Stop

Stopped after synthetic qualification. No P6-A03 evaluation, software authoring or
compilation; zero Redis executions. No P6-A04/P6-A05 inspection. A later P6-A03
execution must be a separately authorized **linked post-first-result research attempt**,
preserving its first result and approved acceptance expectations.
