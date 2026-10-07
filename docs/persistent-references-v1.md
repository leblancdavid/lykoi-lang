# Lykoi persistent reference compositions 1 — R5.109

Select `reference_profile: persistent-references-1` with the existing normal
`typed-mutable-values-1`, input and predicate profiles. The typed FRC facet
`reference_semantics` contains `primary`, `entities`, `references`, `operations`,
`guards`, and `commit`. This is a versioned composition interface, not a core
Relationship node. Normal FRC/reconciliation/coverage/BDI/adequacy/V1/authoring
and compiler dispatch preserve the facet and its recomputed executable meaning.

## Pre-round kernel, preserved exactly

The authoritative [R5.108 audit](semantic-kernel-audit-r5.108.md), sections 3–4,
proposes these **22**, at its stated architectural granularity:

| ID | Concept | ID | Concept |
| --- | --- | --- | --- |
| K01 | record schema | K12 | finite pointwise map |
| K02 | field | K13 | stable-first uniqueness |
| K03 | finite sequence | K14 | transition |
| K04 | typed binding (`var`) | K15 | instant |
| K05 | literal | K16 | strict ordering (`before`) |
| K06 | same-type equality | K17 | operation contract |
| K07 | conjunction | K18 | cardinality |
| K08 | complement (`not`) | K19 | input presence |
| K09 | membership (`contains`) | K20 | typed resource/capability authority |
| K10 | selection | K21 | durable state |
| K11 | trim | K22 | atomic commit |

These names retain the audit's refined meanings, not a replacement membership
list. Identity is already a typed domain under K01/K04/K06; no independently
counted identity primitive is introduced. Normal cardinality previously had only
specialized migration exposure; adding a related-selection interface is real
implementation work, not a new conceptual kernel member. The pre-round audit,
historical evidence and its exact file digest are preserved in the generic lock.

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

## Cycle pressure and explicit reachability candidate

Fixed-depth local equality/membership/selection/count expressions can observe
only a fixed number of reference steps. Pointwise map supplies no recursion,
worklist/fixpoint, accumulated visited set or transitive-path relation. An unroll
to depth k fails on a cycle formed through a chain longer than k; fixing a maximum
depth would change the behavioral contract. Backend-only search would hide the
missing meaning. Adding a generic recursive fold instead would itself expand the
kernel, with a substantially broader authorization/termination boundary.

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

Evidence includes independently observed reference additions/cycle rejection in
project-prerequisite and category-parent domains and 81-record paths/cyclic
termination probes. This is bounded multi-domain synthetic evidence, not proof
of universal irreducibility. The precise decomposition failure is absence of
transitive/fixpoint meaning in the current kernel, not difficulty writing Python.
No Relationship, ForeignKey, Graph or Quantifier core is admitted.

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

## Integration and kernel accounting

Reconciliation compares target types, complete existence/deletion/error authorities,
finite domains/predicates/count relations and reachability/cycle guards. Structural
coverage recomputes the entire IR and facets. Normal V1 retains the full source
contract and facts; recovery rejects material differences. BDI makes reference,
domain/guard, binding and commit choices explicit; adequacy refuses missing decision
authority. Same-agent source captures and synthetic owner seals are evidence limits.

| New construct | Classification | Kernel accounting |
| --- | --- | --- |
| Nominal entity identity / reference value / sequence | Existing-core refinement/composition K01–06/K09 | +0 |
| Existence and reverse restriction | Existing-core composition K10/K18/K17/K22, finite traversal | +0 |
| Selection extent and EXISTS/NONE/ALL | Existing-core composition K07–10/K18 | +0 |
| Explicit aliases / finite selected domain | Composition/profile K01/K04/K10 | +0 |
| Stable reference removal | Composition K03/K06/K08/K10/K14 | +0 |
| One-store read/check/single-record commit | K20–22 scope refinement/composition | +0 |
| Reachable nonempty finite path | **New core candidate K23** | **+1** |
| FRC facet / schemas / normal V1 / BDI | Composition/profile/analysis interface | +0 |
| JSON entities envelope / exclusive lock file / visited worklist | Backend-only implementation concepts | +0 |

**Proposed post-R5.109 kernel: 23 = exact inherited 22 + K23.** An architectural
proposal with bounded executable support, not a minimality proof. Generic tests,
six-domain external evidence and implementation/spec/test content lock precede
exposed-corpus transfer; implementation stays unchanged after any transfer outcome.
