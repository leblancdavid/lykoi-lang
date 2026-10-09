# R6.19 bounded local discovery protocol

Owner authorization: the R6.19 request in this session permits local nonproduction
discovery through unchanged R6.18. No training, downloads, production/VM/wrapper
changes, P6-A04 acceptance or P6-A05 access. Stop after publication.

## Selection and locality

Select existing qwen3:8b, Q4_K_M, on hardware fit and advertised chat/tools support,
before symbolic outcomes. Pin full model digest, local GGUF SHA256, template and
runtime. Dedicated loopback Ollama server, OLLAMA_NO_CLOUD=1, invalid loopback
HTTP/HTTPS proxies, no pull endpoints or remote transport. Record process evidence.
No claim of OS firewall isolation: the runtime's offline setting and pinned local
weights are the inference boundary. Coordinator uses OpenCode to design the harness;
its model is not a participant and authors no candidate repairs.

Fixed inference: think=false, temperature=0, seed=619, num_ctx=8192,
num_predict=4096, top_k=20, top_p=0.95, repeat_penalty=1, stream=false.
Three neutral exact JSON extraction tests and one inert echo tool selection test.
No selection by symbolic score and no post-score configuration tuning.

## Tasks, discovery and evaluation

Freeze three development requirements and four evaluation requirements and finite
acceptance cases before participant exposure. Tasks are coordinator-authored,
capability-tailored synthetic tasks: selection bias is explicit. Evaluation tasks
are unseen to the local participant, not independently sourced or contamination-free.
Read two UInt8 values, compose bounded sums, predicate values, ordered checks and
fixed UInt16BE output. Ordered first failure codes and exact consumption/output are
scored; wrapper-specific provenance is checked for repeatability, not normalized.

Each development session can submit a program and up to two reusable definitions.
At most three calls/session (first + two repairs); previously accepted definitions
are visible in subsequent development. Deterministic sealing fills identity fields
and pins by name; it does not change semantic bodies, deps, order, types or results.
Store raw responses, mechanically sealed proposals and every feedback record.
Admit definitions only with a valid expanded package and passing development suite,
at most six total, names immutable. No manual repair. Freeze every admitted definition
and every failed attempt. No vocabulary selection based on evaluation.

Tracks B (empty registry) and C (frozen discovered registry) each solve four identical
requirements with three calls, 4096 output tokens/call, same validator feedback.
Fresh message arrays per task/track, B never sees C vocabulary. Alternate B/C first
by task; B task order E1,E2,E3,E4; C E2,E1,E4,E3. All frozen definitions retrieved
as one serialized library; retrieval time and token cost counted. Evaluation may
not add/modify definitions or call unknown dependencies. Behavior failures return
only structured counts/first mismatch; acceptance suite is never in author prompts.

## Measurements and decision

First-attempt validity, accepted tasks, mismatches, invalid proposals, repairs,
static call reuse (including transitive), deterministic expansion and full VM
envelope repeats, every work cutoff for one successful input per accepted program.
Unsupported requirements are separate from authoring failures. Input/output tokens
come only from Ollama telemetry. Separate validation, expansion, execution and local
call wall times; charge all discovery calls to C for net comparison. Report vocabulary
bytes and retrieval overhead. Total round wall time includes inventory/publication;
discovery interval is separately recorded. No billing or energy estimate.

Supported requires discovery, reuse and bounded correctness or fully costed benefit;
valid JSON alone is insufficient. Partial permits discovery/reuse without demonstrated
net benefit. Capability gap means the pinned participant cannot complete the bounded
procedure; environment-not-ready means no usable local runtime; protocol halt means
the required experiment boundary fails. Small N, single seed, no capacity-matched
macro control, no independent task curation, unknown pretraining exposure and
nonisolated hardware prevent general reasoning or internal-language claims.
