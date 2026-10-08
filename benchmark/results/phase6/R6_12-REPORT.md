# R6.12 — Instrumented AI-native development benchmark

**Final classification: `R6_12_EXPLORATORY_COMPARISON_ONLY`.**

Conventional Python completed **5/5 tasks, 80/80 base cases**, and **3/3 staged
modifications, 72/72 original/new observations**, all first attempts. It had **zero
repairs and zero regressions on 48 original cases**. Production Lykoi and the
frozen experimental VM each recorded **five base and three modification capability
assessments**, with **0 complete implementations and no scored acceptance execution**.
Their unexecuted cases are **NOT_REACHED**, not observed test failures.

Actual session token usage was recovered from sanitized OpenCode exports after
evaluation. **Actual API billing cost remains unavailable.** No task succeeded on
all three tracks, so there is **no matched-behavior token/time/cost efficiency
comparison**. Python has a practical completion/coverage advantage on this batch;
the results do not establish general superiority, statistical significance, or the
least effort for equivalent successful behavior.

## 1. Authorization, prospective freeze and preservation

The owner's R6.12 request authorizes this bounded comparison, fresh sessions and
publication, without language expansion. Initial Git status was clean at HEAD
`eb5985e7abdcb71e24800168304706f22de05e2f`, tree
`292813595abeb711cd2dd1e49548f7104667221e`.

[BASELINE.json](r6_12/BASELINE.json) records exact protected-file SHA-256 identities,
the **26-construct accounting ledger**, Python/platform identities and actual command
outputs. Production validation/safety passed; **116 baseline unittest methods**
passed: 22 compiler, 9 application, 3 historical baseline and 82 experimental VM.
These preservation tests are not scored tasks. R6.11's protected identities were
checked against the unchanged files before task selection. New requirements were
then prepared and [FREEZE.json](r6_12/FREEZE.json) written **before any track start**.

[Protocol 1](r6_12/PROTOCOL.md) fixes five tasks, three changes, 900 seconds per
task/track/stage, one initial candidate plus at most two repairs, 10 seconds per
case, and base/modification session caps of 4500/2700 seconds. There is no invented
token ceiling. All recorded terminal intervals are within budget. One development
trial per assignment; verification replays are not repeated authoring trials.

Production compiler/lowerer/runtime/schema/model and R6.10 interpreter are unchanged.
R6.3–R6.11 artifacts are byte-preserved. **P6-A04 acceptance executions: 0;
P6-A05 not accessed.** No new semantic operation, benchmark-specific capability,
provider dependency, credential publication or isolation framework was introduced.

## 2. Tasks, provenance and shared formal contracts

A fresh preparer received the research requirements and protocol, with instructions
not to inspect language capabilities or past task contracts. Selection was synthetic,
separate-prompt preparation, **not externally sourced or independently attested
cognition**. Inherited repository guidance included historical capability summaries;
[provenance](r6_12/tasks/PROVENANCE.md) discloses that exposure. No exact prior task
contract/implementation was reused. None is an R6.11 task, CFG66, DSV66 or BXC66.

| Task | Shared behavioral requirements | Base cases | New cases |
| --- | --- | ---: | ---: |
| [T1 Stock holds](r6_12/tasks/T1/contract.md) | Whole-request validation, ordered reserve/release/ship, historical IDs, coupled counters, sorted observations | 15 | 8 |
| [T2 Optimal schedule](r6_12/tasks/T2/contract.md) | Dependency/cycle precedence, deadlines, globally optimal weighted completion, lexical ties, up to 7 jobs | 17 | — |
| [T3 Binary normalization](r6_12/tasks/T3/contract.md) | Framing/checksum precedence, validation before transform, reverse/sort/prune, canonical re-encoding | 17 | 8 |
| [T4 Byte patches](r6_12/tasks/T4/contract.md) | Original-coordinate comparisons, conditional application, ordered conflict errors, variable-length assembly | 16 | 8 |
| [T5 Ranked-choice rounds](r6_12/tasks/T5/contract.md) | Weighted first-active ranking, exhaustion, strict majority, deterministic elimination, full round history | 15 | — |
| Total | Five bounded multi-constraint domains | **80** | **24** |

Each numbered contract is the **one shared formal behavioral requirement**, with
exact JSON shapes, invalid-input phases, deterministic ordering, environment and
resource bounds. These are benchmark contracts, not production-approved FRC/V1
pipeline artifacts. Every track receives identical observations; representation
may differ. Acceptance JSON stores explicit expected outputs, not candidate-derived
expectations. Expectations are visible for the assigned stage. Transport-invalid
JSON, duplicate input-object keys and requests above 16 KiB are explicitly outside
the contract. Other declared type/range violations are scored.

Tasks add state evolution, bounded optimization, integrity/reordering and conditional
splicing beyond the previous tiny pilot. Selection was not filtered to production
capabilities, but the resulting mix has **no wholly production/VM-supported task**.
That is a coverage finding and a major limit on the primary efficiency question.

## 3. Track identities and authoring procedure

| Track | Permitted implementation | Outcome evidence |
| --- | --- | --- |
| A | Python standard-library programs | Eight preserved candidates and RESULT-1 records |
| B | Frozen production Lykoi only | Eight GAP records and source-anchored CAPABILITY assessments; no model/compiler attempt |
| C | Frozen R6.10 semantic-plan-1 only | Eight GAP records and operation/bound assessments; no plan/interpreter attempt |

Base tracks were dispatched A,B,C in separate fresh task sessions; modifications
were dispatched C,B,A in another three fresh sessions. Execution was parallel and
not a balanced per-task crossover. Each author started its clean own directory
before reading that task's assigned contract. Other-track reads were prohibited;
substantive reads are disclosed in each track's AUTHORING.md/MODIFICATIONS.md.
Baseline candidates and first results were preserved. Pass/gap ended the task.

Every exported assistant-response record identifies **model `gpt-6.1-sol`, provider
`openai`**. No model switch was observed. Effective reasoning/sampling configuration
and provider-hidden context remain unobservable. CPython **3.14.3**, Windows AMD64
and installed OpenCode **1.18.32** were observed. The installed CLI does not attest
every aspect of the active harness. No extra provider generation was dispatched
outside the harness task sessions.

## 4. Functional correctness and capability coverage

| Task | A Python | A elapsed s | B production assessment | C VM assessment |
| --- | --- | ---: | --- | --- |
| T1 | 15/15, first attempt | 35.952 | Request record/union validation profile | Ordered state fold and sorting |
| T2 | 17/17, first attempt | 28.501 | Schedule-valued synthesis/optimal result bindings | Permutation generation/optimal selection |
| T3 | 17/17, first attempt | 28.177 | Binary cursor/framing/codec bindings | XOR plus payload reorder/accumulation |
| T4 | 16/16, first attempt | 31.907 | Byte slice/splice/assembly bindings | Original slices and sorted patch assembly |
| T5 | 15/15, first attempt | 31.985 | Correlated first-active/grouped-round result bindings | First-active selection/grouped round-state fold |
| Overall | **5/5; 80/80 executed** | **156.523** | **0/5; 80 NOT_REACHED** | **0/5; 80 NOT_REACHED** |

[Capability matrix](r6_12/CAPABILITY-COVERAGE.md) distinguishes complete coverage,
useful partial compositions and uncertainty. Per-task source/code references are
retained in B/C CAPABILITY.md files. Missing named task primitives alone are not
the justification: the assessments considered predicates, finite enumeration,
cardinality/checked-addition alternatives, existing state/atomic compositions and
VM unrolling. They are **current interface/composition assessments**, not proofs
that the abstract kernel cannot express these behaviors. Especially for C, no
complete within-bound composition was identified; exhaustive exclusion was not proved.

No scored runtime error, timeout or Python authoring failure was observed. There
were **no scored compiler/interpreter executions**, so their failure rate and
authoring reliability cannot be measured. Gap assessment times are not successful
development times. No partial subset is credited as a complete task success.

## 5. Staged modifications and regressions

New contracts were frozen in separate files before base dispatch. Fresh modification
authors received only their own original artifacts and assigned stage. Explicit
disclosures report no base-author reading of later-stage contents. Hash checks read
file bytes internally without returning requirement contents. **Staged disclosure
was operationally observed, but certified unseen/blind modification testing is not
claimed**: filesystem containment and full provider-context logs are unavailable.
No observed early-content incident required a contaminated-stage designation;
unattested access remains a limitation for every stage.

| Change | A original | A new | A elapsed s | B/C result |
| --- | ---: | ---: | ---: | --- |
| [T1 resize active holds](r6_12/tasks/T1/modification/contract.md) | 15/15 | 8/8 | 68.025 | Retained base blockers; additional delta/coupled-state bindings |
| [T3 greedy coalescing](r6_12/tasks/T3/modification/contract.md) | 17/17 | 8/8 | 33.640 | Retained binary/reorder blockers; evolving payload accumulation |
| [T4 absence-conditioned patches](r6_12/tasks/T4/modification/contract.md) | 16/16 | 8/8 | 40.608 | NOT equality available, but original slicing/assembly still missing |
| Total | **48/48** | **24/24** | **142.272** | **0/3 each; 72 cases NOT_REACHED each** |

A passed all modifications on first attempts with **0 repairs and 0/48 original-case
regressions**. B/C regression counts/rates are **unavailable**, not zero, because no
base implementation or modification execution exists. The 72 observations include
48 repeated originals; they are not 72 distinct new requirements. This establishes
bounded extension success for A, not general maintainability or long-term safety.

## 6. Actual usage, cost and effort

[TELEMETRY.json](r6_12/TELEMETRY.json) preserves reported per-response usage/model/
time metadata. [USAGE-SUMMARY.json](r6_12/USAGE-SUMMARY.json) and
[EFFORT.md](r6_12/EFFORT.md) give complete session totals and per-task **partial**
interval allocations with boundary-straddling responses explicitly unallocated.

| Session | Input | Cached read | Output | Reasoning | Responses |
| --- | ---: | ---: | ---: | ---: | ---: |
| A base | 170,739 | 1,553,920 | 8,855 | 221 | 23 |
| A modifications | 133,629 | 1,717,632 | 9,693 | 318 | 25 |
| B base assessments | 140,073 | 3,135,488 | 10,192 | 1,516 | 30 |
| B modification assessments | 96,936 | 1,762,816 | 7,164 | 179 | 24 |
| C base assessments | 99,230 | 2,054,400 | 7,235 | 814 | 26 |
| C modification assessments | 88,402 | 1,577,856 | 6,521 | 184 | 24 |

These are **actual OpenCode-reported fields**, not estimates from generated source.
Cache-read is separate from input in these exports; reported total equals input +
cache-read + output + reasoning. Cache-write is zero. Counts are completed assistant
responses with usage, not an attested count of underlying provider retries/HTTP
requests. Whole sessions include setup, documentation, recording and final responses.
Repeated inherited guidance/cached context makes these unsuitable as standalone
implementation-token costs. Preparation usage is separately retained (114,012 input,
429,952 cached-read, 13,143 output, 3,436 reasoning; 10 responses). Post-result review
usage is outside scoring in REVIEW-USAGE.json. Coordinator/publication usage is not
fully allocated; no complete experiment-wide usage/cost total is asserted.

Every response reports harness **cost=0**. Billing/pricing authority was not available,
so **actual API cost and cost estimate are null**. Zero metadata is not a claim that
the API was free. No source-length token estimate or fabricated price is published.

A task start→acceptance intervals total **298.795 seconds**, including **5.164
seconds of scored test subprocesses**. The 293.631-second residual is not pure AI
reasoning: it includes reads, writing, tool latency and other session overhead.
B/C terminal assessment intervals total **255.530/306.675 seconds**, respectively;
they are not faster/slower accepted development. Full response/tool durations are
separately reported, and may overlap; they cannot be summed into pure development
CPU time. Repairs are zero for A; B/C had zero candidate attempts rather than a
demonstrated zero-repair success rate.

### Late instrumentation discovery — prospective deviation

At baseline, direct harness counters/configuration exports were unavailable and the
protocol allowed exploratory evidence. After results, targeted CLI help revealed
`opencode export --sanitize --pure`, which recovered usage for all seven assigned
preparation/development sessions. The write-once START/baseline and author disclosures
retain their original null-at-the-time statements; this report adds the actual data
without rewriting history. The pre-selection supported-telemetry inventory was
therefore **incomplete**, and usage was not monitored prospectively.

The supplementary model listing contains 883 identifiers across eight providers,
not authenticated usable-provider configurations. It was discovered post-evaluation;
no other configuration was used or credential inspected. Sanitized exports redact
tool inputs, so [tool audit](r6_12/ACCESS-TOOL-AUDIT.json) attests reported names/times,
not read paths or OS containment. No reasoning-configuration identity is established.

## 7. Verification, limitations and analysis

[Manual review](r6_12/VERIFICATION-REVIEW.md) freshly rederived **all 104 explicit
expectations** and inspected eight candidates, finding no incorrect expectation,
fixture table fitting or concrete in-contract candidate violation. It is correlated
same-model review, not independent-model confirmation. [REPLAY.json](r6_12/REPLAY.json)
records **152/152 exact fresh-process replays**, separate from 152 scored observations.
Frozen inputs, candidate hashes and protected historical/implementation identities
match. Publication identities and tracked/untracked text whitespace checks pass;
`git diff --check` passes.

Threats to validity and concrete limitations:

1. Five synthetic tasks from one capability-informed inherited context; no external
   independent source or statistical significance. One trial each, no variance estimate.
2. No common successful task across languages; capability coverage dominates the
   result. Static gap conclusions are not exhaustive nonexpressibility proofs.
3. Fresh prompts improve observed separation but cannot certify filesystem, cognition,
   hidden provider context or blind staged disclosure. No other-track substantive
   read was reported; inherited summaries and model familiarity remain asymmetric.
4. Same model/provider IDs are observed, but effective reasoning/sampling settings
   are not attested. Documentation breadth differs substantially by track.
5. Tokens recovered late, incomplete initial inventory, no authoritative billing;
   task interval allocation excludes boundary responses and setup/documentation.
6. Parallel execution permits resource contention; reversed dispatch order is not
   a rigorous per-task counterbalance. Timings are descriptive, not causal estimates.
7. Acceptance omissions remain for many malformed nested shapes, maximum-size
   interactions and combined-error boundaries. No universal correctness follows.
8. Recorder JSON parsing can collapse duplicate output keys. Current candidates
   emit ordinary unique-key objects; no affected outcome was found. Time cap is
   checked before evaluation and retrospectively against final records; session caps
   are not actively enforced. Every observed assignment stayed within its cap.
9. No scored B/C executable exists, so regression/repair reliability and maintainability
   cannot be compared. Review clarifies VM's 2048 expression-visit bound concerns
   validation traversal, not a runtime-expression budget. Historical artifacts untouched.

**Analysis:** Python delivered the most accepted behavior on this harder batch.
Actual usage now makes development/assessment effort inspectable, but comparing
successful Python authoring with semantic-track gap analysis as an efficiency ratio
would be invalid. This evidence supports an operational Python coverage advantage
on these five contracts, **not an AI-native language-efficiency advantage or general
language ranking**. The primary least-effort-for-equivalent-behavior question remains
unanswered; completed classification is not justified.

## 8. Recommended priorities and stop

1. Before another comparison, check sanitized usage export prospectively, distinguish
   cached/uncached input and obtain authoritative pricing/billing or retain null cost.
2. Use independently supplied tasks with a broader mix: retain genuine coverage
   challenges and include whole tasks demonstrably expressible on all tracks so a
   matched-success efficiency comparison is possible. Do not change this frozen corpus.
3. Separately authorize any general semantic investigation of typed request records,
   state folds, correlated/grouped results, byte slices/assembly and bounded search.
   First distinguish interface composition gaps from new meanings; no task-specific
   opcode or production/VM modification is implemented by this round.
4. If future results require blind modification claims, provide auditable staged
   input control; use repeat trials only within a newly fixed budget.

**Stopped after the bounded comparison and publication. Await explicit owner
authorization before any further benchmark, repair or language development.**
