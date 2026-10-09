# Tool envelope 1

The internal record has version `tool-envelope-1`, provider and model identities,
call_id, optional provider_call_id, function_name, semantic_arguments,
provider_metadata (separate envelope/function objects), and ordering (turn,
position, optional provider_index). Raw provider messages remain in evidence.

Ollama profile: arguments must be objects; id and function.index are optional.
An id is a nonempty string at most256 characters. Index is a nonnegative exact
integer; if any index is supplied, all calls supply indices matching array order.
Invocation order is never inferred by sorting or reordering calls. Missing ids
receive deterministic host:turn:position identities. Supplied identities cannot
repeat across turns within the session. Normalization is batch-atomic.

OpenAI-compatible synthetic profile: id and type=function are required;
arguments are a strict JSON string decoded with duplicate-key and noninteger-number
rejection. Ollama function.index is refused in this profile. This is synthetic
format qualification, not a live-provider certification. Other profiles reject.

Unknown JSON metadata fields are preserved and quarantined. Known structural
fields must have valid shapes. Reserved semantic/context fields at envelope level
reject as ambiguous. Metadata never fills missing arguments or selects a tool.
Tools are authorized explicitly by name before dispatch. Argument objects pass
unchanged through the frozen R6.24 schemas and transactional dispatcher into the
unchanged R6.23 adapter. Additional semantic keys, missing fields, wrong types,
invalid references/dependencies and unauthorized operations retain rejection.
Identity uniqueness and index consistency precede all semantic execution.

Raw JSON parsing rejects duplicate keys throughout the wire document. Finite
provider metadata numbers are retained; semantic argument schemas remain strict.
Size bound
64KiB/call batch; maximum24 calls. Unknown extensions are retained only as inert
JSON. Feedback uses the selected tool_name and matching provider tool_call_id
when supplied. No metadata becomes executable semantics.
