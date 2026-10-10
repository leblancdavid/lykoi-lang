# Smallest recommended practical comparison — proposal only

One existing exposed persistent application, two tracks, one real in-place change.
Recommend direct standard-library Python versus the existing production-backed
Lykoi intent path from R6.16. Do not compare stateful Python against the stateless
R6.18 wrapper, and do not attribute this proposal to adaptive-symbol discovery.

## Concrete bounded scenario

Use a copy of the saved kiln application with its Boolean gate/burning state and
existing create, ignite, set_gate and list operations. Review exact saved behavior
before selecting a new modification contract; do not infer current flags or errors
from names. Both tracks must start from externally qualified, behaviorally matched
existing baselines and the same declared persisted fixture. The historical Python
baseline's blank-label failure must not be silently copied as an accepted baseline.
Baseline qualification is unscored and separately authorized; preserve failures.

A realistic example contract for independent review: move from a policy allowing
a burning kiln with a closed gate to one requiring burning implies gate-open.
Ignite must reject a closed gate, set_gate must reject closing while burning, and
the persisted-state invariant must agree with both operations. Requirements must
define exactly which errors and checks precede others. Apply only if review confirms
that this is a genuine change to the selected baseline, otherwise select another
explicit record-local policy change before freezing. No silent post-author task swap.

Existing intent predicates (eq/not/and/or), operation guards and shared invariants
can express this Boolean relation with no new semantics. Two operation entrypoints
are distinct callers of the shared state policy. This is not a general callable
definition rewrite or symbolic dependency migration. A source/config wrapper may
select entrypoints but must perform no task computation.

## Preservation and independent acceptance

- Install each generated/edited successor at its copied application path, keep
  predecessor artifacts, and operate on the same persisted store before/after.
  Verify artifact identity and behavioral change; an unused new definition fails.
- A valid existing closed/not-burning record must survive verbatim as data.
  Specify treatment of previously burning/closed records: declared invalid-state
  rejection with unchanged bytes, or an explicitly supported/source-authorized
  migration. Never invent normalization or silently discard old state.
- Independently source/review and seal requirements, expectations, error precedence,
  fixtures, case supersession and measurement stages before authoring. The reviewer
  must be named with actual input independence; same-coordinator seals do not attest it.
- Acceptance scenarios: both Boolean values and invariant combinations; ignition
  success/rejection; gate change success/rejection; missing targets, malformed inputs,
  repeated commands; create/list retention; mixed record sequences; fresh subprocess
  reloads; rejected-store exact bytes; retained old records; multiple sequential
  clients using the same store. No concurrency/distributed claim is needed.
- Retain old passing tests unless the new contract explicitly supersedes them.
  Report before/after results, new requirements, regressions and supersession separately.
  Compare behavioral observations, not source shape or byte-for-byte generated code.

## Minimal comparison controls and measurement

Use the same available model/configuration, requirements, tool access and bounded
modification budget. Give each author only its own baseline and released objective;
record permitted inputs and actual separation limitations. Equal access to selftest
facilities; no acceptance-feedback repair. Seal first/final submissions, all failures
and actual repairs. Production author edits declarative intent and generates through
the frozen generator; conventional author edits copied Python. Do not hand-edit
generated behavior or use the observer sidecar as the acceptance oracle.

Use the [measurement checklist](MEASUREMENT-READINESS.md) with existing session/export
and enclosing interval records. Count baseline preparation and all workflow stages;
use null for missing coordinator usage/billing. External scoring and restart execution
must be AI-independent. A small manual stage ledger is sufficient; no telemetry
platform or language extension is required.

## Decision gate and claim ceiling

Practical design is feasible within the production record-local profile, subject
to baseline acceptance and independent requirements review. Those steps have not
been commissioned or performed in R6.43. No new model session, application change,
oracle implementation or benchmark acceptance is authorized by this proposal.

One application/one modification establishes at most a bounded practical development
comparison. It cannot establish generality, superiority, adaptive-symbol benefit or
an independently sampled domain result. A later adaptive stateful comparison needs
a separately authorized architecture decision; no kernel expansion is recommended here.
