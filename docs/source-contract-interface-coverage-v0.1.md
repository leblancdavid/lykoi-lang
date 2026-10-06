# Source-to-Contract/Interface Coverage Attestation 0.1 — R5.84

## 1. Status and principle

`SourceContractInterfaceCoverageAttestation-0.1` (SCCA-0.1) is an experimental,
prospective evidence protocol. Pipeline:

**Human source → independent SOI**, separately **human source → candidate FRC /
structural interface**, then **coverage comparison → discovery → adequacy**.

**No downstream implementation authority may depend on an unsupported boolean
assertion that coverage is complete.** Text accountability, independently reviewed
meaning and qualification of the reviewer process are distinct claims. Inspectable
evidence is necessary; a malicious or mistaken evidence-producing reviewer can
still be wrong. R5.84 qualifies neither universal source understanding nor a
production coverage authority. This specification changes no FRC/BDI/V1/Lykoi
semantics and activates no R5.83 candidate.

## 2. Evidence bundle and separate authority

Executable contract: [source_coverage_r5_84.py](../benchmark/evaluation/source_coverage_r5_84.py).
Canonical JSON/digests use unchanged FRC-0.1 serialization. The evidence bundle has:

| Field | Evidence |
| --- | --- |
| `version` | Exactly SCCA-0.1's serialized version string. |
| `source` | `{revision, record}`; positive version and exact FRC source record including source ID/text/hash/classification. |
| `soi` | [SOI-0.1](source-obligation-inventory-v0.1.md), independently inspectable source-side inventory. |
| `contract` | Candidate FRC-0.1, checked by unchanged validator. Schema validity is not fidelity. |
| `interface` | Exact R5.82 structural sidecar with operations/facts/channels/authority and optional finite domains. |
| `source_map` | Identified many-to-many source → FRC/disposition edges. Reverse coverage is computed from all obligations. |
| `structural_map` | Identified FRC → exact interface projection paths, expected values, family, status and rationale. |
| `implications` | Separate source-premise/inference/result records, including review and denial evidence. |
| `questions`, `disagreements` | Active unresolved coverage/interpretation questions and disagreement records; nonempty blocks approval. |

`metadata` is optional display-only data. `coverage_complete`, if injected, is
ignored as authority and excluded from the evidence digest. Everything else in the
bundle participates in evidence binding. Normative information must not be moved
into metadata; the reviewer protocol must inspect that separation. There is no
whole-source completeness flag in the normalized SOI or authoritative evidence.

Review is separate: `{version, reviewer, context_class, evidence_commitment,
result, judgments}`. Each required judgment key (`inventory:ID`, `mapping:ID`,
`projection:ID`, `exclusion:ID`, `implication:ID`) has `{result, rationale}`.
PASS requires inspectable nonempty rationale; other values block approval. Review
binds the entire source/inventory/FRC/interface/maps/issues/implications content,
not just their IDs. In the synthetic fixtures rationales explicitly identify
bookkeeping judgments rather than truthful independent approvals.

An **external admission**, never read from `coverage_complete`, pins reviewer,
inventory digest, exact review digest and mode. The sole implemented mode is
`PUBLIC_SYNTHETIC_EXPERIMENT`. Different reviewer, extractor and formalizer names
are bookkeeping checks, not isolation proofs. Reviews are cooperative content-bound
records, not signatures or authenticated credentials. A caller able to counterfeit
admission and all review evidence can counterfeit an experimental positive; R5.84
explicitly tests this residual boundary. `PRODUCTION` mode rejects. Every result
has `production_authority=false`; no runtime grant, authoring action or runner
eligibility is issued. A future production deployment needs externally qualified
review/admission and enforced sole-entrypoint containment; none is installed here.

## 3. Bidirectional source/FRC comparison

Each `source_map` edge has `id`, nonempty `source_ids`, `obligation_ids` and
`disposition`. Maps can split one source item across several formal obligations,
combine several source items into one formal obligation, or retain dependencies.
Textual 1:1 equality is not required. Semantic comparison remains reviewer work.

| Disposition | Required preservation / gate |
| --- | --- |
| REPRESENTED | Nonempty existing obligation targets plus separate fidelity judgment. Ambiguity/conflict/explicit unspecified inventory cannot be silently converted into determined behavior. |
| AMBIGUITY / CONFLICT | Existing matching FRC issue (`issue_id`); preserve alternatives in FRC/evidence. Active issues halt. |
| UNSPECIFIED | Source explicitly marked unspecified; `preserved_text` must remain in FRC.unspecified. Silence or a positive requirement cannot be relabeled explicit freedom. |
| NONBEHAVIORAL | Source inventory classifies item nonmaterial and mapping gives `rationale`; a formalizer cannot independently erase a material source item. |
| EXCLUDED | Separate exclusion evidence and review, described below. Exclusion may not erase any continuing FRC obligation. |
| UNSUPPORTED | Preserve material source content and route to unsupported scope; no positive attestation. |

Every source item needs a disposition, including nonbehavioral fragments and
explicit freedom. Every formal obligation needs source justification through a
source mapping or a valid implication record. An existing substring quote is
**not** evidence that invented sorting/default/error/persistence/tie/retry policy
is authorized. Missing targets, missing reverse justifications and unresolved
questions fail closed. An invented policy falsely mapped to a real source span
requires semantic rejection by the reviewer; the graph alone cannot prove it false.

## 4. FRC/structural projection

Each structural row is `{id, obligation_id, status, family, entries, rationale}`.
`entries` contain `{path, value, role}`. Paths are exact list/object navigation
paths into the **same** consumed interface, e.g. `["operations",0,"channels","later"]`.
Roles are FACT, OBSERVATION and AUTHORITY. Review covers encoded values and
conditions, not merely existence of a similarly named key. At least one observation
entry is required per represented material obligation. All consumed facts,
channels, authority clauses and optional finite domains must be accounted for;
unreviewed inhibitors or channel exclusions cannot quietly change discovery.

Statuses: REPRESENTED, UNSUPPORTED, OUTSIDE_SUPPORTED_SCOPE, REVIEWER_ONLY,
MISSING (any non-REPRESENTED status blocks structural approval). A row cannot claim
support by naming an unknown discovery family. Existing R5.82 rule keys are the
only supported labels. Review must establish that those rule conjunctions actually
represent the obligation's relevant behavioral distinctions; pointer/value equality
alone does not establish semantic projection. Source obligations such as arithmetic
with no applicable structural family remain reviewer-only in this corpus.

Deadline boundaries, identity stability, event ordering and event multiplicity are
coverage targets, **not** new discovery families. Their source/FRC content remains
visible; structural rows carry UNSUPPORTED and meaningful timing/identity/events
observations. Experimental source-accounting approval can coexist with failed
structural approval. The corresponding downstream halt is OUTSIDE_ANALYSIS_SCOPE.
No source behavior is discarded to fit current analysis. Candidate deadline/identity
text uses existing declarative FRC containers only as unqualified review capsules;
this does not prove those containers faithfully express arbitrary temporal semantics.

## 5. Exclusion authority

EXCLUDED rows add `{class, premises, rationale}` and, for finite mechanical checks,
`domain`. Premises reference source inventory IDs; exclusion review has its own
judgment key. Distinguish:

* **MECHANICALLY_IRRELEVANT:** the implemented bounded proof checks an explicitly
  exhaustive nonempty list of collections, each with size at most one, anchored
  to a source CARDINALITY_BOUND item. Relative returned-order permutations have no
  distinguishing witness on that exact admitted domain. The source/domain link,
  exact-collection interpretation and exhaustiveness still require independent
  review. This is conditional finite reasoning, not a global unreachability proof.
* **EXPLICIT_NON_SEMANTIC:** an explicit source CONSUMER_RESTRICTION premise and
  review justify the variation being unavailable as a contractual distinction.
  Producer freedom and consumer reliance restriction remain separate source items.
* **REVIEWER_CLASSIFIED_IRRELEVANT:** independent inspectable rationale and premises
  are required; mechanical approval means accepted review evidence, not proven
  irrelevance. Materiality disagreements block. A future qualified human can supply
  the same evidence; an AI/provider label cannot create authority.
* **UNSUPPORTED_EXCLUSION:** unproven irrelevance, missing scope, incorrect premise,
  absent review or unsupported reasoning. Cannot authorize implementation.

“Events do not matter” by itself is never an approved exclusion. An umbrella quote,
new identity label or repeated same-context reasoning is insufficient review evidence.

## 6. Necessary implications

Records identify `id`, source `premises`, FRC `result`, `inference_class`, `mode`,
`rationale` and `review_status=APPROVED`, plus inference-specific evidence. Result
must be an existing NECESSARY_IMPLICATION obligation with valid acyclic FRC parents.
No parentless “necessary implication” is accepted.

Bounded CONJUNCTION_ELIMINATION checks that `conclusion` is a member of
`premise_atoms`, using mode MECHANICAL_CONDITIONAL_ON_REVIEWED_PREMISES. Translation
of prose into the atoms, their source authority and connection to result remain
reviewer-derived; this is not automated entailment. REVIEWER_NECESSITY uses mode
REVIEWER_DERIVED and a nonempty `denial_witness` explaining why denying the result
violates the same source premises/domain. Other inference classes halt. Reasonable
conventions, defaults, helpful sorting and generic “good design” do not establish
necessity. Falsely attested atomization or witness truth remains a qualification gap.

## 7. Outcomes and downstream integration

SCCA returns all findings and a primary result with experimental precedence:
SOURCE_CONFLICTING → SOURCE_AMBIGUOUS → COVERAGE_DISPUTED → COVERAGE_INCOMPLETE →
STRUCTURAL_SCOPE_UNSUPPORTED → COVERAGE_UNREVIEWED → COVERAGE_APPROVED.
Malformed/binding evidence halts; its exception diagnostic is not a semantic proof.
Source and structural approval are reported separately. Falsely claimed completeness
is evidenced by mismatches/unsupported assertions in findings, not inferred from
a bool's value or an allegation of dishonesty.

The mandatory **experimental** `downstream` entrypoint recomputes coverage, checks
unchanged full FRC fidelity review, then calls unchanged R5.82 discover/adapter and
R5.81 adequacy/authorization. Only source **and** structural approval enable the
legacy adapter flag; supported discovery and adequate implementation remain separate
conjuncts. Failure returns discovery NOT_RUN, unauthorized and OUTSIDE_ANALYSIS_SCOPE;
source ambiguity/conflict retain NEEDS_CLARIFICATION/CONFLICTING_REQUIREMENT.
Caller-supplied completeness flags never change this. Experiment eligibility is
not a production authoring grant; `production_authorization` is always false.

The historical naked-flag API remains available to historical experiments and their
unchanged evidence. It is isolated outside this prospective path. Sole-entrypoint
production enforcement has not been qualified by adding a wrapper. No frozen
historical code, requirements, runner, schema or evidence is rewritten.

## 8. Qualification limits

Mechanical claims: exact source identity/spans, graph accounting, reverse
justification, projection value/binding, declared unsupported routing, review
evidence presence/content binding and conjunctive experimental gating.
Reviewer claims: semantic extraction, materiality, fidelity, structural adequacy,
observation scope, implication truth, exclusion premises and review independence.

Qualification of the bounded production process would require independently
administered extraction/admission/review, trustworthy access/publication evidence,
source-derived known-answer omission/invention challenges unavailable to formalizers,
and evidence that false mappings/exclusions/implications are refused or remain
disputed on its declared source/domain scope. Real-human requirements and independent
expert resolution would strengthen that evidence; universal understanding is not a
requirement. No numerical production threshold is fabricated from this development
corpus. Preserve correctly unsupported outcomes as successful **coverage refusals**.
R5.84's report separates these proposals from actual experimental observations.
