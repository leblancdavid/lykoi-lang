# R5.103 — existing-semantic inventory and closure decision

Inventory is based on executable compiler/backend semantics, not expected outputs
or the historical conventional implementation. Historical R5.102 inventory remains
unchanged. References below describe the current repository code.

| Concept | Pre-existing executable authority | R5.103 integration / boundary |
| --- | --- | --- |
| Strings, identifiers, finite enums, input defaults, raw preservation | v0.3 record/enum fields; input/input_default/literal assignments; runtime valid_state/value_of | Fresh scalar facts reach these already-existing operations. B01 improves before any repair; B04 stays successful. |
| Timestamp and existing timestamp nullability | Validator prim:timestamp/nullable and runtime utc_timestamp; input_default null; JSON persistence | Retained. No nullable boolean/integer/string types. |
| Lookup existence | Validator record_exists first on update/delete; runtime execute target lookup and rejection | Guard amendments preserve that first condition and its source error. No cross-entity existence predicate added. |
| Equality/lifecycle-state guards | Validator record_field_equals; transition source/guard/performs safety; runtime ordered conditions | New typed guards/standalone existing-model amendment route uses these nodes only. Rejects contradictory same-field guards and unchanged-state failure is externally checked. |
| Newly introduced field validation | Existing nonblank_input and timestamp_input | Additive-model lowering now binds source-declared new required-input guards and errors. Optional presence-aware nonblank is still unsupported. |
| Independent lifecycle fields | Existing machines/transitions and literal assignments; result_field_equals_assignment admits literal values | Remove normal lowerer's one-literal restriction; use existing additional guarantees. Two independent fields are tested, not arbitrary transitions. |
| Declared clock + timestamp comparison + collection selection | Validator list filter field_before_clock, field_equals, and all; runtime select_records null-exclusion/strict instant comparison; execute(clock=...) | Sufficient machinery already exists. Typed clock_queries now integrate it, including existing equality conjunction and read-only effects. B12 still needs archive storage and scalar-in-set, not a new before-clock predicate. |
| UUID/UTC creation resources | Existing capability kinds, capability assignments, requires/effects, runtime UUID/UTC providers | Normal generated API binds declared provider IDs deterministically. Invalid values/collision fail without a write; reset/default behavior tested. No new resource kind. |
| Additive migration and enum expansion | Existing adjacent migrations/add_fields and enum values; R5.102 extend_model | Preserved and composed with reads/defaults/guarded new fields; no inferred historical repair. |
| Bounded equality/membership queries | Existing CollectionQuery facets and read-only model-state adapter | Compose complete query facets with one actual scalar state, exact type/identity bindings and disjoint command namespace. Full query BDI policies are preserved. |
| Writable boolean/integer/strings arrays | Query views exist; v0.3 writable field algebra does not | **Not an executable orphan.** B03/B08/B13 store failures have missing writable prerequisites; no boolean-to-enum substitution or list persistence is added. |
| OR/NOT/range/in-set predicates | No general executable operators in the accepted validator/runtime | Deferred missing semantic compositions. Existing conjunction is reused; no arbitrary boolean composition is introduced. |
| Relationships, graph invariants, quantified guards, durable events, successors/calendar arithmetic | Not executable general v0.3 capabilities | Deferred. B18 also encounters the existing external-effect BDI gap before downstream authoring. |

The [versioned rules](../../../docs/existing-semantic-composition-v1.md) distinguish
compatible, unsupported and conflicting composition. One state is bound, not a
blind union of separately supplied profiles. Current closure is bounded: full
language/profile composability and all legacy operations are not established.

## Fresh evidence changes the diagnosis

- B01's pre-repair fresh success is stale-capture debt, not new semantics.
- B03 freshly re-emits all current typed membership facets, but the actual model
  binding still refuses missing `tags`. Do not classify this as missing membership.
- B06/B10 freshly retain supported typed equality reads plus structured unsupported
  write transformations. Mixed query/write profile routing alone cannot create the
  required normalized fields or omission-sensitive validation.
- B12's final typed existing-model clock selection reaches the actual base-model
  field lookup and refuses missing `archived`; a separate unmapped scalar-in-set
  relation remains material. Removing it would misstate coverage.
- B13's typed existing-model guard reaches the same absent `archived` field. The
  guard integration seam is closed generically, but notes/append, archive storage
  and B11's compound permission prerequisite remain unresolved for this case.
- B18's structural acceptance is only a bounded external-effect channel projection.
  Its first current halt is BDI, not proof that full event semantics are understood.

These are exposed source/code/native-stage observations. Downstream family demands
are diagnoses, not fabricated compilation or runtime failures.
