# Lightweight generalization protocol 1 — R5.115

Prospective documentation, extending the simplified R5.96 first-result discipline.
Use with the [source-independence policy and plan](phase6-research-plan-r5.115.md).
This document creates no executable infrastructure or actual evaluation case.

## Per-requirement first attempt

1. **Snapshot before semantic access.** Record UTC, commit/root tree, status/diff and
   relevant untracked contents, kernel ledger/count, profile/representation/compiler/
   backend identities, relevant test results and known failures, model/provider when
   available and useful environment provenance. A dirty tree is recorded and retained,
   not silently treated as HEAD or prohibited by machine eligibility.
2. **Bind the independent source.** Curator records exact artifact identity/hash,
   origin/revision, selection rule, legitimate authority and prior exposure declaration.
   Record first semantic delivery UTC and recipients; thereafter it is development-exposed.
3. **Formalize against authority.** Use current FRC, independent source-only obligation
   inventory/reconciliation, legitimate clarification and owner approval as applicable.
   Preserve questions and exact authorized answers with versions; no invented defaults,
   migrations, roles or errors. Predeclare a finite clarification/review budget. On missing
   authority, unresolved ambiguity or exhausted budget record the terminal result.
4. **Attempt unchanged capability pipeline.** FRC → structural coverage → BDI →
   adequacy → faithful V1 → restricted application/model authoring → deterministic
   compiler/backend. Authoring an application with existing capabilities is permitted;
   changing shared semantics, mappings, profiles, representation rules, compiler/runtime,
   prompts supplying new capability knowledge or source-specific bypasses is not. Fix
   author/model-call/time budgets before access. Intermediate review is retained; a
   terminal halt is never repaired and retried as the same first attempt.
5. **Verify externally when reached and authorized.** Independent source-derived criteria
   and expected observations are reviewed and fixed before implementation authoring.
   Run permitted external subprocess/controlled-host tests against the exact built
   artifact, observing outputs, durable effects, rejection, preservation and restart
   when demanded. No oracle feedback repairs before first-result recording.
6. **Publish the first terminal record immediately.** Preserve native classification,
   exact blocker stage, artifacts/logs, evaluated snapshot and coverage. All stages after
   a blocker are `NOT_REACHED`; do not infer their failure. A reached but unexecuted check
   is `NOT_RUN` with reason. Inability to execute evaluation is visible, never success.
7. **Stop before remediation.** Preserve the record unchanged in a new versioned result
   file under `benchmark/results/phase6/` when that future round occurs. Later corrections,
   clarification answers, infrastructure retries and capability improvements are separately
   identified linked records, not overwrites. Informed attempts are post-exposure evidence.

The first terminal result includes infrastructure failures; a later successful retry
does not replace it. Each batch retains its first-attempt denominator and separately
reports interpretable semantic/behavioral subsets. No elaborate machine freeze,
qualification registry or protected activation is necessary.

## Minimum first-result record (manual Markdown or JSON is sufficient)

- Evaluation/attempt ID, UTC chronology, protocol version, exact snapshot identity and
  retained local diff; tests, kernel/profile/backend/model provenance.
- Source identity/hash/revision, origin/authority, independence declaration and limits,
  first exposure, selection rationale, source/clarification artifact links.
- Approved or disputed FRC, source obligation inventory/reconciliation and any review
  limitations; structural/BDI/adequacy/V1 and authored/build artifact identities when reached.
- Stage ledger: each actual stage status, native code/reason and evidence; downstream
  `NOT_REACHED` and reached-but-unexecuted `NOT_RUN` distinguished.
- One normalized terminal outcome, exact native outcome(s), first blocker stage and
  causal category with confidence (`unknown` permitted). Secondary observations do
  not replace the earliest blocker.
- Acceptance source/authority and pre-author plan identity, executed cases/invocations,
  actual/expected observations, failures, coverage exclusions and unverified behavior.
- Concept/composition ledger and separately labeled possible gap analysis; optional
  telemetry or `N/A`; remediation transition only after first record exists.

Store source/acceptance material only where authorized; a result can identify a retained
private artifact without publishing it. Immutability is procedural and Git-versioned,
not a new database, activation service or token-accounting dependency.

## Result taxonomy

Normalize for cross-case reporting while retaining native codes verbatim. Stage and
cause are separate axes: an unsupported stage does not prove an irreducible semantic gap.

| Outcome | Meaning / first blocker |
| --- | --- |
| `SUCCESS` | Complete source-authorized obligations represented and compiled; all authorized required acceptance checks executed and passed, with finite coverage limits disclosed. Native `BEHAVIORALLY_VERIFIED` alone cannot supply independent source evidence. |
| `NEEDS_CLARIFICATION` | Legitimate source ambiguity/conflict or unavailable answer/approval; usually FORMALIZATION/RECONCILIATION. Native `DISPUTED` retained. |
| `FORMALIZATION_FAILURE` | Producer/reconciliation cannot establish a valid faithful FRC despite sufficiently specified authority; malformed or lost obligations, not guessed requirements. |
| `STRUCTURAL_UNSUPPORTED` | Current structural bridge/profile cannot completely cover the approved obligations. Preserve native codes such as `STRUCTURAL_COVERAGE_FAILURE`. |
| `BDI_UNSUPPORTED` | Behavioral decision discovery cannot cover required choices/interaction meaning at BDI. |
| `ADEQUACY_UNSUPPORTED` | Implementation-adequacy analysis cannot establish the required authorized implementation space. |
| `REPRESENTATION_UNSUPPORTED` | Faithful complete V1/program representation unavailable; retain e.g. `UNREPRESENTABLE_SOURCE` and exact reason. |
| `LYKOI_CAPABILITY_GAP` | Explicitly evidenced absence of required existing semantic capability, where the native halt is a capability refusal. Record the actual stage. Never inferred merely from a bridge/backend failure. |
| `AUTHORING_FAILURE` | Author fails to produce a valid faithful candidate within existing supported capabilities/budget. |
| `COMPILATION_FAILURE` | Reached compiler rejects/fails to build the candidate; distinguish invalid authored artifact from supported-profile lowering defect in cause notes. |
| `RUNTIME_FAILURE` | Built target crashes/cannot perform required execution for a target/runtime reason. Source-required rejection is not a crash. |
| `BEHAVIORAL_FAILURE` | Executed software observations contradict independently authorized expected behavior; include exact failed criteria. |
| `EVALUATION_INFRASTRUCTURE_FAILURE` | Harness, transport, missing executable adapter, access or observation failure prevents a trustworthy conclusion at any stage; not a software/semantic verdict. |

When a stage-specific native unsupported code is emitted, use its stage-specific
normalized outcome and annotate a confirmed capability gap as cause if justified.
Use `LYKOI_CAPABILITY_GAP` as the terminal outcome for explicit capability refusals
without a more specific native stage category; do not double-count one attempt.
If acceptance cannot be independently established or executed, explain that precise
prerequisite under clarification or evaluation failure rather than assigning `SUCCESS`.
Predeclare budget exhaustion as the corresponding stage failure with its native/budget
reason; do not invent an unexecuted behavioral failure.

## Behavioral correctness and evidence strength

Acceptance derives from the independently authored source and authorized clarification,
not generated code, its tests, implementation choices or its own success assertions.
An evaluator/source reviewer independent of the implementation author prepares criteria
from source-only material; discrepancies between source inventory, FRC and criteria
require legitimate authority resolution. Review and fix criteria before authoring;
retain all material positive, negative, boundary and preservation obligations. Software
authors cannot alter expectations after observing failures.

Use black-box output and durable-state observations; verifier-owned controlled-host
contexts may supply declared actors without claiming authentication. Criterion-to-source
traceability and coverage tables identify executed, excluded and unverified behavior.
Report separately:

1. **Contract-derived verification:** proves consistency with the approved FRC/plan
   in tested executions, potentially sharing formalization errors.
2. **Independent acceptance evidence:** expectations established from legitimate
   original source authority independently of implementation authorship.
3. **Bounded finite coverage:** actual cases/domains/paths and invocations, not universal
   proof; report uncovered behaviors and assumptions even after a passing result.
4. **Unverified behavior:** unexecuted paths, unsupported obligations, inaccessible
   source authority or broader security/portability claims.

Same-agent synthetic approval/oracle evidence must remain labeled development evidence;
it cannot masquerade as independent held-out acceptance. Public-source provenance does
not by itself make an implementation-derived oracle independent.

## Kernel-growth accounting

For every first attempt preserve baseline **26** (or the declared later baseline),
source obligation IDs and a table with: existing core concept IDs/names used; exact
compositions; involved profile/interface; backend dependency; blocker and evidence;
implementation-specific behavior; unknowns. Partial use is recorded even when later
stages halt. No downstream inference from a blocked stage.

After the immutable result, separately investigate proposed new core candidates. For
each record its meaning, why existing compositions cannot express it, alternative
decompositions, reusable examples beyond the triggering source, interactions, authority
and validator/backend obligations, and admission decision. New functionality (e.g. a
workflow) is not automatically new irreducible meaning. Maintain original count,
candidate count, admitted additions/removals/reclassifications and resulting count;
link prospective ledger revisions without retroactively changing baseline entries.

| Causal category | Evidence required |
| --- | --- |
| Existing composition | A faithful decomposition into identified current meanings, respecting actual bounds and authority; not an opaque host-language escape. |
| Integration gap | Existing semantics suffice but FRC/structure/BDI/V1/dispatch/input/context interfaces cannot carry or connect them. Identify the lost binding/facet. |
| Backend gap | Meaning is represented but target lowering/runtime/storage adapter does not implement it correctly or at all. Identify target-specific evidence. |
| New semantic candidate | A required independently observable relation is absent even after supported compositions are considered. Justify irreducibility prospectively; a failed test alone is insufficient. |
| Implementation-specific behavior | Unicode/time/serialization/resource/platform choices not independently authorized as core meaning; identify observable dependence. |
| Authority/evaluation/authoring issue or unknown | Missing clarification, producer error, inadequate oracle, infrastructure or author mistake; no kernel addition inferred. |

Counts describe hypotheses and implementation coverage, not a minimum proof. Neither
hide new meaning inside adapters to preserve 26 nor expand the kernel for every bridge
repair. Report per-case reuse, integration/backend gaps and growth over ordered cohorts;
all attempted cases, including disputes and failures, remain in the result inventory.
