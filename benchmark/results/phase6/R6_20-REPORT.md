# R6.20 — Local model interface diagnosis

**Final classification: `R6_20_PROTOCOL_HALT`.**

The pinned local runtime completed **49/49 requests with HTTP200** in one bounded
session. The R6.19 HTTP500 was not reproduced and its cause remains undetermined.
Neutral schema-constrained outputs, including depth-six JSON and a 2,457-token
list, succeeded. Deliberately insufficient generation caps produced incomplete JSON.

The symbolic portion exposed an **R6.20 harness/prompt-delivery defect**: embedding
the complete definition schema and all six stage schemas repeatedly expanded the
shared instruction to approximately9,900 tokens. Ollama logged input truncation
to4,098 tokens for **all28 feature/comparison calls**, despite num_ctx8192. This
violated the intended compact, intact common-specification boundary. No model
composition was accepted. Neither feature-specific limitations nor an incremental
authoring advantage can be established from these compromised requests. The
frozen attempt is retained without prompt tuning, manual repair or inference rerun.

## Authorization, freeze and preservation

The owner explicitly authorized this neutral nonproduction diagnosis. No symbolic
discovery scoring or adaptive vocabulary construction occurred. The existing
OpenCode coordinator knew R6.19 outcomes and designed this diagnostic harness;
only the pinned local Qwen model participated in inference. This is an
outcome-informed investigation, not independent replication or unbiased task/model
selection. Synthetic tasks are feature-tailored; unknown pretraining exposure is
not excluded.

[Protocol](r6_20/PROTOCOL.md), [tasks](r6_20/TASKS.json),
[schemas](r6_20/SCHEMAS.json), [common interface](r6_20/INTERFACE.txt), fixed
[identity library](r6_20/LIBRARY.json), runner and nine host controls were
[frozen](r6_20/FREEZE.json) before any participant inference. There was no
post-result runner/schema/prompt modification. A separate posthoc publication
script computes accounting from preserved evidence; it makes no inference calls.

[Baseline](r6_20/BASELINE.json) and [verification](r6_20/VERIFICATION.json) check
**883 protected identities**, including the836 inherited R6.19 baseline files,
all45 R6.19 publication files and its manifest/receipt. Production remains at
**26 constructs**. R6.10 VM identity is
`bf5dbfb96d6d50124d109c35804c81e5a27bf4038b7f65b1a909ad4f0cc13fa3`;
R6.18 wrapper identity is
`e5e57901d4df32bcb2eed3b5bbd7ce6f19ee3145bbf71303d96e15b4e3d67fab`.
R6.18 wrapper, production implementation,
R6.3–R6.19 artifacts, failed proposals, empty vocabulary and HTTP500 records remain
byte-identical. No acceptance checks for P6-A04 and no P6-A05 access occurred.

R6.19's publication manifest also pins shared guidance. To preserve all45 identities,
this round makes only additive publications, including separate
[overview](../../../docs/project-overview-r6.20.md),
[research log](../../../docs/research-log-r6.20.md) and
[decision](../../../docs/decisions-r6.20.md) supplements. Historical guidance is
not rewritten. Initial tracked Git state was clean; no tracked file was modified.

## Local configuration inventory

Exact inventory, model template, default parameters and allowlisted environment
are in [INVENTORY.json](r6_20/INVENTORY.json). Effective server configuration and
runner options are in [SERVER.log](r6_20/SERVER.log); all requests preserve options.

| Setting | Observed |
| --- | --- |
| Ollama | Existing0.35.0, unchanged from R6.19 |
| Model | Existing qwen3:8b,8,190,735,360 parameters, GGUF/Q4_K_M |
| Manifest digest | `500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41` |
| Verified GGUF SHA256 | `a3de86cd1c132c822487ededd47a324c50491393e6565cd14bafa40d0b8e686f` |
| GGUF bytes |5,225,374,496 |
| GPU | NVIDIA RTX4070,12,282MiB, driver617.42;37/37 layers offloaded |
| RAM |32GiB installed; OS-visible33,408,004,096 bytes; sampled available5,491,179,520–14,780,010,496 bytes |
| Context | Model metadata40,960; request/runner8192; observed input truncation limit4098 |
| Sampling | temperature0, seed619, top_k20, top_p0.95, repeat_penalty1 |
| Generation | Baseline4096; frozen diagnostic caps16/64/256/1024; comparison total4096/objective/interface |
| Reasoning/transport | think=false; stream=false; keep_alive10m |
| Concurrency | One sequential caller, OLLAMA_NUM_PARALLEL1, runner `-np 1`, max loaded models1, max queue512 |
| Structured output | Explicit JSON Schema for neutral extraction/list/nested tests; generic `format:"json"` for symbolic authoring and cap probes |
| Tool configuration | Qwen existing Go template; two requests with one inert echo function; no tool executed |
| Runtime buffers | CUDA model4,643.78MiB, KV1,152MiB, compute208.02MiB; runner flash attention auto/enabled |
| Host tooling | Existing Python3.14.3 and jsonschema4.26.0; no installation or download |

The model's stored temperature default0.6 is overridden by temperature0 on every
request. Server-level FLASH_ATTENTION=false and runner auto/enabled are recorded
separately rather than equated. Null inherited configuration fields mean unset,
not missing runtime defaults; the effective server log supplies defaults.

[Locality](r6_20/LOCALITY.json) records the dedicated server on127.0.0.1:11435,
verified local model loaded entirely in VRAM (6,295,440,588 reported bytes), and
bundled llama-server with `--offline` and loopback host. Cloud is disabled and remote
proxies point to invalid loopback127.0.0.1:9. Transport allowlists only local
version/tags/show/ps/chat endpoints; no pull, fallback or remote participant provider.
These are configuration/process observations, not continuous OS network isolation.
The desktop Ollama service remained separate. [Cleanup](r6_20/CLEANUP.json) confirms
termination of the experiment-owned parent and descendants only.

## HTTP500 investigation

[Investigation](r6_20/HTTP500-INVESTIGATION.json) binds the historical log, halt and
reconstructed failed request without replaying the scored request. Historical
SERVER.log lines968–986 show:

- runner slot8192 and prompt2771 tokens;
- active generation through230/457/683/908 tokens at about75tokens/s;
- HTTP500 after15.1508252s, with no logged causal error or normal completion;
- immediately preceding requests completed with HTTP200.

The original response body, final failed-call token count, historical peak resources
and backend crash dump are unavailable. The last logged prompt-plus-generation
count is3,679, below8192; later generation is unknown. There is **no evidence that
VRAM exhaustion or model capacity caused this error**. Current2,457-token outputs
and repeated calls completed, but current resources cannot reconstruct historical
peaks or exclude an intermittent failure.

**Most likely cause:** no specific mechanism can responsibly be ranked. The
inference-serving path failed during active generation; backend disconnect/crash,
transport/output handling and memory faults remain unproved hypotheses. R6.20's
documented prompt truncation is a distinct finding; it does **not** explain the
shorter R6.19 failed prompt. The startup log's transient `llm server error` status
preceded successful loading and is not an observed HTTP500.

All49 current HTTP statuses were200. Version and loaded-model GETs remained
responsive after every call. No timeout, repeated-instability stop, server restart
or error-response retry occurred. Full raw bodies and log byte spans are captured
for each new request; there are no new500 bodies because no500 occurred.

## Neutral structured-output results

[Structured results](r6_20/STRUCTURED-RESULTS.json) preserve every condition;
[prompt delivery](r6_20/PROMPT-DELIVERY.json) separately records truncation and
termination reasons.

| Condition | Objective result | Observation |
| --- | --- | --- |
| Identical short schema requests |3/3 pass | Repeatable exact typed JSON |
| Lists16/128/512 with caps256/1024/4096 |3/3 pass | Outputs61/537/2457 tokens |
| Depth-six nested schemas |2/2 pass | Exact repeated nested output |
| Generic JSON list512 |1/1 pass |2457-token output; no nested symbolic semantics |
| List128 caps16/64/256 |0/3 pass | All hit output cap and return incomplete JSON with HTTP200 |
| Padding1024/4096/7168 words |3/3 exact extraction pass | Actual prompt2092/4098/4098; larger two truncated from8236/14380 tokens |
| Accumulated sequential extraction |3/3 pass | Prompt36/84/132 tokens; fresh user turns plus prior replies |
| Inert echo tool selection |2/2 pass | Correct tool name and arguments; no execution |
| Final neutral short health extraction |1/1 pass | Successful before symbolic series; postcall GETs also successful through final comparison |

Runtime-series JSON-valid rate is**16/19** JSON-bearing responses; the three failures
are intentional low-cap conditions. **15/15 schema-constrained runtime requests**
pass schema and exact objective checks. Generic long JSON1/1 passes; tool2/2
is counted separately. Overall21-call runtime objectives pass18/21. Context-padding
success establishes extraction from the retained prompt, not reliable handling of
the full original8,236/14,380-token requests. No actual8192-token intact-input
pressure qualification was achieved.

## Symbolic interface complexity matrix

Eight individual probes preceded combined objectives. Their neutral closed values,
immutable references, two-input dependency, ordered errors, identity relay,
direct pin, Boolean equality and node-budget examples are distinct from the prior
byte-pair discovery/evaluation requirements. Echo/Relay are fixed host-authored
identity templates, never learned abstractions. They contain no bound-add or
increment witness.

| Feature | JSON | Schema | Accepted composition | First observed failure |
| --- | --- | --- | --- | --- |
| Typed values |pass |fail |none |unexpected `definition` envelope |
| Immutable references |pass |fail |none |unexpected `definition` envelope |
| Dependencies |pass |fail |none |unexpected `$defs`/`definition` schema-like object |
| Ordered regions |pass |fail |none |unexpected `definition` envelope |
| Nested compositions |pass |fail |none |unexpected `definition` envelope |
| Symbol identities |pass |fail |none |unexpected `definition` envelope |
| Type compatibility |pass |fail |none |schema-description fields emitted as data |
| Expansion bounds |pass |fail |none |unexpected `definition` envelope |

Exact first diagnostics are in [feature results](r6_20/FEATURE-RESULTS.json) and
[complexity matrix](r6_20/COMPLEXITY-MATRIX.json). All8 outputs are syntactically
and strictly valid JSON, but0/8 match the definition schema. Types, reference
closure, exact dependencies, ordering, pins and expansion are **NOT_REACHED** for
these model outputs. The common failure concerns the representation envelope and
schema-as-data confusion under truncated instruction delivery. It cannot isolate
which of the eight semantic features is intrinsically difficult for the model.
Nothing was unwrapped, resealed into a guessed structure or manually repaired.

[Nine pre-inference host controls](r6_20/HOST-CONTROLS.json) passed: a valid host
definition and syntax, duplicate-key serialization, schema, type, dependency,
identity, expansion-budget and statically valid/out-of-range encode controls.
They demonstrate that JSON, schema, composition and objective validity are separate
and that downstream rejection categories work. They are **host qualification**, not
evidence that the participant authored a valid composition.

## Complete plan versus incremental construction

[Comparison](r6_20/COMPARISON.json) and individual sessions preserve four objectives:
typed literal73, immutable19 used twice, ordered FIRST/SECOND failure, and nested
identity relay41. Order was N1:A/B, N2:B/A, N3:A/B, N4:B/A. Both received the same
submitted rules/library/objective/stage formats. A had up to six calls with
deterministic rejection feedback; B had six construction stages with deterministic
field-copy assembly and partial validation planned after node construction.
Both had a4096-total-generated-token ceiling per objective; B per-turn cap1024.

| Measure | A: complete plan | B: incremental |
| --- | --- | --- |
| Objectives attempted/completed |4 /0 |4 /0 |
| Calls |16 (four/objective) |4 (one/objective) |
| JSON-valid messages |12/16 |4/4 |
| Schema-valid messages |0/16 |0/4 |
| Accepted compositions |0 |0; final assembly NOT_REACHED |
| Model repair attempts |12 |0; invalid first stage terminal |
| Manual repairs |0 |0 |
| Input tokens reported |65,568 |16,392 |
| Cached-input tokens separately reported |45,089 |16 |
| Output tokens |16,384 |666 |
| Call wall seconds |234.681 |13.611 |
| Session total seconds |235.042 |13.694 |
| Validation seconds |0.003605 |0.000505 |
| Assembly seconds |0 |0; B stage1 failed before assembly |
| Unused generated-token ceiling |0 |15,718 |

A emitted a wrapped definition first, then repeated schema-like output; its last
attempts exhausted remaining tokens and produced invalid JSON. Every B first
stage omitted the required `operations` field. **No B objective advanced to input
declarations, dependencies, expression construction, partial validation or completion.**
The incremental construction workflow therefore remains unqualified.

B's100% versus A's75% per-message JSON syntax is not a useful superiority result:
the messages have different obligations and B terminated at stage1. B's lower cost
reflects early failure, not cheaper successful authoring. Neither interface achieved
schema validity or objective completion. Both suffered logged truncation; intact
semantic-information parity is not established by equality of submitted prompts.
The oversized common prompt is an agent-authored protocol defect and must not be
reported as a pure local-model symbolic authoring gap.

The comparison also differs in per-turn caps, feedback granularity, termination,
host assembly and cache history. Counterbalancing four objectives cannot remove
those differences, shared hardware interference, one seed or the prompt-loss
confound. No causal superiority or AI-discovered abstraction benefit is established.

## Token, timing, resource and failure accounting

[Measurements](r6_20/MEASUREMENTS.json) retain reported sums and missing-value
counts; cached tokens remain separate rather than assumed additive billing.

| Group | Calls | Input | Cached input | Output | Call wall(s) | Validation(s) |
| --- | --- | --- | --- | --- | --- | --- |
| Neutral runtime |21 |11,293 |4,610 |6,143 |82.281 |0.003983 |
| Individual features |8 |32,784 |4,084 |4,953 |76.507 |0.001588 |
| A |16 |65,568 |45,089 |16,384 |234.681 |0.003605 |
| B |4 |16,392 |16 |666 |13.611 |0.000505 |
| Total |49 |126,037 |53,799 |28,146 |407.080 |0.009681 |

Run wall time424.663s includes inventory, monitoring, postcall health GETs,
validation and session bookkeeping before cleanup/publication. Per-call inference
latency and server-reported load/prompt/generation durations are separately saved.
Publication elapsed time is in the verification receipt and includes interactive
analysis. Validation timings include schema/static/expansion/finite objective
work if reached; participant symbolic outputs never reached expansion/execution.
Those downstream timings are **NOT_REACHED**, not measured zero. B assembly was
not entered. Billing, energy and historical failed-call token/resource telemetry
are unavailable. All49 current calls report input/output/cached token fields and
runtime duration fields.

[Resources](r6_20/RESOURCES.json) retain416 samples, all with readable GPU and RAM
telemetry. Sampled GPU use was1,333–7,560MiB of12,282MiB; utilization5–100%.
Available RAM fell to5.114GiB and peaked13.765GiB. Ollama parent's sampled working
set was69,926,912–74,473,472 bytes; it excludes the backend. The end-of-run backend
snapshot was8,841,261,056 working-set bytes. Runtime logs show prompt-cache growth;
RAM loss cannot be assigned exclusively to cache on this shared host. Per-call
backend working set, true peaks and continuous connections were not captured.
Approximately1s sampling can miss brief spikes; these observations are not an OOM
exclusion proof or a general reliability claim.

[Failure classifications](r6_20/FAILURE-CLASSIFICATIONS.json):18 passing neutral
responses,7 invalid JSON responses (three low-cap probes/four final A attempts),
and24 schema violations (eight features/twelve A/four B). HTTP/runtime failures0
in R6.20; the historical critical500 remains unresolved. Thirty requests were
input-truncated: two context-padding tests plus all28 symbolic requests. First
diagnostic precedence prevents claiming downstream type/dependency/semantic errors
that were never evaluated.

## Reliability gate and smallest next experiment

[Reliability assessment](r6_20/RELIABILITY.json):

1. **Repeatable inference:** narrow support from49 sequential HTTP200 calls in one
   approximately7-minute run, not general repeatability across sessions/workloads.
2. **No unresolved critical failures:** not established; the original500 has no
   causal diagnosis and was not reproduced.
3. **Structured output:** bounded neutral handling supported; symbolically typed
   output remains unqualified. Input truncation and generation-cap truncation must
   be distinguished from valid request completion.
4. **At least one valid model-authored composition:** not demonstrated. Valid host
   controls do not satisfy this condition.
5. **Accounting:** all new failures/calls/resources are retained; unavailable
   historical body, exact retained prompts and backend peaks are explicitly missing.

**Do not recommend another discovery experiment yet.** The final classification
is protocol halt because the compact/intact symbolic-interface comparison boundary
failed; the unresolved runtime question is an additional gate, not a proven OOM.

**Smallest separately authorized next step:** a compact prompt-budget integrity
qualification. Deduplicate schema definitions, give both interfaces the identical
short semantics and exact library, qualify actual input-token/delivery limits and
reject any truncated comparison request. Freeze fresh neutral objectives and keep
all failed R6.20 artifacts. This recommendation is a prospective prompt/host
configuration experiment, not a change to Lykoi semantics or permission to rerun.

After intact delivery and one valid composition are established, separately
authorize a bounded neutral sequential runtime soak with full error-body capture
and backend process/exit telemetry, followed by a fresh interface comparison.
Longer successful outputs alone do not clear the historical500. No model download,
training, MCP server or software upgrade is presently justified by this evidence.

## Publication and stop

[Publication identities](r6_20/PUBLICATION-IDENTITIES.json) and
[verification](r6_20/VERIFICATION.json) check all protected/frozen/publication
bytes, JSON parsing, new-text whitespace, report links and `git diff --check`.
There are no tracked-file edits; new untracked text also receives whitespace checks.
No inference is replayed during publication verification.
The [first publication check](r6_20/PUBLICATION-FAILURE-1.md) failed because it
checked links to its own receipt before creating it. The separate publisher's
ordering was corrected and all links were checked after creation; the frozen
diagnostic runner and inference evidence were unchanged.

**Stopped after this bounded diagnostic publication. Further work awaits explicit
owner authorization.**
