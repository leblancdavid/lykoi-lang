# R5.85 — Production Formalization & Evaluation Architecture

## 1. Decision, scope and evidence

**R5_85_PRODUCTION_ARCHITECTURE_DEFINED** — a prospective, implementable design,
not an implemented production system or a qualification result. This document is
the core architecture reference. The [round report](../benchmark/results/phase5c/R5_85-PRODUCTION-FORMALIZATION-AND-EVALUATION-ARCHITECTURE.md)
records scope, preservation and checks. Stop after R5.85; the roadmap is proposed,
not executed.

Build a **requirements-to-software service** with an AI requirements wizard,
an independent source-analysis worker, a human authority interface, an immutable
artifact store and a deterministic workflow controller. The controller mediates
review, sealing, bounded discovery/adequacy, faithful projection, restricted Lykoi
authorship, compilation and independent external verification. Interpretation is
fallible; authority is explicit; every execution refers to exact approved content.

| Evidence | Architectural lesson retained | Consequence |
| --- | --- | --- |
| [R5.79](../benchmark/results/phase5c/R5_79-REQUIREMENT-FORMALIZATION-BOUNDARY-AND-INDEPENDENT-BENCHMARK-AUTHORITY.md) | Interpretation precedes the trusted language boundary. FRC defines WHAT; Lykoi defines HOW. | No prose interpretation inside compiler or authoring callbacks. |
| [R5.80](../benchmark/results/phase5c/R5_80-REQUIREMENT-FORMALIZATION-QUALIFICATION.md) | Candidates can preserve ambiguity/conflict/neutrality; autonomous production formalization is unqualified. Only 1/9 approved projections had a calibrated complete mapping. | Wizard drafts; approved scope and mapping are separate decisions. |
| [R5.81](../benchmark/results/phase5c/R5_81-IMPLEMENTATION-ADEQUACY-QUALIFICATION.md) | Fidelity approval is not implementation authority. Finite adequacy cannot find omitted decisions by itself. | Separate implementation grant; observable silence is not delegation. |
| [R5.82](../benchmark/results/phase5c/R5_82-BEHAVIORAL-DECISION-DISCOVERY.md) | Supported structural rules are useful, not universally complete; four timing/identity/event decisions were missed. | Preserve supported scope, unknowns and unsupported scope; do not add families here. |
| [R5.83](../benchmark/results/phase5c/R5_83-HELD-OUT-EXPOSURE-READINESS.md) | Useful held-out learning needs visible incompleteness, not semantic completeness. False upstream coverage could omit material scope. | Coverage precedes discovery; frozen execution must enforce halts. |
| [R5.84](../benchmark/results/phase5c/R5_84-INDEPENDENT-COVERAGE-AUTHORITY.md) | Bound inventories and bidirectional maps detect many losses, but a dishonest umbrella inventory/review still passed an experimental helper. | Evidence structure establishes bookkeeping facts, not truthful understanding. AI judgment never self-promotes to production authority. |

Existing [FRC-0.1](formal-requirement-contract-v0.1.md),
[SOI-0.1](source-obligation-inventory-v0.1.md),
[SCCA-0.1](source-contract-interface-coverage-v0.1.md),
[BDI-0.1](behavioral-decision-inventory-v0.1.md),
[adequacy-0.1](implementation-adequacy-v0.1.md) and
[V1](benchmark-document-contract-v1.md) are research interfaces to reuse where
compatible. They are not silently promoted to production APIs. Future authority,
policy, admission and lifecycle envelopes need their own versions. In particular,
FRC-0.1 permits PUBLIC/SYNTHETIC only: protected provenance requires a prospective
compatible representation, never relabeling as PUBLIC. No semantics, V1, historical
results or R5.83 precommitment are amended here.

## 2. Authority model and graph

Authority is a **typed, scoped relationship**, not a scalar confidence score.

| Class | Meaning | Typical output |
| --- | --- | --- |
| Suggestion | Useful information; cannot select required behavior. | Wizard alternatives, implementation proposal. |
| Candidate interpretation | Proposed source meaning awaiting reconciliation/approval. | Draft FRC, unreviewed structural projection. |
| Human-authorized decision | Explicit decision by authenticated requirement owner or declared delegate within scope. | Clarification answer, policy adoption, behavioral delegation. |
| Independently reviewed evidence | Evidence obtained with recorded input/access isolation and inspectable rationale; still fallible. | Committed SOI and reconciled semantic review. |
| Mechanically established fact | Deterministic result within declared scope, conditional on admitted premises. | Hash match, graph closure, finite rule result, compiler validation. |
| Sealed authority | Exact artifact authorized for a named downstream use after required approvals/checks. | FRC seal, implementation grant, verifier-plan seal. |

An artifact may carry several claims of different classes. A hash check is mechanical
even when the meaning it binds is AI-judged. A seal attests authorization, not proof
of correctness. Human approval likewise establishes intent/permission, not semantic
omniscience. Every claim records subject digest, scope, producer, basis, limitations
and intended consumer. A reviewer name or confident rationale is never a grant.

```text
Declared owner/delegation registry
  ├─ source authority + clarification decisions
  ├─ policy authority + explicit feature applicability
  └─ FRC approval / materiality and delegation decisions
          ↑ independent SOI + source/FRC reconciliation evidence
          ↑ mechanical identities, references and issue checks
          ↓
      controller issues FRC seal (WHAT only)
          ↓ reviewed structural coverage + bounded BDI
          ↓ scoped adequacy evidence + faithful V1 approval
      controller issues implementation grant (exact HOW-task scope)
          ↓ restricted author → validated Lykoi → generated software
          ↑ independently approved verification plan, sealed before author starts
      external verifier → observations and scoped satisfaction result
```

The owner may delegate product decisions to a named person/organization through an
explicit scope/expiry record. AI may propose decisions but is not the default owner
or approval principal. Research may appoint an independent benchmark authority;
that appointment cannot be inferred from a reviewer model identity. Controller
service credentials issue grants only from recorded approvals and required checks.
Neither wizard, reviewer nor author can write an approval as the owner or invoke
an alternate unmediated production path. Legacy experimental helpers remain outside
the production entrypoint.

## 3. Concrete components and controller

Use a small service architecture, not a stack of reviewer certificates:

1. **Authority/source service and artifact store:** authenticated owner decisions,
   immutable source revisions, policy versions, dependency manifests, access labels,
   append-only event journal. No overwrite-by-revision or mutable `latest` in a grant.
2. **Requirements workspace:** wizard sessions, issue/obligation ledger, product-level
   questions, human-readable approval diff and separate source-only review worker.
3. **Workflow controller:** deterministic state transitions, dependency and role
   checks, content verification, grant issuance, isolated job dispatch and halts.
4. **Analysis/projection workers:** reviewed structural extraction, unchanged bounded
   BDI/adequacy tools and complete unchanged-V1 projection with fidelity review.
5. **Build workspace:** restricted Lykoi author and deterministic toolchain. Compiler
   credentials cannot approve requirements; author cannot modify toolchain or seals.
6. **Verification workspace:** independently constructed acceptance plan and external
   subprocess executor; software executes without access to verification internals.

Each job request contains run ID, stage, role, allowed input digests, output type,
capability profile, version/freeze identity and budget. Results contain those bindings,
native outcome, findings, output digests and execution receipt. The controller verifies
inputs before dispatch and outputs before admission. Workers cannot nominate a new
approval authority or change their own capability profile.

Journal transitions use an atomic compare-and-append against the expected revision
and state. Dispatch reservations are durable and single-use; crashes record incomplete
jobs rather than guessing success. Ordinary development may explicitly start a new
attempt/revision; a frozen evaluation keeps its first terminal result and follows its
predeclared retry policy. No later stage runs to rescue an earlier failed gate.

## 4. AI requirements wizard and question selection

The wizard accepts exact human messages, permitted context and applicable approved
policies. It extracts candidate obligations, conditions, domains, observations,
freedoms, dependencies and provenance; identifies ambiguity, conflict and absent
behavioral authority; maintains stable IDs; and constructs a candidate FRC. It may
consult structural validators, not language support or hidden expected outputs to
decide intent. Policy lookup is explicit and applicability is recorded.

Its outputs are candidate interpretations and suggestions. It cannot approve its
own draft, turn silence into a default, erase unsupported behavior, or present a
necessary-implication claim as proven without the declared evidence process.

### Question-selection policy

Surface a clarification when all three conditions hold:

1. There are materially different **contractual observations** on a reachable or
   credibly admitted input/state. Provide a concrete distinction where possible.
2. Source, applicable approved policy or reviewed necessary implication supplies
   no authority selecting/deliberately delegating the choice.
3. The choice matters within the declared product/interface scope.

Prioritize decisions blocking multiple obligations, conflicting authority, irreversible
effects, migration/compatibility and the next requested implementation slice. Bundle
related questions; explain the user-visible consequence; offer neutral examples
without treating an offered option as selected. Record the question's affected IDs,
alternatives, witness, authority search and scope rationale. Candidate materiality
itself is AI judgment and can be disputed by independent review.

Do not ask about private algorithms or hypothetical out-of-scope states. Do not
ask recurring questions already answered by applicable policies. A product decision
may explicitly delegate a bounded choice, including variation across calls, with
consumer expectations specified. Merely writing `unspecified` is not delegation.
An explicitly out-of-scope branch can remain open; if the proposed implementation
interface admits it, adequacy must revisit that scope. If a question budget is
exhausted, pause visibly with open issues; never invent answers to finish the wizard.

## 5. Clarification protocol

Clarification is a normal transition, available from source review, structural review,
discovery, adequacy, projection-fidelity review or a discovered contract defect.

Example: “Show me my important tasks.” Candidate obligation O17 preserves the
undefined criterion; issue Q4 asks **“How should a task qualify as important?”**
The owner's answer “Tasks whose assigned priority is HIGH or CRITICAL” becomes a
new authoritative source event, not an untraceable edit to O17. If the answer is
“the urgent ones,” the criterion remains ambiguous and the question is refined.

Each event records question ID/version, affected obligation IDs, exact answer bytes,
respondent/authority scope, timestamp, predecessor source root and status. The
source root binds original messages, ordered clarification transcript, permitted
context and policy selections. Amendments are explicit events; two conflicting
answers coexist as a conflict until the authorized owner explicitly supersedes one.
The latest timestamp alone does not select intent. Questions posed by AI are context,
not behavioral authority; only authorized adopted answers become normative.

On an accepted answer:

1. Create source revision N+1 referencing N and the answer; retain N unchanged.
2. Mark candidate/review jobs for N obsolete for new approval. Their publications
   remain immutable and inspectable.
3. Create revised FRC and mappings. Continuing IDs persist with explicit meaning-change
   lineage; split/merge allocate successor IDs and retire parents; never recycle IDs.
4. Independently inventory the revised source before revealing the revised candidate.
   Reuse prior analysis only as explicitly labeled incremental evidence after that
   commitment; it cannot masquerade as fresh source-only analysis.
5. Reconcile and obtain new approval. Dependency invalidation propagates through every
   descendant seal, grant, build and verification claim for the current target.

Old evidence remains valid as historical evidence of old content. It is **stale for
the new target**, not retroactively false. Default implementation invalidation is
conservative full-descendant invalidation; finer reuse needs checked dependency
closure and a new approval. An already released product remains identified by its
old seal until a new release is approved; it must not be relabeled as satisfying N+1.

For frozen benchmarks, unavailable owner clarification is a visible halt. A later
answer or revision creates separately authorized post-exposure research; it cannot
repair the original frozen first result.

## 6. Project Policy Contract (PPC)

Adopt a prospective **Project Policy Contract** as reusable source authority, not
a collection of assistant conventions. No example policy is adopted by R5.85.

A policy is eligible when the owner intentionally wants the same observable rule
across a declared set of interfaces/features, its applicability conditions are
precise, it does not conceal missing feature-specific authority, and its interaction
with existing data/consumers can be reviewed. ID uniqueness/domain, time encoding,
invalid-input outcomes, atomicity boundaries, ordering defaults, persistence guarantees
and normalization can qualify **if explicitly selected and scoped**. They are not
universal necessities: a pure function needs no persistence policy, and “use UUIDs”
is only a product policy if identifier representation is itself required. Private
engineering choices belong to implementation guidance, not behavioral authority.

A PPC binds policy ID/revision, exact rule, applicable operations/domains, triggers,
exceptions, scope of delegation, source/provenance, owner/delegate, approval/seal,
effective project revision and supersession/migration decision. The wizard records
which rule answered which decision and exposes the resulting product summary.
Policy proposals require owner approval; code, framework defaults and model memory
are not project policies. Policies are reviewed/sealed under the same finite trust
model as feature contracts.

### Precedence

* Declared non-waivable external/project constraints must be explicitly admitted
  as authority. A contradictory feature requirement creates conflict, not a silent
  policy override; only the appropriate authority can resolve it.
* Explicit feature-specific authority overrides a **waivable default policy** for
  that feature. Record the exception and continuing policy scope.
* Applicable approved policies fill otherwise undecided choices.
* General suggestions and conventions have no normative precedence.

Conflicting policies, unclear applicability and contradictory owner decisions halt
for resolution. Do not silently choose the newest or most specific phrase. A policy
change creates a new revision; affected contracts require an explicit adoption or
retention decision and reapproval. Existing sealed contracts pin their prior policy
versions; urgent revocation may block new grants/releases, but never rewrite history.

## 7. Finite independent source review and reconciliation

Use **one independent source-analysis role**, followed by evidence reconciliation
and owner approval. This is not an infinite chain of reviewers reviewing reviewers.

Both wizard and reviewer receive the same committed source/context/policy set.
The reviewer initially receives **no candidate FRC, wizard inventory/rationale,
implementation, support result or external oracle**. It constructs an SOI with its
own stable IDs, spans, conditions, uncertainty, freedoms, dependencies and material
observation scope. It publishes an immutable inventory commitment plus an access
receipt before candidate disclosure. Candidate and SOI commitments are withheld
from the other producer until both are committed. Isolation is a deployment fact
from capabilities/logs, not different AI names; same-model correlated bias is recorded.

After commitment, the review role can receive both artifacts to reconcile. Review
the full source, per-item and reverse FRC mappings, implications, exclusions and
structural projection; retain all disagreements. Source-accounting/fidelity review
and structural-scope review are separately reported. Mechanical checks establish
spans, IDs, graph closure, exact paths/values and review bindings, not entailment.
SOI revisions after disclosure are marked reconciliation amendments, never blind
inventory publications.

| Finding | Required action |
| --- | --- |
| Agreement | Record scoped reviewed evidence. Owner still approves the product meaning; agreement alone issues no seal or implementation grant. |
| Omission | Add candidate obligation/issue with provenance, revise maps, review affected source and whole coverage closure again. |
| Invention | Remove unsupported constraint or ask owner whether to adopt it as new authority; adoption is a source change, not proof it was originally entailed. |
| Ambiguity | Present material alternatives to owner; retain issue until authorized resolution. |
| Unsupported semantic scope | Preserve obligation and unsupported row/channel. Source fidelity may be approved, but structural approval/BDI/implementation grant halt. |
| Material disagreement | Mark disputed, return to clarification or a named human semantic-review role. No majority vote, model confidence or wizard preference can settle it. |
| Mechanical mismatch | Reject stale/malformed evidence; no semantic decision from unusable artifacts. |

The owner views an obligation/product summary, changes, open questions, policy
effects and disagreements, with raw provenance available. Approval must reference
the exact version and scope. A human semantic reviewer can examine disputed mappings;
the owner still decides new behavior. Missing authority is a pause, not a reviewer
invitation to improvise. Routine clerical corrections can revise candidates without
new behavioral choices, but require new bound reconciliation before approval.

### Who reviews the reviewer?

Deterministic reconciliation checks evidence structure; the declared human authority
accepts or rejects the reviewed interpretation and unresolved material judgments.
Independent source extraction makes omissions/inventions inspectable. Public known-answer
challenges, incident analysis and process evaluation measure reviewer reliability;
they are engineering/evaluation evidence, not another per-contract AI authority chain.
If judgment remains uncertain, fail closed or obtain human clarification. There is
no claim to mathematically prove arbitrary natural-language understanding. Correlated
omission, dishonest plausible mappings, owner misunderstanding and shared evaluator
error remain residual risks. Human approval bounds responsibility; it does not erase
those risks or retroactively qualify autonomous formalization.

## 8. FRC lifecycle and seals

```text
DRAFT → REVIEW → APPROVED → SEALED
           ├─ CLARIFICATION → new source/candidate revision → REVIEW
           ├─ REVISION_REQUIRED → new candidate revision → REVIEW
           └─ REJECTED (retain evidence; no downstream authority)
SEALED → superseded/revoked-for-new-use through a new event, never edited
```

REVIEW requires committed independent SOI and candidate plus coherent provenance.
APPROVED requires reconciled source fidelity, inspectable coverage, no active
material ambiguity/conflict/dispute, and explicit owner approval. SEALED requires
the controller to recheck all bindings, approval principal/scope and dependency
versions, then issue a purpose-scoped immutable seal.

An FRC seal binds source root/version, clarification transcript, applicable PPCs,
FRC content/revision, independent SOI, source coverage maps and attestation,
ambiguity/conflict dispositions, owner approval, review/access evidence, structural
projection and its review status, schema/serializer versions and dependency manifest.
If no structural projection can be produced, bind an explicit unsupported result
instead of a fabricated digest. **FRC sealing authorizes WHAT only**: an approved
contract can be sealed with unsupported structural scope and remain unimplementable.
BDI dispatch requires a separate positive structural-coverage receipt for that exact
sealed FRC/projection. If projection later changes, issue a new bundle/seal; do not
mutate the previous binding.

Approval, seal issuance and implementation authorization are separate journal events.
A seal is not a boolean field that an AI can set. Source/policy/contract/structural
change invalidates current descendant eligibility via dependency closure. Revocations
are checked at dispatch and release; already running jobs cannot publish newly
authorized outputs under revoked inputs. Their observations remain historical.

## 9. Artifact identity and content binding

Use typed immutable artifact identities: `(type, schema_version, serializer_version,
digest_algorithm, digest)`. SHA-256 is the initial content digest. Raw source,
attachments, transcripts, programs and generated bytes bind exact bytes. Preserve
source-text UTF-8 identity separately from original file bytes; any transcription/
newline conversion is an explicit relationship, never hidden normalization.

Structured artifacts use a versioned canonical JSON serializer (reuse FRC-0.1's
sorted keys, array order, compact UTF-8, no final newline, no NaN/Infinity). Future
implementation must reject duplicate keys and ambiguous/unsupported numeric forms
and establish conformance vectors rather than assume all encoders agree. Binding
envelopes include type/version so identical bytes cannot substitute an unrelated
artifact role. Digests prove identity, not meaning, signer authority or secrecy.

| Artifact | Required binding |
| --- | --- |
| Human source root | Exact message/attachment identities, admitted context, owner/scope and source revision. |
| Clarification transcript | Ordered question/answer events, predecessor root, respondent authority and supersession events. |
| PPC set | Exact adopted policy versions, approvals, exceptions and applicability map. |
| FRC | Full normative content, domains/freedoms/issues, lineage and source-root references. |
| SOI | Exact independent inventory, source/PPC root, extractor configuration and pre-disclosure publication/access receipt. |
| Coverage evidence | Both inventories/FRC, forward/reverse maps, dispositions, implications/exclusions, review judgments and scope. |
| Structural projection | FRC seal, all facts/channels/domains/authority plus exact maps and fidelity/scope receipt. |
| BDI | Same FRC/projection/coverage identities, unchanged discovery rule-set identity, entries/exclusions/unknowns and evidence. |
| Adequacy result | FRC seal, structural receipt, BDI, authority map, reviewed finite-domain/scope evidence and checker version. |
| V1 projection | Complete application/configuration/obligations, full obligation map, FRC/adequacy inputs, fidelity approval and normalized V1 identity. |
| Implementation grant | All preceding authority, exact permitted author input, baseline/context, toolchain/freeze, purpose and dispatch scope. |
| Lykoi input | Exact canonical model bytes and schema/language version; implementation mapping and grant separate. |
| Generated artifact | Exact file inventory/bytes, input model, compiler/backend/runtime/dependency configuration and generation manifest. |
| Verification target/result | Exact executable/package/runtime environment, FRC seal, verifier-plan seal, fixtures/observations and executor/freeze identity. |

Consumers fetch by digest, recompute on use, and compare every dependency to the
grant. Release verifies the actual installed artifact equals the verified target.
Opaque IDs are locators, not commitments. No approval of `latest`, filenames or
matching obligation IDs substitutes for content. Authentication/authorization
comes from the authority service and auditable session/service identity; signatures
may support cross-organization exchange, but a self-signed AI review is not authority.
Protected digests/logs stay in the controller's restricted store: hashes of small
requirements can reveal content through guessing and must not be public by default.

## 10. Discovery, adequacy, V1 and implementation grant

### Behavioral decision discovery

Run only after source/FRC coverage is accepted and exact structural projection is
independently reviewed as supported. Reuse R5.82's **15 families** and two finite
implication mechanisms unchanged: ordering, selection, cardinality, ties, optional
inputs, nullable predicates, default trigger domain, normalization, collisions,
invalid inputs, duplicates, persistence, transitions, retries, failure atomicity.
Finite maxima/lowercase reasoning remains conditional on reviewed exhaustive domains.

BDI separates supported decisions, authorized/delegated choices, missing authority,
exclusions and unknown/unsupported scope. Deadline, identity and event families
remain unsupported; arbitrary traces, concurrency and coupled choices cannot be
declared covered by the existing profile. Missing semantic annotations or uncertain
reachability halt; an empty supported inventory cannot certify arbitrary scope.
Discovery does not decide intent. Newly found missing authority returns upstream.

### Implementation adequacy

Consume the content-bound FRC seal, coverage/structural receipts, BDI and explicit
decision-authority map. Check that relevant discovered decisions have determined
or deliberately delegated authority, consistent finite allowed sets, authorized
observation scope, no material conflict and no ignored unsupported analysis. Probe
labels are not automatically exhaustive alternatives. Reviewed domain completeness
and independence/coupling assumptions remain judgment claims.

Unresolved implementation-scope ambiguity, missing authority or unsupported scope
blocks. Ambiguity outside a deliberately excluded/nonimplemented scope may be
preserved only with explicit scope authority; it cannot license an admitted branch.
Native outcomes remain adequate/underspecified/clarification/conflict/outside scope.
An adequate result is conditional evidence, not proof of every possible decision.

### Faithful V1 projection

Only approved, sealed and adequate input proceeds to complete unchanged-V1 mapping.
A separate fidelity review binds the whole application/configuration/obligations
and every FRC ID, including clauses represented inside components. The deterministic
adapter establishes normalization/identity, not semantic fidelity.

**A valid FRC need not be representable by V1.** Missing complete qualified mapping
returns V1_REPRESENTATION_GAP, with unmapped IDs and no executable author package.
Keep the original contract intact. Distinguish missing mapper from demonstrated
interface impossibility; neither is automatically a Lykoi capability gap.

The controller issues an **implementation grant** only when sealed source fidelity,
source/structural coverage, supported BDI, adequate scope, full faithful V1 and a
ready sealed independent verification plan all bind the same target. This separates
permission to choose HOW from FRC authority to describe WHAT.

## 11. Lykoi authoring boundary

The author receives an **Authoring Bundle**: the implementation grant, complete
faithful V1 behavioral representation, public interface/domain/observation details,
resolved decision-authority and allowed-freedom summary, stable obligation IDs,
required preservation/baseline model context, frozen Lykoi documentation/tools and
output protocol. Any summary transformation is itself fidelity-bound. If V1 cannot
carry the necessary behavioral meaning, halt rather than send prose as a back door.

Default access: no original human prose, clarification transcripts, rejected
interpretations, source-only inventory/rationales, benchmark identity, hidden oracle
or external expected outputs. A developer-visible diagnostic uses obligation IDs
and sealed meaning, not extra source. Ordinary public development can optionally
expose provenance for explanation outside the author worker; doing so does not
authorize reinterpretation, and must be labeled as reduced information isolation.
Protected evaluation uses the restricted default, including history/side-channel
isolation. Public interface names necessarily reveal some meaning; least information
does not mean an uninformative contract.

The author composes HOW and may make private engineering choices within freedom.
It cannot resolve a newly discovered observable ambiguity. It reports that issue
to the controller for upstream revision; current grant halts. A capability claim
needs affirmative frozen-language evidence; a failing test alone proves no gap.
Validator/lowerer use unchanged semantics; generated code is disposable output and
never hand-edited. Backend/toolchain defects and composition errors remain distinct.

## 12. Independent external verification

The question is **“Does this software satisfy the sealed behavioral contract?”**
Four separate results are reported:

* Compilation success: valid model accepted and lowered under the pinned toolchain.
* Runtime success: process executes without an observed execution failure.
* Behavioral correctness: observed inputs/state/effects match required relations.
* Contract satisfaction: all required obligations and authorized observation
  freedoms are covered by the declared independent verification scope, with results
  and limitations. Finite passing tests are evidence, not universal proof.

Split verifier **planning** from execution. Before the author begins, a separate
verification role receives the sealed FRC, approved interface/domain/observation
contract, decisions/freedoms and applicable policy meaning. It may inspect admitted
source/provenance to audit intent preservation if independently authorized; any
discovered discrepancy returns upstream, never creates acceptance behavior absent
from the seal. It receives no author implementation or author-chosen tests while
defining acceptance. The author receives the behavioral contract, not hidden cases.

The plan binds obligation → case/property/trace relationships, admitted initial states,
environmental assumptions, input classes/boundaries, state/failure/restart/regression
observations, exact expected relations and delegated freedoms. It explicitly declares
unobservable/unsupported obligations. Review the plan against the contract and obtain
declared verification-authority approval; this is a different artifact task within
the finite role model, not a reviewer-of-reviewer chain. Missing material coverage or
unsupported observations block implementation dispatch/readiness for that target.
Seal the plan before author dispatch. Changes require a new plan/version and clear
attempt provenance; hidden post-implementation acceptance criteria cannot be adopted.

The executor later receives exact generated software/package, sealed plan/FRC,
pinned runtime/adapters and fixture/environment inventory. Execute through public
subprocess interfaces in fresh state, without importing implementation internals
as the oracle. Software cannot read test definitions/expected data or emit authority.
Capture inputs, outputs, exit status, state/effects and per-obligation findings.
Delegated ordering is not tested as exact sequence unless the contract requires it.

Mismatch yields implementation failure when supported capability is established.
Verifier crash, invalid oracle, missing observation or uncovered material obligation
yields verification failure/inconclusive, never success. Controller/binding drift
is infrastructure failure. Verifier bugs/correlated interpretations remain residual
risk; public adversarial software mutants and known-answer checks exercise the
verifier independently. Benchmark first results remain immutable; ordinary product
repair starts another explicitly bound attempt without rewriting prior observations.

## 13. Protected-source admission and containment design

This section designs eventual held-out use only. It authorizes no protected access.
Use an independent source custodian with encrypted/restricted source storage and
opaque resource handles. **Before admission**, owner authority, selected executable
freeze, capability profiles, compatible provenance representation and access ledger
must exist and pass public rehearsal. Do not enumerate protected filenames/content
metadata to establish readiness.

Admission is a custodian-mediated, purpose-scoped reservation/opening into isolated
interpretation workers. Only wizard/formalizer, source-only reviewer, declared human
source authority and separately authorized verifier-planning role may read raw source.
Reconciliation sees source/candidate only after commitment. Projection/analysis
workers get approved formal artifacts as needed. Lykoi author, compiler-development
workspace, general research agents and publisher may not read raw protected material,
transcripts, rejected drafts or oracle expectations. The verifier executor sees the
oracle/target in its own compartment; the SUT and author do not.

Require separate OS identities/containers or VMs, explicit read-only artifact mounts,
no repository/Git history mount, deny-by-default filesystem/network/tool/credential
access, confined descendants, and mediated artifact egress. A prompt saying “do not
read” and a shared working tree are insufficient. Model calls must use declared
provider retention/training settings or an isolated local deployment. Unknown retention
or cross-session memory is a declared unresolved containment condition, not ignored.

The controller logs attempted and granted reads, readers/job identities, opaque
resource IDs, grants, timing, output labels and denied operations durably. Raw audit
logs/transcripts and derived FRC/SOI/test data remain protected; only approved
non-content-revealing summaries leave the compartment. Handoffs are exact sealed
artifacts through allowlisted channels; they are not automatically safe because JSON
or hashed. Approved contract disclosure to an author is itself authorized development
exposure and permanently accounted, even without original prose.

Track separate monotone states:

```text
source custody: UNOPENED → AUTHORIZED_PREPARATION → PREPARED_SEALED
development knowledge: UNEXPOSED → AUTHORIZED_DERIVED_EXPOSURE
integrity: CLEAN → CONTAMINATED (irreversible for this held-out attempt)
run: PREFLIGHT → RESERVED → OPENED → terminal result / INCOMPLETE
```

Preparation access is logged separately from development exposure; it does not
pretend no one read the source. Unauthorized access, oracle leakage, source-based
tool changes, undeclared readers or component drift quarantine outputs and halt.
No deletion/reseal/reset restores pristine status. Custodian opening and derived
author handoff are distinct grants; static-runner opening authority alone grants
neither raw interpretation nor full software execution. Reuse existing runner
primitives only where scopes actually match; do not accumulate successor authorities.

## 14. Executable production freeze

A prospective **Run Manifest** pins the deployment, not merely a prose protocol:

* component/source/package identities and dependency closure; schema and canonical
  serializer versions; all authority/role/state-transition policies;
* prompts, system/tool instructions and admitted context templates; model/provider
  identifiers, configuration, sampling/tool budgets and declared memory/retention;
* deterministic analysis/projection/compiler tools, platform/runtime/adapters and
  relevant environment configuration;
* unchanged Lykoi semantic version, V1 version, discovery families/finite mechanisms,
  adequacy profiles, verification rules and failure taxonomy;
* isolation profiles, permissible readers/handoffs, journal/first-result policy,
  retry/time limits and selected public rehearsal evidence.

Seal the manifest before protected admission. It specifies interfaces and acceptance
construction procedure; requirement-specific FRC and verifier plan are later bound
under that frozen procedure before implementation. Their content is not falsely
claimed known before source interpretation.

The controller recomputes admitted component identities at startup and each dispatch,
verifies actual worker/launch configuration, permits only pinned executables/tool
closures, and checks target/environment identities before and after verification.
Missing pins, undeclared dependencies, schema mismatch and drift block launch or
invalidate the run; no silent version fallback. Component changes require a new
manifest/run identity. After exposure, changes are post-exposure research, preserving
the original first result. Hosted providers may not guarantee immutable weights:
record that limitation, require available deployment identity evidence and reject
undeclared alias switching. A seed and prompt hash do not prove AI reproducibility.
This design freezes configuration/evidence and enforces known identities, not
identical stochastic outputs across runs.

## 15. End-to-end artifact graph and edge contracts

```text
Owner/delegations ──→ Human Source vN ←── Clarifications vN
Approved PPC set ──────────────────────────┤
                                          ├─→ Candidate FRC (wizard committed)
                                          └─→ Independent SOI (blind committed)
Candidate FRC ↔ Independent SOI → Reconciliation / Coverage Evidence
                         └─ disagreement → Clarification → vN+1 → new review
Coverage + owner approval → Approved FRC → FRC Seal
               Structural Projection + review ──┘
FRC Seal + positive Structural Coverage → BDI → Adequacy Result
FRC Seal + Adequacy → Full V1 Projection + Fidelity Receipt
FRC Seal ──→ Independent Verification Plan + Plan Seal
V1 + Adequacy + Plan Seal + Run Manifest → Implementation Grant / Authoring Bundle
→ Lykoi Input → Validation/Lowering → Generated Software / Build Manifest
Generated target + Plan Seal → External Observations / Verification Result
→ Release identity (or visible terminal halt)
```

All edges below bind typed digests and run/revision identity; no edge trusts an
unbound locator. Authority classes abbreviate §2: **H** human-authorized,
**C** candidate, **E** independently reviewed evidence, **M** mechanical,
**S** sealed. A producer's output class is not automatically its consumer's grant.

| Edge/artifact | Producer → consumer | Authority / exact binding | Failure behavior |
| --- | --- | --- | --- |
| Source/context | Owner/source service → wizard and blind reviewer | H; original bytes, source revision, declared scope/delegations | Missing admission/authority halts before read. |
| Clarification | Owner UI → source service → wizard/reviewer | H; question, answer, predecessor/new root | Ambiguous/conflicting answer remains open; invalidate descendants. |
| Policy selection | Policy authority/store → wizard/reviewer | H/S; policy approvals/versions, applicability/exceptions | Stale/conflicting/unclear policy returns clarification. |
| Candidate FRC | Wizard → committed artifact store → reconciler | C; source/PPC root, complete FRC revision | Malformed/unsupported expression blocks review approval. |
| Independent SOI | Source-only worker → store → reconciler | E after isolation checks; source root, SOI digest, publication/access receipt | Premature candidate access or uncommitted inventory invalidates independence. |
| Bidirectional reconciliation | Reviewer/reconciler → owner/controller | E + M closure; both commitments, all maps/issues/judgments | Omission/invention/dispute routes revision/clarification; no grant. |
| Product approval | Owner/delegate → controller | H; exact FRC/evidence and authority scope | Missing/unauthorized approval cannot seal. |
| Structural projection/review | Projection worker + review role → sealer/discovery | C then E/M; FRC, exact paths/values/domains/channels, scope receipt | Unsupported remains visible; may bind to WHAT seal but cannot dispatch BDI. |
| FRC seal | Controller → discovery, adequacy, projector, verifier planner | S; §8 complete bundle and approval | Binding/revocation issue halts all new downstream use. |
| BDI | Pinned R5.82 worker → adequacy | M conditional on E premises; FRC/projection/coverage and rule set | Unknown/unsupported/unreviewed scope blocks adequacy approval. |
| Adequacy | Scoped checker/review role → V1 projector/grant issuer | M + E; BDI, finite domains, authority map and exact upstream seals | Conflict/ambiguity/outside scope/missing authority halts. |
| Complete V1/fidelity | Projector + independent fidelity review → controller/author bundle | E/M; FRC/adequacy, whole components/map/document/normalized identity | Missing full mapping halts without weakened author package. |
| Verification plan | Independent planner + verification authority → controller/executor | E/S; FRC, cases/properties, coverage/freedoms, frozen rules | Missing material observation/coverage blocks author dispatch. |
| Run Manifest | Deployment authority/controller → every worker | S/M; exact selected components/configuration/protocol | Mismatch/drift denies dispatch or invalidates run. |
| Implementation grant/bundle | Controller → isolated author | S; V1, adequacy, plan seal, baseline, toolchain and permitted scope | Any missing conjunct denies author access/dispatch. |
| Lykoi model/map | Author → compiler controller | Candidate implementation; exact model/grant and obligation mapping | Unauthorized behavior/scope or unsupported capability halts; no source reinterpretation. |
| Build manifest/software | Deterministic compiler → verifier executor | M within compiler scope; model/toolchain/runtime and exact generated files | Invalid model/lowering/tool failure blocks execution; diagnose cause. |
| Target handoff | Build store/controller → isolated executor | S dispatch + M identity; executable/package/environment | Different executed bytes are infrastructure failure. |
| External observations/result | Independent executor → owner/release controller | M observations + E scoped satisfaction; target/plan/FRC/run | Mismatch, invalid verifier or incomplete coverage prevents release success. |
| Release handoff | Release controller → deployment/user | S; actual deployed digest equals verified target and approved scope | Drift/revocation denies release; new build requires new verification. |

## 16. Core trust-boundary table

“Trusted inputs” means admitted authority for a specific purpose, not presumed
truth of every statement. All AI-generated semantic judgments remain fallible.

| Component | Trusted inputs | Untrusted inputs | Output / authority | Isolation | Mechanical checks | Human involvement | Failure result |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Source/authority service | Authenticated scoped owner decisions | Unattributed messages, AI answers | Source roots/decisions H | Protected custody, separate credentials | Identity, revision, role/scope, exact bytes | Owner and delegation administrator | Admission halt |
| Policy service | Approved policy decisions | Suggested defaults, stale applicability | PPC S | Owner write access only | Versions, approvals, adopted set | Approve/override/revoke policies | Policy conflict/clarification |
| Wizard | Admitted source/PPC authority | Its interpretations, unapproved assumptions | FRC/questions C/suggestion | No support/oracle; protected compartment where needed | Schema, IDs, source anchors | Product answers | Draft/issues, no authority |
| Blind source reviewer | Same source/PPC set | Its own extraction; no candidate initially | SOI E | Separate context/process/access profile; commitment barrier | Spans, bindings, access/publication | Human reviewer on disputes | Incomplete/disputed review |
| Reconciliation/review | Committed source and authority decisions | Candidate/SOI/mappings/implications | Review E, closure M | No implementation/support/oracle | Bidirectional closure, exact values, evidence bindings | Owner meaning approval; semantic dispute resolution | Revision/clarification/unsupported |
| Sealer/controller | Authenticated approval plus required receipts | AI labels, caller completeness bools | Purpose-scoped S grants | Separate service keys and sole dispatch path | Dependency digests, transitions, roles, revocation | Explicit approval principal | Denied/stale grant |
| Structural/BDI worker | Sealed FRC and reviewed supported projection | Annotation truth and missing scope | BDI M conditional on E | Read-only pinned analysis; no raw source needed | Rule firing, finite proofs, unknown propagation | Review scope/premises, clarify new authority | Outside analysis scope |
| Adequacy worker | Bound seals/BDI/authority map | Exhaustiveness/independence assumptions | Scoped adequacy M + E | No authority edits; read-only profile | Authority intersections, scope/unknowns | Authorize decisions/delegations; review domains | Underspecified/conflict/unsupported |
| V1 projector/reviewer | Adequate sealed contract | Candidate mapping fidelity | V1 E/M | Independent fidelity role; no support-driven choices | Full ID/component map, normalized identity | Resolve fidelity disputes, not fit V1 | Representation gap |
| Lykoi author | Sealed restricted author bundle | Its proposed implementation | Model candidate HOW | No source/history/hidden oracle or toolchain writes | Grant/tool/output scope | Upstream issue referral | Capability evidence/implementation halt |
| Compiler/lowerer | Valid exact model, pinned semantics | Model before validation | Generated bytes/manifest M | Read-only toolchain; confined resources | Schema, validator, effects/authority, generation bindings | None per valid build | Validation/lowering/tool failure |
| Verifier planner | Sealed WHAT and observation freedoms | Its tests/expected interpretation | Plan E then S | Separate from author; plan before code | Obligation map, versions, plan seal | Declared verification authority; owner on semantic defect | Verification not ready |
| Verifier executor | Exact sealed plan and target | Executable behavior, fixtures before validation | Observations M; scoped result E | External process, fresh state, oracle hidden from SUT | Target/runtime identity, expected relations, completeness | Review inconclusive result/defect | Implementation/verification/infrastructure failure |
| Custodian/freeze launcher | Approved admission/run manifest | Worker requests, paths, model aliases | Access/execution receipts M | OS-enforced mounts/network/descendants | Allowlist, pins, single-use grants, logs | Separate protected-access authorization | Quarantine/contamination |

## 17. Threat and failure model

| Failure | Detection/containment control | Residual risk |
| --- | --- | --- |
| Formalizer omission | Independent SOI, forward mapping, owner summary, unsupported rows | Both analyses/owner may miss the same proposition. |
| Formalizer invention | Reverse justification, implication review, explicit adoption as source change | Plausible dishonest mapping can evade semantic review. |
| Reviewer omission | Separate wizard extraction, source accountability, owner review/public challenges | Lexical coverage cannot establish proposition coverage. |
| Reviewer dishonesty | Restricted credentials, inspectable per-edge evidence, owner approval, audit provenance | Dishonest semantic rationales are not mechanically disproved. |
| Correlated reviewer/formalizer error | Blind commitments, separate contexts, declared model diversity where available, human decisions | Same language biases/shared training can persist across providers. |
| Ambiguous human answer | Preserve answer as source, material-alternative witness, repeat targeted clarification | AI or owner may not recognize ambiguity. |
| Conflicting human answers | Explicit supersession and scope, no automatic last-write meaning | Hidden stakeholder conflicts remain possible. |
| Stale project policy | Pinned versions, adoption/revocation checks, applicability/exception map | Incorrect policy applicability remains judgment. |
| Incorrect structural projection | Full FRC/path/value/observation mapping and separate fidelity/scope review | Correct paths may encode wrong meaning or omit an unrecognized channel. |
| Unsupported BDI family | Explicit unsupported/UNKNOWN, no adequacy/grant | Upstream failure to recognize scope can still conceal it. |
| False adequacy | Bound BDI/authority, reviewed domains/coupling, conservative outside-scope result | Omitted decisions or false exhaustiveness can defeat finite checks. |
| V1 weakening | Whole-contract fidelity/map, no partial author package, representation-gap halt | Reviewer may misunderstand equivalence; hashes do not prove it. |
| Lykoi capability gap | Frozen vocabulary, affirmative gap evidence, no semantic extension/contract weakening | Distinguishing unknown composition from impossibility may be inconclusive. |
| Implementation bug | Validator plus independent prefrozen external state/behavior checks | Finite cases miss behaviors; compiler/runtime can have bugs too. |
| Verifier bug | Independent plan approval, public known-answer/mutant checks, raw observation preservation | Oracle/interpreter and owner may share an incorrect expectation. |
| Artifact/version mismatch | Typed digests, recomputation at dispatch/execution/release, dependency graph | Compromised controller/store/keys or undeclared provider change is outside a hash guarantee. |
| Protected-source leakage | Custodian/OS isolation, least-information bundles, no history mounts, audited egress, irreversible contamination | Provider retention, human disclosure and covert semantic channels need explicit containment assumptions. |
| Crash/timeout/replay | Atomic journal reservations, incomplete terminal recording, scoped retries | Partial external effects need adapter/environment containment and cleanup evidence. |
| Gate bypass/role spoofing | Sole controller dispatch, separate credentials, authenticated scoped approvals | A malicious platform administrator remains a trusted-computing-base risk. |
| Acceptance criteria chosen after code | Independent plan seal before author dispatch | A prematurely biased planner or later undisclosed plan edit remains an integrity/process risk. |

Fail closed means **deny current downstream authorization**, not “prove which AI
is wrong.” Findings retain uncertainty. With trustworthy bindings, native precedence
is conflict → ambiguity → unsupported analysis → missing authority → adequate.
Binding/integrity failure makes semantic evidence unusable and halts first. The
earliest failed stage supplies the terminal stage/category; all known findings and
NOT_RUN descendants remain recorded. Use R5.83's source/representation/capability/
implementation/verification/infrastructure distinctions prospectively without
rewriting its freeze or historic result. No semantic gap is inferred merely from
a broken pipeline. Product status always states scope and verification limitations.

## 18. Normal-user experience

**User:** “Build a task manager where I can assign priorities.”

**Wizard:** “Should tasks without an assigned priority use a default?”

**User:** “Yes, NORMAL.”

**Wizard:** “Should that default also apply when loading older tasks that do not
contain a priority field?”

**User:** “Yes.”

The wizard records separate creation and legacy-loading authority. It checks
applicable approved policies rather than asking about every possible storage/time/ID
choice. Independent review may discover that allowed priority values are still
undefined; the wizard asks that product question too. These are invented product
messages, not a resolution of historical public B01.

The user sees a concise summary: allowed values, NORMAL on creation omission and
old-field absence, preservation of existing priorities, applicable policy effects,
consumer-visible behavior and any unresolved question. “Approve this version” is
an explicit scoped decision. Internally the system binds provenance, reconciles
coverage and seals WHAT. It may say “I need a decision about listing order” if
discovery finds missing authority; or “This requirement cannot be faithfully
represented by the current input interface” on a projection halt.

On a supported route, the system builds and independently verifies, then reports
what was checked and any limitations. Later product changes show a behavioral diff
and focused questions, reusing approved applicable policies. Normal users do not
edit BDI schemas, attestations, hashes or obligation maps; expandable provenance
serves experts/auditors without burdening product decisions. An approval button
cannot hide active material questions or label unverified software complete.

## 19. Product, research and benchmark responsibilities

| Layer | Components |
| --- | --- |
| General Lykoi product | Wizard, clarification/PPC/source authority, finite independent review, FRC lifecycle, artifact store/controller, discovery/adequacy, faithful current interface, restricted authoring, compiler, external verification, release identity. |
| Research/qualification | Public real-human/known-answer challenges, reviewer reliability and correlated-error studies, discovery/adequacy profile evaluation, verifier mutants, versioned failure evidence and public end-to-end rehearsal. These measure the system; they are not extra runtime approval chains. |
| Held-out containment | Independent custodian, protected provenance, locked deployment/freeze, one-time access/exposure journal, source/oracle compartments, immutable first result and contamination accounting. |

Ordinary development supports iterative human collaboration and repairs as new
versions. Frozen benchmarks impose prefrozen attempts and irreversible exposure
accounting. B03 is one eventual validation mechanism, not the architecture's domain
or a reason to add task-specific semantics. Unsupported public rehearsal cases
should halt intelligibly rather than be removed from the denominator.

## 20. Minimal implementation roadmap — proposal only

Four meaningful engineering stages are sufficient; do not execute them in R5.85.

| Stage | Build | Completion evidence |
| --- | --- | --- |
| 1. Authority/artifact controller | Typed identities/canonical serializer, authenticated scoped approvals, dependency DAG, immutable journal, purpose-scoped seals/grants and invalidation. Version lifecycle/PPC/protected-admission envelopes separately from historical experimental schemas. | Public artifact-substitution, stale approval, role spoof, revision race, revocation and crash/replay challenges visibly deny dispatch; approved exact-content lifecycle reloads and reproduces mechanical identities. |
| 2. Human-facing requirements workspace | Wizard, targeted question loop, policy selection/precedence, independent source-only worker/dual commitment, reconciliation, source/FRC/structural review and approval UI. Integrate existing unchanged BDI/adequacy/V1 profiles with visible refusal. | Ordinary human examples complete approval; ambiguous/conflicting/policy/omission/invention/false-mapping/unsupported examples preserve evidence and halt or revise. Access receipts establish actual blindness. No autonomous authority claim from agreement. At least a complete public supported contract traverses all existing analysis/projection boundaries faithfully. |
| 3. Isolated build and independent evaluation | Restricted author bundle, sole grant dispatch, pinned compiler/build manifest, verifier plan constructed/sealed before authoring, external subprocess observations and release binding. Implement executable manifest and capability sandbox using public stand-ins. | Public supported source→clarification→review→seal→BDI→adequacy→V1→author→software→external result executes end to end. Deliberate wrong implementation, verifier crash, target swap, hidden-oracle access and component drift give distinct visible outcomes; no failed upstream gate dispatches author. |
| 4. End-to-end public rehearsal | Freeze one actual deployment and run public known-answer/human scenarios and protected **synthetic** stand-ins from admission through terminal reporting; measure UX, omissions, unsupported halts, reliability and costs. | Inspectable complete run manifests/journals, independent expected outcomes, per-obligation observations, real isolation/egress witnesses and permanent first-result/contamination behavior. Retain failures and limitations; scope-specific reliability acceptance is decided before any future held-out access. |

This is the shortest credible path to a public rehearsal: reuse bounded tools,
build missing authority/lifecycle and operational closure, and demonstrate the
whole path. No new discovery families or universal requirements calculus is needed
for a deliberately supported public example. At stage 4, propose a separate readiness
decision if warranted; no automatic B03 authority, new freeze activation or future
research round is created by this roadmap. A public rehearsal is engineering
evidence, not sufficient by definition for held-out readiness.

## 21. Remaining unknowns

### Must resolve before implementation

* Select the accountable product approval/verification principals and concrete
  authentication/delegation mechanism. The architecture fixes explicit human authority;
  an implementer must not leave owner approval as caller-supplied text.
* Select the initial public deployment/OS isolation mechanism and artifact/journal
  persistence boundary, and version production envelopes compatible with the reused
  research interfaces. The current PUBLIC/SYNTHETIC restriction must remain explicit.
* Define the first rehearsal's supported interface/application scope and independent
  expected-behavior ownership. Do not promise arbitrary prose coverage as the MVP.

These are engineering selections, not invitations for new conceptual gate rounds.

### Can resolve during implementation

* Canonical encoding conformance/numeric bounds, atomic storage details, revocation
  delivery and crash cleanup; test them against the chosen platform.
* Question ranking/batching and owner-summary usability, policy applicability UI,
  and cost/latency of source-only review.
* Exact restricted author-bundle shape and the concrete complete public V1 mapping;
  retain fidelity/representation halts rather than relax V1.
* Verification plan format, fixture/adaptor observation mechanics and public mutant
  corpus; minimal telemetry versus restricted detailed audit retention.
* Conservative full invalidation initially; fine-grained reviewed evidence reuse
  can be evaluated later without blocking a first working implementation.

### Must resolve before B03 exposure

* Demonstrate independently administered source access, protected-compatible provenance,
  enforced reader/egress/provider containment and reliable exposure/access accounting
  using public/synthetic stand-ins only.
* Select/freeze the actual deployment/configuration and verify enforced bindings,
  stage halts, first-result rules and complete authoring/external verification closure.
* Decide the declared process's reliability/acceptance criteria using independently
  administered real-human and known-answer challenges, including false semantic
  mappings/exclusions and unsupported scope. R5.84 supplies no qualified positive
  production authority and no numerical threshold to inherit.
* Declare benchmark clarification policy and independent behavioral/oracle authority;
  any unresolved original requirement must halt rather than be changed to pass.
* Obtain separately authorized prospective readiness adjudication and explicit owner
  access/run authorization. Conditional V1/analysis gaps remain legitimate halts;
  do not inspect B03 to select components or prejudge representability.

### Long-term research questions

* How reliably do different AI/human processes understand arbitrary intent, and what
  correlated-error rates survive blind review and owner approval?
* Which broader formal relation/proof systems or discovery profiles reduce judgment
  without importing implementation choices into WHAT?
* What verification evidence supports stronger-than-finite contract satisfaction,
  especially environmental effects, concurrency and temporal behavior?
* How far can change-local evidence reuse, more general language composition and
  multi-provider reproducibility scale while preserving authority and usability?

These questions do not all become immediate gates. The initial system explicitly
supports bounded scopes and visible refusals.

## 22. R5.85 protection and stop

**B03_PRISTINE / B03_NOT_EVALUATED /
B03_NOT_EXPOSED_TO_LYKOI_DEVELOPMENT** remain true by inherited status and scoped
session accounting. B03 source attempts/reads, content-revealing metadata access,
formalization, review, discovery, adequacy, authorization, reservation, packaging,
opening, consumer observation, generation, execution, acceptance and repair are all
**zero**. No protected ledger/content/hash inspection was performed to assert this.
No B03 inference, commitment, package or eligibility is created.
**R5.83-CANDIDATE-1 remains unactivated**. R5.80–R5.84 retain their original outcomes;
core **30** inherited, semantics/V1 unchanged and Phase 5C paused. No roadmap work
or next round starts.

## 23. Final answers

1. **What exact system are we proposing to build?** A human-facing AI requirements
   wizard backed by versioned source/policies, blind independent source review,
   owner clarification/approval, an immutable artifact and authority controller,
   bounded analysis and faithful V1 handoff, restricted Lykoi authorship,
   deterministic compilation and independently planned external verification.
2. **Which parts are trusted, untrusted, human-authorized, AI-judged and mechanically
   enforced?** Owners/delegates authorize intent and behavioral choices. AI supplies
   fallible candidates and semantic review evidence. The controller/store, isolation
   platform and pinned deterministic tools form a scoped trusted computing base;
   they enforce identities, roles, transitions, bounded checks, grants and halts.
   Author output and software remain untrusted until their respective checks;
   independent verification gives declared-scope evidence, not universal truth.
3. **What is the shortest credible path to a public rehearsal?** Implement the
   authority/artifact controller; add wizard/clarification/policies and blind review
   around existing bounded tools; close isolated authorship and prefrozen external
   verification; run one frozen end-to-end public rehearsal with supported success,
   intentional faults and visible unsupported refusals. Reconsider held-out readiness
   only under separate authorization after that evidence exists.
