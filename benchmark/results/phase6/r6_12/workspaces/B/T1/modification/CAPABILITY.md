# T1 modification — Resize active holds

Terminal: `PRODUCTION_REQUEST_RECORD_UNION_PROFILE_GAP`, static assessment.

The base terminal record is preserved. Base contract clauses 2–3 require exact-key
stock records and a heterogeneous operation-record sequence, validated completely
before any state-dependent error. Modification clauses 1 and 3 retain all those
obligations and extend that union with `{kind:"resize",id,n}`. They do not remove
the original missing production request-record/union validation interface.

Own base evidence (`../base/CAPABILITY.md`, clauses and production references)
identifies scalar/scalar-element-collection parameters rather than record unions.
Current `docs/typed-input-values-v1.md:74–92` likewise retains scalar/collection
types and explicitly declared per-operation parameters; JSON decoding is distinct
from semantic transformation (`40–42`). Stored entity validation cannot replace
whole-request validation or its shape-before-state error precedence.

The new obligation is active-hold lookup followed by signed delta d=n−old_n,
insufficiency checking, and coupled free/held/hold.n changes; decrease returns
units, equality succeeds unchanged, shipped/used IDs remain unchanged. Existing
identity guards, comparisons and checked addition are useful subsets described
by the base assessment. Runtime subtraction is not named there, but the bounded
1–100 domain allows consideration of finite tables, so subtraction alone is not
asserted irreducible. Coupled updates to existing stock and hold rows and a pure
ordered request fold retain the base profile/interface concerns. No newly proven
arithmetic impossibility is claimed. The retained record-union blocker suffices.

All 8 new frozen cases were read after recorder start: increase, decrease, equal,
insufficient, inactive/missing hold, post-ship rejection, interleaved state changes,
and later malformed resize taking precedence over an earlier state error. These
are expected observations, not executed behavior. The base record reports 15
original cases. Original 15 and new 8 cases are `NOT_REACHED`; zero candidate
attempts, compilation/evaluations, repairs or tests. Regression count/rate is
unavailable because there was no base success and no execution. No Python shape
validator or state processor was authored as transport. This is an implemented
production profile assessment, not a failed candidate or abstract kernel proof.

Reads: own base CAPABILITY.md/GAP.json, own base contract, assigned modification
contract/acceptance, current typed-input-values documentation. START.json/GAP.json
provide exact UTC boundaries and elapsed seconds. Session disclosure is in
`../../MODIFICATIONS.md`.
