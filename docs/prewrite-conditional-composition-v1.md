# Lykoi prewrite authorization and conditional effect composition 1 — R5.113

## Declared authority and identities

Select `authorization_profile: prewrite-authorization-1` with the existing typed
mutable/input/predicate/reference/atomic profiles. The closed FRC facet
`authorization_semantics` has `operations`. Each operation declares command,
entity, lookup (null for creation), exact typed parameters, actor binding,
permission predicate, declared error, `observation: committed_operation_before`
and `rejection: unchanged`. There is no implicit permission predicate or role.
An omitted material source permission fails reconciliation/coverage; an omitted
guard is not an authorization default. Read-only filters cannot substitute.
Optional ordered `checks` are existing typed `{predicate,error}` guards in the
same snapshot, before the final permission predicate. They permit declared actor
existence errors without turning unknown actors into filtering or forbidden errors.
Creation parameters inherit a nominal target only from their explicit creation
assignment to a declared persistent-reference field, never an arbitrary cast.

These meanings are distinct:

* **Actor identity**: the nominal identifier attributed to an operation.
* **Authenticated principal**: an identity established by an external trusted
  authenticator. This compiler and CLI establish none.
* **Actor role**: a field of the actor record in committed state, selected by
  an explicitly declared equality/membership predicate.
* **Record owner**: a separately declared nominal reference in the target's
  pre-operation record; on creation an explicitly supplied creation operand.
* **Permission predicate**: a typed condition over these declared operands.
* **Authorization decision**: accept or raise the declared permission error;
  this is never an ordinary empty selection result.

Existing finite selection/cardinality, exact nominal equality, member, AND/OR/NOT
and typed guard interpretation express role, owner and permitted-set policies.
No application role, owner command or permission engine is a core primitive.
Persisted current role, a historical role observation, an explicitly authorized
role migration and a new-entity role default are different authorities. New-user
defaults never supply missing historical role migration. B17's unanswered
non-system historical role is preserved.
Existing reference parameters may explicitly declare a typed omission `default`.
Only absence activates it; supplied null/invalid values follow their own type
validation. It adds no historical entity-field migration authority.
`present` retains the originally supplied parameter set after default binding;
a default value does not retroactively make an omitted input supplied.

## Trusted actor execution context

Actor declarations have `name,type,source,context,missing_error,invalid_error`.
`source: explicit_parameter`, `context: null` admits a source-authorized actor
**selector**, not an authenticated principal. A contract explicitly choosing this
source can evaluate role/owner permissions on that selector, but does not protect
against impersonation. It must not be described as authenticated authorization.
Reconciliation refuses substitution of a selector for a trusted source.

`source: trusted_context` names an explicitly authorized embedding source.
Generated host write entrypoints accept a separate `execution_context` argument
`{source: declared_context_name, actor: nominal_identity}`. The embedding is the
trust boundary and must supply this value through controlled code. A dictionary
is not a cryptographic credential, and arbitrary host-code execution is outside
the boundary. No context is read from CLI flags, environment variables, owner
state or ordinary parameters. A conflicting actor parameter or wrong context
source rejects. Controlled synthetic host processes exercise this adapter.
The CLI has no trustworthy authentication source and cannot execute a trusted
operation successfully by supplying `--actor`.

The model binds an actor asserted by that authorized host, without inferring an
authenticated principal, authentication status or actor-to-principal mapping.
Such mappings require external source authority and remain outside this profile.

## Observation, rejection and stale state

Permissions are checked before invoking existing primary/related writes, including
primary creation, against a private committed snapshot. Existing target-not-found
errors retain precedence when lookup is absent. Creation permissions have no
primary before image; only explicit inputs and finite related committed state.
At commit the current store and operation-before frame must equal the observed
snapshot and the predicate is checked again. A changed observation rejects using
the permission error. All declared failures leave primary, history, successor
and store bytes unchanged. Neither provider observation nor proposed primary
mutation is durable before the existing one-store replacement.

Cooperating CLI operations hold the inherited exclusive reservation. Trusted
hosts must coordinate operations; stale-state detection is not a distributed
transaction or a claim of general host-thread/crash isolation. The supported
atomicity frame is unchanged.

## Conditional effects and images

Select `effect_composition_profile: conditional-created-effects-1`. Existing
reference update changes may declare a typed `when` predicate evaluated against
the coherent pre-operation target/store/inputs; unselected assignments preserve
their field. Creation/deletion contracts do not gain partial required payloads.
Operation-level computation remains unconditional regardless of assignment selection.
Every creation in an extended
operation has unique `binding`, `when` (null means unconditional), exact
`depends_on`, ordinary entity, complete typed bindings and duplicate error.
One to eight creations remain bounded. Conditions use existing typed predicates
over the same operation-before store and primary before image (when available)
and explicit inputs. They cannot observe a candidate prefix, a proposed primary
after image, a newly created row or the committed post image.

Effects may have local `computations` with the existing bounded graph. They
execute only when selected, so a null/overflow in an unselected successor has
no effect. Operation-level computations remain unconditional. Local results
cannot shadow operation results. Resource observation remains declared
once-per-operation; unused declared resources may still be sampled.
Resource bindings may explicitly declare `observation: binding` for UUID identity
capabilities: each distinct named binding samples once, independently of other
names and the primary creation identity. `operation` retains shared capability
observation. Clock resources remain operation-shared. This is K20 observation
scope authority, not a new identity-generation primitive. Independent identities
are never obtained from implicit resampling or Python execution order.

The four images are explicitly distinct:

1. `before`: committed pre-operation target.
2. `after`: proposed primary image, not yet committed.
3. `created`: a named proposed secondary record (including same-entity successor).
4. committed post-operation store: exists only after the atomic replacement;
   it is not an admissible operand while constructing effects.

Created source shape is `{kind:created,type,effect,entity,field,alternative}`.
Entity, nominal identity and field type must match the named producer exactly.
Identity, computed values and other fields are ordinary explicit bindings, not
implicit clones. Dependencies are exactly the named images consumed. Missing
names, mismatched types/entities, self-reference and cycles reject. Graph build
order is derived from dependencies, even for a forward reference; durable
occurrence order stays the declaration order.

A conditional producer must be unconditional, have exactly the consumer's
condition, or supply an explicit typed literal alternative. General implication
proving and arbitrary imperative branching are not admitted. Unselected producers
have no image. The literal alternative means that declared value only when the
producer is unselected; it is not a hidden default. Selected rows and the primary
write are fully validated and commit together. Duplicate, computation, integrity,
stale-state and persistence failures discard the entire candidate.

The admitted frame is an existing primary operation, bounded conditional reference
update assignments and selected creations. Arbitrary lifecycle/legacy primary
instruction branching, partial required creation payloads and conditional deletion
are not admitted.

## Nullable numeric refinement

Select `duration_conversion_profile: elapsed-day-conversion-1` with computation.
`refine_integer` takes a nullable signed-64 integer and produces a nonnullable
integer. Its exact `null` policy is `{policy:reject}` or an independently
source-authorized `{policy:literal,value:integer}`. No implicit zero is admitted.

Absent required parameters use their parameter missing error. Omitted optional
creation inputs use only their independently authorized creation default.
Explicit null is supplied, not absent; selected refinement rejects it or uses
its explicit null policy. Valid signed-64 integers preserve value, including
negative and zero. Booleans, floats, strings and out-of-range integers reject
with the parameter/computation error. This is type/presence/guard/literal
composition, not a new arithmetic primitive. Unselected graphs do not refine.
`refine_instant` applies the same explicit null policy to an existing nullable
timestamp image before K25 consumption, producing a nonnullable instant. It
does not add temporal arithmetic or invent a due date; K25's UTC representation
and range rules still apply. This is the corresponding typed image binding seam.
Computed nonnullable values may flow into the identical nullable target domain;
source/result types remain exact and no null is introduced. The reverse direction,
different nominal entities or different units are rejected. This directional type
widening is required when a refined/displaced instant populates a nullable due field.

## Runtime elapsed-day conversion and kernel pressure

`days_to_seconds` consumes one nonnullable signed-64 integer and produces a
`duration` in seconds. Its exact conversion authority is:

```json
{"source":"elapsed_days","target":"elapsed_seconds","seconds_per_day":86400,
 "negative":"preserve","overflow":"reject"}
```

Mathematical meaning: `duration_seconds = day_count × 86400`, followed by signed-64
range validation. Zero remains zero and negative displacement remains negative;
positive-only application intervals require a separate declared predicate.
Overflow rejects unchanged. K25 then displaces a canonical UTC instant; year
0001..9999 bounds, leap-day behavior and UTC midnight remain inherited. No months,
years, daylight-saving or local-zone arithmetic is introduced.

The preserved K24 graph has at most 16 nodes. Each addition can at most double
the coefficient of N: even 16 addition nodes reach at most 65536N, below 86400N.
Literal constants do not increase that coefficient. A fixed
finite literal-duration enumeration cannot cover runtime signed-64 N, and K25
requires duration rather than integer dimension. No loop, unrestricted multiplication
or host coercion is licensed by the inherited semantics. Thus the exact new
dimensioned conversion relation is proposed **K26**, the smallest admitted
extension for this pressure: kernel **25 → 26**. This is explicit mathematical
meaning in validator, backend, closed producer schema and source-bound evidence;
the Python product is its implementation, not its authority.

Authorization, actor binding, conditional selection, effect graphs, created-image
bindings and nullable refinement compose K01–K22/K24/K25. They add no Policy,
AuthenticatedActor, Event, Audit or Recurrence core primitive. This is proposed
architectural accounting, not a proof of a minimal kernel.

## Normal-path fidelity and evidence boundary

Closed FRC facets retain actor source, predicate, error, observation, selection,
dependency images, conversion and null policy. Source-only inventory reconciliation
detects omissions/substitutions. Structural recomputation and faithful V1 recovery
compare exact facts; BDI records authorization, condition, effect dependency,
nullable/conversion and failure-frame decisions. Adequacy rejects missing authority.
The normal compiler dispatcher emits runtime support; generated Python is not edited.

Five synthetic domains exercise full pipelines and external subprocess persistence/
restart, primary creation rejection, wrong role/owner, conditional nonmembership,
forward created-image references, null rejection and signed conversion. Additional
controlled host probes cover forged selector, wrong trusted source, stale observation
and injected persistence failure. They use same-agent capture/inventory/oracles and
synthetic approval: finite development evidence, not held-out generalization.
