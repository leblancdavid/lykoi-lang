# R6.46 scoped persistence contract

Authorized successor of R6.45; full list-format closure for explicitly declared
nonmigrating version-1 list storage. No new semantic meaning is introduced.

The declaration selects one existing state ID and specifies format=json_list,
schema_version=1, migrations=forbidden, invalid_state_error=invalid_state.
Installation must reject declarations that conflict with the lowered state version
or any declared migration. No declaration means no adapter. No application name,
field name, operation name or input value selects this profile.

At the existing same-read decode boundary, invoke the unchanged decoder. Only its
migration_required failure is translated to invalid_state. Independently require
the original parsed payload to be a list, including when the original decoder
accepts a version-1 envelope. All other failures retain their codes. Successful
lists continue through unchanged whole-store validation and operation execution.
The adapter performs no IO, mutation, migration or second read.

Authority: r6_16/tasks/COMMON.md:3–21 and stateful_modification_r6_44/CONTRACT.md:
6–14,23,33–58. Invalid store precedes lookup, ordered guards and mutation input
validation. Rejection/read preserves exact bytes or absence; writes remain atomic.

K01–K18 retain the R6.45 semantic expectations. Concrete fixture serialization is
UTF-8 JSON with indent=1 plus newline; missing storage is explicit absence. K06
is sequential list then cool, with a fresh subprocess per operation. K01/K11/K12
have multiple observations, so 18 rows comprise 25 observations. Expectations
are checked against source clauses before implementation, without candidate output.
This is same-agent source-based checking, not independent human review.

Regression checks reuse 188 frozen R6.44 modified observations prospectively,
without changing or rescoring R6.44. Existing production migration, unrelated
persistence, transition, invariant and runtime-authority tests are regression
controls. Unresolved V01–V04 remain unscored. Runtime/replay uses only Python,
local files and per-operation subprocesses, with no AI calls.

Preserve baseline and every attempt. Publish evidence and stop. Kernel remains26;
no P6-A04 acceptance, P6-A05 access, global decoder change or further experiment.
