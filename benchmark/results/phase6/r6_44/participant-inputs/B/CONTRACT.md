# R6.44 kiln shared-policy modification

## Starting application

The exposed R6.16 stage-2 kiln application has create, list, ignite, set_gate,
cool and rescue. Each operation reloads records.json. Missing storage is empty.
Records have exactly id, created_at, label, phase, vent and load. id is a UUID-v4
and created_at a UTC timestamp; both come from supplied deterministic providers.
Label is a nonblank string retained verbatim. phase is cold/firing, vent is
open/closed, load is ordinary/emergency. IDs are unique. Creation starts cold.
Successful writes atomically replace the local store. Rejection preserves exact
store bytes or absence. List returns whole records ordered by created_at then id.
The persisted invariant is firing implies open vent OR emergency load.
No normalization, schema migration, concurrency or external effects are required.

Starting ignite requires cold (invalid_transition), then open vent
(gate_required); it changes only phase to firing. Starting set_gate rejects a
supplied closed value while firing (gate_locked), then rejects absent/invalid
value (invalid_input); otherwise it changes only vent. cool requires firing
(invalid_transition) and changes only phase to cold. rescue requires cold
(invalid_transition), then closed vent AND emergency load (exception_denied),
and changes only phase to firing. Lookup failure is not_found before guards.
Invalid whole-store state is invalid_state before lookup/guards/input validation.
Blank creation label is invalid_label. Duplicate provider ID is id_collision.
Creation inputs and providers otherwise conform to declared types.

## One in-place shared-policy change

Emergency loads are now exempt from the open-vent operating restriction in
ordinary ignition and subsequent gate changes, as they already are in the
persisted invariant and rescue pathway.

* ignite still first requires cold (invalid_transition). Its gate policy now
  allows an open vent OR emergency load; otherwise gate_required. Success sets
  only phase=firing, retaining the vent.
* set_gate rejects a supplied closed value while firing ONLY for ordinary loads
  (gate_locked). Emergency firing loads may close or retain a closed vent. The
  guard is before required-value/domain validation; missing or invalid values
  still yield invalid_input for either load.
* No other operation, field, domain, error code, order or invariant changes.
  rescue retains its narrower closed/emergency precondition. cool works on
  ordinary and emergency firing states, including closed emergency states.

Every operation validates the entire persisted store first; an invalid unrelated
record therefore wins over a missing ID, invalid mutation value or phase error.
Missing ID wins over all mutation guards/invalid values. For ignite, phase wins
over gate policy. For set_gate the lock guard wins when applicable; it does not
match missing, null, non-string or out-of-domain values. These then reject at
input validation. All guards observe original state.

## Old-store and retention requirements

Existing valid cold/closed and firing/closed/emergency records remain valid,
without rewrite on list or rejection. Existing firing/closed/ordinary records
remain invalid and are never repaired. Identity, timestamp, label, load and all
unselected records are unchanged by mutations. Test restart with a fresh process
per operation and sequential clients sharing one store. No new endpoint is a
substitute for changing ignite and set_gate.

Superseded observations: cold/closed/emergency ignite previously gate_required;
firing/emergency set_gate(closed) previously gate_locked. Every other original
observation must be retained. One trial, no acceptance-feedback repair.
