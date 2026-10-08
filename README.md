# Lykoi

Lykoi is an AI-native semantic representation for software. This experimental
software-development system is designed around AI authorship: an AI maintains a
semantic model of a software system, validates its relationships and contracts,
and generates disposable implementation artifacts. The model, not Python, is
the source of truth. Python is the first backend, not the definition of Lykoi.

Lykoi (pronounced “lie-KOY”) is named after the Lykoi cat breed. Its central
question is: what should software look like when AI, rather than humans, is the
primary programmer? Human intent leads to an AI-authored Lykoi semantic model,
then validation, lowering and generation, and finally an executable system.

For the work to date, current research boundary and long-term goal, see
[`docs/project-overview.md`](docs/project-overview.md). The project is **Lykoi,
not Axiom**; historical `axiom` names are retained only for compatibility and
reproducible research records.

Contributors and AI agents should start with [`AGENTS.md`](AGENTS.md) and the
[agent workflow](docs/agent-workflow.md) before changing the model, compiler or
benchmark.

**R5.119 prepares P6-A03 for human research review only.**
[Preparation report](benchmark/results/phase6/R5_119-REPORT.md) and
[owner review](benchmark/results/phase6/r5_119/HUMAN-REVIEW.md) contain the exact
source-bound candidate FRC and acceptance plan. The owner is appointed research
approver; no approval given. Redis SELECT category grant/revoke compatibility needs
clarification. Kernel 26 unchanged, historical results preserved, zero authoring or
evaluation. Stop after review; subsequent exact-artifact human decision required.

**R5.118A establishes research-only evaluation authority readiness.**
The [report](benchmark/results/phase6/R5_118A-REPORT.md),
[approval specification](docs/research-evaluation-approval-v1.md) and
[prospective Phase 6 protocol](docs/phase6-generalization-protocol-r5.118a.md)
separate appointed experimental permission from upstream/product approval. Synthetic
native-path and negative controls pass with 146 relevant tests, validation and safety;
research approval cannot confer production authority or waive semantic/verification
gates. No actual approver appointed for external sources; first results preserved,
kernel 26 unchanged. Stop after methodology; no external evaluation or P6-A03 access.

**R5.118 preserves P6-A02's first result: `NEEDS_CLARIFICATION`.**
The [report](benchmark/results/phase6/R5_118-REPORT.md) records
`R5_118_P6_A02_FIRST_EVALUATION_COMPLETE`: exact curl source verified, bounded-change
candidate valid; required FRC approval unavailable, separately from semantic incompleteness.
No implementation authority or downstream verification. Kernel 26 and R5.117 preserved;
procedurally selected external evidence, not blinded/held-out. Stop; no repair or P6-A03 access.

**R5.117 preserves P6-A01's first result: `NEEDS_CLARIFICATION`.**
The [report](benchmark/results/phase6/R5_117-REPORT.md) records
`R5_117_P6_A01_FIRST_EVALUATION_COMPLETE`: exact source verified, source-bound candidate
envelope valid, unresolved scope/format/activation authority. No approved FRC or downstream
pipeline/behavioral verification; implementation remains unchanged at 26 concepts.
This is procedurally selected external evidence, not blinded/held-out. Stop after
first-result publication; no repair or P6-A02 evaluation.

**Preserved R5.116A curated five externally authored, procedurally selected requirements.**
The [report](benchmark/results/phase6/R5_116A-REPORT.md) records
`R5_116A_PROCEDURAL_OPEN_SOURCE_BATCH_CURATED` under a policy committed before issue
inspection: five projects, 12 inspected candidates, seven rule-based exclusions,
exact source hashes and five candidate acceptance records. All require clarification.
This is not blinded curation or held-out evidence; implementation is unchanged and
no requirement was evaluated. Stop after curation; R5.117 needs separate authorization.

**Preserved R5.116 stopped before curation: curator separation unavailable.**
The [independence audit/report](benchmark/results/phase6/R5_116-REPORT.md)
records `R5_116_BLOCKED_CURATOR_SEPARATION_UNAVAILABLE`: no requirements were
searched, selected or inspected; no acceptance records or batch manifests exist.
Development received no requirement semantics. Implementation is unchanged and
the first requirement is not ready for R5.117. Independent curation remains outstanding.

**R5.115 establishes Phase 6 generalization research readiness.**
The [preserved Phase 5 baseline](docs/phase5-baseline-r5.115.md),
[research plan/source-independence policy](docs/phase6-research-plan-r5.115.md) and
[lightweight first-result protocol](docs/phase6-generalization-protocol-r5.115.md)
prioritize unfamiliar-software representation, kernel stability and independent
behavioral correctness; AI efficiency is a later comparison. R5.114's 26 concepts,
397-test receipt and 16/20 exposed successes remain unchanged; 34 default tests,
validation and safety pass freshly. B01–B20 remain exposed development/regression
evidence. `R5_115_PHASE6_RESEARCH_READY` means methodology readiness only.
Stop after planning: no new requirement sourced, inspected or evaluated and no
capability/infrastructure implementation. See the
[transition report](benchmark/results/phase5c/R5_115-REPORT.md).

**Preserved R5.114 closes bounded historical-state and trusted-host verification interfaces.**
[Explicit related-field migrations and sealed controlled-host execution](docs/historical-state-trusted-verification-v1.md)
traverse the normal requirements-to-external-behavior path. Creation defaults never
authorize history; controlled-host assertion is not authentication. Proposed kernel
stays **26**. **397 tests**, validation/safety and **133 synthetic external invocations**
pass before lock. [Fresh exposed transfer](benchmark/results/phase5c/R5_114-REPORT.md)
retains **16/20 B01–B16**, **447 invocations**. B17–B20 remain disputed, B18/B19
downstream NOT_REACHED. `R5_114_HISTORICAL_STATE_TRUSTED_VERIFICATION_CLOSED` is scoped
to explicit additive evolution and the existing trusted-local host boundary.
Stop after R5.114; historical evidence preserved, no held-out/cumulative claim.

**Preserved R5.113 implements bounded prewrite authorization and conditional effect composition.**
[Declared role/owner/set predicates, controlled-host actor binding, conditional atomic
effects, created-record dependencies and nullable refinement](docs/prewrite-conditional-composition-v1.md)
compose existing meanings. Supplied actors are selectors, not authenticated principals;
the CLI has no trusted authentication source. Exact elapsed-day conversion justifies
K26, proposed kernel **25 → 26**. **393 tests**, validation/safety and **144 synthetic
external invocations** pass before lock. [Fresh exposed transfer](benchmark/results/phase5c/R5_113-REPORT.md)
retains **16/20 successes**, **447 invocations**. B17/B20 remain disputed; B18/B19 now
halt on inherited historical role authority at formalization, with no new downstream
stages or behavioral success. Historical related-field migration and sealed trusted-host
success verification remain seams: `R5_113_AUTHORIZATION_CONDITIONAL_EFFECT_COMPOSITION_PARTIAL`.
Stop after R5.113; no next family, infrastructure or held-out/cumulative claim.

**Preserved R5.112 partially integrates primary value/actor/successor interfaces by composition.**
[Primary signed-64/nullable numeric state, supplied actor context, numeric history
and same-primary successors](docs/primary-value-interfaces-v1.md) traverse the normal
pipeline. Explicit absolute UTC-day decoding is separate from unsupported runtime
N-day duration conversion. Proposed kernel remains **25**. **389 tests**, validation/
safety and **115 synthetic external invocations** pass. [Fresh locked transfer](benchmark/results/phase5c/R5_112-REPORT.md)
retains **16/20 successes B01–B16**, **447 invocations**. B18 prewrite authorization
and B19 conditional duration/effect/image interfaces remain structural; B17/B20
remain disputed. No new downstream stages; `R5_112_PRIMARY_INTERFACE_COMPOSITION_PARTIAL`.
Stop after R5.112; no held-out/cumulative claim or new infrastructure.

**Preserved R5.111 implements bounded typed computation with an explicit kernel extension.**
[Signed-64 integers, cardinality bindings, checked addition and typed fixed-second
UTC displacement](docs/typed-computation-v1.md) feed related mutation/predicate/
creation graphs under existing atomicity. No unrestricted expressions; increment,
numeric history and generic successor compose. Checked addition and fixed-duration
displacement (`offset`) take proposed kernel **23 → 25**. **386 tests**, validation/
safety and **75 synthetic external invocations** pass. [Fresh locked transfer](benchmark/results/phase5c/R5_111-REPORT.md)
retains **16/20 successes B01–B16**, **447 invocations**. B18 primary-history/actor
and B19 primary numeric/day/successor/actor interfaces remain structural; B17/B20
remain disputed. No held-out/cumulative claim; stop after R5.111.

**Preserved R5.110 implements bounded atomic durable history by composition.**
[Ordinary typed history records and atomic coupled creations](docs/atomic-durable-history-v1.md)
execute through the normal pipeline with declared shared clocks, rollback, history
queries and append-only operation restrictions. No new core primitive; proposed
kernel stays **23**. **379 tests**, canonical validation/safety and **105 synthetic
external invocations** pass. [Fresh locked transfer](benchmark/results/phase5c/R5_110-REPORT.md)
retains **16/20 successes B01–B16**, **447 invocations**. B18 is now structurally
blocked by numeric history values and primary actor bindings; numeric generation
is not implemented. B17/B20 remain disputed, B19 remains outside implemented scope.
No held-out/cumulative claim; stop after R5.110.

**Preserved R5.109 implements bounded persistent references and cross-entity integrity.**
[Typed reference fields, existence, restrictive deletion and related-state guards](docs/persistent-references-v1.md)
compose through the normal pipeline; cycle rejection justifies one explicit
finite nonempty-path reachability candidate. Proposed kernel **22 → 23**.
**372 tests**, canonical validation/safety and **182 synthetic external invocations**
pass. The [frozen exposed transfer](benchmark/results/phase5c/R5_109-REPORT.md)
verifies **B01–B16**, with B14/B15/B16 newly successful and **447 invocations**.
B17/B20 remain disputed, B18 BDI and B19 structural remain. No held-out/cumulative
claim. Generic content stays exact; stop after R5.109.

**Preserved R5.107 closes the bounded normal predicate/value interfaces.**
[Typed literal writes, existing selection amendments, query preconditions/errors
and declared clock operands](docs/predicate-value-interfaces-v1.md) compose through
the normal source-to-external-behavior path. **361 tests**, canonical validation/
safety and 84 public synthetic external invocations pass. The
[locked exposed transfer](benchmark/results/phase5c/R5_107-REPORT.md) verifies
**B01–B13**, with B08/B09/B11/B12/B13 newly successful and 358 transfer invocations.
Four structural cases, B18 external-effect BDI and B17/B20 disputes remain. Final
generic lock 3 stays fixed; one locked guidance trailing space is reported by the
whitespace audit. R5.106 is preserved; no held-out/cumulative claim. Stop after R5.107.

**Preserved R5.106: bounded typed predicate/guard composition.**
[Typed comparison, AND/OR/NOT, null/presence and membership trees](docs/typed-predicates-v1.md)
share semantics across normal queries, prewrite guards and staged validation;
boolean storage/migration/reload is integrated. **355 tests pass**, with 124 public
synthetic external invocations. The [locked exposed transfer](benchmark/results/phase5c/R5_106-REPORT.md)
retains eight local successes (B01–B07/B10), eight structural, B18 BDI, B17/B20
clarification and B12 invalid typed candidate at clock-resource binding. No new
request-level stage progress or held-out/cumulative claim. Stop after R5.106.

**Preserved R5.105 baseline: bounded typed value/input profile closure.**
[Literal/input/default sources, explicit observation stages, conditional validation
and semantic parameters separate from CLI bindings](docs/typed-input-values-v1.md)
execute through the normal requirements/compiler/external path. **348 tests pass**;
four public domains publish 132 external invocations. The
[frozen exposed transfer](benchmark/results/phase5c/R5_105-REPORT.md) has eight local
successes (B01–B07/B10), nine structural blockers, B18 BDI and B17/B20 clarification.
R5.104 remains preserved; no held-out/cumulative claim. Stop after R5.105.

**Current research policy: R5.96.** Use compatible Python 3.10+ and the AI model
available in the active environment. OpenCode, model/machine/runtime/transport
qualification and protected freeze activation are not benchmark prerequisites.
See the [simplified workflow, infrastructure classification and snapshot command](docs/research-workflow-r5.96.md).
No held-out-informed Lykoi changes are allowed before the first recorded result.
B03 was exposed in R5.97 and halted at structural coverage:
**`B03_FIRST_RESULT = DECISION_DISCOVERY_UNSUPPORTED`** (native
`STRUCTURAL_COVERAGE_FAILURE`). No authoring, compilation or B03 behavioral
verification was reached. See the [R5.97 report](benchmark/results/phase5c/R5_97-B03-HELD-OUT-EVALUATION.md).
The infrastructure descriptions below retain their historical experimental scope.

**R5.98 adds a bounded prospective collection-query capability.** Typed runtime
equality/membership, comparison policies, ordering, validation, inclusion, results
and read-only effects work through structural analysis, adequacy and a separate
query-V1/compiler path on six synthetic compositions. See the
[specification](docs/collection-query-v0.1.md) and
[report, verification and post-exposure transfer limits](benchmark/results/phase5c/R5_98-GENERAL-STRUCTURAL-QUERY-CAPABILITY.md).
The unchanged B03 candidate still halts structurally; the first result is preserved.

**R5.99 integrates the bounded query profile into the normal requirements pipeline.**
Typed FRC output, source reconciliation, explicit normal V1 selection, restricted
authoring/compiler dispatch and a generic read-only model-state adapter reach
external behavior on source-bound AI captures. **280/280 tests pass.** The round
has a **benchmark firewall violation**: a targeted evidence search unexpectedly
returned B04/later historical implementation logs. No requirement files were opened,
but indirect disclosure occurred; B03 transfer 2 was not run. See the
[normal-path specification](docs/collection-query-normal-path-v1.md) and
[R5.99 report and incident](benchmark/results/phase5c/R5_99-COLLECTION-QUERY-NORMAL-PATH-INTEGRATION.md).

**R5.101 diagnoses B01–B20 as an exposed development/regression corpus.**
The [current capability report](benchmark/results/phase5c/R5_101-B01-B20-CURRENT-CAPABILITY-REPORT.md)
and [matrices](benchmark/results/phase5c/R5_101-CAPABILITY-MATRICES.md) classify
all twenty on unchanged Lykoi: B05 local behavioral success, sixteen structural
halts, one BDI halt and two clarifications. This is not cumulative benchmark
achievement or held-out generalization evidence. The roadmap proposes general
capability projects; none was implemented. Future generalization requires a
new development-unexposed evaluation source.

**R5.102 integrates a bounded existing-scalar normal profile.**
[Typed scalar/default/lifecycle/resource/migration facts](docs/existing-scalar-normal-path-v1.md)
reach external behavior through ordinary author/compiler interfaces on public
captures. **314/314 tests pass**. The
[report](benchmark/results/phase5c/R5_102-NORMAL-PATH-REPORT.md) classifies the round
**partial** because material guard/composition/resource-testing seams remain.
The fixed exposed transfer has B04/B05 local success, fifteen structural halts,
one BDI halt and two clarifications; nineteen cases replay old captures. R5.101
remains the pre-development baseline, not replaced or reclassified.

**R5.103 establishes the fresh typed current development baseline.**
[All twenty new candidates and the report](benchmark/results/phase5c/R5_103-REPORT.md)
reach normal reconciliation/coverage: **B01/B04/B05 behavioral success, fourteen
structural blockers, B18 BDI, B17/B20 clarification**. B01 improves solely by
fresh typed formalization reaching existing support. Bounded
[guard/clock/resource/profile composition](docs/existing-semantic-composition-v1.md)
passes **328/328 tests**, model validation/safety and 125 published external CLI
invocations. Historical matrices are preserved. Recommend typed mutable values
and transformations for R5.104; no selected family is implemented. This remains
exposed regression evidence, not held-out generalization or cumulative achievement.

**R5.104 implements bounded typed mutable values through the normal path.**
[Explicit collection/value/presence/pipeline semantics](docs/typed-mutable-values-v1.md)
compose with scalar storage, additive migration, independent lifecycle and existing
CollectionQuery. **340 tests pass**; four synthetic domains publish 96 external
CLI invocations. The locked
[exposed transfer/report](benchmark/results/phase5c/R5_104-REPORT.md) has **six local
successes: B01/B02/B03/B04/B05/B10**, eleven structural blockers, B18 BDI and
B17/B20 clarification. B06/B07 retain bounded profile seams. R5.103's baseline
and historical first results remain preserved; no held-out/cumulative claim.

The [R5.87 requirements workspace](docs/requirements-workspace-r5.87.md) implements
a public synthetic human-intent → clarification → independent source review → exact
approval → controller-sealed requirements lifecycle. With `PYTHONPATH=src`, run
`python -m lykoi_workspace.example` for the wizard transcript or add `--audit` for
exact artifact bindings. This is requirements engineering, not production AI
qualification or an implementation grant.

The [R5.88 sealed authoring/verification pipeline](docs/sealed-authoring-verification-r5.88.md)
adds native analysis/coverage checks, independently presealed acceptance plans,
executable component/run freezes, exact grants, restricted fixture authorship,
deterministic builds and external behavioral verification with restart audit.
`python -m lykoi_pipeline.example` attempts the public wizard's back half and halts
at the existing faithful-V1 adapter gap before authoring. Local fixture isolation
is not an OS sandbox or production AI qualification.

The [R5.89 public rehearsal profile](docs/public-rehearsal-capability-r5.89.md) adds
closed task-title/default mappings, structured HTTPS AI interfaces, independent
WHAT-derived acceptance planning, trusted-target containment and a machine-verifiable
inactive public freeze. `python -m lykoi_rehearsal.freeze check` reports infrastructure
eligibility without inspecting a future requirement. Current status is
`R5_89_PUBLIC_REHEARSAL_BLOCKED_REAL_AI_QUALIFICATION`: live models/calibration and
separate public activation remain. The exact R5.87 wizard still halts before authoring.

The [R5.90 live worker qualification preflight](benchmark/results/phase5c/R5_90-LIVE-AI-WORKER-QUALIFICATION.md)
stops **`R5_90_LIVE_AI_WORKERS_BLOCKED_CREDENTIAL_UNAVAILABLE`**: no service credential
is available and all role models remain unconfigured. Live runs and qualified roles
are zero; infrastructure remains ineligible before future requirement selection.

The [R5.91 live integration](benchmark/results/phase5c/R5_91-LIVE-AI-INTEGRATION-AND-PUBLIC-REHEARSAL-FREEZE.md)
ends **`R5_91_PUBLIC_REHEARSAL_FROZEN`**. Existing OpenCode/GitHub Copilot OAuth now
executes `claude-sonnet-4.6` for all four restricted roles; real smoke evidence is
preserved. **R5.91-PUBLIC-REHEARSAL-2** is active, with mechanical freeze-before-
requirements admission. Model identity is frozen provenance, not semantic authority;
general model qualification is deferred. The [next-round protocol](docs/public-rehearsal-protocol-r5.91.md)
is frozen. No future requirement was selected and no rehearsal was run. R5.90's
historical blocked result, the R5.89 envelope and B03 protection remain intact.

The [R5.94 protected evaluation repair](docs/protected-evaluation-r5.94.md) adds generic
protected provenance, exact opaque-source/run authorization, durable admission and
role-specific access accounting around the existing semantic pipeline. Synthetic
supported/invariance/unsupported challenges pass. A [new generic candidate](benchmark/results/phase5c/r5_94/protected-freeze-candidate.json)
is frozen inactive; no B03 authorization or access occurred. Historical R5.91 machinery
and evidence remain intact. See the [engineering report](benchmark/results/phase5c/R5_94-GENERIC-PROTECTED-EVALUATION-ADMISSION-REPAIR.md)
for checks and trusted-local containment limits.

The [R5.94A runtime contract](docs/python-runtime-contract-v1.md) qualifies Python
behavior independently of exact installation bytes while recording actual runtime
provenance. With `PYTHONPATH=src`, run the chosen interpreter with
`-X utf8 -m lykoi_runtime.verify verify --current`; no global `python` command is
required. CPython 3.14.3 passes. The [engineering report](benchmark/results/phase5c/R5_94A-PORTABLE-RUNTIME-CONTRACT-REPAIR.md)
records an inactive new candidate blocked by inherited file-byte/OpenCode pins,
not Python incompatibility. No protected authorization follows.

The [R5.94B portable freeze](docs/freeze-dependency-classes-v1.md) pins exact canonical
content, qualifies Python/OpenCode through behavioral contracts and records physical
bytes/paths as provenance. **R5.94B-GENERIC-PROTECTED-CANDIDATE-2** initially passed
Python 3.14.3/OpenCode 1.18.32 first/restart and relocated LF/CRLF checks. Later live
OpenCode CLI failures block current machine eligibility; content pins and Python pass.
The configured worker model remains frozen independently. See the
[report and preflight command](benchmark/results/phase5c/R5_94B-CROSS-MACHINE-FREEZE-PORTABILITY.md).
The candidate is inactive; no B03 activation, authorization or access follows.

The [R5.94C worker transport contract](docs/ai-worker-transport-contract-v1.md) makes
OpenCode an optional implementation of a provider-neutral isolated-worker interface.
With `PYTHONPATH=src`, `python -X utf8 -m lykoi_transport.verify verify --implementation
opencode --executable <selected executable>` performs bounded public/synthetic checks.
The frozen Copilot/Sonnet model and all 137 inherited content pins remain unchanged.
Current status is **`R5_94C_BLOCKED_NO_FUNCTIONING_TRANSPORT_FOR_FROZEN_MODEL`**:
all eight first/fresh-process role attempts fail explicitly; final nontransport checks
pass, but no successor freeze or B03 authority is created. See the
[engineering report](benchmark/results/phase5c/R5_94C-PROVIDER-NEUTRAL-AI-WORKER-TRANSPORT.md).

The task application lives in [`air/task_manager.json`](air/task_manager.json)
(the `air/` path and `air_compiler` import path are retained for compatibility).
The current v0.3 model is documented in [`docs/axiom-v0.3.md`](docs/axiom-v0.3.md),
its JSON envelope in [`schema/axiom-v0.3.schema.json`](schema/axiom-v0.3.schema.json),
and the experiment in [`docs/research-log.md`](docs/research-log.md).
The historical v0.1 semantics are preserved in [`docs/air-v0.1.md`](docs/air-v0.1.md).
Existing `air/`, `air_compiler`, `axiom_version`, and schema paths remain stable
compatibility interfaces for saved models and research artifacts.

Phase 5's comparative-maintenance setup, conventional Python baseline,
external behavioral oracle, twenty sequential requests and execution records
are in [`benchmark/`](benchmark/README.md). Historical post-B16 histories were
revalidated against the corrected oracle; R5.3 reconstruction remains unfrozen.
R5.101 treats all twenty requests as exposed diagnostics, preserving those
historical boundaries and achieved histories.

## Large research evidence (Git LFS)

Bulk evidence and per-case result JSON under `benchmark/results/` automatically
use [Git LFS](https://git-lfs.com/) through round-independent patterns in
`.gitattributes`. No new rule is needed for each experiment round. Compact
captures, locks, comparisons, manifests, reports and application models remain
ordinary Git files. LFS preserves original bytes and paths, including research
hashes; Git commits contain small pointers instead of oversized JSON blobs.

Install Git LFS before cloning or contributing, then initialize it and download
the evidence in an existing checkout:

```powershell
git lfs install
git lfs pull
python benchmark/artifacts/git_storage.py install-hook
```

Commit `.gitattributes` together with the evidence files. Normal `git add`,
`git commit` and `git push` then store and upload bulk observations through LFS.
The optional local hook checks actual staged blob sizes and rejects raw data
accidentally staged for an LFS path. Install it once per checkout; hooks are not
cloned by Git. The installer preserves custom hooks and does not change Git config.
GitHub LFS storage and bandwidth quotas still apply.

If files were staged before these patterns changed, re-add the affected files
after staging `.gitattributes`. Older matched evidence may appear modified because
its new Git representation is an LFS pointer; re-adding preserves its local bytes
and records the storage conversion in the next commit. Existing history is not
rewritten. Run the check manually at any time:

```powershell
python benchmark/artifacts/git_storage.py check
```

The [artifact size audit and retention policy](benchmark/artifacts/README.md)
distinguishes disposable generated copies from original research observations.
Its [compact size/hash inventory](benchmark/artifacts/storage-audit-2026-10-07.json)
keeps provenance and reproduction references in Git. Future recreatable scratch
outputs belong in the narrowly ignored artifact directories; published evidence
remains preserved.

## Local development

Python 3.10+; no third-party dependencies. In PowerShell from the repository root:

```powershell
$env:PYTHONPATH='src'
python -m air_compiler.cli validate air/task_manager.json
python -m air_compiler.cli generate air/task_manager.json generated/task_manager.py
python -m air_compiler.cli inspect air/task_manager.json field_priority
python -m air_compiler.cli diff experiments/task_manager-v0.2-before-priority.json air/task_manager.json
python -m air_compiler.cli impact air/task_manager.json field_due_date --manifest generated/task_manager.manifest.json
python -m air_compiler.cli safety air/task_manager.json
python -m air_compiler.cli plan experiments/phase3-due-dates.plan.json
python -m unittest discover -s tests -p test_compiler.py -v
python -m unittest discover -s tests -p test_application.py -v
python -m unittest discover -s benchmark/harness -p test_baseline.py -v
```

The Phase 3 experiment plan is pinned to the **pre-change** model. After it has
been applied, its baseline hash deliberately prevents reapplication; consult
`experiments/phase3-prechange-impact.json` and
`experiments/phase3-impact-comparison.json` for the saved predictions and
outcome. On a matching baseline, `python -m air_compiler.cli apply PLAN` stages
the model and generated artifact, verifies them and rolls back on failure.

Run the application from a separate working directory: it stores `tasks.json`
in that directory. The generated artifact offers `create --title T --description
D [--priority LOW|NORMAL|HIGH] [--due-date UTC_TIMESTAMP]`, `list`, `list-high`,
`list-overdue`, `complete --id ID`,
`delete --id ID`, and `migrate`. Omitted priority defaults to `NORMAL`. An old
task file must be upgraded with `migrate` before other commands will read it;
this is an explicit, atomic schema migration. Overdue means pending with a
non-null due date strictly before the current UTC time.

**Never edit files under `generated/` directly.** Change the Lykoi model,
validate, regenerate, and verify the behavior. `generated/task_manager.manifest.json`
records provenance and the artifact hash. Changing Lykoi's semantic vocabulary
requires a compiler/backend change, a documented capability gap, and tests.

**Intent may be probabilistic. Program semantics should not be.**

**If the system knows an operation is invalid, it should be impossible for an AI-generated change to silently introduce it. Behaviors should possess the minimum authority necessary to perform their declared semantics.**
