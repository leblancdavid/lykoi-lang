# custody stage 2
Preserve stage 1 and base commands including ordinary start's gate requirement.
Add protect by id: missing not_found; first require phase=unsealed
else invalid_transition; then require witness=absent AND
material=fragile else exception_denied. Write phase=sealed
without changing the gate. Broaden the persisted invariant: active implies gate
allowed OR (gate blocked AND category special). set_gate blocked while active
must still reject gate_locked. unseal must work for exception-created states.
No base acceptance expectation is superseded; the corrupt-invariant base record
has category ordinary and remains invalid. New special active/blocked state is valid.
