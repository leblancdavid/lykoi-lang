# R5.74 — Actual held-out authorization path qualification

## Result and boundary

**`R5_74_ACTUAL_HELDOUT_PATH_QUALIFIED`**, within cooperative R5.50 Tier-2
methodology. The prospective runner supports explicit actual-held-out authority
and qualifies its shared one-time observation path with a **non-B02 stand-in**.
R5.74 stops here. It does not authorize the actual B02 experiment.

**B02 structurally eligible for future held-out authorization: YES.** This is a
metadata-only result. B02 read attempts/content reads, grants, reservations,
openings, dispatches/completions, generation/execution/acceptance and repair all
remain zero. Core semantics remain **30**. CheckedPlans, readiness, static audit,
admission, compatibility and whole-contract B02 support remain **unobserved**.

Evidence:

- [Independent summary](R5_74-qualified-evidence/summary.json).
- [Fake actual-mode lifecycle](R5_74-qualified-evidence/fake-lifecycle.json),
  [authorization](R5_74-qualified-evidence/fake-authorization.json),
  [precommitted resource](R5_74-qualified-evidence/fake-contract.txt),
  [commitment](R5_74-qualified-evidence/fake-commitment.json) and
  [freeze](R5_74-qualified-evidence/fake-freeze.json).
- [Safe B02 metadata eligibility](R5_74-qualified-evidence/b02-metadata-eligibility.json).
- [Structured invocation](R5_74-qualified-evidence/invocation.json).
- [Qualification controller](r5_74_qualification.py),
  [independent read-only auditor](r5_74_readonly_audit.py) and
  [post-report audit](R5_74-qualified-evidence/post-report-audit.json).

## Inherited halt and root cause

Preserve **`R5_73_PREEXPOSURE_HALT`** and its original evidence. R5.73 is not
retried or retrospectively authorized. Its original frozen runner identity,
state/freeze records and historical ledgers remain research history; the current
source changes are prospective R5.74 changes, not an alteration of those records.

R5.72 qualified a synthetic lifecycle: `authorize_synthetic` required synthetic
commitments and `observe` independently required synthetic-only scope. Both
blocked actual B02 regardless of R5.73's separate preflight quoting SyntaxError.
R5.74 replaces the scope restriction prospectively and qualifies structured argv
invocation with fake resources. It makes no inference about B02 static support.

## Explicit authorization modes and trust

| Mode | Eligible authority | Issuance operation |
| --- | --- | --- |
| `SYNTHETIC_TEST` | Explicit synthetic classification and synthetic commitment kind; sealed resource set | `WHOLE_CONTRACT_STATIC_SUPPORT_OBSERVATION` only |
| `ACTUAL_HELD_OUT` | Explicit held-out authority classification, pre-existing trusted commitment identity, precommit status, closed seals, frozen authority pin(s), SHA-256 commitments and provenance | Same static operation only |

Mode is never inferred from filenames or resource IDs. Tests deliberately retain
`synthetic:` resource IDs in an **actual-mode fake commitment** to challenge name
inference. Actual B02 classification is derived prospectively by the pinned safe
metadata constructor, which verifies eleven trusted closed commitment/provenance
relationships and two frozen pins using policy/index metadata and Git object
types/mappings. It never obtains protected Git blob contents.

`authorize` requires an explicitly supplied trusted identity. This is a controller
trust input, not a certificate or a self-issued credential. An arbitrary self-sealed
candidate without the independently trusted identity rejects. The stand-in is
created and precommitted during preparation, before its ExperimentFreeze; actual
B02 eligibility uses already-safe pinned metadata. Eligibility itself issues no
grant and changes no ledger.

Actual-mode preflight additionally requires:

- A hash-valid `ExperimentFreeze`, clean repair state and zero frozen observations.
- Current state and runner identity matching that freeze.
- The exact commitment identity bound into that freeze.
- A durable ledger bound **before authorization** into the freeze and still empty.
- The exact static operation; generation, execution, acceptance and repair are false.

A new ledger directory cannot reset authorization under the same actual-mode
freeze. The legacy synthetic convenience function delegates to the same issuer;
synthetic behavior remains qualified and cannot authorize actual-mode authority.

## Shared observation enforcement

Both modes use the **same `observe` implementation**. It validates grant kind and
mode, authority eligibility, experiment/commitment/ledger bindings, static
operation and prohibitions before calling an opener. State capture and safe
metadata comparison precede opening reservation. Exact resource-set comparison
and SHA-256 verification precede dispatch. Safe result publication precedes
completion. Immediate post-check verifies state/runner, commitment and the complete
single-observation ledger.

The callback interface accepts no arbitrary path selection or generic file-access
grant. Openers/evaluators are experiment-controlled callbacks bound by the selected
source/state and commitment, within cooperative Tier 2. This is not a hostile-host
or malicious Python-callback sandbox. The qualification's protected-resource
Boundary remains active, including before worker imports. Any attempted actual B02
read would halt the run. Future actual evaluator/contract behavior remains untested.

## Fake actual-held-out lifecycle

The independently constructed `R5.74/non-B02-stand-in` uses one opaque resource,
`opaque:fake-resource`. Its file contains a generic sample-ordering static contract,
created independently for this qualification, without using B02 content.

1. Create the fake file and persist its commitment during preparation.
2. Complete fresh state-bound health; freeze that experiment with its empty ledger.
3. Confirm zero observations and run the pinned structured preflight.
4. Issue `ACTUAL_HELD_OUT` authorization bound to that fake commitment and ledger.
5. Persist `OPENING_RESERVED` before reading the fake file.
6. Open once, persist `OPENING_CONSUMED`, and verify the resource set and commitment.
7. Persist `DISPATCHED`; perform one static whole-contract callback.
8. Persist `COMPLETED`; post-check passes with one observation and clean state.
9. Reject replay and second authorization with no extra opening or callback.
10. Intentionally mutate the synthetic experiment's captured relevant subject state.
    Post-check rejects state drift. Append terminal `INVALIDATED`; another grant
    under the same freeze rejects. Actual Lykoi source/model is not repaired.

Opening/callback counts are **1/1**. The completion evidence remains preserved
after intentional repair invalidation; the final fake experiment is invalid,
as required. The independent auditor does not replay this lifecycle. Its file
hash check is a read-only integrity check of disposable fake content, not another
authorized opening, dispatch or static observation.

## Rejections and required tests

The runner suite passes **74/74**: the original thirty lifecycle/adversarial tests
run in synthetic mode; the same thirty run against fake actual-mode authority;
thirteen actual-mode-specific tests and one structured-invocation test complete
the suite. The inherited test name `test_complete_synthetic_lifecycle...` also
runs in `ActualModeTests` with its actual-mode setup and issuer.

| Required property | Observed verification |
| --- | --- |
| Existing synthetic behavior; shared enforcement | Same base thirty tests run in both modes |
| Fake actual authorization/opening/observation | Durable exactly-once success and separate qualification lifecycle |
| Frozen commitment, precommit, trusted identity | Missing frozen pins/precommit and wrong trusted identity reject |
| Frozen experiment, zero prior observation | Wrong freeze kind, nonzero count, dirty repair state and nonempty ledger reject |
| Synthetic authority → actual resource | Issuance rejects; synthetic-mode grant on actual authority rejects before opening |
| Actual authority → ordinary synthetic resource | Explicit mode eligibility/issuance rejects |
| Commitment A → B | Wrong commitment argument/metadata reject before opening; substituted bytes/missing resources reject before dispatch |
| Static grant → generation/execution/acceptance | Reject at issuance and at observation; zero openings/callbacks |
| Static authority → repair | Issuance rejects; post-observation state mutation invalidates |
| Replay/second grant | Reject after completion and after issuance, including reloaded/other ledgers |
| Incomplete opening/dispatch | Durable incomplete status; replay rejects; no retry/completion manufactured |
| Repair invalidation | Mutated captured subject state rejects post-check; terminal ledger invalidation and new-grant rejection |
| B02 structural eligibility | Real pinned metadata only; authorization function patched to fail if invoked in that test |
| No B02 grant/read | Protected Boundary, three empty actual ledgers, independent grant-artifact scan and zero worker attempts |
| Quoting-independent invocation | Both modes preflight through argv lists, including paths with spaces; no `-c`; actual-mode standalone controller invocation succeeds |

## Durable one-time accounting

One append-only exclusive-create event sequence remains:

`AUTHORIZED → OPENING_RESERVED → OPENING_CONSUMED → DISPATCHED → COMPLETED`

Each event occurs at most once. Hash-linked events bind the same frozen experiment.
Interruption after issuance/reservation/consumption/dispatch remains incomplete and
fail-closed. Repair adds terminal `INVALIDATED`. The actual-mode freeze binds the
ledger directory, preventing a different empty ledger from manufacturing a second
authorization. Durable directory retention and single-controller ownership are
part of the cooperative trust boundary; hostile deletion/ABA is not claimed.

## B02 structural eligibility without access

**YES**, on structural metadata only: eleven trusted sealed resources are present,
all commitments/provenance relationships verify, and the two frozen pins match.
The prospective metadata record explicitly classifies this authority as
`ACTUAL_HELD_OUT` and precommitted. No B02 ExperimentFreeze or authorization is
issued in this round. Neither the original actual ledger nor either R5.74 B02
ledger receives an event. The result establishes no static support or behavioral
acceptance property.

## Invocation and simplicity audit

Production-facing preflight is a checked-in entry point with structured arguments:

```text
python -B -S -m benchmark.evaluation.phase5_runner_v2 preflight
  --mode ACTUAL_HELD_OUT --trusted-identity <precommitted identity>
  --freeze <record> --commitment <record> --state <record> --ledger <directory>
```

The actual tested invocation is captured as an argv array in evidence. It performs
read-only preflight, not issuance. The pinned qualification controller then calls
the shared authorization/observation interfaces against the fake resource. This
qualifies the invocation shape synthetically without constructing quoted Python
source or adding an orchestration framework. R5.73's original SyntaxError persists.

| Simplicity measure | R5.74 |
| --- | --- |
| Core modules | **2**: runner and existing worker |
| Authorization layers | **1**: shared issuer; synthetic function is a convenience delegation |
| Persistent experiment artifact types | **6**: CurrentState, FrozenBenchmarkCommitment, GenericHealthCheck, ExperimentFreeze, OneTimeObservationAuthorization, ObservationLedger |
| Normal transitions | **5**, listed above |
| Terminal invalidation | **1** |
| Qualification support files | **3**: tests, controller, read-only auditor |

Mode and the actual-mode prefrozen ledger binding are fields in existing artifacts.
Source AST checks confirm the core imports no historical results/framework modules.
No certificate stack, authority successor, compatibility adapter or multigeneration
receipt system is introduced. Qualification evidence and the disposable contract
file do not create new runtime artifact types. **No simplification regression.**

## Fresh health and preserved failures

| Required check | Qualified candidate result |
| --- | --- |
| Runner | **74/74 PASS** |
| Compiler/application | **31/31 PASS** |
| Current generic semantic/support | **157 PASS**, **36 metadata-only prohibited skips**, zero failures/errors |
| Coherence | **16 profiles / 84 rows PASS** |
| Validation / safety | **PASS / PASS** |
| Schema / traceability | **PASS / 99 leaves PASS** |
| Contamination | **Clean**, seven current support implementation files |
| AI independence | Offline/site-disabled validation, deterministic lowering, safety and read-only execution; provider-import and development-mutation checks **PASS** |
| Safe B02 exclusion | **14 generic tests PASS / 36 prohibited skips**, exclusion before protected test import |
| Secret-safe publication | Canonical evidence, source AST-bound public-detection handling and concrete-credential rejection **PASS** in independent audit |
| Historical preservation | **2,347 ordinary result files** byte-preserved; **4 protected files** metadata-preserved |
| `git diff --check` | **PASS** |

No historical framework qualification is run. All eight successful health records
are fresh and bound to the same prospective CurrentState. The independent auditor
also verifies canonical hashes, freeze/health linkage, durable event sequence,
source/evidence pins and historical preservation.

R5.74 failures remain explicit:

1. [Development health failure](R5_74-development-failure.md): the first stripped
   worker could not locate Git for the new metadata-only eligibility test.
   Preserve its incomplete `R5_74-evidence/` and seven PASS stages. No freeze or
   lifecycle occurred. Prospectively declare the resolved Git metadata tool and
   restrict worker PATH to its directory; then prepare a fresh qualified candidate.
2. [Frozen controller publication failure](R5_74-publication-audit-failure.md): after
   the successful fake lifecycle, the original source-text audit rejects its own
   detection-marker concatenation. Preserve that command failure and frozen source.
   A separate read-only auditor qualifies evidence/publication with exact AST-role
   handling, independently rejecting concrete credential values. No lifecycle replay,
   runner repair or retrospective promotion of that failed command follows.
3. The first post-report publication command rejects a long hyphenated prose word
   because an internal substring matches the recognizable credential prefix rule.
   Correct the new report's prose and run the same read-only post-report audit.
   No frozen code, health, grant, lifecycle or observation changes. This documents
   a lexical publication false positive, not an actual credential finding.

These failures are orchestration/publication limitations, not B02 support results.
The final classification rests on the fresh health/lifecycle and independent audit.

| Qualified identity | SHA-256 |
| --- | --- |
| CurrentState | `2700b811ad5914eeea6c2da47fb4f200a56e6da3b26d73111e8d4d77af9adf77` |
| GenericHealthCheck | `9f5d96c3ce405eb9339fe45447cb2f72772d92ab87a6fd451677c15a258dd0a8` |
| Fake ExperimentFreeze | `79a0a2bc1add994b1f3a3a32897bcfef6eac34c241bc4b08c41384f6fbf7876d` |
| Prospective metadata-only B02 commitment | `e9a84957429452ed56138c181143294f9236b86518646346e14f2415cd93c692` |
| Runner source | `565eca10de31acc0c864a96ba4054005e4140d0456560420a38b1b12ef7cb761` |

The prospective B02 record's identity changes because explicit authority metadata
was added; original resource commitments, frozen pins and all R5.73 records remain
unchanged. This is not a successor-authority chain.

Successful qualified commands used the checked-in controller's `prepare`, eight
`health --stage <stage>` selections and `qualify`, then the independent auditor's
`audit` and `final`. The original controller's `audit` remains FAIL.

## B02 accounting and stop

| Actual B02 counter | Before | After |
| --- | ---: | ---: |
| Read attempts / content reads | 0 / 0 | 0 / 0 |
| Authorizations | 0 | 0 |
| Opening reservations / openings | 0 / 0 | 0 / 0 |
| Observation dispatches / completions | 0 / 0 | 0 / 0 |
| Generation / execution / frozen acceptance | 0 / 0 / 0 | 0 / 0 / 0 |
| Repair | 0 | 0 |
| Core semantics | 30 | 30 |

**Final classification: `R5_74_ACTUAL_HELDOUT_PATH_QUALIFIED`.** Actual-mode
mechanics are qualified on fake authority. R5.73 remains halted; B02 remains
unopened and its support question unobserved. A future actual experiment requires
separate owner authorization. Stop after R5.74; Phase 5C remains paused.
