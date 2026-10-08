## Primary integers, presence and migration

Each integer declaration specifies a fresh field name, `{type:integer,domain:[],
nullable:boolean}`, creation source and a separate list of historical migrations.
The domain is exactly signed-64 mathematical integers, serialized as JSON integers.
Booleans, floats, strings and values outside [-2^63,2^63-1] reject. Python arbitrary
precision is not language authority. Null is admitted only by explicit nullability.

Creation sources are typed literal, required input, or input with an explicit
omission default. CLI integer inputs use the existing JSON adapter. Explicit null
is a supplied value, not omission. Optional mutation omission preserves the old
field; supplied null replaces only a nullable field. The default applies only
at creation. Historical introductions declare exact version boundary and value;
missing migration authority is rejected, never inferred from the default.

Existing typed replacement/literal mutation, reference-operation computation,
checked addition, primary persistence/reload and typed equality/order/null queries
consume these fields. Nonnullable integer arithmetic uses the unchanged R5.111
graph/domain/snapshot/overflow policies. A nullable value is not automatically
refined into an arithmetic operand: null-sensitive computation requires explicit
source-authorized refinement; this profile does not invent a null-as-zero rule.
Computed primary **mutation** is supported; legacy primary creation does not gain
arbitrary computed assignments. Literal/runtime primary creation is supported.

## UTC-day conversion analysis and admitted representation

An absolute date and an elapsed day count are different types of authority.
An absolute Gregorian UTC calendar day `YYYY-MM-DD` can denote a K15 instant
only after the contract chooses its boundary. The admitted reference-parameter
adapter uses `encoding:utc_day`, timestamp target type, and an exact conversion:
`{source:gregorian_utc_day,target:instant,boundary:start_of_day,timezone:UTC,
precision:seconds,invalid:reject}`. It denotes `YYYY-MM-DDT00:00:00Z`.
Years 0001..9999, valid Gregorian dates and strict ASCII spelling are required.
Leap seconds, fractions, offsets, local zones and datetime spellings are rejected.
Invalid input uses the declared parameter error before any dependent effect.
This is a source-authorized representation of an existing instant, not K25
displacement. There is no reverse conversion or arbitrary timezone conversion.


## Primary actor context

`context_inputs` declares command, parameter name, nominal actor identity type,
`role:actor`, `authority:explicit_parameter`, and missing/invalid errors.
It adds an explicit context input to an existing primary write operation and its
normal semantic/external parameter contract. Host and CLI paths reject missing
or malformed actors. Coupled effects inherit that parameter by name and nominal
type. Existence is a separately declared ordinary reference policy; commit-time
integrity rejects unknown actors and preserves the entire private candidate.

An explicit actor parameter is not proof of authentication. Authenticated/request
actors, owners, referenced entities and supplied actors cannot substitute for each
other. This adapter implements only explicit supplied actor authority. It supplies
no ambient user, owner fallback, system default, role migration or authorization
decision. Entity-role/permission policies remain ordinary source obligations.

## Primary history and same-primary successors

R5.110's success-only atomic operation may create ordinary records of the primary
entity type as well as related types. Each creation has complete typed bindings,
explicit duplicate error and field provenance: literal, parameter, primary
before/after image, computed graph result or declared clock/identity resource.
Before/after keys retain nominal source-record identity. No implicit clone,
defaults, lifecycle reset or provider resampling is added. Every copied, reset
or fresh successor field must be declared. Complete primary validation and
reference integrity run against the candidate containing all creations.

History uses ordinary append-only durable entity schemas. A declared graph binds
pre-operation selection cardinality, then adds an explicit ordinal offset.
The selection sees the before store, never a secondary append prefix. One-row
append-only histories starting empty can use cardinality + 1; multiple creations
must declare distinct offsets and authorized domains. This is not imported max+1,
distributed sequence allocation or deletion-resistant ordinality. Private primary
mutation, history and successor publish with one existing atomic store replacement.
Typed, duplicate, overflow, integrity and persistence failures discard all writes.
Cooperating CLI reservation is inherited; no distributed/crash-recovery claim.
Conditional effect membership and secondary-created-image bindings are not added.
