# R5.41 — Prospective optional-boundary support

This infrastructure composition policy uses the existing **30** candidate core
semantics. It changes neither v0.3 nor frozen historical compiler/profile code.
The prospective entry is `application_boundary_r5_41.generate` (and `aggregate`
for static admission), with `readiness_r5_41.inspect`. The aggregate wire schema
and public launch compatibility filenames remain R5.39/R5.36; the admission
policy has its own R5.41 identity and sealed prospective runtime bytes.

## Meaning and public decoding

`optional<T>` means record membership may be absent; `nullable<T>` means the
present value may be null. Combined optional/nullable declarations preserve
three states: absent, present null, present non-null. Absence is handled by the
existing binder before decoding, not by a sentinel/default decoder.

Nullable composition intercepts permitted null and otherwise invokes the
underlying scalar decoder. R5.32 already implements that rule. R5.41 corrects
transport admission to ask whether the underlying decoder supports the declared
representation, rather than requiring JSON merely because nullable is a dict.
Text integer, string and instant decoders can therefore compose with nullable.
Boolean retains its JSON requirement. Records, nested nullable wrappers and
undeclared representations remain outside the bounded public decoder family.

Text always supplies a non-null representation: text `null` is a string, not
JSON null. An integer or instant decoder rejects it. A JSON profile supplies
explicit null with JSON `null`. No implicit null token or dual-representation
profile is introduced. Collection mode still requires JSON arrays; repeated
elements retain encounter order and use their declared scalar decoder.

## Durable constraints

Typed shape validation runs first. A finite population domain on an optional
field validates absence by the declared membership rule; a present value is
always checked against its underlying type and the finite domain, with exact
Python/JSON scalar type equality (Boolean is not integer). Explicit null must
be permitted by both the nullable type and the declared domain. Required fields,
nonblank constraints, identity uniqueness, state discriminators and unique
alternative matching retain their independent requirements. No defaults or
migrations are inferred.

Prospective public calls stage the generated operation on a private copy of
the effective pre-state. Post-state must decode to a declared compatible target
alternative before a generated attempted write can commit. An invalid post-state
returns the declared persistence failure and preserves the original durable bytes.
This bounded boundary enforcement is not a concurrency/crash-atomicity guarantee.

## Support coherence

`optional_support_r5_41` provides shared decoder-representation and typed
present-domain rules to admission, runtime and capability inspection.
`application_boundary_r5_41.support_report` validates the compatible path:
CheckedPlan → complete input mapping/decoder → compatible state alternative and
domain → transport/output/persistence policy → launch/provider → aggregate
identity/provenance. Readiness and the supplemental prospective audit consume
this assessment. Readiness additionally checks semantic lowering and declared
whole-contract obligations. The supplemental audit adds structural and
contamination checks, rather than implementing another capability model.

READY means the profile can handle its declared valid and invalid input paths;
it does not assert that every future supplied value is valid. Invalid text,
required omission and present out-of-domain values are dynamic rejections under
a supported profile. Unsupported composition is NOT_READY before generation.
An invalid declared initial state is likewise NOT_READY. No capability inventory
alone establishes support of a whole compatible path.

Historical R5.39/R5.40 readiness, audit and runtime remain reproducible. New
callers must select the prospective entry explicitly; no frozen benchmark retry
or ordinary Phase 5C execution is authorized by this policy.
