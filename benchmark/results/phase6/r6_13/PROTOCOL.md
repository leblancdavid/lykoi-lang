# R6.13 scoring repair and frozen replay — protocol 1

Owner authorization: bounded R6.13 request. No candidate repairs or production/VM
changes. Provider-neutral Python standard library; no provider calls/dependencies.

1. Verify R6.12 freeze, publication, candidate and protected identities and record
   a byte-preservation map before successor scoring or new cases.
2. Scorer version `r6.13-scorer-1`: reject duplicate output keys at every depth;
   reject nonfinite JSON, malformed/trailing output, nonzero return codes, and
   exact type-preserving differences. Object order irrelevant, array order exact.
   Same externally observable rule for A/B/C. Input duplicate object keys and
   transport-invalid JSON remain outside the historical contracts; test duplicate
   domain IDs and malformed valid-JSON shapes instead. No expected-output changes.
3. Freeze acceptance version `r6.13-adversarial-1`, with explicit inputs, outputs,
   IDs and per-case rationale, plus scorer/candidate identities before execution.
   Expectations derived from contracts, not candidate executions. Exposure and
   correlated review are disclosed. Never regenerate expectations after scoring.
4. Run unchanged A snapshots: original suites, then adversarial suites. Modification
   snapshots also run the respective base suites; report repeats as repeats. B/C
   have no historical executable: record NOT_REACHED, never substitute a new probe
   for a frozen candidate. Record raw stdout/stderr, return code, actual/expected,
   timestamps, duration, candidate identity, timeout and scorer errors.
5. Separate newly authored small semantic probes from full acceptance. Preserve
   unsuccessful constructions. No host implementation of central behavior for B/C.
6. Publish finite outcomes, static/executed capability reassessment, validity limits
   and next experiment; stop and await separate authorization.

## Budgets and enforcement

No AI authoring trials occur. Historical per-task development allocation remains
900 seconds (original 4500/2700 session caps); those were partly retrospective and
are not retroactively enforced here. New per-task development budget is N/A, not
zero-second successful authoring. Tokens, authoring time and repair efficiency are
not remeasured. Prospective probe preparation/review is observational coordinator
work, not matched-success development telemetry.

Replay: **10 seconds per process** and **900 seconds per replay session**. UTC start
and completion plus monotonic durations recorded. subprocess.run(timeout=min(10,
remaining_session)) kills/waits for the direct child at timeout; the session loop
checks remaining time before every case, marks subsequent cases NOT_REACHED if
exhausted, and rejects completion beyond the session deadline. Classification is
PROCESS_TIMEOUT or SESSION_TIMEOUT, distinct from SCORER_ERROR and EXECUTION_ERROR.
No hard supervisor of coordinator publication, process creation, OS scheduling or
descendant processes: session cap is cooperative deadline enforcement for dispatch
and acceptance, not whole AI-session containment. Whole AI session budget unsupported
and observational. Child cleanup/deadline detection can overshoot wall limits; record
measured completion. Replay wall time is execution overhead, never development effort.

Qualification here means bounded scorer/replay validation, not independent task,
model, language or statistical qualification. Full-task B/C composition remains
uncertain unless an unchanged-language complete construction is actually demonstrated.
