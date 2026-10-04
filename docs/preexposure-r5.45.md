# R5.45 staged pre-exposure protocol (prospective)

**Draft/prototype only. R5.45 ended `R5_45_STATE_IDENTITY_GAP`; this protocol is
not qualified for benchmark pre-exposure certification.** Synthetic qualification
does not close the execution-input dependency boundary described below.

This protocol is infrastructure-only and grants no benchmark exposure authority.
Implementation: `benchmark/evaluation/preexposure_r5_45.py`. Canonical encoding,
strict decoding, SHA-256 and exclusive fsynced persistence use the unchanged
`lykoi-canonical-evidence-r5.43` implementation. Local trusted execution and
exclusive state ownership are prerequisites, as in R5.43; this is not hostile
runtime attestation or a concurrent-writer protocol.

## Required guarantees

Every certificate must establish: historical lock; prospective lock;
infrastructure lock; frozen authority; core count 30; restricted generic harness;
application/compiler regressions; R5.41 focused regressions; independent matrix
and coherence; model validation; safety; structural schema; traceability;
implementation and profile contamination; qualified recorder byte identity;
qualified canonical protocol byte identity; one-pass/accounting readiness; exact
source, tree, runtime and configuration identity shared by all results.

The identity stage carries core count, authority identity, recorder identity and
canonical protocol identity. All other required guarantees have explicit policy
stages. Policy is hashed into the certificate; it is supplied by qualified trusted
orchestration, never accepted from an untrusted certificate. A PASS without
`successful=true`, any missing stage, or any non-PASS stage is rejected.

## Identity and freshness

Physical file bytes and membership, including ignored and uncommitted files,
are hashed by relative path. Symlinks/nonregular files fail closed. Git commit
is provenance, never a substitute for byte identity. Configuration and exclusions
are themselves hashed. No timestamps or mutable labels prove freshness.
All stages use the broader common state identity: narrower dependency reuse is
not qualified. Same-state reuse requires recomputing identity and matching all
inputs; a changed input invalidates every broader-bound stage.

The implementation has a prospective identity primitive, not an automatic proof
that an arbitrary caller's chosen root/configuration covers all external inputs.
Runtime/library/native tool/environment/configuration dependencies must be
qualified by the orchestration before a real experimental certificate is usable.
Cache exclusion is safe only with a qualified cache-free execution mechanism.
Outputs may be excluded only if they cannot be loaded as verification inputs.
These are qualification obligations, not discretionary exclusions.

## Evidence and certificate

Each stage envelope contains protocol, state digest, stage name, status,
result, qualified mechanism identity and a SHA-256 over all preceding content.
Status is PASS, FAIL or INCOMPLETE. Persistence is exclusive; reload requires
exact canonical bytes plus one LF and validates the envelope digest.

A certificate contains protocol, frozen-state digest, PASS status, policy hash,
the complete map of required stage names to canonical evidence identities, and
deterministic assembly semantics. Evidence identities cryptographically bind
the detailed locks, suites, authority, versions and results. No time field is
required: freshness is exact identity equality. Timing telemetry, when present,
is evidence and changes identity. Identical semantic content assembles identically.

Assembly revalidates every envelope and policy mechanism; validation repeats
assembly and compares canonical bytes, then requires current state equal to the
frozen state. Integrity hashes protect accidental mutation, not malicious
rewriting of all authority. Evidence production is trusted, like R5.43.

## Bounded execution and interruption

Decompose harness discovery into independently bounded module stages; preserve
the existing prohibition runner and check the union and explicit skips. Focused
R5.41 and recorder qualifications remain explicit checks even if duplicated in
the generic suite. Matrix and other non-suite gates are separate commands.

Before work, persist INCOMPLETE attempt evidence. A supervised subprocess may
complete with PASS/FAIL evidence in a distinct immutable receipt; timeout is
INCOMPLETE. A parent/tool interruption leaves the initial INCOMPLETE receipt.
Missing/corrupt completion evidence is not PASS. Infrastructure-only recomputation
uses a new attempt, never rewrites/resumes the old receipt. This does not amend
R5.44 or permit a future experimental retry without its own governing protocol.

Final assembly and validation are small operations over persisted evidence.
Reservation is inaccessible until completeness, current identity, qualified
versions and recorder/accounting have been validated. The provided boundary
accepts only `synthetic-only` policy; it cannot authorize a benchmark run.
Under exclusive state ownership, recheck current state immediately before
reservation, bind the recorder baseline to certificate identity, reserve once
through the unchanged R5.43 recorder, record one callback receipt and stop.
