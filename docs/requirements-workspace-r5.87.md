# R5.87 — AI-assisted requirements workspace, workspace-1

**Implemented:** `src/lykoi_workspace/`, around the unchanged authority-1 controller.
**AI proposes. Humans authorize behavioral decisions. The controller grants authority.**
This is R5.85 roadmap stage 2 engineering, with deterministic semantic producers.
It is not production AI formalization qualification. The
[report](../benchmark/results/phase5c/R5_87-AI-REQUIREMENTS-WORKSPACE.md) records evidence.

## Service and authority boundary

`Workspace(controller, project, session, service_credentials)` represents one
requirement lineage. The trusted embedding service provisions role credentials;
human credentials are supplied separately to each human operation. Producers receive
only copied JSON requests, never the workspace/controller/database/credentials.
`Controller.execute` performs every adoption, clarification, commitment, review,
approval, invalidation and seal. Internal approval/seal/grant artifact types remain
reserved. Strings such as APPROVED, COMPLETE, NO_AMBIGUITY and HUMAN_CONFIRMED are
untrusted output; they cannot select events or create approval.

Session pointers, source versions, candidate versions and review counts are rebuilt
from controller artifacts/events on restart. `status()` returns the controller's
actual authority state alongside derived UX/budget information. No local approval or
seal boolean is persisted. The service and controller database administration remain
trusted; this Python service is not itself an untrusted-worker sandbox.

| Operation | Result |
| --- | --- |
| `ingest(human_credential, text, policies)` | Exact text-bearing message and adopted source root; each ingestion creates a version. Previous live root is explicitly superseded. |
| `define_policy(rule, scope=..., waivable=...)` | Candidate ProjectPolicyContract-0.1 authority wrapper. |
| `adopt_policy(human_credential, identity, rationale=..., replaces=...)` | Mechanical identity receipt, separate synthetic reviewer evidence, explicit human adoption, controller policy seal; replacement invalidates descendants. |
| `formalize(producer)` | Untrusted structured analysis becomes immutable candidate FRC and controller commitment. |
| `ask(question_id)` | Exact structured question; blocking/important questions enter controller clarification lifecycle. |
| `answer(human_credential, question_identity, text)` | Controller-authorized answer and new source root retaining earlier answers; previous candidate is never mutated. |
| `revise_answer(human_credential, answer_identity, text)` | Explicit source supersession and answer invalidation, fresh question/answer, root retaining other answers. |
| `commit_inventory(reviewer)` | Source-only production, exact SOI registration and controller SOI_COMMITTED; starts review of exact candidate. |
| `reconciliation_inputs(inventory_identity)` | Candidate access only after commitment and matching controller REVIEW_STARTED binding. |
| `reconcile(inventory_identity)` | Item-level deterministic coverage evidence and separate requirements-only structural disposition. |
| `route_disagreement(coverage_identity)` | Product-level question tied to exact disputed coverage; human resolution creates a new source/candidate. |
| `approval_summary(exact_frc)` | Commitments, freedoms, questions and issues, bound to displayed exact candidate identity. |
| `approve(human_credential, exact_frc)` / `seal(exact_frc)` | Exact owner approval / controller WHAT seal after bound prerequisites. |

Operations are individual controller transactions with expected revision checks.
Multi-operation service workflows can leave inspectable partial drafts after failure;
they do not imply approval. Journal-derived cursors and consumed review budgets survive
restart. A competing process can receive a controller revision-race refusal.

## Identity, FRC and provenance

Logical IDs such as `TASK.CREATE.TITLE` identify continuing obligations in a lineage.
Typed content identities identify immutable artifacts, including every dependency,
revision, producer attribution and clause. Clarifying priority changes the FRC identity
but preserves an unchanged title obligation's logical ID. Conservative equal
relation/statement checks reject gratuitous renaming. The unchanged R5.80 validator
and `check_revision` validate the nested **FormalRequirementContract-0.1** record,
declarations of meaning change/retirement and derivation shape. Retired IDs cannot be
recycled. Semantic equivalence of different paraphrases is not inferred.

Authority-1 `frc.content` is a workspace wrapper, not a changed historical FRC schema:
`workspace, contract, producer, authority, questions, policy_applications, unsupported,
necessary_implications, exclusions, structure`. `contract.review` stays null. The
`authority` ledger maps each logical obligation to exact human-message, clarification
answer or adopted-policy identities in the source's normative closure. The source
record preserves exact original text; clarification and policy evidence are separate
identities, not silently spliced into that original text. Their exact text is provided
in the source-only evidence manifest. Policy-derived clauses use an original relevant
source anchor and a separate exact policy authority record; a quote alone proves no
behavioral justification.

`PROVENANCE` reserves human_statement, clarification_answer, approved_policy,
observed_legacy_behavior, test_supported_behavior and documentation_claim. Only human
statement/authorized clarification/adopted policy ingestion is implemented here.
Recovery is an extension point, not an implemented parser or automatic adoption of
observed legacy behavior as human intent.

## Clarification and priority

Questions have `id, text, priority` and may record affected logical IDs. Priority is
bounded to BLOCKING, IMPORTANT or INFORMATIONAL. BLOCKING and IMPORTANT remain
approval-blocking until the producer revises against exact human answer evidence;
IMPORTANT may be resolved by an explicit human delegation decision. A producer cannot
authorize delegation by its own label. INFORMATIONAL is retained outside active
material FRC issues and does not prevent approval. Its display operation does not
create a normative answer; normative behavior changes use the clarification path.

Materiality, wording, applicability, decomposition, implication necessity and the
priority classification are semantic-producer/reviewer judgments. This is not a
universal ranking algorithm. An active FRC issue always blocks even if its question
is mislabeled informational. Questions are asked sequentially: after a required
answer, revised formalization supplies questions for the new root.

## Project policy authority and precedence

The minimal policy wrapper records rule, exact scope (`*` or a session), version and
whether a feature exception is permitted. No policy is automatically adopted. The
source root contains all selected adopted policies, preserving exact dependencies.
Formalization records every policy application as DEFAULT or FEATURE_EXCEPTION with
an explicit feature decision. Reconciliation retains feature override evidence;
non-waivable exceptions, unbound policies and invalid/conflicting selections become
visible POLICY_CONFLICT evidence and halt. The controller independently enforces
application/exception rules at approval and sealing.

Public example: ordering is explicitly unconstrained unless feature requirements say
otherwise. Feature source “Show tasks newest first” wins via a permitted explicit
exception; the general policy does not erase it. The non-waivable variant halts.
These are elected synthetic project rules, **not universal Lykoi defaults**. Exact
policy replacement makes existing dependent approval/seal ineligible for new use.

## Source-only review and practical isolation

`Producer` requires role, session, provenance, isolation and `produce(request)`.
The request contains only `role, instructions, session, source, evidence,
output_schema`. Source carries exact identity, text and source revision. Evidence
contains exact authoritative statements/answers/policies. Formalizer and reviewer
contexts cannot share recorded session identities across the lineage. The reviewer
API accepts no FRC, formalizer inventory or reconciliation input.

`ModelAdapter` defines the future model/provider callback boundary: role-specific
instructions, structured-output schema label, exact inputs and recorded session/model/
provider provenance. It claims CONTEXT_SEPARATED_COOPERATIVE only. Providers and
fresh contexts must actually be provisioned by a deployment; metadata does not
demonstrate independence. Results are registered as candidate evidence by the trusted
service after return. No model callback has a controller command interface.

`SubprocessFixture` runs each known-answer producer in a fresh isolated-import Python
interpreter, empty environment, fixed worker, stdin JSON input allowlist and bounded
execution time. Reviewer fixtures are separately configured, with no shared candidate
output. Isolation class: **PROCESS_SEPARATED_FIXTURE_NO_OS_SANDBOX**. Worker imports
neither service nor controller; the actual workspace/controller object and credentials
are unavailable through this interface. This is stronger than a prompt-only instruction
or shared interpreter context. It does not deny an actively malicious arbitrary worker
filesystem/network access, demonstrate different models/providers or qualify strict
containment. Such workers require independently administered OS isolation later.

The committed **SourceObligationInventory-0.1** preserves version, source commitment,
extractor/context class, items, questions and limitations. Each item retains the R5.84
shape `id, spans, meaning, category, material, dependencies`. Exact Unicode offset/
quote checks and nonwhitespace text accountability run before commitment. Sidecar
`interpretations` and `authority` record per-item structured clauses and exact evidence
identities. `domains` and `unspecified` retain independently declared context. This is
an authority-1 wrapper around SOI concepts, not a replacement historical schema or an
SCCA production-admission claim.

## Bounded reconciliation and finite review

The normal path cannot obtain reconciliation inputs until the SOI has been committed
and bound by REVIEW_STARTED to the exact FRC. Deterministic comparison is deliberately
conservative: logical item mapping plus complete statement/relation equality, exact
authority set equality and normative-context checks. Supported outcomes include
MATCHED, SOURCE_OBLIGATION_MISSING, FRC_OBLIGATION_LACKING_AUTHORITY, LACKING_AUTHORITY,
MATERIALLY_DIVERGENT, AMBIGUITY, UNSUPPORTED_SCOPE and UNRESOLVED_MAPPING.
Policy selection conflicts and feature precedence are separately visible.

Material items require individual mappings; an umbrella “everything is covered” item
does not cover the candidate obligations. A nonbehavioral item cannot justify a
positive FRC obligation. Missing, divergent, unsupported and ambiguous evidence gets
DISPUTED controller review, not an approval. Disagreement routes to human clarification;
there is no third AI tiebreaker. Different legitimate decompositions/paraphrases halt
for resolution instead of pretending exact JSON equality proves general equivalence.
Unqualified implication/exclusion and structural proposals halt this bounded path.

**Two inventory commitments per session lineage maximum:** initial review plus one
correction/human-resolution re-review. The consumed count is journal-derived across
source/candidate revisions and process restarts. Reaching the budget while further
review is required yields FINITE_REVIEW_EXHAUSTED; no reviewer-of-reviewer recursion,
silent retry or guessed approval. An acceptable second review can still be approved
and sealed. Restart does not reset the budget.

## WHAT seal and limitations

The public example ends with a real controller WHAT seal. Its bound structural
artifact explicitly records **requirements-only / UNSUPPORTED for authoring projection**:
no actual V1/BDI structural projection is attempted or claimed supported. This is the
R5.86 controller's existing WHAT-only sealing facility. A declared unsupported required
concept/proposed structure blocks workspace reconciliation; a sealed FRC is not an
implementation grant. No BDI, adequacy, V1, verifier plan, author job, generated software
or external evaluation is produced by this round.

The correlated-error test externally declares three expected material obligations.
Both fixtures mistakenly treat listing as nonbehavioral; human approval of the
incomplete summary still obtains a controller seal. The expected inventory comparison
shows it is wrong. Authority binding and isolated agreement do not establish universal
semantic truth. The architecture reduces candidate-conditioned error without eliminating
shared mistakes or a human approving an incomplete summary.

Run the [public transcript](../benchmark/results/phase5c/r5_87/WIZARD-TRANSCRIPT.md)
with `python -m lykoi_workspace.example` (`--audit` opens exact bindings). Set
`PYTHONPATH=src` with a normal Python 3.10+ interpreter. Workspace tests:
`python -m unittest discover -s tests -p test_requirements_workspace.py -v`.
No external model/API or third-party dependency is required. B03 remains unaccessed;
R5.83-CANDIDATE-1 stays unactivated. Stop after R5.87.
