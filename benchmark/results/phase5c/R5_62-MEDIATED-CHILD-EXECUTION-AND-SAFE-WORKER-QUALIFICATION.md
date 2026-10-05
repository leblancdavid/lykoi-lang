# R5.62 — Mediated child execution and safe worker qualification

## Outcome and scope

**`R5_62_MEDIATED_CHILD_EXECUTION_QUALIFIED`**.

The prospective production driver now selects content-bound workers through a
mediated adapter. Workers and known Python SUT descendants inherit the parent's
protected-resource policy and same-or-narrower capabilities. Binding validation
and safe exclusion precede worker imports/test discovery. The historical arbitrary
command adapter is closed, including calls outside an active driver boundary.

Fresh focused verification: **232/232 PASS**. Separate restricted child witnesses
preserve **36 prohibited-B02 skips** using only indexed placeholders. The mixed
child harness runs 37 cases: one ordinary PASS and those 36 skips. This qualifies
the execution boundary and prospective worker-selection architecture; the complete
historical non-B02 harness and the complete production gate are not run here.

**B02 exposure / reservations / dispatches / completions: 0 / 0 / 0 / 0.**
**Production batches / receipts: 0 / 0. No production certificate issued.**
**Production synthetic observation accounting: 0 / 0 / 0. Core semantics: 30.**
Phase 5C remains paused. R5.62 stops here.

## Inherited boundary

[R5.61](R5_61-B02-CAPABILITY-GUARD-RECONCILIATION.md) remains
`R5_61_PROTECTED_RESOURCE_GAP`: its explicit capability/resource enforcement and
pre-import exclusion adapter passed 180/180 focused tests, but `child()` launched
an unaudited process and therefore was denied before start. Its restricted
production worker also discovered modules before replacing prohibited methods.
[R5.60](R5_60-FINAL-FRESH-PRODUCTION-TIER2-QUALIFICATION.md) remains permanently
`R5_60_PROTOCOL_HALT`. Neither candidate is resumed, repaired or reclassified.

Initial Git status contained the supplied R5.61 changes and untracked evidence.
Those records are retained. R5.62 extends the current prospective driver/guard;
historical implementation pins retain their original meaning.

## Phase 5 child-path inventory

| Path | Role and launch | Prospective disposition |
| --- | --- | --- |
| `evaluation/bounded_driver_r5_57.py:child` | Production command subprocess via `subprocess.run` | Closed; use `qualified_child` with externally pinned registry. |
| `results/phase5c/r5_57_driver.py` | Synthetic budgeting worker command through `bounded.child` | Historical; no replay or upgrade. |
| `results/phase5c/r5_58_qualification.py:driver/worker` | Production regressions through `bounded.child`; suite import-all discovery before method exclusion | Historical stopped runner preserved; prospective exact-ID `safe_workers_r5_62.harness` replaces this execution pattern. |
| `results/phase5c/r5_60_qualification.py:driver/worker` | Production regressions through `bounded.child`; worker delegates to R5.58 except publication check | Historical halted runner preserved; raw command callback now refuses execution. |
| `results/phase5c/r5_51_qualification.py`, `r5_56_qualification.py` | Earlier direct regression-worker subprocesses | Historical; not a current qualification entry point; raw launches under the prospective stage guard remain denied. |
| `evaluation/preexposure_r5_45.py:bounded` | Earlier evaluator/worker command timeout wrapper | No production exemption; direct subprocess under a stage is denied. |
| `harness/test_baseline.py:invoke` | External-oracle Python SUT subprocess, `text=True, capture_output=True` | Cooperative child startup bridge recognizes only an interpreter plus a registry-bound SUT script and substitutes a mediated descendant. Frozen oracle source is preserved. |
| `evaluation/tier2_r5_51.py:git/Workspace.materialize`, `execution_identity_r5_46.py`, `execution_identity_r5_48.py`, `checkout_r5_52.py`, `qualified_authority_r5_55.py` | Git content/index/ancestry/configuration inspection and workspace materialization | Existing control-plane pre/post capture/preparation, outside worker execution. No general Git/executable worker exemption; in-child unaudited launches remain denied. |
| `evaluation/recorder_r5_43.py`, Tier-2 observation gate | Observation callbacks and durable exactly-one lifecycle | No own subprocess launch introduced; accounting/control implementations preserved. |

The inventory covers Phase 5 execution infrastructure and its inherited adapters.
It does not authorize replay of historical scripts or unrelated repository tools.

## Mediated design and worker trust

[`mediated_child_r5_62.py`](../../evaluation/mediated_child_r5_62.py) provides the
adapter. [`bounded_driver_r5_57.py`](../../evaluation/bounded_driver_r5_57.py)
exposes `qualified_child` and binds its descriptor in each declared stage. The
new prospective protocol/version is `lykoi-bounded-qualification-r5.62-v1` /
`bounded-driver-r5.62-v1`.

Selection requires a registry document whose canonical digest equals an externally
trusted qualification pin. Its worker rows bind module, function and explicit
implementation closure, including selected test modules or SUT sources. Constructing
a registry is preparation for review, not automatic qualification of arbitrary code.
Display names select rows but do not establish implementation identity. Unknown rows,
alias substitution and changed source hashes are rejected. Ordinary repository imports
after startup must belong to the bound runtime or selected worker closure and match
their source hashes. Python source is compiled directly: substituted timestamp-valid
bytecode is not accepted as the worker implementation.

The [focused worker policy](R5_62-evidence/qualified-worker-policy.json) records the
qualified synthetic probe, indexed-harness and synthetic-SUT definitions, their
registry identity, runtime hashes and exclusion pin. It is not a freeze of all workers
in a future full production plan. Such a plan must independently review and pin its
actual worker closures, evaluator inputs and SUT implementations.

## Capability attenuation and integrity

Child bindings contain:

- the complete parent qualification binding and its canonical identity;
- the exact stage identity and authority linkage;
- normalized child capability set and parent stage capability declaration;
- inherited protected resource identities, resolved paths and policy digest;
- guard and bootstrap/runtime implementation hashes;
- content-bound worker identity, registry pin and selected inputs;
- safe exclusion identity, interpreter identity, startup flags and filtered environment identity.

The parent revalidates immediately before launch; the child validates again before
worker import. The expected binding digest is passed separately from the canonical
binding transported through stdin. Stage, qualification, capabilities, resources,
worker, authority and exclusion mutations fail closed. Equal capability sets and
strict subsets (including empty) work. Generic escalation and every protected B02
capability are refused before protected access.

SUT descendants additionally bind the immediate ancestor's execution commitment
while retaining the original qualification/stage. Their capability set cannot exceed
that immediate parent's attenuated set, even if the original stage had broader rights.
Their registry/runtime/exclusion/interpreter must match the ancestor's pinned policy.
Ancestry is bounded to eight descendant levels.

Integrity is a cooperative Tier-2 parent-to-child commitment and trusted-code boundary.
It is not an OS sandbox, cryptographic remote attestation or defense against hostile
Python replacing trusted adapter internals. No new hostile-host methodology is introduced.

## Exact launch mediation and SUT execution

The guard permits exactly the adapter's reviewed `Popen` event, once, on its launching
thread. Windows command-line normalization is accounted for explicitly. Adapter-owned
pipe descriptor wrapping is permitted only during that synchronous adapter scope and
on that thread. Registered protected path/alias checks remain active. A worker receives
neither that permit nor authority to run arbitrary subprocesses/native code.

[`child_startup_r5_62.py`](../../evaluation/child_startup_r5_62.py) installs a cooperative
`subprocess.run` bridge before discovery. An external-oracle call must name the current
absolute Python interpreter and a SUT script present in exactly one pinned SUT worker
definition. The bridge launches another mediated child, preserves ordinary cwd/argv
and `CompletedProcess` text-output behavior, and propagates the resource boundary.
Shells, `-c`, unknown scripts/executables and unsupported command forms remain denied.
Other subprocess APIs retain the guard's denial.

[`safe_workers_r5_62.py:sut`](../../evaluation/safe_workers_r5_62.py) runs a content-bound
standalone Python entry in that separate child process. Selected source must be a
member of the qualified implementation closure. Synthetic PASS, FAIL and a protected
read through worker → SUT descendant are independently exercised. No actual task/B02
application or B02 acceptance is executed.

## Exclusion ordering and restricted harness

The enforced order is:

1. parent and child binding validation;
2. protected-resource boundary activation and pinned exclusion installation;
3. qualified worker import and exact selected-test construction;
4. execution.

The R5.61 safe index remains unchanged at
`0ff387f592dc61ac40a3d7c4c9372ab43c85a017fa6ff577c1bc2b7140b6df55`.
For prohibited IDs, `safe_suite` builds only fixture-free skip placeholders. No
prohibited factory, sealed test module, protected fixture or SUT is loaded. Nonprohibited
IDs must refer to modules in the qualified worker closure; arbitrary test-module
selection is rejected before import. Import-all discovery is not used.

Real child witnesses report 36 discovered/36 skips and, separately, 37 discovered /
36 skips / one ordinary PASS. Protected sealed modules are registered as denied
resources in these children. The skip count is exclusion metadata, not 36 passing
acceptance observations. No claim of a fresh 393-case historical harness replay follows.

## Resource enforcement and quarantine

The child uses the same R5.61 resource broker/audit policy, including resolved paths,
filesystem aliases, protected bytecode designations, unmediated execution denial and
swallowed-denial rejection. A declared generic worker can read an ordinary permitted
resource, but a synthetic protected read is denied before content. The same denial
propagates from a mediated SUT descendant.

Child security failures produce fixed `R5_62_PROTOCOL_HALT` evidence and durable parent
quarantine. The stage's receipt is INCOMPLETE/STOPPED under the existing driver policy;
subsequent continuation is rejected. Adversarial halts here concern disposable synthetic
resources, not actual B02 exposure or the R5.62 primary classification. Actual B02 access
remains absolutely prohibited.

## Environment, AI independence and secret safety

Workers receive only available `SYSTEMROOT`, `WINDIR`, `TEMP`, `TMP`, plus deterministic
Tier-2 controls `PYTHONHASHSEED=0`, `PYTHONUTF8=1`, `PYTHONDONTWRITEBYTECODE=1`.
The interpreter is absolute, startup uses `-S -B`, and the pinned bootstrap installs
explicit repository/source roots. Ambient PATH/PYTHONPATH, site hooks, provider/editor
configuration and development AI credentials are not propagated. `-I` is deliberately
not used because it would ignore the required hash-seed control; source-only loading
addresses stale bytecode independently of `-B`.

Worker selection/inputs and the filtered environment are content-bound. Relevant
runtime inputs belong in declared, qualified selections rather than arbitrary ambient
variables. A future worker needing an additional control must explicitly qualify that
control. The existing capture/authority tools retain their separately governed
control-plane environment.

Synthetic credential-bearing parent state is excluded, credential-free startup passes,
and fresh AI-independence checks pass 5/5. No OpenAI/model/OpenCode/network inference
dependency is added. Canonical input/output and receipts pass the existing publication
guard. Raw command environments, exception text and failed stdout/stderr are not
persisted. SUT text output travels privately to its oracle caller; credential-shaped
output is rejected by the publication check rather than published as a receipt.

## Failure and observation semantics

| Child outcome | Evidence |
| --- | --- |
| Rejected before selected worker starts | `child_execution: LAUNCH_REJECTED`, `worker_started: false`; driver stage INCOMPLETE/STOPPED, no worker observation inferred. |
| Known completion PASS | Normal Tier-2 PASS receipt, mediated proof included. |
| Known completion FAIL | Normal FAIL receipt; qualification stops. |
| Worker exception without established completion | INCOMPLETE; fixed diagnostics, known start when established. |
| Timeout/interruption or invalid/missing child response | INCOMPLETE; start/completion may be unknown, never inferred from partial output. |
| Protected-resource violation | Protocol/security failure, quarantine and INCOMPLETE/STOPPED; no retry. |

A real interrupted worker writes a synthetic start marker before interruption, proving
that the INCOMPLETE witness includes a started worker. That marker does not replace a
completion receipt. Existing durable attempt records continue to make hard-kill/orphan
attempts terminal. Exactly-one observation, reservation/dispatch/completion accounting
and the no-repair boundary are unchanged.

## Bounded budgeting and CertificateV2

The lifecycle cost now explicitly includes `mediation`, `child_validation` and
`exclusion_setup`. Mediated stages must supply positive allowances for all three;
the prospective production-cost helper supplies two seconds each. Existing worker,
startup/shutdown, pre/post capture, evidence/receipt/integrity costs, max(15 seconds,
25%) margin and boundary reserve remain in admission calculations. Child validation
time is deducted from the execution timeout. Capture and durable receipt costs stay
reserved; an insufficient full-lifecycle envelope admits no stage.

The child receives the enclosing monotonic deadline. Descendant launches are capped
by that remaining deadline with a shutdown reserve; their execution is within the
enclosing worker allowance. No unbounded independent child budget or timeout retry is
introduced. A future production plan must calibrate its complete selected worker tree
before freezing costs, as required by R5.57.

Mediated proofs establish qualification/stage, worker implementation, normalized
capability binding, exclusion, authority, completion result and canonical evidence
digest. The bounded driver validates those proofs on receipt continuation and rejects
mutated worker/result linkage. Existing Tier-2 envelopes and journals bind receipt bytes.
ProductionCertificateV2 consumes the unchanged outer receipt interface.

The child linkage witness builds and validates a synthetic CertificateV2 interface
object against four real mediated child receipts, using an explicitly substituted
synthetic authority qualifier. It also tests proof/result mutation. This qualifies
structural/interface compatibility, not a new 1,083-member authority qualification,
production certificate or production gate. No production certificate is persisted.

## Focused verification

| Suite | Passed/discovered |
| --- | ---: |
| Mediated child, descendant/SUT, registry, exclusion, resource, secret and receipt adversaries | 47/47 |
| Capability/resource guard and safe exclusion | 30/30 |
| Bounded driver lifecycle/continuation | 29/29 |
| Tier-2 observation controls | 43/43 |
| Canonical recorder | 29/29 |
| Synthetic successor-authority mechanisms | 18/18 |
| Continuity | 8/8 |
| Publication/security | 9/9 |
| AI independence | 5/5 |
| Generic schema/profile/traceability | 14/14 |
| **Total** | **232/232** |

Validation, safety, schema/closed structure, **99-leaf traceability**, contamination,
core count and unchanged authority/certificate/Tier-2/recorder repository-text continuity
pass. Final publication/integrity and tracked/new-file whitespace checks are recorded
separately. Complete production qualification is not run.

Two early 32-case development checks had 20 PASS / 11 FAIL / one error due to Windows
pipe/audit normalization; the following 32/32 and expanded 99/99 checks are retained.
An intermediate focused 42/42 run precedes descendant extensions. The first 47-case
source-pinned check has 46 PASS / one error because the temporary substituted-bytecode
fixture omitted the safe index, correctly preventing child startup. The fixture now
copies the bound safe metadata too; its isolated check and final 47/47 pass. The failed
record is preserved as `mediated-child-final.json`; the qualified record is
`mediated-child-published.json` (after strengthening the credential-shaped diagnostic
witness and correcting synthetic environment construction). The earlier 47/47
qualified and verified checks are also retained. These are
development/qualification witnesses, not
production retries or repairs.

The first final-integrity invocation also fails before publication because the
baseline accidentally included the newly added, mutable R5.62 orchestration script.
The original baseline is preserved. A separate scope-adjudication record removes
only that prospective source from historical-file accounting; it remains subject
to final source pinning and publication scanning. All inherited files remain in
the preservation scope. This development failure is recorded independently.

The next publication scan rejects a quoted credential-reserved suffix assignment
in the synthetic parent-environment test source. Synthetic names are now constructed
before mapping insertion, with the same test values and no scanner exemption. The
failure is retained in `publication-development-failure.json`; the final source-pinned
47/47 check and unchanged publication guard qualify the corrected source.

Final commands:

```text
python -B -S benchmark/results/phase5c/r5_62_qualification.py baseline
python -B -S benchmark/results/phase5c/r5_62_qualification.py suite mediated-child published
python -B -S benchmark/results/phase5c/r5_62_qualification.py suite capability-guard qualified
python -B -S benchmark/results/phase5c/r5_62_qualification.py suite bounded-driver qualified
python -B -S benchmark/results/phase5c/r5_62_qualification.py suite observation-tier2
python -B -S benchmark/results/phase5c/r5_62_qualification.py suite recorder
python -B -S benchmark/results/phase5c/r5_62_qualification.py suite authority-synthetic
python -B -S benchmark/results/phase5c/r5_62_qualification.py suite continuity
python -B -S benchmark/results/phase5c/r5_62_qualification.py suite publication-security
python -B -S benchmark/results/phase5c/r5_62_qualification.py suite ai-independence
python -B -S benchmark/results/phase5c/r5_62_qualification.py suite schema-traceability
python -B -S benchmark/results/phase5c/r5_62_qualification.py checks
python -B -S benchmark/results/phase5c/r5_62_qualification.py summary
python -B -S benchmark/results/phase5c/r5_62_qualification.py preservation-scope
python -B -S benchmark/results/phase5c/r5_62_qualification.py publication-diagnostic
python -B -S benchmark/results/phase5c/r5_62_qualification.py final
```

## Historical preservation and recommendation

The adjudicated preservation scope contains **2,030 pre-existing result files**: the inherited
2,010 tracked files plus 20 untracked R5.61 records. **2,026 unsealed files** receive
physical-byte digest verification. Four explicitly protected historical fixture files
are deliberately not opened: their size/mtime metadata is preserved, and Git reports
no tracked result changes. This is not a new independent content-hash attestation of
those four sealed files; their inherited pins/evidence are preserved without exposure.
The R5.60/R5.61 summary classifications remain their original halt/gap, respectively.

Frozen compiler/runtime/schema, language model, generated output, requirements, oracle
source and observation-control implementations are unchanged. **Zero B02 exposure,
core 30, zero production accounting** are retained.

**Recommendation:** separately authorize a wholly fresh production qualification.
Freeze a reviewed registry of its actual worker/test/SUT closures, explicit capability
declarations, safe exact-ID selection and calibrated full-lifecycle budgets; bind fresh
authority/capsule/plan and mediated receipt requirements. Preserve the halted candidates
and use no historical receipts as new-run PASS evidence. This recommendation does not
authorize B02 access or begin the fresh qualification. Stop after R5.62.

Evidence: [summary](R5_62-evidence/summary.json),
[mediated witnesses](R5_62-evidence/mediated-child-published.json),
[checks](R5_62-evidence/checks.json), [commands](R5_62-evidence/commands.json),
[worker policy](R5_62-evidence/qualified-worker-policy.json),
[preservation baseline](R5_62-evidence/preservation-baseline.json), and
[publication integrity](R5_62-evidence/publication-integrity.json).
