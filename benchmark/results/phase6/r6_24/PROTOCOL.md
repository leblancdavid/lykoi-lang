# R6.24 frozen bounded authoring protocol

Owner authorization: local nonproduction typed-tool construction using existing
Qwen3 8B, unchanged R6.18/R6.10 and R6.23 adapter. Coordinator has seen prior
reports and designs synthetic feature-targeted tasks; no independent replication,
unbiased sampling, unseen generalization or population reliability claim.

Freeze five new tasks and literal functional expectations before model exposure.
Requirements target arithmetic, stored Boolean/equality, ordered failures,
two-call dependency reuse and three-definition nesting. No old scored discovery
task or previous participant candidate is supplied. Host controls stay private.
Every task runs T (native tools), A (complete definition), B (compact packet),
rotating the order T/A/B, A/B/T, B/T/A. Each context is fresh except T's own
conversation. Shared runtime/cache and fixed seed limit causal inference.

T exposes exactly four tools with task-required operation variants. It gets24
model calls and24 tool calls,384 output tokens per call and4096 cumulative output
tokens. A/B each get one4096-token call (same total output allowance), no repairs.
T errors are returned verbatim structured; model may retry within its original
budget. No coordinator edits/argument coercion. Batched calls execute in supplied
order. No tool calls in a normal T response ends that attempt incomplete.
Successful validate_candidate ends T; functional expectations are never feedback.
Record every assistant message, tool call, response and incomplete packet.

All tracks: requested context8192; input preflight tokenizer count of serialized
messages/tools plus1024 template reserve <=6144; actual prompt usage <=6144,
input+output+256<=8192; cumulative input <=60000 per task/track; per-task wall180s;
global wall1200s; <=132 total model calls including two neutral warmup/interface
controls. Tokenizer proxy is not exact native template rendering; post-call runtime
logs and reported usage must agree, show slot8192 and no truncation. A guard failure
is protocol halt, preserved without tuning. Output length stops that task; runtime
abort ends that task; second runtime abort halts the whole experiment. Transport,
identity, template/delivery or harness failures halt immediately. No reload tuning.
Sockets timeout60s; streamed deadline checked per line. These are client/cooperative
bounds, not OS resource containment; no safeguard disabled.

Construction bounds:3 definitions,4 inputs and8 steps/definition for T,24 tool
calls,4096 chars/argument object; primitive expression depth1 in T's schema;
unchanged R6.18 expansion nesting4,64 nodes,64KiB, original VM limits. A/B retain
their frozen adapter schema bounds; this asymmetry is reported, not a matched
grammar experiment. Candidate acceptance requires exact signatures, operations,
symbolic edges, target, and all frozen functional cases. Literal acceptance args
instantiate via frozen HostEntry; wrong primitive argument types reject at wrapper
validation. Preserve full packages, expansions and raw VM envelopes. One execution
per case, no historical acceptance execution. Scripted client qualifies4 positive
inputs, malformed syntax/arguments, unknown refs, missing deps/type mismatch and
valid-but-wrong output before freeze.

Metrics distinguish tool envelope syntax, argument schema, semantic append success,
completed typed construction, structure and functional acceptance; inference usage
missing is null, never zero. Repairs count post-error model attempts, not rejected
tool calls by themselves. Supported requires >=1 fully accepted model program AND
reliable tool interaction across the set: all5 T tasks complete without runtime
abort, >=90% syntax and argument validity and >=4/5 functionally accepted. Otherwise
some accepted T program => PARTIAL; none plus repeated abort => RUNTIME_RELIABILITY_GAP;
none with completed runtime => MODEL_TOOL_USE_GAP. Protocol faults override to
PROTOCOL_HALT. Zero model calls due to a failed interface control cannot support a
model programming verdict. Stop after publication, requiring new authorization.
