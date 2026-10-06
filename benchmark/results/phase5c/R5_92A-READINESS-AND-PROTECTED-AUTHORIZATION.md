# R5.92A — Readiness reproduction and protected authorization preflight

## Decision

**`R5_92A_B03_READINESS_NOT_REPRODUCED`**.

Precise operational blocker:
**`R5_92A_PROTECTED_ADMISSION_REQUIRES_FROZEN_MACHINERY_CHANGE`**.

The non-B03 evidence establishes substantial bounded evaluation machinery, but
does not close protected-source admission under the exact frozen configuration.
`R5_92_B03_EXPOSURE_READY` is therefore **not persisted as an affirmative decision**.
No protected authorization/freeze, B03 controller context, reservation, admission,
FRC or result was created. **Stop before first B03 access.**

The [R5.93 pre-access halt](R5_93-PREACCESS-HALT.md) remains byte-preserved and
correct. It is historical controller-boundary evidence, not a B03 benchmark result.
This round does not establish `R5_92A_B03_PROTECTED_EVALUATION_AUTHORIZED`.

## Exact evidence

The persisted [reassessment](r5_92a/readiness.json) has CJ-1 canonical SHA-256 identity:

```text
40f726f1874e989508918d3182fb168a6a28299088509f4cdb4cc3b71ff51bcc
```

It binds physical hashes of the nine named R5.83–R5.91 public reports, R5.93's
halt, R5.91's final freeze/activation/audit/verification, this round's mechanical
verification and pre-access evidence, and the audit script. This identifies a
**negative readiness reassessment**, not positive readiness or access authority.

The exact unchanged R5.91 machinery identity is:

```text
5ccf1410086f117f9527eefc97d39f519e6e2f7207028175f778460a39f134bb
```

[Mechanical verification](r5_92a/verification.json), its seven adjacent raw logs,
and [pre-access checks](r5_92a/preaccess.json) reproduce the checkout's evidence.
The [audit script](r5_92a/audit.py) imports the existing explicit test selections
without running historical publication/activation drivers. It reads named ordinary
files only; no protected requirement, source digest, resource index, content-revealing
metadata, oracle, implementation or historical B03 result was inspected.

## Original blocker reassessment

| Original blocker | Implemented non-B03 evidence | Disposition for this round |
| --- | --- | --- |
| Source-to-contract/interface coverage authority | R5.84 inspectable bidirectional maps; R5.86 content/role authority; R5.87 committed source-only SOI, conservative reconciliation and exact human approval; R5.88 native structural checks; R5.91 fresh live restricted contexts | Bounded workflow is executable and sufficient to investigate imperfect interpretation. Shared semantic omissions remain possible; no universal coverage qualification is claimed. No new model-certification requirement is imposed. |
| Protected-source admission/containment | R5.85 specifies custody, purpose-scoped opening and compatible provenance; R5.89/91 implement restricted public worker inputs and trusted-program containment | **Not closed.** The frozen admission/activation is public-only, and protected FRC provenance is unsupported. No existing B03-specific durable admission reservation/consumption gate is established by these components. |
| Executable freeze/stage boundaries | R5.86 immutable journal/roles, R5.88 component/run binding and grants, R5.91 activation before public requirements and restart integrity | Closed for the bounded **public** workflow; exact current pins pass. A public activation cannot authorize protected custody or one B03 evaluation. |
| Authoring isolation | R5.88 sealed plan before restricted bundle/grant/reservation; R5.89/91 fresh author contexts with allowlisted V1/toolchain/seed inputs | Implemented in the trusted-local scope; raw source and hidden expectations are absent from the author request. Hostile-code isolation is not claimed. |
| Independent behavioral verification | R5.88 external subprocess behavior and wrong-program failure; R5.89 deterministic WHAT-side producer, review/seal and trusted-target containment; R5.91 live author calibration and frozen wiring | Implemented within finite supported coverage. Criteria are sealed before authorship; no source comparison or author-selected acceptance. No B03 plan exists. |

R5.90's credential halt remains historical; R5.91's actual OAuth smoke resolves
the later public operational configuration question without rewriting that halt.
R5.91 smoke is adapter integration, not a live human-approved end-to-end rehearsal.
That evidence limit is retained, rather than used to demand general production
qualification. Narrow mappings and unsupported discovery/verification scope are
interpretable future halts, not reasons to expand semantics before evaluation.

### Concrete frozen-code contradictions

1. `src/lykoi_rehearsal/public_freeze_r5_91.py` fixes `PURPOSE` to
   `FUTURE_PUBLIC_REHEARSAL_ONLY`; native eligibility explicitly returns
   `protected_authorization: false`.
2. `PublicController.activation()` requires exact equality with that public-purpose
   record. Its registration/adoption guards, persisted configuration and restart
   checks do not interpret a separate protected context as admission authority.
   A disposable **non-B03 synthetic** purpose-substitution probe rejects with
   `FREEZE_FAILURE`, registers **zero artifacts**, and leaves activation absent.
   Storing an arbitrary owner-adopted context would not make it an enforced gate.
3. `src/lykoi_workspace/workspace.py:177–182` hardcodes source classification
   `SYNTHETIC` and context `Public synthetic requirements session`. The transitive
   frozen `benchmark/evaluation/formal_requirements_r5_80.py:87` admits only
   `SYNTHETIC`/`PUBLIC`. A valid synthetic control changed only to classification
   `PROTECTED` rejects with `MALFORMED_FRC`. No B03 text is used in this probe.
4. The existing author reservation is single-use per authorized bundle. It is not
   a one-time protected source opening or a benchmark-wide single-evaluation gate.

Relabeling protected B03 as synthetic/public, activating a renamed public freeze,
adding an ordinary context, or selecting calibration mode cannot close these
contradictions. Correct protected provenance/admission would require changing
frozen workspace/validation/controller behavior and its pins. The requested stop
rule applies. No such changes were made; no wrapper bypass was installed.

## Mechanical verification reproduced

Interpreter: `C:\Users\lblan\AppData\Local\Temp\opencode\python312\python.exe`,
CPython 3.12.10. Embedded-runtime imports explicitly include both `src` and root.

```powershell
& "C:\Users\lblan\AppData\Local\Temp\opencode\python312\python.exe" -B -c "import sys,runpy; sys.path[:0]=['src','.']; runpy.run_path('benchmark/results/phase5c/r5_92a/audit.py',run_name='__main__')"
```

The evidence writer is exclusive-create; do not rerun into these completed records.
Read-only final checks are in `r5_92a/final_checks.py` / `final-checks.json`.

| Existing selection/check | Reproduced result |
| --- | --- |
| R5.86 controller | **34/34 PASS** |
| R5.87 workspace | **26/26 PASS** |
| R5.88 sealed pipeline | **30/30 PASS** |
| R5.89 mapping/containment/rehearsal | **33/33 PASS** |
| R5.91 freeze/admission/restart/live-adapter wiring | **14/14 PASS** |
| Compiler/application | **31/31 PASS** |
| Guarded historical R5.80–82/R5.84/V1 | **104 PASS / 2 known CRLF pin failures**, no errors/skips |
| Model CLI validate | `Lykoi validate: ok` |
| Model CLI safety | **0 capability violations / 0 invalid transitions** |
| Frozen canonical identity and exact current snapshot | **PASS**, changed files/sections empty |
| Existing final controller integrity | **PASS**, revision **2**, admissions empty |
| Existing public database physical bytes before/after inspection | **Unchanged** |
| Nonpublic synthetic activation / protected-provenance probes | **Reject**, as detailed above |
| Protected B03 pre-access eligibility | **false** |

Public B01's six CRLF sequences and public independent SOI's 120 CRLF sequences
reproduce both historical pins under **read-only** LF diagnostics. Physical-byte
tests remain failed; neither file, pin, test nor historical evidence was repaired.
All role invocations in the new tests are fixtures/mocked transports. This round
makes no new live worker/model/provider dispatch.

## Declared limitations and post-B03 production concerns

The following remain limitations, not newly invented benchmark blockers:

- Same-model correlated semantic error; separate contexts/source-blind review do
  not prove independent cognition or completeness. Human approval remains fallible.
- Finite behavioral verification and finite BDI/adequacy/reachability assumptions.
- Narrow unchanged V1/semantic/mapping/profile/verification coverage; unsupported
  contracts must halt without weakening source intent.
- Trusted-local controller/SQLite/operator and process/Python-API containment,
  rather than hostile-code OS containment.
- Unpinned provider build/weights; exact configured alias and invocation machinery
  are provenance, not immutable provider internals.

Ordinary post-evaluation production work includes stronger authentication/delegation,
backup/rollback controls, quotas/OS isolation, provider retention/build provenance,
broader adapters/verifiers, and measured semantic reliability. These are not new
preconditions imposed here. The demonstrated blocker is the incompatible protected
admission/provenance path. **Absence of demonstrated exposure blockers cannot be
claimed** while that contradiction remains.

## Protected-role access policy

**Current effective policy: no role is authorized to receive B03-derived information.**
The following least-information policy records the requested target boundary only;
it is inactive and grants nothing until a compatible protected gate is established.

| Role | Target permitted information/stage | Restriction |
| --- | --- | --- |
| Protected source admission service | Exact B03 source, once, following benchmark-only authority and durable pre-opening reservation | No read in R5.92A; authority must bind B03 only and one first frozen held-out evaluation. |
| Formalizer | Admitted source and frozen allowlisted source-side context | Fresh frozen role session; candidate interpretation grants no authority. |
| Source-only reviewer | Frozen allowlisted source/evidence/span/commitment inputs | No candidate; commit SOI before reconciliation. |
| Reconciliation/controller and declared human source authority | Resulting committed artifacts and source needed for existing approval/clarification | Exact bindings, bounded review, explicit human decisions; no silent invention. |
| Projection/analysis | Approved formal artifacts needed by existing native checks | No convenience access to original prose. |
| Lykoi author | Existing authorized V1/implementation bundle after sealed plan and exact grant | No raw B03 prose, rejected drafts, deliberations, hidden criteria or service credentials. |
| Verification-plan role | Existing WHAT/WHAT-seal/profile inputs | No implementation or expanded raw-source visibility. |
| Verifier executor | Exact frozen target/plan/verification-side environment artifacts | No raw B03 prose; separate from author/SUT. |
| General research/development/publisher | Approved non-content-revealing summaries only | No protected-derived development material without separately accounted authority. |

## Contamination-transition policy

No transition occurred. Before first access: **`B03_PRISTINE`**,
**`B03_NOT_EVALUATED`**, **`B03_NOT_EXPOSED_TO_LYKOI_DEVELOPMENT`**.
Use R5.85 §13's existing monotone vocabulary, plus separate per-role access events:

1. Authorization alone keeps source unopened/pristine and counters zero.
2. A future durable reservation precedes opening (`PREFLIGHT → RESERVED → OPENED`).
   Custodian source access is logged separately; **on first source admission/read,
   B03 ceases to be pristine**. Custody moves through
   `UNOPENED → AUTHORIZED_PREPARATION → PREPARED_SEALED` as actually applicable.
3. Record formalizer and reviewer exposure at their separate input deliveries,
   even if a request then fails. Neither implies author/development exposure.
4. The author receiving even a derived authorized V1 bundle is **author exposure**
   and **development knowledge `UNEXPOSED → AUTHORIZED_DERIVED_EXPOSURE`**.
   Original-prose exposure remains separately recorded and prohibited by the target
   policy. No author handoff means no inferred author exposure.
5. Any separate development-context disclosure records development exposure,
   independently of formalizer/reviewer access. Unauthorized disclosure, tool drift,
   oracle leakage or undeclared readers makes integrity `CLEAN → CONTAMINATED`;
   a properly authorized opening is not itself an integrity violation.
6. Preserve the first terminal result or `INCOMPLETE`, including early refusal.
   No repair, reset or reseal restores pristine status or erases exposure history.

This is a prospective accounting policy, not an implemented B03 access ledger.
No content identity is invented before admission.

## Zero-access and eligibility conclusion

[Pre-access evidence](r5_92a/preaccess.json) records **zero** source reads/attempts,
content-revealing metadata accesses, openings, admissions, observations, formalizer/
reviewer/author dispatches, static-consumer accesses, development exposures,
authorizations, FRC creations, projections, compilations and verification runs.
Basis: inherited public `r5_91/final-audit.json` plus this round's scoped operations;
no unavailable protected ledger is presented as independently audited.

The public controller remains at revision **2** with **zero message/source admissions**
and unchanged database SHA-256
`a416e9e01dbad29072101bf0784d39281bc868faa635e9b826dafa2595de60b0`.
Native infrastructure eligibility is true, explicitly **protected authorization false**.
The smallest pre-access check answers **not eligible for protected B03 admission**.
No protected authorization identity or controller event exists from this round.

The remaining action is **not** execution of an already-authorized B03 run.
It is resolution, under separate instructions, of the demonstrated frozen
protected-admission/provenance incompatibility. R5.92A stops here; B03 stays pristine.
