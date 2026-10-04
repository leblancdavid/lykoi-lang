# R5.36 — Checked Public Launch Profile Completion Review

Prospective independent review, 2026-10-03; preceding gate
`R5_35_GENERIC_TRANSPORT_BOUNDARY_PARTIAL`.

**Decision: the known benchmark-critical launch boundary is resolved independently.**
Recommend **R5.37 = comprehensive frozen B02 retry**. The decision follows actual
standalone processes, independent correlation/endpoint challenges and a post-lock
frozen-contract screen. Complete B02 integration remains unexecuted; readiness
does not predict acceptance success or establish universal implementation correctness.

Evidence: [R5_36-launch-evidence.json](R5_36-launch-evidence.json).
Machine readiness: [R5_36-readiness-matrix.json](R5_36-readiness-matrix.json).
Versioned interface: [public-launch-r5.36.md](../../../docs/public-launch-r5.36.md).
Core remains **30**, no #31. No old compiler/binding/transport/runtime files changed.

## 1. Current launch audit

Traced paths: current_pipeline.observe -> generated operation.py ->
refined_runtime_r5_28.run_application/run; R5.35 observe ->
transport_runtime_r5_35.main -> generated operation.py. Public transport receives
four infrastructure positional values before its public operation tokens.

| Externally supplied value/setup | Classification | R5.36 disposition |
| --- | --- | --- |
| interpreter and executable entry path | PUBLIC_PROCESS_INPUT | normal OS/interpreter invocation identifies the copied bundle |
| command and all application flag/value tokens | PUBLIC_PROCESS_INPUT | forwarded byte-for-text-token unchanged to R5.35 |
| cwd | PUBLIC_PROCESS_INPUT | OS supplies it; absolute resolved cwd is independently observed |
| ordinary OS environment, temporary root, interpreter search | PUBLIC_PROCESS_INPUT | ordinary Python/local filesystem prerequisites; no application configuration from these |
| semantic model/operation contracts | CHECKED_LAUNCH_CONFIGURATION | provisioning input to existing compiler, never normal invocation argv |
| application/profile/unit/generation/provenance identity | CHECKED_LAUNCH_CONFIGURATION | canonical checked metadata, existing manifests/seals, launch-profile digest |
| transport route/argument/presentation/error/stream/exit metadata | TRANSPORT_CONFIGURATION | unchanged checked transport.json; launch binds its identity |
| explicit state versions/initial declarations/missing-store reference | PERSISTENCE_CONFIGURATION | unchanged R5.35 declarations/policy; launch binds combined identity |
| store path in observe/helper argv | HIDDEN_INFRASTRUCTURE_DEPENDENCY | eliminated from public argv; checked cwd-relative store policy |
| semantic trace and transport trace paths in helper argv | HIDDEN_INFRASTRUCTURE_DEPENDENCY | internally allocated temporary paths, embedded in evidence bundle |
| invocation identity in helper argv | HIDDEN_INFRASTRUCTURE_DEPENDENCY | generated internally, correlated with observed PID/new evidence file |
| trace/evidence directory/channel | TRACE/OBSERVATION_CONFIGURATION | checked cwd-relative local required channel |
| generation passed directly to operation.py | CHECKED_LAUNCH_CONFIGURATION | unchanged internal runtime protocol; supplied by checked transport |
| decoded JSON payload passed directly to operation.py | TRANSPORT_CONFIGURATION | unchanged R5.32/R5.35 binding output, not public bootstrap input |
| ambient LYKOI_R5_22_CAPS provider descriptor | HIDDEN_INFRASTRUCTURE_DEPENDENCY | overwritten from checked launch provider selection; no ambient semantic override |
| repository PYTHONPATH for research module execution | HIDDEN_INFRASTRUCTURE_DEPENDENCY | unnecessary for copied standalone bundle; public interpreter uses -E |
| controlled clock/ID values | TEST_ONLY | explicitly controlled_test profile, typed and distinguishable from production |
| temp bundle/cwd creation, seeded fault stores, copied mutations | TEST_ONLY | independent experiment setup, not required application arguments |
| expected source/profile/durable snapshots/public capture | TRACE/OBSERVATION_CONFIGURATION | independent observer authority, not passed to application |
| archived experiment/checkpoint paths, old task launch/protocol scripts | HISTORICAL_ONLY | preserved; not used as launcher templates |

Every hidden value needed for normal invocation is now internally derived from
checked configuration or allocated by generic bootstrap. The internal transport
subprocess still uses its established infrastructure protocol; making those values
internal does not require redesigning transport or exposing them to the user.

## 2. Launch responsibility boundary

Launch locates co-located metadata/artifacts, validates compatibility, resolves
infrastructure locations, selects an existing checked capability provider,
allocates invocation/evidence resources, invokes checked transport and relays its
public process result. It cannot define behavior, predicates, state transitions,
semantic defaults, migrations, result values or domain validation. Declared state
values remain in the existing state profile; launch only binds their policy identity.

## 3. Checked launch profile

Deterministic JSON metadata uses exact keys: version, id, application, generation,
provenance, transport, persistence, capabilities, store, trace, runtime, provider.
Canonical SHA-256 references bind source, complete generated manifest, CheckedPlan
unit identities, checked transport, combined persistence declaration/policy and
plan-derived capability signature. Path/runtime/provider fields are bounded data,
not executable templates. Syntax is machine-oriented; no human-friendly language.
Machine evidence contains both independent applications' exact source/configuration
and emitted profile, so hashes and declarations are reproducible from the record.

## 4. Profile validation

Existing transport/generated artifact/runtime/generation/unit integrity checks
precede launch validation. A new generation-bound seal covers launcher, launch.json
and capabilities.json. Runtime checks every identity reference, exact supported
runtime, cwd path policy, evidence policy, no overlapping state/evidence paths,
exact required capability types and provider values/mode. Reject incompatible
identity/transport/persistence/signature, unknown runtime/provider, missing required
provider, incompatible controlled value, unsupported trace or store policy before
normal transport/semantic invocation. Focused tests alter every reference and
stale artifact; five unsealed file mutations reject even with a missing store.
Checksums are revision integrity, not hostile-writer authentication.

## 5. CWD-relative store resolution

Checked `{base:"cwd",path:RELATIVE,parent:"require_existing"}` resolves against
the actual process cwd, with no repository root dependency. `register.json` and
`durable/archive/register.json` are independent study metadata, not launcher
constants. The same launch bytes/profile run from two different temporary cwd
directories and resolve different durable stores while retaining identical identity.

## 6. Path rules

Nonempty slash-separated relative segments; no absolute/drive/colon/backslash,
empty segment, dot/dot-dot traversal, NUL/control characters or trailing space/dot
segments. Ordinary segment-internal spaces are allowed. Normal, nested, changed-cwd,
missing-parent and missing-required-trace-directory subprocesses are tested;
absolute and invalid forms reject at metadata checking. Store parent must already
exist; launch never makes it. Trace directory may create parents or require existing.
Filesystem resolution follows existing symlinks; OS-invalid names/permissions can
still fail. This is predictable local resolution, not a security sandbox.

## 7. Persistence integration

Resolved store path goes directly to unchanged R5.35 persistence mediation.
REQUIRE_EXISTING versus INITIALIZE_DECLARED_STATE remains authoritative there.
Launch never invents or writes state. Missing origin is staged privately by R5.35;
only a successful generated attempted write causes durable realization. Directory
preflight is infrastructure, not state initialization or migration.

## 8. Trace bootstrap

Local required evidence directory is checked configuration. Bootstrap allocates
a UUID plus temporary semantic/transport paths, invokes transport, and emits one
exclusive `<UUID>.json` bundle containing actual internal records and public
process result. Internal temporary files are removed afterward. Evidence creation
is allowed on read-only calls; the application durable store remains absent.
No research-only positional parameters or public trace switches are required.

## 9. Trace integrity

Bundle correlation includes application digest, launch-profile digest/id, generation,
complete provenance and transport identities, invocation UUID, PID, executable,
entry script, exact argv/cwd/resolved store/evidence paths, public stdout/stderr/exit
and physical pre/post digests. Embedded semantic record retains operation identity,
generation, invocation, input/outcome and actual external values. Independent
observation binds evidence to a new file from the actual Popen process. Different
application/profile/generation/PID/path/argv/UUID refuses launch grounding; changed
semantic invocation refuses semantic grounding. No foreign trace silently grounds.

## 10. Public argv isolation

The launcher interprets **zero public tokens** as bootstrap configuration. All
`sys.argv[1:]` tokens go unchanged to checked transport. A focused profile aliases
an actual application collection flag to `--launch-profile`; its value reaches
semantic input correctly. Fault F consumes the command and fails correlation.
Bootstrap metadata is always co-located, never inferred from application flag names.

## 11. Environment boundary

No application launch configuration variable is supported/required in this bounded
architecture. The public command uses Python `-E`; child Python also uses `-E`,
with PYTHON-prefixed environment entries removed. Ambient LYKOI_R5_22_CAPS is
overwritten by the checked provider descriptor. Ordinary OS environment supplies
normal interpreter/temp resources. A real subprocess with poisoned ambient provider,
nonexistent PYTHONPATH and undeclared store/trace variables still uses production
providers and declared paths. No arbitrary environment-based semantic behavior.

## 12. Capability-provider bootstrap

capabilities.json is a canonical union of authoritative CheckedPlan requirements.
Providers must declare exactly those types, consistent with the unchanged runtime's
fresh_unique_id:string / utc_clock:instant registry. Production selects existing
real UUID/UTC behavior with no configured return values. Controlled_test requires
every typed value explicitly; no fallback from a missing test provider. Wrong
clock type, missing provider, unknown provider and production fixed values reject.
Actual used values remain in generated semantic traces. No new capability semantics.

## 13. Application A

Independent same-shape acoustic public station extends the R5.35 non-task source
with a second semantic operation, stamp, requiring clock/identity capabilities.
Calibrate has repeated and JSON-array public routes. Five calls exercise omitted
collections, duplicate/trim normalization with untouched binding input, explicit
empty JSON, production stamp and malformed scalar noninvocation. An additional
changed-cwd call exercises the same bundle. All six pass applicable layers.
Launch contains no acoustic fields or operation-specific behavior.

## 14. Application B

Unchanged R5.33 specimen versioned-envelope source runs through identical launcher
bytes: legacy read -> legacy_insert -> legacy read -> migrate -> current read ->
current_insert -> current read -> unavailable legacy read. Seven typed executions
and one generated applicability rejection; all applicable layers conform. The
changed-cwd legacy read sees a fresh absent store and declared V1, not prior V2.
No application-B launcher change or wrapper. Every adjacent durable byte link agrees.

## 15. Missing-store lifecycle

REQUIRE_EXISTING missing legacy read emits checked public persistence failure,
exit 1, no semantic event and no store creation. INITIALIZE_DECLARED_STATE missing
read executes over declared origin but remains file-free. First legacy_insert
materializes V1 plus its generated write; migrate produces V2, then current writes
and reads use V2. Focused REQUIRE_EXISTING and initialize-read cases corroborate
the full lifecycle. Launch itself never creates semantic state.

## 16. Changed-cwd results

A and B each reuse one temporary generated bundle from two separate temporary cwd
directories. Command/script/profile identity is identical; resolved store and
evidence directories differ. Second-cwd pre-state is absent. B's first cwd reached
V2; its second cwd still reads the declared V1 origin. This exposes repository-root
and previously used store assumptions. Nested preexisting store-parent case writes
successfully; missing-parent/required-trace-directory cases reject before execution.

## 17. Public-only invocation

Exact supported command surface:

```text
python -E "<generated-bundle>/launch_runtime_r5_36.py" calibrate --channels " left " --channels left --samples 3
python -E "<generated-bundle>/launch_runtime_r5_36.py" stamp
python -E "<generated-bundle>/launch_runtime_r5_36.py" legacy
python -E "<generated-bundle>/launch_runtime_r5_36.py" migrate
python -E "<generated-bundle>/launch_runtime_r5_36.py" current
```

Caller supplies interpreter/executable identity and intended public tokens only.
Cwd/environment are ordinary process context. No store, trace, semantic profile or
provenance path appears as an application argument. Checked metadata was provisioned
alongside the generated executable, as configuration normally is.

## 18. Grounding

Observer independently resolves expected state/evidence locations, snapshots
durable bytes/absence, records actual command/cwd/PID/stdout/stderr/exit, and reads
exactly one newly emitted evidence file. Challenger reconstructs expected launch
and checked transport profiles from independent source/configuration and generated
provenance, verifies identity/process/path/public/durable linkage, then delegates
to existing R5.35 binding/persistence/output and current semantic challengers.
No observed state endpoint is taken solely from the trace. UUID comes from bootstrap;
PID and newly created filename couple it to the actual process without a caller-
supplied research invocation argument. Endpoint grounding is not hostile attestation.

## 19. Layered verdicts

LAUNCH_PROFILE_CONFORMANT, TRANSPORT_CONFORMANT, INPUT_BINDING_CONFORMANT,
PERSISTENCE_BOUNDARY_CONFORMANT, SEMANTIC_EXECUTION_CONFORMANT and OUTPUT_CONFORMANT
remain separate; launch_grounded is a separate prerequisite. TRANSPORT_CONFORMANT
combines the existing transport profile, grounding and routing/raw-argument checks;
input conversion and output remain distinct. Unreached layers are null. Malformed
input and persistence/applicability failures never get a fabricated semantic pass.
Structurally valid profile plus missing directory can have profile=true but no
grounded execution; the expected failure is independently observed as exit 4.

## 20. Six-fault matrix

All injections are disposable; copied launcher faults are resealed against actual
bytes, leaving independent source/profile authority unchanged.

| Fault | Injection | Observed discrimination |
| --- | --- | --- |
| A stale application/profile identity | launch application reference incompatible with generation | LAUNCH_PROFILE_CONFORMANT=false; exit 4; no evidence/semantics/store |
| B wrong relative store | resolve a different store instead of declared metadata path | launch_grounded=false; independently expected store remains absent while unexpected store is created; no downstream conformance claimed |
| C wrong trace identity | correct execution records foreign profile_id | launch_grounded=false despite generated record/public/state being emitted; foreign identity cannot ground current launch |
| D hidden helper required | require --research-helper before any normal launch | public-only command fails exit 4/no evidence; architectural readiness gate fails |
| E wrong capability provider | utc_clock provider type changed to integer | LAUNCH_PROFILE_CONFORMANT=false; exit 4 before binding/semantic execution |
| F consume public argument | remove first public argv token in launcher | emitted argv differs from actual observed command; launch_grounded=false; no semantic execution |

Fault B is not merely a wrong filename string: actual generated write reaches the
unexpected store, independently detected against absence at the expected path.
C does not receive a semantic pass under uncorrelated evidence. Additional focused
tests challenge every correlation identity and embedded semantic invocation.

## 21. Metadata-only mutations

Six launch.json-only mutations preserve identical launcher digest and each
application's original generated artifact digest. Launch seal is recomputed; no
algorithms or semantic/transport/state declarations change.

| Mutation | Outcome |
| --- | --- |
| relative store location | B generated write materializes alternate-register.json, with conformant layers |
| trace directory | A evidence appears at alternate-evidence, with conformant layers |
| profile identity | same A semantics/provenance, different checked launch identity, conformant |
| persistence profile reference | incompatible digest rejects before execution; configuration cannot silently override R5.35 policy |
| transport profile reference | incompatible digest rejects before execution |
| controlled provider profile | stamp uses explicit controlled_test typed ID/time; applicable layers conform |

Four valid changes execute conformantly; two intentionally incompatible reference
changes demonstrate preflight rejection. They are not claimed as supported arbitrary
profile selection. Transport/persistence profiles are provisioned through the
existing checked assembly; launch binds the installed profile rather than redesigning
it. Semantic source and emitted algorithm bytes stay identical per application.

## 22. Profile integrity chain

Semantic application digest -> CheckedPlan unit digests -> generated provenance
and artifact/runtime digests -> checked transport digest/seal -> combined checked
persistence policy/state digest -> launch profile digest/seal and capability signature
-> actual invocation UUID/PID/cwd/argv -> embedded transport/semantic trace plus
public/durable evidence. Both independent authority reconstruction and installed
bundle integrity are checked. Stale compatible-looking identities, transport or
persistence references and changed artifacts fail. A resealed disposable runtime
can still be behaviorally challenged; checksums do not prove faithful execution.

## 23. Source-authority audit

Audited new launch_runtime_r5_36.py and checked_launch_r5_36.py. Runtime imports
only generic transport helpers and existing capability type checks; no application
ASTs. It checks metadata/digests/path/provider shape, creates evidence infrastructure,
passes argv unchanged and invokes the unchanged transport. It neither manipulates
application collections nor computes defaults, predicates, migration, domain
validation or result values. Assembly reads existing CheckedPlan capability facts
and calls the existing generator, without a second lowerer/analyzer. Study/test
files alone hold acoustic/specimen source, controlled values and fault algorithms.
No task/B02 path or behavior is present in launcher implementation.

## 24. Generic entry point

One entry: copied launch_runtime_r5_36.py, installed beside launch.json and existing
generated/checked files. One assembly API: checked_launch_r5_36.generate. Both
applications use this entry unchanged; adding a supported semantic application
requires checked profiles/declarations, not launcher Python. Repository research
module imports are provisioning/evaluation tooling, not standalone runtime imports.

## 25. Future deployment boundary

Native executables, installers, OS launch wrappers, HTTP hosting, containers and
production observability are outside R5.36. Absolute-path selection, optional trace,
multi-process transactional/crash-safe persistence and hostile-runtime attestation
are not established. They are non-critical product/deployment limitations for the
frozen local cwd/subprocess contract; no further preparatory phase is justified by
them. Existing Python/temp/writable-local-directory prerequisites remain ordinary
bounded runtime prerequisites. No arbitrary deployment infrastructure implemented.

## 26. Frozen B02 descriptive comparison — after lock

The independent implementation/full tests completed first. Running launch_study_r5_36
produced evidence plus a SHA-256 lock of all benchmark/semantic Python files and the
new focused test before reading frozen B02.md and baseline.md for this comparison.
No launcher/test/semantic implementation edits followed. No B02 launch scripts or
implementation templates were read. The harness protocol only describes absolute
executable paths with independent working directories, consistent with this profile.

| Known frozen launch requirement | Classification | Evidence/boundary |
| --- | --- | --- |
| real CLI subprocess, caller supplies intended public command only | GENERICALLY_SUPPORTED | A/B actual Popen calls and architectural Fault D |
| absolute executable path, isolated temporary cwd | GENERICALLY_SUPPORTED | same bundle from two cwd directories per application |
| exact operation/flag names including repeated --tag | PROFILE_CONFIGURATION_ONLY | existing R5.35 checked public aliases; launcher consumes no tokens |
| implicit cwd durable tasks.json basename | PROFILE_CONFIGURATION_ONLY | checked relative store path; normal/nested/relocation/cwd evidence, no task path in launcher |
| shared state across separate invocations | GENERICALLY_SUPPORTED | B continuous durable lifecycle |
| missing list returns declared [] without creating store | PROFILE_CONFIGURATION_ONLY | R5.35 explicit empty-origin witness plus R5.36 missing-read policy; launch does not initialize |
| first generated write creates declared durable state | GENERICALLY_SUPPORTED | B missing-store insertion |
| migration and version availability through same launch | GENERICALLY_SUPPORTED | B pre/migrate/post lifecycle; application transition remains generated |
| one JSON stdout success/exit 0 | PROFILE_CONFIGURATION_ONLY | unchanged R5.35 direct/presentation/status metadata and actual public capture |
| {error:CODE} stderr failure/exit 1 | PROFILE_CONFIGURATION_ONLY | checked R5.35 presentation/code/stream/exit; no semantic failure invented by launcher |
| production unique ID/UTC time bootstrap | GENERICALLY_SUPPORTED | A stamp actual provider trace; controlled selection separate and checked |
| no research store/trace/provenance/profile arguments | GENERICALLY_SUPPORTED | all normal command arrays contain only interpreter/entry/public argv |
| internal trace/invocation/provenance for research grounding | GENERICALLY_SUPPORTED | checked required local channel, new file/PID/identity linkage |
| no required application environment setup | GENERICALLY_SUPPORTED | co-located bundle and poisoned ambient override witness |
| tags normalization/defaults and exact task transitions/results | BENCHMARK_SPECIFIC | generated application semantics, not launch configuration/algorithm |
| complete cumulative frozen candidate/acceptance equivalence | UNKNOWN | deliberately unexecuted; R5.37 must determine actual integration result |

No known launch requirement is STILL_UNSUPPORTED. UNKNOWN complete acceptance is
an unperformed comprehensive experiment, not a demonstrated preparatory capability
blocker. Frozen text demands no native packaging, installers, HTTP or production
observability. No repair follows this comparison.

## 27. Complete readiness matrix, R5.23–R5.36

| Readiness class | Classification | Independent current evidence |
| --- | --- | --- |
| semantic expressiveness | RESOLVED_INDEPENDENTLY | R5.23 representation review; later existing-type integration, core 30 |
| general lowering | RESOLVED_INDEPENDENTLY | R5.22 known relation coverage and R5.31 current checked pipeline |
| relation composition | RESOLVED_INDEPENDENTLY | R5.18 N-way defaults, R5.30 inventory, R5.33 evolution |
| ordering | RESOLVED_INDEPENDENTLY | R5.20 typed ordering; R5.31 instant ordering |
| optional refinement | RESOLVED_INDEPENDENTLY | R5.31 scoped presence facts/current execution |
| single semantic authority | RESOLVED_INDEPENDENTLY | R5.31 checked-plan authority and poisoning tests |
| input suppliedness | RESOLVED_INDEPENDENTLY | R5.32 and R5.35 omission/empty/value distinctions |
| malformed-input boundary | RESOLVED_INDEPENDENTLY | R5.32 noninvocation + R5.35 public mapping; R5.36 A |
| cross-shape state evolution | RESOLVED_INDEPENDENTLY | R5.33 plus R5.36 B actual standalone lifecycle |
| checked transport | RESOLVED_INDEPENDENTLY | R5.34/R5.35 and checked standalone wrapper |
| repeated collection arguments | RESOLVED_INDEPENDENTLY | R5.35 per-element/order/duplicate evidence and R5.36 A |
| output envelope/stream mapping | RESOLVED_INDEPENDENTLY | R5.35 independent output/semantic faults; actual process relay |
| missing-store policy | RESOLVED_INDEPENDENTLY | R5.35 declared/lazy policy; R5.36 missing lifecycle |
| standalone public launch | RESOLVED_INDEPENDENTLY | R5.36 same entry on A/B; Fault D |
| cwd-relative persistence | RESOLVED_INDEPENDENTLY | changed cwd/nested paths/relocation and Fault B |
| trace bootstrap | RESOLVED_INDEPENDENTLY | local checked channel/PID/profile correlation and Fault C |

Exact benchmark naming, store basename, public documents/status, state origin and
checked provider choices are PROFILE_CONFIGURATION_ONLY. Scope is the required
bounded compositions, not all possible programs. No historical partial gate is
rewritten. Operation-declared malformed-untyped outcomes remain unimplemented but
are unnecessary for frozen public noninvocation failures: a non-critical semantic
prototype limitation, not an unresolved public readiness requirement.

## 28. Final readiness decision

The R5.35 concrete public launch blocker is closed independently. No known
benchmark-critical class remains PARTIALLY_RESOLVED or UNRESOLVED. Remaining
deployment/runtime-guarantee limitations are non-critical for this frozen contract;
complete integrated acceptance is the next experiment, not another prerequisite.
Readiness is judged from supported architecture and frozen obligations, not test
count. Select R5_36_READY_FOR_COMPREHENSIVE_B02_RETRY.

## 29. Readiness-methodology assessment

**Are we continuing to discover genuinely necessary benchmark capabilities, or
moving readiness goalposts toward product-like infrastructure?** R5.23 found real
shared-domain integration gaps; R5.35 identified a real public-only invocation/cwd
bootstrap gap. R5.36 resolves that specific contract boundary. Requiring native
packaging, installation, optional observability channels or production hosting now
would move the goalposts: none is demanded by frozen B02/baseline. The serial
preparatory discovery loop should stop. R5.37 must attempt the complete frozen
contract under a fresh lock, honestly recording any genuine integration failure;
this recommendation does not invent or authorize a benchmark pass.

## 30. Construct/system accounting and verification

| System area | Accounting |
| --- | --- |
| candidate core / historical raw vocabulary | 30 / 46 unchanged; no #31 |
| semantic/compiler/type/binding/transport/persistence authority | unchanged existing files; current_pipeline remains entry |
| launch configuration/runtime | two prospective generic modules; checked profile, signature and generation-bound seal |
| evidence | standalone observer/challenger, local correlated bundle; existing layer verifiers reused |
| study/tests/restriction runner | independent study, 14 focused tests, fail-closed full harness runner |
| readiness | separately versioned matrix; historical R5.24/R5.35 matrix/evidence preserved |

Machine evidence contains **33 actual public subprocess observations**: A 6, B 9,
path/environment 6, disposable faults 6, metadata-only mutations 6. Of 21 normal
path/lifecycle observations, 19 grounded invocations pass every applicable layer;
two defined directory-prerequisite failures reject before execution. Sixteen normal
observations have typed semantic events. Four compatible metadata mutations pass;
two incompatible metadata references correctly reject. All six disposable launch
faults are detected. Focused-only observations additionally exercise public flags
resembling bootstrap configuration and stale artifact/trace identity challenges.
Counts do not choose the decision gate.

Environment: Windows PowerShell, **Python 3.14.3**, standard library only. No
Python/environment failures; no LF mirror or historical hash correction. Git
emitted LF-to-CRLF conversion notices for changed/new files during whitespace
checking; these are separate from actual failures. No whitespace error occurred.

| Required verification | Actual result |
| --- | --- |
| full benchmark harness: python -m benchmark.semantic.verify_launch_r5_36 | 347 discovered; 346 pass, 1 explicit restriction skip; 0 failures/errors; 104.424 s |
| architecture/grounding/semantic/binding/evolution/transport suites | included and passing in full discovery |
| relevant R5.10–R5.35 focused suites | included and passing in full discovery; historical diagnostics retained |
| all new R5.36 launch tests | 14/14 passing in full discovery with final code; initial focused run also 14/14, 8.313 s |
| application/compiler suite, PYTHONPATH=src | 31/31 pass, 2.730 s |
| model validation | OK |
| safety | 0 capability violations, 0 invalid transitions |
| capability/readiness matrix | existing matrix tests and new complete 16-class readiness test pass |
| independent evidence and implementation lock | 33 observations; hashes recorded before descriptive frozen comparison |
| post-comparison recorded-evidence verification | 33 observations/counts, all fault refusals, mutation artifact equality and implementation lock verified intact |
| git diff --check | passes for tracked files; all new files also pass git diff --no-index --check against NUL; LF-to-CRLF notices only |

Restriction runner excludes exactly
`test_phase5e.CapabilityProfileTests.test_read_only_validation_of_both_continuation_states`
and fails on exclusion drift. This prevents its nested frozen B02 acceptance.
Plain unguarded full discovery was not run. Existing historical B02-shaped slice
regressions in full discovery are preserved diagnostics, not a complete new B02
generation/retry/grounding/conformance attempt. Frozen acceptance was not run.
New-file no-index checks permit ordinary difference exit 1 against NUL; no
whitespace diagnostics occurred. Verification summary:
[R5_36-verification.json](R5_36-verification.json).

B02 is **not retried**; Phase 5C remains paused; B03 untouched; B17 unexposed and
unclassified; semantic-first format globally unfrozen; R5.2.2 remains historical
benchmark authority. Universal implementation correctness is not claimed.

## 31. Exact recommendation for R5.37

**R5.37 = comprehensive frozen B02 retry.** Freeze the resulting current generic
pipeline/transport/launch architecture for the attempt, configure the frozen public
surface through checked metadata, attempt complete semantic generation and run
the full frozen contract only within that separately authorized experiment. Do
not create another preparatory phase for non-critical deployment polish. Record
representation, generation, public acceptance, grounding and conformance separately;
do not repair the locked architecture inside that attempt. No B03/Phase 5C/B17
advance follows from readiness alone.

R5_36_READY_FOR_COMPREHENSIVE_B02_RETRY
