# construct-1 — deterministic construction interface

Experimental syntax only over unchanged R6.18/R6.10. Compact JSON is bounded by
the strict R6.18 loader, compact schema and executable adapter checks. No code,
callbacks, unknown operations or task-specific operators. Int64/Bool/Unit preserve
exact frozen types. All expression, template-substitution, seq provenance, failure,
UInt16BE encoding and work meanings remain those of the frozen wrapper and VM.

Packet: `version:"construct-1"`, definitions array, target name. Definition:
name, typed input pairs, ordered ops, result expression and result_type. Scalar
integers/Booleans/null denote const; `$name` denotes a previously declared immutable
value; `[add|le|eq,left,right]` is a binary expression. Call arguments are only
literals/refs. The exact operation tuples are documented in the prompt contract
and compact.schema.json. Explicit dependencies enumerate each referenced local/input
once; missing/extra deps reject. Unit/compose result types are derived from fixed
operation/signature rules, not guessed from task expectations.

Adapter emits s001/s002/... structural step IDs in exact submitted operation order,
resolves aliases without forward references or shadowing, checks expression/call
types, resolves exact dependency lists, computes symbolic dependency pins and
content IDs, then invokes unchanged wrapper validation. Registry cycles reject.
No topological reordering of execution, semantic repair, optimization, inferred
missing computation or hidden task solutions. Definition seal traversal is only
cryptographic dependency ordering, not executable ordering. Seven authored
definitions plus a single generic HostEntry adapter fit the frozen eight limit.

Bounded repeat `{repeat:1..4,body:[operation,...]}` is literal inline unrolling.
Each iteration has a fresh alias scope inheriting outer values; internal aliases
do not escape. Body order and every operation/work charge remain explicit after
unrolling. No carry, runtime loop, recursive repeat or inferred termination.
One..32 expanded steps/region and128/package; wrapper/VM expansion bounds remain.
Repeated alias references outside the scope reject, as do generated-ID collisions.

Track A supplies full R6.18 definitions (all semantic fields, explicit ID/type/deps,
execution order, declared direct dependencies and node objects), omitting the
definition identity and using `AUTO` only for dependency/call cryptographic pins.
Both tracks use the same sealing service; A is not asked to compute SHA256 inside
the model. Any undeclared A call dependency rejects. Header/version/foundation and
HostEntry are supplied identically, not generated as extra model work. Thus this
is complete-definition versus compact-definition authoring, not a comparison of
raw fully signed package generation.

The host instantiates frozen input literals in one generic compose entry, executes
empty byte input and fixed UInt16BE output. Candidate target signature must match
the task; unexpected definitions or semantics are not manually removed. Raw VM
errors and logical work are retained. IDs differ across interfaces, so cross-track
acceptance compares code/offset/value/output/consumption, not ID equality or work
equality. Exact semantic preservation is tested separately with adapter controls
and independent explicit expanded VM twins, including full envelopes and work.
