# R5.50 — Benchmark reproducibility boundary review

## Decision and scope

Phase 5 requires **Tier 2 experimental reproducibility**, with Tier 1 behavioral
reproducibility as its target and selected inexpensive Tier 3 controls. It does
not require a hermetic operating-system build or adversarial-host attestation.
This review qualifies a **methodological boundary**, not a production capsule,
certificate, implementation capability or benchmark result.

Initial `git status --short` was empty. R5.49 remains
`R5_49_DEPENDENCY_CLOSURE_GAP`; its 78 receipts remain diagnostic-only and
non-reusable for production. R5.42–R5.49 records, classifications, failed gates,
locks and quarantines are preserved. The prospective standard below changes the
requirements for a **new** experiment; it does not repair an old experiment.

**R5.50 B02 exposure is zero.** No B02 reservation, dispatch, CheckedPlan,
readiness, audit, admission, static evaluation, generation, execution or frozen
acceptance was performed. B02 was not used as validation data. Core semantics
remain **30**, no #31. Phase 5C remains paused. B03 is prospectively untouched;
B17 remains unexposed/unclassified. No new execution machinery was installed.

## A–C. Research claim, threat model and tiers

The research question is: **Can Lykoi satisfy software-development requests with
behavior equivalent to a conventional implementation approach?** Required
equivalence means satisfaction of the same frozen externally observable contract
and invariants. Source, generated code, functions, classes, control flow, internal
storage, architecture and incidental formatting need not match. Formatting,
ordering, errors and durable-state details that the contract requires do matter.
An oracle's finite checks are evidence of satisfaction, not a universal proof.

| Threat class | Phase 5 obligation | Boundary |
| --- | --- | --- |
| Accidental experimental drift | Protect | Bind relevant state and dependency/configuration inputs; compare immediately before and after each stage and observation; reject stale/mixed evidence and detected mutation. |
| Benchmark overfitting/contamination | Strictly protect | Sealed authority, isolation, no unauthorized B02 feedback, controlled count, no post-lock repair, preserved history and contamination review. A cooperative host does not relax agent discipline. |
| Ordinary host variation | Declare; control when material | Record runtime/platform compatibility assumptions. Explicitly bind a particular component when its change plausibly changes a result relevant to the claim. |
| Actively malicious host | Outside claim | No guarantee against intentional ABA, lying runtime, hostile filesystem, compromised kernel or dispatch outside the trusted recorder. Detection of known interference still invalidates a run. |

Trust assumptions: honest local Python/Git/OS implementations, cooperative operator,
dedicated evaluation workspace, controlled recorder as the sole dispatch path,
no intentional workspace mutation, and ordinary reliable local filesystem
exclusive-create behavior. The benchmark is not an adversarial-host security
evaluation. Protecting project evidence from accidental secret publication is
still required; it is not a claim that the host is trusted with hostile secrets.

| Tier | Definition | Phase 5 choice |
| --- | --- | --- |
| 1 — Behavioral reproducibility | Another run on a compatible declared platform reproduces required externally observable behavior. | Scientific target; a single observation does not demonstrate repeatability by itself. |
| 2 — Experimental reproducibility | Record and preserve the relevant subject, compiler/profile, authority, evaluator, dependencies and effective controls sufficiently to explain and reconstruct the result. | Required standard. |
| 3 — Hermetic build reproducibility | Seal/content-address every material build/runtime dependency under the chosen closure. | Selective use: project file digests, direct dependency artifacts, immutable evidence and fresh dedicated source materialization. Full host closure is unnecessary. |
| 4 — Adversarial execution integrity | Trustworthy even against malicious concurrent mutation or compromised host behavior. | Not required; future separately claimed research. |

Tier 2 is sufficient because the claim concerns a known implementation satisfying
a known behavioral contract on a declared platform. Tier 1 alone cannot explain
which implementation/authority produced a result. Full Tier 3/4 would answer a
stronger, different question without improving the language comparison in
proportion to their cost. Cheap isolation is useful but must not silently become
a prerequisite for hostile-machine security.

## D–G. Controlled state and materiality

**Individually bind a dependency when a reasonably plausible change could alter
the benchmark result in a way relevant to the research claim.** This includes
changes that alter the authority, evaluator's verdict, contamination accounting
or published evidence, not only the application's output. A purely theoretical
ability of every machine component to corrupt computation is not this test.

For each inclusion or exclusion, record: resolved implementation/role, consumer,
plausible failure pathway, treatment and justification. Review declarations,
imports, startup/search paths, subprocess tools and dynamic/plugin entry points;
do not restrict the inventory to imports that happened to execute in one probe.
Use R5.49's resolved-source/content provenance, not helper-name exemptions.
Repository-owned copied/renamed helpers remain project experimental state.
Material UNKNOWN still fails closed. Ordinary host services with a documented
platform rationale are DECLARED_PLATFORM, not UNKNOWN closure obligations.

| State | Classification | Individually bound? | Reason |
| --- | --- | --- | --- |
| Lykoi semantic definitions and registry/ledger | EXPERIMENTAL_STATE | Yes, bytes and membership; count 30 | Determines meaning; count alone misses changed rules. |
| Existing Lykoi program/model | EXPERIMENTAL_STATE | Yes | This is the subject being compiled/tested. |
| Compiler, validator, lowering | EXPERIMENTAL_STATE | Yes | Determines admission and generated behavior. |
| Project runtime/support/profile definitions | EXPERIMENTAL_STATE | Yes | Boundary decoding, launch, persistence and capability configuration affect behavior. |
| Generated artifacts and manifests actually used | EXPERIMENTAL_STATE | Yes, with source/tool linkage | Identifies executed implementation; no source-similarity requirement. |
| Frozen requests/contracts/oracle/fixtures/protocol | BENCHMARK_AUTHORITY | Yes, original pins and versions | Determines required behavior and permissible observation. |
| Recorder/canonical protocol/admission/readiness/audit/harness | EVALUATION_STATE | Yes, used code and configuration | Determines verdict, evidence and counting. |
| Relevant committed/index/worktree/untracked/ignored content | PROJECT_STATE | Yes, scoped content and modes | Distinguishes intended and actually executed state. |
| Python implementation/exact version/build | DECLARED_RUNTIME | Declare exact descriptor and resolved executable; cheap image hash recommended | Python parsing, JSON, lowering and execution are relevant; no unlimited DLL closure. |
| Ordinary stdlib/built-in/frozen implementation | DECLARED_RUNTIME | Normally covered by declared runtime distribution | No per-file recursion by default; local patches/replacements material to computation must be bound. |
| Direct relevant Python dependency | EXTERNAL_DEPENDENCY | Usually yes: version, resolved implementation bytes/artifact | Version labels miss editable or same-version mutations. Core declares no third-party package requirement. |
| Material transitive package/plugin or native adapter | EXTERNAL_DEPENDENCY | Yes | Directness is not an exclusion if a plausible claim-relevant change exists. |
| Required external tool, including Git when used | EVALUATION_DEPENDENCY | Exact version/resolution and material script/config; cheap executable hash | Can change capture/verification; ordinary tool OS dependencies stop at platform. |
| Python interpreter native imports/CRT/system DLLs | DECLARED_PLATFORM | Normally no recursive binding | Ordinary execution substrate, not the experimental subject. |
| Crypto/hash service library | DECLARED_PLATFORM normally | Bind explicitly if crypto behavior/version is under test or a known issue changes evidence | Trust ordinary functioning SHA-256; do not attest its every native descendant. |
| Relevant environment/configuration | EXPERIMENTAL_CONTROL | Yes, effective child controls with absent/empty distinction | Search/startup, encoding, capability, store, provider and trace settings can change results. |
| OS family/version/build, architecture, filesystem behavior | DECLARED_PLATFORM | Declare | Limits compatibility; exact OS library identity is not the claim. |
| Locale/encoding/timezone | DECLARED_PLATFORM or EXPERIMENTAL_CONTROL | Declare/control when consumed | Text, time and path behavior can be materially dependent. |
| Clock/ID inputs, initial store and fixtures | PROGRAM_INPUT | Yes, fixture/provider identity and relevant policy | Nondeterminism must be controlled as required by the contract, not disguised as stable state. |
| AI model/provider/account | DEVELOPMENT_AUTHORING | No | Must not determine meaning of existing source. |
| AI API credential, including presence/fingerprint | DEVELOPMENT_AUTHORING | No | Not a core execution dependency; do not collect it. |
| OpenCode/editor/IDE/prompt history | DEVELOPMENT_AUTHORING | No | Influences creation, not fixed-source execution. |
| Explicit AI service used by a benchmarked application | PROGRAM_DEPENDENCY | Yes, if the contract declares it | Application integration is different from core language semantics; no such integration added here. |
| CPU microcode, machine serial/hostname | HOST_PLATFORM/IRRELEVANT_IDENTITY | No | Outside the behavioral claim; architecture assumptions are declared. |
| Unrelated installed packages and authoring files | OUTSIDE_BOUNDARY | No, after startup/search isolation | No blanket exclusion if an import hook/plugin can actually consume them. |

The current architecture includes both `src/air_compiler/` and the prospective
`benchmark/semantic/current_pipeline.py` family. A future manifest must identify
the pipeline actually used and all relevant project helpers, schema/spec/semantic
ledger, contracts and profile inputs; it must not substitute the root application
for a frozen track's state. `air/task_manager.json` remains canonical for the root
application. No language version, semantic vocabulary or generated file is changed
by this review.

**Native stopping rule:** stop at a declared, normally functioning runtime/OS
distribution unless the individual component is experimentally selected, locally
modified, configured as an application dependency, or has a reasonably plausible
specific effect on the required behavior/verdict. For example a selected native
database/crypto adapter under test is bound; incidental CRT allocation and Windows
API-set implementation are declared platform. Known hash defects would require
explicit control or invalidate evidence, but malicious libcrypto lying is Tier 4.
R5.49's direct PE names remain useful observations, not a future recursive gate.

The declaration must include OS family/version/build, architecture, exact Python
implementation/version/build, filesystem case/path/exclusive-create assumptions,
effective text encodings and any consumed locale/timezone. Compatibility is a
documented set of these requirements, not merely “Windows” or “Python 3”. An OS
patch need not invalidate subject qualification if it remains compatible and has
no material known effect; a new run records its actual platform. Compatibility
is an assumption until replicated, not demonstrated cross-platform equivalence.

## H–J. Git, working state and reasonable TOCTOU

Content identity is sufficient for relevant repository state when combined with
the effective execution configuration and scoped Git provenance. Capture a sorted
manifest with, for each relevant path: committed blob/content identity or absence,
index content/mode or absence, physical worktree byte hash/mode, and the role.
Relevant staged-only differences count even if physical execution bytes agree.
Bind execution-relevant untracked **and ignored** inputs and membership in import,
plugin, fixture or test-discovery roots. Absence, additions and deletions matter.
No whitespace/line-ending normalization is allowed for physical execution bytes.

Record HEAD as provenance, not as a substitute for content or a mandatory identity
of unrelated commits. Raw index file hash, reflogs, branch labels, remote URLs,
user identity, object packing and unrelated Git metadata need not be frozen.
Relevant tuple content/modes are enough; a repack with identical selected objects
is not drift. If a check actually consumes ancestry, replacements, submodules,
filters/attributes/ignore/config/helpers, resolve/control those inputs or omit
that check prospectively with a documented replacement. No historical ancestry
check is silently bypassed. Fail closed on unresolved links, gitlinks or unmerged
inputs until their relevant targets/state can be captured.

Prefer explicit membership and physical hashes, sanitized Git invocations, and
recorded committed/index content obtained without text conversion. Materializing
a dedicated copy and removing input bytecode caches, disabling site/user startup,
and using explicit source/tool paths reduce accidental shadows. `-B` alone does
not prevent bytecode reads. These are small prospective controls to qualify on
generic fixtures before use, not a demand to hermetically reproduce Git or Python.
Report/evidence output directories must not also be import/discovery inputs.

**Required TOCTOU rule:** independently recapture relevant experimental state
immediately before and immediately after observation; invalidate the run on any
material difference or detected concurrent modification. Apply the same rule
around verification stages; all accepted stages must reference one common state,
policy, authority and mechanism set. Recheck immediately before reservation;
leave no intervening editing/configuration step. Check relevant external
dependency content and effective configuration, not merely repository hashes.

Run in a dedicated evaluation workspace, disable automatic formatters/updaters
for the run, use controlled output paths, and prohibit intentional mutation.
If an update, partial capture, filesystem failure or interruption is detected,
record FAIL/INCOMPLETE/HALT as appropriate and stop. A later restored state does
not clear an already recorded violation. Evidence is immutable and not resealed.

R5.49's **A → B → A** counterexample is valid: endpoint hashing cannot establish
exclusive ownership or detect every transient mutation. This is an explicit
limitation of the chosen cooperative-host claim, not a refutation of Tier 2.
No absolute ownership/ABA prevention proof is required. Read-only materialization,
containers or other cheap isolation may be added; they must not be described as
proof against an adversarial kernel. Known transient mutation invalidates a run
even if endpoint hashes match. Unobserved intentional malicious ABA is outside
the threat model. Ordinary concurrency is discouraged and detected where possible;
endpoint checks do not guarantee discovery of every accidental transient either.

## K–M. AI independence and benchmark integrity

**Authoring environment ≠ language execution environment.** Lykoi is an AI-native
language, not an AI runtime. A model, another model or a human editor may create
different programs. Once source exists, semantic definitions, validation,
deterministic lowering, compilation, declared inputs and runtime determine meaning.
The compiler must not ask which model authored it. OpenAI, Anthropic, Google,
OpenCode, model selections, credentials, accounts, editor and prompt history are
excluded from core execution identity. No network-accessible inference is required.
A future explicit application AI dependency is separately declared, not inferred
from the development agent. Authoring telemetry can remain a separate,
secret-safe fairness record: Phase 5's same-model/config/time-budget rule for
comparative *authorship* is preserved, without putting model identity into language
execution identity. Authoring changes may affect a productivity comparison's
fairness; they do not change an already existing program's semantics.

Mandatory at every tier:

1. Preserve frozen B02 authority and its original pins; no authority rewrite.
2. No B02 feedback before separately authorized observation, including static probes.
3. One controlled durable reservation/dispatch path and explicit zero/one/multiple/
   indeterminate accounting; incomplete dispatch is not asserted to be zero.
4. No post-lock observation repair, reduced-slice retry or rerun-to-pass.
5. Preserve historical outcomes and stopped/quarantined evidence.
6. Contamination checks and independent generic evidence; no benchmark-specific logic.
7. Explicit PASS/FAIL/INCOMPLETE and no passing inference from buffered/interrupted work.
8. Diagnostic receipts never authorize qualification by relabeling or reuse.
9. Bind semantic definitions and track exact integer core count **30**.
10. Judge both tracks against required behavior, not implementation resemblance.
11. Secret-safe publication before persistence; no raw environment/config/output dumps.

Recorder exclusive creation and integrity hashes protect ordinary local evidence;
they are not hostile-host attestation. No secret fingerprints/presence metadata
are needed for irrelevant authoring credentials. A material application secret
needs the R5.47 protected keyed treatment and custody policy; its plaintext must
not enter a capsule. The next static gate has no justified core AI credential need.

## N–P. Proposed small experimental capsule and allowed claim

Proposed schema **ExperimentalCapsuleR5.50/Tier2**, not ExecutionCapsuleV2:

| Component | Required contents |
| --- | --- |
| Boundary | Versioned policy, purpose/claim, cooperative threat model, inclusion/exclusion/materiality rationale, core count. |
| Subject | Relevant model/program, semantic/compiler/validator/lowering/runtime/support/profile hashes and membership. |
| Authority | Frozen requirement/contract/oracle/fixture/protocol identity and original pins. |
| Evaluator | Used harness, recorder, canonical protocol, readiness/audit/admission and orchestrator hashes/versions, observation policy. |
| Repository | Relevant committed/index/physical content tuples, modes and membership; generated/source linkage. HEAD is separate provenance. |
| Dependencies | Exact relevant distribution/tool versions, resolved paths/roles, implementation hashes or preserved artifact identifiers; edited sources need content hashes. |
| Runtime/platform | Exact Python descriptor, executable resolution, optional inexpensive image digest; declared OS/build/architecture/filesystem/encoding compatibility. |
| Effective controls | Public allowlisted values, absent/empty distinctions, actual argv, cwd/path roles, import/startup/cache policy, store/fixture/provider/trace controls. No ambient credential collection. |
| Evidence links | New experiment ID, authorization identity, required stage names/mechanisms/statuses/receipt digests, capsule identity, authority identity and contamination outcome. |

Canonical identity covers the relevant state and its boundary policy; observational
metadata such as capture time and unrelated commit labels are provenance, not
freshness proof. Immutable envelope hashes cover the recorded provenance too,
but unrelated authoring changes do not invalidate execution state. Every stage,
reservation and observation links the same state/authority/policy and **new
experiment ID**. Before/after captures are separate evidence. State or platform
description changes produce new recorded capsules; compatibility does not permit
silent reuse of old receipts. No cross-experiment diagnostic reuse is proposed.

Keep exact manifests/artifacts available to reconstruct the subject; hashes alone
cannot recover unavailable content. Runtime/platform distributions must be
identifiable and obtainable, with documented compatibility requirements and known
limitations. This is enough to answer “what exactly did we test?” without preserving
every OS DLL. Production construction/integration remains to be checked in a new
experiment; these review fixtures are not that construction.

**Allowed behavioral-result claim, only after a separately authorized behavioral
observation:** “Under the recorded Lykoi implementation, declared dependency set,
frozen benchmark authority and declared compatible host platform, the observed
implementation satisfied the frozen externally observable behavioral contract
in the recorded acceptance observations, with the reported coverage and limitations.”

Do not claim bit-for-bit reproducibility on every machine, identical source,
universal correctness, generality, hostile-host integrity or demonstrated repeatability
without corresponding evidence. For the next **static** gate the narrower claim is:
“The locked analyzer/profile system reported [result] for the frozen whole-contract
static transfer under recorded state.” A static prediction is not generated
behavioral satisfaction. No such B02 prediction is made in R5.50.

Cross-platform Windows/Linux/macOS or alternate Python results belong to a future
portability experiment unless the frozen contract already requires them. Portability
and benchmark integrity are separate questions; no new portability gate is imposed.

## Q. Outcome taxonomy

| Outcome | Meaning and treatment |
| --- | --- |
| Lykoi capability failure | Frozen language cannot express/compile/execute required behavior; substantiate the missing general capability. |
| Lykoi behavioral failure | Implementation executes but violates frozen behavior/invariants; distinguish compiler/runtime defect from authored implementation error. |
| Infrastructure failure | Recorder/oracle/capture/supervisor fails; invalidate or mark incomplete, not a language capability gap. |
| Platform incompatibility | Declared platform lacks a required supported property; report platform separately. |
| Reproducibility limitation | Evidence cannot support a stronger claim, e.g. hermeticity/ABA resistance; limit the claim. Missing Tier 2 state still blocks qualification. |

A directly material unresolved dependency is an experimental-state gap, not
automatically a language failure. Once the relevant platform assumption is met,
a program violating the contract is not excused as “platform variation” without
evidence. Infrastructure uncertainty cannot be scored as either language success
or failure. Behavioral tests, capability diagnoses and methodology qualifications
must remain separate observations.

## R–S. Reassessment of R5.42–R5.49 safeguards

Every blocking safeguard below protects a stated claim or known integrity risk.
The table is prospective disposition of lessons, not new historical classifications.

| Source / safeguard | Disposition | Research connection |
| --- | --- | --- |
| R5.42: representation-aware evidence comparison; prepass halt | KEEP | False tuple/list inequality is infrastructure failure, not language support failure. |
| R5.43: canonical bytes, strict scalar/order/absence distinctions, immutable receipts | KEEP | Prevents evidence corruption and spurious equality; supports known result identity. |
| R5.43: sole dispatch path, exclusive reservation, indeterminate halt, no retries | KEEP | Prevents feedback loops and false zero/exactly-one claims. |
| R5.44: completed verification before exposure | KEEP | An interrupted prepass cannot authorize an observation. |
| R5.44: monolithic command/full duplicate suites as one tool call | SIMPLIFY | Bounded relevant stages preserve guarantees without an accidental 120-second requirement. |
| R5.45: stage status/mechanism/state binding, complete set, stale/mixed rejection | KEEP | Prevents changed implementations being authorized by old or incompatible evidence. |
| R5.45: repeatedly run all regressions/focused duplicates irrespective of change | SIMPLIFY | Select documented coverage of used mechanisms plus generic coherence/contamination checks; no missing mandatory guarantee disguised by counts. |
| R5.46: before/after state checks and quarantine on detected drift | KEEP | Real concurrent repository correction was detected; cooperative controls must retain this protection. |
| R5.46: broad raw Git/config/all-host identities | SIMPLIFY | Scoped content and effective consumed configuration protect experimental identity; incidental metadata does not. |
| R5.47: secret-safe publication, redacted diagnostics, preserved security correction | KEEP | Protects project evidence; never restore exposed data to satisfy an old seal. |
| R5.47: historical locks and explicit successor/difference records | KEEP | Preserve evidence and authority. New relevant-state manifest can link originals without treating all archived files as executed dependencies. |
| R5.48: AI independence and authoring/execution separation | KEEP | Existing-program meaning must not depend on an authoring provider. |
| R5.48: import/startup/cache/environment inventory | SIMPLIFY | Explicit paths, no-site/fresh-input policy and relevant resolved implementations replace indiscriminate host inventory. |
| R5.49: resolved source/content provenance, editable distinction, material UNKNOWN rejection | KEEP | Deployment names do not establish ownership; real dependencies must be known. |
| R5.49: interpreter/CRT/crypto/OS unlimited recursive closure | DEFER_TO_FUTURE_HERMETIC_WORK | Declared platform suffices for the chosen claim; individually material exceptions stay bound. |
| R5.49: absolute immutable ownership/adversarial ABA exclusion | DEFER_TO_FUTURE_HERMETIC_WORK | Endpoint checks plus cooperative workspace rules serve Tier 2; stronger adversarial attestation needs a separate threat model. |

Unknown ordinary OS descendants and malicious ABA therefore cease to be future
Tier 2 blocking obligations **only through this prospective policy**, not through
retroactive receipt promotion. Relevant project state, authority, dependency
implementations, effective controls and benchmark discipline remain blocking.
Mechanisms disconnected from behavioral correctness, fairness, contamination,
reasonable reproducibility or evidence security are future engineering work.

## Validation: fresh generic/synthetic witnesses and limitations

No unrestricted harness discovery or historical qualification runner was invoked.
Reviewed authority governance: `benchmark/README.md`, `requirements/README.md`,
`harness/README.md`, R5.2.2 checkpoint and R5.42–R5.49 reports. B02 request/profile
or saved semantic application was not loaded into any evaluator.

The default `python` command was unavailable. Validation used the already available
CPython **3.12.10**, Windows AMD64 portable interpreter:

```powershell
& 'C:\Users\lblan\AppData\Local\Temp\opencode\python-r531\python.exe' -B benchmark/results/phase5c/r5_50_review.py
```

The first recorded run, `R5_50-validation.json`, is retained as **FAIL**: 107 tests,
104 passed, two historical security-suite assertion failures and one new fixture
error. The fixture incorrectly expected ProtocolFailure for the publication
wrapper's redacted SecretRejected; it was corrected in review development, before
any benchmark observation. Historical checks were not edited:

- `test_historical_lock_unchanged`: raw physical bytes differ from committed bytes;
  `git ls-files --eol` reports **i/lf w/crlf** for the historical manifest.
- `test_ignore_effective_behavior`: this host's quiet `check-ignore` invocation
  returned 0 for `.env.example`; verbose inspection reports the repository's
  negated `!.env.example` rule. The historical return-code assertion fails.

These are reported infrastructure/checkout diagnostics, not capability failures.
No historical manifest, ignore rule or checkout was rewritten to force a pass.
The focused selection explicitly excludes those **two** historical host checks;
it does not label them skipped/passed or qualify historical locks on this host.
Future production preparation still has to validate physical relevant state and
effective configuration. This review's success is methodological, not a claim
that this checkout satisfies all historical production preconditions.

The corrected focused run, `R5_50-validation-focused.json`, records **105/105 PASS**:
18 new boundary witnesses, 33 synthetic certificate, 29 canonical recorder,
20 publication/security witnesses and 5 fresh AI-independence tests. Used mechanism
hashes match before/after each recorded review run. Existing evidence is context,
not reused qualification. The following required detections are witnessed:

| Required validation | Fresh witness |
| --- | --- |
| Lykoi source mutation | `BoundaryTests.test_lykoi_source_mutation` |
| Semantic-registry mutation | `test_semantic_registry_mutation` |
| Compiler mutation | `test_compiler_mutation` |
| Profile mutation | `test_profile_mutation` |
| Authority mutation | `test_benchmark_authority_mutation`, using synthetic mineral authority |
| Direct relevant dependency mutation | `test_direct_dependency_same_version_mutation` |
| Relevant environment mutation | `test_relevant_environment_mutation`, absent/empty distinction |
| Stale evidence | `test_stale_evidence`, existing certificate stale-stage/authorization tests |
| Mixed-state evidence | `test_mixed_state_evidence`, existing mixed/missing/INCOMPLETE rejection |
| Repeated unauthorized observation | `test_repeated_unauthorized_observation`, canonical recorder second-dispatch and multiple-receipt tests |
| Post-observation repair | `test_post_observation_repair_invalidates_no_recovery`, canonical post-observation halt/no-repair tests |
| Raw-secret persistence | `test_raw_secret_persistence_rejected`, 20 R5.47 publication tests |
| Irrelevant model/editor selection | `test_authoring_selection_does_not_invalidate`; five existing core/offline/provider-mutation probes pass freshly |

Additional new witnesses cover evaluator/generated bytes, new input membership,
and recording a declared platform without native recursion. These deliberately
small tests use the existing synthetic-only certificate primitives; their projected
descriptor is **not a production capsule implementation**. The environmental
exclusion follows this fixture's explicit consumer contract, not a universal
variable-name exemption. Offline probes cover inspected core validation/lowering/
read-only execution, not all future programs. No hermeticity, generality or
cross-platform repeatability follows from 105 passes.

Final review integrity is recorded separately in `R5_50-final-integrity.json`
by `r5_50_final_verify.py`: strict canonical evidence reload, preservation of the
107-test failed run, exact 105-pass focused accounting, unchanged focused mechanism
hashes, only the four intended tracked documentation edits, report/artifact hashes,
and successful `git diff --check`. This is review integrity, not replay or
qualification of any historical physical byte lock.

## T. Smallest next experimental gate — proposed, not performed

The next gate can be a **newly authorized, locked, one-observation whole-contract
static transfer experiment under Tier 2**, with generic preflight in that new
experiment. No separate unlimited host-closure project is a prerequisite.

1. Obtain explicit new experiment authorization and freeze the prospective policy,
   exact static callback/consumers, state membership, mechanisms and stop rules.
   Qualify any small new capsule adapter on generic fixtures first; no B02 data.
2. In a dedicated workspace, verify relevant implementation/semantic/profile,
   evaluator, dependencies and effective controls; fresh bounded checks must cover
   recorder/publication/state mutation, generic support coherence and contamination.
   Construct the Tier 2 capsule with declared platform and preserved artifact access.
   Old R5.49 diagnostics and quarantined receipts cannot satisfy this step.
3. Verify frozen B02 authority by **integrity-only original pins**, without support
   evaluation. Establish exact count 30 and no prohibited implementation repair.
4. Verify a new recorder's zero prior reservations/observations and no halt/final;
   preserve older B02 history separately. “Zero under this experiment” does not
   erase earlier authorized historical B02 observations. Uncertain count halts.
5. Recapture required state immediately before one durable reservation. Authorize
   exactly **one** locked whole-contract static callback; its named CheckedPlan/
   readiness/audit/admission consumers must be declared as that single observation,
   without independent exploratory dispatches. No generation/execution/acceptance.
6. Record raw secret-safe static findings, verdict and accounting, including all
   negative/incomplete outcomes. Do not change implementation/profile after feedback.
7. Immediately recapture state afterward; invalidate on material differences,
   detected interference, broken evidence or uncertain completion. No repair/retry.
8. Stop and preserve final accounting. A static PASS needs separate authorization
   before any behavioral experiment and does not advance Phase 5C automatically.

These steps were **not performed against B02 in R5.50**. Boundary qualification
does not itself authorize or reserve anything. Accidental B02 exposure in this
review would require protocol halt; none occurred.

## Conclusion

The claim, cooperative threat model, required tier, materiality rule and native
stopping boundary are explicit. Tier 2 preserves strong benchmark integrity and
reasonable drift protection while excluding development AI state and stronger
unclaimed hostile-host/hermetic guarantees. Git/context capture is a scoped
content/configuration obligation, not an OS reconstruction obligation. Focused
witnesses support the detection rules; actual future capsule construction and
observation remain unperformed. Core **30**, B02 exposure **zero**, Phase 5C paused.

Primary classification:

**`R5_50_PHASE5_REPRODUCIBILITY_BOUNDARY_QUALIFIED`**
