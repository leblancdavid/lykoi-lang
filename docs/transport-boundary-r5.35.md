# Lykoi checked transport/persistence boundary — R5.35

Prospective extension of [R5.34](checked-transport-r5.34.md), not a language
freeze or another compiler. The sole semantic entry remains
`benchmark.semantic.current_pipeline`. Candidate core constructs remain 30.
Historical R5.32–R5.34 implementations and evidence are retained unchanged.

## Checked collection binding

`checked_transport_r5_35.specification(plans)` derives public slot descriptors
from sealed CheckedPlan inputs. Each argument declares public name, semantic
slot, scalar element decoder, optional finite element domain, representation,
mode, omission policy and order policy. Supported sequence elements are string,
integer, instant and boolean; this uses existing `sequence<T>`, not a new type.

| Mode | Public representation | Membership/order |
| --- | --- | --- |
| single | one text or JSON flag/value pair | duplicate flag rejects |
| repeat | repeated text or JSON scalar flag/value pairs | encounter order and duplicates retained |
| collection | one JSON array flag/value pair | array order and duplicates retained |

The public parser only extracts raw wire values. Every supplied element invokes
the unchanged R5.32 scalar binder. Binding is all-or-failure; diagnostics identify
the malformed element index, and no partially decoded collection is invoked.
Normalization, nonblank conditions, deduplication and fallback remain generated
application behavior. `order=encounter` is required for sequences; sorting and
deduplicating transport modes are not implemented.

Omission is `omit` for optional fields and `required` otherwise, derived from the
plan. Optional omitted input stays absent. An explicit JSON `[]` is supplied and
typed, even though empty. Repeated flag syntax alone has no empty-collection
token; a profile can expose another collection-mode route to the same semantic
operation. No zero-repeat default is installed by transport.

## Checked public documents

Each exact checked outcome tag maps to a descriptor with `type`, public
`status` classification, `stream` (stdout/stderr), `exit` (integer 0–125), and
`presentation`. Public classification and process exit do not change the
semantic branch or tagged outcome. Normal semantic payloads are shape checked.

Presentations are bounded declarative structures:

- `{"mode":"direct"}` emits the typed payload directly.
- Object mode declares `coverage=full|selected` and a **list** of named fields.
  Each field is a checked constant, the string outcome kind, or a typed payload
  path through required record fields. Duplicate destination names reject.
  Unknown paths, optional projections and incompatible field types reject.
  Full coverage requires the whole payload or every required top-level field.

Example: an object with constant Boolean `ok` and whole payload `data` can expose
success as `{"ok":true,"data":...}`. A failure may instead project its checked
reason/code to `error`. No executable formatting hooks or templates exist.
Reserved outcome category names cannot be used as semantic outcome tags; object
field names have no implicit reservations beyond collision checking.

Boundary categories are transport failure, binding failure, missing persistence,
invalid persistence JSON, invalid persistence shape and generated invocation
rejection. Their checked public payload is `record<code:string>`. Internal
binding diagnostics remain in evidence. Complete category codes plus optional
per-public-argument category codes are metadata. Boundary presentation, stream
and exit are checked exactly like semantic output, but cannot masquerade as a
typed semantic event.

Output is exactly one JSON document and one trailing newline on the configured
stream; the other stream is empty. Multi-record/NDJSON/asynchronous streaming is
not implemented: the established readiness requirement calls for a document on
stdout or an error document on stderr, including arrays as single JSON values.
Integrity failure before profile loading uses the fixed stderr/exit-4 fallback.

## Checked persistence declarations

The separate state profile supplies the application's exact registered state
versions and named initial states: `name -> {version, value}`. Version names and
values are checked against application state types originating in CheckedPlans.
Initial state is explicit application/state metadata; it is never inferred from
an operation name, file format, field name or domain convention.

Persistence policy selects exactly one of:

- `REQUIRE_EXISTING`, with no initial reference. Missing store rejects before
  semantic invocation and creates no file.
- `INITIALIZE_DECLARED_STATE`, with a checked named initial reference. Missing
  store supplies that declared semantic pre-state in a disposable staging file.
  A generated read/preserve call leaves the physical store absent. If and only if
  generated execution succeeds and requests a write, its resulting bytes are
  materialized at the configured durable path.

This is lazy initialization, not eager creation. Existing stores are never
reinitialized. Invalid JSON or a value outside all registered state shapes is a
persistence-boundary failure. Operation-specific shape/version/applicability
rejection stays in generated invocation. Persistence policy cannot run migrations,
select a convenient version, compute defaults or alter transitions.

Physical absence is recorded as null bytes/digest, independently from effective
semantic pre-state. The verifier challenges declared initialization, byte
materialization, generated pre/post and output separately. Virtual read pre/post
do not imply that a physical store existed. Direct writes remain crash-nonatomic;
concurrent initialization, hostile runtime isolation and transactional guarantees
are not established.

## Authority and verdicts

Profile generation validates before artifact generation, delegates generation to
current_pipeline and seals the R5.34 dependencies plus the R5.35 runtime. Profiles
carry application/source/unit/generation identity and the checked state profile.
Stale generation rejects before state access; independent authority recomputes
expected metadata and detects incompatible resealed policy changes.

Public subprocess observations ground exact stdout/stderr/exit and physical
pre/post bytes. An independent raw accumulation and scalar decode oracle checks
binding. Semantic challenge uses the existing current pipeline and independently
derived effective pre-state. Verdicts are distinct:

`TRANSPORT_PROFILE_CONFORMANT`, `TRANSPORT_BINDING_CONFORMANT`,
`INPUT_BINDING_CONFORMANT`, `PERSISTENCE_BOUNDARY_CONFORMANT`,
`SEMANTIC_EXECUTION_CONFORMANT`, and `OUTPUT_CONFORMANT`.

Null is not applicable/evaluable, never a semantic success. Public corruption can
fail output while semantics and persistence pass.

## Remaining public launch boundary

The generic adapter still receives infrastructure state/trace/invocation paths
before public argv. There is no checked standalone public-only-argv bootstrap or
cwd-relative store selection declaration. A caller can supply infrastructure
paths, but that is not evidence that metadata alone produces a frozen-style
public executable. R5.35 closes its three implementation areas while retaining a
partial readiness gate for this post-lock descriptive finding. No implementation
repair follows the frozen-text comparison. See the
[R5.35 result](../benchmark/results/phase5c/R5_35-GENERIC-TRANSPORT-BOUNDARY-COMPLETION.md).
