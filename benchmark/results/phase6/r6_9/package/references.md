## Behavioral meaning and nominal reference values

A field stores an identity naming an entity in a declared target domain. Observable
operations separately determine existence, failure, deletion and state conditions.
No database convention supplies any of these authorities.

The identity type is the existing `{type: identifier, domain: []}` refined with
`entity: User` (or another declared entity). `User` and `Project` identities are
different operand types even when both contain the same physical string. Literal,
parameter, lookup and write type bindings must agree exactly. Identity equality
is case-sensitive, unnormalized. Record identity is nonblank and unique, and
immutable after creation. A transport string is decoded in its explicitly bound
nominal input domain; a bare wire string does not carry independently recoverable
caller provenance. Substitution errors are rejected in typed source, not guessed
from indistinguishable external spellings.

A reference field composes a typed field, identity value and target entity type.
Single references store strings. Reference collections use existing finite
sequence element types, insertion order, `allow`/`unique` duplicates and exact
equality. Target metadata lives in FRC, normal V1 and generated semantic SPEC,
including after reload; storage need not repeat an entity tag for every value.
Primary historical scalar/string collection fields are refined by explicit
target authority; related nominal fields require a corresponding integrity policy.

## Existence and deletion, independently authorized

Each reference declares `existence: {policy: required|unchecked, error}` and
`deletion: {policy: restrict|permit|unavailable, error}`, plus `migration` (explicit or null).
`required` and `restrict` require nonempty declared error identities. `unchecked`
and `permit` require null error and affirmative source authority. `unavailable`
records a closed operation interface with no target deletion effect; validation
rejects it if any target delete is exposed. It supplies no invented deletion
behavior where deletion has no source authority. Omitted or
undefined policy/error refuses; formalizers must preserve missing observable
authority as a blocking clarification. No conventional `not_found` is invented.

Lowering publishes typed checks in structural facts:

* Each reference value: `cardinality(select(target, target.id == candidate_id)) == 1`.
* Restrictive deletion: `cardinality(select(source, source.ref == deleted_id)) == 0`.
* Collection reverse lookup substitutes exact scalar-IN-sequence membership.

Pointwise existence checking reuses finite traversal and selection/cardinality;
it is not a special foreign-key predicate. Restriction is evaluated on the
candidate state with the deleted record removed, so references removed by that
same authorized single-record deletion do not falsely block themselves. All
remaining referencing records, including archived ones, participate unless the
contract explicitly selects a different domain in a separate operation guard.

Existence is checked for every reference on a touched/create/update row immediately
before commit, including same-value replacement. Migration checks every reference.
An explicitly permitted target deletion may leave old values dangling; later
source writes still must satisfy their declared required existence condition.
No automatic cleanup/cascade or inferred target creation is implemented.

## Mutation and explicit multi-entity binding

Existing primary creation/resources, immutable identities and protected lifecycle
transitions remain in their qualified normal algebra. Related entity CRUD and
reference updates declare entity, parameters with nominal types/transport/errors,
lookup/missing error, changes, guards and result ordering. Related creation binds
all fields and declares duplicate-ID failure. Updates replace, append, add-unique
or remove existing typed values. Removal is stable selection of elements unequal
to the supplied value (all matching occurrences removed); other order preserved.
Unique append rejects rather than silently deduplicating. Add-unique preserves
the existing sequence and appends only when absent. No reference transform exists.

Operation bindings use `primary.field`; finite selection introduces a fresh
declared alias, e.g. `related.field`. Parameters have their own typed namespace.
No global entity lookup or unqualified field name is accepted. A selection cannot
shadow primary, and its predicate is a pure existing typed tree with both explicit
scopes. Existing primary guard amendments may consume these finite facts; lookup
failure keeps its existing precedence. Lifecycle fields cannot be ordinary writes.

## EXISTS, NONE, ALL and finite-domain scope

`extent` is the composition `cardinality(select(entity,binding,predicate))`
related to an exact nonnegative integer by `eq` or `ge`. It is a bounded
cardinality interface, not arithmetic or a public aggregate facility:

* EXISTS(P): extent(selected related domain AND P) ≥ 1.
* NONE(P): extent(selected related domain AND P) = 0.
* ALL(P): extent(selected related domain AND NOT P) = 0.
* Exactly N: extent(selected related domain AND P) = N.

ALL over empty selection is true. NONE and ALL differ on nonempty mixed-state
domains; EXISTS cannot substitute for ALL. The entity source plus an explicit
membership/equality domain predicate determines the exact finite domain. An
unrelated inactive member must not invalidate ALL over declared team members.
The existing selection/source semantics define this scope adequately; **finite
domain scope is a profile obligation, not an additional core concept**. Reference
existence is a separate condition; selecting no records for a stale identity
does not prove that identity exists. Related selection has no recursive/nested
query or general joins. Logical grouping and null-false predicate policies remain
those of the existing pure typed condition interpreter.


**Admit K23 as a proposed new core candidate: finite nonempty-path reachability.**
`reachable(entity, field, source, target, paths: nonempty)` is true iff a path of
one or more edges in the current explicitly named finite entity domain leads from
source to target. Field is a declared single/collection nominal self-reference;
both endpoints have that entity's identity type. Missing endpoints are false.
Edges to absent records do not traverse outside the domain. Scalar/collection
edge order and duplicates do not alter truth. Evaluation is deterministic and
terminates on finite state, including cyclic input. No path enumeration, shortest
path, weights, arbitrary graph algorithm or unrestricted recursive query is exposed.

For an added A→B edge, reject `A == B OR reachable(B,A)` before mutation. Self
equality is separate because empty paths are not reachable. Reachability uses
prewrite state; graph-validity of every preexisting imported edge is not silently
inferred. A candidate imported cyclic state can be inspected without nontermination;
cycle-rejecting additions reject precisely according to the declared guard.


## Commit, persistence, reload and migration

The composition binds the existing primary state and declared related entity
collections to **one coherent store**, retaining the existing path/schema/record
fields and adding an `entities` map. Absent related sections observe explicitly
declared initial rows; writes persist them. Initial rows are authorized semantic
constants, must remain present, and cannot be deleted or altered inadvertently.
Missing primary state remains empty; read-only commands do not create the store.

Each compiled CLI operation takes an exclusive operation reservation before
reading. A competing cooperating operation fails `store_busy`; it cannot mutate
against a stale check. Checks, related reads, primary or related single-record
candidate and one atomic file replacement share that reservation. Supported commit
failure leaves old bytes unchanged. This is K22 scope refinement over one store,
not database serializability, crash durability, distributed isolation or authority
for arbitrary multi-record writes. Writers bypassing the generated adapter and
stale reservations after process termination are outside that guarantee.

Primary migrations reuse declared additive steps. Optional reference migration
`{when: missing_or_empty, value}` is independent explicit authority to fill an
unowned field, with type/existence validation before any replacement. Nonempty
values are preserved and checked; invalid target rejection leaves storage unchanged
and adding the target can make retry succeed. Migration may update the authorized
historical record set; ordinary operations still mutate one record. Related reads,
entity CRUD and guarded effects do not authorize audit/event/successor semantics.
