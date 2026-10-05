# Requirement formalization boundary v1 — R5.79

## Status and decision

Adopted prospective methodology, not a production formalizer, new core semantic,
historical benchmark amendment or authorization to access a held-out request.
Core semantics remain **30**. Phase 5C remains paused.

**Phase 5 begins from independently formalized behavioral requirements.** It asks
whether Lykoi can represent, compose, lower and satisfy those requirements. It
does not simultaneously measure interpretation of arbitrary human language.
The [R5.78 source gap](../benchmark/results/phase5c/R5_78-TRUSTED-PREEXPOSURE-B03-V1-PACKAGING.md)
is retained: mechanical packaging cannot invent missing intent.

## Layers and stable terminology

| Layer | Meaning and owner | Output |
| --- | --- | --- |
| Human Requirement | A person's request and relevant authorized context | Prose source, preserved as provenance |
| Requirement Formalization | Interpret intent, expose ambiguity, specify observable behavior; independent formalizer and resolving authority | Draft formal requirements and unresolved issues |
| Formal Requirement Contract (FRC) | Approved, versioned authoritative **WHAT**, independent of Lykoi support | Frozen behavior and explicit assumptions |
| Lykoi authoring | Compose an implementation that satisfies the FRC | Lykoi Program / Semantic Representation: **HOW** |
| Compilation/lowering | Deterministically validate and transform the program using versioned language rules | Executable implementation |
| Behavioral acceptance | Compare external observations with frozen required behavior | Obligation-linked evidence |

Formalization is not compilation. Authoring is not formalization. Compilation
does not approve human intent. A requirement contract is not the implementation's
own contracts or a generated artifact. Static support is not behavioral acceptance.

For Phase 5, the development/evaluation side receives only an independently
approved, sealed V1 evaluation package at its separately authorized observation
boundary. Before opening it receives safe metadata only. It does not receive prose
to interpret inside an observation callback. The normalized static input is
`BehavioralContractV1`; program authoring and eventual acceptance are separately
authorized activities, not implied by static observation.

## Formal Requirement Contract minimum content

This is a logical contract specification, **not a new executable JSON schema or
general predicate language**. A qualified formalization process must select and
version a machine-readable behavioral vocabulary before protected use. Its
meaning must be defined independently of Lykoi support. Required information:

| Content | Minimum rule |
| --- | --- |
| Identity | Contract ID, revision and vocabulary/version; immutable frozen content commitment |
| System context | System/application ID, public boundary, relevant initial state and dependencies |
| Configuration assumptions | Only behavior-material transport, state, launch, environment and external-capability assumptions; no silent defaults |
| Obligations | Stable, unique, case-sensitive IDs and precise machine-readable behavioral relations |
| Inputs and outputs | Relevant domains, omission/null distinctions, preconditions, required results and observability |
| State effects | Required changes and preservation/frame conditions, when state exists |
| Failure behavior | Rejected inputs, error categories/results, rollback or permitted partial effects |
| Invariants and side effects | Required persistent constraints and externally visible effects or their absence |
| Ordering | Required order/concurrency relations only when observable behavior depends on them |
| Provenance | Immutable source identity/commitment, fragment locators → obligation IDs, plus authority resolutions |
| Freeze review | Completeness, consistency, ambiguity resolution and projection approval recorded by the independent authority |

These are information obligations, not mandatory empty fields on every obligation.
A pure calculation need not invent state, persistence, ordering or side effects.
Relevant exclusions must be explicit; absence cannot secretly mean “anything goes.”
Configuration choices not specified by prose must be resolved or explicitly
approved as benchmark assumptions by the authority, never chosen for support.

An obligation may specify `Given input X and state S, produce output Y and state
S'`, with quantified domains and failure alternatives. Do not prescribe Python
classes, helper names, internal fields, algorithms or generated source. Public
API names, wire fields, formats and storage content belong in the contract when
they are themselves required observations. Lykoi operation/binding IDs used by a
projection are bookkeeping, not mandatory implementation structure.

## Identity, completeness and ambiguity

Assign IDs such as `REQ-001` before any support query. Never renumber obligations
to fit support or discard an ID on failure. Revisions preserve IDs for continuing
obligations, retire removed IDs and give new obligations new IDs; split/merge and
meaning changes require explicit lineage. Content commitments change with meaning;
stable IDs alone do not establish unchanged meaning.

Complete means every required externally observable behavior, important failure,
invariant and relevant configuration assumption is covered, obligations are
consistent, and no evaluation-relevant ambiguity remains. A source-to-obligation
coverage review must account for every material source fragment and each approved
context/assumption. Schema validity, source hashes and test coverage alone do not
prove completeness. Bound review scope and record remaining limitations.

A draft may contain an issue record with issue ID, `AMBIGUOUS_REQUIREMENT`, source
locator, question, candidate interpretations and affected obligation IDs. It is
**not frozen authority**. The original requester or independent benchmark owner
resolves it, with an immutable resolution record. The formalizer must not silently
guess or ask which interpretation Lykoi supports.

`CONFLICTING_REQUIREMENTS` blocks freeze when obligations demand incompatible
observations under the same conditions, including conflicts across distinct IDs.
Independent consistency review must reject these. V1 detects duplicate IDs and
differing requirements under the same ID, but does not decide arbitrary logical
consistency. Unresolved consistency or missing meaning blocks approval; do not
claim a general automatic satisfiability/completeness solver.

## Deterministic Phase 5 projection into V1

The FRC is behavioral authority. Its approved **evaluation projection** supplies
complete explicit `application`, `configuration`, `obligations` components under
the [existing V1 contract](benchmark-document-contract-v1.md). No prose parsing,
support-based choice, meaning synthesis or fallback occurs during packaging.

1. The independent authority expresses required application relations in the
   existing `id/state.versions/operations` component interface and approved
   configuration in `transport/state/launch`. These declarative relations specify
   behavior for evaluation; they are not the development-authored implementation.
2. Put supplemental obligations in exact `{id, requirement}` entries. Preserve IDs
   and requirement objects. Known V1 kinds are `public_state_alternatives` and
   `durable_content_constraints`; other kinds stay explicit and unchanged.
3. Keep an independently committed coverage map for **every** FRC obligation:
   application relation location(s), configuration location(s), supplemental V1
   obligation ID(s), as applicable. Every supplemental ID must trace to authority.
   A behavior expressed in application relations need not be duplicated under an
   invented readiness kind. One-to-many mappings preserve original ID lineage.
4. Emit one behavioral document with `schema_version = BenchmarkDocumentContractV1`,
   a deterministic document ID fixed by the packaging rule, `role = behavioral`,
   and `payload = {application, configuration, obligations}`. R5.78's existing
   explicit-component packager is a permissible bounded rule, not a formalizer.
5. Preserve provenance/review/coverage in a separately committed protected record
   or permitted descriptive metadata; never put behavioral requirements only in
   metadata. Metadata cannot carry private acceptance answers or execution instructions.
6. The unchanged generic V1 adapter validates the complete document set and emits
   `BehavioralContractV1`, sorted obligations and its canonical behavioral identity.
   IDs survive normalization; existing readiness receives requirement objects only.
   Traceability therefore needs the retained ID-to-projection map, not inference
   from readiness's positional output.

There is **no claim that arbitrary FRCs already have a lossless V1 projection**.
The current component vocabulary is bounded and semantic-facing. Independently
check projection fidelity before freezing; it must not smuggle in a selected
implementation or erase unsupported behavior. Unknown supplemental kinds are
preserved and can yield unsupported static results. If the existing application
interface cannot faithfully express a required relation, record an evaluation
representation gap, retain the full FRC, and halt package qualification. That is
not by itself evidence of a Lykoi capability gap. A versioned infrastructure
extension would require separate authority, never silent requirement weakening.

Formalization includes explicit specification/projection approval; packaging
after that approval is deterministic. Equal approved components give equal V1
bytes/commitments under the fixed rule. This does not require two formalizers to
emit identical JSON or prove their intentions equivalent.

## Behavioral equivalence and acceptance traceability

Judge static support and eventual acceptance against the approved formal
behavioral authority and its faithful projection. Human prose remains provenance
and context, not an alternate runtime interpretation. A discovered disagreement
with prose is a formalization defect requiring an independently versioned
correction, not permission to change a frozen benchmark during evaluation.

Behavioral equivalence means equal permitted externally observable results,
state effects, failures and ordering under declared inputs/assumptions. Different
classes, source layout and internal representations may be equivalent. Canonical
V1 identity is structural identity, **not** a decision procedure for equivalent
meaning. Future chain: `REQ-ID → static evidence → authored implementation
mapping → acceptance case(s) → observed evidence`. Static support, missing
acceptance coverage and actual failed behavior must be distinguished. No complete
acceptance architecture is implemented in R5.79.

## Independent authority and prospective B03–B20 process

A trusted human formalizer is valid. An isolated AI formalizer is also possible.
Neither may inspect Lykoi support, development solutions or evaluation feedback,
query static consumers, modify Lykoi, weaken requirements for expressibility, or
alter obligations to pass. Structural validation is permitted; support inspection
is not. Review must assess intended behavior, not agreement with the formalizer.
The approving authority must be independent of Lykoi development; human review
may use a separate reviewer or an accountable independent benchmark owner.

Prospective process, **not executed here**:

1. Qualify the vocabulary, interpretation/review procedure, ambiguity/conflict
   handling, projection fidelity and containment on synthetic requests, public
   B01 and additional non-held-out examples. Freeze the procedure before B03.
2. Separately authorize a trusted boundary to receive original protected source
   and permitted context; do not expose it to Lykoi development.
3. Produce a draft FRC, retain source coverage, and resolve issues through the
   independent owner. Approve completeness/consistency and implementation neutrality.
4. Approve the complete V1 projection and mapping; structurally validate it
   without static support queries. Halt on missing meaning or representation gaps.
5. Commit immutable FRC, source provenance, resolutions, review, projection map,
   V1 bytes and exact resource inventory. Seal the static package; keep eventual
   acceptance/execution material separately committed and authorized.
6. Publish only reviewed safe schema/version, opaque identity, commitments,
   inventory/roles and non-content-bearing authority attestation. No prose,
   obligations, ambiguity questions, counts that reveal behavior, or payload hints.
   Trusted access and development exposure must have separate recorded accounting.
7. Verify metadata eligibility and freeze qualified state/adapter/consumers using
   the existing runner. Later, separate one-shot `ACTUAL_HELD_OUT` authority may
   permit opening, commitment verification, adaptation and static observation.
   Retain the one-time ledger, exclusion and immediate post-check; then stop.

This is not a new freeze or blanket authority for any B03–B20 access. Existing
exposure classifications apply per request; already exposed material cannot
become pristine through formalization. No B03 contract/package/commitment or
runner eligibility is created here. B03 reads, authorizations, openings,
observations and static-consumer calls remain **zero**.

## AI-native, AI-independent future

Eventual architecture: `Human → human-language requirement → replaceable human/AI
formalizer → review/approval → frozen FRC → Lykoi authoring → deterministic
validation → deterministic lowering/compiler → software`.

AI can understand people, supply context and propose formal intent; Lykoi supplies
precise program semantics and deterministic transformation. Probabilistic reasoning
and deterministic meaning have explicit interfaces. This strengthens the AI-native
goal while preserving [AI independence](ai-independence-r5.48.md).
OpenAI, Anthropic, Gemini, local/future models and humans are possible authors.
Provider/model identity and credentials are not part of the FRC's behavioral
meaning or V1 behavioral identity. Optional authorship/fairness records are separate.
Once a contract exists, its meaning must not depend on the authoring provider.

Separate **Requirement Formalization Research** should study reliability,
completeness, human-review burden, ambiguity elicitation, cross-model normalized
behavioral agreement, interactive formalization and minimal requirement-change
diffs. Behaviorally equivalent contracts need not be structurally identical.
These remain research questions, not guarantees or Phase 5 semantic scores.

## Historical lesson and validation scope

`B02_EXPOSED_IN_R5_75` / `B02_STATIC_RESULT_INDETERMINATE` are permanent.
The public historical callback failure illustrates the danger of implicit
document interpretation during observation. B02 contents, captured documents and
support results are not contract-design feedback here.

See the [R5.79 validation record](../benchmark/results/phase5c/R5_79-VALIDATION.md)
for synthetic conceptual cases and bounded executable V1 corroboration. Architecture
qualification does not qualify a production formalizer or held-out packaging.
