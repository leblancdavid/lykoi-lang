# Task selection and exposure

Four original synthetic contracts authored by coordinator after BASELINE.json.
Source authority is this R6.15 experiment, not externally authored issues or held-out
generalization. Prior R6.11/12 contracts read only for duplicate avoidance; historical
implementations not used as task sources. R6.13/14 findings and VM contract known.
Calibration, run expansion, ordered interval validation and bounded nesting differ
from all prior scored tasks; no CFG66/DSV66/BXC66/XOR8/addmod8/byte-parity reuse.
Ordinary sequencing/UInt8/select/check meanings overlap the VM vocabulary by design;
these tasks were not used to design or modify the frozen VM.

Selection favors byte-serializable small tasks and known bounded composition;
implementation-aware/nonrandom selection bias is substantial. Coordinator writes
both expectations and contracts; correlated mistakes possible. Author contexts get
only their base contracts, common interface and own track docs. Staged extensions
are coordinator-known but withheld from base authors by cooperative instructions;
shared filesystem does not provide a cryptographic access barrier. No superiority
or independence presumed. Freeze includes explicit oracle observations before authors.
