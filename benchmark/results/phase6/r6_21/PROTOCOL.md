# R6.21 frozen bounded qualification

Owner authorizes compact local authoring qualification, not discovery. Additive
files only; preserve production/kernel26, R6.10, R6.18 and all prior evidence.
Coordinator knows R6.19/R6.20 outcomes. Synthetic, feature-tailored neutral tasks,
no independent replication or unseen-generalization claim. No remote participant,
MCP, training, installation, downloads, P6-A04 acceptance or P6-A05 access.

Pin existing Qwen3 8B Q4_K_M weights and Ollama0.35.0. Dedicated offline loopback
server; single sequential caller; context8192, temperature0, seed621, top_k20,
top_p0.95, repeat_penalty1. Explicit raw ChatML serialization with closed empty
thinking prefix; generic JSON format, no tools. This is an intentional prompt
transport correction; R6.20 chat template and duplicated schemas are not reused.
All prompt bytes and full request/response bodies retained. No automatic retries.

Before authoring: load with a short neutral raw generation; discover the owned
backend loopback port from server log and use its /tokenize endpoint to measure
the exact serialized prompt. Verify tokenizer settings against reported input
counts and runner slot context. Conservative safe input bound3584, below R6.20's
observed4098 truncation limit; output reserve2048 and context margin256. Require
runtime n_ctx_slot8192 and /api/ps8192, expected input <=3584 and
input+requested output+256<=8192. Reject oversized requests without generation.
Three neutral sentinel extraction requests (short and two padded requests below
the conservative bound), with exact token-count equality and no logged truncation,
qualify delivery. Token IDs from backend are preserved for every prompt. No output
evaluation before exact reported count and absence of truncation are verified.
Any failed delivery gate stops authoring, any HTTP/transport/runtime error halts
remaining work. Generation hitting cap is retained as incomplete, never repaired.
No prompt/configuration tuning from outcomes. Freeze all task/contracts/harness
before inference. Missing tokenizer or unprovable complete delivery means stop.

Six single-call neutral complete-definition calibrations: operations and typed
literals, typed parameters, local dependencies, ordered checks, nested fixed reuse,
deterministic addition/output. Then four paired new objectives with counterbalanced
A/B order. A one complete definition call, cap2048; B four construction stages,
cap512 each, total2048. Both receive identical semantics/library/objective/formats;
B receives submitted prior fields as data. No feedback-based repair, no manual
repair; invalid stage terminal. Maximum26 authoring calls plus4 delivery calls,
1200s wall and180s per request. Tokenize calls counted separately, not inference.
Differences in caps, assembly and prefix history limit causal comparison.

Use unchanged R6.18 strict load, original definition schema minus host identity,
unchanged validate/expand and unchanged VM execute. Model may submit parameterized
definitions; fixed host adapter passes declared case literals and returns compose
result (identical for both interfaces). Identity sealing is mechanical only.
Separate JSON, strict serialization, schema, static types, semantics/expansion and
finite execution correctness. Downstream checks blocked by first failure are
NOT_REACHED, not false. Require exact parameters, objective structural obligations,
success values/output/consumption or ordered failure code, repeated full envelopes.
Host controls qualify rejection categories before inference; not model success.

Record all calls, input/output/cached tokens, inference and wall/validation/assembly
times, completion/valid-composition counts, failures, zero repairs, utilization and
unused budgets. No inference from text lengths or early-failure efficiency claims.
Readiness requires intact delivery, bounded runtime completions, >=1 model-authored
valid executable composition and preserved accounting. Small sample cannot prove
general reliability; historical500 remains causally unresolved. Recommend only a
separately authorized bounded new discovery pilot if these current gates pass.
Publish and stop. Verify protected/frozen/publication bytes and git diff --check.
