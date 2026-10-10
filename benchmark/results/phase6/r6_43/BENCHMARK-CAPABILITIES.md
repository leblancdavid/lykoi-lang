# R6.43 realistic software-modification capability inventory

Static readiness assessment, not a new application build or acceptance execution.
Sources: [production state/reference semantics](../../../../docs/persistent-references-v1.md),
[atomic state](../../../../docs/atomic-durable-history-v1.md),
[conditional effects](../../../../docs/prewrite-conditional-composition-v1.md),
[historical state](../../../../docs/historical-state-trusted-verification-v1.md),
[R6.16 protocol](../../../../experiments/value_added_r6_16/PROTOCOL.md),
[R6.32 facade specification](../../../../experiments/lifecycle_r6_32/SPEC-1.md),
[R6.39 report](../R6_39-REPORT.md), and [R6.18 semantics](../../../../experiments/typed_composition_r6_18/SEMANTICS-1.md).

## Three distinct infrastructure envelopes

1. Production: bounded typed persistent records, predicates, mutations, related
   entities/references, explicit migrations and cooperating one-store commit.
   Existing generated Python executes without AI. Not unrestricted software.
2. R6.10: bounded byte parsing/assembly pure data VM. No mutable application store,
   network or process effects. It is not a production application runtime.
3. R6.18/R6.32: closed Int64/Bool/Unit arithmetic/check composition and immutable
   definition registry. Registry persistence stores software definitions, not
   mutable application state. Definition callers are not automatically application
   entrypoints; registry migration cannot be substituted for state migration.

The R6.32 application edit facade is a separate production-backed path over the
exposed kiln fixture. It does not give the symbolic wrapper production capabilities.

## Requested practical properties

| Requirement | Current support and evidence | Remaining qualification / boundary |
| --- | --- | --- |
| Existing stateful application | Production and R6.16 saved persistent applications; R6.32 kiln installed-path witness | Exact new baseline/fixtures must be selected and frozen; previous acceptance is not a fresh benchmark result. |
| Interdependent operations | Production declared guards, lifecycle writes and coherent before-state predicates; kiln ignite/set_gate share state | R6.16 adapter covers record-local intent only; broader related-state profiles require their existing normal interfaces, not undocumented adapter expansion. |
| Genuine in-place behavioral changes | R6.32 revise/install generates and installs a successor while retaining store; R6.16 staged changes | revise is fixture-specific; it is not a generic arbitrary application editor. Python comparator can edit its copied source in place. |
| Shared invariants | Production typed predicate invariants applied to candidate/persisted state | Shared requirement fidelity still needs external expected behavior; a well-typed wrong invariant can pass static validation. |
| Multiple callers | Multiple operation entrypoints can observe/update same production store; symbolic direct/transitive callers have explicit immutable pins | No general production callable-symbol linking or adapter support is inferred from symbolic caller migration. Use existing CLI/host entrypoints and a shared store. |
| Regression-sensitive modifications | Existing subprocess oracles can preserve original cases, restart/reload, before/after bytes and selected/retained operations | Need explicit case supersession; passing changed cases alone is insufficient. No new benchmark run here. |
| Independent acceptance expectations | Pre-author seals and external subprocess observation mechanisms exist | Candidate-output independence is attainable; independently sourced/reviewed realistic requirements and reviewer separation are not established by this session. |
| AI-independent execution | Production generated runtime and VM use deterministic data semantics; clocks/IDs can be supplied through declared test capabilities | External services are outside VM; provider test transport must not perform task computation. |

## Outside the supported envelope

- The closed symbolic wrapper has no records, collection application APIs, mutation,
  persistence effects, unrestricted branching/loops or general function calls.
  Adding application logic in a Python transport would change the compared system.
- Production atomicity is one cooperating store with bounded creations (1–8), not
  arbitrary chains of multi-record updates, external transactions or distributed
  recovery. Direct hosts must cooperate with the reservation contract.
- Production checked computations are bounded graphs; no unrestricted arithmetic,
  general recursion, arbitrary callbacks, package-install/process/network semantics
  or native operating-system integration is supplied by the current language.
- Authentication, hostile writers, general concurrency/crash guarantees and
  distributed storage are not established. CLI actor values are selectors.
- Historical changes need explicit source authority; additive field migrations do
  not support arbitrary schema conversion, enum evolution or inferred old roles.
- Authored-text blame and dynamic arithmetic lineage remain unavailable. External
  acceptance must specify raw coordinates or explicitly defined projections.

## Assessment

**Partial readiness.** A small production-backed, record-local modification study
is technically feasible using existing paths. A realistic stateful adaptive-symbolic
comparison on R6.18 is outside its present capability envelope. A robust new study
also lacks an independently reviewed realistic contract and full-workflow measurement
coverage. Neither gap justifies expanding the kernel in this round.

The smallest feasible proposal is [one existing kiln-style application modification](NEXT-EXPERIMENT.md).
This is a bounded exposed-development comparison, not external generalization or
evidence of discovered-symbol advantage. No implementation or AI authoring is begun.
