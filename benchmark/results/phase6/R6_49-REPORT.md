# R6.49 — Training-data admission and stateful family pilot

**Final classification: `R6_49_TRAINING_DATA_PILOT_QUALIFIED`.**

The successor candidate pool contains **10 Tier T episodes and 0 Tier E examples**:
eight reassessed R6.48 symbolic episodes and two new production-backed stateful
episodes in one synthetic requirement family. The process is qualified for this
bounded research-candidate scope. It does not establish broad model-training or
generalization readiness. **No training or fine-tuning occurred.**

## 1. Baseline and historical preservation

Initial git status was clean. [Baseline](r6_49/BASELINE.json) verifies **5,387
protected identities**, including the inherited production/R6.3–R6.48 chain,
R6.47 readiness findings and R6.48 publication, original ledger and receipt.
R6.47 remains `R6_47_DATASET_PARTIAL`; R6.48 remains
`R6_48_DATA_PIPELINE_PARTIAL` with **zero original TRAINING_ADMITTED episodes**.
The separate successor ledger does not rewrite either historical classification.

Kernel **26** is preserved on unchanged R5.114 accounting and implementation
identities, not independently recounted. Production compiler/lowerer/runtime,
R6.10 VM, R6.18 wrapper, R6.23 adapter, R6.25 semantic contracts and R6.32 registry
remain unchanged. Existing stateful profiles and the R6.16 production-backed
generator are reused without edits. There are no new execution primitives,
downloads, training dependencies, P6-A04 acceptance executions or P6-A05 access.

## 2. Separate admission standards

[Tier policy](../../../docs/training-data-admission-r6.49.md) makes source/FRC,
validated faithful target, frozen acceptance, deterministic replay, identities,
absence of known contradictions/evaluation leakage and authorized use conjunctive
Tier T gates. Independent commissioning/review are preferred, but not mandatory.

For this owner-authorized synthetic research pilot, the preserved source is the
authority for the fixture it defines. It is **not independent human authorship,
source-authoritative human acceptance review, or deployment approval**. Same
coordinator, capability-aware commissioning and inherited context are disclosed.
The rights basis is the owner's explicit synthetic-data/training-candidate review
authorization, limited to research preparation; arbitrary redistribution and an
actual training run are not authorized. No third-party requirement is repurposed.

Tier E additionally requires independent sources/review, withheld families,
qualified isolation, leakage-resistant partitions and pre-exposure scoring.
**None of this cohort qualifies for Tier E.** “No known evaluation leakage” in
Tier T is a bounded provenance audit, not certified clean hidden provider context.

## 3. R6.48 successor reassessment

[Successor ledger](r6_49/R6_48-SUCCESSOR-LEDGER.json) binds each gate to the
original source, FRC, symbolic/executable target and evidence. Strict symbol reload,
validation and expansion match saved artifacts. Two new AI-free replays reproduce
**81 cases each, 162 observations**, and match all three historical complete-envelope
replays, including error sites, provenance and work. [Replay evidence](r6_49/R6_48-REASSESSMENT-REPLAY.json)
preserves every new result. Source obligations and ordered symbol construction were
reviewed; correctness is finite and scoped, not a universal equivalence proof.

| Episode | Behavioral distinction | Successor Tier T | Tier E |
| --- | --- | --- | --- |
| E01 | byte sum, capacity 120 | T_CANDIDATE_ADMITTED | NOT_QUALIFIED |
| E02 | doubled-fragile quote, ceiling 600 | T_CANDIDATE_ADMITTED | NOT_QUALIFIED |
| E03 | agreement; validate first flag before second read | T_CANDIDATE_ADMITTED | NOT_QUALIFIED |
| E04 | exactly one; both reads before flag validation | T_CANDIDATE_ADMITTED | NOT_QUALIFIED |
| E05 | early version 7/count validation | T_CANDIDATE_ADMITTED | NOT_QUALIFIED |
| E06 | ordered window/below/above checks | T_CANDIDATE_ADMITTED | NOT_QUALIFIED |
| E07 | nested three-input tally, ceiling 300 | T_CANDIDATE_ADMITTED | NOT_QUALIFIED |
| E08 | shared double/triple packing score | T_CANDIDATE_ADMITTED | NOT_QUALIFIED |

No unresolved correctness defect was found in this review. No episode is admitted
because of a renamed program or repeated execution. Original F5/F6 quarantine is
excluded; E09–E12 are not promoted. Eight direct representations exist, but **no
actual AI construction trajectories exist for these eight historical episodes**.
Their scripted API traces retain their original labels.

## 4. New commissioning, authority and freeze

[Commissioning](r6_49/COMMISSIONING.json) creates one **LOCAL_RELEASE** family:

- **S01:** queued → ready → released, with closed-seal release and terminal state.
- **S02:** queued → ready → held → released, with a meaningful held → queued reset
  that atomically opens the seal; direct release from ready is rejected.

Both have typed enum domains, nonblank labels, ordered lookup/guard/input/invariant
errors, rejected-byte preservation and atomic one-store persistence. Sources specify
the exact sequential API, full-record outputs, provider assumptions, list order,
error precedence and exclusions. No missing behavioral authority is filled in from
test output. Ambiguities identified within this deliberately closed synthetic scope:
**0**. Human product interpretation and independent review are not claimed.

| Episode | Source | FRC | Frozen acceptance |
| --- | --- | --- | --- |
| S01 | [Source](r6_49/episodes/S01/SOURCE.json) | [FRC](r6_49/episodes/S01/FRC.json) | [24 steps](r6_49/episodes/S01/ACCEPTANCE.json) |
| S02 | [Source](r6_49/episodes/S02/SOURCE.json) | [FRC](r6_49/episodes/S02/FRC.json) | [35 steps](r6_49/episodes/S02/ACCEPTANCE.json) |

[Source freeze](r6_49/SOURCE-FREEZE.json) precedes actual symbolic authoring.
Both contracts are representable using existing scalar creation, typed mutable
replacement, ordered guards and record invariants. The experiment adds orchestration
and evidence, not semantic meanings or a stateful extension to the experimental VM.

## 5. Actual AI construction and interface limitation

The working OpenCode route used **`gpt-6.1-sol`**, confirmed by actual exported
session metadata. The coordinator AI selected the enum fields, bindings, transitions,
ordered guard predicates and invariant in two explicit intent files. The unchanged
R6.16 C generator lowers these into genuine production symbolic IR and Python.

[Transcript](r6_49/AI-CONSTRUCTION-TRANSCRIPT.json) contains **10 actual selected
OpenCode tool exchanges**, including construction, validation, replay and capture
tooling. It preserves real typed arguments, outputs, native validation feedback and
the correction. Both episodes share a creation/correction exchange; these are not
ten independent construction episodes. Hidden reasoning is omitted.
[Tool exposure](r6_49/TOOL-EXPOSURE.json) records the relevant actual harness schemas,
input intent schema and downstream contract. The full provider-side tool payload and
hidden context are not attested.

**Actual semantic MCP trajectories: 0.** No Lykoi semantic construction MCP tool
is exposed in this session. **Actual AI-selected symbolic editing trajectories:
2 episode views of the shared session.** Editing calls are not relabeled as semantic
MCP. Each episode's deterministic SCRIPTED-LOWERING remains explicitly separate.

One genuine shared representation defect was corrected: creation input bindings
must use a null preservation value, rather than the input name. The first build
rejects `INVALID_TYPED_SCALAR_RELATION`; an identical second call captures the
failed inputs and diagnostic in [failure evidence](r6_49/BUILD-FAILURE.json).
The original first failure is also in the actual transcript. The AI then corrects
both intents; validation and generation pass. This is **one correction issue,
two failed build invocations**, not two independent learning examples. S02 was not
reached during the first failure. Frozen sources/acceptance were unchanged.

[Candidate freeze](r6_49/CANDIDATE-FREEZE.json) binds the final intents, IR,
generated applications, validation and scripted lowering before functional runs.
The applications are in the episode directories, outside production `generated/`.

## 6. Functional, persistence and restart verification

[Pass 1](r6_49/REPLAY-1.json) and [pass 2](r6_49/REPLAY-2.json) each execute **59
frozen steps plus two final restart reads**, with one request per fresh Python
process: **122 fresh-process requests total**. All pass, and the complete results,
including raw stdout/stderr and before/after storage bytes, are identical:

`8be41065eb78f2a59ac48f4ec50757dfb173a3121b3ddeae19cabc1018943b15`

Both verify absent-store empty state, nonblank creation, valid transitions,
unknown/missing lookup, missing/invalid/type-invalid enum input, wrong-phase versus
unsealed precedence, terminal rejection, staged invariant rejection, read/rejection
byte equality, full persisted records and explicit final restart continuity. S02
also verifies atomic held/reset phase-and-seal changes. Every persisted record is
checked for declared domains, nonblank label and released-implies-closed invariant.
Repeat execution uses **zero AI calls**.

The contract covers normal sequential process termination/restart, not power-loss
recovery, concurrent writers, corrupt external stores or authenticated users. Frozen
tests use one deterministic record; multi-record listing order is represented in
the unchanged lowering but not separately functionally challenged in this pilot.

[Admission controls](r6_49/ADMISSION-CONTROLS.json) pass **12 controls**: eight
mandatory-gate failures block admission, missing gate and evaluation export reject,
invalid enum writes reject before execution, and a well-typed wrong-transition
mutant passes static generation but fails the original acceptance suite. Its
[complete observations](r6_49/WRONG-TRANSITION-CONTROL.json) are kept separately;
it is a seeded process control, not a natural AI defect or admitted episode.

## 7. Dataset, deduplication and partitions

[Dataset index](r6_49/DATASET-INDEX.json) retains **10 direct episode bundles**.
Two new bundles also reference actual AI editing transcripts and tool schemas;
all ten have explicit null semantic-MCP views. No missing historical trajectory is
invented. Generated code, IR, reusable definitions and repeated observations remain
derivatives of one requirement episode, not extra positive examples.

[Deduplication/partition record](r6_49/DEDUPLICATION-AND-PARTITIONS.json) distinguishes
**5 nominal requirement families from 2 broad scaffold components**. F1–F4 share a
stateless read/check/encode scaffold. S01/S02 share production scalar/mutable lowering,
the release invariant and much acceptance logic; held-stage/reset semantics distinguish
them. Related R6.47 arithmetic and R6.16 kiln/custody sources are disclosed as
auxiliary ancestry, not newly counted or independently sourced examples.

All related episodes remain in **training_development**. There is no qualified
evaluation partition. Historical exposed F5/F6 quarantine and future independent
evaluation solutions are excluded. Semantic duplicate findings apply to this bounded
ten-episode cohort; no exhaustive equivalence census of repository history is claimed.

## 8. Cost and training readiness

[Readiness](r6_49/READINESS.json): Tier T **10**, Tier E **0**, accepted stateful
episodes **2**, new stateful families **1**, nominal admitted families **5**.
Coverage now includes enum transitions, guards, staged invariants, atomic rejection,
local durable state and normal restarts alongside the existing stateless arithmetic,
ordered checks and pinned composition. It is not coverage of all26 kernel constructs.
Relations, authority, migrations, dimensioned time and broad domain diversity remain
unrepresented as admitted targets.

[Actual selected-message metadata](r6_49/CONSTRUCTION-COST.json) records 14,297 input,
8,349 output and 874 reasoning-accounting tokens, plus 987,648 cache-read tokens.
These are reported usage categories, not fabricated reasoning text or a complete
coordinator bill. All10 selected messages have usage metadata. Reported cost sums
to zero but **actual API billing is unavailable**; zero metadata does not prove free
inference. Full commissioning/review duration and cost were not separately metered.
The two stateful passes took 3,926 and 3,887 ms respectively on this host; other
preparation and control costs are separate. Publication receipt measures artifact
storage. Training compute and training runs are zero.

**Small LoRA smoke test justified now: no.** Reproducible admission mechanics and
bounded stateful coverage improve the dataset foundation, but ten correlated episodes,
no independently reviewed family and no clean withheld evaluation do not yet justify
a training run. Hardware plausibility from R6.47 remains planning evidence only.
No broad generalization or architectural advantage follows from this pilot.

## 9. Publication and next authorization

[Publication identities](r6_49/PUBLICATION-IDENTITIES.json) and
[verification receipt](r6_49/VERIFICATION.json) verify protected history, new artifact
identities, source/candidate ordering, target regeneration, acceptance observations,
dataset references, partition exclusion, relevant transcript feedback, credentials,
scope, links, additive whitespace and `git diff --check`.

The exact [owner authorization](r6_49/OWNER-AUTHORIZATION.json) is recovered from
the active-session user message. Its first capture encountered Windows cp1252
decoding of UTF-8 export; the [diagnostic](r6_49/CAPTURE-DIAGNOSTIC.json) is retained,
and explicit UTF-8 decoding fixes the evidence consumer. This operational failure
does not change requirements, candidates or acceptance.

Smallest recommended next step: separately authorize **one independently
human-commissioned local-stateful family**, source-authoritative acceptance review,
and a custodian-withheld sibling. Qualify a stateful semantic authoring interface
over existing meanings if semantic MCP trajectories are the intended training target.
Freeze those evaluation controls before exposure. No semantic extension is implied.

**Stopped after this bounded admission review and stateful pilot publication.**
Further commissioning, interface work, model setup or training requires explicit
owner authorization.
