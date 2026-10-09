# Request accounting specification

Supported OpenCode JSON events and session export provide per-assistant-completion
provider/model identifiers, SDK usage, creation/completion timestamps and tool events.
The local wrapper records each CLI dispatch start/end and each MCP request/response
with elapsed time, exact content and serialized content hash. No HTTP interception,
private headers, authentication store, credential values or endpoint override.
Built-in OAuth remains eligible: remove child OPENCODE_DISABLE_DEFAULT_PLUGINS,
retain OPENCODE_PURE=1 using the preserved R6.36 environment helper.

No supported exact upstream serialized-request/tokenizer surface has been established
in this experiment. Completion sequence is an observable proxy, not HTTP attempt count.
Exported messages are locally serialized canonically and content-addressed; schema
delivery to the provider is unknown. Use ceil(character count/4), explicitly estimate.
Provider usage remains authoritative as reported by SDK, not independently billed.
Input/cache/output/reasoning buckets remain separate; processed input adds input and
cache read/write. Signed residual versus local estimate is unattributed, not hidden
tokens. Assistant timestamps are not isolated inference time. Provider billing,
effective reasoning/authentication and internal retries remain null.

Categories: fixed instructions, Lykoi guidance, tool schemas, task requirements,
current symbolic state, historical conversation, tool feedback, retrieval results,
model-generated output, unknown/unattributed. Origins are exclusive per input section;
generated output is counted only once on generation, then historical conversation on
later transmission. Unique hashes deduplicate material separately from repeated input.
Visible section ledgers reconstruct chronology from export, never claim exact boundary
instrumentation. No model behavior changed to obtain measurements. Fully accounted
total development effort and dominant provider-token categories remain unestablished.
