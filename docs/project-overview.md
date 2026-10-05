# Lykoi: project overview and direction

**The project is named Lykoi, not Axiom.** `axiom` appears in historical
filenames, serialized version keys, benchmark track IDs and pinned research
records; `air/` and `air_compiler` remain compatibility paths. Those names do
not rename the project. Historical evidence retains its original spelling so
that saved models, hashes and checkpoints remain reproducible.

## Long-term goal

Lykoi is an experiment in AI-native programming-language design. Its central
research question is: **what is the smallest general-purpose semantic
vocabulary from which an AI can reliably compose complex software?** The
proposed direction is to distill programming into general, composable,
unambiguous, machine-friendly concepts rather than imitate human-oriented
syntax, assemble code-generation templates, or add a benchmark-specific
primitive for each new feature. This is a research hypothesis, not an
established minimum or a claim that the current vocabulary is general-purpose.

The intended architecture is human intent → AI interpretation → Lykoi semantic
representation → validated, compiler-controlled transformation → executable
implementation/runtime → observable behavior. The semantic model, rather
than a generated Python file, is the source of truth. Python is the first
backend, not the definition of the language.

The goal is to make changes easier to reason about and safer to maintain:
identify affected behavior by stable semantic relationships, reject known
invalid states and unauthorized effects before generation, make migrations
explicit, and connect generated artifacts and verification evidence to their
model. Longer term, correctness should move into language semantics,
constraints, compiler/runtime guarantees and validated infrastructure
adapters, so more properties hold by construction rather than by repeatedly
repairing generated application code. Tests remain important for Lykoi's
semantics, compiler/runtime, adapters, intent interpretation and independent
evaluation; they are not a target to fit. This is a research direction, not
a claim of general correctness or that Lykoi already outperforms conventional
programming. The current language supports a bounded task-management domain;
broader operations, stronger verification, more precise provenance and other
backends require further language and compiler work. Core semantics and
external resources such as storage, time and IDs should remain distinguishable.

## Work completed

- **Semantic foundation (v0.1–v0.3).** A task-manager model now represents
  types, states, behaviors, commands, capabilities, contracts, invariants,
  migrations, lifecycle transitions and scoped authority. The closed-world
  validator checks cross-references and effect/authority consistency. The
  Python backend generates the task CLI; its generated file is not hand-edited.
  See [v0.2](axiom-v0.2.md) and [v0.3](axiom-v0.3.md) for the language boundary.
- **Maintenance tools and experiments.** `inspect`, `diff` and `impact` expose
  semantic relationships; `plan` and `apply` support hash-pinned, validated
  changes with staged verification and rollback on failure. Priority, explicit
  storage migration and due-date experiments exposed missing language concepts
  and tested reusable extensions. Generated manifests record artifact-level
  provenance. Phase 4 added lifecycle checks, least-authority declarations and
  safety evidence labels. The observations and limitations are in the
  [research log](research-log.md).
- **Comparative benchmark.** Phase 5 established a frozen conventional Python
  baseline, an external behavioral oracle and twenty ordered maintenance
  requests. A pilot and subsequent checkpointed execution tested the two
  tracks; Lykoi has a documented B02 language capability gap. The protocol
  was repaired prospectively to address workspace observer effects, divergent
  achieved feature sets and acceptance-case supersession. The two authoritative
  post-B16 histories are Conventional B01–B16 and Lykoi {B01,B04}; their
  corrected acceptance suites were independently revalidated. These are
  observed benchmark states, **not** a completed twenty-request comparison or
  evidence of a winner. See the [benchmark protocol](../benchmark/README.md)
  and [post-B16 corrected boundary](../benchmark/results/phase5c/R5_2_2-POST-B16-CORRECTED-CONTINUATION.md).

## Current boundary and next steps

The [R5.54 fresh production qualification](../benchmark/results/phase5c/R5_54-FRESH-PRODUCTION-TIER2-STATIC-GATE-QUALIFICATION.md)
ends **`R5_54_PRODUCTION_CERTIFICATE_GAP`**. Fresh validation of the trusted
1,083-member R5.53 successor, provenance/ancestry/frozen pins and separate checkout
representation passes. A dedicated 2,013-file cooperative copy yields deterministic
capsule capture and canonical round trip; historical physical locks retain their
original FAIL counts. The existing R5.51 certificate rejects successor authority
and still requires the superseded three physical locks. No certificate is issued.
Qualification stops: seven preflight entries PASS, one FAIL, 24 downstream entries
INCOMPLETE; no fresh full regression or production observation-control qualification
is claimed. Final integrity preserves 1,707 pre-existing benchmark-result files.

Next: address the concrete certificate/live-authority successor-policy integration
with the smallest prospective adapter, then freshly complete production qualification.
Do not resume the stopped candidate, expand the R5.50 claim or proceed to B02.
**Production synthetic observations zero, B02 zero, core 30, Phase 5C paused.**
Earlier recommendations and observations below retain their historical boundaries.

The [R5.53 authority adjudication](../benchmark/results/phase5c/R5_53-UNRESOLVED-AUTHORITY-PROVENANCE-AND-SUCCESSOR-BASELINE-ADJUDICATION.md)
ends **`R5_53_SUCCESSOR_PROVENANCE_QUALIFIED`**. All eight missing historical
preimages remain explicitly unavailable; all eight current repository versions
have traceable Git/report/carrier-commit provenance and explicit content-bound
prospective authorization. None is frozen behavioral authority. The separately
versioned **1,083-member** repository-content successor independently qualifies;
checkout representation is separately recorded (**56 exact / 1,027 LF/CRLF**).
Historical physical locks retain FAIL and their original counts; no old result
is retroactively normalized into PASS. R5.47 security and all 81 R5.51 receipts
remain preserved. Fresh tests: R5.53 **18/18**, R5.52 **22/22**, application **31/31**,
methodology **18/18**, Tier-2 mechanisms **43/43**; generic schema/99-leaf traceability,
contamination, validation/safety and core **30** pass. Full security retains its
two diagnosed historical assertions, **20 pass**. Harness observations remain
active **338/36/55**, LF **393/36/0**, explicitly inherited from R5.52.

Next: separately authorized **R5.54 fresh production Tier-2 qualification**
against this successor and its [versioned authority policy](authority-successor-r5.53.md).
R5.53 qualifies the starting authority baseline only; no production capsule,
certificate or B02 exposure follows. **B02 zero, core 30, Phase 5C paused.**
Earlier records below preserve their historical boundaries and recommendations.

The [R5.52 checkout/authority reconciliation](../benchmark/results/phase5c/R5_52-CHECKOUT-AUTHORITY-AND-LOCK-PROVENANCE-RECONCILIATION.md)
ends **`R5_52_CONTENT_PROVENANCE_GAP`**. Historical physical lock meaning is
preserved. Fresh raw matches remain **145/678**, **145/695**, **145/1,065**;
proven representation-only counts are **524**, **541**, **911**. Nine of R5.51's
18 residual mismatches are inverse CRLF→LF representation changes; one README
addition is explicitly R5.50 methodology evolution; **eight physical authority
hashes remain unrecovered/UNKNOWN**. No successor lock or production baseline
is issued, and no physical lock is relabeled PASS through normalization.

All four frozen-pin failures are proven LF/CRLF materialization; a separate clean
LF HEAD checkout reproduces their original raw hashes. Paired restricted harness:
active **338 pass / 36 skips / 55 errors**, clean **393 pass / 36 skips / zero errors**,
429 discovered each. All 55 inherited IDs reproduce and group into seven raw-byte
integrity gates. New diagnostics **22/22**, application/compiler **31/31**, R5.50
methodology **18/18**, Tier-2 **43/43**, schema/99-leaf traceability, contamination,
validation/safety and core 30 pass. Full security remains 20 pass/two diagnosed
historical host assertions; R5.47 protections are preserved. No observed behavioral
regression or unauthorized frozen content mutation follows from these differences.

R5.51 remains its original certificate gap with all 81 receipts preserved.
Resolve the eight historical preimages/provenance before authorizing a versioned
repository-content/checkout-materialization successor and fresh production gates.
R5.53 cannot qualify production directly from this diagnostic LF clone: its
historical physical locks still have 17/17/18 mismatches. **B02 zero, core 30,
Phase 5C paused.** Earlier records retain their historical conclusions.

The [R5.51 capsule/static-gate investigation](../benchmark/results/phase5c/R5_51-TIER2-EXPERIMENTAL-CAPSULE-AND-STATIC-GATE-QUALIFICATION.md)
ends **`R5_51_TIER2_CERTIFICATE_GAP`**. New Tier-2 capture, production-shaped
certificate and cooperative synthetic gate mechanisms pass **43/43** tests and
an independently recorded exactly-one synthetic lifecycle. A byte-preserving,
cache-free dedicated copy binds actual committed/index/worktree content, relevant
dependencies/configuration and declared Windows AMD64 / CPython 3.12.10 platform;
development AI state is excluded and ordinary native descendants are declared.

All **81 bounded stages** finish: **59 PASS, 22 FAIL, zero INCOMPLETE**. Restricted
harness: 429 discovered, 338 passes, 36 preserved skips, 55 failures/errors.
Compiler/application 31, R5.41 focused 14, recorder 29, certificate 33, R5.50
methodology 18 and AI independence 5 pass. Generic 16-profile/84-row coherence,
schema/99-leaf traceability, contamination, validation/safety and core 30 pass.
Full R5.47 security retains its two documented historical failures (20 pass).

Required physical byte locks fail: historical **145/678**, prospective **145/695**,
R5.47 successor **145/1,065**. Successor mismatches comprise 902 CRLF-only and
18 additional content differences; original identities and ancestry pass. Four
frozen-authority physical pins also fail. These initial-checkout differences are
preserved, with no repair, normalization, bypass or production certificate.
Final evidence integrity passes without promoting failed qualification. Next:
separately authorized checkout/authority/lock-provenance and restricted-regression
reconciliation, then a fresh qualification before any authorized B02 static gate.
B02 exposure **zero**, core **30**, Phase 5C paused. Earlier records below retain
their historical results and recommendations.

The [R5.50 methodology review](../benchmark/results/phase5c/R5_50-BENCHMARK-REPRODUCIBILITY-BOUNDARY-REVIEW.md)
qualifies a prospective **Tier 2 experimental-reproducibility boundary**. Phase 5
asks about required externally observable behavioral equivalence, not identical
implementation or a hermetic/hostile-machine guarantee. Bind relevant subject,
semantics/compiler/profile, authority, evaluator, dependency implementations and
effective controls; declare ordinary Python/OS/native platform infrastructure.
Individually bind native components with a documented claim-relevant materiality
reason. Dedicated cooperative workspace and immediate before/after state checks
protect against reasonable accidental drift; absolute malicious ABA resistance
and unlimited CRT/OS descendant closure are deferred to stronger future claims.
Development models/providers/credentials/editors are authoring state, not core
language execution identity. Authoring fairness records remain separate.

Fresh focused witnesses pass **105/105** (new boundary 18, certificate 33,
canonical recorder 29, publication/security 20, AI independence 5). The first
107-test run remains FAIL: one corrected fixture exception expectation and two
preserved historical Git/checkout assertion failures (CRLF bytes and negated
ignore-rule matching). Those two checks are explicitly excluded from the focused
result; historical lock qualification on this host is not claimed. This is
methodology qualification, **not** a production capsule/certificate or evidence
reuse authorization. R5.49 diagnostics remain non-reusable; all earlier outcomes
and recommendations below remain historical.

Next: a separately authorized new Tier 2 locked static-transfer experiment with
generic capsule-adapter preflight, required-state verification, frozen-authority
integrity, zero new-run accounting, exactly one recorded static observation,
immediate final state check and stop. None of those steps was performed against
B02 here. B02 exposure **zero**, core **30**, Phase 5C paused. No automatic exposure,
generation/execution/acceptance or benchmark continuation follows.

The [R5.49 dependency-provenance investigation](../benchmark/results/phase5c/R5_49-DEPENDENCY-PROVENANCE-AND-COMPLETE-EXECUTION-CAPSULE-QUALIFICATION.md)
ends **`R5_49_DEPENDENCY_CLOSURE_GAP`**. Generic resolved-source/content provenance
correctly attributes package, nested, generated, namespace and copied deployment
implementations without helper-name exceptions; eight actual acoustic deployment
helpers resolve to repository sources. External installed/editable implementations
remain distinct or fail closed when unattributed. Fresh PE observations expose
unbound interpreter/CRT/crypto native descendants. A synthetic ABA attack also
demonstrates that final recapture alone does not establish ownership.

All **78 bounded diagnostic receipts** pass against one explicitly incomplete
diagnostic identity; none is reusable for production. Restricted harness 393 passes /
36 preserved skips; compiler 31, focused 14, recorder 29, certificate 33, security 22,
publication 2, historical prototype freshly replayed 52, new provenance 24,
AI-independence 5 and ownership-counterexample 1. Matrix/schema/99-leaf traceability,
contamination, validation/safety and locks pass. R5.47 remains 1,065/1,065 with its
unchanged identity. R5.46/R5.48 evidence is preserved; no receipt reuse or run repair.
No qualified ExecutionCapsuleV2, production certificate or exclusive seal follows.
AI independence remains policy with fresh bounded observations. Next: implement
complete per-computation native/descendant and effective Git/context closure plus
immutable ownership before a separately versioned fresh production qualification.
Zero B02 exposure, core 30, Phase 5C paused. Earlier records retain their conclusions.

The [R5.48 execution-state/AI-independence investigation](../benchmark/results/phase5c/R5_48-EXECUTION-STATE-AND-AI-INDEPENDENCE.md)
ends **`R5_48_PROTOCOL_HALT`**. Of 74 planned bounded stages, 71 receipts were
recorded (70 PASS, one failed dependency inventory) and all are quarantined.
The inventory's direct-import screen misclassified seven repository-owned standalone
runtime/helper imports as third-party dependencies. The failed gate is preserved;
the frozen run was not repaired or resumed. Native/descendant/environment/Git closure
and exclusive production TOCTOU ownership remain unqualified; no production
certificate or qualified v2 execution capsule follows.

**Lykoi is an AI-native language, not an AI runtime.** The
[AI-independence policy](ai-independence-r5.48.md) separates development authorship
from semantic authority. Inspected direct core imports and isolated network-denied,
site-disabled probes support validation, deterministic lowering and read-only
execution without AI/OpenCode credentials/services; synthetic credential/model/editor
changes leave core identity/output unchanged. The fresh 52-test suite passes within
that bounded scope. These observations do not qualify the halted investigation.

Before quarantine: restricted harness 393 passes / 36 preserved skips; compiler
31, focused 14, recorder 29, certificate 33, security 22, publication 2; matrix,
schema, 99-leaf traceability and contamination pass. Separate stopped diagnostics
pass validation/safety/diff; they do not replace the three unrun qualification
stages. R5.47 successor 1,065/1,065, historical 678/678 and prospective 695/695
locks remain valid; R5.43 history and all R5.46 quarantined receipt hashes remain
unchanged. Next: separately authorize a corrected prospective inventory resolver
and complete execution-capsule/ownership qualification. Zero B02 exposure; core
30; B03 prospectively untouched; B17 unexposed/unclassified; Phase 5C paused.
Earlier records below retain their original conclusions and recommendations.

The [R5.47 security/infrastructure reconciliation](../benchmark/results/phase5c/R5_47-SECURITY-RECONCILIATION-AND-INFRASTRUCTURE-LOCK-SUCCESSOR.md)
ends **`R5_47_SECURITY_RECONCILIATION_QUALIFIED`**. The intentional `.gitignore`
correction is preserved; contextual scans of sharing candidates, index, reachable
local/remote-tracking history and archive members find no unresolved credentials.
External rotation remains `ROTATION_STATUS_EXTERNAL_OR_UNVERIFIED`; unavailable
remote history is not attested. A versioned publication guard rejects credential
fields/recognizable credential text before persistence, with redacted diagnostics.
See [secret-safe publication policy](security-evidence-r5.47.md).

The immutable R5.43 lock remains historical (730/731 live matches); the separate
**1,065-member R5.47 v2 infrastructure successor** verifies and reproduces
independently. Historical 678/678 and prospective 695/695 locks pass. Restricted
harness: 393 passes / 36 preserved skips; application/compiler 31, R5.41 focused
14, recorder 29, staged certificate 33 and security tests 22 pass. R5.46 remains
permanently halted with all 16 receipts quarantined and its identity prototype
**unqualified**. No identity qualification or production certificate follows.
Next: separately authorize R5.48 fresh execution/dependency-identity qualification
against this successor and integrate the secret-safe publication boundary.
B02 sealed; core 30; B03 prospectively untouched; B17 unexposed/unclassified;
Phase 5C paused. Earlier findings below remain historical.

The [R5.46 execution-state identity investigation](../benchmark/results/phase5c/R5_46-COMPLETE-EXECUTION-STATE-AND-DEPENDENCY-IDENTITY-QUALIFICATION.md)
ends **`R5_46_PROTOCOL_HALT`**. Concurrent repository/security correction changed
state during verification; before/after hashing rejected a successful worker's
stage. Fifteen earlier PASS receipts and the failed sixteenth receipt are
quarantined; the full 74-stage run did not complete. Historical 678/678 and
prospective 695/695 locks remain valid; the live R5.43 infrastructure lock now
matches **730/731**, with `.gitignore` changed. No successor was issued.

The new execution-identity/certificate bridge is an **unqualified synthetic-only
prototype**. Its initial 46 tests errored in setup; the corrected, expanded
49-test suite was not reached before halt. Complete runtime/native/import/tool
dependency closure and effective environment remain unresolved; no production
certificate, reusable stage evidence or TOCTOU qualification follows. The owner's
[R5.45 security correction](../benchmark/results/phase5c/R5_45-SECURITY-REDACTION.md)
is preserved; its redacted snapshot intentionally fails its historical seal.
Next: separately authorized security/infrastructure-lock reconciliation and a
versioned successor, then complete execution-capsule qualification from an
exclusively owned state. B02 completely sealed; core 30; B03 prospectively
untouched; B17 unexposed/unclassified; Phase 5C paused. Earlier findings remain
historical, not current-state certification.

The [R5.45 pre-exposure reliability investigation](../benchmark/results/phase5c/R5_45-PREEXPOSURE-VERIFICATION-RELIABILITY-AND-BOUNDED-EXECUTION.md)
ends **`R5_45_STATE_IDENTITY_GAP`**. Bounded module stages preserve the 429-test
restricted harness (393 passes / 36 skips), 31 compiler/application, 14 focused
R5.41 and 29 recorder tests; 33 synthetic certificate tests pass. The independent
16-profile/84-row matrix, validation/safety/schema/99-leaf traceability and
contamination pass. Historical 678, prospective 695 and R5.43 infrastructure 731
byte locks remain unchanged. Accumulated regressions explain inadequate monolithic
120-second headroom; R5.44's exact interruption position remains unknown.

The repository snapshot does not yet establish complete Git/runtime/dependency/
effective-environment identity. Qualification stops at that boundary; no production
certificate or B02 exposure is authorized. The [draft staged protocol](preexposure-r5.45.md)
and synthetic prototype are prospective only. R5.43 remains the latest qualified
infrastructure. Next: separately authorized complete execution-state/dependency
identity qualification before any new locked B02 static transfer experiment.
R5.42/R5.44 remain permanent halts; core 30, B03 prospectively untouched, B17
unexposed/unclassified, Phase 5C paused. Earlier records retain their conclusions.

The [R5.44 newly authorized locked static-transfer experiment](../benchmark/results/phase5c/R5_44-NEWLY-AUTHORIZED-LOCKED-WHOLE-CONTRACT-STATIC-SUPPORT-TRANSFER.md)
ends **`R5_44_PROTOCOL_HALT`**, before B02 exposure. Its pre-exposure verification
command was terminated at the 120-second tool limit before persisted verification
or an experimental starting seal. No retry occurred. The qualified R5.43 recorder
preserves a stopped-run accounting baseline: zero reservations, zero completed
observations and HALT. B02 CheckedPlans/readiness/audit/admission/compatible-path
support are not evaluated. Interrupted regression results are incomplete, not
reported as passes. Historical 678, prospective 695 and infrastructure 731 byte
locks remain valid; frozen authority is unchanged and contamination is clean.
Core 30, zero generation/execution/acceptance/repair, B03 prospectively untouched,
B17 unexposed/unclassified, Phase 5C paused. Next: separately authorized
investigation of the verification interruption before a new transfer experiment.
R5.44 is stopped; R5.43 qualification and R5.42 halt remain preserved.

The [R5.43 canonical-evidence infrastructure qualification](../benchmark/results/phase5c/R5_43-EVALUATION-INFRASTRUCTURE-CANONICAL-EVIDENCE-QUALIFICATION.md)
ends **`R5_43_EVALUATION_INFRASTRUCTURE_QUALIFIED`**. A separately versioned
recorder compares immutable canonical JSON bytes, preserves meaningful scalar,
field and sequence distinctions, rejects corruption and enforces one controlled
observation through exclusive reservation and linked receipts. Independent
synthetic success and mismatch simulations pass; incomplete dispatches halt as
indeterminate, without retry. See the explicit local trust boundary in the
[canonical evidence protocol](canonical-evidence-r5.43.md).

Verification: 29/29 independent qualification tests, repeated; 429 harness
discovered / 393 passed / 36 prohibited-B02 skips; 31/31 application/compiler;
14/14 R5.41 focused; 16 coherent profiles / 84 rows; validation/safety and
independent structural/traceability/contamination pass. Historical 678, R5.41
prospective 695 and new infrastructure 731 byte locks pass. R5.42 remains
permanently `R5_42_PROTOCOL_HALT`. Zero B02 exposure, static passes, generation,
execution or acceptance. Core 30, B03 prospectively untouched, B17
unexposed/unclassified, Phase 5C paused. Next: a **newly authorized** locked
whole-contract static support-transfer evaluation, not an R5.42 retry. It has
not begun. Earlier records retain their historical conclusions below.

The [R5.42 locked static support-transfer review](../benchmark/results/phase5c/R5_42-LOCKED-WHOLE-CONTRACT-STATIC-SUPPORT-TRANSFER.md)
ends **`R5_42_PROTOCOL_HALT`**, before B02 exposure. The new recorder's pre-pass
native Python matrix comparison rejects tuple/list differences introduced by JSON
round-tripping; a stopped-run integrity diagnostic finds identical canonical
matrix evidence. The gate was not corrected or retried. Complete B02 support,
readiness, audit and admission are **not evaluated**; zero B02 static passes,
generation, execution or frozen acceptance occurred.

R5.41 capability remains preserved: 14/14 focused tests; 16 coherent profiles / 84
matrix rows; 364 harness passes with 36 prohibited-B02 skips; 31/31 compiler tests;
validation/safety/structural/821-leaf traceability/contamination pass; 678 historical
and 695 prospective lock members unchanged. Core remains 30/no #31; no
implementation/profile repair. B03 prospectively untouched, B17 unexposed and
unclassified, Phase 5C paused. Recommend separately authorized R5.43 evaluation
infrastructure investigation before any new locked static review. Earlier records
retain their historical conclusions below.

The [R5.41 independent optional-boundary support review](../benchmark/results/phase5c/R5_41-INDEPENDENT-OPTIONAL-BOUNDARY-SUPPORT-COHERENCE.md)
ends **`R5_41_SUPPORT_COHERENCE_READY`**. The existing nullable scalar binder was
already compositional; prospective transport admission now follows its underlying
decoder's representation support. Durable finite domains distinguish absent
optional membership from present values, including explicit null. A sealed
prospective public bundle validates staged post-state before committing writes.
Readiness and supplemental audit consume one compatible boundary-path assessment.
Historical implementation/profile/evidence bytes remain preserved.

Independent evidence: 16 profile configurations (14 supported, two Boolean/text
rejected) agree across readiness/audit/admission; 84 value-state probes; 15 grounded
conformant public calls over integer/string/instant; 14 focused tests. Verification:
400 harness discovered, 364 pass, 36 prohibited-B02 skips; 31/31 application/compiler;
validation/safety/structural/99-leaf traceability/contamination pass; historical
678-file authority preserved; prospective 695-file lock and diff check pass.
Zero B02 static passes, generation, execution or acceptance. Core 30/no #31,
Phase 5C paused, B03 prospectively untouched, B17 unexposed/unclassified. Next:
R5.42 separately authorized, locked whole-contract static support transfer review.
Policy: [R5.41 optional-boundary support](optional-boundary-support-r5.41.md).
Earlier records retain their historical conclusions below.

The [R5.40 boundary-profile admission and B02 configuration review](../benchmark/results/phase5c/R5_40-BOUNDARY-PROFILE-ADMISSION-B02-CONFIGURATION.md)
ends **`R5_40_GENERIC_CAPABILITY_GAP`**. A prospective aggregate admission policy
rejects silently unmapped optional invocation inputs on independent seed-bank
and publication profiles; historical R5.39 admission remains reproducible.
Frozen-authority B02 metadata supplies seven public routes, four state alternatives
and all 15 unchanged operation contracts. Equal legacy codecs with separate V2/V3
identities use existing equality constraints; no version-domain algorithm is needed.
All 821 profile leaves are traced; the structural/source/contamination audit passes
as CONFIGURATION_ONLY, but complete checked transport/aggregate admission fails.

After a 678-file lock, one static-only v2 pass returns **NOT_READY**, with 15/15
CheckedPlans. Plain-text supplied due-date is incompatible with the current
nullable decoder's JSON representation requirement. Independently, an admitted
population finite-domain declaration rejects absent optional fields; static
profile checks expose this for legacy priority. Readiness v2's declared-rule
coverage misses that support composition, so its unchanged raw result is reported
with a supplemental generic audit and explicit analyzer limitation. No B02
generation, execution, acceptance or post-pass implementation/profile repair.

Verification: 386 harness discovered, 350 pass, 36 explicit prohibited B02 checks;
31/31 application/compiler; 14/14 new focused tests; model validation, safety,
structural/source/contamination audit, byte lock and diff check pass. Checked-profile
compatibility rejection is the preserved experimental finding. Next **R5.41 =
Independent Public Decoder, Optional Durable-Domain and Readiness Support-Coherence
Review**, not comprehensive B02 evaluation. Core 30/no #31, Phase 5C paused,
B03 prospectively untouched, B17 unexposed/unclassified, format unfrozen, R5.2.2
historical authority, universal correctness unclaimed. Policy:
[R5.40 profile admission](boundary-profile-admission-r5.40.md). Earlier records
retain their historical conclusions below.

The [R5.39 refinement dependency and whole-contract boundary review](../benchmark/results/phase5c/R5_39-REFINEMENT-DEPENDENCY-WHOLE-CONTRACT-BOUNDARY-CLOSURE.md)
ends **`R5_39_WHOLE_CONTRACT_BOUNDARY_PARTIAL`**. Equivalent optional/nullable
providers now justify one scoped fact while preserving all source identities;
historical failures are reconstructed and generated regressions conform. Nullable
public decoding, typed state-alternative dispatch, declared durable content
validation and aggregate transport/state/launch/provider/trace composition are
independently implemented on a versioned seed bank through the single current
pipeline. Twenty-one public lifecycle/invalid-population calls, twelve public faults
and a source-only mutation distinguish reached layers. Invalid loads preserve
bytes and never invoke semantics.

Readiness v2 preserves the 84-cell model (64 supported/20 rejected) and adds
provider dimensions: 336 static rows; baseline and duplicate-provider transfers
each give 128 grounded conformant calls. The complete independent application
predicts READY; seven simultaneous deliberate profile/binding findings are
collected before generation. After a 658-file implementation lock, one static-only
pass forms 15/15 saved B02 CheckedPlans but returns **NOT_READY**: missing concrete
transport, state, launch and aggregate profiles, plus absent public-alternative
and content-constraint coverage. The nullable decoder capability finding is gone;
capability evidence does not populate absent frozen-contract metadata. No B02
generation/execution/acceptance or post-static repair. No retry recommended.
An additional independent static audit finds that aggregate compatibility alone
permits an unmapped optional input, while readiness v2 correctly rejects incomplete
coverage. Whole-contract completeness therefore still requires the separate readiness
gate; aggregate admission should be aligned independently in the next review.

Verification: 372 harness discovered, 336 pass, 36 explicit restrictions; 31/31
application/compiler; 12 new tests; validation/safety/evidence/diff/lock pass.
Core remains 30/no #31. Next: authored boundary and typed-obligation coverage
independently before any separately locked static comparison. Phase 5C paused,
B03 prospectively untouched, B17 unexposed, format unfrozen, R5.2.2 historical
authority, universal correctness NO. Interface:
[R5.39 boundary closure](boundary-closure-r5.39.md). Earlier records retain their
historical conclusions below.

The [R5.38 nullable-domain and whole-contract review](../benchmark/results/phase5c/R5_38-NULLABLE-DOMAIN-WHOLE-CONTRACT-COHERENCE.md)
ends **`R5_38_NULLABLE_COHERENCE_PARTIAL`**. Existing negated
typed-null equality now establishes scoped non-nullness in the authoritative
current analyzer/CheckedPlan, distinct from optional membership. Required nullable
instant before/order/write compositions and nullable string/integer consumers
generate, ground and conform on an independent publication application. Combined
optional-nullable fields require both facts; wrong targets, unsafe use and scope
leakage reject. No new core construct; the emitter consumes checked scheduling,
and the independent verifier consumes authoritative facts.
However, a post-lock independent audit finds that duplicate equivalent presence
guards regress previously accepted optional selected ordering, and duplicate
nullable guards fail the same checked dependency/scope invariant. No post-static
repair occurred. Simple-case integration and green suite counts do not establish
complete nullable/optional coherence.

Readiness now records exact domains, prerequisites, state/composition and consumer
stages rather than broad feature labels. An 84-cell matrix transfers 64 supported
combinations through 128 grounded calls and rejects 20 before generation. Complete
non-task binding/transport/launch readiness predicts successful generation and
seven public calls; safe nested selection ordering is a documented unsupported
population-fact composition. After a 625-file implementation lock, one static-only
pass over R5.37's saved B02 family forms all 15 CheckedPlans but reports **NOT_READY**:
nullable public decoding, public state-alternative dispatch, durable content-validity
constraints, and missing complete transport/state/launch profiles. No B02 generation,
execution or acceptance occurs. R5.36's historical retry gate is preserved; its
nullable readiness implication is explicitly corrected prospectively.

Verification: 360 harness tests discovered, 324 pass, 36 explicit B02 restrictions;
31 application/compiler pass, validation/safety pass; 13 new tests and 37 optional
regressions pass. Five R5.37 evidence checks pass with its historical live-tree lock
assertion explicitly skipped. Byte lock, evidence audit and diff check pass;
LF→CRLF warnings are separate. The redundant-guard audit is a real implementation
failure. Recommend **R5.39 = Independent Refinement Dependency and Whole-Contract
Boundary Closure Review**, repairing producer/dependency idempotence and completing
the whole known boundary set independently before any retry recommendation.
Core 30/no #31; Phase 5C paused, B03 prospectively untouched, B17 unexposed/unclassified,
R5.2.2 historical authority, format globally unfrozen, universal correctness NO.
Interface: [R5.38 nullable/readiness](nullable-readiness-r5.38.md). Earlier records
below retain their historical conclusions and recommendations.

The [R5.37 comprehensive frozen B02 evaluation](../benchmark/results/phase5c/R5_37-B02-COMPREHENSIVE-FROZEN-EVALUATION.md)
ends at **`R5_37_B02_INTEGRATION_GAP`**. The architecture was locked at clean
commit `428a3409ea4d47a57a9fc9e5a94af2595d98ec43` (224 protected file hashes),
then the authoritative frozen contract was reconstructed and one current-format
operation-family source was submitted to `benchmark.semantic.current_pipeline`.
Authoritative analysis rejects the required nullable due-date `before` comparison
even after its non-null guard. Optional membership refinement does not eliminate
nullable values; R5.23 had already identified that separate composition. Thus
R5.36's readiness claim overgeneralized independently validated optional/instant
capabilities. No artifact, complete checked application, public launch or grounded
execution followed; all seven applicable frozen acceptance methods are BLOCKED.
No implementation repair or reduced-slice retry occurred. Static nullable-input,
single-public-operation/multi-version routing and durable content-validity concerns
are recorded separately from the observed analyzer failure.

Baseline: 347/347 harness, 31 application/compiler, validation/safety and 58 focused
architecture tests pass; six R5.37 evidence-integrity tests pass. Direct mandatory
harness discovery replayed an existing historical B03 checkpoint; no B03 evaluation
on a new candidate or prospective exposure occurred. Core remains 30/no #31, zero
new demonstrated complete frozen-B02 transfers, universal correctness NO. Final
implementation hashes remain unchanged. Recommend **R5.38 = Independent Nullable-
Domain and Whole-Contract Boundary Coherence Review**, on non-task domains before
another authorized B02 evaluation; no B03–B16 sweep yet. Phase 5C is paused again,
B17 unexposed/unclassified, R5.2.2 historical authority, format globally unfrozen.
The R5.36 checkpoint and earlier records below retain their historical conclusions.

The [R5.36 public launch completion review](../benchmark/results/phase5c/R5_36-CHECKED-PUBLIC-LAUNCH-PROFILE.md)
closes the R5.35 standalone launch boundary independently. One generic copied entry
consumes only public argv and checked co-located metadata, resolves durable/evidence
paths from actual cwd, selects checked production or controlled-test providers,
and invokes unchanged R5.35 transport/R5.32 binding/current_pipeline. Independent
PID/command/cwd/public/durable observations challenge application/profile/provenance
and trace linkage. Acoustic and unchanged specimen applications supply 33 process
observations: 21 normal/path cases (19 grounded, 2 declared preflight rejections),
6 detected faults and 6 metadata mutations (4 compatible, 2 correctly rejected).
Core remains 30, no #31; launch is infrastructure, not semantic authority.
Gate **`R5_36_READY_FOR_COMPREHENSIVE_B02_RETRY`**. Post-lock descriptive frozen-text
comparison finds all known benchmark-critical readiness classes independently
resolved or profile-configuration-only. Recommend **R5.37 = comprehensive frozen
B02 retry**, with no additional preparatory phase for deployment polish. Complete
frozen integration remains unexecuted. Windows Python 3.14.3: 347 harness tests
discovered, 346 pass, one fail-closed nested frozen-B02 restriction skip; all 14 new
launch tests, 31 application/compiler tests, validation/safety and readiness matrix
pass. Interface: [R5.36 public launch](public-launch-r5.36.md).
B02 not retried/accepted in R5.36, Phase 5C paused, B03 untouched, B17
unexposed/unclassified, R5.2.2 historical authority and format globally unfrozen.
Native packaging/installation/HTTP/production observability, crash/concurrent
persistence guarantees and hostile-runtime attestation are outside this prototype;
universal correctness is unclaimed.

The [R5.35 transport boundary completion review](../benchmark/results/phase5c/R5_35-GENERIC-TRANSPORT-BOUNDARY-COMPLETION.md)
independently validates all three R5.34 extension areas: per-element repeated/JSON
sequence binding with suppliedness and encounter order; checked declarative public
documents with stdout/stderr/exit policy; and explicit declared-state missing-store
policy with lazy materialization only on generated writes. New acoustic calibration
and unchanged R5.33 specimen applications provide 39 observations: 23 normal calls,
10 faults and 6 metadata-only mutations. All applicable normal/mutation layers pass;
faults separately expose input, persistence and public-output defects. No compiler,
old binder or semantic-runtime changes; core 30, no #31.
Gate **`R5_35_GENERIC_TRANSPORT_BOUNDARY_PARTIAL`**: the post-lock descriptive
comparison corrects R5.34's cwd-store configuration assumption. The adapter still
requires infrastructure argv; standalone public-only argv/cwd-store/trace bootstrap
has no checked launch profile. No implementation repair followed comparison.
Recommend R5.36 **Checked Public Launch Profile Completion Review**, not comprehensive
B02 retry yet. The malformed-input public mapping is now resolved independently;
operation-declared malformed semantic outcomes remain separate and unimplemented.
Windows Python 3.14.3: 333 harness tests discovered, 332 pass, one explicit nested
frozen-B02 restriction skip; 31 application/compiler tests, validation/safety and
matrix pass. Interface: [R5.35 boundary](transport-boundary-r5.35.md).
B02 not retried/accepted, Phase 5C paused, B03 untouched, B17 unexposed/unclassified,
R5.2.2 historical authority, format globally unfrozen, universal correctness
unclaimed. Crash atomicity/concurrent initialization and hostile-runtime isolation
remain unestablished.

The [R5.34 checked transport study](../benchmark/results/phase5c/R5_34-CHECKED-TRANSPORT-BINDING.md)
validates a generic checked scalar CLI around `benchmark.semantic.current_pipeline`
and the unchanged R5.32 binder. Public routing, raw suppliedness, typed invocation
and shape-checked JSON encoding are profile driven on a new four-operation mineral
catalogue and both R5.33 specimen row/root evolution applications. Fifteen catalogue
calls and ten cross-shape lifecycle calls pass applicable layered conformance;
ten unavailable calls reject without a typed semantic event. Five semantic/profile
mutations follow metadata with identical adapter bytes; six faults expose routing,
suppliedness, decoder, public status/result and forbidden durable-mutation defects.
Profile identities reject stale generation before execution. Generic architecture
gate **`R5_34_CHECKED_TRANSPORT_VALIDATED`**, core 30, no #31. Exact frozen transport
readiness remains partial: repeated collection arguments, configurable bare/error
stream encoding and missing-store/persistence policy are outside this prototype.
Malformed-input operation-outcome mapping also remains partial. Recommend R5.35
**Generic Transport Boundary Completion Review** independently, rather than B02
retry. Windows Python 3.14.3 passes 318/319 harness tests with one explicit nested
frozen-B02 restriction skip, 31 application/compiler tests, validation and safety.
Versioned interface: [R5.34 checked transport](checked-transport-r5.34.md).
No B02 retry/acceptance, Phase 5C paused, B03 untouched, B17 unexposed/unclassified,
R5.2.2 historical authority, format globally unfrozen and universal correctness
unclaimed. Durable atomicity and hostile-runtime attestation remain unestablished.

The [R5.33 cross-shape evolution review](../benchmark/results/phase5c/R5_33-CROSS-SHAPE-STATE-EVOLUTION.md)
selects **EXISTING_OPERATION_CONTRACT_GENERALIZATION** and validates distinct
typed pre/post durable states through `benchmark.semantic.current_pipeline`.
Existing keyed defaults, target equalities, applicability and cardinality generate
specimen row evolution and collection-to-versioned-envelope promotion. Sealed
CheckedPlan side-qualified bindings feed generation, per-operation persistence
codecs and independent verification. Two five-operation applications each run a
seven-call shared-file lifecycle with V1 insertion/read, migration and V2
insertion/read: 14 grounded conformant calls, two conformant source-only mutations
and five grounded nonconformant faults. Version-incompatible operations reject
before execution. Core remains 30, no #31. The cross-shape blocker is resolved
independently for this bounded composition, not arbitrary row reconstruction.
Direct file writes still lack transactional/crash atomicity. On Python 3.14.3,
full harness discovery passes 307 of 308 with one explicit frozen-B02 restriction
skip; 31 application/compiler tests, model validation and safety pass.
Gate **`R5_33_CROSS_SHAPE_EVOLUTION_VALIDATED`**. Versioned profile:
[R5.33 state evolution](state-evolution-r5.33.md). R5.34 should review checked
transport binding independently on a non-task application. Frozen transport
remains unresolved and malformed-input semantic-outcome mapping remains partially
resolved/separate. No B02 retry/acceptance, Phase 5C paused, B03 untouched, B17
unexposed/unclassified, R5.2.2 historical authority, format globally unfrozen and
universal correctness unclaimed.

The [R5.32 input-binding checkpoint](../benchmark/results/phase5c/R5_32-INPUT-BINDING-TYPED-FAILURE-BOUNDARY.md)
validates a bounded generic public boundary around the single-authority current
pipeline: raw omitted/supplied scalar data becomes checked typed input or a
structured binding failure before semantic invocation. Existing optional key
membership preserves suppliedness through semantic fallback. One generated
four-operation observatory console exercises instant/integer/string and explicit
finite decode domains; malformed input and typed semantic rejection have separate
public outcomes and binding/semantic evidence. Eighteen shared-store calls and
three source-only mutations conform; four grounded disposable faults fail binding
conformance, including independently observed forbidden durable mutation.
Core remains 30, no #31. Suppliedness/well-formedness is resolved independently;
malformed-input outcomes are partially resolved: public boundary mapping is
validated, mapping into declared semantic operation outcomes remains separate.
The full 298-test discovery passes 297 with one deliberate skip to avoid nested
frozen B02 acceptance; 31 application/compiler tests, validation and safety pass.
Gate **`R5_32_INPUT_BINDING_BOUNDARY_VALIDATED`** is bounded architecture evidence.
R5.33 should review cross-shape state evolution independently before implementation.
Frozen transport remains unresolved; no B02 retry/acceptance, Phase 5C paused,
B03 untouched, B17 unexposed/unclassified, R5.2.2 historical authority, format
globally unfrozen and universal correctness unclaimed. Interface profile:
[R5.32 binding rules](input-binding-r5.32.md).

The [R5.31 single semantic authority checkpoint](../benchmark/results/phase5c/R5_31-SINGLE-SEMANTIC-AUTHORITY-CONSOLIDATION.md)
establishes **one current semantic/type-analysis authority** for the supported
same-shape non-task subset. `benchmark.semantic.current_pipeline` records complete
expression, declared/refined, ordering, projection, outcome, state and capability
facts during authoritative analysis. The sealed checked plan feeds generation,
runtime binding and independent semantic verification; current consumers no
longer invoke legacy expression typing or rediscover selection element types.
The archive's eight-call grounded durable chain, inventory application and
grounded nonconformant Faults A–E remain valid. Eight new authority tests cover
poisoned alternate typers, downstream reanalysis, contradictory internal facts,
runtime signatures and source-only mutations. The final supported-environment
checks pass 286 harness and 31 application/compiler tests, validation and safety;
the result records the initial Python 3.9/CRLF environment failures separately.
Gate **`R5_31_SINGLE_SEMANTIC_AUTHORITY_VALIDATED`** is bounded architecture
validation, not universal correctness. Optional refinement and instant ordering
are resolved in the single-authority current subset. Remaining independent
classes are suppliedness/well-formedness, malformed-input typed outcomes,
cross-shape state evolution and frozen transport binding. R5.32 should begin a
bounded non-task suppliedness/well-formedness semantic review before authorizing
implementation. Core remains 30, no #31; no new B02 retry or acceptance gate,
Phase 5C paused, B03 untouched, B17 unexposed/unclassified, R5.2.2 historical
authority and semantic-first format globally unfrozen.

The [R5.30 current-pipeline hardening checkpoint](../benchmark/results/phase5c/R5_30-CURRENT-PIPELINE-HARDENING-STRUCTURED-ASSEMBLY.md)
now assembles checked operation units before a single final target render through
`benchmark.semantic.current_pipeline`. The five-operation archive still runs
eight grounded conformant durable calls. Independently observed omitted and
explicit optional values persist as absent and present fields respectively;
presence-refined reads distinguish them. A new read-only operation fault writes
an unrelated row **during** the call, grounds, and fails semantic conformance.
An inventory-domain current-entry regression demonstrates normalization,
string/integer ordering and overlapping defaults with same-shape migration.
The result is **partial** (`R5_30_CURRENT_PIPELINE_HARDENING_PARTIAL`):
legacy expression typing and downstream checks remain duplicated, complete
checked expression/payload facts are not yet carried end to end, and current
capability fault/mutation coverage is incomplete. Optional refinement and
instant ordering are resolved for the demonstrated current same-shape subset,
not frozen B02. Core 30, no #31; no B02 retry, Phase 5C paused, B03 untouched,
B17 unexposed/unclassified, R5.2.2 historical authority, format unfrozen and
universal correctness unclaimed.

The [R5.29 authoritative-pipeline consolidation checkpoint](../benchmark/results/phase5c/R5_29-AUTHORITATIVE-PIPELINE-CONSOLIDATION.md)
designates `benchmark.semantic.current_pipeline` as the prospective entry for
new non-task same-shape semantic applications. One generated archive program
runs create, refined query, ordered query, guarded replacement and removal on
shared durable state, with independent byte-to-byte continuity and grounded
conformance. Four disposable faults ground and fail semantics. The gate is
**partial** (`R5_29_PIPELINE_CONSOLIDATION_PARTIAL`): old type/ordering inference
remains duplicated inside downstream code, application assembly extracts Python
text, historical general capabilities have not all transferred through the new
entry, omitted optional constructor input does not produce an absent persisted
field, and the continuity fault is between calls rather than caused by a write.
R5.23's optional-refinement and instant-ordering blockers remain partially
resolved at whole-general-pipeline level. Core 30, no #31; no B02 retry, Phase
5C paused, B03 untouched, B17 unexposed/unclassified, R5.2.2 historical
authority, format unfrozen and universal correctness unclaimed.

The [R5.28 refined-plan consumption checkpoint](../benchmark/results/phase5c/R5_28-REFINED-PLAN-CONSUMPTION-INTEGRATION.md)
adds a source-bound checked plan consumed by a prospective non-task generator
and independent verifier fork. Refined chronological reads and guarded replace/
remove writes each execute, ground and conform; all four disposable faults
ground but fail conformance. Historical R5.23 hash-locked components remain
intact. This is **partial** (`R5_28_REFINED_PIPELINE_INTEGRATION_PARTIAL`):
there is no single generated five-command durable program, read-after-write
closure or independently verified command-to-command continuity, and the actual
pinned general compiler/verifier still does not consume the plan. R5.29 should
version a coherent multi-operation general pipeline before revisiting either
R5.23 type-blocker classification. Core 30, no #31; B02 not retried, Phase 5C
paused, B03 untouched, B17 unexposed/unclassified, R5.2.2 historical authority,
semantic-first format unfrozen and universal correctness unestablished.

The [R5.27 unified typed pipeline checkpoint](../benchmark/results/phase5c/R5_27-UNIFIED-TYPED-PIPELINE-INTEGRATION.md)
adds a prospective, shared operand analyzer for read and write contracts:
scoped optional presence, order-independent conjunctions, instant keys and
typed state-transition operands. It does **not** yet lower or verify refined
writes, generate a multi-command program or ground R5.27 executions. Gate
`R5_27_UNIFIED_TYPED_PIPELINE_PARTIAL`; R5.23's two type blockers are not yet
resolved in the general pipeline. Finish the independent generated/grounded
integration before the separate suppliedness/well-formedness study. Core 30,
no #31; no B02 retry, Phase 5C paused, B03 untouched, B17 unexposed and
unclassified, R5.2.2 historical authority and format globally unfrozen.

The [R5.26 general type integration study](../benchmark/results/phase5c/R5_26-GENERAL-TYPE-REFINEMENT-INSTANT-INTEGRATION.md)
generates, grounds and semantically checks read-only non-task operations with
scoped `optional<T>` elimination and chronological `instant` ordering, including
`present + before + select + order`. Both independently demonstrated R5.23
type blockers are resolved in this separately versioned profile, **not yet in
the full general operation pipeline**. The gate is
`R5_26_REFINEMENT_INSTANT_INTEGRATION_PARTIAL`: R5.27 should carry this analysis
through writing/mixed-branch operations on new domains, without altering pinned
history. Input validity/typed malformed outcomes, cross-shape migration and
frozen transport binding remain separate. Core 30, no #31, no B02 retry; Phase
5C paused, B03 untouched, B17 unexposed/unclassified, R5.2.2 historical
authority, format globally unfrozen, universal correctness unestablished.

The [R5.25 optional-presence/refinement review](../benchmark/results/phase5c/R5_25-OPTIONAL-PRESENCE-REFINEMENT-SEMANTIC-REVIEW.md)
chooses `EXISTING_TYPE_SYSTEM_GENERALIZATION`: optional state-row presence is
already defined by typed record membership; a scoped type-elimination witness
lets an existing predicate consume the present value without adding a new core
relation. A separate publication-domain generator checks both conjunction
orders and four absent/before/after/equal witnesses, with a grounded but
nonconforming absent-row fault. This resolves the semantic architecture in a
narrow prototype, **not** the pinned general compiler's integration; the R5.23
optional blocker is partially resolved. Core stays 30; R5.26 should integrate
scoped refinement into a separately versioned general checker, generator and
verifier on independent domains. No B02 retry or frozen acceptance, Phase 5C
remains paused, B03 untouched, B17 unexposed/unclassified, R5.2.2 historically
authoritative, semantic-first format globally unfrozen, universal correctness
unestablished.

The [R5.24 cross-capability coherence review](../benchmark/results/phase5c/R5_24-CROSS-CAPABILITY-TYPE-STATE-COHERENCE.md)
has **halted at semantic-extension review**, not validated whole-program
coherence. An independent publication-domain interpreter confirms that the
existing typed UTC `instant` admits chronological ordering, but the R5.23-
locked generator still rejects instant keys. An independent generated input
probe preserves omitted versus explicitly supplied values and grounds the
valid cases; malformed input stops before a typed semantic outcome. Existing
construct compositions cannot yet express presence-conditioned refinement of
an optional state-row field; pre/post durable shapes also remain coupled to
one declaration. Historical compiler/runtime/verifier locks remain intact;
the full harness passes 249 tests and the application/compiler suite passes
31. Review whether existing optional semantics and #45 can express the
missing guard before any #31 decision, then develop a separately versioned
coherence pipeline and independent cross-shape/whole-program witnesses.
No B02 retry or candidate was produced. Candidate core remains 30, R5.2.2
historical authority, Phase 5C paused, B03 untouched, B17 unexposed and
unclassified, the semantic-first format globally unfrozen and universal
implementation correctness unestablished.

The B01–B20 sequence is intended as a cumulative diagnostic: early requests
probe local data/query operations (B01–B05); middle requests increasingly
stress cross-cutting state and relationships (B06–B10), then behavioral rules,
invariants, dependencies and transitions (B11–B15); later requests probe
architectural/stateful concepts such as persistent entities, identity,
ownership, actors, roles, history, recurrence, projects and permissions
(B16–B20). This is a research framing for the frozen requests, not a new
requirement, implementation claim or acceptance criterion.

R5.2.2 is the frozen corrected acceptance boundary after B16. Exhaustive R5.3
Python-test reconstruction has stopped as a prerequisite for later requests;
its [latest worksheet](../benchmark/results/phase5c/R5_3-BULK-RECONCILIATION-WORKSHEET-PROGRESS.md)
and unresolved coverage remain preserved, not certified equivalent. The
[bounded-bridge decision](../benchmark/results/phase5c/R5_4-BOUNDED-BRIDGE-DECISION.md)
authorizes a prospective semantic-requirement prototype and targeted
historical-carrier preservation against R5.2.2. It is not a new oracle freeze.
B17 has not been exposed; B17–B20 are not completed.

Selected B01/B11/B14/B16 scenarios now have
[prototype witnesses](../benchmark/results/phase5c/R5_4-SEMANTIC-PROTOTYPE-PROGRESS.md)
on pinned post-B16 snapshots; this does not cover all frozen clauses. The
[format adequacy review](../benchmark/results/phase5c/R5_4-SEMANTIC-FORMAT-ADEQUACY-HALT.md)
stopped before schema freeze. Experimental typed UTC-clock and checked
requirement-relationship fixtures now address those vocabulary gaps, but the
[B17 frozen-text dependency review](../benchmark/results/phase5c/R5_4-B17-PARTIAL-DEPENDENCY-ADJUDICATION-HALT.md)
finds independently observable missing-actor behavior alongside B16-dependent
role/owner authorization. The
[prospective adjudication](../benchmark/results/phase5c/R5_4-B17-PARTIAL-DEPENDENCY-ADJUDICATION.md)
keeps Phase 5C request-level: a track missing B16 is blocked on B17 as a whole,
while independently observable clauses may have **separate diagnostic evidence**
without partial achievement. Next: checked clause dependencies and separate
diagnostics, controlled application-clock binding, B01–B16 format adequacy,
the bounded bridge and independently verified B16 checkpoints before any
B17-ready freeze or exposure.
The [adequacy restart](../benchmark/results/phase5c/R5_4-SEMANTIC-ADEQUACY-RESTART-HALT.md)
now exercises a controlled UTC subprocess clock on a disposable post-B16
application but **halts at the format gate**: finite scenario observations do
not express B02's general ordered deduplication of arbitrary repeated tags
(nor B14's arbitrary dependency cycles). No semantic schema, clause bridge or
B17-ready protocol has been frozen. The later gates remain pending.
The [invariant prototype restart](../benchmark/results/phase5c/R5_4-INVARIANT-PROTOTYPE-ADEQUACY-RESTART-HALT.md)
now expresses B02 ordered normalization and B14 cycle rules in a separate,
unfrozen typed collection/graph vocabulary with linked finite semantic
fixtures. A fresh B01–B16 frozen-text screen stops at B01: general exact-HIGH
selection across arbitrary tasks is not yet expressible (B03 adds membership
selection). The adequacy
gate remains halted; no CLI acceptance bridge or later B17 gate has advanced.
The [selection restart](../benchmark/results/phase5c/R5_4-SELECTION-ADEQUACY-RESTART-HALT.md)
now states exact ordered selection for B01/B03 using the same general typed
relation, with [explicit vocabulary counts](../benchmark/results/phase5c/R5_4-SELECTION-VOCABULARY-LEDGER.md).
The fresh screen still halts at B01: normal-order binding and arbitrary
old-task field preservation/default on migration remain unexpressed. This
prototype is unfrozen and does not advance the bridge or B17.
The [B01 order/transition restart](../benchmark/results/phase5c/R5_4-B01-ORDER-TRANSITION-ADEQUACY-HALT.md)
now prototypes typed ascending normal order and keyed migration/default
preservation. B01 remains inadequate: rules over supplied collections are not
yet bound universally to create/list/migrate commands and persistent state;
the meaning of priority rank also needs adjudication. The adequacy gate stays
at B01 and the semantic format remains unfrozen.
The [operation-contract investigation](../benchmark/results/phase5c/R5_4-B01-OPERATION-CONTRACT-ADEQUACY-HALT.md)
finds one plausible generic binder over invocation, pre-state, result and
post-state, reused by existing relations. Its synthetic typed-tuple witnesses
are not universally bound to public calls/storage; B01 remains inadequate,
and priority “above HIGH” has no established observable rank comparison.
The unfrozen ledger counts 45 provisional constructs. No later adequacy gate
has advanced.
The [architectural checkpoint](../benchmark/results/phase5c/R5_4-SEMANTIC-ARCHITECTURE-CHECKPOINT.md)
pauses the B01 repair loop: abstract operation contracts appear reusable, but
the proposed #45 binder conflates the contract with interface mapping, actual
execution observation and conformance/proof. The 45-entry prototype inventory
contains 29 candidate core semantic constructs after separating finite evidence
and benchmark administration; this is not a language freeze or an adequacy
result. A checked static interface/state binding plus independent observed
traces is the next *design hypothesis*, not an implemented capability. B01
remains inadequate and halted, R5.2.2 authoritative, the format unfrozen,
Phase 5C paused, and B17 unexposed and unclassified.
The [R5.5 architecture revision](../benchmark/results/phase5c/R5_5-SEMANTIC-ARCHITECTURE-SEPARATION.md)
now physically separates the provisional #45 abstract relation, checked slot
metadata, execution-record shape and case-scoped verifier. Historical synthetic
fixtures remain synthetic; no actual-call/storage binding or observer fidelity
has been established. The inventory remains 45 raw and 29 candidate core
constructs with observation, verification, evidence and lineage accounted for
separately. R5.5 is **partial**, not an adequacy restart: B01 stays halted and
inadequate, R5.2.2 authoritative, format unfrozen, Phase 5C paused and B17
unexposed and unclassified.
The [R5.6 grounding and trust model](../benchmark/results/phase5c/R5_6-GROUNDING-TRUST-MODEL.md)
recommends compiler-owned operation/persistence boundaries and specific
provenance, challenged by independent public-call and durable-state observation.
This is a ready-to-prototype architecture, **not** an implemented grounded
contract verifier: current records can still self-assert their origin and the
single-artifact manifest cannot attribute an operation. No new semantic
construct or B01 capability was added (45 historical raw, 29 candidate core).
B01 remains inadequate and halted; R5.2.2 authoritative, Phase 5C paused,
B17 unexposed and unclassified, and the semantic-first format unfrozen.
The [R5.7 synthetic grounding implementation](../benchmark/results/phase5c/R5_7-GROUNDING-PROTOTYPE.md)
now generates an isolated operation and per-operation provenance, executes real
subprocess calls, challenges internal records with independently captured public
output and durable file readback, and only then invokes the R5.5 case verifier.
Fault injection distinguishes wrong behavior from false reports and stale
artifacts. It remains **partial**: the 29-candidate contract vocabulary cannot
express conditional typed error classification/no-write obligations; an explicit
adapter policy checks the selected failure case, not semantic conformance alone.
No B01 repair, benchmark activation or format freeze follows. R5.2.2 remains
authoritative, B01 halted/inadequate, Phase 5C paused and B17 unexposed and
unclassified.
The [R5.8 conditional-outcome review](../benchmark/results/phase5c/R5_8-CONDITIONAL-OUTCOME-EXPRESSIVENESS.md)
generalizes the prospective #45 contract to compose typed outcome tags, Boolean
predicates and before/after state relations. The synthetic R5.7 failure now
passes or fails case-scoped semantic conformance after grounding, without the
adapter failure policy. The candidate core count remains 29. This resolves
that narrow semantic gap, not general variant-dependent payload typing or
no-attempted-write proof; B01 remains inadequate and halted, Phase 5C paused,
B17 unexposed and unclassified, R5.2.2 authoritative, format unfrozen.
The [R5.9 B01 end-to-end restart](../benchmark/results/phase5c/R5_9-B01-END-TO-END-ADEQUACY-RESTART.md)
reconstructs the complete frozen B01 contract with its inherited baseline.
Exact selection and ordering suggest a relational insertion/completion frame,
but arbitrary migration count lacks an established typed collection-to-numeric
outcome relation. A checkpoint-pinned B01 executable passes the selected frozen
cases and independent public/durable observations; it does not emit the internal
per-operation event needed to challenge B01 grounding or reach #45 semantic
conformance. This is a **multiple-gap halt** under the 29-candidate ceiling,
not a new construct, universal adequacy or correctness finding. R5.2.2 stays
authoritative, Phase 5C paused, B17 unexposed/unclassified and the format
unfrozen.
The [R5.10 focused migration-count review](../benchmark/results/phase5c/R5_10-MIGRATION-COUNT-EXPRESSIVENESS.md)
adds one general prospective finite-collection cardinality relation (#30):
exact legacy candidate selection can now relate its population to a typed
numeric outcome for arbitrary supplied finite populations. The synthetic
prototype does not integrate a B01 #45 checker or ground B01 execution.
Prospective accounting is 46 raw categorized constructs / 30 candidate core;
the historical 45-entry inventory is retained. B01 remains inadequate and
halted, its R5.7 grounding failed/unestablished, R5.2.2 authoritative, Phase
5C paused, B17 unexposed/unclassified and the semantic-first format unfrozen.
The [R5.11 B01 instrumented integration](../benchmark/results/phase5c/R5_11-B01-INSTRUMENTED-INTEGRATION.md)
builds a distinct, prospectively generated B01 executable with per-operation
provenance and runtime events. The new executable passes the original frozen
B01 profile (5 passes, 2 B02 skips); actual create, list, list-high, complete
and migration calls have independently challenged public and durable endpoints
and case-scoped conformance. A faithfully reported wrong migration count fails
semantics after grounding, while a false post-state report fails grounding
before semantic evaluation. The 30-candidate abstract vocabulary is adequate
for the observable B01 contract without a #31; the B01-specific checker is not
a general typed #45 compiler, and universal implementation correctness remains
unestablished. The historical executable is unchanged and its old acceptance
is not retroactively grounded. R5.2.2 remains authoritative, Phase 5C paused,
B17 unexposed/unclassified and the semantic-first format unfrozen.
The [R5.12 POC health gate](../benchmark/results/phase5c/R5_12-POC-HEALTH-GENERAL-LOWERING-GATE.md)
finds that R5.11's B01 implementation and most of its checker were separately
authored Python, while the semantic label index only affected digests. A small
typed, target-neutral **validating** #45 lowerer now checks read-only B01
list/list-high cases and a structurally different synthetic filter/order/count
contract; mutation changes checked outcomes without lowerer edits. No B01
algorithm is generated from that source, and a valid keyed-default combination
remains unsupported. The 30-core candidate and grounding direction remain
plausible, but lowering is **not general enough to scale**: the next step is
bounded generative operation lowering challenged on a non-task domain, before
any further frozen-request execution. R5.2.2 remains authoritative, Phase 5C
paused, B17 unexposed/unclassified, and the semantic-first format unfrozen.
The [R5.13 non-task generative prototype](../benchmark/results/phase5c/R5_13-SEMANTIC-DRIVEN-GENERATIVE-LOWERING.md)
now emits stateful executable predicates, tagged outcomes and bounded keyed
transitions from typed semantic contracts. Value and structural mutations plus
a novel combination change real subprocess/file behavior without lowerer
edits; independent grounding and contract conformance distinguish an injected
lowering fault. This validates a **constrained** generative slice, not B01
generation, arbitrary synthesis or scaling readiness. Keep 30 candidate core
constructs / 46 raw entries, format unfrozen, Phase 5C paused, R5.2.2
historically authoritative and B17 unexposed/unclassified. At the R5.13
checkpoint, B02 had not been resumed.
The [R5.14 controlled B02 pressure test](../benchmark/results/phase5c/R5_14-B02-FROZEN-ARCHITECTURE-PRESSURE.md)
now reconstructs frozen B02 and inherited obligations without adapting that
architecture. Existing candidate relations express ordered tag normalization,
blank rejection and abstract migration/defaults, but R5.13's general generator
cannot emit those compositions or complete task operations. It halts at the
generative-lowering gate: no B02 candidate, acceptance, grounding or conformance
result follows. The old frozen v0.3 B02 capability gap remains historical; this
is a new prospective compiler-boundary finding, not a retroactive repair.
Next: test general lowering of the missing existing relations on independent
non-task examples before any B02 retry. Keep 30 candidates / 46 raw entries,
 format unfrozen, Phase 5C paused after this B02-only pressure test, R5.2.2
 historically authoritative and B17 unexposed/unclassified.
The [R5.15 independent lowering study](../benchmark/results/phase5c/R5_15-GENERAL-LOWERING-COVERAGE-EXPANSION.md)
now generates ordered normalization, typed record outcomes and a bounded keyed
missing-field default on media, device and library domains. Semantic-only
mutations change generated behavior; three new capabilities compose in one
synthetic operation, with grounded executions and a fault that grounds but fails
conformance. Framed insertion remains an abstract, unintegrated relation; a
full checked versioned migration is also not generated. The result is
**partial**, not B02 readiness: no B02 candidate was generated or retried.
Keep 30 candidate core / 46 historical raw entries, Phase 5C paused, B17
unexposed/unclassified, R5.2.2 historically authoritative and the
semantic-first format globally unfrozen. Next: integrate exact insertion
framing and checked durable version transitions on further non-task domains.
The [R5.16 independent transition study](../benchmark/results/phase5c/R5_16-FRAMED-INSERTION-DURABLE-MIGRATION-LOWERING.md)
now constructively lowers an exact full-record insertion frame and a checked
durable V1→V2 default/version/count transition on specimen and archive data.
Independent public/file grounding, semantic-only mutations, composition and
faithfully grounded nonconforming faults close these **bounded general-lowering**
gaps, not all relation shapes or interface binding. Candidate core remains 30;
no B02 candidate or retry followed. Phase 5C remains paused, R5.2.2 historical
authority, B17 unexposed/unclassified and the semantic-first format unfrozen.
The [R5.17 frozen B02 retry](../benchmark/results/phase5c/R5_17-B02-GENERALIZATION-RETRY.md)
locks the R5.16 working-copy architecture and reconfirms B02 expressibility
with 30 candidate core constructs, but stops at unchanged general lowering:
three missing-field defaults on the same legacy task population encounter the
explicit overlapping-collection rejection. No B02 candidate was generated;
frozen acceptance, grounding and conformance were not reached. This is a
compiler-composition gap, not a new semantic construct or a retroactive change
to the historical v0.3 B02 gap. Next study the unresolved general composition
on independent non-task domains in a separate experiment before any further
frozen retry. Phase 5C does not proceed to B03; B17 remains unexposed and
 unclassified, R5.2.2 historical authority and semantic-first format unfrozen.
The [R5.18 independent relation-composition study](../benchmark/results/phase5c/R5_18-OVERLAPPING-RELATION-COMPOSITION-LOWERING.md)
now plans N compatible keyed defaults over one typed collection, deduplicates
equivalent relations, rejects conflicting literals and unsupported structural
overlaps, and checks their joint post-state in an instrument inventory. Durable
version/count outcomes and a grounded but nonconformant lowering fault exercise
the conjunction. At the R5.18 checkpoint, the R5.17 executable assertion still
expected the old lowerer to reject; R5.18 is not a new frozen retry. Core 30;
Phase 5C paused, B17 unexposed/unclassified, R5.2.2 historical authority,
format unfrozen. Next:
a separately locked retry, not a retroactive R5.17 result.
The [R5.19 second locked B02 retry](../benchmark/results/phase5c/R5_19-B02-SECOND-GENERALIZATION-RETRY.md)
first restored current-suite consistency by updating the executable R5.17
assertion to reflect current compiler behavior, preserving its historical
result. The full harness then passed 164/164 before lock. The unchanged
R5.17 three-default migration slice now types and renders through R5.18's
planner, demonstrating **bounded B02-shaped transfer without task-specific
compiler changes**. But a typed B02 ordered `list` hits the next unchanged
generator limit, `UNSUPPORTED_LOWERING_CAPABILITY: order`. This is another
lowering halt, not a B02 candidate or acceptance/grounding result. Core 30,
no #31, no B03 advance, B17 unexposed/unclassified, R5.2.2 historical
authority, format unfrozen and universal correctness unestablished. Next:
independent non-task generative ordered-outcome study before any further retry.
The [R5.20 general ordering lowering](../benchmark/results/phase5c/R5_20-GENERAL-TYPED-ORDERING-LOWERING.md)
now generatively lowers the existing #43 typed ordering relation on media and
device domains: one-, two-, three- and four-key ascending plans over typed
record collections, composed with exact selection and typed record-valued
outcomes, read-only over durable bytes, grounded and fault-tested; ties remain
semantically unconstrained and direction remains unrepresented (both reject
explicitly). No B02 retry occurred, no #31 follows and benchmark transfer
remains untested; result `R5_20_ORDERING_LOWERING_VALIDATED`. Next: a
separately locked third B02 retry, with direction semantics and scoped
ordering reserved for independent semantic/lowering study.
The [R5.21 third locked B02 retry](../benchmark/results/phase5c/R5_21-B02-THIRD-GENERALIZATION-RETRY.md)
restored suite consistency (no newly obsolete expectations; pre-lock harness
183/183), locked the R5.20 architecture and confirmed the unchanged 30-construct
model again represents frozen B02. R5.20 ordering **transferred**: the exact
R5.19 `order` blocker is resolved and the B02-shaped ordered `list`, together
with executed-slice transfers of R5.13 selection/read-only, R5.15
normalization/defaults/record outcomes, R5.16 durable version transition and
#30 count, and R5.18 N-way defaults, now generate, execute, ground and conform
as disposable slices without task-specific compiler changes. Complete B02 still
stops at the generative lowering gate: create-success needs fresh-ID/UTC-clock
value generation and omitted-input fallback defaults (both rejected explicitly),
and known boundaries remain for strict time comparison, matched-row/post-state
outcome projection, removal transitions and envelope-shaped lifecycle
replacement; the integrated multi-operation AST and CLI/clock/ID binding remain
unreached. This is the last planned one-capability retry cycle: result
`R5_21_B02_KNOWN_LOWERING_COVERAGE_INCOMPLETE` recommends a lowering-coverage
completion phase closing the known set independently before any further B02
retry. Core 30, no #31, no candidate/acceptance/grounding result for a complete
B02, Phase 5C does not advance to B03, B17 unexposed/unclassified, R5.2.2
historical authority, format unfrozen, universal correctness unestablished.
The [R5.22 known lowering-coverage completion](../benchmark/results/phase5c/R5_22-KNOWN-GENERAL-LOWERING-COVERAGE-COMPLETION.md)
replaces the serial B02 discovery loop and closes the **known** R5.21 backlog on
independent non-task domains (sensor readings, publication archive) with **no B02
retry**: `external` values through a typed capability boundary, omitted-input
`fallback` distinct from keyed `default_missing`, `before` (#27) promoted from
validating-only to generative over the typed `instant` form, matched-row/post-state
**projection**, keyed **remove** and envelope **replace_field** through the
relation-set conjunction, and a generic metadata-derived **CLI binding** — each
generated, executed, grounded, semantically conformant, and fault-tested; two
composed operations re-derived from semantics-only mutation with zero lowerer edits.
Four R5.21 frontier rejection expectations were retired by the lifecycle precedent.
Result `R5_22_KNOWN_LOWERING_COVERAGE_COMPLETE` for the lowering-coverage backlog:
no known required relation remains validating-only/unsupported/unknown. This does not
assert a complete B02 serializes or advance acceptance/interface/transport layers.
Core remains 30 with no #31 (the typed instant, `sole`/`project` and boundary are
lowering/typing/binding machinery, not new semantics), Phase 5C paused, B17
unexposed/unclassified, R5.2.2 historical authority, format unfrozen, universal
correctness unestablished. A separately locked comprehensive B02 retry
against the closed lowerer followed.
The [R5.23 comprehensive locked B02 integration retry](../benchmark/results/phase5c/R5_23-B02-COMPREHENSIVE-INTEGRATION-RETRY.md)
reconfirmed the 30-construct model's representation adequacy and reached new
integration firsts: B02-shaped create-success with typed external identity/clock
and fallback inputs executed, grounded and conformed under controlled and real
providers; a twelve-branch multi-command B02-shaped program typed, rendered and
ran as one generated program through the locked pipeline; envelope lifecycle
replacement, keyed removal, N-way migration defaults with the #30 count,
migration-required no-write reads and string-typed ordered reads all re-grounded
conformant (13/13 executable slice cases). Complete whole-program generation
still halted at typed validation, now for a newly identified class: independently
validated capabilities collide on **shared representation domains**. A
semantically typed `instant` creation timestamp is not an admissible ordering key
(`non-orderable key`), while the orderable string column refuses the
`instant`-typed clock (`outcome payload type mismatch`); `before`/`equals` cannot
bind optional or nullable record fields (faithful `list-overdue`, legacy-row
`list-high`); no relation expresses input suppliedness or domain well-formedness,
so `invalid_due_date`/`invalid_state` cannot become typed failure branches; and
one contract admits one state shape, so version-dependent rows (v2/v3 ∩ v4) and
bare-list→envelope promotion are unlowerable. The deliberately deferred
frozen-transport binding (positional argv, error envelope/exit codes,
missing-file→`[]`, shared store) was separately confirmed absent as the known
secondary blocker. Frozen acceptance never ran (7 cases blocked, no candidate);
no repair and no #31; the R5.22 per-relation backlog methodology was true per
relation yet false per program. Result
`R5_23_PREVIOUSLY_UNKNOWN_LOWERING_GAP` directs the next step not to another
isolated one-capability retry but to a focused whole-program integration phase
(inter-capability type integration, versioned-storage handling, input-validity
relations and checked transport binding on independent domains) plus revision of
coverage enumeration from relation kinds to shared-domain compositions, before a
final B02 retry. Keep core 30, Phase 5C paused, B17 unexposed/unclassified,
R5.2.2 historical authority, format unfrozen and universal correctness
unestablished. Longer term, complete the ordered benchmark with
honest accounting for capability gaps, dependency
blocks, regressions and measurement limits. The benchmark tests functional
equivalence against frozen requirements, not similarity to Conventional's
source. Its external acceptance tests independently verify behavior; they
must not become the design target for Lykoi's semantic vocabulary. A capability
gap in a frozen run is evidence to preserve, not an invitation to extend that
version mid-run.

After a completed frozen suite, cluster gaps by underlying semantics, propose
small abstractions that address multiple cases, freeze an evolved language
version and compare it under a controlled rerun. Challenge any apparent
generalization on *new, unseen domains*: indefinitely extending the one task
manager cannot demonstrate it. The prospective B17–B20 protocol will explore
first-class structured semantic requirements with acceptance derived from
them, rather than inferring semantics from Python tests. This is a research
direction, not an established benchmark or language capability. Passing
validation or a safety report alone is never a behavioral proof. See the
[agent workflow](agent-workflow.md)
for the practical change and evidence rules.
