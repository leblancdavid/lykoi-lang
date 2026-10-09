# R6.23 — Deterministic symbolic construction interface

**Final classification: `R6_23_RUNTIME_RELIABILITY_GAP`.**

Experiment-local endpoint rediscovery **passed a live8,192→4,096→8,192 reload
qualification**. The compact construction adapter passed finite mechanical
preservation/rejection controls without changing execution semantics.

The model comparison did **not** demonstrate a functional or structural advantage:
**all seven completed candidates failed schema validation**. Track A's eighth
authoring request, nested composition, then aborted on the token-repeat guard.
Streaming captured101 consecutive newline chunks before the error. The frozen
runtime-failure stop rule ended the comparison; reuse/failure objectives were
not reached. No participant candidate reached expansion or functional execution.

For the **three completed pairs only**, compact output used344 versus602 tokens
and5.240737 versus8.330293s inference wall time, with45 more input tokens. These
are savings on invalid outputs, not an authoring-efficiency or reasoning benefit.
Production adoption or another scored discovery attempt is not recommended.

## 1. Authorization, baseline and exact local identity

The owner authorized this bounded nonproduction comparison and endpoint correction.
Coordinator knew R6.18–R6.22 outcomes and selected six synthetic feature-targeted
tasks. Only the existing local Qwen model authored participant candidates. This is
not independent replication, unbiased task selection or unseen generalization.
Initial Git status contained only the previously published additive R6.22 files;
those files were preserved.

[Baseline](r6_23/BASELINE.json) was recorded **before adapter implementation**:
**1,145 protected identities**, including R6.18–R6.22 publication manifests,
receipts and dedicated artifacts, production and prior history. Seven R6.18
shared-guidance hashes differ from current files because they were superseded
before R6.19. Each has a matching later protected identity; both historical
manifest bytes and current guidance bytes remain preserved. This is explicitly
recorded supersession, not a claim that every historical guidance hash equals
the current workspace. The two preparatory verification observations are retained
in [baseline attempt record](r6_23/BASELINE-ATTEMPT-1.md).

Production kernel remains **26 constructs**, checked against the preserved ledger.
R6.10 VM SHA256 remains
`bf5dbfb96d6d50124d109c35804c81e5a27bf4038b7f65b1a909ad4f0cc13fa3`;
R6.18 wrapper remains
`e5e57901d4df32bcb2eed3b5bbd7ce6f19ee3145bbf71303d96e15b4e3d67fab`.
R6.22's original stale-tokenizer halt and faulty frozen runner are byte-identical.
No production/compiler/runtime/VM/wrapper/schema changes, new execution meanings,
training, remote participant provider, downloads, full MCP server, P6-A04 acceptance
execution or P6-A05 access occurred.

[Inventory](r6_23/INVENTORY.json) and every raw request retain configuration:

| Setting | Recorded value |
| --- | --- |
| Ollama | Existing **0.35.0**, CLI/API checked |
| Model | Existing **qwen3:8b**, Qwen3,8,190,735,360 parameters, GGUF/Q4_K_M |
| Manifest digest | `500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41` |
| Verified GGUF SHA256 | `a3de86cd1c132c822487ededd47a324c50491393e6565cd14bafa40d0b8e686f` |
| GGUF size | 5,225,374,496 bytes |
| Metadata context | 40,960; not the effective budget |
| Effective authoring context | **8,192**, slot logs/loaded model/verified backend process |
| Output budget | **2,048 per track/candidate**;64 for each endpoint control |
| Sampling | temperature0, seed623, top_k20, top_p0.95, repeat_penalty1 |
| Format/transport | Both generic `format:"json"`, `raw:true`, streaming NDJSON, explicit ChatML/closed empty thinking prefix |
| Locality | Dedicated loopback11435, owned offline backend, cloud disabled, parallel1/one model |
| Input guard | Runtime-tokenized<=3,584; input+cap+256<=allocated context |
| Ceilings | <=15 model calls,180s socket timeout,1,200s checked before each call |

Live effective context was measured after qualification loads, not falsely claimed
as a pre-implementation loaded state. All evaluated authoring prompts are669–725
tokens, well below the guard. Failed T4/A preflight/log input is710, with slot8,192
and no truncation, but its final usage is unavailable.

## 2. Endpoint handling repaired and qualified

[Endpoint implementation](r6_23/endpoint.py) never treats a previously discovered
port as authoritative. For each pre/post token accounting operation it:

1. Rediscovers the latest experiment-owned backend startup endpoint from current log.
2. Verifies the active loopback listener's owner, process name, owned-server parent,
   pinned model path, requested context and `--offline` command.
3. Requires exactly one loaded model with matching digest/context.
4. Requires backend health, checks model identity in backend props, then rechecks
   listener ownership before tokenization. Any mismatch fails closed.

[Live qualification](r6_23/ENDPOINT-VERIFICATION.json) completed three neutral
requests with input32/output11 each, exact token/log matches and these endpoints:

| Requested effective context | Verified active backend |
| --- | --- |
| 8,192 | 127.0.0.1:60865 |
| 4,096 | 127.0.0.1:50953 |
| 8,192 restored | 127.0.0.1:52948 |

The old endpoint is valid for pre-reload accounting against the same pinned model;
after each reload, post-accounting uses the freshly verified replacement and
retokenizes the exact prompt. Three distinct ports/PIDs are recorded in
[endpoint evidence](r6_23/ENDPOINTS.json). All seven completed authoring requests
have intact verified delivery; the aborted request has verified preflight but no
postflight because inference halted immediately.

Six [posthoc synthetic negative controls](r6_23/ENDPOINT-NEGATIVE-CONTROLS.json)
reject missing startup, unavailable/stale listener, wrong parent, wrong process
model, wrong loaded digest and wrong context before any backend HTTP/token request.
These are mocked fail-closed branch tests, not six live negative-control runs.
The live positive reload observations are separate. This fixes the observed R6.22
lifecycle defect in the experiment; it is not continuous OS isolation or a general
race-free endpoint authentication proof. No Ollama installation change occurred.

## 3. Versioned compact construction and exact semantic boundary

Deliverables: [compact schema](r6_23/compact.schema.json),
[deterministic adapter](r6_23/adapter.py), [semantics](r6_23/SEMANTICS-1.md),
[complete-track schema](r6_23/complete.schema.json),
[shared/track prompt contract](r6_23/CONTRACT.txt).

**construct-1** packets declare named definitions, typed inputs, ordered operation
tuples, immutable references, explicit dependency aliases and results. Integers,
Booleans/null are constants; `$alias` is a prior reference; binary tuples select
only existing add/le/eq. value/check/compose/atom/end map directly to the frozen
subset. Compose uses only literal/ref arguments and model-authored named definitions.

The adapter validates strict JSON/schema, resolves types/earlier references, emits
s001/s002 structural IDs, verifies exact data dependencies, checks symbolic cycles,
computes pins/content identities, constructs the full representation and invokes
unchanged R6.18 validation/expansion and R6.10 execution. Structured first diagnostics
are retained. Submitted execution order is never sorted or optimized. It does not
infer a missing semantic decision or substitute a task solution.

Optional literal repeat1..4 unrolls an explicitly supplied operation body in order,
with fresh private aliases per iteration. Outer values are visible; inner values
cannot escape/carry between iterations. This is bounded representation assembly
into existing operations, not a runtime loop. Unsupported/nested repeat, ambiguous
references, wrong types, excess/missing deps, callbacks and bound overflow reject.
Existing seq provenance, template expression substitution, absorbing failure,
UInt16BE encoding and logical work remain unchanged.

### Fairness of the complete track

A generates **all semantic fields of complete R6.18 definitions**, including
types/step IDs/deps/node objects/order/direct dependency declarations. Definition
identity is omitted and `AUTO` stands only for dependency/call hash fields. B uses
compact tuples/implicit submitted order and deterministic structural generation.
Both tracks share identical mechanical cryptographic sealing and one generic
closed HostEntry instantiation with acceptance literals. Neither is required to
compute SHA256 through text generation. Therefore this is complete-definition
versus compact-definition construction, not raw fully signed-package generation.

No task solution, fixed library, accepted previous candidate or host-control fixture
was supplied to either track. All nested/reusable definitions must be authored by
the model. Shared semantic-contract and requirement hashes are retained with
[exact prompts](r6_23/PROMPTS.json). B's format contract actually adds15 input
tokens per completed pair; reduced output does not mean smaller input instructions.

### Adapter qualification, distinct from model success

[Frozen host controls](r6_23/HOST-CONTROLS.json): **21 controls pass**: four positive
controls and17 rejection controls. An independently authored complete structural
twin matches compact assembly. A separately handwritten native expanded VM tree
matches the expanded compact fixture exactly, including region/step IDs, template
substitution and repeated checks. Across five inputs and work cutoffs there are
**85 full-envelope differential observations**, with equal work/error/provenance.
Additional positive controls cover authored nested registry, valid-but-wrong output
and unchanged byte read/end. These finite controls are not universal equivalence
or participant reasoning evidence.

[Host expansions](r6_23/HOST-EXPANSIONS.json) publish packages/plans/maps/envelopes
and posthoc overhead for the frozen mechanical fixture. One compact host construction
took0.000177s; wrapper validation0.000186s; schema checking0.001325s. These single
host observations do not estimate participant construction efficiency. No model
candidate reached construction, so its downstream overhead cannot be measured.

Pre-freeze control import selected the historical short-name module accidentally;
the [retained preparation failure](r6_23/PREPARATION-FAILURE.json) and
[correction note](r6_23/PREPARATION-NOTE.md) document exact-path module loading.
The correction preceded freeze/inference; R6.18 was untouched.

## 4. Frozen neutral comparison and functional results

[Protocol](r6_23/PROTOCOL.md), adapter/schema/contracts, runner/endpoint handling,
controls, tasks/cases and prompts were [frozen](r6_23/FREEZE.json) before model
exposure. [Task manifest](r6_23/TASKS.json) defines six new non-scored objectives:

| Objective | Required semantics | Frozen cases per track |
| --- | --- | ---: |
| T1 Shift | Two typed additions with intermediate value | 4 |
| T2 Threshold | Stored Boolean predicate then check | 4 |
| T3 Ordered | ALPHA check then two OMEGA checks; failure precedence | 4 |
| T4 Lift/Bridge/Outer | Three model-authored definitions, nested calls | 4 |
| T5 Offset/Reuse | Same reusable definition called twice, then sum | 4 |
| T6 Guarded | Ordered guard, native overflow and encode failure | 5 |

The tasks do not reuse R6.19 scored targets or R6.21 calibration outputs. The
requirements explicitly state structural obligations; finite behavior alone cannot
substitute inlining for requested reuse. A/B execution order alternates by task;
each track gets one call/candidate, identical2,048-token cap and zero repair
opportunities. No cross-track response, feedback or acceptance cases enter prompts.
One continuing local process/cache means ordering/cache effects remain, despite
separate raw prompts without conversation history.

[Raw streams/requests](r6_23/calls/), [candidate evaluations](r6_23/candidates/),
[acceptance records](r6_23/ACCEPTANCE.json) and
[explicit functional-stage results](r6_23/FUNCTIONAL-RESULTS.json) preserve every
submitted attempt and unreached stage:

| Task | A complete representation | B compact construction |
| --- | --- | --- |
| T1 | JSON/strict pass; schema reject: type `value` instead of Int64/Bool/Unit | JSON/strict pass; schema reject: dependencies submitted as string |
| T2 | JSON/strict pass; schema reject: type `value` | JSON/strict pass; malformed value tuple/operands |
| T3 | JSON/strict pass; schema reject: type `check` | JSON/strict pass; invented literal expression tuples/code form |
| T4 | Runtime repeat-guard abort; candidate not evaluated | JSON/strict pass; malformed value tuple/dependencies |
| T5 | NOT_REACHED | NOT_REACHED |
| T6 | NOT_REACHED | NOT_REACHED |

Totals: **eight authoring requests submitted**, seven normal-stop outputs evaluated;
A3/3 returned JSON valid/strict, **0/3 schema valid**; B4/4 returned JSON valid/strict,
**0/4 schema valid**. First-attempt accepted objectives are0/4 attempted A and0/4
attempted B; this reflects rejection/abort, not executing and failing all cases.
**Type/dependency validation, expansion and functional execution are NOT_REACHED
for every participant candidate; zero acceptance observations executed.** Four
scheduled requests (T5/T6 both tracks) remain unsubmitted. There are no manual repairs.

[Participant representation inventory](r6_23/MODEL-REPRESENTATIONS.json) explicitly
contains no expanded participant plans. The published host expansions are labeled
host-authored; they are never substituted for model success. Expanded participant
plan size, node count and logical VM work are **NOT_REACHED**, not invented zeros.

## 5. Actual token/time accounting

[Measurements](r6_23/MEASUREMENTS.json) separate runtime/model wall time,
tokenization/endpoint verification, construction/schema/validation and unreachable
execution stages. Tokens come from actual local API/tokenizer evidence, not text length.

### Completed comparable pairs T1–T3

| Measurement | A | B | B minus A |
| --- | ---: | ---: | ---: |
| Calls | 3 | 3 | 0 |
| Input tokens | 2,040 | 2,085 | +45 |
| Output tokens | 602 | 344 | −258 |
| Input+output tokens | 2,642 | 2,429 | −213 |
| Model-call wall(s) | 8.330293 | 5.240737 | −3.089556 |
| Prompt-eval runtime(s) | 0.853388 | 0.862953 | +0.009565 |
| Generation runtime(s) | 7.341456 | 4.275787 | −3.065669 |
| Schema-valid / functionally accepted | 0 / 0 | 0 / 0 | No gain |

B emits **42.86% fewer output tokens** and213 fewer total input+output tokens
(8.06%) for these invalid pairs. It also has lower observed call wall time. Different
prefix-cache histories, fixed order and one seed prevent treating these timings as
a randomized causal efficiency estimate. Nothing measures effort per working program.

### All observed authoring and diagnostic costs

| Measurement | A authoring | B authoring |
| --- | ---: | ---: |
| Submitted calls | 4 | 4 |
| Returned/evaluated | 3 | 4 |
| Known input tokens | 2,040* | 2,810 |
| Known cached input (separate field) | 1,241* | 2,226 |
| Known output tokens | 602* | 507 |
| Inference wall(s), including abort | 10.816022 | 7.439915 |
| Serialization(s), returned outputs | 0.000292 | 0.000261 |
| Schema checking(s), including rejection | 0.001389 | 0.003262 |
| Deterministic construction / wrapper / expansion / execution | NOT_REACHED | NOT_REACHED |

\*T4/A has no terminal API usage/runtime durations. Preflight/log710 input tokens
are recorded separately and **not** substituted for unavailable final input usage.
Its170 response chunks are not converted to output-token expenditure.

Three endpoint controls plus eight authoring calls give **11 actual inference calls**.
Ten completed responses report known sums **4,946 input**, **3,467 cached input**
and **1,142 output tokens**. These are incomplete whole-run expenditure because
T4/A usage is missing. Cached input is never added again to reported input.
Inference call wall26.713545s includes the failed call2.485729s. Fresh endpoint
verification takes46.387115s across20 checks; recorded tokenizer calls0.246167s.
Whole bounded run83.123430s includes startup, hashing, controls, accounting overhead
and cleanup. Endpoint checks are deliberately costly diagnostic process verification,
not an inherent compact-interface cost. Publication checks have separate provenance
and issue no inference/tokenizer calls. Billing, energy and resource peaks unmeasured.

## 6. Runtime abort and repetition evidence

[Failure analysis](r6_23/FAILURE-ANALYSIS.json) binds T4/A request
`d9805f25b9d943554cc9fbc853d5f6b69baf449620df11776cfee7dfa200ad4a`
to raw streaming/error/log evidence. It began emitting a malformed full definition,
then emitted **101 identical adjacent newline response chunks**. The final NDJSON
body is `{"error":"prediction aborted, token repeat limit reached"}`.

The established streaming HTTP response is **200**, followed by the runtime error
event. This reproduces the **same repeat-guard error mechanism** as R6.21, not its
nonstreaming HTTP500 transport status. It does not reconstruct or establish the
precise generated-content cause of the historical request. Runtime log line1133
names the abort; line1139 releases the slot with `truncated=0`. Input preflight/log
agree at710; slot8,192; no output cap reached among completed calls.

Observed whitespace repetition directly precedes the current guard abort. Whether
the underlying model distribution or generic-JSON decoder interaction causes it
is not isolated; no matched alternate-decoder rerun was authorized within this
freeze. There is no supporting OOM/VRAM exhaustion evidence. No endpoint failure,
model restart, guard disabling, prompt tuning, candidate repair or additional
inference followed the abort. Only experiment-owned processes were
[cleaned up](r6_23/CLEANUP.json).

[Repetition indicators](r6_23/REPETITION.json) count receipt chunks/characters,
explicitly separate from token usage. Other calls completing without this abort
does not prove compact syntax suppresses repetition: T4/B itself is schema-invalid,
only one nested pair was attempted, and later pairs were never run.

## 7. Architectural analysis and recommendation

| Question | Supported observation / limitation |
| --- | --- |
| Reduces repetitive output? | Shorter B outputs in three completed pairs; no established prevention of repetitive runtime aborts. |
| Improves structural validity? | No: A0/3 and B0/4 returned candidates meet their schemas. Compact fields still misauthored. |
| Improves functional correctness? | Not demonstrated: no participant reaches functional execution. |
| Reduces total model effort? |213 fewer input+output tokens on matched invalid pairs, not cost per successful software artifact. Missing aborted usage prevents whole-run total comparison. |
| Preserves semantic meaning? |Finite adapter controls match independent full/native twins and exact envelopes/work. No universal claim or participant preservation observation. |
| Hidden complexity? |Schema/alias scopes/repeat unrolling/pin resolution/IDs/signature checks add adapter code and diagnostics. Validation cannot infer missing semantic decisions. Endpoint verification overhead is separate. |
| Improves reuse? |Host controls demonstrate assembly of nested definitions. Model-authored reuse fails/unreached; no demonstrated benefit. |

Deterministic assembly can mechanically remove repeated type/hash/ID/order fields
from author output; that design fact is **not improved AI reasoning**. Here the
model misused both supplied grammars before assembly could help. One-shot compact
tuples are not an interactive construction tool, and this experiment makes no
claim about a full MCP interface or multi-step reasoning. The complete track also
receives shared sealing, so hash computation is not an unfair A burden.

**Recommendation:** retain construct-1 as an isolated qualified mechanical prototype,
not a production architecture or demonstrated superior authoring interface. Maintain
the runtime reliability gate and preserve this first halted comparison. Do not
restart discovery or repair/re-evaluate these frozen candidates.

**Smallest separately authorizable next step:** neutral schema-fidelity and repeat-
guard qualification using small unrelated instructions in both formats, with a
predeclared generic-JSON versus exact-schema decoder control and identical repair
opportunities (prefer zero). Check whether the local model can reliably emit one
valid operation and referenced definition before another paired authoring study.
This report commissions no successor execution or semantic change.

## 8. Publication integrity and stop

[Publication identities](r6_23/PUBLICATION-IDENTITIES.json) and
[verification receipt](r6_23/VERIFICATION.json) verify1,145 protected identities,
frozen files, exact request hashes, raw stream reassembly/timestamp order,
recomputed participant rejections and deterministic controls, endpoint evidence,
JSON, relative links, new-text whitespace and `git diff --check`. No production
or historical acceptance execution was required for additive diagnostic artifacts.
New runtime PATH values unrelated to diagnosis were
[filtered with provenance](r6_23/PRIVACY.json); raw model bytes and historical files
are untouched, published log lines retain numbering, byte spans denote original
capture offsets. The [first posthoc accounting failure](r6_23/PUBLICATION-FAILURE-1.md)
was a null-preflight handling error; its correction changed no frozen inference code.

Additive guidance: [overview](../../../docs/project-overview-r6.23.md),
[research log](../../../docs/research-log-r6.23.md),
[decision](../../../docs/decisions-r6.23.md).

**Stopped after R6.23 publication. Await explicit owner authorization.**
