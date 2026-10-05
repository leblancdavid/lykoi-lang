# R5.73 — One-shot held-out B02 static support-transfer experiment

## Result

**`R5_73_PREEXPOSURE_HALT`**. B02 remains sealed and unexposed.

The question was:

> Does the frozen current Lykoi system, using its existing 30 core semantics and
> current generic support machinery, statically support the complete frozen B02
> behavioral contract on its first authorized post-repair exposure?

**Answer: not observed.** No authorized opening or static observation occurred.
This halt establishes neither support nor a semantic, composition, profile or
support-coherence gap. Generation, execution and frozen acceptance remain untested.

Evidence: [stopped record](R5_73-stopped-evidence.json),
[stopped-state auditor](r5_73_stopped_audit.py), and
[post-report audit](R5_73-post-report-audit.json).

## Inherited state and pre-exposure halt

R5.72 remains `R5_72_SIMPLIFIED_PHASE5_RUNNER_QUALIFIED` within cooperative Tier 2.
Its two core modules, one authorization layer and synthetic lifecycle are unchanged.
The accumulated R5.39–R5.71 framework remains historical research evidence.

Source inspection found a concrete prerequisite blocker in the frozen runner:

- `phase5_runner_v2.authorize_synthetic`, line 317, requires commitment kind
  `synthetic` and resource names beginning `synthetic:`. Actual B02 rejects with
  `R5_72_PROTOCOL_HALT: actual benchmark authorization prohibited` before an
  AUTHORIZED ledger event can be written.
- `phase5_runner_v2.observe`, line 332, independently requires `synthetic-only`
  grant scope, synthetic commitment kind and synthetic resource names before
  reservation or opening.
- Its operation is `static-whole-contract`; no actual B02 issuer/consumer for
  `WHOLE_CONTRACT_STATIC_SUPPORT_OBSERVATION` exists in that frozen module.

R5.72's report explicitly preserved this restriction and deferred actual B02
authorization and the real adapter. Owner authorization of this research task
does not change the frozen predicates. No alternate grant, synthetic relabeling,
manual ledger transition, direct protected read or changed runner was used.

The first pre-exposure verification invocation was a `python -B -S -c` command.
PowerShell/Python quoting produced `SyntaxError: unexpected character after line
continuation character`, before imports or checks executed. The command is retained
in the session tool transcript. It is a failed invocation, not successful preflight.
No retry of that invocation or experimental lifecycle followed. The experiment
stopped before authorization; the synthetic-only blocker independently prevents
the requested lifecycle on the unchanged frozen runner.

## Read-only stopped-state verification

The separately scoped stopped auditor cannot authorize, open, dispatch or evaluate
B02. It imports only the qualified runner and verifies public evidence and metadata
under its protected-resource Boundary. Its checks document the halted state;
they do not resume the experiment or promote the failed preflight.

| Identity | SHA-256 |
| --- | --- |
| CurrentState, inherited and stopped recapture | `26bab617ad50b153e61ff19e5bebe6a1eca01881970f74e952b7197426a07530` |
| ExperimentFreeze | `7e5dddc941b99e476d03b5351d4aeb246964946ebea294bf5f12886416a17d4e` |
| GenericHealthCheck | `6070e033f2d8e002decc0f6ad9743600ebbcac58210529622fd20446ffc3bf8c` |
| FrozenBenchmarkCommitment | `9fea81142d3f4da1902aa2580d2951414939539d279288d31560ad16f7b4cea3` |
| Runner | `9007b4068efca1e21a83269c5ee1af04e9bb582656bd2352d4939de0dc05f3ac` |
| Worker | `2f662dd9f35ff58eb6b64a4f3ae37d968b710c9d11b73ee3022444378df206e2` |

All 11 sealed commitment metadata/provenance relationships and both frozen pins
revalidate without content reads. The pins are:

| Frozen resource | Trusted SHA-256 commitment |
| --- | --- |
| Request | `8a76e276240fa840c473be60a8e7ed0e10bd0c165426b1bfc84741e69872032b` |
| Profile | `46ff02e3ff6ea48a7990c2f522fb9fa7bbefcab3c88550be007e0c2c1b75972f` |

Inherited health evidence is canonically reloaded, hash/linkage checked and bound
to the unchanged recaptured state. It records application/compiler 31/31, generic
support 157/157, runner 30/30, 16-profile/84-row coherence, schema/99-leaf traceability,
clean contamination, validation/safety, offline AI independence and safe pre-import
exclusion with 36 metadata-only prohibited skips. **These are inherited R5.72
results, not newly executed R5.73 health suites.** The independent qualification
summary, its artifact pins and post-report PASS relationship also revalidate.

## Required lifecycle and support evidence

| Item | R5.73 record |
| --- | --- |
| One-time authorization | NOT_ISSUED |
| Opening reservation / seal opening | NOT_RUN / NOT_RUN |
| Commitment verification after opening | NOT_RUN; metadata-only verification passes |
| First B02 exposure event | NONE |
| Whole-contract static dispatch / completion | NOT_RUN / NOT_RUN |
| Complete frozen behavioral contract count | UNKNOWN; contract remains unopened |
| CheckedPlans formed / rejected and rejection reasons | NOT_EVALUATED |
| Compatibility relationships / compatible whole-contract path | NOT_EVALUATED |
| Readiness / static audit / admission / support coherence | NOT_EVALUATED |
| Whole-contract support / unsupported requirements | NOT_EVALUATED |
| Post-observation check | NOT_RUN; no observation exists |
| Stopped post-state / runner verification | PASS; unchanged identities |
| No-repair confirmation / final semantic count | PASS / 30 |
| Replay-prevention state | Empty durable actual ledger; no grant; actual path rejects before reservation |
| Second authorization/opening/observation probe | NOT_RUN; no actual-path probe or replay performed |

No contract counts or rejection counts are inferred from unopened resources.
Generic health coherence is not substituted for B02 support coherence. Static
success and static failure classifications remain unavailable.

## Accounting and stop

The existing R5.72 actual ledger remains empty. Stopped evidence is written outside
that ledger; no historical ledger is reset or modified.

| Actual B02 counter | Before | After |
| --- | ---: | ---: |
| Read attempts / content reads | 0 / 0 | 0 / 0 |
| Authorizations | 0 | 0 |
| Opening reservations / openings / exposures | 0 / 0 / 0 | 0 / 0 / 0 |
| Observation dispatches / completions | 0 / 0 | 0 / 0 |
| Generation / execution / frozen acceptance | 0 / 0 / 0 | 0 / 0 / 0 |
| Repair | 0 | 0 |
| Core semantics | 30 | 30 |

The stopped auditor and final publication audit each observe zero protected read
attempts. No repair or retry occurred. R5.72 frozen state and evidence remain
unchanged; new files contain only stopped research evidence and documentation.

Successful stopped-evidence commands:

```powershell
python -B -S benchmark/results/phase5c/r5_73_stopped_audit.py record
python -B -S benchmark/results/phase5c/r5_73_stopped_audit.py final
git diff --check
```

Final classification: **`R5_73_PREEXPOSURE_HALT`**. R5.73 is terminal.

## Recommendation for the next research gate

Separately authorize adjudication of the frozen synthetic-only actual-path blocker
and the preflight invocation failure using non-B02 examples. Any proposed actual
authorization/opening adapter needs an explicit prospective scope and qualification;
it must not be introduced into this halted experiment. Preserve the two-module,
single-layer boundary rather than restore the retired framework. Keep B02 sealed.

A new actual static experiment requires separate owner authorization and a qualified
actual path. Do not proceed to B02 generation/execution/frozen acceptance on this
unobserved result. Observable required behavior remains the authority, with core
semantics 30 and no implementation-structure equivalence requirement.
