# R6.46 scoped persistence integration

See the [report](../../benchmark/results/phase6/R6_46-REPORT.md),
[contract](CONTRACT.md), [runtime mapping](../../benchmark/results/phase6/r6_46/CONTRACT-TO-RUNTIME.md)
and [result](../../benchmark/results/phase6/r6_46/RESULT-v3.json).

`adapter.py` installs an explicit nonmigrating version1 JSON-list decode boundary.
`profile.json` attaches it to the exposed application's existing state.
`build.py` deterministically regenerates the preserved production-backed intent
and appends the integration. Production/compiler/kernel and historical artifacts
remain byte-identical. The corrected application is in
`benchmark/results/phase6/r6_46/build/application.py`; its exposed entrypoint is
`handle`, called by the unchanged R6.16 per-operation JSON transport.

Executed sequence: prepare → build → verify → resume unfinished regressions →
direct-runtime-control completion → publication. These scripts create immutable
evidence with exclusive writes; running them again against the published directory
is not a supported overwrite/replay command. AI-free repeat executions already
exist in MATRIX-REPLAY and KILN-REPLAY. No AI/model/network invocation occurs in
functional verification or replay.

The enclosing240-second orchestration interruption and three180-second full
workflow test timeouts are retained. A direct runtime-control import-path failure
and corrected invocation are both retained. No application candidate or expectation
repair occurred. Full workflow suites are not represented as passes;53 completed
scoped regression methods and188 accepted kiln observations are the completed
regression evidence.

Stopped after publication; further runs or architectural work need authorization.
