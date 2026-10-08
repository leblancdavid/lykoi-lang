# Phase 6 research plan — R5.115

**Planning complete: `R5_115_PHASE6_RESEARCH_READY`.** The central objective is to
test unfamiliar software before investing in broad semantic expansion or optimizing
the representation. The [Phase 5 baseline](phase5-baseline-r5.115.md) remains fixed;
the [protocol](phase6-generalization-protocol-r5.115.md) governs prospective attempts.
No requirement is selected, authored, inspected or evaluated in this round.

## Research questions and evidence

| Question | Priority and operational evidence |
| --- | --- |
| Q1 — Generalization: can unfamiliar requirements be represented with the existing kernel and compositions? | Immediate. Full source obligations, faithful representation, first blocker, source provenance and independent behavior; partial coverage is not complete representation. |
| Q2 — Kernel stability: do new requirements increasingly compose existing concepts or require substantial expansion? | Immediate. Per-case concept/composition ledger and later independently justified irreducible candidates; report growth trajectories and integration debt separately. |
| Q3 — Behavioral correctness: does generated software satisfy independently established acceptance criteria? | Immediate. Source-authorized external observations, coverage and unverified obligations, not validator status alone. |
| Q4 — AI efficiency: does representation eventually reduce context, output tokens, effort, repairs or regression risk versus conventional AI coding? | Later comparative experiment. No superiority claim or implementation requirement now. |

Initial evaluation is a small exploratory batch, proposed **four requirements from at
least three domains**, fixed by an independent curator before seeing outcomes. Domains
may include employee access/roles, document ownership/revisions, inventory reservations,
and membership/approval workflows. These examples are sampling suggestions only.
The source determines behavior, ambiguity, scope and actual domain mix. They must not
be renamed versions of synthetic Phase 5 scaffolding or tailored capability probes.
Report any deviation in batch size/diversity with its reason. A small batch supports
local observations, not population-wide generalization or convergence claims.

Use a recorded non-capability-based selection rule (for example, chronological eligible
items within independently chosen domains). Include difficult cases and ambiguity;
do not select probable passes, hunt known gaps or drop failures from denominators.
Fix order and attempt budget before semantic access. For initial fixed-baseline
evidence, finish the batch's first attempts before informed shared-capability changes;
if the baseline must change, report distinct cohorts rather than pooling them.

## External-source independence policy

Prefer, in order of availability, independently authored real-world specifications,
public issues not used in Lykoi development, independent human requirements, or a
separately isolated AI author with no Lykoi inventory, profiles, synthetic corpus,
development summaries or expected gaps in its prompt/context. Source authors receive
domain/user needs, not instructions to fit 26 concepts. AI-only origins must be labeled;
isolation is not proof of independent cognition or absence of model-training exposure.

An independent human/curator selects and retains the actual source outside the
development agent's context until the evaluation starts. This is ordinary procedural
separation, not new protected activation software. Record origin, revision/time,
author/authority, selection rule, exact text hash and any prior exposure known to the
curator. For public issues preserve URL, issue ID, revision/captured text and attachments;
a changing URL alone is insufficient identity. For private human/AI sources preserve
the authorized artifact, authoring context/prompt where available and lawful access.
Unknown provenance or prior use is disclosed and cannot be asserted pristine.

Before evaluation the development agent receives no semantic previews, descriptive
filenames, summaries, acceptance details or source-linked implementation hints.
At first delivery record exposure. Accidental disclosure before the snapshot is recorded
as contamination; retain it as exposed evidence, not a fresh held-out result. Requirements
and acceptance authors must not use generated code or Lykoi's inventory as normative
authority. An issue lacking an available legitimate clarification authority may terminate
`NEEDS_CLARIFICATION`; do not fill in behavior from its implementation or an oracle.

Selection/exclusion reasons can concern independence, legitimate access, duplicate use
or missing provenance, never predicted difficulty or lack of current support. Record
all screened items and reasons externally, without disclosing rejected semantics to
development. Preserve selected failures and source ambiguity. New requirements must
be capable of exposing new gaps. R5.115 supplies no actual source or requirement.

## Entry criteria and next action

| Objective criterion | R5.115 status |
| --- | --- |
| Exact Phase 5 baseline recorded | Complete: commit/tree, versions, capabilities and limitations |
| Current regressions passing or failures documented | Complete: preserved 397-pass receipt, unchanged implementation, 34 fresh passes and validation/safety; older limitations explicitly retained |
| Lightweight evaluation protocol established | Complete: versioned protocol linked above |
| Source-independence policy established | Complete: this policy, exposure and curator responsibilities |
| First-result recording procedure established | Complete: protocol record fields and immutable first-attempt handling |
| Result taxonomy established | Complete: protocol stage/outcome table |

Readiness means methodology readiness, not that sources exist, live roles are configured,
all requirements will pass, or production security/universal correctness is certified.
Use current compatible tooling and available model, recording useful provenance. No
exact Python/OpenCode/model qualification registry, machine freeze or protected
activation/access infrastructure is required. Existing product authority/seals remain
useful for normal handoffs and do not grant benchmark access.

**Next concrete action, only in a separately instructed evaluation round:** ask an
independent curator to source and fix the small batch without capability guidance,
retain it outside development context, then take the fresh implementation/test snapshot
before delivering the first requirement. No such sourcing or delivery begins here.

## Deferred AI-efficiency comparison outline

After Q1–Q3 have usable evidence, compare isolated conventional and Lykoi authors on
the same independently sourced tasks, source authority, accepted baseline behavior,
model/configuration, tool/time budget, acceptance oracle and permitted clarification.
Predeclare repair feedback/budget and keep first-attempt correctness distinct from
correctness after repairs. Preserve conventional/Lykoi starting snapshots; separate
contexts must not see the other solution. Counterbalance task/track order where useful,
record model changes, and report capability failures rather than compare only successes.

Optional lightweight records from provider receipts/session logs and ordinary diffs:

- Input/context tokens (including repeated context and cached-token categories when
  known), output tokens, model calls; note accounting source and missing values.
- Repair attempts/cycles, tool actions when available, elapsed wall time (distinguish
  machine execution, author time and human clarification wait).
- Changed stable semantic nodes for Lykoi; conventional changed files/lines with the
  diff convention recorded. Generated lines are separate from authored semantic work.
- Independent behavioral correctness, failed criteria, regression counts and achieved
  coverage, using equal criteria and denominators.

No telemetry framework is implemented. Missing metrics are `N/A`, never zero, and do
not block generalization evaluation. Node counts and line counts are different measures,
not direct effort equivalents. Report raw per-task data, correctness-conditioned costs
and all-task outcomes; avoid claiming token reductions from cheaper incomplete work.
Compiler/setup/acceptance-authoring costs should be reported separately with any
amortization assumptions. Token/context optimization is deferred, not a tuning target
for the first generalization batch.

## Deferred research backlog

Frontend/UI semantics; multiple compiler targets; decompilation/requirements recovery;
AI token/context optimization; semantic representation compression; broader runtime/
backend independence. Keep these as hypotheses/backlog, not Phase 6 entry gates or
R5.115 implementations. Source-informed extensions need separate authorization after
immutable first results; no pressure to artificially keep the kernel at 26.
