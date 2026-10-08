# R6.17 — AI-native symbolic software construction: charter and design

**Final classification: `R6_17_SYMBOLIC_RESEARCH_DESIGN_READY`.**

This is a bounded documentation-only research revision. Ready means the hypothesis,
comparators, lifecycle, controls, accounting and stopping rules are sufficiently
specified for separate implementation authorization. No adaptive vocabulary exists
from this round and no hypothesis has been demonstrated.
Harness guidance already supplied a same-round readiness/design summary; the
inventory discloses that priming. This proposal is not independently derived evidence.

## Published deliverables

| Deliverable | Publication |
| --- | --- |
| Revised definition/charter, local architecture, minimal roadmap, open questions | [Charter proposal](../../../docs/symbolic-research-charter-r6.17.md) |
| Historical capability/evidence inventory and changed architectural defaults | [Evidence inventory](r6_17/EVIDENCE-INVENTORY.md) |
| Five representation alternatives and recommendation | [Representations](r6_17/REPRESENTATIONS.md) |
| Proposal/type/validation/identity/version/retrieval/composition/revision/lowering/audit lifecycle | [Lifecycle specification](r6_17/ABSTRACTION-LIFECYCLE.md) |
| Three-track design, fixed-capacity control, development/freeze/generalization, contamination controls, metrics/stopping rules | [Experiment design](r6_17/EXPERIMENT-DESIGN.md) |
| Publication integrity and scope checks | [Verification](r6_17/VERIFICATION.md), [identities](r6_17/PUBLICATION-IDENTITIES.json) |

## Decisions and interpretation

Proposed Lykoi: local, provider-independent AI-native symbolic construction with
deterministic meaning and LLM-free execution. Recommend a typed DAG with ordered
sequence regions, typed expressions and immutable symbolic references. Only learned
compositions of defined operations are in scope; new primitives need separate
specification and implementation. Human readability is optional.

Compare direct Python A, fixed structured B and adaptive compositional C using the
same local model/configuration and behavioral requirements. Required nested B-cap
control has a human-designed macro library of comparable capacity; C-expand tests
compact reference attribution. Eight development tasks, vocabulary/machinery freeze,
24 development-unseen tasks in three strata, three seeds, staged modifications;
tasks/oracles/model are not prepared or run here. Charge discovery/rejections,
retrieval, human work and tooling; distinguish marginal/inherited setup costs.

Resource inventory and neutral calibration precede model selection. Local validation,
lowering, inference and execution must qualify offline. No mandatory MCP/cloud API,
provider-specific executable identity or training. Actual future containment and
metering are gates for causal comparison, not claimed current capabilities.

R6.10/R6.14 support bounded composition, not learned transfer. R6.15 locally favors
Python under exploratory controls; R6.16 establishes no unique scored semantic benefit
and has inherited-outcome priming. None is retrospectively interpreted as evidence
for adaptive symbols. Main risks: memorization, ordinary macro reuse attribution,
retrieval/discovery overhead, typing/expansion errors, foundation limits, local model
capacity and contaminated task contexts. Small initial domain limits external validity.

## Preservation and stop

Initial Git status clean; HEAD `13c5bde277a107435ab62e30dff6a1a798b94ac6`.
Changes are new R6.17 documentation and current guidance only. Existing 26-construct
kernel, production implementation/compiler/runtime/schema/model/generated artifacts,
R6.10 VM and R6.3–R6.16 dedicated historical records retain their identities.
No historical classifications, candidate failures or context supplements are changed.
No model inference/training, benchmark execution or P6-A04 acceptance; P6-A05 not accessed.
Publication checks do not rerun historical acceptance. See verification for exact scope.

**Smallest executable next step:** separately authorize a nonproduction typed
composition wrapper over a tiny unchanged R6.10 subset, with one macro/expanded
equivalence witness and type/dependency/capture/cycle/bound rejection controls.
This qualifies mechanics before model/task commissioning; it is not the scored run.

**Stopped after publication. Await explicit owner authorization before implementation.**
