# Lykoi atomic durable state composition 1 — R5.110

## Preserved pre-development kernel

The exact R5.109 proposed baseline is **23**. Its refined meanings are preserved:
K01 record schema; K02 field; K03 finite sequence; K04 typed binding (`var`);
K05 literal; K06 same-type equality; K07 conjunction; K08 complement (`not`);
K09 membership (`contains`); K10 selection; K11 trim; K12 finite pointwise map;
K13 stable-first uniqueness; K14 transition; K15 instant; K16 strict ordering
(`before`); K17 operation contract; K18 cardinality; K19 input presence;
K20 typed resource/capability authority; K21 durable state; K22 atomic commit;
K23 finite nonempty-path reachability. Identity remains a typed domain, not #24.
See the preserved R5.108 audit and R5.109 reference specification/accounting.

## Meaning and bounded representation

When an authorized operation commits, its primary candidate and a declared finite
sequence of ordinary typed record creations become visible in the same store
replacement. Failure in either candidate or persistence leaves the old store
unchanged. There is no independently observable intermediate effect.

Select `atomic_state_profile: atomic-durable-state-1` alongside the existing
mutable/input/predicate/reference profiles. The ordinary related entity schemas
and nominal identity/reference policies stay in `reference_semantics`.
The additional typed `atomic_state_semantics` facet declares `operations`,
`queries`, `append_only`, and `commit`. Commit is exactly `{scope:one_store,
mutation:bounded_records,isolation:exclusive_operation,rejection:unchanged}`.
This refines K22's frame, not a new Transaction, Event, Audit, Log or Effect core.

Each operation binds an existing primary mutation command, named entity and
explicit parameter types; `on:success`, `sampling:once_per_operation`, and
`ordering:declared_creation_occurrence` are required. One to eight creations
declare target entity, complete typed field bindings and duplicate identity
error. Bindings use existing typed literal, parameter, before-field, after-field
or declared resource values. Before/after fields have explicit names and types.
Delete has no after image; create has no before image. Ordinary related creates
and updates are also eligible as primary effects. No arbitrary update chain,
recursive effects, network operation or free-form JSON payload is supported.

Records have precisely the authorized fields. Subject, action, actor, time and
record ID are not invented defaults. Entity keys reuse ordinary nominal identity;
uniqueness and nonblank keys are validated. Repeated target creations have explicit
occurrence order; duplicate IDs reject the entire candidate. References are checked
against the complete candidate, permitting related creations to satisfy each other.

## Resources and failure frame

Resources explicitly name an existing UUID or UTC clock capability and its typed
value. Each capability is observed once per operation, including any primary
creation observation. A shared clock therefore supplies the same instant to the
primary creation and every secondary record. Distinct IDs need distinct declared
capabilities or supplied identities; silently resampling a shared ID is forbidden.
Host test providers bind only the operation's declared capabilities. Invalid
provider values reject before persistence. CLI defaults use only those capabilities.

Input/lookup/primary guard failures precede secondary construction. Primary
validation, secondary typed validation, duplicate-key failure, reference-integrity
failure and supported persistence failures all preserve bytes. A private candidate
is discarded on failure; one existing atomic file replacement publishes it.
The existing exclusive reservation covers cooperating CLI read/check/write.
Direct host API callers must cooperate with that reservation when concurrent.
No crash recovery, hostile writer isolation or distributed guarantee is claimed.

## Ordering, numeric sequence and append-only authority

Ordinary entity collections are finite sequences. Creation occurrence order is
stored and reloads unchanged. CollectionQuery supports explicit stable occurrence
order with `ordering:[]` only in this selected composition, or existing deterministic
lexicographic keys (including parsed timestamp plus ID). Record creation order can
be observable through history reads; internal primary/secondary evaluation order
is not observable before atomic commit.

Ordering is not a numeric sequence value. There is no `max(sequence)+1` backend
escape hatch. A monotonic ordinal can conceptually compose K18 cardinality of an
append-only candidate prefix, where the source authorizes that rule. The current
normal typed-value profile has no integer field/cardinality-value binding, so this
round does not execute numeric sequence generation. Exact successor of an arbitrary
stored counter/max needs arithmetic absent from the current kernel; whether a
particular contract requires that rule must be established separately. Neither
numeric generation nor B19 arithmetic is added here.

`append_only` names ordinary related entities whose exposed operations are read-only
and whose only write authority is coupled creation. Validation rejects standalone
create/update/delete on those entities. No immutable-record core is required.
Out-of-band file editing is outside the operation contract. Historical rows survive
primary deletion under an explicitly authorized unchecked/permit reference policy.
Migration initializes absent related state only from declared `initial:[]` and
creates no history entries; ordinary reads do not persist initialization.

## Queries, authority and loss detection

Queries are ordinary complete CollectionQuery models bound to an explicitly named
related collection, exact fields and unique key. Existing typed equality/AND/filter,
validation, result and read-only policies apply. Subject selection and action filters
are not a separate audit query language. Queries cannot change store bytes.

FRC distinguishes primary command, secondary field creation, atomic frame, occurrence
order, resource sampling, payload sources, query order and append-only restrictions.
Reconciliation compares these typed relations; complete structural recomputation and
faithful normal V1 recovery reject lost or changed facets. BDI exposes finite choices
for creation cardinality/content, success-only behavior, coupling, resources/order,
query selection and append-only operation authority. Missing material field/source/
sequence authority must remain a clarification or unsupported facet, not a convention.
Same-agent captures and source-side inventories are evidence limits.

## Kernel pressure and accounting

Typed history record/entity: K01–06/K21 composition. Coupled writes: K14/K17/K22
composition/profile extension. Occurrence ordering: K03; sorted history: K10/K16.
Clock/ID binding: K04/K15/K20. Append-only: restricted K17 operations. Query: existing
CollectionQuery composition. FRC/V1/BDI facets: composition/profile. Private candidate,
ContextVar resource cache and JSON envelope: backend-only concepts. Event, ordered
effect and transaction candidates add no missing observable meaning for this bounded
family. Numeric counter successor remains an excluded computation boundary.
**No new core candidate; post-R5.110 proposed count stays 23.**
