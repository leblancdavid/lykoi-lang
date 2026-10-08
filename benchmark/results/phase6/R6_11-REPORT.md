# R6.11 — AI-native development comparison pilot

**Final classification: `R6_11_EXPLORATORY_COMPARISON_ONLY`.**

Python and the **R6.10 experimental semantic interpreter** each passed **4/4 base
tasks (49/49 acceptance cases)** and **2/2 modifications (40/40 combined original/new
cases)** on the first recorded attempt. Both had zero repairs and zero observed
regressions. Production Lykoi completed **0 scored tasks; it was not scored**.
These are finite behavioral observations, not proofs of correctness or an efficiency
advantage. Same-context authorship, capability-aware synthetic selection and missing
token/billing telemetry prevent controlled-comparison or superiority claims.

## 1. Authorization, baseline and selection

The owner's R6.11 authorization permits bounded comparative execution and publication,
preserving production, the experimental VM and historical records. No capability
expansion is performed. [Protocol](r6_11/PROTOCOL.md) records prospective scope/caps;
[inventory](r6_11/BASELINE-INVENTORY.md) distinguishes production K01–K26 from
semantic-plan-1. The original task-manager benchmark/protocol remains untouched.

Initial Git status was clean at `ba2d4244b367f0bf87bb49f9e9c1ed5b81e04ebe`;
tree `a35963b9c653e99a8d6c564df2c31930363d5921`. The subsequent
[baseline](r6_11/BASELINE.json) pins **446 protected tracked files** and verifies
**47 historical publication hashes**. Its status includes this round's preparation
directory, accurately distinguishing the initial clean check from the later snapshot.

Four small standalone synthetic tasks were chosen before implementation to exercise
shared bounded byte/record operations: structured transformation, validation/error
handling, ordered processing and configuration interpretation. Generic operation
examples were exposed; no exact tailored task implementation was known or reused.
Task selection and requirement/oracle authorship were this same capability-informed
session. Consequently independent sourcing in the stronger sense was **not achieved**.
The corpus has a strong simplicity and capability-selection bias.

All tasks require raw-byte recognition, which the existing production normal profiles
do not admit. Therefore the Lykoi track uses the experimental VM throughout. This
static profile gap is not four executed compiler failures or evidence that the
semantic paradigm cannot express the behavior. No production/experimental capability
merge is claimed. Scored tasks are not CFG66, DSV66, BXC66 or curated external tasks.

## 2. Frozen requirements and acceptance

[TASKS.md](r6_11/TASKS.md) specifies input/output domains, error offsets and precedence,
order/multiplicity, boundaries, immutable inputs and absence of persistence. Its M2/M4
sections separately fix the modification behavior before base authoring.
[ACCEPTANCE.json](r6_11/ACCEPTANCE.json) contains explicit expected observations.
The frozen runner adds one shared 65-byte input-bound check per suite.

[FREEZE.json](r6_11/FREEZE.json) pins protocol, task text, acceptance data, recorder,
transport and four [FRC envelopes](r6_11/contracts/). Existing
FormalRequirementContract-0.1 validation accepted all four synthetic, source-bound
bookkeeping envelopes. Review remains null. This is not source-independent fidelity
review, production WHAT approval or successful native coverage/BDI/adequacy/V1.
The modification contracts are frozen textual sections, not separately approved
production FRCs. No historical gate is invoked or waived for the experimental API.

Acceptance was frozen before every candidate and remained unchanged. Modification
suites retain all original cases; newly admitted spellings were reserved for the new
suites before freeze. All expectations are visible to the common author context.
Frozen suite validation used value equality; publication additionally verified exact
JSON types against unchanged expectations, addressing Boolean/integer conflation in
Python equality without changing the scorer, candidates or acceptance requirements.

## 3. Tracks and environment

Session model/provider: **OpenAI `openai/gpt-6.1-sol` / `gpt-6.1-sol`**, same active
session for all authoring. Reasoning/sampling settings, effective full prompt context,
per-track token counters and billing are not exposed. Installed OpenCode CLI **1.18.32**
does not establish active harness build identity. Windows 11 AMD64 10.0.26300,
CPython **3.14.3**, Git **2.52.0.windows.1**, PowerShell **7.6.6** were recorded.
No separate provider dispatch, credential access or mandatory provider dependency.

Python candidates use standard library only. Experimental candidates are explicit
JSON plans interpreted by the unchanged VM. The common transport converts hex to
bytes and projects declared result/error fields; it delegates no task behavior to
Python for the experimental track. No layout is required; assemble=False is explicit.
VM validation still checks each required unused encode node. Base plans contain
5/8/9/10 structural nodes; modification plans contain 10/11, within the unchanged cap.

Clean task/track/stage directories retain starting identities and complete artifacts.
Counterbalanced order: Python first T1/T3, VM first T2/T4; modifications Python first
M2, VM first M4. Each received a 900-second wall cap, nominal 8,000-token cap, at most
three attempts and identical full-suite testing/repair opportunities. All passed on
attempt one within time caps. **Token cap could not be enforced**, and equality of
actual reasoning/context/token consumption cannot be established.

Directory/process boundaries do not isolate filesystem or cognition. The same author
necessarily remembers both candidates. No authoring read of the other-track artifact
was issued, but conversation contamination cannot be prevented. Task-relevant docs
were available; equal documentation consumption and prior familiarity were not
controlled. R6.9's fail-closed review runner was not bypassed or used.

## 4. Base comparison

Seconds are start-record to acceptance completion, including tools/process latency.

| Task | Behavior | Python cases | VM cases | Python s | VM s | First attempt |
| --- | --- | --- | --- | --- | --- | --- |
| T1 | Ordered two-byte fields and mathematical sum | 11/11 | 11/11 | 22.181 | 22.433 | Both pass |
| T2 | Ordered samples; immediate range/occurrence errors | 11/11 | 11/11 | 17.567 | 22.328 | Both pass |
| T3 | Structural parse, uniqueness, stable filtering | 12/12 | 12/12 | 18.426 | 17.937 | Both pass |
| T4 | ASCII config, explicit mode, error precedence | 15/15 | 15/15 | 15.719 | 16.922 | Both pass |
| Total | Four independent base tasks | **49/49** | **49/49** | **73.893** | **79.620** | **4/4 each** |

Each row's full command/input/expected/actual/stdout/stderr/return-code evidence is
in its workspace RESULT-1.json, referenced by [COMPARISON.json](r6_11/COMPARISON.json).
Conventional outputs and VM outputs satisfy exactly the same finite observations.
There is no scored production result and no general expressiveness verdict.

## 5. Incremental modifications and regressions

| Change | Required maintenance | Original cases each | New-suite cases each | Python s | VM s |
| --- | --- | --- | --- | --- | --- |
| M2 | Add B samples with cap20; preserve A cap10 | 11/11 | 7/7 | 14.006 | 20.434 |
| M4 | Add auto config; preserve on/off schedule | 15/15 | 7/7 | 16.115 | 19.272 |
| Total | 2/2 changes pass on both tracks | **26/26** | **14/14** | **30.121** | **39.705** |

Each new suite has six new-behavior fixtures plus a repeated common input-limit
fixture. Therefore 14 new-suite observations are not 14 distinct newly specified
behaviors. Each track passed 40/40 combined observations, had **0 repairs** and
**0 regression failures**. The Python changes add prefix dispatch/range binding;
VM changes add an explicit choice/binding or literal branch, retaining stable node
identities elsewhere. Source snapshots permit inspection. This measures bounded
extension success, not broader maintainability, migration or long-term maintenance.
Anticipation is possible because modification freeze text was already in context.

## 6. Tokens, time and cost

| Measurement | Python | Experimental VM |
| --- | --- | --- |
| Base elapsed seconds | 73.893 | 79.620 |
| Additional modification seconds | 30.121 | 39.705 |
| Total recorded elapsed seconds | 104.014 | 119.325 |
| Input/output/reasoning tokens | Unavailable | Unavailable |
| Model/API cost USD | Unavailable | Unavailable |
| Repairs | 0 | 0 |

Python's recorded total is **15.311 seconds lower**, with shorter intervals in three
base tasks and both modifications; the VM's T3 interval is 0.489 seconds lower.
These small differences are dominated by possible session/tool/process overhead and
uncontrolled context; they are descriptive intervals, **not measured model-efficiency
or statistically significant superiority**. Artifact bytes are retained as an
inspection aid, never substituted for tokens. Whole-session preparation/publication
time is not allocated to tracks. No token/cost difference can be calculated.

## 7. Failure classification and tooling maturity

| Axis | Observation |
| --- | --- |
| Functional acceptance failures | 0/178 scored process observations across both tracks |
| AI authoring errors | None observed in the 12 first candidate attempts; finite tests only |
| Production capability/profile gap | Raw-byte recognition absent; production scoring NOT_REACHED |
| Experimental capability gaps encountered | None blocking these small plans; typing/encode/cost gaps remain outside this task set |
| Compiler/interpreter execution failures | None observed; no scored production compilation |
| Infrastructure/process failures | No process timeout, exception or invalid output observed |
| Tooling/measurement limitations | No enforced token cap/meter, no full prompt/transcript export, no separation; equality checker type weakness caught by exact replay |
| Requirement ambiguities | No unresolved behavior question during execution; same-agent formalization lacks independent review |

Production static typing/profile tooling and VM runtime type rejection are different
guarantees. Tests cannot attribute the prototype's omitted guarantees to the semantic
paradigm. Ordinary Python gave shorter descriptive intervals on most tasks; the VM
made the required parse/check/selection order and result construction explicit in
closed data. Neither representation's general authoring reliability is established.

## 8. Validity and protocol deviations

1. Same-context author, requirement writer, selector and verifier; no independent
   reviewer, hidden tests or independently supplied requirements. Shared solutions and
   expected outputs in conversation can aid second-track authoring despite directory separation.
2. Tasks are tiny, synthetic and selected with knowledge of the experimental envelope.
   No substantial persistence, full applications, production compilation or complex maintenance.
3. All Lykoi scoring is experimental; the primary production comparison is unanswered.
4. Same nominal time/attempt budgets, but token equality/cap enforcement and exact
   reasoning configuration are unverified. Tokens and costs are explicitly null.
5. Complete effective prompt identity and all model/tool interactions are not exportable.
   Frozen task/assignment hashes, candidate artifacts and subprocess commands are retained
   in [authoring ledger](r6_11/AUTHORING-LEDGER.md); this is partial telemetry.
6. Wall intervals include tool and test startup. Python imports code; VM imports its
   engine, loads JSON and validates every process. Prior language familiarity differs.
7. Modification content is frozen early but cannot be cognitively withheld. Regression
   coverage is 26 original cases per track, not exhaustive preservation of the domain.
8. Frozen equality checker can conflate types; all recorded and replayed outputs also
   pass exact canonical-JSON comparison against original expectations. No affected
   candidate was repaired and no expectation changed.

## 9. Verification and publication

[CHECKS.json](r6_11/CHECKS.json) records validation/safety and **116 passing unittest
methods**: 22 compiler, 9 application, 3 Phase 5 baseline, 82 VM. These are separate
preservation checks, not scored pilot cases. Historical CFG66/DSV66/BXC66 regression
methods remain unscored. [REPLAY.json](r6_11/REPLAY.json) records **178/178 exact fresh
process replays**, in addition to 178 original scored observations (356 pilot process
invocations overall). Source hashes match every initial result; frozen acceptance and
contract identities remain intact. Protected byte verification and additive guidance
checks pass. [Publication manifest](r6_11/PUBLICATION-IDENTITIES.json) pins publication
files, excluding itself. `git diff --check` and new-file whitespace checks pass.

Recheck existing publication without rescoring/repair:

```powershell
python -B benchmark/results/phase6/r6_11/run.py verify
python -B benchmark/results/phase6/r6_11/publish.py publication
```

Production kernel remains **26**. Production implementation, R6.10 VM and R6.3–R6.10
artifacts remain unchanged. P6-A04 acceptance executions **0**; P6-A05 not accessed.
No new semantic operation or provider dependency; no credential publication.

## 10. Priorities and stop

Evidence supports the **feasibility of a separately authorized better-instrumented
benchmark**, not automatic expansion or either approach's superiority. Priorities:

1. Independently supplied requirements and verifiable track context/access separation;
   retain exploratory labels wherever that is unavailable.
2. Per-invocation input/output/reasoning tokens, billing and timestamps with effective
   reasoning/prompt identities; equal enforced budgets and exact JSON-type acceptance.
3. A task mix exercising production profiles separately from experimental parsing,
   richer ordered transformations, realistic maintenance and failure/repair scenarios.
4. Preserve the frozen prototype; consider its documented typing/encode/cost gaps only
   in separately authorized development, rather than fitting operations to this pilot.

**Stopped after bounded pilot and publication. Await owner authorization before
benchmark expansion, reruns/repairs, provider qualification or language development.**
