# R6.29 — Guarded semantic construction

**Final classification: `R6_29_CONSTRUCTION_PARTIAL`.**

The capability gate passed and GPT-6.1 Sol constructed a valid guarded symbolic
program in7 semantic calls with0 corrections. Frozen functional acceptance passes
**19/23 observations**; **69/69 AI-independent replay observations** match exactly.
All three genuine guard/overflow conflicts stop at the guard before arithmetic.
The four acceptance failures are a **coordinator frozen-expectation defect**:
the manifest expects guard errors at stage `structure`, while the unchanged VM
correctly reports stage `validation`. The frozen contract, first result and artifact
remain unchanged. Full acceptance is false, so a supported classification is withheld.

## Authorization, baseline and capability gate

The owner authorized one bounded unscored experiment with maximum16 semantic calls,
four correction turns and one authoring session. Initial Git status was clean.
[Baseline](r6_29/BASELINE.json) verifies **1,530 protected identities**, complete
R6.28 publication/receipt and supported classification, the preserved R6.27 route
qualification and exact installed OpenCode executable identity. Production kernel
remains **26 constructs**. Production compiler/lowerer/runtime, R6.10 VM, R6.18
wrapper, R6.23 adapter, R6.24 dispatcher and R6.25 tool definitions/transport are
unchanged. R6.3–R6.28 history remains exact.

[Inventory](r6_29/INVENTORY.md) maps each required behavior to existing specifications.
The [deterministic scripted witness](r6_29/CAPABILITY-WITNESS.json) runs before task
selection, with zero model calls. The original real Session accepts a computed
Bool predicate, an ordered Bool guard and two dependent Int64 additions. A true
guard with n=1 returns3. A false guard with n=Int64_MAX returns WitnessDenied;
the same n with a true guard reaches OVERFLOW. This establishes expressibility
and absorbing guard precedence without an AI-generated capability solution.

The witness has a different signature and predicate from the construction task
and is not included in the model prompt. Its raw native error stages were available
to the coordinator; the later stage-label transcription error is the coordinator's
responsibility, not missing semantics.

## Freeze and model exposure

[Protocol](r6_29/PROTOCOL.md), [requirement](r6_29/REQUIREMENT.json),
[acceptance](r6_29/ACCEPTANCE.json), [prompt](r6_29/PROMPT.json) and
[pre-inference freeze](r6_29/FREEZE.json) precede participant inference.

Target `GuardedLeft(x:Int64,y:Int64)` has four explicitly ordered steps:

1. Store Bool predicate `x <= y`.
2. Check that predicate, declared code GuardDenied and literal site0.
3. Store checked Int64 sum `x + y`.
4. Store checked Int64 sum of the first sum and x; return it.

Exact host argument signature and native type/overflow/UInt16BE encoding behavior
are specified. The requirement is fresh, coordinator-authored, synthetic and
capability-tailored. It explicitly scaffolds the operation sequence; no completed
implementation is supplied. It tests construction feasibility, not algorithm
discovery, independence, held-out generalization or comparative benefit.

[Tool exposure](r6_29/TOOL-EXPOSURE.json) retains the four original truthful
descriptions: declare_input, apply_operation, define_result and validate_candidate.
The only schema publication delta is the R6.27-qualified root object annotation.
Original schemas validate actual arguments. R6.25 normalization → R6.24 Session
→ R6.23 adapter → R6.18 validation/expansion → R6.10 execution is the actual backend.

The model is observed as **openai/gpt-6.1-sol**, using the pinned OpenCode1.18.32
route with requested high variant, output bound4,096 and21 completion steps.
Pure-process UTF-8 stdin delivery matches the exact exported user text. Only
Lykoi tools are enabled. Historical helper launch metadata retains agent key r628
and the R6.28 session title; configuration, prompt, endpoint and evidence are
R6.29-local. This metadata does not substitute another experiment or model.
Effective reasoning and hidden-context exclusion remain unattested.

## Model-authored artifact and lineage

The one authoring session completes with **7/16 calls**, **0/4 correction turns**:
declare two inputs, append Bool predicate, append check, append first addition,
append dependent addition, define result, validate. All seven argument objects
are valid and all seven operations succeed. All four tool names are invoked.
No manual semantic repair or second authoring attempt occurs.

[LIVE](r6_29/LIVE/) preserves raw MCP requests/responses, normalized arguments,
dispatch diagnostics/times, OpenCode events/stderr, exported session, exact delivery,
state, [compact packet](r6_29/LIVE/SYMBOLIC-PACKET.json) and
[sealed symbolic artifact](r6_29/LIVE/ARTIFACT.json). Offline reconstruction from
the original model calls exactly reproduces packet and artifact and verifies native
OpenCode argument and feedback lineage.

| Identity | SHA256/content identity |
| --- | --- |
| Artifact file | `af0c491f532c5b998c926639965eb5ec443a5779b6441694e49074015be29385` |
| Canonical artifact | `bef996e75bd6dfbdb9a397e54b55fc0564751c6ed71d1bd6da277fd7ba03ea2e` |
| Typed definition | `c13eba61a93c860c7dae7c20aba92b3f4891db7dfc608d082a590960da653041` |

## Frozen functional acceptance

[Functional evidence](r6_29/FUNCTIONAL.json) preserves all23 expected/actual
observations with typed packages, complete expansion and identities, native VM
envelopes, provenance, work and ordered node-entry traces. Expansion produces7 VM
nodes. Exact expression/dependency/result structure is verified separately.

| Case category | Observations | Frozen result |
| --- | --- | --- |
| Accepted values: (2,5)→9, (0,0)→0, (-2,4)→0, (1,65533)→65535, (0,65535)→65535 | 5 | 5 PASS |
| False guard: ordinary and three competing-overflow cases | 4 | 4 FAIL: stage label only |
| First/second addition overflow and underflow | 4 | 4 PASS, correct arithmetic site |
| High/negative UInt16BE output rejection | 2 | 2 PASS |
| Bool/string/null invalid Int64 inputs | 3 | 3 PASS, TYPE |
| Float outside representation domain | 1 | 1 PASS, SHAPE |
| Out-of-range signed64 integer | 1 | 1 PASS, TYPE |
| Missing/extra signature, missing signature plus invalid type | 3 | 3 PASS, SHAPE first |

Successful executions consume0 bytes and use22 VM logical work. Wrapper rejections
occur before VM entry and retain full diagnostics. No successful partial result or
output is exposed on rejection. The guard errors are GuardDenied at offset0 and
the correct second step, with9 logical work; only their frozen stage label differs.

## Guard/overflow precedence and coordinator defect

The [post-result explanatory audit](r6_29/PRECEDENCE-AUDIT.json) preserves three
mathematically genuine conflicts:

| Inputs | Guard | Competing arithmetic without the guard | Native observation |
| --- | --- | --- | --- |
| (Int64_MAX,1) | false | First sum overflows | GuardDenied, validation stage |
| (2^62,0) | false | First sum fits; dependent second sum overflows | GuardDenied, validation stage |
| (-2,Int64_MIN) | false | First sum underflows | GuardDenied, validation stage |

Each trace contains only the two sequence entries, predicate and check; neither
addition is entered. Thus guard-first behavior is directly observed on inputs
with competing overflow, rather than inferred from nonconflicting examples.

The immutable acceptance manifest says `structure` for all four GuardDenied cases.
R6.10 check errors use `validation`. The frozen evaluator therefore correctly marks
those observations failed, and its original full-acceptance verification assertion
fails. [Failed verification](r6_29/FAILED-VERIFICATION.json) is retained. The additional
audit verifies integrity and explains this discrepancy; it **does not rescore** the
round or alter its requirement, manifest, evaluator or first result. Behavioral
precedence is supported locally, but full frozen acceptance is not achieved.

## AI-independent replay and offline checks

The author process terminates before acceptance/replay. [Replay](r6_29/REPLAY.json)
reloads only the saved artifact for each of three passes. **69/69 observations**
equal their initial23 records, including the four frozen expectation mismatches.
Compared data include typed results, error classifications/stages/sites, provenance,
logical work, full ordered entry/cursor/work/depth traces, typed package identities,
expanded plan identities and artifact identity. Timing is recorded separately.
There are zero model calls during acceptance, replay and publication.

Trace instrumentation delegates unchanged VM behavior and checks equality with the
uninstrumented public executor. [Offline checks](r6_29/OFFLINE-CHECKS.json) verify
raw model lineage, exact expressions, frozen results and all69 replay records.
The unchanged R6.25 transport regression suite passes **17/17 methods**.
These are integrity checks; their pass does not imply full functional acceptance.

## Measurements

[Measurements](r6_29/MEASUREMENTS.json) and [summary](r6_29/SUMMARY.json):

| Measurement | Observed |
| --- | --- |
| Authoring sessions / model completion calls | 1 / 8 |
| Semantic calls / valid arguments / successful operations | 7 / 7 / 7 |
| Invalid arguments / construction failures / correction turns | 0 / 0 / 0 |
| SDK input / output / reasoning tokens | 7,436 / 324 / 0 |
| Cached-read tokens / SDK total tokens | 1,152 / 8,912 |
| Session wall, including startup/tool work | 23.687s |
| Summed assistant-message elapsed, not pure inference | 21.735s |
| Deterministic tool dispatch total | 5.646ms |
| Final adapter construction / typed validation | 0.179ms / 0.197ms |
| Final adapter strict serialization / schema validation | 0.091ms / 2.118ms |
| Acceptance typed validation total | 2.528ms |
| Acceptance expansion total, including wrapper validation | 3.303ms |
| Acceptance VM total, including VM validation | 0.617ms |
| Invalid-host wrapper rejection total | 0.511ms |
| Unexpected provider/runtime errors | 0 observed |
| Functional acceptance / AI-free replay | 19/23 / 69/69 |

SDK cost0 is not a billing receipt. Pure inference time, API billing, effective
reasoning, raw upstream provider traffic and hidden retry counts are explicitly
unavailable. Reasoning tokens0 do not attest effective reasoning configuration.
The timings describe one tiny run and do not establish an efficiency advantage.

## Attribution, preservation and next experiment

[Failure analysis](r6_29/FAILURE-ANALYSIS.md) distinguishes a coordinator frozen
expectation defect from model argument/semantic errors, guard ordering, semantic
or tool expressibility, provider/runtime failure and exhaustion. No semantic or
model-authoring gap is demonstrated. Correction ability remains untested.

[Publication manifest](r6_29/PUBLICATION-IDENTITIES.json) and
[receipt](r6_29/VERIFICATION.json) bind report/evidence/additive documentation,
verify all protected identities and pre-inference freeze, JSON/links/whitespace,
credential-pattern checks and `git diff --check`. No credentials are collected or
published. No downloads, training, P6-A04 acceptance or P6-A05 access occur.
Provider-independent deterministic execution remains unchanged.

**Recommended next experiment, requiring separate authorization:** first qualify
prospective acceptance expectations against native error stages using a scripted
client before freezing; then conduct one fresh bounded guarded-construction task
through the same unchanged route with mixed guard/overflow conflicts and AI-free
replay. Keep R6.29's failed expectations and partial classification immutable.
Do not infer broad conditional branching, discovery/reuse, generalization or
comparative authoring benefit from this scaffolded artifact.

**Stopped after this one authoring session, deterministic evaluation and publication.
Await explicit authorization before further work.**
