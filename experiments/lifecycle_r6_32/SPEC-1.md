# R6.32 lifecycle/admission/retrieval specification 1

This external nonproduction facade reuses unchanged `typed-composition-1`. It adds
storage/admission metadata, not runtime meanings. Production-backed application
edits are a separate path through unchanged R6.16 `generate(..., 'C')`.

## Registry and identities

`Registry(path, journal)` contains immutable sequential `000001.json` generations.
Each generation stores a complete definition map, predecessor edges and explicit
migration receipts. It hashes canonical JSON of generation/previous/operation/state.
The previous generation hash chains publication. Definition identity is exactly
R6.18 `identity`: version + frozen VM foundation + full definition except identity.
No new identity algorithm for executable content. `revision` remains the frozen
value 1; distinct content hashes and external generation/edges supply versioning.

Objects are indexed by SHA256. Admitted objects remain byte-equivalent in every
later snapshot. Names are exact case-sensitive identifiers, not pointers to latest.
Two versions of one family may coexist, but a fetched dependency closure cannot
contain both versions. Dependency pins resolve both exact family and exact hash.
Pinned old calls never redirect when a successor is admitted.

`retrieve(pin=...)` returns the exact dependency closure sorted by hash.
`retrieve(name=..., signature=[params,result_type])` filters exact lexical name
and exact ordered monomorphic signature, returning hash-sorted hits. No match is
an empty search; exact missing pin rejects. `resolve(name)` requires exactly one
hit and rejects zero/multiple hits. Combining pin and search filters rejects.
`expected` compares exact generation token; stale readers/writers reject.
Retrieval returns deep copies; mutating a fetched host object cannot edit storage.

## Admission

`admit(proposals, expected, predecessor=None, budget=64)` accepts one to eight
definitions atomically. Checks: bounded JSON-domain shape; exact fields; identifier,
signature and pin shape; duplicate identity; dependency resolution/name matching;
graph cycles/mixed versions; canonical identity; frozen R6.18 schema/type/order/
exact-reference/semantic checks; bounded hygienic expansion; frozen VM validation.
Batch failure publishes no registry generation. Cycle tests with forged cyclic
hashes exercise rejection before identity checking; cryptographic self-pinned
cycles are not claimed constructible. Real local value cycles also reject.

For a reusable definition, a closed admission probe calls it with type-correct
0/false/null literals and returns constant Int64 zero. It is **not executed**.
The probe subjects arbitrary exact signatures to the unchanged closed-program
validator; it establishes static compatibility, not overflow freedom, behavioral
correctness or termination beyond frozen bounds. Reserved name `AdmissionProbe`
cannot occur in a closure. Closure at most eight definitions; stored steps128,
per-definition steps32 and inherited representation/depth limits apply. Expansion
counts the probe and its fixed encode too; at most64 nodes and nesting4. This is
conservatively smaller than some standalone packages' theoretical capacity.

Failures preserve the original proposal, input token, predecessor, exact structured
first diagnostic and measured interval in the journal. The code may refuse malformed
serialization at the underlying Python/JSON boundary; no AI judgment participates.

## Successors and selected caller updates

A successor requires an already admitted predecessor and identical name, ordered
parameter signature and result type. Body/dependencies may change only within the
frozen meanings. New identity/edge are recorded; predecessor is retained. Multiple
successors require explicit pins, never a guessed winning revision.

`dependents(pin)` returns sorted direct and transitive definition users.
`migrate(predecessor, successor, decisions, expected)` requires a total disposition
of every admitted direct caller: a pinned caller successor or explicit null to
retain it. Caller successor must itself be admitted with the proper edge. Its entire
definition must equal the predecessor caller with only the chosen dependency/call
pins changed and identity resealed. Incomplete, extra, type-changing or behavioral
caller edits reject. Migrated references are explicit new caller objects; historical
caller objects remain unchanged. Transitive callers remain pinned unless separately
updated at their own immediate dependency layer. The transitive test demonstrates
this; the main witness updates CallerA and explicitly retains CallerB.

## Application edit path

`edit.revise` is a deliberately narrow facade for the copied exposed kiln fixture:
exact predecessor intent hash, explicit selected/retained disposition for ignite,
set_gate and invariant:0, no unrelated intent changes. Both builds use existing
production generation and must yield identical source/IR. No endpoint or execution
primitive is added. Predicates, transition writes, error precedence and persistence
decisions are entirely production-generated; the facade does not execute them.

`install` checks the exact installed source hash, archives/fsyncs predecessor bytes,
fsyncs the fully generated successor, then atomically replaces the experiment-local
application path. Persisted records are untouched by installation. The same-store
witness exercises both existing operations in fresh subprocesses before/after.
This cooperating single-installer interface is not production deployment authority,
a general migration planner or a distributed multi-resource transaction.

## Durable publication and telemetry

Registry publication: writer lock created exclusively, exact token recheck under
lock, fsynced `.pending` file, atomic no-clobber hard link to final generation,
then remove pending name. Readers only use complete `.json` generations, verifying
chain, identity and retained predecessor contents. Existing lock or pending staging
bytes block new writes. Readers may still retrieve the last committed generation.
Completed objects cannot be overwritten using the public admission path.

`Journal` is an exclusive single-writer sequence of immutable hash-linked events.
UTC labels and `perf_counter` intervals are actual measurements, not inferred AI
tokens. Start/complete stages must pair exactly; orphan/duplicate completion and
duplicate start reject. Errors leave a stage incomplete. Recovery reports completed,
incomplete and pending records without completing missing work. Tool intervals are
recorded for admission/retrieval/controls/generation/subprocess/installation; some
metadata-only migration events have only enclosing stage time. The measurement
summary labels absent per-event intervals rather than filling them with zero.

Crash child exits with73 after fsyncing a partial telemetry record and a full but
uncommitted registry snapshot. Recovery reads the prior generation and completed
stub authoring receipt; resumes publication from its exact saved proposal in a new
explicit branch. Original pending bytes are retained. Stub authoring time/usage
are null, never real model measurements. A pending file is never silently promoted
or discarded. A lock left by a crash during its critical section needs explicit
operator recovery; automatic dead-owner lock reclamation is not qualified.

These guarantees cover cooperating processes and abrupt process exit on the tested
local filesystem. SHA256 integrity is not authentication against an adversary who
can rewrite/reseal the whole directory. Directory fsync/power-loss, multiwriter
journals, hostile mutation, distributed storage, provider usage/billing and AI-session
interruption remain unqualified. No such broader readiness claim is made.
