# R6.40 — Adaptive symbolic discovery pilot

**Final classification: `R6_40_COMPARISON_INCONCLUSIVE`.**

GPT-6.1 Sol proposed **3** reusable compositions; **3** were admitted and **0**
rejected. Two identities transfer successfully to the direct-transfer tasks.
No fully accepted combination-transfer witness or adaptive advantage is established.
The primitive-only and expanded-template conditions score6/6, versus4/6 for both
compact libraries. C's measured evaluation speedup is outweighed by discovery time.
Source-offset contract ambiguity, imperfect proxy capacity matching and template
provenance nonequivalence prevent a stronger causal classification.

The owner explicitly authorized **B as an independently frozen AI-designed proxy**
when no human-designed library was supplied. See [authorization](r6_40/AUTHORIZATION.md).
It is not human-authored; advantage beyond human-designed macros is unestablished.

## 1. Preservation and working model route

[Baseline](r6_40/BASELINE.json) verifies R6.39's publication manifest/receipt and
**4,268 protected SHA256 identities**. These include production, the R6.10 VM,
R6.18 wrapper, R6.23 adapter, R6.25 contracts, R6.27 exposure, R6.32 registry/
telemetry and R6.36–R6.39 evidence. Existing untracked R6.39 publication files were
preserved. Kernel **26** is inherited accounting backed by unchanged identities,
not a new independent construct recount. Production/compiler/lowerer/runtime and
all protected experimental semantic machinery remain byte-identical.

[Neutral preflight](r6_40/PREFLIGHT.json) passes on OpenCode **1.18.32**,
**openai/gpt-6.1-sol**, requested **high** variant: one completion,612 input/8 output
tokens, no tool calls. The R6.36 working child route is reused with `OPENCODE_PURE=1`
and default built-in plugins eligible. No credential store or private authentication
header was inspected/exported; effective OAuth authentication and reasoning are
unattested. Frozen per-child configs require no persistent configuration change.

## 2. Prospective freeze and provenance

[Protocol](../../../experiments/adaptive_discovery_r6_40/PROTOCOL.md),
[development freeze](r6_40/DEVELOPMENT-FREEZE.json) and
[task/design freeze](r6_40/TASK-FREEZE.json) precede participant exposure. The
coordinator created new synthetic contracts and requirement-derived expectations;
no previous task solution was copied. Historical findings and narrow arithmetic
skeletons were known to the coordinator. Tasks are capability-tailored, not externally
sourced or cognitively independent; novelty means new exact contracts, not entirely
new underlying computational relations.

The B-proxy pool was computed using only development contracts and froze before
participant discovery/evaluation results. The coordinator already knew planned
evaluation skeletons; pre-file-generation sequencing is not blind control design.
The discovery children receive only their development contract and earlier admitted
development entries. Evaluation manifests and oracle cases are unavailable through
participant tools. Visible sessions/permissions establish limited access controls,
not attested provider/harness hidden-context separation. **All results are exploratory.**

### Development contracts

| Task | Typed parameterized relation | Ordered checks and return |
| --- | --- | --- |
| D1 interval_fee | x,floor,ceiling,fee:Int64 → Int64 | floor<=x, x<=ceiling; x+fee |
| D2 pair_envelope | x,y,floor,cap:Int64 → Int64 | floor<=x, floor<=y, x+y<=cap; x+y |
| D3 echo_charge | x,y,expected,limit,bias:Int64 → Int64 | x==expected, y<=limit; ((x+y)+y)+bias |

Exact codes/sites are in [development manifest](r6_40/DEVELOPMENT-TASKS.json).
The preselected relation contracts constrain discovery to reusable representations
of these relations. This is representation selection/composition, not unrestricted
discovery of a new semantic relation. Earlier admitted entries are available, but
all three admitted definitions use primitive bodies with no symbolic dependencies.

The foundation is unchanged typed Int64/Bool/Unit, ref/const/add/le/eq, ordered
value/check/UInt8 atom/end/compose, and UInt16BE root emission. Limits:32 authored
steps/definition,8-definition closure,64 expanded nodes,depth4, existing VM work100,000.
Per session:360s,24 completions,36 MCP calls,48,000 reported processed-input+output
tokens,12 selftests, at most3 proposals/submissions. Discovery caps3 admitted entries,
24 library steps,16KiB serialized library/documents. Tool/time limits and observed
completion/token supervisor stops are identical across evaluation conditions.

### Six frozen evaluation contracts

All roots read fixed-width UInt8 inputs and check input end **before computation**;
Entry() returns an Int64 and emits UInt16BE. Full requirements are in the
[evaluation manifest](r6_40/EVALUATION-TASKS.json).

| Task | Category | Distinct required behavior |
| --- | --- | --- |
| E1 | Direct transfer | interval checks on derived a+b; bounds31/177, fee14, additional7 |
| E2 | Direct transfer | pair floor17/cap271; additional9 |
| E3 | Novel combination | interval-transform both inputs, then pair-envelope their results |
| E4 | Novel combination | echo-transform x/y, then interval-check/charge the transformed result |
| E5 | Negative transfer | strict interval edges, high-before-low checks, doubled x result |
| E6 | Negative transfer | load-before-key check; x range rather than equality; y counted once |

Expectations froze before artifacts. They are independent of model candidates,
but same-coordinator-authored, not independently human-reviewed. Each two-byte
task has1,186 selected input pairs,4 malformed cases and4 type/work controls:
**1,194 observations**. E5 has256 inputs,3 malformed cases and4 controls: **263**.
Each condition totals **6,233** observations; no complete UInt16 input-space,
general signed64/overflow or universal equivalence claim is made.

## 3. Discovery, admission and immutable vocabulary

Three fresh development sessions produce one proposal each. Admission checks
the exact typed signature, declared frozen relation, representation, dependency
closure, bounded deterministic lowering and candidate-independent development
expectations. A separate probe registry prevents behavior-failed candidates from
entering the reusable vocabulary. Two reload passes each reproduce the finite
512/242/200 observations: **1,908 repeated development checks** altogether.
Contradictory interval bounds challenge error precedence. Finite checks are not
a proof over all Int64 inputs. Model declarations/non-applicability examples are
retained verbatim, with no coordinator semantic repair.

| Admitted composition | Exact immutable identity | Authored steps | Successful full-task transfer |
| --- | --- | ---: | --- |
| interval_fee | `cb2f1d3c16e5e8a960cb08d0d3921773f1739b41c31f2e14efe24c3b4d313b9c` |3 | E1 |
| pair_envelope | `6a1e9b08f0a487c2f9e92a8f9b10efb105e51fc447bf04d06f01eed5ee4058a5` |4 | E2 |
| echo_charge | `330bfb7385b5d3a422f1a26a29fe1f2704c9bd6fbbce6121ab913583fad6b0be` |3 | None |

[Proposals](r6_40/PROPOSALS.json), [empty rejected record](r6_40/REJECTED-ABSTRACTIONS.json),
[C vocabulary](r6_40/C-VOCABULARY.json) and [freeze](r6_40/VOCABULARY-FREEZE.json)
preserve all arguments, semantics, checks and identities before evaluation reveal.
Static learned references total7 across E1–E4: interval4, pair2, echo1.
Only two references occur in fully accepted tasks; partial constituent correctness
does not make E3/E4 successful transfer. The foundation is branch-free and ordered:
all compose regions enter on successful inputs, rather than being unused definitions.

## 4. Conditions and comparator limitations

- **A:** fixed primitive foundation, no reusable library; task-local definitions allowed.
- **B-proxy:** three sealed coordinator-AI-designed macros, drawn by a predetermined
  same-relation/signature/per-entry-step rule from the independently frozen pool.
- **C:** three admitted AI-discovered compositions, exact immutable pins.
- **X:** the C compositions supplied as expanded primitive templates and the same
  C applicability text; no discovered-library pins are preinstalled.

All use the same model/foundation/admission/validation/execution tools. Library
retrieval is read-only; evaluation task-local definitions never enter later tasks.
No extra C implementation hints are given. Order rotates through A/B/C/X,
B/C/X/A, C/X/A/B, X/A/B/C, A/C/B/X, X/B/C/A. There are **24 distinct evaluation
sessions**, plus3 discovery and1 neutral session,28 distinct visible IDs overall.

B matches entry count, all signatures/result types and nesting. It passes the
implemented per-entry one-step tolerance, but **aggregate body capacity does not
match**: B7 steps versus C10, exceeding the one-step/10% total tolerance.
Applicability documents are681 versus2,379 canonical bytes, also unmatched;
exact provider-document tokens are unavailable. The original pool and implemented
`capacity_matched:true` per-entry receipt are preserved; the stricter audit does
not retroactively pad or replace them. This is an additional comparator limitation.

X was executed within budget. Its development hosts establish finite values/checks,
but **not full-envelope equivalence**: flattening primitive steps removes the seq
regions created by compose calls, which changes computed-value source spans in
the unchanged VM. It therefore cannot isolate compact references or prompt length
while holding all provenance semantics equal.

## 5. Functional results, failures, negative transfer and replay

| Condition | First complete construction | First submitted / final accepted tasks | Final observations | Negative tasks |
| --- | ---: | ---: | ---: | ---: |
| A |6/6 |6/6 /6/6 |6,233/6,233 |2/2 |
| B-proxy |4/6 |4/6 /4/6 |6,099/6,233 |2/2 |
| C |4/6 |4/6 /4/6 |6,099/6,233 |2/2 |
| X |6/6 |6/6 /6/6 |6,233/6,233 |2/2 |

All conditions pass both direct-transfer and both negative-transfer tasks. B/C
fail both combination tasks, **46 E3 and88 E4 observations each**. All these
functional failures are source-offset-only; expected values, error codes and
check precedence match. E3's TOTAL_HIGH site offset is2 rather than1; E4's later
RANGE_LOW/HIGH offsets are2 rather than0. VM seq-result spans use their region
start/end, so zero-byte composition after reading two bytes gives a result start2.
This is unchanged inherited behavior, not a newly introduced primitive/runtime defect.

The frozen author wording names derived sites u/v/t without explicitly defining
byte-origin preservation across compose. The oracle assumes originating byte
offsets. This **contract/oracle ambiguity is retained**; the failed scores are not
rescored as successes. A/X's better oracle scores cannot conclusively show an AI
authoring deficit when existing compose spans and underexplicit requirements may
explain the difference. X's source-envelope change compounds the ablation issue.

E3-B first supplies an invalid SHA256 in its Entry candidate; immutable admission
rejects IDENTITY and the model self-corrects. C/E4 submits one self-authored revision,
which retains the source-offset failure. No acceptance feedback is given during
authoring; no coordinator repairs occur. First construction, submitted artifacts,
all selftests and diagnostics remain available. Negative tasks' C artifacts have
no learned dependency: harmful reuse was avoided in these two examples, not proven
absent generally.

E4-B crosses48,000 reported processed-input+output tokens at **50,643**, after its
candidate sealed. The child tree stops at that observed boundary; no retry occurs.
Its nonzero-process `provider_halt` field is a **budget stop, not a provider error**.
The preserved artifact's failed score is descriptive, not within-budget success.

[Provenance](r6_40/PROVENANCE.json) and [supplemental audit](r6_40/SUPPLEMENTAL-AUDIT.json)
verify all **27 model-authored definition pins** after mechanical sealing only,
immutable seeds and registry/telemetry integrity. Two separate model-free reload
passes reproduce all25 sealed submissions, including failures, expanded plans,
maps, values, errors, spans and work: **26,126 observations/pass;52,252 repeated
replay observations**. Replay agreement does not mean functional acceptance passed.

## 6. Tokens, wall time, retrieval and validation overhead

Provider-reported-through-OpenCode usage is reconciled between exports and
step-finish events. [Measurements](r6_40/MEASUREMENTS.json) and
[chronological ledger](r6_40/REQUEST-LEDGER.json) include all observed completions
and MCP exchanges. Cached read tokens are counted, never treated as free.

| Evaluation totals | A | B-proxy | C | X |
| --- | ---: | ---: | ---: | ---: |
| Noncached input |45,337 |57,248 |51,741 |60,395 |
| Cached input/read |58,112 |99,456 |103,552 |86,272 |
| **Processed input** |**103,449** |**156,704** |**155,293** |**146,667** |
| Output |6,596 |6,996 |6,707 |6,979 |
| Reported reasoning |1,126 |903 |582 |682 |
| Model completions |38 |42 |37 |37 |
| MCP calls |61 |68 |64 |69 |
| Retrieval calls |4 |8 |7 |10 |
| Retrieval dispatch seconds |0.032671 |0.060178 |0.074192 |0.097188 |
| Participant wall seconds |295.051 |280.840 |246.831 |260.417 |
| Scored validation/lowering seconds |0.004960 |0.006521 |0.006610 |0.004144 |
| Scored main execution-loop seconds |0.278199 |0.282506 |0.305136 |0.290340 |
| Full acceptance interval seconds |0.290299 |0.295655 |0.318797 |0.301657 |

Cache writes are0 in all reported calls. Reasoning is retained separately rather
than silently added to output. Retrieval payloads total720/20,488/28,020/37,868
serialized result bytes. These are not exact model-token allocations; exact
retrieval tokens are unavailable. Validation/execution MCP intervals and registry
admission/retrieval calls are also recorded in the measurement file. Scored main
execution timing excludes small auxiliary controls; full acceptance includes them.

Discovery costs **15,163 processed input** (13,115 noncached/2,048 cached),**2,183
output**,269 reported reasoning,9 completions,6 MCP calls,3 library retrievals and
**91.780s**. Discovery retrieval costs0.072611s. Mean cost per admitted entry is
5,054.3 processed input/727.7 output/30.593s; exact per-session costs are retained,
including inherited-library retrieval in later discovery. MCP proposal time includes
the two behavior/reload checks; registry admission subintervals overlap it.

Charging the full discovery cost to C gives **170,456 processed input**,8,890 output,
**338.611s** participant/discovery wall, versus A103,449/6,596/295.051s. C evaluation
alone saves48.220s against A, but discovery yields **43.560s more measured wall**
and **69,301 more processed-input+output tokens**. Against B-proxy, C's small1,700
evaluation token reduction becomes15,646 more tokens after discovery; measured wall
also becomes57.771s greater. X is separately charged discovery rather than splitting
it with C:161,830 processed input,9,162 output,352.196s. C's shared discovery cost
cancels in C/X contrasts; X has8,354 fewer evaluation processed-input+output tokens,
while C's evaluation wall is13.586s lower, with different scored correctness.

Participant wall includes initialization/inference/tools, but excludes export and
later offline scoring. Nested MCP/registry/validation intervals must not be added
again. Neutral preflight and measured pool-admission setup remain separately recorded.
**Actual API billing, exact upstream/hidden retry counts, effective reasoning,
coordinator model usage and complete setup/freeze/publication effort are unavailable.**
SDK cost0 is not free billing. Complete economic advantage cannot be inferred.

## 7. Amortization and attribution

[Amortization](r6_40/AMORTIZATION.json) retains per-entry discovery costs, static
reuse4/2/1 and full-task transfer1/1/0. Retrieval is included in observed input and
wall usage, not estimated away. Only E1/E2 provide fully accepted compact-reuse
comparisons against all controls. The [matched-success refinement](r6_40/MATCHED-SUCCESS-AMORTIZATION.json)
shows C's aggregate processed-input+output saving on those two tasks is **negative**:
−1,370 versus A,−8,552 versus B-proxy and−4,775 versus X, before discovery.
E1 individually saves8,657 tokens against A, but E2 costs10,027 more. Session
differences cannot be causally assigned to a macro or treated as stable per-reuse rates.

No measured aggregate break-even reuse count is established. The earlier arithmetic21
versus B in AMORTIZATION.json divides all-task differences, including unsuccessful
combinations/budget overshoot, by two successful references. It is an illustrative
calculation, **not** a measured economic break-even or supported prediction.
No advantage follows from compactness alone or from an extrapolated reuse count.

Separately: valid compositions **yes**; bounded AI-selected reusable representations
**yes**; direct unseen-to-discovery transfer **two witnesses**; full combination
transfer **no under the frozen scores**; benefit over appropriate controls **not
established**; benefit specifically attributable to AI rather than ordinary macro
reuse **unestablished**. No internal language-of-thought or statistical-significance
claim is supported by this small exploratory sample.

## 8. Deliverables, direction and stop

All requested categories are published; the human-control category is explicitly
substituted with the authorized B-proxy and missing-human-control disclosure:

- Report/protocol: this report, round-local PROTOCOL.md,
  [deviations](r6_40/PROTOCOL-DEVIATIONS.md), terminal [result](r6_40/RESULT.json).
- Development/evaluation contracts, candidate-independent expectations and freezes:
  DEVELOPMENT-TASKS.json, DEVELOPMENT-EXPECTATIONS.json, EVALUATION-TASKS.json,
  En-EXPECTATIONS.json, DEVELOPMENT-FREEZE.json and TASK-FREEZE.json.
- Discovery: D1–D3 CONFIG/VISIBLE-DISPATCH/EVENTS/EXPORT/MCP, probe registries,
  PROPOSAL-CHECK records, ADMITTED receipts, PROPOSALS/REJECTED-ABSTRACTIONS.
- Libraries: B-PROXY-POOL/B-POOL-CHECKS, B/C-VOCABULARY, X-TEMPLATES,
  VOCABULARY-FREEZE and CONTROL-LIMITATIONS.
- Every condition: En-A/B/C/X SESSION/registry/telemetry, raw authoring transcripts,
  SUBMISSION, FIRST-CONSTRUCTION-ACCEPTANCE, ACCEPTANCE, REPLAY and closure records.
- Accounting: MEASUREMENTS, REQUEST-LEDGER, AMORTIZATION,
  MATCHED-SUCCESS-AMORTIZATION, PROVENANCE, FAILURES-AND-DIAGNOSTICS,
  CONTROL-QUALIFICATION and SUPPLEMENTAL-AUDIT.
- Versioned [boundary](../../../docs/project-overview-r6.40.md),
  [observations](../../../docs/research-log-r6.40.md) and
  [decision](../../../docs/decisions-r6.40.md).
- [Publication integrity](r6_40/VERIFICATION.json) checks protected/frozen/additive
  hashes, JSON/whitespace, relative links, credential-pattern scan, unchanged tracked
  files and `git diff --check`.

**Recommended direction:** retain the fixed deterministic foundation and immutable
registry, keep discovered compositions optional research artifacts, and avoid a
mandatory adaptive vocabulary layer on this evidence. A separately authorized
successor should explicitly specify byte-origin versus region-span semantics in
requirements and qualify full-envelope-equivalent expanded controls before task
exposure; obtain a real human control or transparently define an AI-selection
comparison, with aggregate capacity/document matching and complete cost metering.
Do not repair the existing runtime or this round's scored artifacts from outcomes.

**Stopped after the bounded pilot, replay, analysis and publication.** No production
or new execution semantics, training, full R6.31 study, P6-A04 acceptance or P6-A05
access occurred. Wait for explicit authorization before further work.
