# Lykoi typed computation 1 — R5.111

## Exact inherited kernel and pressure

The R5.110 proposed kernel is exactly **23**: K01 record schema; K02 field;
K03 finite sequence; K04 typed binding (`var`); K05 literal; K06 same-type
equality; K07 conjunction; K08 complement; K09 membership; K10 selection;
K11 trim; K12 finite pointwise map; K13 stable-first uniqueness; K14 transition;
K15 instant; K16 strict ordering; K17 operation contract; K18 cardinality;
K19 input presence; K20 typed resource/capability authority; K21 durable state;
K22 atomic commit; K23 finite nonempty-path reachability.

K12 maps a supplied transformation over finite values; it does **not** define
integer addition or temporal displacement. Hiding either operation in a backend
map would import new meaning without accounting. This round admits **K24 checked
integer addition** and **K25 fixed-duration instant displacement (`offset`)**.
Proposed count **23 → 25**. These are specific irreducible meanings, not a broad
Expression, Arithmetic, IntegerMath, Counter, Sequence, TemporalMath or generic
arbitrary computation primitive. This is proposed accounting, not a minimality proof.

Integer and duration are value domains/profiles, not additional core operations.
Graph structure, `value`, dependency edges, result names and computed consumption
compose K04/K05/K17. Cardinality values reuse K18, selection K10, persistence K21,
coupling K14/K22, integer comparison the existing typed ordering family K16.
Increment is addition of literal one; successor is ordinary creation with explicit
field values and coupled effects. Neither adds a core concept.

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

## Arithmetic/temporal adequacy

Addition is independently useful for inventory adjustments, retries and ordinal
offsets. A separate subtraction operator was not justified by these contracts:
signed literal/parameter adjustments already express their authorized negative
changes. This is **not** a claim that arbitrary `x-y` can always be represented
without a negation/subtraction meaning, especially at signed-domain boundaries.
Multiplication, division and dynamic unit conversion remain excluded.

`offset` is now a **core fixed-duration displacement meaning**, with duration/unit
as typed policies. Calendar months/years, DST/local tomorrow and unrestricted
recurrence remain unresolved/excluded. A fixed 86400 seconds is not generally local
tomorrow. In this leap-second-free UTC model an explicitly authorized UTC calendar
day displacement agrees with 86400 seconds, but arbitrary runtime day-to-second
conversion is not implemented. B19's runtime N-day interval/nullable primary field,
primary successor cloning and actor integration are therefore not automatically
closed by a synthetic fixed-second example. Clock K20 observes an instant and
never performs arithmetic; displacement consumes an explicit timestamp source.
Unspecified "next month", observable overflow policy or concurrent sequence
authority must be clarified rather than inferred.

## Atomic snapshot, cardinality history and successor

Related computation reads the declared operation-before store and before record.
Coupled computation sees that same before store plus explicit primary before/after
images; it never counts the private secondary append prefix. Each graph is evaluated
once per operation; reference parameters are validated before evaluation. Failure
of input, lookup, computation, predicate, creation validation, duplicate key,
integrity or supported persistence discards the private candidate. One inherited
atomic file replacement publishes primary mutation and all dependent creations.

`ordinal = cardinality(entire append-only history) + 1` is sufficient for synthetic
one-row-per-operation history starting empty, with cooperating exclusive one-store
operation reservation. Zero-based `cardinality` is also representable with `value`.
It is not a general distributed monotonic sequence: deletion, imported arbitrary
ordinals, multiple same-snapshot creations with the same formula, hostile writers
or unreserved host API calls invalidate that inference. Ordinal choices require
source authority. No `max+1`, counter capability or Event primitive is introduced.

Synthetic successor construction uses ordinary related creation from computed
primary after fields, in the existing coupled atomic frame. This verifies composition
of creation + computation + atomicity, not all legacy primary successor interfaces.
`for_each` remains finite pointwise map composition: graph lowering needs no new
iterator semantic. Finite cardinality domain scope is explicit K03/K10/K18 policy;
no unrestricted aggregation or recursive domain is admitted.

## Requirements interfaces and evidence limits

The existing generic `reference_semantics` / `atomic_state_semantics` typed FRC
facets carry the full graph. Closed producer schemas retain operator, type/unit,
operands, finite cardinality selection, exact dependencies, binding/error and policy.
Structural recomputation and faithful V1 recovery compare all graph bytes/facts;
incomplete graphs reject before authoring. Reconciliation detects material graph
changes against the source-only inventory. BDI adds only generic computation graph
and policy decisions under exact source-clause authority; loss of determined
authority fails adequacy. No benchmark identifiers enter product dispatch.

Backend-independent integer boundary vectors reject Python arbitrary precision,
bool-as-int and floats; temporal vectors fix Gregorian leap-year, negative duration,
microsecond preservation, canonical UTC and range errors. Existing broad timestamp
parsers outside this new operator remain a backend-shaped compatibility leak.
The old standalone untyped query integer profile still accepts unbounded host ints;
the selected R5.111 typed durable/query profile rejects them. There is one backend,
so vectors evidence defined semantics, not cross-backend implementation equivalence.

Five-domain full normal-pipeline external fixtures cover Inventory, Retry, Session,
Subscription and Ledger, with numeric reload, signed adjustment, cardinality ordinal,
fixed displacement, ordinary successor, duplicate/computation failure rollback and
query byte preservation. Same-agent captures, inventories, literal plans and synthetic
owner approval are evidence limits; this is not held-out generalization.
