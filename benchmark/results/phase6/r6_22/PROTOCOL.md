# R6.22 frozen local generation diagnosis

Owner authorizes nonproduction neutral generation diagnosis. Preserve all prior
evidence and production/kernel26/R6.10/R6.18. No symbolic authoring, scored
discovery, remote inference, downloads, installation edits, training, MCP,
P6-A04 acceptance or P6-A05 inspection. Coordinator knows historical outcomes;
synthetic requests are diagnostic, not independent or held-out evidence.

Use existing pinned Qwen3 8B Q4_K_M and Ollama0.35.0 in an experiment-owned
offline loopback server, parallel1/one loaded model. Baseline is R6.21 raw
ChatML closed empty thinking prefix, context8192, output2048, temperature0,
seed621, top_k20, top_p0.95, repeat_penalty1, format=json. Streaming is the
declared transport change; never replay R6.21 symbolic requests.

Freeze seven requests, exact schemas/expected values, configurations, schedule,
runner and protocol before inference. One warmup(cap64), then each request
three times (five at baseline, constrained in schema mode and unconstrained
without format), then repeated-identifiers request three times in each
of seven single-variable variants: temperature0.6, top_p0.8, repeat_penalty1.1,
cap512, schema format, no format, context4096. Maximum43 inference calls,
180s socket timeout per request, 1200s whole run checked before every call.
No outcome-selected tuning/retries. Each declared repetition is an attempt,
including identical-seed repeats; no inference of independent random trials.

Record raw NDJSON chunks with UTC/monotonic receipt timestamps and flush each
chunk, exact request bytes/hash, final error/status, usage when available,
assembled text, post-call loaded context and log byte span. Chunks are not
tokens. Backend /tokenize measures each prompt after warmup; require <=1536
input tokens and input+output+256 <= allocated context. Reject without inference
if unsafe. Require matching reported/logged input where available and no
truncation; missing final usage is missing, never estimated from characters.
Capture GPU memory snapshots before/after; no peak-memory/OOM inference.

A repeat-guard abort is an intended observable diagnostic event: continue the
predeclared matrix only if server remains alive and version endpoint responds.
Other runtime/transport failure, delivery truncation, process exit or whole-run
ceiling halts remaining schedule. Never disable repeat guard or change service
installation. Context variant reduces allocation; no raised resource limits.

Strict JSON rejects duplicate keys and nonfinite constants; validate exact frozen
schema and expected value separately. Completion means done=true with stop (not
length), no error. Budget length is exhaustion even if parseable. Classify each
failure with evidence; repeat-guard plus visible repetition supports repetition
but does not isolate model versus decoder cause. Measure max adjacent equal
receipt chunks and occurrences of symbolic identifier; intended repetition is
not itself pathology. Group by request/config with completion/schema rates,
known usage sums and missing-count denominators, latency and runtime errors.

Stable classification requires all21 initial challenges complete/schema-valid
with intact delivery. If not, decoding gap requires matched format evidence,
model repetition gap requires cross-format repeated runaway evidence; otherwise
runtime failure unresolved. Fatal setup/delivery/protocol failure => protocol
halt. Report limited stable subconfigurations separately, never infer symbolic
authoring readiness from neutral successes. Publish integrity and stop.
