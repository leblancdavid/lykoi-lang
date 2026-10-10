# R6.46 integration decision

Use an explicit nonmigrating version1 JSON-list application adapter at the same-read
decode boundary. This is smaller than changing shared decoder semantics and does
not require a new construct. A state reference,shape,version,migration permission
and invalid-state code are declared; scope conflicts fail installation. No profile
means unchanged decoder identity. Record validation,guards,operations and writes
remain existing production meanings.

Do not infer migration-enabled policies from this application. A prospective typed
persistence-contract fact set carried through lowering is the recommended next
architecture question; clarify normal-read old/future version precedence first.
The exposed application passes its complete declared list contract and retained
behavior,with53 completed scoped regression methods. Additional full workflow
timeouts are retained and limit broader qualification. Further work needs explicit
authorization; stop after [publication](../benchmark/results/phase6/R6_46-REPORT.md).
