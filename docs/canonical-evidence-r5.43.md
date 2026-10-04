# R5.43 canonical evidence and locked recorder protocol

This prospective infrastructure protocol does not amend historical experiments
or authorize any benchmark exposure. Its implementation is
`benchmark/evaluation/recorder_r5_43.py`.

## Evidence equivalence (defined before qualification)

Evidence is a finite JSON data tree: objects with unique string keys, ordered
arrays, Unicode strings, integers, finite binary64 numbers, booleans and null.
Native **exact** dict/list/tuple containers and exact scalar types are accepted;
custom objects, subclasses, sets, bytes, non-string keys, cycles and non-finite
numbers are rejected. Tuples and lists both represent the same ordered protocol
array. Object insertion order is non-semantic. No array is unordered.

All fields, identities, provenance, classifications and versions are evidence.
Absence differs from present null. Boolean differs from integer and float;
integer differs from float and string. Float signed zero is retained. Strings
are not Unicode-normalized. No version migration, field dropping, sorting of
arrays, coercion of scalars or default insertion is permitted. Extra/missing
fields change evidence even if a consumer otherwise allows those fields.

Canonical representation is immutable UTF-8 JSON bytes using sorted object
keys, ASCII escaping, compact separators and no non-finite numbers. Python's
JSON integer and finite float spellings are used in the supported Python
environment; this is a versioned local protocol, not an RFC 8785 claim.
Equality means equality of these bytes, **never Python object equality**.
SHA-256 is over these bytes. Persistence adds exactly one LF, not part of the
canonical identity. Strict reload rejects duplicate keys, trailing garbage,
invalid UTF-8, invalid JSON and non-finite numbers. Container traversal detaches
working objects; the authority is immutable bytes and a sealed digest.

Historical generic JSON evidence can be compared read-only under these rules
when it lies in this domain. Existing historical hash algorithms/identities
remain their own authority. This adds no migration or rewriting permission.

## Recorder envelope and lifecycle

The recorder uses exclusive creation for baseline, lock, verification,
reservation, observation, halt and final records. Its versioned baseline has
exact fields `protocol`, `evidence`, `identity`; the identity covers the evidence.
Its lock pins raw baseline bytes and all explicitly protected files. Every
stage rechecks the lock. Reload validates envelope shape, protocol and digest.

Freeze → verify canonical evidence → exclusively reserve one callback → record
its result → verify lock → final stop. A mismatch records a pre-pass or
post-observation halt and never repairs authority. A second reservation is
rejected before its callback and recorded as a protocol halt. Finalization
records zero/one/multiple/indeterminate disposition, reservations, completed
observation count, and whether a completed observation occurred.

## Observation accounting and trust boundary

The controlled recorder is the only authorized dispatch path. Exclusive
reservation is durable before dispatch and cannot be reused, even after failure.
A returned callback produces one immutable observation receipt linked to that
reservation; receipt numbering beyond one is detected and halts. A callback
exception, process interruption or incomplete write can leave a reservation
without a completed receipt. That state is **indeterminate**, never asserted to
mean zero actual exposures: halt, no retry and independent investigation are
required. Successful finalization requires no incomplete reservations.

Thus orderly controlled runs distinguish zero and exactly one completed
observation, block a second dispatch, and detect multiple receipts. They do not
attest arbitrary evaluator calls outside the recorder, malicious filesystem
rewrites, or exactly-once completion across process/power failure. These are
explicit trust boundaries, as in the existing local locked benchmark protocol;
uncertainty cannot qualify a particular run. Observation receipts prove callback
return through the trusted path, not semantic correctness of callback output.
No automatic retry or repair is implemented. No benchmark loader/evaluator is
part of this infrastructure module.
