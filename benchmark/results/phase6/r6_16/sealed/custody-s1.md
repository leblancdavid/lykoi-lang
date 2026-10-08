# custody stage 1
Add unseal by id: missing not_found; require phase=sealed else
invalid_transition; write phase=unsealed. Preserve every other field and all
base behavior. This allows a cycle but does not bypass the gate requirement.
