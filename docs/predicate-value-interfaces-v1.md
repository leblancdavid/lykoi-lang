# Lykoi predicate/value interface closure 1 — R5.107

This bounded normal composition extends existing values, ValueMutation,
CollectionQuery, PredicateTree, validation and UTC clock capabilities. Select
`context.domains.predicate_value_interface_profile: predicate-value-interfaces-1`
alongside the existing mutable, input and predicate profiles. Historical R5.106
captures, evidence and classifications are preserved.

## Exact literal replacement

A ValueMutation change may carry `field`, `source: {kind: literal, type, value}`,
`operation: replace`, `pipeline: []`, and `invalid_error`. The target must exist,
be writable, and be neither identity nor a lifecycle field. Source type must bind
the exact target type. Existing strings, enums, booleans, UTC timestamps (including
authorized nullable values), and existing ordered scalar collections are accepted.
Collection literals retain order, duplicate policy and element domain.

Literal replacement always writes the exact value on successful operation. It has
no input, presence policy, default trigger, transformation or expression evaluator.
Input/default/omission changes retain their previous distinct representation.
Writes share existing lookup, prewrite guard, atomic single-record persistence,
invariant validation and reload behavior. Literal changes compose with independent
lifecycle operations; lifecycle writes still use the transition algebra.

## Query selection amendments

Optional CollectionQuery facet `amendment` is `{base, composition, predicate}`.
The base is a complete supported query normalized to the common typed tree.
Composition is explicitly `and`, `or` or `replace`, authorized by the source.
The resulting query predicate is exactly the corresponding grouped tree (or the
replacement tree). All other base facets remain exact: source view, parameters,
node-local comparison, ordering, validation, inclusion, effect and result.
There is no implicit AND inference. Unknown composition must be clarified.

For an existing model listing, normal compiler binding independently normalizes
the actual declared list behavior and compares it to the amendment base. This
supports the existing no-input, read-only listing and field-equality/all-filter
and declared field-before-clock forms. An unfiltered listing normalizes to typed literal true equality, not a new
predicate primitive. A colliding command without this exact base refuses.
Already-normal query bases can also be amended, including membership selection.
Selection-only amendments intentionally cannot redefine other facets; a broader
authorized revision is represented as a complete new contract rather than hidden
inside a selection amendment. Existing clock-filter listings normalize their exact
clock capability into a typed resource binding; amendment preserves this binding
along with any existing preconditions and parameter errors. Nested amendments
must be flattened to one explicit complete base and composed tree.

## Parameter validation and query preconditions

Optional `parameter_errors` maps a declared parameter to `{missing, invalid}`
application error identities. `missing` may instead reuse `{kind: cli_rejection}`
from the existing required-input binding semantics; this keeps a declared invalid
type error without inventing an unspecified application missing-input identity.
The normal CLI leaves missing application-error inputs to the
application instead of incidental parser-required behavior. Type checking preserves
these identities, including invalid UTC timestamps. Existing nonempty/nonblank
parameter validation remains separate and does not transform inputs.

Optional `preconditions` is an ordered array of
`{predicate, error, stage: before_selection, rejection: unchanged}`. Trees bind
parameters and declared resources only, never record fields. Evaluation order is:
parameter presence/type → parameter validation → declared resource sampling →
preconditions in declared order → state read/validation → collection selection →
ordering/result. A false precondition emits its declared application error without
selection or a state write. An empty successful selection still follows the
declared no-match policy; it is not a precondition failure.

The pure query executor performs the same validation/precondition ordering before
record inspection. The normal CLI evaluates it before reading the state. Neither
path initializes, migrates or writes rejected/read-only queries.

## Declared deterministic clock operands

Optional `resources` contains `{name, type, capability, sampling: once_per_query}`.
Only an already-declared `utc_clock` capability is admitted by model binding;
type is exactly nonnullable timestamp with empty domain. Predicate resource operands
reference this semantic name and exact type. No ambient/system-time operand is
accepted. Default execution uses the existing declared capability adapter, not a
backend-local time calculation. Host/test providers bind capability IDs through
`execute_query(..., providers={capability_id: callable})`; undeclared providers
reject, values are UTC-validated, and each capability is sampled once per query
even when several operands use it. No arithmetic or arbitrary external resources.

Nullable timestamp fields may compare against nonnullable clock timestamps: both
are the existing timestamp value type, with independent exact binding nullability.
Atomic null comparison remains false, with existing NOT/null-test semantics.

## Authority, coverage, discovery and normal V1

Closed typed FRC schemas carry exact literal target/source and complete query
interface facets. Source-only inventory reconciliation compares all material
facts. Its existing bounded predicate equivalence does not erase amendment mode,
base-query preservation, precondition error/stage or resource identity.

Structural projection retains ValueMutation and CollectionQuery facets and full
recomposed IR. Coverage recomputes the exact projection, refusing lost targets,
altered bases, missing errors and unbound resource references. No parallel semantic
system or benchmark-specific node is introduced. BDI adds finite decisions for
literal source/type/value, amendment, preconditions, parameter errors and resource
bindings; existing tree decisions retain operand/grouping/null authority. Adequacy
refuses missing determined authority; undefined source composition, error or clock
choice must remain unresolved. Normal V1 embeds the full source contract, facts
and IR and exact recovery detects material interface changes.

Normal compiler dispatch deterministically lowers to existing atomic replacement,
pure predicate selection, read-only adapter and declared capability mechanisms.
`interface_corpus.py` supplies accounts/products/documents/sessions captures;
`test_query_interfaces.py` challenges authority, coverage, adequacy, faithful V1,
literal writes, lifecycle, membership/order, validation/precondition distinctions,
null timestamps, rejected-storage preservation and injected-clock subprocess output.

Evidence uses same-agent captured source interpretations, inventory and literal
oracles with synthetic owner approval. Agreement is not independent cognition or
proof of live English formalization accuracy. B01–B20 are exposed local regression
data, not held-out generalization. No relationships, events, graph reasoning,
arithmetic, joins, aggregates, pagination or infrastructure work is added.
