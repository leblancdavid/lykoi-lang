# R6.22 — Local generation reliability diagnosis

**Final classification: `R6_22_PROTOCOL_HALT`.**

Streaming reproduced **excessive repetitive generation**, but **not R6.21's
HTTP500/token-repeat abort**. All35 submitted inference requests returned HTTP200;
six exhausted their output caps. The frozen diagnostic harness then halted on a
stale tokenizer port after the requested context reduction reloaded Ollama's
backend. Matched repetitive schema/unconstrained tests were not reached, so the
underlying cause of the historical repeat-guard abort remains **undetermined**.

**Another authoring experiment is not yet justified.** Five neutral request types
completed with exact/schema-valid outputs in15/15 declared repeats, but repetitive
requests failed and configuration qualification is incomplete. This limited
success does not establish symbolic-discovery reliability.

## Baseline and preservation

Owner authorized only bounded nonproduction local diagnosis. Coordinator knew
R6.19–R6.21 outcomes and selected synthetic repetition challenges; no independent
replication, unbiased task selection or unseen-generalization claim is made.

[Baseline](r6_22/BASELINE.json) verifies **1,014 protected file identities**:
R6.21's972 inherited identities, its publication files, publication manifest and
verification receipt. Original request, HTTP500 body, logs, halt and all previous
evidence remain byte-identical. R6.21's request SHA256 remains
`13436f1a540d6659c32cc4ba898537a9e4699ac5b90f0375ba07c838e5d43616`.
Its exact body remains `{"error":"prediction aborted, token repeat limit reached"}`.
The baseline embeds the original failure analysis; it does not regenerate the
missing historical output or repeat the historical symbolic request.

Production kernel remains **26 constructs**; compiler/runtime/model, R6.10 VM
and R6.18 wrapper are protected and unchanged. No training, downloads, model
installation changes, remote participant inference, MCP implementation, scored
discovery, P6-A04 acceptance execution or P6-A05 access occurred. Shared guidance
already pinned by history is preserved; new guidance is additive.

## Exact runtime and declared configuration

[Inventory](r6_22/INVENTORY.json), [configuration matrix](r6_22/CONFIGURATIONS.json),
request records and [runtime analysis](r6_22/RUNTIME-ANALYSIS.json) retain settings.

| Setting | Observation / declaration |
| --- | --- |
| Runtime | Existing Ollama **0.35.0**, API version checked |
| Model | Existing **qwen3:8b**, Qwen3,8,190,735,360 parameters, GGUF/Q4_K_M |
| Model digest | `500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41` |
| Verified GGUF SHA256 | `a3de86cd1c132c822487ededd47a324c50491393e6565cd14bafa40d0b8e686f` |
| GGUF bytes | 5,225,374,496 |
| Model context metadata | 40,960; not the allocated request budget |
| Effective baseline context | **8,192**, confirmed by slot logs and post-call `/api/ps` |
| Context variation | **4,096**, confirmed for one generation; two repetitions not reached |
| Sampling baseline | temperature0, seed621, top_k20, top_p0.95, repeat_penalty1 |
| Logged additional defaults | repeat_last_n64; frequency/presence penalties0; min_p0; typical_p1 |
| Generation limits | 2,048 baseline;64 warmup;512 budget variant |
| Structured output | Generic `format:"json"`; schema-object mode and omitted-format controls |
| Serialization | `raw:true`, explicit ChatML, closed empty thinking prefix |
| Capture change from R6.21 | `stream:true` NDJSON instead of nonstreaming response |
| Runtime bound | One caller/one loaded model/parallel1, offline backend/cloud disabled, loopback11435 |
| Input guard | Runtime-tokenized <=1,536; input+requested output+256 <= allocated context |
| Execution ceiling | <=43 inference calls,180s socket timeout,1,200s checked before calls |

No safeguard was disabled. Context allocation was reduced, not raised. The
runtime also automatically changed batch/microbatch1024→512 on reload: the
context condition is therefore not a pure physical one-variable intervention.
The raw thinking prefix was held fixed; no conclusion about alternative thinking
templates is available. Locality is process/configuration evidence, not continuous
OS network isolation. Only the experiment-owned process tree was terminated
([cleanup](r6_22/CLEANUP.json)); no desktop-service termination was requested.

## Frozen requests and capture

[Protocol](r6_22/PROTOCOL.md), [neutral request manifest](r6_22/REQUESTS.json),
configuration matrix and runner were [frozen](r6_22/FREEZE.json) before inference.
Seven requests cover short objects,64-row long output, eight nested child objects,
128 identical zeros,64 identical symbolic identifiers, a constrained object and
an unconstrained-decoding object. These are synthetic formatting/counting requests,
not scored Lykoi requirements.

Initial schedule: three repeats per request, five generic-JSON baseline types,
one schema-mode type and one omitted-format type. Sensitivity uses the same
identifier request, three repeats for each single-variable variant. Repeats use
the same seed in a sequential warmed/cache-sharing process; they are not
independent probabilistic trials. No outcome-informed retry, prompt correction
or repair to the frozen harness occurred.

[Streaming evidence](r6_22/calls/) includes, for every submitted request:

- Exact serialized request and SHA256; runtime prompt token IDs after warmup.
- Incremental raw NDJSON lines, UTC and monotonic receipt timestamps, flushed
  per line; accumulated output reassembled and verified posthoc.
- HTTP status, terminal `done_reason`, final usage/durations, errors when present.
- Per-call runtime excerpt, original log byte span, effective loaded context and
  GPU memory snapshots before/after.

Receipt chunks are not assumed to be individual tokens. Final runtime usage is
the source of token totals. No submitted generation lacks terminal usage here.
The preflight failure has no generation usage because generation was never sent.
All34 post-warmup generations have matching tokenizer/API/log input counts,
matching context, and no logged truncation.

The new server debug log included unrelated executable-search PATH values.
[Privacy filtering](r6_22/PRIVACY.json) removes those values from the new log and
its duplicated excerpt, retaining relevant runtime lines/settings, original
capture hashes and substitution accounting. Requests and streaming output are
untouched. Original byte spans refer to the prefiltered log; published line
numbers remain unchanged. Historical files were not filtered or altered.

## Measurements and configuration effects

[Measurements](r6_22/MEASUREMENTS.json) include per-call repetition indicators,
group totals, output hashes, latency ranges and explicit unexecuted schedule.
Completion requires terminal `stop`, not merely HTTP200 or valid JSON.

| Request / configuration | Submitted | Complete | Schema valid / exact | Output tokens total | Mean call wall(s) |
| --- | ---: | ---: | ---: | ---: | ---: |
| Short / baseline | 3 | 3 | 3 | 45 | 0.195 |
| Long64 rows / baseline | 3 | 3 | 3 | 3,042 | 12.499 |
| Nested / baseline | 3 | 3 | 3 | 75 | 0.313 |
| Repetitive128 zeros / baseline | 3 | 0 | 0 | 6,144 | 25.729 |
| Repeated64 identifiers / baseline | 3 | 3 | 0 | 1,824 | 7.497 |
| Constrained / schema | 3 | 3 | 3 | 51 | 0.224 |
| Unconstrained / omitted format | 3 | 3 | 3 | 33 | 0.151 |
| Identifiers / temperature0.6 | 3 | 3 | 0 | 1,824 | 7.499 |
| Identifiers / top_p0.8 | 3 | 3 | 0 | 1,824 | 7.500 |
| Identifiers / repeat_penalty1.1 | 3 | 3 | 0 | 579 | 2.404 |
| Identifiers / output cap512 | 3 | 0 | 0 | 1,536 | 6.264 |
| Identifiers / context4,096 | 1 | 1 | 0 | 608 | 10.409 |
| Identifiers / schema | 0 | NOT_REACHED | NOT_REACHED | — | — |
| Identifiers / omitted format | 0 | NOT_REACHED | NOT_REACHED | — | — |

**Across34 submitted challenges:**28/34 complete (**82.35%**),28/34 strict JSON
valid,15/34 schema-valid and exact (**44.12%**); schema-valid among completed is
15/28 (**53.57%**). Six output-budget exhaustions, zero generation HTTP/runtime
errors and zero repeat-guard aborts. Initial21 challenges complete18/21 and
schema-valid15/21; the declared stable gate fails before the terminal harness halt.
Warmup is a separate successful15-output-token call, not a challenge success.

All35 inference requests together report **1,741 input tokens**,**1,403 cached
input tokens** (separate field; not added to input) and **17,600 output tokens**.
Challenge-only totals are1,700 input and17,585 output tokens. Total inference
wall223.619049s; challenge per-call range0.140179–25.757462s. Whole bounded
run241.811894s includes load, hashing, tokenization, snapshots and cleanup.
Publication time is not included. Billing, energy and continuous peak memory are
not measured. Token totals are complete for submitted inference, not a hypothetical
completed43-call schedule.

### Visible repetition and sensitivity

- **Zero array:** each output contains1,023 visible zero lexemes rather than the
  requested128, remains incomplete JSON and consumes the full2,048-token cap.
  This is excessive repetition with budget exhaustion, not an observed repeat-guard
  abort. Lexemes in incomplete JSON are not decoded-array counts.
- **Identifiers baseline:** every output decodes to201 entries:200`"sym_alpha"`
  and one`"sym,"`, rather than64 identical entries. It ends normally at608 output
  tokens and fails both item content and length constraints. JSON syntax alone
  does not enforce the intended schema/count.
- **Temperature0.6 / top_p0.8:** runtime logs confirm applied settings; observed
  outputs match baseline byte-for-byte and remain invalid. This does not establish
  general sampling ineffectiveness; top_p was varied at temperature0, and all
  seeds were identical.
- **Repeat penalty1.1:** runtime confirms1.100. Outputs shrink to63 correct
  identifiers/193 tokens and finish normally, still one item short. This is a
  measured configuration-sensitive output change, not a schema-valid repair or
  proven fix for the historical abort. Fixed ordering/cache state limits causality.
- **Cap512:** all three outputs stop at budget with170 visible identifiers and
  incomplete JSON. A smaller cap bounds cost but does not produce valid output.
- **Context4,096:** first output matches baseline's201-entry failure. Reload
  contributes to latency; one observation and automatic batch changes do not
  establish a context effect on repetition.
- **Schema/unconstrained modes:** short distinct requests each pass3/3, but the
  same repetitive request's mode comparisons are not reached. No decoder-versus-
  model causal separation is established.

## Failure classification and runtime log analysis

[Failure classifications](r6_22/FAILURE-CLASSIFICATIONS.json) enumerate all19
unsuccessful generated challenge attempts, distinguishing budget exhaustion from
normal-stop schema/count failures. [Runtime analysis](r6_22/RUNTIME-ANALYSIS.json)
provides relevant log lines without interpreting discovery subprocess exits as
generation crashes.

| Candidate mechanism | Evidence / conclusion |
| --- | --- |
| Model repetition | Excessive repeated content directly observed. Contribution of model behavior is plausible; decoder contribution not isolated. |
| Decoder/structured-output interaction | Generic JSON permits wrong-length output. Matched schema/no-format repetition controls unavailable; causal attribution undetermined. |
| Runtime resource failure | No supported OOM/VRAM-exhaustion attribution. Model fits allocation and37/37 layers offload; point snapshots are not peaks. |
| Output-budget exhaustion | Established for6 calls by `done_reason:length`, exact cap usage and incomplete output. |
| Intermittent unexplained generation failure | None observed in this run; historical abort is not cleared by zero current aborts. |
| Undetermined | Underlying R6.21 repeat-guard trigger remains undetermined because historical generated text is unavailable and abort was not reproduced. |

The **most likely mechanism for the current excessive output** is failure to
terminate/count repetitive content under generic JSON decoding. The sequence is
directly visible, and increasing repeat penalty changes its length, but this is
not a proven model-only causal diagnosis. For **R6.21**, only the immediate
runtime repeat-guard abort is established; neither model capacity nor memory
exhaustion has supporting evidence.

### Established terminal harness defect

Server log line63 starts backend port52283/context8,192. Line1646 requests a
reload; lines1655–1657 explicitly stop the old backend. Line1677 starts
port62254/context4,096. The first context-reduced generation succeeds and returns
HTTP200 with intact delivery. Before the second, frozen `run.py` uses the backend
address discovered once after warmup; `/tokenize` on obsolete52283 refuses the
connection ([halt](r6_22/HALT.json)).

This is a **diagnostic-harness lifecycle failure**, not a model repetition abort,
OOM or unprompted backend crash. No generation request35 was sent; remaining
two context repetitions and six mode comparisons are unexecuted. A planned
preflight was attempted once and is separately recorded, not included as an
inference failure. The original faulty frozen runner and traceback are retained.
The protocol's fatal transport stop rule was followed; no corrected run occurred.

## Reliability assessment and smallest next experiment

Bounded local streaming is operational for the observed five successful request
types (15/15 exact outputs, no aborts), including1,014-token long outputs. It is
**not qualified across the neutral challenge suite**, and it is **not reliable
enough to commission another authoring experiment** on this evidence. Repetitive
counts fail, six outputs exhaust budget, and the configuration matrix is incomplete.
Deterministic same-seed repetitions cannot quantify a population failure probability.

**Smallest recommended next step, requiring separate authorization:** a new
neutral-only freeze that qualifies tokenizer endpoint rediscovery after one
context reload, then tests the same64-identifier request in generic JSON,
exact-count schema and omitted-format modes at fixed context8,192/cap2,048,
three declared repeats each. Preserve this halted run, guards, weights and
all original outputs; do not resume or repair its frozen records. This focused
test would distinguish whether schema constraints contain the observed repetitive
failure and whether unconstrained output shares it. It would still not establish
symbolic-authoring/discovery benefit or commission a scored comparison.

## Publication integrity and stop

[Publication identities](r6_22/PUBLICATION-IDENTITIES.json) and
[verification receipt](r6_22/VERIFICATION.json) verify all1,014 protected identities,
frozen protocol/runner/request/configuration hashes, request serialization hashes,
stream reassembly/timestamp order, recomputed strict/schema validation, JSON,
relative links, new-text whitespace and `git diff --check`. No production tests
or historical acceptance runs were needed or executed for additive diagnostic files.
The [first publication verification failure](r6_22/PUBLICATION-FAILURE-1.md) was
an output-link ordering defect in the posthoc publisher; correction affected no
frozen experimental code or inference evidence.

Additive guidance: [overview](../../../docs/project-overview-r6.22.md),
[research log](../../../docs/research-log-r6.22.md),
[decision](../../../docs/decisions-r6.22.md).

**Stopped after R6.22 publication. Await explicit owner authorization.**
