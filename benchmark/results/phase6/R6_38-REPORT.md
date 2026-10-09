# R6.38 — State-based context management and token efficiency

**Final classification: `R6_38_COMPARISON_INCONCLUSIVE`.**

Deterministic symbolic-state snapshots supported correct continuation in three
fresh modification sessions. Both tracks passed all frozen functional observations
with zero repairs or regressions. Snapshot-based Track B had **26.7% fewer reported
processed input tokens**, including cached input, across the measured participant
workflow. However, noncached input increased, model calls did not decrease, the
small timing difference was inconsistent across tasks, and complete request/whole-
development accounting and a scored ordinary-summary control were unavailable.
The required fully accounted effort advantage is therefore **not established**.

## Baseline, preservation and scope

The initial worktree was clean. The existing R6.37 verifier passed **3,246 protected
identities and126 publication files**. [R6.38 baseline](r6_38/BASELINE.json) adds the
complete publication and its manifest/receipt, protecting **3,374 SHA256 identities**.
It records exact implementation/source/evidence hashes, including production,
R6.10 VM, R6.18 wrapper, R6.23 adapter, R6.25 semantic contracts, R6.27 MCP exposure,
R6.32 registry/telemetry and all R6.36/R6.37 authoring/token evidence. Production
remains **26 constructs**, on inherited exact accounting rather than a new recount.

All new code is in [the nonproduction experiment](../../../experiments/state_context_r6_38/PROTOCOL.md).
The common semantic facade reuses the preserved R6.37 transport over R6.32;
execution and expansion remain unchanged R6.10/R6.18. Both tracks get the same
additional bounded **read-only** detail tool; it adds no execution meaning.
Historical R6.25 contracts and R6.27 discovery evidence retain their original scope.
No production or earlier experimental source was edited, no training occurred,
no full R6.31 H1/H2 study began, and no P6-A04 acceptance or P6-A05 access occurred.

## Instrumentation and accounting prerequisite

[Specification](../../../experiments/state_context_r6_38/INSTRUMENTATION-1.md),
[chronological request/completion ledger](r6_38/REQUEST-LEDGER-CHRONOLOGICAL.json) and
[section catalog](r6_38/SECTION-CATALOG.json) preserve supported observations:

- Each CLI dispatch: content-addressed visible prompt/instructions/tool schemas,
  request/response wall interval, configuration, events and session export.
- Each completion: model/provider, sequence, SDK input/output/cache/reasoning
  buckets, message identities and assistant creation/completion interval.
- Each MCP exchange: exact arguments and response content plus wall interval;
  retrieval content and overhead are explicitly included.
- Local category counts: **ceil(characters/4)**, labelled estimates; unique content
  deduplicates hashes separately from repeated transmission estimates.

**Exact upstream request boundaries and a model-matched tokenizer were unavailable
through the supported CLI surface.** Locally canonicalized messages and schemas
are not claimed to be provider serialization. Completion count is not hidden HTTP
attempt count. Per-completion exports reconcile with step-finish usage and MCP logs.
Signed residuals are unattributed estimate differences, not hidden-token counts.
Actual billing, coordinator preparation/publication tokens, provider retries,
effective reasoning/authentication and isolated inference time remain unknown.
These gaps prevent quantitative causal category attribution and a fully costed
development-effort claim, while allowing descriptive participant-usage comparison.
The initial ledger's sequence was task/track catalog iteration; the chronological
successor uses actual exported creation timestamps, preserving the initial ledger
and all usage unchanged. Neither is claimed to count invisible provider retries.

The neutral preflight passed on **OpenCode1.18.32 /openai/gpt-6.1-sol**, requested
high reasoning, with one completion, zero tools and **509 input /8 output tokens**.
[Model configuration](r6_38/MODEL.json) uses the qualified R6.36 child environment:
`OPENCODE_PURE=1`, with `OPENCODE_DISABLE_DEFAULT_PLUGINS` removed. Built-in OAuth
was eligible; the actual selected authentication branch is not attested. Credential
stores, authentication values, private headers and endpoint overrides were not used.

## Snapshot qualification and retrieval

[Implementation](../../../experiments/state_context_r6_38/snapshot.py) and
[contract](../../../experiments/state_context_r6_38/SNAPSHOT-1.md) qualify bounded
deterministic, content-addressed context. Snapshots contain exact active definition
closure, immutable pins, parameter/result signatures, dependencies, both caller
bindings, verbatim original constraints and current objective, requirement identity,
registry generation/token, successors/migrations, deterministic validation identities,
and exact retrieval references. There is no LLM generation or semantic paraphrase.

Required task facts come from frozen artifacts supplied by the host; the registry
does not itself store the behavioral requirement. Validation status is recomputed
with unchanged expansion, not misrepresented as an archived historical event.
Every snapshot is regenerated and checked against authoritative current state and
separately supplied frozen facts before participant disclosure. Full required
closure is retained rather than risk omitting essential ordered checks or bindings.

[Four prospective tests](r6_38/SNAPSHOT-TESTS.json) pass deterministic generation,
all five retrieval kinds, dependency closure, ordinary tampering, re-sealed omissions,
stale state, missing callers and unknown identities. [Two supplemental tests](r6_38/CONTINUATION-TESTS.json)
pass selective migration metadata, predecessor retrieval, unchanged registry after
all retrieval kinds, restart and regeneration of all three actual scored snapshots.
Supplemental tests are post-authoring unscored qualification, not oracle amendments.

## Frozen tasks and equivalent information

[Task/oracle/source freeze](r6_38/TASK-FREEZE.json) preceded all participant calls.
The three new synthetic requirements use unchanged checked Int64 addition, le,
UInt8 reading, ordered checks/end and UInt16BE output:

| Task | Reusable abstraction and ordered checks | Base → successor result |
| --- | --- | --- |
| [T1](r6_38/T1-TASK.json) ReserveTotal | x<=y, then x+y<=cap | x+y → x+y+5 |
| [T2](r6_38/T2-TASK.json) DoubleQuota | x<=cap, then y<=cap | x+x+y → x+x+y+y |
| [T3](r6_38/T3-TASK.json) FloorWeight | floor<=x, then x<=y | x+y+y → x+x+y+y |

Each task has two dependent callers: A reads two bytes and adds a fixed bias; B
reads one byte and derives y using a fixed offset. Each requires a signature-
preserving abstraction successor, exact pin-only CallerA successor, total explicit
migration and retained CallerB/predecessor execution. Expectations are in
[T1](r6_38/T1-EXPECTATIONS.json), [T2](r6_38/T2-EXPECTATIONS.json) and
[T3](r6_38/T3-EXPECTATIONS.json), generated from requirements before authoring.
They are AI-independent of participant artifacts, but same-coordinator designed,
capability-tailored and not independently human reviewed or externally sourced.
They differ from the R6.36/R6.37 tasks; exhaustive historical uniqueness is not claimed.

Order was **T1 A/B; T2 B/A; T3 A/B**. Each track starts from the same empty registry
and frozen base requirement, but independently authors its own base definitions.
A continues that accumulating session; B starts a fresh modification session with
the guide, original requirement, exact current-state snapshot and objective.
No modification text appears in any original-stage participant export. Neither
track has tools for another registry, task files or the other implementation.
Strong provider/harness hidden-context exclusion remains unattested.

[Information-equivalence declaration](r6_38/INFORMATION-EQUIVALENCE.json) was frozen
before scoring. Before B continuation, exact closure/constraints/bindings are checked
against its own authoritative base state. Both tracks can retrieve the same **kinds
of task-relevant facts** through identical interfaces. [Actual continuation checks](r6_38/CONTINUATION-EQUIVALENCE.json)
confirm session separation, model configuration and frozen-text identities.
This is not a claim of identical cognitive history: A retains generated explanation,
tool feedback and earlier choices that B omits. Independently authored base layouts
also differ on T2/T3, confounding exact representation matching. Their finite base
behavior is accepted by the same oracle; full semantic equivalence is not proved.

Budgets per task/track were30 completions,50 MCP calls,600s/stage,1200s total authoring
and at most2 correction turns/stage. Limits were checked at stage boundaries,
not hard-enforced within a completion/tool loop. All observed runs stayed inside
limits. Raw errors/proposals were preserved; none required scored correction.

## Functional results and AI-independent replay

| Measure | Track A | Track B |
| --- | ---: | ---: |
| Base acceptance | **1,320/1,320** | **1,320/1,320** |
| Final acceptance | **1,851/1,851** | **1,851/1,851** |
| Completed base + modification task pairs |3/3 |3/3 |
| Passing-to-failing regressions |0 |0 |
| Acceptance repairs /rejected MCP calls |0 /0 |0 /0 |
| Fresh modification sessions |0 (accumulating) |**3/3 accepted** |

Each base stage has440 observations; each final stage617. Final counts include the
unchanged440 predecessor/retained-caller observations and177 successor observations.
They are observations, not unique input claims. Coverage includes169 selected A byte
pairs, all256 B byte inputs, ordered semantic errors with exact hygienic source nodes
and offsets, trailing/truncated input precedence, input-type rejection, work limits,
values/output bytes/provenance, exact dependency pins and total migration records.
Finite byte-domain coverage is not unrestricted signed64/overflow proof.

[Provenance](r6_38/PROVENANCE.json) verifies all **30 admitted definitions** equal
model MCP arguments after mechanical sealing only; coordinator semantic repairs0.
Each original caller and abstraction remains immutable and executable. All original
acceptance rows are retained exactly in final acceptance. Invariant preservation
here means the prescribed checks/order/codes/signatures and binding constraints,
not arbitrary untested program invariants.

The separate [model-free replay](r6_38/REPLAY.json) process executes saved registry
artifacts through unchanged deterministic expansion/VM, with **zero model calls**.
All six runs pass **617/617 on each of three passes**, reproducing full result
envelopes, errors, logical work, identities, expanded plans and provenance maps.
Across the experiment this is11,106 repeated replay observations; no additional
unique behavioral cases. T1 A/B artifacts happen to match; T2/T3 full digests differ
between tracks because representation/pins/work can differ, while each repeats its
own exact accepted results. This is functional task agreement, not equal-work coding.

## Token, call and timing comparison

[Measured totals](r6_38/MEASUREMENTS.json) include both base and modification
authoring, snapshot-context delivery, model retrieval and tool feedback overhead.
The neutral preflight is common setup and separately recorded; it is not assigned
to either track. Cached processing is counted, not treated as free.

| Participant metric | A: full accumulating session | B: fresh snapshot session | B minus A |
| --- | ---: | ---: | ---: |
| SDK noncached input |79,634 |85,615 |+5,981 |
| Cache-read input |217,216 |131,968 |-85,248 |
| **Processed input (input + cache)** |**296,850** |**217,583** |**-79,267 (-26.7%)** |
| Output |14,973 |14,900 |-73 |
| Reported reasoning |246 |686 |+440 |
| Cache-write |0 |0 |0 |
| Model completions |36 |37 |+1 |
| MCP calls |114 |111 |-3 |
| Retrieval calls (all read variants) |19 |20 |+1 |
| Bounded detail retrieval calls |7 |8 |+1 |
| Participant authoring wall seconds |399.549 |386.929 |-12.620 (-3.2%) |
| Snapshot generation + verification seconds |0 |0.018394 |+0.018394 |
| Retrieval dispatch seconds |0.239007 |0.333819 |+0.094813 |
| Retrieval response local token estimate |18,318 |21,138 |+2,820 |
| Scored validation/lowering seconds |0.004821 |0.004719 |-0.000101 |
| Acceptance interval seconds |0.157168 |0.164415 |+0.007247 |

Wall intervals overlap: authoring includes CLI/snapshot/evaluation/export; CLI
includes MCP; acceptance includes validation and VM. Do not add them as independent
effort. Snapshot generation includes verification/re-expansion and is not isolated
string serialization. Retrieval local response estimates include the JSON result
envelope; they are not actual provider-token allocations or a billing measurement.

| Task | A processed input | B processed input | A wall seconds | B wall seconds |
| --- | ---: | ---: | ---: | ---: |
| T1 |98,154 |69,722 |140.215 |125.536 |
| T2 |100,635 |74,091 |124.341 |127.199 |
| T3 |98,061 |73,770 |134.993 |134.194 |

The modification stage alone used244,575 processed input tokens for A versus161,748
for B. Base stages used52,275 versus55,835. Independent base-authoring variation
is included rather than normalized away. Total model calls increased by one; MCP
calls decreased by three. Retrieval increased slightly and offset some savings,
but did not erase the descriptive processed-input difference. Reported noncached
input increased7.5%, so lower processed volume is not proof of lower monetary cost.
The timing result is mainly T1; T2 favored A and T3 was nearly equal. No consistent
development-time improvement or model-call reduction is established.

## Token attribution and ordinary summaries

Visible repeated estimates by origin are:

| Category | A estimate | B estimate |
| --- | ---: | ---: |
| Configured fixed instructions |1,800 |1,850 |
| Lykoi guidance |10,260 |10,545 |
| Tool schemas (delivery hypothesis) |24,624 |25,308 |
| Task requirements |9,771 |10,234 |
| Current snapshot state |0 |35,925 |
| Prior generated history |50,673 |19,440 |
| Tool feedback |53,843 |18,970 |
| Retrieval results |39,080 |27,142 |
| Signed provider-minus-estimate residual |106,799 |68,169 |

New generated-output estimates are9,908/9,881, separate from input. Generated text
and arguments become historical input only on later calls; retrieval responses are
not also tool feedback. Unique estimates deduplicate body hashes separately from
repeated volume. Snapshot text duplicates some original constraints intentionally;
actual transmitted occurrences remain counted. Other fixed/system content is unknown.

Repeated conversation/feedback/retrieval volume is visibly reduced and replaced by
current-state text. Tool feedback is A's largest individual visible local category;
snapshot state is B's largest. **Dominant provider-token categories are not established**:
the estimator is not the tokenizer, schema delivery is hypothetical, serialization
is unknown and residuals are large. No category-specific percentages or hidden
instruction inference are warranted. Semantic reasoning effort is not isolated.

For an ordinary deterministic latest-state extraction, we retained original
requirement, objective, exact definitions and caller bindings without the snapshot's
redundant indexes, generation, validation or history metadata. [Offline size control](r6_38/CONTINUATION-EQUIVALENCE.json)
is **4,223/4,437/4,454 bytes**, versus snapshot **6,379/6,592/6,611 bytes** under the
same local JSON serialization. The generic summary is smaller; it was not tested
as an authoring track and lacks the qualified fail-closed registry verification.
This is a size/coverage diagnostic, not proof of equivalent authoring reliability.

The registry demonstrates useful exact provenance, closure and stale/tamper checks.
No measurable incremental **authoring-efficiency** value beyond ordinary history
reduction/summarization is established. The three small tasks have similar history
length and shape; savings versus complexity or longer histories remain untested.

## Architectural recommendation, integrity and stop

Keep exact symbolic snapshots plus bounded retrieval as a **qualified nonproduction
continuation option**. Do not replace the default context policy or claim Lykoi-wide
superiority from this exploratory sample. Do not optimize away constraints based
on the observed token difference. Fully costed benefit remains unresolved, hence
`R6_38_COMPARISON_INCONCLUSIVE` rather than an advantage/equivalence verdict.

Recommended next separately authorized experiment: qualify safe actual upstream
message/tool-section identities and model-matched tokenizer accounting, then freeze
a three-way full-history /ordinary deterministic summary /registry snapshot study
with identical pre-modification artifact state, varied history lengths and repeated
counterbalanced trials. Account for complete setup/retrieval costs and billing where
reported. No such follow-up is authorized or started here.

[Publication verification](r6_38/VERIFICATION.json) checks all3,374 protected hashes,
the prospective task freeze, additive publication identities, JSON/whitespace,
relative links, credential-pattern scans, unchanged tracked files and
`git diff --check`. The prior publications remain byte-identical. The initial
protocol/source freeze excludes later analysis and supplemental controls explicitly;
these never alter participant instructions or scored expectations.

**Stopped after the bounded six-run comparison, replay, accounting and publication.
Await explicit authorization before further work.**
