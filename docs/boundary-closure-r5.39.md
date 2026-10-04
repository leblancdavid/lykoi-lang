# R5.39 checked whole-application boundary

This prospective interface uses `benchmark.semantic.current_pipeline` and its
single authoritative analyzer. Candidate core semantics remain **30**. No new
expression, union, state transition or semantic construct is introduced.

## Refinement facts and provider multiplicity

`CheckedPlan.refinement_facts` records one fact per value/kind/positive conjunction
scope, including declared/effective types and every stable source justification.
Optional presence and nullable non-nullness remain separate facts. Equivalent
presence witnesses, or existing negated equality to the correctly typed null
(including reversed operands), justify the same fact. Source identities survive;
the checked scope contains all providers and scheduling evaluates membership
before non-nullness before consumers. Neither emitter nor verifier handles
duplicate guards specially. Singleton selection guards have the same fact model.

Wrong fields, other bindings, negative scopes and other state sides do not license
refinement. A positive non-null guard plus a typed-null equality consumer rejects
as incompatible domains. Other predicates on the same target are not automatically
providers. General satisfiability checking is not claimed: `present(x)` plus
`not(present(x))` can denote false without establishing a contradictory runtime
value. Nested selection population-fact propagation remains the R5.38 limitation.

## Public nullable decoding

The R5.32 decoder composes `nullable<T>` with its existing scalar decoder for `T`:
JSON null is a supplied typed null, and any non-null raw value must decode as `T`.
Malformed values never become null. Omission is key absence, independently of
nullability; outer optional controls whether absence is accepted. A required
nullable input omitted is still `missing_required`.

Checked CLI nullable descriptors require JSON representation. The public null
representation is the JSON token `null`; a string literal is quoted JSON.
`BOUND_TYPED` plus the typed input value distinguishes null from a non-null value;
`OMITTED` and `BINDING_FAILED` remain independent evidence states. Collections use
existing R5.35 per-element binding; nullable scalar elements are supported, with
element-index failures. Nested collections/optional element sentinels are not
broadened by the readiness-v2 decoder table.

## Declared durable alternatives and constraints

`application_boundary_r5_39.state_profile` links the application's registered
state names to exact codecs, typed content declarations and checked initial states.
An alternative has `codec` and `constraints`. Bounded declarations are:

- `equals` at a record path, for an existing typed discriminator;
- `population` at a typed record sequence, with an optional string identity,
  explicitly declared nonblank string fields and finite typed field domains.

These are persistence/profile restrictions expressed using existing type,
identity, equality, nonblank and domain concepts. They do not invent an application
invariant or infer one from an operation name. New kinds reject for separate
semantic review. Applications must explicitly declare required constraints.

Loading proceeds bytes → JSON parse → full recursive codec → declared content
checks → exactly one typed alternative. Zero or multiple matches reject. Empty
populations are checked too: envelope discriminator checks do not depend on rows.
No invalid element is dropped, filled, trimmed or normalized. Failed loads never
reach generated semantic invocation and do not write durable bytes.

The prototype validates declared content on **load**; it does not prove every
operation universally preserves arbitrary profile predicates. Independent semantic
verification and post-observation persistence checking remain separate. Direct
generated writes retain existing crash/concurrency limitations.

## Dispatch and applicability

A public route declares `alternatives: {state-name: operation-mapping}`. Static
validation checks each mapping against its CheckedPlan's pre-state codec and
registered post-state alternatives; every plan must have a public mapping.
After typed persistence decoding, transport consumes the checked alternative name.
It contains no application-specific version algorithm. A route unavailable in the
current alternative is an invocation boundary failure, with no semantic execution.
An available route can still fail its generated semantic applicability predicate;
that is separately recorded as generated execution rejection, not a typed outcome.

## Aggregate profile

`application_boundary_r5_39.aggregate` links semantic application identity,
CheckedPlan digests, generated artifact manifest, checked transport, input binding,
state/persistence, checked launch, capability provider and trace/provenance profiles.
Its schema descriptor is saved as `R5_39-aggregate-profile-schema.json`.
Compatibility is checked before generation; the actual aggregate is sealed after
generation. Launch validates linked identities before touching state or invoking
transport. Integrity hashes establish revision consistency, not hostile-writer
attestation. The aggregate is infrastructure metadata, never semantic source.

`verify_boundary_r5_39` independently reconstructs public binding and persistence
expectations from observed bytes and checked metadata. It returns separate
`APPLICATION_PROFILE`, `LAUNCH`, `TRANSPORT`, `INPUT_BINDING`, `STATE/PERSISTENCE`,
`SEMANTIC_EXECUTION`, `OUTPUT` verdicts. `null` verdicts mean the layer was not
reached, not a pass. Semantic grounding uses the existing current-pipeline verifier.

## Whole-contract readiness v2

`readiness_r5_39.inspect` collects semantic and boundary findings in one pass;
it never generates or executes. It retains v1's exact operand/domain scans and
replaces boundary capability tables with nullable decoding and checked alternative
composition. It checks every plan's input mapping, route/output mapping, state
codec, persistence policy, launch/provider and aggregate compatibility. Supplied
content obligations require typed constraint coverage references, not a blanket
"content validation supported" label.

The original 84 cells remain intact: 64 supported, 20 rejected. The 336-row
extension retains each exact cell under single-provider, equivalent-duplicate,
independent-required and conflicting-provider dimensions. Independent-required
means both original presence/non-nullness where applicable; it does not imply a
second independent fact in a required non-null domain. Opposite typed-null
premises exercise conflict only where nullable refinement is applicable. Boundary
dimensions are linked to separate independent profile/binding/persistence evidence;
matrix static status is not itself a public execution claim.

An absent profile is NOT_READY even when the capability exists. Readiness cannot
infer omitted natural-language obligations or authorize frozen generation. Only
the single locked static B02 pass is permitted in this review; B02 generation,
execution and frozen acceptance remain prohibited.
