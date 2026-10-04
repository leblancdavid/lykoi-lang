# R5.38 prospective nullable and static readiness profile

This versions the prospective semantic/type interface consumed by
`benchmark.semantic.current_pipeline`. It does not amend the historical v0.3
model or frozen R5.23 artifacts. Candidate core vocabulary remains 30.

## Domain authority and taxonomy

The type declarations (`shape_valid`) and typed-value interpretation (`_type`)
define these domains. A record's required-field set excludes **only fields
whose outer declaration is `optional`**. These are semantic definitions, not an
inference from generated Python dictionary behavior.

| Declaration | Record membership | Present value domain |
| --- | --- | --- |
| `T` | required | `T` |
| `optional<T>` | may be absent | `T` |
| `nullable<T>` | required | `null ∪ T` |
| `optional<nullable<T>>` | may be absent | `null ∪ T` |

The serialized forms are respectively `T`, `{"optional": T}`,
`{"nullable": T}`, and `{"optional": {"nullable": T}}`. Existing scalar
domains include string, integer, boolean and typed UTC instant; sequences and
records also exist. An instant is not just an arbitrary string. Integer excludes
boolean. Optionality has omission meaning at record membership, not a sentinel
value admitted by the scalar domain. A required nullable field cannot be omitted.

The recursive shape validator also admits redundant wrappers and
`nullable<optional<T>>`. The latter is **not** equivalent to an optional nullable
record field: its outer nullable declaration still requires membership; inner
optional value validation supplies no standalone absent value. General wrapper
normalization and nullable/optional parent-record traversal are not established
by this profile. Readiness must report concrete compositions rather than infer
closure across arbitrary nesting.

## Two facts, two eliminations

Field presence and value non-nullness are independent facts. Existing semantic
record membership (`present(reference)`) establishes the former for an optional
field. Existing negated typed equality to null establishes the latter:
`not(equals(reference, literal(null, nullable<T>)))`, with either equality operand
order. These are descriptions of serialized semantic relations, not prescribed
human syntax or a new `non_null` construct.

In a checked positive conjunction:

* `optional<T>` plus that field's presence licenses `T`.
* `nullable<T>` plus that value's non-nullness licenses `T`.
* `optional<nullable<T>>` needs **both** facts to license `T`.

Neither fact implies the other. An optional-nullable reference cannot even be
safely evaluated against null without membership or equivalent established
presence; negated equality does not make a missing field exist. Presence alone
leaves nullable intact. Required nullable membership is already established by
its declaration, not by an optional-field witness.

Equality against typed null is analyzed in the original nullable value domain,
with membership retained when required. Its own conclusion is not used to type
its premise. The rule unwraps the domain generically; there is no instant,
string, integer, operation-name or field-name dispatch.

## Scope, identity, scheduling and population facts

Facts are keyed by reference slot/path and fact kind, scoped to the containing
positive conjunction. Analysis checks all same-scope facts independent of
serialization order. Checked scheduling puts membership before null evaluation,
then typed consumers; this is safe lowering of a relation set, not procedural
left-to-right language semantics. Ordinary negation does not export a fact.

Selection introduces a fresh `item` binding and does not export it to sibling
selections, branch alternatives, outcomes, or state-transition operands. A pre
fact is not a post fact. A different record slot or field cannot consume it.
The direct selected population can supply checked ordering-key dependencies.
Nested selection population-fact propagation is currently unsupported; a
semantically safe nested selection may consequently be rejected. No implicit
null-first/null-last ordering exists. Unrefined nullable instant comparisons
and ordering reject.

CheckedPlan retains source-bound object handles for compatibility with its
consumers and seal. Facts additionally retain stable contract/document-path
identities, declared type, declared presence/nullability domains, established
presence/non-null states, effective type, and stable producer/scope identities.
Ordering keys retain every producer dependency, including both facts for a
combined domain. A changed source or fact seal rejects before consumption.
Document-path identities survive deserialization; they are not permission to
transfer a fact across a changed source or another binder instance.

The analyzer is the sole type authority. The emitter schedules checked producers
and consumes checked effective key types. It does not inspect null equality to
unwrap a type. The independent verifier interprets semantic relations and
checked scheduling over independently observed values, never generated code.

## Whole-contract static readiness

`benchmark.semantic.readiness_r5_38.inspect` collects a whole application's
operation facts and every encountered unsupported composition in one invocation.
Each operation is checked separately through the current authoritative entry;
failed operations are additionally traversed with correct local contexts so
later operand failures are not hidden by the first error. Relation-set planning,
registered pre/post states, branch read/write contexts, ordering dependencies,
input decoder domains, transport routes/outcomes/persistence and launch metadata
are evaluated before any target unit is rendered.

Consumer capability coverage is a separate implementation inventory, not a
second type authority. `SUPPORTED_STATIC` means supported by the checked
analysis and documented consumer boundary, **not** executed or universally
proved correct. Independent generation/execution tests challenge that prediction.
Missing public/state/launch profiles are explicit gaps. External contract
obligations omitted by the source must be supplied explicitly for boundary
coverage; the pass cannot infer natural-language obligations from a source that
does not represent them. Unknown obligation kinds fail closed. Population/content
validity and public state-alternative routing currently fail closed as unsupported.

The 84-row machine-readable closure matrix distinguishes relation, base type,
wrapper domain, required facts, state shape, context and stage. Every accepted
matrix row also receives current-pipeline generated/grounded semantic evidence;
typed nullable input execution does not establish public nullable decoder support.

Only a whole-contract `READY`, including benchmark-critical profiles and explicit
boundary obligations, can recommend a comprehensive retry. Semantic-only `READY`
cannot authorize it. This bounded static analysis is not a formal proof of
application totality, arbitrary domain closure or universal implementation
correctness.
