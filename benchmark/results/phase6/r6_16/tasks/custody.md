# Evidence custody seal registry — base

Use COMMON.md. phase domain [unsealed, sealed], initially unsealed.
witness domain [present, absent].
material domain [routine, fragile].
Command seal: require phase=unsealed else invalid_transition, then
witness=present else gate_required; write phase=sealed.
Behavioral invariant: phase=sealed implies witness=present.
set_gate guard and create/list are exactly COMMON.md. No return transition yet.
