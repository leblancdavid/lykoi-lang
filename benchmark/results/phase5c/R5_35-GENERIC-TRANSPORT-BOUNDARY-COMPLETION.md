# R5.35 — Generic Transport Boundary Completion Review

Prospective independent review, 2026-10-03; preceding gate
`R5_34_CHECKED_TRANSPORT_VALIDATED`. **Decision: partial frozen readiness.**
All three requested extensions are generically implemented and independently
challenged. A post-lock descriptive audit identifies one remaining generic launch
boundary: standalone public-only argv and checked cwd-relative persistence/trace
bootstrap. R5.34 had treated cwd store selection as profile configuration; this
review corrects that classification prospectively because no such launch profile
exists. No algorithm repair follows that comparison. Recommend a bounded R5.36
launch-profile completion review, **not** comprehensive B02 retry yet.

Evidence: [R5_35-transport-evidence.json](R5_35-transport-evidence.json).
Versioned interface: [transport-boundary-r5.35.md](../../../docs/transport-boundary-r5.35.md).
Candidate core semantics remain **30**, no #31; no transport architecture redesign.

## 1. Repeated-argument reconstruction

R5.34 accepts one text/JSON value per scalar flag and rejects duplicate flags.
R5.32 metadata admits string/integer/instant/boolean, not collection slots.
A JSON array supplied once is wire collection encoding; repeated scalar flags
are another representation of a semantic collection, not semantic repetition.
R5.35 adds both representations of existing `sequence<T>` inputs. The current
checked type vocabulary uses sequence, not a distinct new collection type.

## 2. Checked collection binding

Profiles bind public name to exact plan input slot and scalar element decoder,
finite element domain, mode (`repeat`, `collection`, `single`), text/JSON wire
representation, plan-derived omission (`omit`/`required`) and encounter order.
Required mappings are complete; duplicate slots/names, incompatible decoders,
wrong omission, unsupported order/mode and incompatible JSON representation reject.
All four existing scalar base types can be sequence elements. No new semantic type.

## 3. Repetition/suppliedness semantics

Encounter order, duplicates and case distinctions survive raw accumulation and
per-element R5.32 binding. No sorting, trimming or deduplication in transport.
Omitted optional collection stays absent; JSON `[]` is explicitly supplied empty;
nonempty repeated inputs are supplied. Repeat grammar alone cannot express an
explicit empty collection: A exposes a second collection-JSON route to the same
semantic operation. Required omission fails, while explicitly supplied empty
can bind. Generated semantic fallback owns any omitted collection default.

## 4. Repeated-argument results/faults

Acoustic calibration exercises omission/zero, one, multiple, duplicates,
case-distinct values, explicitly empty/encoded collections and a malformed integer
between valid integers. `3,bad,1` fails at index 1 with no typed invocation; a
focused binder challenge also visits all four values in `3,bad,bad,+1`, retaining
both failure indices. Supplied `[' right ','left']` becomes the same typed list,
then generated normalization returns `['right','left']`. Duplicates reach binding
as `['left','left','Left']`; semantics alone reduces them to `['left','Left']`.

| Disposable fault | Independently exposed |
| --- | --- |
| A reverse repeated raw values | transport binding and input binding fail; semantic grounding against requested input also fails |
| B silently remove duplicate | transport/input fail even though normalization hides duplicate in public result |
| C drop malformed element | transport/input fail; forbidden invocation and wrong public failure mapping also fail |

Faults mutate copied adapters, resealed with real artifact bytes. Expected source
and profile remain authoritative.

## 5. Public-envelope boundary

R5.34 fixes one stdout JSON object `{status,outcome}` and fixed process exits.
Semantic outcome remains `{kind,value}` with checked branch-dependent payload.
R5.35 public presentation operates on that checked payload, without changing
branch selection, meaning or generated state transition. Internal typed results
are retained separately from external public bytes.

## 6. Checked envelope profile

Bounded presentations are direct payload or a structured object field list.
Field sources: typed constants, string outcome kind, and typed required-record
payload paths. Full coverage promises whole payload or all required top-level
record fields; selected coverage explicitly permits projection. Example A exposes
`{ok:true,data:record}` and `{ok:false,error:record}`; focused calls also emit
direct values, projected record fields and `{error:binding_code}`. No executable
templates, arbitrary formatting callbacks or application serializer.

## 7. Envelope validation/conformance

Exact tags/types must match sealed plan outcomes. Nonexistent result paths,
wrong projected type, missing promised payload, duplicate destination fields,
foreign variants, incompatible outcome or boundary payload types, invalid stream
and invalid/Boolean exit reject. Boundary-category identifiers are reserved
against semantic tag collision. Object field names are otherwise configurable.
Fault D exposes a correct semantic success as a failure envelope; E omits the
whole `data` field. Both retain semantic conformance and fail output conformance.
No public classification is used as evidence that semantics ran.

## 8. Stream requirement analysis

The R5.34 recorded readiness boundary distinguishes one JSON stdout result from
one stderr error/diagnostic document. Collections can be arrays in that document.
Nothing independently justifies multiple records, NDJSON, asynchronous/network
streaming or a general streaming runtime. Implement only configurable process
destination for one checked JSON document, with a trailing newline.

## 9. stdout/stderr/status policy

Each exact semantic tag and each boundary category declares public classification,
stdout/stderr destination and exit 0–125. Profiles may route even success to
stderr or choose a different exit; semantic success/failure remains unchanged.
Binding diagnostics are retained internally; public codes come from complete
category and optional argument-specific code metadata. Persistence categories
and generated invocation rejection are independently configurable. Integrity
rejection before a profile can be trusted retains stderr/exit 4.

## 10. Stream results/faults

Metadata-only mutations route a correct success document to stderr, and change
its exit to 5, with unchanged adapter digest. Disposable wrong-destination and
wrong-exit faults independently fail output while semantics passes. Envelope
omission/corruption faults cover document content. Missing/extra NDJSON records
are inapplicable: multi-record streaming was not required or implemented.

## 11. Missing-store reconstruction

R5.34 reads the physical store before routing and has no missing-store policy.
Missing file is neither an empty semantic collection nor an operation outcome.
Classifications reviewed:

| Interpretation | Layer/decision |
| --- | --- |
| EMPTY_INITIAL_STATE | only valid if explicitly declared state happens to be empty |
| PERSISTENCE_NOT_INITIALIZED / FAIL_IF_MISSING | persistence boundary, implemented as REQUIRE_EXISTING |
| PUBLIC_BINDING_FAILURE | inaccurate: argument binding can succeed without a store |
| SEMANTIC_OPERATION_FAILURE | inaccurate if no typed pre-state/execution exists |
| AUTO_INITIALIZE_FROM_DECLARED_INITIAL_STATE | explicit checked persistence policy, implemented lazily |
| INVALID_APPLICATION_CONFIGURATION | invalid policy/reference/state declaration rejects before generation |

No empty file is created merely to satisfy an implementation convenience.

## 12. Layer ownership

Binding owns conversion/suppliedness. Persistence supplies checked pre-state and
mediates durable realization. Application/state metadata owns initial values.
Generated operations own applicability, normalization, defaults, writes and
migration. Transport maps actual boundary/semantic categories to public process
behavior. No persistence failure manufactures semantic execution.

## 13. Persistence-policy metadata

`REQUIRE_EXISTING` permits no initial reference; missing file produces a public
persistence-missing category before invocation. `INITIALIZE_DECLARED_STATE`
requires a named checked initial reference. Realization is bounded/lazy: staged
initial state becomes a physical store only on successful generated attempted
write. No eager initialization policy or executable hook was added. Existing
files are never reinitialized. Invalid JSON and invalid registered state shape
are distinct persistence errors; version/applicability rejection stays generated.

## 14. Declared initial state

The state profile copies exact application registered versions and supplies named
`{version,value}` declarations. Validation checks version existence, exact state
profile compatibility and value type. The specimen origin explicitly declares
V1/revision 1 and three existing records; it is not inferred from field names.
Alternative empty V1 and current V2 declarations are explicit metadata for
mutation/fault witnesses. Transport does not invent `[]`, `{}` or revision 1.
The focused root-promotion witness explicitly declares empty V1 `[]`.

## 15. Cross-shape interaction

B runs missing-store legacy read -> legacy insertion -> legacy read -> migrate
-> current read -> current insertion -> current read -> incompatible legacy read.
First read receives declared V1 but leaves the file absent. Insertion materializes
V1. Generated migration creates V2; current operations then operate on V2.
All seven adjacent physical byte links agree, including absent -> absent linkage.
An independent focused empty-root case reads missing V1 without creation, then
migrates with count 0 into generated V2. Nothing initializes a convenient version
based on the selected operation.

## 16. Missing-store failure behavior

REQUIRE_EXISTING on absent storage preserves absence, reports persistence failure,
does not invoke semantics and has no semantic verdict. Invalid JSON and invalid
state-shape calls preserve exact corrupt bytes and also do not invoke. Generated
unavailable legacy-on-V2 rejection preserves bytes but is an invocation-boundary
result, not persistence initialization or a fabricated typed semantic outcome.

## 17. Persistence fault results

| Fault | Injection | Result |
| --- | --- | --- |
| F | REQUIRE_EXISTING silently creates `[]` | persistence fails on actual absent -> present bytes; public missing error alone would have looked correct |
| G | initialize declared V2 instead of referenced V1 | independent effective-pre/persistence expectation fails; generated V1 operation rejects and no semantic success is claimed |
| H | correct V1 initialization/insertion, wrong public report | persistence and semantics pass; output fails |

G is well-typed for another registered state version, so a type-only check would
not detect it. The checked initial reference and independently reconstructed
effective state are necessary. F/G outputs can conform while persistence fails.

## 18. Layered verdict model

Evidence keeps TRANSPORT_PROFILE_CONFORMANT, TRANSPORT_BINDING_CONFORMANT,
INPUT_BINDING_CONFORMANT, PERSISTENCE_BOUNDARY_CONFORMANT,
SEMANTIC_EXECUTION_CONFORMANT and OUTPUT_CONFORMANT separately, with independent
transport grounding. Physical pre/post absence/digests are separate from effective
semantic pre-state. Semantics is null for noninvocation/rejection, not passed.
Correct output does not imply correct persistence; correct semantics does not
imply correct public envelope. No single aggregate correctness Boolean.

## 19. Independent application A

New acoustic calibration operation, not a task domain: optional ordered channel
strings and integer samples, generated trimming/stable uniqueness/nonblank guard,
sample count, record outcome, semantic rejection and configurable envelopes.
Repeat and collection routes map to the same operation. Twelve public calls;
seven typed semantic executions, five binding/routing/grammar failures.
All applicable normal layers pass. Semantic source is recorded in machine evidence.

## 20. Independent application B

Independent R5.33 specimen versioned envelope application, using unchanged
current_pipeline and generated state/operation codecs. Eight lifecycle calls
(seven typed executions, one unavailable rejection), plus missing-store,
malformed-JSON and invalid-shape failures. Eleven public calls; all applicable
layers pass. No transport algorithm inspects specimen fields or revision values.
The focused root-promotion case independently validates an explicitly empty origin.

## 21. Metadata-only mutations

Six changes preserve identical production adapter bytes: repeated argument name
channels -> channel; payload destination data -> reading; success stdout -> stderr;
success exit 0 -> 5; initialize -> require-existing; initial origin -> empty_v1.
All applicable layers pass and observed public/effective-state behavior changes
accordingly. Neither adapter nor generated semantic algorithm changes for these
witnesses. Initial-reference mutation leaves read storage absent.

## 22. Profile integrity

Application/source/unit/generation identities bind profiles to sealed plan and
state facts. R5.34 dependency seals are reused; an additional R5.35 runtime seal
protects extension bytes. Semantic regeneration retaining old profile rejects
before binding/state access, even with absent store. Incompatible state profiles,
invalid initial versions/types and invalid references reject statically. A
resealed reference swap to current V2 is rejected by independent expected-profile
authority. Checksums establish revision integrity, not hostile-writer authentication.

## 23. Source-authority audit

Production `checked_transport_r5_35.py` validates metadata, generates through the
current entry and independently challenges observations. Production
`transport_runtime_r5_35.py` accumulates raw values, invokes R5.32 per element,
mediates declared-state staging, invokes existing operation.py and encodes checked
documents. No channel/specimen/task fields, normalization, sorting, filtering,
default computation, migration or state-transition algorithm occurs there.
Domain source, declared state values and faults live in study/test machinery.
Compiler, generated semantic algorithm, old binder and old runtime are unchanged.
The physical materialization copy is persistence machinery, not a state transition.

## 24. Frozen B02 descriptive readiness comparison

Independent implementation and tests were locked **before** reading frozen
`requirements/B02.md` and `baseline.md` descriptively. Evidence records SHA-256
identities for 14 implementation/test/current-authority files. No B02 fixture
template, candidate, retry or acceptance run; no implementation edits follow this
comparison. Historical harness diagnostics remain regressions, not a new retry.

| Frozen transport requirement | Classification | Grounding/limit |
| --- | --- | --- |
| generic public operation and named scalar pairs | GENERICALLY_SUPPORTED | R5.34 routing and R5.35 CLI calls |
| exact command/flag names | PROFILE_CONFIGURATION_ONLY | checked aliases |
| zero-or-more repeated --tag values | GENERICALLY_SUPPORTED | optional sequence omission and repeated per-element binding |
| case-sensitive encounter order/duplicates before semantics | GENERICALLY_SUPPORTED | A witnesses and A/B faults |
| trim/nonblank/stable dedup; tags defaults/migration | BENCHMARK_SPECIFIC | application relations, never transport logic |
| supplied/omitted optional due date and priority | GENERICALLY_SUPPORTED | unchanged R5.32 scalar membership/decoder evidence |
| exact direct JSON result on stdout, exit 0 | PROFILE_CONFIGURATION_ONLY | checked direct presentation/stream/exit |
| expected errors `{error:CODE}` on stderr, exit 1 | PROFILE_CONFIGURATION_ONLY | typed failure or boundary-code projection and checked process policy |
| invalid_tag/invalid_due_date public codes | PROFILE_CONFIGURATION_ONLY | semantic-failure payload/constant and argument-code policy; no semantic execution for malformed decode |
| shared file across subprocesses | GENERICALLY_SUPPORTED | B durable lifecycle |
| missing store read -> declared empty state, no file | PERSISTENCE_POLICY_SUPPORTED | explicit origin and lazy realization; focused empty-root read |
| missing-store migration -> typed count 0 | PERSISTENCE_POLICY_SUPPORTED | focused empty-root generated migration; exact record result is source semantics |
| JSON corruption/invalid shape -> public invalid_state | PROFILE_CONFIGURATION_ONLY | persistence category checked envelope/code projection |
| state-domain invalidity, duplicate IDs, enums, timestamps | BENCHMARK_SPECIFIC | generated contracts/type/applicability, not transport filtering |
| version availability/migration routing | GENERICALLY_SUPPORTED | unchanged generated R5.33 predicates/codecs |
| IDs/clock/filter/order/transitions/exact task result fields | BENCHMARK_SPECIFIC | existing semantic/capability authority |
| public-only argv executable, implicit cwd tasks.json, trace bootstrap | STILL_UNSUPPORTED | adapter currently requires infrastructure argv; no checked launch metadata exists |
| complete inherited frozen integration/acceptance | UNKNOWN | intentionally unexecuted; no universal transfer inference |

The launch row is a **prospective correction** to R5.34's configuration-only
classification, not a rewrite of its evidence. A caller passing paths manually
does not demonstrate profile-only standalone launch. Resolving this requires a
generic launch extension, not benchmark-specific task behavior; it was not added
after comparison or folded into these three implementation areas.

## 25. Full R5.23 readiness matrix

| Major blocker | Classification | Scope/evidence |
| --- | --- | --- |
| optional refinement | RESOLVED_INDEPENDENTLY | R5.31 single-authority current pipeline |
| instant ordering | RESOLVED_INDEPENDENTLY | checked chronological ordering |
| suppliedness/well-formedness | RESOLVED_INDEPENDENTLY | R5.32 plus collection binding |
| malformed-input boundary | RESOLVED_INDEPENDENTLY | structured noninvocation plus checked public code/envelope/stream mapping |
| cross-shape evolution | RESOLVED_INDEPENDENTLY | R5.33 and B missing-origin lifecycle |
| transport binding | PARTIALLY_RESOLVED | checked routing works; standalone checked launch bootstrap absent |
| repeated collection binding | RESOLVED_INDEPENDENTLY | A, JSON route, required-empty focused witness, Faults A-C |
| public envelope/stream mapping | RESOLVED_INDEPENDENTLY | document presentation/process policy, faults D/E/H/stream/exit |
| missing-store policy | RESOLVED_INDEPENDENTLY | explicit state declaration/lazy policy, F/G/H and cross-shape calls |

Malformed-input resolution here means the frozen-readiness **public boundary**,
not adding a declared semantic branch for malformed untyped values. R5.32's
separate operation-declared malformed-outcome integration remains outside this
profile; no such event is needed to classify a nonexecuted binding error publicly.
No historical partial gate is retroactively changed.

## 26. B02 retry gate

**Do not recommend comprehensive B02 retry yet.** One known generic requirement
still needs runtime launch machinery rather than merely configuring an existing
checked profile. The three R5.35 extensions are validated independently, but
their test success cannot authorize a launch capability that does not exist.
B02 is not retried or accepted in this review.

## 27. #31 decision

No new application-semantic concept emerged. Collection representation, public
documents/process status and physical persistence initialization are checked
interface/state configuration and mediation. No #31 or automatic semantic addition.
Any future genuinely semantic initial-state rule would require separate review;
this implementation only consumes explicit typed declarations.

## 28. Capability matrix

`R5_24-type-matrix.json` preserves historical profiles and adds
`r5_35_transport_boundary`, with nine supported bounded dimensions, evidence and
limits, the nine-class readiness table, and the explicit remaining launch boundary.
Supported dimensions do not imply complete frozen integration. Focused/full
validation checks dimension coverage, evidence/limits, entry identity and core 30.

## 29. Construct/system accounting and verification

| Area | Accounting |
| --- | --- |
| candidate core / historical raw entries | 30 / 46 unchanged; no #31 |
| transport-profile machinery | extended checked sequence/presentation/process metadata; new prospective module |
| persistence-policy machinery | checked version/initial reference and lazy materialization; no semantic initial-state inference |
| binding | collection orchestration of unchanged R5.32 scalar binder; independent oracle |
| compiler | current_pipeline unchanged; no alternate pipeline or semantic analyzer |
| runtime | one prospective R5.35 adapter extends R5.34; old runtime/binder unchanged |
| verifier | distinct public/input/persistence/semantic/output challenge; current semantic verifier unchanged |
| evidence/tests | study, restriction runner, 14 focused tests, machine evidence and implementation lock |

Machine evidence contains **39 public observations**: A 12, B 11, faults 10,
metadata-only mutations 6. All 23 normal and 6 mutation calls pass applicable
layers; 14 normal calls have typed semantic execution. All ten faults are exposed
at their specified layers. Focused-only cases additionally cover direct/projected
output, required empty input, every-element binding, stale/resealed authority and
empty-root migration. Endpoint evidence does not prove no transient writes,
concurrent isolation, crash atomicity or universal correctness.

Environment: Windows PowerShell, **Python 3.14.3**, no third-party dependencies.
No Python-version/environment failures occurred. No LF mirror was used; historical
hash checks passed. Git LF-to-CRLF notices are reported separately from failures.

| Verification | Actual result |
| --- | --- |
| `python -m benchmark.semantic.verify_transport_r5_35` | 333 discovered, 332 pass, 1 explicit restriction skip; 0 failures/errors, 88.997 s |
| architecture/grounding/semantic/binding/evolution/transport and relevant R5.10–R5.34 focused suites | included and passed in full discovery |
| R5.35 focused discovery | 14/14 pass, 6.427 s before lock; all 14 also pass after lock in full discovery |
| application/compiler suite, PYTHONPATH=src | 31/31 pass, 2.575 s |
| model validation | OK |
| safety | 0 capability violations, 0 invalid transitions |
| capability-matrix validation | passes in full discovery; post-comparison focused matrix recheck 1/1 pass, 5.155 s |
| independent study | 39 observations with separate layered verdicts and implementation hashes |
| `git diff --check` | passes; tracked and new-file no-index checks show no whitespace errors; LF-to-CRLF notices only |

The restriction runner excludes exactly
`test_phase5e.CapabilityProfileTests.test_read_only_validation_of_both_continuation_states`,
which otherwise launches nested frozen B02 acceptance. Exclusion must match once
or the runner fails. Plain unguarded discovery was not run. Existing historical
B02 diagnostic regressions do not construct a new current B02 candidate.
New-file `git diff --no-index --check` returns 1 for differing files against NUL;
that ordinary difference status is separate from whitespace/test failures.

B02 **not retried**, frozen B02 acceptance **not run**, Phase 5C remains paused,
B03 untouched, B17 unexposed/unclassified, semantic-first format globally unfrozen,
R5.2.2 historical benchmark authority. Universal implementation correctness is
not claimed. Durability remains nontransactional and integrity is not sandboxing.

## 30. Exact recommendation for R5.36

Begin **Checked Public Launch Profile Completion Review**, independently on
non-task applications, with public-only argv, explicitly checked cwd-relative
store selection and generic trace/invocation bootstrap. Preserve the validated
R5.34/R5.35 routing/binding/generated-execution/persistence/output architecture.
Use independent subprocess cwd/file observations, stale-profile checks, metadata
mutations and faults; no task command/default/state logic in launch machinery.
Lock implementation before another descriptive frozen-text comparison. Reassess
the launch and full readiness matrix before recommending a comprehensive B02
retry. Do not repair against acceptance fixtures or run frozen B02 as part of that
completion review. No #31, Phase 5C activation, B03 advance or B17 exposure.

The partial gate follows an explicitly unsupported generic public boundary,
not test count, semantic extension need or architectural redesign.

R5_35_GENERIC_TRANSPORT_BOUNDARY_PARTIAL
