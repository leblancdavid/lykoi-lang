# Lykoi bounded existing-semantic composition — R5.103

This prospective normal-path specification extends integration of the existing
v0.3 algebra. It adds no writable primitive type, predicate operator, relationship,
collection mutation, resource kind, migration operation or atomic-effect family.
The R5.102 [existing-scalar-1 specification](existing-scalar-normal-path-v1.md)
remains the historical boundary; the rules below describe the current additive path.

## Typed facets and amendments

The six existing scalar facets remain mandatory. Two optional facets may be
explicitly emitted as `crud` relations with
`parameters: {profile:"existing-scalar-1",facet,value}`:

| Facet | Closed value shape | Existing executable meaning |
| --- | --- | --- |
| `guards` | Array of `{command,field,value,error,rejection:"unchanged"}` | Append an equality precondition to an existing lookup update/delete. Existing `record_exists` remains first; prior guard order/failures remain authoritative. |
| `clock_queries` | Array of `{command,predicates,order,result:"whole_records",effect:"read_only"}` | Add a disjoint read-only command using ascending field keys including identity. |

Each predicate is exactly `{kind:"field_equals",field,value}` or
`{kind:"field_before_clock",field,clock:"utc_clock"}`. Multiple predicates use
the **already-existing conjunction** (`filter.kind=all`). Clock authority binds
an existing UTC resource or an explicitly requested UTC resource declaration;
effects/dependencies/requires are recomputed by the existing validator.
Before-clock means strict instant comparison; a null timestamp does not match.
Equality guards on lifecycle fields remain subject to existing transition safety.
Conflicting guards on the same command/field, including differing rejection errors,
refuse. Repeat/incompatible commands refuse rather than overwrite.

Standalone amendments select `capability_profile:"existing-model-1"`, provide
reviewed prior authority as `existing_base_model`, and emit one or both of the
same facets with `profile:"existing-model-1"`. No complete scalar restatement is
required to amend an already-authorized model. At least one nonempty amendment
is required. Every additional material obligation remains in structural coverage.
The entire prior model is validated and preserved; it is not an unrestricted
author candidate. This uses the same contextual-authority trust boundary as
R5.102's `scalar_base_model`, with synthetic approval in the published experiment.

The producer may record a boolean guard/equality value in an existing-model
amendment (the FRC and query vocabulary already represent booleans). That does
**not** add boolean field storage. Lowering still requires a real field and an
existing executable v0.3 type. B12/B13 therefore honestly refuse missing
`archived` bindings instead of substituting an enum or declaring coverage complete.

Existing-model additive evolution also binds guards for newly introduced required
inputs. Nonblank requires a supplied required input; no inferred presence predicate
is added. Timestamp input validation retains the existing nullable timestamp rule.
Creation defaults never authorize historical migration defaults. Explicit additive
migration maps, prior migrations, unrelated fields and existing command/resource
authority remain required.

Independent single-transition lifecycle fields can coexist in one record. Creation
uses the existing primary literal guarantee and existing
`result_field_equals_assignment` guarantees for further initialized literal fields.
Every lifecycle field still has only one declared source→target transition in this
profile. No general state-machine programming or new transition operation is added.

## Compatible scalar/query composition

Select `capability_profile:"existing-composed-1"` and explicitly declare
`collection_store:{kind:"composed_scalar",state:STATE_ID}`. Emit the complete
scalar profile and complete typed CollectionQuery facet groups. The query view
binds the **actual derived scalar model**, not a second unrelated supplied model.

Composition has three outcomes:

1. **Compatible composition:** one declared state; exact model/view type and
   identity-uniqueness binding; disjoint commands; complete facets; read-only query
   effect (`state:read_only,persistence:unchanged`); source-authorized comparison,
   validation, ordering, inclusion and result policies. Scalar writes, creation
   defaults/resources, explicit migration, identity and independent lifecycle
   facets may coexist with those reads.
2. **Unsupported composition:** missing/nullable/nonprojectable query fields,
   mutating query/write interactions, additional unmapped obligations, arbitrary
   cross-state/relationship/effect interactions, or incomplete facet groups.
   Having each isolated concept does not qualify its interaction.
3. **Conflict:** contradictory selected state or command authorities refuse;
   equal-field guard authorities also cannot disagree on value/error. The new
   composition projection records `COMPATIBLE_COMPOSITION`,
   `UNSUPPORTED_COMPOSITION` or `CONFLICT`. The underlying native failure remains
   structural coverage failure; no grant is issued.

Model/query type disagreement is refused by the existing model-state adapter.
The classification is conservatively unsupported where that adapter cannot
distinguish an unsupported representation from inconsistent authority; no generic
logical contradiction solver is claimed.

BDI preserves existing scalar decisions **and** all existing query decisions
(runtime binding, comparison, validation, inclusion, order, effects, results).
Adequacy uses their determined/freedom clauses and the full contract commitment.
It does not replace them with profile membership. Complete structural coverage,
source reconciliation, clarification, policy handling and owner approval precede
these stages. `LykoiContractV1` preserves the full contract and derived facts;
recovery recomputes exact content. Restricted authoring/compiler dispatch reruns
coverage, BDI/adequacy, faithful recovery and existing v0.3 validation.

Standalone model amendments and composed scalar/query contracts are two bounded
routes, not proof that every combination of all profiles is qualified. A model
amendment plus arbitrary query group still refuses. Multiple entities, mutable
query effects and interactions not specified here remain outside scope.

## Creation-provider binding

Normal generated Python exposes the existing API as
`execute(behavior,inputs,clock=None,*,providers=None)`. Creation providers are
callables keyed by **declared capability IDs**, restricted to the behavior's
creation assignments and `requires`. UUID outputs must be UUID v4 strings;
clock outputs must satisfy the existing UTC timestamp validation. Invalid values
fail before persistence. Existing collision/state validation remains in force.
The existing list `clock` argument remains available for exact boundary checks.

This is host/test resource binding, not new resource semantics, CLI flags,
serialized provider values or arbitrary capability access. A ContextVar scopes
bindings to execution and resets them after success/failure; defaults still call
the original UUID/UTC providers. The legacy runtime template, generator, canonical
model and generated historical application remain unchanged. The normal dispatcher
includes `creation_provider_runtime.py` before the normal entrypoint.

## Bounded verification and limits

The [R5.103 report](../benchmark/results/phase5c/R5_103-REPORT.md) publishes
source-authorized synthetic normal chains and fresh exposed-corpus chains.
Tests include command/state conflicts, missing/null views, unsupported write/query
frames, V1/coverage tampering, guard existence/failure preservation, required-field
guard evolution, two independent lifecycle fields, strict clock equal/past/future/
null/terminal-state boundaries and deterministic provider collision/refusal/reset.

CollectionQuery still supports only its existing equality/membership vocabulary.
The clock-query route uses existing v0.3 list semantics; it does not expand
CollectionQuery with nullable/range/OR/NOT/in-set/joins/aggregation/pagination.
No mutable arrays, relationship quantification, temporal arithmetic, successor
creation or durable audit effects are introduced. BDI retains bounded discovery
limitations. The R5.102 isolated Unicode stdout observation is preserved; no
encoding/portability repair is part of this specification.
