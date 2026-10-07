# Lykoi typed predicate and guard composition 1 — R5.106

`typed-predicates-1` is a bounded, explicitly selected extension of the normal
`typed-mutable-values-1` / `typed-input-values-1` profile. Set
`context.domains.predicate_profile` to `typed-predicates-1` and provide the
`predicate_semantics` facet, including explicitly empty arrays. Historical v0.3
serialization and R5.105 evidence retain their interpretation.

## Closed boolean trees and operands

Every node declares `result_type: boolean`. Nodes are:

* `compare`: `operator` eq/lt/le/gt/ge, typed `left`, `right`, `policy`, `nulls`.
* `and` / `or`: ordered serialization of at least two `children`, with explicit
  nesting. All children are pure; evaluation computes every child without effects.
* `not`: one `child`. Inequality is **only NOT eq**, avoiding a competing != node.
* `is_null`: one supported nullable `operand`; IS NOT NULL is NOT is_null.
* `present`: mapping presence of a declared input or local supplied pipeline value.
* `member`: `operator: in`, scalar `left`, compatible collection `right`, policy
  and nulls. Collection CONTAINS scalar normalizes to scalar IN collection.

Operands declare exact semantic `type` and use `kind: field/parameter/resource`
with semantic `name`, `kind: literal` with typed `value`, or `kind: value` with
RAW/TRANSFORMED/PERSISTED `stage`. The local value operand is scoped to the
pipeline being validated, not a free-form executable string. Resource operands
are representable by the algebra validator with an explicit environment; this
round does not add a normal query resource binding/clock sampling mechanism.
Normal queries use declared typed parameters for timestamp bounds.

Scalar types are strings, identifiers, enums with exact finite domain, booleans,
and supported UTC timestamps. Collection types retain element domain, insertion
order, duplicate policy and exact storage equality. Reference declarations must
match their bound type; no string-to-enum, bool-to-integer or other coercion.
Nullability is restricted to the existing timestamp profile. Literal booleans
must be actual JSON/Python booleans; integers 0/1 are not substitutes.

The compiler validator allows depth below 32; the closed formalizer producer
schema bounds nesting to four composition layers. AND/OR permit 2–64 children.
Trees round-trip structurally, without textual precedence or arbitrary code.

## Comparison and null rules

Equality supports all declared scalar types. Strings/identifiers/enums declare
independent `policy: {case: sensitive|casefold, normalization: none|strip}`;
neither storage nor parameters are transformed by comparison. Boolean/timestamp
comparisons require sensitive/none. UTC timestamps compare parsed instants,
including equivalent fractional-second representations.

Ordered comparisons are timestamp-only. Integer type/write/store integration is
still insufficient for this normal profile, so integer comparison is refused;
no arithmetic or successor semantics are introduced. Inclusive/exclusive range
boundaries compose ordinary ge/le or gt/lt nodes under AND. No range primitive.

Every comparison/membership node explicitly declares `nulls: false`: an atomic
comparison with a null (or omitted optional input) yields false. NOT complements
that result, so NOT(null == timestamp) is true. Null exclusion must be an explicit
IS NOT NULL conjunct when required. Null participation is never inferred.
Presence is independent of empty/whitespace/null value and transformation stage.

## One condition language, distinct effects

CollectionQuery predicate facets accept trees with fully typed source fields and
parameters. `comparison: {scope: predicate_nodes}` and empty `inclusion` place
all selection conditions in the tree. Existing equality/collection-CONTAINS and
inclusion facts normalize at execution into this same interpreter, preserving
legacy comparison/ordering/results. No joins, aggregates, pagination, nullable
sort policy or new result semantics. Nonnullable scalar ordering with unique
identity tie-break remains required. The normal CLI decodes collection/boolean
parameters as JSON and validates declared types before selection.

Mutation guards accept `{predicate,error}` and evaluate against the original
record and declared operation parameters before preparation. The
`predicate_semantics.guards` array adds `{command,predicate,error,rejection}`
preconditions to existing lookup lifecycle/delete operations. False produces the
declared error and `rejection: unchanged`; existing lookup errors retain precedence.
Queries remain read-only; predicate reuse does not grant write authority.

R5.105 validation `when` accepts a common tree over the explicitly scoped local
staged value. RAW remains a private copy before transforms; TRANSFORMED observes
the pipeline point; PERSISTED observes the final candidate before commit. No
transform may follow a PERSISTED observation. Append element pipelines cannot
pretend their element is the persisted collection. Omitted optional writes skip
pipelines, preserving R5.105's presence/default semantics. Cross-parameter staged
validation is not included in this profile.

`predicate_semantics.invariants` accepts record-local trees at read/write boundaries
with the existing `invalid_state` rejection. This is bounded per-record validation,
not quantified or cross-entity invariants.

## Boolean store seam

`predicate_semantics.booleans` declares `{name,creation,migration}`. Creation is
`{source: literal,value: true|false}`; explicit additive migration values are also
booleans. Writable updates reuse generic mutable `replace` with JSON-encoded
boolean input and existing atomic rejection. The composed model carries a boolean
field and the mutable runtime validates, persists and reloads it. The frozen
legacy generator/schema is not extended or used to validate this new IR as v0.3.
Boolean input creation, literal mutation commands and replacement of an existing
listing's implicit selection are not added by this bounded profile.

## Authority, projection, BDI and faithful normal V1

The closed typed FRC producer schemas carry complete trees, types, operands,
operators, grouping, policies, null behavior, stages and rejection behavior under
source-quoted relations. Source-only inventory reconciliation compares full facts.
For trees it recognizes only bounded mechanical equivalence: associative,
commutative and idempotent same-operator AND/OR, plus double negation. It does not
expand distribution or guess source intent. A AND (B OR C) remains distinct from
(A AND B) OR C. Faithful V1 retains exact serialized grouping even where
reconciliation can establish equivalence.

Coverage recomputes complete facts/IR/facets and refuses omitted or altered tree
components. BDI enumerates each complete material node and subnode, including
operands, operator/inclusivity, membership direction, grouping, policy and null
participation; guards also expose error/rejection decisions. Removing determined
authority makes adequacy IMPLEMENTATION_UNDERSPECIFIED. Formalizer guidance
requires clarification for undefined recent boundaries, observable unspecified
inclusivity/null participation and ambiguous AND/OR grouping. Structured agreement
is not a proof that an English interpretation was authorized: public captures,
inventory and literal external plans remain same-agent evidence with synthetic
approval, not independent cognition or measured live formalization accuracy.

Normal V1 embeds the source contract, full typed facts and recomposed IR. Recovery
compares the complete projection. Normal compiler dispatch deterministically
inserts a self-contained standard-library predicate runtime into the application;
predicates contain no executable source and type errors refuse before execution.

## Verification and boundaries

`src/lykoi_workspace/predicate_corpus.py` defines public products/users/sessions/
documents captures; `tests/test_predicates.py` exercises the complete normal path,
source disputes, adversarial trees, typing, stage conditions, BDI/adequacy and V1.
Independent subprocess plans check grouping, nulls, UTC boundaries, scalar-IN-set,
persisted collection membership/state composition, transformed strings, boolean
creation/update/reload, guarded lifecycle and rejection byte preservation.

No persistent relationships, graph integrity, quantified guards, external events,
durable ordered events, successor creation, arithmetic or infrastructure work.
See the R5.106 report for actual verification, locks and exposed local transfer.
