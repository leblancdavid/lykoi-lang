# R6.32 — Symbolic lifecycle and modification qualification

**Final classification: `R6_32_LIFECYCLE_PARTIAL`.**

Bounded immutable admission/retrieval, explicit successor/caller updates, genuine
existing-operation behavioral modification and process-interruption telemetry
recovery are demonstrated. Production impact analysis does not identify the changed
extension predicates or guarded mutations; automatic dependency-complete H2 impact
is not qualified. These are scripted infrastructure witnesses, not AI-discovered
abstraction benefit, modification superiority or full H1/H2 results.

## Baseline and preservation

Initial worktree clean. [Baseline](r6_32/BASELINE.json) captures **1,771** protected
SHA256 identities before implementation, including R6.31 publication and all inherited
production/historical preservation anchors. [Inventory](r6_32/INVENTORY.md) records
the unchanged R6.18 wrapper, R6.23 construction adapter, production guarded state
changes/invariants, impact/diff, deterministic generation and R6.30 telemetry.
Kernel remains **26 constructs**. Publication verifies every protected identity,
source freezes, evidence hashes, relative links and `git diff --check`.

All code lives in [the separate experiment](../../../experiments/lifecycle_r6_32/README.md).
Admission/storage/retrieval/edits are specified in
[SPEC-1](../../../experiments/lifecycle_r6_32/SPEC-1.md), with the
[preimplementation protocol and expected impact sets](r6_32/PROTOCOL.md).
Coordinator authored scripted fixtures/tests; there were zero AI participant/model
calls. This is same-coordinator, capability-tailored exposed-fixture qualification,
not independent task sourcing or blinded review.

## Registry and admission

Primary completed evidence is [attempt 5](r6_32/attempt-5/RESULT.json).
[Registry results](r6_32/attempt-5/REGISTRY.json) record **5 admitted definitions**:
original Increment, CallerA/CallerB, Increment successor and CallerA successor.
Exact old/new identities coexist. Retrieval is hash-pinned, type-filtered and sorted;
name-only resolution rejects ambiguity. Restart and returned-object mutation do not
change admitted content. Admission is deterministic and invokes the unchanged
R6.18 schema/type/dependency/order/expansion checks plus frozen VM validation.
No application decision or new execution meaning is introduced by the facade.

**18/18 primary adversarial controls** pass: duplicates, identity tampering, missing
dependencies, dependency and local value cycles, invalid predecessor, type-changing
successor, malformed schema/type, unsupported host meaning, expansion exhaustion,
unauthorized mutation, ambiguous resolution, mixed-version closure, stale read/write,
partial caller migration and incorrect caller successor. Original proposals and
exact diagnostics are durable events, not just aggregate pass counts.

Graph-cycle controls deliberately use forged cyclic hashes, rejected before identity
checking; no constructible cryptographic fixed point is asserted. A static admission
probe is never executed and is not functional correctness proof. Conservative inherited
closure/expansion limits and reserved probe name are documented.

## Successors and dependency-aware modification

Increment changes `x+1` to `x+2` under a distinct immutable identity. Its predecessor
remains retrievable. Direct dependent CallerA/CallerB are identified. CallerA is
explicitly resealed/admitted/selected; CallerB receives an explicit retain decision.
Partial and wrong migrations reject, with no implicit old-reference redirection.
Caller successors must differ only in the selected dependency/call pins.

**12/12 VM observations** verify original CallerA (+1), selected successor CallerA
(+2), and retained CallerB (+1), at four byte inputs each. Exact envelopes and output
hex are retained. A separate transitive regression test confirms nested callers
remain pinned until their own immediate dependency layer is explicitly updated.
This is a bounded pin-update mechanism, not a general refactoring planner.

## Genuine stateful in-place modification

The source is the **previously exposed R6.16 C/kiln/base intent**, copied with its
exact source hash and preserved predecessor. The modification changes the existing
ignite/set_gate behavior: a firing kiln may have its vent closed only for an
emergency load. It updates both existing guards and the shared invariant. No new
endpoint is introduced. Ordinary-load constraints, cold-state gate writes, phase
precedence, creation/listing, field declarations and ID/time behavior remain intact.

Both copies lower/generate through unchanged production semantics. The facade
performs no runtime predicate decisions. The copied [original](r6_32/attempt-5/fixture/original.intent.json)
and [modified](r6_32/attempt-5/fixture/modified.intent.json) intents, generated source
and IR are published. Generation repeats yield identical source/IR.

[Functional evidence](r6_32/attempt-5/FUNCTIONAL.json): **148/148 observations** pass,
including two deterministic runs of all eight phase/vent/load tuples across ignite,
two set_gate values and listing, plus create/ignite/rejection/reload/nonblank sequences.
That is74 observations per run, not148 distinct inputs. Persisted invalid states
reject, rejected bytes remain unchanged, and successful mutations preserve the
appropriate original/modified invariant. Expectations are specified from requirements,
not inferred from generated predicates. Scorer and candidate are same-coordinator.

The [same-store installation witness](r6_32/supplement-2/RESULT.json) additionally
uses one installed application path and one persistent store: original emergency/
closed ignition rejects `gate_required`; after an exact-pinned generated-source
replacement, it fires, retains a closed gate, rejects repeated ignition
`invalid_transition`, and reloads the same record. **5/5 before/after observations**
match. Installation preserves record bytes and archives exact predecessor source.
Consumer-disposition, stale intent/source and unrelated-edit controls reject.

A deliberately well-typed incomplete modified fixture still compiles but fails the
emergency/closed ignition requirement. That negative scorer control is preserved;
passing static validation is not mistaken for behavioral correctness.

## Impact analysis accuracy and limitation

The expected changed semantic set was independently specified *from the requirement
before tool output*, not independently reviewed: policy definition, two guard
predicates, shared invariant and two affected transitions (**6 items**). Unaffected
create/list behavior and six field declarations were separately fixed.

[Actual comparison](r6_32/attempt-5/IMPACT.json) preserves native impact/diff output.
The production scalar-base diff is empty because changes reside in extension facts.
Each extension-only seed is unknown to the legacy API. A supported `field:vent`
seed returns12 scalar structural entities, including unchanged create/list.
With the declared change-footprint mapping, there are **0 true positives, 6 false
negatives and12 off-footprint hits**. Two of those are explicitly unaffected behavior
hits; ten are ancillary native structural nodes without extension counterparts.
These12 are reported as false positives against the chosen behavioral-change set,
not errors in the API's documented structural traversal. They are not a universal
precision/recall estimate. All raw IDs/paths/mappings remain available.

The registry's explicit pinned dependency traversal works for its admitted symbolic
definitions. It does not repair or replace production impact analysis. Automatic
identification of changed production extension predicates/mutations remains a
capability gap; the copied fixture uses explicit verified consumer dispositions.

## Telemetry and interruption durability

[Recovery evidence](r6_32/attempt-5/RECOVERY.json) uses a real child exiting73 after
fsyncing an incomplete telemetry record and an uncommitted registry snapshot.
The previously committed registry remains readable. Completed stub authoring and
its exact saved proposal are reconstructed; publication resumes in an explicit new
branch **without repeating completed authoring**. Original pending bytes and
incomplete start remain preserved. Registry/journal refuse writing over pending
records. No missing elapsed time or usage is fabricated.

Immutable event files record stage starts/completions, input pins, admission/retrieval,
caller decisions, generation, modification/installations, functional observations,
errors, UTC labels and measured wall/tool intervals. Metadata-only migration events
have enclosing stage wall time rather than measured individual intervals; those
missing measurements are labeled. Stub authoring has null time/usage. No AI billing,
tokens, harness-wide setup duration or reasoning telemetry is claimed.

[Focused regression tests](r6_32/TEST-RESULTS-1.json): **14/14 methods** pass, covering
restart/immutability, atomic batch rejection, malformed signatures, stale competing
writers, writer lock, interrupted publication, pin-only migrations, transitive
dependencies, incomplete events, orphan/duplicate stages, removed records,
no-clobber writes and total application consumer dispositions.
[Supplement](r6_32/supplement-2/RESULT.json): **7/7 additional rejection controls**
cover application edit/install preconditions and committed registry/journal tampering.
Pending-write refusal and branch recovery are separately observed. Counts are not
pooled with retained repeated attempts.

Durability is bounded to cooperating single-writer processes on this filesystem.
Power-loss/directory-fsync guarantees, hostile whole-chain resealing, distributed
storage, automatic stale-lock reclamation, multiwriter journal recovery and provider
session interruption are unqualified. Hash integrity is not authentication.

## Failed attempts and remaining blockers

All failures remain in place: baseline receipt-field error; attempt1 raw output-byte
JSON serialization with a retained partial file; attempt2 unsupported seeded store
envelope; attempt3 replay-label collision. Successor runner corrections changed
serialization/seeding/labels only, not candidate rules or requirement expectations.
Attempt4 completed; final attempt5 additionally qualifies schema/stage handling and
snapshot consistency. Earlier successes are retained, not pooled into final counts.
The first publication check also refused trailing indentation in the retained
partial JSON. Its exact bytes remain untouched, with an explicit parse/whitespace
exception in the verification receipt; all other new files pass those checks.

Remaining blockers:

1. Dependency-complete production extension impact is unsupported by the existing API.
2. Fixture/edit facade covers one exposed record-local skeleton; broader shared-state
   modifications and equivalence are not qualified.
3. Admission/expansion is the small R6.18 subset with documented conservative bounds.
4. Provider-neutral execution works, but AI proposal workflows, actual usage/billing,
   context exclusion and real model-session recovery have not been qualified here.
5. Local cooperative process durability does not imply hostile/distributed/power-loss
   storage guarantees or authenticated registry authority.

## Smallest recommended AI-authored pilot and stop

Separately authorize one **exploratory H1 workflow pilot** on a development-exposed
synthetic task: freeze model/route/configuration and minimal package, ask for one
parameterized composition using existing meanings, deterministically admit it,
retrieve its exact pin and construct two callers, then propose one signature-preserving
successor and explicitly update one caller while retaining the other. Predefine
functional expectations and preserve every rejected proposal, tool event and actual
usage/missing measurement. No adaptive-benefit or comparative-efficiency claim.

For an H2 pilot, require an explicitly frozen independent impact/consumer map and
one copied exposed application edit; mark production automatic impact unavailable.
Do not rely on the legacy API as a complete oracle. Neither pilot is authorized
by this publication, and full H1/H2 comparisons remain unstarted.

**Stopped after bounded AI-free qualification and publication.** Production/compiler/
runtime, R6.10/R6.18/R6.23/R6.25 and R6.3–R6.31 artifacts remain unchanged. No new
execution semantics, training, inference, P6-A04 acceptance or P6-A05 access.
Await explicit authorization before proceeding.
