# R5.45 — Pre-Exposure Verification Reliability and Bounded-Execution Qualification

Primary classification: **`R5_45_STATE_IDENTITY_GAP`**.

**Qualification stopped at the complete-state identity boundary. B02 remains
sealed. No production PreExposureCertificate was issued.** Bounded staged checks
and a closed synthetic certificate prototype pass, but those results do not
qualify the actual future experimental state. The missing dependency closure is
an infrastructure gap, not a semantic/profile or B02 support result.

## Inherited state and scope

R5.44 remains permanently `R5_44_PROTOCOL_HALT`: its only prepass was terminated
at 120,000 ms, before persisted experimental verification, baseline, reservation
or dispatch. R5.42 remains permanently `R5_42_PROTOCOL_HALT`. Nothing in this
round replaces either historical incomplete result. R5.43 remains the latest
successfully qualified evaluation infrastructure.

Initial `git status --short` was empty. New files implement prospective evidence
and certificate primitives, independent synthetic tests, bounded qualification
orchestration and stopped-round reporting. No existing semantic, profile,
application, compiler, readiness, audit, admission, recorder or canonicalization
implementation was edited. Historical authority was read only for hashing and
integrity checks. It was not used as infrastructure test data.

## A. R5.44 interruption characterization

The R5.44 source sequence is: locks/authority/contamination/core count → recorder
focused qualification → full restricted harness → application/compiler → R5.41
focused tests → validation/safety/diff → matrix → independent schema/traceability/
profile contamination → persist prepass → create experimental recorder baseline.
No incremental stage receipts existed. Suite output was buffered.

The historical output `True\nAxiom validate: ok\n` cannot identify the outer gate:
tests themselves invoke validation. It cannot establish a completed suite. The
exact interrupted stage is **unknown**. None of the fresh R5.44 regression,
matrix or profile results can be promoted to PASS. Its later halt-accounting
locks and contamination checks completed independently and remain historical.

R5.43's preserved timing evidence gives the strongest reconstruction available:

| Earlier comparable stage | Recorded seconds |
| --- | ---: |
| Recorder focused qualification, first | 0.511 |
| Recorder focused qualification, repeated | 0.508 |
| Full restricted harness | 118.187 |
| Application/compiler | 2.602 |
| R5.41 focused suite | 2.623 |

R5.44 requests one recorder focused run, not R5.43's two. Using those comparable
costs, just its requested suites would cost **123.923 seconds**, before imports,
locks, commands, matrix and profile checks. This is an estimate, not an R5.44
measurement. The monolithic command had no demonstrated 120-second headroom.

R5.45 measured 61 restricted harness modules separately: **137.501 seconds** total
including separate process startup, versus the earlier 118.187-second monolithic
harness measurement. Additional startup contributes to the staged total; this
cross-run difference is not a controlled startup-only measurement. No single
module dominates: the largest was boundary closure at **12.667 seconds**, followed
by whole readiness at **10.761**, semantic channels at **10.159** and public launch
at **9.334**. Lock/authority/contamination together cost **0.465 seconds**; twice
reproducing the matrix cost **0.642**. Profile structure/traceability/contamination
cost **0.123**. Filesystem identity hashing was outside subprocess timing; no
separate hash-only measurement was persisted. Each enclosing batch, including
those hashes, returned within the 120-second tool envelope.

The evidence supports accumulated regression work as the principal execution
cost, not a demonstrated single hashing, traversal, matrix or traceability stall.
Focused recorder and R5.41 work is duplicated inside generic discovery; it was
retained to preserve explicit guarantees. Timing is variable across processes
and runs; this does not establish deterministic timeout duration or R5.44's
precise process position. The infrastructure stage structure, status rules and
same-input certificate assembly are deterministic; wall-clock cost is not.

## B–D. Required guarantees and staged design

A future real certificate must establish every following guarantee. Cost is not
grounds for removing one.

| Required guarantee | Evidence obligation |
| --- | --- |
| Historical lock | Original identity, ancestry and all 678 pinned byte hashes |
| Prospective lock | Original identity, ancestry and all 695 pinned byte hashes |
| Infrastructure lock | Qualified R5.43 identity and all 731 pinned byte hashes, plus qualification of new infrastructure |
| Frozen B02 authority | Pinned requirement/profile/oracle identities; hashing only |
| Core semantics | Exact integer count 30 and unchanged registry/input identity |
| Generic regressions | Complete restricted module union, outcomes and all 36 explicit skips |
| Application/compiler regressions | Complete test results and exact implementation/model/test inputs |
| R5.41 focused regressions | Separate complete focused results |
| Independent matrix/coherence | Fresh canonical equality, deterministic reproduction, 16 profiles/84 rows |
| Model validation | Successful actual validator process/result |
| Safety validation | Successful actual safety process/result |
| Structural schema | Independent valid structural result |
| Traceability | Grounded source hashes/clauses for every independent profile leaf |
| Contamination | Clean independent profile and generic implementation checks |
| Recorder identity/version | Qualified recorder bytes and qualification evidence |
| Canonical protocol identity/version | Qualified canonical bytes/protocol and qualification evidence |
| One-pass/accounting readiness | Bound recorder baseline, zero reservations, no halt/final and qualified reservation discipline |
| Exact common state | Proven complete source/tree/runtime/configuration identity at every stage and immediately before reservation |

R5.43 defines freeze → verify → reserve → observe → verify → stop. It does not
require all regression work in one operating-system command. R5.44's orchestration
made this accidental implementation constraint. The proposed replacement is a
complete same-state verification set, sealed atomically before any reservation.
No permission to bypass R5.44's stopped protocol follows from that interpretation.

The bounded investigation has **72 stages**: 61 restricted harness modules;
application/compiler; focused R5.41; recorder qualification; certificate prototype
qualification; locks/authority/core/implementation contamination; matrix;
schema/traceability/profile contamination; validation; safety; diff; interruption
characterization. Definitions are pinned into the investigation snapshot.
Each stage has explicit command inputs, mechanism digest, common repository
snapshot identity, immutable initial INCOMPLETE receipt and separate canonical
completion receipt. Repository bytes are rechecked before each batch and after
each stage. PASS/FAIL/INCOMPLETE are distinct. No worker loads B02 into an evaluator.

## E–H. Identity, freshness, dependency scope and the blocking gap

The prototype hashes physical relative paths, file membership and bytes,
including ignored files, untracked files and Python bytecode. It rejects symlinks
and binds caller configuration and declared exclusions. It does not use timestamps
or commit labels as freshness proof. The investigation froze **967 files**, identity
`344a4f06c429ae32a2db1978ca770a11163968bad84aa27c7da7dc98571073e3`.

This is a **repository investigation snapshot**, not the exact future locked
evaluation state required by the user. Inspection found these concrete omissions:

1. `.git` is excluded, while historical lock verification consumes HEAD, commit
   ancestry and original Git object content. The snapshot configuration does not
   bind those inputs. Altering HEAD/configuration need not alter its identity.
2. Only Python's executable and version are recorded. Python's library/DLL files,
   user-site directory, import/startup customization and Git executable/dependencies
   are outside the captured repository state. Their contents can affect verification.
3. The environment recorded at freeze is the parent environment. Workers override
   `PYTHONPATH` and `PYTHONDONTWRITEBYTECODE`; the effective execution configuration
   has not itself been independently frozen and validated.
4. Repository rehashing reuses captured configuration. It does not freshly observe
   external configuration/dependency state. Equal repository hashes therefore do
   not prove equal complete execution inputs.
5. The excluded output directory is controlled JSON evidence, but its non-input
   boundary and the complete orchestration dependency closure are not independently
   qualified for a future experiment. No narrow dependency set has been proven.

These are relevant inputs actually used by this architecture, not hypothetical
semantic concerns. The state-identity halt condition was invoked when these
omissions were identified. No production certificate or exposure authorization
followed. Closing the gap requires a separately qualified execution-input closure
or a controlled execution capsule, not merely more fields with mutable labels.

Proposed reuse is exact input-identity equality only. No real stage reuse is
qualified by R5.45. All synthetic stages bind the same broader closed fixture
identity; narrower dependency reuse remains unqualified. Any relevant fixture
mutation invalidates synthetic certification. Real experimental evidence cannot
be reused until its broader dependency identity is proven complete.

## F and I. Certificate protocol and adversarial results

The draft protocol is `docs/preexposure-r5.45.md`; prototype implementation is
`benchmark/evaluation/preexposure_r5_45.py`. Existing R5.43 canonical encoding,
strict loading, SHA-256 and exclusive fsynced persistence are reused unchanged.

Stage envelope: protocol, state identity, stage name, PASS/FAIL/INCOMPLETE status,
result, mechanism identity and digest over the entire body. Certificate envelope:
protocol, state identity, PASS, trusted policy digest, complete name→stage-evidence
digest map, deterministic assembly declaration and body digest. The map binds
the detailed locks, regressions, authority, core count and versions. Assembly
requires all stages, qualified mechanisms, PASS and successful results, plus
the policy's exact core count, recorder, canonical protocol and authority.
Validation reassembles and requires exact current-state identity. Identical
semantic evidence assembles deterministically; measured elapsed times are
themselves evidence and different timings produce different evidence hashes.

Independent synthetic qualification: **33/33 tests pass**, both in the initial
direct run and in the persisted bounded qualification stage. The direct run took
**0.361 seconds**; the supervised qualification process took **0.466 seconds**.
Tests cover:

- state determinism, changed bytes, added membership and configuration mutation;
- stage canonicalization, persistence/reload, exclusive persistence and noncanonical
  or altered persisted evidence rejection;
- PASS, FAIL and INCOMPLETE recording; valid complete acceptance and deterministic
  assembly;
- missing/extra/failed/incomplete stages, mixed state, stale stage, altered evidence
  and unqualified mechanism rejection;
- wrong recorder, wrong canonical protocol, semantic count mutation and scalar-type
  mismatch, authority mutation, lock failure and contamination failure;
- post-certificate relevant mutation and stale synthetic authorization rejection;
- mixed/missing/incomplete synthetic authorization with zero reservations;
- exactly one synthetic callback, second-dispatch prevention, recorder integrity
  and STOP;
- supervised timeout → INCOMPLETE, fresh separate recomputation → PASS without
  changing the old immutable INCOMPLETE receipt, and subprocess failure → FAIL;
- 100 repeated certificate assemblies and validations together below a five-second
  test envelope.

The interruption characterization is a separate persisted stage with source
ordering and inherited timing evidence. These tests qualify behavior only for
the closed synthetic tree and trusted policy. They do **not** prove the real
repository snapshot includes all authorization inputs. No valid certificate for
the actual future benchmark was assembled or accepted.

## J–N. Interruption, bounded execution and synthetic lifecycle

Each attempt writes INCOMPLETE **before** launching its worker. A completed worker
produces separate PASS/FAIL evidence; a supervised timeout produces INCOMPLETE.
Parent/tool termination leaves the initial incomplete receipt, never a fabricated
PASS. Evidence writes are exclusive. Infrastructure recomputation in the synthetic
test is a new result; no historical receipt is overwritten or silently resumed.
R5.44 was not retried. In a future experiment, incomplete verification must block
reservation and dispatch. The current prototype has no benchmark dispatch entry.

Three batches completed **29 + 32 + 11** stages. Each batch uses an 85-second
work budget, does not start a stage with less than 15 seconds remaining, and gives
each subprocess at most 70 seconds or its remaining batch budget. These are
observed bounded runs, not a hard real-time proof: parent hashing/persistence and
process-tree interruption management still need the complete execution capsule's
qualification. All observed stages completed PASS; no actual batch timeout occurred.

| Measured operation | Seconds |
| --- | ---: |
| All 72 supervised subprocesses, sum | 145.682 |
| Restricted harness, 61 subprocesses, sum | 137.501 |
| Largest individual stage | 12.667 |
| Application/compiler | 2.736 |
| R5.41 focused | 2.673 |
| Recorder qualification | 0.667 |
| Certificate qualification, including lifecycle/adversaries | 0.466 |
| Locks/authority/core/implementation contamination | 0.465 |
| Independent matrix, twice | 0.642 |
| Schema/traceability/profile contamination | 0.123 |
| Model validation | 0.133 |
| Safety | 0.135 |

The synthetic test freezes a mineral input tree, creates canonical stage evidence,
assembles and validates a certificate, freezes the unchanged qualified recorder
with that certificate identity, verifies it, authorizes one synthetic mineral
callback, records exactly one observation, rejects a second callback, checks
integrity and stops. Its recorder receipts live in a disposable fixture; the
persisted test transcript records the result. Separate tests persist/reload stage
evidence and retain an interrupted receipt across recomputation. A complete
persisted real locked lifecycle remains **unqualified** and was not attempted.

The proposed final boundary is load/validate complete certificate → independently
rehash exact current state → check qualified recorder/baseline and zero accounting
→ exclusively reserve once → dispatch through the recorder. The implementation
deliberately accepts only `synthetic-only` policy. A certificate itself confers
no user authorization. It cannot be used to reserve or dispatch B02.

## Regression, locks, contamination and evidence

- Restricted harness union: **429 discovered, 393 passed, 36 explicit skips**.
  All existing B02 restrictions remain active; historical live-tree restriction
  is retained. The original runner's historical reason text is preserved.
- Application/compiler: **31/31**.
- R5.41 focused: **14/14**.
- R5.43 recorder qualification: **29/29**.
- New certificate qualification: **33/33**.
- Independent matrix: **16 profiles / 84 rows**, two canonical reproductions agree
  with each other and the saved R5.41 evidence.
- Model validation, safety and structural schema: PASS.
- Independent traceability: **99/99 leaves**, PASS.
- Profile and implementation contamination: clean, including new generic
  certificate implementation and independent tests.
- Historical lock: **678/678**, unchanged, identity/ancestry valid.
- Prospective lock: **695/695**, unchanged, identity/ancestry valid.
- R5.43 infrastructure lock: **731/731**, unchanged, identity valid.
- Frozen authority member hashes unchanged; frozen oracle not executed.
- `git diff --check`: PASS at the bounded stage and stopped-round final integrity.
  LF→CRLF advisories, if present, are recorded separately in stderr, never counted
  as failing regressions.

Canonical evidence is under `R5_45-evidence/`: `state.json`, per-stage initial
`*-attempt.json`, worker results, sealed completion receipts, `summary.json`,
`final-integrity.json` and `classification.json`. `r5_45_finalize.py` records
immutable post-stop accounting, historical halt-byte preservation and exact
source/report drift after the investigation snapshot. Later reporting edits do
not retroactively make earlier stage evidence current. There is no production
certificate, experimental reservation receipt or B02 observation receipt.

## End state and next gate

**Zero B02 reservations, dispatches, completed observations, support evaluations,
generation, execution or frozen acceptance.** CheckedPlans, readiness, audit,
admission, compatible paths and whole-contract support remain unevaluated.
Core semantics = **30**. B03 prospectively untouched. B17 unexposed/unclassified.
Phase 5C paused. R5.42 and R5.44 halt records are unchanged.

The primary classification is **`R5_45_STATE_IDENTITY_GAP`**. Bounded decomposition
is demonstrated and synthetic certificate rejection works, but the complete
pre-exposure qualification did not succeed. Next gate: separately authorize
complete execution-state/dependency closure and freshness qualification, retaining
these stopped-round observations. A new locked B02 static transfer experiment is
**not yet the next gate**; it needs that qualification and fresh user authorization.
