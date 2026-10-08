# Kiln firing permits — base

Use COMMON.md. phase domain [cold, firing], initially cold.
vent domain [open, closed].
load domain [ordinary, emergency].
Command ignite: require phase=cold else invalid_transition, then
vent=open else gate_required; write phase=firing.
Behavioral invariant: phase=firing implies vent=open.
set_gate guard and create/list are exactly COMMON.md. No return transition yet.
