# R5.83 candidate B03 evaluation precommitment

**Version: `R5.83-CANDIDATE-1`. Frozen protocol candidate; NOT ACTIVATED.**
Decision: **`R5_83_B03_EXPOSURE_NOT_READY`**. This record creates neither a B03
package nor source/runner/authoring authority. No B03-specific content, inventory,
commitment or eligibility has been obtained. Only a separately authorized future
round can reconsider the blocker. An amendment requires a new prospective version
before protected access; this candidate must never be silently updated into READY.

## 1. Identity and freeze

| Component | Frozen selection |
| --- | --- |
| Boundary | Requirement formalization boundary v1, R5.79 |
| FRC | `FormalRequirementContract-0.1`, R5.80 schema/specification and `formal_requirements_r5_80.py` |
| BDI | `BehavioralDecisionInventory-0.1`, R5.82 specification, `discover` and `adequacy_sidecar` |
| Adequacy | `ImplementationAdequacy-0.1`, R5.81 specification, `analyze` and `authorization` |
| V1 | `BenchmarkDocumentContractV1` → `BehavioralContractV1`, R5.77 specification and existing adapter; no new kinds/meaning |
| Lykoi | v0.3 serialized language and current `src/air_compiler/` snapshot; inherited generic core count **30** |
| Static runner | Existing `phase5_runner_v2.py` only; its static observation authority does not authorize software execution/acceptance |
| Outcome/precedence authority | Sections 3–4 below; stage inventory in the [readiness report](../R5_83-HELD-OUT-EXPOSURE-READINESS.md) |
| Component commitments | Exact physical-byte SHA-256 allowlist in [audit.json](audit.json); no newline normalization/fallback |
| Operational closure | **UNQUALIFIED**: no selected qualified production formalizer/reviewer deployment, complete authoring/execution controller, full dependency closure or independent end-to-end acceptance procedure is claimed |

This freezes the **selection, protocol and known absences**, not an executable
production freeze. The pinned static runner is not repurposed for an implementation
experiment. Deployment identities, isolated admitted inputs, authoring model/tools/
limits, complete dependencies/platform, fresh pre/post integrity checks and an
independent acceptance procedure must be fixed and qualified before any access;
they cannot be chosen after learning B03. Failure to establish them halts admission
as `FORMALIZATION_UNQUALIFIED` or `EVALUATION_INFRASTRUCTURE_FAILURE` with the exact
failed prerequisite. They are not vague conditions conferring conditional readiness.
No value for these missing items is fabricated here.

FRC-0.1 currently admits `SYNTHETIC`/`PUBLIC` provenance only. A protected input
must not be mislabeled PUBLIC to get through its validator. A qualified admission
authority/compatible representation has not been established. Record this as an
input-production boundary, not permission for a format repair in this audit.

## 2. Discovery bounds

Frozen rule keys are **ordering, selection, cardinality, tie, optional,
nullable_predicate, default_trigger_domain, normalization, collision,
invalid_input, duplicates, persistence, transition, retry, failure_atomicity**.
Finite necessary-implication mechanisms are only repeated maxima in exhaustive
declared score states and lowercase collisions/identity in exhaustive declared
string domains. Probe alternatives are not complete behavioral domains.

Known unsupported decisions: **deadline boundary, identity stability, event
ordering, event multiplicity**. Timing, identity and events declared as meaningful
or delegated channels produce UNKNOWN. Serialization, effects and arbitrary other
channels have no qualified discovery rules either. General temporal reachability,
concurrency, arbitrary traces, coupled-decision constraints and arbitrary prose
annotation/entailment/completeness are not qualified. Declared private exclusions
need independent source authority; silence cannot exclude an observation.

No new discovery family, capability, V1 expansion or benchmark requirement change
is part of this candidate. Unknown scope or missing qualification must not be
removed to make a sidecar adequate.

## 3. Frozen outcome taxonomy

Each result records `stage`, one terminal category, exact **native status/code**,
all available findings, affected IDs, evidence commitments, and downstream stages
as `NOT_RUN`. Categories below are reporting distinctions, not new runtime APIs.
Existing native names remain authoritative; aliases are never a second scored result.

| Reporting category | Native classification / use |
| --- | --- |
| `REQUIREMENT_AMBIGUOUS` | FRC/adequacy `NEEDS_CLARIFICATION`, reason = unresolved material interpretation (`AMBIGUOUS_REQUIREMENT` is historical boundary prose) |
| `REQUIREMENT_CONFLICT` | `CONFLICTING_REQUIREMENT`; retain historical plural spelling if reading old records; incompatible source obligations, not mere malformed duplicate packaging |
| `FORMALIZATION_UNQUALIFIED` | `REJECTED`, `INCOMPLETE_FORMALIZATION`, structural/review error, or no qualified independent source/review authority; candidate production/review cannot establish trustworthy complete meaning |
| `DECISION_DISCOVERY_UNSUPPORTED` | `OUTSIDE_ANALYSIS_SCOPE` at discovery/coverage; materially unsupported family/channel, unknown facts, unqualified annotation/reachability/coverage, or unsupported adequacy profile. Subreason distinguishes known family from unqualified general coverage |
| `IMPLEMENTATION_UNDERSPECIFIED` | Same native status; known relevant decisions lack behavioral authority. `next_action: NEEDS_CLARIFICATION` is retained and is not a second ambiguity result |
| `V1_REPRESENTATION_GAP` | Projection `UNREPRESENTABLE_SOURCE / NO_QUALIFIED_COMPLETE_MAPPING` or evidenced faithful-interface gap. Distinguish **missing qualified mapping** from proof of fundamental V1 impossibility |
| `LYKOI_CAPABILITY_GAP` | Existing canonical new-run classification; adequate faithfully represented contract needs an evidenced semantic capability unavailable in the frozen language. Historical `AXIOM_CAPABILITY_GAP` is an alias, not a new result |
| `IMPLEMENTATION_FAILURE` | Capability available, authored/composed/lowered artifact fails required behavior or fails validation/lowering due to implementation error. Record substage; failed behavior verification is not a retroactive capability finding |
| `VERIFICATION_FAILURE` | Verification cannot establish a result: incomplete/invalid/missing oracle evidence, unsupported observation or verifier failure. Do not count as behavioral failure, capability gap or success |
| `EVALUATION_INFRASTRUCTURE_FAILURE` | Operational admission, package integrity/adapter/runner or experimental-control failure; distinguish from source conflict, V1 expressiveness and language capability. Retain native error and observed/attempted activity |
| `SUCCESS` | Approved adequate contract, faithful V1 and implementation pass the frozen independent external behavioral contract, including required preservation/regression checks; validator/static-support PASS alone is insufficient |

Verification and infrastructure categories are necessary reporting additions because
the existing experimental stages do not supply a complete cross-stage outcome
format. They do not introduce semantics or relabel the R5.75 historical result.
Uncertainty about capability versus bug prevents either positive capability
assertion or SUCCESS: report the unresolved verification/evidence failure with
the competing diagnoses retained. A gap requires affirmative support, not a failed test.

## 4. Stage and failure precedence

Order: **0 admission → 1 formalization → 2 FRC review → 3 discovery/coverage →
4 adequacy → 5 faithful V1 projection → 6 Lykoi authoring → 7 validation/lowering
→ 8 external verification → terminal recording/stop**.

1. A failed prerequisite halts the whole downstream chain. Diagnose only from
   evidence already admitted; do not run downstream to choose an easier label.
2. Failed integrity/binding makes the evidence unusable. Halt as infrastructure
   failure (or native malformed/unqualified stage result); do not infer a semantic
   conflict from untrusted artifacts.
3. Within trustworthy FRC/adequacy evidence preserve native precedence:
   **conflict → ambiguity → outside scope → missing authority → adequate**.
   Preserve all findings even though there is one primary result. If fidelity
   already failed, later conceptual diagnostics are secondary, not evaluated stages.
4. Discovery UNKNOWN or unqualified scope/coverage blocks adequacy approval.
   `coverage_reviewed=False` stays the default. A TRUE flag is not its own evidence.
   No hand-authored missing decision, invariant, channel exclusion or exhaustive
   domain may be asserted by an implementer to bypass the gate.
5. Only exact approved FRC + adequate, scope-bound complete analysis proceeds.
   Missing authority cannot become an author's policy, including an assumed default.
6. Projection must cover the **whole** approved adequate contract with independent
   fidelity review. A missing mapping halts without any weakened package/consumer call.
7. Only the faithfully represented approved contract reaches capability analysis/
   authoring. Frozen vocabulary stays fixed; no requirement weakening, generated-code
   edit or external emulation of unavailable semantics can rescue a gap.
8. Validation and lowering failures retain their stage and cause. Unsupported
   semantics require capability evidence; malformed composition is implementation
   failure; tooling/controller breakdown is infrastructure failure.
9. External oracle cases are frozen independently before implementation, tied to
   obligation IDs, domains and observation freedoms. Behavioral mismatch is
   implementation failure when capability is available; invalid/incomplete verifier
   evidence is verification failure. Neither is SUCCESS or a guessed capability gap.
10. First terminal frozen-pipeline result is immutable. No downstream trial,
    interpretation change, repair/retry or second first-result run follows a halt.

## 5. Authority, contamination and evidence

The independent benchmark authority owns source/context and resolutions. Formalizer,
source-WHAT reviewer, discovery/coverage reviewer, projection reviewer, implementer
and verifier have distinct roles and admitted inputs. Identity inequality is not
independence. Trusted deployment and isolation are currently **not qualified**;
the candidate cannot be activated just by assigning different author labels.

Only a future separately authorized independent source step could see sealed prose.
Lykoi development receives an approved sealed faithful V1 contract at its separately
authorized boundary, never hidden acceptance answers or prose for interpretation
inside a static callback. Acceptance inputs/oracle are separately frozen and protected.
No support query, implementation, downstream consumer or hidden test may resolve
source intent, annotation, authority or projection fidelity. Unresolved material
questions halt; B03-specific owner clarification/requirements revision cannot repair
the original frozen evaluation. Any such work is separately versioned research.

Preserve exact admitted inputs/commitments, prompt/model/tool configuration,
transcripts/tool calls, author/reviewer roles/isolation, source coverage/derivations,
unresolved alternatives and witnesses, BDI unknowns/exclusions, adequate-analysis
scope, full projection map/review, model/generated provenance, validator/lowering
outputs and external per-obligation observations. Preserve failures, unrun stages,
budgets and unavailable telemetry as such. Hashes bind evidence, not truthful review
or completeness. Disclose coordinating/shared-context evidence; do not call it blind
or independently qualified. No aggregate score authorizes exposure or SUCCESS.

Before/after future authorized observation record component drift and access/activity
accounting durably. Accidental protected access, unauthorized oracle/solution feedback,
support-driven reinterpretation or protocol drift stops the run and permanently records
contamination. Exposure cannot be undone by deletion, resealing or reverting a commit.
The frozen result must carry the integrity/contamination failure; no pristine claim.

## 6. Post-exposure policy

**Evaluation result:** the first frozen-pipeline result, its original evidence,
limitations, budgets, failures and contamination state remain permanently recorded.
If the attempt stops upstream, that upstream outcome is the result; no language
pass/fail has occurred. Do not extend the static-only runner's permission to execute.

**Subsequent research:** only after recording/stopping the original result and under
separate authority, investigate a discovered gap, modify a future method/semantic
version, clarify requirements or perform diagnostics/regressions. Each later run
references the first result and states **post-exposure, B03-informed**. Never rewrite
the original category into success or present repaired iterations as pristine B03
development. Independent preparation access and development exposure are separately
accounted; any B03-derived development information permanently ends pristine
held-out status for that benchmark. New unseen benchmarks are needed for future
pristine capability evidence.

R5.83 activity is protocol-only. All B03 counters remain zero; status remains
**B03_PRISTINE / B03_NOT_EVALUATED / B03_NOT_EXPOSED_TO_LYKOI_DEVELOPMENT**.
**Stop after the readiness decision. No access authorization is issued.**
