# Formal Requirement Contract v0.1 — R5.80 experimental specification

## 1. Status, purpose and boundary

`FormalRequirementContract-0.1` (FRC-0.1) is a bounded experimental
specification and methodology for independently formalizing behavioral
requirements. It implements the methodological distinction in
[requirement-formalization-boundary-v1.md](requirement-formalization-boundary-v1.md):
source interpretation establishes WHAT; subsequent program authoring chooses HOW;
compilation and acceptance are separate activities. This document defines a
review protocol with a bounded structural validator, not an executable requirement language,
general proof system, or production-qualified formalizer.

The relation vocabulary below consists of **structured, reviewed declarative
clauses**. Its names are experimental requirement labels, not new Lykoi
primitives. Neither vocabulary selection nor interpretation may be fitted to
Lykoi support. No Lykoi change, protected-source access, benchmark opening,
static-consumer call, new freeze or acceptance qualification follows from this
document. Phase 5C's existing boundary remains authoritative.

The design inputs for this document are the boundary specification, agent
workflow, the first 100 lines of the project overview, and
`benchmark/results/phase5c/r5_80/corpus.json`. References to other material below
describe future authorized evidence; they do not report inspecting it.

## 2. Contract record

An FRC is a JSON object with exactly these top-level fields:

```json
{
  "schema_version": "FormalRequirementContract-0.1",
  "contract_id": "FRC-S01",
  "revision": 1,
  "source": {
    "id": "S01",
    "text": "Given two integers x and y, return their sum. No state or external effects are permitted.",
    "sha256": "<lowercase SHA-256 of the exact source text UTF-8 bytes>",
    "classification": "SYNTHETIC"
  },
  "context": {
    "scope": "<public boundary and applicable initial conditions>",
    "domains": {},
    "assumptions": [],
    "component_authority": null
  },
  "obligations": [],
  "issues": [],
  "unspecified": [],
  "implementation_choices": [],
  "lineage": [],
  "formalizer": "<recorded author identity>",
  "review": null
}
```

This is a shape illustration, not an approved contract: its placeholder hash,
context and empty obligations cannot qualify. All listed fields are required.
An absent field is not equivalent to an explicit `null`. `review` is always
`null`: review authority lives in a separate, content-bound receipt.

### Field rules

* `schema_version` is exactly `FormalRequirementContract-0.1`; `contract_id` is a
  nonempty, stable, case-sensitive identifier. `revision` is a positive integer,
  increasing for each changed contract record. Reusing a revision with different
  content is invalid.
* `source.id` is a stable source identifier, `text` preserves the exact authorized
  source text representation, and `sha256` commits to UTF-8 text without trimming, newline conversion,
  Unicode normalization or an added byte-order mark. `classification` is exactly
  `SYNTHETIC` or `PUBLIC`. It is provenance, not permission to read a source.
  For this round public B01 uses the admitted LF tool-text transcription. The
  unchanged physical `.md` bytes have a separate commitment in `qualification.json`;
  its explicit newline-representation relationship is provenance, not a changed
  requirement or an assertion that the text hash is the physical-file hash.
* `context.scope` is a precise string identifying the required public boundary,
  relevant initial state and dependencies. `domains` is an object naming input,
  output and state domains with explicit restrictions. `assumptions` is an array
  of strings specifying behavior-material conditions and their authority.
  Assumptions must not silently add product requirements or select easier behavior.
* `context.component_authority` is `null` unless an independently authorized
  whole public component source is deliberately selected. The object contains
  exactly `application` and `configuration`, with complete inline content. Its
  immutable content commitment, source selection and scope are recorded in the
  source/context and review evidence. References alone do not supply missing
  components; selected content and its inventory must be available to review.
* `unspecified` contains strings identifying genuinely open behavioral dimensions,
  including out-of-domain cases. `implementation_choices` contains strings
  identifying internal freedoms that preserve every required observation. A
  required public API, wire field or durable content format is not an internal
  choice merely because an implementation exposes it.
* `formalizer` is a nonempty recorded identity. It is attribution, not evidence
  of correctness. `lineage` is an array of revision/change records as defined below.

Every obligation has exactly the following fields:

```json
{
  "id": "REQ-001",
  "basis": "STATED",
  "source_quote": "Given two integers x and y, return their sum.",
  "derived_from": [],
  "relation": {
    "kind": "sum",
    "parameters": {
      "domain": "x and y are integers",
      "condition": "for every pair in that domain",
      "result": "the integer x + y"
    }
  },
  "statement": "For every pair of integer inputs x and y, the returned result shall equal x + y."
}
```

`id` is unique and case-sensitive within the contract. `basis` is `STATED` or
`NECESSARY_IMPLICATION`. `source_quote` is a nonempty exact substring of
`source.text`; paraphrases are not quotes. A quote need not be a whole sentence,
but its scope and context must remain visible in the coverage record.
`derived_from` is an array of obligation IDs in this contract. Stated obligations
normally have no derivation parents. Necessary implications require nonempty
parents, an acyclic derivation, and a separately recorded entailment rationale.
An implication's quote anchors its source basis; quoting text alone does not
establish entailment. `relation.parameters` is an object. `statement` is precise
normative text defining the required observation, not an implementation recipe.

Every issue has exactly these fields:

```json
{
  "id": "ISSUE-001",
  "category": "AMBIGUITY",
  "description": "The source does not define what makes a task best.",
  "affects": ["REQ-001"],
  "alternatives": ["Rank by urgency", "Rank by another owner-specified criterion"],
  "witness": null,
  "resolved": false
}
```

Issue IDs are unique. `category` is `AMBIGUITY`, `CONFLICT` or `QUESTION`;
`affects` names existing obligation IDs, or is empty for a contract-wide issue
with the scope explained in `description`. `alternatives` is an array of
strings, not a formalizer-selected resolution. `witness` is `null` or an object
describing applicable inputs/state, competing required observations and why
they differ. `resolved` is always `false` in an issue record under this shape.
Resolution produces a new revision, removes the active issue and references an
immutable authority resolution in lineage and the review evidence. Old drafts
retain their unresolved issues. Approval requires no active issues; an apparently
immaterial issue must first be scoped and explicitly dispositioned by authority.

## 3. Controlled relations and semantic obligations

Only these `relation.kind` values belong to FRC-0.1:

| Kind | Meaning and required parameter information when applicable |
| --- | --- |
| `sum` | Operand domains, quantified condition, arithmetic result and numeric boundary assumptions. |
| `increment` | Input domain, increment amount and exact result; no invented policy outside the domain. |
| `crud` | Public entity/key/value domains; each creation/read/update/deletion condition, observation and effect; frame for other entities; absent/duplicate-key scope. |
| `filter_order` | Input record domain, exact selection predicate, multiplicity, ordering comparison, tie rule and input-preservation frame. |
| `normalize_ascii` | ASCII domain, exactly which leading/trailing characters are removed, case mapping, composition and unchanged internal content. |
| `transition` | Applicable prior state/input, accepted and rejected branches, output, successor state and unaffected-state frame. |
| `invariant` | State domain, quantified constraint and when it must hold, including relevant initial and post-operation states. |
| `persist` | Key/value domain, successful write/read observations, restart durability, failure result and preservation/atomicity frame. |
| `optional_dispatch` | Public field, absent/present-null/present-valid/present-invalid branches, exact results, domain and required effect frame. |
| `selection_prefix` | Input domain, qualifying predicate, bound, earliest-prefix selection, multiplicity/order, zero case and input frame. |
| `effects` | Trigger conditions, observable effect kind/recipient/content, exact or bounded cardinality, prohibited effects and failure/rejection cases. |
| `priority_extension` | Public priority field/value domain, applicability to entities and extension boundary; explicitly required preservation of unrelated existing behavior. |
| `priority_rank` | Defined priority comparison/rank mapping and tie conditions; no guessed ordering from labels alone. |
| `priority_create` | Creation input domain, omission versus explicit values, resulting public priority and rejection/effect conditions if required. |
| `priority_list` | Listing domain, required priority observations, ordering, tie behavior and preservation of other required observations. |
| `priority_filter` | Query/value domain, exact selection and output/multiplicity/order constraints where required. |
| `migration_preserve` | Relevant old/new public state domains, migration trigger, preservation mapping, defaults and required failure/frame behavior. |
| `default` | Precisely identified omission/initialization condition, required value and scope; explicit null is distinct unless authority equates it. |
| `public_state_alternatives` | Required public-state alternatives and their conditions, using the existing V1 requirement meaning without reinterpretation. |
| `durable_content_constraints` | Required durable content constraints and scope, using the existing V1 requirement meaning without reinterpretation. |

This table fixes review topics, not an executable grammar for parameter values.
Parameters may use JSON values and precise declarative text. Each applicable
clause must explicitly carry domain, condition and frame information (the exact
parameter key spelling is not prescribed);
additional keys name the result, branches, ordering or other relevant facts.
An obligation may reference a named domain in `context.domains`, but the domain
must be resolvable and its use explicit. Inapplicable concepts need no invented
fields. A frame stated elsewhere may be explicitly referenced by obligation ID.
Silence cannot be interpreted as a preservation guarantee or an effect ban.

Parameter objects must describe behavior, not classes, algorithms, helper names,
Lykoi operation IDs or selected storage engines. Public names and storage content
are legitimate parameters only when they are required observations. A compound
requirement may need several clauses; no single kind is assumed to encode its
whole meaning. An unrepresentable required concept creates a vocabulary gap and
halts qualification rather than being forced into a superficially similar kind.

The statement, parameters and context jointly define the reviewed claim. A
disagreement between them is a consistency defect, not a precedence rule allowing
one field to erase another. Necessary implications may expose constraints already
entailed by the source; they may not strengthen it with convenient policies.
For example, nonnegative available seats constrains accepted reservation results;
it does not alone entail locking, fairness or a retry algorithm.

### Optional semantic dimensions

Reviewers explicitly ask whether quantification, domain boundaries, frame
conditions, temporal relations or concurrency affect observable behavior. They
include such concepts only where source/context warrants them. State-free
arithmetic does not require persistence. A later read after process restart does
require temporal/durability meaning. Stable sorting requires tie behavior, not
an implementation algorithm. Concurrent invocation, linearizability, isolation,
timeouts, integer overflow and invalid-input behavior are not implicit defaults.
If material and unresolved they create issues; if genuinely outside authority
they are recorded as unspecified. Sequential examples do not prove concurrency
semantics. Transport-level JSON `null` and omitted object keys remain distinct
even when some domain expressly admits both.

## 4. Methodology A–F

The six activities have separate artifacts and claims. Completing a later
activity cannot retroactively repair missing authority in an earlier one.

### A — Source admission and context declaration

Record source identity, exact text, classification, commitment, permitted context
and authority scope before interpretation. Keep original sentence/fragment
boundaries with character offsets in a separate coverage ledger. Record who may
resolve intent, permitted public component sources, and the reading inventory.
No protected request material or development support evidence is admitted by
this experiment. Labels such as `PUBLIC` do not replace explicit access authority.

### B — Draft formalization and coverage

Assign stable obligation IDs before any support query. Extract externally
observable requirements, write precise clauses, and distinguish stated content,
necessary implications, assumptions, unspecified behavior and internal choices.
Construct a coverage ledger that accounts for **every source sentence** and every
material fragment, with exact quotes and offsets, mapped obligation/issue IDs,
and a rationale for context-only or nonnormative text. Repeated identical quotes
require occurrence locators. Split a sentence's multiple requirements if needed;
several obligations may share a quote. No material fragment may disappear merely
because it lacks a convenient relation kind.

For every necessary implication retain parent IDs, source anchors and a rationale
showing that denying it would violate the parent requirements under the same
context. Check that the derivation is not circular and does not rely on an
implementation convention. Coverage of approved assumptions and component
authority is recorded separately from source-quote coverage; neither fabricates
an exact prose quote for context not present in the source.

### C — Issue elicitation and authority resolution

Flag ambiguous terms, incompatible demands and missing material conditions.
Present alternatives and distinguishing witnesses without consulting Lykoi
support. Only the authorized requester or independent benchmark owner resolves
intent. Retain its identity, decision, rationale and exact prior/new commitments
in a separate resolution record. Revise the contract and coverage ledger, keeping
stable IDs and explicit lineage. Unresolved meaning or conflict blocks approval.
For an unresolvable source, a correctly blocked draft is a successful detection
result, not an approved behavioral contract.

### D — Independent review and approval

A separate reviewer receives the admitted source/context, draft, coverage,
derivations and resolution evidence, but no support results or developer solution.
Review the eight dimensions in section 7. Record a content-bound receipt; request
revision or block rather than choosing an interpretation silently. Approval is
scoped to the reviewed record and evidence. Draft generation and review must
remain distinguishable even when both use AI.

### E — Evaluation projection and deterministic packaging

Only an approved contract proceeds to prospective projection. Independently
approve complete explicit application/configuration/obligation components and an
ID-to-component coverage map before deterministic packaging. A projection gap
halts package qualification; it is not automatically a Lykoi capability gap.
The contract remains intact, including behavior unsupported by current consumers.

### F — Bounded assessment and reporting

Compare independently produced contracts by meaning as well as structure. Report
source accounting, implication validity, issue detection, review disagreements,
revision burden, projection coverage and qualification outcomes with denominators.
Separate drafting success, correctly blocked sources, approved contracts,
projection failures, static support and eventual observed acceptance. No aggregate
score may count an unresolved source as successfully approved. Preserve failed
drafts and counterexamples. State which activities actually ran; this document
does not itself report empirical outcomes.

## 5. Calibration sources and projection limits

The R5.80 corpus contains twelve synthetic sources:

| Source | Principal calibration concern |
| --- | --- |
| S01 | Integer sum and explicit absence of state/external effects. |
| S02 | CRUD composition, unaffected-note frame, explicitly unspecified absent/duplicate cases. |
| S03 | Exact active selection, Unicode code-point ordering and stable ties. |
| S04 | ASCII-only trimming/case normalization without changing internal spaces. |
| S05 | Initialization, conditional closure, rejection result, frame and state invariant. |
| S06 | Last-successful-write durability across restart and failure preservation, without choosing an engine. |
| S07 | Omitted versus null versus integer versus invalid and an explicit effect prohibition. |
| S08 | Undefined “best”; approval must await authority-defined meaning. |
| S09 | Conflicting insertion/alphabetical orders; `["z", "a"]` witnesses incompatible outputs. |
| S10 | Positive-integer success domain; invalid cases and effects remain unspecified. |
| S11 | Earliest positive-value prefix, nonnegative limit, zero case and input preservation. |
| S12 | Conditional reservation, state invariant and exact confirmation cardinality. |

These are AI-authored human-style sources from the coordinating R5.80 session,
not an independent real-user corpus. They calibrate selected failure modes, not
general language understanding. The corpus also identifies the existing public
human-written B01 source; this document does not import its contents or the whole
baseline as B01 authority. Priority relation names are bounded public calibration
vocabulary, not evidence that a B01 formalization has been completed here.

Additional non-held-out source **P01** may explicitly select the pre-existing
public optional-measurement fixture's **whole configuration and behavior** as
component authority. Such a calibration must identify and commit the exact public
fixture selection before drafting; retain required prose obligations with exact
quotes and separately account for authoritative component content. This is an
explicit component-selection experiment, not arbitrary prose-to-component
conversion and not permission to import an unrelated baseline. P01 is additional
to the twelve synthetic sources and public B01, not silently another corpus entry.
No P01 content or commitment is invented by this specification.

The only known supplemental forms with existing V1 meaning are
`public_state_alternatives` and `durable_content_constraints`. Their requirement
objects must retain that meaning and required fields; this document defines no
replacement parameter schema for them. Other relation kinds have **no generic
mapper** to V1. Matching kind names does not authorize copying arbitrary parameter
objects into an existing V1 requirement interface.

Application relations may represent some obligations only through explicitly
reviewed component authoring. Preserve the ID-to-projection map even where an
obligation has no supplemental entry. The complete V1 document has explicit
application, configuration and obligations components under the existing
`BenchmarkDocumentContractV1` interface; generic adaptation yields
`BehavioralContractV1`. Mechanical packaging begins after meaning and projection
are approved. It cannot infer missing intent, select assumptions, discard unknown
kinds or weaken requirements. Fidelity approval must be separately bound to the
exact projection and map; an FRC-only approval does not approve future V1 bytes.

## 6. Equivalence, identity and open-world meaning

Let `Beh(C)` denote the set of permitted externally observable behavior traces
for contract C over its declared inputs, initial states and approved environmental
assumptions. Traces include relevant results, state changes, failures, effects,
ordering and temporal observations. This is a review model, not an implemented
logic or automatically enumerable set.

Two contracts are behaviorally equivalent when their authority scopes and domain
interpretations align and `Beh(C1) = Beh(C2)`. Reviewers must explicitly align any
renamed public observations; they cannot hide a required difference behind an
internal renaming. If domains or assumptions differ, equivalence is unestablished
unless the difference is justified as meaning-preserving. Equality only on an
intersection of domains is restricted agreement, not whole-contract equivalence.

Unspecified behavior is **open-world freedom**, not an implicit rejection,
no-effect promise, default value or hidden acceptance rule. Equivalence preserves
those freedoms as well as positive requirements. Filling an open dimension with
a mandated policy can be a strict refinement, but is not equivalence. For example,
S10 does not prohibit external effects; silently adding S01's effect prohibition
changes its permitted behavior set. Required frame conditions, by contrast, do
constrain behavior and must not be lost as “implementation details.”

Canonical equality of `kind` plus `parameters` provides only bounded structural
support for comparison. It is not a semantic equivalence decision: reviewers must
also compare normative statements, source authority, domains, assumptions and
frames. Different clause decompositions or parameter wording may be equivalent;
equal parameter bytes can still conceal divergent statements or contexts. Neither
stable IDs, equal source hashes, matching tests nor matching V1 structural identity
proves behavioral equivalence. Review judgments should record agreed differences,
counterexamples and remaining uncertainty; unclear cases are `INDETERMINATE`, not
declared equal. Distinguish `EQUIVALENT`, `NOT_EQUIVALENT` with a distinguishing
witness, and `INDETERMINATE` from approval outcomes.

## 7. Independent, content-bound review protocol

The reviewer must independently examine source fidelity, rather than merely
ratifying a formalizer's rationale. Reviewer identity must differ from
`formalizer`. Identity inequality is a bookkeeping check, **not proof of human
trust, organizational independence, model diversity or absence of shared bias**.
Record the isolation procedure and admitted artifacts. Same-model procedural
isolation is possible and must be reported as such, not called cross-model
validation. Reviewers and formalizers may check structure but must not inspect
Lykoi support, development solutions or acceptance feedback, query static
consumers, or revise requirements for expressibility.

### Eight mandatory dimensions

| Receipt check | Independent review question |
| --- | --- |
| `source_coverage` | Does sentence/fragment accounting cover every material requirement and all approved context, with exact quotes and no unexplained omissions? |
| `no_invention` | Are constraints stated or necessarily entailed, with valid derivation evidence and explicitly authorized assumptions rather than guessed defaults? |
| `ambiguity` | Are material interpretations explicit and authority-resolved, with no active issues or silently selected alternatives? |
| `conflict` | Are simultaneously applicable clauses compatible, including across IDs, domains, statements, parameters and approved context? |
| `neutrality` | Is WHAT independent of implementation and Lykoi support, with only required public structure prescribed? |
| `identity` | Are source/content commitments, revision identity, unique stable IDs, references and lineage valid and bound to the reviewed artifacts? |
| `consistency` | Do all representations, derivations, unspecified freedoms, assumptions and lineage agree without circularity or contradictory frames? |
| `fidelity` | Does the full contract preserve source meaning and freedoms, and, if reviewed, does the exact projection preserve the full approved contract? |

`conflict` focuses on incompatible demands; `consistency` also covers internal
record coherence. Passing either is a bounded reasoned judgment, not a general
satisfiability proof. Fidelity at FRC scope and projection scope must be identified
separately; no absent projection is silently approved.

### Separate receipt and commitment checks

An experimental receipt records at least: receipt version and ID, `contract_id`,
`revision`, FRC content SHA-256, source SHA-256, reviewer and formalizer identities,
review scope, outcome, the eight named check results with rationales/evidence,
review limitations, and commitments to coverage, derivations, resolutions and
lineage evidence. Projection-scope receipts additionally commit to the exact
component set, projection map and packaged bytes under their declared rule.
An absent artifact is explicitly out of scope, not represented by a fabricated
commitment. Receipt records are immutable and retained separately from the FRC.

For the experiment, canonical FRC JSON uses recursively lexicographically sorted
object keys, preserves array order, emits UTF-8 with unescaped Unicode, uses
compact `,`/`:` separators and no final newline, and permits only ordinary JSON
values (no NaN or infinity). Do not normalize text or coerce numeric values.
Specify the same serialization rule for JSON side-artifact commitments; raw
artifacts have hashes of their exact bytes. This deterministic identity rule is
not semantic normalization. The source text hash and whole-record hash have
different inputs and are checked separately.

Before accepting a receipt, a consumer must:

1. Recompute the source and FRC commitments and match the exact contract ID,
   revision and version; reject mismatches or a receipt for earlier content.
2. Verify referenced evidence commitments and inventory, unique IDs, reference
   validity, derivation acyclicity and lineage continuity within the admitted scope.
3. Verify the reviewer/formalizer identity inequality and documented isolation
   procedure, while retaining the limited trust meaning of that check.
4. Require all eight dimensions to be present, scoped and supported. For approval,
   each must be `PASS`; `FAIL` or `UNDETERMINED` prevents approval.
5. Require no active issues, no unresolved evaluation-material assumptions and a
   coherent authority-resolution trail. Validate projection commitments and
   fidelity separately when package qualification is requested.
6. Check outcome against findings and scope. A valid digest proves content binding,
   not truthful review or correct interpretation. No digital signature or trusted
   identity infrastructure is claimed here.

Implemented review outcomes are `APPROVED`, `REJECTED`, `NEEDS_CLARIFICATION`,
`CONFLICTING_REQUIREMENT` and `INCOMPLETE_FORMALIZATION`. `APPROVED` means all
eight checks pass at the declared scope. `INCOMPLETE_FORMALIZATION` identifies
missing required clauses or accounting. `NEEDS_CLARIFICATION` preserves unresolved
intent or authority. `CONFLICTING_REQUIREMENT` preserves incompatible demands.
`REJECTED` identifies a disqualified record or process, including invented policy
or implementation leakage. Representation gaps are projection outcomes, not
formalization disapprovals. Findings are recorded for every nonapproval.
An approved FRC is authoritative only after the independent authority freezes its
exact content and receipt; draft status cannot be inferred from shape alone.

## 8. Revision identity and lineage

IDs persist for continuing obligations and are never renumbered to fit support.
Every change to an already recorded revision produces a new revision and content
commitment. Meaning changes retain the continuing ID only with an explicit
`meaning_change` lineage event. Removed IDs are retired permanently within the
contract; they are not recycled. Splits retire the original ID and allocate new
IDs; merges retire the inputs and allocate a new ID. Record original IDs, successor
IDs, previous/new revisions and commitments, change reason, authority and any
resolution reference in each lineage object. Initial records may have empty
lineage; subsequent records must explain their predecessor and changes.

The implemented lineage entry has exactly `change`, `previous`, `current` and
`reason`. `change` is `meaning_change`, `retire`, `split` or `merge`; previous/current
are ID arrays. Revision commitments, authority and resolution evidence remain in
a separate revision ledger. New IDs and unchanged continuation are detectable
without inventing lineage events. Source-owner resolution is specified but not
implemented; an active issue cannot be cleared by setting a boolean. Coverage and projection maps follow the
successor IDs without erasing earlier evidence. Compare meaning across revisions;
a stable ID alone cannot establish unchanged behavior. Each revised contract
requires a new content-bound review. A defect discovered after freeze produces an
independently versioned correction, not an in-place change to historical authority
or evaluation evidence.

## 9. Claims and completion criteria

The experiment can establish bounded observations about the selected sources,
review procedure and expressly reviewed projections. Qualification requires exact
source accounting, justified derivations, resolved issues, stable identity and
lineage, all eight independent checks, and immutable content-bound approval. A
package additionally requires complete, faithfully reviewed projection and
deterministic packaging. Failing that gate must preserve the unweakened contract
and identify whether the failure is interpretation, review, representation or
packaging; it must not automatically be scored as a language capability failure.

Natural-language interpretation, implication judgments, equivalence judgments
and review remain fallible. Synthetic calibration, same-model isolation and a
small public example set cannot establish general formalization reliability,
real-user elicitation quality, provider independence in practice or production
qualification. Structural validity and deterministic commitments provide useful
bookkeeping, not logical proof. No general mapper, executable DSL, full automatic
equivalence solver or complete acceptance architecture is supplied by FRC-0.1.
Future protected use, new vocabulary versions and production qualification each
require their own authority and evidence.

## 10. Equivalence classification and implemented receipt scope

| Classification | Criterion |
| --- | --- |
| Structurally identical | Equal complete canonical serialization, including identities and attribution. |
| Semantically equivalent | Same permitted observable traces over aligned authority/domain/context, including unspecified freedoms; decompositions and IDs may differ. |
| Compatible but incomplete | One omits required constraints of the other without adding incompatible constraints; joint satisfaction is possible. A subset alone does not establish compatibility in arbitrary logic. |
| Materially divergent | Different observable requirements, conditions, frames, issue dispositions or freedoms; record a witness or mark comparison indeterminate. |
| Conflicting | The contracts require incompatible observations on the same admissible input/state; joint satisfaction is impossible there. |

`compare_relations` implements only complete structural equality, exact reviewed
clause-set equality and exact clause subset diagnostics. It retains normative
statement/context/unspecified/issue meaning, ignores author identity and local
obligation IDs for clause comparison, and returns `REFER_TO_REVIEW` when it cannot
decide. It does not implement the general semantic classifications above. The
independent A/B comparison is a separately recorded judgment, not that function's
output. Provider identity never supplies a behavioral definition or approval.

The v0.1 executable receipt is the smaller closed shape
`{contract_commitment, reviewer, outcome, checks, findings}`. The whole-record
commitment binds contract ID/revision/source hash as well. Session isolation,
coverage and limitations are recorded in `reviews.json`; not all the richer
evidence inventory rules in section 7 are mechanically enforced. Receipts are
content-bound cooperative evidence, not signed credentials. This limitation is
part of the PARTIAL result. Mechanical recovery reads recognized V1 requirements
and verifies complete context/ID preservation; retained source statements are
review evidence, not a derivation of prose from V1.
