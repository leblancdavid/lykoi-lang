# R5.41 — Independent Optional Boundary Support Coherence

Primary classification: **`R5_41_SUPPORT_COHERENCE_READY`**.

The two known generic boundary gaps and their readiness mismatch are resolved
in an explicitly prospective boundary implementation. This is independent
optional-value support evidence, not a frozen-request achievement or universal
correctness claim. Core semantics remain **30**; semantic #31 was neither
needed nor implemented. Phase 5C remains paused.

## Starting authority and isolation

R5.40 ended `R5_40_GENERIC_CAPABILITY_GAP`: one locked static pass was NOT_READY
despite 15/15 CheckedPlans. Its 821 traced profile leaves were classified
CONFIGURATION_ONLY, all 15 behavioral contracts remained unchanged, and its
678-file lock is retained. R5.2.2 remains the corrected post-B16 authority.
R5.39/R5.40 source, profiles, runtime, readiness, schemas and evidence are
preserved rather than retroactively corrected.

The working tree was clean before this review. Implementation and test inputs
come from synthetic measurements and the independent seed-bank semantic
constructor, not frozen request fixtures or expected output. New generic modules
contain no request-ID, task, due-date or frozen-output special cases. B02 was
not generated, executed, accepted or statically reevaluated. B03 received no
prospective exposure; B17 remains unexposed and unclassified. There is no
ordinary Phase 5C execution or new freeze.

## A. Exact decoder root cause and correction

`input_binding_r5_32.decode` already implements nullable composition: null
succeeds for a nullable declaration, and a non-null raw value recursively uses
the underlying decoder. Its integer textual decoder and string/instant type
validation remain the value authority. Omission is handled separately by
`bind` using membership, before decoding; missing required values produce
`missing_required`. There is no decoder-level conversion from absence to null.

The actual defect is at `checked_transport_r5_35.validate`, lines 159–165.
It recognizes the underlying nullable scalar, but its representation predicate
requires JSON whenever the element shape is a dictionary. Nullable's structural
representation therefore overrides an already available text decoder. It is a
transport-profile composition/admission defect, not a missing nullable semantic
or terminal scalar decoder.

R5.41 asks whether the declared underlying scalar supports the representation.
Text string/integer/instant compose with nullable; Boolean still requires JSON.
Collection mode still requires a JSON array, while repeat mode decodes each
element and retains encounter order. Record decoders, nested nullable wrappers,
unknown representations and text Boolean remain unsupported. Invalid integer
or instant text remains malformed; a wrong raw scalar type remains a binding
failure. String has no syntactic textual failure in the existing type system;
an independently declared finite public string domain rejects supplied `south`
when only null/`north` are admitted.

Explicit null has a JSON public path. Text `null` is not a special null token:
it remains text and either succeeds as a string or fails its integer/instant
decoder. A text-only profile is not represented as offering an explicit-null
public spelling. Optional omission, nullable null, valid supplied text, invalid
text and binding/type failures are independently distinguished.

## B. Exact durable-domain root cause and correction

`state_runtime_r5_39.conforms`, lines 37–39, unconditionally indexes `row[field]`
for every finite population domain. Its preceding structural type check admits
an absent optional field. The domain indexing then raises KeyError; `decode`
swallows it as a nonmatching alternative and reports invalid state. Absence is
thus rejected as though present-value validation had failed.

The prospective codec first retains structural type validation, then uses:

- Absent: valid only when the field's declaration permits omission.
- Present: validate the underlying declared type and exact typed domain membership.
- Explicit null: present; both nullable type and finite domain must admit null.
- Required absent: structurally invalid, before the population rule.

No absence-to-null/default/empty conversion occurs. Defaults and migrations
remain declared operation behavior. Identity uniqueness, nonblank values,
state equality discriminators and unique alternative matching remain required.
Boolean/integer equality cannot accidentally validate the wrong typed member.
Present invalid optional values are rejected just like present invalid required
values. An optional-nullable domain omitting null still rejects present null.

The public bundle also validates staged generated post-state against its declared
content rules and compatible target alternatives before committing an attempted
write. A well-decoded integer outside the durable domain therefore reaches
semantics but returns `persistence_invalid_state` with original bytes unchanged.
Invalid loaded content stops before semantic invocation. Staging introduces no
implicit migration, default or application algorithm; concurrency/crash-atomicity
is not established by this prototype.

## C. Exact readiness root cause and shared support model

Readiness v2 separately unwraps decoder types and validates transport profiles,
but durable-content obligations check declaration presence/equality only
(`readiness_r5_39.inspect`, lines 119–130). The admitted optional-domain rule is
therefore treated as available even though the runtime cannot implement its
absence path. Individual capability labels and declared rules are insufficient
to establish an executable compatible path.

The prospective model has two shared components:

1. `optional_support_r5_41`: decoder/representation compatibility, optional and
   sequence decomposition, present-domain support and membership validation.
   Admission, raw public parsing, durable runtime and generic capability
   inspection consume these rules.
2. `application_boundary_r5_41.support_report`: CheckedPlan → complete public
   input mapping/binding → state codec/constraints/alternatives → transport and
   persistence policy → launch/provider → aggregate identities/provenance.
   Both readiness and the supplemental prospective audit consume this path
   assessment; neither implements an independent support algorithm.

Readiness additionally checks semantic lowering and declared whole-contract
obligations. Structural and contamination audits remain distinct integrity gates.
Unsupported composition is NOT_READY before generation. READY predicts supported
handling, including declared rejection of invalid future values; it does not
predict that every supplied value is valid. Changing only an expected readiness
label did not resolve the problem: admission and actual durable/runtime behavior
were independently corrected and challenged.

## Independent coherence matrix

The saved matrix has **16 profile configurations**: four scalar types × optional
or required membership × text or JSON representation. **14 support**; the two
Boolean/text profiles reject. Readiness, supplemental audit and actual aggregate
admission agree on all 16. Each supported profile has six raw/value-state probes,
giving **84 rows**. Explicit-null probes on a text profile are explicitly scoped
to the raw binder; the paired JSON profile supplies the public null representation.

| Public/raw state | Decoder | Binding | Durable state | Domain result | Readiness/value disposition |
| --- | --- | --- | --- | --- | --- |
| Optional omitted | Membership path | Absent | Absent field | Valid | READY; accepted |
| JSON explicit null | Nullable intercept | Present null | Present null | Valid only if nullable and domain admit it | READY for supported handling; reject when domain disallows |
| Valid supplied text | Underlying scalar decoder | Typed value | Present typed value | Valid member | READY; accepted |
| Invalid integer/instant text | Underlying decoder fails | Failure | No bound durable value | Rejected | READY profile handles binding rejection |
| Invalid finite-domain string text | String decoder succeeds; input domain fails | Failure | No bound durable value | Rejected | READY profile handles outside-domain rejection |
| Required omitted | Missing-required path | Failure | Required field missing | Rejected | READY profile handles missing-required rejection |
| Wrong supplied scalar type | Underlying type failure | Failure | No bound durable value | Rejected | READY profile handles rejection |
| Present value outside durable domain | Decoder can succeed | Typed value | Present invalid member | Rejected | READY profile handles durable rejection; no commit |
| Unsupported decoder representation/composition | No compatible path | Not admitted | N/A | N/A | NOT_READY; audit unsupported; admission rejects |
| Invalid declared initial durable value | Typed codec/domain failure | N/A | Invalid initial state | Rejected | NOT_READY; admission rejects |

Additional tests cover required valid/invalid present values, null excluded by
domain or type, equal-codec state alternatives with separate discriminators,
nonblank/duplicate-identity rejection, missing optional mappings, wrong decoder
links, provider mismatch, stale aggregate identity, unsupported durable constraint
kinds, invalid domain members, repeated nullable elements, JSON nullable arrays
and sealed support-byte corruption. Optionality is never a general validation
bypass. No test depends on frozen B02 acceptance material.

**15 actual standalone public subprocess calls** independently transfer omission,
supplied values and JSON null for integer, string and instant profiles into
generated durable state. Public PID/cwd/argv/output and durable digests ground
the launch records; the unchanged current pipeline challenges semantic execution.
All 15 are grounded and conformant. Further focused tests exercise malformed
binding, invalid loaded content and invalid generated post-state with durable
byte preservation. The static matrix is not mislabeled as 84 executed calls.

## Implementation and versioning

New modules: `optional_support_r5_41`, `state_runtime_r5_41`,
`checked_transport_r5_41`, `application_boundary_r5_41`,
`transport_runtime_r5_41`, `readiness_r5_41`, `profile_audit_r5_41`.
The existing scalar binder, semantic analyzer/generator/verifier, output schema,
launch/provider rules and aggregate wire schema are reused. The prospective
bundle explicitly installs and seals the new runtime under compatibility
filenames. Historical entry points remain historical; new callers must select
the prospective boundary entry. The policy is documented in
[`docs/optional-boundary-support-r5.41.md`](../../../docs/optional-boundary-support-r5.41.md).

No semantic source vocabulary, v0.3 schema, frozen runtime, frozen contract,
acceptance criterion or benchmark profile was changed. Membership, nullable
alternatives, typed decoding and finite domains already express the needed
behavior. The defects were incomplete profile/runtime composition. Multiple
unrelated scalar types and the independent population witnesses require no
genuinely new semantic concept. Core count remains **30**.

## Verification and integrity

| Check | Observed result |
| --- | --- |
| Restricted full harness | 400 discovered; **364 passed**, **36 explicit prohibited-B02 skips** |
| Application/compiler | **31/31 passed** |
| New focused tests | **14/14 passed** |
| Historical R5.37 evidence checks | **5 passed**; one explicit historical live-tree-lock skip |
| Model validation / safety | Both pass, command exits 0 |
| Independent structural configuration schema | Pass |
| Independent profile-source traceability | **99/99 leaves** traced to the synthetic profile source |
| Configuration contamination | No findings; production provider, no fixture provider values |
| New implementation contamination review | No benchmark/task/field-specific identifiers or frozen-output branches |
| Frozen/historical byte authority | All **678** R5.40 lock members and lock identity unchanged |
| Tracked authority | **681 tracked authority files** unchanged; no tracked benchmark/compiler/schema/model/generated edits |
| Prospective lock | **695 files**, valid; no mismatches |
| `git diff --check` | Pass |

The historical lock's pre-commit HEAD is not asserted against the later current
HEAD; its recorded identity and every protected byte are checked. The prospective
lock checks both bytes and its current HEAD. Its identity is
`ac53da927f116639c52d7c2df5d6e9574e7cf0b516fa8ac5037a3f6538dca2aa`.
The initial 120-second verification invocation timed out without completing its
recorder; a longer bounded rerun completed, and the final recorded verification
includes the subsequently added negative tests. No timeout is counted as a pass.

Reproduce the recorded evidence with `r5_41_review.py summary`; verify the lock
with `r5_41_review.py lock-check`. Verification and lock replacement after sealing
are prohibited by the recorder. Evidence files beside this report:

- `R5_41-verification.json`
- `R5_41-independent-coherence-matrix.json`
- `R5_41-independent-public-evidence.json`
- `R5_41-independent-profile-traceability.json`
- `R5_41-implementation-lock.json`
- `R5_41-lock-verification.json`

## Locked static benchmark decision and R5.42 recommendation

**Zero final B02 static passes.** The optional final comparison was not taken;
independent support closure satisfies this review's objective. The historical
R5.40 recorder's one-shot pass remains consumed and is never rerun. No B02
generation, execution, output inspection, acceptance or iterative repair occurs.
R5.40's frozen result remains unchanged. R5.41 does not claim current full-B02
readiness.

Recommend **R5.42: Separately Locked Whole-Contract Static Support Transfer Review**.
Authorize its prospective static mechanism explicitly before use, preserve the
frozen contracts/profiles, and assess the complete declared boundary using the
now independently demonstrated policy. If authorized, perform exactly one
locked static pass with no post-pass implementation/profile repair; classify and
stop on a new gap. Any later generation or frozen acceptance needs its own
authorization and cannot follow merely from this generic READY classification.
Phase 5C remains paused; B03 is prospectively untouched and B17 remains
unexposed/unclassified.
