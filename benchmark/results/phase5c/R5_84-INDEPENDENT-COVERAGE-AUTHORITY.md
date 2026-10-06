# R5.84 — Independent source-to-contract/interface coverage authority

## Decision and central answer

**`R5_84_INDEPENDENT_COVERAGE_AUTHORITY_PARTIAL`**.

The system can require **inspectable, content-bound coverage evidence** rather than
accept a bare completeness assertion. The prospective R5.84 wrapper rejects the
R5.83-style omission/false-attestation attack for all 16 tested coverage classes,
requires bidirectional source justification, checks structural preservation and
routes declared unsupported behavior to a visible halt. It does not establish a
reliable independent production process for extracting **all material source
meaning** or verifying that review evidence is truthful.

The decisive remaining limitation is experimentally visible: a vague source
inventory with a full-text umbrella span, paired with a fresh dishonest review and
caller-pinned admission, can still authorize the **experimental** helper. No
production authority is exposed by this path. Adding evidence fields is a material
improvement over a naked boolean, but does not itself qualify the evidence-producing
reviewer. The requested strong independent-authority claim is therefore not qualified.

**B03_PRISTINE / B03_NOT_EVALUATED / B03_NOT_EXPOSED_TO_LYKOI_DEVELOPMENT**.
All B03 access/activity counters are **zero**. `R5.83-CANDIDATE-1` remains **NOT
ACTIVATED**. Stop after R5.84; no readiness reconsideration or subsequent round begins.

## Deliverables and scope

| Deliverable | Artifact |
| --- | --- |
| Versioned attestation, bidirectional mapping, structural mapping, exclusions, implications, human review and authorization protocol | [SCCA-0.1](../../../docs/source-contract-interface-coverage-v0.1.md) |
| Source inventory specification and independent extraction methodology | [SOI-0.1](../../../docs/source-obligation-inventory-v0.1.md) |
| Pure experimental evidence checker and downstream wrapper | [source_coverage_r5_84.py](../../evaluation/source_coverage_r5_84.py) |
| 23 public synthetic sources and deterministic candidate triples | [sources.json](r5_84/sources.json), [fixtures.py](r5_84/fixtures.py), driver `--corpus` |
| Independent source-only inventory | [independent-soi.json](r5_84/independent-soi.json) |
| Omission/invention/false-attestation/mutation tests and residual negative control | [test_source_coverage_r5_84.py](../../evaluation/test_source_coverage_r5_84.py) |
| Comparison results, B01 inventory/mappings, assertions and reproduction | [qualify.py](r5_84/qualify.py), [README.md](r5_84/README.md) |
| Frozen authored observation summary and protection accounting | [results.json](r5_84/results.json) |
| Remaining readiness blockers, production distinction and final classification | This report |

Worktree started clean. Historical FRC/BDI/adequacy/V1 helpers, compiler/runtime/
schema, requirements, precommitment and benchmark evidence retain their content.
Only prospective experiment code, evidence and project research records are added.
This is coverage-method research, not language/semantic-family expansion, software
implementation, full authoring/verification qualification or a production freeze.

## Evidence model and what is established mechanically

Source identity includes exact text/hash and revision. Source inventory spans
account for all nonwhitespace text, including nonbehavioral material, and retain
conditions, freedoms, uncertainty and dependencies. Separately produced candidates
map SOI items to existing formal obligation IDs or explicit dispositions. Every FRC
obligation needs a source mapping or an approved necessary-implication record; a
quote alone cannot justify invention. Structural maps bind obligation IDs to exact
consumed paths/values/families/observations. Unsupported, reviewer-only or missing
material projections cannot approve structural coverage.

Separate review evidence binds the whole bundle and provides per-item/per-edge
rationales. Separate experimental admission binds inventory, reviewer and review
content. Identity inequality is not isolation; content binding is not semantic truth.
`coverage_complete` is ignored as authority. The wrapper, rather than its caller,
computes whether the old adapter's flag may be true.

Mechanically established: lexical source accountability, references, graph closure,
reverse justification presence, projection value identity, explicit unsupported
scope, evidence binding and approval conjunctions. Independently reviewed meaning
would additionally require truthful, qualified extraction/materiality/fidelity/
observation/exclusion/implication judgments. R5.84 does not collapse the two.

## Source corpus and coverage challenges

The primary corpus has **23** short coordinating-AI-authored human-style sources.
The 16 required corruption classes are filtering, ordering, cardinality, ties,
defaults, omission/null, normalization, persistence, transitions, retries, errors,
failure atomicity, deadlines, identity stability, event ordering and event count.
Seven additional sources exercise explicit freedom/consumer restriction, explicit
unspecified behavior, ambiguity, conflict, cross-clause combination, nonbehavioral
planning text and a conditional cardinality-based exclusion.

Primary same-context bookkeeping gives **15 COVERAGE_APPROVED / 6 structural
unsupported / 1 ambiguous / 1 conflicting**. These are graph-review mechanism
controls, **not 15 independent semantic approvals** or universal recall measurements.
Arithmetic clauses without an applicable existing discovery family remain reviewer-
only, explaining two of the six structural halts. Candidate relations and probe
authorities remain textual experimental capsules; complete finite behavior domains
and exact source entailment are not qualified by those labels. Cardinality and
cross-clause examples retain missing tie authority; failure-only source does not
invent successful durability authority. Coverage approval is separate from adequacy.

| Challenge | Denominator / observed result | Claim supported |
| --- | --- | --- |
| Material FRC removal plus false complete flag | **16/16** COVERAGE_INCOMPLETE; authorization false | Existing inventoried source targets cannot disappear. |
| Same corrupt candidates through legacy naked-flag helpers | **16/16** authorization true | Generalized R5.83 failure, not events-only. No valid approval/grant is claimed. |
| Material interface operation removed with FRC retained | **16/16** COVERAGE_INCOMPLETE; authorization false | Projection paths cannot silently disappear. |
| False EXPLICIT_NON_SEMANTIC exclusions without source consumer restriction | **16/16** rejected; authorization false | Formalizer labels cannot supply exclusion authority. |
| Invented sorting/default/rejection/persistence/tie/retry obligations | **6/6** lack reverse justification; rejected | Unmapped invented obligations detected; dishonest mapped semantic invention is not proved detectable. |
| Same six policies claimed necessary because “good design” | **6/6** unsupported inference class; rejected | Necessary implication is not a generic convention escape hatch. |
| Deadline / identity / event order / event count present | **4/4** STRUCTURAL_SCOPE_UNSUPPORTED → OUTSIDE_ANALYSIS_SCOPE; unauthorized | Material unsupported meaning remains visible; no new discovery support. |
| Durability mechanism control | Coverage approved, adequate, experimental helper true, production false | Positive mechanism control; no real authoring or independent production approval. |
| Vague inventory + freshly counterfeit review/admission | **1/1** experimental helper true, production false | Residual reviewer/extractor truth boundary; requires PARTIAL. |

The unchanged R5.83 synthetic negative control also reproduces: declared events
and unreviewed omission halt; false complete omission/exclusion pass old helpers.
No historical output is overwritten or retrospectively relabeled.

## Mutation, exclusions and implications

Nine enumerated mutations are tested against both the old receipt and fresh
synthetic bookkeeping review: remove FRC obligation, remove structural map, remove
fact, remove observation, misexclude observation, change failure reachability,
append unbound source event, damage source span and add unresolved question.
All deny authorization. An additional **consistently rebound** source extension with
a new public event but no inventory extension fails UNACCOUNTED_SOURCE_TEXT even
with fresh review. Freedom-map deletion, implication-premise deletion, invalid
conjunction conclusion and invariant weakening with old proof also block. Adding a
two-record case invalidates the finite singleton ordering exclusion. Display-only
metadata plus an injected complete flag leave the coverage result identical.
These are separate, overlapping mutation groups, not an inflated aggregate score.

Exclusions distinguish conditional finite irrelevance, explicit consumer restriction,
reviewer-classified irrelevance and unsupported exclusions. Independent source
premises/rationale and a separate review judgment are required. A failed or
undetermined reviewer exclusion judgment blocks despite fresh receipt pinning.
The finite ordering check is conditional on reviewed exhaustive collections; it
does not infer the collection/admission relationship from prose.

Cross-clause “one returned record” plus “every returned record active” supports a
reviewer-derived active-singleton implication with a denial witness. A mechanical
conjunction-elimination check operates only on independently reviewed premise atoms.
It does not prove prose-to-atom truth or arbitrary implication entailment. The same
truth gap applies to fabricated rationale/witness strings. One-to-many and many-to-one
maps pass without 1:1 textual correspondence; equivalence remains semantic review.

## Independence experiment: actual protocol and disagreement

Process B received the public source corpus only, in a fresh same-model context.
It extracted six representative SOIs and published its record before Process A's
candidate code existed. The coordinating process pinned its exact physical digest
**ff124b66301901a9e945338ccad1a354f8e393d8fe9175f06d1fbf3068d29d44** before
reading the publication and creating candidate machinery. This is publication
commitment, not a Git commit, trusted timestamp or independent cryptographic identity.

Process B explicitly disclosed repository guidance from the harness and a narrowly
scoped pre-edit Git status command. Metadata internals were not traced. The workspace
was cooperatively restricted; no enforced source-only sandbox or separate provider
was available/used. All source IDs/texts in the corpus were visible, though only six
were inventoried. Process A could see the committed SOI before candidate creation;
the experiment is one-way source-extractor isolation, not double-blind independence.
Process C's comparisons run in the coordinating context, after both artifacts exist.

| Evidence dimension | Actual evidence |
| --- | --- |
| Same-context development inventories/review | 23 primary capsules, synthetic bookkeeping receipts and tests; not independent. |
| Context-isolated source extraction | **6 sources / 29 items / 9 ambiguity items**, candidate unseen before publication. |
| Context-isolated comparison/final semantic approval | **0**; Process C is coordinating-context. |
| Model-isolated / provider-isolated review | **0 / 0**. |
| Strict-isolation-qualified review | **0**; shared filesystem/cooperative access and metadata deviation disclosed. |
| Independent positive whole-source approvals | **0**. |

Process C retains source-span navigation to candidate IDs, not asserted entailment.
Optional/null input representation, event attribution/observation window, record
universe and consumer dependence, missing active-record cases, bound-to-collection
scope and supplied integer domain raise unresolved interpretation differences.
All **6/6** representative comparisons become **COVERAGE_DISPUTED / unauthorized**.
No majority decision, source-specific exception or candidate completeness claim
resolves them. Not every unknown necessarily needs a product rule; materiality and
the intended review scope themselves require resolution. Conservative dispute is
not evidence of universal ambiguity detection or that the reviewer is always correct.

The human-compatible protocol lets a qualified reviewer inspect the raw source
ledger, candidate, mappings, exclusions, implications, unsupported projections and
disagreements, and reject or approve exact evidence under declared authority.
Human/AI/provider identity does not define behavioral meaning or substitute for
qualified review. A separately isolated AI might perform that role; this round
does not establish its production reliability.

## Downstream integration and production distinction

The prospective wrapper enforces:

**source coverage approved ∧ structural coverage approved ∧ full FRC fidelity
approved ∧ discovery supported ∧ implementation adequate → experimental eligibility**.

Incomplete/disputed/unreviewed/unsupported coverage returns discovery **NOT_RUN**
and implementation authorization false, regardless of supplied bools. Ambiguity
and conflict retain their precise native statuses. Full FRC review remains separate
from coverage. Old helpers remain only as unchanged historical components; direct
legacy invocation is not the R5.84 authority path. Production sole-entrypoint
enforcement is a deployment qualification issue, not established by this wrapper.

**Every production authorization remains false.** Synthetic graph tests cannot
approve actual held-out input. The remaining false-review counterexample concerns
the extraction/reviewer/admission truth boundary, not a bare-boolean bypass. To
qualify the declared bounded process would require independently administered
source-only admission/extraction, verifiable publication/access isolation, truthful
coverage/exclusion/implication review under a declared protocol and unseen-to-
formalizer known-answer challenges that include falsely mapped meaning. Real-human
requirements and independent expert resolution are additional needed reliability
evidence; no universal NLP requirement or arbitrary numerical threshold is asserted.
These are evidence requirements for the existing authority boundary, not automatically
opened new research rounds or added semantic gates.

## Public B01 calibration

Read only already-public B01.md and the R5.80 public candidate. The source-side
calibration inventories eight items: heading, six behavioral clause groups and a
separate default-trigger uncertainty. Exact source text hash remains
`b7b2d714db5cee566e9e55982dd4c4d95d3d57f0c341e04ba1e15c24e9a8e94d`.
“A missing priority still defaults to NORMAL.” occupies characters **[295,339)**,
maps to **B01.O08**, and its uncertainty maps to **B01.I1**, dependent on the
migration/default clauses. Omitted create argument versus absent historical field
remains unresolved. The generic AMBIGUITY disposition, not B01-specific gate logic,
preserves the uncertainty.

Observed **SOURCE_AMBIGUOUS → NEEDS_CLARIFICATION**, discovery **NOT_RUN**, authoring
unauthorized. Removing I1 and falsely converting the source-side ambiguity into a
represented obligation still cannot authorize this path. No default-domain resolution,
implementation or oracle inspection occurs. This is known-issue same-context
calibration, not independent rediscovery, not a repair to historical B01 acceptance.

## Exact blockers if coverage authority were qualified

Coverage qualification alone would not make B03 ready. The remaining R5.83 blockers
would be:

1. **Protected admission / input-generation and containment deployment:** selected
   trusted source/context admission, isolation, formalizer/FRC reviewer deployment
   and independent controlled production review are not qualified. FRC-0.1 currently
   admits PUBLIC/SYNTHETIC provenance only; protected input cannot be mislabeled
   public. Qualifying coverage judgment does not by itself supply that operational
   source admission or authorize source access.
2. **Executable production freeze and enforcement:** complete selected platform,
   dependencies, deployment inputs/identities/tools/limits, exact cross-stage bindings,
   fresh integrity checks and enforced stage halts/first-result/contamination policy
   remain unqualified. The nonactivated R5.83 snapshot records these absences.
3. **Full authoring/external-verification closure:** qualified authoring/controller
   transitions, obligation-linked independent prefrozen oracle construction,
   execution/acceptance evidence linkage, and reliable distinctions between source,
   representation, capability, implementation, verification and infrastructure
   outcomes have not been demonstrated end-to-end. The static runner is not that
   full evaluator.
4. **Conditional representation/analysis boundaries:** any future admitted source
   still needs faithful full unchanged-V1 projection; missing mapping must visibly
   halt as V1_REPRESENTATION_GAP. Required finite adequacy-domain completeness,
   implications, reachability or coupled behavior outside supported scope must halt,
   not be presumed qualified by source coverage. These are conditional boundaries,
   not demands to implement every family or infer anything about B03.
5. **Separate readiness/owner authorization:** no qualified deployment selection or
   coverage result activates R5.83-CANDIDATE-1 automatically. Any reconsideration
   needs separately authorized prospective readiness adjudication before access.

Under the actual R5.84 PARTIAL outcome, **independent source/interface coverage
authority itself also remains an active blocker**. No automatic successor gates or
rounds are created. The four missed discovery families need not be added merely to
change readiness: visible supported-scope refusal is the relevant methodological goal.

## Verification and protected accounting

New tests **21/21** pass; unchanged R5.80/R5.81/R5.82 tests **52/52** pass. Driver
assertions and exact isolated inventory pin pass. See reproduction commands and
authored observation summary; unit-test counts differ from per-class challenge
denominators. No broad protected harness discovery is run. Core **30** inherited;
Phase 5C paused. Historical content is preserved and scoped whitespace checks pass.

All B03 counters **zero**: source access attempts/reads, content-revealing metadata,
formalization, discovery, adequacy, authorization, reservation, packaging, opening,
consumer observation, generation, execution, acceptance and repair. This is scoped
session activity plus inherited pristine status, **not** a protected-ledger inspection.
No source/metadata/content commitment/package/eligibility for B03 is obtained. No
other held-out requirement is read. B02 exposed/indeterminate history is preserved.

**Final: R5_84_INDEPENDENT_COVERAGE_AUTHORITY_PARTIAL. Stop after R5.84.**
