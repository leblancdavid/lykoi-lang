# R6.24 typed-tool interface 1

`tools.py` publishes Ollama native function schemas and a transactional dispatcher.
`TOOLS.json` freezes the actual task-specific definitions. Only structured JSON
arguments are admitted, with strict closed schemas and exact Int64/Bool/Unit types.

- `declare_input(definition, inputs:[{name,type}])` declares an entire signature.
- `apply_operation(definition, alias, operation, ...)` appends value/check/compose.
  value requires type/expression/dependencies; check requires expression/site/code/
  dependencies; compose requires symbol/arguments/dependencies. Expressions are
  scalar/ref or a single binary add/le/eq tuple; compose args only scalar/ref.
- `define_result(definition,result,result_type)` finalizes a nonempty definition.
- `validate_candidate(target)` requires all declarations finalized, invokes frozen
  construct-1 adapter validation/sealing, R6.18 validation and bounded expansion.

Named definitions cannot be edited after finalization; callees must be finalized
before compose. Unknown refs, wrong types, missing/extra dependencies, aliases and
illegal schemas return structured errors and roll back the attempted mutation.
Tool responses contain `{ok,...}` or `{ok:false,error:{code,path?,detail}}`.
Measured tool wall time includes argument validation and adapter work. Full validation
also retains the frozen adapter's stage timings. No host callbacks, code execution,
implicit dependency repair, reordering, task solution or supplied macro library.

Partial operation validation uses adapter.compact_defs on a private snapshot, with
literal0 temporary result sentinels for unfinished definitions. These sentinels are
never final candidates and cannot complete validate_candidate; all results must be
explicitly authored. This removes repeated packet scaffolding, not semantic choices.
Completion returns a typed artifact but does not establish requirements correctness.
Functional evaluation is separate and never fed back to the model.

Limits are in PROTOCOL.md. Existing semantics/signature pins/IDs and UInt16BE output
remain those of R6.23/R6.18/R6.10. This is a local dispatcher, not an MCP server.
