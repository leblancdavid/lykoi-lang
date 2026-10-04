# R5.40 — Prospective boundary profile admission and configuration audit

This is an infrastructure admission policy around the existing 30 candidate
core constructs. It does not change the semantic language, compiler, runtime,
transport algorithms or historical R5.39 implementation. The prospective entry
is `benchmark.semantic.application_boundary_r5_40.aggregate`; its serialized
aggregate remains the R5.39 schema, with a separately versioned R5.40 admission
policy identity. Historical generation/launch entries still use their original
admission policy. This static experiment does not silently retrofit them.

## Completeness invariant

For every declared public route/state alternative:

1. The semantic operation references a sealed current CheckedPlan.
2. Every declared invocation input slot has exactly one public mapping, including
   optional slots. Public argument identities and slot identities are unique.
3. Decoder type, raw representation, scalar/collection mode, encounter order,
   finite input domain and omission policy match the declared slot. `omit` is a
   declared policy for a mapped optional argument, not permission to forget it.
4. The route's pre-state codec matches its declared alternative. Its post-state
   codec belongs to the declared state family. Alternatives, initial-state
   reference, persistence policy and content declarations validate.
5. Every outcome variant has a shape-compatible public mapping and declared
   status/stdout/stderr/exit policy. Every plan has a public route.
6. Application/plan/artifact, transport/binding/state, launch/store/provider and
   trace/provenance relationships match their checked identities. Public launch
   availability is established by checked profile linkage, not by executing it.

The current public profile model exposes all **invocation input** slots. It has
no explicit internal-input mapping or transport-wide always-omitted slot policy.
Neither is invented in R5.40. A capability input is separate CheckedPlan metadata
and needs a provider, not a public argument. Other semantic slots (`pre`, `post`,
scoped `item`, outcomes, external values) do not require argv mappings. A future
internal invocation-input exemption would need a declared binder and matching
readiness policy; optionality alone cannot supply that exemption.

Readiness v2 already checks mapped slots equal all invocation inputs. R5.40 adds
that same coverage condition **before** aggregate formation, then delegates
existing compatibility checks. It may remain stricter for whole-contract
obligations. Profile structural admission is not proof of complete frozen
behavior, runtime codec fidelity or public state-pair applicability beyond the
declared route model.

## Configuration versus implementation

Allowed data describes public names; semantic operation/CheckedPlan slot
references; decoder/profile references; input domains, omission and repetition;
output envelope/stream/status/exit mapping; state alternative/version/codec and
declared content-constraint references; persistence policy/initial state/store
path; launch, production capability providers and trace linkage. Equal typed
codecs may have distinct state identities with existing `equals` discriminators.
An initial empty population or an error **label** is interface metadata, not an
expected benchmark result.

Prohibited data implements predicates, transformations, filtering, sorting,
normalization, migration algorithms, expected counts/results, fixture lookup
tables, arbitrary code or frozen-request special cases. Ordering and migrations
belong in semantic source; a profile only links their checked operation/state
identities. Production providers cannot contain controlled fixture values.

`profile_audit_r5_40.structure` checks a bounded closed declarative key/type
schema. Existing validators separately check semantic/profile compatibility;
these are distinct gates. `contamination` rejects behavior fields, executable
objects, fixture providers and non-interface output constants. Record-field
names in typed shapes are identities, not executable instructions. Every leaf,
including empty containers, must have an exact source-trace record: path, value,
artifact, artifact hash, clause and interpretation. Unknown, stale, duplicate,
unexplained or unapproved source records reject.

An auditor must review the source interpretation as well as its hash. The bounded
mechanism does not prove prose entailment or malicious-code security. An audit
may classify metadata `CONFIGURATION_ONLY` while compatibility is `REJECTED`;
that means legitimate configuration could not be admitted by the current
architecture, not that the application is ready. Such a result cannot authorize
generation or evaluation.

The bounded `capability_findings` pass separately collects two independently
observed current support limits from profile types: nullable elements with raw
text representation, and population domains on optional fields. It is generic
over operation/state/field identities and does not implement the missing
behavior. Readiness v2 remains byte-unchanged; its rule-presence check does not
establish optional-domain runtime fidelity. The static report preserves both
the original v2 result and these supplemental findings rather than treating
the declared-rule coverage as a correctness proof.

## Prospective evaluation discipline

For an authorized future request, author semantic source and boundary metadata
from its frozen specification and inherited authority; keep generic algorithms
locked during evaluation; audit schema/source provenance/contamination; run
whole-contract readiness before generation; preserve the evaluation result
without repair. This is a proposed later policy, not authorization for B03 or
B17. R5.40 permits one locked B02 **static** readiness pass only. No target
generation, B02 execution or frozen B02 acceptance is permitted.
