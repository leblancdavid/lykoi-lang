# R5.57 — Bounded qualification driver budgeting repair

## Outcome and scope

**The prospective bounded driver is independently qualified for scheduling and
continuation.** This is infrastructure qualification using synthetic/non-B02
stages, not complete production Tier-2 qualification or production authorization.

Primary classification: **`R5_57_BOUNDED_DRIVER_QUALIFIED`**.

R5.56 remains **`R5_56_PRODUCTION_REGRESSION_GAP`**: five PASS receipts, 75
INCOMPLETE receipts, 87/87 completed tests, no certificate, gate preparation or
synthetic lifecycle. Its interrupted CertificateV2 stage was not retried and its
candidate was not resumed. None of its receipts is consumed here or eligible for
R5.58. Initial Git status was clean. All **1,873** pre-existing tracked research
result files, including R5.56 and its 1,763-file preservation evidence, remain
byte-identical.

**B02 exposure: zero. Core semantics: 30. Phase 5C: paused.** No B02 reservation,
dispatch, static evaluation, CheckedPlans, readiness, audit, admission, generation,
execution or frozen acceptance occurred. Production observation accounting remains
0 reservations / 0 dispatches / 0 completions. Synthetic qualification workers are
ordinary pre-exposure test processes, not locked benchmark observations.

## Inherited defect and reproduced failure class

The historical loop admitted a stage whenever elapsed batch time was below 70
seconds, then allowed a child up to 65 seconds, with state capture and evidence
completion outside that allowance. At elapsed 69 seconds, only 51 seconds remain
in a 120-second envelope. Even a 40-second worker estimate can fit while the
complete stage lifecycle cannot. The independent worker-only-fit test reproduces
this admission error and verifies rejection by the prospective policy before any
attempt marker, pre-stage capture or worker dispatch.

The historical CertificateV2 result is particularly important: R5.55 records
**103.157 seconds for its 33-test suite alone**. It cannot be safely scheduled as
one stage in a 120-second envelope under this conservative policy, even in an
otherwise empty invocation. No absent R5.56 worker result is inferred from that
historical timing.

## Stage-cost characterization

[`R5_57-evidence/stage-cost-characterization.json`](R5_57-evidence/stage-cost-characterization.json)
records available worker timings and source-byte hashes from R5.45, R5.51,
R5.55 and R5.56. These are scheduling observations, not qualification receipts.

| Stage class / available observation | Historical worker seconds |
| --- | ---: |
| R5.56 AI independence | 1.813 |
| R5.56 compiler/application | 4.985 |
| R5.56 authority mechanism tests | 0.062 |
| R5.56 staged certificate tests | 0.719 |
| R5.55 CertificateV2 | 103.157 |
| R5.55 Tier-2 mechanisms | 10.516 |
| R5.55 recorder / methodology / security | 1.922 / 1.563 / 0.484 |
| R5.45 historical monolithic harness | 118.187 |

Prior artifacts do **not** separately measure setup/capture, process startup,
teardown, post-capture, serialization/persistence or receipt finalization. Their
individual historical values remain **unmeasured**. The 120-second interruption
is an enclosing bound, not a measured distribution for those components. For
non-suite authority/workspace/coherence/validation stages without worker timing,
the unseen-class fallback applies. Timing evidence does not establish that all
future stage classes are fast.

Fresh production-driver dry evidence separately records actual small synthetic
capture and child wall times. For example, batch 1 captures range approximately
0.078–0.120 seconds and children approximately 0.093–0.095 seconds. These small
synthetic scopes do not calibrate a full production capsule. Startup, execution
and shutdown remain combined in that child measurement; no invented subdivision
is reported.

## Full-lifecycle budget model and explicit margin

Implementation: [`benchmark/evaluation/bounded_driver_r5_57.py`](../../evaluation/bounded_driver_r5_57.py).
Production integration: [`r5_57_driver.py`](r5_57_driver.py).
Historical R5.56 driver bytes remain unchanged. The integration accepts freshly
supplied capsule, authority identity, fixed ordered stages and live verification
callbacks; it offers no observation API and rejects R5.56 continuation and B02
identifiers.

All costs are seconds. The production allowance model is:

| Lifecycle component | Conservative allowance |
| --- | ---: |
| Pre-stage setup/state capture | 12 |
| Process startup | 3 |
| Worker execution, including worker-result persistence | max(35, available worker estimate) |
| Process shutdown/teardown | 3 |
| Post-stage capture | 12 |
| Canonical evidence generation/serialization | 2 |
| Durable receipt persistence/finalization | 2 |
| Canonical reload/integrity confirmation | 2 |

`total = sum(all eight components)`

`margin = max(15 seconds, 25% of total)`

`required = total + margin + 5-second batch-boundary reserve`

For unseen classes, the worker allowance is **65 seconds**, giving a required
budget of **131.25 seconds**. Such a stage is conservatively **not admitted** in
a 120-second invocation. This is intentional: unseen work needs prior bounded
calibration or smaller predeclared units, not an optimistic guess. A measured
small class receives a 35-second worker floor: total 71, margin 17.75, required
93.75 seconds. The historical CertificateV2 suite requires about **178.946
seconds**, and is rejected as a monolithic stage.

The fixed capture/process/persistence allowances are engineering allowances,
not claims of historical component measurements. The worker floor and substantial
absolute/proportional margin cover ordinary startup, filesystem, serialization,
scheduler and runtime variation. They deliberately favor reliability over window
utilization. Caller-supplied costs are part of the immutable qualification
identity; they cannot be silently reduced between batches to improve throughput.

Default internal invocation budget is **110 seconds**, leaving external launch
headroom inside a 120-second tool limit. Production callers can pass the entry
timestamp so imports/startup count against the envelope. Initial continuation
verification is timed before admission. Every subsequent decision uses the
remaining budget, including elapsed validation and completed-stage work. The
child timeout is further capped after pre-capture to preserve post-capture,
persistence, integrity, margin and boundary reserve. An unexpected overrun cannot
be relabeled PASS merely because a child previously wrote a result.

## Admission, clean boundaries and continuation

Before each stage, compare remaining invocation time with its conservative full
lifecycle requirement. Only a successful comparison permits an exclusive durable
attempt marker, pre-stage capture and child execution. On insufficient budget:

1. do not begin the stage or create its attempt/receipt;
2. preserve all completed canonical receipts;
3. persist and reload a sealed batch journal;
4. return normally with `BOUNDARY` and the exact next stage.

An unadmitted stage is **pending**, not INCOMPLETE or a qualification failure.
There is no requirement to fit the complete stage set into a single invocation.
An oversized stage remains pending until a separately defined fresh stage plan
provides units that fit; mutating the existing pinned plan is rejected.

The qualification binding includes experiment identity, capsule identity,
authority identity, protocol/version, actual scheduler implementation hash, ordered
stage mechanisms and lifecycle cost model. Journals link their predecessor hash,
exact new receipt-byte digests, decisions, disposition and next required stage.
Receipt and attempt seals, canonical bytes, capsule/experiment/mechanism links,
stage sequence and predecessor linkage are validated before continuation. Receipt
maps are interpreted in the **pinned stage sequence**, not JSON mapping order.

Live state and authority must still match. State, authority, receipt, driver
version, stage-plan or qualification identity mutation rejects continuation before
further work. No compatible migration is supplied. Within a future fresh R5.58,
earlier R5.58 batch receipts can continue only under these checks. Historical
R5.56 receipts are never a source of fresh qualification evidence.

The trust boundary remains R5.50's cooperative workspace with ordinary reliable
exclusive-create/fsync behavior. Hash linkage detects accidental evidence mutation;
it is not hostile-host attestation or protection against deliberate reconstruction
of an entire locally trusted evidence history. Live capture callbacks must cover
the relevant qualification state as required by the unchanged methodology.

## Interrupted admitted-stage semantics

Attempt markers are durably written with `INCOMPLETE`. Timeout, capture failure,
invalid worker evidence, publication rejection or unexpected exception produces an
INCOMPLETE receipt and `STOPPED`, never inferred PASS. A child exit failure yields
FAIL with diagnostics withheld. Detected before/after drift uses unchanged Tier-2
receipt behavior and fails closed. Neither stopped case is silently retried.

If the parent is actually killed before final receipt/journal persistence, an
orphan attempt remains durable INCOMPLETE evidence. Subsequent validation rejects
the candidate; it does not infer the worker result or rerun it. The synthetic
suite challenges both a timeout callback and an actual terminated child that
writes successful-looking output before remaining blocked.

This batching policy applies only to **pre-exposure qualification**. The existing
recorder and StaticGate observation machinery were not changed. An interrupted
locked synthetic observation still halts permanently and rejects a second dispatch,
as freshly exercised by the budgeting tests and existing recorder/Tier-2 suites.

## Synthetic multi-batch and production-driver dry qualification

Final evidence: [`R5_57-evidence/dry-qualified/`](R5_57-evidence/dry-qualified/).
The real production integration and subprocess adapter execute six non-B02
synthetic stages, with actual Tier-2 capture, canonical child-result files,
durable standard receipts and integrity-bound journals.

Three **separate process invocations** use artificial budgets 49, 39 and 29
seconds. Each synthetic cost totals 9 seconds, with a 15-second margin and
5-second boundary reserve: required admission budget 29. The artificial clock
debits 10 seconds per completed stage; actual wall timing is recorded separately.
It intentionally makes the six-stage qualification unable to fit in one test
invocation, without making tests wait for artificial wall deadlines.

| Invocation | New receipts | Disposition | Next stage |
| --- | --- | --- | --- |
| 1 | PASS PASS PASS | BOUNDARY | synthetic-3 |
| 2 | PASS PASS | BOUNDARY | synthetic-5 |
| 3 | PASS | COMPLETE | none |

Each invocation validates the previous receipts/state/authority, and completion
is recognized only after all six PASS receipts exist. No stage is interrupted
because the artificial batch budget expires. This is a scoped driver dry
qualification, not the complete R5.56/R5.58 regression suite, production gate
preparation or a production observation lifecycle.

## Fresh affected verification

Canonical, secret-safe result records reside in [`R5_57-evidence/`](R5_57-evidence/).

| Verification | Final result |
| --- | --- |
| New budgeting/adversarial/real-child tests | **29/29 PASS** |
| CertificateV2 assertions plus scheduler-to-certificate receipt linkage | **34/34 PASS**, two bounded groups of 17 |
| Tier-2 production mechanism regressions | **43/43 PASS** |
| Canonical recorder/evidence | **29/29 PASS** |
| Staged CertificateV1 mechanisms | **33/33 PASS** |
| QualifiedAuthority successor mechanisms | **18/18 PASS** |
| R5.50 methodology constraints | **18/18 PASS** |
| R5.47 publication/security | **22/22 PASS on this checkout** |
| Compiler/application, including schema/manifest/trace-ID checks | **31/31 PASS** |
| Synthetic profile schema/structure and 99-leaf traceability | PASS |
| Implementation/profile contamination and core count | PASS / 30 |
| Model validation / safety | PASS / zero capability violations and invalid transitions |
| Final prior-result preservation, canonical publication and receipt rehash | PASS / 1,873 unchanged files / six receipts |
| `git diff --check` | PASS |

Final focused tests total **257/257 PASS**. They do not represent complete
production Tier-2 qualification. Earlier historical security outcomes retain
their own checkout-specific observations; this fresh 22/22 result does not
retroactively reclassify them.

### Preserved development failures and prospective fixture

The original budgeting run had 25 PASS / one fixture-setup ERROR: its observation
test accidentally shared an already-populated qualification evidence directory.
It was corrected to use a separate fresh observation directory.

The old CertificateV2 fixture failed before running tests on both the active
checkout and a separate LF clone. Its raw manifest is noncanonical on the active
checkout; four authorized additions have LF/CRLF differences against repository
content pins, and three predecessor manifests require their independently pinned
CRLF physical representation. No authority mechanism or historical file was
changed to bypass these checks.

`test_certificate_driver_r5_57.py` declares a prospective synthetic fixture before
qualification: canonical manifest, hash-confirmed LF authorized additions, pinned
research-prose blobs and hash-confirmed predecessor CRLF representations selected
from Git content. It uses unchanged QualifiedAuthority v1 and CertificateV2 APIs
with a freshly pinned explicit fixture authorization. This is fixture materialization,
not recovery of missing historical preimages, historical lock reclassification,
production baseline issuance or reuse of old receipts. All 33 unchanged adversarial
certificate assertions pass on that fixture.

The first new scheduler/certificate-linkage witness exposed canonical-map ordering
loss (33 PASS / one ERROR across its two groups). Validation was corrected to use
the fixed stage sequence. A new nonlexical-order witness and fresh 34/34 certificate
checks pass. The earlier dry run is preserved under `dry/` as development evidence;
only the separately initialized `dry-qualified/` binds the final scheduler bytes.
Earlier result files and failures are retained, not overwritten into PASS.

## Security, architecture and boundaries

All JSON evidence uses the unchanged R5.47 publication guard before exclusive
creation, flush/fsync and canonical reload. Timing diagnostics contain numeric
costs, stage IDs, status and hashes. They do not publish environment dumps,
credential-bearing commands, stdout/stderr or arbitrary exception messages.
Synthetic secret-bearing results are rejected and exception text is withheld.
The final audit independently rehashes receipts and checks the scheduler code pin.

R5.50 methodology, R5.53 authority, QualifiedAuthority v1, ProductionCertificateV2,
observation restrictions and the cooperative threat model are unchanged. Compiler,
runtime, schema, semantic profiles and generated artifacts are unchanged. Lykoi
remains AI-independent; Git remains provenance/research infrastructure. No new
language concept or semantic #31 is introduced.

## Recommendation for R5.58

Separately authorize a **fresh complete production Tier-2 qualification**, using
the prospective production scheduler across as many clean bounded invocations as
needed. Before freezing its fresh capsule, predeclare smaller CertificateV2 test
groups with complete membership and method identities, and conservative lifecycle
budgets. The measured 103.157-second monolithic suite and uncalibrated fallback
must not be squeezed into a 120-second stage. Calibrate or subdivide other oversized
classes before the fixed plan is captured; do not tune a frozen candidate's model
between batches.

Every required fresh receipt must validate against the same qualified state before
certificate assembly and live production-gate integration. Driver qualification
does not establish that the previously unreached CertificateV2/StaticGate integration
will pass. R5.58 must freshly verify it. R5.57 performs none of that complete gate
qualification and authorizes no B02 exposure.

**`R5_57_BOUNDED_DRIVER_QUALIFIED`**
