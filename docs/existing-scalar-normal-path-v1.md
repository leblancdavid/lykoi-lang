# Lykoi ExistingScalar normal-path profile 1 — R5.102

This additive `existing-scalar-1` profile exposes a **bounded subset of existing
v0.3 semantics** through the ordinary requirements workspace, pipeline, normal
`LykoiContractV1`, restricted author and `LykoiProgram-1` compiler dispatcher.
It introduces no v0.3 type, predicate, assignment, effect, resource or migration
operation. The existing validator and Python runtime remain normative for the
lowered model. Historical documents and profiles retain their routing.

## Typed producer interface

The FRC-0.1 obligation envelope is unchanged. Each profile relation is:

```json
{"kind":"crud","parameters":{"profile":"existing-scalar-1","facet":"fields","value":[]}}
```

The example demonstrates shape only; an empty fields facet is invalid. Exactly
one relation for **each** of the following facets is required. Empty lifecycle
and evolution arrays are explicit facts, not defaults inferred from omission.
The closed producer schema is executable in
[`scalar_schema.py`](../src/lykoi_workspace/scalar_schema.py); native
cross-reference/value validation in
[`scalar_profile.py`](../src/lykoi_pipeline/scalar_profile.py) is normative.

| Facet | Closed value shape and meaning |
| --- | --- |
| `storage` | `{path,version,missing,write,rejection}`; local JSON filename, positive schema version, `empty_collection`, `atomic`, `unchanged`. |
| `fields` | Array of `{name,type,domain,nullable,preservation}`. Types: `string`, `identifier`, `enum`, `timestamp`. Domain is the exact finite string array for enums, otherwise `[]`. Nullable is a boolean, true only for timestamps. Preservation is `verbatim`. |
| `creation` | `{command,bindings,validation}`. Bindings are `{field,source,value,default}`; source is `input`, `literal`, `uuid_v4` or `utc_clock`. Input/resource value is null. Default is null (none) or `{value,trigger:"omitted",boundary:"creation"}` for an input. Validation is an array of `{field,rule,error}` using `nonblank` or `timestamp_utc`. |
| `listing` | `{command,order,result}`; explicit ascending field-key sequence containing identity, result `whole_records`. |
| `lifecycle` | Array of `{field,initial,source,target,command,missing_error,transition_error,rejection}`. Bounded initial/source agreement, one guarded transition per lifecycle field, repeat rejection and unchanged rejected state. |
| `evolution` | Array of `{from,to,defaults,boundary,preservation}`; adjacent schema versions, explicit introduced-field default map, `explicit_migration`, `unrelated_fields`. The complete existing chain is required. |

`default:null` means **no default**, distinct from `default:{value:null,...}`
which is permitted only by existing timestamp nullability. Input omission
triggers an input-default assignment. A supplied empty string remains supplied;
it does not trigger a default. CLI textual `null` is not explicit null: it is an
invalid timestamp input. Existing timestamp-null values can occur in stored
records and the underlying Python API. No persistent presence tag or general
nullable type is added.

Validation observes values without transforming them. Nonblank checking may
inspect `.strip()` but the assignment retains the original string. No normalized
or trimmed write is authorized by this profile. Existing CollectionQuery
comparison `none`/`strip` and sensitive/casefold policies remain distinct and
unchanged; an end-to-end gallery-store query tests exact whitespace/case neighbors.
Enums retain exact domain/value/default/JSON persistence semantics. Out-of-domain
CLI enum input uses the existing argparse choices refusal (exit 2); the profile
does not replace it with a guessed application error. Timestamp/nonblank guards
use the declared application error and preserve stored state.

## Authority, structure and adequacy

AI interpretation produces typed facts at the normal formalizer boundary. Both
producer roles receive the profile guidance. The source-only inventory remains
candidate-blind. For closed typed facts, relation equality can reconcile different
display prose; domains, source commitment, evidence references, missing/extra
material items, clarification, approved policy and exact owner approval remain
required. Structured output is untrusted until that lifecycle completes.

Projection consumes facets/types, never English, benchmark IDs or wording
patterns. It validates that existing lowering can express the facts, traces each
obligation and recomputes exact coverage. Any nonprofile material obligation or
incompatible component context remains unsupported. A query plus a write request
is not automatically complete because its fields are understood. Mixed-profile
contracts still fail closed; sequencing separately authorized normal contracts
against an existing model is demonstrated, not general mixed-profile composition.

Existing BDI rules expose optional input, invalid input, persistence, failure
atomicity, transition and retry. The unchanged adequacy engine consumes their
explicit determined clauses. Removing an optional/default authority clause still
produces `IMPLEMENTATION_UNDERSPECIFIED`. Missing/invalid typed scopes are rejected,
not converted into freedom. Unresolved WHAT questions still prevent approval.

Creation-only default authority cannot authorize migration. Evolution requires a
separate explicit map at an explicit migration boundary. The historical B01
missing-priority ambiguity remains separate: no generic rule repairs historical
missing fields from a creation default. A supplied existing model's previously
authorized migration is retained as context, not invented as an answer to an
ambiguous new requirement.

## Normal V1 and deterministic lowering

Domains explicitly select `capability_profile: existing-scalar-1`.
`LykoiContractV1` contains exactly `{schema_version,profile,contract,facts}`.
It retains the whole FRC and independently recomputes its typed facts on recovery;
changed facts or obligation loss cannot produce faithful recovery. The normal
author emits the authorized `LykoiProgram-1` envelope; the controller rejects
substitution and the compiler reruns coverage, BDI, adequacy and v0.3 validation.

Lowering creates declared record/enum types, JSON storage/read/write authorities,
clock/UUID resources, assignments, conditions, guarantees, identity uniqueness,
transition guards and additive migrations using existing v0.3 nodes. Existing
backend constraints apply, including one UUID identity and the creation literal
result guarantee. The demonstrated creation profile has one literal initialized
field; arbitrary multi-machine composition is outside this integration.

An explicitly reconciled `scalar_base_model` domain selects a validated existing
v0.3 model. Generic evolution preserves its stable IDs, commands, inputs, resource
authority, guard behavior and prior migrations. It supports verbatim input-field
introduction with explicit creation/migration defaults and finite enum expansion.
Existing field type changes/removal, enum removal, historical repairs and added
input guards in an existing-model amendment refuse. Existing diagnostic scenarios
receive only the explicitly authorized introduced-field migration values.

External plans remain source-bound and sealed before authorship. Fixture/storage
allowlists derive from the declared local JSON resource, allowing multiple public
domains without task-specific store names. No acceptance oracle is inferred from
the author or generated Python.

## Evidence and material limits

See the [R5.102 inventory/report](../benchmark/results/phase5c/R5_102-NORMAL-PATH-REPORT.md).
Three public domains and additional existing-model/enum/query compositions execute
normally. These are captured AI interpretations replayed through ModelAdapter;
they are not a general English parser, live formalization accuracy evidence,
independent cognition or real-owner approval. Synthetic owners explicitly approve
the captured contracts. Application verification uses external processes.

Boolean/integer fields exist only in the read-only query view, not the writable
v0.3 record algebra. Date-only types are absent. Arbitrary equality-guard amendments,
clock-relative list projection, broader lifecycle composition, general mixed
write/query contracts and deterministic creation-resource injection remain seams.
Clock/UUID creation is explicit and property-tested, but uses the existing actual
resource providers. A Unicode probe fails stdout serialization in the current
isolated Windows subprocess environment after persistence; no portability repair
is part of this round. Thus **full existing-semantics normal-path closure is not
claimed**.
