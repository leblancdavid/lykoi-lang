# R5.75 — Actual one-shot held-out B02 static experiment

## Result and permanent exposure boundary

**Final classification: `R5_75_OBSERVATION_INDETERMINATE`.**

The actual experiment issued **one ACTUAL_HELD_OUT authorization**, reserved
**one opening**, opened the complete committed resource set **once**, verified
**all eleven commitments and both frozen pins**, recorded **`B02_EXPOSED`**, and
dispatched **one whole-contract static observation** through the unchanged
R5.74-qualified runner. The experiment-bound callback failed with
**`KeyError: 'obligations'`** while extracting the frozen obligation document,
before invoking the existing CheckedPlan/readiness/audit/admission consumers.
Observation completions are **zero**. The durable ledger remains **incomplete**.

**B02 is permanently exposed and must never again be described as unseen.**
The complete-contract support question remains **undetermined**. This failed
observation establishes neither static support nor a language capability gap.
No repair, retry, second dispatch, generation, application execution or frozen
acceptance follows. Core semantics remain **30**. R5.75 stops.

## Evidence and inherited R5.74 state

- [Structured experiment controller](r5_75_experiment.py), unchanged after issuance.
- [Final pre-exposure verification](R5_75-evidence/preexposure.json).
- [CurrentState](R5_75-evidence/state.json),
  [ExperimentFreeze](R5_75-evidence/freeze.json), and
  [all eleven sealed commitments](R5_75-evidence/commitment.json).
- [Preauthorization callback/source binding](R5_75-evidence/callback-binding.json).
- [Actual authorization](R5_75-evidence/authorization.json).
- [Durable ledger](R5_75-evidence/actual-ledger/00.json):
  [reservation](R5_75-evidence/actual-ledger/01.json),
  [opening consumed](R5_75-evidence/actual-ledger/02.json),
  [dispatch](R5_75-evidence/actual-ledger/03.json).
- [Opening commitment verification](R5_75-evidence/opening-verification.json) and
  [permanent first exposure](R5_75-evidence/exposure.json).
- [Decoded documents captured during the single dispatch](R5_75-evidence/opened-static-documents.json).
  These are preserved evidence, not permission to resume analysis.
- [Terminal failure](R5_75-evidence/terminal.json).
- [Read-only stopped auditor](r5_75_stopped_audit.py),
  [stopped integrity](R5_75-evidence/stopped-integrity.json), and
  [final publication/integrity audit](R5_75-evidence/post-report-audit.json).

Inherited classification is **`R5_74_ACTUAL_HELDOUT_PATH_QUALIFIED`** within
cooperative Tier 2. R5.73 remains historically **`R5_73_PREEXPOSURE_HALT`**.
R5.74's fake actual-mode observation is separate from this actual B02 experiment.
Its preserved health evidence reports runner **74/74**, compiler/application
**31/31**, generic support **157 PASS**, **36 metadata-only prohibited skips**,
coherence **16 profiles / 84 rows**, schema/traceability **99 leaves**, and
validation, safety, contamination, AI independence and safe exclusion PASS.
These results were inherited and identity/linkage-verified, not rerun after exposure.

## Final pre-exposure verification

The repository was clean before preparing R5.75 artifacts. All prerequisites
passed without protected content access:

| Identity or prerequisite | Verified result |
| --- | --- |
| CurrentState | `2700b811ad5914eeea6c2da47fb4f200a56e6da3b26d73111e8d4d77af9adf77` — exact R5.74 match |
| ExperimentFreeze | `39f257b3793443a773388e1286f9cc0a045700b644d43a9dd9b44ca012e7b5c9` — clean, zero observations, actual ledger bound before authorization |
| GenericHealthCheck | `9f5d96c3ce405eb9339fe45447cb2f72772d92ab87a6fd451677c15a258dd0a8` — all eight inherited stages linked to CurrentState |
| B02 commitment identity | `e9a84957429452ed56138c181143294f9236b86518646346e14f2415cd93c692` — explicit pre-existing trusted actual-held-out authority |
| Runner source | `565eca10de31acc0c864a96ba4054005e4140d0456560420a38b1b12ef7cb761` — unchanged |
| Worker source | `2f662dd9f35ff58eb6b64a4f3ae37d968b710c9d11b73ee3022444378df206e2` — unchanged |
| Sealed resource metadata | 11/11 closed commitments, provenance and Git mappings verified without blob-content reads |
| Frozen request pin | `8a76e276240fa840c473be60a8e7ed0e10bd0c165426b1bfc84741e69872032b` |
| Frozen profile pin | `46ff02e3ff6ea48a7990c2f522fb9fa7bbefcab3c88550be007e0c2c1b75972f` |
| Contamination / semantic count | Inherited state-bound clean evidence / 30 |
| Actual ledgers | New R5.75 ledger and three inherited actual B02 ledgers empty |
| Pre-exposure B02 accounting | Attempts, content reads, authorizations, reservations, openings, dispatches and completions all zero |

The pinned module entry point ran via structured arguments:

```text
python -B -S -m benchmark.evaluation.phase5_runner_v2 preflight
  --mode ACTUAL_HELD_OUT --trusted-identity <trusted B02 identity>
  --freeze <R5.75 freeze> --commitment <R5.75 commitment>
  --state <unchanged R5.74 state> --ledger <R5.75 actual-ledger>
```

The exact argv and successful output are in pre-exposure evidence. No inline
Python source or R5.73 quoting pattern was used. Immediately before issuance,
the controller rechecked state, commitment, health linkage and empty-ledger
authorization predicates. Its completed callback source was separately pinned
before issuance at `22f5f4c4b7f8026d79202a7e9e3d964ec1b76db93b00bb1b927fdd067fbe9de5`.
The controller was completed before authorization; no post-exposure edit followed.

## Authorization, opening and exposure

The shared issuer persisted `AUTHORIZED` before the grant artifact and before
opening. The grant binds the experiment, trusted B02 identity and prefrozen
durable ledger to **`WHOLE_CONTRACT_STATIC_SUPPORT_OBSERVATION`**. Generation,
execution, acceptance and repair are explicitly false.

The unchanged `observe` path durably persisted `OPENING_RESERVED` before its
opener. The opener read precisely the eleven precommitted resources, each once.
Their pre-existing representation is UTF-8 LF text; CRLF checkout representation
was converted to LF according to that already-declared identity rule, before
comparison, without mismatch-driven substitution. Each resource was immediately
checked against its trusted SHA-256. The two frozen pins matched. Opening
verification and `B02_EXPOSED` were persisted before static dispatch. The runner
also verified the exact resource set and all digests before `DISPATCHED`.

No protected test module was imported or executed. Its committed bytes were
included in the single authorized opening and commitment verification.

## Whole-contract dispatch and precise failure

The sole callback decoded the opened frozen static documents together and
selected the latest precommitted semantic application and complete profile
configuration. Before calling any static support API, it attempted to extract
the obligation list with the following frozen callback expression:

```python
obligations = (obligation_document['obligations'] if isinstance(obligation_document, dict)
               else obligation_document)
```

This raised **`KeyError: 'obligations'`**. The callback assumed an envelope shape
that did not provide that key. No fallback extraction, changed evaluator,
resource substitution, exploratory clause analysis or repeated invocation followed.
The terminal artifact preserves the exact exception. This is an incomplete
experiment-controller observation, not evidence that B02 requires semantic #31
or that the existing generic support machinery rejected a behavioral requirement.

| Required support evidence | Actual observation |
| --- | --- |
| Total frozen behavioral requirements / contracts | NOT_DETERMINED before interruption; no invented denominator |
| CheckedPlans attempted / formed / rejected | 0 / 0 / 0; static consumers were not reached |
| Rejection reasons | No CheckedPlan rejection; callback failed extracting the obligation envelope |
| Compatibility relationships | NOT_EVALUATED |
| Readiness | NOT_EVALUATED |
| Static support / audit | NOT_EVALUATED |
| Admission / compatible-path assessment | NOT_EVALUATED |
| Whole-contract aggregation | NOT_EVALUATED |
| Support-view disagreement | NOT_OBSERVED |
| Unsupported behavioral requirements | NOT_IDENTIFIED; failure is not a behavioral gap finding |
| Whole-contract result | INDETERMINATE, neither PASS nor capability FAIL |

The missing support views and denominator are limitations of this stopped
attempt. Decoded evidence was preserved during dispatch; it was not used to
finish the observation afterward. No completion was manufactured.

## Accounting, post-verification and replay prevention

| Actual B02 accounting | Before exposure | Final |
| --- | ---: | ---: |
| Authorization | 0 | 1 |
| Opening reservation | 0 | 1 |
| Whole-set opening | 0 | 1 |
| Protected resource read attempts / content reads | 0 / 0 | 11 / 11 |
| Permanent exposure event | 0 | 1 |
| Whole-contract observation dispatch | 0 | 1 |
| Observation completion | 0 | **0** |
| Generation / execution / frozen acceptance | 0 / 0 / 0 | 0 / 0 / 0 |
| Semantic / profile / compiler / evaluator / runner repair | 0 | 0 |
| Core semantics | 30 | 30 |

The durable hash-linked ledger ends:

`AUTHORIZED → OPENING_RESERVED → OPENING_CONSUMED → DISPATCHED`

The terminal handler captured unchanged CurrentState immediately after the
exception. A separate read-only stopped audit verified unchanged CurrentState,
runner, semantic count, callback/source binding, commitment relationship,
canonical evidence identities, grant binding and the four-event ledger.
**Stopped integrity PASS** does not establish completed-observation post-check
PASS. The qualified completion post-check is inapplicable: there is no
`COMPLETED` event and no completed result. No relevant state drift was found.

Replay prevention was verified through ledger and frozen control inspection:

- A second authorization requires `ledger.status() == 'zero'`; the actual
  ledger is `incomplete`, so issuance rejects.
- A second opening or observation requires `len(events) == 1` before reaching
  the opener; the ledger has four events, so both reject before access/dispatch.
- No rejection-demonstration grant, opening or observation call was made.

The stopped audit made **zero protected read attempts**. Final read-only
publication/evidence integrity and `git diff --check` passed. No generic or B02
application test was run after exposure.

## Recommendation and absolute stop

**Preserve `R5_75_OBSERVATION_INDETERMINATE` and stop.** B02's first actual
exposure has been consumed. Do not repair or resume this controller, replay this
ledger, probe the captured B02 documents to finish the result, or classify B02
static support from inherited generic health. Generation/execution/acceptance
remain unauthorized; this round provides no basis to advance to that gate.

If separately authorized in the future, investigate generic frozen-document
envelope handling and complete observation orchestration using **non-B02**
examples first. This recommendation authorizes no further experiment, no B02
retry and no semantic addition. Phase 5C remains paused. Earlier classifications
retain their historical scope.
