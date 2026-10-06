# Lykoi CollectionQuery normal-path profile 1 — R5.99

This additive profile connects normal requirements to the unchanged
[CollectionQuery-0.1 semantics](collection-query-v0.1.md). It adds no predicate,
numeric, nullable, mutation, join or pagination feature family.

## Integration seam

| Stage | Before R5.99 | Normal-path profile 1 |
| --- | --- | --- |
| Human/source | Natural language, source hash, clarification/policies | Unchanged; AI interprets source/evidence once. |
| Candidate FRC | FRC-0.1 `kind` plus opaque JSON `parameters`, display statement | Same envelope; closed typed `filter_order` query relations validated at formalizer output. |
| SOI/reconciliation | Exact statement **and** relation equality | Typed relations compared independently of display prose; authority, source spans, missing/extra items, context, issues and policies still reviewed. |
| Structural | Normal adapter recognized only older bounded patterns | Explicit typed-profile dispatch into R5.98 structural projection. |
| BDI/adequacy | No normal query routing | Existing query BDI and unchanged adequacy, normal stage outcomes/artifact dependencies. |
| V1 | Historical mapper refused query contracts | `LykoiContractV1` explicitly declares `collection-query-1` and contains faithful `CollectionQueryDocumentV1`. |
| Author/compiler | Fixture v0.3 models only | Fixed semantic author emits `LykoiProgram-1` from authorized V1; normal compiler dispatch validates, recovers and lowers. |
| External behavior | Task CLI observations | Preauthor source-bound external plans also observe exact JSON and persisted byte/absence preservation. |

Typed information was **never produced** by the original normal formalizer
schema/prompts; FRC bookkeeping allowed opaque parameters but assigned no query
meaning. It was not a compiler bug losing existing typed information. R5.98's
corpus constructed facet contracts prospectively; the normal structural/V1/author
dispatchers never selected that profile. Prose-only historical relations stay
unsupported; no English regex, substring, benchmark identity or example lookup
occurs in structural projection, BDI, V1 recovery or lowering.

## Typed FRC/formalizer interface

Use the normal FRC-0.1 obligation envelope. The architecture-consistent relation
kind remains `filter_order`, with parameters **exactly** `{query, facet, value}`.
`query` is a CLI-safe operation identity, not an applicability key. Each operation
must have exactly one source, parameters, predicate, comparison, ordering,
validation, inclusion, effect and result relation. All values have the R5.98
closed types and cross-reference rules. Meaning lives in `relation`; `statement`
and `source_quote` are retained independently for inspection/provenance.

`src/lykoi_workspace/query_schema.py:relation_schema` publishes the closed
per-facet output schema at the normal AI adapter. Workspace validates that schema
and the full group through `query_profile.validate_relations`; the additive
[FRC profile schema](../schema/frc-collection-query-1.schema.json) describes the
unchanged envelope and discriminated relation shape. Native validation, rather
than the intentionally broader envelope schema, is normative for value semantics.
Supported string equality/collection membership, comparison policy, ordering,
validation, inclusion, effects and result are reused verbatim.

Missing material policies are explicit `null`, distinct from empty validation or
inclusion lists and explicit finite freedom. Formalizers must emit blocking
questions/issues for material uncertainty. Workspace's ordinary `ask`, `answer`,
revision/lineage and policy-adoption paths remain in use. A null policy never
obtains adequate implementation authority. Representable `mutating/write` is
distinct but this compiler rejects it. Finite freedom remains analyzable; backend
selection from freedom is not implemented.

Source-only reviewer inputs contain source/evidence and profile instructions,
never candidate output. Reviewers can use different display descriptions;
exact typed relation equality is the bounded equivalence criterion. Stable item
IDs, exact spans and the source commitment, both producers' authorized references,
full context/domain agreement, missing/invented items and unresolved questions
remain required. A typed assertion does not bypass coverage or human approval.
Agreement is not proof of correct source interpretation: correlated omission
remains possible, and same-agent synthetic captures do not claim independent
cognition. Profile validity alone does not issue approval or a grant.

## Normal V1, authoring and execution

The normal `lykoi_pipeline.contracts` dispatcher routes typed queries to the
existing R5.98 machinery. Mixed/unmapped obligations, duplicate/missing facets,
stale values and incompatible storage bindings fail closed. The normal controller
recomputes structural, coverage, BDI, adequacy, faithful V1 and target evidence;
all normal owner seals, separate preauthor plan seals, grants and reservations
remain in force.

Normal formalizer/source-side domains explicitly select
`capability_profile: collection-query-1` for the V1 extension. Existing prospective
R5.98 contracts without that selection retain historical normal-V1 refusal;
their standalone query document path is unchanged. Profile selection cannot
weaken behavior and is independently reconciled with the source-side domain record.

`LykoiContractV1` is an explicit versioned extension envelope: schema version,
capability profile, faithful query document and storage adapter. Historical V1
documents and semantics retain their original mapper. Exact recovery preserves
the complete FRC, facet origins, all typed values and storage authority.

`LykoiProgram-1` is a semantic model containing that authorized contract/profile.
The fixed author creates it from normal V1, not from tests or source prose. The
normal build and `air_compiler.cli validate/generate/safety` dispatch use
`air_compiler.profiles`; all executable queries rerun coverage/BDI/adequacy and
complete query validation before lowering. Author model substitution is rejected
against the authorized V1. Generated Python stays disposable.

Each query is a normal command using its declared runtime string flags. JSON-array
storage uses `COMMAND --store PATH --PARAMETER VALUE`; query errors use declared
JSON stderr and exit 1. The service must supply an independent external plan bound
to the exact source text; no query oracle is inferred from an implementation.
Plans are sealed before authoring. Exact JSON and storage-byte/absence observations
augment the existing external process verifier; no internal application import is
used for acceptance.

## General model-state/store adapter

An explicitly reconciled context domain `collection_store` can select:

- `{kind: json_array}`: existing R5.98 read-only collection storage;
- `{kind: model_state, model: <validated v0.3 model>, state: <state ID>}`:
  read a declared collection field using its existing storage/version/invariants.

The latter is an integration adapter, not a new query family. The source collection
must bind the state ID, every exposed query-view field must match an existing
non-nullable supported field, and the unique key needs a declared model uniqueness
invariant. Existing model state validation handles unrelated fields (including
legacy nullable payload fields). The query sees a typed view; selected records are
returned whole and detached. It cannot predicate/order on nullable fields, create
missing fields, migrate, write, normalize stored values or invent a string-list
field absent from the model. Legacy commands remain available; query/legacy command
collisions refuse. Query execution delegates only to the legacy read path and
never triggers initialization/migration/write. Existing legacy command effects
are unchanged; the profile's read-only claim applies to query commands.

## Evidence boundary

`query_corpus.py` records the active available AI agent's source-bound synthetic
interpretations; ModelAdapter replays them through the ordinary producer interface.
The corpus is not a general English interpreter or a live-provider qualification.
Three pairs of phrasings converge, near-neighbor meanings stay distinct, material
ambiguity invokes normal clarification, and no typed query document is inserted
after formalization. Source-side inventory and literal external oracle captures
are same-agent analytical evidence. The external process and controller lifecycle
are real; human approvals are synthetic test-owner actions. This supports bounded
normal-path integration, not universal formalization accuracy or deployment readiness.
