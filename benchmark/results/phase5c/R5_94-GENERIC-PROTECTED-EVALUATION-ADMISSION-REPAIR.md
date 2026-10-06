# R5.94 — Generic Protected Evaluation Admission Repair

## Classification and stop

**`R5_94_GENERIC_PROTECTED_EVALUATION_IMPLEMENTED`** in trusted-local synthetic
engineering scope. The new generic candidate is **frozen, inactive, and has no target
authorizations**. No B03 source, content-revealing metadata, oracle, implementation,
FRC or mapping was inspected or created. Stop at the generic freeze.

Candidate: **`R5.94-GENERIC-PROTECTED-CANDIDATE-1`**.

```text
f19c6dab34128813558a636e37d1f8c2ff109c45cd82172ab561712ba192f77e
```

[Machine candidate](r5_94/protected-freeze-candidate.json) and
[final checks](r5_94/final-checks.json) bind the implementation and validation evidence.
The exact historical R5.91 freeze still passes integrity. Historical R5.79–R5.90,
R5.91, R5.92A negative readiness and R5.93 pre-access halt remain untouched. Original
controller/workspace/pipeline/compiler/mapping files are byte-preserved.

## Implemented repair

- `src/lykoi_protected/` supplies separately versioned protected controller,
  workspace, adapter, pipeline, role policy and freeze machinery.
- `PROTECTED_EVALUATION` means arbitrary source material admitted under restricted
  held-out evaluation rules; `PROTECTED_HELD_OUT_EVALUATION` is a distinct activation
  scope. Neither encodes a benchmark identity or semantic rule.
- Owner authorization binds the exact active candidate/project, opaque source identity,
  role-policy digest, one run and clarification authority **before** custodian access.
  No source content or content hash is needed for pre-access authorization.
- A durable one-time reservation precedes the custodian callback. Completed reads are
  separately recorded before admission. Exact content identities then bind the source
  to the preauthorized opaque identity. Failed admission cannot erase a read; interrupted
  openings cannot silently retry. Terminal outcomes block subsequent workflow use.
- Native source/FRC provenance stays protected. Dependency closure retains the origin
  through WHAT seals, structural projection, BDI, adequacy, V1, verification plans,
  implementation grants, models, compiled targets and verification. No relabeling occurs.
- Append-only journal receipts record actual mediated deliveries by principal, role,
  session and exact artifact, distinguishing raw source from derived representations.
  Authorization does not count as source access. Later exposure milestones are not
  inferred from earlier ones. Author delivery records authorized derived development
  knowledge, distinct from separately prohibited research/development disclosure.
- Source-only reviewer candidate/structural access is denied before SOI commitment.
  The author receives only the existing grant/reservation-bound V1/toolchain/seed
  representation. Original prose, transcripts, rejected drafts and verifier criteria
  are unavailable through its worker API. Verifier WHAT handoffs omit source prose/quotes.
- Clarification supports an exact human authority, another preauthorized authority,
  or unavailable/terminate policy. Answers use existing revision/review/approval rules;
  unavailable material clarification terminates without invented answers.

[Versioned interface and limitations](../../../docs/protected-evaluation-r5.94.md)
describe the private compatibility-view recipe and residual local-process boundary.
The recipe changes only enumerated provenance/version/context anchors and privately
rebinds dependencies. It neither changes historical globals nor maintains a second
semantic engine. Unexpected anchors fail closed; all originals and recipe files are
pinned. The prospective provenance schema references the existing semantic definitions.

## Synthetic calibration evidence

All requirements below are entirely synthetic, using `HELDOUT-SYNTH-001` in fresh
disposable engineering stores. They are **not held-out results** or live protected
model runs. Worker transport receipts explicitly identify test transport.

| Case | Observed result | Evidence |
| --- | --- | --- |
| Supported task-title creation with explicit omitted-priority NORMAL | Authorization → admission → formalizer → blind source-only reviewer → reconciliation → approval/WHAT seal → structural coverage → supported BDI → adequacy → faithful V1 → reviewed/sealed independent plan → implementation grant → restricted author → unchanged compiler → `BEHAVIORALLY_VERIFIED` | [success.json](r5_94/success.json) |
| Same source plus unconstrained task-list ordering | Protected admission/review/seal succeed; structural/BDI/adequacy succeed; unchanged complete mapping refuses `UNREPRESENTABLE_SOURCE / NO_QUALIFIED_COMPLETE_MAPPING`; no grant/author exposure | [unsupported.json](r5_94/unsupported.json) |
| Identical content as PUBLIC and PROTECTED_EVALUATION | Equal formal semantics, structural projection, BDI decisions, adequacy outcome and normalized V1; provenance/content-bound record identities differ appropriately | [provenance-invariance.json](r5_94/provenance-invariance.json) |
| Unauthorized/scoped access | Denied and audited; unauthorized custodian callbacks are never invoked, forbidden recipient exposures remain zero | [unauthorized-access.json](r5_94/unauthorized-access.json), [protected.txt](r5_94/protected.txt) |

Supported evidence records one authorization/open/read/admission, one formalizer,
one source-only reviewer and one author delivery, plus three verifier deliveries
(formal WHAT, target, sealed-plan handle). Separate development-context exposures
are zero. Derived author exposure permanently changes development knowledge to
`AUTHORIZED_DERIVED_EXPOSURE`; it is not called pristine. Unsupported evidence records
zero implementation grants and zero author deliveries.

The 32 focused challenges include no activation, no source-specific authority,
wrong/cross-source identity, wrong run, stale authority, public scope/public active
controller misuse, protected scope misuse, author raw-source/role escalation attempts,
reviewer candidate/structural side-channel before commitment, verifier raw-source/SOI
attempts, reopening/reauthorization, configuration mismatch, content substitution and
public/synthetic relabeling, append-only enforcement, failed producer delivery, failed
opening, completed read followed by rejected admission, all three clarification modes,
provenance/schema invariance and restart/freeze identity enforcement.

## Verification

[Verification summary](r5_94/verification.json) binds adjacent raw suite logs.

| Selection | Result |
| --- | --- |
| R5.94 protected provenance/activation/authorization/access/lifecycle/invariance | **32/32 PASS** |
| R5.86 controller | **34/34 PASS** |
| R5.87 workspace | **26/26 PASS** |
| R5.88 sealed pipeline | **30/30 PASS** |
| R5.89 mappings/containment/rehearsal | **33/33 PASS** |
| R5.91 public activation/freeze/adapter wiring | **14/14 PASS** |
| Compiler/application | **31/31 PASS** |
| External baseline | **3/3 PASS** |
| Guarded R5.80–82/R5.84/V1 | **104 PASS / 2 unchanged historical CRLF pin failures** |
| Model validation/safety | **PASS**, zero capability violations/invalid transitions |
| New candidate integrity and evidence bindings | **PASS** |
| Exact historical R5.91 integrity | **PASS** |
| Whitespace/change scope | **PASS**; no semantic/compiler/mapping/historical evidence changes |

Total **307 passes / 2 known historical failures / 0 errors / 0 skips**. No historical
CRLF bytes, pins or results were normalized or repaired. Initial development exposed
an argument-name collision, a test's incorrect BDI field name and command time limits;
these were resolved before the new freeze. The final evidence writer's first invocation
completed all suites and model checks, then timed out during additional synthetic
record materialization. [attempt-1.json](r5_94/attempt-1.json) preserves that interruption:
no candidate or success result had been published. Resumption reconstructed verification
from completed immutable logs and used fresh synthetic calibration stores; it did not
rerun historical suites or resume any actual held-out evaluation.

Reproduce the **read-only frozen check** with the designated CPython 3.12.10 runtime:

```powershell
& "C:\Users\lblan\AppData\Local\Temp\opencode\python312\python.exe" -B -c "import sys,runpy; sys.path[:0]=['src','.']; sys.argv=['rehearsal/validate_r5_94.py','check']; runpy.run_path('rehearsal/validate_r5_94.py',run_name='__main__')"
```

`run` is an exclusive-create evidence writer; completed records must not be overwritten.

## Scope and honest limitations

Worker input/API restrictions and source-only commitment barriers are mechanically
enforced in the existing trusted-local architecture. Controller `artifact()`, workspace
`inputs()`, SQLite, local operators and arbitrary Python in the service process remain
trusted capabilities, not an OS security boundary. Counts measure delivered artifacts,
not model cognition; a custodian must honestly report partial external reads on failed
callbacks. Source-bearing records/digests belong in restricted storage for real protected
sources. This round publishes synthetic data only. Same-model correlated error, finite
verification, narrow existing mappings/BDI/adequacy, and provider retention/build identity
limits remain. There is no claim of hostile-code containment or universal understanding.

The candidate binds the controller/workspace/pipeline, provenance schemas, activation
and access policies, ledger, unchanged profile/mappings/BDI/adequacy/compiler, model
configurations, prompts, runtime and verification behavior. It grants no target access.

## Completion answers

1. **Truthful protected workspace provenance:** yes, through clarification/review/seal.
2. **Access only after exact authorization:** yes at the custodian/worker admission API,
   with candidate/project/source/policy/run binding and durable reservation.
3. **Actual role exposure tracking:** yes for mediated deliveries, including failed
   producer execution; local-process bypasses remain outside this observation boundary.
4. **Author protected from original prose:** yes through the enforced restricted bundle
   API and existing worker allowlist; this is not an operator-proof OS sandbox.
5. **Semantic meaning unchanged by provenance:** yes for the paired synthetic invariance
   challenge; native semantics and mappings are byte-preserved.
6. **Unsupported protected requirement halts normally:** yes, no weakening or grant.
7. **Generic freeze before B03 authorization:** yes, inactive new candidate established;
   no B03 authorization exists from R5.94.
8. **B03 counters zero:** yes by inherited R5.92A status plus this round's explicitly
   synthetic-only activity. No B03 content, metadata or protected ledger was inspected
   to claim an independent target audit. B03 remains pristine, unevaluated and unexposed.
