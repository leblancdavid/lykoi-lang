The R5.110 proposed kernel is exactly **23**: K01 record schema; K02 field;
K03 finite sequence; K04 typed binding (`var`); K05 literal; K06 same-type
equality; K07 conjunction; K08 complement; K09 membership; K10 selection;
K11 trim; K12 finite pointwise map; K13 stable-first uniqueness; K14 transition;
K15 instant; K16 strict ordering; K17 operation contract; K18 cardinality;
K19 input presence; K20 typed resource/capability authority; K21 durable state;
K22 atomic commit; K23 finite nonempty-path reachability.


## Types, domain and serialization

Select `computation_profile: typed-computation-1` with the normal mutable/reference
profile, and atomic-state profile when coupled creation is needed. Compatibility
v0.3 serialization and canonical model are not extended.

* Integer: `{type:integer,domain:[]}`, exactly mathematical integers in
  **[-9223372036854775808, 9223372036854775807]**. Negative values are admitted.
  JSON integer numbers, not strings, floats, booleans, null or implicit coercions.
  CLI parameters declare `encoding:json`; integral-valued floats are rejected.
  Addition is mathematical sum, followed by domain check; no wrap/saturation.
* Duration: `{type:duration,domain:[],unit:seconds}`. Signed-64 integral fixed elapsed
  seconds serialized as JSON integer numbers. The type/unit supplies dimension;
  timestamp plus plain integer is rejected. No duration addition is admitted.
* Displacement input: Gregorian UTC instant, year 0001..9999, canonical
  `YYYY-MM-DDTHH:MM:SS[.fraction]Z`, 1..6 decimal fractional digits. Valid dates,
  hours 00..23, minutes/seconds 00..59. No leap seconds. Result uses UTC `Z`,
  fractional microseconds as six digits when nonzero; otherwise no fraction.
  Reject out-of-range result rather than clamp or host overflow exposure.

Integer fields/literals/runtime parameters, equality/order, typed ordinary related
record creation, persistence and reload traverse the normal pipeline. The inherited
scalar primary-schema introduction remains string/enum/boolean-oriented: this round
does not add integer fields to legacy primary creation/migration serialization.
Related entity initial rows are explicit typed authority; append-only history may
initialize empty using the existing migration profile. There is no numeric reset
or implicit migration default.

## Bounded value graph

Reference write operations and atomic coupled-creation operations may declare
`computations: {nodes:[...],policy:{integer_domain:signed_64,overflow:reject,
snapshot:operation_before,rejection:unchanged}}`. At most 16 nodes per graph.
Each node has exactly `binding, operator, type, operands, depends_on, error`.

Admitted operators:

| Operator | Operands | Result | Meaning |
| --- | --- | --- | --- |
| `value` | one integer source | integer | Explicit local binding, including cardinality |
| `add` | two integers | integer | Checked mathematical sum |
| `shift_utc_seconds` | timestamp, typed duration in seconds | timestamp | Fixed elapsed-second displacement |

Operands are closed typed literal, parameter, before/after field, declared resource,
computed binding or cardinality nodes. Literal has `value`; named sources have
`name`; cardinality has explicit `selection:{entity,binding,predicate}`. Selection
is over one declared finite existing entity collection, with a fresh row alias and
an existing nonrecursive typed predicate. It counts occurrences, not distinct values.
No hidden subject filter, domain, max, deleted-history policy or ambient resource.
Cardinality rejects if outside integer domain, before any persistence.

`depends_on` must equal the set of consumed computed bindings; every dependency
must appear earlier in the topologically declared list. Cycles, forward references,
duplicate/shadowing result names, missing operand/type/result/error/policy/domain
and arbitrary backend expressions are rejected. Independent node order is not
imperative authority; nodes are pure and no intermediate result is externally
visible. No nested operator trees, functions, loops, recursion, dispatch or overload.

A write/creation uses `{kind:computed,type:...,name:...}`. Related operation guards
use the same explicit computed operand in existing typed predicates. Computed
bindings cannot masquerade as input parameters. Related create/update can consume
results; coupled creations can consume their own graph results and explicit primary
after fields. Existing predicates support integer equality and strict/non-strict
ordering with exact no-normalization policy. No implicit coercion.


## Atomic snapshot, cardinality history and successor

Related computation reads the declared operation-before store and before record.
Coupled computation sees that same before store plus explicit primary before/after
images; it never counts the private secondary append prefix. Each graph is evaluated
once per operation; reference parameters are validated before evaluation. Failure
of input, lookup, computation, predicate, creation validation, duplicate key,
integrity or supported persistence discards the private candidate. One inherited
atomic file replacement publishes primary mutation and all dependent creations.
