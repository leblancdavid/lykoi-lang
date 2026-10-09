# R6.31 — Symbolic discovery and in-place modification experiment design

**Final classification: `R6_31_EXPERIMENT_DESIGN_READY`.**

This is a documentation-only prospective design. H1 asks whether AI-selected
compositions transfer to development-unseen tasks after full discovery costs; H2
asks whether edits to shared existing application behavior improve reliability or
effort. They have separate task pools, machinery, scores and verdicts. Neither
hypothesis is demonstrated by this publication. Ready means sufficiently specified
for separate implementation authorization, not execution readiness or advantage.

## Evidence boundary

The [evidence and capability inventory](r6_31/INVENTORY.md) preserves the original
R6.16, R6.17, R6.18, R6.23 and R6.25–R6.30 classifications. R6.16 supports actual
production-semantic persistent applications but no C-specific scored benefit.
R6.18 qualifies bounded typed composition; R6.23 qualifies deterministic assembly
despite halted model authoring. R6.25–R6.29 distinguish transport, exposure and
scaffolded construction. R6.30 reports A/B/C each56/56 base and27/27 extension
observations, with37/37 original rechecks; its originals remain byte-identical
beside added endpoints. It tests neither discovery nor genuine in-place safety.
Its separate R6.29 successor replay23/23 does not replace R6.29's19/23 or partial
classification. No historical result is reinterpreted.

Production remains at **26 constructs**. [Baseline identities](r6_31/BASELINE.json)
record the current commit, exact experimental subsystem hashes and inherited
preservation anchors. All **1,752** distinct identities in the union of R6.30's
protected baseline and publication manifest match before design publication.
Tracked repository files remain unchanged; R6.31 consists of additive documents.

## Designs and deliverables

| Deliverable | Governing document |
| --- | --- |
| H1 proposal, admission, freeze and unseen evaluation | [H1 protocol](r6_31/H1-PROTOCOL.md) |
| H2 shared-state in-place changes, base/modified separation | [H2 protocol](r6_31/H2-PROTOCOL.md) |
| Six H1 conditions, three H2 tracks and attribution controls | [Tracks and controls](r6_31/TRACKS-AND-CONTROLS.md) |
| Demonstrated versus missing capabilities and identities | [Inventory](r6_31/INVENTORY.md), [baseline](r6_31/BASELINE.json) |
| Independent selection, partitions, withholding and exposure | [Task and contamination controls](r6_31/TASKS-AND-CONTAMINATION.md) |
| Acceptance, regression, impact and failure scoring | [Acceptance and scoring](r6_31/ACCEPTANCE-AND-SCORING.md) |
| Comparable models, telemetry, discovery and amortization | [Telemetry and cost](r6_31/TELEMETRY-AND-COST.md) |
| Falsifiable decisions and practical thresholds | [Thresholds and outcomes](r6_31/THRESHOLDS-AND-OUTCOMES.md) |
| Minimal implementation, risks and smallest next experiment | [Roadmap and risks](r6_31/ROADMAP-AND-RISKS.md) |
| Publication integrity | [Manifest](r6_31/PUBLICATION-IDENTITIES.json), [verification](r6_31/VERIFICATION.json) |

### H1

Use the unchanged R6.18/R6.23 Int64/Bool/Unit composition subset and provider-neutral
deterministic execution. Four development tasks, then seal vocabulary, machinery,
retrieval and all rejected proposals before revealing12 evaluation tasks in three
strata; three replicate sessions per task/condition. Six conditions give216
evaluation sessions: direct Python, lean fixed intent, primitive-only Lykoi,
AI-discovered Lykoi, human capacity-matched Lykoi macros and expanded discovered
templates. AI can define parameterized compositions only during development.
Discovery attribution requires transfer beyond both fixed symbolic and human-macro
controls; shorter representations alone do not qualify. Empty vocabulary remains
valid negative evidence. Hypothesis H2 is not embedded in these scores.

### H2

Use production stateful semantics through the existing R6.16 B/C research interface,
not the stateless experimental VM. Select four already-existing accepted applications
covering at least two behavioral skeletons, each with shared state, interdependent
operations and multiple consumers. Prepare four independent change branches per
application: shared invariant, shared transition, validation exception and precedence
or behavior-preserving refactor. A/B/C and three replicate sessions give144
modification sessions. Each branch starts from the same frozen accepted base for
that track; it changes existing callers, not a parallel added endpoint. The existing
kiln/custody implementations are an exposed feasibility shortlist, not two diverse
independent families. Exact selection and fixtures require later preparation.

## Feasibility and implementation boundary

Existing deterministic type/pin/cycle/expansion checks can support bounded H1.
Missing essentials are an immutable admission/storage/retrieval lifecycle, model
proposal workflow and durable comparable measurement. Existing production guards,
mutations, invariants and generation can support narrow H2. Missing essentials are
qualified equivalent application fixtures, a successor-copy edit/snapshot interface,
an independent impact oracle and frozen supersession-aware acceptance. R6.25's four
semantic contracts stay unchanged; external lifecycle plumbing may only call frozen
APIs and cannot supply application decisions. No general-purpose language extension
is necessary for the bounded design; unsupported tasks remain gaps rather than
justifying semantics invented by a harness.

The same capable model/configuration must be used across tracks. GPT-6.1 Sol is
historically feasible, not newly qualified here; provider choice is pinned before
task exposure. Reasoning attestation, actual billing and enforced context exclusion
remain unestablished. Unenforced separation makes affected results exploratory;
missing metering blocks fully costed claims. Development-unseen never means proven
absent from model pretraining. Practical thresholds and uncertainty reporting are
predefined, with no significance claims from a small pilot.

## Recommended next bounded experiment and stop

Authorize **only an AI-free lifecycle/edit qualification** first: append-only
content-addressed storage, deterministic lexical/type retrieval, one composition
successor and two dependent callers; separately use a copied exposed R6.16 stateful
application to change an existing validation/invariant rule across two operations.
Test stale pins, cycles, bounds, replay, unchanged cases and intended changes with
scripted fixtures. Qualify durable telemetry using stub events, including interruption
and missing usage. Preserve all original implementations. This is infrastructure
qualification, not H1/H2 comparative evidence. The roadmap gives separate subsequent
pilot authorization boundaries.

No language implementation, scored authoring, inference request, model training,
historical acceptance execution or P6-A04 acceptance occurs in R6.31; P6-A05 is not
accessed. Production compiler/lowerer/runtime, R6.10 VM, R6.18 wrapper, R6.23 adapter,
R6.25 semantic contracts and R6.3–R6.30 history are preserved. Publication verification
checks hashes, JSON, relative links, additive-file whitespace and `git diff --check`.

**Stopped after publication. Await explicit authorization before implementation,
task commissioning, capability execution or authoring trials.**
