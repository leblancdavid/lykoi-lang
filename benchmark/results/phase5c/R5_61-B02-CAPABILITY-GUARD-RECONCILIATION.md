# R5.61 — B02 capability-guard reconciliation

## Outcome and boundary

**`R5_61_PROTECTED_RESOURCE_GAP`**.

The stage-name collision is corrected and the new capability/resource and safe
exclusion mechanisms pass focused qualification. **Complete production
reconciliation is not qualified:** the existing bounded `child()` adapter starts
an unaudited subprocess. Allowing that launch would bypass the new Python resource
boundary; the prospective driver instead rejects it before the child starts.
Production-compatible mediated child execution remains a concrete integration gap.
The historical restricted workers also require prospective adoption of the new
pre-import exclusion adapter; they are not silently upgraded or resumed.

**B02: 0 exposure / 0 reservation / 0 dispatch / 0 completion.**
**Production: 0 batches / 0 receipts / no certificate issued.**
**Production synthetic reservation / dispatch / completion: 0 / 0 / 0.**
**Core semantics: 30. Phase 5C: paused.**

This is infrastructure evidence, not a Lykoi semantic or behavioral regression.
R5.61 stops here. No full production qualification or protected B02 observation
is authorized or begun.

## Inherited R5.60 halt and historical preservation

R5.60 remains permanently **`R5_60_PROTOCOL_HALT`**, with its failed initialization,
original sealed plan, prerequisite PASS record and zero downstream production
accounting intact. Its inherited observations are:

- R5.59 implementation continuity PASS;
- fresh QualifiedAuthority PASS, 1,083 members;
- fresh Tier-2 capsule PASS, deterministic capture/canonical reload;
- clean contamination and 30 core semantics;
- driver initialization FAIL before any production batch, receipt or certificate;
- synthetic and B02 production accounting zero;
- 1,989 then-pre-existing tracked benchmark-result files byte-preserved.

Seven restricted-harness stage IDs in that plan contain `b02`. R5.57's constructor
treated that substring as prohibited exposure before test exclusions were reached.
A stage ID is descriptive metadata; this collision does not establish an application
regression. R5.61 adds no exemption for those seven IDs and does not rename them.

Initial `git status --short` was clean. The new preservation baseline includes
**2,010 pre-existing tracked benchmark-result files**, including R5.60's subsequent
records. [Publication integrity](R5_61-evidence/publication-integrity.json) verifies
their unchanged physical bytes. Prior result files and classifications are not
rewritten. The driver keeps its compatibility filename but has a new prospective
protocol/version, `bounded-driver-r5.61-v1`; historical R5.57 implementation pins
retain their original meaning and are not updated to the new source.

## Protected capability and resource model

[`capability_guard_r5_61.py`](../../evaluation/capability_guard_r5_61.py) defines
thirteen explicit protected capabilities:

```text
B02_AUTHORITY_READ       B02_CONTRACT_READ       B02_FIXTURE_READ
B02_STATIC_EVALUATION    B02_CHECKEDPLAN         B02_READINESS
B02_AUDIT               B02_ADMISSION           B02_RESERVATION
B02_DISPATCH            B02_GENERATION          B02_EXECUTION
B02_ACCEPTANCE
```

No protected capability is grantable under the R5.61 policy or its prospective
R5.62 qualification use. Missing, non-list/tuple, duplicate, unknown and protected
declarations fail closed. The generic allow-set covers harness execution, test
discovery, regression evidence, authority/certificate linkage, continuity,
publication, validation, safety, schema and traceability.

Trusted `Resource` records bind resource identity, resolved location and protected
capability. Explicit repository designations cover the frozen request, profile,
capability contract, sealed test modules and their Python bytecode forms, and
identified semantic/profile/obligation fixtures. Registration does not read their
contents. Matching a registered location or filesystem identity is resource
identification, not an inference of authority from a filename's spelling. This
inventory is not claimed to be an exhaustive closure of every historical B02
carrier or inherited native handle.

The same model accepts synthetic protected resources whose filenames contain no
`b02`. Changing their names does not grant permission. Operational broker checks
reject protected reads/evaluation before invoking the content reader or evaluator.

## Stage declaration, binding and enforcement

Every stage constructed through the prospective bounded driver must supply an
explicit `capabilities` list or tuple, including an empty declaration when needed.
There is no implicit legacy grant. Authorization is checked before a qualification
binding is issued; missing declarations in historical callers are rejected rather
than guessed from commands, method IDs or stage names.

The binding records the normalized declaration, generic allow-set, policy version,
resource-policy identity and guard implementation digest alongside existing stage,
mechanism, lifecycle cost, authority and capsule linkage. Normalization is
deterministic and order-independent. Revalidation compares live declarations,
stage definitions and guard/resource identities with the frozen binding before
execution. A capability mutation invalidates continuation.

Stage-name mutation alone leaves the **authorization decision** unchanged.
The descriptive name remains part of journal identity/order: renaming an already
bound stage is not permission to resume or alter evidence. Syntax/path-safety
validation of journal names remains. The old stopped R5.56 experiment-identity
exclusion also remains; it is not used to determine B02 permissions.

Both stage-ID and experiment-ID B02 substring checks are removed. No replacement
substring, filename, function-name, test-name or command-text heuristic grants
access. The certificate linkage fixture now explicitly declares generic regression
capability, without changing its certificate semantics.

## Actual-access defense and concrete resource gap

During a bounded callback, a process-wide Python audit hook checks registered
resource opens, resolved aliases and filesystem identities. A synthetic hardlink
and cross-thread read are denied. Resource-broker reads and static evaluation also
check explicit capabilities. A lying generic declaration therefore cannot directly
read the registered synthetic authority or fixture.

Denial produces fixed, secret-safe protocol evidence: `R5_61_PROTOCOL_HALT`,
`quarantine: true`, and `DENIED_BEFORE_CONTENT`. The driver persists quarantine,
records the interrupted stage as INCOMPLETE/STOPPED using existing receipt rules,
and prohibits continuation. Swallowing the access exception cannot produce PASS.
These deliberately triggered halts concern disposable **synthetic** fixtures;
they are not actual B02 exposure or the R5.61 primary result.

Unmediated subprocess/native execution, descriptor-based opens and memory mapping
are refused where Python provides audit events. No OS sandbox, hostile-Python
proof, inherited-descriptor closure or complete native-library mediation is claimed.
This retains the cooperative Tier-2 methodology rather than reopening machine
hermeticity or adversarial runtime research.

**Concrete gap:** `bounded_driver_r5_57.child()` uses `subprocess.run()` with no
protected-resource enforcement inside the worker. Its `subprocess.Popen` event is
denied under the new stage boundary. The fresh synthetic witnesses verify that no
child starts and no child-result file appears. Granting a generic subprocess
capability, trusting a harmless command name, or disabling the hook would not fix
this gap. A separately qualified mediated worker/SUT execution adapter and reviewed
resource inventory are prerequisites to production use. They are not implemented
or qualified by this bounded reconciliation, and the raw adapter is not exempted.

## Restricted harness: late exclusion versus safe exclusion

The inherited R5.60 worker delegates restricted suite execution to the R5.58
worker. Its order is exactly:

1. `loader.discover()` imports test modules and constructs their cases;
2. selected exact IDs are collected;
3. prohibited test methods are replaced with callbacks raising `SkipTest`;
4. the unittest suite runs.

This is **late method exclusion**, not pre-import/pre-construction exclusion.
Unittest can perform module/class/setup work before calling that replacement
method. A limited structural-only inventory returned no `setUp`/`setUpClass`
definitions for the indexed prohibited modules, but that does not prove that
their imports and dependencies are free of protected-content loads. No contract,
assertion or fixture contents were exported by that inventory or supplied to the
SUT. It is not evidence that historical imports exposed B02, and the inherited
runner was not run against B02 here. Its pre-import protection guarantee remains
unestablished. The retained metadata utility now reads only the frozen stage plan,
not sealed test sources.

[`restricted_harness_r5_61.py`](../../evaluation/restricted_harness_r5_61.py)
provides a prospective safe selection boundary: consult the immutable, content-pinned
prohibition index **before invoking any allowed-test factory**. Prohibited entries
become decorated, fixture-free `Prohibited` placeholders. They do not import the
original module, construct its test class, execute setup, read fixtures or invoke
the SUT. Ordinary entries are delegated to the caller's allowed factory.

The fresh 36-case witness checks zero factory calls and zero new imported modules.
A synthetic dangerous factory would immediately fail if reached; it is not reached
for a prohibited case. An ordinary case is constructed and runs normally. This
qualifies the new exclusion adapter, not an unrestricted import/discovery of the
full historical harness. Production workers must prospectively adopt it and use
safe indexed selection rather than importing prohibited modules for discovery.

## Discovery versus exposure and skip accounting

A test/resource identity with an explicit `PROHIBITED` status and capability
designation is safe exclusion metadata. Knowing that B02 exists, listing an ID,
counting an exclusion or registering a path is not reading its behavioral contract.
Protected request/profile/fixture contents, assertions, evaluated results and SUT
inputs remain outside that discovery boundary.

[`prohibited_test_index_r5_61.json`](../../evaluation/prohibited_test_index_r5_61.json)
contains only the 36 pre-existing prohibited IDs and their policy designations,
derived from R5.60's frozen plan and inherited exclusion set. Its canonical identity
is pinned to
`0ff387f592dc61ac40a3d7c4c9372ab43c85a017fa6ff577c1bc2b7140b6df55`.
It contains no frozen request text, contracts, fixtures, assertions or behavior.
Removing an entry, even with canonical reserialization, is rejected.

**36 prohibited-B02 skips** are derivable from this safe index without opening a
frozen B02 contract. Fresh placeholder execution reports the same 36 skips.
Those skips are exclusion/accounting evidence, not acceptance runs or behavioral
observations. Historic non-B02 skip policies are not reinterpreted here.

## Fresh tests and focused verification

Final focused suites pass **180/180**, with no suite failures, errors or skips:

| Focused suite | Passed/discovered |
| --- | ---: |
| New capability/resource/exclusion/linkage witnesses | 30/30 |
| Bounded-driver authorization, lifecycle and continuation | 29/29 |
| Tier-2 observation controls | 43/43 |
| Canonical recorder / incomplete and exactly-one controls | 29/29 |
| Synthetic successor-authority mechanisms | 18/18 |
| R5.59 continuity | 8/8 |
| R5.59 publication/security | 9/9 |
| Generic schema/traceability/profile mechanisms | 14/14 |

The separate safe-placeholder run reports **36/36 prohibited skips**. It is not
included as 36 passing acceptance cases in the 180-test denominator.

The fresh witnesses cover all sixteen requested categories: harmless B02 and
ordinary names; protected capabilities under harmless/B02 names; mixed declarations;
undeclared direct access; synthetic authority, fixture and static-evaluation denial;
generic harness authorization; content-free skip accounting and pre-factory
exclusion; deterministic binding; mutation rejection; name-independent authorization;
and unchanged observation controls. Additional witnesses cover all thirteen
protected operations, unknown/missing/duplicate declarations, hardlink aliases,
threads, forged resource records, swallowed denial, durable quarantine/no retry,
index mutation and subprocess escape denial.

QualifiedAuthority linkage uses a sealed synthetic interface value and verifies
live-identity mutation rejection. ProductionCertificateV2 linkage assembles and
validates against fresh synthetic bounded receipts with an explicitly substituted
synthetic qualifier, then rejects mutated authority linkage. This tests the
integration interface; it is **not** a fresh 1,083-member authority qualification,
production certificate or full CertificateV2 fixture run. The existing repository
materialization fixture reads protected authority carriers and is not run here.

Fresh checks also pass closed structure/schema, **99-leaf traceability**,
implementation/profile contamination, validation, safety and repository-text
continuity of unchanged QualifiedAuthority, CertificateV2, Tier-2 and recorder
implementations. Final publication checks preserve old result bytes, scan changed
and new source/evidence, verify canonical JSON and secret-safe output, and pass
`git diff --check` plus new-file whitespace checks.

An early development run had 37 errors among 55 tests because the new binding used
a credential-reserved field name rejected by the existing publication guard.
The field was prospectively corrected without changing or exempting publication
security. The subsequent intermediate 55/55 run and final source-pinned 30/30 and
29/29 runs are retained separately. No failed check is reclassified as production
evidence or hidden; see [development checks](R5_61-evidence/development-checks.json).
The first final-integrity invocation also stopped on an incorrect historical
summary-field lookup, before issuing a publication record. R5.60 uses
`primary_classification`; the prospective reader was corrected without altering
that summary. The failed integrity attempt is retained separately in
[integrity development failure](R5_61-evidence/integrity-development-failure.json).

## Preserved controls, methodology and AI independence

No recorder, reservation/dispatch/completion, exactly-one, incomplete-observation,
second-observation or no-repair implementation is changed. Disposable synthetic
unit fixtures exercise those mechanisms; their actions are not production
observations and their receipts are not reusable qualification evidence.

R5.50's research claim, QualifiedAuthority, ProductionCertificateV2, Tier-2 capsule,
continuity/publication semantics, cooperative workspace and bounded budgeting
policy remain unchanged. Lifecycle costs, margins, boundary reserve and the
existing INCOMPLETE/STOPPED receipt behavior are preserved. The versioned change is
pre-exposure stage authorization/resource access only. Frozen compiler/runtime,
schema, language model, generated output, requirements and acceptance oracles are
unchanged. Lykoi remains a language, not an AI runtime; AI-provider state is
unrelated to this correction. No fresh broader AI-independence claim is added.

## General principle and next gate

> Security and benchmark-protocol boundaries should be enforced through explicit
> capabilities and actual protected-resource access rather than naming conventions
> whenever practical.

Names are descriptive. Capabilities are authoritative.

The naming defect is corrected, but successful local guard witnesses cannot qualify
an unmediated production subprocess or the inherited late-discovery worker.
Final classification remains **`R5_61_PROTECTED_RESOURCE_GAP`**, not
`R5_61_B02_CAPABILITY_GUARD_RECONCILED`.

**Recommendation:** separately authorize the narrow mediated child/SUT boundary
and safe indexed-worker integration qualification. Once those mechanisms are
qualified, authorize a **wholly fresh production qualification**, with explicit
capability declarations, new implementation/policy pins and fresh authority,
capsule, plan, receipts and certificate. Preserve R5.60 as halted; do not resume its
candidate, reuse its prerequisites as production PASSes or begin production from
this partial reconciliation. B02 authorization remains withheld.

Evidence: [summary](R5_61-evidence/summary.json),
[checks](R5_61-evidence/checks.json),
[commands](R5_61-evidence/commands.json),
[capability guard](R5_61-evidence/capability-guard-final.json),
[bounded driver](R5_61-evidence/bounded-driver-final.json),
[preservation baseline](R5_61-evidence/preservation-baseline.json), and
[publication integrity](R5_61-evidence/publication-integrity.json).

Commands executed for the final focused qualification:

```text
python -B -S benchmark/results/phase5c/r5_61_qualification.py baseline
python -B -S benchmark/results/phase5c/r5_61_qualification.py suite capability-guard
python -B -S benchmark/results/phase5c/r5_61_qualification.py suite bounded-driver
python -B -S benchmark/results/phase5c/r5_61_qualification.py suite observation-tier2
python -B -S benchmark/results/phase5c/r5_61_qualification.py suite recorder
python -B -S benchmark/results/phase5c/r5_61_qualification.py suite authority-synthetic
python -B -S benchmark/results/phase5c/r5_61_qualification.py suite continuity
python -B -S benchmark/results/phase5c/r5_61_qualification.py suite publication-security
python -B -S benchmark/results/phase5c/r5_61_qualification.py suite schema-traceability
python -B -S benchmark/results/phase5c/r5_61_qualification.py checks
python -B -S benchmark/results/phase5c/r5_61_qualification.py suite capability-guard final
python -B -S benchmark/results/phase5c/r5_61_qualification.py suite bounded-driver final
python -B -S benchmark/results/phase5c/r5_61_qualification.py summary
python -B -S benchmark/results/phase5c/r5_61_qualification.py integrity-diagnostic
python -B -S benchmark/results/phase5c/r5_61_qualification.py final
```
