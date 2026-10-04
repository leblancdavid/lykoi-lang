# R5.40 — Boundary Profile Admission and Frozen B02 Configuration

**Result: generic boundary capability gaps remain.** One locked static pass
returns **NOT_READY**, with **15/15 CheckedPlans**. Reconstructed metadata passes
the bounded **CONFIGURATION_ONLY** audit and closed structural schema, but the
transport/aggregate compatibility gate rejects it. Complete checked B02 profiles
were therefore **not** established. No B02 generation, execution or frozen
acceptance occurred. No post-pass implementation/profile repair occurred.

The central question has a mixed, experimentally bounded answer: most missing
profile declarations can be supplied as legitimate application configuration;
the faithful supplied-text/nullable-input and optional-content-domain
compositions still require generic boundary support. They are not resolved by
adding public names and profile references alone. There is also an evidenced
readiness support-check defect. No new core construct is indicated.

## 1. R5.39 admission defect

[R5_40-admission-reconstruction.json](R5_40-admission-reconstruction.json)
records a one-operation, one-public-route, one-state-alternative seed-bank
query with one optional nullable integer invocation input. Removing its sole
argument mapping still forms the historical aggregate. Readiness v2 rejects
the identical incomplete application with incomplete input-binding coverage.

The causal difference is exact: R5.35 checks `required <= mapped`, whereas
readiness v2 checks `mapped == all invocation input slots`. Optional slots
disappear from the former obligation. The reconstruction uses the existing
historical implementation directly; its bytes remain unchanged. It contains no
task behavior or target generation.

## 2. Profile completeness invariant

The versioned [admission policy](../../../docs/boundary-profile-admission-r5.40.md)
and `application_boundary_r5_40.py` establish exactly one mapping for every
declared public invocation input, including optional inputs, before delegating
the existing aggregate compatibility checks. The delegated checks cover
CheckedPlan identity; decoder/type/domain/representation; collection mode and
encounter order; omission; public argument identity; pre/post state codecs and
alternatives; initial/missing-store persistence; all outcome mappings and
stream/status/exit policy; plan-to-route coverage; launch/store/provider/trace
and artifact/provenance identity relationships.

Internal semantic slots (`pre`, `post`, scoped items, outcome and external
capability facts) are not invocation inputs and need no argv mapping. Complete
declared-profile structure is distinct from proving every frozen requirement or
runtime composition. R5.40 does not widen that claim.

## 3. Optional-input coverage

A mapped optional argument must explicitly declare `omission: omit`, its decoder
and its input slot. Optionality does not waive public coverage. This version has
no explicit internal invocation-input exemption or transport-wide always-omit
policy; introducing either implicitly would weaken the profile model. An
attempted `internal` field rejects. Capability-provider inputs remain separate
from public invocation arguments under the inherited model.

## 4. Admission/readiness consistency

R5.40's prospective aggregate entry and byte-unchanged readiness v2 now agree on
missing required/optional input mappings. Existing compatibility validation
still rejects wrong slot identity, duplicate mapping, incompatible decoder,
omission mismatch and stale linked profiles. Readiness remains stricter about
whole-contract obligations.

The R5.40 admission policy wraps the unchanged R5.39 serialized aggregate; it
does not rewrite historical R5.39 admission, old generation entries or runtime
loaders. The prospective static gate explicitly invokes R5.40 admission through
the profile audit. Historical admission remains reproducible and its defect
remains documented; no claim is made that old entry points were retrofitted.

## 5. Independent admission tests

`benchmark/harness/test_profile_admission_r5_40.py`: **14/14 pass**. Evidence
includes complete required and optional inputs; omitted required and optional
mappings; seed-bank and publication profiles; wrong slots; duplicate public
mapping; incompatible decoder; wrong omission; stale binding/transport identity;
unsupported internal-input declarations; equal codecs with distinct state
discriminators; closed-schema behavior-field and fixture-output rejection;
source-trace omission/duplication/staleness/non-authority rejection; and the two
independently observed boundary limitations below. Multiple subcases do not
inflate the test-method denominator. No B02 operation executes in these tests.

The independent optional-domain witness declares an optional `habitat` field
with a finite domain on a seed row. Schema validation accepts the declaration;
an absent field is structurally valid; the inherited codec returns
`persistence_invalid_state`. The population implementation accesses
`row[field]` without an optional-presence policy. The witness is saved in
[R5_40-independent-capability-witnesses.json](R5_40-independent-capability-witnesses.json).
This is a preserved implementation/support finding, not an intentionally
failing regression or a B02 runtime experiment.

## 6. Configuration definition

Configuration may describe public operation and argument names, semantic
operation and CheckedPlan slot references, decoder/profile references, finite
input domains, repetition/collection mode, omission, output envelope and
stream/status/exit mappings, state alternatives and codec/discriminator/content
references, persistence and initial/missing-store policy, cwd-relative paths,
launch/provider/trace/provenance relationships. Distinct V2/V3 state identities
using equal legacy codec shapes are such metadata.

## 7. Prohibited behavior definition

Profiles may not implement application predicates, transforms, filtering,
ordering, tag normalization, migration algorithms, expected counts/results,
fixture lookup tables, arbitrary code or frozen-request branches. Such behavior
belongs in the already-authored semantic contracts. Output constants in this
bounded audit are interface labels only, not arbitrary result constants;
production providers contain no fixture values.

## 8. Configuration audit

`profile_audit_r5_40.py` checks closed declarative fields and typed shape
declarations, separately invokes existing compatibility validators, scans for
behavioral/executable/fixture data, and requires one exact source record for
every leaf, including empty containers. Each source record supplies path,
value, authority artifact/hash, clause and interpretation. Unapproved,
unexplained, duplicated or stale records reject.

It additionally checks two independently witnessed current capability limits
from declared types: raw-text nullable element decoding, and population domains
on optional fields. This is static support analysis; it does not implement the
missing behavior. Its code contains no B02 identity, command, field-name or
expected-output branch. The original readiness v2 result is retained separately.

The audit is bounded research-integrity tooling, not malicious-code security or
automated proof that a prose interpretation follows from its source. Source
interpretations were reviewed as well as hashed. Structural schema admission,
configuration-only classification, checked compatibility and runtime correctness
are reported separately.

## 9. Frozen authority sources

Normative application data was read from `benchmark/baseline.md`, frozen
`requirements/B01.md`, `requirements/B02.md`, `harness/profiles/B02.json`, the
original frozen shared regression clauses, and `harness/capabilities/B02.json`.
The latter confirms the tags field/default and has no additional prerequisites.
Phase 5B `FROZEN.md`, the harness protocol and R5.2.2 boundary govern provenance.
R5.37/R5.39 analyses were locators/comparison records, not normative replacements.

The live `harness/regression.py` has a later Phase 5D edit. Its Phase 5B blob
was recovered with `git show 5064950:benchmark/harness/regression.py` and checked
against the frozen SHA-256:
`16d55bac4dc1efa3debc6764ddde9dc27c16b7538de476a0fae9cf7db7519596`.
The text-only copy and extraction provenance are
[R5_40-frozen-regression-authority.txt](R5_40-frozen-regression-authority.txt)
and [R5_40-frozen-authority.json](R5_40-frozen-authority.json). The oracle was
read, not run. B01/B02 request and B02 public-schema hashes also match the
Phase 5B freeze. No Conventional internals, historical generated target or
previous failed target code supplied configuration.

Inherited generic infrastructure defaults are separately traced to checked
launch/transport definitions; these are not claimed as B02-specific requirements.
Opaque semantic/slot identities refer to the saved semantic contracts, with
their public meanings traced to frozen authority.

## 10. B02 transport profile

[R5_40-B02-profiles.json](R5_40-B02-profiles.json) declares seven public
commands: create, list, list-high, list-overdue, complete, delete and migrate.
Creation maps required title/description, optional priority, optional due-date
and optional repeated `--tag`; repeated values retain encounter order. Omission
stays omission. Trim/deduplication/defaults remain semantic expressions.

Success maps the checked payload directly to stdout/exit 0. Semantic failures
map the payload to stderr `error`/exit 1; malformed due-date binding maps the
specified `invalid_due_date` label. Invalid JSON/state maps `invalid_state` as
specified. Generic policies for unspecified infrastructure failures are marked
as inherited defaults, not frozen expected outputs.

Frozen due-date argv supplies plain text. Its faithful saved semantic input is
optional nullable instant. The current profile requires JSON representation for
a nullable decoder and rejects the text descriptor. No JSON-quoted replacement
interface, weaker decoder or hand-authored adapter was substituted. Thus this
is a complete declarative attempt, **not an admitted checked transport profile**.

## 11. B02 state profile

Four declared alternatives: bare legacy V1, version-2 envelope V2, version-3
envelope V3, and current version-4 envelope V4. V2/V3 share the original legacy
typed codec; separate existing `equals(schema_version, 2/3)` constraints remove
overlap with V4. V4 declares equality to 4. Empty missing-store state is V4
with an empty record population; initialization is lazy and only writes
materialize it.

The registration-only source is
[R5_40-b02-semantic-application.json](R5_40-b02-semantic-application.json).
Only the application state registry replaces `legacy_envelope` with equal-codec
V2/V3 identities. **All 15 operation contracts have identical semantic trees**
to R5.37, with identical canonical contract digests. The original source
is preserved. [R5_40-source-registration.json](R5_40-source-registration.json)
records both source hashes, authority and all plan digests. No semantic predicate,
transformation, ordering or migration relation was changed.

A scalar finite-domain discriminator initially appeared to exceed the profile
schema, but this is resolved pre-lock by declared alternatives and existing
equality, independently tested. It is **not** a remaining B02 capability gap.

## 12. Durable-content coverage

The declared codecs check record/collection/nullable/instant shapes. Population
constraints reference the existing identity field, nonblank ID/title and
status/priority domains from frozen validity obligations. They do not duplicate
tag-normalization or migration algorithms. Typed instants retain inherited UTC
validity. No extra persisted-tag normalization rule is invented.

Readiness v2 means: every state descriptor has a constraint, the obligation
supplies typed `requirements`, and each required rule equals a declared rule.
This checks declaration coverage, **not** executable support for every optional
constraint composition. V1/V2/V3 declare domains on optional priority; this passes
schema/rule coverage but the inherited population decoder rejects absence.
Dropping the domain would weaken frozen invalid-enum coverage. Making the legacy
field required would weaken frozen missing-field migration. Neither was done.

## 13. Public state-alternative coverage

[R5_40-B02-obligations.json](R5_40-B02-obligations.json) records all **28**
public/state pairs, with **19 routed bindings** covering all 15 plans:

| Public operations | V1 | V2 | V3 | V4 |
| --- | --- | --- | --- | --- |
| list, list-high, list-overdue | ROUTABLE_BUT_SEMANTICALLY_GUARDED | ROUTABLE_BUT_SEMANTICALLY_GUARDED | ROUTABLE_BUT_SEMANTICALLY_GUARDED | AVAILABLE |
| migrate | MIGRATION_TRANSITION | MIGRATION_TRANSITION | MIGRATION_TRANSITION | AVAILABLE |
| create, complete, delete | NOT_APPLICABLE | NOT_APPLICABLE | NOT_APPLICABLE | AVAILABLE |

Legacy reads route to their existing typed migration-required contracts; migration
routes to existing transition contracts; current migration preserves state.
Legacy writes are not fully specified by frozen authority and are not asserted
available. `NOT_APPLICABLE` means no frozen-authorized successful legacy-write
obligation is claimed, not an invented public rejection contract. No pair is
declared `UNAVAILABLE` merely to manufacture an unspecified benchmark outcome.
Missing storage uses effective V4 under the separately declared policy.

These are declared compatible/routing relationships. The complete **checked**
route-family gate still fails because transport admission fails first; readiness's
missing-coverage diagnostic is a downstream consequence, not absent route data.

## 14. B02 launch profile

Launch configuration uses the semantic application identity, public-only argv,
cwd-relative `tasks.json`, the existing local Python runtime, generic trace
bootstrap defaults and production fresh-ID/UTC-clock providers. Provider types
come from CheckedPlan capability requirements; provider values are empty.
Persistence and transport/state/provenance relationships are computed by the
existing validators. No hidden research arguments or launch process were used.
Component launch configuration validates independently, but no complete checked
application launch is asserted while transport/aggregate admission fails.

## 15. Aggregate B02 profile

The audit attempts to link semantic application/all 15 plans, declared transport
and its argument bindings, state/persistence, launch/provider and trace/provenance
using a **static** manifest. It calls R5.40 aggregate admission. The manifest's
generation label is a static-analysis identity, not a target artifact or evidence
of generation. Aggregate validation **rejects incompatible checked binding**.
No aggregate profile was issued and no generated application was manually authored.

## 16. Profile-source traceability

[R5_40-profile-source-traceability.json](R5_40-profile-source-traceability.json)
contains **821 exact leaf records**. Validation passes with no missing,
duplicate, altered-value, stale-hash or unapproved-source record. Normative
application fields, opaque checked identity references and inherited generic
defaults are explicitly distinguished by their artifact/clause/interpretation.
Expected fixture values from the authority oracle are not copied into profile
outcome data. Empty initial population is frozen missing-store policy, not a
case-specific expected list result.

## 17. Contamination audit

[R5_40-configuration-audit.json](R5_40-configuration-audit.json):
**CONFIGURATION_ONLY**, zero contamination findings, closed structural schema
valid, traceability valid; checked compatibility **REJECTED**. The only schema
compatibility diagnostics are the create/V4 binding and aggregate consequences.
Separate capability findings identify the optional-domain composition.

Review found no expected acceptance output, fixture-specific task/clock/ID,
behavior lookup, generated-code snippet, Conventional implementation knowledge,
filter/order/tag/migration algorithm or request-specific implementation branch.
The copied frozen oracle is an authority document, not profile code or a target.

## 18. Implementation/profile lock

Initial repository clean; HEAD remains
`bdb10e95a27d3739caf284ab044f6cd7b416efd3`. New work was uncommitted; exact status
is saved in [R5_40-implementation-profile-lock.json](R5_40-implementation-profile-lock.json).
**678 working-copy byte hashes** protect compiler/runtime/readiness, schemas,
semantic source, profiles, traces, independent tests/verification, frozen
authority and historical evidence. Reporting documents/static output are
excluded intentionally; they do not authorize implementation or profile repair.

Lock identity:
`e58888b096d317cb6a3f5d2673a901df2c3ed6d25d0b503c323b4b1c1fe4486e`.
Before/after static verification and final lock check pass. A persisted
[one-pass marker](R5_40-static-pass-start.json) prevents a second static pass or
lock/profile reconstruction after evaluation starts.

| Protected identity | SHA-256 |
| --- | --- |
| Unchanged current pipeline | `27a83b7e86c45d787822b5dd28670dd6f46fac2223d1f2ef79d9985169c56350` |
| Unchanged readiness v2 | `136b54d0978499bdcac95ef0ea05cb7a22407e30823928ccf19fae32641dbcd3` |
| Prospective admission implementation | `8d9afb3896a155a45390883304ed3b7b5a310f8e79661fb23f3fa8d8af064498` |
| Bounded profile audit | `24dac8664f54187e0c3b61d8dfdb1f714cd7d0302ebb77d016b195dba8cccd2b` |
| Profile schemas record | `1d365f23f772da03b9462fe9444cd3676660260efd75ac5686c68bba8f2a5be0` |
| B02 profile configuration | `cf27c18b9fc07fb2b9d85a25951aa1812ff226790fe73495f98c7798d3111e29` |
| Registered semantic source | `63c7d2e6f738f98dbaea7342e5614c1b573d2fc9ef515d2d9d6f2a7aed59dd58` |

Every individual compiler/backend/runtime/profile hash, including `src/`,
`schema/`, `air/`, analyzer/emitter/verifier and transport/launch dependencies,
is recorded by exact path in the lock's `files` map. No generic behavioral
implementation changed in this experiment, either before or after the lock.
The new admission/audit support checks were independently verified before lock.

## 19. Frozen B02 static readiness result

Exactly one `readiness_r5_39.inspect` call on the locked configured application,
with transport/state/launch and typed obligations, followed in the same pass by
generic profile schema/admission and declared-capability checks.
[R5_40-B02-static-readiness.json](R5_40-B02-static-readiness.json):
**NOT_READY**; **15/15 SUPPORTED CheckedPlans**; generated/executed false.
Generation/render entry points are patched to raise during this static call.

Raw v2 collects four diagnostics: create/V4 incompatible binding, full-transport
incompatible binding, aggregate incompatible binding, and missing checked public
state-alternative coverage. The last three are downstream admission consequences.
The complete report retains these raw findings, four supplemental capability
occurrences and one analyzer defect. No B02 slice generation or target execution
was used to discover them.

## 20. Complete remaining-gap set

Within the complete frozen boundary obligations considered here, the known set
has **two underlying generic support gaps and one analyzer support-check defect**:

1. Plain-text supplied due-date cannot bind to the faithful optional nullable
   instant input under the current checked transport representation rules.
2. Population finite-domain constraints on an optional legacy field are admitted,
   but do not tolerate legitimate absence. This occurs for priority on V1/V2/V3.
3. Readiness v2 counts exact declared content-rule coverage without detecting
   that optional-domain runtime support is incomplete. The supplemental static
   audit exposes it; the raw v2 report alone is insufficient for that property.

The complete machine report has **nine diagnostic occurrences**: four capability
occurrences (one decoder, three state alternatives), four raw-v2 consequences,
and one analyzer finding. Those are not nine independent capabilities. Known
version-discrimination concerns were resolved with configuration before lock;
they are not relabeled as remaining gaps. No gaps were patched after the pass.

## 21. Gap classification

| Root / consequence | Classification | Evidence |
| --- | --- | --- |
| Text-to-nullable public decoder composition | MISSING_GENERIC_CAPABILITY | Frozen argv clauses; independent nullable text admission rejection; locked binding diagnostic |
| Optional population finite-domain policy | MISSING_GENERIC_CAPABILITY | Existing admitted non-task optional habitat declaration rejects absent field; generic static checks mark the three legacy priority declarations |
| Transport/aggregate/checked-route-family rejection | MISSING_GENERIC_CAPABILITY, downstream of decoder gap | Metadata covers the routes/plans; admission prevents issuing checked family |
| Declared content coverage overstates supported optional-domain composition | READINESS_ANALYZER_DEFECT | v2 rule-equality coverage has no corresponding support finding; independent codec witness and supplemental static type check |

No remaining root is classified MISSING_CONFIGURATION, PROFILE_SCHEMA_LIMITATION,
SEMANTIC_GAP, FROZEN_REQUIREMENT_AMBIGUITY or UNKNOWN. Unspecified legacy-write
availability, invalid-input precedence and extra persisted-tag rules remain
explicitly unclaimed; they do not justify inventing configuration or a new core
construct. The capability finding is bounded to the faithful source/profile
composition tested, not a proof that every conceivable re-authoring is impossible.

## 22. Readiness convergence analysis

| Review | Established boundary |
| --- | --- |
| R5.36 | Independent launch worked; descriptive readiness overgeneralized optional/instant evidence to nullable/whole-contract support. |
| R5.38 v1 | All 15 plans formed, but nullable decoder, public state alternatives, durable validity and concrete profile completeness remained. |
| R5.39 v2 | Independently added nullable JSON decoding, dispatch and content declarations; collected all six then-known missing B02 boundary/profile classes in one pass. No complete concrete B02 profiles were admitted. |
| R5.40 | Frozen-authority metadata supplies profile relationships and version registration; exact representation/content compositions reveal two support gaps before generation, plus the analyzer's optional-domain coverage limitation. |

Failures are moving earlier into static preparation/readiness rather than
serial generated-target repairs. R5.39 collected its whole **known** set, but
missing configuration hid exact representation and optional-state compositions.
R5.40 does not resolve the full set merely by authoring profiles. The remaining
roots are not mostly missing application names/paths; they are generic boundary
composition and support-analysis limits. Green suite counts do not establish
whole-contract closure.

## 23. Overfitting analysis

Configuring public names, flags, codecs and state relationships after reading a
frozen application specification is expected application authoring. It becomes
benchmark fitting if profiles replace semantic algorithms or embed expected
outputs, or if generic behavior changes to accommodate frozen cases.

Safeguards here: independent non-task admission/support witnesses; preserved
generic compiler/runtime/transport/verifier algorithms; declarative closed
profile structure; exact leaf provenance; no fixture providers/outputs; a
pre-pass implementation/profile byte lock; one static pass; no post-pass repair.
The version-registry change is application metadata, not a request-specific
compiler branch. The interface label `invalid_state` is frozen public protocol,
not an expected result population. This bounded audit does not establish
universal absence of overfitting or language generality.

## 24. Future benchmark policy

Prospective proposal for a separately authorized B03+ evaluation:

1. Author semantic source from frozen specification and inherited authority.
2. Configure checked boundary profiles from the same authority.
3. Lock generic compiler/runtime algorithms during evaluation.
4. Require structural/compatibility, contamination and exact source-trace audits.
5. Run complete readiness/support analysis before generation.
6. Preserve the evaluation result without repair.

R5.40 supports the configuration/implementation distinction, but does not yet
validate the complete READY-to-evaluation path. Adoption requires resolving the
known generic support/analyzer set independently. This proposal does not advance
B03, resume Phase 5C or authorize B17 exposure.

## 25. B02 retry decision

**Do not recommend comprehensive B02 evaluation.** The configuration-only
condition and no-post-lock-repair condition hold; **READY does not**. The
three-part gate therefore fails. No R5.41 acceptance retry is authorized by
this result. Profiles and source attempts remain evidence, not accepted B02.

## 26. Construct/system/profile accounting and verification

Candidate core semantics remain **30**, no #31. Historical raw accounting
remains **46**. R5.40 adds one prospective admission policy and one bounded
configuration/support audit system; these are infrastructure, not core constructs.
Application configuration comprises transport, state, launch, typed obligations,
argument bindings, persistence/provider/trace linkage and the state registry.
No aggregate checked B02 profile or target application was issued. The original
84-cell matrix remains 64 supported/20 rejected; prior baseline/duplicate-provider
evidence remains 256 grounded conformant calls. R5.40 adds **zero B02 calls**.

[R5_40-verification.json](R5_40-verification.json) records actual commands,
outputs, discovery-module coverage, failures/errors/skips and environment:

| Verification | Result |
| --- | --- |
| Full benchmark harness, restriction-aware discovery | 386 discovered, 350 pass, 36 explicit B02 rendering/execution/nested-acceptance restrictions; zero failures/errors |
| Application/compiler suite | 31/31 pass |
| R5.37 focused evidence suite | 5 pass, 1 explicit historical live-tree-lock skip |
| New R5.40 focused suite | 14/14 pass |
| Architecture/grounding/semantic/binding/evolution/transport/launch and relevant R5.10–R5.39 suites | Included in full discovery; forbidden historical B02 methods explicitly skipped, never counted as passes |
| Model validation | PASS (`Axiom validate: ok` is the compatibility CLI text) |
| Safety | PASS |
| Closed profile structural schema | PASS |
| Checked profile compatibility | Expected REJECTED; this is the experiment finding, not a failed test |
| Source traceability | PASS, 821 fields |
| Contamination | CONFIGURATION_ONLY |
| Implementation/profile lock | PASS, 678 byte hashes before/after/final |
| `git diff --check` | PASS before lock and after reporting |

Windows/Python **3.14.3**, PowerShell 7, no third-party dependencies,
`core.autocrlf=true`. Final diff checking exits 0 with LF→CRLF checkout warnings
for `docs/decisions.md`, `docs/project-overview.md` and `docs/research-log.md`;
these are separate from actual binding/runtime findings. Hashes use working-copy
bytes. The live-versus-frozen
oracle difference is a historical Phase 5D revision, not an environment failure;
the recovered oracle matches its frozen hash. No environment/test failure caused
the NOT_READY result. Preparatory schema/hash/audit corrections occurred before
lock; the locked pass was not patched or rerun.

Regardless of outcome: Phase 5C paused; B03 prospectively untouched; B17
unexposed/unclassified; semantic-first format globally unfrozen; R5.2.2 remains
historical benchmark authority; universal implementation correctness is not
claimed. Frozen B02 acceptance and B02 generation/execution remain prohibited
for this review.

## 27. Exact recommendation for R5.41

**R5.41 = Independent Public Decoder, Optional Durable-Domain and Readiness
Support-Coherence Review.** On multiple non-task applications, review and resolve
the complete set together: plain-text supplied scalar binding into nullable
semantic inputs with omission preserved; present-only finite-domain validation
for optional persisted fields without defaulting/repairing absent content; and
static admission/readiness checks that reject unsupported content compositions.
Keep representation, generic boundary implementation and semantic constructs
separate. Do not add #31 merely for these existing type/domain compositions.
Only after independent verification should a separately authorized, newly locked
static comparison be considered. **R5.41 is not comprehensive B02 evaluation.**

R5_40_GENERIC_CAPABILITY_GAP
