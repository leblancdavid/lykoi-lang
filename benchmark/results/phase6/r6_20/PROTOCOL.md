# R6.20 — frozen local interface diagnosis

Owner authorizes neutral nonproduction inference and local diagnostics only.
No discovery scoring, downloads, training, MCP infrastructure, production/VM/wrapper
edits, P6-A04 acceptance or P6-A05 access. Stop after bounded publication.

## Preservation and locality

Verify every R6.19 baseline and publication identity (including published guidance),
then add only new files. Use existing Ollama 0.35.0 and qwen3:8b digest
500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41,
Q4_K_M local GGUF a3de86cd1c132c822487ededd47a324c50491393e6565cd14bafa40d0b8e686f.
Dedicated 127.0.0.1:11435 server, cloud disabled, invalid loopback proxies,
one loaded model; existing desktop service untouched. No remote inference endpoints.
Record actual runtime configuration and process/network evidence. This is not an
OS firewall attestation. The OpenCode coordinator designs the neutral harness;
the pinned local model is the only inference participant. Coordinator knows R6.19
outcomes; this is an outcome-informed diagnosis, not independent replication.

Baseline options match R6.19: temperature0, seed619, context8192,
num_predict4096, top_k20, top_p0.95, repeat_penalty1, think=false, stream=false,
keep_alive10m. Explicitly varied output caps and format modes are diagnostic
conditions, not silent baseline changes. Do not change installed software.

## Precommitted schedule and bounds

Prepare and hash all tasks, schemas, prompt templates, library, runner, protocol
and host controls before any inference. No post-result prompt/schema tuning.
Requests are sequential; no concurrent participant inference. Runtime series:
three identical short schema extractions; list lengths16/128/512 with caps
256/1024/4096; two depth6 nested schemas; generic JSON long list; short-output
caps16/64/256 on the same length128 objective; neutral context padding
1024/4096/7168 words (record actual tokens/truncation, not assumed token lengths);
three sequential accumulated neutral extraction turns; two inert tool selections;
final short health extraction. Feature series: eight individual neutral probes
before combined objectives, one call each, generic JSON, cap4096.

Transport timeout180s. Stop all remaining participant work on two HTTP5xx/transport
failures in the round, any runner exit, or one unresponsive post-error health check.
After any runtime error perform only GET version/ps and one frozen short extraction
health request if those GETs succeed; include health calls in costs and stop count.
No restart/retry of the failed objective. Overall inference wall ceiling1200s;
maximum80 participant calls including health. Expected schedule is at most77 calls.
If a ceiling prevents completion mark remaining work NOT_REACHED, never zero.

## Representation and comparison

Individual probes use the unchanged R6.18 validator and VM; host mechanically seals
the omitted program identity and inserts package version/foundation only. Library
content IDs are supplied verbatim; no AUTO resolution or semantic repair. Existing
R6.18 JSON Schema (with program identity omitted for model output) checks shape;
validator/expansion checks exact types, refs, deps, order, symbol pins and bounds.
Frozen negative controls qualify distinct serialization/schema/type/dependency/
semantic/expansion/runtime-objective categories before inference.

Four new closed neutral objectives: typed literal73, immutable reference19 used
twice, ordered FIRST/SECOND failures returning5, and nested identity relay41.
No byte-pair parsing, bounded-add/increment witness, discovery vocabulary or
previous discovery/evaluation task is reused. Names/constants are diagnostic
choices, no claim of exclusion from unknown pretraining. Fixed two-definition
identity library is host-authored, not discovered.

Each A/B objective receives the same full compact semantics, fixed library,
objective, allowed operations, stage formats and constraints. Fresh message arrays.
Schedule N1:A,B; N2:B,A; N3:A,B; N4:B,A. A generates a complete definition;
after rejection it may regenerate within six calls/4096 total generated-token cap.
B builds operation list, header/signatures, dependency map, node map, order,
result in six calls with cap min(1024, remaining4096). The host copies submitted
fields into a definition without inventing steps/order/deps/expressions; full
content identity alone is computed. Selection must agree with node operations.
B validates shape every turn, then validates a provisional complete region after
nodes using submitted signatures/deps, submitted step order, and dummy const0
result (clearly partial); final submitted order/result are validated normally.
Feedback is deterministic validation only, no oracle solution/mismatch detail.
Invalid B stage ends that objective (no automatic guessed fields or repair).
A gets equivalent validation feedback after complete submissions; feedback timing
and granularity, host assembly, six-stage schema decomposition and accumulated
context differ and are intrinsic confounds. No controlled causal superiority claim.
Zero manual repairs; A regeneration counts as repair. B continuations are not
repairs; an invalid stage is terminal. Unused budget is reported, not equalized
through wasteful calls. Compare objective-level completion and final composition
validity separately from per-message JSON/schema rates.

## Measurement and gate

Preserve every request/response body/status, headers restricted to content-type,
timestamps, exact prompt/schema hashes, options, log byte spans, postcall version/ps,
tokens and runtime durations (null when missing), call/validation/assembly/total
wall times and approximately1s sampled GPU/RAM/process memory. Samples are not
peak guarantees; warm load/cache/shared desktop contention are disclosed.
JSON syntax, strict serialization, schema, static/expansion validity and independent
finite objective checks are separate. Valid composition never follows from JSON.
Tool selection is inert and supplies no executable host capability.

The original R6.19 failure is inspected without replaying scored prompts. Its
response body/token counts are missing; do not invent an OOM/capacity explanation.
Readiness requires repeated inference, no unresolved critical failure, structured
handling, at least one valid composition and complete failure/resource accounting.
An unreproduced historical critical500 remains unresolved absent causal evidence;
successful neutral calls alone do not clear it. Runtime gap outranks a favorable
interface trend. Recommend only the smallest separate repair/configuration test;
no further experiment without explicit authorization.
