# Source Obligation Inventory 0.1 — R5.84 experiment

## Purpose and claim boundary

`SourceObligationInventory-0.1` (SOI) identifies candidate material source meaning
**before and separately from** candidate Formal Requirement Contract (FRC)
formalization. It is not an FRC, a natural-language parser, a complete ontology,
an implementation specification or an approval. The experiment supplies human/AI
methodology and inspectable records, not universal natural-language completeness.
See [SCCA-0.1](source-contract-interface-coverage-v0.1.md) for comparison and gates.

Material content can constrain required observations, permitted variations,
input/state/environment domains, consumer reliance or the interpretation of another
clause. Removing it can change a permitted behavior, or hide uncertainty about one.
An ambiguous constraint is material even when no resolved behavior can be encoded.

## Executable normalized inventory

The prospective experimental bundle carries:

| Field | Shape / meaning |
| --- | --- |
| `version` | Exactly `SourceObligationInventory-0.1`. |
| `source_commitment` | Canonical digest of `{revision, record}`; record includes exact source ID/text/text hash/classification. |
| `extractor` | Recorded human/AI identity; attribution does not establish independence. |
| `context_class` | Actual context/isolation class, not a claim inferred from different names. |
| `items` | Identified source items with spans, meaning, materiality, category and dependencies. |
| `questions` | Unresolved coverage questions; nonempty blocks approval. |
| `limitations` | Scope of interpretation, unavailable context and extraction limitations. |

Each item is `{id, spans, meaning, category, material, dependencies}`. `spans`
contains `{start, end, quote}` with zero-based Python Unicode character offsets,
half-open intervals and exact substring equality. Repeated phrases need occurrence
locators. Multiple spans and overlapping items are legitimate. The checker requires
all nonwhitespace source characters to occur in at least one item span, including
punctuation and nonnormative headings. This establishes **text accountability only**.
An umbrella span can still conceal missing semantic distinctions; it is not a proof
of source completeness. `dependencies` reference existing source item IDs and
identify cross-clause interpretation relationships, not execution ordering.

`material` records a reasoned source-side classification. The downstream comparison
cannot change a material item into nonbehavioral content just by relabeling a map.
Independent review must challenge the inventory's classification itself. This field
is not a naked whole-source completeness boolean.

Recognized review categories include BEHAVIOR, FREEDOM, CONSUMER_RESTRICTION,
UNSPECIFIED, AMBIGUITY, CONFLICT, NONBEHAVIORAL and CARDINALITY_BOUND. Additional
labels may document source meaning; they confer no automatic downstream support.
Vocabulary is an elicitation aid, not an exhaustive definition of behavior.

## Source-only extraction protocol

1. **Admit source and permitted context.** Identify the exact text representation,
   version, provenance and who can clarify intent. Inventory all admitted context
   separately. Do not supply candidate FRC, interface, support results, developer
   implementation or acceptance feedback to the source extractor.
2. **First read: actor/actions and observations.** Identify what happens, to whom,
   and what consumers can observe. Split compound clauses when a condition, count,
   exception or outcome could independently be lost.
3. **Second read: modifiers and boundaries.** Challenge selection, conditions,
   quantities, ordering/ties, omission/null, normalization, default triggers,
   state/persistence, errors/retries, atomicity, temporal and identity relations,
   events, frames, invariants, exclusions and explicit freedoms. These prompts are
   deliberately open-ended; ask what the checklist itself fails to express.
4. **Cross-clause read.** Resolve references only where the source warrants it;
   retain combined conditions and conflicts. Test whether a proposed exclusion
   requires an unstated invariant, domain or consumer restriction. Silence is not
   an explicit freedom, error policy or effect prohibition.
5. **Uncertainty read.** Record competing materially different interpretations,
   missing dependencies and unknown observation/admission domains. Do not select
   a convenient interpretation or assume that every unstated detail is material.
   When materiality itself is uncertain, preserve a review question and witness.
6. **Account for all text.** Give nonbehavioral fragments a rationale. Inventory
   positive requirements, explicit unspecified dimensions and consumer restrictions
   separately. Phrase overlap alone never proves equivalent meaning.
7. **Publish and commit.** Freeze exact inventory content/digest, source identity,
   input manifest, reviewer/context class, limitations and access deviations **before
   candidate access**. Here “commit” means immutable evidence publication, not a
   Git commit. Changed interpretation creates a successor record; retain originals.
8. **Compare later.** Process C sees both the committed SOI and Process A's draft.
   Map meaning bidirectionally and review structural projection under SCCA. Only
   declared source authority resolves disagreements; never choose by majority.

## Isolation and human compatibility

Prefer an independently administered source-only workspace with an enforced
input allowlist and inaccessible candidate/development/oracle files. If that is
unavailable, use a fresh cooperative context and disclose the limitation. Record
SAME_CONTEXT, CONTEXT_ISOLATED_SAME_MODEL_COOPERATIVE, MODEL_ISOLATED,
PROVIDER_ISOLATED and STRICT_ISOLATION_QUALIFIED separately; these are evidence
dimensions, not interchangeable ranks or model-name guarantees. A human reviewer
can use the same source ledger and publication protocol; provider identity does
not define semantic authority. Access evidence and protocol qualification matter.

## R5.84 records and limitations

[sources.json](../benchmark/results/phase5c/r5_84/sources.json) supplies 23 short
public synthetic sources. [fixtures.py](../benchmark/results/phase5c/r5_84/fixtures.py)
constructs known-answer source inventories without a candidate input and only then
constructs candidates. This is **same-context development evidence**.

[independent-soi.json](../benchmark/results/phase5c/r5_84/independent-soi.json) is a
source-only publication for six representative sources from a fresh same-model
context. It uses a human-review-friendly extraction record (`quote`, `meaning`,
`category`, `material`, `dependencies`) and retains exact source texts, unknowns and
input provenance. This raw publication is not silently rewritten into the smaller
executable normalized inventory. Process C verifies its physical digest and source
text equality, records span-navigation links, and carries disagreements into the
experimental bundle. Navigation links do not certify semantic equivalence.

All six have additional unresolved interpretation questions. Scope of admission,
zero/null representation, missing eligible records, event attribution and consumer
dependence cannot be settled by a candidate's apparently complete inventory.
No independent positive whole-source approval is established. B01 is a disclosed
same-context, known-public-issue calibration, not blind rediscovery.
