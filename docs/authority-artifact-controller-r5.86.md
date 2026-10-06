# R5.86 — Authority/artifact controller, authority-1

**Implemented engineering layer:** `src/lykoi_controller/`, with public executable
challenges in `tests/test_authority_controller.py`. Baseline:
[R5.85 architecture](production-formalization-evaluation-architecture-r5.85.md),
especially §§2–3, 5–10, 12, 15 and roadmap stage 1. No architectural contradiction
was encountered. This envelope does not amend FRC-0.1, SOI-0.1, SCCA-0.1, BDI,
adequacy, V1 or Lykoi semantics. See the
[engineering report](../benchmark/results/phase5c/R5_86-AUTHORITY-AND-ARTIFACT-CONTROLLER.md).

## Extracted requirements and implementation

| R5.85 requirement | Mechanism |
| --- | --- |
| Typed scoped authority, authenticated owners; AI evidence cannot issue grants (§2) | Provisioned credential digest/role/project registry; command allowlist; internal-only approval/seal/grant artifact types. |
| Immutable store; atomic compare-and-append (§3) | SQLite transaction with `BEGIN IMMEDIATE`, exact expected journal revision and command-specific lifecycle checks; artifact and journal update/delete triggers. |
| Clarification creates new roots, no inherited old approval (§5) | Owner-answer event, new root, explicit predecessor, ordered retained answers, source supersession and fresh candidate/review. |
| Explicit PPC adoption and precedence (§6) | Independently reviewed/mechanically checked policy, owner adoption, controller seal; explicit FRC application/feature exception records. |
| Committed SOI and candidate with bound access evidence (§7) | Distinct producer roles, source-set equality, committed input manifests and explicit access lists; no candidate edge in SOI. Actual blindness remains deployment work. |
| DRAFT → REVIEW → APPROVED → SEALED, with halts (§8) | Derived journal lifecycle; owner approval distinct from controller WHAT seal; clarification, rejected and revision-required branches. |
| Exact typed canonical content and dependencies (§9) | CJ-1 serializer, SHA-256 typed envelope identity; exact byte wrapper; digest reads and dependency closure checks. |
| Separate implementation permission (§10) | Exact bundle/grant binding, accepted coverage/structure, supported BDI, adequate reviewed result, faithful complete reviewed V1, sealed independent plan and same freeze. |
| Verification plan before author dispatch (§12) | Separate verification-authority approval/controller plan seal precedes grant and single-use author reservation; result binds exact target/plan/freeze. |
| Substitution, stale approval, race, revocation, crash/replay challenges (stage 1) | Executable public tests plus cross-process reload, incomplete reservations, denied stale completion, immutable history and integrity failure tests. |

## Identity boundary: CJ-1

An identity has the form
`type:schema:CJ-1:sha256:hex_digest`. SHA-256 covers the entire canonical envelope:
type, schema, serializer, digest algorithm, project, authoritative content and named
typed dependency identities. Identical content in a different role/project/schema
or with a different dependency is a different artifact. Registration always checks
dependencies already exist: only backward edges are admitted, forming a DAG.

Structured input permits null, booleans, strings, arrays, string-keyed objects and
integers in `[-(2^53-1), 2^53-1]`. Sorted object keys, ordered arrays, compact UTF-8,
no trailing newline, no Unicode/newline normalization. Duplicate JSON keys, floats,
exponents, negative zero, nonfinite numbers, oversized integers and invalid Unicode
are rejected. The tests include a byte-level non-ASCII conformance vector.

Bytes are represented by a distinguished `base64-exact-bytes` content envelope:
every original byte affects identity, including CRLF versus LF. Message/answer/model/
target producers can submit bytes directly. Textual content likewise preserves its
exact UTF-8 string value. No source transcription or newline conversion is performed;
a future adapter must register such a conversion explicitly instead of replacing
original byte identity. This is a repository-owned serializer profile, not a claim
of cross-language canonical-number conformance for arbitrary JSON.

All fields submitted as `content` are authoritative to this wrapper. Presentation
paths/names are external locators and confer no authority; if placed inside content,
they are deliberately content-bound. JSON formatting and key insertion order do not
affect structured identity. Credential secrets and observational journal wall times
are not artifact content. No optional historical metadata field is silently treated
as normative: future adapters must specify their boundary before admission.

## Graph and lifecycle

The graph supports source messages/context, clarification questions/answers/roots,
policies, candidate FRC, SOI, coverage, structural projection, WHAT approval/seal,
structural receipt, BDI, adequacy, V1, verification plan/seal, freeze, bundle, grant,
author reservation/model, generated target and external result. Required edges are
typed; optional source/context/policy/transcript edges are separately allowlisted.
Cross-project dependencies and mixed source/FRC/WHAT-seal/plan/freeze graphs reject.
An approved FRC is the exact candidate plus an immutable approval artifact/event,
not a mutable replacement with the same display name.

Pre-seal structural content refers to the candidate FRC and is included in its WHAT
seal. A later positive structural receipt refers to **both that exact projection and
the WHAT seal**. This implements R5.85's pre-seal binding and post-seal discovery
handoff without a circular dependency. Unsupported structural review may accompany
a WHAT seal, but implementation authorization fails.

FRC lifecycle is derived from controller events: `DRAFT`, `REVIEW`, `APPROVED`,
`SEALED`, `CLARIFICATION`, `REVISION_REQUIRED`, `REJECTED`. `CLARIFICATION` is the
architecture's lifecycle name; it represents the requested clarification-required
halt. An answer creates a new root/candidate; it never mutates the old lifecycle.
Candidate, reviewed, human-authorized, mechanically validated, sealed and
implementation-authorized are separate inspected claims. Invalid transitions return
`Failure(code, details)` and a denial event; they cannot manufacture state.

## Actors and evidence

The embedding trusted service provisions named principals with secret credentials,
roles and explicit project scopes. Persisted role/scope/credential-digest configuration
must match on restart; callers cannot supply their own role or change the registry.
Synthetic identities in tests stand in for authenticated humans/services. Initial
scope is project-level with static named principals; dynamic delegation, expiry and
credential rotation are future authority-service integration.

Roles are owner, formalizer, independent reviewer, mechanical worker, controller,
author, external verifier and verification authority. The reviewer may publish its
own reconciliation/structural evidence; this is R5.85's single finite independent
review role, not a second reviewer-of-reviewer chain. It cannot authorize behavior.
Policy/structural/V1/plan producers cannot review their own candidates. An actor with
both author and verifier roles still cannot verify its own model. Verification
planning authority is distinct from plan production; the controller creates the seal
after the authorized plan-approval event.

Every event records exact subject, direct prerequisite identities, attributable
actor/role, resulting state, reason/evidence and evidence identity. Its own canonical
digest plus predecessor digest identifies the event. Seals/grants include exact
supporting event identities in addition to their artifact dependency closure.
Journal wall-clock `recorded_at` is immutable observational metadata separate from
the semantic event hash. Event order is authoritative; a later wall clock never
selects behavioral meaning. Deterministic replay compares semantic events/identities,
not incidental wall times.

Review rationale/access evidence is bound, not proven true. Mechanical
`identity-closure` receipts establish bookkeeping only. Test-only
`synthetic-producer-receipt` evidence explicitly labels placeholder stage results.
Trusted worker events and separate accepted review are required in addition to native
stage outcomes. A candidate's `approved`, `coverage_complete`, `verified`,
`human_confirmed` or adequacy label has no authority on its own.

## Invalidation, dispatch and persistence

Supersession/revocation append events. Conservative authoritative dependency closure
blocks every current descendant's new use; old artifacts, approvals, seals and grants
remain inspectable. A grant cannot match a new graph just because names/IDs agree.
Historical predecessor/question anchors remain in the audit DAG, but are not reused
as the new root's execution authority. All adopted clarification answers remain
normative dependencies in later roots; revoking an earlier answer invalidates them.

Conflicting answers to the same question cannot be selected by timestamp: the second
adoption rejects pending explicit human resolution. The minimal controller does not
implement the final conflict-resolution wizard. Policy choices require explicit
default or feature-exception bindings; a declared feature decision cannot be silently
overridden by a default, and non-waivable exceptions reject. Recognition of a hidden
natural-language conflict remains a producer/reviewer responsibility.

`reserve` rechecks grant subject, action, freeze, dependency freshness and disputes;
it makes a durable single-use author reservation. A restarted unfinished reservation
is reported incomplete, never presumed complete or re-dispatched. Model admission
requires that reservation; target admission requires completed model publication.
Reissuing a grant for the same bundle rejects; a new attempt must use an explicitly
new content-bound bundle. A plan producer/approver cannot reserve its own author job.
Completion rechecks authority, so withdrawn inputs cannot publish newly authorized
output. Verification binds checked exact target, sealed plan and matching freeze.
No worker execution or release mechanism is implemented by this round.

SQLite is the smallest standard-library atomic durable store here. Both artifacts
and semantic events are insert-only through triggers, with FULL synchronous writes.
Startup recomputes artifact identities, graph references and journal digest/revision
chain. Tests forcibly bypass triggers to corrupt copies and verify startup refuses.
The service, registry, database administration and filesystem permissions are the
trusted boundary; hash chains do not defend against a privileged administrator
rewriting the whole database or rolling back its external backup. Workers must
receive a mediated command interface, not the Python controller/database object.
OS isolation, remote authentication, executable pin checking and actual launch
containment are later R5.85 stages.

## Programmatic interface and executable public case

```python
from lykoi_controller import Controller, Failure

controller = Controller(database_path, administrator_provisioned_principals)
artifact_id = controller.execute(
    human_credential, "project-id", "register",
    expected_revision=controller.revision,
    kind="message", content=b"Exact original public source bytes",
)
controller.execute(human_credential, "project-id", "adopt",
                   expected_revision=controller.revision, subject=artifact_id)
audit = controller.audit(artifact_id)
controller.close()
```

`artifact`, `closure`, `state`, `events`, `audit` and `applicable` inspect identities,
source ancestry, scoped evidence/principals, seals, relevant grants, denials,
supersessions and incomplete reservations. Returned values are copies, not mutable
authority objects. `applicable(grant_id, exact_bundle_id, exact_freeze_id, action)`
returns a structured positive or refusal. These are service-side audit interfaces;
deployment must restrict raw audit disclosure.

Normal Python 3.10+ commands from repository root:

```powershell
$env:PYTHONPATH='src'
python -m unittest discover -s tests -p test_authority_controller.py -v
python benchmark/results/phase5c/r5_86/demonstrate.py
```

The public case adopts one policy/source, commits a candidate/SOI, asks for the
missing priority default, adopts exact `NORMAL` answer bytes into a new root,
commits/reconciles a revised FRC, approves/seals WHAT, binds synthetic structural/
BDI/adequacy/V1 evidence and an independent sealed plan, and obtains a grant.
Reload preserves authority; superseding the source makes that retained grant stale.
Semantic placeholders do **not** demonstrate actual AI understanding, supported
bounded producer integration, faithful real V1 mapping or software satisfaction.

Future recovery can register source evidence with observed-implementation,
test-supported, documentation-claim or human-authorized provenance. Such provenance
does not implicitly create human authority. Recovery itself is not implemented.
